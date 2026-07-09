"""
Reveal.js 平台：Slides 的专用运行环境。
"""
from .base import PlatformAdapter


class RevealAdapter(PlatformAdapter):
    name = 'reveal'
    supported_forms = ['slides']
    constraints = {
        'slides': {
            'description': 'Reveal.js 幻灯片',
            'allow_script': True,
        }
    }
