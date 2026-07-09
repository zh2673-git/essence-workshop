"""
本质工坊 · SVG→Whiteboard 桥接器

把其他场景（K12拆解、知识图谱、HTML管线、演示管线等）生成的SVG
转换为Excalidraw可嵌入的image元素，实现"SVG→PNG→image元素"混合渲染。

流程：
  1. 读取SVG文件
  2. 调用同目录 svg_to_png.py 转换为PNG（Playwright渲染，中文字体正确）
  3. PNG转base64，按Excalidraw的files格式嵌入
  4. 生成对应的image元素JSON（type="image"，含x/y/width/height/status/fileId）
  5. 输出可直接合并到 .whiteboard.json 的片段

用法：
  # 单SVG文件
  python svg_to_whiteboard.py -i input.svg -o scene_assets.json --scene-index 0 --position-x 100 --position-y 200

  # SVG目录（批量转换，纵向排列）
  python svg_to_whiteboard.py -i svg_dir/ -o scene_assets.json --scene-index 0 --position-x 100 --position-y 200

  # 直接合并到 .whiteboard.json（可选）
  python svg_to_whiteboard.py -i input.svg -o scene_assets.json --scene-index 0 --merge-to project.whiteboard.json

输出片段结构：
  {
    "scene_index": 0,
    "image_elements": [...],
    "files": { "file_scene0_xxx": { mimeType, id, dataURL } }
  }

合并方式：
  - image_elements 合并到 .whiteboard.json 对应 scene.elements
  - files 合并到 .whiteboard.json 顶层 files 字段
"""

import argparse
import base64
import json
import os
import re
import sys
import random
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

# 引入同目录的 svg_to_png（Playwright渲染，中文字体正确）
from svg_to_png import svg_to_png


def _read_png_size(png_path):
    """
    读取PNG文件的宽高（不依赖PIL，直接解析PNG头部IHDR chunk）
    PNG格式：8字节signature + IHDR chunk（含4字节width + 4字节height，big-endian）
    """
    with open(png_path, "rb") as f:
        f.seek(16)  # 跳过8字节signature + 4字节length + 4字节"IHDR"
        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
    return width, height


def _safe_id(name):
    """把SVG文件名转为安全的ID片段（仅字母数字下划线）"""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "asset"


def svg_to_image_element(svg_path, scene_index, x, y, max_width=800, max_height=600, dpi=2):
    """
    把单个SVG转换为Excalidraw image元素 + files条目

    Args:
        svg_path: SVG文件路径
        scene_index: 场景索引（用于ID命名）
        x, y: image元素的左上角坐标
        max_width, max_height: image元素在白板上的最大显示尺寸（按比例缩放）
        dpi: PNG渲染倍率（默认2x）

    Returns:
        (image_element_dict, file_entry_dict, file_id)
    """
    if not os.path.isfile(svg_path):
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    # 1. 调用svg_to_png转换为PNG（临时文件）
    png_fd, png_path = tempfile.mkstemp(suffix=".png", prefix="svg2wb_")
    os.close(png_fd)
    try:
        print(f"[SVG→Whiteboard] 渲染: {Path(svg_path).name} → PNG (dpi={dpi})")
        svg_to_png(svg_path, png_path, dpi=dpi)

        # 2. 读取PNG并转base64
        with open(png_path, "rb") as f:
            png_data = f.read()
        b64_data = base64.b64encode(png_data).decode("ascii")

        # 3. 获取PNG像素尺寸（直接解析PNG头部，不依赖PIL）
        png_w, png_h = _read_png_size(png_path)
    finally:
        try:
            os.unlink(png_path)
        except OSError:
            pass

    # 4. 计算缩放后的显示尺寸（保持宽高比，不超过max_width/max_height）
    scale = min(max_width / png_w, max_height / png_h, 1.0)
    final_width = int(png_w * scale)
    final_height = int(png_h * scale)

    # 5. 生成file_id和image元素
    svg_name = Path(svg_path).stem
    safe_name = _safe_id(svg_name)
    file_id = f"file_scene{scene_index}_{safe_name}"
    img_id = f"img_scene{scene_index}_{safe_name}"

    image_element = {
        "type": "image",
        "id": img_id,
        "x": x,
        "y": y,
        "width": final_width,
        "height": final_height,
        "angle": 0,
        "strokeColor": "transparent",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "seed": random.randint(1, 1000000),
        "version": 1,
        "versionNonce": random.randint(1, 1000000),
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
        "status": "saved",
        "fileId": file_id,
        "scale": [1, 1]
    }

    file_entry = {
        "mimeType": "image/png",
        "id": file_id,
        "dataURL": f"data:image/png;base64,{b64_data}"
    }

    return image_element, file_entry, file_id


def convert_dir(svg_dir, scene_index, x_start, y_start, max_width=800, max_height=600, gap=50, dpi=2):
    """
    批量转换目录下所有SVG，纵向排列（每张图从上到下堆叠）

    Args:
        svg_dir: SVG目录
        scene_index: 场景索引
        x_start, y_start: 起始坐标
        max_width, max_height: 单图最大显示尺寸
        gap: 多图之间的纵向间距
        dpi: PNG渲染倍率

    Returns:
        (image_elements_list, files_dict)
    """
    elements = []
    files = {}
    current_y = y_start

    svg_files = sorted([f for f in os.listdir(svg_dir) if f.lower().endswith(".svg")])
    if not svg_files:
        print(f"[SVG→Whiteboard] WARNING: 目录下没有SVG文件: {svg_dir}")
        return elements, files

    for i, svg_file in enumerate(svg_files):
        svg_path = os.path.join(svg_dir, svg_file)
        print(f"[SVG→Whiteboard] 处理 {i + 1}/{len(svg_files)}: {svg_file}")
        el, file_entry, file_id = svg_to_image_element(
            svg_path, scene_index, x_start, current_y,
            max_width, max_height, dpi
        )
        elements.append(el)
        files[file_id] = file_entry
        current_y += (el["height"] + gap)

    return elements, files


def merge_to_whiteboard(whiteboard_path, scene_index, image_elements, files):
    """
    把生成的image元素和files合并到现有的 .whiteboard.json

    Args:
        whiteboard_path: .whiteboard.json 文件路径
        scene_index: 目标场景索引
        image_elements: 待合并的image元素列表
        files: 待合并的files字典

    Returns:
        合并的元素数量
    """
    if not os.path.isfile(whiteboard_path):
        raise FileNotFoundError(f"Whiteboard project not found: {whiteboard_path}")

    with open(whiteboard_path, "r", encoding="utf-8") as f:
        project = json.load(f)

    # 找到目标场景
    target_scene = None
    for scene in project.get("scenes", []):
        if scene.get("index") == scene_index:
            target_scene = scene
            break

    if target_scene is None:
        raise ValueError(f"Scene index {scene_index} not found in {whiteboard_path}")

    # 合并image元素到目标场景的elements
    if "elements" not in target_scene:
        target_scene["elements"] = []
    target_scene["elements"].extend(image_elements)

    # 合并files到顶层files字段
    if "files" not in project:
        project["files"] = {}
    project["files"].update(files)

    with open(whiteboard_path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)

    return len(image_elements)


def main():
    parser = argparse.ArgumentParser(
        description="本质工坊 · SVG→Whiteboard桥接器（SVG→PNG→image元素混合渲染）"
    )
    parser.add_argument("-i", "--input", required=True,
                        help="SVG文件路径或SVG目录")
    parser.add_argument("-o", "--output", required=True,
                        help="输出JSON片段路径（含image_elements和files）")
    parser.add_argument("--scene-index", type=int, default=0,
                        help="场景索引（用于ID命名，默认0）")
    parser.add_argument("--position-x", type=int, default=100,
                        help="起始X坐标（默认100）")
    parser.add_argument("--position-y", type=int, default=200,
                        help="起始Y坐标（默认200）")
    parser.add_argument("--max-width", type=int, default=800,
                        help="单图最大显示宽度（默认800px）")
    parser.add_argument("--max-height", type=int, default=600,
                        help="单图最大显示高度（默认600px）")
    parser.add_argument("--gap", type=int, default=50,
                        help="多图之间的纵向间距（默认50px）")
    parser.add_argument("--dpi", type=float, default=2,
                        help="PNG渲染倍率（默认2x）")
    parser.add_argument("--merge-to", default=None,
                        help="可选：直接合并到指定的 .whiteboard.json 文件路径")
    args = parser.parse_args()

    # 1. 转换SVG为image元素
    if os.path.isfile(args.input):
        el, file_entry, file_id = svg_to_image_element(
            args.input, args.scene_index,
            args.position_x, args.position_y,
            args.max_width, args.max_height, args.dpi
        )
        elements = [el]
        files = {file_id: file_entry}
    elif os.path.isdir(args.input):
        elements, files = convert_dir(
            args.input, args.scene_index,
            args.position_x, args.position_y,
            args.max_width, args.max_height, args.gap, args.dpi
        )
    else:
        print(f"ERROR: Input not found: {args.input}")
        sys.exit(1)

    if not elements:
        print("[SVG→Whiteboard] 没有生成任何image元素，退出")
        sys.exit(1)

    # 2. 输出片段JSON
    output = {
        "scene_index": args.scene_index,
        "image_elements": elements,
        "files": files,
        "merge_guide": {
            "image_elements": "合并到 .whiteboard.json 对应 scene.elements",
            "files": "合并到 .whiteboard.json 顶层 files 字段"
        }
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[SVG→Whiteboard] 转换完成:")
    print(f"  image元素数量: {len(elements)}")
    print(f"  files条目数量: {len(files)}")
    print(f"  片段输出: {args.output}")

    # 3. 可选：直接合并到 .whiteboard.json
    if args.merge_to:
        print(f"\n[SVG→Whiteboard] 正在合并到: {args.merge_to}")
        merged = merge_to_whiteboard(
            args.merge_to, args.scene_index, elements, files
        )
        print(f"  已合并 {merged} 个image元素到场景 {args.scene_index}")
        print(f"  已更新顶层 files 字段")
    else:
        print(f"\n  合并方式（手动）：")
        print(f"  - 把 image_elements 合并到 .whiteboard.json 对应 scene.elements")
        print(f"  - 把 files 合并到 .whiteboard.json 顶层 files 字段")
        print(f"  或使用 --merge-to <path.whiteboard.json> 自动合并")


if __name__ == "__main__":
    main()
