'''
Filters : functions that process and modify HTML snippets

A filter is a function designed to alter or process a block of
HTML-like code in some useful way.  It takes as input a string, meant
to be a snippet of HTML, and returns another string.  The returned
string may in general be the same thing as the input, but often it is
modified in some way.

'''

def noinlinestyles(htmlstr):
    '''
    Remove any inline styles on all tags

    @param htmlstr : An HTML snippet
    @type  htmlstr : str

    @return        : The same HTML snippet with all "style" attributed deleted
    @rtype         : str
    
    '''
    from lxml import html
    doc = html.fromstring(htmlstr)
    for elem in doc.iter():
        if 'style' in elem.attrib:
            del elem.attrib['style']
    return html.tostring(doc)
