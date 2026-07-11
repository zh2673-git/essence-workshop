"""
生成公众号封面图（调用 text_to_image API）

原理：
  text_to_image API 基于 SDXL（Stable Diffusion XL）文生图模型。
  通过 HTTP GET 请求传入 prompt（画面描述）和 image_size（画幅比例），
  返回 image/jpeg 二进制流，应按 prompt 内容生成对应图片。

历史问题根因（已修复）：
  之前生成的封面"无法显示具体图案和文字"，并非 SDXL 模型能力不足，
  而是请求被 CDN 边缘节点当作静态资源缓存：
    - 响应头缺少 Cache-Control: no-store
    - CDN 缓存 key 仅用 URL 路径，忽略 query string
    - 所有不同 prompt/image_size 的请求都命中同一份缓存
    - 返回 2025-09-12 的固定占位图（MD5: 19a0b822edb11957055e4588c2159058）
  本脚本通过检测占位图 MD5 避免使用缓存结果。

注意：
  prompt 必须是具体、可视化的画面描述（场景/物体/光线/构图），
  不要要求图中包含文字——SDXL 对中文文字渲染能力差。
  封面的文字由公众号标题位承载，图只负责视觉氛围。
"""
import hashlib
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"
# 已知的 CDN 占位图 MD5（2025-09-12 缓存的固定图）
PLACEHOLDER_MD5 = "19a0b822edb11957055e4588c2159058"
JPEG_HEADER = b"\xff\xd8\xff\xe0"
PNG_HEADER = b"\x89PNG"


def generate_cover(
    prompt: str,
    output_path: str,
    image_size: str = "landscape_16_9",
) -> Path:
    """
    调用 text_to_image API 生成封面图。

    Args:
        prompt: 具体的画面描述（英文 SDXL 风格 prompt，避免中文文字）
        output_path: 输出文件路径
        image_size: 画幅比例（landscape_16_9 最接近公众号 1240×770）

    Returns:
        生成的图片路径

    Raises:
        RuntimeError: API 返回占位图（CDN 缓存命中）或下载失败
    """
    params = urllib.parse.urlencode({"prompt": prompt, "image_size": image_size})
    url = f"{API_BASE}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache, no-store",
            "Pragma": "no-cache",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as e:
        raise RuntimeError(f"API 请求失败: {e}")

    if len(data) < 1024:
        raise RuntimeError(f"返回数据过小（{len(data)} bytes），可能不是有效图片")

    # 验证文件头，确定真实格式
    header = data[:4]
    if header == PNG_HEADER:
        ext = ".png"
    elif header == JPEG_HEADER:
        ext = ".jpg"
    else:
        raise RuntimeError(
            f"文件头异常: {list(header)}，非 PNG/JPEG 格式"
        )

    # 检测是否命中 CDN 占位图缓存
    md5 = hashlib.md5(data).hexdigest()
    if md5 == PLACEHOLDER_MD5:
        raise RuntimeError(
            "API 返回了 CDN 缓存的固定占位图（MD5 匹配 19a0b822...），"
            "而非按 prompt 生成的图片。这是 CDN 层面的缓存问题，"
            "需服务端添加 Cache-Control: no-store 响应头解决。"
        )

    out = Path(output_path)
    # 根据真实格式调整扩展名
    if out.suffix.lower() != ext:
        out = out.with_suffix(ext)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    print(f"封面已生成: {out} ({len(data)} bytes, {ext[1:].upper()}, MD5={md5[:8]})")
    return out


if __name__ == "__main__":
    # 示例：具体、可视化的画面描述，不含中文文字
    sample_prompt = (
        "A lone traveler walking up a winding mountain path at golden hour, "
        "warm sunlight, mist in valley, cinematic composition, photorealistic"
    )
    output_dir = Path(__file__).resolve().parent.parent / "output"
    generate_cover(
        prompt=sample_prompt,
        output_path=str(output_dir / "cover.jpg"),
    )
