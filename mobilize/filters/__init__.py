'''
Filters : functions that process and modify HTML snippets

A filter is a function designed to alter or process a block of
HTML-like code in some useful way.  It takes as input a string, meant
to be a snippet of HTML, and returns another string.  The returned
string may in general be the same thing as the input, but often it is
modified in some way.

FILTER API

A function conforms to the filter API if it:
  * accepts an lxml.html.HTMLElement instance as an argument, and
  * does not return any value,
  * operates by making any changes directly on the element as a side effect, and
  * is a no-op if the passed element is somehow not relevant to the particular filter (rather than raising an error).

'''

from mobilize.common import (
    findonetag,
    htmlelem,
    )

def noinlinestyles(elem):
    '''
    Remove any inline styles on a tag

    As a side effect, if the passed element has a 'style' attribute,
    then that attribute is removed.
    
    @param elem : Element representing an html tag
    @type  elem : lxml.html.HTMLElement

    '''
    if 'style' in elem.attrib:
        del elem.attrib['style']

def nomiscattrib(elem):
    '''
    Remove certain miscellaneous unwanted attributes
    
    As a side effect, if the passed element has any of the following
    attributes, then that attribute is removed:
    
     * align
     TODO: update this list
    
    @param elem : Element representing an html tag
    @type  elem : lxml.html.HTMLElement

    '''
    unwanteds = (
        'align',
        'border',
        'cellspacing',
        'cellpadding',
        'valign',
        )
    for unwanted in unwanteds:
        if unwanted in elem.attrib:
            del elem.attrib[unwanted]

def noevents(elem):
    '''
    Removes "onSOMETHING" events

    As a side effect, removes all "onClick", "onMouseover",
    etc. events from the tag.
    
    @param elem : Element representing an html tag
    @type  elem : lxml.html.HTMLElement

    '''
    for attr in elem.attrib:
        if attr.startswith('on'):
            del elem.attrib[attr]

def noimgsize(elem):
    '''
    Strip the height and width attributes from the first child img tag

    This filter searches for the first img in the element, and removes
    any sizing attributes.  This is useful if you have a large source
    image, and want to use a "width: 100%" trick in CSS to make it
    span any device.

    @param elem : Element representing an html tag
    @type  elem : lxml.html.HTMLElement
    
    '''
    img_elem = findonetag(elem, 'img')
    if img_elem is not None:
        for a in ('height', 'width'):
            if a in img_elem.attrib:
                del img_elem.attrib[a]

def noattribs(parent_elem, tag, attribs):
    '''
    Will recursively delete the indicated attributes from elements of
    the given tag name.

    @param parent_elem : Containing element to hunt within
    @type  parent_elem : lxml.html.HtmlElement
    
    @param tag         : Name of tag (element) to remove attributes from
    @type  tag         : str

    @param attribs     : Attributes of the tags to remove
    @type  attribs     : list of str
    
    '''
    def delattrib(elem):
        for key in attribs:
            if key in elem.attrib:
                del elem.attrib[key]
    if tag == parent_elem.tag:
        delattrib(parent_elem)
    for elem in parent_elem.iterfind('.//%s' % tag):
        delattrib(elem)

def _setwidth(elem, width):
    if 'height' in elem.attrib:
        del elem.attrib['height']
    elem.attrib['width'] = str(width)

def resizeobject(elem, width=280):
    '''
    Resize something embedded in an object tag to have a mobile-friendly width

    If elem contains (or is) a OBJECT element, set its width to a
    mobile-friendly value.  This is handled by deleting the height
    attribute, if it is present; and setting or adding a width
    attribute with the indicated value.  This is done for both the
    "object" tag, and also any "embed" tag that may be present inside.

    TODO: This will operate on only the first object; if there are
    several object elements within, those beyond the first will be
    ignored.  Best thing is probably to just find and operate on all
    of them.

    TODO: If the original element defines a height attribute, rather
    than elimitating it, better to read it, can calculate a new
    proportional value, so that the height/width ratio is the same
    before and after the transformation.
    
    '''
    object_elem = findonetag(elem, 'object')
    if object_elem is not None:
        _setwidth(object_elem, width)
        embed_elem = object_elem.find('.//embed')
        if embed_elem is not None:
            _setwidth(embed_elem, width)

def resizeiframe(elem, width=280):
    '''
    Resize an iframe to have a mobile-friendly width

    If elem contains (or is) an iframe element, set its width to a
    mobile-friendly value.  This is handled by deleting the height
    attribute, if it is present; and setting or adding a width
    attribute with the indicated value.  This is done for both the
    "object" tag, and also any "embed" tag that may be present inside.

    This was originally created for the resizing of iframe-based
    embedded Youtube videos.

    TODO: see TODOs on resizeobject, which are mostly relevant to this filter

    '''
    iframe_elem = findonetag(elem, 'iframe')
    if iframe_elem is not None:
        _setwidth(iframe_elem, width)

def omit(elem, xpaths=None, csspaths=None):
    '''
    Omit child element(s), identified by XPath or CSS path

    The elements identified will be removed if they exist in as a
    child of the element.  If the do not exist, this filter will
    silently do nothing.

    xpaths and csspaths are each a list of 0 or more strings.  Each
    string specifies a child element to omit, identified by their
    xpath expression, or their css path, respectively.  If either
    argument is unspecified, the default is an empty list.  You have
    to supply at least one string between the two.

    @param xpaths : XPath expressions defining elements to omit
    @type  xpaths : list of str

    @param csspaths : CSS path expressions defining elements to omit
    @type  csspaths : list of str
    
    '''
    from lxml.cssselect import CSSSelector
    if xpaths is None:
        xpaths = []
    if csspaths is None:
        csspaths = []
    assert len(xpaths) > 0 or len(csspaths) > 0, 'You must specify at least one XPath or CSS path expression'
    for xpath in xpaths:
        for child in elem.xpath(xpath):
            child.drop_tree()
    for csspath in csspaths:
        sel = CSSSelector(csspath)
        for child in sel(elem):
            child.drop_tree()
    
from .tables import (
    table2divrows,
    table2divs,
    table2divgroups,
    )

COMMON_FILTERS = [
    noinlinestyles,
    noevents,
    nomiscattrib,
    ]

