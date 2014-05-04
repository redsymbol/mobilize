'''
Utilities used by tests in this project
'''

import os
from mobilize.templates import TemplateLoader
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_TEMPLATE_DIR = os.path.join(TEST_DATA_DIR, 'templates')
test_template_loader = TemplateLoader([TEST_TEMPLATE_DIR])

def data_file_path(*components):
    '''
    path to test data file
    '''
    parts = [os.path.dirname(__file__), 'data'] + list(components)
    return os.path.join(*parts)

def normxml(s):
    '''
    normalize an XML string for relaxed comparison
    '''
    if type(s) is bytes:
        s = s.decode()
    from lxml import html
    unstripped = html.tostring(html.fromstring(str(s)), pretty_print=True).decode('utf-8')
    return ''.join(line.strip() for line in unstripped.split('\n'))

def gtt(name):
    '''
    Get Test Template - load a test template

    @param name : name of template to load
    @type  name : str

    @return     : template object
    @rtype      : jinja2.Template
    
    '''
    return test_template_loader.get_template(name)

def wsgienviron(**kw):
    '''
    Create a test WSGI environment dictionary
    '''
    import io
    fake_wsgi_input = io.StringIO('hello')
    environ = dict([
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
            ('MWU_SRC_DOMAIN', 'example.com'),
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
    environ.update(**kw)
    return environ
