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
