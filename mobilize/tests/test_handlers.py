import unittest
from lxml import html


class TestMoplate(unittest.TestCase):
    def test_source_params(self):
        '''test that default parameters are correctly extracted from the source document'''
        from mobilize.handlers import _rendering_params
        src1 = '''<!doctype html>
<html>
<head>
<title>Source Title</title>
</head>
<body>
<h1>Source Heading</h1>
<p>Hello.</p>
<h1>Second Source Heading that we want to ignore</h1>
</body>
</html>'''
        doc = html.fromstring(src1)
        # general case
        expected = {
            'title' : 'Source Title',
            'heading' : 'Source Heading',
            }
        actual = _rendering_params(doc, [])
        self.assertEqual(expected, actual)

        # with an override
        expected = {
            'title' : 'Override Title',
            'heading' : 'Source Heading',
            }
        actual = _rendering_params(doc, [{'title' : 'Override Title'}])
        self.assertEqual(expected, actual)

    def test__todesktoplink(self):
        from mobilize.handlers import _todesktoplink
        self.assertEqual('http://example.com/foobar.html?mredir=0',
                         _todesktoplink('http', 'example.com', '/foobar.html'))
        self.assertEqual('https://example.com/foobar.html?mredir=0',
                         _todesktoplink('https', 'example.com', '/foobar.html'))
        self.assertEqual('http://example.com/foobar.html?baz=2&mredir=0',
                         _todesktoplink('http', 'example.com', '/foobar.html?baz=2'))

class TestWebSourcer(unittest.TestCase):
    def test_source_uri(self):
        from mobilize.handlers import WebSourcer
        testdata = [
            {'source_uri_mapper' : None,
             'rel_uri_in' : '/foo/bar',
             'rel_uri_out' : '/foo/bar',
             },
            {'source_uri_mapper' : '/baz',
             'rel_uri_in' : '/foo/bar',
             'rel_uri_out' : '/baz',
             },
            {'source_uri_mapper' : lambda u: u.replace('.php', '.html', 1),
             'rel_uri_in' : '/foo.php',
             'rel_uri_out' : '/foo.html',
             },
            {'source_uri_mapper' : lambda u: u,
             'rel_uri_in' : '/foo/bar',
             'rel_uri_out' : '/foo/bar',
             },
            ]
        for ii, td in enumerate(testdata):
            ws = WebSourcer(source_uri_mapper = td['source_uri_mapper'])
            expected = td['rel_uri_out']
            actual = ws.source_rel_uri(td['rel_uri_in'])
            self.assertSequenceEqual(expected, actual, ii)

class TestRedirect(unittest.TestCase):
    def test_mk_redirect(self):
        from mobilize.handlers import (
            redirect_to,
            Redirect,
            )
        handler = redirect_to('/foo/bar')
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('302 Found', handler.status)

        handler = redirect_to('/foo/bar', 302)
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('302 Found', handler.status)

        handler = redirect_to('/foo/bar', 301)
        self.assertTrue(isinstance(handler, Redirect), handler)
        self.assertEqual('301 Moved Permanently', handler.status)
