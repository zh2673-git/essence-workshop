"""
本质工坊 · 内容输出统一调度器

根据 --form + --platform 路由到对应生成器，并应用平台约束。
为避免 `scripts` / `html` 等通用命名冲突，生成器通过 importlib 按文件路径加载。
"""
import argparse
import importlib.util
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_module_by_path(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _module_path(relpath: str) -> str:
    return os.path.join(SCRIPT_DIR, relpath)


def apply_platform(platform: str, form: str, options: dict) -> dict:
    platforms = _load_module_by_path('platforms', _module_path('platforms/__init__.py'))
    adapter = platforms.get_adapter(platform)
    errors = adapter.validate(form, options)
    if errors:
        raise ValueError('; '.join(errors))
    return adapter.apply(form, options)


def route_html(elements_dir: str, output_dir: str, platform: str, **kwargs):
    generator = _load_module_by_path('html_generator', _module_path('html/generator.py'))
    options = apply_platform(platform, 'html', {
        'elements_dir': elements_dir,
        'output_dir': output_dir,
        'brand_spec_path': kwargs.get('brand_spec'),
        'title': kwargs.get('title', '课程'),
        'mode': kwargs.get('mode', 'scroll'),
    })
    generator.generate_html(
        elements_dir=options['elements_dir'],
        output_dir=options['output_dir'],
        brand_spec_path=options.get('brand_spec_path'),
        title=options.get('title', '课程'),
        mode=options.get('mode', 'scroll'),
    )
    return os.path.join(output_dir, 'index.html')


def route_slides(elements_dir: str, output_dir: str, platform: str, **kwargs):
    generator = _load_module_by_path('slides_generator', _module_path('slides/generator.py'))
    options = apply_platform(platform, 'slides', {
        'elements_dir': elements_dir,
        'output_dir': output_dir,
        'title': kwargs.get('title', '演示'),
        'theme': kwargs.get('theme', 'black'),
    })
    generator.generate_slides(
        elements_dir=options['elements_dir'],
        output_dir=options['output_dir'],
        title=options.get('title', '演示'),
        theme=options.get('theme', 'black'),
    )
    return os.path.join(output_dir, 'index.html')


def route_pptx(elements_dir: str, output_dir: str, platform: str, **kwargs):
    generator = _load_module_by_path('pptx_generator', _module_path('pptx/generator.py'))
    options = apply_platform(platform, 'pptx', {
        'elements_dir': elements_dir,
        'output_dir': output_dir,
        'template_path': kwargs.get('template'),
        'brand_spec_path': kwargs.get('brand_spec'),
        'title': kwargs.get('title', '演示'),
        'mode': kwargs.get('mode', 'simple'),
        'layout': kwargs.get('layout', 'LAYOUT_16x9'),
    })
    generator.generate_pptx(
        elements_dir=options['elements_dir'],
        output_dir=options['output_dir'],
        template_path=options.get('template_path'),
        brand_spec_path=options.get('brand_spec_path'),
        title=options.get('title', '演示'),
        mode=options.get('mode', 'simple'),
        layout=options.get('layout', 'LAYOUT_16x9'),
    )
    return os.path.join(output_dir, 'output.pptx')


def route_markdown(elements_dir: str, output_dir: str, platform: str, **kwargs):
    generator = _load_module_by_path('markdown_generator', _module_path('markdown/generator.py'))
    options = apply_platform(platform, 'markdown', {
        'elements_dir': elements_dir,
        'output_dir': output_dir,
        'title': kwargs.get('title', ''),
        'platform': platform,
        'attachment_dir': kwargs.get('attachment_dir', 'assets'),
    })
    generator.generate_markdown(
        elements_dir=options['elements_dir'],
        output_dir=options['output_dir'],
        title=options.get('title', ''),
        platform=options.get('platform', 'obsidian'),
        attachment_dir=options.get('attachment_dir', 'assets'),
    )
    return os.path.join(output_dir, 'index.md')


def route_notebook(elements_dir: str, output_dir: str, platform: str, **kwargs):
    options = apply_platform(platform, 'notebook', {
        'elements_dir': elements_dir,
        'output_dir': output_dir,
        'title': kwargs.get('title', 'Notebook'),
    })
    project_root = os.path.join(SCRIPT_DIR, '..', '..')
    template_path = os.path.join(project_root, 'templates', 'notebook-template.ipynb')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'notebook.ipynb')

    if os.path.isfile(template_path):
        import shutil
        shutil.copy(template_path, output_path)
    else:
        import json
        nb = {
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 4,
            "cells": [
                {"cell_type": "markdown", "metadata": {}, "source": [f"# {options.get('title', 'Notebook')}"]},
                {"cell_type": "markdown", "metadata": {}, "source": ["由本质工坊自动生成。"]},
            ],
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=2)

    return output_path


def dispatch(form: str, platform: str, elements_dir: str = '', output_dir: str = '', **kwargs):
    """统一调度入口。"""
    if not elements_dir or not os.path.isdir(elements_dir):
        raise ValueError(f'请提供有效的元素层目录: {elements_dir}')

    if form == 'html':
        return route_html(elements_dir, output_dir, platform, **kwargs)
    elif form == 'slides':
        return route_slides(elements_dir, output_dir, platform, **kwargs)
    elif form == 'pptx':
        return route_pptx(elements_dir, output_dir, platform, **kwargs)
    elif form == 'markdown':
        return route_markdown(elements_dir, output_dir, platform, **kwargs)
    elif form == 'notebook':
        return route_notebook(elements_dir, output_dir, platform, **kwargs)
    else:
        raise ValueError(f"不支持的 form: {form}")


def main(argv=None):
    parser = argparse.ArgumentParser(description='本质工坊 · 内容输出统一调度器')
    parser.add_argument('--form', required=True,
                        choices=['html', 'slides', 'pptx', 'markdown', 'notebook'],
                        help='内容形式')
    parser.add_argument('--platform', required=True,
                        choices=['browser', 'wechat', 'office', 'jupyter', 'reveal', 'obsidian'],
                        help='目标平台')
    parser.add_argument('--elements', required=True, help='元素层目录路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    parser.add_argument('--title', default='', help='标题')
    parser.add_argument('--brand-spec', default=None, help='品牌规格文件路径')
    parser.add_argument('--template', default=None, help='模板文件路径（PPT）')
    parser.add_argument('--mode', default=None, help='生成模式')
    parser.add_argument('--theme', default=None, help='主题（slides）')
    parser.add_argument('--layout', default=None, help='布局（pptx precise）')

    args = parser.parse_args(argv)

    kwargs = {}
    for key in ['title', 'brand_spec', 'template', 'mode', 'theme', 'layout']:
        value = getattr(args, key)
        if value is not None:
            kwargs[key] = value

    result = dispatch(args.form, args.platform, args.elements, args.output, **kwargs)
    print(f"[Dispatcher] {args.form}/{args.platform} → {result}")


if __name__ == '__main__':
    main()
