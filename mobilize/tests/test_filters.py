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

    def test_calculate_common_filters(self):
        '''A crude test to at least partly validate the filterapi decorator'''
        from mobilize.filters import apply, noinlinestyles, COMMON_FILTERS
        assert noinlinestyles in COMMON_FILTERS # a known filter api function
        assert apply not in COMMON_FILTERS # a known non-filter-api function
        
