"""Tiny image helpers shared by make_screenshots.py and make_banner.py (needs Pillow)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

_FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/inter",
              "/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts"]


def font(names, size):
    """First font file found among `names` (e.g. 'Inter-Bold.otf'), else Pillow's default."""
    for d in _FONT_DIRS:
        for n in names:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def gradient_bg(w, h, top=(9, 12, 22), bottom=(20, 17, 44)):
    g = Image.linear_gradient("L").resize((w, h))
    return ImageOps.colorize(g, black=top, white=bottom).convert("RGBA")


def blob(canvas, cx, cy, r, color, alpha=120, blur=None):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur or r // 2)))


def rounded(img, r):
    """Round the corners of an RGBA/RGB image (4x supersampled mask)."""
    img = img.convert("RGBA")
    m = Image.new("L", (img.width * 4, img.height * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, m.width - 1, m.height - 1), r * 4, fill=255)
    img.putalpha(m.resize(img.size, Image.LANCZOS))
    return img


def shadow(canvas, x, y, w, h, r, dy=40, blur=60, opacity=150):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((x, y + dy, x + w, y + h + dy), r, fill=(0, 0, 0, opacity))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def window_frame(shot, title, bar=52, radius=22):
    """Wrap an app screenshot in a minimal desktop-window frame with a title bar."""
    w, h = shot.size
    s = w / 1720                                   # screenshots are taken at 2x of 860 px
    bar = int(bar * 2 * s)
    win = Image.new("RGBA", (w, h + bar), (27, 27, 27, 255))
    d = ImageDraw.Draw(win)
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx, cy, rr = int(46 * s) + i * int(40 * s), bar // 2, int(10 * s)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col)
    f = font(["Inter-Medium.otf", "Inter-Regular.otf", "DejaVuSans.ttf"], int(24 * s))
    tw = d.textlength(title, font=f)
    d.text(((w - tw) / 2, bar / 2 - int(14 * s)), title, font=f, fill=(138, 138, 138))
    d.rectangle((0, bar - 1, w, bar), fill=(46, 46, 46))
    win.paste(shot.convert("RGBA"), (0, bar))
    return rounded(win, int(radius * 2 * s))


def place(canvas, win, x, y, width, **shadow_kw):
    """Scale `win` to `width`, drop a shadow and paste it at (x, y)."""
    h = round(win.height * width / win.width)
    win = win.resize((width, h), Image.LANCZOS)
    shadow(canvas, x, y, width, h, 36, **shadow_kw)
    canvas.alpha_composite(win, (x, y))
    return h
