import unittest
import os
import mobilize
from utils4test import data_file_path, DATA_DIR

class TestHttp(unittest.TestCase):
    maxDiff = 1024**2
    def test_get_request_headers(self):
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
            ('wsgi.input', None),
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
        from mobilize.http import RequestInfo
        reqinfo = RequestInfo(environ1)
        actual = reqinfo.headers({})
        self.assertDictEqual(expected, actual)
        
        
        
