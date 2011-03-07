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
  * does not return any value, and
  * operates by making any changes directly on the element as a side effect.

'''

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
        'width',
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
    
      * mwu-table2div-rowR-colC
      * mwu-table2div-rowR
      * mwu-table2div-colC

    So the above example would actually render out something like:
    
    <div class="mwu-table2div-row0-col0 mwu-table2div-row0 mwu-table2div-col0">Eggs</div>
    <div class="mwu-table2div-row0-col1 mwu-table2div-row0 mwu-table2div-col1">Ham</div>
    <div class="mwu-table2div-row1-col0 mwu-table2div-row1 mwu-table2div-col0">Beer</div>
    <div class="mwu-table2div-row1-col1 mwu-table2div-row1 mwu-table2div-col1">Milk</div>

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

    <div class="mwu-table2div-row0-col0 mwu-table2div-row0 mwu-table2div-col0"><table id="foobar">...</table></div>
    <div class="mwu-table2div-row0-col1 mwu-table2div-row0 mwu-table2div-col1">Key Lime Pie</div>

    If future need justifies it, we may add a "depth" argument to this
    filter, to allow recursive table-to-div conversion.

    OMITTING CONTENT-FREE CELLS

    If omit_whitespace is True, then any TD cells that render as empty
    whitespace will be omitted from the resulting sequence of divs.
    That means any TD whose content consists of whitespace, &nbsp;
    entities, HTML comments, etc., as well as cells that are
    completely empty.

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
        <td>     &nbsp; &nbsp; &nbsp; <!-- where's my beer?!? --> </td>
        <td>Milk</td>
      </tr>
    </table>    

    ... will render like this:
    
    <div class="mwu-table2div-row0-col0 mwu-table2div-row0 mwu-table2div-col0">Eggs</div>
    <div class="mwu-table2div-row1-col1 mwu-table2div-row1 mwu-table2div-col1">Milk</div>

    '''

def table2divrows(elem, omit_whitespace=True):
    '''
    like table2divs, but rows are organized into their own divs
    '''

COMMON_FILTERS = [
    noinlinestyles,
    noevents,
    nomiscattrib,
    ]
