"""
测试 video-generator 的 validator 与 prompt 构建逻辑。
通过 Node.js 调用编译后的 @essence/video-generator dist。
"""
import json
import os
import subprocess
import sys
import unittest

VIDEO_DSL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_node(code: str):
    cmd = ['node', '-e', code]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=VIDEO_DSL)


class TestValidator(unittest.TestCase):
    def _validate(self, code: str, spec: dict):
        spec_json = json.dumps(spec)
        js = f"""
        import {{ validateVideoProgram, buildPrompt }} from './packages/video-generator/dist/index.js';
        const spec = {spec_json};
        const report = validateVideoProgram({json.dumps(code)}, spec);
        console.log(JSON.stringify(report));
        """
        result = run_node(js)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout.strip().splitlines()[-1])

    def test_valid_code_passes(self):
        code = """
import { Composition, useCurrentFrame, interpolate } from '@essence/video-core';
export const VideoProgram = () => <Composition id="T" component={() => null} width={1080} height={1920} fps={30} durationInFrames={90} />;
"""
        report = self._validate(code, {'title': 'T', 'aspectRatio': '9:16', 'durationSeconds': 3, 'fps': 30, 'sections': [{'type': 'title', 'durationFrames': 90}]})
        self.assertTrue(report['valid'])

    def test_missing_composition_fails(self):
        code = "export const VideoProgram = () => <div>hi</div>;"
        report = self._validate(code, {'title': 'T', 'aspectRatio': '9:16', 'durationSeconds': 3, 'fps': 30, 'sections': []})
        self.assertFalse(report['valid'])
        self.assertIn('缺少', '\n'.join(report['errors']))

    def test_css_animation_fails(self):
        code = """
import { Composition } from '@essence/video-core';
export const VideoProgram = () => <Composition id="T" component={() => <div style={{animation:'fade 1s'}} />} width={1080} height={1920} fps={30} durationInFrames={90} />;
"""
        report = self._validate(code, {'title': 'T', 'aspectRatio': '9:16', 'durationSeconds': 3, 'fps': 30, 'sections': []})
        self.assertFalse(report['valid'])


class TestPrompt(unittest.TestCase):
    def test_prompt_includes_dimensions(self):
        spec = {'title': 'T', 'aspectRatio': '9:16', 'durationSeconds': 3, 'fps': 30, 'sections': []}
        js = f"""
        import {{ buildPrompt }} from './packages/video-generator/dist/index.js';
        console.log(buildPrompt({json.dumps(spec)}));
        """
        result = run_node(js)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('1080', result.stdout)
        self.assertIn('1920', result.stdout)


if __name__ == '__main__':
    unittest.main()
