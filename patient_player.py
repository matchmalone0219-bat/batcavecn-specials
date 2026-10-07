"""Shared tape controls for the patient terminal and interview reading page."""
import json
from render_common import esc


def recording_controls(patient):
    tapes = patient['tapes']
    buttons = ''.join(f'<button type="button" data-tape="{n}" aria-pressed="{str(n == 0).lower()}"><span>TAPE {n + 1:02d}</span><small>{int(t["duration"])//60}:{int(t["duration"])%60:02d}</small></button>' for n, t in enumerate(tapes))
    payload = json.dumps([dict(src='/assets/' + t['audioFile'], label=f'TAPE {n + 1:02d}', cues=t['cues']) for n, t in enumerate(tapes)], ensure_ascii=False).replace('<', '\\u003c')
    fallback = ''.join(f'<a href="/assets/{esc(t["audioFile"])}">录音 {n + 1:02d}</a> ' for n, t in enumerate(tapes))
    return f'''<nav class="tape-selector" aria-label="选择录音">{buttons}</nav>
<p class="label tape-label" data-tape-label>TAPE 01 / 05</p>
<canvas class="voice-waveform" data-waveform width="720" height="140" role="img" aria-label="实时音频波形">实时音频波形</canvas>
<div class="recording-subtitles" aria-label="中文字幕"><p class="label">中文字幕</p><p data-subtitle>点击播放，显示本段字幕。</p></div>
<button type="button" class="load-recording" data-load-recording hidden>播放所选录音</button><div class="patient-player"><audio controls preload="none" hidden aria-label="{esc(patient['name'])}访谈录音"></audio><noscript>{fallback}</noscript></div>
<script type="application/json" data-tape-data>{payload}</script>'''
