import types
import re
from collections import OrderedDict
import exceptions, common

class MobileSite(object):
    '''
    Represents a mobile website

    '''
    
    def __init__(self, fullsite, template_map):
        '''
        ctor
        
        @param fullsite     : domain of corresponding full (desktop) website
        @type  fullsite     : str

        @param template_map : Template mapper
        @type  template_map : TemplateMap
        
        '''
        self.fullsite = fullsite
        self.template_map = template_map
    
    def render_body(self, url, full_body):
        '''
        Render the mobile page's body

        If no mobile template exists for the URL, pass the body
        through unmodified.

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
            template = self.template_map.get_template_for(url)
            rendered = template.render(full_body, extra_params)
        except exceptions.NoMatchingTemplateException:
            rendered = full_body
        return rendered

    def has_match(self, url):
        '''
        Indicate whether there is a template matching this URL.
        '''
        matched = True
        try:
            template = self.template_map.get_template_for(url)
        except exceptions.NoMatchingTemplateException:
            matched = False
        return matched

class Template(object):
    '''
    A mobile web page template (abstract base class)

    The mobile template represents a transformation, from a source
    (desktop page's) body, to the body of the corresponding mobile
    page.  Typically the template can be applied to a group of pages
    with similar DOM structure.

    The selectors is an ordered list of objects - strings, or
    refinements - identifying content elements in the full body.  From
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
        
        @param params        : Other template parameters
        @type  params        : dict (str -> mixed)
        
        '''
        self.template_name = template_name
        self.selectors = selectors
        if params:
            self.params = dict(params)
        else:
            self.params = {}
        assert 'elements' not in self.params, '"elements" is reserved/magical in mobile template params.  See Template class documention'

    def render(self, full_body, extra_params=None):
        '''
        Render the template for a particular HTML document body

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

class TemplateMap(object):
    '''
    Represents a mapping between pages (URLs) and their mobile
    templates
    '''
    def __init__(self, mapping):
        '''
        ctor

        The mapping object is a list of tuples, each representing a
        possible template match.  The order matters; templates will
        match the first URL in the list.

        Each element of the mapping list is a (key, value) 2-tuple.
        The keys can be either raw strings, or Python regular
        expression objects.  If the former, the key will be internally
        converted to a Python regex object, after prepending with
        start-of-line match (i.e. the "^" character).

        TEMPLATE RESOLUTION
        
        The values of the mapping object specify a mobilize template.
        This can be either:
          1) a Template instance
          2) a string
          3) a tuple of two strings

        If a string, this is assumed to be an template module that has
        a 'template' attribute.

        If a tuple of two strings, this is assumed to be an template
        module (first string) that has a attribute (second string)
        that is the template to import.

        The mechanics of this resolution are handled with the
        find_template and import_template functions in this module.
          
        @param mapping : The mobile domain mapping
        @type  mapping : list of tuple(key, value)
        
        '''
        self._mapping = OrderedDict()
        for k, v in mapping:
            self._mapping[_regex(k)] = find_template(v)

    def get_template_for(self, url):
        '''
        Get template for a given URL

        @param url : Relative URL to check
        @type  url : str

        @return    : The mobile template
        @rtype     : Template
        
        @raises exceptions.NoMatchingTemplateException : No matching template found

        '''
        for pattern, template in self._mapping.iteritems():
            if pattern.search(url):
                return template
        raise exceptions.NoMatchingTemplateException('no template match found for %s' % url)

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

def import_template(pagemodule, template_object='template'):
    '''
    Imports a mobilize template

    pagemodule is the module name under msite.moplates, i.e. there
    should be an object named "template" in
    msite/moplates/${pagemodule}.py (or
    msite/moplates/${pagemodule}/__init__.py).

    @param pagemodule : Name of module under msite.moplates
    @type  pagemodule : str

    @param template_object : Name of template object to import from module
    @type  template_object : str

    @return : Mobilize template
    @rtype  : mobilize.Template

    @raise ImportError: page module not found
    
    '''
    import importlib
    mod = importlib.import_module('.' + pagemodule, 'msite.moplates')
    template = getattr(mod, template_object)
    assert isinstance(template, Template), type(template)
    return template

def find_template(arg):
    '''
    Find a mobile template

    arg is some piece of data that specifies a mobile template, in one
    of a number of different ways.  See the documentation of
    TemplateMap.__init__ for details.  This function essentially
    handles the template resolution process described there.

    @param arg : Some data that specifies a template to import
    @type  arg : mixed

    @return    : mobilize template
    @rtype     : mobilize.Template
    
    '''
    if type(arg) in types.StringTypes:
        template = import_template(arg)
    elif type(arg) is tuple:
        template = import_template(*arg)
    else:
        template = arg
    return template
    
