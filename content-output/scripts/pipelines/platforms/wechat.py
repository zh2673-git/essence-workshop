"""
微信公众号平台：受限 HTML，必须内联样式。
"""
from .base import PlatformAdapter


class WechatAdapter(PlatformAdapter):
    name = 'wechat'
    supported_forms = ['html']
    constraints = {
        'html': {
            'description': '微信公众号受限 HTML',
            'inline_css': True,
            'allow_script': False,
            'forbidden_tags': ['script', 'style', 'iframe'],
            'image_hosting': 'wechat_cdn',
            'file_extension': '.html',
        }
    }
