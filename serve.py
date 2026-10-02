"""Loopback-only preview and small text editor; not a public CMS."""
import argparse
import hashlib
import json
import os
import secrets
import threading
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from build import CONTENT, DIST, ROOT, build, route, validate

TOKEN = secrets.token_urlsafe(32)
LOCK = threading.Lock()
LABELS = {
    "name": "专题名称", "english": "英文名称", "eyebrow": "页首小标题", "title": "标题",
    "intro": "导言", "prologue": "首页导读", "conroyTitle": "康罗伊板块标题",
    "conroyText": "康罗伊板块导读", "summary": "无剧透简介", "body": "段落正文",
    "subtitle": "副标题", "spoiler": "剧透折叠正文", "gaps": "资料缺口",
    "nameNote": "译名说明", "dateNote": "发售日期口径"
}


def editable(data):
    entries = []
    for site in ("arkham", "tas"):
        obj = data["sites"][site]
        fields = [{"label": LABELS[key], "path": ["sites", site, key]} for key in obj if key in LABELS]
        entries.append({"label": obj["name"] + " / 首页", "url": f"/{site}/", "fields": fields})
    for group in ("games", "episodes", "person", "capedCrusader"):
        rows = [data[group]] if group in ("person", "capedCrusader") else data[group]
        for index, row in enumerate(rows):
            prefix = [group] if group in ("person", "capedCrusader") else [group, index]
            fields = [{"label": LABELS[key], "path": prefix + [key]} for key in row if key in LABELS and isinstance(row[key], str)]
            for section_index, section in enumerate(row["sections"]):
                for key in ("title", "body"):
                    fields.append({"label": section["title"] + " / " + LABELS[key], "path": prefix + ["sections", section_index, key]})
            entries.append({"label": row["title"], "url": "/people/kevin-conroy/" if group == "person" else route(row), "fields": fields})
    return entries


def digest():
    return hashlib.sha256(CONTENT.read_bytes()).hexdigest()


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def reply(self, code, data):
        encoded = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def local_host(self):
        return self.headers.get("Host") in (f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}")

    def do_GET(self):
        if not self.local_host():
            return self.reply(403, {"error": "仅支持本机预览。"})
        if urlparse(self.path).path == "/api/editor":
            with LOCK:
                data = json.loads(CONTENT.read_text())
                self.reply(200, {"token": TOKEN, "version": digest(), "content": data, "entries": editable(data)})
        else:
            super().do_GET()

    def do_POST(self):
        origin = self.headers.get("Origin")
        expected = f'http://{self.headers.get("Host")}'
        if not self.local_host() or origin != expected or not secrets.compare_digest(self.headers.get("X-Editor-Token", ""), TOKEN):
            return self.reply(403, {"error": "编辑请求需要来自当前本地页面。"})
        if urlparse(self.path).path != "/api/editor":
            return self.reply(404, {"error": "无此接口。"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 100_000:
                return self.reply(400, {"error": "文字过长或请求为空。"})
            request = json.loads(self.rfile.read(length))
            with LOCK:
                if request["version"] != digest():
                    return self.reply(409, {"error": "文件已被其他窗口或外部修改。请保留当前文字，刷新编辑器后重新保存。"})
                data = json.loads(CONTENT.read_text())
                permitted = [f["path"] for e in editable(data) for f in e["fields"]]
                path, value = request["path"], request["value"]
                if path not in permitted or not isinstance(value, str) or not value.strip() or len(value) > 20000:
                    return self.reply(400, {"error": "只允许编辑已列出的非空文字字段。"})
                obj = data
                for key in path[:-1]:
                    obj = obj[key]
                obj[path[-1]] = value
                data["updated"] = datetime.now().strftime("%Y-%m-%d")
                validate(data)
                old = CONTENT.read_bytes()
                backups = ROOT / "backups"
                backups.mkdir(exist_ok=True)
                backup = backups / (datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json")
                backup.write_bytes(old)
                temporary = CONTENT.with_suffix(".tmp")
                temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                try:
                    build(data)
                    os.replace(temporary, CONTENT)
                except Exception:
                    temporary.unlink(missing_ok=True)
                    build(json.loads(old))
                    raise
                self.reply(200, {"backup": str(backup.relative_to(ROOT))})
        except (KeyError, TypeError, ValueError, AssertionError):
            self.reply(400, {"error": "内容校验未通过，原文件未覆盖。"})
        except Exception:
            self.reply(500, {"error": "保存失败，原文件保留；请检查本地服务。"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    build()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(DIST)))
    print(f"Local preview: http://127.0.0.1:{args.port}/", flush=True)
    server.serve_forever()
