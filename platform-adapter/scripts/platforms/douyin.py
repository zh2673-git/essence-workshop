"""
抖音适配器：竖屏 9:16，建议 720x1280。
"""
from .base import VideoPlatformAdapter


class DouyinAdapter(VideoPlatformAdapter):
    name = 'douyin'
    supported_forms = ['video']
    constraints = {
        'width': 720,
        'height': 1280,
        'fps': 30,
        'max_duration_seconds': 600,
        'preferred_format': 'mp4',
        'aspect_ratio': '9:16',
    }
