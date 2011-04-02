#!/usr/bin/env python3
import os
from lxml import html
def get_args():
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
    elem = html.fromstring(html_str)
    if 'map' == elem.tag:
        map_elem = elem
    else:
        map_elem = elem.find('map')
    assert map_elem is not None
    return map_elem

def choicedata(map_elem, imgformat):
    def choice(area_elem, nn):
        def a(key):
            return area_elem.attrib[key]
        imgsrc = imgformat.format(nn)
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
    converts a coordinates string (from the map tag coords attrib) to imagemagick geom string
    '''
    parts = map(int, coords.split(','))
    x1, y1, x2, y2 = parts
    width = x2 - x1
    height = y2 - y1
    return '{}x{}+{}+{}'.format(width, height, x1, y1)

def convertcmd(coords, mapimg, outimg):
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
    

