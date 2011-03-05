import types
import re
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import exceptions
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
                classname='mwu-melem'
                idname='mwu-melem-%d' % ii
                elem.process(classname, idname, COMMON_FILTERS)
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

        The mapping object is an ordered dictionary.  Each entry
        represents a possible template match.

        The keys can be either raw strings, or Python regular
        expression objects.  If the former, the key will be internally
        converted to a Python regex object, after prepending with
        start-of-line match (i.e. the "^" character).

        The values of the mapping object are Template instances.

        @param mapping : The mobile domain mapping
        @type  mapping : OrderedDict: regex -> Template
        
        '''
        self._mapping = OrderedDict()
        for k, v in mapping.iteritems():
            self._mapping[_regex(k)] = v

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

def elem2str(elem):
    '''
    Render an HTML element as a string

    @param elem : element
    @type  elem : lxml.htmlHtmlElement

    @return : HTML snippet
    @rtype  : str
    
    '''
    from lxml import html
    return html.tostring(elem, method='xml').strip()
