# TODO: use abc

from mobilize.filters import COMMON_FILTERS
from mobilize import common

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

    def __init__(self, selector, filters=None, prefilters=None, postfilters=None, classvalue=None, idname=None):
        '''
        ctor

        The selector's job is to unambiguously specify which part of
        the source document to extract.  Its exact syntax and meaning
        depends on the subclass.  For example, it could be an xpath
        expression, a CSS "path", etc.

        Before final rendering, zero or more filters will be applied
        to the extracted content. Since each filter may transform the
        HTML snippet in an arbitrary way, the order matters.

        The filters, prefilters, and postfilters arguments all allow
        you to control what filters are applied to the extracted
        content. Each argument, if supplied, must be a list of filter
        functions. By default, filters.COMMON_FILTERS are set to be
        applied.  If you specify prefilters, that list is prepended to
        the default list; likewise, postfilters is appended to the
        default.  If you specificy filters, that will *replace* the
        default.

        If you use filters, you cannot specify prefilters or
        postfilters.  You can use one or both of prefilters or
        postfilters, but then cannot use filters.  To specify that no
        filters are to be used at all, pass filters=[].

        @param selector    : What part of the document to extract
        @type  selector    : str

        @param filters     : Absolute list of filters to use
        @type  filters     : list of function

        @param prefilters  : Filters to prepend to default list
        @type  prefilters  : list of function
        
        @param postfilters : Filters to append to default list
        @type  postfilters : list of function
        
        '''
        self.selector = selector
        if filters is None:
            these_filters = list(COMMON_FILTERS)
        else:
            assert (prefilters is None) and (postfilters is None),  'If you specify filters, you cannot specify either prefilters or postfilters'
            these_filters = list(filters)
        if prefilters is not None:
            these_filters = prefilters + these_filters
        if postfilters is not None:
            these_filters += postfilters
        self.filters = these_filters
        if classvalue is None:
            classvalue = common.classvalue()
        self.classvalue = classvalue
        self.idname = idname

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

    def process(self, default_idname):
        '''
        Process the extracted element, before rendering as a string

        This is for an HTML element that has been extracted and parsed
        from the document source.  We apply certain transformations and
        mods needed before it can be rendered into a string.

        Operates on self.elem, replacing it as a side effect.

        The element will be wrapped in a new div, which are given the
        class and ID according to the classvalue and idname member
        variables.  default_idname is used as a fallback idname; If
        self.idname has already been set, that will be used instead.

        @param elem      : HTML element to process
        @type  elem      : lxml.html.HtmlElement

        @param default_idname    : ID attribute to apply to the enclosing div
        @type  default_idname    : str

        @param filters   : Filters to apply to the element
        @type  filters   : list of filterapi functions from mobilize.filter

        @return          : New element with the applied changes
        @rtype           : lxml.html.HtmlElement
        
        '''
        from lxml.html import HtmlElement
        assert type(self.elems) is list, self.elems
        if self.idname is None:
            idname = default_idname
        else:
            idname = self.idname
        # apply common filters
        for elem in self.elems:
            for filt in self.filters:
                filt(elem)
        # wrap in special mobilize class, id
        newelem = HtmlElement()
        newelem.tag = 'div'
        newelem.attrib['class'] = self.classvalue
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

