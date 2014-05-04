import unittest
import os
import mobilize
from utils4test import gtt

def norm_html(s):
    '''
    Normalize an HTML string

    This is meant to make it easier to compare HTML strings, without
    false positives from things like whitespace and indenting issues.
    '''
    return ''.join([x.strip() for x in s.split('\n')])

class TestHandlerMap(unittest.TestCase):
    def test_get_handler_for(self):
        from mobilize.exceptions import NoMatchingHandlerException
        # test templates
        t_a = mobilize.Moplate([], template=gtt('a.html'))
        t_b = mobilize.Moplate([], template=gtt('b.html'))
        t_c = mobilize.Moplate([], template=gtt('c.html'))
        t_d = mobilize.Moplate([], template=gtt('d.html'))

        mapping = [
            (r'/alpha/',    t_a),
            (r'/beta/$',    t_b),
            (r'/beta/',     t_c),
            (r'/\w+$',      t_d),
            ]
        hmap = mobilize.HandlerMap(mapping)
        def matching(url):
            # the name of the moplate actually matched
            h = hmap.get_handler_for(url)
            return h.template.name

        self.assertEqual('a.html', matching('/alpha/'))
        self.assertEqual('b.html', matching('/beta/'))
        self.assertEqual('c.html', matching('/beta/flava/'))
        self.assertEqual('d.html', matching('/foobar'))
        self.assertRaises(NoMatchingHandlerException, matching, '/no/such/url/')

class TestMobileSite(unittest.TestCase):
    maxDiff = None

    def test_render(self):
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
        <img src="/logo.png" alt="Acme">
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
        from utils4test import TEST_TEMPLATE_DIR
        from mobilize.components import (
            FromTemplate,
            XPath,
            CssPath,
            RawString,
            )
        components = [
            XPath(r'//*[@id="header"]'),
            CssPath('ul.navigation'),
            CssPath('div#main-content'),
            RawString('<div class="custom-elem"><a href="http://mobilewebup.com">Mobile Websites</a> by Mobile Web Up</div>'),
            FromTemplate('footer1.html', {'full_site_url' : 'http://www.example.com'}, template_dirs=[TEST_TEMPLATE_DIR]),
            ]
        params = {
            'title'        : '&lt;Mobile Test One&gt;',
            'fullsite'     : 'example.com',
            'request_path' : '/foo',
            }
        moplate = mobilize.Moplate(components, params, template=gtt('one.html'))
        hmap = mobilize.HandlerMap([('/foo$', moplate)])
        domains = mobilize.Domains(mobile='m.example.com', desktop='example.com')
        msite = mobilize.MobileSite(domains, hmap)

        expected = mobile_body
        actual = moplate.render(full_body, params)
        self.assertSequenceEqual(norm_html(expected), norm_html(actual))
        
    def test_postprocess_response_headers(self):
        '''test that we rewrite the Location: header on 301 or 302 redirect, that we drop the transfer-encoding header, and other postprocessing of headers for all content (not just that which is mobilizeable'''
        from mobilize.base import MobileSite, Domains
        domains = Domains(mobile='m.example.com', desktop='www.example.com')
        msite = MobileSite(domains, [])

        # drop transfer-encoding header
        headers = [
            ('transfer-encoding' , 'chunked'),
            ('host'              , 'www.example.com'),
            ]
        modified = msite.postprocess_response_headers(headers, 200)
        modified_keys = set(k for k, v in modified)
        self.assertTrue('transfer-encoding' not in modified_keys)

        # rewrite location on 301
        headers = [
            ('host'     , 'www.example.com'),
            ('location' , 'http://www.example.com/path/to/file'),
            ]
        modified = msite.postprocess_response_headers(headers, 301)
        location_values = list(v for k, v in modified if 'location' == k)
        # Should just find one match...
        assert len(location_values) == 1, len(location_values)
        self.assertEqual('http://m.example.com/path/to/file', location_values[0])
                        
        # same for 302
        modified = msite.postprocess_response_headers(headers, 302)
        location_values = list(v for k, v in modified if 'location' == k)
        # Should just find one match...
        assert len(location_values) == 1, len(location_values)
        self.assertEqual('http://m.example.com/path/to/file', location_values[0])

    def test_postprocess_response_headers_precise(self):
        '''
        Test that a recursively similar Location: domain target is not recursively replaced
        '''
        from mobilize.base import MobileSite, Domains
        domains = Domains(mobile='testwww.example.com:2280', desktop='www.example.com', production_http_desktop='www.example.com')
        msite = MobileSite(domains, [])
        headers = [
            ('host'     , 'testwww.example.com'),
            ('location' , 'http://testwww.example.com:2280/path/to/file'),
            ]
        modified = msite.postprocess_response_headers(headers, 302)
        location_values = list(v for k, v in modified if 'location' == k)
        # Should just find one match...
        assert len(location_values) == 1, len(location_values)
        # Make sure it's not http://testtestwww.example.com:2280:2280/path/to/file
        self.assertEqual('http://testwww.example.com:2280/path/to/file', location_values[0])

        # again with different location
        headers = [
            ('host'     , 'testwww.example.com'),
            ('location' , 'http://testwww.example.com:2280'),
            ]
        modified = msite.postprocess_response_headers(headers, 302)
        location_values = list(v for k, v in modified if 'location' == k)
        assert len(location_values) == 1, len(location_values)
        self.assertEqual('http://testwww.example.com:2280', location_values[0])
        

    def test__new_location(self):
        from mobilize.base import (
            Domains,
            _new_location,
            )
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

    def test_must_fake_http_head(self):
        from mobilize.base import MobileSite, Domains, HandlerMap
        class MockRequestInfo:
            method = None
            rel_url = None

        msite = MobileSite(Domains('m.example.com', 'example.com'), HandlerMap([]))
        reqinfo = MockRequestInfo()

        msite.fake_head_requests = True
        reqinfo.method = 'HEAD'
        reqinfo.rel_url = '/'
        self.assertTrue(msite.must_fake_http_head(reqinfo))
        
        msite.fake_head_requests = False
        reqinfo.method = 'HEAD'
        reqinfo.rel_url = '/'
        self.assertFalse(msite.must_fake_http_head(reqinfo))
        
        msite.fake_head_requests = True
        reqinfo.method = 'GET'
        reqinfo.rel_url = '/'
        self.assertFalse(msite.must_fake_http_head(reqinfo))
        
        msite.fake_head_requests = True
        reqinfo.method = 'HEAD'
        reqinfo.rel_url = '/foo'
        self.assertFalse(msite.must_fake_http_head(reqinfo))
        
        msite.fake_head_requests = True
        reqinfo.method = 'POST'
        reqinfo.rel_url = '/'
        self.assertFalse(msite.must_fake_http_head(reqinfo))

class TestUtil(unittest.TestCase):
    def test_mobilizeable(self):
        '''tests for mobilize.httputil.mobilizeable'''
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
        from mobilize.httputil import mobilizeable
        for ii, td in enumerate(testdata):
            resp = td['headers']
            expected = td['is_m']
            actual = mobilizeable(resp)
            msg = 'e: %s, a: %s [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)
            
    def test_srchostport(self):
        testdata = [
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'foobar.com',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'foobar.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com:80',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 80,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com:81',
                    'SERVER_PORT' : 80,
                    },
             'host' : 'example.com',
             'port' : 81,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com:443',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 443,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 443,
             },
            {'environ' : {
                    'MWU_SRC_DOMAIN' : 'example.com:42',
                    'SERVER_PORT' : 443,
                    },
             'host' : 'example.com',
             'port' : 42,
             },
            ]
        from mobilize.httputil import srchostport
        for ii, td in enumerate(testdata):
            host, port = srchostport(td['environ'])
            self.assertEqual(td['host'], host, 'e: %s, a: %s [%d]' % (td['host'], host, ii))
            self.assertEqual(td['port'], port, 'e: %s, a: %s [%d]' % (td['port'], port, ii))
            
if '__main__'==__name__:
    import unittest
    unittest.main()
