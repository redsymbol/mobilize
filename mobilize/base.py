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
        mobilize.httputil.get_response_headers for documentation.

        @param wsgienviron : WSGI environment for this request/response cycle
        @type  wsgienviron : dict

        @return : Overrides
        @rtype  : dict
        
        '''
        return {}

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

