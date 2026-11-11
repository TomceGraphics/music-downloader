"""Generate assets/icons/<name>@1x.png (18 px) and @2x.png (36 px): line icons drawn on a 24-unit grid,
supersampled 8x. The app loads them with tk.PhotoImage, so it needs no Pillow at runtime.
    python tools/make_icons.py        (needs Pillow)"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
GRAY, WHITE, GREEN, RED = (138, 138, 138), (255, 255, 255), (77, 170, 87), (235, 87, 87)
SS = 8


def render(draw_fn, color, px):
    k = px * SS / 24
    img = Image.new("RGBA", (px * SS, px * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = color + (255,)

    def stroke(pts, w=1.9):
        pts = [(x * k, y * k) for x, y in pts]
        d.line(pts, fill=c, width=round(w * k), joint="curve")
        r = w * k / 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)

    def rrect(box, r, w=1.9, fill=None):
        b = [v * k for v in box]
        d.rounded_rectangle(b, radius=r * k, outline=None if fill else c, width=round(w * k), fill=fill)

    def circle(cx, cy, r, w=1.9, fill=False):
        b = ((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k)
        d.ellipse(b, outline=None if fill else c, width=round(w * k), fill=c if fill else None)

    draw_fn(stroke, rrect, circle, d, k, c)
    return img.resize((px, px), Image.LANCZOS)


def gear(stroke, rrect, circle, d, k, c):
    for i in range(8):
        a = math.radians(i * 45)
        stroke([(12 + 7.6 * math.cos(a), 12 + 7.6 * math.sin(a)), (12 + 9.8 * math.cos(a), 12 + 9.8 * math.sin(a))], 3.6)
    circle(12, 12, 6.2, 2.6)
    circle(12, 12, 2.2, 2.0)


def paste(stroke, rrect, circle, d, k, c):
    rrect((5, 5.5, 19, 21), 2.5)
    rrect((8.5, 3, 15.5, 7.5), 1.6)
    stroke([(8.5, 12), (15.5, 12)]); stroke([(8.5, 16), (13, 16)])


def download(stroke, rrect, circle, d, k, c):
    stroke([(12, 4), (12, 15.5)], 2.2); stroke([(7, 11), (12, 16), (17, 11)], 2.2); stroke([(5.5, 20), (18.5, 20)], 2.2)


def folder(stroke, rrect, circle, d, k, c):
    stroke([(3.5, 7.5), (9.5, 7.5), (11.5, 9.5), (20.5, 9.5), (20.5, 18.5), (3.5, 18.5), (3.5, 7.5)])


def back(stroke, rrect, circle, d, k, c):
    stroke([(19, 12), (5.5, 12)]); stroke([(11.5, 6), (5.5, 12), (11.5, 18)])


def chev_down(stroke, rrect, circle, d, k, c):
    stroke([(6, 9.5), (12, 15.5), (18, 9.5)], 2.1)


def chev_up(stroke, rrect, circle, d, k, c):
    stroke([(6, 14.5), (12, 8.5), (18, 14.5)], 2.1)


def check(stroke, rrect, circle, d, k, c):
    stroke([(5, 12.5), (10, 17.5), (19, 7)], 2.4)


def cross(stroke, rrect, circle, d, k, c):
    stroke([(6.5, 6.5), (17.5, 17.5)], 2.3); stroke([(17.5, 6.5), (6.5, 17.5)], 2.3)


def skip(stroke, rrect, circle, d, k, c):
    stroke([(6, 7), (11, 12), (6, 17)], 2.1); stroke([(13, 7), (18, 12), (13, 17)], 2.1)


def note(stroke, rrect, circle, d, k, c):
    circle(8.5, 17.5, 2.7, fill=True); circle(16.5, 15.5, 2.7, fill=True)
    stroke([(11.2, 17.5), (11.2, 6.8)], 1.8); stroke([(19.2, 15.5), (19.2, 4.8)], 1.8)
    d.polygon([(11.2 * k, 6.8 * k), (19.2 * k, 4.8 * k), (19.2 * k, 8 * k), (11.2 * k, 10 * k)], fill=c)


def dup(stroke, rrect, circle, d, k, c):
    rrect((4.5, 4.5, 15, 15), 2)
    rrect((9, 9, 19.5, 19.5), 2, fill=(0, 0, 0, 0))         # knock out what is behind the front square
    rrect((9, 9, 19.5, 19.5), 2)


ICONS = {"gear": (gear, GRAY), "paste": (paste, GRAY), "download": (download, WHITE), "folder": (folder, GRAY),
         "back": (back, GRAY), "chev-down": (chev_down, GRAY), "chev-up": (chev_up, GRAY), "check": (check, GREEN),
         "cross": (cross, RED), "skip": (skip, GRAY), "note": (note, GRAY), "dup": (dup, GRAY)}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (fn, color) in ICONS.items():
        for tag, px in (("1x", 18), ("2x", 36)):
            render(fn, color, px).save(OUT / f"{name}@{tag}.png", optimize=True)
    print("wrote", len(list(OUT.glob("*.png"))), "icons to", OUT)
