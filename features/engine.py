"""Startup job: make sure yt-dlp / ffmpeg / JS runtime exist, then update yt-dlp."""
from core import binaries, installer
from .base import Feature


class EngineFeature(Feature):
    id = "engine"
    name = "Engine"
    slot = None
    config_defaults = {"prefer_system_binaries": True, "fetch_deno": True}

    def on_startup(self, ctx):
        installer.ensure(ctx.config, ctx.log)
        if ctx.ffmpeg_path:
            ctx.log("[sys] ffmpeg ready\n", "success")
        else:
            ctx.log("[sys] ffmpeg not found — thumbnail embedding will fail\n", "error")
        if not binaries.has_js_runtime():
            ctx.log("[sys] no JavaScript runtime (deno/node/bun) — YouTube downloads may fail\n", "warning")
        installer.update_ytdlp(ctx.config, ctx.log)
