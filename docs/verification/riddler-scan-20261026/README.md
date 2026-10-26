# 谜语人点击扫描本地验收 · 2026-10-26

- 26条当前Pages工作流验证命令通过，见`workflow.json`；另通过`/batcavecn-specials`发布子路径打包，见`pages.txt`。构建160页、832条搜索记录，Pages公开159页。
- 主浏览器检查193项通过，见`browser-check.js`与`browser-results.json`。覆盖320／390／1280／1440宽度、三作分析动画、默认折叠、重复点击、谜底／漫画独立折叠、静音零请求、三段原声音频真实解码、Enter、切换作品、手机返回、减少动态、无脚本、禁止存储与无脚本错误。
- 补充检查20项通过，见`edge-check.js`与`edge-results.json`。覆盖空格键、声音请求失败、区域切换取消、现场图失败后仍可阅读与收起、三作发布子路径的原图／实际音频解码／揭示，以及SVG遮罩路径。
- 页面隐藏检查通过发送hidden状态的visibilitychange事件验证清理逻辑；pagehide单独验证。浏览器工具的切换标签不会改变其无头环境的页面可见性，未将此项表述为真实设备后台测试。
- 图片位于`output/playwright/riddler-scan-{asylum,city,knight}-{320,390,1280,1440}-{active,revealed}.png`。长详情元素截图可能受滚动容器裁剪，视觉复查以另存的`*-viewport-{idle,solved}.png`及现场图active截图为准；已查看疯人院1440、之城390、骑士320视口，以及三作分析帧，未见横向溢出。

## 范围与来源

`verify-riddler-scan.py`校验当前137道物件／人物题的现场钩子、漫画默认折叠、三项声音哈希与原片时间边界、专用资源仅在谜语人页加载，以及蝙蝠遮罩字节。17道透视技巧的播放方式不在本批改动范围。

实施前文件备份位于`output/riddler-scan-before-20261026/sources.tar.gz`。相对该基线，`arkham_pages.py`仅新增谜语人资源引入；`app.js`仅在谜语人函数加入销毁／挂载／返回事件。详情滚动复位、隐藏空技巧区和骑士题库／身份漫画改动来自并行任务，已保留。

`scope.json`保存整个共享工作区的产物哈希对比，不把其他并行工作或既有产物与源码差异归为扫描增强。基线798条搜索记录逐条保持，新增34条来自骑士题库；扫描效果未把答案写入搜索。原图、声音原片、患者与监听源码未因本批增强改写。

取材时间、版本和声音处理见`../../research/riddler-scan-feedback-20261026.md`及根目录`riddler-scan-feedback.json`。当前修改位于发布Git仓库，未整包同步日常目录，也未提交、推送或发布。

本机预览：`http://127.0.0.1:8895/arkham/archive/riddler/`。
