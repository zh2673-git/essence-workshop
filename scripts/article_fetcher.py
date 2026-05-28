"""
本质工坊 · 公众号文章拉取
支持两种方式：
  1. API方式：从自己公众号拉取已发布文章列表，选择后获取正文
  2. 链接方式：直接给公众号文章URL，抓取正文

用法:
  python article_fetcher.py --list                    列出最近文章
  python article_fetcher.py --list --count 20         列出最近20篇
  python article_fetcher.py --media-id XXXXX          按media_id拉取正文
  python article_fetcher.py --url https://mp.weixin.qq.com/s/xxx  按链接抓取
  python article_fetcher.py --media-id XXXXX --save output/article.md  保存为文件
"""

import argparse
import json
import os
import re
import sys
import tempfile


def get_wechat_client():
    try:
        from wechat_pub.wechat import WeChatClient
        client = WeChatClient()
        if not client.is_configured():
            print("ERROR: wechat-pub not configured. Run: wechat-pub config init")
            sys.exit(1)
        return client
    except ImportError:
        print("ERROR: wechat-pub not installed. Run: pip install wechat-pub")
        sys.exit(1)


def get_access_token():
    client = get_wechat_client()
    return client.get_access_token()


def list_published_articles(count=10, offset=0):
    import httpx

    token = get_access_token()
    resp = httpx.post(
        "https://api.weixin.qq.com/cgi-bin/material/batchget_material",
        params={"access_token": token},
        json={"type": "news", "offset": offset, "count": count},
        timeout=15,
    )
    data = resp.json()

    if "item" not in data:
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "unknown")
        print(f"ERROR: [{errcode}] {errmsg}")
        return []

    articles = []
    for item in data["item"]:
        for article in item.get("content", {}).get("news_item", []):
            articles.append({
                "media_id": item.get("media_id", ""),
                "title": article.get("title", ""),
                "author": article.get("author", ""),
                "digest": article.get("digest", ""),
                "url": article.get("url", ""),
                "update_time": item.get("update_time", 0),
            })

    return articles


def get_article_content(media_id):
    import httpx

    token = get_access_token()
    resp = httpx.post(
        "https://api.weixin.qq.com/cgi-bin/material/get_material",
        params={"access_token": token},
        json={"media_id": media_id},
        timeout=15,
    )
    data = resp.json()

    if "news_item" not in data:
        errcode = data.get("errcode", -1)
        errmsg = data.get("errmsg", "unknown")
        print(f"ERROR: [{errcode}] {errmsg}")
        return None

    articles = []
    for article in data["news_item"]:
        articles.append({
            "title": article.get("title", ""),
            "author": article.get("author", ""),
            "digest": article.get("digest", ""),
            "content": article.get("content", ""),
            "url": article.get("url", ""),
        })

    return articles


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
