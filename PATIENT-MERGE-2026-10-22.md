# 患者板块合并 · 2026-10-22

“患者临床录音”与“患者终端”使用同一份patient-interviews.json，原来各渲染七名患者、35段录音、人物导读与字幕，确属重复。现统一保留`/arkham/patients/`患者终端。

## 结果

- 档案馆总览和侧栏移除“患者临床录音”，只保留互动区的“患者终端”。
- 移除终端中返回重复“人物阅读档案”的链接。
- 七名患者的身份、聆听问题、导读、35段录音、中文字幕、折叠边界及收听记录均保留，患者原始数据与音频文件未改。
- 旧`/arkham/archive/interviews/`转向患者终端；旧`#joker`、`#harley`等七名患者书签映射为`#patient-joker`、`#patient-harley`等，兼容GitHub Pages项目路径。
- 搜索移除旧页面和七名患者的8条重复结果；原来的英文姓名和访谈关键词合并到终端结果中。
- 生成规模160页（含旧址跳转页）、493条搜索记录；本轮9个页面变化。TAS、共同档案及两站来源页保持原样。

## 修改文件

| 文件 | 修改 |
| --- | --- |
| `arkham_pages.py` | 移除重复栏目与播放器，旧页面改为兼容跳转，移除重复搜索记录。 |
| `arkham_interactions.py` | 移除回链，合并患者英文名和访谈关键词至唯一搜索结果。 |
| `verify.py` | 检查唯一入口、旧地址兼容、导读与播放器完整性、关键词合并和目录数量。 |
| `verify-build.py` | 将去重后的搜索记录数更新为493。 |

日常源目录：`/Users/dinghaowei/Downloads/batcavecn/specials`。发布仓库副本：`/Users/dinghaowei/Downloads/batcavecn/specials/output/github-release-20261022/repository`。4个文件已逐字节同步；未提交、未推送。

## 验证

- 全量内容检查通过：160页、493条搜索记录、5730个内部链接及锚点，音频和字幕数据及剧透边界通过。
- 构建回归4项、患者播放／字幕／波形／暂停与切换的现有交互回归通过。
- Pages项目路径检查通过：7385项链接与资源引用。
- 浏览器检查16种旧地址／书签（本地路径与Pages项目路径各8种），全部跳到正确患者。
- 档案馆、档案页、患者终端在1440／390px共6次视图检查：无横向溢出，无重复标签或旧阅读页回链。
- 七名患者均实际播放第一段录音并切换至第二段；没有脚本异常。
- 中文患者搜索显示8个唯一结果（终端总入口＋七名患者）；英文Patient Interviews检索为七名患者，各只指向患者终端。
- 去重之外的486条搜索结果保持不变；7条终端人物结果仅合并英文名和检索标签。两站来源页及TAS页面逐字节未变。
- `git diff --check`通过。

## 证据

- `patient-merge-content-checks.json`：9个变化页面、8条移除结果及7条关键词合并记录。
- `patient-merge-browser-checks.json`：旧地址跳转、桌面手机检查、播放状态及中英文检索结果。
- `patient-terminal-1440.png`、`patient-terminal-390.png`：合并后的终端截图。
- `正文文案清理.patch`：包含此前文案清理和本次合并的累计差异。
- 本轮修改前备份：`/Users/dinghaowei/Documents/Codex/2026-10-22/referenced-chatgpt-conversation-this-is-an/work/patient-merge/before`。

前面的160页／501条记录描述此前本地状态；线上仍是原发布版本，本次493条记录的合并结果尚未发布。

完整检查证据：`/Users/dinghaowei/Documents/Codex/2026-10-22/referenced-chatgpt-conversation-this-is-an/outputs`。
