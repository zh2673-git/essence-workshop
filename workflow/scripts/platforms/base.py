"""
平台适配器基类。

- PlatformAdapter：通用基类，支持 html / slides / pptx / notebook 等形式。
- VideoPlatformAdapter：视频专用，处理 width/height/fps/duration 等数值约束。
"""
from typing import TypedDict, Optional


class PlatformConstraint(TypedDict, total=False):
    description: str
    max_width: Optional[int]
    max_height: Optional[int]
    inline_css: bool
    allow_script: bool
    allowed_tags: list[str]
    forbidden_tags: list[str]
    image_hosting: str
    file_extension: str
    inline_svg: bool
    wiki_links: bool
    callouts: bool
    attachment_dir: str


DEFAULT_CONSTRAINTS: dict[str, PlatformConstraint] = {
    'html': {
        'description': '标准 HTML',
        'max_width': None,
        'max_height': None,
        'inline_css': False,
        'allow_script': True,
        'allowed_tags': [],
        'forbidden_tags': [],
        'image_hosting': 'relative',
        'file_extension': '.html',
    },
    'slides': {
        'description': '演示幻灯片',
        'max_width': 1920,
        'max_height': 1080,
        'inline_css': False,
        'allow_script': True,
        'allowed_tags': [],
        'forbidden_tags': [],
        'image_hosting': 'relative',
        'file_extension': '.html',
    },
    'pptx': {
        'description': 'PowerPoint',
        'max_width': 1920,
        'max_height': 1080,
        'inline_css': False,
        'allow_script': False,
        'allowed_tags': [],
        'forbidden_tags': [],
        'image_hosting': 'inline',
        'file_extension': '.pptx',
    },
    'notebook': {
        'description': 'Jupyter Notebook',
        'max_width': None,
        'max_height': None,
        'inline_css': False,
        'allow_script': True,
        'allowed_tags': [],
        'forbidden_tags': [],
        'image_hosting': 'inline',
        'file_extension': '.ipynb',
    },
    'markdown': {
        'description': 'Markdown',
        'max_width': None,
        'max_height': None,
        'inline_svg': True,
        'wiki_links': False,
        'callouts': False,
        'attachment_dir': 'assets',
        'file_extension': '.md',
    },
}


class PlatformAdapter:
    """通用平台适配器基类，适用于 html / slides / pptx / notebook 等形式。"""
    name: str = ''
    supported_forms: list[str] = []
    constraints: dict[str, PlatformConstraint] = {}

    def get_constraint(self, form: str) -> PlatformConstraint:
        base = DEFAULT_CONSTRAINTS.get(form, {})
        override = self.constraints.get(form, {})
        merged = dict(base)
        merged.update(override)
        return merged

    def apply(self, form: str, options: dict) -> dict:
        """用平台约束覆盖或校验选项。"""
        result = dict(options)
        constraint = self.get_constraint(form)
        result['_platform'] = self.name
        result['_platform_description'] = constraint.get('description', '')
        return result

    def validate(self, form: str, options: dict) -> list[str]:
        errors: list[str] = []
        if form not in self.supported_forms:
            errors.append(f"平台 {self.name} 不支持形式 {form}")
        return errors


class VideoConstraints(TypedDict):
    width: int
    height: int
    fps: int
    max_duration_seconds: int
    preferred_format: str
    aspect_ratio: str


class VideoPlatformAdapter:
    """视频平台适配器基类，处理数值型分辨率/帧率/时长约束。"""
    name: str = ''
    constraints: VideoConstraints = {
        'width': 1080,
        'height': 1920,
        'fps': 30,
        'max_duration_seconds': 600,
        'preferred_format': 'mp4',
        'aspect_ratio': '9:16',
    }

    def apply(self, options: dict) -> dict:
        """用平台约束覆盖或校验用户选项，返回调整后的选项。

        宽、高、fps 等数值若用户传入 0，视为未指定，由平台默认值填充。
        """
        result = dict(options)
        for key, value in self.constraints.items():
            if key == 'max_duration_seconds':
                continue
            current = result.get(key)
            if current is None or current == 0 or current == '':
                result[key] = value
        return result

    def validate(self, options: dict) -> list[str]:
        """返回校验错误列表，空列表表示通过。"""
        errors: list[str] = []
        duration = options.get('duration', 0)
        if duration > self.constraints['max_duration_seconds']:
            errors.append(
                f"{self.name} 最大时长 {self.constraints['max_duration_seconds']}s，"
                f"当前 {duration}s"
            )
        return errors
