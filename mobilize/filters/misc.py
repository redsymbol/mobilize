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
    from urlparse import urlparse
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
