from lxml import html

#: Default prefix used for all mobile-site CSS identifiers
MWU_PREFIX = 'mwu-'
#: Default CSS identifier prefix used for extracted elements (i.e, rendered components)
ELEMENT_NAME = MWU_PREFIX + 'elem'

def classvalue(*extra_class_suffixes):
    '''
    Calculate the class argument for an extracted element

    This handles the bureaucratic details of constructing the correct
    value of the "class" attribute.

    By policy, every class name needs to start with
    common.ELEMENT_NAME (see classname() below).  extra_class_suffixes
    will be the suffix of the additional class names.  Examples:
    (assuming ELEMENT_NAME is "mwu-elem")

    classvalue() -> "mwu-elem"
    classvalue("alpha") -> "mwu-elem mwu-elem-alpha"
    classvalue("alpha", "beta") -> "mwu-elem mwu-elem-alpha mwu-elem-beta"

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

def fullsiteurl(mobileurl, mobiledomain, fullsitedomain):
    '''
    Generates a full site URL link

    This is the link the mobile site visitor clicks on to specify they
    prefer the desktop view.
    
    '''
    s = mobileurl.replace(mobiledomain, fullsitedomain, 1)
    if '?' in s:
        s += '&'
    else:
        s += '?'
    s += 'mredir=0'
    return s

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

def phone_href(phone):
    '''
    Create the HREF for a click-to-call link

    Phone number is a string in any common format, e.g. 415-245-3234,
    1.800.218.3141, etc.

    @param phone : Phone number
    @type  phone : str

    @return : tel link HREF
    @rtype  : str
    
    '''
    digits = ''.join(c for c in phone if c in '0123456789')
    if len(digits) == 10:
        digits = '1' + digits
    return 'tel:+' + digits

def urlbase(url):
    '''
    Determine the base of a URL

    The base of a URL is defined as the absolute prefix of relative
    URLs within the document.  For example, suppose a document whose
    URL is http://example.com/fruit/lemons.html contains an image
    whose SRC attribute is "Images/sliced-lemons.png".  The absolute
    path of this image would be
    http://example.com/fruit/Images/sliced-lemons.png.  Thus, the base
    URL for this document is http://example.com/fruit/.

    By definition, base URLs will always end with a trailing slash.
    Base URLs are always absolute.

    @param url : URL of document
    @type  url : str

    @return    : base URL
    @rtype     : str
    
    '''
    from urlparse import urlparse
    parsed = urlparse(url)
    assert '' != parsed.scheme
    parts = parsed.path.lstrip('/').split('/')
    if parsed.path in ('', '/') or len(parts) < 2:
        basepath = '/'
    elif parsed.path.endswith('/'):
        basepath = parsed.path
    else:
        basepath = '/' + '/'.join(parts[:-1]).strip('/') + '/'
    return '%s://%s%s' % (parsed.scheme, parsed.netloc, basepath)
