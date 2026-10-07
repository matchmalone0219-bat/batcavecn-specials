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

保留用户原稿和译名，本轮未自动重写文案。结构、文件哈希和链接检查不代表逐条剧情核验。

- TAS 首页导言的“亡妻”不适合用作整套动画连续性的概述；建议改为“为诺拉挣扎”一类表述。
- 《梦境之间》的主题段写出识破梦境和跃下钟楼，《双面人》下篇及《罗宾的清算》下篇写出破局方式；目前这些段落在剧透折叠之外。
- 《之城》创作与版本段、《骑士》声音段包含小丑结局，亦在普通正文中；应在后续修订中回到剧透折叠区。
- “唯一”“最顶级”“被公认为”等属于较强的评价性用语，可由用户决定保留；不把主观评价包装成外部共识。
