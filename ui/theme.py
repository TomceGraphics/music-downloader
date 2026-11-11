"""Design tokens. Colours are (light, dark) pairs: CustomTkinter picks the right one and
follows the OS appearance. Plain tk widgets (the log) use pick()/mode_index() instead."""
import ctypes
import sys
import tkinter.font as tkfont
import warnings

import customtkinter as ctk

from core.paths import IS_WINDOWS, resource_dir

warnings.filterwarnings("ignore", message=".*not CTkImage.*")   # we use plain PNG PhotoImages (no Pillow)

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# ── colour tokens: (light, dark) ───────────────────────────────────────────
C_BG = ("#ffffff", "#191919")
C_SURFACE = ("#f7f6f3", "#202020")       # nav, footer, cards, rows
C_INPUT = ("#efeeeb", "#2a2a2a")         # inputs, raised bits inside surfaces
C_HOVER = ("#e6e5e1", "#323232")
C_BORDER = ("#e3e2de", "#303030")
C_TEXT = ("#2f2e2b", "#f2f2f2")
C_SECONDARY = ("#6f6e69", "#a0a0a0")
C_DIM = ("#a3a29d", "#666666")
C_BLUE = ("#2383e2", "#2f8bec")          # primary action + live progress only
C_BLUE_HOV = ("#1a6fc4", "#4a9cf0")
C_RED = ("#d9453d", "#ef6a63")
C_GREEN = ("#2f9e44", "#52b05f")
C_WARNING = ("#c98a1b", "#d9ad55")
C_LOG_BG = ("#f3f2ef", "#121212")
C_SELECT = ("#cfe3f8", "#1e3a5f")

LOG_TAGS = [
    ("success", C_GREEN), ("error", C_RED), ("warning", C_WARNING), ("info", C_BLUE),
    ("progress", C_SECONDARY), ("meta", C_BLUE), ("skip", C_DIM), ("normal", C_SECONDARY),
    ("ts", ("#bdbcb7", "#444444")),
]

# ── spacing scale and radii ────────────────────────────────────────────────
S1, S2, S3, S4, S5, S6 = 4, 8, 12, 16, 24, 32
R_SM, R_MD, R_LG = 8, 10, 14

SCALE = 1.0                                # window scaling, set by the shell


def set_scale(s: float) -> None:
    global SCALE
    SCALE = s


def mode_index() -> int:
    """0 = light, 1 = dark (current effective appearance)."""
    return 0 if ctk.get_appearance_mode() == "Light" else 1


def pick(pair):
    return pair[mode_index()] if isinstance(pair, (tuple, list)) else pair


def apply_appearance(mode: str) -> None:
    ctk.set_appearance_mode(mode if mode in ("system", "light", "dark") else "system")


# ── fonts: bundled Inter first, then whatever the OS has ───────────────────
UI_FONTS = ("Inter", "Segoe UI", "Cantarell", "DejaVu Sans", "Liberation Sans")
MONO_FONTS = ("Consolas", "DejaVu Sans Mono", "Liberation Mono", "Courier New")
_FM = "Inter"
_MONO = "Consolas"


def _register_font_file(path) -> bool:
    """Make a font file available to this process only (nothing is installed system-wide)."""
    try:
        if IS_WINDOWS:
            return bool(ctypes.windll.gdi32.AddFontResourceExW(str(path), 0x10, 0))   # FR_PRIVATE
        if sys.platform.startswith("linux"):
            fc = ctypes.CDLL("libfontconfig.so.1")
            fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            return bool(fc.FcConfigAppFontAddFile(None, str(path).encode()))
    except Exception:
        pass
    return False


def init_fonts(root) -> None:
    """Call once, right after the Tk root exists."""
    global _FM, _MONO
    for name in ("Inter-Regular.otf", "Inter-Bold.otf"):
        _register_font_file(resource_dir() / "assets" / "fonts" / name)
    have = set(tkfont.families(root))
    ui_default = tkfont.nametofont("TkDefaultFont", root=root).actual("family")
    mono_default = tkfont.nametofont("TkFixedFont", root=root).actual("family")
    _FM = next((f for f in UI_FONTS if f in have), ui_default)
    _MONO = next((f for f in MONO_FONTS if f in have), mono_default)


def F(size: int, weight: str = "normal"):
    return (_FM, size, weight)


def FMONO(size: int, weight: str = "normal"):
    return (_MONO, size, weight)
