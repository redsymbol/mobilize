# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Mobilize handlers

Extendable classes for handlers, including Moplate.

Also includes some standard instances that are generally useful and
reusable (e.g., todesktop, which is an instance of ToDesktop)

'''
import re
from mobilize.log import logger
from . import util
from . import httputil

class Handler:
    '''
    Handles a mobile page request

    This objects knows how to generate the HTTP response for a
    specific page on the mobile site.  It's a basis for more
    specialized services such as moplates.
    
    '''
    
    #: Optional name/label for this handler instance.  Used for debug logging.
    _name = None
    def get_name(self):
        if self._name is None:
            return '{} instance'.format(self.__class__.__name__)
        return self._name
    def set_name(self, value):
        self._name = value
    name = property(get_name, set_name)
    
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

    def handler_log(self, log):
        pass

class WebSourcer(Handler):
    '''
    A Handler that uses another web page as an HTTP source

    Subclasses must implement the _final_wsgi_response method.

    '''

    _source = None

    def __init__(self, source = None, **kw):
        '''
        ctor
        
        source defines the policy mapping between incoming request
        URLs and the corresponding URL from the source.  Normally,
        this is just going to be the default value of None, indicating
        that the requested relative URL is the same as the relative
        URL on the source.  Arbitrary alternatives are possible, as
        encapsulated by the source_url method of this class. See that
        method's documentation for more info.

        @param source : Specifies source URL mapping policy 
        @type  source : mixed; see documention for self.source_url

        '''
        super().__init__(**kw)
        from mobilize.httputil import NewBaseUrl
        if type(source) is str:
            source = NewBaseUrl(source)
        assert source is None or callable(source), source
        self._source = source

    def source_rel_url(self, requested_url):
        '''
        Return the relative URL to fetch from the source site

        This method calculates the relative URL of the resource to
        fetch on the source site, based on the incoming request URL to
        the mobile site. The default case is to return the value of
        requested_url unmodified, but you also can specify arbitrary
        transformation rules. Its behavior depends on the value of
        source passed to the instance's constructor.

        If source is not supplied, or is None, then the relative URL
        of the source is the same as for the incoming request.  In
        other words, source_url will return the value of
        requested_url.  For many websites this simple case is all you
        need.

        Otherwise, source must be a SourceUrlMapper instance (or quack
        like one - see below).  As a special case
        exception/convenience/shortcut, if source is a string, an
        instance of NewBaseUrl (with source as an argument) will be
        used instead.
        
        Source must be a callable that accepts requested_url as an
        argument, and return a modified URL value. SourceUrlMapper
        objects meet this interface, though any callable that behaves
        this way can be used instead.

        Note: all references to URLs in this description are meant to
        be relative URLs, not absolute.

        @param requested_url : Incoming relative URL
        @type  requested_url : str

        @return              : Relative URL to fetch from source
        @rtype               : str
        
        '''
        
        url = requested_url
        if self._source is not None:
            url = self._source(requested_url)
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
        '''
        Generate the WSGI response

        FAKING HEAD REQUESTS

        According to HTTP 1.1, HTTP HEAD requests are supposed to
        elicit the exact same response headers as a GET request, with
        an empty response body.  But some real-world web servers don't
        follow this, and may return a 500 or some other error.  This
        has affected our uptime monitoring for at least one client,
        since the third-party monitoring we use checks the server via
        an HTTP HEAD request to the home page.

        To deal with this, we fake such HEAD requests by (1)
        converting them to a GET request; (2) discarding the response
        body; and (3) adding an X-MWU-Info response header describing
        what we have done.

        TODO: Have this disablable by the msite, controlled by a boolean setting in defs.py

        @param msite          : Mobile site
        @type  msite          : MobileSite
        
        @param environ        : WSGI environment
        @type  environ        : dict
        
        @param start_response : WSGI start_response callable
        @type  start_response : callable
        
        @return               : Final body components
        @rtype                : list of str
        
        '''
        from mobilize.log import format_headers_log
        logger.info('Matching moplate: {}'.format(self.name))
        reqinfo = httputil.RequestInfo(environ)
        for sechook in msite.sechooks():
            sechook.check_request(reqinfo)
        def do_fake_head_req(_msite, _reqinfo):
            return 'HEAD' == _reqinfo.method and '/' == _reqinfo.rel_url
        fakeable_head_req = do_fake_head_req(msite, reqinfo)
        if fakeable_head_req:
            reqinfo.method = 'GET'
        http = msite.get_http()
        request_overrides = msite.request_overrides(environ)
        logger.info(format_headers_log('NEW: raw request headers', reqinfo, list(reqinfo.iterrawheaders())))
        request_headers = reqinfo.headers(request_overrides)
        logger.info(format_headers_log('modified request headers', reqinfo, request_headers))
        source_url = reqinfo.root_url + self.source_rel_url(reqinfo.rel_url)
        resp, src_resp_bytes = http.request(source_url, method=reqinfo.method, body=reqinfo.body,
                                           headers=request_headers)
        if fakeable_head_req:
            src_resp_bytes = b''
        logger.info(format_headers_log('raw response headers', reqinfo, resp, status=resp.status))
        charset = httputil.guess_charset(resp, src_resp_bytes, msite.default_charset)
        status = '%s %s' % (resp.status, resp.reason)
        # Note that for us to mobilize the response, both the request
        # AND the response must be "mobilizeable".
        if reqinfo.mobilizeable and httputil.mobilizeable(resp):
            src_resp_body = httputil.netbytes2str(src_resp_bytes, charset)
            final_body, final_resp_headers = self._final_wsgi_response(environ, msite, reqinfo, resp, src_resp_body)
        else:
            # TODO: must apply response overrides, at least for 301/302 redirs for one specific client
            final_resp_headers = httputil.dict2list(resp)
            final_body = src_resp_bytes
        final_resp_headers = msite.postprocess_response_headers(final_resp_headers, resp.status)
        assert type(final_resp_headers) == list
        if fakeable_head_req:
            final_resp_headers.append(('X-MWU-Info', 'Faked HEAD request as GET on source server'))
        logger.info(format_headers_log('final resp headers', reqinfo, final_resp_headers))
        # TODO: if the next line raises a TypeError, catch it and log final_resp_headers in detail (and everything else while we're at it)
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

    '''
      
    DEFAULT_TEMPLATE_NAMES = [
        'base.html',
        'globalbase.html',
        ]

    def __init__(self,
                 components,
                 params          = None,
                 template        = None,
                 name            = None,
                 imgsubs         = None,
                 template_loader = None,
                 **kw):
        '''
        ctor

        components is an ordered list of mobilize page components (see
        L{mobilize.components}), identifying content elements in the
        mobile page body, some of which are based on content from the
        desktop page.  From this, a list of HTML snippets will be made
        available to the template as the "elements" attribute of the
        parameter dictionary.

        The params field is for a starting set of template parameters
        for final rendering.  It is optional, defaulting to an empty
        dict, and there are ways to add to this set later on.  It MUST
        NOT contain a key named "elements", as that is reserved for
        later use; the ctor will check double check this for you, so
        if you accidentally put it in, you'd get an immediate runtime
        error.

        template can be either a string, or an instance of
        jinja2.Template.  If the former, it's assumed to be the name
        of a template to load from TEMPLATE_DIRS.
        
        The imgsubs parameter can be used to specify image URL
        substitutions specific to this moplate.  If provided, a
        filters.imgsubs filter will be applied to all moplate components
        with the indicated URL substitutions.

        Because of the magical "elements" parameter, the supplied params
        cannot have a key of that name.

        @param components      : Components of content elements to extract from full body
        @type  components      : list
        
        @param params          : Starting set of rendering parameters
        @type  params          : dict (str -> mixed); no "elements" key allowed

        @param template        : Template to use
        @type  template        : str, or instance of jinja2.Template

        @param name            : Human-readable name or label for this moplate
        @type  name            : str
        
        @param imgsubs         : Image URL substitutions
        @type  imgsubs         : dict: str -> str

        @param template_loader : Alternative template loader to use
        @type  template_loader : mobilize.templates.TemplateLoader
        
        '''
        from jinja2 import Template
        if template_loader is None:
            template_loader = self.default_template_loader()
        if template is None:
            template = self.DEFAULT_TEMPLATE_NAMES
        if not isinstance(template, Template):
            template = template_loader.get_template(template)
        assert isinstance(template, Template), type(template)
        logger.debug('Moplate {} using template named "{}"'.format(name, template.name))
        super().__init__(**kw)
        self.template = template
        self.components = components
        if params:
            self.params = dict(params)
        else:
            self.params = {}
        assert 'elements' not in self.params, '"elements" is reserved/magical in mobile template params.  See Moplate class documention'
        self.imgsubs = imgsubs

    def default_template_loader(self):
        '''
        Get the default template loader for this moplate

        Originally created as a useful testing hook.

        @return : template loader
        @rtype  : mobilize.templates.TemplateLoader
        
        '''
        from mobilize.templates import TemplateLoader
        return TemplateLoader()
    
    def render(self, full_body, extra_params=None, site_filters=None, reqinfo=None):
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
        if '' == full_body:
            rendered = ''
        else:
            rendered = self._render_str(full_body, extra_params, site_filters, reqinfo)
        return rendered
    
    def _render_str(self, full_body, extra_params, site_filters, reqinfo):
        '''
        Workhorse for render() method
        '''
        assert '' != full_body
        doc = self.fromstring(full_body)
        params = _rendering_params(doc, [self.params, extra_params])
        assert 'elements' not in params # Not yet anyway
        if site_filters is None:
            site_filters = []
        all_filters = self.mk_moplate_filters(params) + list(site_filters)
        components = [c for c in self.components
                      if c.relevant(reqinfo)]
        for ii, component in enumerate(components):
            if component.extracted:
                component.extract(doc)
                component.process(util.idname(ii), all_filters, reqinfo)
        params['elements'] = [component.html() for component in components]
        return self.template.render(**params)

    def mk_moplate_filters(self, params):
        '''
        Create moplate-level extra filters

        Builds a list of filters specific to this moplate, that will
        be applied to the extracted content of every mobile page.

        This method is a hook that can be altered by subclasses.  By
        default, it returns an empty list, unless the Moplate was
        instantiated with a non-empty imgsub argument; in that case it
        will contain a properly initialized imgsub filter.

        The params argument can be used to generate filters specific
        to the parameter set.

        Note that these are applied after any component-level filters,
        but before any site-level filters.

        @param params : Moplate template parameters
        @type  params : dict

        @return       : Filters
        @rtype        : list of callable
        
        '''
        from mobilize.filters import imgsub
        filts = []
        if self.imgsubs:
            filts.append(lambda elem: imgsub(elem, self.imgsubs))
        return filts

    def _final_wsgi_response(self, environ, msite, reqinfo, resp, src_resp_body):
        extra_params = {
            'fullsite'     : msite.fullsite,
            'request_path' : reqinfo.rel_url,
            'todesktop'    : _todesktoplink(reqinfo.protocol, msite.fullsite, reqinfo.rel_url),
            }
        final_body = self.render(src_resp_body, extra_params, msite.mk_site_filters(extra_params), reqinfo)
        response_overrides = msite.response_overrides(environ)
        response_overrides['content-length'] = str(len(final_body))
        final_resp_headers = httputil.get_response_headers(resp, environ, response_overrides)
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
    status = httputil.HTTP_STATUSES[302]
    
    def wsgi_response(self, msite, environ, start_response):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ)
        to = 'http://{}{}'.format(msite.fullsite, reqinfo.rel_url)
        start_response(self.status, [('location', to)])
        return ['<html><body><a href="{}">Go to page</a>'.format(to)]

class ToDesktopPermanent(ToDesktop):
    '''
    Operates similarly to ToDesktop, but with a 301 permanent redirect.
    
    '''
    
    status = httputil.HTTP_STATUSES[301]

class PassThrough(WebSourcer):
    '''
    Pass through the response from the desktop source
    '''
    def _final_wsgi_response(self, environ, msite, reqinfo, resp, src_resp_body):
        logger.info('Passing through response for {}'.format(reqinfo.url))
        return _passthrough_response(src_resp_body, resp)

class SecurityBlock(Handler):
    '''
    Block normal request and response

    This is meant to convey that the http request is effectively being
    dropped for security reasons.  It's useful, for example, in the
    context of a secure mobile web server, to prevent exploitation of
    a hole in the source/desktop site on the client's web server.
    '''
    status = httputil.HTTP_STATUSES[403]

    def wsgi_response(self, msite, environ, start_response):
        from mobilize.httputil import RequestInfo
        reqinfo = RequestInfo(environ)
        message = '''<html><head><title>{status}</title></head><body>
<h1>{status}</h1>
The request to {rel_url} is forbidden as a security measure.'''.format(status=self.status, rel_url = reqinfo.rel_url)
        start_response(self.status, [])
        return [message]

class Redirect(Handler):
    '''
    General redirect handeler

    destination is either 
    '''
    status = None
    where = None

    def __init__(self, *a):
        assert self.status is not None, 'subclass must define self.status'
        assert self.where is not None, 'subclass must define self.where'
        super().__init__(*a)
    
    def wsgi_response(self, msite, environ, start_response):
        import re
        from mobilize.httputil import _get_root_url
        if re.match(r'\w+://', self.where):
            # Has explicit protocol, so must be an absolute url
            location = self.where
        else:
            # Relative URL; construct relative URL from current request
            # TODO: I think there may be bug here regarding the desktop vs. mobile domain.
            location = _get_root_url(environ, use_defined_fullsite=False) + self.where
        start_response(self.status, [('Location', location)])
        return ['<html><body><a href="{}">Go to page</a>'.format(location)]

def redirect_to(where, status_code=302):
    '''
    Returns a redirect handler for a specific url

    where is either a relative URL, or can be a full absolute URL.
    See the documentation of the where attribute of the Redirect class
    for more information (where is basically copied to
    Redirect.where).

    @param where       : URL to redirect to - absolute, or relative
    @type  where       : str

    @param status_code : Status code of response
    @type  status_code : int: 301 or 302

    @return            : redirect handler
    @rtype             : Redirect
    
    '''
    from mobilize.httputil import HTTP_STATUSES
    assert status_code in {301, 302}, status_code
    _where = where # Just to avoid a NameError in the subclass below
    class ThisRedirect(Redirect):
        status = HTTP_STATUSES[status_code]
        where = _where
    return ThisRedirect()

# Standard/reusable handler instances
todesktop = ToDesktop()
passthrough = PassThrough()
securityblock = SecurityBlock()

# Supporting code

def _passthrough_response(body, resp):
    resp_headers = httputil.dict2list(resp)
    return body, resp_headers

_HTML_FROMSTRING_ENCODING_RE = re.compile(r'^\s*<\?xml', re.I)
def _html_fromstring(body):
    '''
    Used by, for example, WebSourcer.fromstring.  Separated out here for easier testing
    '''
    from lxml import html
    try:
        return html.fromstring(body)
    except ValueError:
        # Does this have an encoding declaration?
        if _HTML_FROMSTRING_ENCODING_RE.match(body):
            # yes, it does!
            enc_start = body.find('<?')
            enc_end = body.find('\n', enc_start)
            body = body[enc_end:]
            return html.fromstring(body)
        # No it doesn't, so let the error propagate
        raise

def _todesktoplink(protocol, fullsite, rel_url):
    '''
    Calculate the "todesktop" link string

    @param protocol : protocol (http or https)
    @type  protocol : str

    @param fullsite : Desktop (full) site domain, and port of applicable
    @type  fullsite : str
    
    @return         : rel_url
    @rtype          : The relative URL

    @return         : The link the mobile user can follow to view the desktop version of the page
    @rtype          : str
    
    '''
    link = '{}://{}{}'.format(protocol, fullsite, rel_url)
    if '?' in rel_url:
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
