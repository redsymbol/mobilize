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

Such a function is used as a primitive when iterating through a DOM tree.

'''

def filterapi(f):
    '''
    Marks a function as belonging to the filter API.  Decorator.
    '''
    f.is_filter = True
    return f

@filterapi
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

@filterapi
def nomiscattrib(elem):
    '''
    Remove certain miscellaneous unwanted attributes
    
    As a side effect, if the passed element has any of the following
    attributes, then that attribute is removed:
    
     * align
    
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

@filterapi
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

COMMON_FILTERS = [
    noinlinestyles,
    noevents,
    nomiscattrib,
    ]
