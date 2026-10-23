"""The opening editing table lives only in the TAS production room."""
import json
from pathlib import Path
from render_common import esc

ROOT = Path(__file__).resolve().parent
TARGET = '/tas/archive/production/#opening-edit'


def load():
    return json.loads((ROOT / 'tas-opening.json').read_text())


def media_assets():
    packet = load()
    return packet['panels'] + [packet['poster'], packet['video']]


def search_record():
    return dict(title='片头剪辑台', original='Opening Storyboard',
                summary='重排九张分镜，还原经典片头的镜头顺序，完成后播放完整开场。',
                tags=['片头', '分镜', '拼图', '互动', 'Bruce Timm'], site='tas',
                status='分镜互动', url=TARGET)


def render():
    packet = load()
    panels = packet['panels']
    tiles = ''
    for position, index in enumerate([4, 0, 7, 2, 8, 1, 5, 3, 6], 1):
        panel = panels[index]
        tiles += (f'<li class="opening-cell"><button type="button" class="opening-tile" '
                  f'data-frame="{esc(panel["id"])}" data-sequence="{index}" '
                  f'aria-label="位置{position}：{esc(panel["title"])}" aria-pressed="false" '
                  f'draggable="true" disabled><span class="opening-mount">'
                  f'<img src="/assets/media/{esc(panel["file"])}" width="{panel["width"]}" '
                  f'height="{panel["height"]}" alt="{esc(panel["title"])}" draggable="false" loading="lazy">'
                  f'</span><span class="opening-position" aria-hidden="true">{position:02d}</span>'
                  '</button></li>')
    video = packet['video']
    poster = packet['poster']
    return f'''<section class="opening-edit" id="opening-edit" data-opening-puzzle aria-labelledby="opening-heading">
<div class="opening-intro"><h2 id="opening-heading">片头剪辑台</h2>
<p>九张分镜，一分钟的哥谭之夜。把镜头排回原来的顺序，点亮这段经典开场。</p></div>
<div class="opening-workspace">
<div class="opening-board"><p class="opening-instructions" id="opening-instructions">从左到右、从上到下排列。拖动交换，或点选两格。</p>
<div class="opening-stage"><ol class="opening-grid" aria-label="片头分镜排序" aria-describedby="opening-instructions">{tiles}</ol>
<div class="opening-screen" data-opening-screen role="region" aria-label="完整片头放映" hidden>
<div class="opening-screen-bar"><span>经典片头</span><button type="button" data-opening-back>收起视频</button></div>
<video data-opening-video data-video-src="/assets/media/{esc(video['file'])}" poster="/assets/media/{esc(poster['file'])}" preload="none" controls playsinline tabindex="0" aria-label="蝙蝠侠动画系列完整片头"></video>
<p class="opening-credit">Remastered Opening Titles · Warner Bros. Entertainment</p><p data-opening-video-status role="status" aria-live="polite"></p></div></div>
<p class="opening-credit">分镜：Bruce Timm · 色彩：Eric Radomski · 1992</p></div>
<div class="opening-console"><div class="opening-progress"><span>镜头就位</span><strong data-opening-count>0 / 9</strong></div>
<p class="opening-status" data-opening-status role="status" aria-live="polite" aria-atomic="true">正在摆放分镜…</p>
<div class="opening-tools"><button type="button" data-opening-enlarge aria-label="放大选中画面" disabled>放大画面</button>
<button type="button" data-opening-hint disabled>提示一格</button><button type="button" data-opening-reset disabled>重新打乱</button></div>
<div class="opening-reward"><p data-opening-gate>完成九格，解锁完整片头。</p><button type="button" class="opening-play" data-opening-play hidden disabled>播放完整片头</button></div>
</div></div>
<dialog class="opening-detail" data-opening-dialog aria-labelledby="opening-detail-title"><button type="button" data-opening-close>关闭大图</button><h3 id="opening-detail-title">分镜画面</h3><img data-opening-large alt=""></dialog>
<noscript><p>启用 JavaScript 即可重排分镜。也可以阅读<a href="#artbook-t03">片头分镜与镜头设计</a>。</p></noscript>
</section>'''
