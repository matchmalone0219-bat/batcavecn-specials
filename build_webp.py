"""Create WebP copies of the JPEGs used on Protocol Arkham pages.

Run locally after `python3 build.py` (needs Pillow), then build again. The WebP
files sit beside their JPEG sources; build.py points Arkham pages at them. Data
files keep their JPEG paths, so other pages and media credits are unchanged.
"""
import html
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
JPEG = re.compile(r'/assets/((?:media/)?[^"\'\s)>&]+\.jpg)')
# Credited photographs and zoomable reference maps are shipped exactly as published.
KEEP_ORIGINAL = ('kevin-conroy-',)
KEEP_FOLDERS = ('maps',)


def source_of(reference):
    return ROOT / (reference[len('media/'):] if reference.startswith('media/') else reference)


def main():
    references = set()
    for page in (ROOT / 'dist/arkham').rglob('*.html'):
        references.update(JPEG.findall(html.unescape(page.read_text())))
    made = kept = 0
    for reference in sorted(references):
        source = source_of(reference)
        target = source.with_suffix('.webp')
        if source.name.startswith(KEEP_ORIGINAL) or source.parent.name in KEEP_FOLDERS or not source.is_file() or target.exists():
            continue
        with Image.open(source) as image:
            image.save(target, 'WEBP', quality=82, method=6)
        if target.stat().st_size > source.stat().st_size * 0.9:
            target.unlink()
            kept += 1
        else:
            made += 1
    print(f'Created {made} WebP files; kept {kept} JPEGs that WebP did not shrink')


if __name__ == '__main__':
    main()
