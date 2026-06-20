"""
测试 TTS 音频生成。
"""
import asyncio
import os
import subprocess
import sys
import unittest

VIDEO_DSL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, VIDEO_DSL)
from scripts.generate_audio import generate_audio
SPEC = os.path.join(VIDEO_DSL, 'examples', 'negative-numbers', 'spec.json')


class TestAudio(unittest.TestCase):
    def test_generate_audio(self):
        output_dir = os.path.join(VIDEO_DSL, 'output', 'test-audio')
        audio_path = asyncio.run(generate_audio(SPEC, output_dir))
        self.assertTrue(os.path.exists(audio_path))
        self.assertGreater(os.path.getsize(audio_path), 0)
        # Verify duration ~ 9s
        ffmpeg = self._find_ffmpeg()
        result = subprocess.run([ffmpeg, '-i', audio_path], capture_output=True, text=True)
        self.assertRegex(result.stderr, r'Duration: 00:00:09\.\d{2}')

    def _find_ffmpeg(self):
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            return 'ffmpeg'


if __name__ == '__main__':
    unittest.main()
