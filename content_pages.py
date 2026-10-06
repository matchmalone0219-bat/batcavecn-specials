"""Home, work and creator pages from archive.json."""
from render_common import (esc, route, paragraphs, sources, actor_markup,
                           image_gallery, person_url)
from site_layout import shell
from arkham_ui import arkham_screen
from tas_pages import production_preview


def home(data, site):
    info = data["sites"][site]
    items = data["games"] if site == "arkham" else data["episodes"]
    if site == "arkham":
        return arkham_screen(data)
    else:
        body = f'<section class="reel-cover reel-art-cover cinema-cover"><div class="reel-frame reel-art-frame"><p class="reel-overline">BATCAVECN PRESENTS // DARK DECO</p><svg class="cinema-ornament" viewBox="0 0 800 32" aria-hidden="true"><path d="M0 26H230V18H300V10H366M800 26H570V18H500V10H434M380 16L400 2L420 16L400 30Z"/></svg><img class="reel-key-art" src="/assets/tas-home-title.jpg" width="1200" height="675" fetchpriority="high" alt="Batman: The Animated Series；黑色背景上的蝙蝠侠与红色圆形"><h1>蝙蝠侠 · 动画放映室</h1><p class="reel-quote">{esc(info["title"]).replace(chr(10), "<br>")}</p><div class="reel-rule"></div><p class="reel-intro">{esc(info["intro"])}</p><a class="reel-ticket" href="/tas/catalog/">入场 · 浏览分集节目单</a><p class="reel-caption">故事 / 美术 / 声音 / 创作</p></div></section>'
        body += '<section class="section cinema-features"><a class="cinema-feature" href="/tas/archive/"><img src="/assets/media/btas-ensemble.jpg" width="900" height="587" alt="经典TAS蝙蝠侠侧面画面" loading="lazy"><div><p class="label">走进档案馆 / BEHIND THE ANIMATION</p><h2>画稿、声音与故事的来处。</h2><p>制作与美术 · 角色配音 · 动画电影 · 漫画与出版 · 配乐档案</p></div></a><a class="cinema-feature cinema-collectibles" href="/tas/collectibles/"><img src="/assets/media/merch-mondo-redux-1.jpg" width="1200" height="1200" alt="Mondo Batman Redux人偶厂商宣传图" loading="lazy"><div><p class="label">屏幕之外 / COLLECTIBLES</p><h2>让动画线条，走进陈列柜。</h2><p>人偶与雕像 · 动画蝙蝠车 · 哥谭积木 · 单集衍生桌游</p></div></a></section>'
        body += f'<section class="section programme-intro"><p class="label">本期放映 / OPENING PROGRAMME</p><h2>一集动画，<br>一座小小的哥谭。</h2><p>{esc(info["prologue"])}</p></section>'
        body += '<section class="section programme"><div class="programme-heading"><h2>精选节目单</h2><p>BTAS / 精选篇目</p></div>'
        for index, item in enumerate(items[:3]):
            tag = "a" if item["status"] == "详情样板" else "article"
            href = f' href="{route(item)}"' if tag == "a" else ""
            body += f'<{tag}{href} class="programme-row"><span class="programme-number">0{index + 1}</span><div class="programme-title"><p>{esc(item["original"])}</p><h3>{esc(item["title"])}</h3><span>{esc(item["nameNote"])}</span></div><div class="programme-description"><p>{esc(item["summary"])}</p><span>{"分集导读" if tag == "a" else "分集条目"}</span></div></{tag}>'
        body += '<p class="programme-footnote">按本期放映次序浏览精选篇目。<br>BTAS85条与TNBA24条基础目录分别编目；动画电影另列。</p></section>'
        body += '<section class="section cinema-folio"><div class="programme-heading"><h2>翻开制作图册</h2><p>MODEL / STORYBOARD</p></div><p class="folio-intro">从角色的转身，到镜头的运动。两页制作扫描，呈现角色设定与实验室分镜。</p>' + production_preview() + '</section>'
        modern = data["capedCrusader"]
        body += f'<section class="section"><p class="label">延续与再诠释 / MODERN GOTHAM</p><a class="route-card" href="{route(modern)}"><h2>{esc(modern["title"])}</h2><p>{esc(modern["summary"])}</p><span class="fine">系列概览 · 两季二十集节目单</span></a></section>'
        body += f'<section class="section"><a href="/people/kevin-conroy/#voice" class="radio-column"><div class="radio-mark" aria-hidden="true"><span>ON AIR</span><strong>KC</strong><small>1955—2022</small></div><div><p class="label">声音专栏 / THE VOICE BEHIND THE MASK</p><h2>{esc(info["conroyTitle"])}</h2><p>{esc(info["conroyText"])}</p><span>凯文·康罗伊 · 共同人物档案</span></div></a></section>'
        body += '<section class="section programme-tail"><a href="/tas/episodes/nothing-to-fear/"><p class="label">主题放映 / FEAR & WILL</p><h3>恐惧与意志</h3><p>从《Nothing to Fear》看面具下的坚定与脆弱。</p></a><a href="/tas/sources/"><p class="label">放映资料 / SOURCE NOTES</p><h3>从片尾到档案</h3><p>查阅英文原名、制作署名与分集资料出处。</p></a></section>'
    return shell(data, site, "动画放映室", body, "home")


def detail(data, item):
    site = item["site"]
    body = f'<div class="section{" episode-feature" if site == "tas" else ""}"><a class="breadcrumb" href="/{site}/catalog/">← {"作品档案" if site == "arkham" else "分集目录"}</a><div class="detail-title"><p class="label">{"GAME DOSSIER" if site == "arkham" else "EPISODE DOSSIER"} / {"作品档案" if site == "arkham" else "分集档案"}</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p><p class="fine">{esc(item["nameNote"])}</p></div>'
    title_card = image_gallery(site, item["id"], "title-card")
    if title_card:
        body += '<div class="episode-title-card">' + title_card + '</div>'
    if site == "arkham":
        fields = [("官方发售日", item["date"]), ("日期口径", item["dateNote"]), ("开发", item["developer"]), ("发行", item["publisher"]), ("原版平台", item["platforms"])]
    else:
        fields = [("所属系列", item["series"]), ("辅助指南编号", item["guideNumber"]), ("原始制作代码", item["productionCode"]), ("来源所载首播日", item["airDate"]), ("首播地区", item["airRegion"]), ("影音目录编号", item["mediaOrder"]), ("编剧", item["writer"]), ("导演", item["director"]), ("动画制作", item["animation"]), ("配乐", item["music"]), ("客串配音", item["guests"])]
    voice = f'<div><dt>蝙蝠侠英语配音</dt><dd>{actor_markup(item)}</dd></div>' if item["actor"] else ''
    body += '<dl class="facts">' + "".join(f'<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>' for key, value in fields if value) + voice + '</dl>'
    body += '<nav class="chapter-nav" aria-label="档案章节">' + "".join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in item["sections"]) + '<a href="#sources">资料来源</a></nav>'
    body += '<div class="reading">' + "".join(f'<section id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</section>' for s in item["sections"])
    if item.get("related"):
        linked = [e for e in data["episodes"] if e["id"] in item["related"]]
        body += '<section><h2>同一双集故事</h2>' + ''.join(f'<a class="route-card" href="{route(e)}"><h3>{esc(e["title"])}</h3><p>{esc(e["original"])}</p></a>' for e in linked) + '</section>'
    if item.get("readingLinks"):
        body += '<section><h2>关联阅读</h2>' + ''.join(f'<a class="route-card" href="{esc(link["url"])}"><h3>{esc(link["title"])}</h3></a>' for link in item["readingLinks"]) + '</section>'
    gallery = image_gallery(site, item["id"], "frame")
    if gallery:
        body += '<section><h2>图片资料</h2>' + gallery + '</section>'
    if item["spoiler"]:
        body += f'<details class="spoiler"><summary>剧情与结局 · 含剧透，展开阅读</summary>{paragraphs(item["spoiler"])}</details>'
    if item["actorLink"]:
        continuation = "继续阅读相关的作品与表演资料。" if site == "arkham" else "继续阅读动画与游戏中的表演。"
        body += f'<section><h2>继续沿着声音阅读</h2><a class="route-card" href="{person_url(site)}#works"><span class="label">共同演员 / 表演路线</span><h3>凯文·康罗伊：蝙蝠侠之声</h3><p>从这份作品档案回到共同人物档案，{continuation}</p></a></section>'
    body += f'<section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></div>'
    return shell(data, site, item["title"], body, "catalog")


def caped_series(data):
    item = data["capedCrusader"]
    body = f'<section class="section"><a class="breadcrumb" href="/tas/">← 动画放映室</a><div class="detail-title"><p class="label">MODERN GOTHAM / 延续与再诠释</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p></div><dl class="facts"><div><dt>英语版蝙蝠侠配音</dt><dd>{actor_markup(item)}</dd></div><div><dt>第一季</dt><dd>10集 · 独立节目单</dd></div></dl><nav class="chapter-nav" aria-label="系列章节">' + ''.join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in item["sections"]) + '<a href="#programme">第一季节目单</a><a href="#programme-season2">第二季节目单</a><a href="#sources">资料来源</a></nav><div class="reading">'
    body += ''.join(f'<section id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</section>' for s in item["sections"])
    body += '<section id="programme"><h2>第一季节目单</h2><p>按Prime Video节目单顺序排列英文原名。</p><ol class="episode-register" aria-label="披风斗士第一季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["episodes"]) + '</ol></section>'
    body += '<section id="programme-season2"><h2>第二季节目单</h2><p>按Prime Video第二季节目单顺序排列英文原名。</p><ol class="episode-register" aria-label="披风斗士第二季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["season2Episodes"]) + '</ol></section>'
    body += '<section><h2>图片资料</h2>' + image_gallery("tas", "caped-crusader") + '</section>'
    body += f'<section><a class="route-card" href="/tas/catalog/"><h3>回到经典TAS</h3><p>阅读BTAS分集目录，比较两座动画哥谭。</p></a></section><section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></section>'
    return shell(data, "tas", item["title"], body, "caped")


def person(data, site="shared"):
    p = data["person"]
    memorial_links = '<a href="/arkham/menu/">返回Protocol Arkham</a>' if site == "arkham" else '<a href="/tas/">动画 / 声音的起点</a><a href="/arkham/">游戏 / 哥谭的回声</a>'
    body = f'<section class="memorial-hero"><p class="label">BATCAVECN / SHARED CREATOR ARCHIVE</p><p class="original">{esc(p["original"])} · {esc(p["years"])}</p><h1>{esc(p["title"])}<span>{esc(p["subtitle"])}</span></h1><p class="lead">{esc(p["intro"])}</p><div class="memorial-links">{memorial_links}</div></section><div class="section"><nav class="chapter-nav" aria-label="人物章节">' + "".join(f'<a href="#{s["id"]}">{esc(s["title"])}</a>' for s in p["sections"]) + '</nav><div class="reading">'
    for s in p["sections"]:
        body += f'<section id="{s["id"]}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}'
        if s["id"] == "works":
            linked = [i for i in data["games"] + data["episodes"] if i["actor"] == "Kevin Conroy" and i["status"] == "详情样板"]
            if site == "arkham":
                linked = [i for i in linked if i["site"] == "arkham"]
            body += '<div class="grid routes">' + "".join(f'<a class="route-card" href="{route(i)}"><span class="label">{esc(data["sites"][i["site"]]["english"])} / {esc(i["year"])}</span><h3>{esc(i["original"])}</h3><p>{esc(i["title"])}</p></a>' for i in linked) + '</div>'
        body += '</section>'
    body += f'<section><h2>原始资料与延伸阅读</h2>{sources(data, p["sources"])}</section></div></div>'
    return shell(data, site, p["title"], body, "person")
