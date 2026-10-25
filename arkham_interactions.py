"""Interactive investigations, patient listening terminal and intercepted transmissions."""
import json
import math
from render_common import ROOT, esc, paragraphs
from patient_player import recording_controls
from transmission_player import transmission_controls
from arkham_icons import icon


TERMINALS = [('/arkham/detective/', 'evidence', '案件重建'), ('/arkham/patients/', 'patient', '患者终端'), ('/arkham/transmissions/', 'radio', '频段监听')]
# Interface positions, independent of the source recordings' frequency fields.
TUNING_POSITIONS = {
    'joker-city': (24, 34), 'sharp-city': (62, 22), 'zsasz-city': (78, 70),
    'knight-oracle': (14, 20), 'knight-scarecrow': (44, 15),
    'knight-harley': (78, 18), 'knight-riddler': (25, 48),
    'knight-penguin': (60, 46), 'knight-stagg': (87, 53),
    'knight-joker-case': (35, 80), 'knight-pyg': (74, 82),
}


def terminal_bar(current):
    """Bottom bar shared by the three terminals: back, switch terminal, key hint."""
    links = ''.join(f'<a href="{href}"' + (' aria-current="page"' if href == current else '') + f'><i data-arkham-icon="{icon}"></i>{title}</a>' for href, icon, title in TERMINALS)
    return f'<nav class="terminal-bar" aria-label="切换终端"><a class="terminal-back" href="/arkham/archive/">← 哥谭档案馆</a><span class="terminal-switch"><span class="terminal-switch-label">TERMINALS</span>{links}</span><a class="terminal-esc" href="/arkham/menu/"><kbd>Esc</kbd> 主菜单</a></nav>'


def build_interactions(data, shell):
    research = json.loads((ROOT / 'riddler-research.json').read_text())
    archive = json.loads((ROOT / 'arkham-archive-research.json').read_text())
    patients = json.loads((ROOT / 'patient-interviews.json').read_text())
    transmissions = json.loads((ROOT / 'arkham-transmissions.json').read_text())
    portraits = json.loads((ROOT / 'recording-portraits.json').read_text())
    portrait_assets = {asset['id']: asset for asset in portraits['assets']}
    assert set(portraits['patients']) == {patient['id'] for patient in patients['patients']}
    assert set(portraits['channels']) == {channel['id'] for channel in transmissions['channels']}
    cases = json.loads((ROOT / 'arkham-interactions.json').read_text())['cases']
    sources = {s['id']: s for packet in (research, archive, patients, transmissions) for s in packet['sources']}
    images = {i['id']: i for i in research['images']}
    entries = {e['id']: e for e in research['entries']}
    topics = {c['id']: c for c in research['cases']}
    records = []

    def portrait(group, record_id, small=False):
        asset = portrait_assets[portraits[group][record_id]]
        classes = 'recording-portrait' + (' recording-portrait--small' if small else '')
        alt = '' if small else asset['alt']
        return f'<img class="{classes}" src="/assets/media/{esc(asset["file"])}" width="{asset["width"]}" height="{asset["height"]}" alt="{esc(alt)}" loading="lazy" decoding="async">'

    def links(items):
        return '<div class="terminal-links">' + ''.join(f'<a href="{esc(i["url"])}">{esc(i["title"])}</a>' for i in items) + '</div>'

    def record(title, summary, url):
        records.append(dict(title=title, original=title, summary=summary, tags=['调查终端'], site='arkham', status='互动档案', url=url))

    def page(title, body, sequencer=False):
        extra = '<script src="/assets/arkham-sequencer.js" defer></script>' if sequencer else ''
        return shell(data, 'arkham', title, body, 'archive').replace('</head>', '<link rel="stylesheet" href="/assets/arkham-investigation.css">' + extra + '<script src="/assets/arkham-investigation.js" defer></script></head>')

    case_data = []
    fallback = ''
    for n, c in enumerate(cases, 1):
        assert c['entry'] in entries and c['research'] in topics
        image = images[c['image']]
        assert c['entry'] in topics[c['research']]['entries']
        assert c['image'] in topics[c['research']]['images']
        assert 0 <= c['hotspot']['x'] <= 100 and 0 <= c['hotspot']['y'] <= 100
        for e in c['evidence']:
            assert set(e['sources']) <= sources.keys()
        item = dict(c, number=f'{n:02d}', src='/assets/media/' + image['file'], width=image['width'], height=image['height'], caption=image['caption'])
        item['evidence'] = [dict(e, linksHtml=links(e['links']), iconHtml=icon('evidence' if index == 0 else 'dossiers')) for index, e in enumerate(c['evidence'])]
        case_data.append(item)
        fallback += f'<article id="case-{esc(c["id"])}"><h2>{esc(c["title"])}</h2><p>{esc(c["game"])} · {esc(c["region"])}</p><img src="{item["src"]}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["caption"])}">' + ''.join(f'<h3>{esc(e["title"])}</h3>{paragraphs(e["body"])}{links(e["links"])}' for e in c['evidence']) + f'<h3>案件总结</h3>{paragraphs(c["summary"])}</article>'
        record(c['title'] + ' · 案件重建', c['subtitle'], '/arkham/detective/#case-' + c['id'])

    payload = json.dumps(case_data, ensure_ascii=False).replace('<', '\\u003c')
    first = case_data[0]
    tabs = ''.join(f'<a href="#case-{esc(c["id"])}" data-case="{esc(c["id"])}"><span>{c["number"]}</span>{esc(c["title"])}</a>' for c in case_data)
    detective = f'''<section class="section arkham-investigation" data-detective>
<div class="terminal-heading"><p class="label"><i data-arkham-icon="evidence"></i>BATCOMPUTER / DETECTIVE MODE</p><h1>现场案件重建</h1><p class="lead">锁定关键物证，沿物证链推演现场始末与嫌犯心理侧写。</p><p class="fine">机密案件调查 · 含现场物证分析与嫌犯身份档案</p></div>
<nav class="case-register" aria-label="选择调查">{tabs}</nav>
<div class="investigation-workspace" hidden data-workspace>
<section class="scene-console"><div class="console-bar"><span data-case-number>CASE 01</span><button type="button" class="terminal-motion" data-motion aria-pressed="true">终端动效：开</button><span data-mode-label>NORMAL VISION</span></div><h2 data-case-title>{esc(first['title'])}</h2><p class="scene-location" data-location>{esc(first['game'])} · {esc(first['region'])}</p>
<div class="scan-controls scene-toolbar"><button type="button" data-mode aria-pressed="false">激活侦探模式 <small>ACTIVATE DETECTIVE MODE</small></button><span data-progress role="status">0 / 3 条证据</span><p class="terminal-feedback" data-feedback role="status">普通视野 · 激活侦探模式以锁定现场物证</p></div>
<div class="investigation-scene" data-scene><img data-scene-image src="{first['src']}" width="{first['width']}" height="{first['height']}" alt="{esc(first['caption'])}"><div class="scan-grid" aria-hidden="true"></div><button type="button" class="scan-hotspot" data-scan hidden aria-label="扫描现场物件"><span>01</span><small>SCAN</small></button></div></section>
<aside class="evidence-console" aria-label="证据详情"><p class="label">EVIDENCE CHAIN / 现场物证与关联档案</p><div class="evidence-chain" data-evidence-chain></div><div data-evidence-panel><p class="evidence-id" data-evidence-label>AWAITING SCAN</p><h2 data-evidence-title>现场等待扫描</h2><div data-evidence-body><p>激活侦探模式，选择画面中的扫描点。</p></div><div data-evidence-links></div></div></aside></div>
<section class="case-summary" data-summary hidden><p class="label">CASE SUMMARY / 调查完成</p><h2>物证链已闭合，案情重建完成</h2><p data-summary-text></p><div class="terminal-links"><a href="/arkham/archive/riddler/" data-summary-link>查阅关联机密档案</a><button type="button" data-reset>重置本案调查</button></div></section>
<div class="terminal-fallback" data-case-fallback>{fallback}</div>
{terminal_bar("/arkham/detective/")}
<script type="application/json" data-case-data>{payload}</script></section>'''

    def make_nab_spool(is_left=True, uid='spool'):
        tape_r = 78 if is_left else 55
        holes_d = []
        for center_deg in [-90, 30, 150]:
            s_deg = center_deg - 26
            e_deg = center_deg + 26
            rad_s, rad_e = math.radians(s_deg), math.radians(e_deg)
            x1, y1 = 100 + 75 * math.cos(rad_s), 100 + 75 * math.sin(rad_s)
            x2, y2 = 100 + 75 * math.cos(rad_e), 100 + 75 * math.sin(rad_e)
            x3, y3 = 100 + 42 * math.cos(rad_e), 100 + 42 * math.sin(rad_e)
            x4, y4 = 100 + 42 * math.cos(rad_s), 100 + 42 * math.sin(rad_s)
            holes_d.append(f"M {x1:.1f} {y1:.1f} A 75 75 0 0 1 {x2:.1f} {y2:.1f} L {x3:.1f} {y3:.1f} A 42 42 0 0 0 {x4:.1f} {y4:.1f} Z")
        holes_path = " ".join(holes_d)

        screws = []
        for deg in [-30, 90, 210]:
            rad = math.radians(deg)
            sx, sy = 100 + 83 * math.cos(rad), 100 + 83 * math.sin(rad)
            screws.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.8" fill="#4a5456" stroke="#1b1d1e" stroke-width="0.8"/><line x1="{sx-1.8:.1f}" y1="{sy:.1f}" x2="{sx+1.8:.1f}" y2="{sy:.1f}" stroke="#1b1d1e" stroke-width="0.8"/>')
        screws_svg = "".join(screws)

        ticks = []
        for i in range(24):
            deg = i * 15
            rad = math.radians(deg)
            x1, y1 = 100 + 91 * math.cos(rad), 100 + 91 * math.sin(rad)
            x2, y2 = 100 + 94.5 * math.cos(rad), 100 + 94.5 * math.sin(rad)
            stroke_w = "1.2" if i % 6 == 0 else "0.6"
            stroke_col = "#677477" if i % 6 == 0 else "#383f40"
            ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_col}" stroke-width="{stroke_w}"/>')
        ticks_svg = "".join(ticks)

        return f'''<svg class="reel-spool-svg" viewBox="0 0 200 200" aria-hidden="true">
<defs>
<radialGradient id="al-flange-{uid}" cx="45%" cy="40%" r="60%">
<stop offset="0%" stop-color="#373e40"/>
<stop offset="45%" stop-color="#1e2223"/>
<stop offset="75%" stop-color="#313839"/>
<stop offset="100%" stop-color="#151718"/>
</radialGradient>
<radialGradient id="tape-pack-{uid}" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="#301a0f"/>
<stop offset="50%" stop-color="#20110a"/>
<stop offset="85%" stop-color="#2a160d"/>
<stop offset="100%" stop-color="#150a05"/>
</radialGradient>
<radialGradient id="hub-met-{uid}" cx="40%" cy="35%" r="65%">
<stop offset="0%" stop-color="#4b5456"/>
<stop offset="60%" stop-color="#252a2b"/>
<stop offset="100%" stop-color="#131515"/>
</radialGradient>
<mask id="mask-{uid}">
<rect width="200" height="200" fill="white"/>
<path d="{holes_path}" fill="black"/>
</mask>
</defs>
<circle cx="100" cy="100" r="96" fill="#0c0c0b"/>
<circle cx="100" cy="100" r="{tape_r}" fill="url(#tape-pack-{uid})"/>
<circle cx="100" cy="100" r="{tape_r - 8}" fill="none" stroke="#381f12" stroke-width="0.7" stroke-dasharray="3 2"/>
<circle cx="100" cy="100" r="{tape_r - 18}" fill="none" stroke="#381f12" stroke-width="0.7" stroke-dasharray="4 2"/>
<circle cx="100" cy="100" r="96" fill="url(#al-flange-{uid})" mask="url(#mask-{uid})" stroke="#5d686b" stroke-width="1.8"/>
<circle cx="100" cy="100" r="90" fill="none" stroke="#242829" stroke-width="1" mask="url(#mask-{uid})"/>
<path d="{holes_path}" fill="none" stroke="#5d686b" stroke-width="1.4" opacity="0.85"/>
{ticks_svg}
{screws_svg}
<circle cx="100" cy="100" r="36" fill="url(#hub-met-{uid})" stroke="#626d70" stroke-width="1.5"/>
<circle cx="100" cy="100" r="28" fill="none" stroke="#313839" stroke-width="1.2"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#111313" stroke="#444c4e" stroke-width="0.8"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#111313" stroke="#444c4e" stroke-width="0.8" transform="rotate(120 100 100)"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#111313" stroke="#444c4e" stroke-width="0.8" transform="rotate(240 100 100)"/>
<circle cx="100" cy="100" r="16" fill="#1c1f20" stroke="#828f92" stroke-width="1.2"/>
<circle cx="100" cy="100" r="7" fill="#090908" stroke="#535d5f" stroke-width="1"/>
</svg>'''

    VU_SCALE_SVG = '''<svg viewBox="0 0 110 44" class="vu-scale-svg" aria-hidden="true">
<path d="M 10 38 A 60 60 0 0 1 100 38" fill="none" stroke="#2b3132" stroke-width="2"/>
<path d="M 76 21 A 60 60 0 0 1 100 38" fill="none" stroke="#d94b38" stroke-width="2.2"/>
<line x1="16" y1="33" x2="19" y2="30" stroke="#586365" stroke-width="1"/>
<line x1="32" y1="26" x2="34" y2="23" stroke="#586365" stroke-width="1"/>
<line x1="52" y1="21" x2="53" y2="18" stroke="#586365" stroke-width="1.2"/>
<line x1="76" y1="21" x2="77" y2="18" stroke="#d94b38" stroke-width="1.4"/>
<line x1="92" y1="28" x2="94" y2="25" stroke="#d94b38" stroke-width="1.4"/>
<text x="18" y="40" fill="#5d686a" font-size="6" font-family="monospace">-20</text>
<text x="50" y="29" fill="#5d686a" font-size="6" font-family="monospace">-5</text>
<text x="74" y="27" fill="#d94b38" font-size="7" font-weight="bold" font-family="monospace">0</text>
<text x="94" y="36" fill="#d94b38" font-size="6" font-weight="bold" font-family="monospace">+3</text>
</svg>'''

    BARCODE_SVG = '<svg viewBox="0 0 140 22" class="inmate-barcode-svg" aria-hidden="true">' + ''.join(
        f'<rect x="{x}" y="0" width="{w}" height="22" fill="#4d5658"/>'
        for x, w in [(4, 2), (8, 4), (14, 1), (17, 3), (22, 1), (25, 4), (31, 2), (35, 1), (38, 4), (44, 2), (48, 1), (51, 3), (56, 4), (62, 1), (65, 3), (70, 2), (74, 4), (80, 1), (83, 3), (88, 2), (92, 4), (98, 1), (101, 3), (106, 2), (110, 4), (116, 2), (120, 1), (123, 3), (128, 4), (134, 2)]
    ) + '</svg>'

    def game_tabs(games):
        return '<nav class="recording-game-tabs" aria-label="选择游戏" hidden>' + ''.join(f'<button type="button" data-recording-game="{esc(key)}" aria-pressed="{str(n == 0).lower()}">{esc(title)}</button>' for n, (key, title) in enumerate(games)) + '</nav>'

    registers = ''
    panels = ''
    for n, p in enumerate(patients['patients'], 1):
        assert set(p['sources']) <= sources.keys()
        game_id = p.get('gameId', 'asylum')
        game_name = p.get('game', '阿卡姆疯人院')
        uid_l = f"p{n}-l"
        uid_r = f"p{n}-r"
        spool_l = make_nab_spool(True, uid_l)
        spool_r = make_nab_spool(False, uid_r)
        registers += f'<a href="#patient-{p["id"]}" data-patient="{p["id"]}" data-game="{game_id}"><span class="patient-slot-num">{n:02d}</span>{portrait("patients", p["id"], small=True)}<span class="patient-slot-info"><strong>{esc(p["name"])}</strong><small>{esc(p["english"])}</small></span><span class="patient-slot-status"><span class="inmate-status-pip" aria-hidden="true"></span><span class="patient-tape-pips" aria-hidden="true">{"■" * len(p["tapes"])}</span></span></a>'
        panels += f'''<article class="patient-file" id="patient-{p['id']}" data-patient-file="{p['id']}" data-game="{game_id}" data-audio-recording>
<span class="chassis-bolt bolt-tl" aria-hidden="true"></span>
<span class="chassis-bolt bolt-tr" aria-hidden="true"></span>
<span class="chassis-bolt bolt-bl" aria-hidden="true"></span>
<span class="chassis-bolt bolt-br" aria-hidden="true"></span>
<div class="console-bar">
<div class="console-case-track">
<span class="case-badge">RECORD INDEX {n:02d} // SEC-0{n}</span>
<span class="dept-badge">PSYCHIATRIC EVALUATION DIVISION</span>
</div>
<span class="security-level">{esc(game_name)} // MAXIMUM SECURITY</span>
</div>
<div class="patient-identity">
<div class="patient-monogram-frame">
{portrait('patients', p['id'])}
<span class="monogram-tag" aria-hidden="true">INMATE #{1000 + n * 137}</span>
</div>
<div class="patient-dossier-meta">
<div class="patient-meta-header">
<p class="label">PATIENT INTERVIEW // PSYCHIATRIC EVALUATION</p>
<div class="security-badges">
<span class="threat-badge" aria-hidden="true">SECURITY CLEARANCE LEVEL 4</span>
<span class="containment-badge" aria-hidden="true">MAX-SECURITY</span>
</div>
</div>
<h2>{esc(p['name'])}</h2>
<p class="patient-en-name">{esc(p['english'])}</p>
<div class="inmate-telemetry-strip">
<div class="barcode-card">{BARCODE_SVG}<code>ARK-PSY-770{n}-X</code></div>
<p class="fine identity-tag">身份索引：<strong>{esc(p['identity'])}</strong></p>
</div>
</div>
<div class="dossier-stamp-seal" aria-hidden="true">
<div class="stamp-inner">
<span>ARKHAM ASYLUM</span>
<strong>CLASSIFIED</strong>
<small>RESTRICTED ARCHIVE</small>
</div>
</div>
</div>
<div class="listening-question">
<div class="observation-header">
<p class="label">CLINICAL OBSERVATION // 临床聆听导读</p>
<span class="observation-tag" aria-hidden="true">DIRECT EVALUATION</span>
</div>
<p>{esc(p['angle'])}</p>
</div>
<details class="spoiler patient-recording">
<summary>访谈导读与原声 · 含剧透</summary>
{recording_controls(p, compact=True)}
<div class="tape-console">
<div class="tape-deck-housing">
<span class="chassis-screw screw-tl" aria-hidden="true"></span>
<span class="chassis-screw screw-tr" aria-hidden="true"></span>
<span class="chassis-screw screw-bl" aria-hidden="true"></span>
<span class="chassis-screw screw-br" aria-hidden="true"></span>
<div class="tape-deck-topbar">
<div class="deck-brand-block">
<span class="deck-badge-rivet"></span>
<span class="tape-deck-brand">ARKHAM SANITARIUM PSYCHIATRIC RECORDING DECK</span>
<span class="deck-badge-rivet"></span>
</div>
<div class="deck-specs">
<span class="tape-deck-speed">7.5 IPS · HI-FI TAPE</span>
<span class="tape-deck-serial">MODEL AS-REC-709</span>
</div>
</div>
<div class="tape-reels" aria-hidden="true">
<span class="spool spool-left">{spool_l}</span>
<div class="tape-bridge">
<span class="tension-arm tension-left"><span class="tension-roller"></span></span>
<i class="tape-ribbon"></i>
<div class="tape-head-block">
<div class="head-top-plate">
<span class="head-plate-label">HEAD ASSEMBLY</span>
<span class="azimuth-screw"></span>
</div>
<div class="head-cluster">
<div class="head-unit head-erase"><span class="head-core"></span><small>ERASE</small></div>
<div class="head-unit head-rec"><span class="head-core"></span><small>REC</small></div>
<div class="head-unit head-play"><span class="head-core"></span><small>PLAY</small></div>
</div>
<div class="tape-lifter-bar"><span class="lifter-pin"></span><span class="lifter-pin"></span></div>
</div>
<div class="capstan-assembly">
<span class="capstan-shaft"></span>
<span class="pinch-roller"><span class="pinch-cap"></span></span>
</div>
<span class="tension-arm tension-right"><span class="tension-roller"></span></span>
</div>
<span class="spool spool-right">{spool_r}</span>
</div>
<div class="tape-deck-meter-panel" aria-hidden="true">
<div class="vu-meter-pair">
<div class="vu-meter vu-left">
<div class="vu-dial">
<div class="vu-glass-glare"></div>
{VU_SCALE_SVG}
<span class="vu-needle needle-ch1"></span>
<span class="vu-pivot"></span>
<span class="vu-peak-led peak-ch1"></span>
</div>
<span class="vu-title">CH 1 // INPUT</span>
</div>
<div class="vu-meter vu-right">
<div class="vu-dial">
<div class="vu-glass-glare"></div>
{VU_SCALE_SVG}
<span class="vu-needle needle-ch2"></span>
<span class="vu-pivot"></span>
<span class="vu-peak-led peak-ch2"></span>
</div>
<span class="vu-title">CH 2 // OUTPUT</span>
</div>
</div>
<div class="tape-deck-telemetry">
<div class="tape-counter-box">
<div class="counter-header"><small>TAPE INDEX</small><span class="counter-reset-dot" title="Reset Counter"></span></div>
<div class="tape-counter"><span class="odo-slot">0</span><span class="odo-slot">0</span><span class="odo-div">:</span><span class="odo-slot">0</span><span class="odo-slot">0</span></div>
</div>
<div class="deck-pilot-group">
<div class="pilot-jewel lamp-pwr"><span class="pwr-led"></span><small>PWR</small></div>
<div class="pilot-jewel lamp-rec"><span class="tape-rec-led">● REC</span><small>REC</small></div>
</div>
<div class="deck-switch-group">
<div class="switch-toggle"><span class="toggle-bar"></span><small>7.5 IPS</small></div>
<div class="switch-toggle"><span class="toggle-bar"></span><small>NAB</small></div>
</div>
</div>
</div>
</div>
<div class="tape-console-sidebar">
<div class="sidebar-header">
<p class="label">TRANSCRIPTION DECK // 实体机芯遥测</p>
<span class="deck-mode-badge" aria-hidden="true">REPRO</span>
</div>
<div class="sidebar-telemetry-box" aria-hidden="true">
<div class="telemetry-row"><span class="t-key">TRANSPORT</span><span class="t-val">SERVO LOCKED</span></div>
<div class="telemetry-row"><span class="t-key">TAPE SPEED</span><span class="t-val">7.5 IPS / 19cm/s</span></div>
<div class="telemetry-row"><span class="t-key">EQUALIZATION</span><span class="t-val">NAB 50µs</span></div>
<div class="telemetry-row"><span class="t-key">SIGNAL AUDIO</span><span class="t-val">44.1kHz ARCHIVE</span></div>
</div>
<div class="playback-state-wrapper">
<span class="state-led-pip" aria-hidden="true"></span>
<p class="playback-state" data-playback-state role="status">等待播放</p>
</div>
</div>
</div>
{paragraphs(p['gist'])}

</details>
</article>'''
        records.append(dict(title=p['name'] + ' · ' + game_name + '访谈', original=p['english'] + ' · Patient Interviews', summary=p['angle'], tags=['调查终端', '患者访谈', '原声录音', game_name, p['english']], site='arkham', status='互动档案', url='/arkham/patients/#patient-' + p['id']))
    terminal = f'''<section class="section arkham-investigation arkham-patient-terminal" data-patient-terminal>
<div class="terminal-heading">
<div class="terminal-heading-tags">
<p class="label"><i data-arkham-icon="patient"></i>ARKHAM // PATIENT INTERVIEW ARCHIVE</p>
<span class="system-status-pips" aria-hidden="true">{len(patients["patients"])} SUBJECT FILES · LEVEL 4 RESTRICTED</span>
</div>
<h1>患者终端</h1>
<p class="lead">调取阿卡姆收治档案，审查临床问诊录音与罪犯心理防御机制。</p>
<p class="fine">《疯人院》35 盘 · 《之城》34 盘 · 选择游戏与角色收听原声</p>
</div>
{game_tabs([("asylum", "阿卡姆疯人院"), ("city", "阿卡姆之城")])}
<div class="patient-workspace">
<nav class="patient-selector" aria-label="选择患者">{registers}</nav>
<div class="patient-files">{panels}</div>
</div>
{terminal_bar("/arkham/patients/")}
</section>'''
    record('案件重建 · Detective Mode', '扫描现场物证，沿物证链推演案情始末与嫌犯背景。', '/arkham/detective/')
    record('患者终端', '《疯人院》与《之城》的患者访谈原声与导读。', '/arkham/patients/')

    channels = transmissions['channels']
    assert set(TUNING_POSITIONS) == {ch['id'] for ch in channels}
    tuning_data = json.dumps([dict(id=ch['id'], game=ch['gameId'], title=ch['title'], x=TUNING_POSITIONS[ch['id']][0], y=TUNING_POSITIONS[ch['id']][1]) for ch in channels], ensure_ascii=False).replace('<', '\\u003c')
    channel_cards = ''
    panels_trans = ''
    for n, ch in enumerate(channels, 1):
        assert set(ch['sources']) <= sources.keys()
        actor_note = ' · 配音：' + ch['actor'] if ch.get('actor') else ''
        channel_cards += f'<a class="transmission-channel-card" href="#channel-{ch["id"]}" data-channel="{ch["id"]}" data-game="{ch["gameId"]}">{portrait("channels", ch["id"], small=True)}<div><p class="label">CHANNEL: {esc(ch["frequency"])}</p><h3>{esc(ch["title"])}</h3><p>{esc(ch["game"])} · {esc(ch["speaker"])}</p></div></a>'
        track_rows = ''.join(
            f'<tr><td>{t["number"]:02d}</td><td><strong>{esc(t["title"])}</strong><br><small>{esc(t["englishTitle"])}</small></td><td>{esc(t["phase"])}</td><td>{int(t["duration"])//60}:{int(t["duration"])%60:02d}</td></tr>'
            for t in ch['tracks']
        )
        panels_trans += f'''<article class="transmission-file" id="channel-{ch['id']}" data-transmission-channel="{ch['id']}" data-game="{ch['gameId']}" data-audio-recording>
<div class="console-bar"><span>CRYPTOGRAPHIC SEQUENCER · CHANNEL {esc(ch['frequency'])}</span><span>{esc(ch['game'])}</span></div>
<div class="patient-identity">
{portrait('channels', ch['id'])}
<div><p class="label">INTERCEPTED FREQUENCY · 截获通信</p><h2>{esc(ch['title'])}</h2><p>{esc(ch['englishTitle'])}</p><p class="fine">发信人：{esc(ch['speaker'])} ({esc(ch['speakerEnglish'])}){esc(actor_note)} · {esc(ch['device'])}</p></div>
</div>
<details class="spoiler transmission-recording"><summary>原声与录音导读 · 含剧透</summary>
{transmission_controls(ch)}
<div class="listening-question"><p class="label">TRANSMISSION OVERVIEW / 信道背景</p><p>{esc(ch['summary'])}</p></div>
<div class="transmission-lore">
<p class="label">TACTICAL ANALYSIS / 叙事解构与背景</p>
<h2>{esc(ch.get("loreTitle", "泰坦绝症下的病态共生"))}</h2>
<p>{esc(ch['loreIntro'])}</p>
<table class="data-table" style="margin-top:16px;width:100%;font-size:13px">
<thead><tr><th>编号</th><th>录音标题</th><th>触发阶段</th><th>时长</th></tr></thead>
<tbody>{track_rows}</tbody>
</table>
</div>
</details>
</article>'''
        record(ch['title'] + ' · 频段监听', ch['summary'], '/arkham/transmissions/#channel-' + ch['id'])

    terminal_trans = f'''<section class="section arkham-investigation" data-transmissions-terminal>
<div class="terminal-heading"><p class="label"><i data-arkham-icon="radio"></i>CRYPTOGRAPHIC SEQUENCER / INTERCEPTED TRANSMISSIONS</p><h1>频段监听</h1><p class="lead">调取哥谭的电话留言、广播访谈、密谈与案件录音。</p><p class="fine">阿卡姆通讯频段终端 · 含主线重要剧情与片尾剧透</p></div>
{game_tabs([("arkham-city", "阿卡姆之城"), ("arkham-knight", "阿卡姆骑士")])}
<div class="transmission-desk"><div class="transmission-browser">
<div class="sequencer-modes" data-sequencer-modes hidden aria-label="选择信道方式"><button type="button" data-sequencer-mode="list" aria-pressed="true">信道列表</button><button type="button" data-sequencer-mode="tune" aria-pressed="false">双轴调谐</button></div>
<div class="transmission-channels" data-sequencer-list aria-label="可用频段">{channel_cards}</div>
<section class="sequencer" data-sequencer hidden aria-label="双轴信道调谐器">
<div class="sequencer-coordinates"><span>专题调谐坐标</span><output data-tuning-coordinates aria-live="off">X 050 · Y 050</output></div>
<p class="fine" id="sequencer-help">拖动准星或使用下方滑块；在网格中按方向键微调，Shift 加速。</p>
<div class="sequencer-field" data-tuning-field tabindex="0" role="group" aria-label="调谐网格" aria-describedby="sequencer-help"><div data-tuning-signals></div><span class="sequencer-cursor" data-tuning-cursor aria-hidden="true"></span></div>
<div class="sequencer-sliders"><label for="tuning-x">横轴 X</label><input id="tuning-x" type="range" min="0" max="100" value="50" data-tuning-x><label for="tuning-y">纵轴 Y</label><input id="tuning-y" type="range" min="0" max="100" value="50" data-tuning-y></div>
<p class="sequencer-state" data-tuning-state role="status" aria-live="polite">搜寻信号</p>
<button class="sequencer-retrieve" type="button" data-tuning-retrieve disabled>锁定后调取信道</button>
<script type="application/json" data-tuning-data>{tuning_data}</script>
</section></div>
<div class="transmission-workspace">{panels_trans}</div>
</div>
{terminal_bar("/arkham/transmissions/")}
</section>'''
    record('频段监听 · Cryptographic Sequencer', '收听《之城》的电话与广播，以及《骑士》的密谈和案件录音。', '/arkham/transmissions/')

    return {
        'arkham/detective/index.html': page('案件重建', detective),
        'arkham/patients/index.html': page('患者终端', terminal),
        'arkham/transmissions/index.html': page('频段监听', terminal_trans, sequencer=True)
    }, records
