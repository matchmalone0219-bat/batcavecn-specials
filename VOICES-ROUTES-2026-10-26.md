# 康罗伊特稿：共用页面与页内分岔（2026-10-26，本地，未推送）

用户要求：两站的“蝙蝠侠之声”做成真正的共用页面；共同内容共读，读到动画与游戏不同的章节时页内切换、不跳转；视觉上让人感觉到两边的不同。备份：`backups/voices-routes-before-20261026/`。

## 结构
- 特稿只有一份，在根首页 `#kevin-conroy`。章节编号：01–04 共同 → 05 分岔 → 06–09 共同（Finding Batman、观众、回声、回到作品）。
- 分岔区（`#routes`）：动画线 05.1「声音如何进入一个人的内心」、05.2「让布鲁斯慢慢老去」；游戏线 05.1「游戏录音中的独角戏」。分组由 `conroy_profile.BRANCH` 定义。
- “回到作品”用同一套切换：动画列 BTAS/TNBA 与分集目录，游戏列阿卡姆作品；文案分别取 `works.siteBodies`。共享导语只保留第一句（archive.json 已改）。
- 年表中属于某一站的条目带“动画/游戏”标记，当前路线的标记会高亮。
- 入口：两站导航“蝙蝠侠之声”、页脚“凯文·康罗伊”、阿卡姆主菜单格子、作品页与 TAS 首页的人物链接 → `/?route=arkham#…` / `/?route=tas#…`。旧地址 `/arkham|tas/people/kevin-conroy/` 改为带路线的跳转页（`../../../`）。
- 默认路线：链接锚点落在某条线内时打开那条线 → 否则用 `?route=` → 否则动画。切换时 URL 的 `route` 参数跟着更新（replaceState）。
- 无 JS：两条线依次全文显示，标签与切换按钮隐藏。

## 视觉
- 共同部分保持共同档案原样（炭黑、米色、Georgia 章节号）。
- 两扇门（标签）：选中的一扇展开并连进下方内容；另一扇收起成标题条，下方用各自站点的分隔线封住（阿卡姆 HUD 刻度尺 / Dark Deco 双线）。
- 动画线：奶油纸面加颗粒，深红色，思源黑体 ExtraLight 标题与章节号，照片双线框，红色月亮标记。切换动画是 TAS 式的光圈从所选门的位置展开。
- 游戏线：#121716 底色加细网格，DIN 窄体大写标签，切角标签，录音笔记为切角面板。切换动画是扫描线自上而下扫过。
- 每条线结尾的“换到另一条线”按钮，用另一边的视觉做成一条（动画线末尾是阿卡姆暗条，游戏线末尾是 TAS 纸条）。
- 减弱动态偏好下没有动画。手机端门缩成两个并排标签。

## 改动文件
conroy_profile.py（新的 `voices_chapters`、门、作品切换、年表标记；删去旧的 `shared_work_directory`/`timeline`）、content_pages.py（移除 `person` 与 `person_chapters`）、crossover_pages.py（`redirect` 支持查询参数；章节搜索 `scopedUrls` 带路线）、site_pages.py、render_common.py（`person_url(site, anchor)`）、site_layout.py、arkham_ui.py、tas_pages.py、app.js（`voiceRoutes`；搜索里的康罗伊链接）、prepare_pages.py（`/?` 也加路径前缀）、conroy-profile.css（末尾 xroute 样式）、archive.json（works 共享导语）、AGENTS.md（两站边界规则）。

## 检查
全部 verify 通过（verify.py、verify-conroy.py 改写为共用页检查，含跳转页相对路径解析；verify-build.py、verify-arkham-nav.js 相应更新）。本地 Chrome 端到端：两站入口路线、默认、锚点直达、旧地址跳转、目录点进隐藏的线、门/作品标签/方向键/线尾切换同步、ARIA、减弱动态、无 JS 阅读。

## 发布注意
日常目录里还有另一路未提交的谜语人扫描溯源等改动（见 PROJECT-HANDOFF-2026-10-25.md 第5节）。远程 main 已到 5f070cf。推送这批时只同步上面列出的文件，并先在发布仓库里核对这些文件是否也被那路改动修改过（app.js、archive.json、site_layout.py、arkham_ui.py、verify.py 等）。

## 2026-10-27：共同页压缩（分支 voices-compact，基于 384e4ae）
- 用户反馈首页过长（桌面约 48 屏、手机约 61 屏）。特稿正文不动，压缩后三块：桌面降到约 29 屏、手机约 36 屏。
- 顶部（两站连续性说明之后）加三项本页目录：凯文·康罗伊 / 两座哥谭的角色（`#characters`）/ 演职员（`#credits`），整项可点。
- 角色对照：每组一行，左侧名字与概要，右侧动画与游戏两张小图（4:3），图片署名保持可见；作品列表和资料收进“作品与资料”。
- 演职员：片尾名单式（职务、姓名、外文名与年份、一句概要），小传、作品与资料收进“小传与作品”。
- 资料来源与人物资料出处默认折叠（“展开全部 N 条资料”）；正文引用编号不变。
- 改动：crossover_pages.py、conroy_profile.py（`profile_sources`）、conroy-profile.css（末尾 compact 样式）、verify-conroy.py（目录、折叠与署名检查）。
- 2026-10-27：引语块（封面与章节，含动画线/游戏线变体）去掉左侧竖线，改为上下细横线加顶部短横强调；verify-conroy.py 检查 conroy-profile.css 不含 border-left。
- 2026-10-27：阿卡姆体检修正（1–4）
  1. 场景细节页：删去《阿卡姆之城》39 段原视频折叠目录（违反文案规范“禁止前台堆砌长篇视频折叠目录”）。开头署名保留《疯人院》《骑士》各段与《之城》总集；每个《之城》条目底部列出所用视频（主来源加相关来源），用中性序号“彩蛋 NN / 总集 / 追加彩蛋”。verify-easter-eggs.py 相应更新。
  2. 共同页特稿：目录编号不透明度 0.85、声音对照小标签 #6e5a40 改为全局规则（原只作用于已停用的阿卡姆版页面）；手机端该标签 8px→10px。紧凑角色卡的“Dark Deco”标签与展开后作品年份的透明度一并提高，对比度全部 ≥4.5:1。
  3. 小丑、哈莉的游戏配图原为同一张宣传图，改为《阿卡姆疯人院》设定集中的各自角色设定图（crossover.json）。
  4. “用户提供录屏 / 用户提供游戏录制”改为来源类型“玩家录制（画面）”（arkham_soul.py、asylum-history、arkham-transmissions、patient-interviews、crossover 的来源标题与类型）；后台元数据未改。verify-conroy.py 检查页面不含“用户提供”。
- 2026-10-27：哥谭档案馆总览配图（arkham_pages.py `hub_art`）
  - 患者终端 a05-diploma（哈琳·奎泽尔心理学学位证书）；频段监听 arkham-city-05（新增，Steam 官方截图：霓虹招牌间俯瞰街区的蝙蝠侠）；场景细节 arkham-city-06（新增，Steam 官方截图：斯奥尼斯钢铁厂招牌）；哥谭故事 a07-layers；漫画与出版文献 a16-lighthouse；谜语人暂用 a12-robot（待换三部曲奖杯拼图）；院史、Rocksteady 不变。
  - 新截图登记在 media.json（WB Games / DC，官方商店截图，Steam GOTY，1280×720 原文件），并生成 webp；verify.py 媒体数 32→34。两张也会出现在《阿卡姆之城》作品页与图片资料页。
  - DC 漫画封面在 arkham-archive-research.json 标注为私有研究素材、未取得转载授权，未用于前台。
  - 预览框高度来自 aspect-ratio，原 is-contain / is-small 的 height:100% 不生效，竖图和证书被裁。改为把这类图绝对定位铺满框后再 contain；证书另设 is-document，按高度完整显示并微放大 4.2%，把扫描页上下的纸页白边推出框外（原图不改）。
  - 证书两侧不留黑边：同一张图的模糊压暗副本（aria-hidden）铺满预览框作底，证书本体加投影。
  - 证书原裁剪（设定集扫描 1 (80).jpg，x 101–1519）切掉了左侧约 60px 边框，上下又带纸页白边。按证书外框重裁为 [38,1981,1518,2860]，1480×879；arkham-artbook.json 的尺寸、裁剪坐标与 sha256 同步更新，webp 重新生成。预览不再需要放大，去掉 scale。
  - 注意：build_webp.py 会为别的工作流新增、尚无 webp 的图片（如 riddler-scans）批量生成副本；只提交本轮相关的 webp。
  - 谜语人机关考据配图改为用户提供的谜语人藏身处画面（riddler-hideout.jpg，1600×900），登记在新增的 arkham-hub-art.json（含 sha256，原始出处待补），build.py 复制到 dist，verify.py 校验哈希。竖图（如录音磁带截帧）在预览中与证书同样完整显示加模糊底；art_pool 纳入 recording-portraits。
