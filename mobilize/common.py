from lxml import html

MWU_PREFIX = 'mwu-'
ELEMENT_NAME = MWU_PREFIX + 'melem'

def classvalue(*extra_class_suffixes):
    '''
    Calculate the class argument for an extracted element

    This handles the bureaucratic details of constructing the correct
    value of the "class" attribute.

    By policy, every class name needs to start with
    common.ELEMENT_NAME (see classname() below).
    extra_class_suffixes, will be the suffix of the additional class
    names.  Examples: (assuming ELEMENT_NAME is "mwu-melem")

    classvalue() -> "mwu-melem"
    classvalue("alpha") -> "mwu-melem mwu-melem-alpha"
    classvalue("alpha", "beta") -> "mwu-melem mwu-melem-alpha mwu-melem-beta"

    @param extra_class_suffixes : Suffixes of any additional CSS classes
    @type  extra_class_suffixes : list of string
    
    @return : Return the conforming value of the CSS class
    @rtype  : str
    
    '''
    if len(extra_class_suffixes) > 0:
        return ELEMENT_NAME + ' ' + ' '.join(map(classname, extra_class_suffixes))
    return ELEMENT_NAME

def classname(suffix=None):
    '''
    Calculate a valid CSS class name for an extracted element

    Every extracted snippet of HTML will be wrapped in a div with one
    or more CSS classes.  Such classes need to match a certain
    (prefix) pattern.  This function encapsulates that.

    Note this constructs just a single class name; the whole value of
    the tag's attribute is calculated by common.classvalue().

    @param suffix : Custom suffix to CSS class name, if any
    @type  suffix : str or None

    @return : Valid CSS class name
    @rtype  : str
    
    '''
    return _csslabel(suffix)

def idname(suffix):
    '''
    Calculate a valid CSS ID name for an extracted element

    This is meant to be the value of the "id" attribute of an
    extracted element.

    @param suffix : Custom suffix to CSS ID name
    @type  suffix : str or None

    @return : Valid CSS class id
    @rtype  : str
    
    '''
    assert suffix is not None
    return _csslabel(suffix)

def _csslabel(suffix=None):
    if suffix is not None:
        return '%s-%s' % (ELEMENT_NAME, suffix)
    return ELEMENT_NAME

def findonetag(elem, tagname):
    '''
    Finds the first tag within an element

    This returns the element, if it has the given tag name; or its
    first found child of that tag name.  If no such element is within,
    return None.

    @param elem : Element to search within
    @type  elem : lxml.html.HtmlElement

    @param tagname : Name of tag to find
    @type  tagname : str
    
    '''
    if tagname == elem.tag:
        found = elem
    else:
        found = elem.find('.//' + tagname)
    return found
        
def elem2str(elem):
    '''
    Render an HTML element as a string

    @param elem : element
    @type  elem : lxml.htmlHtmlElement

    @return : HTML snippet
    @rtype  : str
    
    '''
    return html.tostring(elem, method='html')

def htmlelem(tag='div',
             children=None,
             attrib=None,
             text=None,
             ):
    '''
    Create a new HTML element

    Every argument is optional, with sensible defaults.

    @param tag      : The element's tag
    @type  tag      : str

    @param children : Children of the created element
    @type  children : list of 0 or more HtmlElement instances

    @param attrib   : Attributes of the created element (such as "class" and "id")
    @type  attrib   : dict

    @param text     : Child text
    @type  text     : str

    @return         : Created HTML element
    @rtype          : lxml.html.HtmlElement
    
    '''
    elem = html.HtmlElement()
    elem.tag = tag
    if children is not None:
        for child in children:
            elem.append(child)
    if attrib is not None:
        for k, v in attrib.iteritems():
            elem.attrib[k] = v
    if text is not None:
        elem.text = text
    return elem

