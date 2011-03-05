import unittest
from utils4test import data_file_path, DATA_DIR
from mobilize.refineclass import Extracted

class DummyExtracted(Extracted):
    def _extract(self, source):
        assert self.elem, 'You must set the elem property manually in this test class'

class TestRefine(unittest.TestCase):
    def test_process(self):
        from lxml import html
        testdata = [
            {'elem_str'    : '<p>Hello</p>',
             'classname'   : 'alpha',
             'idname'      : 'beta',
             'newelem_str' : '<div class="alpha" id="beta"><p>Hello</p></div>',
             },
            ]
        for ii, td in enumerate(testdata):
            refinement = DummyExtracted('')
            refinement.elem = html.fromstring(td['elem_str'])
            newelem = refinement.process(td['classname'], td['idname'], {})
            self.assertEqual(newelem, refinement.elem)
            self.assertEqual(html.HtmlElement, type(refinement.elem))
            self.assertSequenceEqual(td['newelem_str'], html.tostring(refinement.elem))

    def test_extract_csspath(self):
        from mobilize.refineclass import CssPath
        from lxml import html
        testdata = [
            {'datafile' : 'a.xml',
             'selectors' : [CssPath('div#happy')],
             'extracted' : ['<div id="happy">lucky</div>'],
             },
            {'datafile' : 'b.xml',
             'selectors' : [CssPath('div#joyful')],
             'extracted' : ['<div id="joyful">fun</div>'],
             },
            {'datafile' : 'c.xml',
             'selectors' : [CssPath('p.graceful')],
             'extracted' : ['<p class="graceful">laughing</p>'],
             },
            {'datafile' : 'd.xml',
             'selectors' : [CssPath('p.graceful')],
             'extracted' : ['<p class="skipping graceful enthusiastic">laughing</p>'],
             },
            # {'datafile' : 'e.xml',
            #  'selectors' : [CssPath('p.graceful')],
            #  'extracted' : ['<p class="skipping graceful enthusiastic">laughing</p>', '<p class="graceful">enthusiastic</p>'],
            #  },
            ]
        for ii, td in enumerate(testdata):
            doc = html.fromstring(open(data_file_path('extract_celems', td['datafile'])).read())
            for sel in td['selectors']:
                sel.extract(doc)
            expected = td['extracted']
            actual = [sel.html() for sel in td['selectors']]
            msg = 'e: %s, a: %s [%d %s]' % (expected, actual, ii, td['datafile'])
            self.assertEqual(expected, actual, msg)

