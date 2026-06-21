"""
测试 content-output/scripts/pipelines/platforms/ 统一平台适配器
"""
import os
import sys
import unittest

PIPELINES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'pipelines')
)
sys.path.insert(0, PIPELINES_DIR)

from platforms import get_adapter, list_platforms, supported_platforms_for_form
from platforms.browser import BrowserAdapter
from platforms.wechat import WechatAdapter
from platforms.office import OfficeAdapter
from platforms.jupyter import JupyterAdapter
from platforms.reveal import RevealAdapter
from platforms.obsidian import ObsidianAdapter


class TestUnifiedPlatforms(unittest.TestCase):
    def test_list_platforms(self):
        platforms = list_platforms()
        self.assertIn('browser', platforms)
        self.assertIn('wechat', platforms)
        self.assertIn('office', platforms)
        self.assertIn('jupyter', platforms)
        self.assertIn('reveal', platforms)
        self.assertIn('obsidian', platforms)

    def test_supported_platforms(self):
        self.assertIn('obsidian', supported_platforms_for_form('markdown'))
        self.assertIn('browser', supported_platforms_for_form('html'))
        self.assertIn('wechat', supported_platforms_for_form('html'))
        self.assertIn('browser', supported_platforms_for_form('slides'))
        self.assertIn('reveal', supported_platforms_for_form('slides'))
        self.assertIn('office', supported_platforms_for_form('pptx'))
        self.assertIn('jupyter', supported_platforms_for_form('notebook'))

    def test_browser_adapter(self):
        adapter = BrowserAdapter()
        options = adapter.apply('html', {})
        self.assertEqual(options['_platform'], 'browser')
        self.assertFalse(adapter.validate('html', {}))
        self.assertTrue(len(adapter.validate('pptx', {})) > 0)

    def test_wechat_adapter(self):
        adapter = WechatAdapter()
        options = adapter.apply('html', {})
        self.assertEqual(options['_platform'], 'wechat')
        constraint = adapter.get_constraint('html')
        self.assertTrue(constraint['inline_css'])
        self.assertFalse(constraint['allow_script'])

    def test_office_adapter(self):
        adapter = OfficeAdapter()
        options = adapter.apply('pptx', {})
        self.assertEqual(options['_platform'], 'office')

    def test_jupyter_adapter(self):
        adapter = JupyterAdapter()
        options = adapter.apply('notebook', {})
        self.assertEqual(options['_platform'], 'jupyter')

    def test_reveal_adapter(self):
        adapter = RevealAdapter()
        options = adapter.apply('slides', {})
        self.assertEqual(options['_platform'], 'reveal')

    def test_obsidian_adapter(self):
        adapter = ObsidianAdapter()
        options = adapter.apply('markdown', {})
        self.assertEqual(options['_platform'], 'obsidian')
        constraint = adapter.get_constraint('markdown')
        self.assertTrue(constraint['wiki_links'])
        self.assertFalse(constraint['inline_svg'])

    def test_get_adapter_unknown(self):
        with self.assertRaises(ValueError):
            get_adapter('unknown')


if __name__ == '__main__':
    unittest.main()
