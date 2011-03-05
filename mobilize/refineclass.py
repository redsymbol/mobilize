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

    #: The extracted elements. type: list of lxml.html.HtmlElement
    elems = None

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
        Extracts content from the source, sets to self.elems

        Relies on self._extract, which should be implemented by the subclass.
        
        '''
        self.elems = self._extract(source)
        return self.elems

    def process(self, classname, idname, filters):
        '''
        Process the extracted element, before rendering as a string

        This is for an HTML element that has been extracted and parsed
        from the document source.  We apply certain transformations and
        mods needed before it can be rendered into a string.

        Operates on self.elem, replacing it as a side effect.

        The element will be wrapped in a new div, which are given the class and ID indicated.

        @param elem      : HTML element to process
        @type  elem      : lxml.html.HtmlElement

        @param classname : CSS class attribute to apply to the enclosing div
        @type  classname : str
        
        @param idname    : ID attribute to apply to the enclosing div
        @type  idname    : str

        @param filters   : Filters to apply to the element
        @type  filters   : list of filterapi functions from mobilize.filter

        @return          : New element with the applied changes
        @rtype           : lxml.html.HtmlElement
        
        '''
        from lxml.html import HtmlElement
        assert type(self.elems) is list, self.elems
        # apply common filters
        for elem in self.elems:
            for filt in filters:
                filt(elem)
        # wrap in special mobilize class, id
        newelem = HtmlElement()
        newelem.tag = 'div'
        newelem.attrib['class'] = classname
        newelem.attrib['id'] = idname
        for elem in self.elems:
            newelem.append(elem)
        self.elem = newelem
        return newelem
        
    def html(self):
        from lxml import html
        assert self.elem is not None, 'Must invoke self.extract() and self.process() before rendering to html'
        return html.tostring(self.elem, method='xml').strip()


class Unextracted(RefineClassBase):
    '''abstract base of all refinements that are independent of the source HTML page'''
    extracted = False

class XPath(Extracted):
    def _extract(self, source):
        return source.xpath(self.selector)

class CssPath(Extracted):
    def _extract(self, source):
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
        from django.template.loader import render_to_string
        return render_to_string(self.template, self.params)

class RawString(Unextracted):
    def __init__(self, rawstring):
        self.rawstring = rawstring

    def html(self):
        return self.rawstring

