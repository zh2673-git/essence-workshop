"""
Jupyter 平台：Notebook。
"""
from .base import PlatformAdapter


class JupyterAdapter(PlatformAdapter):
    name = 'jupyter'
    supported_forms = ['notebook']
    constraints = {
        'notebook': {
            'description': 'Jupyter Notebook',
            'image_hosting': 'inline',
        }
    }
