import unittest
import os
import mobilize
from utils4test import (
    data_file_path, DATA_DIR,
    )

TEMPLATE_DIR = os.path.join(DATA_DIR, 'templates')
MINIMAL_HTML_DOCUMENT = '''<!doctype html>
<html>
  <body>Hi.</body>
</html>
'''

def norm_html(s):
    '''
    Normalize an HTML string

    This is meant to make it easier to compare HTML strings, without
    false positives from things like whitespace and indenting issues.
    '''
    return ''.join([x.strip() for x in s.split('\n')])

from mobilize.dj import init_django
init_django([TEMPLATE_DIR])

class TestMoplate(unittest.TestCase):
    def test_render(self):
        from mobilize.dj import DjangoMoplate
        moplate = DjangoMoplate('a.html', [])
        expected = 'abc xyz'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        moplate = DjangoMoplate('b.html', [], {'a' : 42})
        expected = 'a: 42'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = DjangoMoplate('c.html', [], params)
        expected = 'a: 42\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT)
        self.assertEqual(expected, actual)

        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = DjangoMoplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # override params with extra_params
        params = {
            'a' : 42,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = DjangoMoplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\n'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

        # add in extra_params (no clobbering)
        params = {
            'a' : 42,
            'b' : 21,
            'elems' : ['X', 'Y', 'Z'],
            }
        moplate = DjangoMoplate('c.html', [], params)
        expected = 'a: 84\nX\nY\nZ\nb: 21'
        actual = moplate.render(MINIMAL_HTML_DOCUMENT, {'a' : 84})
        self.assertEqual(expected, actual)

    def test_params(self):
        from mobilize.dj import DjangoMoplate
        # Expect the mobilize.Moplate ctor to loudly fail if we try to pass in controlled parameters
        ok = False
        try:
            moplate = DjangoMoplate('a.html', [], {'elements' : ['a', 'b']} )
        except AssertionError:
            ok = True
        self.assertTrue(ok)

class TestHandlerMap(unittest.TestCase):
    def test_get_handler_for(self):
        from mobilize.exceptions import NoMatchingMoplateException
        from mobilize import DjangoMoplate
        # test templates
        t_a = DjangoMoplate('a.html', [])
        t_b = DjangoMoplate('b.html', [])
        t_c = DjangoMoplate('c.html', [])
        t_d = DjangoMoplate('d.html', [])

        mapping = [
            (r'/alpha/',    t_a),
            (r'/beta/$',    t_b),
            (r'/beta/',     t_c),
            (r'/\w+$',      t_d),
            ]
        tmap = mobilize.HandlerMap(mapping)
        def matching(url):
            # the name of the moplate actually matched
            t = tmap.get_handler_for(url)
            return t.template_name

        self.assertEqual('a.html', matching('/alpha/'))
        self.assertEqual('b.html', matching('/beta/'))
        self.assertEqual('c.html', matching('/beta/flava/'))
        self.assertEqual('d.html', matching('/foobar'))
        self.assertRaises(NoMatchingMoplateException, matching, '/no/such/url/')

class TestMobileSite(unittest.TestCase):
    maxDiff = None
    def test_no_match(self):
        t_a = mobilize.DjangoMoplate('a.html', [])
        mapping = [
            (r'/alpha/$',    t_a),
            ]
        tmap = mobilize.HandlerMap(mapping)
        msite = mobilize.MobileSite('example.com', tmap)
        self.assertTrue(msite.has_match('/alpha/'))
        self.assertFalse(msite.has_match('/beta/'))

    def test_has_match(self):
        full_body = 'veggies are good for you<br/>' * 5
        msite = mobilize.MobileSite('example.com', mobilize.HandlerMap([]))
        rendered = msite.render_body('/someurl', full_body)
        
    def test_render(self):
        from mobilize.dj import DjangoMoplate
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
    <div class="mwu-elem" id="mwu-elem-0">
      <div id="header">
        <img src="http://example.com/logo.png" alt="Acme">
        <h1>Acme Services</h1>
      </div>
    </div>
    <div class="mwu-elem" id="mwu-elem-1">
      <ul class="navigation">
        <li><a href="/">Home</a></li>
        <li><a href="/services/">Services</a></li>
        <li><a href="/about/">About</a></li>
        <li><a href="/contact/">Contact Us</a></li>
      </ul>
    </div>
    <div class="mwu-elem" id="mwu-elem-2">
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
        from mobilize.components import DjangoTemplate, XPath, CssPath, RawString
        components = [
            XPath(r'//*[@id="header"]'),
            CssPath('ul.navigation'),
            CssPath('div#main-content'),
            RawString('<div class="custom-elem"><a href="http://mobilewebup.com">Mobile Websites</a> by Mobile Web Up</div>'),
            DjangoTemplate('footer1.html', {'full_site_url' : 'http://www.example.com'}),
            ]
        params = {
            'title'        : '<Mobile Test One>',
            'fullsite'     : 'example.com',
            'request_path' : '/foo',
            }
        moplate = DjangoMoplate('one.html', components, params)
        tmap = mobilize.HandlerMap([('/foo$', moplate)])
        msite = mobilize.MobileSite('example.com', tmap)

        expected = mobile_body
        actual = msite.render_body('/foo', full_body)
        self.assertSequenceEqual(norm_html(expected), norm_html(actual))
        
class TestUtil(unittest.TestCase):
    def test_mobilize(self):
        testdata = [
            {'is_m' : False,
             'headers' : dict([('date', 'Tue, 05 Oct 2010 22:32:54 GMT'), ('connection', 'Keep-Alive'), ('etag', '"5e60d8-37e-491aadf613440"'), ('keep-alive', 'timeout=15, max=100'), ('server', 'Apache/2.2.9 (Debian) PHP/5.2.6-1+lenny8 with Suhosin-Patch mod_wsgi/3.2 Python/2.6.6 mod_perl/2.0.4 Perl/v5.10.0'), ('content-type', 'image/x-icon')]),
             },
            {'is_m' : False,
             'headers' : {
                    'content-type' : 'image/x-icon',
                    },
             },
            {'is_m' : False,
             'headers' : {
                    'content-type' : 'text/css',
                    },
             },
            {'is_m' : False,
             'headers' : {
                    'content-type' : 'text/plain',
                    },
             },
            {'is_m' : True,
             'headers' : {
                    'content-type' : 'text/html',
                    },
             },
            {'is_m' : True,
             'headers' : {
                    'content-type' : 'application/xhtml+xml',
                    },
             },
            ]
        from mobilize.http import mobilizeable
        for ii, td in enumerate(testdata):
            resp = td['headers']
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
            
if '__main__'==__name__:
    import unittest
    unittest.main()
