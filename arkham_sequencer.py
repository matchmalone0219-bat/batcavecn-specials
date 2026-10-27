"""One playable security console beside the intercepted-frequency archive."""
import json
from render_common import ROOT, esc


def sequencer():
    packet = json.loads((ROOT / 'arkham-sequencer.json').read_text())
    terminal = packet['terminal']
    payload = dict(terminal, sounds={clip['id']: '/assets/' + clip['file'] for clip in packet['clips']})
    data = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    controls = ''.join(f'''<div class="seq-control"><span>{label}密钥 <small>{side.upper()} PASSKEY</small></span>
<div class="seq-dial" data-seq-dial="{side}" role="group" tabindex="0" aria-label="{label}密钥调谐盘，拖动或用四个方向键调整" aria-describedby="seq-help"><span class="seq-dial-ring" aria-hidden="true"></span><span class="seq-dial-knob" aria-hidden="true"></span></div>
<span class="seq-signal" data-seq-signal="{side}">等待接入</span></div>''' for side, label in [('left', '左'), ('right', '右')])
    return f'''<div class="seq-modes" data-seq-modes role="group" aria-label="密码解析器模式" hidden>
<button type="button" data-seq-mode="listen" aria-pressed="true">监听频段 <small>FREQUENCIES</small></button>
<button type="button" data-seq-mode="decode" aria-pressed="false">密码破译 <small>SECURITY CONSOLE</small></button></div>
<section class="sequencer" id="password-terminal" data-sequencer data-active="false" data-phase="ready" hidden aria-labelledby="seq-title">
<div class="seq-heading"><div><p class="label">WAYNETECH / CRYPTOGRAPHIC SEQUENCER</p><h2 id="seq-title">警局安保门</h2><p>接入哥谭市政网络，调谐两组密钥，解除门禁。</p></div><div class="seq-lock" data-seq-lock><i data-arkham-icon="classified"></i><span data-seq-lock-label>LOCKED</span></div></div>
<div class="seq-console"><div class="seq-network"><span>Hacking: {esc(terminal['network'])}<br>Target: {esc(terminal['target'])}</span><span class="seq-security">SECURITY LEVEL <b aria-label="安全等级一，共五级"><i></i><i></i><i></i><i></i><i></i></b></span></div>
<div class="seq-display" aria-hidden="true"><div class="seq-columns" data-seq-columns></div><div class="seq-reticle"></div><p class="seq-exchange" data-seq-exchange hidden>Exchanging key…</p></div>
<div class="seq-device"><span class="seq-grip" aria-hidden="true"></span><div class="seq-controls">{controls}</div><span class="seq-grip" aria-hidden="true"></span></div>
<p class="seq-state" data-seq-state role="status" aria-live="polite">选择接入，启动密码解析器。</p></div>
<div class="seq-actions"><button type="button" data-seq-start>接入安保终端</button><button type="button" data-seq-cancel hidden>取消连接</button><button type="button" data-seq-sound aria-pressed="true">原声音效：开</button></div>
<p class="seq-help" id="seq-help">拖动左右调谐盘，寻找字符最清晰的位置。选中调谐盘后，可用方向键微调；两组密钥同时稳定后自动开锁。</p>
<section class="seq-unlocked" data-seq-unlocked hidden><p class="label">ACCESS GRANTED / 访问获准</p><h3>市政网络已接通</h3><p>警局电脑中的哥谭市政密码，让蝙蝠侠能够破解接入这套网络的安保设备。密码解析器依靠掌握的访问代码，打开城市中原本封闭的通道。</p><a href="/arkham/games/arkham-city/">阅读《阿卡姆之城》作品档案</a></section>
<a href="{esc(packet['source']['url'])}" hidden aria-hidden="true">实机流程</a>
<audio data-seq-audio preload="none" hidden></audio><script type="application/json" data-seq-data>{data}</script></section>'''
