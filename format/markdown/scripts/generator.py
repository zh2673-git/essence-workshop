"""
本质工坊 · Markdown 管线

从元素层读取 → 合并为 Markdown 文件。

用法:
  python -m scripts.pipelines.markdown.generator --elements output/elements/ --output output/markdown/
  python -m scripts.pipelines.markdown.generator --elements output/elements/ --output output/markdown/ --title "笔记标题"
"""
import argparse
import os
import re
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _sanitize_filename(name: str) -> str:
    """把字符串转换为可用的文件名/锚点。"""
    return re.sub(r'[^\w\-\.\u4e00-\u9fff]', '_', name).strip('_')


def _load_text_elements(elements_dir: str) -> list[tuple[str, str]]:
    """读取文本元素，返回 [(filename, content), ...] 。"""
    text_dir = os.path.join(elements_dir, 'text')
    if not os.path.isdir(text_dir):
        return []
    results = []
    for fname in sorted(os.listdir(text_dir)):
        if not fname.endswith('.md'):
            continue
        path = os.path.join(text_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            results.append((fname, f.read()))
    return results


def _load_svg_elements(elements_dir: str) -> dict[str, str]:
    """读取 SVG 图形元素，返回 {name: filepath}。"""
    graphics_dir = os.path.join(elements_dir, 'graphics')
    if not os.path.isdir(graphics_dir):
        return {}
    svgs = {}
    for fname in sorted(os.listdir(graphics_dir)):
        if not fname.endswith('.svg'):
            continue
        name = os.path.splitext(fname)[0]
        svgs[name] = os.path.join(graphics_dir, fname)
    return svgs


def _extract_title(texts: list[tuple[str, str]]) -> str:
    """从第一份文本的第一个 H1 提取标题。"""
    for _, content in texts:
        for line in content.splitlines():
            if line.startswith('# '):
                return line[2:].strip()
    return '笔记'


def generate_markdown(
    elements_dir: str,
    output_dir: str,
    title: str = '',
    attachment_dir: str = 'assets',
):
    """生成 Markdown 文件。"""
    print('[Markdown Pipeline] Starting...')

    texts = _load_text_elements(elements_dir)
    svgs = _load_svg_elements(elements_dir)

    if not title:
        title = _extract_title(texts)

    os.makedirs(output_dir, exist_ok=True)
    assets_dir = os.path.join(output_dir, attachment_dir)
    os.makedirs(assets_dir, exist_ok=True)

    asset_names = []
    for name, src_path in svgs.items():
        safe_name = _sanitize_filename(name) + '.svg'
        dst_path = os.path.join(assets_dir, safe_name)
        shutil.copy2(src_path, dst_path)
        asset_names.append(_sanitize_filename(name))

    sections = []
    for fname, content in texts:
        sections.append(content)

    # 在文末追加图形引用
    if asset_names:
        sections.append('## 图形')
        for name in asset_names:
            sections.append(f'![{name}]({attachment_dir}/{name}.svg)')

    body = '\n\n'.join(sections)

    frontmatter = f'---\ntitle: {title}\n---\n\n'
    output = frontmatter + f'# {title}\n\n' + body

    output_path = os.path.join(output_dir, 'index.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'  Text elements: {len(texts)}, SVG assets: {len(svgs)}')
    print(f'  Output: {output_path}')
    print('[Markdown Pipeline] Done.')
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description='本质工坊 · Markdown 管线')
    parser.add_argument('--elements', required=True, help='元素层目录路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    parser.add_argument('--title', default='', help='笔记标题')
    parser.add_argument('--attachment-dir', default='assets', help='附件目录名')
    args = parser.parse_args(argv)

    generate_markdown(
        elements_dir=args.elements,
        output_dir=args.output,
        title=args.title,
        attachment_dir=args.attachment_dir,
    )


if __name__ == '__main__':
    main()
