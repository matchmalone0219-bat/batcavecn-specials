"""Arkham icons: simple silhouettes, restrained shading and the official-manual bat contour."""

import re
from pathlib import Path
from xml.etree import ElementTree

ROOM_ICONS = {"": "dossiers", "riddler": "riddle", "clues": "district", "stories": "classified", "publications": "comics", "asylum-history": "asylum", "interviews": "patient", "rocksteady": "studio"}
LINK_ICONS = {"/arkham/detective/": "evidence", "/arkham/patients/": "patient", "/arkham/transmissions/": "radio", "/arkham/catalog/": "games", "/arkham/archive/": "dossiers"}

ICONS = {
    'games': 'M3 6h6l2 2h10v10l-3 3H3z M3 11h18 M14 15h4',  # 作品档案
    'dossiers': 'M7 3h11l2 2v13H7z M4 7v14h13 M10 8h7 M10 11h7 M10 14h4',  # 档案馆
    'voice': 'M4 10v4 M8 6v12 M12 3v18 M16 8v8 M20 10v4',  # 蝙蝠侠之声
    'collectibles': 'M12 2.5l8.5 4.75v9.5L12 21.5l-8.5-4.75v-9.5z M3.5 7.25L12 12l8.5-4.75 M12 12v9.5',  # 周边
    'gallery': 'M3 7V3h4 M17 3h4v4 M21 17v4h-4 M7 21H3v-4 M6 17l4-5 3 3 2-2 3 4 M15 8h1',  # 图片资料
    'search': 'M10.5 5a5.5 5.5 0 1 0 0 11a5.5 5.5 0 1 0 0-11z M14.5 14.5L21 21 M10.5 1.5v2 M10.5 17.5v2 M1.5 10.5h2 M10.5 9.5v2 M9.5 10.5h2',  # 搜索
    'sources': 'M5 3h10l4 4v11l-3 3H5z M15 3v4h4 M8 9h2.5v3H8z M13 9h2.5v3H13z M8 16h8',  # 资料来源
    'riddle': 'M4 3h16v15l-3 3H4z M9 9.5V7.5L10.5 6h3L15 7.5V10l-3 2.2V14 M12 16.5v1.5',  # 谜语人
    'evidence': 'M12 2v4 M12 18v4 M2 12h4 M18 12h4 M12 7a5 5 0 1 0 0 10a5 5 0 1 0 0-10z M12 11.5v1',  # 现场物证
    'patient': 'M3 5h18v14H3z M6 10a2 2 0 1 0 4 0a2 2 0 1 0-4 0 M5 16.5c.6-1.6 1.7-2.3 3-2.3s2.4.7 3 2.3 M14 9h4 M14 12h4 M14 15h2',  # 患者档案
    'tape': 'M2 6h20v12H2z M5 18l2-3h10l2 3 M6 10.5a1.75 1.75 0 1 0 3.5 0a1.75 1.75 0 1 0-3.5 0 M14.5 10.5a1.75 1.75 0 1 0 3.5 0a1.75 1.75 0 1 0-3.5 0 M9.5 10.5h5',  # 录音磁带
    'radio': 'M12 9v12 M8.5 21L12 9l3.5 12 M9.5 17h5 M11 6.5h2 M8 3.5a5 5 0 0 0 0 6 M16 3.5a5 5 0 0 1 0 6 M5 1.5a8.5 8.5 0 0 0 0 10 M19 1.5a8.5 8.5 0 0 1 0 10',  # 频段监听
    'comics': 'M12 6v15 M12 6L9 4H3v15h6l3 2 3-2h6V4h-6z',  # 漫画出版
    'asylum': 'M3 21h18 M5 21V10 M19 21V10 M3 10l9-6 9 6 M9 21v-6h6v6 M9 10h6',  # 院史
    'studio': 'M12 3l9 4.5-9 4.5-9-4.5z M3 12l9 4.5 9-4.5 M3 16.5l9 4.5 9-4.5',  # 创作变迁
    'district': 'M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z M9 3v15 M15 6v15',  # 辖区
    'date': 'M3 5h18v14l-2 2H3z M3 9h18 M8 3v4 M16 3v4 M7 13h2 M11 13h2 M15 13h2 M7 17h2',  # 日期
    'platform': 'M7 8h10l3 2 1 7-2 2-3-3H8l-3 3-2-2 1-7z M8 11v3 M6.5 12.5h3 M15 12h.01 M17 14h.01',  # 平台
    'maker': 'M3 3h9l9 9-9 9-9-9z M7.5 7.5h.01',  # 厂商
    'filter': 'M4 6h16 M4 12h16 M4 18h16 M8 4v4 M15 10v4 M10 16v4',  # 筛选
    'prev': 'M14 6l-6 6 6 6 M18 6v12',  # 上一部
    'next': 'M10 6l6 6-6 6 M6 6v12',  # 下一部
    'back': 'M10 5L4 11l6 6 M4 11h12l4 4v4',  # 返回
    'classified': 'M5 11h14v10H5z M8 11V7l2-3h4l2 3v4 M12 15v2',  # 机密
    'record': 'M4 4h16v16H4z M7 9l2 2 4-4 M15 9h2 M7 15l2 2 4-4 M15 15h2',  # 调查记录
    'spoiler': 'M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z M12 9.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5z M4 20L20 4',  # 剧透折叠
}


BATMARK = ElementTree.parse(Path(__file__).with_name('arkham-batmark.svg')).find('{http://www.w3.org/2000/svg}path').attrib['d']
PAINT = 'var(--icon-paint, url(#arkham-icon-metal))'
FILLED_ICONS = {
    'games': f'<path transform="translate(3 19.24) scale({58 / 675})" d="{BATMARK}"/>',
    'dossiers': '<path fill-rule="evenodd" d="M9 10h46v34H9z M13 14v26h38V14z"/><path d="M25 44h14v7h10v4H15v-4h10z M17 19h30v3H17z M17 26h30v3H17z M17 33h22v3H17z"/><path class="icon-shade" d="M9 40h46v4H9z M25 44h14v4H25z"/>',
    'patient': '<path d="M20 9C13 9 10 15 10 21v5l-3 5 4 2v6l5 3v5l-9 4v5h28v-6l-9-4V34c5-3 7-8 7-14 0-7-5-11-13-11z"/><path d="M40 17h17v3H40z M40 25h17v3H40z M40 33h17v3H40z M40 41h13v3H40z M40 49h13v3H40z"/><path class="icon-shade" d="m16 43 10-9v12l9 4v6H7v-5l9-4z"/>',
    'district': '<circle cx="32" cy="32" r="26" fill="none" stroke="var(--icon-paint, url(#arkham-icon-metal))" stroke-width="2.5"/><path d="m32 10 5 17 12-10-9 13 15 2-16 5 10 12-13-9-4 15-5-16-12 10 9-14-15-3 16-5-10-12 14 9z"/><path class="icon-shade" d="M32 10v22l5-5z M55 32H32l7 5z M32 55V32l-5 7z M9 32h23l-7-5z"/>',
    'riddle': '<path d="M17 21v-5l7-8h16l8 8v11L36 38v6H26V33l11-11v-4H28v4H17z M26 49h10v10H26z"/><path class="icon-shade" d="M26 39h10v5H26z M26 55h10v4H26z"/>',
    'evidence': '<g fill="none" stroke="var(--icon-paint, url(#arkham-icon-metal))" stroke-width="2.8"><path d="M5 22V7h16M43 7h16v15M59 42v15H43M21 57H5V42"/><path d="M15 41V29c0-22 34-22 34 0v14M21 46V29c0-15 22-15 22 0v18M27 48V30c0-7 10-7 10 0v21M32 33v22" stroke-linecap="round"/></g>',
    'radio': '<g fill="none" stroke="var(--icon-paint, url(#arkham-icon-metal))"><path d="m9 13 43-5 4 43-43 5z" stroke-width="2.5"/><path d="m16 38 31-14M31 17l4 29" stroke-width="2"/><circle cx="33" cy="31" r="8" stroke-width="2.5"/></g><circle cx="33" cy="31" r="2.5"/>',
    'tape': '<path fill-rule="evenodd" d="M7 12h50v39H7z M13 18v23h38V18z"/><path fill-rule="evenodd" d="M29 29a7 7 0 1 0-14 0 7 7 0 0 0 14 0z M25 29a3 3 0 1 1-6 0 3 3 0 0 1 6 0z M49 29a7 7 0 1 0-14 0 7 7 0 0 0 14 0z M45 29a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/><path d="M27 27h10v4H27z M18 45h28v3H18z"/><path class="icon-shade" d="M7 48h50v3H7z"/>',
    'voice': '<path d="M7 25h5v14H7z M18 16h5v32h-5z M29 7h6v50h-6z M41 20h5v24h-5z M52 27h5v10h-5z"/><path class="icon-shade" d="M18 40h5v8h-5z M29 45h6v12h-6z M41 37h5v7h-5z"/>',
    'collectibles': '<path d="m22 7 8 8h4l8-8v20l-5 8v5l13 7v5H14v-5l13-7v-5l-5-8z M11 55h42v5H11z"/><path class="icon-shade" d="M32 15h2l8-8v20l-5 8v5l13 7v5H32z M11 58h42v2H11z"/>',
    'gallery': '<path fill-rule="evenodd" d="M12 9h46v43H12z M17 14v33h36V14z"/><path d="M6 18h4v37h39v4H6z M20 40l9-13 8 9 5-6 9 13H20z"/><circle cx="43" cy="23" r="4"/><path class="icon-shade" d="M12 47h46v5H12z M37 36l5-6 9 13H37z"/>',
    'search': '<path fill-rule="evenodd" d="M45 26a19 19 0 1 0-38 0 19 19 0 0 0 38 0z M39 26a13 13 0 1 1-26 0 13 13 0 0 1 26 0z"/><path d="m38 39 5-5 16 17-8 8z M24 2h4v9h-4z M2 24h9v4H2z M24 41h4v9h-4z M41 24h9v4h-9z"/><path class="icon-shade" d="m38 39 4-1 13 17-4 4z"/>',
    'sources': '<path fill-rule="evenodd" d="M14 7h29l10 10v40H14z M20 25v4h26v-4z M20 35v4h26v-4z M20 45v4h18v-4z"/><path d="M7 15h4v45h35v4H7z"/><path class="icon-shade" d="M43 7v10h10z M14 53h39v4H14z"/>',
    'comics': '<path fill-rule="evenodd" d="M5 10h20l7 4 7-4h20v42H40l-8 5-8-5H5z M11 16v30h15l3 2V20l-6-4z M35 20v28l3-2h15V16H41z"/><path d="M15 23h9v3h-9z M15 32h9v3h-9z M40 23h9v3h-9z M40 32h9v3h-9z"/><path class="icon-shade" d="M32 14v43l8-5h19v-6H39l-4 2V20z"/>',
    'asylum': '<path d="m32 5 26 16v5H6v-5z M9 29h7v24H9z M48 29h7v24h-7z M5 55h54v5H5z"/><path fill-rule="evenodd" d="M19 29h26v24H19z M26 53V39a6 6 0 0 1 12 0v14z"/><path class="icon-shade" d="M32 5v21h26v-5z M48 29h7v24h-7z M5 58h54v2H5z"/>',
    'studio': '<path fill-rule="evenodd" d="M7 26h50v31H7z M26 32v18l16-9z"/><path d="m6 13 47-8 3 15-47 8z"/><path class="icon-shade" d="m14 12 7-1 9 14-7 1z M34 8l7-1 9 14-7 1z M7 52h50v5H7z"/>',
    'date': '<path fill-rule="evenodd" d="M7 13h50v44H7z M12 26v25h40V26z"/><path d="M16 5h5v15h-5z M43 5h5v15h-5z M17 32h7v6h-7z M29 32h7v6h-7z M41 32h7v6h-7z M17 42h7v6h-7z M29 42h7v6h-7z"/><path class="icon-shade" d="M7 51h50v6H7z"/>',
    'platform': '<path fill-rule="evenodd" d="M17 15h30l10 10 4 25-7 6-13-13H23L10 56l-7-6 4-25z M18 25v5h-5v5h5v5h5v-5h5v-5h-5v-5z M42 27a3 3 0 1 0 6 0 3 3 0 0 0-6 0z M49 35a3 3 0 1 0 6 0 3 3 0 0 0-6 0z"/><path class="icon-shade" d="M23 39h18l13 13 6-5 1 3-7 6-13-13H23L10 56l-7-6 1-3 6 5z"/>',
    'maker': '<path fill-rule="evenodd" d="M7 8h24l27 27-24 24L7 32z M16 16a4 4 0 1 0 8 0 4 4 0 0 0-8 0z"/><path class="icon-shade" d="m7 27 27 27 21-22 3 3-24 24L7 32z"/>',
    'filter': '<path d="M6 14h9v5H6z M27 14h31v5H27z M6 30h31v5H6z M49 30h9v5h-9z M6 46h14v5H6z M32 46h26v5H32z M17 9h8v15h-8z M39 25h8v15h-8z M22 41h8v15h-8z"/><path class="icon-shade" d="M17 19h8v5h-8z M39 35h8v5h-8z M22 51h8v5h-8z"/>',
    'prev': '<path d="M11 12h5v40h-5z M47 10v44L21 32z"/><path class="icon-shade" d="m21 32 26 14v8z"/>',
    'next': '<path d="M48 12h5v40h-5z M17 10l26 22-26 22z"/><path class="icon-shade" d="M17 46 43 32 17 54z"/>',
    'back': '<path d="M27 10v13h15c11 0 16 6 16 16v15h-8V39c0-5-3-8-8-8H27v13L5 27z"/><path class="icon-shade" d="M5 27h22v17z M50 47h8v7h-8z"/>',
    'classified': '<path fill-rule="evenodd" d="M18 25V17a14 14 0 0 1 28 0v8h8v34H10V25z M24 25h16V17a8 8 0 0 0-16 0z M29 38v12h6V38z"/><path class="icon-shade" d="M10 53h44v6H10z M40 17h6v8h-6z"/>',
    'record': '<path fill-rule="evenodd" d="M10 8h44v51H10z M17 20l5 5 10-11-4-3-6 7-2-2z M17 39l5 5 10-11-4-3-6 7-2-2z M36 18v4h11v-4z M36 37v4h11v-4z"/><path class="icon-shade" d="M10 53h44v6H10z"/>',
    'spoiler': '<path fill-rule="evenodd" d="M2 32s11-18 30-18 30 18 30 18-11 18-30 18S2 32 2 32z M8 32s9 12 24 12 24-12 24-12-9-12-24-12S8 32 8 32z M22 32a10 10 0 1 0 20 0 10 10 0 0 0-20 0z"/><path d="m8 55-4-4L56 7l4 4z"/>',
}


def definitions():
    """One pair of paints per page, shared by all inline icons and their selected states."""
    return '<svg class="arkham-icon-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs><linearGradient id="arkham-icon-metal" x2="0" y2="1"><stop stop-color="#edf3eb"/><stop offset=".55" stop-color="#c7d8d2"/><stop offset="1" stop-color="#8eabb2"/></linearGradient><linearGradient id="arkham-icon-metal-dark" x2="0" y2="1"><stop stop-color="#203b3b"/><stop offset="1" stop-color="#0c2022"/></linearGradient></defs></svg>'


def icon(name, size=None, cls="ai"):
    dimensions = f' width="{size}" height="{size}"' if size else ''
    if name in FILLED_ICONS:
        return f'<svg class="{cls}" data-arkham-shape="{name}" viewBox="0 0 64 64"{dimensions} aria-hidden="true" focusable="false"><g fill="{PAINT}" stroke="none">{FILLED_ICONS[name]}</g></svg>'
    return f'<svg class="{cls}" viewBox="0 0 24 24"{dimensions} aria-hidden="true" focusable="false"><path d="{ICONS[name]}" fill="none" stroke="{PAINT}"/></svg>'


TOKEN = re.compile(r'<i data-arkham-icon="([a-z-]+)"></i>')


def expand(html):
    """Replace explicit icon tokens written by the Arkham templates."""
    return TOKEN.sub(lambda match: icon(match.group(1)), html)


def token(name):
    return f'<i data-arkham-icon="{name}"></i>'


def shelf_icon(href):
    path = href.split("#")[0]
    for prefix, name in LINK_ICONS.items():
        if path == prefix:
            return token(name)
    if path.startswith("/arkham/archive/"):
        return token(ROOM_ICONS.get(path.strip("/").split("/")[-1], "dossiers"))
    return ""


def file_link(href, name, title, note, label=""):
    """One-line link to a related file: icon, optional label, title, short note."""
    tag = f'<span class="file-link-label">{label}</span>' if label else ''
    return f'<a class="file-link" href="{href}">{token(name)}{tag}<strong>{title}</strong><span class="file-link-note">{note}</span></a>'
