"""Conroy's illustrated biography, scoped reading aids and plain-text references."""
import json

from render_common import ROOT, esc, paragraphs, route, external_link_icon


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
        f'<span class="profile-main-action">前往主站{external_link_icon()}</span></a>'
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


def with_profile_styles(html):
    return html.replace('</head>', '<link rel="stylesheet" href="/assets/conroy-profile.css"></head>', 1)


def cover(title, intro, shared=False):
    lines = ('蝙蝠侠', '之声') if shared else ('凯文·', '康罗伊')
    heading = ''.join(f'<span>{esc(line)}</span>' for line in lines)
    label = '声音人物志 / THE VOICES OF GOTHAM' if shared else '人物档案 / KEVIN CONROY'
    sub = '从动画到阿卡姆' if shared else '1955—2022 · 蝙蝠侠之声'
    tag = 'h2' if shared else 'h1'  # the shared cover sits under the home page's h1
    quote = (
        '<blockquote class="profile-cover-quote">'
        '<p class="profile-quote-en">&ldquo;I am vengeance. I am the night. I am Batman!&rdquo;</p>'
        '<p class="profile-quote-cn">&ldquo;我是复仇，我是黑夜，我是蝙蝠侠！&rdquo;</p>'
        '<cite>&mdash;&mdash; 凯文&middot;康罗伊（《动画系列》1992 &middot; 《阿卡姆骑士》2015）</cite>'
        '</blockquote>'
    )
    return (
        '<section class="profile-cover"><div class="profile-cover-meta"><span>BATCAVECN / SPECIAL ARCHIVES</span>'
        '<span>人物 · 声音 · 创作</span></div><div class="profile-cover-grid"><div class="profile-cover-copy">'
        f'<p class="profile-eyebrow">{label}</p><{tag} class="profile-cover-title" aria-label="{esc(title)}">{heading}</{tag}>'
        f'<p class="profile-cover-sub">{sub}</p>{quote}<p class="profile-cover-intro">{esc(intro)}</p>'
        '<a class="profile-cover-jump" href="#life"><span>01</span> 开始阅读 <span aria-hidden="true">↓</span></a></div>'
        f'<div class="profile-cover-portrait">{profile_photo("conroy-2017", eager=True)}'
        '<p class="profile-cover-signature" aria-hidden="true">KEVIN<br>CONROY<span>THE VOICE BEHIND THE MASK</span></p></div></div></section>'
    )


# Chapters that belong to one medium. They sit in a two-lane branch on the shared page.
BRANCH = {'performances': 'tas', 'beyond': 'tas', 'comparison': 'arkham', 'arkham-climax': 'arkham'}
ROUTES = {
    'tas': {'medium': '动画', 'site': 'Dark Deco', 'english': 'ANIMATION', 'image': 'tas-episode-i-am-the-night-01.jpg'},
    'arkham': {'medium': '游戏', 'site': 'Protocol Arkham', 'english': 'GAMES', 'image': 'arkham-knight-03.jpg'},
}
CHAPTER_ENGLISH = {'life': 'EARLY YEARS', 'stage': 'ON THE STAGE', 'voice': 'BECOMING BATMAN', 'ensemble': 'IN THE BOOTH',
                   'performances': 'THE INNER VOICE', 'beyond': 'A LIFETIME IN GOTHAM', 'comparison': 'VOICING THE GAMES',
                   'arkham-climax': 'THE FINAL CRUSADE',
                   'finding': 'FINDING BATMAN', 'audience': 'BEYOND THE MICROPHONE', 'memory': 'THE VOICE REMAINS', 'works': 'SELECTED WORKS'}
CHAPTER_QUOTES = {
    'performances': (
        '&ldquo;I am vengeance. I am the night. I am Batman!&rdquo;',
        '&ldquo;我是复仇，我是黑夜，我是蝙蝠侠！&rdquo;',
        '《无所畏惧》（Nothing to Fear, 1992）&middot; 突破恐惧之音'
    ),
    'comparison': (
        '&ldquo;It&rsquo;s just you in a booth for four-hour sessions doing every possible variation on lines.&rdquo;',
        '&ldquo;只有你独自留在录音棚里，在一次次长达四小时的高压录音中，穷尽每一句台词的所有语气变体。&rdquo;',
        '2011年《WIRED》专访 &middot; 独立录音棚的挑战'
    ),
    'arkham-climax': (
        '&ldquo;Even after everything you&rsquo;ve done, I would have saved you.&rdquo;',
        '&ldquo;即便在你做尽了这一切之后，我也依然会救你。&rdquo;',
        '《蝙蝠侠：阿卡姆之城》（2011）&middot; 最后的底线'
    ),
}


def route_tabs(prefix, label, compact=False):
    """Tab buttons for the two reading routes; app.js reveals them, so pages without JS read both lanes."""
    buttons = ''
    for side, info in ROUTES.items():
        inner = (f'<span class="xroute-tab-medium">{info["medium"]}</span><span class="xroute-tab-site">{info["site"]}</span>' if compact else '')
        buttons += (f'<button class="xroute-tab xroute-tab-{side}" type="button" id="{prefix}-tab-{side}" aria-controls="{prefix}-{side}" '
                    f'data-route-tab="{side}">{inner}')
        if not compact:
            buttons += '{door-' + side + '}'
        buttons += '</button>'
    return f'<div class="xroute-tabs{" is-compact" if compact else ""}" role="tablist" aria-label="{esc(label)}" data-route-ui hidden>{buttons}</div>'


def timeline_tagged(data):
    rows = ''
    for event in data['person']['timeline']:
        scope = [s for s in event.get('sites', ()) if s in ROUTES]
        side = scope[0] if len(scope) == 1 else ''
        tag = f'<em class="xroute-tag">{ROUTES[side]["medium"]}</em>' if side else ''
        rows += f'<li{f" data-route-item={chr(34)}{side}{chr(34)}" if side else ""}><span>{esc(event["year"])}</span><p>{tag}{esc(event["text"])}</p></li>'
    return '<details class="profile-timeline" open><summary><span>1955—2022</span>生平与作品年表</summary><ol>' + rows + '</ol></details>'


def route_works(data, section):
    linked = [i for i in data['games'] + data['episodes'] + data['tnbaEpisodes'] if i['actor'] == 'Kevin Conroy' and i['status'] == '详情样板']
    animation = [i for i in linked if i['site'] == 'tas']
    games = sorted((i for i in linked if i['site'] == 'arkham'), key=lambda i: i.get('date') or i['year'])
    series_names = {'BTAS': ('蝙蝠侠：动画系列', 'Batman: The Animated Series'), 'TNBA': ('蝙蝠侠新冒险', 'The New Batman Adventures')}
    groups = [(series, sorted((i for i in animation if i.get('series') == series), key=lambda i: i.get('airDate') or i['year'])) for series in series_names]
    groups = [(series, episodes) for series, episodes in groups if episodes]

    def rows(works):
        return ''.join(f'<li><span class="xc-year">{esc(i["year"])}</span><a href="{route(i)}">{esc(i["title"])}</a>'
                       f'<span class="xc-note">{esc(i["original"])}</span></li>' for i in works)

    series_rows = ''.join(f'<li><span class="xc-year">{len(episodes)}集</span><a href="/tas/catalog/#{series.lower()}">{esc(series_names[series][0])}</a>'
                          f'<span class="xc-note">{esc(series_names[series][1])}</span></li>' for series, episodes in groups)
    standalone = [i for i in animation if i.get('series') not in series_names]
    directory = ''.join(f'<div class="profile-episode-group"><h3>{series} · {len(episodes)}集</h3><ol class="work-list profile-episode-list">{rows(episodes)}</ol></div>'
                        for series, episodes in groups)
    count = sum(len(episodes) for _, episodes in groups)
    lists = {
        'tas': f'<ol class="work-list">{series_rows}{rows(standalone)}</ol><details class="profile-episode-directory"><summary>展开动画分集目录 · {count}集</summary>{directory}</details>',
        'arkham': f'<ol class="work-list">{rows(games)}</ol>',
    }
    panels = ''.join(
        f'<div class="xroute-works-panel xroute-skin-{side}" id="works-{side}" data-route-panel="{side}">'
        f'<p class="xroute-lane-label"><span>{info["medium"]}</span>{info["site"]}</p>'
        f'{paragraphs(section["siteBodies"][side])}{lists[side]}</div>'
        for side, info in ROUTES.items()
    )
    return f'<div class="profile-works xroute-works">{route_tabs("works", "作品目录", compact=True)}{panels}</div>'


def door(side, chapters_in_lane, number):
    info = ROUTES[side]
    titles = ''.join(f'<span><b>{number}.{k}</b>{esc(s["title"].split(" / ", 1)[-1])}</span>' for k, s in enumerate(chapters_in_lane, 1))
    media = {a['file']: a for name in ('media.json', 'episode-media.json') for a in json.loads((ROOT / name).read_text())['assets']}[info['image']]
    return (f'<span class="xroute-door-image"><img src="/assets/media/{info["image"]}" width="{media["width"]}" height="{media["height"]}" alt="" aria-hidden="true" loading="lazy"></span>'
            f'<span class="xroute-door-copy"><span class="xroute-door-label">{info["english"]} / {info["site"].upper()}</span>'
            f'<span class="xroute-door-medium">{info["medium"]}</span><span class="xroute-door-chapters">{titles}</span></span>')


def voices_chapters(data):
    """Shared Conroy feature: common chapters, a two-lane branch for animation and games, then the shared ending."""
    sections = chapters(data, 'shared')
    common = [s for s in sections if s['id'] not in BRANCH]
    branch_at = next(i for i, s in enumerate(common) if s['id'] == 'ensemble') + 1
    branch_number = f'{branch_at + 1:02d}'
    numbers = {s['id']: f'{n:02d}' for n, s in enumerate(common[:branch_at], 1)}
    numbers.update({s['id']: f'{n:02d}' for n, s in enumerate(common[branch_at:], branch_at + 2)})
    lanes = {side: [s for s in sections if BRANCH.get(s['id']) == side] for side in ROUTES}
    for side, lane in lanes.items():
        numbers.update({s['id']: f'{branch_number}.{k}' for k, s in enumerate(lane, 1)})

    def title_of(s):
        return s['title'].split(' / ', 1)[-1]

    def link(s, prefix=''):
        route_attr = f' data-route-link="{BRANCH[s["id"]]}"' if s['id'] in BRANCH else ''
        title = f'<strong class="xroute-toc-title">{prefix}{esc(title_of(s))}</strong>' if prefix else esc(title_of(s))
        return f'<li><a href="#{s["id"]}"{route_attr}><span>{numbers[s["id"]]}</span>{title}</a></li>'

    groups = [('I', '面具之前', common[:3]), ('II', '声音的工作', common[3:branch_at]), ('III', '生活与回声', common[branch_at:])]
    contents = ''
    for number, label, items in groups:
        contents += f'<div><p><span>{number}</span>{label}</p><ol>' + ''.join(link(s) for s in items)
        if number == 'II':
            contents += (f'<li class="profile-contents-branch"><a href="#routes"><span>{branch_number}</span>分岔：动画与游戏</a><ol>'
                         + ''.join(link(s, f'<em class="xroute-tag">{ROUTES[side]["medium"]}</em>') for side, lane in lanes.items() for s in lane) + '</ol></li>')
        contents += '</ol></div>'

    def chapter(s):
        number = numbers[s['id']]
        if s['id'] == 'finding':
            return finding_feature(number)
        quote_html = ''
        if s['id'] in CHAPTER_QUOTES:
            en, cn, cite = CHAPTER_QUOTES[s['id']]
            quote_html = (
                f'<blockquote class="profile-chapter-quote">'
                f'<p class="profile-quote-en">{en}</p>'
                f'<p class="profile-quote-cn">{cn}</p>'
                f'<cite>{cite}</cite>'
                f'</blockquote>'
            )
        html = (f'<section class="profile-chapter profile-chapter-{s["id"]}" id="{s["id"]}"><div class="profile-chapter-heading">'
                f'<span class="profile-chapter-number" aria-hidden="true">{number}</span><p class="profile-eyebrow">{CHAPTER_ENGLISH[s["id"]]}</p>'
                f'<h2>{esc(title_of(s))}</h2></div><div class="profile-chapter-copy">{quote_html}{paragraphs(s["body"])}')
        if s['id'] == 'voice':
            html += '<div class="profile-voice-pair"><div><p>BRUCE WAYNE</p><h3>在人群之中</h3><span>轻松、圆滑的公众形象</span></div><div><p>BATMAN</p><h3>在面罩之后</h3><span>压低声音，让话语更有重量</span></div></div>'
        html += chapter_citations(data, s, 'shared') + recording_notes(data, s, 'shared')
        if s['id'] == 'works':
            html += route_works(data, s)
        html += '</div>' + ''.join(profile_photo(photo) for photo in s.get('photos', [])) + '</section>'
        if s['id'] == 'memory':
            html += timeline_tagged(data)
        return html

    branch_intro = ('动画一线写康罗伊如何把角色的内心戏和年长的布鲁斯演出来；游戏一线写他在阿卡姆系列里独自录音的工作方式。'
                    '选一条线读下去，随时可以换到另一条。')
    tabs = route_tabs('route', '选择阅读路线')
    for side, lane in lanes.items():
        tabs = tabs.replace('{door-' + side + '}', door(side, lane, branch_number))
    lane_html = ''
    for side, lane in lanes.items():
        other = next(o for o in ROUTES if o != side)
        info = ROUTES[side]
        switch = (f'<button class="xroute-switch" type="button" data-route-switch="{other}" data-route-ui hidden>'
                  f'<span>换到{ROUTES[other]["medium"]}线</span>{esc(title_of(lanes[other][0]))}<span aria-hidden="true">→</span></button>')
        lane_html += (f'<div class="xroute-lane xroute-skin-{side}" id="route-{side}" data-route-panel="{side}">'
                      f'<p class="xroute-lane-label"><span>{info["medium"]}</span>{info["site"]} · {len(lane)}章</p>'
                      + ''.join(chapter(s) for s in lane) + switch + '</div>')
    branch = (f'<section class="xroute" id="routes" data-voice-routes aria-labelledby="routes-title"><div class="xroute-head">'
              f'<span class="profile-chapter-number" aria-hidden="true">{branch_number}</span><p class="profile-eyebrow">TWO BOOTHS / 分岔阅读</p>'
              f'<h2 id="routes-title">动画与游戏，两条录音线</h2><p>{branch_intro}</p></div>{tabs}{lane_html}'
              '<p class="xroute-merge"><span>两条线在这里汇合</span></p></section>')

    body = '<nav class="profile-contents" aria-label="人物章节">' + contents + '</nav><div class="reading conroy-reading">'
    for i, s in enumerate(common):
        if i == branch_at:
            body += branch
        body += chapter(s)
    return body + '</div>'
