"""TEMPLATE — copy to features/my_feature.py, rename the class, then register it:
   features/__init__.py:  from .my_feature import MyFeature   +   add MyFeature to FEATURES.
This example adds a footer button that counts MP3s in the output folder."""
from pathlib import Path

from ui.theme import C_TEXT, S2, S4    # (light, dark) colour tokens, spacing scale S1..S6, F(size) font helper
from ui.widgets import ghost_btn       # Label, primary_btn, text_input, Card live in ui/widgets.py
from .base import Feature


class CountMp3Feature(Feature):
    id = "count_mp3"                   # unique, lowercase
    name = "Count MP3s"                # card title when slot == "settings"
    slot = "footer"                    # "source" (URL row) | "settings" (card on the gear page) | "footer" | None
    config_defaults = {"count_mp3_recursive": False}   # auto-registered; read with ctx.get()

    def build_ui(self, parent, ctx):   # MAIN thread: add widgets to `parent` (the slot's frame)
        ghost_btn(parent, self.name, lambda: self.run(ctx), width=130, height=34,
                  color=C_TEXT, icon="folder").pack(side="right", padx=(0, S4), pady=S2)   # icons: assets/icons

    def run(self, ctx):                # button callback = main thread; hand slow work to a thread
        ctx.set_status("counting...")
        ctx.run_in_thread(self._work, ctx, ctx.output_folder, ctx.get("count_mp3_recursive"))

    def _work(self, ctx, folder, recursive):   # WORKER thread: never touch widgets here
        files = list(Path(folder).glob("**/*.mp3" if recursive else "*.mp3"))
        ctx.log(f"{len(files)} mp3 file(s)\n", "success")  # thread-safe; tags: success error
        ctx.set_status("done")                             # warning info progress meta skip normal
        # Need to update a widget you created? ->  ctx.on_main(self.some_widget.configure, text="x")

    def on_startup(self, ctx):         # optional; runs once in a worker thread at launch
        pass
    # Tools:  ctx.ytdlp_cmd (list)  ctx.ffmpeg_path  ctx.js_args  — spawn with core.proc.popen/run
    # Heavy logic belongs in core/<name>.py as plain functions (no tkinter) so it is testable.
