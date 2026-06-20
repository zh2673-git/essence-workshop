"""
测试 content-output/scripts/pipelines/platforms/ 中的视频平台适配器
"""
import os
import sys
import unittest

PIPELINES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'pipelines')
)
sys.path.insert(0, PIPELINES_DIR)

from platforms import get_adapter, list_platforms
from platforms.video_channel import VideoChannelAdapter
from platforms.bilibili import BilibiliAdapter
from platforms.douyin import DouyinAdapter


class TestVideoPlatformAdapters(unittest.TestCase):
    def test_list_platforms(self):
        platforms = list_platforms()
        self.assertIn('video-channel', platforms)
        self.assertIn('bilibili', platforms)
        self.assertIn('douyin', platforms)

    def test_video_channel_defaults(self):
        adapter = VideoChannelAdapter()
        options = adapter.apply({'duration': 9, 'width': 0, 'height': 0})
        self.assertEqual(options['width'], 1080)
        self.assertEqual(options['height'], 1920)
        self.assertEqual(options['fps'], 30)

    def test_bilibili_defaults(self):
        adapter = BilibiliAdapter()
        options = adapter.apply({'duration': 9, 'width': 0, 'height': 0})
        self.assertEqual(options['width'], 1920)
        self.assertEqual(options['height'], 1080)

    def test_douyin_defaults(self):
        adapter = DouyinAdapter()
        options = adapter.apply({'duration': 9, 'width': 0, 'height': 0})
        self.assertEqual(options['width'], 720)
        self.assertEqual(options['height'], 1280)

    def test_user_override_preserved(self):
        adapter = VideoChannelAdapter()
        options = adapter.apply({'duration': 9, 'width': 1920, 'height': 1080})
        self.assertEqual(options['width'], 1920)
        self.assertEqual(options['height'], 1080)

    def test_duration_validation(self):
        adapter = VideoChannelAdapter()
        errors = adapter.validate({'duration': 9999})
        self.assertTrue(len(errors) > 0)

    def test_get_adapter_unknown(self):
        with self.assertRaises(ValueError):
            get_adapter('unknown')


if __name__ == '__main__':
    unittest.main()
