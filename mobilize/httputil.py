# Copyright 2010-2011 Mobile Web Up. All rights reserved.
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

def _get_root_uri(environ, use_defined_fullsite=True):
    '''
    Get the root URI of the incoming request

    The "root URI" is defined as the full url with the request path
    trunacted.  So the root URI of
    "http://example.com/foo/bar?answer=42" is simply
    "http://example.com".

    @param environ : wsgi environment
    @type  environ : quackslike(dict)

    @return : root URI
    @rtype  : str
    
    '''
    proto = environ.get('wsgi.url_scheme', 'http')
    host, port = srchostport(environ, use_defined_fullsite)
    assert type(port) is int, type(port)
    uri = '%s://%s' % (proto, host)
    stdport = PROTOMAP.get(proto, False)
    if stdport and port != stdport:
        uri += ':' + str(port)
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

    @return : True iff the response is mobilizeable
    @rtype  : bool
    
    '''
    is_mob = False
    contenttype = resp.get('content-type', '')
    if 'xml' in contenttype or 'html' in contenttype:
        is_mob = True
    return is_mob

def srchostport(environ, use_defined_fullsite=True):
    '''
    Calculate/choose source hostname and port

    environ is meant to be the WSGI environment dictionary,
    expected to contain the following keys:

      MWU_OTHER_DOMAIN
      SERVER_PORT

    This function returns a tuple of hostname and port, so you will
    probably want to invoke it like:

      host, port = srchostport(wsgi_environ)

    @param param : WSGI environment
    @type  param : dict

    @return      : Source host and port
    @rtype       : tuple(str, int)
    
    '''
    hostkey = 'MWU_OTHER_DOMAIN' if use_defined_fullsite else 'SERVER_NAME'
    full_host = environ[hostkey]
    if ':' in full_host:
        full_host, full_port = full_host.split(':')
        full_port = int(full_port)
    else:
        requesting_port = int(environ['SERVER_PORT'])
        # TODO: these are development hooks.  Need to fix
        devremap = {
            2280 : 80,
            2443 : 443,
            }
        if requesting_port in devremap:
            full_port = devremap[requesting_port]
        else:
            full_port = requesting_port
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

    Note in most cases, handlers and other code should use the
    get_http method of a MobileSite instance, rather than using this
    function directly, in case the desktop source of a particular
    mobile site needs further customization.

    @return : http object
    @rtype  : httplib2.Http
    
    '''
    from httplib2 import Http
    http = Http()
    http.follow_redirects = False
    http.force_exception_to_status_code = True
    return http

def dict2list(d):
    '''
    Convert the type of dictionary we use to represent http headers into a list of (header, value) pairs

    The keys of this dict are strings: header names.  The value can be either a string, or an iterable of strings
    '''
    def items(header, value):
        from mobilize.util import isscalar
        if isscalar(value):
            yield (header, str(value))
        else:
            for oneval in value:
                yield (header, str(oneval))
    return [item for header, value in d.items() for item in items(header, value)]

class QueryParams(dict):
    '''
    Request query parameters and their values

    This dictionary-like data structure has keys of unescaped query string parameters.
    The values are lists

    '''
    def __init__(self, querystring=''):
        from urllib.parse import unquote
        for pair in querystring.split('&'):
            if '' == pair:
                continue
            try:
                k, v = map(unquote, pair.split('='))
            except ValueError:
                k = unquote(pair)
                v = None
            if k not in self:
                self[k] = []
            if v is not None:
                self[k].append(v)
    
class RequestInfo:
    '''
    Encapsulates information about an incoming HTTP request.

    This is for the request directly from the client, prior to any handler.

    Properties:
      body         : The request body, or None if not applicable
      method       : the request method: 'GET', 'POST', etc.
      mobilizeable : whether the request is mobilizeable or not
      protocol     : request protocol (http, https, etc.)
      queryparams  : query params (a QueryParams instance)
      querystring  : query string
      rel_uri      : the relative request URI
      root_uri     : the request URI sans the request path
      uri          : full request URI

    '''
    _rawheaders = None
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
        self.querystring = wsgienviron['QUERY_STRING']
        self.queryparams = QueryParams(self.querystring)
        self.root_uri = _get_root_uri(wsgienviron)
        self.rel_uri = get_rel_uri(wsgienviron)
        self.uri = self.root_uri + self.rel_uri
        self.protocol = wsgienviron['wsgi.url_scheme']
        self.mobilizeable = wsgienviron.get('HTTP_X_REQUESTED_WITH', None) != 'XMLHttpRequest'

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
        from .headers.request import request_additions
        headers = {}
        for header, value in self.rawheaders().items():
            # We want to preserve the Camel-Casing of the header names
            # we're about to send, because who knows what web server
            # or gateway will randomly go crazy if we don't.  But for
            # consistency and simplicity, related data
            # (e.g. overrides) are keyed by their fully-lowercased
            # equivalents.  These two ideas are labeled "header" and
            # "headerkey" respectively.
            headerkey = header.lower()
            if headerkey in overrides:
                # An override has been specified for this request header
                override = overrides[headerkey]
                if isinstance(override, collections.Callable):
                    newvalue = override(self.wsgienviron, value)
                else:
                    newvalue = override
            else:
                # No override defined, so check whether there is a stock transformer
                xformer = get_request_xform(headerkey, self.method)
                newvalue = xformer(self.wsgienviron, value)
            headers[header] = newvalue
        for header, xformer in request_additions:
            if header not in headers:
                headerkey = header.lower()
                headers[header] = xformer(self.wsgienviron, None)
        return headers

    def rawheaders(self):
        if self._rawheaders is None:
            self._rawheaders = dict(self.iterrawheaders())
        return self._rawheaders

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

def _headbytes(html_bytes):
    '''fetch the portion of a document before the opening of the body element'''
    def findpos(key):
        match = re.search(key, html_bytes, re.I)
        if match is None:
            return -1
        return match.start()
    start = findpos(b'<head')
    end = findpos(b'<body')
    return html_bytes[start:end].strip() if (start >= 0 and end >= 0) else b''

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
    # That means either an html5 'meta charset="..."', or html4 'meta http-equiv="content-type"'
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

def netbytes2str(rawbytes, charset):
    '''
    Create a lxml-friendly Python string from the raw HTTP response

    This is necessary because httplib2.Http.request returns a response
    body of type bytes, but we want to feed a correctly decoded string
    with properly handled newlines, etc. to lxml.

    @param rawbytes : The response body from the network
    @type  rawbytes : bytes

    @param charset : Character encoding of rawbytes
    @type  charset : str

    @return : lxml-friendly Python string
    @rtype  : str

    '''
    return rawbytes.replace(b'\r\n', b'\n').decode(charset)

def mk_wsgi_application(msite):
    '''
    Create the WSGI application

    @param msite : mobile site
    @type  msite : mobilize.base.MobileSite

    @return      : WSGI application function
    @rtype       : function accepting (environ, start_response) arguments
    
    '''
    def application(environ, start_response):
        from mobilize.handlers import (
            passthrough,
            securityblock,
            )
        from mobilize.secure import DropResponseSignal
        from mobilize.exceptions import NoMatchingHandlerException
        def response(_handler):
            return _handler.wsgi_response(msite, environ, start_response)
        try:
            handler = msite.handler_map.get_handler_for(get_rel_uri(environ))
        except NoMatchingHandlerException:
            handler = passthrough
        
        try:
            return response(handler)
        except DropResponseSignal:
            return response(securityblock)
        except Exception as ex:
            # Something went fatally wrong, so attempt to fallback on the passthrough handler.
            # TODO: log exception
            if not msite.is_production:
                # Don't mask the problem in development mode
                raise
            if handler == passthrough:
                # Nothing to do here...
                raise
            # TODO: Sometimes this will block, under conditions I haven't characterized yet.  Maybe when start_response is already invoked?
            return response(passthrough)
    return application

#: HTTP status codes, mapping numbers (int's) to the full string response. e.g., HTTP_STATUSES[302] == '302 Found'
HTTP_STATUSES = dict((code, '{} {}'.format(code, message))
                     for code, message in {
        301 : 'Moved Permanently',
        302 : 'Found',
        403 : 'Forbidden',
        }.items())

#: Mapping of protocol port numbers (int) to names (str)
PORTMAP = {
    21  : 'ftp',
    80  : 'http',
    115 : 'sftp',
    443 : 'https',
    }

#: Mapping of protocol port names (str) to numbers (int).  Just the inverse of PORTMAP
PROTOMAP = dict((v, k) for k, v in PORTMAP.items())

assert set(PORTMAP.keys()) == set(PROTOMAP.values())
assert set(PORTMAP.values()) == set(PROTOMAP.keys())

class SourceUriMapper:
    '''
    Base class for source URI remappings

    Instances must be callable, accepting requested_uri as an
    argument, and returning the new value.
    
    Usable as the value of the source argument in the Moplate constructor.
    
    '''
    def __call__(self, requested_uri):
        '''
        @param requested_uri : Incoming URI
        @type  requested_uri : str

        @return              : Source URI
        @rtype               : str
        
        '''
        assert False, 'subclass must implement'

class RequestedUriModifier(SourceUriMapper):
    def __init__(self, new_rel_uri):
        '''
        @param new_rel_uri : New relative URI
        @type  new_rel_uri : str
        
        '''
        self.new_rel_uri = new_rel_uri
        
    
class NewBaseUri(RequestedUriModifier):
    '''
    Rewrite the base URI, preserving GET params

    This is useful when you don't want to just replace the incoming
    uri with a different static value, because you want to keep any
    GET parameters.
    
    '''
    def __call__(self, requested_uri):
        '''
        @param requested_uri : Incoming URI
        @type  requested_uri : str

        @return              : Source URI
        @rtype               : str
        
        '''
        uri = self.new_rel_uri
        pos = requested_uri.find('?')
        if pos > -1:
            uri += requested_uri[pos:]
        return uri

class ForceUri(RequestedUriModifier):
    '''
    Hard remaps to a new static source URI, discarding GET parameters
    '''
    def __call__(self, requested_uri):
        return self.new_rel_uri

def is_absolute_url(url):
    protocols = {
        'http',
        'https',
        'ftp',
        }
    is_abs = False
    for protocol in protocols:
        if url.startswith(protocol + '://'):
            is_abs = True
            break
    return is_abs

def replace_domain(url, old_domain, new_domain):
    '''
    Swap out the domain in a URL.

    If the starting domain is different from what's supplied, the url is unchanged.
    
    '''
    re_pattern = r'^\w+://(?P<domain>{domain})/?.*$'.format(domain=old_domain)
    match = re.search(re_pattern, url)
    if match:
        start, end = match.start('domain'), match.end('domain')
        url = url[:start] + new_domain + url[end:]
    return url
