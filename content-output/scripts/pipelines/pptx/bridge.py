"""
本质工坊 · PPT管线 Python→Node.js 桥接
调用 html2pptx.js 将 HTML 幻灯片转换为精确的 PPTX 文件

用法（内部调用）:
  from scripts.pipelines.pptx.bridge import html_to_pptx
  html_to_pptx("output/html/index.html", "output/pptx/presentation.pptx")
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML2PPTX_JS = os.path.join(SCRIPT_DIR, "html2pptx.js")


def html_to_pptx(html_path, output_path, layout="LAYOUT_16x9"):
    if not os.path.isfile(HTML2PPTX_JS):
        print(f"ERROR: html2pptx.js not found: {HTML2PPTX_JS}")
        return False

    if not os.path.isfile(html_path):
        print(f"ERROR: HTML file not found: {html_path}")
        return False

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    cmd = ["node", HTML2PPTX_JS, html_path, output_path, "--layout", layout]
    print(f"  [bridge] Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"  [html2pptx] {line}")

        if result.returncode != 0:
            print(f"ERROR: html2pptx.js failed with exit code {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split("\n"):
                    print(f"  [html2pptx:err] {line}")
            return False

        return os.path.isfile(output_path)

    except FileNotFoundError:
        print("ERROR: Node.js not found. Install Node.js to use --mode precise")
        print("  Download: https://nodejs.org/")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: html2pptx.js timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"ERROR: html2pptx.js failed: {e}")
        return False
