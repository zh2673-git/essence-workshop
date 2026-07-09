"""
测试 format/video/scripts/router.py

形式层 router 只负责在 video 形式内部选择 method（dsl / html_record），
不涉及平台路由（平台适配由 workflow 层负责）。
"""
import os
import sys
import unittest

VIDEO_SCRIPTS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
)
sys.path.insert(0, VIDEO_SCRIPTS)

from router import select_method, select_pipeline, explain_decision  # noqa: E402


class TestRouter(unittest.TestCase):
    def test_prefer_dsl(self):
        d = select_method({}, {'preferDsl': True})
        self.assertEqual(d['method'], 'dsl')
        self.assertNotIn('platform', d)  # 形式层不含平台字段

    def test_html_record(self):
        d = select_method({'hasStructuredHtml': True, 'visualComplexity': 'low', 'durationSeconds': 30})
        self.assertEqual(d['method'], 'html_record')

    def test_high_complexity_goes_dsl(self):
        d = select_method({'visualComplexity': 'high'})
        self.assertEqual(d['method'], 'dsl')

    def test_animation_goes_dsl(self):
        d = select_method({'hasAnimationRequirements': True})
        self.assertEqual(d['method'], 'dsl')

    def test_media_sync_goes_dsl(self):
        d = select_method({'hasMediaSync': True})
        self.assertEqual(d['method'], 'dsl')

    def test_default_goes_dsl(self):
        d = select_method({})
        self.assertEqual(d['method'], 'dsl')
        self.assertEqual(d['fallback'], 'html_record')

    def test_explain_non_empty(self):
        d = select_method({'visualComplexity': 'high'})
        self.assertTrue(len(explain_decision(d)) > 0)
        # 形式层 explain 不应包含平台名
        for platform in ('video-channel', 'bilibili', 'wechat', 'douyin'):
            self.assertNotIn(platform, explain_decision(d))

    def test_decision_has_required_fields(self):
        d = select_method({})
        for field in ('method', 'reason', 'confidence', 'fallback'):
            self.assertIn(field, d)

    # 向后兼容
    def test_legacy_select_pipeline(self):
        d = select_pipeline({'hasAnimationRequirements': True})
        self.assertEqual(d['method'], 'dsl')


if __name__ == '__main__':
    unittest.main()
