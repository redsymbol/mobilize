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

import re
from common import findonetag

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
    '''
    def setwh(e):
        if 'height' in e.attrib:
            del e.attrib['height']
        e.attrib['width'] = str(width)
    object_elem = findonetag(elem, 'object')
    if object_elem is not None:
        setwh(object_elem)
        embed_elem = object_elem.find('.//embed')
        if embed_elem is not None:
            setwh(embed_elem)

def table2divs(elem, omit_whitespace=True):
    '''
    Transform a table into a one-dimensional sequence of DIVs

    This filter finds the most top-level table tag in the element, and
    replaces it with a list of DIVs, each of whose content was in a TD
    tag.  So for example, something like:

    <table>
      <tr>
        <td>Eggs</td>
        <td>Ham</td>
      </tr>
      <tr>
        <td>Beer</td>
        <td>Milk</td>
      </tr>
    </table>

    ... will produce something with a structure like this:

    <div class="...">Eggs</div>
    <div class="...">Ham</div>
    <div class="...">Beer</div>
    <div class="...">Milk</div>

    ATTRIBUTES

    The divs will have the following class attributes set, where R and
    C are the zero-based row and column numbers of the source TD tag:
    
      * mwu-table2divs-rowR-colC
      * mwu-table2divs-rowR
      * mwu-table2divs-colC

    So the above example would actually render out something like:
    
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-row1 mwu-table2divs-col0">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-row1 mwu-table2divs-col1">Milk</div>

    These css class "hooks" are meant to help with styling of the mobile page.

    DEPTH

    Only the parent-most table will be converted.  If any tables are
    nested inside, these will not be converted to divs.  So that
    something like this:

    <table>
      <tr>
        <td><table id="foobar">...</table></td>
        <td>Key Lime Pie</td>
      </tr>
    </table>

    ... will render as this:

    <div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0"><table id="foobar">...</table></div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Key Lime Pie</div>

    If future need justifies it, we may add a "depth" argument to this
    filter, to allow recursive table-to-div conversion.

    OMITTING CONTENT-FREE CELLS

    If omit_whitespace is True, then any TD cells that render as empty
    whitespace will be omitted from the resulting sequence of divs.
    That means any TD whose content consists of whitespace, &nbsp;
    entities, etc., as well as cells that are completely empty.

    Note that the mapping of specific TD cells to the numbering div
    classes, as described in ATTRIBUTES above, isn't affected by this;
    the numbering is just skipped over if any such cells are omitted.

    Example: a table like this:

    <table>
      <tr>
        <td>Eggs</td>
        <td></td>
      </tr>
      <tr>
        <td>     &nbsp; &#160; &nbsp; </td>
        <td>Milk</td>
      </tr>
    </table>    

    ... will render like this:
    
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">Eggs</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-row1 mwu-table2divs-col1">Milk</div>

    '''
    from lxml.html import HtmlElement
    MARKER_BASE = 'mwu-table2divs'
    def rcmarker(row=None, col=None):
        s = MARKER_BASE
        if row is not None:
            s += '-row%s' % row
        if col is not None:
            s += '-col%s' % col
        return s
    container_elem = HtmlElement()
    container_elem.tag = 'div'
    container_elem.attrib['class'] = MARKER_BASE
    if 'table' == elem.tag:
        table_elem = elem
    else:
        table_elem = elem.find('table')
    if table_elem is not None:
        tbody_elem = table_elem.find('tbody')
        if tbody_elem is not None:
            root_elem = tbody_elem
        else:
            root_elem = table_elem
        rows = root_elem.findall('./tr')
        for rownum, row in enumerate(rows):
            cols = row.findall('./td')
            for colnum, tdelem in enumerate(cols):
                if omit_whitespace and elementempty(tdelem):
                    continue # skip over this empty cell
                cell_elem = HtmlElement()
                cell_elem.tag = 'div'
                cell_elem.text = tdelem.text
                for colchild in tdelem:
                    anychildren = True
                    cell_elem.append(colchild)
                cell_elem.attrib['class'] = ' '.join([
                        rcmarker(row=rownum, col=colnum),
                        rcmarker(row=rownum),
                        rcmarker(col=colnum),])
                container_elem.append(cell_elem)
        if elem == table_elem:
            # Table is the root element, so we need to do a dance to replace it
            table_elem.clear()
            table_elem.tag = container_elem.tag
            table_elem.text = container_elem.text
            for k, v in container_elem.attrib.iteritems():
                table_elem.attrib[k] = v
            for child in container_elem:
                table_elem.append(child)
        else:
            table_elem.getparent().replace(table_elem, container_elem)
            
def table2divrows(elem, omit_whitespace=True):
    '''
    like table2divs, but rows are organized into their own divs
    '''

_ELEMENTEMPTY_WS_RE = re.compile(r'(?:\s|\n|&nbsp;|&#160;)*$', re.UNICODE | re.I)
def elementempty(elem, ignore_whitespace = True):
    '''
    True iff an element is empty.

    "Emtpy" means that it has no children, including no inner text.

    If ignore_whitespace is True, then count the cell as "empty" even
    if it has text that *renders* as whitespace in the browser.  This
    includes entities like &nbsp;, &#160;, etc.

    '''
    def is_ws(s):
        return _ELEMENTEMPTY_WS_RE.match(s) is not None
    isempty = False
    if len(elem) == 0:
        if elem.text in ('', None):
            isempty = True
        elif ignore_whitespace and is_ws(elem.text):
            isempty = True
    return isempty

COMMON_FILTERS = [
    noinlinestyles,
    noevents,
    nomiscattrib,
    ]
