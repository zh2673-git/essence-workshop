"""
浏览器平台：标准 HTML/Slides，无特殊限制。
"""
from .base import PlatformAdapter


class BrowserAdapter(PlatformAdapter):
    name = 'browser'
    supported_forms = ['html', 'slides']
    constraints = {
        'html': {'description': '标准浏览器 HTML'},
        'slides': {'description': '浏览器中运行的 Reveal.js 演示'},
    }
