import types
import re
from collections import OrderedDict
from mobilize import (
    exceptions,
    util,
    filters,
    )

class MobileSite(object):
    '''
    Represents a mobile website

    '''

    #: Desktop website default charset
    default_charset='utf-8'
    
    #: Enable verbose logging iff true
    verboselog=False
    
    def __init__(self, fullsite, handler_map):
        '''
        ctor
        
        @param fullsite     : domain of corresponding full (desktop) website
        @type  fullsite     : str

        @param handler_map : Handler/moplate mapping
        @type  handler_map : HandlerMap
        
        '''
        self.fullsite = fullsite
        self.handler_map = handler_map

    def mk_site_filters(self, params):
        '''
        Create global mobile-site filters

        Builds a list of filters that will be passed on to every
        moplate during rendering, to be applied to the extracted
        content of every mobile page.

        This list can be altered or added to by subclasses.

        @param params : Site-level template parameters
        @type  params : dict
        
        @return       : Filters
        @rtype        : list of callable
        
        '''
        site_filters = []
        if 'fullsite' in params and 'request_path' in params:
            desktop_url = 'http://%(fullsite)s%(request_path)s' % params
            site_filters.append(
                lambda elem: filters.absimgsrc(elem, desktop_url),
                )
        return site_filters
    
    def render_body(self, url, full_body):
        '''
        Render the mobile page's body

        If no moplate exists for the URL, pass the body through
        unmodified.

        @param url       : relative URL on the mobile site
        @type  url       : str

        @param full_body : Source body, e.g. from the corresponding desktop site page
        @type  full_body : str

        @return          : Mobile page body
        @rtype           : str
        
        '''
        rendered = ''
        extra_params = {
            'fullsite' : self.fullsite,
            'request_path' : url,
            }
        site_filters = self.mk_site_filters(extra_params)
        try:
            moplate = self.handler_map.get_handler_for(url)
            rendered = moplate.render(full_body, extra_params, site_filters)
        except exceptions.NoMatchingMoplateException:
            rendered = full_body
        return rendered

    def has_match(self, url):
        '''
        Indicate whether there is a moplate matching this URL.
        '''
        moplate = None
        try:
            moplate = self.handler_map.get_handler_for(url)
        except exceptions.NoMatchingMoplateException:
            pass
        return moplate is not None

    def request_overrides(self, wsgienviron):
        '''
        Site-specific HTTP request overrides

        Overriding this method allows custom overrides to the mobile
        site request headers under particular conditions.  This
        function must return a dictionary with 0 or more key-value
        pairs.  The keys are lowercased HTTP response header names.
        The values are overrides; see
        mobilize.http.get_response_headers for documentation.

        @param wsgienviron : WSGI environment for this request/response cycle
        @type  wsgienviron : dict

        @return : Overrides
        @rtype  : dict
        
        '''
        return {}

    def response_overrides(self, wsgienviron):
        '''
        Site-specific HTTP response overrides

        Overriding this method allows custom overrides to the mobile
        site response headers under particular conditions.  This
        function must return a dictionary with 0 or more key-value
        pairs.  The keys are lowercased HTTP response header names.
        The values are overrides; see
        mobilize.http.get_response_headers for documentation.

        @param wsgienviron : WSGI environment for this request/response cycle
        @type  wsgienviron : dict

        @return : Overrides
        @rtype  : dict
        
        '''
        return {}

class Handler(object):
    '''
    Handles a mobile page request

    This objects knows how to generate the HTTP response for a
    specific page on the mobile site.  It's a basis for more
    specialized services such as moplates.
    
    '''
    def wsgiresponse(self, fullsite, environ, start_response):
        assert False, 'subclass must implement'

class Moplate(Handler):
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
        from mobilize import http as httputil
        reqinfo = httputil.RequestInfo(environ)
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
        if not (httputil.mobilizeable(resp) and msite.has_match(reqinfo.rel_uri)):
            # No matching template found, so pass through the source response
            resp_headers = dict2list(resp)
            if msite.verboselog:
                log_headers('raw response headers [passthru]', resp_headers)
            start_response(status, resp_headers)
            return [src_resp_bytes]
        if msite.verboselog:
            log_headers('raw response headers', resp, status=status)
        mobilized_body = msite.render_body(reqinfo.rel_uri, src_resp_body)
        response_overrides = msite.response_overrides(environ)
        response_overrides['content-length'] = str(len(mobilized_body))
        if 'transfer-encoding' in resp:
            del resp['transfer-encoding'] # Currently what's returned to the client is not actually chunked.
        mobilized_resp_headers = httputil.get_response_headers(resp, environ, response_overrides)
        if msite.verboselog:
            log_headers('modified resp headers', mobilized_resp_headers)
        start_response(status, mobilized_resp_headers)
        return [mobilized_body]


class HandlerMap(object):
    '''
    Represents a mapping between pages (URLs) and their handlers
    '''
    def __init__(self, mapping):
        '''
        ctor

        The mapping object is a list of tuples, each representing a
        possible moplate match.  The order matters; moplates will
        match the first URL in the list.

        Each element of the mapping list is a (key, value) 2-tuple.
        The keys can be either raw strings, or Python regular
        expression objects.  If the former, the key will be internally
        converted to a Python regex object, after prepending with
        start-of-line match (i.e. the "^" character).

        MOPLATE RESOLUTION
        
        The values of the mapping object specify handlers, which are
        often moplates. Each value can be either:
          1) a Handler instance
          2) a string
          3) a tuple of two strings

        The last two are shortcuts for specifying particular moplates.
        If a single string, this is assumed to be a module that has a
        'moplate' attribute, of type Moplate.  That object is imported
        as the handler.

        If a tuple of two strings, this is assumed to be a module
        (first string) that has a attribute (second string) that is
        the moplate to import.

        The mechanics of this resolution are handled with the
        find_moplate and import_moplate functions in this module.
          
        @param mapping : The mobile domain mapping
        @type  mapping : list of tuple(key, value)
        
        '''
        self._mapping = OrderedDict()
        for k, v in mapping:
            if type(v) is str:
                handler = find_moplate(v)
            else:
                handler = v
            self._mapping[_regex(k)] = handler

    def get_handler_for(self, url):
        '''
        Get moplate for a given URL

        @param url : Relative URL to check
        @type  url : str

        @return    : The moplate
        @rtype     : Moplate
        
        @raises exceptions.NoMatchingMoplateException : No matching template found

        '''
        for pattern, moplate in self._mapping.items():
            if pattern.search(url):
                return moplate
        raise exceptions.NoMatchingMoplateException('no moplate match found for %s' % url)

def _regex(re_or_str):
    '''
    Create a compiled regular expression object.  Magically, if a
    string, '^' will be prepended before compiling.

    @param re_or_str : Either a RegexObject, or a (raw) string that can be compiled to a RegexObject
    @type  re_or_str : mixed

    @return          : compiled regular expression
    @rtype           : RegexObject
    
    '''
    if type(re_or_str) is str:
        return re.compile(r'^' + re_or_str)
    return re_or_str

def import_moplate(pagemodule, moplate_object='moplate'):
    '''
    Imports a moplate

    pagemodule is the module name under msite.moplates, i.e. there
    should be an object whose name is the value of moplate_object in
    msite/moplates/${pagemodule}.py (or
    msite/moplates/${pagemodule}/__init__.py).

    For example, if pagemodule is "contact", there could be a file
    named msite/moplates/contact.py containing an object named
    "moplate", which is a Moplate instance.

    @param pagemodule     : Name of module under msite.moplates
    @type  pagemodule     : str

    @param moplate_object : Name of template object to import from module
    @type  moplate_object : str

    @return               : Moplate
    @rtype                : mobilize.Moplate

    @raise ImportError: page module not found
    
    '''
    import importlib
    import msite.moplates
    mod = importlib.import_module('.' + pagemodule, 'msite.moplates')
    moplate = getattr(mod, moplate_object)
    assert isinstance(moplate, Moplate), type(moplate)
    return moplate

def find_moplate(arg):
    '''
    Find a mobile moplate

    arg is some piece of data that specifies a moplate, in one of a
    number of different ways.  See the documentation of
    HandlerMap.__init__ for details.  This function essentially
    handles the resolution process described there.

    @param arg : Some data that specifies a moplate to import
    @type  arg : mixed

    @return    : moplate
    @rtype     : mobilize.Moplate
    
    '''
    if type(arg) is str:
        moplate = import_moplate(arg)
    elif type(arg) is tuple:
        moplate = import_moplate(*arg)
    else:
        moplate = arg
    return moplate

