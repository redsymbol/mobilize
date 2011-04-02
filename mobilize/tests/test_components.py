import unittest
from utils4test import data_file_path, normxml
from mobilize.components import Extracted
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
            self.assertSequenceEqual(td['newelem_str'], html.tostring(component.elem))

    def test_extract_csspath(self):
        from mobilize.components import CssPath

        testdata = [
            {'datafile' : 'a.xml',
             'selectors' : [CssPath('div#happy', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><div id="happy">lucky</div></div>'],
             },
            {'datafile' : 'b.xml',
             'selectors' : [CssPath('div#joyful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><div id="joyful">fun</div></div>'],
             },
            {'datafile' : 'c.xml',
             'selectors' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="graceful">laughing</p></div>'],
             },
            {'datafile' : 'd.xml',
             'selectors' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="skipping graceful enthusiastic">laughing</p></div>'],
             },
            {'datafile' : 'e.xml',
             'selectors' : [CssPath('p.graceful', classvalue='some-class')],
             'extracted' : ['<div class="some-class" id="some-id"><p class="skipping graceful enthusiastic">laughing</p><p class="graceful">enthusiastic</p></div>'],
             },
            ]
        for ii, td in enumerate(testdata):
            doc = html.fromstring(open(data_file_path('extract_celems', td['datafile'])).read())
            for sel in td['selectors']:
                sel.extract(doc)
                sel.process('some-id')
            expected = map(normxml, td['extracted'])
            actual = [normxml(sel.html()) for sel in td['selectors']]
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
        from mobilize.filters import COMMON_FILTERS
        extracted = DummyExtracted('')
        self.assertEquals(extracted.filters, COMMON_FILTERS)
        extracted = DummyExtracted('', filters=[])
        self.assertEquals(extracted.filters, [])
        extracted = DummyExtracted('', prefilters=[foo], postfilters=[bar])
        self.assertEquals(extracted.filters, [foo] + COMMON_FILTERS + [bar])
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
        # Check positive case, where we expect to find the GA tracking code
        doc_str = open(data_file_path('whole-html', 'luxwny.html')).read()
        doc = html.fromstring(doc_str)
        ga = GoogleAnalytics()
        ga.extract(doc)
        ga.process('nothing')
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

        # Check negative case where we expect to not find any code
        doc_str = open(data_file_path('whole-html', 'cnn.html')).read()
        doc = html.fromstring(doc_str)
        noga = GoogleAnalytics()
        noga.extract(doc)
        noga.process('nothing')
        actual = normxml(noga.html())
        expected = normxml('''<div class="mwu-elem" id="mwu-elem-ga"></div>''')
        self.assertSequenceEqual(expected, actual)
        
