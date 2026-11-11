"""Footer button: move duplicate MP3s into <output>/Duplicates (core.duplicates)."""
from core.duplicates import check_duplicates
from ui.theme import C_TEXT, S2, S4
from ui.widgets import ghost_btn
from .base import Feature


class DuplicatesFeature(Feature):
    id = "duplicates"
    name = "Check duplicates"
    slot = "footer"

    def build_ui(self, parent, ctx):
        ghost_btn(parent, "Check duplicates", lambda: self.run(ctx), width=150, height=34,
                  color=C_TEXT, icon="dup").pack(side="right", padx=(0, S4), pady=S2)

    def run(self, ctx):
        ctx.set_status("scanning")
        ctx.run_in_thread(
            check_duplicates, ctx.output_folder, ctx.log,
            lambda n: ctx.set_status(f"{n} duplicate(s) moved" if n else "no duplicates found"),
        )
