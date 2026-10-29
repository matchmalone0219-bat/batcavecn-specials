# 《之城》哥谭故事界面配图 · 2026-10-28

状态：本地接入完成；未提交、推送或部署。

## 范围与呈现

- 现有14组《阿卡姆之城》故事新增21张WebP。10组单篇各1张；戈登与夏普、疯帽匠、急冻人各2张，科波特家族5张。
- 单篇图置于既有梗概后；多篇图放在对应分篇梗概下，按原有分篇顺序排列。所有新图位于默认收起的剧透折叠内，图库中对应图片亦折叠。
- 完整保留游戏标题、英文正文、配图与画幅。源视频为1152×720、30fps、1:1像素，显示比例8:5；成图保持1152×720，没有为统一到16:9而拉伸、裁切或放大。
- 21张成图合计2,230,644字节，全部已解码并目视检查。
- 本批只更新City截图、来源与核验字段；既有中文标题、导读、梗概、解读、扫描题互链、Knight记录及图片保持。
- 28组故事现在均有已检查的游戏故事界面截图；`originalText`仍为null，梗概没有变成全文转录。

## 来源与证据

本地文件：`/Users/dinghaowei/Downloads/Gemini/Arkham_City_Stories_Zevik.mp4`。H.264／AAC，312.726349秒，78,075,812字节。前一轮完成全片音画解码，无错误；逐项读取14组／21篇界面，完整时间点及原帧哈希保留。

来源链接沿用[Zevik：ALL Arkham City Stories (HD demonstration)](https://www.youtube.com/watch?v=V8rJSfDh0A4)。署名依据本地文件名及前轮候选记录；没有另外读取下载工具原始元数据，也没有把文件名当成开放转载授权。玩家录制与英文界面的来源类型保留。

[本批逐项记录](docs/research/city-story-captures-20261028.json)包含视频哈希、21张成图哈希、原帧哈希、逐篇时间点及导出参数。[前轮素材检查记录](docs/research/city-story-video-review-20261028.json)按其当时状态保留。

## 逐项时间点

| 英文原题 | 各篇时间点 |
| --- | --- |
| Arkham Island Sold | 00:21 |
| Arkham City Medical Team | 00:27 |
| Seismic Disturbances | 00:37 |
| Compulsory Purchase | 00:41 |
| Studying the Bat | 00:47 |
| A New Robin | 03:53 |
| The Ratcatcher | 03:48 |
| Brokering Deals | 04:15 |
| Election Time | 03:43 |
| Gordon vs. Sharp | 02:04 / 02:10 |
| The Mad Hatter | 02:34 / 02:38 |
| Illegal Operations | 03:06 |
| A Cold Start | 02:56 / 03:01 |
| The Cobblepot Feud | 03:10 / 03:14 / 03:19 / 03:24 / 03:30 |

## 实现与同步

- 数据：`arkham-archive-research.json`；素材：`story-captures/city-*.webp`。
- `arkham_reading.py`沿用现有图片函数，将多篇图片放入对应`story-part`，并正确拼接YouTube已有查询参数后的`&t=`；原B站录像的`?t=`保持有效。
- `verify-story-captures.py`扩展为两作28组、35张成图、63个页面／分篇时间点；检查源文件与成图哈希、City分篇归属、原比例、搜索与故事页／图库折叠。
- 发布Git目录为基线，日常目录逐处合入本批字段与代码段。两份原有案件、演示、院史、导航等差异保留；未整包覆盖。
- 两处备份分别位于`backups/city-story-captures-before-20261028/`，包含4个修改前文件及SHA-256清单。

## 验证

- 两份代码：`verify.py`、`verify-story-captures.py`、`verify-riddler.py`通过。
- 发布目录：`verify-build.py`的4项检查、`verify-clues.js`、`verify-arkham-nav.js`及`git diff --check`通过。
- Pages子路径构建通过：158页、818条搜索记录、10170项链接／资源。
- 发布目录本地159页、818条搜索记录；日常目录161页、851条搜索记录；两份搜索记录数量各自保持。
- 浏览器1280×900及390×900共192项检查通过：21张City图逐张解码、原始8:5比例与分篇归属、35张图默认隐藏、Knight既有截图保留、故事与扫描题往返、来源时间参数、图库折叠；无横向溢出及脚本／console错误。
- 浏览器检查结果见`docs/verification/city-story-captures-20261028/`，页面检查图见`output/playwright/city-story-captures-20261028/`。
- 本地预览：`http://127.0.0.1:8901/arkham/archive/stories/#city-cobblepot-feud`，服务仅监听本机。

## 后续边界

新下载的《骑士》Zevik英文录像尚未用于替换当前汉化界面配图或逐字校勘。该项与本批City接入分别处理；本批没有新增全文翻译或上线发布。
