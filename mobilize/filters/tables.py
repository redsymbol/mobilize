'''
Filters that operate on tables

'''

import re
from mobilize.common import (
    findonetag,
    htmlelem,
    )

# Supporting code

class Spec(object):
    '''
    A specification of tables cells

    This is used by many of the table filters to define exactly which
    table cells (TD elements) to operate on.
    '''
    def __init__(self,
                 rowstart=None,
                 colstart=None,
                 rowend=None,
                 colend=None,
                 ):
        self.rowstart = rowstart
        self.colstart = colstart
        self.rowend = rowend
        self.colend = colend

def replace_child(parent, oldchild, newchild):
    '''
    swap out an element

    This works even if parent and oldchild are the same element.
    parent is modified in place so that the oldchild element is
    removed entirely, and newchild is put in its place.
    
    '''
    if parent == oldchild:
        # This is the root element, so we need to do a dance to replace it
        oldchild.clear()
        oldchild.tag = newchild.tag
        oldchild.text = newchild.text
        for k, v in newchild.attrib.iteritems():
            oldchild.attrib[k] = v
        for child in newchild:
            oldchild.append(child)
    else:
        oldchild.getparent().replace(oldchild, newchild)

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
    
    <div class="mwu-melem-table2divgroups-group" id="mwu-melem-contact">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>

    ... and:
    
    <div class="mwu-melem-table2divgroups-group" id="mwu-melem-ourteam">
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
    (key, value) tuples.  The keys are DOM ID names
    ('mwu-melem-contact' and 'mwu-melem-ourteam') above.  The value
    for each key is a tuple of four integers, specifying the
    "rectangle" in the table grid to extract:
    
      (tr_start, td_start, tr_end, td_end)

    These integers are 0-based indices of the row and column.  So a
    specmap for the above would read:

    specmap = [
      (idname('contact'), (0, 0, 3, 0)),
      (idname('ourteam'), (1, 2, 4, 3)),
    ]

    TODO: would like to be able to specify 'grab all cells in columns 0 and 2' without specifying the exact number of rows; makes for faster development, and a more robust filter if the desktop site adds or deletes rows.  Sanity probably requries a Spec class to encapsulate all the possibilities
    
    By default, any TD cells that would render as whitespace in the
    browser are omitted. Set omit_whitespace=False if you don't want
    these cells discarded.

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
    import copy
    from lxml import html
    table_elem = findonetag(elem, 'table')
    cells = cell_lookup(table_elem)
    groups = []
    for groupid, spec in specmap:
        group_elem = htmlelem(attrib={
                'class' : 'mwu-melem-table2divgroups-group',
                'id'    : groupid,
                })
        assert spec.rowend >= spec.rowstart
        assert spec.colend >= spec.colstart
        wrap_rows = (spec.colend > spec.colstart) and (spec.rowend > spec.rowstart) # whether to wrap cells from the same TR tag in their own DIV
        for ii in xrange(spec.rowstart, spec.rowend+1):
            cell_elems = []
            for jj in xrange(spec.colstart, spec.colend+1):
                td_elem = cells.get((ii, jj), None)
                if td_elem is None: #TODO: unit test for this
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
            groups.append(group_elem)
    if table_elem is not None:
        groups_elem = htmlelem(attrib={'class' : 'mwu-melem-table2divgroups'})
        for group_elem in groups:
            groups_elem.append(group_elem)
        replace_child(elem, table_elem, groups_elem)

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
    like table2divs, but rows are organized into their own divs
    '''

