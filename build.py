"""Build the two local archive samples from one content file. No dependencies."""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "archive.json"
DIST = ROOT / "dist"


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


def validate(data):
    ids = [i["id"] for i in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["person"], data["capedCrusader"]]]
    assert len(ids) == len(set(ids)), "Duplicate archive ID"
    source_ids = [s["id"] for s in data["sources"]]
    assert len(source_ids) == len(set(source_ids)), "Duplicate source ID"
    for site in ("arkham", "tas"):
        for key in ("name", "english", "eyebrow", "title", "intro", "prologue", "conroyTitle", "conroyText"):
            assert isinstance(data["sites"][site][key], str) and data["sites"][site][key].strip()
    for item in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["person"], data["capedCrusader"]]:
        for key in ("id", "title", "original", "sources"):
            assert item[key], f'Missing {key}: {item["id"]}'
        assert set(item["sources"]) <= set(source_ids), "Unknown source"
        for section in item["sections"]:
            assert all(section[k] for k in ("id", "title", "body"))
        assert len({s["id"] for s in item["sections"]}) == len(item["sections"])
    for source in data["sources"]:
        assert source["url"].startswith("https://")
    assert data["person"]["id"] == "kevin-conroy"


def cards(items, catalog=False):
    rendered = []
    for item in items:
        title = item["original"].replace("Batman: ", "")
        fields = ""
        if catalog and item["site"] == "tas":
            fields = f'<p class="fine">指南编号 {esc(item["guideNumber"] or "待核")} · 日期 {esc(item["airDate"] or "待核")}<br>原始制作代码 / 地区 / 影音序号：待核</p>'
        rendered.append(f'<a class="card" id="{esc(item["id"])}" href="{route(item)}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">{esc(item["status"])} · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}</div></a>' if item["status"] == "详情样板" else f'<article class="card basic" id="{esc(item["id"])}"><div class="card-art art-{esc(item["id"])}" aria-hidden="true"><span>{esc(item["year"] or item.get("series", ""))}</span><strong>{esc(title)}</strong></div><div class="card-copy"><span class="label">基础条目 · {esc(item.get("series", "CORE GAME"))}</span><h3>{esc(item["title"])}</h3><p>{esc(item["summary"])}</p>{fields}<p class="fine">{esc(item["gaps"])}</p></div></article>')
    return "".join(rendered)


def sources(data, ids=None):
    rows = [s for s in data["sources"] if ids is None or s["id"] in ids]
    return '<div class="source-list">' + "".join(f'<article><span class="label">{esc(s["type"])} · 核查 {esc(s["checked"])}</span><h3><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></h3><p>{esc(s["scope"])}</p></article>' for s in rows) + '</div>'


def shell(data, site, title, body, active=""):
    info = data["sites"].get(site, {"name": "蝙蝠侠之声", "english": "A VOICE IN THE DARK"})
    nav = [("主菜单" if site == "arkham" else "首页", "/arkham/menu/" if site == "arkham" else f"/{site}/", "home"), ("作品档案" if site == "arkham" else "分集目录", f"/{site}/catalog/", "catalog"), ("蝙蝠侠之声", "/people/kevin-conroy/", "person"), ("资料来源", f"/{site}/sources/", "sources"), ("搜索", f"/{site}/search/", "search")] if site in data["sites"] else [("阿卡姆档案", "/arkham/", "arkham"), ("TAS 动画档案", "/tas/", "tas"), ("共同档案", "/people/kevin-conroy/", "person")]
    if site == "tas":
        nav.insert(2, ("披风斗士", "/tas/series/caped-crusader/", "caped"))
    if site in ("arkham", "tas"):
        nav.insert(-1, ("图片资料", f"/{site}/gallery/", "gallery"))
    nav_html = "".join(f'<a href="{url}" {"aria-current=page" if key == active else ""}>{label}</a>' for label, url, key in nav)
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(title)} · {esc(info["name"])} | Batman小站</title><link rel="stylesheet" href="/assets/style.css"><script src="/assets/app.js" defer></script></head><body class="{esc(site)}"><a class="skip" href="#main">跳到正文</a><header><a class="brand" href="/{site + "/" if site in data["sites"] else "people/kevin-conroy/"}"><span class="brand-symbol" aria-hidden="true">✦</span><span>{esc(info["english"])}<small>{esc(info["name"])}</small></span></a><nav aria-label="主导航">{nav_html}</nav><a class="back-site" href="https://www.batcavecn.com/">BATCAVECN ↗</a></header><main id="main">{body}</main><footer><div><p class="label">BATCAVECN SPECIAL ARCHIVES</p><p>{esc(info["name"])} · 非商业影迷资料库</p><p class="fine">本地建设样板 · 更新 {esc(data["updated"])} · 与 DC / Warner Bros. 无官方合作关系。</p></div><div class="footer-links"><a href="/arkham/">阿卡姆</a><a href="/tas/">TAS</a><a href="/people/kevin-conroy/">凯文·康罗伊</a><a href="/editor/" data-local-edit hidden>编辑文案</a></div></footer></body></html>'


def section_header(number, english, title, text=""):
    return f'<div class="section-head"><p class="label">{number} / {english}</p><h2>{esc(title)}</h2>{paragraphs(text)}</div>'


def home(data, site):
    info = data["sites"][site]
    items = data["games"] if site == "arkham" else data["episodes"]
    if site == "arkham":
        return arkham_screen(data)
    else:
        body = f'<section class="reel-cover"><div class="reel-frame"><p class="reel-overline">BATCAVECN PRESENTS</p><div class="reel-emblem" aria-hidden="true">✦</div><h1>BATMAN<small>THE ANIMATED ARCHIVE</small><span>蝙蝠侠 · 动画放映室</span></h1><p class="reel-quote">{esc(info["title"]).replace(chr(10), "<br>")}</p><div class="reel-rule"></div><p class="reel-intro">{esc(info["intro"])}</p><a class="reel-ticket" href="/tas/catalog/">入场 · 浏览分集节目单</a><p class="reel-caption">故事 / 美术 / 声音 / 创作</p></div></section>'
        body += f'<section class="section programme-intro"><p class="label">本期放映 / OPENING PROGRAMME</p><h2>一集动画，<br>一座小小的哥谭。</h2><p>{esc(info["prologue"])}</p></section>'
        body += '<section class="section programme"><div class="programme-heading"><h2>精选节目单</h2><p>BTAS / 选集样板</p></div>'
        for index, item in enumerate(items[:3]):
            tag = "a" if item["status"] == "详情样板" else "article"
            href = f' href="{route(item)}"' if tag == "a" else ""
            body += f'<{tag}{href} class="programme-row"><span class="programme-number">0{index + 1}</span><div class="programme-title"><p>{esc(item["original"])}</p><h3>{esc(item["title"])}</h3><span>{esc(item["nameNote"])}</span></div><div class="programme-description"><p>{esc(item["summary"])}</p><span>{"详情样板 · 可阅读" if tag == "a" else "基础条目 · 深度档案待补"}</span></div></{tag}>'
        body += '<p class="programme-footnote">这是一份策展选集，编号是本期节目位置，不能作为制作或首播顺序。<br>BTAS85条与TNBA24条基础目录分别编目；动画电影另列。</p></section>'
        modern = data["capedCrusader"]
        body += f'<section class="section"><p class="label">延续与再诠释 / MODERN GOTHAM</p><a class="route-card" href="{route(modern)}"><h2>{esc(modern["title"])}</h2><p>{esc(modern["summary"])}</p><span class="fine">系列概览 · 两季二十集节目单</span></a></section>'
        body += f'<section class="section"><a href="/people/kevin-conroy/#voice" class="radio-column"><div class="radio-mark" aria-hidden="true"><span>ON AIR</span><strong>KC</strong><small>1955—2022</small></div><div><p class="label">声音专栏 / THE VOICE BEHIND THE MASK</p><h2>{esc(info["conroyTitle"])}</h2><p>{esc(info["conroyText"])}</p><span>凯文·康罗伊 · 共同人物档案</span></div></a></section>'
        body += '<section class="section programme-tail"><a href="/tas/episodes/nothing-to-fear/"><p class="label">主题放映 / FEAR & WILL</p><h3>恐惧与意志</h3><p>从《Nothing to Fear》看面具下的坚定与脆弱。</p></a><a href="/tas/sources/"><p class="label">放映资料 / SOURCE NOTES</p><h3>从片尾到档案</h3><p>英文原名、署名、编号与出处，保持各自的资料口径。</p></a></section>'
    return shell(data, site, info["name"], body, "home")


def arkham_screen(data, menu=False):
    if menu:
        entries = [
            ("作品档案", "CORE GAMES", "/arkham/catalog/", "四部核心作品 · 按原作年份编目", "01"),
            ("开始阅读", "START READING", "/arkham/games/arkham-asylum/", "进入《阿卡姆疯人院》详情样板", "02"),
            ("蝙蝠侠之声", "KEVIN CONROY", "/people/kevin-conroy/", "动画与游戏之间，共同的声音", "KC"),
            ("搜索档案", "SEARCH", "/arkham/search/", "检索作品、人物与主题", "⌕"),
            ("资料来源", "SOURCE NOTES", "/arkham/sources/", "查看核查记录与资料缺口", "≡"),
            ("动画放映室", "TAS ARCHIVE", "/tas/", "进入另一座哥谭", "TAS"),
        ]
        tiles = "".join(f'<a class="menu-tile" href="{url}" data-title="{esc(title)}" data-description="{esc(desc)}"><span class="tile-icon" aria-hidden="true">{icon}</span><span>{esc(title)}</span><small>{english}</small></a>' for title, english, url, desc, icon in entries)
        body = f'<div class="game-menu"><p class="game-eyebrow">BATCAVECN / ARKHAM ARCHIVE</p><h1 id="menu-title">作品档案</h1><p id="menu-description" aria-live="polite">四部核心作品 · 按原作年份编目</p><nav class="menu-grid" aria-label="档案主菜单">{tiles}</nav><div class="game-controls"><a href="/arkham/"><kbd>Esc</kbd> 返回启动画面</a><span><kbd>↵</kbd> 进入 · 方向键选择</span></div></div>'
    else:
        body = '<div class="start-title"><p class="game-eyebrow">BATCAVECN PRESENTS</p><h1><span>BATMAN</span>ARKHAM<small>阿卡姆游戏档案</small></h1><a class="press-start" href="/arkham/menu/">点击进入<span>PRESS ENTER TO START</span></a><p class="start-note">作品 · 人物 · 哥谭的故事</p></div>'
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>阿卡姆档案 · {"主菜单" if menu else "启动画面"}</title><link rel="stylesheet" href="/assets/style.css"><script src="/assets/app.js" defer></script></head><body class="arkham game-screen {"menu-screen" if menu else "start-screen"}"><a class="skip" href="#main">跳到正文</a><div class="game-scene" aria-hidden="true"></div><div class="game-fog" aria-hidden="true"></div><div class="game-rain" aria-hidden="true"></div><main id="main">{body}</main><a class="screen-home" href="https://www.batcavecn.com/">BATCAVECN ↗</a><p class="screen-note">非商业影迷档案 · 建设样板</p></body></html>'


def actor_markup(item):
    actor = esc(item["actor"] or "待核")
    return f'<a href="{esc(item["actorLink"])}">{actor}</a>' if item["actorLink"] else actor


def episode_catalog(items):
    rows = []
    for item in sorted(items, key=lambda item: int(item["guideNumber"])):
        title = f'<strong>{esc(item["original"])}</strong>'
        if item["status"] == "详情样板":
            title = f'<a href="{route(item)}">{title}<span> · {esc(item["title"])}</span></a>'
        rows.append(f'<li id="{esc(item["id"])}"><span class="label">{esc(item["guideNumber"])}</span><div>{title}<p class="fine">{esc(item["airDate"])} · {esc(item["status"])} · {esc(item["nameNote"])}</p></div></li>')
    return '<ol class="episode-register" aria-label="分集基础目录">' + "".join(rows) + '</ol>'


def image_gallery(site, item_id=None):
    assets = json.loads((ROOT / "media.json").read_text())["assets"]
    assets = [a for a in assets if a["site"] == site and (item_id is None or a["item"] == item_id)]
    if not assets:
        return ""
    return '<div class="archive-gallery">' + ''.join(f'<figure><a href="/assets/media/{esc(a["file"])}"><img src="/assets/media/{esc(a["file"])}" width="{a["width"]}" height="{a["height"]}" loading="lazy" alt="{esc(a["alt"])}"></a><figcaption><strong>{esc(a["title"])}</strong><span>{esc(a["caption"])}</span><span>{esc(a["credit"])}</span><a href="{esc(a["sourcePage"])}">图片出处 ↗</a></figcaption></figure>' for a in assets) + '</div>'


def detail(data, item):
    site = item["site"]
    body = f'<div class="section"><a class="breadcrumb" href="/{site}/catalog/">← {"作品档案" if site == "arkham" else "分集目录"}</a><div class="detail-title"><p class="label">{"GAME DOSSIER" if site == "arkham" else "EPISODE DOSSIER"} / {esc(item["status"])}</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p><p class="fine">{esc(item["nameNote"])}</p></div>'
    if site == "arkham":
        fields = [("官方发售日", item["date"]), ("日期口径", item["dateNote"]), ("开发", item["developer"]), ("发行", item["publisher"]), ("原版平台", item["platforms"])]
    else:
        fields = [("所属系列", item["series"]), ("辅助指南编号", item["guideNumber"]), ("原始制作代码", item["productionCode"]), ("来源所载首播日", item["airDate"]), ("首播地区", item["airRegion"]), ("影音目录编号", item["mediaOrder"]), ("编剧", item["writer"]), ("导演", item["director"]), ("动画制作", item["animation"]), ("配乐", item["music"]), ("客串配音", item["guests"])]
    body += '<dl class="facts">' + "".join(f'<div><dt>{esc(key)}</dt><dd>{esc(value or "待核")}</dd></div>' for key, value in fields) + f'<div><dt>蝙蝠侠英语配音</dt><dd>{actor_markup(item)}</dd></div></dl>'
    body += '<nav class="chapter-nav" aria-label="档案章节">' + "".join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in item["sections"]) + '<a href="#sources">资料来源</a></nav>'
    body += '<div class="reading">' + "".join(f'<section id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</section>' for s in item["sections"])
    if item.get("related"):
        linked = [e for e in data["episodes"] if e["id"] in item["related"]]
        body += '<section><h2>同一双集故事</h2>' + ''.join(f'<a class="route-card" href="{route(e)}"><h3>{esc(e["title"])}</h3><p>{esc(e["original"])}</p></a>' for e in linked) + '</section>'
    gallery = image_gallery(site, item["id"])
    if gallery:
        body += '<section><h2>图片资料</h2>' + gallery + '</section>'
    body += f'<details class="spoiler"><summary>剧情与结局 · 含剧透，展开阅读</summary>{paragraphs(item["spoiler"])}</details>'
    if item["actorLink"]:
        body += '<section><h2>继续沿着声音阅读</h2><a class="route-card" href="/people/kevin-conroy/#works"><span class="label">共同演员 / 表演路线</span><h3>凯文·康罗伊：蝙蝠侠之声</h3><p>从这份作品档案回到共同人物档案，再走向另一站的已建作品。</p></a></section>'
    body += f'<section class="gaps"><h2>资料边界</h2><p>{esc(item["gaps"])}</p></section><section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></div>'
    return shell(data, site, item["title"], body, "catalog")


def caped_series(data):
    item = data["capedCrusader"]
    body = f'<section class="section"><a class="breadcrumb" href="/tas/">← 动画放映室</a><div class="detail-title"><p class="label">MODERN GOTHAM / 延续与再诠释</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p></div><dl class="facts"><div><dt>英语版蝙蝠侠配音</dt><dd>{actor_markup(item)}</dd></div><div><dt>第一季</dt><dd>10集 · 独立节目单</dd></div></dl><nav class="chapter-nav" aria-label="系列章节">' + ''.join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in item["sections"]) + '<a href="#programme">第一季节目单</a><a href="#programme-season2">第二季节目单</a><a href="#sources">资料来源</a></nav><div class="reading">'
    body += ''.join(f'<section id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</section>' for s in item["sections"])
    body += '<section id="programme"><h2>第一季节目单</h2><p>Prime Video显示顺序；英文原名，不作为制作代码。</p><ol class="episode-register" aria-label="披风斗士第一季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["episodes"]) + '</ol></section>'
    body += '<section id="programme-season2"><h2>第二季节目单</h2><p>Prime Video显示顺序；日期口径与第一季分别记录。</p><ol class="episode-register" aria-label="披风斗士第二季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["season2Episodes"]) + '</ol></section>'
    body += '<section><h2>图片资料</h2>' + image_gallery("tas", "caped-crusader") + '</section>'
    body += f'<section class="gaps"><h2>资料边界</h2><p>{esc(item["gaps"])}</p></section><section><a class="route-card" href="/tas/catalog/"><h3>回到经典TAS</h3><p>阅读BTAS分集目录，比较两座动画哥谭。</p></a></section><section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></section>'
    return shell(data, "tas", item["title"], body, "caped")


def person(data):
    p = data["person"]
    body = f'<section class="memorial-hero"><p class="label">BATCAVECN / SHARED CREATOR ARCHIVE</p><p class="original">{esc(p["original"])} · {esc(p["years"])}</p><h1>{esc(p["title"])}<span>{esc(p["subtitle"])}</span></h1><p class="lead">{esc(p["intro"])}</p><div class="memorial-links"><a href="/tas/">动画 / 声音的起点</a><a href="/arkham/">游戏 / 哥谭的回声</a></div></section><div class="section"><nav class="chapter-nav" aria-label="人物章节">' + "".join(f'<a href="#{s["id"]}">{esc(s["title"])}</a>' for s in p["sections"]) + '</nav><div class="reading">'
    for s in p["sections"]:
        body += f'<section id="{s["id"]}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}'
        if s["id"] == "works":
            linked = [i for i in data["games"] + data["episodes"] if i["actor"] == "Kevin Conroy" and i["status"] == "详情样板"]
            body += '<div class="grid routes">' + "".join(f'<a class="route-card" href="{route(i)}"><span class="label">{esc(i["site"].upper())} / {esc(i["year"])}</span><h3>{esc(i["original"])}</h3><p>{esc(i["title"])}</p></a>' for i in linked) + '</div>'
        body += '</section>'
    body += f'<section><h2>原始资料与延伸阅读</h2>{sources(data, p["sources"])}</section></div></div>'
    return shell(data, "shared", p["title"], body, "person")


def build(data=None):
    data = data or json.loads(CONTENT.read_text())
    validate(data)
    pages = {}
    for site in ("arkham", "tas"):
        info = data["sites"][site]
        pages[f"{site}/index.html"] = home(data, site)
        items = data["games"] if site == "arkham" else data["episodes"] + data["tnbaEpisodes"]
        note = "按原作年份排列；移植与合集不计为新故事。" if site == "arkham" else "BTAS85条基础目录与11篇详情样板；TNBA24条基础目录单独排列。按各自辅助指南编号排列，并非首播日期排序。电影另编。完整制作代码、首播地区、影音序号仍待核。"
        pages[f"{site}/catalog/index.html"] = shell(data, site, "作品档案" if site == "arkham" else "分集目录", f'<section class="section"><p class="label">ARCHIVE INDEX</p><h1>{"作品档案" if site == "arkham" else "分集目录"}</h1><p class="lead">{note}</p>{'<h2>BTAS · 85集</h2>' + episode_catalog(data["episodes"]) + '<h2>TNBA · 24集</h2>' + episode_catalog(data["tnbaEpisodes"]) if site == "tas" else chr(60) + 'div class="grid">' + cards(items, True) + '</div>'}</section>', "catalog")
        pages[f"{site}/sources/index.html"] = shell(data, site, "资料来源", f'<section class="section"><p class="label">SOURCES / EDITORIAL NOTES</p><h1>每条资料，都有来处。</h1><p class="lead">官方事实、辅助索引与本站评论分开记录。以下是本轮实际使用的资料，核查日期并不表示所有字段均已确认。</p>{sources(data, {sid for i in items + [data["person"]] + ([data["capedCrusader"]] if site == "tas" else []) for sid in i["sources"]})}</section>', "sources")
        pages[f"{site}/gallery/index.html"] = shell(data, site, "图片资料", '<section class="section"><p class="label">IMAGE ARCHIVE</p><h1>图片资料</h1><p class="lead">游戏截图、动画画面与官方宣传图，按作品分别记录。</p><p class="fine">图片保留原始比例与来源；版权归原权利人。当前收录素材不代表完整图库。</p>' + image_gallery(site) + '</section>', "gallery")
        pages[f"{site}/search/index.html"] = shell(data, site, "搜索档案", f'<section class="section"><p class="label">SEARCH / {esc(info["english"])}</p><h1>寻找一段故事。</h1><form id="search-form" class="search-form"><label for="query">集名、作品名、人物或主题</label><div><input id="query" name="q" type="search" placeholder="试试：康罗伊、稻草人、Nothing to Fear"><button class="button">搜索</button></div><label for="scope">检索范围</label><select id="scope"><option value="{site}">当前专题＋共同人物</option><option value="all">两个专题＋共同人物</option></select></form><p id="search-count" role="status"></p><div id="search-results" class="grid routes"></div></section>', "search")
        for item in items:
            if item["status"] == "详情样板":
                pages[route(item).strip("/") + "/index.html"] = detail(data, item)
    pages["tas/series/caped-crusader/index.html"] = caped_series(data)
    pages["arkham/menu/index.html"] = arkham_screen(data, True)
    pages["people/kevin-conroy/index.html"] = person(data)
    pages["index.html"] = shell(data, "shared", "两座哥谭", '<section class="section hub"><p class="label">BATCAVECN / SPECIAL ARCHIVES</p><h1>两座哥谭。<br>一段熟悉的声音。</h1><p class="lead">Batman小站 · 阿卡姆与TAS独立专题的本地样板。</p><div class="grid routes"><a class="route-card hub-arkham" href="/arkham/"><p class="label">INTERACTIVE GOTHAM</p><h2>阿卡姆档案</h2><p>游戏、人物与创作故事。</p></a><a class="route-card hub-tas" href="/tas/"><p class="label">ANIMATED GOTHAM</p><h2>TAS 动画档案</h2><p>分集、声音与动画艺术。</p></a></div></section>')
    pages["editor/index.html"] = shell(data, "shared", "编辑文案", '<section class="section editor"><p class="label">BATCAVECN / LOCAL EDITOR</p><h1>编辑文案</h1><p class="lead">选择条目，修改文字，预览后保存。页面样式单独保留；每次保存自动备份。</p><p id="editor-status" role="status">正在读取本地内容…</p><form id="editor-form"><label for="entry">选择页面或条目</label><select id="entry"></select><label for="field">选择文字字段</label><select id="field"></select><label for="text">正文</label><textarea id="text" rows="8" required></textarea><div class="editor-actions"><button class="button" type="submit">保存到本地文件</button><button type="button" id="reset-text">撤销未保存修改</button><a id="preview-link" href="/arkham/" target="_blank" rel="noopener">查看页面 ↗</a></div></form><section class="editor-preview"><h2>文字预览</h2><div id="text-preview"></div></section></section>')
    DIST.mkdir(exist_ok=True)
    for filename, body in pages.items():
        path = DIST / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    (DIST / "assets").mkdir(exist_ok=True)
    for filename in ("style.css", "app.js", "arkham-city-background.jpg"):
        shutil.copyfile(ROOT / filename, DIST / "assets" / filename)
    (DIST / "assets/media").mkdir(exist_ok=True)
    media = json.loads((ROOT / "media.json").read_text())
    for asset in media["assets"]:
        shutil.copyfile(ROOT / asset["file"], DIST / "assets/media" / asset["file"])
    (DIST / "content").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "media.json", DIST / "content/media.json")
    (DIST / "content/archive.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    index = [{"title": i["title"], "original": i["original"], "summary": i["summary"], "tags": i["tags"], "site": i["site"], "status": i["status"], "url": route(i)} for i in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["capedCrusader"]]]
    index.append({"title": data["person"]["title"], "original": data["person"]["original"], "summary": data["person"]["intro"], "tags": ["蝙蝠侠之声", "Kevin Conroy", "共同演员"], "site": "shared", "status": "共同档案样板", "url": "/people/kevin-conroy/"})
    (DIST / "content/search.json").write_text(json.dumps(index, ensure_ascii=False))
    print(f"Built {len(pages)} pages, {len(index)} searchable records")
    return pages


if __name__ == "__main__":
    build()
