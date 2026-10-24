"""Conroy's illustrated biography, scoped reading aids and plain-text references."""
import json

from render_common import ROOT, esc, paragraphs, route


def shared_work_directory(items):
    animation = [i for i in items if i['site'] == 'tas']
    games = sorted((i for i in items if i['site'] == 'arkham'), key=lambda i: i.get('date') or i['year'])
    groups = [(series, sorted((i for i in animation if i.get('series') == series), key=lambda i: i.get('airDate') or i['year']))
              for series in ('BTAS', 'TNBA')]
    groups = [(series, episodes) for series, episodes in groups if episodes]
    series_names = {'BTAS': ('蝙蝠侠：动画系列', 'Batman: The Animated Series'),
                    'TNBA': ('蝙蝠侠新冒险', 'The New Batman Adventures')}
    series_rows = ''.join(
        f'<li><span class="xc-year">{len(episodes)}集</span><a href="/tas/catalog/#{series.lower()}">{esc(series_names[series][0])}</a>'
        f'<span class="xc-note">{esc(series_names[series][1])}</span></li>' for series, episodes in groups
    )

    def rows(works):
        return ''.join(f'<li><span class="xc-year">{esc(i["year"])}</span><a href="{route(i)}">{esc(i["title"])}</a>'
                       f'<span class="xc-note">{esc(i["original"])}</span></li>' for i in works)

    standalone = [i for i in animation if i.get('series') not in series_names]
    episode_count = sum(len(episodes) for _, episodes in groups)
    directory = ''.join(
        f'<div class="profile-episode-group"><h3>{series} · {len(episodes)}集</h3>'
        f'<ol class="work-list profile-episode-list">{rows(episodes)}</ol></div>' for series, episodes in groups
    )
    return (
        '<div class="profile-works profile-shared-works"><div class="profile-work-overview">'
        f'<div><p class="xcredit-medium">动画<span>Dark Deco</span></p><ol class="work-list">{series_rows}{rows(standalone)}</ol></div>'
        f'<div><p class="xcredit-medium">游戏<span>Protocol Arkham · {len(games)}部</span></p><ol class="work-list">{rows(games)}</ol></div></div>'
        f'<details class="profile-episode-directory"><summary>展开动画分集目录 · {episode_count}集</summary>{directory}</details></div>'
    )


def media_assets():
    return json.loads((ROOT / 'conroy-media.json').read_text())['assets']


def finding_packet():
    return json.loads((ROOT / 'finding-batman.json').read_text())


def finding_assets():
    return finding_packet()['images']


def main_reading_packet():
    return json.loads((ROOT / 'conroy-reading.json').read_text())


def main_reading():
    packet = main_reading_packet()
    rows = ''.join(
        f'<a class="profile-main-row" href="{esc(a["url"])}"><span class="profile-main-date"><time datetime="{a["date"]}">{a["date"][:4]}<small>{a["date"][5:].replace("-", " / ")}</small></time></span>'
        f'<span class="profile-main-copy"><span class="profile-main-type">{esc(a["type"])}</span><strong>{esc(a["title"])}</strong><span>{esc(a["summary"])}</span></span>'
        '<span class="profile-main-action">前往主站 <span aria-hidden="true">↗</span></span></a>'
        for a in packet['articles']
    )
    return (
        '<section class="profile-main-reading" id="main-reading" aria-labelledby="main-reading-title">'
        '<div class="profile-main-head"><p class="profile-eyebrow">BATCAVECN / FROM THE MAIN ARCHIVE</p>'
        f'<h2 id="main-reading-title">{esc(packet["title"])}</h2><p>{esc(packet["intro"])}</p></div>'
        f'<div class="profile-main-rows">{rows}</div></section>'
    )


def finding_feature(number):
    packet = finding_packet()
    numbers = {s['id']: n for n, s in enumerate(packet['sources'], 1)}
    credits = ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(name)}</dd></div>' for label, name in packet['credits'])
    contents = ''.join(f'<a href="#{s["id"]}"><span>{n:02d}</span>{esc(s["title"])}</a>' for n, s in enumerate(packet['sections'], 1))
    body = (
        '<section class="finding-feature" id="finding" aria-labelledby="finding-title">'
        f'<div class="finding-cover"><p class="finding-kicker"><span>{esc(number)} / A COMIC MEMOIR</span><span>DC PRIDE · 2022</span></p>'
        f'<h2 id="finding-title">Finding<br><em>Batman</em><span>{esc(packet["subtitle"])}</span></h2>'
        f'<p class="finding-intro">{esc(packet["intro"])}</p></div>'
        f'<dl class="finding-credits">{credits}</dl>'
        f'<nav class="finding-contents" aria-label="Finding Batman专题章节">{contents}</nav>'
    )
    for n, section in enumerate(packet['sections'], 1):
        if section['id'] == 'finding-page-language':
            image = packet['images'][0]
            notes = ''.join(f'<li><span>{i:02d}</span><div><h4>{esc(title)}</h4><p>{esc(text)}</p></div></li>' for i, (title, text) in enumerate(packet['imageNotes'], 1))
            body += (
                '<div class="finding-folio" id="finding-original">'
                f'<figure class="finding-comic"><a href="/assets/media/{esc(image["file"])}" target="_blank" rel="noopener" aria-label="放大阅读Finding Batman开篇原页">'
                f'<img src="/assets/media/{esc(image["file"])}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["alt"])}" loading="lazy"></a>'
                f'<figcaption>{esc(image["caption"])}<span>{esc(image["rights"])}</span><span>原页节选 · 点按图像放大阅读 · 原作见资料 [F01]</span></figcaption></figure>'
                f'<aside class="finding-page-notes" aria-label="原页阅读提示"><p class="finding-label">LOOK CLOSER / 看这一页</p><h3>从门口，<br>走进回忆。</h3><ol>{notes}</ol></aside></div>'
            )
        citations = ' · '.join(f'[F{numbers[r]:02d}]' for r in section['sourceRefs'])
        body += (
            f'<section class="finding-essay" id="{esc(section["id"])}"><div class="finding-essay-heading"><span>{n:02d}</span>'
            f'<p class="finding-label">{esc(section["eyebrow"])}</p><h3>{esc(section["title"])}</h3></div>'
            f'<div class="finding-essay-copy">{paragraphs(section["body"])}<p class="finding-citations">资料 {citations}</p></div></section>'
        )
    sources = ''.join(f'<li><span>[F{n:02d}]</span><div><p>{esc(s["title"])}</p><small>{esc(s["type"])}</small></div></li>' for n, s in enumerate(packet['sources'], 1))
    return body + f'<div class="finding-sources"><h3>本篇阅读资料</h3><ol>{sources}</ol></div></section>'


def visible(item, site):
    return site in item.get('sites', ('shared', 'arkham', 'tas'))


def chapters(data, site):
    return [s for s in data['person']['sections'] if visible(s, site)]


def profile_photo(photo_id, eager=False):
    photo = next(a for a in media_assets() if a['id'] == photo_id)
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    # Only attribution/provenance and licence links leave the reading page.
    return (
        f'<figure class="profile-photo" data-profile-photo="{esc(photo_id)}">'
        f'<img src="/assets/media/{esc(photo["file"])}" width="{photo["width"]}" height="{photo["height"]}" '
        f'alt="{esc(photo["alt"])}" {loading}>'
        f'<figcaption>{esc(photo["caption"])}<span class="profile-photo-credit">'
        f'摄影：{esc(photo["author"])} · <a href="{esc(photo["sourcePage"])}">照片署名与出处</a> · '
        f'<a href="{esc(photo["licenseUrl"])}" rel="license">{esc(photo["license"])}</a> · '
        f'{esc(photo["changes"])}</span></figcaption></figure>'
    )


def reference_rows(data, site):
    person = data['person']
    used = {r for s in chapters(data, site) for r in s['sourceRefs']}
    used.update(r for s in chapters(data, site) for note in s.get('recordingNotes', []) if visible(note, site) for r in note['sourceRefs'])
    used.update(r for event in person['timeline'] if visible(event, site) for r in event['sources'])
    by_id = {s['id']: s for s in data['sources']}
    return [by_id[sid] for sid in person['sources'] if sid in used]


def chapter_citations(data, section, site):
    numbers = {s['id']: n for n, s in enumerate(reference_rows(data, site), 1)}
    return '<p class="profile-citations">资料 ' + ' · '.join(f'[{numbers[r]:02d}]' for r in section['sourceRefs']) + '</p>'


def recording_notes(data, section, site):
    numbers = {s['id']: n for n, s in enumerate(reference_rows(data, site), 1)}
    body = ''
    for note in section.get('recordingNotes', []):
        if not visible(note, site):
            continue
        refs = ' · '.join(f'[{numbers[r]:02d}]' for r in note['sourceRefs'])
        body += f'<aside class="profile-recording-note"><p class="profile-eyebrow">IN THE RECORDING ROOM / 录音笔记</p><h3>{esc(note["title"])}</h3>{paragraphs(note["body"])}<p class="profile-citations">资料 {refs}</p></aside>'
    return body


def profile_sources(data, site='shared'):
    rows = ''.join(
        f'<li><span class="profile-reference-number">[{n:02d}]</span><div><p>{esc(s["title"])}</p>'
        f'<small>{esc(s["type"])}' + (f' · {esc(s["published"])}' if s.get('published') else '') + '</small></div></li>'
        for n, s in enumerate(reference_rows(data, site), 1)
    )
    return '<section class="profile-sources"><h2>人物资料出处</h2><ol class="profile-reference-list">' + rows + '</ol></section>'


def timeline(data, site):
    rows = ''.join(f'<li><span>{esc(e["year"])}</span><p>{esc(e["text"])}</p></li>' for e in data['person']['timeline'] if visible(e, site))
    return '<details class="profile-timeline" open><summary><span>1955—2022</span>生平与作品年表</summary><ol>' + rows + '</ol></details>'


def with_profile_styles(html):
    return html.replace('</head>', '<link rel="stylesheet" href="/assets/conroy-profile.css"></head>', 1)


def cover(title, intro, shared=False):
    lines = ('蝙蝠侠', '之声') if shared else ('凯文·', '康罗伊')
    heading = ''.join(f'<span>{esc(line)}</span>' for line in lines)
    label = '声音人物志 / THE VOICES OF GOTHAM' if shared else '人物档案 / KEVIN CONROY'
    sub = '从动画到阿卡姆' if shared else '1955—2022 · 蝙蝠侠之声'
    tag = 'h2' if shared else 'h1'  # the shared cover sits under the home page's h1
    return (
        '<section class="profile-cover"><div class="profile-cover-meta"><span>BATCAVECN / SPECIAL ARCHIVES</span>'
        '<span>人物 · 声音 · 创作</span></div><div class="profile-cover-grid"><div class="profile-cover-copy">'
        f'<p class="profile-eyebrow">{label}</p><{tag} class="profile-cover-title" aria-label="{esc(title)}">{heading}</{tag}>'
        f'<p class="profile-cover-sub">{sub}</p><p class="profile-cover-intro">{esc(intro)}</p>'
        '<a class="profile-cover-jump" href="#life"><span>01</span> 开始阅读 <span aria-hidden="true">↓</span></a></div>'
        f'<div class="profile-cover-portrait">{profile_photo("conroy-2017", eager=True)}'
        '<p class="profile-cover-signature" aria-hidden="true">KEVIN<br>CONROY<span>THE VOICE BEHIND THE MASK</span></p></div></div></section>'
    )
