# Protocol Arkham互动档案 · 2026-10-06

## 入口与范围

- /arkham/patients/：患者终端；档案馆及原患者访谈阅读页提供入口。
- /arkham/transmissions/：频段监听（Cryptographic Sequencer）；密码破译器调谐终端，收录小丑《阿卡姆之城》电话留言与片尾绝唱《Only You》。
- 七项主菜单保持，档案馆说明提示互动内容。TAS、新蝙、原作品资料不改。

## 患者终端

复用patient-interviews.json七组人物资料。左侧人物选择，右侧身份与聆听导读；手机为上下布局。大字母为姓名缩写的终端索引图形，RECORD INDEX为页面索引。录音与字幕默认收在剧透折叠中。

用户提供七个B站录制MP4，按画面的五个录音槽位切为每人五段，共35段M4A／34.20MB。原AAC音轨直拷贝，不重编码或改变音量。359条中文字幕来自原视频画面，校正识别错字、漏句、行序与明显错字；每段有独立字幕时间轴。切点、来源与验证口径见[PATIENT-AUDIO.md](PATIENT-AUDIO.md)。B站录制者署名与原页链接保留，YouTube只作为其他录制入口。

患者终端与原访谈阅读页通过patient_player.py共用五段选择、原生audio控制与中文字幕：初始无src、preload=none；点击播放／TAPE才加载选中段。页面同一时刻仅一个音源保留src；切段、换人／播放另一条时释放旧音源，折叠／隐藏暂停，离页清理。字幕根据currentTime匹配，seeked后立即更新。

Web Audio读取当前录音的实际时域采样绘制波形。显示增益最多24倍，只影响画线；无随机数据，不改变音量。磁带轮和波形跟随playing，缓冲／暂停／结束／错误停止；减少动态关闭连续动画，原生音频与字幕仍可用。失败可重试或访问原出处；无脚本时有每段音频直达链接。两页不再请求YouTube嵌入／API。

## 文件与验证

arkham_interactions.py生成患者终端与频段监听，复用既有患者、通信与来源数据；arkham-investigation.js管理单播放器、字幕及波形，同名CSS供两张录音终端使用。site_pages.py接入路由与索引，build.py复制录音终端资产。

python3 verify.py核对59页／487记录／1703内部链接、来源／图片关联、七组折叠、35段文件哈希与连续切点、字幕边界／顺序、搜索无字幕剧情正文；verify-build.py四项构建／编辑器检查通过。node verify-investigation.js覆盖终端／阅读页按需加载、五段选择、拖动字幕、实际采样绘图、音频图复用、单音源、旧事件、折叠／缓冲／隐藏、错误重试和离页清理。原开场／菜单／转场检查保留。

恢复backups/patient-audio-before-20261007/；初版互动截图output/arkham-interactions-20261006/；全轨提取检查output/patient-audio-20261007/；切点／字幕／35段试播与手机截图output/patient-segments-20261007/。已逐段试播并检查字幕和声音状态，未逐句人工听完全部音频。2026-10-06首版YouTube嵌入限制已由本站音频替代；GitHub最新提交以外层专题交接卡末节为准。
