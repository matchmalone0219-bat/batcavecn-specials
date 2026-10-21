# GitHub Pages 预览部署

2026-10-07：已同步用户在 GitHub 提交的整体文案（1483ca2）。本次发布范围为现有两个专题；声音档案新栏目仍处于计划阶段。

## 部署方式

使用 `.github/workflows/pages.yml` 构建与发布。验证通过后生成独立 `pages-dist/`，由 GitHub Pages 托管；本地 `dist/` 与预览网址保持不变。仓库 Settings → Pages → Source 需选择 GitHub Actions。

`prepare_pages.py` 仅在发布产物中加入 Pages 项目路径，涵盖 HTML、CSS、脚本、搜索结果及内嵌播放数据；保留媒体字节、站外链接与 `noindex,nofollow`。Pages 只上传生成站点，不上传源码目录、备份或本地录音视频。本地编辑器依然只在本机可用。

```sh
python3 verify.py
python3 verify-build.py
node verify-intro.js
node verify-arkham-nav.js
node verify-arkham-menu.js
node verify-investigation.js
python3 prepare_pages.py --base-path /batcavecn-specials
```

默认项目地址预期为 `https://matchmalone0219-bat.github.io/batcavecn-specials/`；实际发布成功后以 Pages 返回的网址为准。没有更改正式域名或主站。

## 发布设置

2026-10-07：用户明确授权公开 `matchmalone0219-bat/batcavecn-specials` 并部署。仓库现已公开，Pages 来源已保存为 GitHub Actions，默认域名强制 HTTPS。公开范围包含源码、素材和提交历史；网页发布产物由工作流单独生成。

后续推送 `main` 会自动检查、构建与发布；也可在 Actions 手动运行 Publish special archives。没有创建收费订阅或更改正式域名。

## 文案阅读记录

保留用户原稿和译名，未自动重写文案。结构、文件哈希和链接检查不代表逐条剧情核验。

### 已处理（2026-10-21，`29d1ac1` 上线）

- 《梦境之间》《双面人·下篇》《罗宾的清算·下篇》的主题／人物段，《之城》创作与年度版段，《骑士》声音与DLC段：均以 `containsSpoilers` 收入剧透折叠，线上复查折叠外无结局句。

### 待用户决定的文案（2026-10-21 线上审核记录，未修改）

| 位置 | 原文 | 问题 | 建议方向 |
| --- | --- | --- | --- |
| `/tas/` 本期放映导言 | 冰霜里为亡妻哭泣的急冻人 | 《Heart of Ice》中诺拉被视为已逝（DC回顾亦写“夺走诺拉生命”），后续《Deep Freeze》与《SubZero》才让她复苏；作为整套动画概述略有偏差，但不算错误 | 可保留；若想涵盖后续剧情，可改为“为冰封的诺拉哭泣” |
| `/tas/episodes/almost-got-im/` 主题与叙事 | 被公认为整部剧集最精妙耐看的一集 | 把主观评价写成外部共识，且无对应来源 | 删去“被公认为”，或改为本站视角的直接评价 |
| `/arkham/games/arkham-asylum/` 故事创作段 | 最顶级的宿命张力 | 评价性大词；“宿命”与 The Batman 文案禁用词同类 | 改为具体描述两位演员的对手戏 |
| `/tas/` 声音专栏 | 定义了整整两代人心中唯一的蝙蝠侠 | “唯一”为强评价 | 可保留；或改为“许多观众心中的蝙蝠侠之声” |
| `/arkham/games/arkham-knight/` DLC段（折叠内） | 为整场十年传奇留下……终章 | 三部曲 2009—2015，约六年 | 改为“为 Rocksteady 三部曲留下终章” |

其余分集中“唯一的希望之光／唯一恒定的温暖港湾”等属人物描写，非外部共识表述，可保留。
