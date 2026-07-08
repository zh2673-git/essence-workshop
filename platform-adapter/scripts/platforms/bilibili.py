"""
B站适配器：横屏 16:9。
"""
from .base import VideoPlatformAdapter


class BilibiliAdapter(VideoPlatformAdapter):
    name = 'bilibili'
    supported_forms = ['video']
    constraints = {
        'width': 1920,
        'height': 1080,
        'fps': 30,
        'max_duration_seconds': 600,
        'preferred_format': 'mp4',
        'aspect_ratio': '16:9',
    }
