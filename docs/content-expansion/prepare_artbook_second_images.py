"""Rebuild the second selection from the supplied local scans; run in specials/."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PACKETS = {site: [] for site in ('arkham', 'tas')}


def crop(site, number, box):
    name = f'1 ({number}).jpg' if site == 'arkham' else f'BA_pg{number:03d}.jpg' if isinstance(number, int) else f'BA_pg{number}.jpg'
    path = ROOT.parent / ('蝙蝠侠设定集' if site == 'arkham' else 'C0022—Batman Animated') / name
    with Image.open(path) as source:
        pixels = [round(value * source.size[i % 2]) for i, value in enumerate(box)]
        result = source.crop(pixels).convert('RGB')
        meta = dict(sourceFile=name, cropNormalized=box, cropPixels=pixels,
                    sourceSize=list(source.size), sourceSHA256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result, meta


def save(site, id, selections, alt, kind, group, creator='', spoiler=False):
    pieces, sources = zip(*(crop(site, number, box) for number, box in selections))
    if len(pieces) == 1:
        image = pieces[0]
    else:
        image = Image.new('RGB', (1800, 1120), '#f2f0e9')
        for n, piece in enumerate(pieces):
            piece.thumbnail((850, 1040), Image.Resampling.LANCZOS)
            image.paste(piece, (n * 900 + (900-piece.width)//2, (1120-piece.height)//2))
    image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    file = f'artbook/{site}/{id}.jpg'
    image.save(ROOT / file, quality=91, subsampling=0, optimize=True)
    PACKETS[site].append(dict(id=id, file=file, width=image.width, height=image.height,
        alt=alt, kind=kind, group=group, creator=creator, sources=list(sources),
        sha256=hashlib.sha256((ROOT/file).read_bytes()).hexdigest(), spoiler=spoiler,
        book='rocksteady-2015' if site == 'arkham' else 'animated-1998', batch=2))


def A(id, number, box, alt, kind='装备概念设计', group='装备', creator='', spoiler=False):
    save('arkham', id, [(number, box)], alt, kind, group, creator, spoiler)


def T(id, number, box, alt, kind, group, creator='', spoiler=False):
    save('tas', id, [(number, box)], alt, kind, group, creator, spoiler)


A('a09-batarang', 54, [0, .02, .495, .97], '《疯人院》蝙蝠镖的游戏内渲染', '游戏装备渲染')
A('a10-grapnel', 87, [.052, .104, .447, .54], '抓钩枪收拢与发射状态的设计', creator='Lee Oliver')
A('a10-catgear', 88, [.555, .11, .755, .75], '猫女的尖刺、缠绕索与鞭子设计')
A('a10-staff', 89, [.025, .055, .49, .95], '罗宾长棍的伸展与盾面探索')
A('a11-clay', 82, [.025, .035, .49, .425], '泥面吞入蝙蝠侠的未采用遭遇概念', '未采用遭遇概念', '角色', 'Kan Muftic', True)
A('a11-watch', 82, [.705, .04, .99, .302], '蝙蝠侠在坠落怀表上与疯帽匠交战的概念', '遭遇概念探索', '环境', 'Lee Oliver', True)
A('a11-tea', 82, [.505, .36, .99, .80], '缩小的蝙蝠侠与巨型茶具的遭遇概念', '遭遇概念探索', '环境', 'Lee Oliver', True)
A('a12-mech', 132, [.006, .036, .493, .956], '谜语人机甲、废料机器人与机械臂的概念设计组图', creator='Oliver Odmark', spoiler=True)
A('a12-robot', 132, [.35, .425, .475, .90], '由废料拼装的谜语人机器人全身设计', creator='Oliver Odmark')
A('a13-launcher', 127, [.022, .03, .452, .476], '军事导弹发射器的折叠与展开设计', creator='Lee Oliver')
A('a13-drone', 127, [.022, .492, .452, .956], '自主步行无人机的概念方案', creator='Lee Oliver')
A('a13-tank', 128, [.507, .038, .994, .488], '以人物作尺度参照的重型无人战车概念', creator='Lee Oliver')
A('a13-cloud', 130, [.005, .035, .995, .97], 'Stagg Industries云爆装置及内部结构设计', creator='Lee Oliver', spoiler=True)

T('t13-dream', '019A', [.025, .303, .312, .428], '《Dreams in Darkness》以束缚姿态与栅栏光影构成的标题卡', '分集标题卡', '制作')
T('t13-abstract', '019B', [.348, .45, .637, .576], '《Harley and Ivy》用红黑橙绿构成的抽象标题卡', '分集标题卡', '制作', 'Eric Radomski / Glen Murakami')
T('t13-mudslide', 95, [.36, .46, 1, .755], '《Mudslide》标题画中泥脸与人类面孔的局部', '标题画局部', '制作', 'Eric Radomski / John Calmette')
T('t14-riddler', 106, [0, 0, .48, .96], '阴影中的谜语人绘画与口部动画的构图', '制作绘画', '角色', 'John Calmette')
T('t14-ivy', 116, [.405, .005, 1, .61], '琳恩·内勒为毒藤女绘制的头部与姿态研究', '角色设计草图', '角色', 'Lynne Naylor')
T('t14-bane', 118, [0, .015, 1, .40], '贝恩的正面体形与弯身姿态研究', '早期角色设计', '角色', 'Bruce Timm')

for id, left, right, alt in [
    ('t15-clay', (95, [0, 0, 1, .37]), (135, [.49, .51, 1, 1]), '左：BTAS泥脸的动作研究；右：TNBA更圆厚的色彩模型'),
    ('t15-croc', (117, [0, .57, 1, 1]), (136, [0, .54, .39, 1]), '左：BTAS《Vendetta》动作分镜；右：TNBA杀手鳄色彩模型'),
    ('t15-bane', (118, [0, .015, 1, .40]), (136, [.66, .518, 1, 1]), '左：BTAS贝恩初步模型；右：TNBA黑色皮装与铆钉造型'),
    ('t15-hatter', (108, [.218, .16, .80, .475]), (135, [.25, 0, .57, .51]), '左：BTAS疯帽匠探索稿；右：TNBA更接近坦尼尔插画的造型'),
]:
    save('tas', id, [left, right], alt, 'BTAS／TNBA图像对照', '角色')

T('ep2-joker-turn', 67, [.035, .325, .995, 1], '小丑慢慢转身、向前逼近的分镜', '表演分镜', '分镜', 'Bruce Timm', True)
T('ep2-joker-pause', 68, [.01, 0, .99, .73], '小丑激动指责、短暂停顿后恢复微笑的分镜', '表演分镜', '分镜', 'Bruce Timm', True)
T('ep2-garden-mirror', 112, [0, .005, 1, .36], '车内后视镜出现怪物与突然袭击的分镜', '悬念分镜', '分镜', 'Ronaldo Del Carmen', True)
T('ep2-garden-road', 115, [0, .005, 1, .60], '布鲁斯下车检查伤口并回望的分镜', '悬念分镜', '分镜', 'Ronaldo Del Carmen', True)
T('ep2-avatar-rise', 99, [.005, .005, .995, .465], '泥浆中的手脸聚成触手的动作分镜', '动作与效果分镜', '分镜', 'Bruce Timm', True)
T('ep2-avatar-rescue', 101, [0, .005, 1, .50], '蝙蝠侠跃下、接住塔莉亚并拔剑的动作分镜', '动作分镜', '分镜', 'Bruce Timm', True)

T('t17-harley', 69, [0, 0, .445, 1], '1996年华纳商店哈莉瓷像的书内商品摄影', '历史商品摄影', '收藏', 'Geoff Spear')
T('t17-penguin', 92, [.60, 0, 1, .61], '1992年英国Avon企鹅人儿童清洁用品瓶盖的书内摄影', '历史商品摄影', '收藏', 'Geoff Spear')
T('t17-riddler', 106, [.48, 0, 1, .43], '1995年Prelude UK谜语人泡泡浴瓶的书内摄影', '历史商品摄影', '收藏', 'Geoff Spear')
T('t17-batman-maquette', '137B', [0, 0, 1, 1], '格伦·王制作的TNBA蝙蝠侠立体参考模型', '立体参考模型摄影', '制作', 'Glenn Wong / Geoff Spear')
T('t17-robin-maquette', '138A', [0, 0, 1, 1], '格伦·王制作的蒂姆·德雷克罗宾立体参考模型', '立体参考模型摄影', '制作', 'Glenn Wong / Geoff Spear')

A('a14-civilians', 137, [.01, .02, .49, .98], '《骑士》男性市民的体形与服装概念组图', '人物概念设计', '角色', 'Oliver Odmark')
A('a15-penguin', 77, [.505, 0, .995, 1], '《之城》企鹅人的宣传渲染', '宣传渲染', '角色')
A('a15-tyger', 84, [.015, .36, .49, .955], 'TYGER保安的正背面、手套与靴子参考', '角色与服装研究', '角色', 'Kan Muftic')
A('a16-lighthouse', 46, [0, 0, .87, 1], '疯人院灯塔早期平面图中的入口与维修通道', '早期环境平面图', '环境')
A('a16-studios', 119, [.505, .025, .995, .47], '哥谭电影城入口的衰败建筑与屋顶雕像', '环境概念图', '环境', 'Kan Muftic')
A('a16-clock', 117, [.675, .49, .995, .962], '因体形显得矮胖而被放弃的哥谭钟楼地标', '未采用建筑概念', '环境', 'Kan Muftic')

T('t19-day', 141, [0, 0, .435, .521], 'TNBA警察总部与病黄色的白昼天空', '背景设计与色稿', '环境', 'Richie Chavez / David McBride')
T('t19-night', 141, [.47, 0, 1, .521], 'TNBA高架铁路与红色夜空', '背景设计与色稿', '环境', 'Michele Graybeal / David McBride')
T('t19-beyond', 151, [0, 0, 1, .935], '1998年《Batman Beyond》的姿态与轮廓探索', '开发期角色研究', '角色', 'Bruce Timm')
T('t20-gordon', 79, [.02, .05, .77, .505], '1990年提案片戈登的全身与头部模型', '提案片模型纸', '角色', 'Bruce Timm')
T('t20-montoya', 80, [.005, .65, .305, .995], '1991年蒙托亚两种表情与角度的头部研究', '初步角色模型', '角色', 'Lynne Naylor')
T('t21-cave', 50, [0, 0, 1, .415], '蝙蝠洞里的人物、平台与巨大岩壁', '布局与背景色稿', '环境', 'Ted Blackman / Russell Chong')
T('t21-car', 52, [0, 0, 1, .425], '流线型蝙蝠车的背景绘画与原页设计说明', '载具设计色稿与原页说明', '装备', 'Shayne Poindexter / Russell Chong')
T('t21-wing', 52, [0, .45, 1, .94], '黑色蝙蝠翼的机翼与座舱造型', '载具设计色稿', '装备', 'Bruce Timm / Shayne Poindexter / Russell Chong')
T('t22-ras', 97, [.27, .87, 1, 1], '拉斯·奥·古不同角度与表情的头部研究', '表情与角度研究', '角色', 'Chen-Yi Chang')
T('t22-freeze', 110, [0, .265, 1, .495], '《Heart of Ice》急冻人望向小雕像的分镜', '表演分镜', '分镜', 'Bruce Timm', True)
T('t23-early', 94, [0, 0, 1, .585], '早期未来主义哥谭色彩方案中的企鹅人与蝙蝠侠', '早期风格概念画', '环境', 'Bruce Timm / Laura Lee Lizak')
save('tas', 't23-sega', [(93, [.54, .01, .995, .25]), (93, [.54, .535, .995, .845])], '世嘉蝙蝠侠CD-ROM游戏删去的企鹅人段落分镜节选', '游戏删去段落分镜选区并置', '分镜', 'Butch Lukic')
T('ep2-batgirl-whip', 85, [0, 0, 1, .388], '猫女挥鞭、蝙蝠女投出蝙蝠镖的分镜', '动作分镜', '分镜')
T('ep2-batgirl-route', 86, [.005, .222, .995, .655], '猫女沿展品、栏杆和高处窗框逃走的分镜', '连续运动分镜', '分镜')

if __name__ == '__main__':
    out = ROOT / 'work/artbook-second'
    out.mkdir(parents=True, exist_ok=True)
    for site, rows in PACKETS.items():
        (out/f'{site}-images.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
    print({site: len(rows) for site, rows in PACKETS.items()})
