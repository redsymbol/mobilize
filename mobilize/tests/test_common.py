import unittest
from mobilize import common

class TestCommon(unittest.TestCase):
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
            actual = common.fullsiteurl(td['mobileurl'], td['mobiledomain'], td['fullsitedomain'])
            self.assertSequenceEqual(expected, actual)
            
