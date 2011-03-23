'''
Filters whose job is to resize elements

'''

from mobilize.common import (
    findonetag,
    )

# Supporting code

def setwidth(elem, width):
    if 'height' in elem.attrib:
        del elem.attrib['height']
    elem.attrib['width'] = str(width)

# Filters

def resizeobject(elem, width=280):
    '''
    Resize something embedded in an object tag to have a mobile-friendly width

    If elem contains (or is) a OBJECT element, set its width to a
    mobile-friendly value.  This is handled by deleting the height
    attribute, if it is present; and setting or adding a width
    attribute with the indicated value.  This is done for both the
    "object" tag, and also any "embed" tag that may be present inside.

    TODO: This will operate on only the first object; if there are
    several object elements within, those beyond the first will be
    ignored.  Best thing is probably to just find and operate on all
    of them.

    TODO: If the original element defines a height attribute, rather
    than elimitating it, better to read it, can calculate a new
    proportional value, so that the height/width ratio is the same
    before and after the transformation.
    
    '''
    object_elem = findonetag(elem, 'object')
    if object_elem is not None:
        setwidth(object_elem, width)
        embed_elem = object_elem.find('.//embed')
        if embed_elem is not None:
            setwidth(embed_elem, width)

def resizeiframe(elem, width=280):
    '''
    Resize an iframe to have a mobile-friendly width

    If elem contains (or is) an iframe element, set its width to a
    mobile-friendly value.  This is handled by deleting the height
    attribute, if it is present; and setting or adding a width
    attribute with the indicated value.  This is done for both the
    "object" tag, and also any "embed" tag that may be present inside.

    This was originally created for the resizing of iframe-based
    embedded Youtube videos.

    TODO: see TODOs on resizeobject, which are mostly relevant to this filter

    '''
    iframe_elem = findonetag(elem, 'iframe')
    if iframe_elem is not None:
        setwidth(iframe_elem, width)

