"""
测试 content-output/scripts/pipelines/dispatcher.py
"""
import os
import sys
import tempfile
import unittest

PIPELINES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'pipelines')
)
sys.path.insert(0, PIPELINES_DIR)

from dispatcher import dispatch, apply_platform


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.elements_dir = os.path.join(self.tmpdir.name, 'elements')
        os.makedirs(os.path.join(self.elements_dir, 'text'))
        with open(os.path.join(self.elements_dir, 'text', 'intro.md'), 'w', encoding='utf-8') as f:
            f.write('# Test\n\nHello')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_apply_platform_browser_html(self):
        options = apply_platform('browser', 'html', {'elements_dir': self.elements_dir})
        self.assertEqual(options['_platform'], 'browser')

    def test_apply_platform_wechat_html(self):
        options = apply_platform('wechat', 'html', {'elements_dir': self.elements_dir})
        self.assertEqual(options['_platform'], 'wechat')
        self.assertTrue(options.get('_platform_description'))

    def test_apply_platform_unsupported(self):
        with self.assertRaises(ValueError):
            apply_platform('wechat', 'pptx', {'elements_dir': self.elements_dir})

    def test_dispatch_notebook(self):
        output_dir = os.path.join(self.tmpdir.name, 'out')
        path = dispatch('notebook', 'jupyter', self.elements_dir, output_dir, title='Test')
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith('.ipynb'))

    def test_dispatch_html(self):
        output_dir = os.path.join(self.tmpdir.name, 'out-html')
        path = dispatch('html', 'browser', self.elements_dir, output_dir, title='Test')
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith('index.html'))

    def test_dispatch_slides(self):
        output_dir = os.path.join(self.tmpdir.name, 'out-slides')
        path = dispatch('slides', 'browser', self.elements_dir, output_dir, title='Test')
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith('index.html'))

    def test_dispatch_markdown(self):
        output_dir = os.path.join(self.tmpdir.name, 'out-md')
        path = dispatch('markdown', 'obsidian', self.elements_dir, output_dir, title='Test')
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith('index.md'))


if __name__ == '__main__':
    unittest.main()
