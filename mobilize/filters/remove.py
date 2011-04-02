'''
Filters designed to omit or remove certain parts of the source HTML
'''

from mobilize.util import (
    findonetag,
    )

# Supporting code
# (none yet)

# Filters

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

def noeventson(parent, xpath):
    '''
    Recursively apply the noevents filter on sub-elements matching expression

    '''
    for elem in parent.iterfind(xpath):
        noevents(elem)
    
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

def noinputwidth(elem):
    '''
    strip the inline size attributes from textual form inputs

    This will remove the following attributes from the following tags:

     - SIZE from INPUT
     - COLS from TEXTAREA
    '''
    for input_elem in elem.findall('.//input'):
        if 'size' in input_elem.attrib:
            del input_elem.attrib['size']
    for textarea_elem in elem.findall('.//textarea'):
        if 'cols' in textarea_elem.attrib:
            del textarea_elem.attrib['cols']

