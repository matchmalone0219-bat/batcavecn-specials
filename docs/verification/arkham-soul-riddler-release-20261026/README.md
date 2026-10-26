# 发布验证证据

部署与正式站确认于2026-10-27完成，发布内容提交为06df259；后续8de0f58继续补齐题库并保留本批交互。完整说明见根目录`ARKHAM-SOUL-RIDDLER-RELEASE-2026-10-27.md`。

- `workflow.json`、`pages.txt`：独立06df259候选的26条工作流命令与项目子路径打包。
- `riddler-browser-results.json`、`soul-browser-results.json`：实际候选278＋64项通过。谜语人沿用`../riddler-swap-20261026/browser-check.js`，仅把预览端口改为8897；播放器执行脚本另存`soul-browser.js`，隐藏检查使用visibilitychange事件。
- `github-runs.json`、`jobs-0.json`、`jobs-1.json`：06df259与后续8de0f58的build、deploy成功记录。
- `online-assets.json`：10项正式站关键文件与Pages产物的哈希一致性。
- `online-check.js`、`online-browser-results.json`：正式站32项实际操作检查；录音进入1.5秒起的字幕时段后核对中文文字。
- `release.json`：提交、计数、验证范围、当前线上版本与并行修改隔离说明。

没有把临时录屏原文件、登录凭据、浏览器会话或整个本地输出目录加入发布。本目录名称沿用开始发布检查的日期。
