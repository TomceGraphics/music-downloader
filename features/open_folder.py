"""Footer button: open the output folder in the system file manager."""
from pathlib import Path

from core.proc import open_path
from ui.theme import C_TEXT, S2, S4
from ui.widgets import ghost_btn
from .base import Feature


class OpenFolderFeature(Feature):
    id = "open_folder"
    name = "Open folder"
    slot = "footer"

    def build_ui(self, parent, ctx):
        ghost_btn(parent, "Open folder", lambda: self.run(ctx), width=128, height=34,
                  color=C_TEXT, icon="folder").pack(side="right", padx=(0, S4), pady=S2)

    def run(self, ctx):
        Path(ctx.output_folder).mkdir(parents=True, exist_ok=True)
        open_path(ctx.output_folder)
