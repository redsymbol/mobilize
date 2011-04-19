_protocols = (
    'http',
    'https',
    'ftp',
    )
def absimgsrc(elem, desktop_url):
    '''
    Modify img "src" relative paths to be absolute

    This finds all img elements in the parent element, and inspects
    the value of their src attribute.  If the src is a relative path,
    and it is not a mobile-site image as indicated by a URL prefix of
    mobilize.util.STATIC_URL, then the 
    '''
    fiximg = _link_converter('src', desktop_url)
    if 'img' == elem.tag:
        fiximg(elem)
    else:
        for img_elem in elem.iterfind('.//img'):
            fiximg(img_elem)

def abslinkfilesrc(elem, desktop_url, extensions):
    '''
    Make the targets of links to specific file extensions absolute on desktop site

    This will scan through all the A tags in the element, finding
    those which link to files of a specific type (as discerned by
    their file extension in the link).  Matching links are converted
    to be full absolute URLS, pointing to the file on the desktop site.

    For example, suppose the document at http://m.example.com/about/papers.html
    on the mobile site contains the following snippet:

    -- begin --
    <p><a href="marketstudy.xls">Market Study</a></p>
    <p><a href="/whitepapers/fill-in-blank.doc">Make your own white paper!</a></p>
    <p><a href="/whitepapers/widgets.pdf">Widget White Paper</a></p>
    -- end --

    And suppose this filter is applied with
    desktop_url='http://example.com/about/papers.html' and extensions=['.xls', '.pdf'].
    The html is transformed to:
    
    -- begin --
    <p><a href="http://example.com/about/marketstudy.xls">Market Study</a></p>
    <p><a href="/whitepapers/fill-in-blank.doc">Make your own white paper!</a></p>
    <p><a href="http://example.com/whitepapers/widgets.pdf">Widget White Paper</a></p>
    -- end --

    NOTE: The extensions need to contain the dot, e.g. ".pdf", not
    "pdf".

    @param desktop_url : Full URL of the corresponding current page on the desktop site
    @type  desktop_url : str

    @param extensions : Filename extensions of href values to convert
    @type  extensions : list of str
    
    '''
    fixanchor = _link_converter('href', desktop_url)
    def check_anchor(anchor):
        for ext in extensions:
            if anchor.attrib.get('href', '').endswith(ext):
                fixanchor(anchor)
    if 'a' == elem.tag:
        check_anchor(elem)
    else:
        for anchor in elem.iterfind('.//a'):
            check_anchor(anchor)
    
def _link_converter(attribute, desktop_url):
    '''
    Create a function that will convert link attributes to absolute desktop urls

    This utility creates and returns a function that can be applied to
    an element, to convert URL attribute which is relative to a full
    absolute URL on the desktop site.  Examples include the 'src'
    attribute of an IMG tag, or the 'href' attribute of an A tag.

    If the value of the URL attribute is already absolute, or starts
    with mobilize.util.STATIC_URL, that value will be unchanged.

    @param attribute   : The name of the element's attribute to inspect, and possibly change
    @type  attribute   : str

    @param desktop_url : The URL of the current page's corresponding desktop version
    @type  desktop_url : str

    @return            : link converter
    @rtype             : function

    '''
    from mobilize.util import urlbase
    from urllib.parse import urlparse
    def is_desktop_relative(src):
        from mobilize.util import STATIC_URL
        if src.startswith(STATIC_URL):
            return False
        for protocol in _protocols:
            if src.startswith(protocol + '://'):
                return False
        return True
    parsed = urlparse(desktop_url)
    desktop_root_url = '%s://%s' % (parsed.scheme, parsed.netloc)
    base_url = urlbase(desktop_url)
    def convert(elem):
        if attribute in elem.attrib:
            if is_desktop_relative(elem.attrib[attribute]):
                if elem.attrib[attribute].startswith('/'):
                    elem.attrib[attribute] = desktop_root_url + elem.attrib[attribute]
                else:
                    elem.attrib[attribute] = base_url + elem.attrib[attribute]
    return convert
