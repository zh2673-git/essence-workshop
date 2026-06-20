"""
测试 DSL 渲染器能输出有效 MP4/GIF。
"""
import os
import subprocess
import unittest

VIDEO_DSL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(VIDEO_DSL, 'examples', 'negative-numbers', 'VideoProgram.tsx')
AUDIO = os.path.join(VIDEO_DSL, 'output', 'negative-numbers-audio', 'audio.m4a')
CLI = os.path.join(VIDEO_DSL, 'packages', 'video-renderer', 'dist', 'cli.js')


class TestRender(unittest.TestCase):
    def test_render_mp4(self):
        output_dir = os.path.join(VIDEO_DSL, 'output', 'test-negative-numbers')
        cmd = [
            'node', CLI, EXAMPLE,
            '--output', output_dir,
            '--fps', '30',
            '--width', '1080',
            '--height', '1920',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=VIDEO_DSL)
        self.assertEqual(result.returncode, 0, result.stderr)
        video_path = os.path.join(output_dir, 'final.mp4')
        self.assertTrue(os.path.exists(video_path))
        self.assertGreater(os.path.getsize(video_path), 0)

    def test_render_mp4_with_audio(self):
        if not os.path.exists(AUDIO):
            self.skipTest('音频文件未生成')
        output_dir = os.path.join(VIDEO_DSL, 'output', 'test-with-audio')
        cmd = [
            'node', CLI, EXAMPLE,
            '--output', output_dir,
            '--fps', '30',
            '--width', '1080',
            '--height', '1920',
            '--audio', AUDIO,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=VIDEO_DSL)
        self.assertEqual(result.returncode, 0, result.stderr)
        video_path = os.path.join(output_dir, 'final.mp4')
        self.assertTrue(os.path.exists(video_path))

    def test_render_gif(self):
        output_dir = os.path.join(VIDEO_DSL, 'output', 'test-gif')
        cmd = [
            'node', CLI, EXAMPLE,
            '--output', output_dir,
            '--fps', '10',
            '--width', '540',
            '--height', '960',
            '--format', 'gif',
            '--quality', 'draft',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=VIDEO_DSL)
        self.assertEqual(result.returncode, 0, result.stderr)
        gif_path = os.path.join(output_dir, 'final.gif')
        self.assertTrue(os.path.exists(gif_path))
        self.assertGreater(os.path.getsize(gif_path), 0)


if __name__ == '__main__':
    unittest.main()
