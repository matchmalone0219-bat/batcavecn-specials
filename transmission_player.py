"""Transmission controls for the cryptographic sequencer radio terminal."""
import json
from render_common import esc


def transmission_controls(channel):
    tracks = channel["tracks"]
    total = len(tracks)
    btn_list = []
    for n, t in enumerate(tracks):
        climax_cls = " is-climax" if t.get("isClimax") else ""
        pressed = "true" if n == 0 else "false"
        short_name = esc(t["title"].split("：")[-1])
        dur_min = int(t["duration"]) // 60
        dur_sec = int(t["duration"]) % 60
        btn_list.append(
            f'<button type="button" data-tape="{n}" aria-pressed="{pressed}" class="transmission-track-btn{climax_cls}">'
            f'<span class="track-num">TRACK {t["number"]:02d}</span>'
            f'<span class="track-name">{short_name}</span>'
            f'<small>{dur_min}:{dur_sec:02d}</small>'
            f'</button>'
        )
    buttons = "".join(btn_list)
    track_payload = []
    for t in tracks:
        track_num = t['number']
        track_title = t['title']
        track_payload.append(dict(
            src='/assets/' + t['audioFile'],
            label=f"TRACK {track_num:02d} / {total:02d} · {track_title}",
            isClimax=bool(t.get('isClimax')),
            cues=t['cues']
        ))
    payload = json.dumps(track_payload, ensure_ascii=False).replace('<', '\\u003c')
    fallback = "".join(f'<a href="/assets/{esc(t["audioFile"])}">{esc(t["title"])}</a> ' for t in tracks)
    first_title = tracks[0]["title"]
    freq = esc(channel["frequency"])
    return (
        f'<nav class="tape-selector transmission-selector" aria-label="选择通讯录音">{buttons}</nav>\n'
        f'<div class="transmission-console-meta">'
        f'<p class="label tape-label" data-tape-label>TRACK 01 / {total:02d} · {esc(first_title)}</p>'
        f'<div class="transmission-meta-right">'
        f'<span class="frequency-indicator">FREQ: {freq}</span>'
        f'<span class="playback-state transmission-playback-state" data-playback-state role="status">等待播放</span>'
        f'</div>'
        f'</div>\n'
        '<canvas class="voice-waveform transmission-waveform" data-waveform width="720" height="140" role="img" aria-label="实时无线电波形">实时无线电波形</canvas>\n'
        '<div class="recording-subtitles transmission-subtitles" aria-label="实时对白字幕">'
        '<p class="label">LIVE TRANSMISSION SUBTITLES · 实时同步双语字幕</p>'
        '<div class="subtitle-display" data-subtitle>'
        '<p class="sub-zh">点击播放，截获并解密信道音频。</p>'
        '<p class="sub-en">Click play to intercept and decode frequency audio.</p>'
        '</div></div>\n'
        '<button type="button" class="load-recording" data-load-recording hidden>播放所选通讯</button>'
        f'<div class="patient-player"><audio controls preload="none" hidden aria-label="{esc(channel["title"])}"></audio><noscript>{fallback}</noscript></div>\n'
        f'<script type="application/json" data-tape-data>{payload}</script>'
    )
