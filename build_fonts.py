"""Ship Source Han Sans cut down to the characters the built pages actually use."""
import io

from build_assets import copy_asset

FONTS = ("SourceHanSansCN-ExtraLight.woff2", "SourceHanSansCN-Regular.woff2")
# Printable ASCII, typographic punctuation and full-width forms stay available for typed searches.
BASE = "".join(map(chr, range(0x20, 0x7F))) + "“”‘’—–…·•×→←↗↓↑№" + "".join(map(chr, range(0x3000, 0x3040))) + "".join(map(chr, range(0xFF01, 0xFF5F)))


def used_text(dist):
    text = set(BASE)
    for pattern in ("**/*.html", "content/*.json", "assets/*.js"):
        for path in dist.glob(pattern):
            text.update(path.read_text(errors="ignore"))
    return "".join(sorted(ch for ch in text if ch.isprintable()))


def ship_fonts(root, dist):
    target = dist / "assets/fonts"
    target.mkdir(parents=True, exist_ok=True)
    copy_asset(root / "fonts/LICENSE.txt", target / "LICENSE.txt")
    try:
        from fontTools import subset
    except ImportError:
        for filename in FONTS:
            copy_asset(root / "fonts" / filename, target / filename)
        print("Fonts copied in full (install fonttools and brotli to subset them)")
        return
    text = used_text(dist)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    for filename in FONTS:
        font = subset.load_font(root / "fonts" / filename, options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=text)
        subsetter.subset(font)
        buffer = io.BytesIO()
        subset.save_font(font, buffer, options)
        font.close()
        # Unchanged text leaves the shipped file untouched, like every other asset.
        destination = target / filename
        if not destination.is_file() or destination.read_bytes() != buffer.getvalue():
            destination.write_bytes(buffer.getvalue())
    print(f"Fonts subset to {len(text)} characters")
