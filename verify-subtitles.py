"""Guard subtitle coverage and the recordings preserved by the October repair."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def cue_hash(cues):
    value = json.dumps(cues, ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(value).hexdigest()


recordings = {}
for filename, collection, tracks in (
    ('patient-interviews.json', 'patients', 'tapes'),
    ('arkham-transmissions.json', 'channels', 'tracks'),
    ('asylum-history.json', 'records', None),
):
    for owner in read(filename)[collection]:
        for tape in owner[tracks] if tracks else [owner['audio']]:
            name = tape['audioFile']
            assert name not in recordings, name
            recordings[name] = tape
            assert tape['cues'], f'{name}: an introduction cannot replace subtitles'
            end = 0
            for cue in tape['cues']:
                assert all(isinstance(cue[k], (float, int)) and math.isfinite(cue[k]) for k in ('start', 'end')), name
                assert end <= cue['start'] < cue['end'] <= tape['duration'] + .15, (name, cue)
                assert isinstance(cue['text'], str) and cue['text'].strip(), name
                assert not any(ord(c) < 32 for c in cue['text']), (name, cue)
                end = cue['end']

batch = read('audio-subtitles-20261025.json')
assert len(recordings) == 129
added = {item['audioFile']: item for item in batch['entries']}
preserved = {item['audioFile']: item for item in batch['preservedCueHashes']}
assert len(added) == 88 and len(preserved) == 41 and not added.keys() & preserved.keys()
assert added.keys() | preserved.keys() == recordings.keys()
assert batch['cueCount'] == sum(len(recordings[name]['cues']) for name in added)
assert set(batch['audioHashes']) == set(recordings)
sources = {item['file']: item for item in batch['sourceFiles']}
for name, tape in recordings.items():
    digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert digest == tape['audioSha256'] == batch['audioHashes'][name], name
    expected = (added.get(name) or preserved[name])['cueSha256']
    assert cue_hash(tape['cues']) == expected, f'{name}: reviewed subtitle text changed'
    if name in added:
        entry = added[name]
        assert tape['subtitleSource'] == batch['id']
        assert entry['sourceFile'] in sources and len(sources[entry['sourceFile']]['sha256']) == 64
        assert entry['sourceStart'] == tape['sourceStart'] and entry['sourceEnd'] == tape['sourceEnd']
        assert entry['cueCount'] == len(tape['cues'])
        assert all('en' not in cue for cue in tape['cues']), 'Do not publish unreviewed English OCR'

assert 'textMode' in read('audio-import-20261023.json')
assert read('audio-import-20261023.json')['subtitleCompletion'] == 'audio-subtitles-20261025.json'
print(f'PASS: 129 recordings have timed subtitles; {len(added)} repaired, {len(preserved)} original cue sets and all audio hashes preserved')
