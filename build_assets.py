"""Copy only assets whose bytes differ; source timestamps are not trusted."""
import re
import shutil

ARKHAM_JPEG = re.compile(r'/assets/((?:media/)?[^"\'\s)>&]+)\.jpg')


def copy_asset(source, destination):
    if destination.is_file() and source.stat().st_size == destination.stat().st_size:
        with source.open("rb") as original, destination.open("rb") as copied:
            while True:
                chunk = original.read(1024 * 1024)
                if chunk != copied.read(1024 * 1024):
                    break
                if not chunk:
                    return False
    shutil.copyfile(source, destination)
    return True


def prefer_webp(pages, root, dist):
    """Point Protocol Arkham pages at the WebP copies made by build_webp.py."""
    shipped = {}

    def swap(match):
        reference = match.group(1)
        source = root / f"{reference.removeprefix('media/')}.webp"
        if reference.startswith('media/maps/') or not source.is_file():
            return match.group(0)
        shipped[source] = dist / 'assets' / f'{reference}.webp'
        return f'/assets/{reference}.webp'

    for name, body in pages.items():
        if name.startswith('arkham/'):
            pages[name] = ARKHAM_JPEG.sub(swap, body)
    return shipped
