# Copyright 2010-2012 Mobile Web Up. All rights reserved.
import copy
import logging

from mobilize import util
from .common import Component

#: Indicates that filtering should be applied on every extracted element individually
FILT_EACHELEM = 1
#: Indicates that filtering should be done on the constructed final single element
FILT_COLLAPSED = 2

def _csspath2xpath(csspath):
    from lxml.cssselect import CSSSelector
    return CSSSelector(csspath).path
    
class Extracted(Component):
    '''
    abstract base of all components that are extracted from the source HTML page

    TODO: use abc (abstract base classes)
    '''
    extracted = True

    #: The raw extracted elements. type: list of lxml.html.HtmlElement
    elems = None

    #: What becomes the processed element for the mobile page
    elem = None

    #: Element selection predicate.  None means keep everything
    keep_if = None

    def __init__(self,
                 selector,
                 filters=None,
                 prefilters=None,
                 postfilters=None,
                 omitfilters=None,
                 classvalue=None,
                 idname=None,
                 style='',
                 filtermode=FILT_EACHELEM,
                 usecopy=False,
                 tag='div',
                 innerhtml=False,
                 keep_if=None,
                 ):
        '''
        ctor

        The selector's job is to unambiguously specify which part of
        the source document to extract.  Its exact syntax and meaning
        depends on the subclass.  For example, it could be an xpath
        expression, a CSS "path", etc.

        In general, the selector may actually be plural, i.e. some
        iterable of individual selectors.  The effect, again depending
        on the subclass, will be to the matches of each selector
        together.

        SPECIFYING FILTERS
        
        Before final rendering, zero or more filters will be applied
        to the extracted content. By "filter", we mean some callable
        that conforms to the Mobilize filter API; read the docs of
        mobilize.filters for details.  Since each filter may transform
        the HTML snippet in an arbitrary way, the order matters.

        The filters, prefilters, postfilters, and omitfilters
        arguments all allow you to control what filters are applied to
        the extracted content. Each argument is optional, and if
        supplied, is a collection of filter-api callables. By default,
        filters.DEFAULT_FILTERS are set to be applied.  If you specify
        prefilters, that list is prepended to the default list;
        likewise, postfilters is appended to the default.  If you
        specify filters, that will *replace* the default.

        omitfilters is a set of filters, or some sequence convertable
        to a set (with the set() constructor).  If you specify
        omitfilters, any filters within (identified by Python's id())
        will be removed from the default list.  This is convenient if
        you want to use all default filters except one or two for a
        component, in a forward-compatible way.

        If you use the filters argument, you cannot specify
        prefilters, postfilters or omitfilters.  You can use one or
        more of prefilters, postfilters or omitfilters, but then
        cannot use filters.  To specify that no filters are to be used
        at all, pass filters=[].

        OTHER OPTIONS
        
        filtermode specifies the manner and timing in which filters
        are applied to matching source elements.  In the process of
        creating the final HTML used in the mobile web page, the first
        step is fetching and extracting 0 or more elements from the
        source page. If filtermode is FILT_EACHELEM, the filters are
        then applied to each element individually before
        proceeding. The next stage is to collapse these elements into
        a single container div element.  If filtermode is
        FILT_COLLAPSED, the filters are instead applied to this final
        single element.

        Note the significant complexity difference here: with N
        filters and M elements matched from the source, the filter
        application has complexity of no less than \Omega(N*M) with
        filtermode FILT_EACHELEM, but complexity \Omega(M) for
        FILT_COLLAPSED.

        If innerhtml is False (the default), the selected element will
        be extracted.  If innerhtml is True, the actual content of
        that element is extracted; the parent tag itself is dropped.
        This only has an effect if there is exactly one matching
        element, otherwise the innerhtml=False behavior is forced.

        keep_if is, if supplied, a function taking an HtmlElement
        argument, and returning True or False.  The function is called
        on every matching element; if False, the element is discarded
        before proceeding.  All this happens before any filters are
        applied.

        TODO: make FILT_COLLAPSED the default filtermode

        @param selector    : What part of the document to extract
        @type  selector    : str, or list of str

        @param filters     : Absolute list of filters to use
        @type  filters     : list of function

        @param prefilters  : Filters to prepend to default list
        @type  prefilters  : list of function
        
        @param postfilters : Filters to append to default list
        @type  postfilters : list of function

        @param omitfilters : Filters to omit from default
        @type  omitfilters : set, or sequence that can be converted to a set

        @param classvalue  : Value of "class" attribute for containing div
        @type  classvalue  : str or None (indicating use default)
        
        @param idname      : Value of "id" attribute for containing div
        @type  idname      : str or None (indicating use default)

        @param style       : Value for "style" attribute for containing div
        @type  style       : str

        @param filtermode  : Filter application mode
        @type  filtermode  : int

        @param usecopy     : Whether to operate on a copy of the source element
        @type  usecopy     : bool

        @param tag         : Name of containing tag
        @type  tag         : str

        @param keep_if     : Selection predicate
        @type  keep_if     : function: HtmlElement -> bool
    
        @param innerhtml   : If true, select the matching element's content only
        @type  innerhtml   : bool
        
        '''
        if type(selector) in (list, tuple):
            self.selectors = list(selector) # casting tuple to list
        else:
            self.selectors = [selector]
        self.filters = _pick_filters(filters, prefilters, postfilters, omitfilters)
        if classvalue is None:
            classvalue = util.classvalue()
        self.classvalue = classvalue
        self.idname = idname
        self.style = style
        self.filtermode = filtermode
        self.usecopy = usecopy
        self.tag = tag
        self.innerhtml = innerhtml
        self.keep_if = keep_if

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
        
        @param source : HTML element of source to extract from
        @type  source : lxml.html.HtmlElement

        @return       : html elements representing extracted content
        @rtype        : list of lxml.html.HtmlElement
        
        '''
        if self.keep_if is None:
            keepable = lambda elem: True
        else:
            keepable = self.keep_if
        self.elems = [elem for elem in self._extract(source)
                      if keepable(elem)]
        # Omit duplicate extractions. See test_omit_dupe_extractions
        found_ids = set()
        def keep(elem):
            _k = True
            nonlocal found_ids
            if id(elem) in found_ids:
                _k = False
            else:
                found_ids.add(id(elem))
            return _k
        nondupe_elems = [elem for elem in self.elems
                         if keep(elem)]
        self.elems = nondupe_elems
        # TODO: strip out duplicate elements
        if self.usecopy:
            for ii, elem in enumerate(self.elems):
                self.elems[ii] = copy.deepcopy(elem)
        return self.elems

    def process(self, default_idname=None, extra_filters=None, reqinfo=None):
        '''
        Process the extracted element, before rendering as a string

        This is for an HTML element that has been extracted and parsed
        from the document source.  We apply certain transformations and
        mods needed before it can be rendered into a string.

        Operates on self.elem, replacing it as a side effect.

        The element will be wrapped in a new div, which is given the
        class and ID according to the classvalue and idname member
        variables.  default_idname is used as a fallback idname; If
        self.idname has already been set, that will be used instead.
        It is a runtime error if neither are set.

        @param elem           : HTML element to process
        @type  elem           : lxml.html.HtmlElement

        @param default_idname : Optional fallback ID attribute to apply to the enclosing div
        @type  default_idname : str

        @param extra_filters  : Additional filters to post-apply, from moplate
        @type  extra_filters  : list of callable; or None for no filters (empty list)

        @return               : New element with the applied changes
        @rtype                : lxml.html.HtmlElement
        
        '''
        from lxml.html import HtmlElement
        if extra_filters is None:
            extra_filters = []
        def applyfilters(elem):
            from itertools import chain
            def relevant(filt):
                _is_relevant = True
                if hasattr(filt, 'relevant'):
                    assert callable(filt.relevant), filt.relevant
                    _is_relevant = filt.relevant(reqinfo)
                return _is_relevant
            for filt in chain(self.filters, extra_filters):
                if relevant(filt):
                    filt(elem)
        assert type(self.elems) is list, self.elems
        if self.idname is None:
            assert default_idname is not None, 'cannot determine an idname!'
            idname = default_idname
        else:
            idname = self.idname
        if self.filtermode == FILT_EACHELEM:
            # applying filters to extracted elements individually
            for elem in self.elems:
                applyfilters(elem)
        # wrap in special mobilize class, id
        if self.innerhtml and len(self.elems) == 1:
            newelem = copy.deepcopy(self.elems[0])
            newelem.tag = self.tag
        else:
            newelem = HtmlElement()
            newelem.tag = self.tag
            for elem in self.elems:
                newelem.append(elem)
        if self.filtermode == FILT_COLLAPSED:
            # applying filters to the single collapsed element
            applyfilters(newelem)
        newelem.attrib['class'] = self.classvalue
        newelem.attrib['id'] = idname
        if bool(self.style):
            newelem.attrib['style'] = self.style
        self.elem = newelem
        return newelem
        
    def html(self):
        assert self.elem is not None, 'Must invoke self.extract() and self.process() before rendering to html'
        return util.elem2str(self.elem)

class XPath(Extracted):
    def _extract(self, source):
        extracted = []
        for selector in self.selectors:
            extracted += source.xpath(selector)
        return extracted

class CssPath(XPath):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        for ii, selector in enumerate(self.selectors):
            self.selectors[ii] = _csspath2xpath(selector)
            
class GoogleAnalytics(Extracted):
    '''
    Locates and extracts Google Analytics tracking code from desktop page

    '''
    def __init__(self, **kw):
        '''
        ctor

        Unlike many extracted components, this one currently does not
        accept a selector argument.  The source of the desktop page is
        scanned to locate the google analytics tracking code.
        
        '''
        assert 'selector' not in kw
        if 'idname' not in kw:
            kw['idname'] = util.idname('ga')
        kw['selector'] = None
        super().__init__(**kw)

    def _extract(self, source):
        '''
        TODO: any incarnations of GA we still need to recognize?
        '''
        elems = []
        for script_elem in source.iterfind('.//script'):
            if len(elems) > 0:
                break
            if script_elem.text is not None:
                scripttext = script_elem.text.lstrip()
                if scripttext.startswith('var _gaq ='):
                    # newer ga version
                    elems = [script_elem]
                elif scripttext.startswith('var gaJsHost'):
                    # older ga version
                    next_elem = script_elem.getnext()
                    if next_elem is not None and 'script' == next_elem.tag:
                        elems = [
                            script_elem,
                            next_elem,
                            ]
        return elems

class BigImage(XPath):
    '''
    Extract and style a large image for mobile

    This extracts a largish image element, identified by CSS path or
    xpath.  It then has its height and width elements removed, and is
    wrapped in a div with CSS class mwu-elem-bigimage class.  As
    defined by default in the mobilize-skel CSS file, this class will
    cause the image to span the width of the screen.

    Given current (2011) mobile screen sizes, it's best to use these
    on images that are 480px or wider, and look good when compressed
    to as low as half that width.
    
    '''

    def __init__(self, csspath=None, xpath=None, idname=None):
        from mobilize.util import classvalue
        from mobilize.filters import noimgsize
        assert not (csspath is None and xpath is None), 'You must provide either a csspath or an xpath!'
        if xpath is None:
            xpath = _csspath2xpath(csspath)
        kwargs = dict(
            classvalue = classvalue('bigimage'),
            postfilters = [noimgsize],
            )
        if idname is not None:
            kwargs['idname'] = idname
        super().__init__(xpath, **kwargs)

# supporting code
from mobilize.filters import DEFAULT_FILTERS
def _pick_filters(filters, prefilters, postfilters, omitfilters, _default=DEFAULT_FILTERS):
    if filters is not None:
        assert (prefilters is None) and (omitfilters is None) and (postfilters is None),  'If you specify filters, you cannot specify any of prefilters, postfilters or omitfilters.'
        return list(filters)
    if omitfilters is None:
        omitfilters = set()
    elif type(omitfilters) is not set:
        omitfilters = set(omitfilters)
    picked = list(filt for filt in _default
                  if filt not in omitfilters)
    if prefilters is not None:
        picked = prefilters + picked
    if postfilters is not None:
        picked += postfilters
    return picked
