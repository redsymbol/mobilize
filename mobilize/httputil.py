'''
HTTP and WSGI server utilities

'''

import re
import collections

def _name2field(name, prefix=''):
    '''
    Convert HTTP_FOO_BAR_BAZ to Foo-Bar-Baz

    @param name : HTTP_FOO_BAR_BAZ
    @type  name : str

    @return : Foo-Bar-Baz
    @rtype  : str
    
    '''
    assert name.startswith(prefix), 'Field name "%s" is supposed to start with "%s"' % (name, prefix)
    parts = name[len(prefix):].split('_')
    field = '-'.join(part.capitalize() for part in parts)
    return field

def _get_uri(environ):
    '''
    Get the incoming request URI
    
    '''
    proto = environ.get('wsgi.url_scheme', 'http')
    host, port = srchostport(environ)
    assert type(port) is int, type(port)
    uri = '%s://%s' % (proto, host)
    if 80 != port:
        uri += ':' + str(port)
    uri += get_rel_uri(environ)
    return uri

def get_response_headers(resp_headers, environ, overrides):
    '''
    Fetch and calculate the mobile response headers

    Overrides is a dictionary mapping response header names
    (lowercase) to what's called an "override". An override is either
    a static value, or a callable that accepts one argument.

    If the override is a callable, it is invoked on the header's
    existing value; the returned is then used as the new value for the
    header.  This assumes this header already has a value in the
    response.

    Otherwise, the header is simply set to the override, as a value.
    If the header wasn't defined before, this creates it.

    TODO: Maybe we should Camel-Case the header names. currently they are lower-cased

    @param resp      : Response from target server
    @type  resp      : ?

    @param environ   : WSGI environment
    @type  environ   : dict

    @param overrides : Additional response transformations
    @type  overrides : dict: str -> mixed

    @return          : transformed response headers
    @rtype           : list of (header, value) tuples
    
    '''
    from .headers import get_response_xform
    def hv(header, value):
        if header in overrides:
            override = overrides[header]
            if isinstance(override, collections.Callable):
                newvalue = override(environ, value)
            else:
                newvalue = override
            respheader = (header, newvalue)
        else:
            xformer = get_response_xform(header.lower())
            value = xformer(environ, value)
            respheader = (header, value)
        return respheader
    return list(hv(header, value) for header, value in resp_headers.items())

def mobilizeable(resp):
    '''
    Indicates whether this response is "mobilizeable" or not.

    (We don't want to try to mobilize images or other binary data, for
    example - at least at this level.)

    @param resp : response headers
    @type  resp : dict
    
    '''
    contenttype = resp.get('content-type', '')
    if 'xml' in contenttype or 'html' in contenttype:
        return True
    return False

def srchostport(environ):
    '''
    Calculate/choose source hostname and port

    environ is meant to be the WSGI environment dictionary,
    expectected to contain the following keys:

      MWU_OTHER_DOMAIN
      SERVER_PORT

    This function returns a tuple of hostname and port, so you will
    probably want to invoke it like:

      host, port = srchostport(wsgi_environ)

    @param param : WSGI environment
    @type  param : dict

    @return : Source host and port
    @rtype  : tuple(str, int)
    
    '''
    full_host = environ['MWU_OTHER_DOMAIN']
    if ':' in full_host:
        full_host, full_port = full_host.split(':')
        full_port = int(full_port)
    else:
        requesting_port = int(environ['SERVER_PORT'])
        if requesting_port in (80, 443):
            full_port = requesting_port
        else:
            full_port = 80
    return full_host, full_port
    
def get_rel_uri(environ):
    '''
    Shortcut function for getting the relative request URI

    So if the request is to http://m.example.com/foo/bar.html, this
    will return '/foo/bar.html'.

    @return : relative request URI
    @rtype  : str
    
    '''
    return environ['REQUEST_URI']

def get_http():
    '''
    Get an http object

    This is just an instance of the httplib2.Http class, properly
    customized, extended and configured.

    @return : http object
    @rtype  : httplib2.Http
    
    '''
    from httplib2 import Http
    http = Http()
    http.follow_redirects = False
    return http

def dict2list(d):
    return list((header, value) for header, value in d.items())

class RequestInfo(object):
    '''
    Encapsulates information about an incoming HTTP request.

    This is for the request directly from the client, prior to any handler.
    
    '''
    def __init__(self, wsgienviron):
        '''
        ctor

        @param wsgienviron : WSGI environment
        @type  wsgienviron : dict
        
        '''
        self.wsgienviron = wsgienviron
        self.method = wsgienviron['REQUEST_METHOD'].upper()
        if self.method in ('POST', 'PUT'):
            self.body = wsgienviron['wsgi.input'].read()
        else:
            self.body = None
        self.uri = _get_uri(wsgienviron)
        self.rel_uri = get_rel_uri(wsgienviron)

    def headers(self, overrides):
        '''
        get request headers
    
        See docs of get_response_headers for an explanation of overrides.
        
        @param environ   : WSGI environment
        @type  environ   : dict
    
        @param overrides : Additional response transformations
        @type  overrides : dict: str -> mixed
    
        @return          : transformed request headers
        @rtype           : dict
        
        '''
        from .headers import get_request_xform
        headers = {}
        for header, value in self.iterrawheaders():
            # We want to preserve the Camel-Casing of the header names
            # we're about to send, because who knows what web server
            # or gateway will randomly go crazy if we don't.  But for
            # consistency and simplicity, related data
            # (e.g. overrides) are keyed by their fully-lowercased
            # equivalents.  These two ideas are labeled "header" and
            # "headerkey" respectively.
            headerkey = header.lower()
            if headerkey in overrides:
                override = overrides[headerkey]
                if isinstance(override, collections.Callable):
                    newvalue = override(self.wsgienviron, value)
                else:
                    newvalue = override
            else:
                xformer = get_request_xform(headerkey, self.method)
                newvalue = xformer(self.wsgienviron, value)
            headers[header] = newvalue
        return headers

    def iterrawheaders(self):
        '''
        Generate the raw http headers and their values

        These are the raw headers from the client, before any
        overrides or other customization.  The header name is camel
        cased, with words separated by hyphens - e.g. "Last-Modified",
        not "HTTP_LAST_MODIFIED" nor "last-modified".

        @return : (header, value) pairs
        @rtype  : iterator of (str, str)
        
        '''
        extrakeys = (
            'CONTENT_LENGTH',
            'CONTENT_TYPE',
            )
        def headername(rawkey):
            '''Returns Camel-Case field name if this is an http request header, or None if it's not.'''
            header = None
            if rawkey.startswith('HTTP_'):
                header = _name2field(rawkey, 'HTTP_')
            elif rawkey in extrakeys:
                header = _name2field(rawkey)
            return header
        for rawkey, value in self.wsgienviron.items():
            header = headername(rawkey)
            if header is not None:
                yield header, value

def guess_charset(resp, src_resp_bytes, default_charset):
    '''
    Make the best guess of the charset of an http response

    @param resp            : response headers
    @type  resp            : dict

    @param src_resp_bytes  : The raw response body
    @type  src_resp_bytes  : bytes

    @param default_charset : Charset to use if no other choice is clearly indicated
    @type  default_charset : str

    @return                : Likely best charset
    @rtype                 : str
    
    '''
    def _has_xml_header(body):
        key = b'<?xml'
        initial = body[:len(key)].lower()
        return key == initial
    def _headbytes(html_bytes):
        '''fetch the portion of a document before the opening of the body element'''
        def findpos(key):
            match = re.search(key, html_bytes, re.I)
            assert match is not None, key
            return match.start()
        start = findpos(b'<head')
        end = findpos(b'<body')
        return html_bytes[start:end].strip()
    def _ctcharset(resp):
        if 'content-type' in resp:
            match = re.search(r'\bcharset=([^; ]+)', resp['content-type'])
            if match is not None:
                return match.groups()[0]
        return None
    charset = default_charset
    check_ct = _ctcharset(resp)
    # Look for content-type HTTP response header
    if check_ct is not None:
        charset = check_ct
    # Does the document have an xml encoding declaration?
    elif _has_xml_header(src_resp_bytes):
        n = src_resp_bytes.find(b'<html')
        firstline = src_resp_bytes[:n].decode()
        match = re.search(r'encoding="([^"]+)"', firstline)
        if match is not None:
            charset = match.groups()[0].lower()
    # Does the HEAD element set the encoding in a META declaration?
    # That means either an html5 'meta charset="..."', or 'meta http-equiv="content-type"'
    else:
        headbytes = _headbytes(src_resp_bytes).decode()
        match_ct = re.search(
            r'<meta\s+http-equiv\s*=\s*(?:"content-type"|content-type)\s+[^>]*charset=("[^>"]+"|[^>"]+)',
            headbytes, re.I)
        if match_ct is not None:
            charset = match_ct.groups()[0].lower()
        else:
            match_ct_html5 = re.search(
                r'<meta\s+charset\s*=\s*("[^>"]+"|[^>" ]+)',
                headbytes, re.I)
            if match_ct_html5 is not None:
                charset = match_ct_html5.groups()[0].lower().strip('" ')
    # Else just keep the default charset.
    return charset

def mk_wsgi_application(msite, verboselog=False):
    '''
    Create the WSGI application

    @param msite           : mobile site
    @type  msite           : mobilize.base.MobileSite

    @return                : WSGI application function
    @rtype                 : function accepting (environ, start_response) arguments
    
    '''
    def application(environ, start_response):
        from mobilize.handlers import passthrough
        from mobilize.exceptions import NoMatchingMoplateException
        try:
            handler = msite.handler_map.get_handler_for(get_rel_uri(environ))
        except NoMatchingMoplateException:
            handler = passthrough
        return handler.wsgi_response(msite, environ, start_response)
    return application
