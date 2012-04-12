# Copyright 2010-2012 Mobile Web Up. All rights reserved.
'''
Code related to image optimization
'''
from mobilize.filters.filterbase import filterapi
import re

#: maximum image width when otherwise unspecified
DEFAULT_MAXW=300

# For recognizing the leading integer specified in a height/width value string
_IMG_SIZE_INT_RE = re.compile(r'^\s*(\d+)')

def to_imgserve_url(url, maxw):
    '''
    Calculate the value of an imgserve URL for an image

    Example:
    to_imgserve_url('http://example.com/foo.png', 42)
      -> '/_mwuimg/?src=http%3A%2F%2Fexample.com%2Ffoo.png&maxw=42'

    @param url  : URL pointing to the source image
    @type  url  : str

    @param maxw : Maximum desired width of the image
    @type  maxw : int

    @return     : URL to the imgserve version of the URL
    @rtype      : str
    
    '''
    from urllib.parse import quote
    if maxw <= 0:
        maxw = DEFAULT_MAXW
    return '/_mwuimg/?src={src}&maxw={maxw}'.format(src=quote(url, safe=''), maxw=str(maxw))

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
    import imgserve
    imgdb = imgserve.ImgDb()
    for img_elem in elem.iter(tag='img'):
        if 'src' in img_elem.attrib:
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
            if 'width' in img_elem.attrib:
                if data_width is None or img_elem.attrib['width'] != data_width:
                    img_elem.attrib['src'] = to_imgserve_url(img_elem.attrib['src'], int(img_elem.attrib['width']))

def normalize_img_size(value):
    '''
    Tries to normalize the value of an img tag's "height" or "width" tag

    You'd think this would be simple, but people will put all manner
    of surprising stuff within the value of HTML attributes. This
    function will attempt to extract a valid integer value whenever
    possible.  If it cannot, return None.

    SOME SOUL-SEARCHING ON VALUES OF ZERO

    What's the best thing to do with values of 0, or negative numbers?
    Right now, if the value is not castable to a positive integer,
    it's considered invalid (i.e. the function returns None).  But
    there may be situations where that isn't what we want.  I imagine
    that somewhere/somewhen on the web, someone has an img tag
    deliberately inserted for some kind of tracking purpose, and set
    its width and/or height to 0 to prevent it from rendering.

    Whatever we do with the value of 0, it seems reasonable to treat
    negative integer values the same.  To the point of, early the
    code, saying something to the effect of, "if value < 0: value = 0".

    When the value evaluates to an integer <= 0, possibly we'll want
    omit the img tag entirely from the mobile page.  Maybe the best
    way to signal that would be to have this function/method raise a
    special exception.

    @param value : Value of the "width" or "height" attribute of an image tag
    @type  value : str

    @return      : Valid tag value, or None
    @rtype       : int, or None
    
    '''
    normed = None
    if value is not None:
        match = _IMG_SIZE_INT_RE.match(value)
        if match:
            normed = int(match.group(1))
            if normed <= 0:
                normed = None
    return normed
    
def new_img_sizes(tag_width,
                  tag_height,
                  data_width,
                  data_height,
                  default_maxw = DEFAULT_MAXW):
    '''
    Calculate new height and width values of an image for the mobile view.
    
    Any function parameter can be "None" if undefined.  The returned
    dictionary may be empty, or have a 'width' key, a 'height' key, or
    both.  If a key is missing, that means the img tag in the mobile
    view should omit that attribute.

    @param tag_height  : Height value on img tag in source HTML document
    @type  tag_height  : None or str
    
    @param tag_width   : Width value on img tag in source HTML document
    @type  tag_width   : None or str
    
    @param data_height : Actual height value of source image in pixels, if known
    @type  data_height : None or int
    
    @param data_width  : Actual width value of source image in pixels, if known
    @type  data_width  : None or int

    @param default_maxw : Default maximum width to use for an image
    @type  default_maxw : int

    @return            : a dict with 0 or 1 'width' keys, and 0 or 1 'height' keys
    @rtype             : dict
    
    '''
    height = tag_height
    width  = tag_width

    have_full_data = (data_width is not None) and (data_height is not None)
    if have_full_data:
        if height is None:
            if tag_width == data_width:
                height = data_height
            else:
                if tag_width is not None:
                    height = scale_height(data_width, data_height, tag_width)
        if width is None:
            if tag_height == data_height:
                width = data_width
            else:
                if tag_height is not None:
                    width = scale_width(data_width, data_height, tag_height)
    if width is not None and width > default_maxw:
        width = default_maxw
        height = scale_height(data_width, data_height, default_maxw)
    sizes = dict()
    if width is not None:
        sizes['width'] = width
    if height is not None:
        sizes['height'] = height
    return sizes
