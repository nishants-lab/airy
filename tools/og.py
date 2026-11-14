"""Builds assets/og.png, the 1200x630 link preview image, from assets/hero.webp.

Usage, from the repository root or anywhere:  python tools/og.py
Needs Pillow (pip install pillow). Fonts are in tools/fonts (SIL Open Font License).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = 1200, 630

im = Image.new("RGB", (W, H))
gd = ImageDraw.Draw(im)
for y in range(H):
    t = y / H
    gd.line([(0, y), (W, y)], fill=(int(248 - 18 * t), int(250 - 12 * t), int(253 - 2 * t)))
d = ImageDraw.Draw(im)


def font(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght:
        f.set_variation_by_axes([wght])
    return f


serif = font("InstrumentSerif.ttf", 72)
sans = font("Figtree.ttf", 24, 650)
sans2 = font("Figtree.ttf", 21, 500)
ink, blue, grey = (28, 33, 48), (30, 84, 200), (92, 100, 118)

icon = Image.open(ROOT / "assets" / "icon-256.png").resize((52, 52), Image.LANCZOS)
im.paste(icon, (64, 58), icon)
d.text((128, 66), "Airy", font=font("Figtree.ttf", 32, 700), fill=ink)
d.text((64, 168), "A light, private", font=serif, fill=ink)
d.text((64, 244), "browser for Windows", font=serif, fill=blue)
d.text((64, 376), "8 busy tabs, after 60 s idle", font=sans2, fill=grey)
for i, (name, mb) in enumerate([("Chrome", 2043), ("Edge", 1460), ("Airy", 777)]):
    y = 414 + i * 44
    c = blue if name == "Airy" else ink
    d.text((64, y + 3), name, font=sans, fill=c)
    w = int(270 * mb / 2043)
    d.rounded_rectangle([160, y + 6, 160 + w, y + 32], 5, fill=blue if name == "Airy" else (190, 196, 208))
    d.text((172 + w, y + 3), f"{mb:,} MB", font=sans, fill=c)
d.text((64, 568), "Free for Windows 10 and 11", font=sans2, fill=grey)

shot = Image.open(ROOT / "assets" / "hero.webp").convert("RGB").crop((0, 0, 1000, 1030))
shot = shot.resize((600, 618), Image.LANCZOS)
x0, y0 = 668, 110
shadow = Image.new("RGBA", (shot.width + 80, shot.height + 80), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle([40, 52, 40 + shot.width, 52 + shot.height], 18, fill=(30, 50, 110, 90))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
im.paste(shadow, (x0 - 40, y0 - 40), shadow)
mask = Image.new("L", shot.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, shot.width, shot.height], 14, fill=255)
im.paste(shot, (x0, y0), mask)

out = ROOT / "assets" / "og.png"
im.save(out, optimize=True)
print("wrote", out.relative_to(ROOT), im.size)
