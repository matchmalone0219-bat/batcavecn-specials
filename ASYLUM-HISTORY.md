# 疯人院院史 · 核查与接入记录

核查日期2026-10-03。数据见asylum-history.json，页面/arkham/archive/asylum-history/，由arkham_pages.py生成。已接入阿卡姆档案馆整卡、分类导航、搜索、来源和图库。本站暂译“阿卡姆之魂”，官方中文名待核。

## 已保存内容

23处刻字石碑与一条最终记录；24条主题索引沿用Homm_Syndrome转录中的Deciphered Messages顺序，不是攻略地点编号。未把任一剧情序号绑定具体截图或扫描位置。正文增加家族记忆与不可靠讲述者导读、Paul Dini的空间设计访谈、漫画与游戏连续性的区别。24条是简短主题索引，不是完整译文或游戏原文。身份与最终画面默认折叠，搜索只含中性编号与导言。

## 来源及用途

- [Homm_Syndrome / GameFAQs，2009-09-03](https://gamefaqs.gamespot.com/ps3/952338-batman-arkham-asylum/faqs/57651)：已读取24条转录及角色说明。PS3索引；原游戏版本、音轨和解锁画面尚未逐条核验。
- [Faxagate，2023-10-19](https://www.faxagate.com/en/gaming/batman-arkham-asylum-spirit-of-arkham)：正文与现场图片已读取。用于数量、载体与场景辨认；攻略扫描位置不作叙事顺序。
- [GameSpot / Paul Dini访谈，2009-04-21](https://www.gamespot.com/articles/batman-arkham-asylum-qanda-writer-paul-dini-on-arkham-batman-and-more/1100-6208260/)：旧庄园、现代医院、岛屿隔离感等空间构想。未声称其具体解释了Chronicles的写作意图。
- [DC / Alex Jaffe，2022-01-26](https://www.dc.com/blog/2022/01/26/a-tough-cell-arkham-asylums-seriously-troubled-history)：漫画回顾。1974年登场与1989年漫画作跨媒介背景，不补入游戏年表。
- 身份段落另以DC Database社区人物汇编交叉核查，链接和身份说明在页面收起显示。续作的补充解释不混入本作索引。

## 图片

四张Faxagate原始WebP，均1280×720：重症治疗区、庄园、阿卡姆东区石碑及最终地面记录。图片原地址、图注、来源、尺寸、sha256和剧透状态保存在JSON。保留原字节和HUD，不裁切、重绘或改水印。原游戏画面归DC / Warner Bros. / Rocksteady；未取得开放转载授权。甲虫纹样仅用于辨认石碑；东区图片未被擅自命名为阿玛迪斯墓碑。

## 待补

原版与重制版逐条音轨、字幕／中文措辞、解锁界面及版本差异；游戏内人物档案与具体历史事件的逐条对应。现有第一人称材料不作无争议的客观建院年表，也未认定超自然附身成立。

## 验证与发布状态

52页、451条搜索记录、1413处内部链接／锚点检查通过；新增四图原件及输出hash一致。24序号连续、身份和最终截图仅出现在关闭的剧透折叠中。浏览器检查1280px桌面与390px手机无横向溢出，搜索记录24可定位并展开、院史整卡可达、Enter可展开身份及主题。截图output/playwright/asylum-history-*-20261003.png。

本地预览服务已重启；编辑器只覆盖archive.json，本档案修改JSON后需重新构建。上传包已准备；GitHub未同步、未部署。恢复基线backups/asylum-history-before-20261003/。本轮未改TAS、WordPress主页、其他专题、既有游戏正文及样式。
