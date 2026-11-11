"""Checks GitHub for a newer release at startup and shows the result in the footer.
Silent when offline. Never downloads or installs anything. Disable: config check_updates=false."""
import json
import re
import urllib.request

from core.version import GITHUB_REPO, VERSION
from .base import Feature


def _ver(s: str) -> tuple:
    return tuple(int(n) for n in re.findall(r"\d+", s))[:3]


class UpdateCheckFeature(Feature):
    id = "update_check"
    name = "Update check"
    slot = None
    config_defaults = {"check_updates": True}

    def on_startup(self, ctx):
        if not ctx.get("check_updates", True) or "OWNER" in GITHUB_REPO:
            return
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": "music-downloader", "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.load(r)
            tag, url = data.get("tag_name", ""), data.get("html_url", "")
            if tag and _ver(tag) > _ver(VERSION):
                ctx.log(f"[sys] update available: {tag} — {url}\n", "info")
                ctx.set_footer(f"Update available: {tag}", url)
            elif tag:
                ctx.set_footer(f"v{VERSION}  ·  up to date")
        except Exception:
            pass
