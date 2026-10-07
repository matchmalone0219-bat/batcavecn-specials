"""Interactive investigations, patient listening terminal and intercepted transmissions."""
import json
import math
from render_common import ROOT, esc, paragraphs
from patient_player import recording_controls
from transmission_player import transmission_controls


def build_interactions(data, shell):
    research = json.loads((ROOT / 'riddler-research.json').read_text())
    archive = json.loads((ROOT / 'arkham-archive-research.json').read_text())
    patients = json.loads((ROOT / 'patient-interviews.json').read_text())
    transmissions = json.loads((ROOT / 'arkham-transmissions.json').read_text())
    cases = json.loads((ROOT / 'arkham-interactions.json').read_text())['cases']
    sources = {s['id']: s for packet in (research, archive, patients, transmissions) for s in packet['sources']}
    images = {i['id']: i for i in research['images']}
    entries = {e['id']: e for e in research['entries']}
    topics = {c['id']: c for c in research['cases']}
    records = []

    def refs(ids):
        return '<div class="terminal-sources">' + ''.join(f'<a href="{esc(sources[id]["url"])}">{esc(sources[id]["title"])} ↗</a>' for id in ids) + '</div>'

    def links(items):
        return '<div class="terminal-links">' + ''.join(f'<a href="{esc(i["url"])}">{esc(i["title"])}</a>' for i in items) + '</div>'

    def record(title, summary, url):
        records.append(dict(title=title, original=title, summary=summary, tags=['调查终端'], site='arkham', status='互动档案', url=url))

    def page(title, body):
        return shell(data, 'arkham', title, body, 'archive').replace('</head>', '<link rel="stylesheet" href="/assets/arkham-investigation.css"><script src="/assets/arkham-investigation.js" defer></script></head>')

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
        item = dict(c, number=f'{n:02d}', src='/assets/media/' + image['file'], width=image['width'], height=image['height'], caption=image['caption'], sourceHtml=refs([image['source']]))
        item['evidence'] = [dict(e, sourceHtml=refs(e['sources']), linksHtml=links(e['links'])) for e in c['evidence']]
        case_data.append(item)
        fallback += f'<article id="case-{esc(c["id"])}"><h2>{esc(c["title"])}</h2><p>{esc(c["game"])} · {esc(c["region"])}</p><img src="{item["src"]}" width="{image["width"]}" height="{image["height"]}" alt="{esc(image["caption"])}">' + ''.join(f'<h3>{esc(e["title"])}</h3>{paragraphs(e["body"])}{links(e["links"])}{refs(e["sources"])}' for e in c['evidence']) + f'<h3>案件总结</h3>{paragraphs(c["summary"])}</article>'
        record(c['title'] + ' · 案件重建', c['subtitle'], '/arkham/detective/#case-' + c['id'])

    payload = json.dumps(case_data, ensure_ascii=False).replace('<', '\\u003c')
    first = case_data[0]
    tabs = ''.join(f'<a href="#case-{esc(c["id"])}" data-case="{esc(c["id"])}"><span>{c["number"]}</span>{esc(c["title"])}</a>' for c in case_data)
    detective = f'''<section class="section arkham-investigation" data-detective>
<div class="terminal-heading"><p class="label">BATCOMPUTER / DETECTIVE MODE</p><h1>案件重建</h1><p class="lead">从一件物品出发，沿人物与历史完成调查。</p><p class="fine">专题调查 · 含角色背景与身份信息</p></div>
<nav class="case-register" aria-label="选择调查">{tabs}</nav>
<div class="investigation-workspace" hidden data-workspace>
<section class="scene-console"><div class="console-bar"><span data-case-number>CASE 01</span><span data-mode-label>NORMAL VISION</span></div><h2 data-case-title>{esc(first['title'])}</h2><p class="scene-location" data-location>{esc(first['game'])} · {esc(first['region'])}</p>
<div class="investigation-scene" data-scene><img data-scene-image src="{first['src']}" width="{first['width']}" height="{first['height']}" alt="{esc(first['caption'])}"><div class="scan-grid" aria-hidden="true"></div><button type="button" class="scan-hotspot" data-scan hidden aria-label="扫描现场物件"><span>01</span><small>SCAN</small></button></div>
<div class="scan-controls"><button type="button" data-mode aria-pressed="false">激活侦探模式 <small>ACTIVATE DETECTIVE MODE</small></button><span data-progress role="status">0 / 3 条证据</span></div><p class="fine" data-scene-caption>{esc(first['caption'])}</p><div data-scene-source>{first['sourceHtml']}</div></section>
<aside class="evidence-console" aria-label="证据详情"><p class="label">EVIDENCE CHAIN</p><div class="evidence-chain" data-evidence-chain></div><div data-evidence-panel><p class="evidence-id" data-evidence-label>AWAITING SCAN</p><h2 data-evidence-title>现场等待扫描</h2><div data-evidence-body><p>激活侦探模式，选择画面中的扫描点。</p></div><div data-evidence-links></div><div data-evidence-sources></div></div></aside></div>
<section class="case-summary" data-summary hidden><p class="label">CASE SUMMARY / 调查完成</p><h2>线索已经连成一段故事</h2><p data-summary-text></p><div class="terminal-links"><a href="/arkham/archive/riddler/" data-summary-link>继续阅读关联档案</a><button type="button" data-reset>重新调查本案</button></div></section>
<div class="terminal-fallback" data-case-fallback>{fallback}</div>
<div class="terminal-footer"><a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>听见档案中的人物</h2><p>打开七组患者访谈，沿人物的声音继续阅读。</p></a><a class="dossier-shelf" href="/arkham/transmissions/"><p class="label">CRYPTOGRAPHIC SEQUENCER</p><h2>调谐加密无线电</h2><p>截获小丑秘密电话留言与片尾绝唱。</p></a></div>
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
            screws.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.8" fill="#425e4f" stroke="#15241c" stroke-width="0.8"/><line x1="{sx-1.8:.1f}" y1="{sy:.1f}" x2="{sx+1.8:.1f}" y2="{sy:.1f}" stroke="#15241c" stroke-width="0.8"/>')
        screws_svg = "".join(screws)

        ticks = []
        for i in range(24):
            deg = i * 15
            rad = math.radians(deg)
            x1, y1 = 100 + 91 * math.cos(rad), 100 + 91 * math.sin(rad)
            x2, y2 = 100 + 94.5 * math.cos(rad), 100 + 94.5 * math.sin(rad)
            stroke_w = "1.2" if i % 6 == 0 else "0.6"
            stroke_col = "#5a846e" if i % 6 == 0 else "#2e4a3c"
            ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke_col}" stroke-width="{stroke_w}"/>')
        ticks_svg = "".join(ticks)

        return f'''<svg class="reel-spool-svg" viewBox="0 0 200 200" aria-hidden="true">
<defs>
<radialGradient id="al-flange-{uid}" cx="45%" cy="40%" r="60%">
<stop offset="0%" stop-color="#2e493b"/>
<stop offset="45%" stop-color="#182920"/>
<stop offset="75%" stop-color="#284235"/>
<stop offset="100%" stop-color="#111c16"/>
</radialGradient>
<radialGradient id="tape-pack-{uid}" cx="50%" cy="50%" r="50%">
<stop offset="0%" stop-color="#301a0f"/>
<stop offset="50%" stop-color="#20110a"/>
<stop offset="85%" stop-color="#2a160d"/>
<stop offset="100%" stop-color="#150a05"/>
</radialGradient>
<radialGradient id="hub-met-{uid}" cx="40%" cy="35%" r="65%">
<stop offset="0%" stop-color="#3e6350"/>
<stop offset="60%" stop-color="#1d3327"/>
<stop offset="100%" stop-color="#0e1a13"/>
</radialGradient>
<mask id="mask-{uid}">
<rect width="200" height="200" fill="white"/>
<path d="{holes_path}" fill="black"/>
</mask>
</defs>
<circle cx="100" cy="100" r="96" fill="#07100b"/>
<circle cx="100" cy="100" r="{tape_r}" fill="url(#tape-pack-{uid})"/>
<circle cx="100" cy="100" r="{tape_r - 8}" fill="none" stroke="#381f12" stroke-width="0.7" stroke-dasharray="3 2"/>
<circle cx="100" cy="100" r="{tape_r - 18}" fill="none" stroke="#381f12" stroke-width="0.7" stroke-dasharray="4 2"/>
<circle cx="100" cy="100" r="96" fill="url(#al-flange-{uid})" mask="url(#mask-{uid})" stroke="#4e7a63" stroke-width="1.8"/>
<circle cx="100" cy="100" r="90" fill="none" stroke="#1c3125" stroke-width="1" mask="url(#mask-{uid})"/>
<path d="{holes_path}" fill="none" stroke="#4e7a63" stroke-width="1.4" opacity="0.85"/>
{ticks_svg}
{screws_svg}
<circle cx="100" cy="100" r="36" fill="url(#hub-met-{uid})" stroke="#528068" stroke-width="1.5"/>
<circle cx="100" cy="100" r="28" fill="none" stroke="#264434" stroke-width="1.2"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#0c1812" stroke="#385a47" stroke-width="0.8"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#0c1812" stroke="#385a47" stroke-width="0.8" transform="rotate(120 100 100)"/>
<rect x="97.5" y="68" width="5" height="8" rx="1" fill="#0c1812" stroke="#385a47" stroke-width="0.8" transform="rotate(240 100 100)"/>
<circle cx="100" cy="100" r="16" fill="#16261d" stroke="#2fe58b" stroke-width="1.2"/>
<circle cx="100" cy="100" r="7" fill="#050c08" stroke="#446e57" stroke-width="1"/>
</svg>'''

    VU_SCALE_SVG = '''<svg viewBox="0 0 110 44" class="vu-scale-svg" aria-hidden="true">
<path d="M 10 38 A 60 60 0 0 1 100 38" fill="none" stroke="#223b2e" stroke-width="2"/>
<path d="M 76 21 A 60 60 0 0 1 100 38" fill="none" stroke="#d94b38" stroke-width="2.2"/>
<line x1="16" y1="33" x2="19" y2="30" stroke="#48755e" stroke-width="1"/>
<line x1="32" y1="26" x2="34" y2="23" stroke="#48755e" stroke-width="1"/>
<line x1="52" y1="21" x2="53" y2="18" stroke="#48755e" stroke-width="1.2"/>
<line x1="76" y1="21" x2="77" y2="18" stroke="#d94b38" stroke-width="1.4"/>
<line x1="92" y1="28" x2="94" y2="25" stroke="#d94b38" stroke-width="1.4"/>
<text x="18" y="40" fill="#4d7a62" font-size="6" font-family="monospace">-20</text>
<text x="50" y="29" fill="#4d7a62" font-size="6" font-family="monospace">-5</text>
<text x="74" y="27" fill="#d94b38" font-size="7" font-weight="bold" font-family="monospace">0</text>
<text x="94" y="36" fill="#d94b38" font-size="6" font-weight="bold" font-family="monospace">+3</text>
</svg>'''

    BARCODE_SVG = '<svg viewBox="0 0 140 22" class="inmate-barcode-svg" aria-hidden="true">' + ''.join(
        f'<rect x="{x}" y="0" width="{w}" height="22" fill="#3f6652"/>'
        for x, w in [(4, 2), (8, 4), (14, 1), (17, 3), (22, 1), (25, 4), (31, 2), (35, 1), (38, 4), (44, 2), (48, 1), (51, 3), (56, 4), (62, 1), (65, 3), (70, 2), (74, 4), (80, 1), (83, 3), (88, 2), (92, 4), (98, 1), (101, 3), (106, 2), (110, 4), (116, 2), (120, 1), (123, 3), (128, 4), (134, 2)]
    ) + '</svg>'

    registers = ''
    panels = ''
    for n, p in enumerate(patients['patients'], 1):
        assert set(p['sources']) <= sources.keys()
        monogram = ''.join(w[0] for w in p['english'].split() if w != 'The')
        uid_l = f"p{n}-l"
        uid_r = f"p{n}-r"
        spool_l = make_nab_spool(True, uid_l)
        spool_r = make_nab_spool(False, uid_r)
        registers += f'<a href="#patient-{p["id"]}" data-patient="{p["id"]}"><span class="rack-mount-rivet" aria-hidden="true"></span><span class="patient-slot-num">{n:02d}</span><span class="patient-slot-info"><strong>{esc(p["name"])}</strong><small>{esc(p["english"])}</small></span><span class="patient-slot-status"><span class="inmate-status-pip" aria-hidden="true"></span><span class="patient-tape-pips" aria-hidden="true">■■■■■</span></span></a>'
        panels += f'''<article class="patient-file" id="patient-{p['id']}" data-patient-file="{p['id']}" data-audio-recording>
<span class="chassis-bolt bolt-tl" aria-hidden="true"></span>
<span class="chassis-bolt bolt-tr" aria-hidden="true"></span>
<span class="chassis-bolt bolt-bl" aria-hidden="true"></span>
<span class="chassis-bolt bolt-br" aria-hidden="true"></span>
<div class="console-bar">
<div class="console-case-track">
<span class="case-badge">RECORD INDEX {n:02d} // SEC-0{n}</span>
<span class="dept-badge">PSYCHIATRIC EVALUATION DIVISION</span>
</div>
<span class="security-level">ARKHAM ASYLUM // MAXIMUM SECURITY</span>
</div>
<div class="patient-identity">
<div class="patient-monogram-frame">
<span class="patient-monogram" aria-hidden="true">{esc(monogram)}</span>
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
{paragraphs(p['gist'])}
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
{recording_controls(p)}
<div class="terminal-links">
<a href="/arkham/archive/interviews/#{p['id']}">人物阅读档案</a>
</div>
{refs(p['sources'])}
</details>
</article>'''
        record(p['name'] + ' · 患者终端', p['angle'], '/arkham/patients/#patient-' + p['id'])
    terminal = f'''<section class="section arkham-investigation arkham-patient-terminal" data-patient-terminal>
<div class="terminal-heading">
<div class="terminal-heading-tags">
<p class="label">ARKHAM ASYLUM // PSYCHIATRIC RECORD SYSTEM</p>
<span class="system-status-pips" aria-hidden="true">■■■■■ 7/7 INMATES ARCHIVED · LEVEL 4 RESTRICTED</span>
</div>
<h1>患者终端</h1>
<p class="lead">选择一个人物，听医院如何记录他们，也听他们如何改变对话。</p>
<p class="fine">收录阿卡姆疯人院 7 组角色共 35 盘现场心理评估录音 · 原声访谈与中文字幕</p>
</div>
<div class="patient-workspace">
<nav class="patient-selector" aria-label="选择患者">{registers}</nav>
<div class="patient-files">{panels}</div>
</div>
<div class="terminal-footer">
<a class="dossier-shelf" href="/arkham/detective/"><p class="label">DETECTIVE MODE</p><h2>回到现场调查</h2><p>扫描物件，连接人物与城市的记忆。</p></a>
<a class="dossier-shelf" href="/arkham/transmissions/"><p class="label">CRYPTOGRAPHIC SEQUENCER</p><h2>调谐加密无线电</h2><p>截获小丑秘密电话留言与片尾绝唱。</p></a>
</div>
</section>'''
    record('案件重建 · Detective Mode', '扫描现场物件，沿证据链阅读人物与历史。', '/arkham/detective/')
    record('患者终端', '七组患者访谈与聆听导读。', '/arkham/patients/')

    channels = transmissions['channels']
    channel_cards = ''
    panels_trans = ''
    for n, ch in enumerate(channels, 1):
        assert set(ch['sources']) <= sources.keys()
        channel_cards += f'<a class="transmission-channel-card" href="#channel-{ch["id"]}" aria-current="true"><p class="label">FREQUENCY: {esc(ch["frequency"])}</p><h3>{esc(ch["title"])}</h3><p>{esc(ch["game"])} · {esc(ch["speaker"])} ({esc(ch["actor"])})</p></a>'
        track_rows = ''.join(
            f'<tr><td>{t["number"]:02d}</td><td><strong>{esc(t["title"])}</strong><br><small>{esc(t["englishTitle"])}</small></td><td>{esc(t["phase"])}</td><td>{int(t["duration"])//60}:{int(t["duration"])%60:02d}</td></tr>'
            for t in ch['tracks']
        )
        panels_trans += f'''<article class="transmission-file" id="channel-{ch['id']}" data-transmission-channel="{ch['id']}" data-audio-recording>
<div class="console-bar"><span>CRYPTOGRAPHIC SEQUENCER · FREQUENCY {esc(ch['frequency'])}</span><span>{esc(ch['game'])}</span></div>
<div class="patient-identity">
<span class="patient-monogram" aria-hidden="true" style="color:#2fe58b;border-color:#2fe58b55;background:repeating-linear-gradient(0deg,#091a11 0 3px,#0c2317 3px 4px)">{esc(ch['speaker'][0])}</span>
<div><p class="label">INTERCEPTED FREQUENCY · 截获通信</p><h2>{esc(ch['title'])}</h2><p>{esc(ch['englishTitle'])}</p><p class="fine">发信人：{esc(ch['speaker'])} ({esc(ch['speakerEnglish'])}) · 配音：{esc(ch['actor'])} · 载具/装置：{esc(ch['device'])}</p></div>
</div>
<div class="listening-question"><p class="label">TRANSMISSION OVERVIEW / 信道背景</p><p>{esc(ch['summary'])}</p></div>
{transmission_controls(ch)}
<div class="transmission-lore">
<p class="label">TACTICAL ANALYSIS / 叙事解构与背景</p>
<h2>泰坦绝症下的病态共生</h2>
<p>{esc(ch['loreIntro'])}</p>
<table class="data-table" style="margin-top:16px;width:100%;font-size:13px">
<thead><tr><th>编号</th><th>录音标题</th><th>触发阶段</th><th>时长</th></tr></thead>
<tbody>{track_rows}</tbody>
</table>
</div>
{refs(ch['sources'])}
</article>'''
        record(ch['title'] + ' · 频段监听', ch['summary'], '/arkham/transmissions/#channel-' + ch['id'])

    terminal_trans = f'''<section class="section arkham-investigation" data-transmissions-terminal>
<div class="terminal-heading"><p class="label">CRYPTOGRAPHIC SEQUENCER / INTERCEPTED TRANSMISSIONS</p><h1>频段监听</h1><p class="lead">使用密码破译器调谐哥谭频段，截获并解密未公开的通话与无线电留言。</p><p class="fine">阿卡姆通讯频段终端 · 含主线重要剧情与片尾剧透</p></div>
<div class="transmission-channels" aria-label="可用频段">{channel_cards}</div>
<div class="transmission-workspace">{panels_trans}</div>
<div class="terminal-footer"><a class="dossier-shelf" href="/arkham/patients/"><p class="label">PATIENT RECORD DATABASE</p><h2>患者终端</h2><p>聆听阿卡姆疯人院内部病患心理访谈录音。</p></a><a class="dossier-shelf" href="/arkham/detective/"><p class="label">DETECTIVE MODE</p><h2>案件重建</h2><p>激活侦探模式，从现场遗留物件串联完整证据链。</p></a></div>
</section>'''
    record('频段监听 · Cryptographic Sequencer', '调谐密码破译器频段，截获小丑电话留言与片尾绝唱《Only You》。', '/arkham/transmissions/')

    return {
        'arkham/detective/index.html': page('案件重建', detective),
        'arkham/patients/index.html': page('患者终端', terminal),
        'arkham/transmissions/index.html': page('频段监听', terminal_trans)
    }, records
