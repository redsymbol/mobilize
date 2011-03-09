from unittest import TestCase
from mobilize.base import elem2str
from lxml import html
from utils4test import normxml

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
    doc = html.fragment_fromstring(htmlstr, create_parent=False)
    for elem in doc.iter():
        for filt in filters:
            filt(elem)
    return doc
    

class TestFilters(TestCase):
    maxDiff=1024**2
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

    def test_noimgsize(self):
        from mobilize.filters import noimgsize
        testdata = [
            {'in'  : '''<div><img src="http://example.com/booger.png" width="1920" height="1280" alt=""/></div>''',
             'out' :  '''<div><img src="http://example.com/booger.png" alt=""/></div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertSequenceEqual(td['out'], elem2str(apply_filters(td['in'], [noimgsize])))
        
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

    def test_resizeobject(self):
        from mobilize.filters import resizeobject
        testdata = [
            {'object_str' : '''<div class="foobar"><ul><li><object width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"/>
</object></li></ul></div>''',
             'resized_str' : '''<div class="foobar"><ul><li><object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"/>
</object></li></ul></div>''',
             },
            {'object_str' : '''<object width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"/>
</object>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"/>
</object>''',
             },
            {'object_str' : '''<OBJECT width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"/>
</OBJECT>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"/>
</object>''',
             },
            {'object_str' : '''<p>Nothing to see here.</p>''',
             'resized_str' : '''<p>Nothing to see here.</p>''',
             },
            ]
        for ii, td in enumerate(testdata):
            object_elem = html.fragment_fromstring(td['object_str'], create_parent=False)
            resizeobject(object_elem)
            self.assertSequenceEqual(normxml(td['resized_str']), normxml(elem2str(object_elem)))

    def test_table2divs(self):
        testdata = [
            {'in_str' : '''<div><table>
      <tr>
        <td>Eggs</td>
        <td>Ham</td>
      </tr>
      <tr>
        <td>Beer</td>
        <td>Milk</td>
      </tr>
    </table></div>
''',
             'out_str' : '''<div><div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-row1 mwu-table2divs-col0">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-row1 mwu-table2divs-col1">Milk</div></div></div>
''',
             },
            {'in_str' : '''<div><table><tbody>
      <tr>
        <td>Eggs</td>
        <td>Ham</td>
      </tr>
      <tr>
        <td>Beer</td>
        <td>Milk</td>
      </tr>
    </tbody></table></div>
''',
             'out_str' : '''<div><div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-row1 mwu-table2divs-col0">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-row1 mwu-table2divs-col1">Milk</div></div></div>
''',
             },
            ]
        from mobilize.filters import table2divs
        for ii, td in enumerate(testdata):
            in_elem = html.fragment_fromstring(td['in_str'], create_parent=False)
            table2divs(in_elem)
            self.assertSequenceEqual(normxml(td['out_str']), normxml(elem2str(in_elem)))
