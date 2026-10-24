"""Original Protocol Arkham line icons: 24px grid, 1.5 stroke, square caps, chamfer / bracket / tick motifs."""

import re

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


def icon(name, size=None, cls="ai"):
    dimensions = f' width="{size}" height="{size}"' if size else ''
    return f'<svg class="{cls}" viewBox="0 0 24 24"{dimensions} aria-hidden="true" focusable="false"><path d="{ICONS[name]}"/></svg>'


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
