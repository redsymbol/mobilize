from unittest import TestCase

class TestFilters(TestCase):
    def test_noinlinestyles(self):
        from mobilize.filters import apply, noinlinestyles
        testdata = [
            {'in'  : '''<div class="foo" style="background-color: red;">Hello.</div>''',
             'out' :  '''<div class="foo">Hello.</div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertEquals(td['out'], apply(td['in'], filters=[noinlinestyles]))
