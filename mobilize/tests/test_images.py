# Copyright 2010-2012 Mobile Web Up. All rights reserved.
import unittest

class TestImageOpt(unittest.TestCase):
    '''
    test related to image resizing/optimization
    '''
    def test_new_img_sizes(self):
        testdata = [
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : 101,
                    'measured_width'  : None,
                    'measured_height' : None,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : None,
                    'measured_width'  : 100,
                    'measured_height' : 102,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 102,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : 101,
                    'measured_width'  : 102,
                    'measured_height' : 103,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : None,
                    'measured_width'  : 200,
                    'measured_height' : 204,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 102,
                    },
             },
            {'in' : {
                    'tag_width'   : None,
                    'tag_height'  : 101,
                    'measured_width'  : 200,
                    'measured_height' : 202,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : None,
                    'tag_height'  : None,
                    'measured_width'  : None,
                    'measured_height' : None,
                    },
             'out'                : {
                    },
             },
            {'in' : {
                    'tag_width'   : 1200,
                    'tag_height'  : 800,
                    'measured_width'  : 1200,
                    'measured_height' : 800,
                    'default_maxw' : 300,
                    },
             'out'                : {
                    'width'       : 300,
                    'height'      : 200,
                    },
             },
            {'in' : {
                    'tag_width'   : 1200,
                    'tag_height'  : 900,
                    'measured_width'  : 1200,
                    'measured_height' : 900,
                    'default_maxw' : 400,
                    },
             'out'                : {
                    'width'       : 400,
                    'height'      : 300,
                    },
             },
            {'in' : {
                    'tag_width'   : 1200,
                    'tag_height'  : 800,
                    'measured_width'  : 12000,
                    'measured_height' : 8000,
                    'default_maxw' : 300,
                    },
             'out'                : {
                    'width'       : 300,
                    'height'      : 200,
                    },
             },
            # For next test, important that default_maxw < tag_width, and all other inputs are None
            {'in' : {
                    'tag_width'       : 104,
                    'tag_height'      : None,
                    'measured_width'  : None,
                    'measured_height' : None,
                    'default_maxw'    : 103,
                    },
             'out'                    : {
                    'width'           : 103,
                    },
             },
            {'in' : {
                    'tag_width'       : 200,
                    'tag_height'      : 100,
                    'measured_width'  : None,
                    'measured_height' : None,
                    'default_maxw'    : 100,
                    },
             'out'                    : {
                    'width'           : 100,
                    'height'          : 50,
                    },
             },
            # If the w/h ratio is as defined by the tag attributes is very different from that of the source, use the tag attrib ratio.
            {'in' : {
                    'tag_width'       : 200,
                    'tag_height'      : 100,
                    'measured_width'  : 300,
                    'measured_height' : 150,
                    'default_maxw'    : 100,
                    },
             'out'                    : {
                    'width'           : 100,
                    'height'          : 50,
                    },
             },
            {'in' : {
                    'tag_width'       : 200,
                    'tag_height'      : 100,
                    'measured_width'  : 100,
                    'measured_height' : 200,
                    'default_maxw'    : 1000,
                    },
             'out'                    : {
                    'width'           : 200,
                    'height'          : 100,
                    },
             },
            # Don't scale up
            {'in' : {
                    'tag_width'       : 100,
                    'tag_height'      : 200,
                    'measured_width'  : 10,
                    'measured_height' : 20,
                    'default_maxw'    : 1000,
                    },
             'out'                    : {
                    'width'           : 10,
                    'height'          : 20,
                    },
             },
            # {'in' : {
            #         'tag_width'       : None,
            #         'tag_height'      : None,
            #         'measured_width'  : None,
            #         'measured_height' : None,
            #         },
            #  'out'                    : {
            #         'width'           : None,
            #         'height'          : None,
            #         },
            #  },
            
            ]
        from mobilize.images import new_img_sizes
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = new_img_sizes(**td['in'])
            self.assertDictEqual(expected, actual, str(ii))

    def test_to_imgserve_url(self):
        from mobilize.images import to_imgserve_url
        testdata = [
            {'url'          : 'http://example.com/foo/bar.png',
             'maxw'         : 107,
             'maxh'         : 42,
             'imgserve_url' : '/_mwuimg/?src=http%3A%2F%2Fexample.com%2Ffoo%2Fbar.png&maxw=107&maxh=42',
             },
            {'url'          : 'http://example.com/robot.jpg',
             'maxw'         : 107,
             'maxh'         : 207,
             'imgserve_url' : '/_mwuimg/?src=http%3A%2F%2Fexample.com%2Frobot.jpg&maxw=107&maxh=207',
             },
            {'url'          : 'http://example.com/robot.jpg',
             'maxw'         : 107,
             'imgserve_url' : '/_mwuimg/?src=http%3A%2F%2Fexample.com%2Frobot.jpg&maxw=107',
             },
            ]
        for ii, td in enumerate(testdata):
            maxh = td.get('maxh', None)
            expected = td['imgserve_url']
            actual = to_imgserve_url(td['url'], td['maxw'], maxh=maxh)
            self.assertEqual(expected, actual, ii)

    def test_convertable(self):
        '''tests for mobilize.images.convertable'''
        from lxml import html
        from mobilize.images import convertable
        class ImgElement(html.HtmlElement):
            def __init__(self):
                super().__init__()
                self.tag = 'img'

        # defined width & height
        img_wh = ImgElement()
        img_wh.attrib['width'] = '100'
        img_wh.attrib['height'] = '42'
        # height but no width
        img_h = ImgElement()
        img_h.attrib['height'] = '42'
        # neither width nor height
        img_ = ImgElement()

        ### Convertable situations
        # data width, tag width and tag height all defined, but widths are unequal
        self.assertTrue(convertable(img_wh, '90'))
        # data width is not known
        self.assertTrue(convertable(img_wh, None))

        ### Nonconvertable situations
        # data width is known to be same as tag width
        self.assertFalse(convertable(img_wh, '100'))
        # Tag has no defined width
        self.assertFalse(convertable(img_h, '90'))
        self.assertFalse(convertable(img_, '90'))
        
            
if '__main__'==__name__:
    import unittest
    unittest.main()
