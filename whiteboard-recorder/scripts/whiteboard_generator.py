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
CONTENT_OUTPUT_SCRIPTS = SKILL_DIR.parent / "content-output" / "scripts"
sys.path.insert(0, str(CONTENT_OUTPUT_SCRIPTS))

ELEMENT_SPEC_PATH = SKILL_DIR / "references" / "excalidraw-element-spec.md"
PROMPT_GUIDE_PATH = SKILL_DIR / "references" / "ai-prompt-guide.md"

def load_system_prompt():
    """加载系统Prompt，拼接元素规范"""
    base_prompt = """你是一位世界级的白板讲解大师，擅长用手绘Excalidraw白板把复杂知识讲得通俗易懂。

## 任务
根据用户提供的内容，完成以下工作：
1. 深度理解内容逻辑，自主拆分讲解场景（每页1-3分钟讲解量）
2. 把所有场景按横向排列在同一个无限大画布上，每页占1920px宽度，相邻场景之间留300px空白间距
3. 为每个场景手绘最适合表达内容逻辑的Excalidraw图解
4. 给出每个场景的镜头中心坐标，方便讲解时镜头自动跟随
5. 为每个场景写出自然口语化的提词器讲解脚本

## 核心原则
- 不要使用固定模板！怎么清楚怎么画，根据内容自由选择图解形式
- 不要列大段文字要点，要画图：流程画箭头、对比画两栏、包含画嵌套、层级画树状、因果画链路
- 多使用视觉隐喻：如果一个比喻能让观众秒懂，就直接画出来
- 手绘风格：元素不需要完全对齐，稍微有点歪更自然，roughness=1
- 每页有一个视觉焦点，重点内容放大、用强调色
- 留白充足，不要把页面塞太满

## 色板
描边色优先用 "#1e1e1e" 黑色，重点强调用红色 "#e03131"、绿色 "#2f9e44"、蓝色 "#1971c2"、橙色 "#f08c00"
填充色用对应浅色，fillStyle用"hachure"（手绘阴影）默认

## 坐标计算规则（横向排列）
第N页（scene_index=N）的视口中心坐标计算：
- viewport_x = 960 + N * (1920 + 300)
- viewport_y = 540
- viewport_zoom = 1
- 该页所有元素的x坐标需要加上全局偏移量 N * (1920 + 300)，确保每页内容不重叠

## 元素要求
- 每页顶部居中放场景标题，字号36，黑色加粗感觉（用大字号即可）
- 文本不要太长，用关键词，字号正文20，标题28/36
- 字体用fontFamily=1（手写字体Virgil）
- 箭头必须绑定到形状元素，使用startBinding/endBinding，gap=5
- 每个元素必须有id、seed、version等必填字段
- 如果文本要放在形状内部，设置containerId为形状id即可自动居中

## 提词器脚本要求
- 完全口语化，像对着观众面对面说话一样
- 不要书面语，不要念稿子
- 每页对应1-3分钟（约200-600字）
- 先点出这页讲什么，再逐个解释图上的元素
- 多用自然过渡语

## 输出格式
严格输出JSON，不要任何其他解释文字，不要markdown代码块包裹，直接输出JSON：
{
  "title": "内容标题",
  "canvas_layout": "horizontal",
  "total_scenes": 0,
  "scenes": [
    {
      "scene_index": 0,
      "scene_title": "场景标题",
      "viewport_x": 960,
      "viewport_y": 540,
      "viewport_zoom": 1,
      "duration_estimate": 60,
      "teleprompter_script": "讲解文本...",
      "elements": []
    }
  ]
}
"""
    return base_prompt


def fetch_content(source: str) -> dict:
    """获取内容：支持本地md文件路径、公众号URL、纯文本"""
    if source.startswith("http://") or source.startswith("https://"):
        from shared.article_fetcher import fetch_article_by_url
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


def validate_elements(elements: list, scene_index: int) -> list:
    """验证并修复Excalidraw元素，保证能正常加载"""
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
                el["fontFamily"] = 1
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
        "files": {}
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(excalidraw_file, f, ensure_ascii=False, indent=2)
    print(f"[Generator] Excalidraw文件已保存: {output_path}")


def export_whiteboard_project(result: dict, output_path: str):
    """导出为WhiteboardCaster项目格式（含场景和提词器）"""
    project = {
        "version": "1.0",
        "title": result.get("title", "未命名白板"),
        "canvas_layout": result.get("canvas_layout", "horizontal"),
        "total_scenes": result.get("total_scenes", 0),
        "scenes": []
    }
    
    for scene in result["scenes"]:
        project["scenes"].append({
            "index": scene["scene_index"],
            "title": scene["scene_title"],
            "viewport": {
                "x": scene["viewport_x"],
                "y": scene["viewport_y"],
                "zoom": scene["viewport_zoom"]
            },
            "duration_estimate": scene.get("duration_estimate", 60),
            "teleprompter_script": scene["teleprompter_script"],
            "elements": scene["elements"]
        })
    
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
        f.write(f"# {title} - 提词器脚本\n\n")
        for i, scene in enumerate(result["scenes"]):
            f.write(f"## 第{i+1}页：{scene['scene_title']}\n\n")
            f.write(f"预计时长：{scene.get('duration_estimate', 60)}秒\n\n")
            f.write(scene["teleprompter_script"])
            f.write("\n\n---\n\n")
    print(f"[Generator] 提词器脚本已保存: {script_path}")
    
    print(f"\n[Generator] ✅ 生成完成！")
    print(f"   请在WhiteboardCaster中导入项目文件: {project_path}")


if __name__ == "__main__":
    main()
