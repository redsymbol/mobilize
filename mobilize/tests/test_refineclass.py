import unittest
from utils4test import data_file_path, DATA_DIR, normxml
from mobilize.refineclass import Extracted

class DummyExtracted(Extracted):
    def _extract(self, source):
        assert self.elem, 'You must set the elem property manually in this test class'

class TestRefine(unittest.TestCase):
    def test_process(self):
        from lxml import html
        testdata = [
            {'elem_str'    : '<p>Hello</p>',
             'idname'      : 'beta',
             'newelem_str' : '<div class="alpha" id="beta"><p>Hello</p></div>',
             },
            ]
        for ii, td in enumerate(testdata):
            refinement = DummyExtracted('', filters=[], classvalue='alpha')
            refinement.elems = [html.fromstring(td['elem_str'])]
            newelem = refinement.process(td['idname'])
            self.assertEqual(newelem, refinement.elem)
            self.assertEqual(html.HtmlElement, type(refinement.elem))
            self.assertSequenceEqual(td['newelem_str'], html.tostring(refinement.elem))

    def test_extract_csspath(self):
        from mobilize.refineclass import CssPath
        from lxml import html

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

    def test_Extracted_filtersetup(self):
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

