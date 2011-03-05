# TODO: use abc

class RefineClassBase(object):
    '''abstract base of all refinement classes'''
    def html(self):
        '''
        Render the element content HTML

        @return : html snippet/content
        @rtype  : str
        
        '''
        assert False, 'Subclass must implement'


class Extracted(RefineClassBase):
    '''abstract base of all refinements that are extracted from the source HTML page'''
    extracted = True

    #: The extracted element. type: lxml.html.HtmlElement
    elem = None

    def __init__(self, selector):
        '''
        ctor

        The selector's job is to unambiguously specify which part of
        the source document to extract.  Its exact syntax and meaning
        depends on the subclass.  For example, it could be an xpath
        expression, a CSS "path", etc.

        @param selector : What part of the document to extract
        @type  selector : str
        
        '''
        self.selector = selector

    def _extract(self, source):
        '''
        Extract an HTML element from the source

        source is normally parsed from the HTML body of the source
        page, via lxml.html.fromstring.
        
        @param source : HTML element of source to extract from
        @type  source : lxml.html.HtmlElement

        @return       : html element representing extracted content
        @rtype        : lxml.html.HtmlElement
        
        '''
        assert False, 'Subclass must implement'

    def extract(self, source):
        '''
        Extracts content from the source, sets to self.elem

        Relies on self._extract, which should be implemented by the subclass.
        
        '''
        self.elem = self._extract(source)
        return self.elem

    def html(self):
        from lxml import html
        assert self.elem, 'Must invoke self.extract() before rendering to html'
        return html.tostring(self.elem, method='xml').strip()

class Unextracted(RefineClassBase):
    '''abstract base of all refinements that are independent of the source HTML page'''
    extracted = False

def XPath(Extracted):
    def elem(self, source):
        return source.xpath(self.selector)

class CssPath(Extracted):
    def elem(self, source):
        from lxml.cssselect import CSSSelector
        css_sel = CSSSelector(self.selector)
        return source.xpath(css_sel.path)
    
class RawTemplate(Unextracted):
    '''
    Unextracted refinement from a template
    '''
    def __init__(self, template, params = None):
        '''
        @param template : Path to the template to render
        @type  template : str

        @param params : Template parameters
        @type  params : 
        
        '''
        if not params:
            params = {}
        self.template = template
        self.params = params

    def html(self):
        from refine import raw_template
        return raw_template(self.template, self.params)

class RawString(Unextracted):
    def __init__(self, rawstring):
        self.rawstring = rawstring

    def html(self):
        return self.rawstring

