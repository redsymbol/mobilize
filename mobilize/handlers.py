'''
Mobilize handlers

Extendable classes for handlers, including Moplate.

Also includes some standard instances that are generally useful and
reusable (e.g., todesktop, which is an instance of ToDesktop)

'''
from . import util
from . import httputil

class Handler:
    '''
    Handles a mobile page request

    This objects knows how to generate the HTTP response for a
    specific page on the mobile site.  It's a basis for more
    specialized services such as moplates.
    
    '''
    
    def wsgi_response(self, msite, environ, start_response):
        '''
        Create WSGI HTTP response

        @param msite          : The mobile site object
        @type  msite          : MobileSite

        @param environ        : WSGI environment
        @type  environ        : dict

        @param start_response : WSGI start_response
        @type  start_response : callable

        @return               : response body
        @rtype                : sequence of str
        
        '''
        assert False, 'subclass must implement'

class WebSourcer(Handler):
    '''
    A Handler that uses another web page as an HTTP source

    Subclasses must implement the _final_wsgi_response method.

    '''

    _source_uri_mapper = None

    def __init__(self, source_uri_mapper = None):
        '''
        ctor
        
        source_uri_mapper defines the mapping between incoming request
        URLs and the corresponding URL from the source, as
        encapsulated by the source_uri method of this class.  See that
        method's documentation for more info.

        @param source_uri_mapper : Specifies source URI mapping policy 
        @type  source_uri_mapper : mixed; see documention for self.source_uri
        
        
        '''
        self._source_uri_mapper = source_uri_mapper

    def source_rel_uri(self, requested_uri):
        '''
        Return the relative URI to fetch from the source site

        This method calculates the relative URI of the resource to
        fetch on the source site, based on the incoming request URI to
        the mobile site. The default case is to return the value of
        requested_uri unmodified, but you also can specify arbitrary
        transformation rules. Its behavior depends on the value of
        source_uri_mapper passed to the instance's constructor.

        If source_uri_mapper is not supplied, or is None, then the
        relative URI of the source is the same as for the incoming
        request.  In other words, source_uri will return the value of
        requested_uri.  For many websites this simple case is all you
        need.

        If source_uri_mapper is a string, this is used as the value of
        the relative URI in the source document, regardless of what
        request_url's value is.  Typically this will be used for a handler
        that is always routed from a specific URL.

        If source_uri_mapper is a callable, it must accept
        requested_uri as an argument, and return a modified URL value.

        Note: all references to URLs in this description are meant to
        be relative URLs, not absolute.

        @param requested_uri : Incoming relative URI
        @type  requested_uri : str

        @return : Relative URI to fetch from source
        @rtype  : str
        
        '''
        
        url = requested_uri
        if self._source_uri_mapper is not None:
            if callable(self._source_uri_mapper):
                url = self._source_uri_mapper(requested_uri)
            else:
                assert type(self._source_uri_mapper) is str
                url = self._source_uri_mapper
        return url

    def fromstring(self, body):
        '''
        @param body : body of html
        @type  body : str

        @return     : HTML element
        @rtype      : lxml.html.HtmlElement
        
        '''
        return _html_fromstring(body)
    
    def wsgi_response(self, msite, environ, start_response):
        reqinfo = httputil.RequestInfo(environ)
        for sechook in msite.sechooks():
            sechook.check_request(reqinfo)
        def log_headers(label, headers, **kw):
            from mobilize.log import mk_wsgi_log
            log = mk_wsgi_log(environ)
            msg = '%s (%s %s): %s' % (
                label,
                reqinfo.method,
                reqinfo.uri,
                str(headers),
                )
            for k, v in kw.items():
                msg += ', %s=%s' % (k, v)
            log(msg)
        http = msite.get_http()
        request_overrides = msite.request_overrides(environ)
        request_overrides['X-MWU-Mobilize'] = '1'
        if msite.verboselog:
            log_headers('NEW: raw request headers', list(reqinfo.iterrawheaders()))
        request_headers = reqinfo.headers(request_overrides)
        if msite.verboselog:
            log_headers('modified request headers', request_headers)
        source_uri = reqinfo.root_uri + self.source_rel_uri(reqinfo.rel_uri)
        resp, src_resp_bytes = http.request(source_uri, method=reqinfo.method, body=reqinfo.body,
                                           headers=request_headers)
        if msite.verboselog:
            log_headers('raw response headers', resp, status=resp.status)
        charset = httputil.guess_charset(resp, src_resp_bytes, msite.default_charset)
        status = '%s %s' % (resp.status, resp.reason)
        # Note that for us to mobilize the response, both the request
        # AND the response must be "mobilizeable".
        if reqinfo.mobilizeable and httputil.mobilizeable(resp):
            src_resp_body = httputil.netbytes2str(src_resp_bytes, charset)
            final_body, final_resp_headers = self._final_wsgi_response(environ, msite, reqinfo, resp, src_resp_body)
        else:
            final_resp_headers = httputil.dict2list(resp)
            final_body = src_resp_bytes
        final_resp_headers = _postprocess_response_headers(final_resp_headers, msite.sechooks())
        if msite.verboselog:
            log_headers('final resp headers', final_resp_headers)
        start_response(status, final_resp_headers)
        return [final_body]

    def _final_wsgi_response(self, environ, msite, reqinfo, resp, src_resp_body):
        '''
        Create the final WSGI response body and headers

        This method must return a pair: the final response body as a
        string (not bytes), and the final response headers.  The
        response headers are in the form of a list of (key, value)
        pairs.

        @param environ       : WSGI environment
        @type  environ       : dict

        @param msite         : Mobile site
        @type  msite         : mobilize.base.MobileSite

        @param reqinfo       : request info
        @type  reqinfo       : mobilize.httputil.RequestInfo

        @param resp          : Response from source
        @type  resp          : ? from httplib2

        @param src_resp_body : Decoded body of response from source
        @type  src_resp_body : str
        
        @return              : tuple(final_body, final_resp_headers)
        @rtype               : tuple of (str, list of (str, str) pairs)
        
        '''
        assert False, 'subclass must implement'

    
class Moplate(WebSourcer):
    '''
    A kind of mobile webpage template with magical powers

    A moplate represents a transformation, from a source (desktop
    page's) body, to the body of the corresponding mobile page.
    Typically the moplate can be applied to a group of pages with
    similar DOM structure.

    components is an ordered list of mobilize page components (see
    L{mobilize.components}), identifying content elements in the
    mobile page body, some of which are based on content from the
    desktop page.  From this, a list of HTML snippets will be made
    available to the template as the "elements" attribute of the
    parameter dictionary.

    Because of the magical "elements" parameter, the supplied params
    cannot have a key of that name.

    Currently this is intended to be used as a base class. Subclasses
    must implement at least self._render().

    '''
    def __init__(self, template_name, components, params=None, **kw):
        '''
        ctor
        
        @param template_name : Template name (file)
        @type  template_name : str

        @param components    : Components of content elements to extract from full body
        @type  components    : list
        
        @param params        : Other template rendering parameters
        @type  params        : dict (str -> mixed)
        
        '''
        super(Moplate, self).__init__(**kw)
        self.template_name = template_name
        self.components = components
        if params:
            self.params = dict(params)
        else:
            self.params = {}
        assert 'elements' not in self.params, '"elements" is reserved/magical in mobile template params.  See Moplate class documention'

    def render(self, full_body, extra_params=None, site_filters=None):
        '''
        Render the moplate for a particular HTML document body

        extra_params is a dictionary of extra parameters for just this
        rendering, which can be used to override any of the default
        template parameters as well.
        
        @param full_body    : Source HTML - body of full website's page
        @type  full_body    : str

        @param extra_params : Extra template parameters to use for this rendering
        @type  extra_params : dict
        
        @param site_filters : Mobile site filters to apply
        @type  site_filters : list of filter callables
        
        @return             : Rendered mobile page body
        @rtype              : str

        '''
        doc = self.fromstring(full_body)
        params = _rendering_params(doc, [self.params, extra_params])
        assert 'elements' not in params # Not yet anyway
        if site_filters is None:
            site_filters = []
        all_filters = list(site_filters) + self.mk_moplate_filters(params)
        for ii, component in enumerate(self.components):
            if component.extracted:
                component.extract(doc)
                component.process(util.idname(ii), all_filters)
        params['elements'] = [component.html() for component in self.components]
        return self._render(params)

    def _render(self, params):
        '''
        Implementation-dependent final rendering

        Subclasses should implement this.

        @param params : Template parameters
        @type  params : dict (str -> mixed)

        @return       : Rendered mobile page body
        @rtype        : str
        
        '''
        assert False, 'must be implemented in subclass'

    def mk_moplate_filters(self, params):
        '''
        Create moplate-level extra filters

        Builds a list of filters specific to this moplate, that will
        be applied to the extracted content of every mobile page.

        This method is a hook that can be altered by subclasses.  By
        default, it returns an empty list.  The params argument can be
        used to generate filters specific to the parameter set.

        @param params : Moplate template parameters
        @type  params : dict

        @return       : Filters
        @rtype        : list of callable
        
        '''
        return []

    def _final_wsgi_response(self, environ, msite, reqinfo, resp, src_resp_body):
        extra_params = {
            'fullsite'     : msite.fullsite,
            'request_path' : reqinfo.rel_uri,
            'todesktop'    : _todesktoplink(reqinfo.protocol, msite.fullsite, reqinfo.rel_uri),
            }
        final_body = self.render(src_resp_body, extra_params, msite.mk_site_filters(extra_params))
        response_overrides = msite.response_overrides(environ)
        response_overrides['content-length'] = str(len(final_body))
        final_resp_headers = httputil.get_response_headers(resp, environ, response_overrides)
        
        # convert type of final_body from type django.utils.safestring.SafeUnicode to network-friendly bytes
        # (Someday if/when we are no longer always using Django templates, need to omit or move this conversion.)
        from django.utils.safestring import SafeUnicode
        assert SafeUnicode == type(final_body), type(final_body).__name__
        final_body = bytes(final_body, 'utf-8')

        assert type(final_body) is bytes
        return final_body, final_resp_headers

class ToDesktop(Handler):
    '''
    Send the mobile request to the desktop URL

    Intended to be used where we're intentially not defining a mobile
    view for certain URLs, sending the visitor to the desktop site.

    TODO: what if the device detection redirects them here?  Could get in a redirect loop
    
    '''

    #: HTTP response status
    status = '302 FOUND'
    
    def wsgi_response(self, msite, environ, start_response):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ)
        to = 'http://{}{}'.format(msite.fullsite, reqinfo.rel_uri)
        start_response(self.status, [('location', to)])
        return ['<html><body><a href="{}">Go to page</a>'.format(to)]

class ToDesktopPermanent(ToDesktop):
    '''
    Operates similarly to ToDesktop, but with a 301 permanent redirect.
    
    '''
    
    status = '301 MOVED PERMANENTLY'

class PassThrough(WebSourcer):
    '''
    Pass through the response from the desktop source
    '''
    def _final_wsgi_response(self, environ, msite, reqinfo, resp, src_resp_body):
        # TODO: if msite.verboselog, log that we're passing through
        return _passthrough_response(src_resp_body, resp)

class SecurityBlock(Handler):
    '''
    Block normal request and response

    This is meant to convey that the http request is effectively being
    dropped for security reasons.  It's useful, for example, in the
    context of a secure mobile web server, to prevent exploitation of
    a hole in the source/desktop site on the client's web server.
    '''
    status = '403 Forbidden'

    def wsgi_response(self, msite, environ, start_response):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ)
        message = '''<html><head><title>{status}</title></head><body>
<h1>{status}</h1>
The request to {rel_uri} is forbidden as a security measure.'''.format(status=self.status, rel_uri = reqinfo.rel_uri)
        start_response(self.status, [])
        return [message]

# Standard/reusable handler instances
todesktop = ToDesktop()
passthrough = PassThrough()
securityblock = SecurityBlock()

# Supporting code

def _passthrough_response(body, resp):
    resp_headers = httputil.dict2list(resp)
    return body, resp_headers

def _html_fromstring(body):
    '''
    Used by, for example, WebSourcer.fromstring.  Separated out here for easier testing

    TODO: write these purported tests
    '''
    from lxml import html
    try:
        return html.fromstring(body)
    except ValueError:
        # Does this have an encoding declaration?
        dec_key = '<?xml'
        if body[:len(dec_key)].lower() == dec_key:
            # yes, it does!
            body = body[body.find('\n'):]
            return html.fromstring(body)
        # No it doesn't, so let the error propagate
        raise

def _todesktoplink(protocol, fullsite, rel_uri):
    '''
    Calculate the "todesktop" link string

    @param protocol : protocol (http or https)
    @type  protocol : str

    @param fullsite : Desktop (full) site domain, and port of applicable
    @type  fullsite : str
    
    @return         : rel_uri
    @rtype          : The relative URI

    @return         : The link the mobile user can follow to view the desktop version of the page
    @rtype          : str
    
    '''
    link = '{}://{}{}'.format(protocol, fullsite, rel_uri)
    if '?' in rel_uri:
        link += '&'
    else:
        link += '?'
    link += 'mredir=0'
    return link

def _rendering_params(doc, paramdictlist):
    params = {}
    for paramdict in paramdictlist:
        if type(paramdict) is dict:
            params.update(paramdict)
    def mk_findtext(xpath):
        '''
        Creates a no-argument callable that extracts the text content of a single element in the source document

        This will operate on the *first* element the supplied xpath
        expression finds, so normally you will want to use it for
        unique page elements (e.g., ".//title").

        @param tag : Xpath of element
        @type  tag : str

        @return    : Text content of said element if found, else empty string
        @rtype     : str
        
        '''
        def findtext():
            elem = doc.find(xpath)
            if elem is not None:
                return getattr(elem, 'text', '')
            return ''
        return findtext
    source_params = {
        'title'   : mk_findtext('.//title'),
        'heading' : mk_findtext('.//h1'),
        }
    for param, finder in source_params.items():
        if param not in params:
            params[param] = finder()
    return params

def _postprocess_response_headers(headers, hooks):
    from mobilize.util import isscalar
    removed = (
        'transfer-encoding', # What's returned to the client is not actually chunked.
        )
    def expand(items):
        for k, v in items:
            if isscalar(v):
                yield k, v
            else:
                for _v in v:
                    yield k, _v
    def modify(header, value):
        import re
        if 'location' == header:
            # Development hook
            if re.match(r'http://[^/]*:2443/', value):
                value = value.replace(':2443/', ':2280/')
        return (header, value)
    modified = [modify(header, value)
                for header, value in expand(headers)
                if header not in removed]
    for hook in hooks:
        modified = hook.response(modified)
    return modified

