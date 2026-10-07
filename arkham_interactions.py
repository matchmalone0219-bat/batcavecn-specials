"""Interactive investigations, patient listening terminal and intercepted transmissions."""
import json
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

    registers = ''
    panels = ''
    for n, p in enumerate(patients['patients'], 1):
        assert set(p['sources']) <= sources.keys()
        registers += f'<a href="#patient-{p["id"]}" data-patient="{p["id"]}"><span>{n:02d}</span><span>{esc(p["name"])}<small>{esc(p["english"])}</small></span></a>'
        panels += f'''<article class="patient-file" id="patient-{p['id']}" data-patient-file="{p['id']}" data-audio-recording><div class="console-bar"><span>RECORD INDEX {n:02d}</span><span>ARKHAM ASYLUM</span></div><div class="patient-identity"><span class="patient-monogram" aria-hidden="true">{esc(''.join(w[0] for w in p['english'].split() if w != 'The'))}</span><div><p class="label">PATIENT INTERVIEW</p><h2>{esc(p['name'])}</h2><p>{esc(p['english'])}</p><p class="fine">身份：{esc(p['identity'])}</p></div></div><div class="listening-question"><p class="label">LISTENING NOTES / 聆听导读</p><p>{esc(p['angle'])}</p></div>
<details class="spoiler patient-recording"><summary>访谈导读与原声 · 含剧透</summary>{paragraphs(p['gist'])}<div class="tape-console"><div class="tape-reels" aria-hidden="true"><span></span><i></i><span></span></div><div><p class="label">INTERVIEW RECORDING</p><p class="fine">英语游戏录音 · 玩家录制 · {esc(p['biliUploader'])}</p><p class="playback-state" data-playback-state role="status">等待播放</p></div></div>{recording_controls(p)}<div class="terminal-links"><a href="{esc(p['biliUrl'])}">B站 · {esc(p['biliPart'])} · {p['biliDuration']//60}:{p['biliDuration']%60:02d}</a><a href="{esc(p['watchUrl'])}">YouTube原页 ↗</a><a href="/arkham/archive/interviews/#{p['id']}">人物阅读档案</a></div>{refs(p['sources'])}</details></article>'''
        record(p['name'] + ' · 患者终端', p['angle'], '/arkham/patients/#patient-' + p['id'])
    terminal = f'''<section class="section arkham-investigation" data-patient-terminal><div class="terminal-heading"><p class="label">ARKHAM ASYLUM / PATIENT RECORD DATABASE</p><h1>患者终端</h1><p class="lead">选择一个人物，听医院如何记录他们，也听他们如何改变对话。</p></div><div class="patient-workspace"><nav class="patient-selector" aria-label="选择患者">{registers}</nav><div class="patient-files">{panels}</div></div><div class="terminal-footer"><a class="dossier-shelf" href="/arkham/detective/"><p class="label">DETECTIVE MODE</p><h2>回到现场调查</h2><p>扫描物件，连接人物与城市的记忆。</p></a><a class="dossier-shelf" href="/arkham/transmissions/"><p class="label">CRYPTOGRAPHIC SEQUENCER</p><h2>调谐加密无线电</h2><p>截获小丑秘密电话留言与片尾绝唱。</p></a></div></section>'''
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
