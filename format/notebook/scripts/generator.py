"""
本质工坊 · Notebook 管线

从元素层读取 → 生成 Jupyter Notebook (.ipynb)。

用法:
  python -m scripts.pipelines.notebook.generator --elements output/elements/ --output output/notebook/
"""
import argparse
import json
import os


def generate_notebook(elements_dir, output_dir, title="Notebook"):
    """从元素层读取文本元素，组装为 .ipynb 文件。"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "notebook.ipynb")

    # 读取文本元素作为 markdown cell 来源
    text_dir = os.path.join(elements_dir, "text")
    cells = []
    if os.path.isdir(text_dir):
        for f in sorted(os.listdir(text_dir)):
            if not f.endswith(".md"):
                continue
            with open(os.path.join(text_dir, f), "r", encoding="utf-8") as fp:
                content = fp.read()
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": content.splitlines(keepends=True),
            })

    if not cells:
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"# {title}"],
        })

    nb = {
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
        "nbformat": 4,
        "nbformat_minor": 4,
        "cells": cells,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=2)

    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="本质工坊 · Notebook 管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--title", default="Notebook", help="标题")
    args = parser.parse_args(argv)

    result = generate_notebook(args.elements, args.output, args.title)
    print(f"[Notebook Pipeline] Output: {result}")


if __name__ == "__main__":
    main()
