# 阿卡姆首页 · 原游戏开场与网页转场

2026-10-05：用户认可分离音效，授权搭建首页；随后反馈清晰度偏低，已从原文件重新导出1080p／60fps版。

## 素材与播放

- 原视频：`/Users/dinghaowei/Downloads/batcavecn/Batman  Arkham City Title Screen Theme Song ｜ (60fps) - Unforgettable Memories (1080p, h264).mp4`。用户本地提供，下载页面URL未登记；版权仍归原权利人。
- 使用0:00—4:55（295秒），保留游戏原标题、画面、原配乐；不含结尾上传者推广画面。原文件未修改。
- 网页视频`arkham-city-intro.mp4`：1920×1080、60fps、H264，CRF20／maxrate2500k／bufsize5000k，AAC128k；moov置前可边加载边播。大小97,629,600字节（93.11MiB），低于GitHub单文件100MiB限制。
- 首帧`arkham-city-intro-poster.jpg`为1920×1080。桌面和手机按16:9完整显示，黑色留白保留构图；手机横屏可看到更大画面。
- 初版720p／30fps、约33MiB已被替换。现版本仍有重新编码，不能视为原码率或无损副本。
- 原生loop返回开头；295秒附近与第一帧构图相近，镜头与雨滴仍有细小差异，并非逐像素无缝剪辑。没有重绘或插帧。

## 进入与声音

点击画面／进入按钮或Enter，触发1.3秒Canvas蝙蝠群转场。大小、速度、方向与翅膀相位不同，遮黑阶段展示现有八项资料菜单。菜单预置在同一文档中，音效不会被页面导航切断；地址更新为/arkham/menu/，刷新可直接打开菜单，返回／Esc回到标题页。方向键选择、Enter进入具体栏目沿用原菜单。

默认开场配乐静音，用户可“开启配乐”；“转场音效”独立开关，默认开启，仅点击／Enter播放。已认可M4A／WAV原字节保持，AAC浏览器容器约1.37秒（编码填充）自然播完。原始分离方法见BAT-TRANSITION-AUDIO.md。

暂停开场、减少动态偏好静帧、标签隐藏停止声音与画面、视频无法播放时仍可进菜单、无JavaScript时原生链接回退均保留。减少动态偏好跳过蝙蝠运动。

## 验证和交付

- python3 specials/verify.py：53页、459搜索记录、1462内部链接／锚点通过。与本轮备份比较，仅arkham/index.html变化；TAS和其他资料页面HTML、数据内容与媒体原件保持。
- node specials/verify-intro.js：重复点击、遮黑时机、音效连续性、减少动态、静音、播放／Canvas失败及动画停顿回退检查通过。
- 17,700帧完整解码通过，浏览器确认实际1920×1080、295秒及可播放状态；媒体校验值见output/arkham-intro-20261005/media.json。
- 浏览器1280×900／390×844：播放暂停、配乐开关、转场音效启闭、点击进入、Enter、方向键、菜单刷新、浏览器返回和Esc；无横向溢出。减少动态及故障路径通过脚本测试，不冒称已在真机切换系统设置验证。
- 截图在output/arkham-intro-20261005/；高清替换后home-desktop.png与home-mobile.png更新。转场截图为先前720p版时的过程记录。
- 本地预览http://127.0.0.1:8765/arkham/。恢复备份backups/arkham-intro-before-20261005/；本地更新包output/tas-pages-upload/已刷新。未推送GitHub、未部署。

## 进入提示位置调整（2026-10-05）

按用户要求，将“点击进入”移到视频内“Click to Start”下方，共用一个进入区域；保留Enter提示。进入链接按视频实际16:9画面定位，横向中心36.8%、纵向起点82%，随黑边和屏幕尺寸缩放。只改入口限定CSS，未改视频、音效、菜单或TAS。桌面1280×720、手机390×844实际检查位置与无横向溢出；点击原英文提示处成功进入菜单，音效自然结束。截图entry-together-desktop.png及entry-together-mobile.png。恢复CSS：backups/arkham-entry-placement-before-20261005/style.css。本地更新包已刷新；GitHub与部署状态保持未同步。

## 游戏菜单与共用转场续改（2026-10-05）

上述八项旧菜单已改为七项阿卡姆独立菜单，加入真实图片预览并移除TAS入口。入口动画提取为arkham-transition.js供标题进入及档案换页共用；arkham-nav.js保留音频节点以播完音效。当前54页／459记录／1467内部链接通过，视频和音效字节未改。详细范围见ARKHAM-GAME-UI.md。
