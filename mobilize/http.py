'''
HTTP and WSGI server utilities
'''

import re

def _case(s):
    s = s.lower()
    if len(s):
        c, tail = s[0], s[1:]
        s = c.upper() + tail
    return s

def _name2field(name):
    prefix = 'HTTP_'
    assert name.startswith(prefix), 'Keys are all supposed to start with "%s": %s' % (prefix, name)
    parts = name[len(prefix):].split('_')
    field = '-'.join(_case(part) for part in parts)
    return field

def get_request_headers(environ):
    '''
    @param environ : WSGI environment
    @type  environ : dict

    @return        : transformed request headers
    @rtype         : dict
    
    '''
    from headers import get_request_xform
    method = get_method(environ)
    headers = {}
    for key, val in environ.iteritems():
        if key.startswith('HTTP_'):
            httpname = _name2field(key)
            xformer = get_request_xform(httpname.lower(), method)
            val = xformer(environ, val)
            headers[httpname] = val
    return headers

def get_response_headers(resp, environ, overrides):
    '''
    @param resp    : Response from target server
    @type  resp    :

    @param environ : WSGI environment
    @type  environ : dict

    @return        : transformed response headers
    @rtype         : list of (header, value) tuples
    
    '''
    from headers import get_response_xform
    def hv(pair):
        header, value = pair
        if header in overrides:
            override = overrides[header]
            if callable(override):
                newvalue = override(value)
            else:
                newvalue = override
            respheader = (header, newvalue)
        else:
            xformer = get_response_xform(header.lower())
            value = xformer(environ, value)
            respheader = (header, value)
        return respheader
    return list(hv(pair) for pair in resp.getheaders())

def mobilizeable(resp):
    '''
    Indicates whether this response is "mobilizeable" or not.

    @param resp : Response object from source server
    @type  resp : httplib.HTTPResponse
    
    '''
    content_type = resp.msg.gettype()
    if 'xml' in content_type or 'html' in content_type:
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


_DEST_RE = re.compile(r'\bdest=([^&]+)')
def redir_dest(uri):
    '''
    Find the destination URI to redirect to on the desktop site

    Note that this takes in a relative URI, and returns a *different*
    relative URI.  The input URI is the link the person clicked on the
    mobile site, to switch to the desktop view.  The returned value is
    the URI they should be sent do on the desktop site.

    @param uri : URI of the redirecting GET requst
    @type  uri : str

    @return    : destination URI on the desktop site
    @rtype     : str
    
    '''
    from urllib import unquote
    match = _DEST_RE.search(uri)
    if match:
        dest = unquote(match.group(1))
    else:
        dest = '/'
    return dest
    
def todesktop(environ, start_response, full_domain):
    '''
    Redirection to desktop view

    This WSGI sub-application will redirect the current page, assumed
    to be on the mobile view, to the corresponding page on the desktop
    view (site).
    '''
    uri = environ['REQUEST_URI']
    method = environ['REQUEST_METHOD'].upper()
    assert 'GET' == method, method
    dest = redir_dest(uri)
    assert dest.startswith('/'), dest
    headers = [
        ('Location', 'http://%s%s' % (full_domain, dest)),
        ('Set-Cookie', 'mredir=0; path=/'), # TODO: expires
        ]
    start_response('302 Found', headers)
    return ['']

def get_method(environ):
    return environ['REQUEST_METHOD'].upper()

def mk_wsgi_application(msite):
    '''
    Create the WSGI application

    @param msite : mobile site
    @type  msite : mobilize.base.MobileSite

    @return      : WSGI application function
    @rtype       : function accepting (environ, start_response) arguments
    
    '''
    from httplib import HTTPConnection
    def application(environ, start_response):
        uri = environ['REQUEST_URI']
        if uri.startswith('/todesktop/'):
            return todesktop(environ, start_response, msite.fullsite)
        method = get_method(environ)
        environ['HTTP_ACCEPT_ENCODING'] = 'identity' # We need an uncompressed response
        req_body = None
        full_host, full_port = srchostport(environ)
        conn = HTTPConnection(full_host, full_port)
        if method in ('POST', 'PUT'):
            req_body = environ['wsgi.input'].read()
        request_headers = get_request_headers(environ)
        conn.request(method, uri, body=req_body, headers=request_headers)
        resp = conn.getresponse()
        src_resp_body = resp.read()
        status = '%s %s' % (resp.status, resp.reason)
        if not (mobilizeable(resp) and msite.has_match(uri)):
            # No matching template found, so pass through the source response
            start_response(status, resp.getheaders())
            return [src_resp_body]
        mobilized_body = str(msite.render_body(uri, src_resp_body))
        overrides = msite.response_overrides()
        overrides['content-length'] = str(len(mobilized_body))
        mobilized_resp_headers = get_response_headers(resp, environ, overrides)
        start_response(status, mobilized_resp_headers)
        return [mobilized_body]
    return application
