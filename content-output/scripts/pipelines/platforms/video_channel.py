"""
微信视频号适配器：竖屏 9:16。
"""
from .base import VideoPlatformAdapter


class VideoChannelAdapter(VideoPlatformAdapter):
    name = 'video-channel'
    supported_forms = ['video']
    constraints = {
        'width': 1080,
        'height': 1920,
        'fps': 30,
        'max_duration_seconds': 600,
        'preferred_format': 'mp4',
        'aspect_ratio': '9:16',
    }
