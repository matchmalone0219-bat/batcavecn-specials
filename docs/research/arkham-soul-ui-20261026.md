# 阿卡姆之魂原作菜单取材 · 2026-10-26

## 取材与实现

用户最终要求采用《疯人院》的原作档案菜单样式：黑白漫画纸页、错位叠放边框、六列甲虫录音图标、琥珀黄色选中状态与下方中文字幕。实景石碑照片与实体播放器外壳方案均未采用。

用户录屏：`/Users/dinghaowei/Downloads/batcavecn/阿卡姆疯人院 病人访谈记录.mp4`。本轮直接查看8秒、60秒和200秒的界面帧，确认菜单布局、选中状态和字幕位置；没有据此宣称完整连续观看整段录屏。源视频哈希沿用`audio-subtitles-20261025.json`的记录。

- `asylum-history-scarab.png`：8秒，裁取`x=1068,y=305,width=82,height=80`。原86像素高的候选带入下一排图标白边，按用户反馈收窄下缘6像素。没有重画或生成图标。
- `asylum-history-player-art.webp`：Faxagate攻略的`main.webp`，838×472，原图即石碑与人影。页面保留用户最后选择的纸页取景。来源为 https://www.faxagate.com/en/gaming/batman-arkham-asylum-spirit-of-arkham ，图片为 https://www.faxagate.com/resources/-/gaming/batman-arkham-asylum-spirit-of-arkham/main.webp 。
- `asylum-history-player-portrait.webp`：用户录屏8秒，裁取完整人物与石碑所在纸页区域`x=285,y=125,width=660,height=820`，排除其他档案栏和底部操作提示。人物与石碑完整，页面以contain展示，无放大取景。
- 上述三项媒体哈希与出处保存在`asylum-history.json`的`playerImage`、`playerFinalImage`和`playerIcon`；原有录音、字幕、来源与图库图片字段未改。

## 最终揭示规则

按用户最新指示：默认用石碑与人影图，实际播放第24条时切换完整人物图。仅选择第24条不切图；暂停后保留人物图；选择前23条或收起最终留言后恢复人影图。未采用遮盖层，也没有等待第24条播完才揭示的逻辑。图像切换与最终署名文字、现场剧透折叠分别维护。

原图与图标为游戏原作素材，版权归DC / Warner Bros. / Rocksteady；玩家录屏与攻略截图不表述为开放授权素材。新增资产不进入共同图库，避免自动展示人物身份图。
