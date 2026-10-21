# TAS 字体

- 字体：Adobe Source Han Sans CN ExtraLight（思源黑体简体中文区域子集，Version 2.005）。字体自身的 OS/2 字重为250，网页按250声明，未使用浏览器模拟细体。
- 原始字体：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-ExtraLight.otf
- 官方项目：https://github.com/adobe-fonts/source-han-sans
- 许可原文：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/master/LICENSE.txt；本目录保留完整 LICENSE.txt。
- 获取日期：2026-10-02。通过FontTools将官方OTF转换为WOFF2，保留原有字形和字符覆盖，没有按当前标题删减汉字。后续修改中文文案无需重新生成字体。
- 网页文件：SourceHanSansCN-ExtraLight.woff2，5,262,276字节；SHA256：349a4515add48c4171abbe48279f5b50d4aed1adb6425fedee17c09ac333e80c。
- 生成网站时复制字体与许可到 `/assets/fonts/`。字体仅由 `.tas` 页面使用，设置font-display:swap；阿卡姆和共同人物档案保持原字体。
- 转换工具只在本地临时目录使用，构建与预览不需要FontTools或Brotli依赖。原始OTF保存在忽略的backups/tas-home-before-font-20261002/中。

## 2026-10-10 阅读字重

- 常规正文、导航与辅助信息使用 Adobe Source Han Sans CN Regular（真实字重400）；展示标题继续使用 ExtraLight250。
- 官方原始文件：https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-Regular.otf
- 获取日期：2026-10-10，使用临时 FontTools 环境转换，保留全部原始字符覆盖。构建不需要字体转换依赖。
- 网页文件：SourceHanSansCN-Regular.woff2，6199972字节；SHA256：f15ec1f3555fc73598e50183864139591dba2d4edd286badb4f64b0a94409e5b。
- 两个字重均使用原有 SIL Open Font License，本目录 LICENSE.txt 保持。Regular 与许可随构建复制到 /assets/fonts/。
