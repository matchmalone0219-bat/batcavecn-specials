# 专题资料核查记录｜2026-10-02

本轮目标：补充资料与可阅读档案；阿卡姆原游戏动态首页待素材，不继续自行仿制动画。当前为本地建设资料，不是完整百科或线上发布。

## 已整理

| 范围 | 入库成果 | 依据与口径 |
| --- | --- | --- |
| 四部核心游戏 | 四篇基础详情；开发、发行、原版平台、无剧透导读、声音及版本边界 | DC作品资料、历史公告、演员本人访谈、发行商商店 |
| BTAS | 85条英文名称、指南编号、来源所载日期；001–085连续且无重复 | The World’s Finest三页指南；不复制剧情梗概和评论 |
| 三篇动画详情 | Nothing to Fear / Perchance to Dream / I Am the Night | 分集辅助署名；另有康罗伊本人访谈与DC回顾 |
| 演员关系 | Asylum / City / Knight → Kevin Conroy；Origins → Roger Craig Smith | 三部曲回顾、City历史回顾、Smith本人访谈；未知单集角色留空 |
| 版本 | 原作、Steam GOTY与Return to Arkham区别；City六类DLC | Steam具体版本条目、华纳意大利历史公告 |
| TAS制作背景 | 已收集主要制作／配音人员、109集全集盒装与另附两部电影 | 华纳历史新闻稿转载；此资料收在来源表，制作专题尚待展开 |

结构化资料在 `archive.json`。每条作品／分集通过 `sources` 引用来源记录；来源记录说明适用字段与边界。当前共25条来源，只有完成阅读的来源写入“已核查”。

## 字段依据

- Asylum：日期／平台→`dc-asylum`；玩法与GOTY挑战地图→`steam-asylum`；重制合集→`wb-return`；演员合作→`dc-trilogy`。
- City：原版早期首发计划／开发→`dc-city-announcement`；故事主创与两位演员→`dc-city-history`；GOTY收录／商店版本日期→`steam-city`。
- Origins：基本信息与前传定位→`dc-origins`；Smith／Baker及年轻角色表演→`rcs-origins-interview`。
- Knight：日期／平台／蝙蝠车→`dc-knight`；Conroy／Hamill合作→`dc-trilogy`（原文含剧透）。
- BTAS001–030→`wf-guide`；031–060→`wf-guide-31-60`；061–085→`wf-guide-61-85`。三页同时出现旧版和新版排版文本；入库时核对两份的名称与日期一致，只统一直／弯引号，消除重复。
- Nothing to Fear署名→`wf-fear`；Perchance to Dream署名→`wf-dream`；I Am the Night署名→`wf-night`。
- 系列制作背景／盒装范围→`wb-btas-blu`。历史稿的预定上市日未当成最终上市事实。

## 需要保留的区别

1. 《之城》2011年公告含后来调整的PC计划，不直接用它填PC最终日期。Steam GOTY的2012-09-07与原作2011年分开。
2. 《疯人院》Steam GOTY的2010-03-26与原作2009年分开。
3. Return to Arkham由Virtuos重制Asylum／City；引用的2016-10-18是意大利上市记录，不推广为全地区日期。
4. Rocksteady三部曲与本站首批四部核心游戏名单不同，不把Origins塞进三部曲合集。
5. 指南编号、完整制作代码、首播地区与影音目录编号分开。当前85条只有辅助指南和来源所载日期，完整制作代码、地区与影音编号全部留空。
6. 《Perchance to Dream》Story与Teleplay分开；未署名声音不能当成已核片尾署名。《I Am the Night》配乐列Michael McCuistion，不统一填Shirley Walker。
7. 109集盒装包含不同电视阶段，另附电影不计入85条BTAS基础目录。TNBA暂未入库。
8. 现有三集中文名为本站暂译，新增82条先显示英文名称，不批量制造所谓正式中文译名。

## 下一批资料

- 核对85集片尾／完整制作代码与家庭影音目录，建立可靠的美国首播地区字段；再开放顺序切换。
- 深度选集优先：Heart of Ice、Beware the Gray Ghost、Joker’s Favor、Almost Got ’Im，以及双面人／罗宾／拉斯的双集故事。先核对单集主创再撰写原创导读。
- 四部游戏：主创片尾、配乐、关键角色／地点关系，逐作DLC及地区实际发售日期。City的PC延后报道已找到，最终一手公告仍待补。
- 扩展与收藏：Blackgate、VR、Shadow，Return to Arkham／Trilogy／Collection分别建版本记录，不能混作新故事。
- 站内旧文章／访谈关联仍需逐篇核对，不根据标题自动挂接。

## 恢复与验证

资料更新前的内容备份：`backups/archive-before-research-20261002.json`（本地保留，不上传）。基础条目没有虚构详情页；搜索可定位目录中的真实记录。检查覆盖85条编号唯一连续、90条搜索记录、详情实际链接、Origins演员关系与剧透边界。

## 披风斗士增补

按用户要求纳入TAS站，单独以“延续与再诠释”编目。“现代延续尝试”为本站策展视角，不等于剧情续作或DCAU连续性。DC两篇介绍／评论、Amazon官方更新与Prime Video第一季节目单为4条新增来源。首季10集仅登记英文原名与平台顺序；不加入BTAS85条。Prime第7集日期显示与其他集不同，不据此批量填写首播日。Amazon核查时已更新为第二季10集上线，第二季逐集目录待补。新增配音Hamish Linklater独立记录。

增量检查：20页、91搜索记录、297内部链接与锚点；BTAS数量85保留；新系列实际详情页可达，康罗伊作品列表未增加本作。

## 文字与图片增补（2026-10-02）

- BTAS新增8篇：Heart of Ice、Beware the Gray Ghost、Joker’s Favor、Almost Got ’Im、Two-Face上下篇、Robin’s Reckoning上下篇。共11篇可阅读选集档案，署名来自逐集辅助资料，原创导读与来源评论分开。
- 两篇Story／Teleplay分别记录；Heart of Ice作曲Todd Hayen、监制Shirley Walker；Robin’s Reckoning两篇作曲Carlos Rodriguez／Peter Tomashek不同。幼年Dick年龄来源不一致，留空。
- TNBA24条英文名、辅助指南编号及来源日期单独编目，网址中的01–26不当成26集；电影及其他系列客串不加入24条。
- 披风斗士第二季10集英文原名与平台顺序已补；Prime美国页面日期与Amazon公告相差一天，不把差异抹去后填成全球首播。
- Origins补Cold, Cold Heart与PC在线服务退役说明；Knight区分Harley Quinn／Red Hood角色故事包与Prototype Batmobile外观皮肤。尚未完成全DLC清单。
- 图片24张：游戏每作4张，共16张；DC经典动画配图3张；披风斗士系列美术1张、第二季宣传图4张。每张实际解码、尺寸核查、目视检查、来源及归属登记。
- 图片主要来源Steam发行商商品页／公开资料接口、DC文章及Amazon官方报道；The World’s Finest截图本轮仅作为参考入口，不搬运其图库。
- 30页、115条搜索记录、41条文字来源；24张图片另有逐张来源记录。不宣称全文主创、全部分集或图片库已完整。

## 同日补充：Blackgate、Suicide Squad与创作变迁（2026-10-06）

作品目录由四部增至六部；原谜语人与场景研究的四作范围保持。Blackgate依据DC原作页与Armature总监Mark Pacini署名文，原版2013-10-25／Vita、3DS；豪华版Steam 2014-04-01。英语配音字段暂留空，模板不输出空事实。Suicide Squad依据WB发表公告、游戏FAQ、Steam普通版日期与DC编辑文章确认康罗伊出演；DC人物后续来源本身含剧透，标题标注。正文不展开主线与赛季结局。

rocksteady-history.json保存十三节正文与来源ID。2020公告与2022交接信作为人事／产品顺序的一手依据；HundredStar公司官方简介列2023年与两位创办人。2024Q1财报只用于收入表现，不将任何业绩差额写为游戏制作预算。2024年9月、2025年1月的裁员来源为Game Developer对Eurogamer员工采访的转述，保留来源级别。2026-07-02设计人员回顾读取GamesRadar转述，日期由公开页面datePublished确认；Bloomberg原文未全文读取，不伪称直接采访。分析以独立章节标识，不将人物离职自动当成玩法转向的原因。

Steam API原始响应与新闻保留在output/arkham-expansion-20261006；12月离线模式公告经公开重定向读取，使用最终Steam公告URL。2025-01-14第八章依据官方更新日志与第四赛季FAQ编排；公告保留线上功能是来源陈述，未实测线上服务连通性。
