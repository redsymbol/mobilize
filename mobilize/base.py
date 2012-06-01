# Copyright 2010-2012 Mobile Web Up. All rights reserved.
import types
import re
from collections import OrderedDict
from mobilize import (
    exceptions,
    util,
    filters,
    )

class Domains:
    '''
    Represents the various domains involved in mobilization

    This encapsulates reasoning on the different domain names involved
    in the client's web presence - desktop, mobile and everything in
    between.

    In general, there will be four canonical domains for a client's site:
      - the HTTP desktop (www.example.com)
      - the HTTPS desktop (secure.example.com)
      - the HTTP mobile (m.example.com)
      - the HTTPS mobile (m.secure.example.com)

    In many cases, the HTTPS and HTTP domains will be the same, so
    there are only two (www.example.com and m.example.com).  And of
    course for non-ecommerce sites, only the HTTP domains are needed,
    so again two.  At the other extreme, there may more (e.g. if there
    are desktop, tablet and mobile versions).

    For now, let's assume there are four domains to balance.

    Within these four, we have to make additional distinctions.  The
    best use case is in dealing with 301 and 302 redirects that send
    the Location: header during development.  In development, you'll
    need to use alternate domains (such as example.mwuclient.com:2280
    and example.mwuclient.com:2443 for the regular and secure mobile
    sites, respectively).  And if you hit a 301 that sends a
    "Location: http://example.com/foo/bar" header, you want Mobilize
    to recognize that and replace it with "Location:
    http://example.mwuclient.com:2280/foo/bar" - but only during
    development.

    The Domains instance manages the info needed to make all this
    happen.  Different parts of Mobilize use it whenever they need to
    calculate based on what the different domains are.

    The only values you need to supply to the constructor are mobile
    and desktop.  For simple regular and ecommerce websites, the
    Domains ctor will be able to correctly guess at the other values.

    In practice when configuring real mobilize sites, you'll want to
    often use the from_defs class method.

    The Domains object will have str-valued attributes representing
    all the distinctions Mobilize may need.  These are exactly the
    same as the arguments to the constructor (not repeating here so
    the two lists won't get out of sync).  You can always access any
    of these properties; in simple cases they will just have the same
    value as either the mobile or desktop domain.

    '''

    def __init__(self,
                 mobile,
                 desktop,
                 https_mobile=None,
                 production_http_desktop=None,
                 production_https_desktop=None,
                 ):
        '''
        ctor

        By convention, arguments prefixed with "https_" refer to HTTPS
        domains, while those with no prefix refer to HTTP. Only the
        arguments mobile and desktop are required: the ctor will make
        an educated guess on any values not supplied.

        Note there is no argument for https_desktop right now.  We can
        add it at some point if a client's site needs it.
        
        @param mobile                   : The HTTP mobile domain (m.example.com)
        @type  mobile                   : str

        @param desktop                  : The HTTP desktop domain, i.e. the full "source" site (www.example.com)
        @type  desktop                  : str

        @param https_mobile             : The HTTPS mobile domains (m.secure.example.com)
        @type  https_mobile             : str
        
        @param production_http_desktop  : The HTTP domain of the client's production desktop site (www.mwuclient.com)
        @type  production_http_desktop  : str
        
        @param production_https_desktop : The HTTPS domain of the client's production desktop site (secure.mwuclient.com)
        @type  production_https_desktop : str
        
        '''
        self.desktop = desktop
        self.mobile = mobile

        # If https domains are not set, fall back to non-https versions
        if https_mobile:
            self.https_mobile = https_mobile
        else:
            self.https_mobile = mobile
            
        self.production_http_desktop = production_http_desktop
        self.production_https_desktop = production_https_desktop

    @classmethod
    def from_defs(cls, defs):
        '''
        Attempt to create a Domains instance from the site's defs module

        Will read the following settings from defs (only the first two
        are required):
        
          - MOBILE_DOMAIN
          - DESKTOP_DOMAIN
          - PRODUCTION_HTTP_DESKTOP_DOMAIN
          - PRODUCTION_HTTPS_DESKTOP_DOMAIN
          - HTTPS_MOBILE_DOMAIN

        @param defs : definitions module
        @type  defs : module

        @return     : domains instance
        @rtype      : Domains
        
        '''
        domains = cls(mobile = defs.MOBILE_DOMAIN, desktop = defs.DESKTOP_DOMAIN)
        if hasattr(defs, 'PRODUCTION_HTTP_DESKTOP_DOMAIN'):
            domains.production_http_desktop = defs.PRODUCTION_HTTP_DESKTOP_DOMAIN
        if hasattr(defs, 'PRODUCTION_HTTPS_DESKTOP_DOMAIN'):
            domains.production_https_desktop = defs.PRODUCTION_HTTPS_DESKTOP_DOMAIN
        if hasattr(defs, 'HTTPS_MOBILE_DOMAIN'):
            domains.https_mobile = defs.HTTPS_MOBILE_DOMAIN
        return domains
        
class MobileSite:
    '''
    Represents a mobile website

    '''

    #: Desktop website default charset
    default_charset = 'utf-8'
    
    #: Signals whether this is a production environment, or we're in development mode
    is_production = False

    #: Whether to fake certain HTTP HEAD requests
    fake_head_requests = True
    
    def __init__(self,
                 domains,
                 handler_map,
                 imgsubs=None):
        '''
        ctor
        
        @param domains     : Domains instance specifying domains for desktop, mobile, etc.
        @type  domains     : str

        @param handler_map : Handler/moplate mapping
        @type  handler_map : HandlerMap
        
        '''
        self.domains = domains
        self.fullsite = domains.desktop
        self.handler_map = handler_map
        self.imgsubs = imgsubs

    def mk_site_filters(self, params):
        '''
        Create global mobile-site filters

        Builds a list of filters that will be passed on to every
        moplate during rendering, to be applied to the extracted
        content of every mobile page.

        Note that these are applyed *after* any moplate-level filters,
        which are themselves applied after any component-level
        filters.

        This list can be altered or added to by subclasses.

        @param params : Site-level template parameters
        @type  params : dict
        
        @return       : Filters
        @rtype        : list of callable
        
        '''
        from mobilize.images import to_imgserve
        site_filters = []
        if self.imgsubs:
            site_filters.append(lambda elem: filters.imgsub(elem, self.imgsubs))
        if 'fullsite' in params and 'request_path' in params:
            desktop_url = 'http://%(fullsite)s%(request_path)s' % params
            site_filters.extend((
                lambda elem: filters.absimgsrc(elem, desktop_url),
                to_imgserve,
                lambda elem: filters.abslinkfilesrc(elem, desktop_url),
                ))
        return site_filters

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
        Site-specific HTTP response overrides for mobilizeable content

        Overriding this method allows custom overrides to the mobile
        site response headers under particular conditions.  This
        function must return a dictionary with 0 or more key-value
        pairs.  The keys are lowercased HTTP response header names.
        The values are overrides; see
        mobilize.httputil.get_response_headers for documentation.

        @param wsgienviron : WSGI environment for this request/response cycle
        @type  wsgienviron : dict

        @return : Overrides
        @rtype  : dict
        
        '''
        return {}

    def get_http(self):
        '''
        Get the Http object used for making source requests

        On rare occasions, a particular desktop site may need custom
        settings on the http object used to fetch the source
        documents, which can be done by overriding this method.
        
        @return : http object
        @rtype  : httplib2.Http
    
        '''
        from .httputil import get_http
        return get_http()

    def sechooks(self):
        '''
        Security hooks applicable for this site

        To include security hooks for the site, override this method
        in a subclass.

        @return : SecurityHook instances to apply
        @rtype  : ordered sequence

        '''
        return []

    def postprocess_response_headers(self, headers, status):
        '''
        Apply any final universal postprocessing to response headers

        @param headers : Response headers
        @type  headers : list of (name, value)

        @param status : HTTP status response code from source server
        @type  status : 200

        @return : Modified response headers
        @rtype  : list of (name, value)
        
        '''
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
                # rewrite domain on redirect
                if status in {301, 302}:
                    value = _new_location(value, self.domains)
                # Development hook
                if re.match(r'http://[^/]*:2443/', value):
                    value = value.replace(':2443/', ':2280/')
            return (header, value)
        modified = [modify(header, value)
                    for header, value in expand(headers)
                    if header not in removed]
        for hook in self.sechooks():
            modified = hook.response(modified)
        return modified

    def must_fake_http_head(self, reqinfo):
        '''
        Whether this is a HEAD request that we need to fake
    
        See docs of mobilize.handlers.WebSourcer.wsgi_response for
        explanation and info, including what exactly we mean by
        "fake".
    
        @return : msite
        @rtype  : MobileSite
    
        @return : request info
        @rtype  : RequestInfo
        
        @return : True iff this is an HTTP HEAD request that we need to fake
        @rtype  : bool
        
        '''
        must_fake = False
        if 'HEAD' == reqinfo.method and '/' == reqinfo.rel_url:
            if self.fake_head_requests:
                must_fake = True
        return must_fake

class HandlerMap:
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

        HANDLER AND MOPLATE RESOLUTION
        
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

        The mechanics of these moplate resolution shortcuts are
        handled with the find_moplate and import_moplate functions in
        this module.
          
        @param mapping : The mobile domain mapping
        @type  mapping : list of tuple(key, value)
        
        '''
        from mobilize.handlers import Handler
        self._mapping = OrderedDict()
        for k, v in mapping:
            if isinstance(v, Handler):
                handler = v
            else:
                handler = find_moplate(v)
            self._mapping[_regex(k)] = handler

    def get_handler_for(self, url):
        '''
        Get moplate for a given URL

        @param url : Relative URL to check
        @type  url : str

        @return    : The moplate
        @rtype     : Moplate
        
        @raises exceptions.NoMatchingHandlerException : No matching template found

        '''
        for pattern, moplate in self._mapping.items():
            if pattern.search(url):
                return moplate
        raise exceptions.NoMatchingHandlerException('no moplate match found for %s' % url)

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
    from .handlers import Moplate
    import importlib
    import msite.moplates
    mod = importlib.import_module('.' + pagemodule, 'msite.moplates')
    moplate = getattr(mod, moplate_object)
    assert isinstance(moplate, Moplate), type(moplate)
    moplate.name = pagemodule + ' ' + moplate_object
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

    @raise RuntimeError: arg is not in a usable format
    
    '''
    if type(arg) is str:
        moplate = import_moplate(arg)
    elif type(arg) is tuple:
        moplate = import_moplate(*arg)
    else:
        raise RuntimeError('Cannot apply find_moplate to argument of type {}'.format(str(type(arg))))
    return moplate

# Supporting code
def _new_location(location, domains):
    '''
    Calculate the new value of the Location: response header

    @param location : Unmodified value of Location: header
    @type  location : str

    @param domains  : The mobile site's Domains object
    @type  domains  : mobilize.base.Domains
    
    @return         : altered location
    @rtype          : str
    
    '''
    from urllib.parse import urlsplit
    from mobilize.httputil import replace_domain
    scheme = urlsplit(location)[0]
    if scheme not in {'http', 'https'}:
        # Only know how to deal with http and https
        return location
    
    new_domain = domains.mobile
    if 'http' == scheme:
        production_desktop = domains.production_http_desktop
    else:
        production_desktop = domains.production_https_desktop
        new_domain = domains.https_mobile
    if production_desktop:
        old_domain = production_desktop
    else:
        old_domain = domains.desktop
    location = replace_domain(location, old_domain, new_domain)
    return location

