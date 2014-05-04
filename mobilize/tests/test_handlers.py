import unittest
from lxml import html
import mobilize
from utils4test import (
    normxml,
    test_template_loader,
    gtt,
    )

MINIMAL_HTML_DOCUMENT = '''<!doctype html>
<html>
  <body>Hi.</body>
</html>
'''

class TestMoplate(mobilize.Moplate):
    '''
    This is exactly like the regular mobilize.handler.Moplate, except
    that it uses the test_template_loader to load templates.
    '''
    def default_template_loader(self):
        return test_template_loader
    
class TestForMoplate(unittest.TestCase):
    def test_ctor_template(self):
        '''
        test that Moplate ctor can automatically create a Template from a name
        '''
        m_name = TestMoplate([], template='a.html')
        m_template = TestMoplate([], template=gtt('a.html'))
        # select the first matching template by name
        m_multi_a = TestMoplate([], template=['a.html', 'b.html'])
        self.assertEqual('a.html', m_multi_a.template.name)
        m_multi_b = TestMoplate([], template=['b.html', 'a.html'])
        self.assertEqual('b.html', m_multi_b.template.name)
        # if no match for first named template, fall back to second
        m_multi_a2 = TestMoplate([], template=['doesnotexist.html', 'a.html'])
        self.assertEqual('a.html', m_multi_a2.template.name)

    def test_render(self):
        moplate = mobilize.Moplate([], template=gtt('a.html'))
        expected = 'abc xyz'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        moplate = mobilize.Moplate([], {'a' : 42}, template=gtt('b.html'))
        expected = 'a: 42'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = mobilize.Moplate([], params, template=gtt('c.html'))
        expected = 'a: 42\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = mobilize.Moplate([], params, template=gtt('c.html'))
        expected = 'a: 84\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # override params with extra_params
        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = mobilize.Moplate([], params, template=gtt('c.html'))
        expected = 'a: 84\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # add in extra_params (no clobbering)
        params = {
            'a' : 42,
            'b' : 21,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = mobilize.Moplate([], params, template=gtt('c.html'))
        expected = 'a: 84\nX\nY\nZ\nb: 21'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

    def test_params(self):
        # Expect the mobilize.Moplate ctor to loudly fail if we try to pass in controlled parameters
        ok = False
        try:
            moplate = mobilize.Moplate([], {'elements' : ['a', 'b']} , template=gtt('a.html'))
        except AssertionError:
            ok = True
        self.assertTrue(ok)

    def test_source_params(self):
        '''test that default parameters are correctly extracted from the source document'''
        from mobilize.handlers import _rendering_params
        src1 = '''<!doctype html>
<html>
<head>
<title>Source Title</title>
</head>
<body>
<h1>Source Heading</h1>
<p>Hello.</p>
<h1>Second Source Heading that we want to ignore</h1>
</body>
</html>'''
        doc = html.fromstring(src1)
        # general case
        expected = {
            'title' : 'Source Title',
            'heading' : 'Source Heading',
            }
        actual = _rendering_params(doc, [])
        self.assertEqual(expected, actual)

        # with an override
        expected = {
            'title' : 'Override Title',
            'heading' : 'Source Heading',
            }
        actual = _rendering_params(doc, [{'title' : 'Override Title'}])
        self.assertEqual(expected, actual)

    def test__todesktoplink(self):
        from mobilize.handlers import _todesktoplink
        self.assertEqual('http://example.com/foobar.html?mredir=0',
                         _todesktoplink('http', 'example.com', '/foobar.html'))
        self.assertEqual('https://example.com/foobar.html?mredir=0',
                         _todesktoplink('https', 'example.com', '/foobar.html'))
        self.assertEqual('http://example.com/foobar.html?baz=2&mredir=0',
                         _todesktoplink('http', 'example.com', '/foobar.html?baz=2'))

class TestWebSourcer(unittest.TestCase):
    def test_source_url(self):
        from mobilize.handlers import WebSourcer
        testdata = [
            {'source'      : None,
             'rel_url_in'  : '/foo/bar',
             'rel_url_out' : '/foo/bar',
             },
            {'source'      : '/baz',
             'rel_url_in'  : '/foo/bar',
             'rel_url_out' : '/baz',
             },
            {'source'      : lambda u: u.replace('.php', '.html', 1),
             'rel_url_in'  : '/foo.php',
             'rel_url_out' : '/foo.html',
             },
            {'source'      : lambda u: u,
             'rel_url_in'  : '/foo/bar',
             'rel_url_out' : '/foo/bar',
             },
            ]
        for ii, td in enumerate(testdata):
            ws = WebSourcer(source = td['source'])
            expected = td['rel_url_out']
            actual = ws.source_rel_url(td['rel_url_in'])
            self.assertSequenceEqual(expected, actual, ii)

class TestRedirect(unittest.TestCase):
    def test_mk_redirect(self):
        from mobilize.handlers import (
            redirect_to,
            Redirect,
            )
        testenviron = {
            'wsgi.url_scheme'  : 'https',
            'SERVER_PORT'      : '443',
            'SERVER_NAME' : 'www.example.com',
            }
        def mk_start_response(expected_status, expected_location):
            def start_response(status, headers):
                self.assertEqual(expected_status, status)
                hdict = dict(headers)
                assert 'Location' in hdict
                self.assertEqual(expected_location, hdict['Location'])
            return start_response
        class FakeMsite:
            def __init__(mobiledomain):
                self.mobiledomain 
        handler = redirect_to('/foo/bar')
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('302 Found', handler.status)

        handler = redirect_to('/foo/bar', 302)
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('302 Found', handler.status)
        sr = mk_start_response('302 Found', 'https://www.example.com/foo/bar')
        handler.wsgi_response(None, testenviron, sr)

        handler = redirect_to('http://mobilewebup.com/baz', 301)
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('301 Moved Permanently', handler.status)
        sr = mk_start_response('301 Moved Permanently', 'http://mobilewebup.com/baz')
        handler.wsgi_response(None, testenviron, sr)


class TestHandlers(unittest.TestCase):
    def test__html_fromstring(self):
        from mobilize.handlers import _html_fromstring

        html_ref = '''<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''
        
        html_xml_encoding1 = '''<?xml version="1.0" encoding="UTF-8"?>
<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''
        
        testdata = [
        ('html_ref', html_ref),

        # with leading newlines
        ('html_plain1', '''


<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),
        
        # no doctype
        ('html_plain2', '''<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),
        
        # With XML encoding
        ('html_xml_encoding1', html_xml_encoding1),

        # With XML encoding, but with leading newline thrown in for good measure
        ('html_xml_encoding2', '''
<?xml version="1.0" encoding="UTF-8"?>
<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),

        # With XML encoding, but with a truly disturbing number of leading newlines.  IT WILL HAPPEN
        ('html_xml_encoding3', '\n' * 1024 + html_xml_encoding1),
        
        # With XML encoding and generous newlines interspersed
        ('html_xml_encoding4', '''

<?xml version="1.0" encoding="UTF-8"?>


<!doctype html>


<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),
        # mix case
        ('html_xml_mixcase1', '''<?XML version="1.0" encoding="UTF-8"?>
<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),

        ('html_xml_mixcase2', '''<?Xml version="1.0" encoding="UTF-8"?>
<!doctype html>
<html>
  <head><title>Hey</title></head>
  <body>
    <h1>Test Page</h1>
    <p>Have a nice day!</p>
  </body>
</html>'''),
        ]
        
        expected_html = normxml(html_ref)
        for ii, td in enumerate(testdata):
            label, html_input = td
            actual = _html_fromstring(html_input)
            actual_html = normxml(html.tostring(actual))
            self.assertEqual(expected_html, actual_html, '{} [{}]'.format(label, ii))

