from unittest import TestCase
from mobilize.common import elem2str
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
             'out' :  '''<div><img src="http://example.com/booger.png" alt=""></div>''',
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
            {'in'  : '''<img src="http://example.com/boo.gif" alt="boo!" onmouseover="alert('boo!');">''',
             'out' : '''<img src="http://example.com/boo.gif" alt="boo!">''',
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
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"></embed>
</object></li></ul></div>''',
             },
            {'object_str' : '''<object width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"></embed>
</object>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"></embed>
</object>''',
             },
            {'object_str' : '''<OBJECT width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"/>
</OBJECT>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"></embed>
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

    def test_resizeiframe(self):
        from mobilize.filters import resizeiframe
        testdata = [
            {'iframe_str' : '''<p>
<iframe width="533" height="330" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>
</p>''',
             'resized_str' : '''<p>
<iframe width="280" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>
</p>''',
             },
            {'iframe_str' : '''<iframe width="533" height="330" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>''',
             'resized_str' : '''<iframe width="280" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>''',
             },
            {'iframe_str' : '''<p>Nothing to see here.</p>''',
             'resized_str' : '''<p>Nothing to see here.</p>''',
             },
            ]
        for ii, td in enumerate(testdata):
            iframe_elem = html.fragment_fromstring(td['iframe_str'], create_parent=False)
            resizeiframe(iframe_elem)
            self.assertSequenceEqual(normxml(td['resized_str']), normxml(elem2str(iframe_elem)))

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
            {'in_str' : '''<div><p>Nothing here.</p></div>''',
             'out_str' : '''<div><p>Nothing here.</p></div>''',
             },
            {'in_str' : '''<div><table>
      <tr>
        <td><table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table></td>
        <td>Key Lime Pie</td>
      </tr>
    </table></div>''',
             'out_str' : '''<div><div class="mwu-table2divs">
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">
      <table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
    </div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Key Lime Pie</div>
    </div>
</div>''',
             },
            {'in_str' : '''<div><table>
      <tr>
        <td>
Does html like this exist somewhere in the wild?
<table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
<p>yeah, I bet somewhere it does</p>
(probably on some website that gets 10K hits on a slow day)
<table id="foobar"><tr><td>Game</td><td>Over Man</td></tr></table>
here's some extra trailing text for you too
</td>
        <td>Key Lime Pie</td>
      </tr>
    </table></div>''',
             'out_str' : '''<div><div class="mwu-table2divs">
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">
Does html like this exist somewhere in the wild?
<table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
<p>yeah, I bet somewhere it does</p>
(probably on some website that gets 10K hits on a slow day)
<table id="foobar"><tr><td>Game</td><td>Over Man</td></tr></table>
here's some extra trailing text for you too
    </div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Key Lime Pie</div>
    </div>
</div>''',
             },
            {'in_str' : '''<table>
      <tr>
        <td>Eggs</td>
        <td>Ham</td>
      </tr>
      <tr>
        <td>Beer</td>
        <td>Milk</td>
      </tr>
    </table>
''',
             'out_str' : '''<div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-row0 mwu-table2divs-col0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-row0 mwu-table2divs-col1">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-row1 mwu-table2divs-col0">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-row1 mwu-table2divs-col1">Milk</div></div>
''',
             },
            ]
        from mobilize.filters import table2divs
        for ii, td in enumerate(testdata):
            in_elem = html.fragment_fromstring(td['in_str'], create_parent=False)
            table2divs(in_elem)
            self.assertSequenceEqual(normxml(td['out_str']), normxml(elem2str(in_elem)))

    def test_elementempty(self):
        testdata = [
            {'in_str' : '''<div></div>''',
             'isempty' : True,
             },
            {'in_str' : '''<div> </div>''',
             'ignore_whitespace' : True,
             'isempty' : True,
             },
            {'in_str' : '''<div> </div>''',
             'ignore_whitespace' : False,
             'isempty' : False,
             },
            {'in_str' : '''<div> &nbsp;	&nbsp;&#160;     </div>''',
             'ignore_whitespace' : True,
             'isempty' : True,
             },
            {'in_str' : '''<div> &nbsp;	&nbsp;&#160;           </div>''',
             'ignore_whitespace' : False,
             'isempty' : False,
             },
            {'in_str' : '''<div>hey</div>''',
             'isempty' : False,
             },
            {'in_str' : '''<div><span></span></div>''',
             'isempty' : False,
             },
            {'in_str' : '''<div><p>alpha</p><p>beta</p></div>''',
             'isempty' : False,
             },
            ]
        from mobilize.filters import elementempty
        for ii, td in enumerate(testdata):
            elem = html.fromstring(td['in_str'])
            ignore_whitespace = td.get('ignore_whitespace', False)
            expected = td['isempty']
            actual = elementempty(elem, ignore_whitespace)
            msg = 'e: %s, a: %s [%d]' % (expected, actual, ii)
            self.assertEqual(expected, actual, msg)

    def test_omit(self):
        from lxml import html
        from mobilize.filters import omit
        ELEMSTR1 = '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<p id="child2">Child Numero Dos</p>
<div id="child3">Child Numero Tres</div>
</div>
'''
        testdata = [
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['div#child1'],
             'out_str' : '''<div class="foo">
<p id="child2">Child Numero Dos</p>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['div#child2'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<p id="child2">Child Numero Dos</p>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['p#child2'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['p'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['p#child2', 'div#child3'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : None,
             'csspaths' : ['div#child3', 'p#child2'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : ['./p'],
             'csspaths' : None,
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : ['.//p'],
             'csspaths' : None,
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
<div id="child3">Child Numero Tres</div>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : ['./div'],
             'csspaths' : None,
             'out_str' : '''<div class="foo">
<p id="child2">Child Numero Dos</p>
</div>''',
             },
            {'elem_str' : ELEMSTR1,
             'xpaths' : ['./p'],
             'csspaths' : ['div#child3'],
             'out_str' : '''<div class="foo">
<div id="child1">Child Numero Uno</div>
</div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            elem = html.fromstring(td['elem_str'])
            omit(elem, xpaths=td['xpaths'], csspaths=td['csspaths'])
            expected = normxml(td['out_str'])
            actual = normxml(html.tostring(elem))
            self.assertSequenceEqual(expected, actual)

        # check that an arg is required
        testelem = html.fromstring(ELEMSTR1)
        self.assertRaises(AssertionError, omit, testelem)
        self.assertRaises(AssertionError, omit, testelem, [], [])
