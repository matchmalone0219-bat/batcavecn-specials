# 阿卡姆站审核修正（2026-10-25，本地，未推送）

依据外部审核报告的核查结果，只改 Protocol Arkham 页面与发布流程。备份：`backups/audit-fixes-before-20261025/`。

## 改动
1. **主菜单转场丢样式**（线上已复现）：`arkham-nav.js` 只替换 body，经主菜单进入康罗伊页、图片页时缺 `conroy-profile.css` / `artbook.css`。现在转场前先加载新页面的样式表，切换后移除不再需要的；目标页需要额外脚本或样式表加载失败时，改走普通跳转。`verify-arkham-nav.js` 增加三项检查。
2. **对比度**：`arkham-investigation.css` 的 `.tape-deck-serial`、`.dept-badge` 改为 `#849193`（≥5.5:1）；`conroy-profile.css` 末尾增加仅限 `.arkham` 的两条规则（声音对照小标签 `#6e5a40` 4.86:1，目录编号不透明度 0.85）。磁带机上其余暗色小字位于 `aria-hidden` 装饰硬件内，保持原样。
3. **WebP**：`build_webp.py`（本地运行，需要 Pillow）为阿卡姆页用到的 jpg 生成同名 webp，共 124 个，约 19 MB，原 jpg 合计约 41 MB。`build_assets.prefer_webp()` 只改写 `arkham/` 页面里的引用；数据文件、TAS、共享首页仍用 jpg。康罗伊署名照片和 `maps/` 参考地图保留原图。新增阿卡姆图片后：先 `build.py`，再 `build_webp.py`，再 `build.py`。
4. **开场视频**：新增 `arkham-city-intro-720.mp4`（8.7 MB，原 1080p 为 19 MB），宽度 ≤760px 时优先使用。
5. **编辑器不发布**：`prepare_pages.py` 不再输出 `/editor/` 和隐藏的“编辑文案”链接，本地 `serve.py` 不受影响。
6. **清理**：删除 `arkham.css` 中无页面使用的规则（start-title、patient-register、dossier-nav、clue-case、catalog-art-sources 等），文件从 58.5 KB 降到 54.6 KB；开场 h1 的英文副标题设为 `aria-hidden`。
7. `verify.py` 的目录页配图检查改为接受 webp 副本。

## 检查
CI 全部 14 步与其余 verify 脚本均通过；`prepare_pages.py` 通过。本地预览实测：两条转场都加载了对应样式，webp 与 720p 视频可正常访问，`/editor/` 返回 404，两页的可读文字对比度都 ≥4.5:1。

## 推送时注意
需要一并提交新文件：124 个 `.webp`、`arkham-city-intro-720.mp4`、`build_webp.py`。
