"""
本质工坊 · 视频管线路由器

新模型：
- form = 'video'（当前目录只负责 video 形式）
- method = dsl / html_record / article_to_video（同一形式内的不同实现路径）

router 负责根据内容特征选择 method。
"""
from typing import Literal, Optional, TypedDict

Method = Literal['dsl', 'html_record', 'article_to_video']


class ContentSpec(TypedDict, total=False):
    source: str
    hasStructuredHTML: bool
    htmlPath: str
    articleUrl: str
    visualComplexity: str
    hasAnimationRequirements: bool
    hasMediaSync: bool
    durationSeconds: int
    sections: list


class RouterConfig(TypedDict, total=False):
    preferDsl: bool
    maxHtmlRecordDuration: int
    enableFallback: bool


class RouterDecision(TypedDict):
    method: Method
    reason: str
    confidence: Literal['high', 'medium', 'low']
    fallback: Optional[Method]


def select_method(content_spec: ContentSpec, config: Optional[RouterConfig] = None) -> RouterDecision:
    config = config or {}

    if config.get('preferDsl'):
        return {
            'method': 'dsl',
            'reason': '用户显式选择 DSL 管线',
            'confidence': 'high',
            'fallback': None,
        }

    source = content_spec.get('source', 'user_input')
    if source == 'web_article':
        return {
            'method': 'article_to_video',
            'reason': '来源是网页文章，使用 slides 模板转视频',
            'confidence': 'high',
            'fallback': 'html_record',
        }

    has_html = content_spec.get('hasStructuredHTML', False)
    complexity = content_spec.get('visualComplexity', 'medium')
    has_animation = content_spec.get('hasAnimationRequirements', False)
    has_sync = content_spec.get('hasMediaSync', False)

    if has_html and complexity != 'high' and not has_animation and not has_sync:
        max_duration = config.get('maxHtmlRecordDuration', 300)
        if content_spec.get('durationSeconds', 60) <= max_duration:
            return {
                'method': 'html_record',
                'reason': '已有结构化 HTML，且动画需求低，直接录制最轻量',
                'confidence': 'high',
                'fallback': 'dsl',
            }

    if complexity == 'high' or has_animation or has_sync:
        return {
            'method': 'dsl',
            'reason': '存在帧级动画或音画同步需求，DSL 更精确',
            'confidence': 'high',
            'fallback': None,
        }

    return {
        'method': 'dsl',
        'reason': '默认使用 DSL 管线以获得更好的动画控制能力',
        'confidence': 'medium',
        'fallback': 'html_record',
    }


def explain_decision(decision: RouterDecision) -> str:
    return (
        f"形式 video / 方法 {decision['method']}，"
        f"原因：{decision['reason']}（置信度：{decision['confidence']}）"
    )


# 向后兼容：旧函数名保留，内部调用新方法
def select_pipeline(content_spec: ContentSpec, config: Optional[RouterConfig] = None) -> RouterDecision:
    return select_method(content_spec, config)
