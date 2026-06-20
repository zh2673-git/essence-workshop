"""
测试 content-output/scripts/pipelines/video/router.py
"""
import os
import sys
import unittest

VIDEO_PIPELINE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'pipelines', 'video')
)
sys.path.insert(0, VIDEO_PIPELINE)

from router import select_pipeline, select_method, explain_decision


class TestRouter(unittest.TestCase):
    def test_prefer_dsl(self):
        d = select_method({}, {'preferDsl': True})
        self.assertEqual(d['method'], 'dsl')
        self.assertEqual(d['platform'], 'video-channel')

    def test_wechat_article(self):
        d = select_method({'source': 'wechat_article'})
        self.assertEqual(d['method'], 'article_to_video')
        self.assertEqual(d['platform'], 'video-channel')

    def test_html_record(self):
        d = select_method({'hasStructuredHTML': True, 'visualComplexity': 'low', 'durationSeconds': 30})
        self.assertEqual(d['method'], 'html_record')

    def test_high_complexity_goes_dsl(self):
        d = select_method({'visualComplexity': 'high'})
        self.assertEqual(d['method'], 'dsl')

    def test_animation_goes_dsl(self):
        d = select_method({'hasAnimationRequirements': True})
        self.assertEqual(d['method'], 'dsl')

    def test_platform_bilibili(self):
        d = select_method({'platform': 'bilibili', 'hasAnimationRequirements': True})
        self.assertEqual(d['method'], 'dsl')
        self.assertEqual(d['platform'], 'bilibili')

    def test_explain_non_empty(self):
        d = select_method({'visualComplexity': 'high'})
        self.assertTrue(len(explain_decision(d)) > 0)
        self.assertIn('video-channel', explain_decision(d))

    # 向后兼容
    def test_legacy_select_pipeline(self):
        d = select_pipeline({'hasAnimationRequirements': True})
        self.assertEqual(d['method'], 'dsl')


if __name__ == '__main__':
    unittest.main()
