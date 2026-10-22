"""Home, work and creator pages from archive.json."""
import json

from render_common import (ROOT, esc, route, paragraphs, sources, actor_markup,
                           image_gallery, person_url)
from site_layout import shell
from arkham_ui import arkham_screen
from tas_pages import production_preview
from tas_deco import film_strip


def home(data, site):
    info = data["sites"][site]
    items = data["games"] if site == "arkham" else data["episodes"]
    if site == "arkham":
        return arkham_screen(data)
    else:
        body = f'<section class="reel-cover reel-art-cover cinema-cover"><div class="reel-frame reel-art-frame"><p class="reel-overline">BATCAVECN PRESENTS // DARK DECO</p><svg class="cinema-ornament" viewBox="0 0 800 32" aria-hidden="true"><path d="M0 26H230V18H300V10H366M800 26H570V18H500V10H434M380 16L400 2L420 16L400 30Z"/></svg><img class="reel-key-art" src="/assets/tas-home-title.jpg" width="1200" height="675" fetchpriority="high" alt="Batman: The Animated Series；黑色背景上的蝙蝠侠与红色圆形"><div class="cinema-copy"><h1>蝙蝠侠 · 动画放映室</h1><p class="reel-quote">{esc(info["title"]).replace(chr(10), "<br>")}</p><div class="reel-rule"></div><p class="reel-intro">{esc(info["intro"])}</p><a class="reel-ticket" href="/tas/catalog/">入场 · 浏览分集节目单</a><p class="reel-caption">故事 / 美术 / 声音 / 创作</p></div></div></section>'
        body += '<section class="section cinema-features"><a class="cinema-feature" href="/tas/archive/"><img src="/assets/media/btas-ensemble.jpg" width="900" height="587" alt="经典TAS蝙蝠侠侧面画面" loading="lazy"><div><p class="label">动画档案馆 / BEHIND THE ANIMATION</p><h2>画稿、声音与经典篇章的诞生始末。</h2><p>制作与美术 · 角色配音 · 动画电影 · 漫画与出版 · 配乐档案</p></div></a><a class="cinema-feature cinema-collectibles" href="/tas/collectibles/"><img src="/assets/media/merch-mondo-redux-1.jpg" width="1200" height="1200" alt="Mondo Batman Redux人偶厂商宣传图" loading="lazy"><div><p class="label">屏幕之外 / COLLECTIBLES</p><h2>定格光影：经典造物与实体收藏。</h2><p>人偶与雕像 · 动画蝙蝠车 · 哥谭积木 · 单集衍生桌游</p></div></a></section>'
        body += f'<section class="section programme-intro"><p class="label">本期放映 / OPENING PROGRAMME</p><h2>一卷光影胶片，<br>照见整座哥谭的暗夜。</h2><p>{esc(info["prologue"])}</p></section>'
        body += '<section class="section programme"><div class="programme-heading"><h2>精选节目单</h2><p>BTAS / 精选篇目</p></div>'
        for index, item in enumerate(items[:3]):
            tag = "a" if item["status"] == "详情样板" else "article"
            href = f' href="{route(item)}"' if tag == "a" else ""
            body += f'<{tag}{href} class="programme-row"><span class="programme-number">0{index + 1}</span><div class="programme-title"><p>{esc(item["original"])}</p><h3>{esc(item["title"])}</h3><span>{esc(item["nameNote"])}</span></div><div class="programme-description"><p>{esc(item["summary"])}</p><span>{"分集导读" if tag == "a" else "分集条目"}</span></div></{tag}>'
        body += '<p class="programme-footnote">按本期放映次序浏览精选篇目。<br>BTAS85条与TNBA24条基础目录分别编目；动画电影另列。</p></section>'
        body += '<section class="section cinema-folio"><div class="programme-heading"><h2>翻开制作图册</h2><p>MODEL / STORYBOARD</p></div><p class="folio-intro">珍贵制作原案扫描：展示角色正侧面模型设定稿与实验室经典分镜线稿。</p>' + production_preview() + '</section>'
        modern = data["capedCrusader"]
        body += f'<section class="section"><p class="label">延续与再诠释 / MODERN GOTHAM</p><a class="route-card" href="{route(modern)}"><h2>{esc(modern["title"])}</h2><p>{esc(modern["summary"])}</p><span class="fine">系列概览 · 两季二十集节目单</span></a></section>'
        body += f'<section class="section"><a href="/tas/people/kevin-conroy/#voice" class="radio-column"><div class="radio-mark" aria-hidden="true"><span>ON AIR</span><strong>KC</strong><small>1955—2022</small></div><div><p class="label">声音专栏 / THE VOICE BEHIND THE MASK</p><h2>{esc(info["conroyTitle"])}</h2><p>{esc(info["conroyText"])}</p><span>凯文·康罗伊 · 动画人物档案</span></div></a></section>'
        body += '<section class="section programme-tail"><a href="/tas/episodes/nothing-to-fear/"><p class="label">主题放映 / FEAR & WILL</p><h3>恐惧与意志</h3><p>从《Nothing to Fear》看面具下的坚定与脆弱。</p></a><a href="/tas/sources/"><p class="label">放映资料 / SOURCE NOTES</p><h3>片尾署名与制作档案</h3><p>查阅英文原名、制作署名与分集资料出处。</p></a></section>'
    return shell(data, site, "动画放映室", body, "home")


def detail(data, item):
    site = item["site"]
    title_block = f'<div class="detail-title"><p class="label">{'<i data-arkham-icon="games"></i>GAME DOSSIER' if site == "arkham" else "EPISODE DOSSIER"} / {"作品档案" if site == "arkham" else "分集档案"}</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p><p class="fine">{esc(item["nameNote"])}</p></div>'
    body = f'<div class="section{" episode-feature" if site == "tas" else ""}"><a class="breadcrumb" href="/{site}/catalog/">← {"作品档案" if site == "arkham" else "分集目录"}</a>'
    if site == "arkham":
        image = next(a for a in json.loads((ROOT / "media.json").read_text())["assets"] if a["file"] == f'{item["id"]}-01.jpg')
        body += f'<div class="detail-hero"><img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["alt"])}" fetchpriority="high"></div>' + title_block
    else:
        title_card = image_gallery(site, item["id"], "title-card")
        if title_card:
            title_block = title_block.replace('<p class="original">', f'<div class="episode-title-card">{title_card}</div><p class="original">', 1)
        body += title_block
    if site == "arkham":
        fields = [("官方发售日", item["date"]), ("日期口径", item["dateNote"]), ("开发", item["developer"]), ("发行", item["publisher"]), ("原版平台", item["platforms"])]
        summary_lines = [[f'{item["date"]} 发售', item["developer"], item["platforms"].split("（")[0]]]
    else:
        fields = [("所属系列", item["series"]), ("辅助指南编号", item["guideNumber"]), ("原始制作代码", item["productionCode"]), ("来源所载首播日", item["airDate"]), ("首播地区", item["airRegion"]), ("影音目录编号", item["mediaOrder"]), ("编剧", item["writer"]), ("导演", item["director"]), ("动画制作", item["animation"]), ("配乐", item["music"]), ("客串配音", item["guests"])]
        summary_lines = [[f'{item["airDate"]} 首播', item["series"], f'指南 {item["guideNumber"]}'], [f"{label} {value}" for label, value in (("编剧", item["writer"]), ("导演", item["director"]), ("动画", item["animation"].split("；")[0])) if value]]
    voice = f'<div><dt>蝙蝠侠英语配音</dt><dd>{actor_markup(item)}</dd></div>' if item["actor"] else ''
    summary = "".join(f'<p>{" · ".join(esc(part) for part in line if part)}</p>' for line in summary_lines if line)
    if site == "arkham":
        summary = '<p class="facts-icons">' + "".join(f'<span><i data-arkham-icon="{name}"></i>{esc(text)}</span>' for name, text in (("date", f'{item["date"]} 发售'), ("studio", item["developer"]), ("platform", item["platforms"].split("（")[0])) if text) + '</p>'
    if item["actor"]:
        summary += f'<p>{'<i data-arkham-icon="voice"></i>' if site == "arkham" else ""}蝙蝠侠英语配音 {actor_markup(item)}</p>'
    full = '<details class="facts-more"><summary>完整资料</summary><dl class="facts">' + "".join(f'<div><dt>{esc(key)}</dt><dd>{esc(value)}</dd></div>' for key, value in fields if value) + voice + '</dl></details>'
    if site == "tas":
        credits = "".join(f'<div><dt>{label}</dt><dd>{esc(value)}</dd></div>' for label, value in (("编剧", item["writer"]), ("导演", item["director"]), ("动画", item["animation"].split("；")[0]), ("配乐", item["music"])) if value)
        voice_line = f'<p class="ticket-voice">蝙蝠侠英语配音 {actor_markup(item)}</p>' if item["actor"] else ''
        body += f'<div class="episode-ticket" role="group" aria-label="放映信息"><div class="ticket-main"><p class="ticket-kicker">放映单 · {esc(item["series"])}</p><p class="ticket-date">{esc(item["airDate"])}<span>首播</span></p><dl class="ticket-credits">{credits}</dl>{voice_line}</div><div class="ticket-stub"><span>No.</span><strong>{esc(item["guideNumber"])}</strong><span>{esc(item["airDate"][:4])}</span></div></div><div class="ticket-more">{full}</div>'
    else:
        body += f'<div class="facts-summary">{summary}{full}</div>'
    body += '<nav class="chapter-nav" aria-label="档案章节">' + "".join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}{" · 含剧透" if s.get("containsSpoilers") and "含剧透" not in s["title"] else ""}</a>' for s in item["sections"]) + '<a href="#sources">资料来源</a></nav>'
    body += '<div class="reading">'
    strip = film_strip(item["id"]) if site == "tas" else ""
    for index, section in enumerate(item["sections"]):
        text = paragraphs(section["body"])
        if section.get("containsSpoilers"):
            text = f'<details class="spoiler section-spoiler"><summary>剧情与结局分析 · 含剧透，展开阅读</summary>{text}</details>'
        body += f'<section id="{esc(section["id"])}"><h2>{esc(section["title"])}</h2>{text}</section>'
        if index == 0 and strip:
            body += strip
    if item.get("related"):
        linked = [e for e in data["episodes"] + data["tnbaEpisodes"] if e["id"] in item["related"]]
        cards = {a["item"]: a for a in json.loads((ROOT / "episode-media.json").read_text())["assets"] if a.get("role") == "title-card"}
        def related_row(e):
            card = cards.get(e["id"])
            thumb = f'<img class="route-thumb" src="/assets/media/{esc(card["file"])}" width="{card["width"]}" height="{card["height"]}" alt="" loading="lazy">' if card else ""
            return f'<a class="route-card{" has-thumb" if card else ""}" href="{route(e)}">{thumb}<span class="label">指南 {esc(e["guideNumber"])}</span><h3>{esc(e["title"])}</h3><p>{esc(e["original"])}</p></a>'
        body += '<section><h2>同一双集故事</h2>' + ''.join(related_row(e) for e in linked) + '</section>'
    if item.get("readingLinks"):
        body += '<section><h2>关联阅读</h2>' + ''.join(f'<a class="route-card" href="{esc(link["url"])}"><h3>{esc(link["title"])}</h3></a>' for link in item["readingLinks"]) + '</section>'
    gallery = image_gallery(site, item["id"], "frame") if not strip else ""
    if gallery:
        body += '<section><h2>图片资料</h2>' + gallery + '</section>'
    if item["spoiler"]:
        body += f'<details class="spoiler"><summary>剧情与结局 · 含剧透，展开阅读</summary>{paragraphs(item["spoiler"])}</details>'
    if item["actorLink"]:
        continuation = "继续阅读相关的作品与表演资料。" if site == "arkham" else "继续阅读动画作品与表演资料。"
        body += f'<section><h2>继续沿着声音阅读</h2><a class="route-card" href="{person_url(site)}#works"><span class="label">演员档案 / 表演路线</span><h3>凯文·康罗伊：蝙蝠侠之声</h3><p>打开凯文·康罗伊的人物档案，{continuation}</p></a></section>'
    body += pager(data, item)
    body += f'<section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></div>'
    return shell(data, site, item["title"], body, "catalog")


def pager(data, item):
    if item["site"] == "arkham":
        ordered = sorted(data["games"], key=lambda game: (game["year"], game["date"]))
        labels = ("上一部", "下一部")
    else:
        episodes = data["episodes"] if item["series"] == "BTAS" else data["tnbaEpisodes"]
        ordered = sorted((e for e in episodes if e["status"] == "详情样板"), key=lambda e: int(e["guideNumber"]))
        labels = ("上一篇导读", "下一篇导读")
    index = next(i for i, other in enumerate(ordered) if other["id"] == item["id"])
    links = []
    for label, other, side in ((labels[0], ordered[index - 1] if index > 0 else None, "prev"), (labels[1], ordered[index + 1] if index + 1 < len(ordered) else None, "next")):
        if other:
            meta = other["year"] if item["site"] == "arkham" else f'指南 {other["guideNumber"]}'
            mark = f'<i data-arkham-icon="{side}"></i>' if item["site"] == "arkham" else ""
            links.append(f'<a class="pager-{side}" href="{route(other)}" rel="{side}"><span>{mark if side == "prev" else ""}{label} · {esc(meta)}{mark if side == "next" else ""}</span><strong>{esc(other["title"])}</strong></a>')
        else:
            links.append(f'<span class="pager-{side} is-empty"></span>')
    return '<nav class="detail-pager" aria-label="' + "／".join(labels) + '">' + "".join(links) + '</nav>'


def caped_series(data):
    item = data["capedCrusader"]
    body = f'<section class="section"><a class="breadcrumb" href="/tas/">← 动画放映室</a><div class="detail-title"><p class="label">MODERN GOTHAM / 延续与再诠释</p><p class="original">{esc(item["original"])}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p></div><dl class="facts"><div><dt>英语版蝙蝠侠配音</dt><dd>{actor_markup(item)}</dd></div><div><dt>第一季</dt><dd>10集 · 独立节目单</dd></div></dl><nav class="chapter-nav" aria-label="系列章节">' + ''.join(f'<a href="#{esc(s["id"])}">{esc(s["title"])}</a>' for s in item["sections"]) + '<a href="#programme">第一季节目单</a><a href="#programme-season2">第二季节目单</a><a href="#sources">资料来源</a></nav><div class="reading">'
    body += ''.join(f'<section id="{esc(s["id"])}"><h2>{esc(s["title"])}</h2>{paragraphs(s["body"])}</section>' for s in item["sections"])
    body += '<section id="programme"><h2>第一季节目单</h2><p>按Prime Video节目单顺序排列英文原名。</p><ol class="episode-register" aria-label="披风斗士第一季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["episodes"]) + '</ol></section>'
    body += '<section id="programme-season2"><h2>第二季节目单</h2><p>按Prime Video第二季节目单顺序排列英文原名。</p><ol class="episode-register" aria-label="披风斗士第二季">' + ''.join(f'<li><span class="label">{e["number"]:02d}</span><div><strong>{esc(e["original"])}</strong></div></li>' for e in item["season2Episodes"]) + '</ol></section>'
    body += '<section><h2>图片资料</h2>' + image_gallery("tas", "caped-crusader") + '</section>'
    body += f'<section><a class="route-card" href="/tas/catalog/"><h3>回到经典TAS</h3><p>查阅BTAS全集目录，对照两座不同时代的动画哥谭。</p></a></section><section id="sources"><h2>资料来源</h2>{sources(data, item["sources"])}</section></div></section>'
    return shell(data, "tas", item["title"], body, "caped")


def person_chapters(data, site="shared"):
    from conroy_profile import chapters, chapter_citations, profile_photo, timeline, finding_feature, recording_notes
    sections = chapters(data, site)
    titles = {s['id']: f'{n:02d} / ' + s['title'].split(' / ', 1)[-1] for n, s in enumerate(sections, 1)}
    groups = [
        ('I', '面具之前', {'life', 'stage', 'voice'}),
        ('II', '声音的工作', {'ensemble', 'performances', 'beyond', 'comparison'}),
        ('III', '生活与回声', {'finding', 'audience', 'memory', 'works'}),
    ]
    contents = ''.join(f'<div><p><span>{number}</span>{label}</p><ol>' + ''.join(f'<li><a href="#{s["id"]}"><span>{titles[s["id"]].split(" / ")[0]}</span>{esc(titles[s["id"]].split(" / ",1)[-1])}</a></li>' for s in sections if s['id'] in ids) + '</ol></div>' for number, label, ids in groups)
    body = '<nav class="profile-contents" aria-label="人物章节">' + contents + '</nav><div class="reading conroy-reading">'
    for s in sections:
        text = s.get('siteBodies', {}).get(site, s['body'])
        number, title = titles[s['id']].split(' / ', 1)
        if s['id'] == 'finding':
            body += finding_feature(number)
            continue
        english = {'life':'EARLY YEARS','stage':'ON THE STAGE','voice':'BECOMING BATMAN','ensemble':'IN THE BOOTH','performances':'THE INNER VOICE','beyond':'A LIFETIME IN GOTHAM','comparison':'VOICING THE GAMES','finding':'FINDING BATMAN','audience':'BEYOND THE MICROPHONE','memory':'THE VOICE REMAINS','works':'SELECTED WORKS'}[s['id']]
        body += f'<section class="profile-chapter profile-chapter-{s["id"]}" id="{s["id"]}"><div class="profile-chapter-heading"><span class="profile-chapter-number" aria-hidden="true">{number}</span><p class="profile-eyebrow">{english}</p><h2>{esc(title)}</h2></div><div class="profile-chapter-copy">{paragraphs(text)}'
        if s['id'] == 'voice':
            body += '<div class="profile-voice-pair"><div><p>BRUCE WAYNE</p><h3>在人群之中</h3><span>轻松、圆滑的公众形象</span></div><div><p>BATMAN</p><h3>在面罩之后</h3><span>压低声音，让话语更有重量</span></div></div>'
        body += chapter_citations(data, s, site) + recording_notes(data, s, site) + '</div>'
        for photo in s.get('photos', []):
            if photo == 'conroy-2009' and site == 'tas':
                continue
            body += profile_photo(photo)
        if s["id"] == "works":
            linked = [i for i in data["games"] + data["episodes"] + data["tnbaEpisodes"] if i["actor"] == "Kevin Conroy" and i["status"] == "详情样板"]
            if site in ("arkham", "tas"):
                linked = sorted((i for i in linked if i["site"] == site), key=lambda i: i.get("airDate") or i.get("date") or i["year"])
                body += f'<details class="profile-works"><summary>展开作品目录 · {len(linked)}项</summary><ol class="work-list">' + "".join(f'<li><span class="xc-year">{esc(i["year"])}</span><a href="{route(i)}">{esc(i["title"])}</a><span class="xc-note">{esc(i["original"])}</span></li>' for i in linked) + '</ol></details></section>'
                continue
            else:
                columns = "".join(f'<div><p class="xcredit-medium">{label}<span>{name}</span></p><ol>' + "".join(f'<li><span class="xc-year">{esc(i["year"])}</span><a href="{route(i)}">{esc(i["title"])}</a><span class="xc-note">{esc(i["original"])}</span></li>' for i in sorted((i for i in linked if i["site"] == key), key=lambda i: i.get("airDate") or i.get("date") or i["year"])) + '</ol></div>' for key, label, name in (("tas", "动画", "Dark Deco"), ("arkham", "游戏", "Protocol Arkham")))
                body += f'<details class="profile-works"><summary>展开动画与游戏作品目录 · {len(linked)}项</summary><div class="xcredit-works">{columns}</div></details></section>'
                continue
        body += '</section>'
        if s['id'] == 'memory':
            body += timeline(data, site)
    return body + '</div>'


def person(data, site):
    from conroy_profile import cover, profile_sources, with_profile_styles
    p = data["person"]
    memorial_links = '<a href="/arkham/menu/">返回Protocol Arkham</a>' if site == "arkham" else '<a href="/tas/">返回Dark Deco</a>'
    body = '<div class="profile-feature">' + cover(p['title'], p['intro']) + f'<div class="profile-return">{memorial_links}</div>{person_chapters(data, site)}'
    body += profile_sources(data, site) + '</div>'
    return with_profile_styles(shell(data, site, p["title"], body, "person"))
