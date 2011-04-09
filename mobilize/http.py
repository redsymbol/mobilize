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
    return environ['REQUEST_URI']

def get_uri(environ, proto='http'):
    host, port = srchostport(environ)
    assert type(port) is int, type(port)
    rel_uri = environ['REQUEST_URI']
    uri = '%s://%s' % (proto, host)
    if 80 != port:
        uri += ':' + str(port)
    uri += rel_uri
    return uri

def get_http():
    from httplib2 import Http
    http = Http()
    http.follow_redirects = False
    return http

def dict2list(d):
    return list((header, value) for header, value in d.items())

class RequestInfo(object):
    def __init__(self, wsgienviron):
        self.wsgienviron = wsgienviron
        self.method = self.wsgienviron['REQUEST_METHOD'].upper()
        self.body = None
        self.uri = get_uri(self.wsgienviron)
        self.rel_uri = get_rel_uri(self.wsgienviron)

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

def mk_wsgi_application(msite, verboselog=False):
    '''
    Create the WSGI application

    @param msite : mobile site
    @type  msite : mobilize.base.MobileSite

    @return      : WSGI application function
    @rtype       : function accepting (environ, start_response) arguments
    
    '''
    def application(environ, start_response):
        from mobilize.log import mk_wsgi_log
        log = mk_wsgi_log(environ)
        reqinfo = RequestInfo(environ)
        def log_headers(label, headers, **kw):
            msg = '%s (%s %s): %s' % (
                label,
                reqinfo.method,
                reqinfo.uri,
                str(headers),
                )
            for k, v in kw.items():
                msg += ', %s=%s' % (k, v)
            log(msg)
        http = get_http()
        if reqinfo.method in ('POST', 'PUT'):
            reqinfo.body = environ['wsgi.input'].read()
        request_overrides = msite.request_overrides(environ)
        request_overrides['X-MWU-Mobilize'] = '1'
        if verboselog:
            log_headers('NEW: raw request headers', list(reqinfo.iterrawheaders()))
        request_headers = reqinfo.headers(request_overrides)
        if verboselog:
            log_headers('modified request headers', request_headers)
        resp, src_resp_body = http.request(reqinfo.uri, method=reqinfo.method, body=reqinfo.body,
                                           headers=request_headers)
        status = '%s %s' % (resp.status, resp.reason)
        if not (mobilizeable(resp) and msite.has_match(reqinfo.rel_uri)):
            # No matching template found, so pass through the source response
            resp_headers = dict2list(resp)
            if verboselog:
                log_headers('raw response headers [passthru]', resp_headers)
            start_response(status, resp_headers)
            return [src_resp_body]
        if verboselog:
            log_headers('raw response headers', resp, status=status)
        mobilized_body = msite.render_body(reqinfo.rel_uri, str(src_resp_body))
        response_overrides = msite.response_overrides(environ)
        response_overrides['content-length'] = str(len(mobilized_body))
        if 'transfer-encoding' in resp:
            del resp['transfer-encoding'] # Currently what's returned to the client is not actually chunked.
        mobilized_resp_headers = get_response_headers(resp, environ, response_overrides)
        if verboselog:
            log_headers('modified resp headers', mobilized_resp_headers)
        start_response(status, mobilized_resp_headers)
        return [mobilized_body]
    return application
