# Copyright 2010-2012 Mobile Web Up. All rights reserved.
import unittest
import os
import mobilize

from utils4test import wsgienviron

class TestHttp(unittest.TestCase):
    maxDiff = 1024**2
    def test_get_request_headers(self):
        expected = {
             'Content-Length': '151',
             'Content-Type' : 'application/x-www-form-urlencoded',
             'Host': 'example.com',
             'Accept-Language': 'en-us,en;q=0.5',
             'Accept-Encoding': 'identity',
             'Keep-Alive': '115',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100710 Firefox/3.6.7',
             'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
             'Connection': 'keep-alive',
             'Referer': 'http://example.mwuclient.com:2280/windsong_place_contact.html',
             'Pragma': 'no-cache',
             'Cache-Control': 'no-cache',
             'X-Forwarded-For' : '10.0.2.2',
             'X-MWU-Mobilize' : '1',
             }
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(wsgienviron())
        actual = reqinfo.headers({})
        self.assertDictEqual(expected, actual)
        self.assertEqual(reqinfo.body, 'hello')
        self.assertEqual(reqinfo.method, 'POST')
        self.assertEqual(reqinfo.url, 'http://example.com/Scripts/FormMail_WP2.asp')
        self.assertEqual(reqinfo.rel_url, '/Scripts/FormMail_WP2.asp')

    def test_request_mobilizeable(self):
        from mobilize.httputil import RequestInfo
        env_noajax = dict(wsgienviron())
        reqinfo_noajax = RequestInfo(env_noajax)
        self.assertTrue(reqinfo_noajax.mobilizeable)
        
        env_ajax = dict(wsgienviron())
        env_ajax['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        reqinfo_ajax = RequestInfo(env_ajax)
        self.assertFalse(reqinfo_ajax.mobilizeable)
        
    def test_guess_charset(self):
        testdata = [
            {'msg' : 'Kitchen sink - all encoding signals present, and say utf-8',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                    'content-type' : 'text/html; charset=utf-8',
                    },
             'src_resp_bytes' : b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
             'default_charset' : 'utf-8',
             'charset' : 'utf-8',
             },
            {'msg' : 'signaled by content-type header (utf-8)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                    'content-type' : 'text/html; charset=utf-8',
                    },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            }, 
            {'msg' : 'signaled by content-type header (ISO-8859-1)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                    'content-type' : 'text/html; charset=iso-8859-1',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            }, 
            {'msg' : 'signaled by XML entity encoding (utf-8)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                    'content-type' : 'text/html',
                },
            'src_resp_bytes' : b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg': 'signaled by XML entity encoding (ISO-8859-1)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                    'content-type' : 'text/html',
                },
            'src_resp_bytes' : b'''<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            },
            {'msg' : 'Signaled by meta http-equiv tag (utf-8)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg' : 'Signaled by meta http-equiv tag (utf-8, uppercase)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg' : 'Signaled by meta http-equiv tag (utf-8, missing quotes)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content=text/html; charset=utf-8>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg' : 'Signaled by meta http-equiv tag (iso-8859-1)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            },
            {'msg' : 'Signaled by meta http-equiv tag (iso-8859-1, uppercase)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            },
            {'msg' : 'Signaled by meta http-equiv tag (iso-8859-1, missing quotes)',
             # BTW, we need this because much HTML in the wild omits the quotes here:
             #   <meta http-equiv="content-type" content=text/html; charset=iso-8859-1>
             # Of course, this completely changes the semantics,
             # making charset a separate attribute of the meta tag.
             # But that's what real web pages do, so we have to handle it!
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <meta http-equiv="content-type" content=text/html; charset=iso-8859-1>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            },
            {'msg' : 'signaled by html5-style meta charset tag (utf-8)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet"/>
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg' : 'signaled by html5-style meta charset tag (utf-8, uppercase with extra cruft)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset = " UTF-8 " >
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet"/>
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'utf-8',
            },
            {'msg' : 'signaled by html5-style meta charset tag (ISO-8859-1)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="iso-8859-1">
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet"/>
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'iso-8859-1',
            },
            {'msg' : 'No perceivable signal, so falling back on default charset (us-ascii)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet"/>
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'us-ascii',
            'charset' : 'us-ascii',
            },
            {'msg' : 'No perceivable signal, so falling back on default charset (utf-8)',
             'resp' : {
                    'date' : 'Sat, 09 Apr 2011 02:44:35 GMT',
                    'server' : 'Apache/2.2.16 (Debian)',
                    'content-length' : '1488',
                    'content-encoding' : 'gzip',
                    'vary' : 'User-Agent,Cookie,Accept-Encoding',
                    'etag' : '"240deff688b75f3166b4baf12518926c"',
                    'cache-control' : 'no-transform',
                    'keep-alive' : 'timeout=15, max=100',
                    'connection' : 'Keep-Alive',
                },
            'src_resp_bytes' : b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet"/>
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
            'default_charset' : 'utf-8',
            'charset' : 'utf-8',
            },
            ]
        from mobilize.httputil import guess_charset
        for ii, td in enumerate(testdata):
            expected = td['charset']
            actual = guess_charset(td['resp'], td['src_resp_bytes'], td['default_charset'])
            msg = '{}: e: "{}", a: "{}" [{}]'.format(td['msg'], expected, actual, ii)
            self.assertEqual(expected, actual, msg)

    def test__headbytes(self):
        testdata = [
            # normal case
            {'bytesin' : b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>
  <body>Hi.</body></html>''',
             'bytesout' : b'''<head>
    <link href="http://media.redsymbol.net/redsymbol.css" rel="stylesheet" type="text/css" />
    <title>Test Page</title>
  </head>''',
             },
            # no head
            {'bytesin' : b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <body>Hi.</body></html>''',
             'bytesout' : b'',
             },
            ]
        from mobilize.httputil import _headbytes
        for ii, td in enumerate(testdata):
            expected = td['bytesout']
            actual = _headbytes(td['bytesin'])
            self.assertEqual(expected, actual)

    def test_netbytes2str(self):
        from mobilize.httputil import netbytes2str
        kungfu = '功夫' # b'\xe5\x8a\x9f\xe5\xa4\xab'
        src = b'<html><body><p>\xe5\x8a\x9f\xe5\xa4\xab means:\r\n<ul>\r\n<li>hard work</li>\r\n<li>great skill</li>\r\n</ul>'
        expected = '<html><body><p>功夫 means:\n<ul>\n<li>hard work</li>\n<li>great skill</li>\n</ul>'
        actual = netbytes2str(src, 'utf-8')
        self.assertEquals(expected, actual)

    def test__get_root_url(self):
        from mobilize.httputil import _get_root_url
        def env(**kw):
            environ = {
            'MWU_SRC_DOMAIN' : 'www.example.com',
            'wsgi.url_scheme' : 'http',
            'SERVER_PORT' : 80,
            'REQUEST_URI' : '/',
            }
            if 'proto' in kw:
                environ['wsgi.url_scheme'] = kw['proto']
                del kw['proto']
            environ.update(kw)
            return environ
        testdata = [
            {'environ' : env(),
             'url'     : 'http://www.example.com',
             },
            {'environ' : env(REQUEST_URI='/foo/bar'),
             'url'     : 'http://www.example.com',
             },
            {'environ' : env(REQUEST_URI='/foo/bar', SERVER_PORT=42),
             'url'     : 'http://www.example.com:42',
             },
            {'environ' : env(),
             'url'     : 'http://www.example.com',
             },
            {'environ' : env(proto='https', SERVER_PORT=443),
             'url'     : 'https://www.example.com',
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['url']
            try:
                actual = _get_root_url(td['environ'])
            except AttributeError:
                print(td['environ'])
                raise
            self.assertSequenceEqual(expected, actual)

    def test_dict2list(self):
        from collections import OrderedDict
        from mobilize.httputil import dict2list
        testdata = [
            {'dict' : [],
             'list' : [],
             },
            {'dict' : [('alpha', 'beta')],
             'list' : [('alpha', 'beta')],
             },
            {'dict' : [('a', 'b'), ('c', 'd')],
             'list' : [('a', 'b'), ('c', 'd')],
             },
            {'dict' : [('a', ['b', 'c'])],
             'list' : [('a', 'b'), ('a', 'c')],
             },
            {'dict' : [('u', 'v'), ('a', ['b', 'c']), ('z', 'x')],
             'list' : [('u', 'v'), ('a', 'b'), ('a', 'c'), ('z', 'x')],
             },
            # Convert all values to string
            {'dict' : [('content-length', 42)],
             'list' : [('content-length', '42')],
             },
            {'dict' : [('a', [7, 9])],
             'list' : [('a', '7'), ('a', '9')],
             },
            ]
        for ii, td in enumerate(testdata):
            # We use the ordered dict to make it easier to test
            dict1 = OrderedDict(td['dict'])
            expected1 = td['list']
            actual1 = dict2list(dict1)
            self.assertListEqual(expected1, actual1, str(ii))

            # It's possible there could somehow be an error that is
            # masked by the use of OrderedDict rather than dict.  Out
            # of an abundance of caution, let's do another test that
            # ignores the ordering info.

            dict2 = dict(td['dict'])
            expected2 = set(td['list'])
            actual2 = set(dict2list(dict2))
            self.assertSetEqual(expected2, actual2, str(ii))

    def test_queryparams(self):
        from mobilize.httputil import QueryParams
        self.assertDictEqual({}, QueryParams())
        self.assertDictEqual({'' : ['foo']}, QueryParams('=foo'))
        self.assertDictEqual({'foo' : ['bar']}, QueryParams('foo=bar'))
        self.assertDictEqual({'foo' : ['bar'], 'baz' : ['42']}, QueryParams('foo=bar&baz=42'))
        self.assertDictEqual({'foo' : ['bar'], 'baz' : ['42']}, QueryParams('baz=42&foo=bar'))
        self.assertDictEqual({'foo' : ['bar'], 'baz' : ['42', '21']}, QueryParams('baz=42&foo=bar&baz=21'))

    def test_mobilizeable(self):
        from mobilize.httputil import mobilizeable
        # Test requests that are expected to be mobilizeable
        testdata_yes = [
            {'content-type' : 'text/html'},
            {'content-type' : 'application/xhtml+xml'},
            ]

        testdata_no = [
            {'content-type' : 'text/css'},
            {'content-type' : 'image/png'},
            ]
        for ii, headers in enumerate(testdata_yes):
            self.assertTrue(mobilizeable(headers), ii)
        for ii, headers in enumerate(testdata_no):
            self.assertFalse(mobilizeable(headers), ii)

    def test_NewBaseUrl(self):
        from mobilize.httputil import NewBaseUrl
        requested_url = '/Event/browse?search_term=tour&search=Search&month=9&year=2011&event_type_id=&region_ids=&calendar_id=&page_number=1'
        ur = NewBaseUrl('/Event/browseMobile')
        expected = '/Event/browseMobile?search_term=tour&search=Search&month=9&year=2011&event_type_id=&region_ids=&calendar_id=&page_number=1'
        actual = ur(requested_url)
        self.assertEqual(expected, actual)

class TestRequestInfo(unittest.TestCase):
    def test_rawheaders(self):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(wsgienviron())
        rawheaders = reqinfo.rawheaders()
        self.assertTrue(type(rawheaders) is dict, type(rawheaders))
        self.assertSequenceEqual('Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100710 Firefox/3.6.7', rawheaders['User-Agent'])
        
