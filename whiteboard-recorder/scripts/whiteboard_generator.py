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
    """加载系统Prompt，拼接元素规范（v2.1方法论版本，思考层/输出层分离）"""
    base_prompt = """你是一位世界级的白板讲解大师，擅长用手绘Excalidraw白板把复杂知识讲得通俗易懂。

## v2.1 方法论锚点（思考层 vs 输出层分离）

你生成的白板内容必须遵循本质工坊 v2.1 方法论（含第九章思考层 vs 输出层分离原则）：

### 思考层（智能体生成内容前内部必走）

1. **三阶合一思考路径**：思考时走"阶段1（是什么·点出本质）→ 阶段2（为什么·建立因果）→ 阶段3（怎么做·展开方法·视角升级）"——这是智能体内部推理路径，**不要求白板按此分页**
2. **本质定义先行**（思考层）：每个主题先用本质定义揭底，禁止用描述性定义
   - ❌ 禁止："区块链是按时间顺序链接的区块组成的分布式账本"（属加种差，描述外延）
   - ✅ 必须："区块链是用算力代价换取无需信任第三方的机制"（揭示本质属性）
   - 必须通过本质检验：本质定义能否解释所有其他属性？不能就降级重写（思考校验，不强制在白板露出）
3. **顿悟触发器规划**（思考层规划三件套）：一句话点破 + 反常识根因 + 视角升级

### 输出层（白板按视觉节奏组织，不强绑三阶分页）

**白板分页方式按视觉节奏自由组织**，不强制按"阶段1/阶段2/阶段3"机械拆分：
- 一个三阶可以拆成3-5页（每页一个视觉焦点+一个核心信息点）
- 也可以一个三阶合成1页（信息密度高时）
- 也可以多页讲一个阶段（复杂概念需要分解时）
- 每页1-3分钟讲解量，按视觉焦点自然分页

**每页必须有"顿悟触发点"作为视觉焦点**（内容要求，非分节要求）：
- 视觉形式：红色标记（strokeColor="#e03131"）+ 问号图标 + 反差对比
- 内容形式：一句话点破最底层逻辑 / 反常识根因 / 视角升级金句（可独立传播）
- 顿悟触发点的类型由该页内容决定，不强制每页都是"一句话点破"

4. **结构性比喻照亮本质**（取代"视觉隐喻"）：
   - ❌ 装饰性比喻：区块链=把区块串成链（只描述外观）
   - ✅ 结构性比喻：区块链=用算力换信任的拍卖场（比喻内部结构与本质同构）
   - 比喻的每个组件必须能映射回本质定义的某个属性

## 任务
根据用户提供的内容，完成以下工作：
1. 深度理解内容逻辑，**思考时走三阶合一**（阶段1是什么/阶段2为什么/阶段3怎么做），但**白板分页按视觉节奏自由组织**（不强制按三阶分页）
2. 把所有场景按横向排列在同一个无限大画布上，每页占1920px宽度，相邻场景之间留300px空白间距
3. 为每个场景手绘最适合表达内容逻辑的Excalidraw图解，**每页有一个顿悟触发点作为视觉焦点**（红色+问号+反差），再展开图解
4. 给出每个场景的镜头中心坐标，方便讲解时镜头自动跟随
5. 为每个场景写出自然口语化的提词器讲解脚本，**整个白板必须包含"反常识根因"和"视角升级收尾"**（不强制每页都有，但整体三件套齐备）

## 核心原则
- 不要使用固定模板！怎么清楚怎么画，根据内容自由选择图解形式
- 不要列大段文字要点，要画图：流程画箭头、对比画两栏、包含画嵌套、层级画树状、因果画链路
- ❌ 不要用描述性定义平铺！思考时必须用本质定义揭底（思考层）
- ✅ 用结构性比喻照亮本质：比喻的内部结构与本质同构，不是装饰性比喻
- ✅ 每页必须有一个顿悟触发点：红色标记（#e03131）+ 问号图标 + 反差对比（视觉焦点）
- ✅ 白板分页按视觉节奏，不强制按"阶段1/阶段2/阶段3"机械拆分
- ✅ 手绘风格：元素不需要完全对齐，稍微有点歪更自然，roughness=1
- 留白充足，不要把页面塞太满

## 顿悟触发点的视觉表达

每个场景必须有一个"顿悟触发点"，视觉上这样表达：
1. **红色描边（#e03131）+ 浅红填充（#ffc9c9）** 的关键框
2. 框内放一句话点破本质的金句（如"区块链的本质是：用算力换信任"）或反常识根因或视角升级金句
3. 在金句旁边画一个**问号图标**（text类型，内容"？"，字号36，红色#e03131）
4. 用**反差对比**强化顿悟：左边画"表面认知"（灰色#adb5bd），右边画"本质揭示"（红色#e03131）

## 色板
描边色优先用 "#1e1e1e" 黑色，顿悟触发点用红色 "#e03131"，正向用绿色 "#2f9e44"、信息用蓝色 "#1971c2"、提示用橙色 "#f08c00"
填充色用对应浅色，fillStyle用"hachure"（手绘阴影）默认

## 坐标计算规则（横向排列，硬约束）
第N页（scene_index=N）的视口中心坐标计算：
- viewport_x = 960 + N * (1920 + 300)
- viewport_y = 540
- viewport_zoom = 1
- 该页所有元素的x坐标需要加上全局偏移量 N * (1920 + 300)，确保每页内容不重叠
- **坐标偏移只算一次**（memory硬约束，避免重复偏移导致元素错位）

## 元素要求
- 每页顶部居中放场景标题（标题由内容决定，不强制"阶段1·是什么"格式），字号36，黑色
- 文本不要太长，用关键词，字号正文20，标题28/36
- 字体用fontFamily=2（印刷体，**硬约束**：fontFamily=1 Virgil会导致中文渲染不稳定）
- 箭头必须绑定到形状元素，使用startBinding/endBinding，gap=5
- 每个元素必须有id、seed、version等必填字段
- 如果文本要放在形状内部，设置containerId为形状id即可自动居中
- **每页先有"顿悟触发点"（红色描边+浅红填充+问号）作为视觉焦点，再展开图解**

## 提词器脚本要求
- 完全口语化，像对着观众面对面说话一样
- 不要书面语，不要念稿子
- 每页对应1-3分钟（约200-600字）
- 整个白板讲解必须包含三件套（不强制每页都对齐三阶段）：
  - **本质点破**：在合适的页点出"它的本质是XXX（一句话点破）"
  - **反常识根因**：在合适的页暴露至少1个反常识根因（"你可能会觉得XXX，但其实真相是YYY"），用反差制造"原来如此"
  - **视角升级收尾**：最后一页或收尾页必须视角升级——不是总结，是重新定义问题（"所以下次再看到XXX，不要问A，要问B"）
- 多用自然过渡语

## 输出格式
严格输出JSON，不要任何其他解释文字，不要markdown代码块包裹，直接输出JSON。v2.1 扩展字段（scene_phase/essence_definition等）为**可选元数据**，不强制每页都有：
{
  "title": "内容标题",
  "canvas_layout": "horizontal",
  "methodology_version": "v2.1",
  "total_scenes": 0,
  "scenes": [
    {
      "scene_index": 0,
      "scene_title": "页面标题（由内容决定，不强制'阶段1·是什么'格式）",
      "viewport_x": 960,
      "viewport_y": 540,
      "viewport_zoom": 1,
      "duration_estimate": 60,
      "epiphany_trigger": "顿悟触发点金句（可独立传播）",
      "teleprompter_script": "讲解文本...",
      "elements": [],
      "scene_phase": "stage1_what",
      "essence_definition": "本质定义一句话（揭底式，可选元数据）",
      "essence_check": "本质检验通过说明（可选元数据，思考层校验）",
      "causal_chain": "因果链一句话总结（可选元数据）",
      "counterintuitive_root": "反常识根因（可选元数据）",
      "structural_metaphor": "结构性比喻（可选元数据）",
      "perspective_upgrade": "视角升级金句（可选元数据）"
    }
  ]
}

> 说明：
> - scene_phase 可选值：stage1_what / stage2_why / stage3_how（可选，用于标注该页主要对应哪个思考阶段；一页可跨阶段或无关阶段时省略）
> - essence_definition/essence_check/causal_chain/counterintuitive_root/structural_metaphor/perspective_upgrade 为可选元数据，不强制每页都有
> - 必填字段：scene_index / scene_title / viewport_x / viewport_y / viewport_zoom / duration_estimate / epiphany_trigger / teleprompter_script / elements
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
    """导出为WhiteboardCaster项目格式（含场景和提词器，v2.1含可选方法论元数据）"""
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
        # v2.1 可选元数据字段（不强制每页都有）
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
        f.write(f"# {title} - 提词器脚本（v2.1方法论，思考层/输出层分离）\n\n")
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
