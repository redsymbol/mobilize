# Copyright 2010-2011 Mobile Web Up. All rights reserved.
'''
Filters designed to omit or remove certain parts of the source HTML
'''

from .filterbase import filterapi
from mobilize.util import (
    findonetag,
    )

# Filters

@filterapi
def nomiscattrib_if(root_elem, predicate):
    '''
    Apply the nomiscattrib_one filter to certain child elements

    predicate is a callable taking a single HtmlElement instance
    argument, and returns True iff the nomiscattrib_one filter is to
    be applied.
    '''
    if predicate(root_elem):
        nomiscattrib_one(root_elem)
    for elem in root_elem.iterdescendants():
        if predicate(elem):
            nomiscattrib_one(elem)
    
@filterapi
def nomiscattrib(root_elem):
    '''
    Apply the nomiscattrib_one filter to all child elements
    '''
    nomiscattrib_one(root_elem)
    for elem in root_elem.iterdescendants():
        nomiscattrib_one(elem)
        
    # Attributes we want to remove from all elements
_NOMISCATTRIB_UNIVERSALS = {
        'align',
        'border',
        'valign',
        'style',
        }

@filterapi
def nomiscattrib_one(elem, universals = _NOMISCATTRIB_UNIVERSALS):
    '''
    Remove certain miscellaneous unwanted attributes
    
    As a side effect, if the passed element has any of the following
    attributes, then that attribute is removed:
    
     * align
     TODO: update this list
    
    @param elem : an html element
    @type  elem : lxml.html.HTMLElement

    '''
    # Attributes we want to remove only from certain tags
    # tag name -> list of attributes to remove
    singles = {
        'a' : ['target'],
        }
    def toremoves():
        for universal in universals:
            yield universal
        if elem.tag in singles:
            for single in singles[elem.tag]:
                yield single
    omitattrib_one(elem, toremoves())

@filterapi
def noevents_one(elem):
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

@filterapi
def noevents(parent, xpath):
    '''
    Apply the noevents_one filter on sub-elements matching expression

    '''
    for elem in parent.iterfind(xpath):
        noevents_one(elem)
    
@filterapi
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

@filterapi
def noattribs(parent_elem, tags, attribs):
    '''
    Will recursively delete the indicated attributes from elements of
    the given tag names.

    @param parent_elem : Containing element to hunt within
    @type  parent_elem : lxml.html.HtmlElement
    
    @param tag         : Name of tags (elements) to remove attributes from
    @type  tag         : list of str

    @param attribs     : Attributes of the tags to remove
    @type  attribs     : list of str
    
    '''
    def delattrib(elem):
        for key in attribs:
            if key in elem.attrib:
                del elem.attrib[key]
    if parent_elem.tag in tags:
        delattrib(parent_elem)
    for tag in tags:
        for elem in parent_elem.iterfind('.//%s' % tag):
            delattrib(elem)

@filterapi
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

@filterapi
def squeezebr(elem):
    '''
    Filter that collapses several sequential BR tags into a single BR tag

    Anywhere within elem that 2 or more BR tags occur with only
    whitespace separating them, they will be compressed to a single BR
    tag.  This can be very useful with HTML that aggresively uses
    break tags for layout.
    '''
    for br_elem in elem.findall('.//br'):
        if br_elem.tail is None or '' == br_elem.tail.strip():
            next = br_elem.getnext()
            if next is not None and 'br' == next.tag:
                br_elem.drop_tree()

@filterapi
def noinputsize(elem):
    '''
    strip the inline size attributes from textual form inputs

    This will remove the following attributes from the following tags:

     - SIZE from INPUT
     - COLS and ROWS from TEXTAREA
    '''
    for input_elem in elem.findall('.//input'):
        if 'size' in input_elem.attrib:
            del input_elem.attrib['size']
    for textarea_elem in elem.findall('.//textarea'):
        for attrib in {'cols', 'rows'}:
            if attrib in textarea_elem.attrib:
                del textarea_elem.attrib[attrib]

@filterapi
def nobr(elem, space=True):
    '''
    Remove all BR tags from the innerHTML of an element.

    If space is True, ensure at least one space is present after the
    BR tag's position (before dropping), inserting if necessary.  This
    is useful because sometimes only a BR tag is used to separate
    words that we don't want to run together (i.e., we want
    "buy<br>now" to become "buy now", not "buynow").

    If space is False, the br tags are simply dropped.

    @param space : If True, leave a space character behind
    @type  space : bool
    
    '''
    for br_elem in elem.iterfind('.//br'):
        if space:
            if br_elem.tail is None:
                br_elem.tail = ' '
            elif not br_elem.tail.startswith(' '):
                br_elem.tail = ' ' + br_elem.tail 
        br_elem.drop_tree()

@filterapi
def omitattrib_one(elem, toremove):
    '''
    Omit the indicated attributes from an element.

    @param elem     : Element to trim attributes from
    @type  elem     : HtmlElement

    @param toremove : Names of attributes to kill
    @type  toremove : list of str
    
    '''
    for item in toremove:
        if item in elem.attrib:
            del elem.attrib[item]

# Supporting code
def applyall_if(root_elem, filt, predicate):
    '''
    Apply a filter to certain child elements

    predicate is a callable taking a single HtmlElement instance
    argument, and returns True iff the nomiscattrib_one filter is to
    be applied.
    '''
    
