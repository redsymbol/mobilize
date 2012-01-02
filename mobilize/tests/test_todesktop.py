# Copyright 2010-2012 Mobile Web Up. All rights reserved.
import unittest
class TestHttp(unittest.TestCase):
    def test_redir_dest(self):
        testdata = [
            {'in'  : '/todesktop/',
             'out' : '/',
             },
            {'in'  : '/todesktop/?dest=/latest.html%3Fa%3Db%26q%3Dz',
             'out' : '/latest.html?a=b&q=z',
             },
            {'in'  : '/todesktop/?dest=/latest.html%3Fa%3Db%26q%3Dz&xyz=42',
             'out' : '/latest.html?a=b&q=z',
             },
            ]
        from mobilize.todesktop import redir_dest
        for ii, td in enumerate(testdata):
            expected = td['out']
            actual = redir_dest(td['in'])
            msg = 'e: %s, i: %s [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

