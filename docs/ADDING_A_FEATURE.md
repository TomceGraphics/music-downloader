# Adding a feature

A feature = one file in `features/` + one line in `features/__init__.py`.
Give an AI only this file and `features/_template.py`.

## Steps
1. `cp features/_template.py features/my_feature.py`; rename the class; set `id`, `name`, `slot`.
2. In `features/__init__.py`: `from .my_feature import MyFeature` and add it to `FEATURES`.
3. `python main.py`.

## Contract (`features/base.py`)
| member | meaning |
|---|---|
| `id`, `name` | unique id; `name` is the card title for the `settings` slot |
| `slot` | `"source"` (the URL row), `"settings"` (a card on the gear/settings page, title added for you), `"footer"` (pack `side="right"`), or `None` (no UI) |
| `config_defaults` | `{key: default}` — registered automatically |
| `build_ui(parent, ctx)` | main thread; add widgets to `parent` |
| `on_startup(ctx)` | optional; runs in a worker thread at launch |

## `ctx` (thread-safe unless noted)
- `get(key, default)` / `set(key, value)` — config, auto-saved. Prefix keys with your `id`.
- `output_folder` (get/set), `ffmpeg_path`, `ytdlp_cmd` (list), `js_args` (list)
- `log(msg, tag)` — end `msg` with `\n`; tags: success error warning info progress meta skip normal
- `set_status(text)`, `set_dot(hex)`, `set_progress(0–100)`, `set_counter(cur, total)`, `set_counter_text(text, color)`
- `track_event(kind, index=..., **data)` — drive the track list (`reset start name progress stage done skip fail cover`)
- `set_footer(text, url=None)` — footer text (a url makes it a link); `notify(title, body)` — desktop notification (respects the user's setting)
- `ui_scale` — window scaling (size bitmaps with it)
- `run_in_thread(fn, *args)` — start a daemon worker
- `on_main(fn, *args)` — run `fn` on the Tk thread (needed to touch your own widgets from a worker)

## Rules
- Never touch widgets from a worker thread; use `ctx.on_main`.
- Put logic in `core/<name>.py` as plain functions taking callbacks. `core/` must not import tkinter.
- Colours are `(light, dark)` tokens from `ui/theme.py` (CustomTkinter widgets accept them directly); spacing `S1..S6`, radii `R_SM/R_MD/R_LG`. No hard-coded fonts or hex colours.
- Widgets from `ui/widgets.py`; icons are PNGs in `assets/icons` (`ghost_btn(..., icon="folder")`); regenerate with `tools/make_icons.py`.
- Subprocesses via `core.proc.popen/run` (hides the Windows console, fixes Linux library paths).
- Never hard-code `.exe` or user paths; use `core.paths` and `ctx`.
- User data (config, downloads, archives) never goes in the repo or the app folder.
