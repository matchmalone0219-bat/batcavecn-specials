# TAS 字体

- 字体：Adobe Source Han Sans CN ExtraLight（思源黑体简体中文区域子集，Version 2.005）。字体自身的 OS/2 字重为250，网页按250声明，未使用浏览器模拟细体。
- 原始字体：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-ExtraLight.otf
- 官方项目：https://github.com/adobe-fonts/source-han-sans
- 许可原文：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/master/LICENSE.txt；本目录保留完整 LICENSE.txt。
- 获取日期：2026-10-02。通过FontTools将官方OTF转换为WOFF2，保留原有字形和字符覆盖，没有按当前标题删减汉字。后续修改中文文案无需重新生成字体。
- 网页文件：SourceHanSansCN-ExtraLight.woff2，5,262,276字节；SHA256：349a4515add48c4171abbe48279f5b50d4aed1adb6425fedee17c09ac333e80c。
- 生成网站时复制字体与许可到 `/assets/fonts/`。字体仅由 `.tas` 页面使用，设置font-display:swap；阿卡姆和共同人物档案保持原字体。
- 转换工具只在本地临时目录使用，构建与预览不需要FontTools或Brotli依赖。原始OTF保存在忽略的backups/tas-home-before-font-20261002/中。
