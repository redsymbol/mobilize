import unittest
from mobilize.refineclass import Extracted
class DummyExtracted(Extracted):
    def _extract(self, source):
        assert self.elem, 'You must set the elem property manually in this test class'

class TestRefine(unittest.TestCase):
    def test_process(self):
        from lxml import html
        from mobilize.base import process_elem
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
