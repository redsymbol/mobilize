import types
import re
from collections import OrderedDict
import exceptions, common

class MobileSite(object):
    '''
    Represents a mobile website

    '''
    
    def __init__(self, fullsite, moplate_map):
        '''
        ctor
        
        @param fullsite     : domain of corresponding full (desktop) website
        @type  fullsite     : str

        @param moplate_map : Moplate mapper
        @type  moplate_map : MoplateMap
        
        '''
        self.fullsite = fullsite
        self.moplate_map = moplate_map
    
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
        try:
            moplate = self.moplate_map.get_moplate_for(url)
            rendered = moplate.render(full_body, extra_params)
        except exceptions.NoMatchingMoplateException:
            rendered = full_body
        return rendered

    def has_match(self, url):
        '''
        Indicate whether there is a moplate matching this URL.
        '''
        moplate = None
        try:
            moplate = self.moplate_map.get_moplate_for(url)
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

class Moplate(object):
    '''
    A kind of mobile webpage template with magical powers

    A moplate represents a transformation, from a source (desktop
    page's) body, to the body of the corresponding mobile page.
    Typically the moplate can be applied to a group of pages with
    similar DOM structure.

    The selectors is an ordered list of objects - strings, or
    components - identifying content elements in the full body.  From
    this, a list of HTML snippets will be made available to the
    template as the "elements" attribute of the parameter dictionary.

    Because of the magical "elements" parameter, the supplied params
    cannot have a key of that name.

    Currently this is intended to be used as a base class. Subclasses
    must implement at least self._render().

    '''
    def __init__(self, template_name, selectors, params=None):
        '''
        ctor
        
        @param template_name : Template name (file)
        @type  template_name : str

        @param selectors     : Selectors of content elements to extract from full body
        @type  selectors     : list
        
        @param params        : Other template rendering parameters
        @type  params        : dict (str -> mixed)
        
        '''
        self.template_name = template_name
        self.selectors = selectors
        if params:
            self.params = dict(params)
        else:
            self.params = {}
        assert 'elements' not in self.params, '"elements" is reserved/magical in mobile template params.  See Moplate class documention'

    def render(self, full_body, extra_params=None):
        '''
        Render the moplate for a particular HTML document body

        extra_params is a dictionary of extra parameters for just this
        rendering, which can be used to override any of the default
        template parameters as well.
        
        @param full_body    : Source HTML - body of full website's page
        @type  full_body    : str

        @param extra_params : Extra template parameters to use for this rendering
        @type  extra_params : dict
        
        @return             : Rendered mobile page body
        @rtype              : str

        '''
        from lxml import html
        from filters import COMMON_FILTERS
        params = dict(self.params)
        if extra_params:
            params.update(extra_params)
        assert 'elements' not in params # Not yet anyway
        doc = html.fromstring(full_body)
        elements = self.selectors
        for ii, elem in enumerate(elements):
            if elem.extracted:
                elem.extract(doc)
                elem.process(common.idname(ii))
        params['elements'] = [elem.html() for elem in elements]
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

    def get_params(self):
        '''
        Get the current template parameters

        @return : current parameters
        @rtype  : dict
        
        '''
        return self.params

class MoplateMap(object):
    '''
    Represents a mapping between pages (URLs) and their mobile
    templates
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
        
        The values of the mapping object specify moplates.
        Each can be either:
          1) a Moplate instance
          2) a string
          3) a tuple of two strings

        If a string, this is assumed to be a module that has a
        'moplate' attribute.

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
            self._mapping[_regex(k)] = find_moplate(v)

    def get_moplate_for(self, url):
        '''
        Get moplate for a given URL

        @param url : Relative URL to check
        @type  url : str

        @return    : The moplate
        @rtype     : Moplate
        
        @raises exceptions.NoMatchingMoplateException : No matching template found

        '''
        for pattern, moplate in self._mapping.iteritems():
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
    if type(re_or_str) in types.StringTypes:
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
    mod = importlib.import_module('.' + pagemodule, 'msite.moplates')
    moplate = getattr(mod, moplate_object)
    assert isinstance(moplate, Moplate), type(moplate)
    return moplate

def find_moplate(arg):
    '''
    Find a mobile moplate

    arg is some piece of data that specifies a moplate, in one of a
    number of different ways.  See the documentation of
    MoplateMap.__init__ for details.  This function essentially
    handles the resolution process described there.

    @param arg : Some data that specifies a moplate to import
    @type  arg : mixed

    @return    : moplate
    @rtype     : mobilize.Moplate
    
    '''
    if type(arg) in types.StringTypes:
        moplate = import_moplate(arg)
    elif type(arg) is tuple:
        moplate = import_moplate(*arg)
    else:
        moplate = arg
    return moplate

