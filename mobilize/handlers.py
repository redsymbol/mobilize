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
    #: Headers to remove from the final response
    REMOVE_RESP_HEADERS = (
        'transfer-encoding', # What's returned to the client is not actually chunked.
        'content-location',  # Can confuse client browser in certain situations
        )
        
    def wsgi_response(self, msite, environ, start_response):
        reqinfo = httputil.RequestInfo(environ)
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
        http = httputil.get_http()
        request_overrides = msite.request_overrides(environ)
        request_overrides['X-MWU-Mobilize'] = '1'
        if msite.verboselog:
            log_headers('NEW: raw request headers', list(reqinfo.iterrawheaders()))
        request_headers = reqinfo.headers(request_overrides)
        if msite.verboselog:
            log_headers('modified request headers', request_headers)
        resp, src_resp_bytes = http.request(reqinfo.uri, method=reqinfo.method, body=reqinfo.body,
                                           headers=request_headers)
        if msite.verboselog:
            log_headers('raw response headers', resp, status=resp.status)
        charset = httputil.guess_charset(resp, src_resp_bytes, msite.default_charset)
        status = '%s %s' % (resp.status, resp.reason)
        for toremove in self.REMOVE_RESP_HEADERS:
            if toremove in resp:
                del resp[toremove]
        if httputil.mobilizeable(resp):
            src_resp_body = httputil.netbytes2str(src_resp_bytes, charset)
            final_body, final_resp_headers = self._final_wsgi_response(environ, msite, reqinfo, resp, src_resp_body)
        else:
            final_resp_headers = httputil.dict2list(resp)
            final_body = src_resp_bytes
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
    def __init__(self, template_name, components, params=None):
        '''
        ctor
        
        @param template_name : Template name (file)
        @type  template_name : str

        @param components    : Components of content elements to extract from full body
        @type  components    : list
        
        @param params        : Other template rendering parameters
        @type  params        : dict (str -> mixed)
        
        '''
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
        from lxml import html
        params = dict(self.params)
        if site_filters is None:
            site_filters = []
        if extra_params:
            params.update(extra_params)
        assert 'elements' not in params # Not yet anyway
        all_filters = list(site_filters) + self.mk_moplate_filters(params)
        doc = html.fromstring(full_body)
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
            'fullsite' : msite.fullsite,
            'request_path' : reqinfo.rel_uri,
            }
        final_body = self.render(src_resp_body, extra_params, msite.mk_site_filters(extra_params))
        response_overrides = msite.response_overrides(environ)
        response_overrides['content-length'] = str(len(final_body))
        final_resp_headers = httputil.get_response_headers(resp, environ, response_overrides)
        return final_body, final_resp_headers

class ToDesktop(Handler):
    '''
    Send the mobile request to the desktop URL

    Indented to be used where we're intentially not defining a mobile
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
        resp_headers = httputil.dict2list(resp)
        return src_resp_body, resp_headers
    
# Standard/reusable handler instances
todesktop = ToDesktop()
passthrough = PassThrough()
