from unittest import TestCase

class TestFilters(TestCase):
    def test_noinlinestyles(self):
        from mobilize.filters import applyone, noinlinestyles
        testdata = [
            {'in'  : '''<div class="foo" style="background-color: red;">Hello.</div>''',
             'out' :  '''<div class="foo">Hello.</div>''',
             },
            {'in'  : '''<div class="foo" STYLE="background-color: red;">Hello.</div>''',
             'out' :  '''<div class="foo">Hello.</div>''',
             },
            {'in'  : '''<div class="foo" Style="background-color: red;">Hello.</div>''',
             'out' :  '''<div class="foo">Hello.</div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertEquals(td['out'], applyone(td['in'], noinlinestyles))
            
    def test_noevents(self):
        from mobilize.filters import applyone, noevents
        testdata = [
            {'in'  : '''<a href="#" id="makeHPLink" onclick="cnnMakeHP('homepage_set_overlay')" class="realmLink">Make CNN Your Homepage</a>''',
             'out' : '''<a href="#" id="makeHPLink" class="realmLink">Make CNN Your Homepage</a>''',
             },
            {'in'  : '''<a href="#" id="makeHPLink" ONCLICK="cnnMakeHP('homepage_set_overlay')" class="realmLink">Make CNN Your Homepage</a>''',
             'out' : '''<a href="#" id="makeHPLink" class="realmLink">Make CNN Your Homepage</a>''',
             },
            {'in'  : '''<a href="#" id="makeHPLink" onClick="cnnMakeHP('homepage_set_overlay')" class="realmLink">Make CNN Your Homepage</a>''',
             'out' : '''<a href="#" id="makeHPLink" class="realmLink">Make CNN Your Homepage</a>''',
             },
            {'in'  : '''<img src="http://example.com/boo.gif" alt="boo!" onmouseover="alert('boo!');">''',
             'out' : '''<img src="http://example.com/boo.gif" alt="boo!">''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertEquals(td['out'], applyone(td['in'], noevents))
            
    def test_calculate_common_filters(self):
        '''A crude test to at least partly validate the filterapi decorator'''
        from mobilize.filters import apply, noinlinestyles, COMMON_FILTERS
        assert noinlinestyles in COMMON_FILTERS # a known filter api function
        assert apply not in COMMON_FILTERS # a known non-filter-api function
        
