"""Entry point only."""
import sys

try:
    import tkinter  # noqa: F401
except ImportError:
    sys.exit("Tkinter is missing. On Fedora: sudo dnf install python3-tkinter")

from core.config import Config
from core.context import AppContext
from features import FEATURES
from ui import theme
from ui.main_window import App


def main() -> None:
    config = Config()
    features = [cls() for cls in FEATURES]
    for f in features:
        config.register(f.config_defaults)
    theme.apply_appearance(config.get("appearance", "system"))
    App(AppContext(config), features).mainloop()


if __name__ == "__main__":
    main()
