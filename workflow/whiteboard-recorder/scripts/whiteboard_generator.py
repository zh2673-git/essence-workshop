"""
本质工坊 · 白板录制 AI生成器
输入：Markdown文件 / 公众号URL / 纯文本
输出：无限画布Excalidraw JSON + 提词器脚本，可直接导入WhiteboardCaster
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent

# v3.0 职责分层：Prompt组件来自format，方法论来自cognitive，本文件只负责执行
PROMPT_GUIDE_PATH = PROJECT_ROOT / "format" / "whiteboard" / "references" / "ai-prompt-guide.md"
METHODOLOGY_PATH = PROJECT_ROOT / "cognitive" / "general-logic" / "references" / "methodology.md"
ELEMENT_SPEC_PATH = SKILL_DIR / "references" / "excalidraw-element-spec.md"

def load_system_prompt():
    """加载系统Prompt：拼接白板格式Prompt（format）和认知方法论（cognitive）。
    本函数不重定义任何方法论或Prompt设计，仅做读取和拼接。"""
    with open(PROMPT_GUIDE_PATH, "r", encoding="utf-8") as f:
        prompt_guide = f.read()
    with open(METHODOLOGY_PATH, "r", encoding="utf-8") as f:
        methodology = f.read()
    return f"{prompt_guide}\n\n---\n\n## 方法论详细内容（引用自cognitive）\n\n{methodology}"


def fetch_content(source: str) -> dict:
    """获取内容：支持本地md文件路径、公众号URL、纯文本"""
    if source.startswith("http://") or source.startswith("https://"):
        sys.path.insert(0, str(PROJECT_ROOT / "workflow" / "wechat" / "scripts"))
        from article_fetcher import fetch_article_by_url
        print(f"[Generator] 正在抓取文章: {source}")
        return fetch_article_by_url(source)
    elif os.path.isfile(source):
        print(f"[Generator] 正在读取本地文件: {source}")
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else Path(source).stem
        return {"title": title, "content_markdown": content}
    else:
        lines = source.strip().split("\n")
        title = lines[0].lstrip("# ").strip() if lines else "未命名内容"
        return {"title": title, "content_markdown": source}


def bind_text_to_containers(elements: list) -> list:
    """安全绑定：仅将位于形状内部且尚未绑定的第一个文本绑定到该容器。
    Excalidraw 每个容器只能绑定一个文本；多文本绑定同一个容器会导致全部无法渲染。
    绑定条件：文本中心点位于 rectangle/ellipse/diamond 范围内。
    """
    shapes = [el for el in elements if el.get("type") in ("rectangle", "ellipse", "diamond")]
    texts = [el for el in elements if el.get("type") == "text"]
    already_bound = set()
    for text in texts:
        if text.get("containerId"):
            already_bound.add(text["containerId"])
            continue
        tx = text.get("x", 0) + text.get("width", 0) / 2
        ty = text.get("y", 0) + text.get("height", 0) / 2
        for shape in shapes:
            if shape["id"] in already_bound:
                continue
            sx, sy = shape.get("x", 0), shape.get("y", 0)
            sw, sh = shape.get("width", 0), shape.get("height", 0)
            if sx <= tx <= sx + sw and sy <= ty <= sy + sh:
                text["containerId"] = shape["id"]
                shape.setdefault("boundElements", []).append({
                    "id": text["id"],
                    "type": "text"
                })
                already_bound.add(shape["id"])
                break
    return elements


def validate_elements(elements: list, scene_index: int) -> list:
    """验证并修复Excalidraw元素，保证能正常加载"""
    # 先绑定文本到容器，再偏移，避免文字被形状填充遮挡
    elements = bind_text_to_containers(elements)
    offset_x = scene_index * (1920 + 300)
    validated = []
    for i, el in enumerate(elements):
        if "id" not in el:
            el["id"] = f"el_{scene_index}_{i}"
        if "seed" not in el:
            import random
            el["seed"] = random.randint(1, 1000000)
        if "version" not in el:
            el["version"] = 1
        if "versionNonce" not in el:
            el["versionNonce"] = random.randint(1, 1000000)
        if "isDeleted" not in el:
            el["isDeleted"] = False
        if "boundElements" not in el:
            el["boundElements"] = []
        if "updated" not in el:
            el["updated"] = 1
        if "link" not in el:
            el["link"] = None
        if "locked" not in el:
            el["locked"] = False
        if "opacity" not in el:
            el["opacity"] = 100
        if "roughness" not in el:
            el["roughness"] = 1
        if "strokeWidth" not in el:
            el["strokeWidth"] = 2
        if "strokeStyle" not in el:
            el["strokeStyle"] = "solid"
        if "fillStyle" not in el:
            el["fillStyle"] = "hachure"
        if "strokeColor" not in el:
            el["strokeColor"] = "#1e1e1e"
        if "backgroundColor" not in el:
            el["backgroundColor"] = "transparent"
        if "angle" not in el:
            el["angle"] = 0
        if "groupIds" not in el:
            el["groupIds"] = []
        
        el["x"] = el.get("x", 0) + offset_x
        
        if el["type"] == "text":
            if "fontSize" not in el:
                el["fontSize"] = 20
            if "fontFamily" not in el:
                el["fontFamily"] = 2  # v2: fontFamily=1(Virgil)导致中文渲染不稳定，强制用2(印刷体)
            if "textAlign" not in el:
                el["textAlign"] = "left"
            if "verticalAlign" not in el:
                el["verticalAlign"] = "top"
            if "containerId" not in el:
                el["containerId"] = None
            if "originalText" not in el:
                el["originalText"] = el.get("text", "")
            if "autoResize" not in el:
                el["autoResize"] = True
            if "lineHeight" not in el:
                el["lineHeight"] = 1.25
            if "width" not in el or el["width"] < 20:
                el["width"] = max(20, len(el.get("text", "")) * el.get("fontSize", 20) * 0.6)
            if "height" not in el or el["height"] < 20:
                el["height"] = el.get("fontSize", 20) * 1.5
        
        if el["type"] in ["arrow", "line"]:
            if "points" not in el or len(el["points"]) < 2:
                continue
            if "startArrowhead" not in el:
                el["startArrowhead"] = None
            if "endArrowhead" not in el:
                el["endArrowhead"] = "arrow" if el["type"] == "arrow" else None
            if "startBinding" not in el:
                el["startBinding"] = None
            if "endBinding" not in el:
                el["endBinding"] = None
        
        validated.append(el)
    return validated


def generate_with_ai(content: str, title: str, api_key: str = None, model: str = "doubao-4", api_base: str = None):
    """调用LLM生成白板内容"""
    try:
        from openai import OpenAI
    except ImportError:
        print("[Generator] 正在安装openai依赖...")
        os.system(f"{sys.executable} -m pip install openai --quiet")
        from openai import OpenAI
    
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DOUBAO_API_KEY")
    if not api_key:
        raise ValueError("请设置OPENAI_API_KEY或DOUBAO_API_KEY环境变量，或通过--api-key传入")
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base or os.environ.get("OPENAI_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
    )
    
    system_prompt = load_system_prompt()
    user_prompt = f"标题：{title}\n\n内容：\n{content}"
    
    print(f"[Generator] 正在调用AI生成白板内容（model={model}）...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content.strip()
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as e:
        print(f"[Generator] JSON解析错误，尝试修复: {e}")
        json_match = re.search(r"\{[\s\S]*\}", result_text)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            raise ValueError(f"AI输出不是合法JSON: {result_text[:200]}")
    
    for scene in result.get("scenes", []):
        scene_idx = scene.get("scene_index", 0)
        expected_x = 960 + scene_idx * (1920 + 300)
        scene["viewport_x"] = expected_x
        scene["viewport_y"] = scene.get("viewport_y", 540)
        scene["viewport_zoom"] = scene.get("viewport_zoom", 1)
        scene["elements"] = validate_elements(scene.get("elements", []), scene_idx)
    
    result["total_scenes"] = len(result.get("scenes", []))
    result["canvas_layout"] = result.get("canvas_layout", "horizontal")
    result["methodology_version"] = result.get("methodology_version", "v2.1")
    result["files"] = result.get("files", {})
    return result


def export_excalidraw_file(result: dict, output_path: str):
    """导出为Excalidraw可直接打开的文件格式"""
    all_elements = []
    for scene in result["scenes"]:
        all_elements.extend(scene["elements"])

    excalidraw_file = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": all_elements,
        "appState": {
            "viewBackgroundColor": "#ffffff",
            "gridSize": None
        },
        "files": result.get("files", {})
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(excalidraw_file, f, ensure_ascii=False, indent=2)
    print(f"[Generator] Excalidraw文件已保存: {output_path}")


def export_whiteboard_project(result: dict, output_path: str):
    """导出为WhiteboardCaster项目格式（含场景和提词器，含可选方法论元数据）"""
    project = {
        "version": "2.1",
        "methodology_version": result.get("methodology_version", "v2.1"),
        "title": result.get("title", "未命名白板"),
        "canvas_layout": result.get("canvas_layout", "horizontal"),
        "total_scenes": result.get("total_scenes", 0),
        "scenes": []
    }

    for scene in result["scenes"]:
        scene_obj = {
            "index": scene["scene_index"],
            "title": scene["scene_title"],
            "viewport": {
                "x": scene["viewport_x"],
                "y": scene["viewport_y"],
                "zoom": scene["viewport_zoom"]
            },
            "duration_estimate": scene.get("duration_estimate", 60),
            "epiphany_trigger": scene.get("epiphany_trigger", ""),
            "teleprompter_script": scene["teleprompter_script"],
            "elements": scene["elements"]
        }
        # 可选元数据字段（不强制每页都有）
        if "scene_phase" in scene:
            scene_obj["scene_phase"] = scene["scene_phase"]
        if "essence_definition" in scene:
            scene_obj["essence_definition"] = scene["essence_definition"]
        if "essence_check" in scene:
            scene_obj["essence_check"] = scene["essence_check"]
        if "causal_chain" in scene:
            scene_obj["causal_chain"] = scene["causal_chain"]
        if "counterintuitive_root" in scene:
            scene_obj["counterintuitive_root"] = scene["counterintuitive_root"]
        if "structural_metaphor" in scene:
            scene_obj["structural_metaphor"] = scene["structural_metaphor"]
        if "perspective_upgrade" in scene:
            scene_obj["perspective_upgrade"] = scene["perspective_upgrade"]
        project["scenes"].append(scene_obj)

    # v2: files 字段（image元素对应的base64数据，由 svg_to_whiteboard.py 合并）
    project["files"] = result.get("files", {})

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    print(f"[Generator] WhiteboardCaster项目已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · AI白板内容生成器")
    parser.add_argument("source", help="输入源：本地Markdown文件路径 / 公众号URL / 纯文本")
    parser.add_argument("--output", "-o", default=None, help="输出目录（默认：whiteboard-recorder/output/<作品名>/）")
    parser.add_argument("--title", "-t", default=None, help="自定义标题（可选）")
    parser.add_argument("--api-key", default=None, help="LLM API Key")
    parser.add_argument("--model", default="ep-20241203203426-7hr9v", help="模型名称")
    parser.add_argument("--api-base", default=None, help="API Base URL")
    
    args = parser.parse_args()
    
    content_data = fetch_content(args.source)
    title = args.title or content_data["title"]
    content = content_data["content_markdown"]
    
    print(f"[Generator] 标题: {title}")
    print(f"[Generator] 内容长度: {len(content)} 字符")
    
    result = generate_with_ai(content, title, args.api_key, args.model, args.api_base)
    
    base_name = re.sub(r'[^\w\u4e00-\u9fff]+', '_', title)[:50]
    skill_dir = Path(__file__).resolve().parent.parent
    output_dir = args.output or os.path.join(skill_dir, "output", base_name)
    os.makedirs(output_dir, exist_ok=True)
    
    excalidraw_path = os.path.join(output_dir, f"{base_name}.excalidraw")
    project_path = os.path.join(output_dir, f"{base_name}.whiteboard.json")
    script_path = os.path.join(output_dir, f"{base_name}-提词器.md")
    
    export_excalidraw_file(result, excalidraw_path)
    export_whiteboard_project(result, project_path)
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(f"# {title} - 提词器脚本（方法论，思考层/输出层分离）\n\n")
        for i, scene in enumerate(result["scenes"]):
            f.write(f"## 第{i+1}页：{scene['scene_title']}\n\n")
            # scene_phase 为可选元数据，存在时才显示阶段标签
            phase = scene.get("scene_phase")
            if phase:
                phase_label = {
                    "stage1_what": "阶段1·是什么",
                    "stage2_why": "阶段2·为什么",
                    "stage3_how": "阶段3·怎么做"
                }.get(phase, phase)
                f.write(f"**阶段**：{phase_label}（可选标注）\n\n")
            if scene.get("epiphany_trigger"):
                f.write(f"**顿悟触发点**：{scene['epiphany_trigger']}\n\n")
            # 以下为可选元数据，存在时才显示
            if scene.get("essence_definition"):
                f.write(f"**本质定义**：{scene['essence_definition']}\n\n")
            if scene.get("counterintuitive_root"):
                f.write(f"**反常识根因**：{scene['counterintuitive_root']}\n\n")
            if scene.get("perspective_upgrade"):
                f.write(f"**视角升级**：{scene['perspective_upgrade']}\n\n")
            f.write(f"预计时长：{scene.get('duration_estimate', 60)}秒\n\n")
            f.write(scene["teleprompter_script"])
            f.write("\n\n---\n\n")
    print(f"[Generator] 提词器脚本已保存: {script_path}")
    
    print(f"\n[Generator] ✅ 生成完成！")
    print(f"   请在WhiteboardCaster中导入项目文件: {project_path}")


if __name__ == "__main__":
    main()
