"""
本质工坊 · 口播稿 → 白板录制桥接器
输入：content-output 生成的 broadcast-script.md
输出：whiteboard-recorder 项目文件（.whiteboard.json / .excalidraw / 提词器.md）

根据口播稿中每个镜头的「旁白」和「白板提示」，自动生成对应的白板画面元素。
"""
import argparse
import json
import os
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


def build_system_prompt() -> str:
    """为口播稿生成白板内容的专用系统 Prompt。"""
    return """你是一位擅长白板讲解的视觉设计师。

任务：根据用户提供的口播稿镜头列表，为每个镜头生成一组 Excalidraw 手绘元素。

## 输入格式
每个镜头包含：
- scene_title：场景标题
- duration：预计时长（秒）
- whiteboard_hint：白板上要呈现什么内容
- narration：主播要念的旁白

## 输出格式
严格输出 JSON，不要任何其他解释文字，不要 markdown 代码块：
{
  "title": "视频标题",
  "total_scenes": 0,
  "scenes": [
    {
      "scene_index": 0,
      "scene_title": "场景标题",
      "duration_estimate": 60,
      "teleprompter_script": "旁白文本",
      "elements": []
    }
  ]
}

## 元素生成规则
1. 每个场景独立绘制，元素坐标以场景左上角 (0,0) 为原点
2. 每页内容建议控制在 1600×900 范围内
3. 必须包含场景标题文本（顶部居中，fontSize=36）
4. 根据 whiteboard_hint 决定画图方式：
   - 流程/步骤 → 用箭头连接的矩形
   - 对比 → 左右/上下两栏
   - 概念定义 → 中心关键词 + 周围解释
   - 数据 → 大数字 + 简短标签
   - 寓言场景 → 画出寓言中的角色/场景
5. 文字要短，用关键词和短句，不要写长段落
6. 手绘风格：roughness=1，fontFamily=1（Virgil）
7. 色板：
   - 默认描边："#1e1e1e"
   - 重点强调："#e03131" 红 / "#1971c2" 蓝 / "#2f9e44" 绿 / "#f08c00" 橙
   - 浅填充："#ffc9c9" / "#a5d8ff" / "#b2f2bb" / "#ffec99"
8. 每个元素必须包含 id、type、x、y、width、height、seed、version、versionNonce、isDeleted、boundElements、updated、link、locked 等字段
9. 箭头尽量绑定到形状（startBinding/endBinding），不要悬空
10. teleprompter_script 直接使用输入的 narration，可适当精简口语化
"""


def generate_whiteboard_from_broadcast(
    script_data: dict,
    api_key: str = None,
    model: str = "doubao-4",
    api_base: str = None,
):
    """调用 LLM，为口播稿每个镜头生成白板元素。"""
    try:
        from openai import OpenAI
    except ImportError:
        print("[BroadcastBridge] 正在安装 openai 依赖...")
        os.system(f"{sys.executable} -m pip install openai --quiet")
        from openai import OpenAI

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DOUBAO_API_KEY")
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 或 DOUBAO_API_KEY 环境变量，或通过 --api-key 传入")

    client = OpenAI(
        api_key=api_key,
        base_url=api_base or os.environ.get("OPENAI_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
    )

    system_prompt = build_system_prompt()
    user_prompt = json.dumps(script_data, ensure_ascii=False, indent=2)

    print(f"[BroadcastBridge] 正在调用 AI 生成白板内容（model={model}）...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    result_text = response.choices[0].message.content.strip()
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as e:
        print(f"[BroadcastBridge] JSON 解析错误，尝试修复: {e}")
        json_match = re.search(r"\{[\s\S]*\}", result_text)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            raise ValueError(f"AI 输出不是合法 JSON: {result_text[:200]}")

    # 校验元素并添加场景偏移
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
    parser = argparse.ArgumentParser(description="本质工坊 · 口播稿转白板录制项目")
    parser.add_argument("script", help="口播稿 Markdown 文件路径（broadcast-script.md）")
    parser.add_argument("--output", "-o", default=None, help="输出目录（默认：whiteboard-recorder/output/<作品名>/）")
    parser.add_argument("--title", "-t", default=None, help="自定义标题（可选）")
    parser.add_argument("--api-key", default=None, help="LLM API Key")
    parser.add_argument("--model", default="ep-20241203203426-7hr9v", help="模型名称")
    parser.add_argument("--api-base", default=None, help="API Base URL")

    args = parser.parse_args()

    script_data = parse_broadcast_script(args.script)
    title = args.title or script_data["title"]
    script_data["title"] = title

    print(f"[BroadcastBridge] 标题: {title}")
    print(f"[BroadcastBridge] 解析到 {len(script_data['scenes'])} 个镜头")

    result = generate_whiteboard_from_broadcast(script_data, args.api_key, args.model, args.api_base)

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
