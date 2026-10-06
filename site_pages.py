"""Assemble page routes and the search index without writing output."""
from render_common import esc, route, cards, sources, episode_catalog, image_gallery
from site_layout import shell, SEARCH_OPTIONS
from content_pages import home, detail, caped_series, person
from arkham_ui import arkham_screen, arkham_catalog
from tas_pages import build_archive
from merchandise_pages import build_collectibles
from arkham_pages import build_arkham_archive
from arkham_interactions import build_interactions


def render_pages(data):
    pages = {}
    for site in ("arkham", "tas"):
        info = data["sites"][site]
        pages[f"{site}/index.html"] = home(data, site)
        items = data["games"] if site == "arkham" else data["episodes"] + data["tnbaEpisodes"]
        detail_count = sum(e["status"] == "详情样板" for e in data["episodes"])
        note = "按原作年份排列；移植与合集不计为新故事。" if site == "arkham" else f"BTAS · 85集，其中{detail_count}篇分集导读；TNBA · 24集。两份目录按各自的The World’s Finest指南编号排列，动画电影单独编目。"
        pages[f"{site}/catalog/index.html"] = shell(data, site, "作品档案" if site == "arkham" else "分集目录", f'<section class="section"><p class="label">ARCHIVE INDEX</p><h1>{"作品档案" if site == "arkham" else "分集目录"}</h1><p class="lead">{note}</p>{'<h2>BTAS · 85集</h2>' + episode_catalog(data["episodes"]) + '<h2>TNBA · 24集</h2>' + episode_catalog(data["tnbaEpisodes"]) if site == "tas" else chr(60) + 'div class="grid">' + cards(items, True) + '</div>'}</section>', "catalog")
        pages[f"{site}/sources/index.html"] = shell(data, site, "资料来源", f'<section class="section"><p class="label">SOURCES / EDITORIAL NOTES</p><h1>每条资料，都有来处。</h1><p class="lead">作品资料、主创访谈、分集指南与评论文章，按来源类型查阅。</p>{sources(data, {sid for i in items + [data["person"]] + ([data["capedCrusader"]] if site == "tas" else []) for sid in i["sources"]})}</section>', "sources")
        pages[f"{site}/gallery/index.html"] = shell(data, site, "图片资料", '<section class="section"><p class="label">IMAGE ARCHIVE</p><h1>图片资料</h1><p class="lead">游戏截图、动画画面与官方宣传图，按作品分别记录。</p><p class="fine">图片版权归原权利人。</p>' + image_gallery(site) + '</section>', "gallery")
        search_placeholder, extra_scope = SEARCH_OPTIONS[site]
        pages[f"{site}/search/index.html"] = shell(data, site, "搜索档案", f'<section class="section"><p class="label">SEARCH / {esc(info["english"])}</p><h1>寻找一段故事。</h1><form id="search-form" class="search-form"><label for="query">集名、作品名、人物或主题</label><div><input id="query" name="q" type="search" placeholder="试试：{search_placeholder}"><button class="button">搜索</button></div><label for="scope">检索范围</label><select id="scope"><option value="{site}">当前专题＋共同人物</option>{extra_scope}</select></form><p id="search-count" role="status"></p><div id="search-results" class="grid routes"></div></section>', "search")
        for item in items:
            if item["status"] == "详情样板":
                pages[route(item).strip("/") + "/index.html"] = detail(data, item)
    pages["tas/series/caped-crusader/index.html"] = caped_series(data)
    pages["arkham/menu/index.html"] = arkham_screen(data, True)
    pages["arkham/catalog/index.html"] = arkham_catalog(data)
    pages["arkham/people/kevin-conroy/index.html"] = person(data, "arkham")
    pages["people/kevin-conroy/index.html"] = person(data)
    pages["index.html"] = shell(data, "shared", "两座哥谭", '<section class="section hub"><p class="label">BATCAVECN / SPECIAL ARCHIVES</p><h1>两座哥谭。<br>一段熟悉的声音。</h1><p class="lead">Batman小站 · Protocol Arkham与Dark Deco专题档案。</p><div class="grid routes"><a class="route-card hub-arkham" href="/arkham/"><p class="label">PROTOCOL ARKHAM</p><h2>阿卡姆协议</h2><p>游戏、人物与创作故事。</p></a><a class="route-card hub-tas" href="/tas/"><p class="label">DARK DECO</p><h2>TAS 动画档案</h2><p>分集、声音与动画艺术。</p></a></div></section>')
    pages["editor/index.html"] = shell(data, "shared", "编辑文案", '<section class="section editor"><p class="label">BATCAVECN / LOCAL EDITOR</p><h1>编辑文案</h1><p class="lead">选择条目，修改文字，预览后保存。页面样式单独保留；每次保存自动备份。</p><p id="editor-status" role="status">正在读取本地内容…</p><form id="editor-form"><label for="entry">选择页面或条目</label><select id="entry"></select><label for="field">选择文字字段</label><select id="field"></select><label for="text">正文</label><textarea id="text" rows="8" required></textarea><div class="editor-actions"><button class="button" type="submit">保存到本地文件</button><button type="button" id="reset-text">撤销未保存修改</button><a id="preview-link" href="/arkham/" target="_blank" rel="noopener">查看页面 ↗</a></div></form><section class="editor-preview"><h2>文字预览</h2><div id="text-preview"></div></section></section>')
    tas_pages, tas_records, tas_sources, tas_gallery, tas_images = build_archive(data, shell)
    pages.update(tas_pages)
    pages["tas/sources/index.html"] = pages["tas/sources/index.html"].replace("</main>", tas_sources + "</main>")
    pages["tas/gallery/index.html"] = pages["tas/gallery/index.html"].replace("</main>", '<div class="section">' + tas_gallery + "</div></main>")
    ark_pages, ark_records, ark_sources, ark_gallery, ark_images = build_arkham_archive(data, shell)
    pages.update(ark_pages)
    interactive_pages, interactive_records = build_interactions(data, shell)
    pages.update(interactive_pages)
    pages["arkham/sources/index.html"] = pages["arkham/sources/index.html"].replace("</main>", ark_sources + "</main>")
    pages["arkham/gallery/index.html"] = pages["arkham/gallery/index.html"].replace("</main>", ark_gallery + "</main>")
    merch_pages, merch_records, merch_sources, merch_galleries, merch_images = build_collectibles(data, shell)
    pages.update(merch_pages)
    for site in ("arkham", "tas"):
        pages[f"{site}/sources/index.html"] = pages[f"{site}/sources/index.html"].replace("</main>", merch_sources[site] + "</main>")
        pages[f"{site}/gallery/index.html"] = pages[f"{site}/gallery/index.html"].replace("</main>", merch_galleries[site] + "</main>")
    index = [{"title": i["title"], "original": i["original"], "summary": i["summary"], "tags": i["tags"], "site": i["site"], "status": "作品档案" if i["site"] == "arkham" else ("系列档案" if i["id"] == "caped-crusader" else "分集导读" if i["status"] == "详情样板" else "分集条目"), "url": route(i)} for i in data["games"] + data["episodes"] + data["tnbaEpisodes"] + [data["capedCrusader"]]]
    index.append({"title": data["person"]["title"], "original": data["person"]["original"], "summary": data["person"]["intro"], "tags": ["蝙蝠侠之声", "Kevin Conroy", "共同演员"], "site": "shared", "status": "人物档案", "url": "/people/kevin-conroy/"})
    index.extend(tas_records)
    index.extend(merch_records)
    index.extend(ark_records)
    index.extend(interactive_records)
    return pages, index, tas_images + merch_images + ark_images
