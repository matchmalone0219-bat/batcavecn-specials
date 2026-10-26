"""Shared HTML fragments and archive routes; no build side effects."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def person_url(site, anchor="kevin-conroy"):
    """The Conroy feature lives in the shared archive; each site opens it on its own reading route."""
    route_query = f"?route={site}" if site in ("arkham", "tas") else ""
    return f"/{route_query}#{anchor}"


def esc(value):
    return html.escape(str(value), quote=True)


def route(item):
    if item["id"] == "caped-crusader":
        return "/tas/series/caped-crusader/"
    if item["status"] != "详情样板":
        return f'/{item["site"]}/catalog/#{item["id"]}'
    return f'/{item["site"]}/{"games" if item["site"] == "arkham" else "episodes"}/{item["id"]}/'


def paragraphs(text):
    return "".join(f"<p>{esc(p)}</p>" for p in text.split("\n") if p.strip())


def cards(items, catalog=False):
    rendered = []
    for item in items:
        title = item["original"].replace("Batman: ", "")
        fields = ""
        if catalog and item["site"] == "tas":
            fields = f'<p class="fine">指南编号 {esc(item["guideNumber"] or "待核")} · 日期 {esc(item["airDate"] or "待核")}</p>'
        rendered.append(f'<a class="card" id="{esc(item["id"])}" href="{route(item)}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">{"分集档案" if item["site"] == "tas" else "作品档案"} · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}</div></a>' if item["status"] == "详情样板" else f'<article class="card basic" id="{esc(item["id"])}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">基础条目 · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}</div></article>')
    return "".join(rendered)


def sources(data, ids=None):
    rows = [s for s in data["sources"] if ids is None or s["id"] in ids]
    return '<div class="source-list">' + "".join(f'<article><span class="label">{esc(s["type"])}</span><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3><p>{esc(s["scope"])}</p></article>' for s in rows) + '</div>'


def section_header(number, english, title, text=""):
    return f'<div class="section-head"><p class="label">{number} / {english}</p><h2>{esc(title)}</h2>{paragraphs(text)}</div>'


def actor_markup(item):
    actor = esc(item["actor"] or "待核")
    link = item["actorLink"]
    if link == "/people/kevin-conroy/":
        link = person_url(item["site"])
    return f'<a href="{esc(link)}">{actor}</a>' if link else actor


def episode_credits():
    path = ROOT / "episode-credits.json"
    return json.loads(path.read_text()) if path.exists() else {"episodes": {}}


def credit_options(credits, key, minimum=1):
    counts = {}
    for record in credits.values():
        values = record[key] if isinstance(record[key], list) else [record[key]]
        for value in values:
            counts[value] = counts.get(value, 0) + 1
    ranked = sorted((item for item in counts.items() if item[1] >= minimum), key=lambda item: (-item[1], item[0]))
    return "".join(f'<option value="{esc(name)}">{esc(name)} · {count}集</option>' for name, count in ranked)


def title_cards():
    return {a["item"]: a for a in json.loads((ROOT / "episode-media.json").read_text())["assets"] if a.get("role") == "title-card"}


def episode_catalog(items, credits=None):
    credits = credits or {}
    cards = title_cards()
    rows = []
    for item in sorted(items, key=lambda item: int(item["guideNumber"])):
        guided = item["status"] == "详情样板"
        record = credits.get(item["id"])
        title = f'<strong>{esc(item["original"])}</strong>'
        if guided:
            title += f'<span> · {esc(item["title"])}</span>'
        credit_line = ""
        attributes = ""
        query = item["original"] + " " + item["title"] + " " + item["guideNumber"]
        if record:
            parts = [("编剧", record["writer"]), ("导演", record["director"]), ("动画", record["studio"])]
            credit_line = '<p class="episode-credits">' + " · ".join(f'<span>{label}&nbsp;{esc(value)}</span>' for label, value in parts if value) + "</p>"
            if record["villains"]:
                credit_line += '<p class="episode-villains">' + "".join(f"<span>{esc(name)}</span>" for name in record["villains"]) + "</p>"
            attributes = "".join(f' data-{key}="{esc("|".join(record[key]) if isinstance(record[key], list) else record[key])}"' for key in ("villains", "writers", "directors", "studio"))
            query += " " + " ".join(record["writers"] + record["directors"] + record["villains"] + [record["studio"]])
        card = cards.get(item["id"]) if guided else None
        thumb = f'<img class="episode-thumb" src="/assets/media/{esc(card["file"])}" width="{card["width"]}" height="{card["height"]}" alt="" loading="lazy">' if card else ""
        contents = f'<span class="label">{esc(item["guideNumber"])}</span>{thumb}<div>{title}<p class="fine">{esc(item["airDate"])} · {"分集导读" if guided else "分集条目"} · {esc(item["nameNote"])}</p>{credit_line}</div>'
        if guided:
            contents = f'<a class="episode-row-link" href="{route(item)}">{contents}</a>'
        card_attribute = f' data-card="/assets/media/{esc(card["file"])}"' if card else ""
        rows.append(f'<li id="{esc(item["id"])}"{' class="has-card"' if card else ""} data-episode data-series="{esc(item["series"])}" data-guided="{str(guided).lower()}"{card_attribute}{attributes} data-query="{esc(query)}">{contents}</li>')
    return '<ol class="episode-register" aria-label="分集基础目录">' + "".join(rows) + '</ol>'


def episode_runs(series, items):
    ordered = sorted(items, key=lambda item: int(item["guideNumber"]))
    if series != "BTAS":
        return [("全季", ordered)]
    return [("首轮播出", [i for i in ordered if int(i["guideNumber"]) <= 65]), ("The Adventures of Batman & Robin", [i for i in ordered if int(i["guideNumber"]) > 65])]


def episode_run(number, name, items, credits):
    dates = sorted(item["airDate"] for item in items)
    head = f'<div class="run-head"><span class="run-plate">{number:02d}</span><div><h3>{esc(name)}</h3><p>{esc(items[0]["guideNumber"])}—{esc(items[-1]["guideNumber"])} · {len(items)}集 · 首播 {esc(dates[0])} — {esc(dates[-1])}</p></div></div>'
    return f'<div class="episode-run" data-episode-run>{head}{episode_catalog(items, credits)}</div>'


def air_years(items):
    counts = {}
    for item in items:
        counts[item["airDate"][:4]] = counts.get(item["airDate"][:4], 0) + 1
    peak = max(counts.values())
    bars = "".join(f'<li><span class="air-bar" style="--h:{round(count / peak * 100)}%"></span><strong>{count}</strong><span>{year}</span></li>' for year, count in sorted(counts.items()))
    return f'<figure class="air-years"><figcaption>首播年份</figcaption><ol>{bars}</ol></figure>'


def tas_catalog(data):
    doc = episode_credits()
    credits = doc["episodes"]
    selects = (("episode-villain", "villains", "反派", "全部反派", 1), ("episode-writer", "writers", "编剧", "全部编剧", 2), ("episode-director", "directors", "导演", "全部导演", 1), ("episode-studio", "studio", "动画制作", "全部工作室", 1))
    credit_filters = '<fieldset class="episode-credit-filter"><legend>按反派与主创筛选 · BTAS</legend>' + "".join(f'<div><label for="{field}">{label}</label><select id="{field}" data-credit="{key}"><option value="all">{empty}</option>{credit_options(credits, key, minimum)}</select></div>' for field, key, label, empty, minimum in selects) + '</fieldset>' if credits else ""
    filters = f'<form id="episode-filter" class="episode-filter" hidden role="search" aria-label="筛选分集目录"><div><label for="episode-query">查找集名、编号或主创</label><input id="episode-query" type="search" placeholder="中文名、英文名、指南编号或人名"></div><div><label for="episode-series">所属系列</label><select id="episode-series"><option value="all">全部系列</option><option value="BTAS">BTAS · 85集</option><option value="TNBA">TNBA · 24集</option></select></div>{credit_filters}<label class="episode-guided"><input id="episode-guided" type="checkbox">仅看分集导读</label><button type="reset">重置筛选</button><p id="episode-count" role="status" aria-live="polite"></p></form><p id="episode-empty" hidden>没有匹配的分集。试试其他集名或重置筛选。</p>'
    registers = ''.join(f'<section data-episode-series="{series}"><h2 id="{series.lower()}">{series} · {len(items)}集</h2>{air_years(items)}{"".join(episode_run(number, name, run, credits if series == "BTAS" else None) for number, (name, run) in enumerate(episode_runs(series, items), 1))}</section>' for series, items in (("BTAS", data["episodes"]), ("TNBA", data["tnbaEpisodes"])))
    registers = f'<div class="episode-browser"><div class="episode-runs">{registers}</div><aside class="episode-preview" data-episode-preview hidden aria-live="polite"></aside></div>'
    return filters + '<nav class="episode-series-links" aria-label="系列目录"><a href="#btas">BTAS · 85集</a><a href="#tnba">TNBA · 24集</a></nav>' + registers


def image_gallery(site, item_id=None, role=None):
    assets = json.loads((ROOT / "media.json").read_text())["assets"]
    assets += json.loads((ROOT / "episode-media.json").read_text())["assets"]
    assets = [a for a in assets if a["site"] == site and (item_id is None or a["item"] == item_id) and (role is None or a.get("role", "frame") == role)]
    if not assets:
        return ""
    return '<div class="archive-gallery">' + ''.join(f'<figure><a href="/assets/media/{esc(a["file"])}"><img src="/assets/media/{esc(a["file"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy" alt="{esc(a["alt"])}"></a></figure>' for a in assets) + '</div>'
