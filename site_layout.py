"""Topic navigation, styles and shared page chrome."""
from render_common import esc
from tas_deco import expand as expand_deco, screen_head
from arkham_icons import expand as expand_icons

NAVIGATION = {
    "arkham": (
        ("主菜单", "/arkham/menu/", "home"),
        ("作品档案", "/arkham/catalog/", "catalog"),
        ("档案馆", "/arkham/archive/", "archive"),
        ("蝙蝠侠之声", "/arkham/people/kevin-conroy/", "person"),
        ("资料来源", "/arkham/sources/", "sources"),
        ("周边档案", "/arkham/collectibles/", "collectibles"),
        ("图片资料", "/arkham/gallery/", "gallery"),
        ("搜索", "/arkham/search/", "search"),
    ),
    "tas": (
        ("首页", "/tas/", "home"),
        ("分集目录", "/tas/catalog/", "catalog"),
        ("档案馆", "/tas/archive/", "archive"),
        ("披风斗士", "/tas/series/caped-crusader/", "caped"),
        ("蝙蝠侠之声", "/tas/people/kevin-conroy/", "person"),
        ("资料来源", "/tas/sources/", "sources"),
        ("周边档案", "/tas/collectibles/", "collectibles"),
        ("图片资料", "/tas/gallery/", "gallery"),
        ("搜索", "/tas/search/", "search"),
    ),
    "shared": (
        ("Protocol Arkham", "/arkham/", "arkham"),
        ("Dark Deco", "/tas/", "tas"),
        ("蝙蝠侠之声", "/voices/", "voices"),
    ),
}
SEARCH_OPTIONS = {
    "arkham": ("康罗伊、谜语人、疯人院", ""),
    "tas": ("康罗伊、稻草人、Nothing to Fear", ""),
}


def icon(site):
    filename = "logo-tas-transparent.svg" if site == "tas" else "logo-arkham-transparent.svg" if site == "arkham" else "icon-shared.svg"
    return f'<link rel="icon" href="/assets/{filename}" type="image/svg+xml">'


def stylesheets(site):
    files = ["style.css"]
    if site in ("arkham", "tas"):
        files.append(f"{site}.css")
        files.append("topic-navigation.css")
    return icon(site) + "".join(f'<link rel="stylesheet" href="/assets/{file}">' for file in files)


ARKHAM_CONTROLS = '<button class="arkham-quick" data-arkham-quick type="button" aria-pressed="false" hidden title="省略回访开场与菜单转场">快速浏览：关</button><button class="arkham-sound" data-arkham-sound type="button" aria-pressed="true" hidden>转场音效：开</button>'


def arkham_effects(controls=True):
    """Floating controls belong to the intro and menu; inner pages carry them in the 更多导航 menu."""
    return '<canvas id="intro-bats" aria-hidden="true" hidden></canvas><audio id="intro-audio" preload="auto"><source src="/assets/arkham-bat-transition.m4a" type="audio/mp4"><source src="/assets/arkham-bat-transition.wav" type="audio/wav"></audio>' + (ARKHAM_CONTROLS if controls else '')


def arkham_scripts():
    return '<script src="/assets/arkham-transition.js" defer></script><script src="/assets/arkham-menu.js" defer></script><script src="/assets/app.js" defer></script><script src="/assets/arkham-nav.js" defer></script>'


def shell(data, site, title, body, active=""):
    info = data["sites"].get(site, {"name": "蝙蝠侠之声", "english": "A VOICE IN THE DARK"})
    nav = NAVIGATION[site]
    if site == "tas":
        body = screen_head(body)
    brand_mark = (f'<img class="brand-logo" src="/assets/{"logo-tas-transparent.svg" if site == "tas" else "logo-arkham-transparent.svg"}" width="40" height="40" alt="" aria-hidden="true">'
                  if site in ("arkham", "tas") else '<span class="brand-symbol" aria-hidden="true">✦</span>')
    brand_subtitle = {"arkham": "阿卡姆协议", "tas": "TAS 动画档案"}.get(site, info["name"])
    footer_links = {
        "arkham": '<a href="/arkham/menu/">主菜单</a><a href="/arkham/people/kevin-conroy/">凯文·康罗伊</a><a href="/voices/">两站共同档案</a>',
        "tas": '<a href="/tas/">Dark Deco</a><a href="/tas/people/kevin-conroy/">凯文·康罗伊</a><a href="/voices/">两站共同档案</a>',
    }.get(site, '<a href="/arkham/">Protocol Arkham</a><a href="/tas/">Dark Deco</a><a href="/voices/">蝙蝠侠之声</a>') + '<a href="/editor/" data-local-edit hidden>编辑文案</a>'
    scripts = arkham_scripts() if site == "arkham" else '<script src="/assets/app.js" defer></script>'
    if site == "tas":
        scripts += '<script src="/assets/tas-motion.js" defer></script><script src="/assets/tas-lightbox.js" defer></script>'
    effects = arkham_effects(controls=False) if site == "arkham" else ''
    nav_html = ""
    more_html = ""
    for label, url, key in nav:
        menu_return = site == "arkham" and key == "home"
        attributes = 'class="menu-return" aria-label="返回主菜单" title="Esc 返回主菜单"' if menu_return else ""
        text = '<kbd>Esc</kbd><span>MAIN MENU</span>' if menu_return else label
        link = f'<a href="{url}" {"aria-current=page" if key == active else ""} {attributes}>{text}</a>' if site == "arkham" else f'<a href="{url}" {"aria-current=page" if key == active else ""}>{label}</a>'
        if site in ("arkham", "tas") and key not in ("home", "catalog", "archive", "search"):
            more_html += link
        else:
            nav_html += link
    if site == "arkham":
        more_html += f'<div class="topic-menu-controls">{ARKHAM_CONTROLS}</div>'
    if more_html:
        nav_html += f'<details class="topic-more"><summary>更多导航</summary><div class="topic-menu">{more_html}</div></details>'
    html = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(title)} · {esc(info["name"])} | Batman小站</title>{stylesheets(site)}{scripts}</head><body class="{esc(site)}"><a class="skip" href="#main">跳到正文</a><header><a class="brand" href="/{site + "/" if site in data["sites"] else ""}">{brand_mark}<span>{esc(info["english"])}<small>{esc(brand_subtitle)}</small></span></a><nav aria-label="主导航">{nav_html}</nav><a class="back-site" href="https://www.batcavecn.com/">BATCAVECN ↗</a></header><main id="main">{body}</main>{effects}<footer><div><p class="label">BATCAVECN SPECIAL ARCHIVES</p><p>{esc(info["name"])} · 非商业影迷资料库</p><p class="fine">非商业影迷项目 · 与 DC / Warner Bros. 无官方合作关系。</p></div><div class="footer-links">{footer_links}</div></footer></body></html>'
    return expand_icons(html) if site == "arkham" else expand_deco(html) if site == "tas" else html
