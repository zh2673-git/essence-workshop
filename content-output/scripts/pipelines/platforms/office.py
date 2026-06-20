"""
Office 平台：PPT/WPS。
"""
from .base import PlatformAdapter


class OfficeAdapter(PlatformAdapter):
    name = 'office'
    supported_forms = ['pptx']
    constraints = {
        'pptx': {
            'description': 'Microsoft PowerPoint / WPS',
            'image_hosting': 'inline',
        }
    }
