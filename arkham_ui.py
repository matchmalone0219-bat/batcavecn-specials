"""Arkham title screen, game menu and game catalogue."""
import json
from render_common import ROOT, esc, route
from arkham_icons import icon as arkham_icon
from site_layout import shell, stylesheets, arkham_effects, arkham_scripts


def arkham_menu_background():
    slides = [
        ("arkham-city-02.jpg", "《阿卡姆之城》官方商店截图"),
        ("arkham-asylum-01.jpg", "《阿卡姆疯人院》官方商店截图"),
        ("arkham-origins-01.jpg", "《阿卡姆起源》官方商店截图"),
        ("arkham-origins-blackgate-01.jpg", "《阿卡姆起源：黑门》官方商店截图 · 豪华版（2014）"),
        ("arkham-knight-01.jpg", "《阿卡姆骑士》官方商店截图"),
        ("suicide-squad-kill-the-justice-league-01.jpg", "《自杀小队：消灭正义联盟》官方商店截图"),
    ]
    images = [{"src": f"/assets/media/{image}", "caption": caption} for image, caption in slides]
    return f'<div class="game-scene menu-backdrop" aria-hidden="true" data-slides="{esc(json.dumps(images, ensure_ascii=False))}"><img class="menu-background-base" src="{images[0]["src"]}" alt=""><img class="menu-background-next" alt=""></div><div class="game-fog" aria-hidden="true"></div><div class="game-rain" aria-hidden="true"></div>'


def arkham_menu(heading="h1"):
    entries = [
        ("作品档案", "GAME ARCHIVE", "/arkham/catalog/", "八部作品 · 阿卡姆岛、黑门、虚拟现实与大都会", "arkham-city-02.jpg", "《阿卡姆之城》官方商店截图", "games"),
        ("哥谭档案馆", "GOTHAM DOSSIERS", "/arkham/archive/", "案件重建 · 患者终端 · 场景与创作档案", "arkham-asylum-01.jpg", "《阿卡姆疯人院》官方商店截图", "dossiers"),
        ("蝙蝠侠之声", "KEVIN CONROY", "/arkham/people/kevin-conroy/", "凯文·康罗伊 · 游戏作品与表演档案", "arkham-city-03.jpg", "《阿卡姆之城》官方商店截图", "voice"),
        ("周边档案", "COLLECTIBLES", "/arkham/collectibles/", "人偶 · 战衣版本 · 雕像与游戏衍生收藏", "arkham-origins-01.jpg", "《阿卡姆起源》官方商店截图", "collectibles"),
        ("图片资料", "IMAGE ARCHIVE", "/arkham/gallery/", "八部游戏与研究图片", "arkham-knight-01.jpg", "《阿卡姆骑士》官方商店截图", "gallery"),
        ("搜索档案", "SEARCH", "/arkham/search/", "检索阿卡姆作品、人物、物件与主题", "arkham-origins-blackgate-01.jpg", "《阿卡姆起源：黑门》官方商店截图 · 豪华版（2014）", "search"),
        ("资料来源", "SOURCE NOTES", "/arkham/sources/", "作品资料 · 主创访谈 · 版本书目", "suicide-squad-kill-the-justice-league-01.jpg", "《自杀小队：消灭正义联盟》官方商店截图", "sources"),
    ]
    tiles = "".join(f'<a class="menu-tile" href="{url}" data-title="{esc(title)}" data-description="{esc(desc)}" data-image="/assets/media/{image}" data-caption="{esc(caption)}">{arkham_icon(icon, cls="menu-icon")}<span>{esc(title)}</span><small>{english}</small></a>' for title, english, url, desc, image, caption, icon in entries)
    return f'<div class="game-menu game-menu-console"><div class="menu-selection"><p class="game-eyebrow">BATCAVECN // PROTOCOL ARKHAM</p><p class="menu-brand">阿卡姆协议<span>PROTOCOL ARKHAM</span></p><nav class="menu-grid" aria-label="档案主菜单">{tiles}</nav><div class="game-controls"><a href="/arkham/?opening=1"><kbd>Esc</kbd> 返回启动画面</a><span class="keyboard-hint"><kbd>↵</kbd> 进入 · ↑ ↓ 选择</span></div></div><div class="menu-preview"><p class="game-eyebrow">ARCHIVE SELECT</p><{heading} id="menu-title">作品档案</{heading}><p id="menu-description" aria-live="polite">八部作品 · 阿卡姆岛、黑门、虚拟现实与大都会</p><p class="menu-preview-note">作品 · 人物 · 现场机要档案</p></div></div><div class="menu-background-tools"><button id="menu-background-toggle" type="button" aria-pressed="true" hidden>背景轮播：开</button></div>'


def arkham_catalog(data):
    rows = []
    images = {asset["item"]: asset for asset in json.loads((ROOT / "catalog-art.json").read_text())["assets"]}
    for item in sorted(data["games"], key=lambda game: (game["year"], game["date"])):
        image = images[item["id"]]
        rows.append(f'<a class="arkham-game-card" href="{route(item)}"><div class="arkham-game-image"><img src="/assets/media/{image["file"]}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["alt"])}"><span>{esc(item["year"])}</span></div><div class="arkham-game-copy"><p class="game-eyebrow">{esc(item["original"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["summary"])}</p><div class="arkham-game-meta"><span>{esc(item["developer"])}</span><span>{esc(item["date"])}</span></div></div></a>')
    games = sorted(data["games"], key=lambda game: (game["year"], game["date"]))
    items = "".join(f'<li><a class="browser-item" href="{route(item)}" data-browse-item data-target="game-{item["id"]}"><span class="browser-year">{esc(item["year"])}</span><span class="browser-name">{esc(item["title"])}<small>{esc(item["original"])}</small></span></a></li>' for item in games)
    panels = "".join(f'<a class="browser-panel" href="{route(item)}" data-panel="game-{item["id"]}"{"" if n == 0 else " hidden"}><img src="/assets/media/{images[item["id"]]["file"]}" width="{images[item["id"]]["width"]}" height="{images[item["id"]]["height"]}" alt="{esc(images[item["id"]]["alt"])}" loading="lazy"><div class="browser-panel-copy"><p class="game-eyebrow">{esc(item["original"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["summary"])}</p><p class="facts-icons"><span><i data-arkham-icon="date"></i>{esc(item["date"])}</span><span><i data-arkham-icon="studio"></i>{esc(item["developer"])}</span><span><i data-arkham-icon="platform"></i>{esc(item["platforms"].split("（")[0])}</span></p></div></a>' for n, item in enumerate(games))
    browser = f'<div class="game-browser" data-browser data-browse-mode="panels" data-browse-hover hidden><div class="browser-side"><ol class="browser-list">{items}</ol><p class="browser-hint"><kbd>↑</kbd><kbd>↓</kbd> 选择 · <kbd>↵</kbd> 进入档案</p></div><div class="browser-preview">{panels}</div></div>'
    body = '<section class="section arkham-game-catalog"><div class="arkham-catalog-heading"><div><p class="game-eyebrow"><i data-arkham-icon="games"></i>GAME ARCHIVE / ARCHIVE SELECT</p><h1>作品档案</h1></div><p>八部作品，<br>按原作年份排列。</p></div>'+browser+'<div class="arkham-games-grid" data-browser-fallback>'+''.join(rows)+'</div>'+'<a class="dossier-shelf" href="/arkham/archive/rocksteady/"><p class="label">CREATIVE HISTORY</p><h2>Rocksteady与创作变迁</h2><p>合作射击与赛季制如何改变了工作室的制作方向。</p></a></section>'
    return shell(data, "arkham", "作品档案", body, "catalog")


def arkham_screen(data, menu=False):
    if not menu:
        body = '<div class="intro-stage" id="intro-stage"><h1 class="intro-identity">阿卡姆协议<span>BATCAVECN / PROTOCOL ARKHAM</span></h1><div class="intro-film" aria-hidden="true"><video id="intro-video" loop muted playsinline preload="metadata" poster="/assets/arkham-city-intro-poster.jpg"><source src="/assets/arkham-city-intro.mp4" type="video/mp4"></video></div><audio id="intro-score" loop preload="none" data-src="/assets/arkham-city-intro-music.m4a"></audio><a class="intro-entry" href="/arkham/menu/" aria-label="激活阿卡姆协议，进入主菜单"><span>激活协议<span>ACTIVATE PROTOCOL</span></span></a><div class="intro-tools" aria-label="开场播放设置"><button id="intro-play" type="button" hidden>播放开场</button><button id="intro-music" type="button" aria-pressed="false" hidden>开启配乐</button><button data-arkham-quick type="button" aria-pressed="false" hidden title="省略回访开场与菜单转场">快速浏览：关</button><button id="intro-sound" type="button" aria-pressed="true" hidden>转场音效：开</button></div><p class="intro-status" id="intro-status" role="status"></p></div>'
        body += '<section id="intro-menu" hidden>' + arkham_menu("h2") + '</section>'
        return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Protocol Arkham · 启动画面</title>{stylesheets("arkham")}{arkham_scripts()}<script src="/assets/arkham-intro.js" defer></script></head><body class="arkham game-screen arkham-intro"><a class="skip" href="#main">跳到正文</a>{arkham_menu_background()}<main id="main">{body}</main>{arkham_effects()}<a class="screen-home" href="https://www.batcavecn.com/">BATCAVECN ↗</a><p class="screen-note">非商业影迷档案</p></body></html>'
    body = arkham_menu()
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Protocol Arkham · {"主菜单" if menu else "启动画面"}</title>{stylesheets("arkham")}{arkham_scripts()}</head><body class="arkham game-screen {"menu-screen" if menu else "start-screen"}"><a class="skip" href="#main">跳到正文</a>{arkham_menu_background()}<main id="main">{body}</main>{arkham_effects()}<a class="screen-home" href="https://www.batcavecn.com/">BATCAVECN ↗</a><p class="screen-note">非商业影迷档案</p></body></html>'
