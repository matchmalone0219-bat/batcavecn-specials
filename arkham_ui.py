"""Arkham title screen, game menu and game catalogue."""
import json
from render_common import ROOT, esc, route
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
        ("作品档案", "GAME ARCHIVE", "/arkham/catalog/", "六部作品 · 从阿卡姆岛、黑门到大都会", "arkham-city-02.jpg", "《阿卡姆之城》官方商店截图", "M3 5h7l2 2h9v13H3z"),
        ("哥谭档案馆", "GOTHAM DOSSIERS", "/arkham/archive/", "场景与人物档案 · Rocksteady与创作变迁", "arkham-asylum-01.jpg", "《阿卡姆疯人院》官方商店截图", "M12 3v18M3 12h18M5 5l14 14M19 5L5 19"),
        ("蝙蝠侠之声", "KEVIN CONROY", "/arkham/people/kevin-conroy/", "凯文·康罗伊 · 游戏作品与表演档案", "arkham-city-03.jpg", "《阿卡姆之城》官方商店截图", "M4 9v6M8 5v14M12 3v18M16 7v10M20 9v6"),
        ("周边档案", "COLLECTIBLES", "/arkham/collectibles/", "人偶 · 战衣版本 · 雕像与游戏衍生收藏", "arkham-origins-01.jpg", "《阿卡姆起源》官方商店截图", "M12 3l9 5v9l-9 5-9-5V8zM3 8l9 5 9-5M12 13v9"),
        ("图片资料", "IMAGE ARCHIVE", "/arkham/gallery/", "六部游戏与研究图片 · 保留版本和出处", "arkham-knight-01.jpg", "《阿卡姆骑士》官方商店截图", "M3 4h18v16H3zM3 17l6-7 4 4 3-3 5 6M16 8h1"),
        ("搜索档案", "SEARCH", "/arkham/search/", "检索阿卡姆作品、人物、物件与主题", "arkham-origins-blackgate-01.jpg", "《阿卡姆起源：黑门》官方商店截图 · 豪华版（2014）", "M15 15l6 6M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0"),
        ("资料来源", "SOURCE NOTES", "/arkham/sources/", "作品资料 · 主创访谈 · 版本书目", "suicide-squad-kill-the-justice-league-01.jpg", "《自杀小队：消灭正义联盟》官方商店截图", "M5 3h14v18H5zM8 7h8M8 11h8M8 15h5"),
    ]
    tiles = "".join(f'<a class="menu-tile" href="{url}" data-title="{esc(title)}" data-description="{esc(desc)}" data-image="/assets/media/{image}" data-caption="{esc(caption)}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{icon}"/></svg><span>{esc(title)}</span><small>{english}</small></a>' for title, english, url, desc, image, caption, icon in entries)
    return f'<div class="game-menu game-menu-console"><div class="menu-selection"><p class="game-eyebrow">BATCAVECN // PROTOCOL ARKHAM</p><p class="menu-brand">阿卡姆协议<span>PROTOCOL ARKHAM</span></p><nav class="menu-grid" aria-label="档案主菜单">{tiles}</nav><div class="game-controls"><a href="/arkham/"><kbd>Esc</kbd> 返回启动画面</a><span><kbd>↵</kbd> 进入 · ↑ ↓ 选择</span></div></div><div class="menu-preview"><p class="game-eyebrow">ARCHIVE SELECT</p><{heading} id="menu-title">作品档案</{heading}><p id="menu-description" aria-live="polite">六部作品 · 从阿卡姆岛、黑门到大都会</p><p class="menu-preview-note">作品 · 人物 · 哥谭的故事</p></div></div><div class="menu-background-tools"><span id="menu-background-caption">《阿卡姆之城》官方商店截图</span><button id="menu-background-toggle" type="button" aria-pressed="true" hidden>背景轮播：开</button></div>'


def arkham_catalog(data):
    rows = []
    images = {asset["item"]: asset for asset in json.loads((ROOT / "media.json").read_text())["assets"] if asset["file"].endswith("-01.jpg")}
    for item in sorted(data["games"], key=lambda game: (game["year"], game["date"])):
        image = images[item["id"]]
        rows.append(f'<a class="arkham-game-card" href="{route(item)}"><div class="arkham-game-image"><img src="/assets/media/{item["id"]}-01.jpg" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["caption"])}"><span>{esc(item["year"])}</span></div><div class="arkham-game-copy"><p class="game-eyebrow">{esc(item["original"])}</p><h2>{esc(item["title"])}</h2><p>{esc(item["summary"])}</p><div class="arkham-game-meta"><span>{esc(item["developer"])}</span><span>{esc(item["date"])}</span></div></div></a>')
    body = '<section class="section arkham-game-catalog"><a class="breadcrumb menu-return" href="/arkham/menu/" aria-label="返回主菜单"><kbd>Esc</kbd><span>MAIN MENU</span></a><div class="arkham-catalog-heading"><div><p class="game-eyebrow">GAME ARCHIVE / ARCHIVE SELECT</p><h1>作品档案</h1></div><p>六部作品，<br>按原作年份排列。</p></div><div class="arkham-games-grid">'+''.join(rows)+'</div><a class="dossier-shelf" href="/arkham/archive/rocksteady/"><p class="label">CREATIVE HISTORY</p><h2>Rocksteady与创作变迁</h2><p>从成为蝙蝠侠到合作射击与赛季制，沿作品与制作人员阅读转向。</p></a></section>'
    return shell(data, "arkham", "作品档案", body, "catalog")


def arkham_screen(data, menu=False):
    if not menu:
        body = '<div class="intro-stage" id="intro-stage"><h1 class="intro-identity">阿卡姆协议<span>BATCAVECN / PROTOCOL ARKHAM</span></h1><div class="intro-film" aria-hidden="true"><video id="intro-video" loop muted playsinline preload="metadata" poster="/assets/arkham-city-intro-poster.jpg"><source src="/assets/arkham-city-intro.mp4" type="video/mp4"></video></div><audio id="intro-score" loop preload="none" data-src="/assets/arkham-city-intro-music.m4a"></audio><a class="intro-entry" href="/arkham/menu/" aria-label="激活阿卡姆协议，进入主菜单"><span>激活协议<span>ACTIVATE PROTOCOL</span></span></a><div class="intro-tools" aria-label="开场播放设置"><button id="intro-play" type="button" hidden>播放开场</button><button id="intro-music" type="button" aria-pressed="false" hidden>开启配乐</button><button id="intro-sound" type="button" aria-pressed="true" hidden>转场音效：开</button></div><p class="intro-status" id="intro-status" role="status"></p></div>'
        body += '<section id="intro-menu" hidden>' + arkham_menu("h2") + '</section>'
        return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Protocol Arkham · 启动画面</title>{stylesheets("arkham")}{arkham_scripts()}<script src="/assets/arkham-intro.js" defer></script></head><body class="arkham game-screen arkham-intro"><a class="skip" href="#main">跳到正文</a>{arkham_menu_background()}<main id="main">{body}</main>{arkham_effects()}<a class="screen-home" href="https://www.batcavecn.com/">BATCAVECN ↗</a><p class="screen-note">非商业影迷档案</p></body></html>'
    body = arkham_menu()
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Protocol Arkham · {"主菜单" if menu else "启动画面"}</title>{stylesheets("arkham")}{arkham_scripts()}</head><body class="arkham game-screen {"menu-screen" if menu else "start-screen"}"><a class="skip" href="#main">跳到正文</a>{arkham_menu_background()}<main id="main">{body}</main>{arkham_effects()}<a class="screen-home" href="https://www.batcavecn.com/">BATCAVECN ↗</a><p class="screen-note">非商业影迷档案</p></body></html>'
