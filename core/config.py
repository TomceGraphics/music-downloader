"""JSON config with defaults. Existing keys (output_folder, browser) stay compatible."""
import json
import threading
from pathlib import Path

from .paths import config_dir, default_music_dir, legacy_config_file


class Config:
    def __init__(self, path: Path | None = None):
        self._path = path or config_dir() / "config.json"
        self._lock = threading.Lock()
        self._defaults: dict = {"output_folder": str(default_music_dir())}
        self._data: dict = self._load()

    def _load(self) -> dict:
        # new location first, then the legacy file next to the exe (one-time migration)
        for p in (self._path, legacy_config_file()):
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
        return {}

    def register(self, defaults: dict) -> None:
        """Features declare their keys; existing defaults are never overwritten."""
        for k, v in (defaults or {}).items():
            self._defaults.setdefault(k, v)

    def get(self, key: str, default=None):
        return self._data.get(key, self._defaults.get(key, default))

    def set(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = value
            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
            except Exception:
                pass
