import unittest
import os
import mobilize
from utils4test import data_file_path, DATA_DIR

class TestHttp(unittest.TestCase):
    maxDiff = 1024**2
    def test_get_request_headers(self):
        import io
        fake_wsgi_input = io.StringIO('hello')
        environ1 = dict([
            ('mod_wsgi.listener_port', '80'),
            ('HTTP_REFERER', 'http://example.mwuclient.com:2280/windsong_place_contact.html'),
            ('mod_wsgi.listener_host', ''),
            ('SERVER_SOFTWARE', 'Apache/2.2.16 (Debian)'),
            ('SCRIPT_NAME', ''),
            ('mod_wsgi.handler_script', ''),
            ('SERVER_SIGNATURE', '<address>Apache/2.2.16 (Debian) Server at luxuryaptswny.mwuclient.com Port 2280</address>\\n'),
            ('REQUEST_METHOD', 'POST'),
            ('HTTP_KEEP_ALIVE', '115'),
            ('SERVER_PROTOCOL', 'HTTP/1.1'),
            ('QUERY_STRING', ''),
            ('CONTENT_LENGTH', '151'),
            ('HTTP_ACCEPT_CHARSET', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('HTTP_USER_AGENT', 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100710 Firefox/3.6.7'),
            ('HTTP_CONNECTION', 'keep-alive'),
            ('SERVER_NAME', 'luxuryaptswny.mwuclient.com'),
            ('REMOTE_ADDR', '10.0.2.2'),
            ('mod_wsgi.request_handler', 'wsgi-script'),
            ('wsgi.url_scheme', 'http'),
            ('PATH_TRANSLATED', '/var/www/m.example.com/wsgiscript.py/Scripts/FormMail_WP2.asp'),
            ('SERVER_PORT', '2280'),
            ('wsgi.multiprocess', True),
            ('mod_wsgi.input_chunked', '0'),
            ('SERVER_ADDR', '10.0.2.15'),
            ('DOCUMENT_ROOT', '/etc/apache2/htdocs'),
            ('mod_wsgi.process_group', ''),
            ('HTTP_PRAGMA', 'no-cache'),
            ('SCRIPT_FILENAME', '/var/www/m.example.com/wsgiscript.py'),
            ('SERVER_ADMIN', '[no address given]'),
            ('wsgi.input', fake_wsgi_input),
            ('HTTP_HOST', 'example.mwuclient.com:2280'),
            ('wsgi.multithread', True),
            ('mod_wsgi.callable_object', 'application'),
            ('HTTP_CACHE_CONTROL', 'no-cache'),
            ('REQUEST_URI', '/Scripts/FormMail_WP2.asp'),
            ('HTTP_ACCEPT', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('wsgi.version', (1, 1)),
            ('GATEWAY_INTERFACE', 'CGI/1.1'),
            ('wsgi.run_once', False),
            ('MWU_OTHER_DOMAIN', 'example.com'),
            ('wsgi.errors', None),
            ('REMOTE_PORT', '49810'),
            ('HTTP_ACCEPT_LANGUAGE', 'en-us,en;q=0.5'),
            ('mod_wsgi.version', (3, 3)),
            ('CONTENT_TYPE', 'application/x-www-form-urlencoded'),
            ('mod_wsgi.application_group', 'm.example.com:2280|'),
            ('mod_wsgi.script_reloading', '1'),
            ('wsgi.file_wrapper', None),
            ('HTTP_ACCEPT_ENCODING', 'identity'),
            ('PATH_INFO', '/Scripts/FormMail_WP2.asp')
            ])
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
             }
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ1)
        actual = reqinfo.headers({})
        self.assertDictEqual(expected, actual)
        self.assertEqual(reqinfo.body, 'hello')
        self.assertEqual(reqinfo.method, 'POST')
        self.assertEqual(reqinfo.uri, 'http://example.com/Scripts/FormMail_WP2.asp')
        self.assertEqual(reqinfo.rel_uri, '/Scripts/FormMail_WP2.asp')
        
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
