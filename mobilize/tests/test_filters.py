from unittest import TestCase
from mobilize.util import elem2str
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
    def test_nomiscattrib(self):
        from mobilize.filters import nomiscattrib
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
            {'in'  : '''<div><a href="/a">Hello.</a> <a href="http://example.com" target="_blank">New Tab</a></div>''',
            'out'  : '''<div><a href="/a">Hello.</a> <a href="http://example.com">New Tab</a></div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            self.assertEquals(td['out'], elem2str(apply_filters(td['in'], [nomiscattrib])))

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
        from mobilize.filters.remove import noevents_one
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
            self.assertEquals(td['out'], elem2str(apply_filters(td['in'], [noevents_one])))
            
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
        from mobilize.filters import nomiscattrib
        from mobilize.filters.remove import noevents_one
        my_filters = [
            nomiscattrib,
            noevents_one,
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
             'resized_str' : '''<div class="foobar"><ul><li><object width="280" height="120">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280" height="120"></embed>
</object></li></ul></div>''',
             },
            {'object_str' : '''<object width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"></embed>
</object>''',
             'resized_str' : '''<object width="280" height="120">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280" height="120"></embed>
</object>''',
             },
            {'object_str' : '''<OBJECT width="800" height="344">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="344"/>
</OBJECT>''',
             'resized_str' : '''<object width="280" height="120">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280" height="120"></embed>
</object>''',
             },
            # If not height defined, or otherwise can't calculate aspect ratio, just ignore that attribute
            {'object_str' : '''<OBJECT width="800">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800"/>
</OBJECT>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"></embed>
</object>''',
             },
            {'object_str' : '''<OBJECT>
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true"/>
</OBJECT>''',
             'resized_str' : '''<object width="280">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US">
<param name="allowFullScreen" value="true">
<param name="allowscriptaccess" value="always">
<embed src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="280"></embed>
</object>''',
             },
            {'object_str' : '''<OBJECT width="800" height="beer">
<param name="movie" value="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US"/>
<param name="allowFullScreen" value="true"/>
<param name="allowscriptaccess" value="always"/>
<EMBED src="http://www.youtube.com/v/fJ8FGIQG8gM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="800" height="beer"/>
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
<iframe width="280" height="173" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>
</p>''',
             },
            {'iframe_str' : '''<iframe width="533" height="330" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>''',
             'resized_str' : '''<iframe width="280" height="173" frameborder="0" allowfullscreen="" src="http://www.youtube.com/embed/HE6uqPPrVfo" title="YouTube video player"></iframe>''',
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
        <td class="from-poultry 	  roundish">Eggs</td>
        <td>Ham</td>
      </tr>
      <tr>
        <td class=" ">Beer</td>
        <td>Milk</td>
      </tr>
    </table></div>
''',
             'out_str' : '''<div><div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0 mwu-td-from-poultry mwu-td-roundish">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-col1 mwu-table2divs-row0">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-col0 mwu-table2divs-row1">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-col1 mwu-table2divs-row1">Milk</div></div></div>
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
             'out_str' : '''<div><div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-col1 mwu-table2divs-row0">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-col0 mwu-table2divs-row1">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-col1 mwu-table2divs-row1">Milk</div></div></div>
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
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0">
      <table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
    </div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-col1 mwu-table2divs-row0">Key Lime Pie</div>
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
    <div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0">
Does html like this exist somewhere in the wild?
<table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
<p>yeah, I bet somewhere it does</p>
(probably on some website that gets 10K hits on a slow day)
<table id="foobar"><tr><td>Game</td><td>Over Man</td></tr></table>
here's some extra trailing text for you too
    </div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-col1 mwu-table2divs-row0">Key Lime Pie</div>
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
             'out_str' : '''<div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0">Eggs</div>
    <div class="mwu-table2divs-row0-col1 mwu-table2divs-col1 mwu-table2divs-row0">Ham</div>
    <div class="mwu-table2divs-row1-col0 mwu-table2divs-col0 mwu-table2divs-row1">Beer</div>
    <div class="mwu-table2divs-row1-col1 mwu-table2divs-col1 mwu-table2divs-row1">Milk</div></div>
''',
             },
            # find more deeply nested table
            {'in_str' : '''<div><ul><li><div>
<table>
  <tr>
   <td>Eggs</td>
  </tr>
</table>
</div></li></ul></div>
''',
             'out_str' : '''<div><ul><li><div>
<div class="mwu-table2divs"><div class="mwu-table2divs-row0-col0 mwu-table2divs-col0 mwu-table2divs-row0">Eggs</div></div>
</div></li></ul></div>
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
        from mobilize.filters.tables import elementempty
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
            
            
    def test_table2divgroups(self):
        from mobilize.filters.tables import Spec
        ELEMSTR1 = '''<div id="some-container">
<table>
      <tbody>
        <tr>
          <td>CONTACT US</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
        <tr>
          <td>123 Main Str</td>
          <td>&nbsp;</td>
          <td>OUR TEAM</td>
          <td>&nbsp;</td>
        <tr>
          <td>Springfield, IL</td>
          <td>&nbsp;</td>
          <td>Mike Smith</td>
          <td><img src="/mike-smith.jpg"/></td>
        <tr>
          <td>1-800-BUY-DUFF</td>
          <td>&nbsp;</td>
          <td>Jen Jones</td>
          <td><img src="/jen-jones.jpg"/></td>
        <tr>
          <td>&nbsp;</td>
          <td>&nbsp;</td>
          <td>Scruffy</td>
          <td><img src="/scruffy-the-dog.jpg"/></td>
        <tr>
      </tbody>
    </table>
</div>
'''
        testdata = [
            {'elem_str' : ELEMSTR1,
             'specmap' : [],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname1', 0, 0, 0, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname1', 0, 0, 3, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname1', 0, 0, 0, 0)),
                    (Spec('idname2', 0, 0, 3, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
    </div>
    <div class="mwu-elem-table2divgroups-group" id="idname2">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname2', 0, 0, 3, 0)),
                    (Spec('idname1', 0, 0, 0, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname2">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname2', 0, 0, 3, 0)),
                    (Spec('idname1', 0, 0, 0, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname2">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname1', 0, 0, 4, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'omit_whitespace' : False,
             'specmap' : [
                    (Spec('idname1', 0, 0, 4, 0)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
      <div>&#160;</div>
    </div>
  </div>
</div>
''',
             },
            {'elem_str' : ELEMSTR1,
             'specmap' : [
                    (Spec('idname1', 1, 2, 4, 3)),
                    ],
             'out_str' : '''
<div id="some-container">
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div>
        <div>OUR TEAM</div>
      </div>
      <div>
        <div>Mike Smith</div>
        <div><img src="/mike-smith.jpg"></div>
      </div>
      <div>
        <div>Jen Jones</div>
        <div><img src="/jen-jones.jpg"></div>
      </div>
      <div>
        <div>Scruffy</div>
        <div><img src="/scruffy-the-dog.jpg"></div>
      </div>
    </div>
  </div>
</div>
''',
             },
            
            {'elem_str' : '''<div>
<table>
<tr><td colspan="3">a</td></tr>
<tr>
  <td>b</td>
  <td>c</td>
  <td>d</td>
</tr>
</table>
''',
             'specmap' : [
                    (Spec('idname1', 0, 0, 1, 1)),
                    ],
             'out_str' : '''
<div>
  <div class="mwu-elem-table2divgroups">
    <div class="mwu-elem-table2divgroups-group" id="idname1">
      <div><div>a</div></div>
      <div>
        <div>b</div>
        <div>c</div>
      </div>
    </div>
  </div>
</div>
''',
             },
            ]
        from mobilize.filters import table2divgroups
        for ii, td in enumerate(testdata):
            omit_whitespace = td.get('omit_whitespace', True)
            elem = html.fromstring(td['elem_str'])
            table2divgroups(elem, td['specmap'], omit_whitespace=omit_whitespace)
            expected = normxml(td['out_str'])
            actual = normxml(elem2str(elem))
            self.assertSequenceEqual(expected, actual)

    def test_noattribs(self):
        ELEMSTR1 = '''<table width="600" style="color: fuscia;">
<tr><td width="200">one</td><td>two</td></tr>
<tr><td>three</td><td>four</td></tr>
</table>
'''
        ELEMSTR2 = '''<div>
<table width="600" style="color: fuscia;">
<tr><td width="200">one</td><td>two</td></tr>
<tr><td>three</td><td>four</td></tr>
</table>
</div>
'''
        testdata = [
            {'in_str' : ELEMSTR1,
             'tags' : ['table'],
             'attribs' : ['width', 'style'],
             'out_str' : '''<table>
<tr><td width="200">one</td><td>two</td></tr>
<tr><td>three</td><td>four</td></tr>
</table>
'''
             },
            {'in_str' : ELEMSTR2,
             'tags' : ['table'],
             'attribs' : ['width', 'style'],
             'out_str' : '''<div>
<table>
<tr><td width="200">one</td><td>two</td></tr>
<tr><td>three</td><td>four</td></tr>
</table>
</div>
'''
             },
            {'in_str' : ELEMSTR2,
             'tags' : ['table', 'td'],
             'attribs' : ['width', 'style'],
             'out_str' : '''<div>
<table>
<tr><td>one</td><td>two</td></tr>
<tr><td>three</td><td>four</td></tr>
</table>
</div>
'''
             },
            ]
        from mobilize.filters import noattribs
        for ii, td in enumerate(testdata):
            elem = html.fragment_fromstring(td['in_str'], create_parent=False)
            noattribs(elem, td['tags'], td['attribs'])
            expected = normxml(td['out_str'])
            actual = normxml(elem2str(elem))
            self.assertSequenceEqual(expected, actual)

    def test_squeezebr(self):
        from mobilize.filters import squeezebr
        testdata = [
            {'in_str' : '''<p>Hi.</p>''',
             'out_str' : '''<p>Hi.</p>''',
             },
            {'in_str' : '''<p>Hi.<br>Hey.</p>''',
             'out_str' : '''<p>Hi.<br>Hey.</p>''',
             },
            {'in_str' : '''<p>Hi.<br><br>Hey.</p>''',
             'out_str' : '''<p>Hi.<br>Hey.</p>''',
             },
            {'in_str' : '''<p>Hi.<br/><br/><br/><br/><br/><br/><br/><br/><br/>Hey.</p>''',
             'out_str' : '''<p>Hi.<br>Hey.</p>''',
             },
            {'in_str' : '''<div>
<p>Hi.<br><br>Hey.</p>
<p>This is some more text
<br><br><br><br><br><img src="foo.png" alt="foo"/>
</p>
</div>''',
             'out_str' : '''<div>
<p>Hi.<br>Hey.</p>
<p>This is some more text
<br><img src="foo.png" alt="foo">
</p>
</div>
''',
             },
            {'in_str' : '''<p>Hi.<br>    <br>Hey.</p>''',
             'out_str' : '''<p>Hi.<br>Hey.</p>''',
             },
            {'in_str' : '''<p>Hi.<br>How.<br>Hey.</p>''',
             'out_str' : '''<p>Hi.<br>How.<br>Hey.</p>''',
             },
            ]
        for ii, td in enumerate(testdata):
            elem = html.fragment_fromstring(td['in_str'], create_parent=False)
            squeezebr(elem)
            expected = normxml(td['out_str'])
            actual = normxml(elem2str(elem))
            self.assertSequenceEqual(expected, actual)

    def test_collapse(self):
        '''
        Test for collapsing filter application mode
        '''
        from mobilize.components import (
            XPath,
            FILT_EACHELEM,
            FILT_COLLAPSED,
            )
        def testfilter(elem):
            if elem.tag == 'a':
                elem.attrib['class'] = 'foo'
            for ii, child in enumerate(elem):
                if 'a' == child.tag:
                    child.attrib['id'] = 'child-%d' % ii
            
        htmlstr1 = '''<a href="/">a</a>
<a href="/">b</a>
<a href="/">c</a>
'''
        nocollapse = XPath('//a', postfilters=[testfilter], filtermode=FILT_EACHELEM)
        nocollapse.extract(html.fromstring(htmlstr1))
        actual = nocollapse.process('idname')
        actual_str = html.tostring(actual)
        expected_str = '''<div class="mwu-elem" id="idname">
<a href="/" class="foo">a</a>
<a href="/" class="foo">b</a>
<a href="/" class="foo">c</a>
</div>
'''
        self.assertSequenceEqual(normxml(expected_str), normxml(actual_str))
        
        expected_str = '''<div id="idname">
<a href="/">a</a>
<a href="/">b</a>
<a href="/">c</a>
</div>
'''
        collapse = XPath('//a', postfilters=[testfilter], filtermode=FILT_COLLAPSED)
        collapse.extract(html.fromstring(htmlstr1))
        actual = collapse.process('idname')
        actual_str = html.tostring(actual)
        expected_str = '''<div class="mwu-elem" id="idname">
<a href="/" id="child-0">a</a>
<a href="/" id="child-1">b</a>
<a href="/" id="child-2">c</a>
</div>
'''
        self.assertSequenceEqual(normxml(expected_str), normxml(actual_str))

    def test_absimgsrc(self):
        html1_in = '''<div>
<p>Hi there.</p>
<img src="http://foo.example.com/path/to/bananas.jpg" alt="yellow fruit" width="23" height="480">
<img src="/_mwu/bananatree.jpg" alt="where they come from">
<p>Here's some more.</p>
<img src="/fruitpics/strawberry.jpg" alt="berry good">
<p>and then:
<img src="standard/nrolling-kiwi.gif" alt="delicious but takes time to peel">
<img src="data:image/gif;base64,R0lGODlhQgEDAJEAANTW2Pr06rO8yAAAACH5BAAAAAAALAAAAABCAQMAAAIilI+0Po5y02ouz3lyDDobiSJbmiXZA8KXuC8fyTDdrApy+QA7 alt="GIF data URL"/>
<img src="DATA:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAkCAMAAACpD3pbAAAAYFBMVEVZbYftuWNoP0iYbFJDHkBcNEWAVk3JmFzVo17hrmG8jVmQk5+8sJOwgldse4xPKUN0S0r3yXdLJULcwpI4FD75x2f5yniSmJ07Fz/WpF6MYU/wyoShn5XTvZT84bL5xGZPqaqJAAAAdUlEQVQ4y+XTRw7EQAgEQJg8jmtvdOz//9IvaE57c19LQoBAvjuNiMgJmkdrMl69yXjbfNyFtfMN5zo4P0RlPCYAzjN+KoDsGIcKoKGcRkAjLb78JhcS7TyuJRc6WIrWWrqgFodsLrXc95j+yq3Jm/X+n7mXC9defIzz7p9PAAAAAElFTkSuQmCC" alt="PNG data URL"/>
<img src="" alt="Pathological HTML!">
</p>
</div>'''
        html1_out = '''<div>
<p>Hi there.</p>
<img src="http://foo.example.com/path/to/bananas.jpg" alt="yellow fruit" width="23" height="480">
<img src="/_mwu/bananatree.jpg" alt="where they come from">
<p>Here's some more.</p>
<img src="http://desktop.example.com/fruitpics/strawberry.jpg" alt="berry good">
<p>and then:
<img src="http://desktop.example.com/articles/standard/nrolling-kiwi.gif" alt="delicious but takes time to peel">
<img src="data:image/gif;base64,R0lGODlhQgEDAJEAANTW2Pr06rO8yAAAACH5BAAAAAAALAAAAABCAQMAAAIilI+0Po5y02ouz3lyDDobiSJbmiXZA8KXuC8fyTDdrApy+QA7 alt="GIF data URL"/>
<img src="DATA:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAkCAMAAACpD3pbAAAAYFBMVEVZbYftuWNoP0iYbFJDHkBcNEWAVk3JmFzVo17hrmG8jVmQk5+8sJOwgldse4xPKUN0S0r3yXdLJULcwpI4FD75x2f5yniSmJ07Fz/WpF6MYU/wyoShn5XTvZT84bL5xGZPqaqJAAAAdUlEQVQ4y+XTRw7EQAgEQJg8jmtvdOz//9IvaE57c19LQoBAvjuNiMgJmkdrMl69yXjbfNyFtfMN5zo4P0RlPCYAzjN+KoDsGIcKoKGcRkAjLb78JhcS7TyuJRc6WIrWWrqgFodsLrXc95j+yq3Jm/X+n7mXC9defIzz7p9PAAAAAElFTkSuQmCC" alt="PNG data URL"/>
<img src="" alt="Pathological HTML!">
</p>
</div>'''
        desktop_url = 'http://desktop.example.com/articles/delicious.html'
        from mobilize.filters.misc import absimgsrc
        elem = html.fromstring(html1_in)
        absimgsrc(elem, desktop_url)
        result = elem2str(elem)
        self.assertSequenceEqual(normxml(html1_out), normxml(result))

    def test_abslinkfilesrc(self):
        from mobilize.filters import abslinkfilesrc
        html_in = '''<div>
    <p><a href="marketstudy.xls">Market Study</a></p>
    <p><a href="/whitepapers/fill-in-blank.doc">Make your own white paper!</a></p>
    <p><a href="/whitepapers/widgets.pdf">Widget White Paper</a></p>
    <p><a href="">HTML Pathology 101</a></p>
</div>'''
        html_out ='''<div>
    <p><a href="http://example.com/about/marketstudy.xls">Market Study</a></p>
    <p><a href="/whitepapers/fill-in-blank.doc">Make your own white paper!</a></p>
    <p><a href="http://example.com/whitepapers/widgets.pdf">Widget White Paper</a></p>
    <p><a href="">HTML Pathology 101</a></p>
</div>'''
        desktop_url = 'http://example.com/about/papers.html'
        extensions=['.xls', '.pdf']

        elem = html.fromstring(html_in)
        abslinkfilesrc(elem, desktop_url, extensions)
        result = html.tostring(elem)
        self.assertSequenceEqual(normxml(html_out), normxml(result))

    def test_nobr(self):
        from mobilize.filters import nobr
        html_in = "<p>Hello.<br> This is a <br> broken<br>up paragraph.</p>"
        expected_space = "<p>Hello. This is a  broken up paragraph.</p>"
        expected_nospace = "<p>Hello. This is a  brokenup paragraph.</p>"
        elem_space = html.fromstring(html_in)
        nobr(elem_space, space=True)
        space_out = elem2str(elem_space)
        self.assertSequenceEqual(expected_space, space_out)
        
        elem_nospace = html.fromstring(html_in)
        nobr(elem_nospace, space=False)
        nospace_out = elem2str(elem_nospace)
        self.assertSequenceEqual(expected_nospace, nospace_out)

    def test_table2divrows(self):
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
             'out_str' : '''<div>
  <div class="mwu-table2divrows">
    <div class="mwu-table2divrows-row0">
      <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">Eggs</div>
      <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Ham</div>
    </div>
    <div class="mwu-table2divrows-row1">
      <div class="mwu-table2divrows-row1-col0 mwu-table2divrows-col0">Beer</div>
      <div class="mwu-table2divrows-row1-col1 mwu-table2divrows-col1">Milk</div>
    </div>
  </div>
</div>
''',
             },
            #================
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
             'out_str' : '''<div>
  <div class="mwu-table2divrows">
    <div class="mwu-table2divrows-row0">
      <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">Eggs</div>
      <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Ham</div>
    </div>
    <div class="mwu-table2divrows-row1">
      <div class="mwu-table2divrows-row1-col0 mwu-table2divrows-col0">Beer</div>
      <div class="mwu-table2divrows-row1-col1 mwu-table2divrows-col1">Milk</div>
    </div>
  </div>
</div>
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
             'out_str' : '''<div><div class="mwu-table2divrows">
<div class="mwu-table2divrows-row0">
    <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">
      <table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
    </div>
    <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Key Lime Pie</div>
    </div>
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
             'out_str' : '''<div><div class="mwu-table2divrows">
  <div class="mwu-table2divrows-row0">
    <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">
Does html like this exist somewhere in the wild?
<table id="foobar"><tr><td>Whoa</td><td>dude</td></tr></table>
<p>yeah, I bet somewhere it does</p>
(probably on some website that gets 10K hits on a slow day)
<table id="foobar"><tr><td>Game</td><td>Over Man</td></tr></table>
here's some extra trailing text for you too
    </div>
    <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Key Lime Pie</div>
    </div>
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
             'out_str' : '''<div class="mwu-table2divrows">
  <div class="mwu-table2divrows-row0">
    <div class="mwu-table2divrows-row0-col0 mwu-table2divrows-col0">Eggs</div>
    <div class="mwu-table2divrows-row0-col1 mwu-table2divrows-col1">Ham</div>
  </div>
  <div class="mwu-table2divrows-row1">
    <div class="mwu-table2divrows-row1-col0 mwu-table2divrows-col0">Beer</div>
    <div class="mwu-table2divrows-row1-col1 mwu-table2divrows-col1">Milk</div>
  </div>
</div>
''',
             },
            ]
        from mobilize.filters import table2divrows
        for ii, td in enumerate(testdata):
            in_elem = html.fragment_fromstring(td['in_str'], create_parent=False)
            table2divrows(in_elem)
            self.assertSequenceEqual(normxml(td['out_str']), normxml(elem2str(in_elem)))

    def test_formcontroltypes(self):
        from mobilize.filters import formcontroltypes
        instr = '''<form>
<dl>
<dt>Name</dt>
<dd><input type="text" name="name"/></dd>
<dt>Email</dt>
<dd><input type="email" name="email"/></dd>
<dt>Favorite color</dt>
<dd>
  <ul>
    <li><input type="radio" name="color" value="red" class="nonstandard"/>Red</li>
    <li><input type="radio" name="color" value="blue" class="nonstandard"/>Blue</li>
    <li><input type="radio" name="color" value="green" class="nonstandard"/>Green</li>
  </ul>
</dd>
</dl>
</form>'''
        
        expected = '''<form>
<dl>
<dt>Name</dt>
<dd><input type="text" name="name" class="mwu-fc-input-text"/></dd>
<dt>Email</dt>
<dd><input type="email" name="email" class="mwu-fc-input-email"/></dd>
<dt>Favorite color</dt>
<dd>
  <ul>
    <li><input type="radio" name="color" value="red" class="nonstandard mwu-fc-input-radio"/>Red</li>
    <li><input type="radio" name="color" value="blue" class="nonstandard mwu-fc-input-radio"/>Blue</li>
    <li><input type="radio" name="color" value="green" class="nonstandard mwu-fc-input-radio"/>Green</li>
  </ul>
</dd>
</dl>
</form>'''
        root_elem = html.fromstring(instr)
        formcontroltypes(root_elem)
        actual = html.tostring(root_elem)
        self.assertSequenceEqual(normxml(expected), normxml(actual))
        
    def test_relhyperlinks(self):
        from mobilize.filters import (
            relhyperlinks,
            relhyperlinks_full,
            )
        htmlA='''
<div>
<ul>
  <li><a href="http://alpha.com">Alpha home page</a></li>
  <li><a href="http://www.alpha.com">Alt Alpha home page</a></li>
  <li><a href="http://beta.com">Beta home page</a></li>
</ul>

<p>The beautiful <a href="/about/birds/cranes">white cranes</a> of <a href="http://alpha.com/places/Lancashire">Lancashire</a> drink surprising amounts of <a href="https://alpha.com/secure/about/drinks/coffee">coffee</a>.</p> </div>
'''

        root1 = html.fromstring(htmlA)
        relhyperlinks(root1, 'alpha.com')
        actual1 = html.tostring(root1)
        expected1 = '''
<div>
<ul>
  <li><a href="/">Alpha home page</a></li>
  <li><a href="http://www.alpha.com">Alt Alpha home page</a></li>
  <li><a href="http://beta.com">Beta home page</a></li>
</ul>

<p>The beautiful <a href="/about/birds/cranes">white cranes</a> of <a href="/places/Lancashire">Lancashire</a> drink surprising amounts of <a href="https://alpha.com/secure/about/drinks/coffee">coffee</a>.</p> </div>
'''
        self.assertSequenceEqual(normxml(expected1), normxml(actual1))

        root2 = html.fromstring(htmlA)
        relhyperlinks_full(root2, ['alpha.com', 'www.alpha.com'], ['http', 'https'])
        actual2 = html.tostring(root2)
        expected2 = '''
<div>
<ul>
  <li><a href="/">Alpha home page</a></li>
  <li><a href="/">Alt Alpha home page</a></li>
  <li><a href="http://beta.com">Beta home page</a></li>
</ul>

<p>The beautiful <a href="/about/birds/cranes">white cranes</a> of <a href="/places/Lancashire">Lancashire</a> drink surprising amounts of <a href="/secure/about/drinks/coffee">coffee</a>.</p> </div>
'''
        self.assertSequenceEqual(normxml(expected2), normxml(actual2))
        
    def test_relevant_filter(self):
        '''
        Tests for Filter.relevant
        '''
        from mobilize.filters import filterapi, Filter
        from mobilize.components import CssPath
        # test filters
        # The three test filters t1, t2, and t3 mark a div with an attribute.
        # Only t1 and t3 are meant to be relevant; t2 is not.
        @filterapi
        def tf1(elem):
            elem.attrib['tf1'] = '1'
        class TF2(Filter):
            def __call__(self, elem):
                elem.attrib['tf2'] = '2'
            def relevant(self, reqinfo):
                return False
        tf2 = TF2()
        class TF3(Filter):
            def __call__(self, elem):
                elem.attrib['tf3'] = '3'
            def relevant(self, reqinfo):
                return True
        tf3 = TF3()
        root = html.fromstring('<div id="foo">Hello.</div>')
        component = CssPath('div#foo')
        component.extract(root)
        actual = component.process('idname', extra_filters=[tf1, tf2, tf3])
        actual_str = html.tostring(actual).decode('utf-8')
        self.assertSequenceEqual('<div class="mwu-elem" id="idname"><div id="foo" tf1="1" tf3="3">Hello.</div></div>', actual_str)

    def test_formaction(self):
        from mobilize.filters import formaction
        testdata = [
            {'form_html_in'  : '''<div><form action="http://example.com/foo/" ><input type="text" name="bar"></form></div>''',
             'form_html_out' : '''<div><form action="/foo/" ><input type="text" name="bar"></form></div>''',
             },
            {'form_html_in'  : '''<div><form action="/foo/" ><input type="text" name="bar"></form></div>''',
             'form_html_out' : '''<div><form action="/foo/" ><input type="text" name="bar"></form></div>''',
             },
            {'form_html_in'  : '''<div><form action="http://example.com/foo/" ><input type="text" name="bar"></form></div>''',
             'urlprefix'     : 'https://mobilewebup.com/',
             'form_html_out' : '''<div><form action="https://mobilewebup.com/foo/" ><input type="text" name="bar"></form></div>''',
             },
            ]
        for ii, td in enumerate(testdata):
            elem = html.fromstring(td['form_html_in'])
            if 'urlprefix' in td:
                formaction(elem, td['urlprefix'])
            else:
                formaction(elem)
            expected = normxml(td['form_html_out'])
            actual = normxml(html.tostring(elem))
            self.assertSequenceEqual(expected, actual)

    def test_imgsub(self):
        from mobilize.filters import imgsub
        html1 = '''<div>
<ul>
<li><img id="a" alt="ima image" width="10" height="20" src="/path/to/a.png"/></li>
<li><img id="b" alt="ima image" width="10" height="20" src="/path/to/b.png"/></li>
<li><img id="c" alt="ima image" width="10" height="20" src="/path/to/c.png"/></li>
<li><img id="d" alt="ima image" width="10" height="20" src="/path/to/d.png"/></li>
<li><img id="e" alt="ima image" width="10" height="20" src="/path/to/e.png"/></li>
<li><img id="f" alt="ima image" width="10" height="20" src="/path/to/f.png"/></li>
<li><img id="g" alt="ima image" width="10" height="20" src="/path/to/g.png"/></li>
</ul>
  <section>
    <div>
      <p>
        <aside>
          <div>
          <span>
<img id="h" alt="ima image" width="10" height="20" src="/path/to/h.png"/>
          </span>
          </div>
        </aside>
      </p>
    </div>
  </section>
</div>
'''
        # This dict defines the mapping of img IDs to the values in
        # html1 and html2 above.  You can create a copy with certain
        # overriden values with the id2src() functions, following, in order
        # to make a specific test. 
        # E.g.:
        #   d = id2src1(a='/path/to/NEWa.png')
        #   d['a']
        #     -> '/path/to/NEWa.png'
        #   d['b']
        #     -> '/path/to/b.png'
        
        _id2src = {
            'a' : '/path/to/a.png',
            'b' : '/path/to/b.png',
            'c' : '/path/to/c.png',
            'd' : '/path/to/d.png',
            'e' : '/path/to/e.png',
            'f' : '/path/to/f.png',
            'g' : '/path/to/g.png',
            'h' : '/path/to/h.png',
            }
        def id2src(**overrides):
            d = dict(_id2src)
            d.update(overrides)
            return d

        testdata = [
            {'subs' : {
                    '/path/to/c.png' : '/mobile/c.png',
                    '/path/to/e.png' : '/mobile/a.png',
                    },
             'expected' : id2src(
                    c = '/mobile/c.png',
                    e = '/mobile/a.png',
                    ),
             },
            {'subs' : {},
             'expected' : id2src(),
             },
            {'subs' : {
                    '/path/to/h.png' : '/mobile/h.png',
                    '/path/to/f.png' : '/mobile/h.png',
                    },
             'expected' : id2src(
                    h = '/mobile/h.png',
                    f = '/mobile/h.png',
                    ),
             },
            ]
        for ii, td in enumerate(testdata):
            root = html.fromstring(html1)
            # check test precondition
            for imgid, srcval in _id2src.items():
                img = root.get_element_by_id(imgid)
                self.assertEqual(img.tag, 'img')
                self.assertEqual(img.attrib['src'], srcval)
            imgsub(root, td['subs'])
            for imgid, srcval in td['expected'].items():
                img = root.get_element_by_id(imgid)
                self.assertEqual(img.attrib['src'], srcval)

        # test for callable imgsub value
        def alter_c(elem):
            self.assertEqual('img', elem.tag)
            elem.attrib['src'] = '/mobile/c.png'
            elem.attrib['width'] = '45'
            elem.attrib['height'] = '95'
        def alter_h(elem):
            self.assertEqual('img', elem.tag)
            elem.attrib['src'] = '/mobile/h.png'
            elem.attrib['width'] = '145'
            del elem.attrib['height']
        subs = {
            '/path/to/c.png' : alter_c,
            '/path/to/h.png' : alter_h,
            }
        root = html.fromstring(html1)
        imgsub(root, subs)
        img_c = root.get_element_by_id('c')
        self.assertEqual('/mobile/c.png', img_c.attrib['src'])
        self.assertEqual('45', img_c.attrib['width'])
        self.assertEqual('95', img_c.attrib['height'])
        img_h = root.get_element_by_id('h')
        self.assertEqual('/mobile/h.png', img_h.attrib['src'])
        self.assertEqual('145', img_h.attrib['width'])
        self.assertFalse('height' in img_h.attrib)
