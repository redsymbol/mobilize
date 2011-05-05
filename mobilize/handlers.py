'''
Mobilize handlers

Extendable classes for handlers, including Moplate.

Also includes some standard instances that are generally useful and
reusable (e.g., todesktop, which is an instance of ToDesktop)

'''
from . import util

class Handler(object):
    '''
    Handles a mobile page request

    This objects knows how to generate the HTTP response for a
    specific page on the mobile site.  It's a basis for more
    specialized services such as moplates.
    
    '''
    
    def wsgiresponse(self, msite, environ, start_response):
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
    A Handler that uses another web page as a source

    '''
    
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

        @param components     : Components of content elements to extract from full body
        @type  components     : list
        
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

    def get_params(self):
        '''
        Get the current template parameters

        @return : current parameters
        @rtype  : dict
        
        '''
        return self.params

    def wsgiresponse(self, msite, environ, start_response):
        from mobilize import httputil
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
        if reqinfo.method in ('POST', 'PUT'):
            reqinfo.body = environ['wsgi.input'].read()
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
            log_headers('raw response headers', resp, status=status)
        charset = httputil.guess_charset(resp, src_resp_bytes, msite.default_charset)
        src_resp_body = src_resp_bytes.decode(charset)
        status = '%s %s' % (resp.status, resp.reason)
        if httputil.mobilizeable(resp):
            extra_params = {
                'fullsite' : msite.fullsite,
                'request_path' : reqinfo.rel_uri,
                }
            mobilized_body = self.render(src_resp_body, extra_params, msite.mk_site_filters(extra_params))
            response_overrides = msite.response_overrides(environ)
            response_overrides['content-length'] = str(len(mobilized_body))
            if 'transfer-encoding' in resp:
                del resp['transfer-encoding'] # Currently what's returned to the client is not actually chunked.
            mobilized_resp_headers = httputil.get_response_headers(resp, environ, response_overrides)
            if msite.verboselog:
                log_headers('modified resp headers', mobilized_resp_headers)

            final_body = mobilized_body
            final_resp_headers = mobilized_resp_headers
        else:
            final_resp_headers = httputil.dict2list(resp)
            final_body = src_resp_bytes
        start_response(status, final_resp_headers)
        return [final_body]

class ToDesktop(Handler):
    '''
    Send the mobile request to the desktop URL

    Indented to be used where we're intentially not defining a mobile
    view for certain URLs, sending the visitor to the desktop site.

    TODO: what if the device detection redirects them here?  Could get in a redirect loop
    
    '''
    status = '302 FOUND'
    def wsgiresponse(self, msite, environ, start_response):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ)
        to = 'http://{}{}'.format(msite.fullsite, reqinfo.rel_uri)
        start_response(self.status, [('location', to)])
        return ['<html><body><a href="{}">Go to page</a>'.format(to)]

class ToDesktopPermanent(Handler):
    '''
    Operates similarly to ToDesktop, but with a 301 permanent redirect.
    
    '''
    status = '301 MOVED PERMANENTLY'

class PassThrough(WebSourcer):
    '''
    Pass through the response from the desktop source
    '''
    def wsgiresponse(self, msite, environ, start_response):
        from mobilize import httputil
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
        if reqinfo.method in ('POST', 'PUT'):
            reqinfo.body = environ['wsgi.input'].read()
        request_overrides = msite.request_overrides(environ)
        request_overrides['X-MWU-Mobilize'] = '1'
        if msite.verboselog:
            log_headers('NEW: raw request headers', list(reqinfo.iterrawheaders()))
        request_headers = reqinfo.headers(request_overrides)
        if msite.verboselog:
            log_headers('modified request headers', request_headers)
        resp, src_resp_bytes = http.request(reqinfo.uri, method=reqinfo.method, body=reqinfo.body,
                                           headers=request_headers)
        charset = httputil.guess_charset(resp, src_resp_bytes, msite.default_charset)
        src_resp_body = src_resp_bytes.decode(charset)
        status = '%s %s' % (resp.status, resp.reason)
        resp_headers = httputil.dict2list(resp)
        if msite.verboselog:
            log_headers('raw response headers [passthru]', resp_headers)
        start_response(status, resp_headers)
        return [src_resp_bytes]

# Standard/reusable handler instances
todesktop = ToDesktop()
passthrough = PassThrough()
