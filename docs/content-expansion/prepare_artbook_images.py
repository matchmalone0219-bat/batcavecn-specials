from pathlib import Path
import hashlib,json
from PIL import Image,ImageOps,ImageDraw
ROOT=Path('.').resolve()
(ROOT/'work/artbook-expansion').mkdir(parents=True,exist_ok=True)
assets={s:[] for s in ['arkham','tas']}

def crop(site,n,box):
    fn=f'1 ({n}).jpg' if site=='arkham' else f'BA_pg{n:03d}.jpg' if isinstance(n,int) else f'BA_pg{n}.jpg'
    folder='蝙蝠侠设定集' if site=='arkham' else 'C0022—Batman Animated'
    src=ROOT.parent/folder/fn
    with Image.open(src) as im:
        px=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box))
        result=im.crop(px).convert('RGB')
        meta=dict(sourceFile=fn,cropNormalized=box,cropPixels=px,sourceSize=list(im.size),sourceSHA256=hashlib.sha256(src.read_bytes()).hexdigest())
    return result,meta

def asset(site,id,n,box,alt,kind,group,creator='',spoiler=False):
    im,meta=crop(site,n,box)
    return save(site,id,im,[meta],alt,kind,group,creator,spoiler)

def save(site,id,im,sources,alt,kind,group,creator='',spoiler=False):
    file=f'artbook/{site}/{id}.jpg';p=ROOT/file;p.parent.mkdir(parents=True,exist_ok=True)
    im.thumbnail((1800,1800),Image.Resampling.LANCZOS);im.save(p,quality=91,subsampling=0,optimize=True)
    row=dict(id=id,file=file,width=im.width,height=im.height,alt=alt,kind=kind,group=group,creator=creator,sources=sources,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),spoiler=spoiler,book='rocksteady-2015' if site=='arkham' else 'animated-1998')
    assets[site].append(row);return id

# Crops are selected from the supplied scans; all source rectangles stay in the manifest.
A=lambda id,n,b,alt,k,g,c='':asset('arkham',id,n,b,alt,k,g,c)
A('a01-vision',5,[0,0,.495,1],'《疯人院》蝙蝠侠宣传渲染','宣传渲染后期绘制','角色')
A('a01-arrival',6,[0,0,1,1],'雨中的蝙蝠侠游戏画面','游戏画面','角色')
A('a01-legacy',150,[0,0,.495,1],'《之城》宣传形象与城市背景','宣传渲染','角色')
A('a02-pencil',15,[.51,.32,.72,.88],'早期高瘦蝙蝠侠与滴水兽草案','概念草图','角色','John Gravato')
A('a02-croc',16,[0,0,.495,1],'鳞片与链条构成的杀手鳄模型','游戏角色渲染','角色')
A('a02-batman',19,[.04,.03,.49,.46],'胸徽与体形不同的两版蝙蝠侠草案','概念草图','角色','John Gravato')
A('a03-exterior',30,[0,0,.495,1],'尖顶与入口体量夸张的疯人院外景','环境概念图','环境','Drew Wilson')
A('a03-light',34,[0,.17,.49,.495],'高大室内以冷色光突出行进方向','光照研究','环境','John Gravato')
A('a03-pipes',36,[.005,.02,.495,.97],'管线模块与巨门组成的室内设计','环境设计组件','环境')
A('a04-cape',58,[.04,.02,.485,.35],'披风开口与布料运动探索','动作设计草图','装备','John Gravato')
A('a04-predator',61,[0,0,.495,1],'高处观察的蝙蝠侠剪影','概念插画','角色','John Gravato')
A('a05-skyline',69,[.02,.025,.46,.955],'污染色调下的旧哥谭天际线探索','环境概念图','环境','Kan Muftic')
A('a05-iceberg',72,[.165,.03,.335,.39],'冰山俱乐部复古招贴设计','道具与标识设计','装备')
A('a05-museum',73,[.54,.07,.965,.365],'博物馆展陈空间与牢笼改造','环境概念图','环境','Kan Muftic')
A('a05-diploma',80,[.02,.565,.302,.83],'哈琳·奎泽尔的哥谭大学心理学学位证书道具','环境叙事道具','装备')
A('a06-city',94,[.665,.07,.995,.34],'黑暗街道中的蝙蝠侠与城市灯光','概念插画','环境','Kan Muftic')
A('a07-vertical',112,[.035,.16,.465,.97],'哥谭高楼的垂直尺度','环境概念图','环境','Lee Oliver')
A('a07-layers',114,[.505,.035,.98,.58],'密集标识与建筑叠加的城市研究','环境设计图','环境')
A('a07-wayne',116,[.515,.025,.97,.95],'韦恩大楼立面与高度探索','环境概念图','环境','Lee Oliver / Oliver Odmark')
A('a07-sculpture',118,[.505,0,1,1],'屋顶雕像改变建筑轮廓','环境设计探索','环境')
A('a08-cape-fastener',106,[.01,.03,.49,.32],'披风肩部连接结构','游戏角色细部渲染','装备')
A('a08-armour',106,[.505,0,1,1],'《骑士》战衣宣传渲染','宣传渲染','角色')
A('a08-wheel',143,[0,0,.495,1],'蝙蝠车轮毂与车身细节','游戏车辆渲染','装备')
A('a08-batmobile',144,[0,0,1,1],'蝙蝠车与蝙蝠侠的游戏画面','游戏画面','装备')
T=lambda id,n,b,alt,k,g,c='',spoiler=False:asset('tas',id,n,b,alt,k,g,c,spoiler)
T('t01-batman',3,[.015,0,.99,.76],'1990年布鲁斯·蒂姆的蝙蝠侠研究','早期角色研究','角色','Bruce Timm')
T('t01-team',26,[.165,.675,.565,.90],'1992年首播周的制作团队合影','制作团队照片','制作','')
T('t02-layout',38,[.01,0,.99,.46],'《猫与爪》屋顶追逐布局稿','场景布局稿','环境','Kevin Altieri')
T('t02-colour',41,[0,0,1,.39],'哥谭楼群线稿与色稿并置','背景设计与色稿','环境','Keith Weesner / John Calmette')
T('t02-alley',42,[0,.575,1,1],'犯罪巷的色块与透视','背景色稿','环境','Keith Weesner / John Calmette')
T('t02-height','045and046',[0,0,1,1],'高楼之间俯视的哥谭夜景','背景色稿','环境')
T('t03-bank',26,[.67,.01,1,1],'片头银行的竖向构图与爆炸','1992年片头分镜节选','分镜','Bruce Timm / Eric Radomski')
T('t03-car',27,[0,0,1,.54],'蝙蝠车离洞与驶入街区的片头分镜','1992年片头分镜节选','分镜','Bruce Timm / Eric Radomski')
T('t03-fight',30,[0,0,1,.70],'片头屋顶格斗的姿态与剪影','1992年片头分镜节选','分镜','Bruce Timm / Eric Radomski')
T('t03-reveal',32,[.05,.68,.99,1],'片头闪电揭示蝙蝠侠的收束镜头','1992年片头分镜节选','分镜','Bruce Timm / Eric Radomski')
T('t04-batman',48,[0,0,1,.54],'蝙蝠侠的动态姿态研究','模型纸','角色','Bruce Timm')
T('t04-robin',55,[0,0,.77,.56],'迪克·格雷森的罗宾初步模型','早期模型纸','角色','Bruce Timm')
T('t04-batgirl',56,[.40,.01,.78,.72],'蝙蝠女原始色彩模型','色彩模型','角色','Bruce Timm')
T('t04-alfred',57,[.34,.52,1,1],'阿尔弗雷德的表情与头部角度','表情模型纸','角色','Mike Gougen')
T('t05-notes',35,[0,.36,1,.63],'广播审看修改单的局部','制作修改记录','制作')
T('t05-satire',36,[0,.443,.605,.984],'布鲁斯·蒂姆讽刺播出限制的插画','制作团队讽刺画','制作','Bruce Timm')
T('t06-recording',33,[0,.685,.525,1],'《Almost Got ’Im》1992年录音演员合影','录音合影','制作')
T('t06-joker',65,[0,0,.46,.435],'小丑夸张下巴与牙齿的早期草图','早期角色草图','角色','Bruce Timm')
T('t07-score',34,[0,.53,1,1],'雪莉·沃克为《Never Fear》写作的手稿局部','配乐手稿','制作','Shirley Walker')
T('t08-sketch',69,[.445,0,1,.54],'保罗·迪尼的哈莉初稿','初步角色草图','角色','Paul Dini')
T('t08-board',70,[0,.69,1,1],'哈莉与小丑对戏的表情变化','表演分镜','分镜')
T('t08-model',71,[.445,.40,1,.69],'哈莉的旋转模型纸','模型纸','角色')
# Six image pairs keep the two designs in separate, uncropped source rectangles.
def pair(id,left,right,alt):
 ims=[];metas=[]
 for n,b in [left,right]:
  im,m=crop('tas',n,b);im.thumbnail((850,1000),Image.Resampling.LANCZOS);ims.append(im);metas.append(m)
 board=Image.new('RGB',(1800,1080),'#f2f0e9')
 for x,im in zip([25,925],ims):board.paste(im,(x+(850-im.width)//2,40+(1000-im.height)//2))
 save('tas',id,board,metas,alt,'BTAS／TNBA设计对照','角色')
pair('t09-batman',(48,[0,0,1,.54]),('139A',[0,0,1,1]),'左：BTAS蝙蝠侠动态模型；右：TNBA色彩设计')
pair('t09-robin',(54,[.30,0,1,.65]),('139B',[0,0,1,.85]),'左：迪克·格雷森罗宾；右：蒂姆·德雷克罗宾设计')
pair('t09-catwoman',(84,[.38,.05,1,.66]),(136,[.71,.02,1,.54]),'左：BTAS猫女；右：TNBA猫女设计')
pair('t09-penguin',(91,[0,0,.59,.78]),(135,[.66,0,1,.51]),'左：BTAS企鹅人初步模型；右：TNBA企鹅人')
pair('t09-ivy',(111,[.10,0,1,.55]),(135,[.25,.51,.48,1]),'左：BTAS毒藤女头部研究；右：TNBA色彩模型')
pair('t09-scarecrow',(108,[.18,.60,1,1]),(136,[0,0,.37,.62]),'左：BTAS《Fear of Victory》标题画；右：TNBA稻草人模型')
T('t10-posters',119,[0,.52,1,.78],'《幽灵的面具》的海报探索','海报概念稿','制作','Bruce Timm')
T('t10-future',120,[0,.40,1,.70],'世界博览会未来之家的明亮室内','背景设计','环境','Rae McCarson / Steve Butz')
T('t10-ruin',120,[0,.72,1,1],'多年后废弃的未来之家','背景设计','环境','Rae McCarson / Steve Butz',True)
T('t11-cave',125,[0,.53,1,.98],'急冻人的北极冰穴与诺拉的容器','背景铅笔稿','环境','Ted Blackman')
T('t11-operation',126,[0,.36,1,1],'海上平台手术室','背景色稿','环境','Ted Blackman / John Calmette')
T('t12-pencils',74,[0,0,1,.60],'1998年《Harley & Ivy》开发铅笔页','漫画开发铅笔稿','出版','Bruce Timm')
T('t12-colour',75,[0,0,1,.64],'《Mad Love》的色彩指导稿','漫画着色指导','出版','Bruce Timm')
# Episode-specific additions reuse main assets where possible, with a few focused crops.
T('ep-leather',107,[.16,.495,1,.747],'凯文·诺兰的人蝠姿态研究','角色研究','角色','Kevin Nowlan')
T('ep-twoface-one',87,[0,.50,1,1],'《Two-Face: Part 1》揭面分镜与修改贴纸','分镜与修改稿','分镜','Kevin Altieri',True)
T('ep-twoface-two',89,[0,0,.78,.65],'哈维·丹特双面构图的初步铅笔研究','初步角色研究','角色','Bruce Timm',True)
T('ep-fish',64,[0,0,1,.46],'《The Laughing Fish》中小丑逼近受害者的分镜','分镜','分镜','Bruce Timm / Ronaldo Del Carmen')
T('ep-freeze',109,[0,.55,1,1],'急冻人的机械服与头部模型研究','模型纸','角色','')
T('ep-clay',96,[0,.47,1,1],'泥脸的动作与表情研究','动作模型纸','角色','')
T('ep-hatter',108,[.218,.16,.80,.475],'疯帽匠的角色探索','角色概念稿','角色','Kevin Nowlan')
T('ep-legends-sprang',144,[0,0,.70,.45],'蒂姆重释迪克·斯普朗式蝙蝠侠与罗宾','剧中风格模型','角色','Bruce Timm',True)
T('ep-legends-miller',146,[0,0,1,.58],'米勒式壮硕蝙蝠侠与凯莉·凯利','剧中风格模型','角色','',True)
T('ep-creeper',143,[0,.73,1,1],'杰克·莱德与狂笑人的角色设计','角色设计','角色','')
joker_body,body_meta=crop('tas',133,[0,0,.445,.79])
joker_faces,face_meta=crop('tas',133,[.445,0,1,.64])
joker_body.thumbnail((650,1400),Image.Resampling.LANCZOS)
joker_faces.thumbnail((1100,1400),Image.Resampling.LANCZOS)
joker_board=Image.new('RGB',(1800,1500),'#f2f0e9')
joker_board.paste(joker_body,(25+(650-joker_body.width)//2,(1500-joker_body.height)//2))
joker_board.paste(joker_faces,(700+(1100-joker_faces.width)//2,(1500-joker_faces.height)//2))
save('tas','t09-joker-detail',joker_board,[body_meta,face_meta],'TNBA小丑的全身与表情设计','模型与表情研究','角色','Bruce Timm')
T('t09-nightwing',131,[0,0,1,.46],'夜翼的转身模型','模型纸','角色','Glen Murakami')
T('t09-batgirl-detail',140,[.47,0,.73,.50],'TNBA蝙蝠女的黑色服装造型','角色设计','角色','Bruce Timm')
# Existing role anchors and cast facts are retained.
roles=[('role-1',47,[.05,.03,.65,.49],'蝙蝠侠'),('role-2',57,[.69,.575,.86,.75],'阿尔弗雷德'),('role-3',79,[.41,.12,.62,.35],'戈登'),('role-4',55,[.46,.16,.75,.42],'迪克·格雷森／罗宾'),('role-5',79,[.45,.59,.81,.94],'布洛克'),('role-6',65,[0,0,.46,.435],'小丑'),('role-7',89,[.02,0,.62,.51],'哈维·丹特／双面人'),('role-8',81,[0,0,1,.94],'猫女'),('role-9',70,[.35,0,1,.65],'哈莉'),('role-10',91,[.10,.01,.53,.54],'企鹅人'),('role-11',56,[.42,.08,.67,.34],'芭芭拉／蝙蝠女'),('role-12',95,[.40,.01,.72,.23],'泥脸'),('role-13',109,[.19,.495,.40,.65],'急冻人'),('role-14',97,[.40,.22,.99,.80],'拉斯·奥·古'),('role-15',105,[.40,.593,.60,.738],'谜语人')]
for role,n,b,name in roles:
 im,meta=crop('tas',n,b);im=ImageOps.pad(im,(480,480),method=Image.Resampling.LANCZOS,color='#f1eee5')
 rowid=save('tas','portrait-'+role,im,[meta],name+' · BTAS角色设计','BTAS角色头像','头像')
 assets['tas'][-1]['portraitRole']=role
 thumb=ROOT/f'artbook/tas/portrait-{role}-small.jpg';im.resize((120,120),Image.Resampling.LANCZOS).save(thumb,quality=90,subsampling=0)
 assets['tas'][-1]['thumbnail']=str(thumb.relative_to(ROOT))
 assets['tas'][-1]['thumbnailSHA256']=hashlib.sha256(thumb.read_bytes()).hexdigest()
 # Keep the padding transformation alongside the original selected rectangle.
 assets['tas'][-1]['transform']='crop source rectangle, resize to fit 480x480, pad with neutral paper colour; thumbnail 120x120'
for site in assets:
 (ROOT/f'work/artbook-expansion/{site}-assets.json').write_text(json.dumps(assets[site],ensure_ascii=False,indent=2)+'\n')
print({s:len(a) for s,a in assets.items()})
