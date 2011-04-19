_protocols = (
    'http',
    'https',
    'ftp',
    )
def _is_desktop_relative(src):
    from mobilize.util import STATIC_URL
    if src.startswith(STATIC_URL):
        return False
    for protocol in _protocols:
        if src.startswith(protocol + '://'):
            return False
    return True

def absimgsrc(elem, desktop_url):
    '''
    Modify img "src" relative paths to be absolute

    This finds all img elements in the parent element, and inspects
    the value of their src attribute.  If the src is a relative path,
    and it is not a mobile-site image as indicated by a URL prefix of
    mobilize.util.STATIC_URL, then the 
    '''
    from mobilize.util import urlbase
    from urllib.parse import urlparse
    parsed = urlparse(desktop_url)
    desktop_root_url = '%s://%s' % (parsed.scheme, parsed.netloc)
    base_url = urlbase(desktop_url)
    def fiximg(img_elem):
        if 'src' in img_elem.attrib:
            if _is_desktop_relative(img_elem.attrib['src']):
                if img_elem.attrib['src'].startswith('/'):
                    img_elem.attrib['src'] = desktop_root_url + img_elem.attrib['src']
                else:
                    img_elem.attrib['src'] = base_url + img_elem.attrib['src']
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
    from mobilize.util import urlbase
    from urllib.parse import urlparse
    parsed = urlparse(desktop_url)
    desktop_root_url = '%s://%s' % (parsed.scheme, parsed.netloc)
    base_url = urlbase(desktop_url)
    def replace_href(anchor):
        if _is_desktop_relative(anchor.attrib['href']):
            if anchor.attrib['href'].startswith('/'):
                anchor.attrib['href'] = desktop_root_url + anchor.attrib['href']
            else:
                anchor.attrib['href'] = base_url + anchor.attrib['href']
    def check_anchor(anchor):
        for ext in extensions:
            if anchor.attrib.get('href', '').endswith(ext):
                replace_href(anchor)
    if 'a' == elem.tag:
        check_anchor(elem)
    else:
        for anchor in elem.iterfind('.//a'):
            check_anchor(anchor)
    
