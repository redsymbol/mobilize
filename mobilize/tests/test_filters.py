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
  <div class="mwu-melem-table2divgroups">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
      <div>CONTACT US</div>
    </div>
    <div class="mwu-melem-table2divgroups-group" id="idname2">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname2">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname2">
      <div>CONTACT US</div>
      <div>123 Main Str</div>
      <div>Springfield, IL</div>
      <div>1-800-BUY-DUFF</div>
    </div>
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
  <div class="mwu-melem-table2divgroups">
    <div class="mwu-melem-table2divgroups-group" id="idname1">
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
        from mobilize.refineclass import (
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
        expected_str = '''<div class="mwu-melem" id="idname">
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
        expected_str = '''<div class="mwu-melem" id="idname">
<a href="/" id="child-0">a</a>
<a href="/" id="child-1">b</a>
<a href="/" id="child-2">c</a>
</div>
'''
        self.assertSequenceEqual(normxml(expected_str), normxml(actual_str))
