# Architecture

| module | responsibility |
|---|---|
| `main.py` | entry point: build config, features, context, window |
| `core/version.py` | VERSION and app names — the single source of truth |
| `core/paths.py` | frozen/source detection; config, data and bin dirs (XDG / %APPDATA%) |
| `core/config.py` | JSON config with defaults; legacy `config.json` migration |
| `core/binaries.py` | locate yt-dlp / ffmpeg / JS runtime (config → system → managed) |
| `core/installer.py` | first-run downloads into the bin dir; yt-dlp updater |
| `core/proc.py` | the only place subprocesses start (UTF-8, no console flash) |
| `core/downloader.py` | yt-dlp command + output parsing + cookie fallback (callbacks only) |
| `core/duplicates.py` | duplicate MP3 finder (callbacks only) |
| `core/context.py` | `AppContext`: the only object features talk to |
| `core/covers.py` | embedded cover → small PNG via ffmpeg (no Pillow) |
| `core/notify.py` | desktop notifications (notify-send / PowerShell toast) |
| `ui/theme.py` | (light, dark) colour tokens, spacing/radii, bundled Inter + font fallback |
| `ui/icons.py` | PNG line icons (1x/2x) |
| `ui/widgets.py` | Label, ghost_btn, primary_btn, text_input, Card, StatusPill |
| `ui/track_list.py` | scrollable per-track rows (cover, progress, state) |
| `ui/log_panel.py` | collapsible "Details" log |
| `ui/main_window.py` | window shell: nav, main page, settings page, footer; no feature logic |
| `features/` | one file per feature; `__init__.py` holds `FEATURES` |
| `tools/` | dev-only: README screenshots and banner generators |

## AppContext API
- Config: `get(key, default)`, `set(key, value)`, `output_folder`
- Tools: `ffmpeg_path`, `ytdlp_cmd`, `js_args`
- Feedback (thread-safe): `log(msg, tag)`, `set_status(msg)`, `set_dot(color)`,
  `set_progress(pct)` (eased), `set_counter(cur, total)`, `set_counter_text(text, color)`,
  `track_event(kind, **data)`, `set_footer(text, url)`, `notify(title, body)`
- Threads: `run_in_thread(fn, *args)`, `on_main(fn, *args)`; `ui_scale` is the window scaling

Worker threads never touch Tk: updates are queued and run by the shell every 40 ms.
User data lives in `~/.config/music-downloader`, `~/.local/share/music-downloader`
(Windows: `%APPDATA%` / `%LOCALAPPDATA%\MusicDownloader`).
`archive.txt` stays in the chosen output folder, next to the music it describes.
