'''
Filters that operate on HTML tables

'''

import re
from mobilize.util import (
    findonetag,
    htmlelem,
    replace_child,
    )

# Supporting code

class Spec:
    '''
    A specification of tables cells

    This is used by many of the table filters to define exactly which
    table cells (TD elements) to operate on.

    If defined, the function lastfilter is applied to the extracted
    element before it is packed into a div.  lastfilter is a function
    that takes one argument - an HtmlElement instance - and modifies
    it in place.

    TODO: would like to be able to specify 'grab all cells in columns 0 and 2' without specifying the exact number of rows; makes for faster development, and a more robust filter if the desktop site adds or deletes rows
    
    '''
    def __init__(self,
                 idname,
                 rowstart=None,
                 colstart=None,
                 rowend=None,
                 colend=None,
                 classname=None,
                 lastfilter=None,
                 ):
        self.idname = idname
        self.rowstart = rowstart
        self.colstart = colstart
        self.rowend = rowend
        self.colend = colend
        self.classname = classname
        self.lastfilter = lastfilter

def cell_lookup(table_elem):
    '''
    Builds a lookup mapping of cells in an TABLE element

    Returns a dictionary mapping zero-based (rownum, colnum) pairs to
    TD HtmlElement instances.

    TODO: This algorithm is O(num_rows*num_cols), in time and space, so it'd be good to substitute a more scaleable approach at some point

    '''
    cells = {}
    assert 'table' == table_elem.tag, table_elem.tag
    rownum, colnum = 0, 0
    base_elem = rowsparent(table_elem)
    for rownum, row_elem in enumerate(base_elem.findall('./tr')):
        for colnum, cell_elem in enumerate(row_elem.findall('./td')):
            cells[(rownum, colnum)] = cell_elem
    return cells

def rowsparent(table_elem):
    '''
    Finds the content root of a table element, i.e. immediate parent of first TR tag
    
    This handles an ambiguitiy in real-world HTML, where TABLE tags
    are supposed to contain a TBODY element, but often do not.  If the
    table_elem directly contains the TR lists, then return table_elem.
    If not, and these are contained by a tbody child, return that
    element instead.

    @param table_elem : Table element
    @type  table_elem : HtmlElement

    @return           : immediate parent of TR elements
    @rtype            : HtmlElement
    
    '''
    assert table_elem.tag == 'table', table_elem.tag
    tbody_elem = table_elem.find('tbody')
    if tbody_elem is not None:
        return tbody_elem
    return table_elem
    
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

# Filters

def table2divgroups(elem, specmap, omit_whitespace=True):
    '''
    Extract blocks arranged in a table grid as more semantic elements

    Table based layouts sometimes lead to a grid of elements
    semantically spanning some set of rows and columns.  This filter
    helps extract them into a clearer semantic organization.

    Let's try to make this concrete.  Consider this html:

    <table>
      <tbody>
        <tr>
          <td>CONTACT US</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
        <tr>
          <td>123 Main Str</td>
          <td>&nbsp;</td>
          <td>OUR TEAM</td>
          <td>&nbsp;</td>
        <tr>
          <td>Springfield, IL</td>
          <td>&nbsp;</td>
          <td>Mike Smith</td>
          <td><img src="/mike-smith.jpg"/></td>
        <tr>
          <td>1-800-BUY-DUFF</td>
          <td>&nbsp;</td>
          <td>Jen Jones</td>
          <td><img src="/jen-jones.jpg"/></td>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>Scruffy</td>
          <td><img src="/scruffy-the-dog.jpg"/></td>
        <tr>
      </tbody>
    </table>

    Schematically, this would render as something like this (with ___
    indicating a content-free TD cell):

    CONTACT US       ___  ___         ___
    123 Main Str     ___  OUR TEAM    ___
    Springfield, IL  ___  Mike Smith  <img src="/mike-smith.jpg"/>
    1-800-BUY-DUFF   ___  Jen Jones   <img src="/jen-jones.jpg"/>
    ___              ___  Scruffy     <img src="/scruffy-the-dog.jpg"/>

    There are two clear semantic elements here.  From a mobile design
    perspective, it would be great to parse them more like this:
    
    <div class="mwu-elem-table2divgroups-group" id="mwu-elem-contact">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>

    ... and:
    
    <div class="mwu-elem-table2divgroups-group" id="mwu-elem-ourteam">
      <div>
        <div>OUR TEAM</div>
      </div>
      <div>
        <div>Mike Smith</div>
        <div><img src="/mike-smith.jpg"/></div>
      </div>
      <div>
        <div>Jen Jones</div>
        <div><img src="/jen-jones.jpg"/></div>
      </div>
      <div>
        <div>Scruffy</div>
        <div><img src="/scruffy-the-dog.jpg"/></div>
      </div>
    </div>

    That's exactly what this filter can do.

    You'll need to specify what the semantic groups are, and how to
    extract them from a table grid.  The specmap argument is a list of
    Spec instances.  Each spec object defines a square of cells, from
    1 or more rows and 1 or more columns in the source table.  It also
    defines a DOM ID name (equivalent to 'mwu-elem-contact' and
    'mwu-elem-ourteam') above.  See the Spec class documentation for
    more details, but briefly, one way to define a group of cells is
    with these four numbers:
    
      (tr_start, td_start, tr_end, td_end)

    These integers are 0-based indices of the row and column.  So a
    specmap for the above would read:

    specmap = [
      Spec(idname('contact'), 0, 0, 3, 0)),
      Spec(idname('ourteam'), 1, 2, 4, 3)),
    ]

    By default, any TD cells that would render as whitespace in the
    browser are omitted. Set omit_whitespace=False if you don't want
    these cells discarded.

    TODO: make the above paragraph true even if a TD element contains, say, an empty SPAN

    If the extracted cells are one-dimensional (i.e. a single column
    or row), the group will be a list of DIVs (as in the "contact us"
    example). But if the cells extend over more than one row and
    column in the source table, they will be organized in divs by row,
    as in the "our team" example.

    @param elem            : Element to operate on
    @type  elem            : lxml.html.HtmlElement

    @param specmap            : Specification of what groups of cells to extract
    @type  specmap            : list of (key, value) tuples

    @param omit_whitespace : Whether to omit cells just containing content that would render as whitespace in the browser
    @type  omit_whitespace : bool
    
    '''
    table_elem = findonetag(elem, 'table')
    return _table2divgroups(elem, table_elem, specmap, omit_whitespace)

def _table2divgroups(elem, table_elem, specmap, omit_whitespace=True):
    import copy
    from lxml import html
    assert table_elem.tag == 'table', table_elem.tag
    cells = cell_lookup(table_elem)
    groups = []
    for spec in specmap:
        groupid = spec.idname
        classvalue = 'mwu-elem-table2divgroups-group'
        if spec.classname is not None:
            classvalue += ' ' + spec.classname
        group_elem = htmlelem(attrib={
                'class' : classvalue,
                'id'    : groupid,
                })
        assert spec.rowend >= spec.rowstart
        assert spec.colend >= spec.colstart
        wrap_rows = (spec.colend > spec.colstart) and (spec.rowend > spec.rowstart) # whether to wrap cells from the same TR tag in their own DIV
        for ii in range(spec.rowstart, spec.rowend+1):
            cell_elems = []
            for jj in range(spec.colstart, spec.colend+1):
                td_elem = cells.get((ii, jj), None)
                if td_elem is None:
                    continue # Could be a colspan issue.  Just skip over to next found cell
                if omit_whitespace and elementempty(td_elem):
                    continue # skip over this empty cell
                cell_elem = copy.deepcopy(td_elem)
                for k in cell_elem.attrib:
                    del cell_elem.attrib[k]
                cell_elem.tag = 'div'
                cell_elems.append(cell_elem)
            if wrap_rows:
                append_elem = htmlelem()
                group_elem.append(append_elem)
            else:
                append_elem = group_elem # meaning, we'll just append the contents of cell_elem directly, not wrapping them in a div
            for cell_elem in cell_elems:
                append_elem.append(cell_elem)
        if not elementempty(group_elem):
            if spec.lastfilter:
                spec.lastfilter(group_elem)
            groups.append(group_elem)
    if table_elem is not None:
        groups_elem = htmlelem(attrib={'class' : 'mwu-elem-table2divgroups'})
        for group_elem in groups:
            groups_elem.append(group_elem)
        replace_child(elem, table_elem, groups_elem)

def rcmarkerbase(prefix, row=None, col=None):
    '''
    Construct a row-column marker string

    Used by some filters (e.g., table2divs and relatives) to construct
    a CSS class label that indicates a row and/or column source.  The
    returned value will be a valid CSS class name, provided the prefix
    is well-behaved.

    @param prefix : Initial part of the label
    @type  prefix : str

    @param row    : Row number (zero-based)
    @type  row    : int
    
    @param column : Column number (zero-based)
    @type  column : int

    @return       : Marker string
    @rtype        : str
    
    '''
    s = prefix
    if row is not None:
        s += '-row%s' % row
    if col is not None:
        s += '-col%s' % col
    return s

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
    def rcmarker(**kw):
        return rcmarkerbase(MARKER_BASE, **kw)
    container_elem = htmlelem(attrib={'class' : MARKER_BASE})
    if 'table' == elem.tag:
        table_elem = elem
    else:
        table_elem = elem.find('table')
    if table_elem is not None:
        root_elem = rowsparent(table_elem)
        rows = root_elem.findall('./tr')
        for rownum, row in enumerate(rows):
            cols = row.findall('./td')
            for colnum, tdelem in enumerate(cols):
                if omit_whitespace and elementempty(tdelem):
                    continue # skip over this empty cell
                cell_elem = htmlelem(text=tdelem.text)
                for colchild in tdelem:
                    anychildren = True
                    cell_elem.append(colchild)
                cell_elem.attrib['class'] = ' '.join([
                        rcmarker(row=rownum, col=colnum),
                        rcmarker(row=rownum),
                        rcmarker(col=colnum),])
                container_elem.append(cell_elem)
        replace_child(elem, table_elem, container_elem)
            
def table2divrows(elem, omit_whitespace=True):
    '''
    like table2divs, but rows are organized into their own divs.

    See the documentation of table2divs for a complete explanation.
    The method signature and return type are identical. The only
    differences are:
    
      0) The CSS class markers are prefixed by "mwu-table2divrows", not
         "mwu-table2divs" (see example below).
      1) "TD" divs generated from table cells from the same row are grouped
         into a parent "TR" div.
      2) The row marker CSS class appears in that parent "TR" div, and not
         in the child "TD" divs.

    For example, this HTML:
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

    ... will render like this:

    <div class="mwu-table2divrows">
      <div class="mwu-table2divrows-row0">
        <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">Eggs</div>
        <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Ham</div>
      </div>
      <div class="mwu-table2divrows-row1">
        <div class="mwu-table2divrows-row1-col0 mwu-table2divrows-col0">Beer</div>
        <div class="mwu-table2divrows-row1-col1 mwu-table2divrows-col1">Milk</div>
      </div>
    </div>
    
    '''
    from lxml.html import HtmlElement
    MARKER_BASE = 'mwu-table2divrows'
    def rcmarker(**kw):
        return rcmarkerbase(MARKER_BASE, **kw)
    container_elem = htmlelem(attrib={'class' : MARKER_BASE})
    if 'table' == elem.tag:
        table_elem = elem
    else:
        table_elem = elem.find('table')
    if table_elem is not None:
        root_elem = rowsparent(table_elem)
        rows = root_elem.findall('./tr')
        for rownum, row in enumerate(rows): 
            rowcontainer_elem = htmlelem(attrib={'class' : rcmarker(row=rownum)})
            cols = row.findall('./td')
            for colnum, tdelem in enumerate(cols):
                if omit_whitespace and elementempty(tdelem):
                    continue # skip over this empty cell
                cell_elem = htmlelem(text=tdelem.text)
                for colchild in tdelem:
                    anychildren = True
                    cell_elem.append(colchild)
                cell_elem.attrib['class'] = ' '.join([
                        rcmarker(row=rownum, col=colnum),
                        rcmarker(col=colnum),])
                rowcontainer_elem.append(cell_elem)
            container_elem.append(rowcontainer_elem)
        replace_child(elem, table_elem, container_elem)

def table2divgroupsgs(elem, specmapgen, omit_whitespace=True):
    '''
    Apply the table2divgroups filter with a dynamically generated spec map

    This filter is much like table2divgroups.  However, instead of
    taking a explicit spec map argument, table2divgroupsgs takes a
    callable that generates the spec map.  This callable, specmapgen,
    accepts a table element as its single argument, and returns a spec
    map.
    
    @param elem            : Element to operate on
    @type  elem            : lxml.html.HtmlElement

    @param specmapgen      : Callable that generates a spec map
    @type  specmapgen      : function: HtmlElemnt -> type(specmap)

    @param omit_whitespace : Whether to omit cells just containing content that would render as whitespace in the browser
    @type  omit_whitespace : bool
    
    '''
    table_elem = findonetag(elem, 'table')
    specmap = specmapgen(table_elem)
    return _table2divgroups(elem, table_elem, specmap, omit_whitespace)

