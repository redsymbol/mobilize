'''
Code related to image optimization

CONCEPTS

Throughout this code, we'll often be specifying the size of an image
as a pair of integers.  The convention is that the first number is
ALWAYS the width, and the second is always the height.  Following this
just makes it so much more maintainable, dodging lots of silly bugs.

Semantically there are two kinds of sizes: the "tag" width/height; and
the "data" width/height.  The tag size refers to the values of the
"width" and "height" attributes in the HTML img tag.  In contrast, the
data size refers to the *measured* dimensions of the image that is
actually downloaded.

For any width or height variable, the valid value is either a positive
integer; or, the value None. None means that the value is not known or
unspecified.  For a tag, that means the img tag in the HTML doesn't
have that attribute; for the data, it means we haven't yet measured
the dimensions of the source image.

'''

from mobilize.filters.filterbase import filterapi
from mobilize.log import logger

#: maximum image width when otherwise unspecified
DEFAULT_MAXW=300

def to_imgserve_url(url, maxw, maxh):
    '''
    Calculate the value of an imgserve URL for an image

    Both the maximum width and height are specified for scaling.  This
    is mainly to prevent off-by-one rounding errors: sometimes the
    code of this module will come up with a barely different scaled
    value of the height for a different resize width than Imagemagick
    will (which is currently used on the backend), which would
    mismatch the height attribute of the img tag in the final HTML
    document.

    So we just sidestep this by calculating the height in exactly one
    place - the new_img_sizes function in this library - and directing
    imgserve to scale both dimensions as we specify. This might lead
    to a slight distortion in aspect ratio, but is going to be subtle
    at worst, and worth the tradeoff.

    Example:
    to_imgserve_url('http://example.com/foo.png', 42, 70)
      -> '/_mwuimg/?src=http%3A%2F%2Fexample.com%2Ffoo.png&maxw=42&maxh=70'

    @param url  : URL pointing to the source image
    @type  url  : str

    @param maxw : Maximum desired width of the image
    @type  maxw : int

    @param maxh : Maximum desired height of the image
    @type  maxh : None, or int

    @return     : URL to the imgserve version of the URL
    @rtype      : str
    
    '''
    logger.debug('Converting img URL: {}'.format(url))
    from urllib.parse import quote
    assert maxw > 0, maxw
    imgserve_url = '/_mwuimg/?src={src}&maxw={maxw}'.format(src=quote(url, safe=''), maxw=str(maxw))
    if maxh is not None:
        imgserve_url += '&maxh=' + str(maxh)
    return imgserve_url

def scale_height(start_width, start_height, end_width):
    '''
    Scale a height value

    Given starting height and width values, and an ending width,
    calculate the proportional ending height.

    @param start_width  : starting width
    @type  start_width  : int

    @param start_height : starting height
    @type  start_height : int

    @param end_width    : ending width
    @type  end_width    : int
    
    @return             : scaled ending height
    @rtype              : int
    
    '''
    assert start_width
    assert start_height
    assert end_width
    return int(round(start_height * end_width / start_width))

def scale_width(start_width, start_height, end_height):
    '''
    @param start_width  : starting width
    @type  start_width  : int

    @param start_height : starting height
    @type  start_height : int

    @param end_height   : ending height
    @type  end_height   : int
    
    @return             : scaled ending width
    @rtype              : int
    
    '''
    assert start_width
    assert start_height
    assert end_height
    return int(round(start_width * end_height / start_height))

@filterapi
def to_imgserve(elem):
    '''
    Convert all img tags within the tree to point to imgserve source, as needed

    This filter access the imgserve database of image source values.
    When the height and width data is available for an image, that
    info will be used to decide whether we need to scale the image for
    the mobile device.  If we do, the img tag's src attribute is
    modified appropriately.
    
    '''
    from imgserve import (
        normalize_img_size,
        ImgDb,
        )
    imgdb = ImgDb()
    for img_elem in elem.iter(tag='img'):
        if 'src' in img_elem.attrib:
            if elem.attrib.get('src', '').lower().startswith('data:'):
                logger.error('Should not be converting data URL: {}'.format(elem.attrib.get('src', '')))
                continue
            img_data = imgdb.get(img_elem.attrib['src']) or {}
            tag_width = normalize_img_size(img_elem.attrib.get('width', None))
            tag_height = normalize_img_size(img_elem.attrib.get('height', None))
            data_width = img_data.get('width', None)
            data_height = img_data.get('height', None)
            sizes = new_img_sizes(tag_width, tag_height, data_width, data_height)
            # need to cast size values to type str, for lxml
            for k, v in sizes.items():
                sizes[k] = str(v)
            for k in 'width', 'height':
                if k in img_elem.attrib:
                    del img_elem.attrib[k]
            img_elem.attrib.update(sizes)
            if convertable(img_elem, data_width):
                if 'height' in img_elem.attrib:
                    maxh = int(img_elem.attrib['height'])
                else:
                    maxh = None
                img_elem.attrib['src'] = to_imgserve_url(img_elem.attrib['src'],
                                                         int(img_elem.attrib['width']),
                                                         maxh)

def convertable(img_elem, data_width):
    '''
    Determine whether this is an image whose src attribute should be
    converted to an imgserve URL.

    Note carefully the dimension types.  data_width is either an
    integer, or None.  The width and heigh attributes of img_elem, if
    they are present, are strings.

    @param img_elem   : The image element being considered
    @type  img_elem   : lxml.html.HtmlElement

    @param data_width : The measured width of he source image in pixels; or None if that is not known
    @type  data_width : int > 0; or, None
    
    @return           : True iff this img's source attribute should be converted to an imgserve URL
    @rtype            : bool
    
    '''
    from imgserve import normalize_img_size
    if data_width is not None:
        assert type(data_width) == int, type(data_width)
    if 'width' in img_elem.attrib:
        if data_width is None:
            return True
        tag_width = normalize_img_size(img_elem.attrib.get('width', None))
        if tag_width != data_width:
            return True
    return False

def new_img_sizes(tag_width,
                  tag_height,
                  measured_width,
                  measured_height,
                  default_maxw = DEFAULT_MAXW):
    '''
    Calculate new height and width values of an image for the mobile view.
    
    Any function parameter can be "None" if undefined.  The returned
    dictionary may be empty, or have a 'width' key, a 'height' key, or
    both.  If a key is missing, that means the img tag in the mobile
    view should omit that attribute.

    @param tag_height      : Height value on img tag in source HTML document
    @type  tag_height      : None or int > 0
    
    @param tag_width       : Width value on img tag in source HTML document
    @type  tag_width       : None or int > 0
    
    @param measured_height : Actual height value of source image in pixels, if known
    @type  measured_height : None or int > 0
    
    @param measured_width  : Actual width value of source image in pixels, if known
    @type  measured_width  : None or int > 0

    @param default_maxw    : Default maximum width to use for an image
    @type  default_maxw    : int

    @return                : a dict with 0 or 1 'width' keys, and 0 or 1 'height' keys
    @rtype                 : dict
    
    '''
    assert tag_width is None or (tag_width > 0), tag_width
    assert tag_height is None or (tag_height > 0), tag_height
    assert measured_width is None or (measured_width > 0), measured_width
    assert measured_height is None or (measured_height > 0), measured_height
    
    have_all_measured = (measured_width is not None) and (measured_height is not None)
    have_all_tag = (tag_width is not None) and (tag_height is not None)
    height = tag_height
    width  = tag_width
    # Whether we consider the aspect ratios of the measured and tag
    # dimensions to be equivalent.  Valued True, False, or None - the
    # latter if it's undefined because any piece of info is undefined.
    ar_equal = None

    done = False
    if have_all_tag and have_all_measured:
        ar_measured = measured_width / measured_height
        ar_tag = tag_width / tag_height
        ar_equal = abs((ar_measured - ar_tag) / (ar_measured + ar_tag)) < 0.001
        if ar_equal:
            if width > measured_width:
                width = measured_width
                assert height >= measured_height
                height = measured_height
    if have_all_measured:
        if height is None:
            if tag_width == measured_width:
                height = measured_height
            elif tag_width is not None:
                height = scale_height(measured_width, measured_height, tag_width)
        if width is None:
            if tag_height == measured_height:
                width = measured_width
            elif tag_height is not None:
                width = scale_width(measured_width, measured_height, tag_height)
    if (width is not None) and (width > default_maxw):
        if have_all_measured:
            height = scale_height(measured_width, measured_height, default_maxw)
        elif height is not None:
            height = scale_height(width, height, default_maxw)
        width = default_maxw
    sizes = dict()
    if width is not None:
        sizes['width'] = width
    if height is not None:
        sizes['height'] = height
    return sizes
