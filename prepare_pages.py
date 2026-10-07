"""Prepare a separate GitHub Pages artifact without changing local preview URLs."""
import argparse
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
LOCAL_URL = re.compile(r'(?<![\w:/])/(?:arkham|tas|people|assets|content|editor)(?=/)')


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs
                         if key in ('href', 'src', 'poster') and value)


def prepare(base_path):
    if base_path and not re.fullmatch(r'/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*', base_path):
        raise ValueError('Base path must be empty or a slash-prefixed project path')
    source, target = ROOT / 'dist', ROOT / 'pages-dist'
    if not (source / 'index.html').is_file():
        raise ValueError('Run build.py before preparing Pages')
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    for file in target.rglob('*'):
        if file.is_file() and file.suffix in ('.html', '.js', '.css', '.json'):
            text = file.read_text()
            text = LOCAL_URL.sub(lambda match: base_path + match.group(), text)
            text = text.replace('href="/"', f'href="{base_path}/"')
            file.write_text(text)
    (target / '.nojekyll').touch()
    links = 0
    for page in target.rglob('*.html'):
        parser = PageLinks()
        parser.feed(page.read_text())
        for url in parser.urls:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            if parsed.path.startswith('/'):
                assert parsed.path.startswith(base_path + '/'), (page, url)
                relative = unquote(parsed.path[len(base_path):]).lstrip('/')
                destination = target / relative
            else:
                destination = page.parent / unquote(parsed.path)
            if destination.is_dir():
                destination /= 'index.html'
            assert destination.is_file(), (page, url)
            links += 1
    index = json.loads((target / 'content/search.json').read_text())
    assert all(item['url'].startswith(base_path + '/') for item in index)
    for file in source.rglob('*'):
        if file.is_file() and file.suffix not in ('.html', '.js', '.css', '.json'):
            assert file.read_bytes() == (target / file.relative_to(source)).read_bytes()
    print(f'Pages ready: {len(list(target.rglob("*.html")))} pages, '
          f'{len(index)} search records, {links} links/assets; base={base_path or "/"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path', required=True)
    prepare(parser.parse_args().base_path.rstrip('/'))
