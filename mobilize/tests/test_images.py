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
                    'data_width'  : None,
                    'data_height' : None,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : None,
                    'data_width'  : 100,
                    'data_height' : 102,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 102,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : 101,
                    'data_width'  : 102,
                    'data_height' : 103,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : 100,
                    'tag_height'  : None,
                    'data_width'  : 200,
                    'data_height' : 204,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 102,
                    },
             },
            {'in' : {
                    'tag_width'   : None,
                    'tag_height'  : 101,
                    'data_width'  : 200,
                    'data_height' : 202,
                    },
             'out'                : {
                    'width'       : 100,
                    'height'      : 101,
                    },
             },
            {'in' : {
                    'tag_width'   : None,
                    'tag_height'  : None,
                    'data_width'  : None,
                    'data_height' : None,
                    },
             'out'                : {
                    },
             },
            {'in' : {
                    'tag_width'   : 1200,
                    'tag_height'  : 800,
                    'data_width'  : 1200,
                    'data_height' : 800,
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
                    'data_width'  : 1200,
                    'data_height' : 900,
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
                    'data_width'  : 12000,
                    'data_height' : 8000,
                    'default_maxw' : 300,
                    },
             'out'                : {
                    'width'       : 300,
                    'height'      : 200,
                    },
             },
            # {'in' : {
            #         'tag_width'   : None,
            #         'tag_height'  : None,
            #         'data_width'  : None,
            #         'data_height' : None,
            #         },
            #  'out'                : {
            #         'width'       : None,
            #         'height'      : None,
            #         },
            #  },
            ]
        from mobilize.images import new_img_sizes
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = new_img_sizes(**td['in'])
            self.assertDictEqual(expected, actual, str(ii))

    def test_normalize_img_size(self):
        testdata = [
            {'value'  : None,
             'result' : None,
             },
            {'value'  : '1',
             'result' : 1,
             },
            {'value'  : '12345',
             'result' : 12345,
             },
            {'value'  : '',
             'result' : None,
             },
            {'value'  : 'lolwot',
             'result' : None,
             },
            {'value'  : '11px',
             'result' : 11,
             },
            {'value'  : '-42',
             'result' : None,
             },
            {'value'  : '42 pixels wide',
             'result' : 42,
             },
            ]
        from mobilize.images import normalize_img_size
        for ii, td in enumerate(testdata):
            expected = td['result']
            actual = normalize_img_size(td['value'])
            self.assertEqual(expected, actual, ii)
            
if '__main__'==__name__:
    import unittest
    unittest.main()
