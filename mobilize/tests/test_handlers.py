# Copyright 2010-2011 Mobile Web Up. All rights reserved.
import unittest
from lxml import html
from utils4test import normxml

class TestMoplate(unittest.TestCase):
    def test_render_empty(self):
        '''
        test that we can render an empty document body correctly
        '''
        from mobilize.handlers import Moplate
        class TestMoplate(Moplate):
            def _render(self, params):
                return ''
        tm = TestMoplate('foo', [])
        self.assertEquals('', tm.render(''))
        
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
    def test_source_uri(self):
        from mobilize.handlers import WebSourcer
        testdata = [
            {'source'      : None,
             'rel_uri_in'  : '/foo/bar',
             'rel_uri_out' : '/foo/bar',
             },
            {'source'      : '/baz',
             'rel_uri_in'  : '/foo/bar',
             'rel_uri_out' : '/baz',
             },
            {'source'      : lambda u: u.replace('.php', '.html', 1),
             'rel_uri_in'  : '/foo.php',
             'rel_uri_out' : '/foo.html',
             },
            {'source'      : lambda u: u,
             'rel_uri_in'  : '/foo/bar',
             'rel_uri_out' : '/foo/bar',
             },
            ]
        for ii, td in enumerate(testdata):
            ws = WebSourcer(source = td['source'])
            expected = td['rel_uri_out']
            actual = ws.source_rel_uri(td['rel_uri_in'])
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

    def test_postprocess_response_headers(self):
        '''test that we rewrite the Location: header on 301 or 302 redirect, that we drop the transfer-encoding header, and other postprocessing of headers for all content (not just that which is mobilizeable'''
        from mobilize.handlers import postprocess_response_headers
        from mobilize.base import MobileSite, Domains
        domains = Domains(mobile='m.example.com', desktop='www.example.com')
        msite = MobileSite(domains, [])

        # drop transfer-encoding header
        headers = [
            ('transfer-encoding' , 'chunked'),
            ('host'              , 'www.example.com'),
            ]
        modified = postprocess_response_headers(msite, headers, 200)
        modified_keys = set(k for k, v in modified)
        self.assertTrue('transfer-encoding' not in modified_keys)

        # rewrite location on 301
        headers = [
            ('host'     , 'www.example.com'),
            ('location' , 'http://www.example.com/path/to/file'),
            ]
        modified = postprocess_response_headers(msite, headers, 301)
        location_values = list(v for k, v in modified if 'location' == k)
        # Should just find one match...
        assert len(location_values) == 1, len(location_values)
        self.assertEqual('http://m.example.com/path/to/file', location_values[0])
                        
        # same for 302
        modified = postprocess_response_headers(msite, headers, 302)
        location_values = list(v for k, v in modified if 'location' == k)
        # Should just find one match...
        assert len(location_values) == 1, len(location_values)
        self.assertEqual('http://m.example.com/path/to/file', location_values[0])


    def test__new_location(self):
        from mobilize.handlers import _new_location
        from mobilize.base import Domains
        # basic case
        domains = Domains('m.example.com', 'www.example.com')
        location = 'http://www.example.com/something'
        expected = 'http://m.example.com/something'
        actual = _new_location(location, domains)
        self.assertSequenceEqual(expected, actual)

        # production overrides
        domains = Domains('m.example.com', 'www.example.com',  production_http_desktop='www.mobilewebup.com')
        location = 'http://www.mobilewebup.com/something'
        expected = 'http://m.example.com/something'
        actual = _new_location(location, domains)
        self.assertSequenceEqual(expected, actual)

        # https
        domains = Domains('m.example.com', 'www.example.com', production_https_desktop='www.mobilewebup.com')
        location = 'https://www.mobilewebup.com/something'
        expected = 'https://m.example.com/something'
        actual = _new_location(location, domains)
        self.assertSequenceEqual(expected, actual)

        # https w/ development overrides
        domains = Domains('m.example.com', 'www.example.com', https_mobile = 'secure-mobile.example.com', production_https_desktop='www.mobilewebup.com')
        location = 'https://www.mobilewebup.com/something'
        expected = 'https://secure-mobile.example.com/something'
        actual = _new_location(location, domains)
        self.assertSequenceEqual(expected, actual)
