"""A playable version of the game's comic-book Chronicle dossier."""
import json
from render_common import esc, external_link_icon


def soul_player(history):
    image, icon = history['playerImage'], history['playerIcon']
    glyph = f'<img class="soul-glyph" src="/assets/media/{esc(icon["file"])}" width="{icon["width"]}" height="{icon["height"]}" alt="">'
    choices = []
    for record in history['records']:
        number, audio = record['number'], record['audio']
        seconds = int(audio['duration'])
        duration = f'{seconds // 60}:{seconds % 60:02d}'
        title = f'记录 {number:02d}'
        payload = json.dumps(dict(
            id=record['id'], number=number, src='/assets/' + audio['audioFile'],
            duration=audio['duration'], cues=audio['cues'], topic=record['topic'],
        ), ensure_ascii=False).replace('<', '\\u003c')
        row = (f'<a class="soul-choice" href="#{record["id"]}" data-soul-choice="{number - 1}" aria-controls="soul-stage" aria-label="{title} · {duration}">'
               f'{glyph}<span>{number:02d}</span><time>{duration}</time><small data-soul-row-state></small></a>'
               f'<details class="spoiler soul-fallback"><summary>主题与原声 · 含剧透</summary>'
               f'<p>{esc(record["topic"])}</p><a href="/assets/{esc(audio["audioFile"])}">打开{title}原声</a></details>'
               f'<script type="application/json" data-soul-track>{payload}</script>')
        if number == 24:
            row = ('<details class="spoiler soul-final" data-soul-final><summary aria-label="最终留言 · 含身份剧透">'
                   + glyph + '<span>24</span><small>身份剧透</small></summary>' + row + '</details>')
        choices.append(f'<article id="{record["id"]}" class="soul-entry">{row}</article>')
    return f'''<section class="soul-player" data-soul-player id="records" aria-label="阿卡姆之魂录音">
<figure class="soul-art" data-soul-illustration><p class="soul-art-title">阿卡姆之魂</p><div class="soul-art-paper"><img data-soul-art src="/assets/media/{esc(image['file'])}" data-final-src="/assets/media/{esc(history['playerFinalImage']['file'])}" width="{image['width']}" height="{image['height']}" alt="{esc(image['caption'])}" fetchpriority="high"></div><figcaption data-soul-art-credit>游戏档案插画 · <a href="{esc(image['sourceUrl'])}">Faxagate{external_link_icon()}</a></figcaption><figcaption data-soul-final-credit hidden>游戏档案插画 · 用户提供录屏</figcaption></figure>
<div class="soul-file" id="soul-stage" tabindex="-1"><div class="soul-file-body">
<div class="soul-now"><div><h2>被破译的信息</h2><p data-soul-title>破译信息 #01</p></div><p data-soul-state role="status">等待播放</p></div>
<div class="soul-register"><button type="button" class="soul-directory-toggle" data-soul-directory-toggle aria-expanded="false" aria-controls="soul-directory" hidden>选择记录 · 01</button><div id="soul-directory" data-soul-directory><h3 class="soul-directory-heading">选择记录</h3><div class="soul-icon-grid">{''.join(choices)}</div></div></div>
<div class="soul-console" data-soul-console hidden>
<audio preload="none" data-soul-audio hidden aria-label="阿卡姆之魂录音"></audio>
<div class="soul-subtitles" aria-label="中文字幕"><p data-soul-subtitle aria-live="off">选择一条记录，播放破译的信息。</p></div>
<div class="soul-timeline"><output data-soul-time aria-live="off">0:00 / 0:24</output><input type="range" data-soul-seek min="0" max="24" step="0.1" value="0" aria-label="录音进度" aria-valuetext="0:00 / 0:24"></div>
<div class="soul-transport" role="group" aria-label="录音播放控制"><button type="button" data-soul-prev>上一条</button><button type="button" data-soul-play aria-label="播放"><span data-soul-play-label>播放</span></button><button type="button" data-soul-next>下一条</button></div>
<div class="soul-options"><label><input type="checkbox" data-soul-sequence>顺序连播</label><a data-soul-original href="/assets/{esc(history['records'][0]['audio']['audioFile'])}">打开原声</a></div><p class="soul-sequence-note">连播至记录23，最终留言单独展开。</p>
<details class="spoiler soul-theme" data-soul-theme><summary>本条主题 · 含剧透</summary><p data-soul-topic></p></details>
</div></div></div></section>'''
