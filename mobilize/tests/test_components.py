import unittest
from utils4test import data_file_path, normxml
from mobilize.components import Extracted
from mobilize.util import elem2str
from lxml import html

class DummyExtracted(Extracted):
    def _extract(self, source):
        assert self.elem, 'You must set the elem property manually in this test class'

class DirectExtracted(Extracted):
    def _extract(self, source):
        return [source]

class TestExtracted(unittest.TestCase):
    maxDiff = 1024**2
    def test_process(self):
        testdata = [
            {'elem_str'    : '<p>Hello</p>',
             'idname'      : 'beta',
             'newelem_str' : '<div class="alpha" id="beta"><p>Hello</p></div>',
             },
            ]
        for ii, td in enumerate(testdata):
            component = DummyExtracted('', filters=[], classvalue='alpha')
            component.elems = [html.fromstring(td['elem_str'])]
            newelem = component.process(td['idname'])
            self.assertEqual(newelem, component.elem)
            self.assertEqual(html.HtmlElement, type(component.elem))
            self.assertSequenceEqual(td['newelem_str'], elem2str(component.elem))

    def test_extract_csspath(self):
        from mobilize.components import CssPath

        testdata = [
            {'datafile' : 'a.xml',
             'components' : [CssPath('div#happy', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><div id="happy">lucky</div></div>'],
             },
            {'datafile' : 'b.xml',
             'components' : [CssPath('div#joyful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><div id="joyful">fun</div></div>'],
             },
            {'datafile' : 'c.xml',
             'components' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="graceful">laughing</p></div>'],
             },
            {'datafile' : 'd.xml',
             'components' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="skipping graceful enthusiastic">laughing</p></div>'],
             },
            {'datafile' : 'e.xml',
             'components' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="skipping graceful enthusiastic">laughing</p><p class="graceful">enthusiastic</p></div>'],
             },
            ]
        for ii, td in enumerate(testdata):
            doc = html.fromstring(open(data_file_path('extract_celems', td['datafile'])).read())
            for sel in td['components']:
                sel.extract(doc)
                sel.process('some-id')
            expected = list(map(normxml, td['extracted']))
            actual = [normxml(sel.html()) for sel in td['components']]
            msg = 'e: %s, a: %s [%d %s]' % (expected, actual, ii, td['datafile'])
            self.assertEqual(expected, actual, msg)

    def test_filtersetup(self):
        '''test that filters are set up properly'''
        def foo(elem):
            pass
        def bar(elem):
            pass
        def baz(elem):
            pass
        from mobilize.filters import DEFAULT_FILTERS
        extracted = DummyExtracted('')
        self.assertEquals(extracted.filters, DEFAULT_FILTERS)
        extracted = DummyExtracted('', filters=[])
        self.assertEquals(extracted.filters, [])
        extracted = DummyExtracted('', prefilters=[foo], postfilters=[bar])
        self.assertEquals(extracted.filters, [foo] + DEFAULT_FILTERS + [bar])
        ok = False
        try:
            extracted = DummyExtracted('', filters=[baz], prefilters=[foo], postfilters=[bar])
        except AssertionError:
            ok = True
        self.assertTrue(ok)

    def test_style(self):
        '''test that style attribute is set properly'''
        style = 'background-color: red; font-size: large;'
        sourcestr = '''<ul>
  <li>Dre</li>
  <li>Snoop</li>
  <li>Thug Life</li>
</ul>'''
        extracted = DirectExtracted('', style=style)
        extracted._sourcestr = sourcestr
        extracted.extract(html.fromstring(sourcestr))
        extracted.process('foo')
        rendered = extracted.elem
        # verify that the first child is the source string...
        firstchild_elem = rendered[0]
        self.assertSequenceEqual(normxml(sourcestr), normxml(html.tostring(firstchild_elem)))
        # check the style attribute
        self.assertEqual(style, rendered.attrib['style'])

    def test_GoogleAnalytics(self):
        from mobilize.components import GoogleAnalytics
        # Check positive case, where we expect to find the GA tracking code (older version)
        doc_str = open(data_file_path('whole-html', 'luxwny.html')).read()
        doc = html.fromstring(doc_str)
        ga = GoogleAnalytics()
        ga.extract(doc)
        ga.process()
        actual = normxml(ga.html())
        expected = normxml('''<div class="mwu-elem" id="mwu-elem-ga">
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-7559570-4");
pageTracker._trackPageview();
} catch(err) {}</script>
</div>
''')
        self.assertSequenceEqual(expected, actual)

        # Check positive case, where we expect to find the GA tracking code (newer version)
        doc_str = open(data_file_path('whole-html', 'msia.org.html')).read()
        doc = html.fromstring(doc_str)
        ga = GoogleAnalytics()
        ga.extract(doc)
        ga.process()
        actual = normxml(ga.html())
        expected = normxml('''<div class="mwu-elem" id="mwu-elem-ga">
<script type="text/javascript"> 

  var _gaq = _gaq || []; 
  _gaq.push(['_setAccount', 'UA-17055085-1']); 
  _gaq.push(['_trackPageview']); 

  (function() { 
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; 
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; 
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); 
  })(); 
</script>
</div>
''')
        self.assertSequenceEqual(expected, actual)
        
        # Check negative case where we expect to not find any code
        doc_str = open(data_file_path('whole-html', 'cnn.html')).read()
        doc = html.fromstring(doc_str)
        noga = GoogleAnalytics()
        noga.extract(doc)
        noga.process()
        actual = normxml(noga.html())
        expected = normxml('''<div class="mwu-elem" id="mwu-elem-ga"></div>''')
        self.assertSequenceEqual(expected, actual)


    def test_innerhtml(self):
        from mobilize.components import XPath
        html_str = '''<table><tr><td>Hello</td></tr></table>'''
        # test for innerhtml=False
        component_f = XPath('//td', idname='foo', innerhtml=False)
        component_f.extract(html.fromstring(html_str))
        extracted = component_f.process()
        extracted_str = html.tostring(extracted)
        expected = '<div class="mwu-elem" id="foo"><td>Hello</td></div>'
        e = normxml(expected)
        a = normxml(extracted_str)
        self.assertSequenceEqual(e, a)
        
        # test for innerhtml=True
        component_t = XPath('//td', idname='foo', innerhtml=True)
        component_t.extract(html.fromstring(html_str))
        extracted = component_t.process()
        extracted_str = html.tostring(extracted)
        expected = '<div class="mwu-elem" id="foo">Hello</div>'
        self.assertSequenceEqual(normxml(expected), normxml(extracted_str))
        
        # test for ineffectiveness of innerhtml=True with multiple matching elements
        component_t = XPath('//td', idname='foo', innerhtml=True)
        component_t.extract(html.fromstring('''
<table><tr>
<td>Hello</td>
<td>Goodbye</td>
</tr></table>
'''))
        extracted = component_t.process()
        extracted_str = html.tostring(extracted)
        expected = '<div class="mwu-elem" id="foo"><td>Hello</td><td>Goodbye</td></div>'
        self.assertSequenceEqual(normxml(expected), normxml(extracted_str))
        
    def test_select_multiple(self):
        '''
        Test that extracted components can accept multiple selectors
        '''
        from mobilize.components import CssPath, XPath
        selectors = [
            'nav',
            'section',
            ]
        src_html = '''<div>
<nav>
  <a href="/A">A</a>
  <a href="/B">B</a>
</nav>
<table><tr><td>&nbsp;</td><td>I'm using tables for layout!!! DUR</td></tr></table>
<section>
<p>Hello.</p>
</section>
</div>
'''
        expected_html = '''<div class="mwu-elem" id="foo">
<nav>
  <a href="/A">A</a>
  <a href="/B">B</a>
</nav>
<section>
<p>Hello.</p>
</section>
</div>'''
        # test for CssPath
        css_component = CssPath(selectors, idname='foo')
        css_component.extract(html.fromstring(src_html))
        extracted = css_component.process()
        extracted_str = html.tostring(extracted)
        self.assertSequenceEqual(normxml(expected_html), normxml(extracted_str))

        # test for XPath
        x_component = XPath(selectors, idname='foo')
        x_component.extract(html.fromstring(src_html))
        extracted = x_component.process()
        extracted_str = html.tostring(extracted)
        self.assertSequenceEqual(normxml(expected_html), normxml(extracted_str))

    def test_process_idname(self):
        from mobilize.components import CssPath, XPath
        src_html = '''<div>
<nav>
  <a href="/A">A</a>
  <a href="/B">B</a>
</nav>
'''
        def prep_component(**kw):
            return c
        # check that default_idname is required if self.idname not defined
        c1 = CssPath('nav')
        c1.extract(html.fromstring(src_html))
        with self.assertRaises(AssertionError):
            c1.process()

        # check that idname argument 
        c2 = CssPath('nav', idname='foo')
        c2.extract(html.fromstring(src_html))
        c2.process() # no AssertionError on this line meanst the test passes

        # check that default_idname supresses the error
        c3 = CssPath('nav')
        c3.extract(html.fromstring(src_html))
        c3.process('foo') # no AssertionError on this line meanst the test passes

    def test__pick_filters(self):
        from mobilize import filters
        from mobilize.components.extracted import _pick_filters

        # Some filters we'll use in the tests
        @filters.filterapi
        def dummyfilter1(elem): pass
        @filters.filterapi
        def dummyfilter2(elem): pass
        @filters.filterapi
        def dummyfilter3(elem): pass
        @filters.filterapi
        def dummyfilter4(elem): pass
        
        defaultfilters = [
            dummyfilter1,
            dummyfilter2,
            ]
        testdata = [
            {'args' : {'filters' : None,
                       'prefilters' : None,
                       'postfilters' : None,
                       'omitfilters' : None,
                       },
             'expected' : list(defaultfilters),
             },
            {'args' : {'filters' : [dummyfilter3, dummyfilter1],
                       'prefilters' : None,
                       'postfilters' : None,
                       'omitfilters' : None,
                       },
             'expected' : [dummyfilter3, dummyfilter1],
             },
            {'args' : {'filters' : None,
                       'prefilters' : [dummyfilter4],
                       'postfilters' :[dummyfilter3],
                       'omitfilters' : None,
                       },
             'expected' : [
                        dummyfilter4,
                        dummyfilter1,
                        dummyfilter2,
                        dummyfilter3,
                        ]
             },
            {'args' : {'filters' : None,
                       'prefilters' : [dummyfilter4],
                       'postfilters' :[dummyfilter3],
                       'omitfilters' : [dummyfilter1],
                       },
             'expected' : [
                        dummyfilter4,
                        dummyfilter2,
                        dummyfilter3,
                        ]
             },
            ]
        for ii, td in enumerate(testdata):
            args = dict(td['args'])
            args['_default'] = defaultfilters
            self.assertListEqual(td['expected'], _pick_filters(**args), ii)

        # Should fail loudly if filters and some other arg are specified
        # TODO: implement assertRaises tests
