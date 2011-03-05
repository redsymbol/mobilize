import unittest
import os
import mobilize
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEMPLATE_DIR = os.path.join(DATA_DIR, 'templates')
MINIMAL_HTML_DOCUMENT = '''<!doctype html>
<html>
  <body>Hi.</body>
</html>
'''

class _FakeMsg(object):
    def __init__(self, content_type):
        self.content_type = content_type
    def gettype(self):
        return self.content_type

class _FakeHTTPResponse(object):
    '''
    Duck type mimic of httplib.HTTPResponse

    Some attributes you may want to consider:
      status   -  200, 404, etc.
      version  - 'HTTP/1.1'
      _headers  - {'Content-Type' : 'text/plain'}, etc.
      
    '''
    def __init__(self, **attributes):
        if '_headers' not in attributes:
            attributes['_headers'] = {}
        assert '_content-type' in attributes.keys(), 'must define _content-type'
        for k, v in attributes.iteritems():
            setattr(self, k, v)
        self.msg = _FakeMsg(content_type=attributes['_content-type'])

def data_file_path(*components):
    '''
    path to test data file
    '''
    parts = [os.path.dirname(__file__), 'data'] + list(components)
    return os.path.join(*parts)

def norm_html(s):
    '''
    Normalize an HTML string

    This is meant to make it easier to compare HTML strings, without
    false positives from things like whitespace and indenting issues.
    '''
    return ''.join([x.strip() for x in s.split('\n')])

from mobilize.dj import init_django
init_django([TEMPLATE_DIR])

class TestTemplate(unittest.TestCase):
    def test_render(self):
        from mobilize.dj import DjangoTemplate
        template = DjangoTemplate('a.html', [])
        expected = 'abc xyz'
        actual = template.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        template = DjangoTemplate('b.html', [], {'a' : 42})
        expected = 'a: 42'
        actual = template.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        template = DjangoTemplate('c.html', [], params)
        expected = 'a: 42\nX\nY\nZ\n'
        actual = template.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        template = DjangoTemplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\n'
        actual = template.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # override params with extra_params
        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        template = DjangoTemplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\n'
        actual = template.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # add in extra_params (no clobbering)
        params = {
            'a' : 42,
            'b' : 21,
            'elems' : ['X', 'Y', 'Z'],
            }
        template = DjangoTemplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\nb: 21'
        actual = template.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

    def test_params(self):
        from mobilize.dj import DjangoTemplate
        # Expect the mobilize.Template ctor to loudly fail if we try to pass in controlled parameters
        ok = False
        try:
            template = DjangoTemplate('a.html', [], {'elements' : ['a', 'b']} )
        except AssertionError:
            ok = True
        self.assertTrue(ok)

class TestTemplateMap(unittest.TestCase):
    def test_get_template_for(self):
        from mobilize.exceptions import NoMatchingTemplateException
        from mobilize import DjangoTemplate
        # test templates
        t_a = DjangoTemplate('a.html', [])
        t_b = DjangoTemplate('b.html', [])
        t_c = DjangoTemplate('c.html', [])
        t_d = DjangoTemplate('d.html', [])

        mapping = OrderedDict([
            (r'/alpha/',    t_a),
            (r'/beta/$',    t_b),
            (r'/beta/',     t_c),
            (r'/\w+$',      t_d),
            ])
        tmap = mobilize.TemplateMap(mapping)
        def matching(url):
            # the name of the template actually matched
            t = tmap.get_template_for(url)
            return t.template_name

        self.assertEqual('a.html', matching('/alpha/'))
        self.assertEqual('b.html', matching('/beta/'))
        self.assertEqual('c.html', matching('/beta/flava/'))
        self.assertEqual('d.html', matching('/foobar'))
        self.assertRaises(NoMatchingTemplateException, matching, '/no/such/url/')

class TestMobileSite(unittest.TestCase):
    maxDiff = None
    def test_no_match(self):
        t_a = mobilize.DjangoTemplate('a.html', [])
        mapping = OrderedDict([
            (r'/alpha/$',    t_a),
            ])
        tmap = mobilize.TemplateMap(mapping)
        msite = mobilize.MobileSite('example.com', tmap)
        self.assertTrue(msite.has_match('/alpha/'))
        self.assertFalse(msite.has_match('/beta/'))

    def test_has_match(self):
        full_body = 'veggies are good for you<br/>' * 5
        msite = mobilize.MobileSite('example.com', mobilize.TemplateMap(OrderedDict()))
        rendered = msite.render_body('/someurl', full_body)
        
    def test_render(self):
        from mobilize.dj import DjangoTemplate
        full_body = '''<!doctype html>
<html>
  <title>Test Page Content</title>
  <body>
    <div id="header">
      <img src="/logo.png" alt="Acme"/>
      <h1>Acme Services</h1>
    </div>
    <ul class="navigation">
      <li><a href="/">Home</a></li>
      <li><a href="/services/">Services</a></li>
      <li><a href="/about/">About</a></li>
      <li><a href="/contact/">Contact Us</a></li>
    </ul>
    <!-- main page content -->
    <div id="main-content">
      <h2>Services by Acme</h2>
      <p>Lorem ipsum</p>
      <p>forum gypsum</p>
    </div>
    <!-- sidebar -->
    <div id="sidebar">
      <h2>Acme News</h2>
      <p>Our new product has launched! <a href="/press-releases/2020-04-01/acme-new-product/">Learn More</a></p>
    </div>
  </body>
</html>
'''
        mobile_body = '''<!doctype html>
<html>
  <head>
    <title>&lt;Mobile Test One&gt;</title>
    <meta http-equiv="HandheldFriendly" content="True" />
  </head>
  <body>
    <div class="mwu-melem" id="mwu-melem-0">
      <div id="header">
        <img src="/logo.png" alt="Acme"/>
        <h1>Acme Services</h1>
      </div>
    </div>
    <div class="mwu-melem" id="mwu-melem-1">
      <ul class="navigation">
        <li><a href="/">Home</a></li>
        <li><a href="/services/">Services</a></li>
        <li><a href="/about/">About</a></li>
        <li><a href="/contact/">Contact Us</a></li>
      </ul>
    </div>
    <div class="mwu-melem" id="mwu-melem-2">
      <div id="main-content">
        <h2>Services by Acme</h2>
        <p>Lorem ipsum</p>
        <p>forum gypsum</p>
      </div>
    </div>
      <div class="custom-elem"><a href="http://mobilewebup.com">Mobile Websites</a> by Mobile Web Up</div>
<div class="mwu-mfoot">
  <a href="http://www.example.com">Full Site</a>
</div>
  </body>
</html>
'''
        from mobilize.refine import raw_template, xpath, simple, raw_string
        selectors = [
            xpath(r'//*[@id="header"]'),
            simple('ul.navigation'),
            'div#main-content',
            (raw_string, '<div class="custom-elem"><a href="http://mobilewebup.com">Mobile Websites</a> by Mobile Web Up</div>'),
            (raw_template, 'footer1.html', {'full_site_url' : 'http://www.example.com'}),
            ]
        params = {
            'title' : '<Mobile Test One>',
            }
        template = DjangoTemplate('one.html', selectors, params)
        tmap = mobilize.TemplateMap(OrderedDict([('/foo$', template)]))
        msite = mobilize.MobileSite('example.com', tmap)

        expected = mobile_body
        actual = msite.render_body('/foo', full_body)
        self.assertSequenceEqual(norm_html(expected), norm_html(actual))
        
class TestUtil(unittest.TestCase):
    def test_process_elem(self):
        from lxml import html
        from mobilize.base import process_elem
        testdata = [
            {'elem_str'    : '<p>Hello</p>',
             'classname'   : 'alpha',
             'idname'      : 'beta',
             'newelem_str' : '<div class="alpha" id="beta"><p>Hello</p></div>',
             },
            ]
        for ii, td in enumerate(testdata):
            elem = html.fromstring(td['elem_str'])
            newelem = process_elem(elem, td['classname'], td['idname'])
            self.assertEqual(html.HtmlElement, type(newelem))
            self.assertSequenceEqual(td['newelem_str'], html.tostring(newelem))


    def test_xpathsel(self):
        from mobilize.refine import xpathsel
        testdata = [
            {'selector' : 'div#joyful',
             'xpath'    : r'//div[@id="joyful"]',
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['xpath']
            actual = xpathsel(td['selector'])
            msg = 'e: "%s", a: "%s" [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)
        
    def test_extract_celems(self):
        from mobilize.refine import xpathsel
        testdata = [
            {'datafile' : 'a.xml',
             'selectors' : ['div#happy'],
             'extracted' : ['<div id="happy">lucky</div>'],
             },
            {'datafile' : 'b.xml',
             'selectors' : ['div#joyful'],
             'extracted' : ['<div id="joyful">fun</div>'],
             },
            {'datafile' : 'c.xml',
             'selectors' : ['p.graceful'],
             'extracted' : ['<p class="graceful">laughing</p>'],
             },
            {'datafile' : 'd.xml',
             'selectors' : ['p.graceful'],
             'extracted' : ['<p class="skipping graceful enthusiastic">laughing</p>'],
             },
            {'datafile' : 'e.xml',
             'selectors' : ['p.graceful'],
             'extracted' : ['<p class="skipping graceful enthusiastic">laughing</p>', '<p class="graceful">enthusiastic</p>'],
             },
            ]
        from mobilize.base import extract_celems, elem2str
        for ii, td in enumerate(testdata):
            body = open(data_file_path('extract_celems', td['datafile'])).read()
            expected = td['extracted']
            selectors = map(xpathsel, td['selectors'])
            actual = map(elem2str, extract_celems(body, selectors))
            msg = 'e: %s, a: %s [%d %s]' % (expected, actual, ii, td['datafile'])
            self.assertEqual(expected, actual, msg)

    def test_mobilize(self):
        testdata = [
            {'is_m' : False,
             'attributes' : {
                    '_headers' : dict([('date', 'Tue, 05 Oct 2010 22:32:54 GMT'), ('connection', 'Keep-Alive'), ('etag', '"5e60d8-37e-491aadf613440"'), ('keep-alive', 'timeout=15, max=100'), ('server', 'Apache/2.2.9 (Debian) PHP/5.2.6-1+lenny8 with Suhosin-Patch mod_wsgi/3.2 Python/2.6.6 mod_perl/2.0.4 Perl/v5.10.0')]),
                    '_content-type' : 'image/x-icon',
                    },
             },
            {'is_m' : False,
             'attributes' : {
                    '_content-type' : 'image/x-icon',
                    },
             },
            {'is_m' : False,
             'attributes' : {
                    '_content-type' : 'text/css',
                    },
             },
            {'is_m' : False,
             'attributes' : {
                    '_content-type' : 'text/plain',
                    },
             },
            {'is_m' : True,
             'attributes' : {
                    '_content-type' : 'text/html',
                    },
             },
            {'is_m' : True,
             'attributes' : {
                    '_content-type' : 'application/xhtml+xml',
                    },
             },
            ]
        from mobilize.http import mobilizeable
        for ii, td in enumerate(testdata):
            resp = _FakeHTTPResponse(**td['attributes'])
            expected = td['is_m']
            actual = mobilizeable(resp)
            msg = 'e: %s, a: %s [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)
            
    def test_srchostport(self):
        testdata = [
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'foobar.com',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'foobar.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com:80',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com:81',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 81,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com:443',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 443,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 443,
             },
            {'environ' : {
                    'MWU_OTHER_DOMAIN' : 'example.com:42',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 42,
             },
            ]
        from mobilize.http import srchostport
        for ii, td in enumerate(testdata):
            host, port = srchostport(td['environ'])
            self.assertEqual(td['host'], host, 'e: %s, a: %s [%d]' % (td['host'], host, ii))
            self.assertEqual(td['port'], port, 'e: %s, a: %s [%d]' % (td['port'], port, ii))
            
class TestHttp(unittest.TestCase):
    def test_redir_dest(self):
        testdata = [
            {'in'  : '/todesktop/',
             'out' : '/',
             },
            {'in'  : '/todesktop/?dest=/latest.html%3Fa%3Db%26q%3Dz',
             'out' : '/latest.html?a=b&q=z',
             },
            {'in'  : '/todesktop/?dest=/latest.html%3Fa%3Db%26q%3Dz&xyz=42',
             'out' : '/latest.html?a=b&q=z',
             },
            ]
        from mobilize.http import redir_dest
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = redir_dest(td['in'])
            msg = 'e: %s, i: %s [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

if '__main__'==__name__:
    import unittest
    unittest.main()
