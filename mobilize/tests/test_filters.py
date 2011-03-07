from unittest import TestCase
from mobilize.base import elem2str

def apply_filters(htmlstr, filters):
    '''
    Apply filters to an HTML snippet
    
    @param htmlstr : An HTML snippet
    @type  htmlstr : str

    @param filters : Filters to apply to the snippet
    @type  filters : list of functions (each conforming to filter API)

    @return        : The same HTML snippet with the indicated filters applied
    @rtype         : str
    
    '''
    from lxml import html
    doc = html.fragment_fromstring(htmlstr, create_parent=False)
    for elem in doc.iter():
        for filt in filters:
            filt(elem)
    return doc
    

class TestFilters(TestCase):
    def test_noinlinestyles(self):
        from mobilize.filters import noinlinestyles
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
            self.assertEquals(td['out'], elem2str(apply_filters(td['in'], [noinlinestyles])))
            
    def test_noevents(self):
        from mobilize.filters import noevents
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
            self.assertEquals(td['out'], elem2str(apply_filters(td['in'], [noevents])))
            
    def test_chain_filters(self):
        '''test that filters can be chained'''
        htmlin = '''<div class="foo" style="color: blue">
<h1 style="font-size: large;">The Headline</h1>
<a href="#" onclick="alert('Good Job!');">Click Here</a>
</div>'''
        htmlout = '''<div class="foo">
<h1>The Headline</h1>
<a href="#">Click Here</a>
</div>'''
        from mobilize.filters import noinlinestyles, noevents
        my_filters = [
            noinlinestyles,
            noevents,
            ]
        self.assertEquals(elem2str(apply_filters(htmlin, my_filters)), htmlout)
