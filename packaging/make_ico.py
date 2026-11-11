"""Windows build step: assets/icon.png -> assets/icon.ico (needs Pillow, build-time only)."""
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parent.parent
img = Image.open(root / "assets" / "icon.png").convert("RGBA")
img.save(root / "assets" / "icon.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
print("wrote assets/icon.ico")
