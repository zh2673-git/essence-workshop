"""
测试 content-output/scripts/pipelines/markdown/generator.py
以及 obsidian 平台适配器
"""
import os
import sys
import tempfile
import unittest

PIPELINES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'pipelines')
)
sys.path.insert(0, PIPELINES_DIR)

from markdown.generator import generate_markdown
from platforms.obsidian import ObsidianAdapter


class TestMarkdownGenerator(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.elements_dir = os.path.join(self.tmpdir.name, 'elements')
        self.output_dir = os.path.join(self.tmpdir.name, 'out')
        os.makedirs(os.path.join(self.elements_dir, 'text'))
        with open(os.path.join(self.elements_dir, 'text', 'intro.md'), 'w', encoding='utf-8') as f:
            f.write('# Hello\n\nThis is a test.\n\n> [!NOTE]\n> Obsidian callout')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_generate_markdown_default(self):
        path = generate_markdown(self.elements_dir, self.output_dir, title='Test')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('title: Test', content)
        self.assertIn('# Hello', content)
        self.assertIn('This is a test.', content)

    def test_generate_markdown_obsidian(self):
        path = generate_markdown(self.elements_dir, self.output_dir, title='Test', platform='obsidian')
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # callout 转换
        self.assertIn('> [!NOTE]', content)
        # 标题
        self.assertIn('# Test', content)

    def test_generate_markdown_with_svg(self):
        os.makedirs(os.path.join(self.elements_dir, 'graphics'))
        svg_path = os.path.join(self.elements_dir, 'graphics', 'diagram.svg')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg"><text>Hi</text></svg>')

        path = generate_markdown(self.elements_dir, self.output_dir, title='Test', platform='obsidian')
        asset_path = os.path.join(self.output_dir, 'assets', 'diagram.svg')
        self.assertTrue(os.path.exists(asset_path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('![[diagram.svg]]', content)


class TestObsidianAdapter(unittest.TestCase):
    def test_supported_forms(self):
        adapter = ObsidianAdapter()
        self.assertEqual(adapter.supported_forms, ['markdown'])

    def test_constraint(self):
        adapter = ObsidianAdapter()
        constraint = adapter.get_constraint('markdown')
        self.assertTrue(constraint['wiki_links'])
        self.assertTrue(constraint['callouts'])
        self.assertFalse(constraint['inline_svg'])
        self.assertEqual(constraint['attachment_dir'], 'assets')

    def test_validate_unsupported_form(self):
        adapter = ObsidianAdapter()
        errors = adapter.validate('html', {})
        self.assertTrue(len(errors) > 0)


if __name__ == '__main__':
    unittest.main()
