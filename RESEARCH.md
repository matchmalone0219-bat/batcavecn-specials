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

结构化资料在 `archive.json`。每条作品／分集通过 `sources` 引用来源记录；来源记录说明适用字段与边界。当前共21条来源，只有完成阅读的来源写入“已核查”。

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
