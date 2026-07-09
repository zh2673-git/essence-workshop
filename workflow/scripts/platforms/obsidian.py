"""
Obsidian 平台适配器：Markdown 笔记 / 知识库。

约束：
- 使用 wiki-link 语法：[[附件]]
- 支持 callout：> [!NOTE]
- SVG 必须作为附件，不能内联
- 附件统一放入 assets/ 目录
- 优先使用本地相对路径
"""
from .base import PlatformAdapter


class ObsidianAdapter(PlatformAdapter):
    name = 'obsidian'
    supported_forms = ['markdown']
    constraints = {
        'markdown': {
            'description': 'Obsidian Markdown',
            'inline_svg': False,
            'wiki_links': True,
            'callouts': True,
            'attachment_dir': 'assets',
            'file_extension': '.md',
        }
    }
