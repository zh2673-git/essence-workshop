"""
本质工坊 · 公众号文章拉取
支持两种方式：
  1. URL方式（默认推荐）：直接给公众号文章URL，抓取正文
     - 适用于任何公众号的已发布文章
     - 无权限要求，稳定可靠
  2. API方式（受权限制约）：从自己公众号拉取已发布文章列表
     - 需要认证服务号才能使用 freepublish 接口
     - 订阅号/未认证服务号只能使用 material 接口（仅含API上传的素材）
     - 需要配置 ~/.config/essence-workshop/config.yaml（AppID/AppSecret）

API权限制约说明：
  - freepublish/batchget（已发布文章列表）：需认证服务号，否则返回 48001
  - material/batchget_material（素材管理）：基础权限，但只能看到API上传的素材
  - 后台直接发布的文章不在素材管理中，只能通过URL方式获取

用法:
  python article_fetcher.py --url https://mp.weixin.qq.com/s/xxx  按链接抓取（推荐）
  python article_fetcher.py --list                                列出已发布文章（需API权限）
  python article_fetcher.py --list --count 20                     列出最近20篇
  python article_fetcher.py --media-id XXXXX                      按media_id拉取正文（需API权限）
  python article_fetcher.py --url https://mp.weixin.qq.com/s/xxx --save output/article.md  保存为文件
"""

import argparse
import json
import os
import re
import sys
import tempfile


def get_wechat_client():
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipelines", "wechat"))
        from client import WeChatClient
        client = WeChatClient()
        if not client.is_configured():
            print("ERROR: WeChat not configured. Create ~/.config/essence-workshop/config.yaml")
            sys.exit(1)
        return client
    except ImportError:
        print("ERROR: wechat client.py not found in scripts/pipelines/wechat/")
        sys.exit(1)


def get_access_token():
    client = get_wechat_client()
    return client.get_access_token()


def list_published_articles(count=10, offset=0):
    client = get_wechat_client()
    return client.list_published_articles(count=count, offset=offset)


def get_article_content(media_id):
    client = get_wechat_client()
    return client.get_article_content(media_id)


def html_to_markdown(html):
    if not html:
        return ""

    text = html

    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', text, flags=re.DOTALL)

    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)

    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', text, flags=re.DOTALL)

    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)

    text = re.sub(r'<img[^>]+alt="([^"]*)"[^>]*>', r'![\1]', text)
    text = re.sub(r'<img[^>]+>', '', text)

    text = re.sub(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<hr\s*/?>', '\n---\n', text)

    text = re.sub(r'<section[^>]*>', '', text)
    text = re.sub(r'</section>', '', text)
    text = re.sub(r'<span[^>]*>', '', text)
    text = re.sub(r'</span>', '', text)
    text = re.sub(r'<div[^>]*>', '', text)
    text = re.sub(r'</div>', '', text)
    text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)

    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def fetch_article_by_url(url):
    import httpx

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30,
                         headers={
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                         })
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: Failed to fetch URL: {e}")
        return None

    html = resp.text

    title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    author_match = re.search(r'class="rich_media_meta_nickname"[^>]*>.*?<a[^>]*>(.*?)</a>', html, re.DOTALL)
    author = author_match.group(1).strip() if author_match else ""

    content_match = re.search(r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL)

    content_html = content_match.group(1) if content_match else ""

    if not title and not content_html:
        print("ERROR: Could not extract article content from URL")
        return None

    markdown = html_to_markdown(content_html)

    return {
        "title": title,
        "author": author,
        "content_html": content_html,
        "content_markdown": markdown,
        "url": url,
    }


def validate_article(article_data):
    warnings = []
    title = article_data.get("title", "")
    markdown = article_data.get("content_markdown", "")

    if not title:
        warnings.append("标题为空，抓取可能失败")
    if len(markdown) < 500:
        warnings.append(f"正文仅 {len(markdown)} 字符，抓取内容可能不完整")
    h2_count = len(re.findall(r'^##\s+', markdown, re.MULTILINE))
    if h2_count < 2:
        warnings.append(f"仅 {h2_count} 个二级标题，Markdown 结构可能丢失")

    for w in warnings:
        print(f"  WARNING: {w}")

    return len(warnings) == 0, warnings


def save_article(article_data, output_path):
    title = article_data.get("title", "Untitled")
    author = article_data.get("author", "")
    markdown = article_data.get("content_markdown", "")
    url = article_data.get("url", "")

    content = f"# {title}\n\n"
    if author:
        content += f"作者: {author}\n\n"
    if url:
        content += f"原文链接: {url}\n\n"
    content += "---\n\n"
    content += markdown

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Article saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 公众号文章拉取")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="列出已发布文章")
    group.add_argument("--media-id", type=str, help="按media_id拉取文章正文")
    group.add_argument("--url", type=str, help="按公众号文章URL抓取正文")

    parser.add_argument("--count", type=int, default=10, help="列出文章数量（默认10）")
    parser.add_argument("--offset", type=int, default=0, help="列表偏移量")
    parser.add_argument("--save", type=str, default="", help="保存为Markdown文件路径")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    if args.list:
        articles = list_published_articles(count=args.count, offset=args.offset)
        if not articles:
            print("No articles found.")
            return

        if args.json:
            print(json.dumps(articles, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  已发布文章列表 (共 {len(articles)} 篇)")
            print(f"{'='*60}\n")
            for i, a in enumerate(articles, 1):
                print(f"  {i}. {a['title']}")
                print(f"     media_id: {a['media_id']}")
                if a['digest']:
                    print(f"     摘要: {a['digest'][:60]}...")
                print()

    elif args.media_id:
        articles = get_article_content(args.media_id)
        if not articles:
            print("Article not found.")
            return

        for i, a in enumerate(articles):
            markdown = html_to_markdown(a.get("content", ""))
            a["content_markdown"] = markdown

        if args.json:
            output = []
            for a in articles:
                output.append({
                    "title": a["title"],
                    "author": a["author"],
                    "digest": a["digest"],
                    "content_markdown": a["content_markdown"],
                    "url": a.get("url", ""),
                })
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            for i, a in enumerate(articles):
                print(f"\n{'='*60}")
                print(f"  文章 {i+1}: {a['title']}")
                print(f"  作者: {a['author']}")
                print(f"{'='*60}\n")
                print(a["content_markdown"][:2000])
                if len(a["content_markdown"]) > 2000:
                    print(f"\n... (共 {len(a['content_markdown'])} 字)")

        if args.save:
            save_article(articles[0], args.save)

    elif args.url:
        article = fetch_article_by_url(args.url)
        if not article:
            return

        validate_article(article)

        if args.json:
            print(json.dumps(article, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  {article['title']}")
            print(f"  作者: {article['author']}")
            print(f"{'='*60}\n")
            print(article["content_markdown"][:2000])
            if len(article["content_markdown"]) > 2000:
                print(f"\n... (共 {len(article['content_markdown'])} 字)")

        if args.save:
            save_article(article, args.save)


if __name__ == "__main__":
    main()
