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
    def test_source_url(self):
        from mobilize.handlers import WebSourcer
        testdata = [
            {'source_url_mapper' : None,
             'url_in' : '/foo/bar',
             'url_out' : '/foo/bar',
             },
            {'source_url_mapper' : '/baz',
             'url_in' : '/foo/bar',
             'url_out' : '/baz',
             },
            {'source_url_mapper' : lambda u: u.replace('.php', '.html', 1),
             'url_in' : '/foo.php',
             'url_out' : '/foo.html',
             },
            {'source_url_mapper' : lambda u: u,
             'url_in' : '/foo/bar',
             'url_out' : '/foo/bar',
             },
            ]
        for ii, td in enumerate(testdata):
            ws = WebSourcer(source_url_mapper = td['source_url_mapper'])
            expected = td['url_out']
            actual = ws.source_url(td['url_in'])
            self.assertSequenceEqual(expected, actual, ii)
