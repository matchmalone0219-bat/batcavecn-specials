"""Crop nine opening storyboard panels and copy the supplied video unchanged."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT.parent / 'C0022—Batman Animated'
DEST = ROOT / 'opening'
PANELS = [
    ('night-patrol', 25, [.565, .052, .94, .302], '夜巡飞艇', 7.2, '纵移镜头上段；保留飞艇与探照灯'),
    ('bank-blast', 26, [.701, .854, .964, .995], '银行爆炸', 18.1, '银行爆炸画格'),
    ('batmobile', 27, [.37, .016, .664, .176], '蝙蝠车出动', 21.7, '蝙蝠车尾部；点火前的画格'),
    ('fleeing', 28, [.035, .063, .398, .265], '歹徒逃跑', 29.0, '巷道奔跑画格'),
    ('rooftop', 29, [.697, .013, .972, .168], '屋顶对峙', 36.2, '蝙蝠侠展开披风落下'),
    ('draw-guns', 29, [.374, .189, .647, .336], '歹徒拔枪', 38.0, '两名歹徒持枪画格'),
    ('batarang', 29, [.7, .361, .973, .511], '蝙蝠镖击枪', 40.5, '蝙蝠镖击中持枪手部'),
    ('fight', 30, [.701, .014, .97, .156], '近身格斗', 44.0, '披风翻转与歹徒后仰'),
    ('police', 30, [.372, .692, .649, .844], '警方接手', 50.7, '警用飞艇照亮屋顶歹徒'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    import cv2
    DEST.mkdir(exist_ok=True)
    panels = []
    for id, page, box, title, time, note in PANELS:
        source = SOURCE / f'BA_pg{page:03d}.jpg'
        with Image.open(source) as scan:
            pixels = [round(v * scan.size[i % 2]) for i, v in enumerate(box)]
            crop = scan.crop(pixels).convert('RGB')
            crop.thumbnail((1200, 1000), Image.Resampling.LANCZOS)
            file = f'opening/{id}.jpg'
            crop.save(ROOT / file, quality=92, subsampling=0, optimize=True)
            panels.append(dict(id=id, title=title, file=file, width=crop.width,
                               height=crop.height, sha256=digest(ROOT / file),
                               sourceFile=source.name, sourceSHA256=digest(source),
                               cropNormalized=box, cropPixels=pixels, note=note,
                               videoReferenceSeconds=time))
    source_video = next(ROOT.parent.glob('Batman*Remastered Opening Titles*.mp4'))
    video_file = 'opening/tas-opening.mp4'
    shutil.copy2(source_video, ROOT / video_file)
    capture = cv2.VideoCapture(str(source_video))
    fps = capture.get(cv2.CAP_PROP_FPS)
    duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    video_width, video_height = int(capture.get(3)), int(capture.get(4))
    capture.set(cv2.CAP_PROP_POS_MSEC, 36200)
    ok, frame = capture.read()
    assert ok
    poster = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    poster.thumbnail((1200, 675), Image.Resampling.LANCZOS)
    poster_file = 'opening/poster.jpg'
    poster.save(ROOT / poster_file, quality=90, optimize=True)
    capture.release()
    packet = dict(title='片头剪辑台', panels=panels,
                  storyboard=dict(book='Batman Animated', year=1998,
                                  drawing='Bruce Timm', color='Eric Radomski', storyboardYear=1992),
                  video=dict(file=video_file, sourceFile=source_video.name,
                             sha256=digest(source_video), duration=round(duration, 3),
                             width=video_width, height=video_height,
                             publisher='Warner Bros. Entertainment'),
                  poster=dict(file=poster_file, width=poster.width, height=poster.height,
                              sha256=digest(ROOT / poster_file), videoSeconds=36.2))
    (ROOT / 'tas-opening.json').write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n')
    print(f'Prepared {len(panels)} panels, original {duration:.2f}s video and poster')


if __name__ == '__main__':
    prepare()
