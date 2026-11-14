"""Screenshots index.html at desktop and phone width with headless Edge, to check the layout.

Usage:  python tools/preview.py [output folder]
The default output folder is airy-site-preview in the system temp folder. Writes:
  desk.png     full page at 1440 px wide, plus top.png and tail.png crops
  phone.png    full page at 390 px wide, plus phone-sheet.png (the page cut into 6 columns)
Needs Pillow and Microsoft Edge.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.gettempdir()) / "airy-site-preview"
OUT.mkdir(parents=True, exist_ok=True)
PROFILE = OUT / "edge-profile"


def find_edge():
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")):
        if base:
            p = Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
            if p.exists():
                return str(p)
    p = shutil.which("msedge")
    if p:
        return p
    sys.exit("Microsoft Edge not found")


EDGE = find_edge()


def screenshot(url, w, h, name, budget=4000):
    target = OUT / name
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--user-data-dir={PROFILE}", f"--window-size={w},{h}", f"--virtual-time-budget={budget}",
                    f"--screenshot={target}", url], capture_output=True, timeout=120)
    return Image.open(target).convert("RGB")


def content_end(im, width):
    """Last row that differs from the bottom-left background colour."""
    w, h = im.size
    bg = im.getpixel((5, h - 5))
    for y in range(h - 1, 0, -10):
        if any(abs(sum(im.getpixel((x, y))) - sum(bg)) > 6 for x in range(0, min(w, width), 10)):
            return y
    return h


page = (ROOT / "index.html").as_uri()

desk = screenshot(page, 1440, 9000, "desk.png")
end = content_end(desk, 1440)
desk.crop((0, 0, 1440, 1300)).save(OUT / "top.png")
desk.crop((0, max(0, end - 1500), 1440, min(desk.height, end + 20))).save(OUT / "tail.png")
print("desktop page height", end)

# Headless Edge has a minimum window width, so the phone view loads the page in a 390 px iframe.
frame = OUT / "phone-frame.html"
frame.write_text('<!doctype html><html><body style="margin:0;background:#888"><iframe src="' + page +
                 '" style="border:0;width:390px;height:16000px;display:block;background:white"></iframe></body></html>',
                 encoding="utf-8")
phone = screenshot(frame.as_uri(), 600, 16000, "phone-full.png", budget=5000).crop((0, 0, 390, 16000))
end = content_end(phone, 390)
phone = phone.crop((0, 0, 390, end + 10))
phone.save(OUT / "phone.png")
cols = 6
seg = -(-phone.height // cols)
sheet = Image.new("RGB", (cols * 400, seg), (136, 136, 136))
for i in range(cols):
    sheet.paste(phone.crop((0, i * seg, 390, min((i + 1) * seg, phone.height))), (i * 400, 0))
sheet.save(OUT / "phone-sheet.png")
(OUT / "phone-full.png").unlink(missing_ok=True)
print("phone page height", phone.height)
print("screenshots in", OUT)
