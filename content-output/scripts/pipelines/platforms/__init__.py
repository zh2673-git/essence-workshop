"""
本质工坊 · 统一平台适配器

不同形式（form）在不同平台（platform）上有不同约束。
适配器根据 form + platform 对选项进行校验和默认填充。
"""
from .base import PlatformAdapter, PlatformConstraint
from .browser import BrowserAdapter
from .wechat import WechatAdapter
from .office import OfficeAdapter
from .jupyter import JupyterAdapter
from .reveal import RevealAdapter
from .video_channel import VideoChannelAdapter
from .bilibili import BilibiliAdapter
from .douyin import DouyinAdapter

ADAPTERS = {
    'browser': BrowserAdapter,
    'wechat': WechatAdapter,
    'office': OfficeAdapter,
    'jupyter': JupyterAdapter,
    'reveal': RevealAdapter,
    'video-channel': VideoChannelAdapter,
    'bilibili': BilibiliAdapter,
    'douyin': DouyinAdapter,
}


def get_adapter(platform: str):
    if platform not in ADAPTERS:
        raise ValueError(f"Unknown platform: {platform}. Supported: {list(ADAPTERS.keys())}")
    return ADAPTERS[platform]()


def list_platforms() -> list[str]:
    return list(ADAPTERS.keys())


def supported_platforms_for_form(form: str) -> list[str]:
    return [name for name, cls in ADAPTERS.items() if form in cls().supported_forms]
