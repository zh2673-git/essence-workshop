"""
本质工坊 · 白板录制项目生成器
输入：预生成的白板内容 JSON（由 format 生成，含场景和元素）
输出：whiteboard-recorder 项目文件（.whiteboard.json / .excalidraw / 提词器.md）

平台适配职责：
- 应用白板场景坐标布局（横向排列，视口偏移）
- 校验 Excalidraw 元素
- 导出平台特定格式（.whiteboard.json / .excalidraw / 提词器.md）

注意：白板元素内容由 format 生成，本脚本不做 LLM 内容生成。
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from whiteboard_generator import (
    validate_elements,
    export_excalidraw_file,
    export_whiteboard_project,
)


def parse_broadcast_script(file_path: str) -> dict:
    """解析口播稿 Markdown，提取标题、场景列表、旁白、白板提示。"""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # frontmatter
    frontmatter = {}
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip().strip('"')
        text = text[fm_match.end():]

    # 标题
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = frontmatter.get("title") or (title_match.group(1).strip() if title_match else Path(file_path).stem)

    # 按 ## 镜头 XX 拆分
    scene_blocks = re.split(r"\n(?=##\s+镜头\s+\d+)", text)
    scenes = []
    for block in scene_blocks:
        block = block.strip()
        if not block.startswith("## 镜头"):
            continue

        header_match = re.match(r"##\s+镜头\s+(\d+).*[|｜]\s*(.+?)(?:（|\()", block)
        if not header_match:
            header_match = re.match(r"##\s+镜头\s+(\d+).*?(.+?)$", block, re.MULTILINE)

        scene_index = int(header_match.group(1)) if header_match else len(scenes)
        scene_title = header_match.group(2).strip() if header_match else f"场景 {scene_index}"

        # 时长
        duration_match = re.search(r"[\-\*]\s*时长[：:]\s*(.+)", block)
        duration_str = duration_match.group(1).strip() if duration_match else "60s"
        duration = int(re.search(r"\d+", duration_str).group()) if re.search(r"\d+", duration_str) else 60

        # 白板提示
        wb_match = re.search(r"[\-\*]\s*白板[：:]\s*(.+?)(?=\n[\-\*]|\n###|\n##|$)", block, re.DOTALL)
        whiteboard_hint = wb_match.group(1).strip() if wb_match else ""

        # 旁白
        nar_match = re.search(r"[\-\*]\s*旁白[：:]\s*(.*?)(?=\n[\-\*]|\n###|\n##|$)", block, re.DOTALL)
        narration = ""
        if nar_match:
            narration_lines = []
            for line in nar_match.group(1).strip().split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    line = line.lstrip("-*").strip()
                if line:
                    narration_lines.append(line)
            narration = "\n".join(narration_lines)

        scenes.append({
            "scene_index": scene_index,
            "scene_title": scene_title,
            "duration": duration,
            "whiteboard_hint": whiteboard_hint,
            "narration": narration,
        })

    # 按镜头编号排序
    scenes.sort(key=lambda s: s["scene_index"])
    # 重新连续编号
    for i, s in enumerate(scenes):
        s["scene_index"] = i

    return {
        "title": title,
        "target_duration": frontmatter.get("target_duration", ""),
        "audience": frontmatter.get("audience", ""),
        "sensitive_mode": frontmatter.get("sensitive_mode", "false").lower() == "true",
        "scenes": scenes,
    }


def apply_scene_layout(result: dict) -> dict:
    """为白板场景应用平台特定的坐标偏移和元素校验。

    场景按横向排列，每个场景间隔 1920+300 像素。
    """
    for scene in result.get("scenes", []):
        scene_idx = scene.get("scene_index", 0)
        scene["viewport_x"] = 960 + scene_idx * (1920 + 300)
        scene["viewport_y"] = scene.get("viewport_y", 540)
        scene["viewport_zoom"] = scene.get("viewport_zoom", 1)
        scene["elements"] = validate_elements(scene.get("elements", []), scene_idx)

    result["total_scenes"] = len(result.get("scenes", []))
    result["canvas_layout"] = "horizontal"
    return result


def export_teleprompter(result: dict, output_path: str):
    """导出提词器 Markdown。"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {result.get('title', '未命名白板')} - 提词器\n\n")
        for scene in result.get("scenes", []):
            f.write(f"## 第{scene['scene_index'] + 1}页：{scene['scene_title']}\n\n")
            f.write(f"预计时长：{scene.get('duration_estimate', 60)} 秒\n\n")
            f.write(scene.get("teleprompter_script", ""))
            f.write("\n\n---\n\n")
    print(f"[BroadcastBridge] 提词器已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 白板录制项目生成器")
    parser.add_argument("whiteboard_json", help="预生成的白板内容 JSON 文件（由 format 生成，含场景和元素）")
    parser.add_argument("--script", default=None, help="口播稿 Markdown 文件路径（可选，用于提取标题）")
    parser.add_argument("--output", "-o", default=None, help="输出目录（默认：whiteboard-recorder/output/<作品名>/）")
    parser.add_argument("--title", "-t", default=None, help="自定义标题（可选）")

    args = parser.parse_args()

    # 加载预生成的白板内容
    with open(args.whiteboard_json, "r", encoding="utf-8") as f:
        result = json.load(f)

    # 从口播稿提取标题（可选）
    title = args.title or result.get("title")
    if args.script:
        script_data = parse_broadcast_script(args.script)
        title = title or script_data["title"]
    if not title:
        title = Path(args.whiteboard_json).stem
    result["title"] = title

    # 应用平台特定的场景布局
    result = apply_scene_layout(result)

    print(f"[BroadcastBridge] 标题: {title}")
    print(f"[BroadcastBridge] 场景数: {len(result['scenes'])}")

    base_name = re.sub(r"[^\w\u4e00-\u9fff]+", "_", title)[:50]
    output_dir = Path(args.output) if args.output else SKILL_DIR / "output" / base_name
    output_dir.mkdir(parents=True, exist_ok=True)

    excalidraw_path = output_dir / f"{base_name}.excalidraw"
    project_path = output_dir / f"{base_name}.whiteboard.json"
    teleprompter_path = output_dir / f"{base_name}-提词器.md"

    export_excalidraw_file(result, str(excalidraw_path))
    export_whiteboard_project(result, str(project_path))
    export_teleprompter(result, str(teleprompter_path))

    print(f"\n[BroadcastBridge] 生成完成！")
    print(f"   WhiteboardCaster 项目: {project_path}")
    print(f"   可直接在 WhiteboardCaster 中导入并录制。")


if __name__ == "__main__":
    main()
