"""Conroy's illustrated biography, scoped reading aids and plain-text references."""
import json

from render_common import ROOT, esc


def media_assets():
    return json.loads((ROOT / 'conroy-media.json').read_text())['assets']


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
    used.update(r for event in person['timeline'] if visible(event, site) for r in event['sources'])
    by_id = {s['id']: s for s in data['sources']}
    return [by_id[sid] for sid in person['sources'] if sid in used]


def chapter_citations(data, section, site):
    numbers = {s['id']: n for n, s in enumerate(reference_rows(data, site), 1)}
    return '<p class="profile-citations">资料 ' + ' · '.join(f'[{numbers[r]:02d}]' for r in section['sourceRefs']) + '</p>'


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
    return (
        '<section class="profile-cover"><div class="profile-cover-meta"><span>BATCAVECN / SPECIAL ARCHIVES</span>'
        '<span>人物 · 声音 · 创作</span></div><div class="profile-cover-grid"><div class="profile-cover-copy">'
        f'<p class="profile-eyebrow">{label}</p><h1 aria-label="{esc(title)}">{heading}</h1>'
        f'<p class="profile-cover-sub">{sub}</p><p class="profile-cover-intro">{esc(intro)}</p>'
        '<a class="profile-cover-jump" href="#life"><span>01</span> 开始阅读 <span aria-hidden="true">↓</span></a></div>'
        f'<div class="profile-cover-portrait">{profile_photo("conroy-2017", eager=True)}'
        '<p class="profile-cover-signature" aria-hidden="true">KEVIN<br>CONROY<span>THE VOICE BEHIND THE MASK</span></p></div></div></section>'
    )
