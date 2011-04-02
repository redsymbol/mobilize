#!/usr/bin/env python3
import os
from lxml import html
def get_args():
    '''fetch arguments from commmand line'''
    import argparse
    parser = argparse.ArgumentParser(description='Generate an HTML list of links from a map menu.')
    parser.add_argument(
        '-i',
        '--mapimage',
        type     = str,
        default  = None,
        dest     = 'mapimage',
        help     = 'Path to map image',
        required = True,
        )
    parser.add_argument(
        '-f',
        '--image-format',
        dest     = 'imageformat',
        type     = str,
        help     = 'Format of map sub-images, with numeric index field (e.g. "foo{}.jpg" -> "foo0.jpg", "foo1.jpg", etc.)',
        required = True,
        )
    return parser.parse_args()

def findmap(html_str):
    '''
    Find the map element

    Raise an error if this HTML fragment does not contain a MAP element.

    This is normally meant to be invoked on an HTML fragment that
    contains exactly one map element.  If the fragment contains
    several, the first found is returned.

    @param html_str : HTML fragment containing a MAP tag
    @type  html_str : str

    @return         : map element
    @rtype          : lxml.html.HtmlElement
    
    '''
    elem = html.fromstring(html_str)
    if 'map' == elem.tag:
        map_elem = elem
    else:
        map_elem = elem.find('map')
    assert map_elem is not None
    return map_elem

def choicedata(map_elem, imageformat):
    '''
    Extract and calculate useful information from a map element

    This collects the raw information used to construct a meaningful
    list of mobile-friendly links.

    imageformat needs to be a Python format string that accepts
    exactly one integer field.  Something like "/path/to/foo{}.png".
    This will be rendered with a zero-based integer index
    corresponding to the link.  So the first choice would render as
    "/path/to/foo0.png", then "/path/to/foo1.png", and so on.

    TODO: ideally raise an error if the imageformat string does not include an int-compatible field.  Apparently need to implement a custom string.Formatter subclass that implements the check_unused_args method

    @param map_elem    : Map element
    @type  map_elem    : lxml.html.HtmlElement

    @param imageformat : a Python format string that can be used to generate a choice/link image path
    @type  imageformat : str

    @return            : Detailed data on possible link choices
    @rtype             : list of dict
    
    '''
    def choice(area_elem, nn):
        def a(key):
            return area_elem.attrib[key]
        imgsrc = imageformat.format(nn)
        imgfile = os.path.basename(imgsrc)
        return {
            'alt'    : a('alt'),
            'href'   : a('href'),
            'coords' : a('coords'),
            'imgsrc' : imgsrc,
            'imgfile' : imgfile,
            }
    return [choice(area_elem, nn)
            for nn, area_elem in enumerate(map_elem.iterfind('area'))]

def im_geom(coords):
    '''
    converts area tag coordinates string to imagemagick geometry string

    coords is the value of the "coords" attrib of an AREA tag,
    corresponding to one possible choice in a MAP element.

    The returned geometry string defines a subset of the map source
    image, which can be directly passed to the ImageMagick library to
    extract the clickable/touchable are of the map.

    @param coords : The value of the "coords" attribute of the area tag
    @type  coords : str

    @return       : The equivalent geometry that will extract the area from the map's source image
    @rtype        : str
    
    '''
    x1, y1, x2, y2 = map(int, coords.split(','))
    width = x2 - x1
    height = y2 - y1
    return '{}x{}+{}+{}'.format(width, height, x1, y1)

def convertcmd(coords, mapimg, outimg):
    '''
    Calculate the command-line "convert" command for generating a single choice image
    '''
    return 'convert -crop {geom} {mapimg} {outimg}'.format(
        geom   = im_geom(coords),
        mapimg = mapimg,
        outimg = outimg,
        )

if '__main__' == __name__:
    import sys
    args = get_args()
    map_elem = findmap(sys.stdin.read())
    choices = choicedata(map_elem, args.imageformat)
    htmlout = '<ul class="mwu-map2links">\n'
    for choice in choices:
        htmlout += '  <li><a href="{href}"><img src="{imgsrc}" alt="{alt}"/></a></li>\n'.format(**choice)
    htmlout += '</ul>\n'
    # convert commands
    htmlout += '<!--\n'
    for choice in choices:
        htmlout += convertcmd(choice['coords'], args.mapimage, choice['imgfile']) + '\n'
    htmlout += '-->\n'
    print(htmlout)
    

