"""Shared tape controls for the patient terminal and interview reading page."""
import json
from render_common import esc


def recording_controls(patient, *, compact=False):
    tapes = patient['tapes']
    buttons = ''.join(
        f'<button type="button" data-tape="{n}" aria-pressed="{str(n == 0).lower()}" class="cassette-btn">'
        f'<span class="cassette-track-pip" aria-hidden="true"><span class="pip-core"></span></span>'
        f'<span class="cassette-label">TAPE {n + 1:02d}</span>'
        f'<small>{int(t["duration"])//60}:{int(t["duration"])%60:02d}</small>'
        f'<span class="cassette-sub" aria-hidden="true">TRACK 0{n + 1}</span>'
        f'</button>'
        for n, t in enumerate(tapes)
    )
    payload = json.dumps([dict(src='/assets/' + t['audioFile'], label=f'TAPE {n + 1:02d}', cues=t['cues'], summary=t.get('summary', '')) for n, t in enumerate(tapes)], ensure_ascii=False).replace('<', '\\u003c')
    fallback = ''.join(f'<a href="/assets/{esc(t["audioFile"])}">录音 {n + 1:02d}</a> ' for n, t in enumerate(tapes))
    transport = f'<button type="button" class="load-recording" data-load-recording hidden>播放所选录音</button><div class="patient-player"><audio controls preload="none" hidden aria-label="{esc(patient["name"])}访谈录音"></audio><div data-recording-fallback>{fallback}</div></div>'
    return f'''{transport if compact else ''}<nav class="tape-selector" aria-label="选择录音" hidden>{buttons}</nav>
<div class="tape-deck-telemetry">
<p class="label tape-label" data-tape-label>TAPE 01 / {len(tapes):02d}</p>
<span class="vu-meter-tag" aria-hidden="true">OSCILLOSCOPE // 44.1kHz AAC · MONO</span>
</div>
<div class="waveform-chassis crt-monitor-chassis">
<div class="crt-hud-overlay" aria-hidden="true">
<div class="crt-hud-grid">
<span class="hud-item hud-tl">SIG-IN: 44.1kHz</span>
<span class="hud-item hud-tr">CH-1 MONO</span>
<span class="hud-item hud-bl">SWEEP: 50ms/DIV</span>
<span class="hud-item hud-br">CALIBRATED</span>
</div>
<div class="crt-graticule"></div>
<div class="crt-scanlines"></div>
<div class="crt-glare"></div>
</div>
<span class="db-scale" aria-hidden="true">+3dB<br>0dB<br>-6dB<br>-12dB<br>-24dB</span>
<canvas class="voice-waveform" data-waveform width="720" height="140" role="img" aria-label="实时音频波形">实时音频波形</canvas>
</div>
<div class="recording-subtitles" aria-label="录音文字">
<div class="transcript-title-bar">
<p class="label" data-transcript-heading>{'LISTENING NOTES // 本段导读' if tapes[0].get('summary') else 'AUDIO TRANSCRIPT // 实时录音文字记录'}</p>
</div>
<p data-subtitle>{esc(tapes[0].get('summary') or '点击播放，显示本段字幕。')}</p>
</div>
{'' if compact else transport}
<script type="application/json" data-tape-data>{payload}</script>'''
