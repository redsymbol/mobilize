# Copyright 2010-2011 Mobile Web Up. All rights reserved.
import unittest
from mobilize import util

class TestUtil(unittest.TestCase):
    def test_fullsiteurl(self):
        testdata = [
            {'mobileurl' : 'http://m.example.com/',
             'mobiledomain' : 'm.example.com',
             'fullsitedomain' : 'www.example.com',
             'expected' : 'http://www.example.com/?mredir=0',
             },
            {'mobileurl' : 'http://m.example.com/?foo=bar',
             'mobiledomain' : 'm.example.com',
             'fullsitedomain' : 'www.example.com',
             'expected' : 'http://www.example.com/?foo=bar&mredir=0',
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['expected']
            actual = util.fullsiteurl(td['mobileurl'], td['mobiledomain'], td['fullsitedomain'])
            self.assertSequenceEqual(expected, actual)
            
    def test_classvalue(self):
        self.assertSequenceEqual('mwu-elem', util.classvalue())
        self.assertSequenceEqual('mwu-elem mwu-elem-alpha mwu-elem-beta', util.classvalue('alpha', 'beta'))

    def test_classname(self):
        self.assertSequenceEqual('mwu-elem', util.classname())
        self.assertSequenceEqual('mwu-elem-alpha', util.classname('alpha'))

    def test_idname(self):
        self.assertSequenceEqual('mwu-elem-42', util.idname(42))
        self.assertSequenceEqual('mwu-elem-0', util.idname(0))
        self.assertSequenceEqual('mwu-elem-blah', util.idname('blah'))

    def test_urlbase(self):
        testdata =[
            {'url'  : 'http://example.com',
             'base' : 'http://example.com/',
             },
            {'url'  : 'http://example.com/',
             'base' : 'http://example.com/',
             },
            {'url'  : 'http://example.com/foo.html',
             'base' : 'http://example.com/',
             },
            {'url'  : 'http://example.com/baz/something.html',
             'base' : 'http://example.com/baz/',
             },
            {'url'  : 'http://example.com/baz/index.html',
             'base' : 'http://example.com/baz/',
             },
            {'url'  : 'http://example.com/baz/',
             'base' : 'http://example.com/baz/',
             },
            {'url'  : 'http://example.com/baz/x.html?a=2&b=3',
             'base' : 'http://example.com/baz/',
             },
            {'url'  : 'http://example.com/baz/x.html#hey',
             'base' : 'http://example.com/baz/',
             },
            ]
        from mobilize.util import urlbase
        for ii, td in enumerate(testdata):
            actual = urlbase(td['url'])
            msg = 'e: "%s", a; "%s" [%d]' % (td['base'], actual, ii)
            self.assertSequenceEqual(td['base'], actual, msg)

    def test_isscalar(self):
        testdata = [
            {'obj' : 'x',
             'isscalar' : True,
             },
            {'obj' : 'hello',
             'isscalar' : True,
             },
            {'obj' : b'hello',
             'isscalar' : True,
             },
            {'obj' : 42,
             'isscalar' : True,
             },
            {'obj' : ['a', 'b', 'c'],
             'isscalar' : False,
             },
            {'obj' : ('a', 'b', 'c'),
             'isscalar' : False,
             },
            {'obj' : {2: 3, 'a': 'g'},
             'isscalar' : False,
             },
            {'obj' : iter([2, 3, 4]),
             'isscalar' : False,
             },
            ]
        for ii, td in enumerate(testdata):
            expected = td['isscalar']
            actual = util.isscalar(td['obj'])
            self.assertEqual(expected, actual, td['obj'])
