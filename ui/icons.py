"""Line icons as plain PNG PhotoImages (assets/icons/<name>@1x|2x.png). No Pillow needed."""
import tkinter as tk

from core.paths import resource_dir
from . import theme

_cache: dict = {}


def get(name: str | None):
    """PhotoImage for `name` (1x, or 2x when the window is scaled >= 1.5), or None if missing."""
    if not name:
        return None
    tag = "2x" if theme.SCALE >= 1.5 else "1x"
    key = (name, tag)
    if key not in _cache:
        try:
            _cache[key] = tk.PhotoImage(file=str(resource_dir() / "assets" / "icons" / f"{name}@{tag}.png"))
        except Exception:
            _cache[key] = None
    return _cache[key]
