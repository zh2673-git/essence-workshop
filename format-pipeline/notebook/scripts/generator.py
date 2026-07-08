"""
本质工坊 · Notebook 管线

从元素层读取 → 生成 Jupyter Notebook (.ipynb)。

用法:
  python -m scripts.pipelines.notebook.generator --elements output/elements/ --output output/notebook/
"""
import argparse
import os


def main(argv=None):
    parser = argparse.ArgumentParser(description="本质工坊 · Notebook 管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--title", default="Notebook", help="标题")
    args = parser.parse_args(argv)

    from ..dispatcher import dispatch
    dispatch('notebook', args.elements, args.output, title=args.title)


if __name__ == "__main__":
    main()
