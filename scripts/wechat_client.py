"""
本质工坊 · 微信 API 客户端
基于 md2wechat-py 最新代码，自包含无外部依赖

功能：
- access_token 获取与缓存
- 素材上传（封面缩略图 / 正文图片）
- 草稿箱创建 / 列表 / 删除
- 已发布文章列表 / 正文拉取
- 配置文件读取（~/.config/essence-workshop/config.yaml）
- sandbox 测试号模式
"""

import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx


CONFIG_PATH = Path.home() / ".config" / "essence-workshop" / "config.yaml"

LEGACY_CONFIG_PATH = Path.home() / ".config" / "wechat-pub" / "config.yaml"


@dataclass
class WeChatConfig:
    app_id: str = ""
    app_secret: str = ""
    sandbox: bool = False


@dataclass
class UploadResult:
    media_id: str = ""
    url: str = ""


@dataclass
class DraftResult:
    media_id: str = ""


class WeChatClient:
    BASE_URL = "https://api.weixin.qq.com"
    SANDBOX_URL = "https://api.weixin.qq.com/sandbox"

    def __init__(self, config: WeChatConfig | dict | None = None,
                 app_id: str = "", app_secret: str = ""):
        if config is not None:
            if isinstance(config, dict):
                config = WeChatConfig(**config)
            self.app_id = config.app_id
            self.app_secret = config.app_secret
            self.sandbox = config.sandbox
        else:
            self.app_id = app_id
            self.app_secret = app_secret
            self.sandbox = False

        self._token = ""
        self._token_expires_at = 0

    @property
    def _base(self) -> str:
        return self.SANDBOX_URL if self.sandbox else self.BASE_URL

    def _load_config_from_file(self) -> None:
        if not self.app_id:
            self.app_id = os.environ.get("WECHAT_APP_ID", "")
        if not self.app_secret:
            self.app_secret = os.environ.get("WECHAT_APP_SECRET", "")
        if self.app_id and self.app_secret:
            return

        for cfg_path in [CONFIG_PATH, LEGACY_CONFIG_PATH]:
            if cfg_path.exists():
                try:
                    import yaml
                    with open(cfg_path, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    wechat = data.get("wechat", {})
                    if not self.app_id:
                        self.app_id = wechat.get("app_id", "")
                    if not self.app_secret:
                        self.app_secret = wechat.get("app_secret", "")
                    if self.app_id and self.app_secret:
                        return
                except Exception:
                    pass

    def is_configured(self) -> bool:
        if not self.app_id or not self.app_secret:
            self._load_config_from_file()
        return bool(self.app_id and self.app_secret)

    def get_access_token(self) -> str:
        if self._token and time.time() < self._token_expires_at:
            return self._token

        if not self.is_configured():
            raise RuntimeError(
                "微信凭证未配置。请设置环境变量 WECHAT_APP_ID / WECHAT_APP_SECRET，"
                "或创建配置文件 ~/.config/essence-workshop/config.yaml"
            )

        resp = httpx.get(
            f"{self._base}/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret,
            },
            timeout=10,
        )
        data = resp.json()

        if "access_token" not in data:
            errcode = data.get("errcode", -1)
            errmsg = data.get("errmsg", "unknown")
            raise RuntimeError(f"获取 access_token 失败: [{errcode}] {errmsg}")

        self._token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"] - 200
        return self._token

    def upload_image(self, file_path: str, image_type: str = "thumb") -> UploadResult:
        token = self.get_access_token()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")
        if path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError(f"图片超过 5MB 限制: {file_path}")

        with open(path, "rb") as f:
            resp = httpx.post(
                f"{self._base}/cgi-bin/material/add_material",
                params={"access_token": token, "type": image_type},
                files={"media": (path.name, f, "image/jpeg")},
                timeout=30,
            )

        data = resp.json()
        if "media_id" not in data:
            errcode = data.get("errcode", -1)
            errmsg = data.get("errmsg", "unknown")
            raise RuntimeError(f"上传图片失败: [{errcode}] {errmsg}")

        return UploadResult(
            media_id=data["media_id"],
            url=data.get("url", ""),
        )

    def upload_content_image(self, file_path: str) -> str:
        token = self.get_access_token()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")

        with open(path, "rb") as f:
            resp = httpx.post(
                f"{self._base}/cgi-bin/media/uploadimg",
                params={"access_token": token},
                files={"media": (path.name, f, "image/jpeg")},
                timeout=30,
            )

        data = resp.json()
        if "url" not in data:
            errcode = data.get("errcode", -1)
            errmsg = data.get("errmsg", "unknown")
            raise RuntimeError(f"上传正文图片失败: [{errcode}] {errmsg}")

        return data["url"]

    def create_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str = "",
        author: str = "",
        digest: str = "",
        show_cover_pic: int = 0,
    ) -> DraftResult:
        token = self.get_access_token()

        if len(title) > 64:
            raise ValueError(f"标题超过 64 字符限制（当前 {len(title)} 字符）")
        if len(content) > 20000:
            raise ValueError(f"正文超过 20000 字符限制（当前 {len(content)} 字符）")

        if not digest:
            plain = re.sub(r"<[^>]+>", "", content)
            digest = plain[:120].strip()

        article = {
            "title": title,
            "author": author or "",
            "digest": digest or "",
            "content": content,
            "show_cover_pic": show_cover_pic,
        }
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id

        resp = httpx.post(
            f"{self._base}/cgi-bin/draft/add",
            params={"access_token": token},
            json={"articles": [article]},
            timeout=15,
        )

        data = resp.json()
        if "media_id" not in data:
            errcode = data.get("errcode", -1)
            errmsg = data.get("errmsg", "unknown")
            raise RuntimeError(f"创建草稿失败: [{errcode}] {errmsg}")

        return DraftResult(media_id=data["media_id"])

    def list_drafts(self, offset: int = 0, count: int = 5) -> list[dict]:
        token = self.get_access_token()
        resp = httpx.post(
            f"{self._base}/cgi-bin/draft/batchget",
            params={"access_token": token},
            json={"offset": offset, "count": count, "no_content": 1},
            timeout=10,
        )
        return resp.json().get("item", [])

    def delete_draft(self, media_id: str) -> bool:
        token = self.get_access_token()
        resp = httpx.post(
            f"{self._base}/cgi-bin/draft/delete",
            params={"access_token": token},
            json={"media_id": media_id},
            timeout=10,
        )
        return resp.json().get("errcode", -1) == 0

    def list_published_articles(self, count: int = 10, offset: int = 0) -> list[dict]:
        token = self.get_access_token()

        resp = httpx.post(
            f"{self._base}/cgi-bin/freepublish/batchget",
            params={"access_token": token},
            json={"offset": offset, "count": count, "no_content": 1},
            timeout=15,
        )
        data = resp.json()

        if "item" in data:
            articles = []
            for item in data["item"]:
                news_item = item.get("content", {}).get("news_item", [])
                for article in news_item:
                    articles.append({
                        "media_id": item.get("article_id", ""),
                        "title": article.get("title", ""),
                        "author": article.get("author", ""),
                        "digest": article.get("digest", ""),
                        "url": article.get("url", ""),
                        "update_time": item.get("update_time", 0),
                    })
            return articles

        errcode = data.get("errcode", -1)
        if errcode == 48001:
            resp2 = httpx.post(
                f"{self._base}/cgi-bin/material/batchget_material",
                params={"access_token": token},
                json={"type": "news", "offset": offset, "count": count},
                timeout=15,
            )
            data2 = resp2.json()
            if "item" in data2:
                articles = []
                for item in data2["item"]:
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

            errcode2 = data2.get("errcode", -1)
            errmsg2 = data2.get("errmsg", "unknown")
            raise RuntimeError(f"获取文章列表失败(素材接口): [{errcode2}] {errmsg2}")

        errmsg = data.get("errmsg", "unknown")
        raise RuntimeError(f"获取文章列表失败: [{errcode}] {errmsg}")

    def get_article_content(self, article_id: str) -> list[dict]:
        token = self.get_access_token()

        resp = httpx.post(
            f"{self._base}/cgi-bin/freepublish/getarticle",
            params={"access_token": token},
            json={"article_id": article_id},
            timeout=15,
        )
        data = resp.json()

        if "news_item" in data:
            return data["news_item"]

        errcode = data.get("errcode", -1)
        if errcode == 48001:
            resp2 = httpx.post(
                f"{self._base}/cgi-bin/material/get_material",
                params={"access_token": token},
                json={"media_id": article_id},
                timeout=15,
            )
            data2 = resp2.json()
            if "news_item" in data2:
                return data2["news_item"]

            errcode2 = data2.get("errcode", -1)
            errmsg2 = data2.get("errmsg", "unknown")
            raise RuntimeError(f"获取文章内容失败(素材接口): [{errcode2}] {errmsg2}")

        errmsg = data.get("errmsg", "unknown")
        raise RuntimeError(f"获取文章内容失败: [{errcode}] {errmsg}")
