"""Generate assets/banner.png. Run tools/make_screenshots.py first (the banner reuses a crop of it).
    python tools/make_banner.py        (needs Pillow)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from PIL import Image, ImageDraw  # noqa: E402

import _gfx  # noqa: E402

W, H = 2400, 720
c = _gfx.gradient_bg(W, H)
for fx, fy, fr, col, a in [(0.08, 0.5, 0.20, (35, 131, 226), 150), (0.95, 0.15, 0.25, (124, 92, 255), 130),
                           (0.55, 1.1, 0.22, (25, 195, 178), 70)]:
    _gfx.blob(c, int(W * fx), int(H * fy), int(W * fr), col, a)

# icon with glow
_gfx.blob(c, 290, 230, 170, (35, 131, 226), 140)
icon = Image.open(ROOT / "assets" / "icon.png").convert("RGBA").resize((220, 220), Image.LANCZOS)
c.alpha_composite(icon, (180, 120))

d = ImageDraw.Draw(c)
d.text((150, 350), "Music Downloader", font=_gfx.font(["InterDisplay-Bold.otf", "Inter-Bold.otf", "DejaVuSans-Bold.ttf"], 104), fill="white")
sub = _gfx.font(["Inter-Regular.otf", "DejaVuSans.ttf"], 40)
d.text((154, 500), "Playlists to tagged MP3s.", font=sub, fill=(168, 180, 204))
d.text((154, 556), "One window. Windows and Linux.", font=sub, fill=(120, 134, 164))

# crop of the real UI on the right
shot = Image.open(ROOT / "docs" / "screenshots" / "01-download.png").convert("RGBA")
card = _gfx.rounded(shot.crop((380, 330, 1620, 930)), 40)
w = 960
h = round(card.height * w / card.width)
card = card.resize((w, h), Image.LANCZOS)
x, y = W - w - 100, 120
_gfx.shadow(c, x, y, w, h, 30, dy=30, blur=50, opacity=170)
c.alpha_composite(card, (x, y))

out = ROOT / "assets" / "banner.png"
c.convert("RGB").save(out, optimize=True)
print("wrote", out, c.size)
