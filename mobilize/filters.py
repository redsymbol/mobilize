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

COMMON_FILTERS = [
    noinlinestyles,
    ]

def apply(htmlstr, filters=COMMON_FILTERS):
    '''
    Apply filters to an HTML snippet
    
    @param htmlstr : An HTML snippet
    @type  htmlstr : str

    @param filters : Filters to apply to the snippet
    @type  filters : list of function

    @return        : The same HTML snippet with the indicated filters applied
    @rtype         : str
    
    '''
    from lxml import html
    doc = html.fromstring(htmlstr)
    for elem in doc.iter():
        for filt in filters:
            filt(elem)
    return html.tostring(doc)
    
