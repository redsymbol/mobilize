import unittest

class TestResponse(unittest.TestCase):
    def test_set_cookie(self):
        testdata = [
            {'in' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Path=/',
             'out' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Path=/',
             },
            {'in' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Domain=secure.msia.org; Path=/',
             'out' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Domain=.msia.org; Path=/',
             },
            {'in' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Domain=.msia.org; Path=/',
             'out' : 'PHPSESSID=0s506lc6m6p7o5m0l2mv5d51a2; Domain=.msia.org; Path=/',
             },
            {'in' : 'zed=1; Domain=foo.example.org',
             'out' : 'zed=1; Domain=.example.org',
             },
            {'in' : 'zed=1; Domain=.example.org',
             'out' : 'zed=1; Domain=.example.org',
             },
            {'in' : 'zed=1; Domain=example.org',
             'out' : 'zed=1; Domain=example.org',
             },
            {'in' : 'zed=1; Domain=foo.baz.example.org',
             'out' : 'zed=1; Domain=.example.org',
             },
            ]
        from mobilize.headers.response import set_cookie
        environ = {}
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = set_cookie(environ, td['in'])
            self.assertSequenceEqual(expected, actual)
