from .filterbase import filterapi
_protocols = (
    'http',
    'https',
    'ftp',
    )
@filterapi
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

# Default file extensions to convert to absolute links
ABSLINK_EXTENSIONS = {
    '.avi',
    '.bz2',
    '.doc',
    '.flv',
    '.gif',
    '.gz',
    '.iso',
    '.jpeg',
    '.jpg',
    '.mov',
    '.pdf',
    '.png',
    '.ppt',
    '.ps',
    '.rar',
    '.xls',
    '.zip',
    }

@filterapi
def abslinkfilesrc(elem, desktop_url, extensions = ABSLINK_EXTENSIONS, ignore_case=True):
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
    "pdf".  This gives the flexiblity for matching extensions that
    don't start with a dot.

    If ignore_case is True, ".pdf" will match both ".pdf" and
    ".PDF". Otherwise, you'd need to include bot ".pdf" and ".PDF" in
    extensions explicitly.

    @param desktop_url : Full URL of the corresponding current page on the desktop site
    @type  desktop_url : str

    @param extensions  : Filename extensions of href values to convert
    @type  extensions  : set of str

    @param ignore_case : Iff True, filename extension matching is case insensitive
    @type  ignore_case : bool
    
    '''
    fixanchor = _link_converter('href', desktop_url)
    def check_anchor(anchor):
        url = anchor.attrib.get('href', '')
        if ignore_case:
            url = url.lower()
        for ext in extensions:
            if url.endswith(ext):
                fixanchor(anchor)
    if 'a' == elem.tag:
        check_anchor(elem)
    else:
        for anchor in elem.iterdescendants('a'):
            check_anchor(anchor)

#: Form control tags (elements) modified by the formcontroltypes and formcontroltypes_one filters.
FC_TAGS = {
    'input',
    }
from mobilize.util import MWU_PREFIX
FC_PREFIX = MWU_PREFIX + 'fc-'
            
@filterapi
def formcontroltypes(root_elem):
    '''
    Apply the formcontroltypes_one filter to all relevant descendant tags 
    '''
    xpath ='.//' + '|'.join(FC_TAGS)
    for elem in root_elem.iterfind(xpath):
        formcontroltypes_one(elem)

@filterapi
def formcontroltypes_one(elem):
    '''
    Mark certain form control with a special CSS class indicating type

    This provides a hook for styling form controls by type, by setting
    a CSS class attribute defining the (tag, type) combination.  The
    format of the class name is "mwu-fc-{tagname}-{type}".  So for
    example, an <input type="checkbox"> element will become
    <input type="checkbox" class="mwu-fc-input-checkbox">.

    These CSS class hooks will be unnecessary when CSS3 type selector
    support [0] reaches saturation; we can then just style to
    "input[type=radio]", etc. instead.  As of 2011 at least, not
    enough mobile browsers support this module well enough for us to
    rely on it.

    [0] http://www.w3.org/TR/css3-selectors/#attribute-selectors
    '''
    if elem.tag in FC_TAGS:
        marker = '{}{}-{}'.format(FC_PREFIX, elem.tag, elem.attrib.get('type', ''))
    if 'class' in elem.attrib:
        elem.attrib['class'] = elem.attrib['class'] + ' ' + marker
    else:
        elem.attrib['class'] = marker

@filterapi
def relhyperlinks_full(root_elem, domains, protocols):
    '''
    Convert absolute hyperlinks to relative - full control interface

    This provides a richer interface to the engine behind the
    relhyperlinks filter, recognizing links for multiple domains and
    protocols.  For example:
      relhyperlinks_full(elem, ['www.example.com', 'example.com'], ['http', 'https'])

    @param root_elem : Root of document fragment
    @type  root_elem : HtmlElement

    @param domains   : Domain names of absolute links to convert
    @type  domains   : list of str

    @param protocols : Protocols to check for
    @type  protocols : sequence of str

    '''
    prefixes = {'{}://{}'.format(protocol, domain)
                for domain in domains
                for protocol in protocols}
    return _relhyperlinks_prefixes(root_elem, prefixes)

@filterapi
def relhyperlinks(root_elem, domain, protocol='http'):
    '''
    Convert absolute hyperlinks to relative
    
    This will cycle through the A tags in the tree, find those whose
    HREF attribute is an absolute link on the given domain, and
    convert it to a relative link.

    Some CMSs, notably Wordpress, will render the HREF attribute of A
    tags as full absolute hyperlinks, even if they are on the same
    domain.  For a mobile site, it's better if these URLs are relative
    so that someone viewing the mobile page will go to another mobile
    page when clicking on the link.  (If the href is a absolute link
    to the desktop view, at best they will have to suffer the extra
    latency of another device redirection.)

    @param root_elem : Root of document fragment
    @type  root_elem : HtmlElement

    @param domain    : Domain name of absolute links to convert
    @type  domain    : list of str

    @param protocol  : Protocol of absolute link to convert
    @type  protocol  : list of str

    '''
    return _relhyperlinks_prefixes(root_elem, {'{}://{}'.format(protocol, domain)})

# Supporting code

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
    from mobilize.util import STATIC_URL
    def is_desktop_relative(src):
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

def _relhyperlinks_prefixes(root_elem: 'lxml.html.HtmlElement', prefixes : set) -> None:
    def rewriter(link):
        for prefix in prefixes:
            if link.startswith(prefix):
                link = link[len(prefix):]
                if '' == link:
                    link = '/'
                break
        return link
    root_elem.rewrite_links(rewriter)
