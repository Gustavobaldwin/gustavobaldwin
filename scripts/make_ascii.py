"""Turn source-photo.jpg into a green ASCII portrait.

Put a head-and-shoulders photo at the repo root as `source-photo.jpg`
(or .png) and run:  python scripts/make_ascii.py
Without a photo it draws a placeholder so the README never breaks.
"""
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from common import ROOT, BG, BORDER, DIM, BRIGHT, FONT, esc

COLS = 74
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE
# dark -> light (background is dark, so dense chars = bright pixels)
RAMP = " .:-=+*#%@"  # short ramp reads much cleaner than a 70-char one at this size
W, H = 400, 400
ROWS = int(COLS * (CHAR_W / LINE_H))


def find_photo():
    for name in ("source-photo.jpg", "source-photo.jpeg", "source-photo.png"):
        p = ROOT / name
        if p.exists():
            return p
    return None


def prep(img):
    """Square-crop, equalize the subject, black out the background.

    If the photo has transparency (background already removed), the alpha
    channel is used as the subject mask; otherwise the whole frame counts.
    """
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    img = img.crop((left, 0, left + s, s))  # square, anchored at the top (face)
    if img.mode in ("RGBA", "LA"):
        mask = img.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    else:
        mask = Image.new("L", img.size, 255)
    g = ImageOps.equalize(img.convert("L"), mask=mask)
    g = ImageEnhance.Contrast(g).enhance(1.2)
    g = g.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
    g = Image.composite(g, Image.new("L", g.size, 0), mask)
    g.save(ROOT / "source-prepped.png")
    return g


def to_rows(img):
    small = img.resize((COLS, ROWS), Image.LANCZOS)
    px = small.load()
    n = len(RAMP) - 1
    return ["".join(RAMP[int(px[x, y] / 255 * n)] for x in range(COLS)) for y in range(ROWS)]


def placeholder_rows():
    msg = [""] * 14 + [
        "        [ no source-photo.jpg found ]",
        "",
        "        drop a head-and-shoulders photo",
        "        at the repo root and run:",
        "",
        "        $ python scripts/make_ascii.py",
    ]
    return msg + [""] * (ROWS - len(msg))


def render(rows, stretch=True):
    grid_w = COLS * CHAR_W
    grid_h = len(rows) * LINE_H
    ox = (W - grid_w) / 2
    oy = 34 + (H - 34 - grid_h) / 2
    lines = []
    for i, r in enumerate(rows):
        color = BRIGHT if i < len(rows) * 0.8 else DIM  # CRT fall-off at the bottom
        lines.append(
            f'<text x="{ox:.1f}" y="{oy + (i + 1) * LINE_H:.1f}" fill="{color}" '
            + (f'textLength="{grid_w:.1f}" lengthAdjust="spacingAndGlyphs" ' if stretch else "")
            + f'xml:space="preserve">{esc(r.ljust(COLS) if stretch else r)}</text>')
    body = "\n    ".join(lines)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <text x="16" y="22" fill="{DIM}" font-family="{FONT}" font-size="11">~/portrait.txt</text>
  <line x1="0" y1="32" x2="{W}" y2="32" stroke="{BORDER}"/>
  <g font-family="{FONT}" font-size="{FONT_SIZE}">
    {body}
  </g>
</svg>
'''


if __name__ == "__main__":
    photo = find_photo()
    if photo:
        svg = render(to_rows(prep(Image.open(photo))))
    else:
        svg = render(placeholder_rows(), stretch=False)
    (ROOT / "ascii-portrait.svg").write_text(svg, encoding="utf-8")
    print("ascii-portrait.svg written", "(from photo)" if photo else "(placeholder)")
