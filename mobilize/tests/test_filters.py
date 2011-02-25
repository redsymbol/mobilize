from unittest import TestCase
from mobilize.base import elem2str

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
            self.assertEquals(td['out'], elem2str(applyone(td['in'], noinlinestyles)))
            
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
            {'in'  : '''<img src="http://example.com/boo.gif" alt="boo!" onmouseover="alert('boo!');"/>''',
             'out' : '''<img src="http://example.com/boo.gif" alt="boo!"/>''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertEquals(td['out'], elem2str(applyone(td['in'], noevents)))
            
    def test_calculate_common_filters(self):
        '''A crude test to at least partly validate the filterapi decorator'''
        from mobilize.filters import apply, noinlinestyles, COMMON_FILTERS
        assert noinlinestyles in COMMON_FILTERS # a known filter api function
        assert apply not in COMMON_FILTERS # a known non-filter-api function
        
    def test_chain_filters(self):
        '''test that apply() correctly chains filters'''
        htmlin = '''<div class="foo" style="color: blue">
<h1 style="font-size: large;">The Headline</h1>
<a href="#" onclick="alert('Good Job!');">Click Here</a>
</div>'''
        htmlout = '''<div class="foo">
<h1>The Headline</h1>
<a href="#">Click Here</a>
</div>'''
        from mobilize.filters import apply, noinlinestyles, noevents
        my_filters = [
            noinlinestyles,
            noevents,
            ]
        self.assertEquals(elem2str(apply(htmlin, my_filters)), htmlout)
