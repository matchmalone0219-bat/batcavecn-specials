"""Dark Deco ornaments for the TAS site: original line work, a screen header band and a film strip."""
import json
import re

from render_common import ROOT, esc

# Each ornament is drawn on its own viewBox with 1px non-scaling strokes in currentColor.
DECO = {
    "rule": ("0 0 800 32", '<path d="M0 26H230V18H300V10H366M800 26H570V18H500V10H434"/><path d="M380 16L400 2L420 16L400 30Z"/><path d="M392 16L400 10L408 16L400 22Z"/>'),
    "spire": ("0 0 120 40", '<path d="M60 2V38M54 9V38M66 9V38M48 17V38M72 17V38M42 25V38M78 25V38M14 38H106"/>'),
    "diamond": ("0 0 12 12", '<path d="M6 1L11 6L6 11L1 6Z"/>'),
    "step": ("0 0 96 16", '<path d="M0 15H24V10H36V5H60V10H72V15H96"/><path d="M44 5V1H52V5"/>'),
}
TOKEN = re.compile(r'<i data-deco="([a-z]+)"(?: class="([^"]*)")?></i>')


def deco(name, cls=""):
    box, paths = DECO[name]
    return f'<svg class="deco deco-{name}{" " + cls if cls else ""}" viewBox="{box}" aria-hidden="true" focusable="false" preserveAspectRatio="xMidYMid meet">{paths}</svg>'


def token(name, cls=""):
    return f'<i data-deco="{name}"' + (f' class="{cls}"' if cls else "") + '></i>'


def expand(html):
    return TOKEN.sub(lambda m: deco(m.group(1), m.group(2) or ""), html)


HEAD_START = re.compile(r'^<(section|div) class="([^"]*)">')
CLOSING_P = re.compile(r'\s*<p class="(?:lead|fine)">.*?</p>', re.S)


def screen_head(body):
    """Wrap an inner page's breadcrumb, label, title and lead in a black screen band."""
    opening = HEAD_START.match(body)
    if not opening or "section" not in opening.group(2).split() or "<h1" not in body:
        return body
    start = opening.end()
    h1 = body.index("<h1", start)
    end = body.index("</h1>", h1) + 5
    wrapper = re.search(r'<div class="(?:archive-heading|detail-title)[^"]*">', body[start:h1])
    if wrapper:
        end = body.index("</div>", end) + 6
    else:
        while (more := CLOSING_P.match(body, end)):
            end = more.end()
    head = body[start:end]
    band = f'<div class="screen-head">{token("spire", "screen-spire")}{head}{token("rule", "screen-rule")}</div>'
    return body[:start] + band + body[end:]


def film_strip(item_id):
    """Three frames on a strip of film, with the image source kept under the strip."""
    frames = [a for a in json.loads((ROOT / "episode-media.json").read_text())["assets"] if a["item"] == item_id and a.get("role") == "frame"]
    if not frames:
        return ""
    cells = "".join(
        f'<li><a href="/assets/media/{esc(a["file"])}"><img src="/assets/media/{esc(a["file"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy" alt="{esc(a["alt"])}"></a><span>{esc(a["title"])}</span></li>'
        for a in frames
    )
    return f'<figure class="film-strip"><ol>{cells}</ol><figcaption>{esc(frames[0]["credit"])} <a href="{esc(frames[0]["sourcePage"])}">图片出处 ↗</a></figcaption></figure>'
