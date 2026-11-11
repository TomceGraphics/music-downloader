"""The Feature contract. Keep it minimal — anything more goes through ctx."""


class Feature:
    id: str = ""                 # unique, lowercase
    name: str = ""               # section title for slot "source"/"settings"
    slot: str | None = None      # "source" | "settings" | "footer" | None (no UI)
    config_defaults: dict = {}   # config keys this feature owns, with defaults

    def build_ui(self, parent, ctx) -> None:
        """Main thread. Add widgets to `parent` (the slot's frame)."""

    def on_startup(self, ctx) -> None:
        """Optional. Runs in a worker thread at launch (never touch widgets here)."""
