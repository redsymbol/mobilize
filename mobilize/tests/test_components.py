# Copyright 2010-2012 Mobile Web Up. All rights reserved.
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

    def test_keep_if(self):
        from mobilize.components import CssPath
        from lxml import html
        html = html.fromstring('''<!doctype html>
<html>
<body>
<div id="foo">
  <a href="/beta">Read Beta</a>
  <a href="/alpha">Download Alpha</a>
  <a href="/gamma/">Experience Gamma</a>
</div>
</body>
</html>
''')
        # verify default is to keep everything
        component_all = CssPath('div#foo a')
        extracted_all = component_all.extract(html)
        self.assertEqual(3, len(extracted_all))

        # keep only the "download" link
        def pred(elem):
            return 'download' in elem.text.lower()
        component = CssPath('div#foo a', keep_if=pred)
        extracted = component.extract(html)
        self.assertEqual(1, len(extracted))
        self.assertEqual('/alpha', extracted[0].attrib['href'])
        
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

    def test_GoogleAnalytics_v1(self):
        from mobilize.components import GoogleAnalytics
        # Check positive case, where we expect to find the GA tracking code (older version)
        doc_str = open(data_file_path('whole-html', 'luxwny.html')).read()
        doc = html.fromstring(doc_str)
        ga = GoogleAnalytics()
        ga.extract(doc)
        ga.process()
        extracted_str = ga.html()
        extracted = html.fromstring(extracted_str)
        extracted_script_tags = extracted.cssselect('script')
        self.assertEqual(len(extracted_script_tags), 2)
        ga_script1_text = extracted_script_tags[0].text
        self.assertTrue('var gaJsHost' in ga_script1_text)
        ga_script2_text = extracted_script_tags[1].text
        self.assertTrue('UA-12345678-1' in ga_script2_text)

    def test_GoogleAnalytics_none(self):
        # Check negative case where we expect to not find GA tracking codes
        from mobilize.components import GoogleAnalytics
        doc_str = open(data_file_path('whole-html', 'cnn.html')).read()
        doc = html.fromstring(doc_str)
        noga = GoogleAnalytics()
        noga.extract(doc)
        noga.process()
        actual = normxml(noga.html())
        expected = normxml('''<div class="mwu-elem" id="mwu-elem-ga"></div>''')
        self.assertSequenceEqual(expected, actual)
        
    def test_GoogleAnalytics_v2(self):
        # Check positive case, where we expect to find the GA tracking codes
        from mobilize.components import GoogleAnalytics
        testdatafiles = [
            'msia.org.html',   # variant 1
            'msia.org.2.html', # variant 2
            ]
        for testdatafile in testdatafiles:
            doc_str = open(data_file_path('whole-html', testdatafile)).read()
            doc = html.fromstring(doc_str)
            ga = GoogleAnalytics()
            ga.extract(doc)
            ga.process()
            extracted_str = ga.html()
            extracted = html.fromstring(extracted_str)
            extracted_script_tags = extracted.cssselect('script')
            self.assertEqual(len(extracted_script_tags), 1, testdatafile)
            ga_script_text = extracted_script_tags[0].text
            self.assertTrue('UA-12345678-1' in ga_script_text, testdatafile)

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

    def test_omit_dupe_extractions(self):
        '''
        Verify that selectors resolving to duplicate elements are discarded

        It's entirely possible for a list of N selectors (either xpath
        strings, or css path strings) to produce a list of extracted
        elements that have some duplicates.  A real world example is
        when one client inconsistendly used <div id="content1"> and
        <div class="content1"> in their templates, while intending
        them to mean the same thing.  A component catching both was
        CssPath(['div#content1', 'div.content1']).  This worked fine
        until the client started creating divs like: <div
        class="content1" id="content1">.

        What we normally want to do is to keep only the first matching
        element, and perhaps log a warning.
        '''
        from mobilize.components.extracted import CssPath
        doc_str = '''<html>
  <body>
    <div id="hello" class="blargh hello">
      Hello, earthling! Are you... CRUNCHY
    </div>
  </body>
</html>'''
        css_selectors = [
            'div.hello',
            'div#hello',
            ]
        doc = html.fromstring(doc_str)
        component = CssPath(css_selectors)
        extracted = component.extract(doc)
        self.assertEqual(1, len(extracted))
        

