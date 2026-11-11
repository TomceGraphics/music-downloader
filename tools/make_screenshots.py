"""Generate docs/screenshots/*.png from the REAL UI, driven with staged sample data
(fictional artists, generated cover art, no network, no yt-dlp). Needs Pillow and a display. Headless:

    xvfb-run -a -s "-screen 0 1800x1500x24" python tools/make_screenshots.py
"""
import colorsys
import os
import struct
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import customtkinter as ctk                      # noqa: E402
from PIL import Image, ImageDraw, ImageGrab      # noqa: E402

import _gfx                                      # noqa: E402
from core.config import Config                   # noqa: E402
from core.context import AppContext              # noqa: E402
from core.downloader import _stream_proc         # noqa: E402
from core.duplicates import check_duplicates     # noqa: E402
from core.version import APP_NAME, VERSION       # noqa: E402
from features import FEATURES                    # noqa: E402
from ui import theme                             # noqa: E402
from ui.main_window import App                   # noqa: E402

S = 2                                            # render at 2x for crisp images
OUT = ROOT / "docs" / "screenshots"
FOLDER = "/home/you/Music"
URL = "https://music.youtube.com/playlist?list=PLdemo-sample-playlist"
TRACKS = [("Nova Drift", "Midnight Signal"), ("Lumen Park", "Glass Harbour"), ("Aster Vale", "Slow Orbit"),
          ("Kite & Ember", "Paper Moons"), ("Hollow Pine", "Late Bloom"), ("Sable Coast", "Neon Tides"),
          ("Odette Rue", "Afterglow Theory"), ("Mira Voss", "Static Garden"), ("The Low Tides", "Seventeen Miles"),
          ("Juno Arc", "Velvet Hours"), ("Frost & Fable", "Northern Window"), ("Pale Cartel", "Drive Home")]
SKIPPED = {3, 9}                                 # items already in archive.txt


class FakeProc:
    """Stands in for yt-dlp so the REAL output parser and track events drive the UI."""
    returncode = 0

    def __init__(self, lines):
        self.stdout = iter(l + "\n" for l in lines)

    def wait(self):
        pass


def ytdlp_lines(upto=12, partial_pct=None):
    out = ["[youtube:tab] Playlist: Demo Mix: Downloading 12 items"]
    for i in range(1, upto + 1):
        artist, title = TRACKS[i - 1]
        name = f"{artist} - {title}"
        out.append(f"[download] Downloading item {i} of 12")
        if i in SKIPPED:
            out.append("[download] dQw4w9WgXc%02d has already been recorded in the archive" % i)
            continue
        out.append(f"[download] Destination: {FOLDER}/{name}.webm")
        if i == upto and partial_pct is not None:
            out.append(f"[download]  {partial_pct:.1f}% of 3.84MiB at 2.40MiB/s ETA 00:01")
            break
        out += ["[download] 100% of 3.84MiB in 00:00:02 at 1.80MiB/s",
                f"[ExtractAudio] Destination: {FOLDER}/{name}.mp3",
                f'[EmbedThumbnail] ffmpeg: Adding thumbnail to "{FOLDER}/{name}.mp3"']
    return out


def make_cover(path, hue, px):
    """Generated cover art: two-tone gradient with a soft circle (sample data, not real album art)."""
    img = Image.new("RGB", (px, px))
    d = ImageDraw.Draw(img)
    for y in range(px):
        r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.95 - 0.35 * y / px)
        d.line([(0, y), (px, y)], fill=(int(r * 255), int(g * 255), int(b * 255)))
    r, g, b = colorsys.hsv_to_rgb((hue + 0.12) % 1, 0.45, 1.0)
    d.ellipse((px * 0.18, px * 0.18, px * 0.82, px * 0.82), outline=(int(r * 255), int(g * 255), int(b * 255)), width=max(2, px // 14))
    img.save(path)


def make_mp3(path, artist, title):
    """Tiny MP3 (ID3v2.3 tag + silent frames) so the duplicate checker runs for real."""
    def frame(fid, text):
        data = b"\x00" + text.encode("latin-1", "replace")
        return fid + struct.pack(">I", len(data)) + b"\x00\x00" + data
    body = frame(b"TIT2", title) + frame(b"TPE1", artist)
    size = bytes((len(body) >> s) & 0x7F for s in (21, 14, 7, 0))
    Path(path).write_bytes(b"ID3\x03\x00\x00" + size + body + (b"\xff\xfb\x90\x00" + b"\x00" * 413) * 8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    cfg = Config(tmp / "config.json")
    cfg.set("output_folder", FOLDER)
    cfg.set("browser", "firefox")
    feats = [cls() for cls in FEATURES if cls.slot]          # skip Engine/UpdateCheck: no network
    for f in feats:
        cfg.register(f.config_defaults)
    by_id = {f.id: f for f in feats}

    ctk.set_widget_scaling(S)
    ctk.set_window_scaling(S)
    ctx = AppContext(cfg)
    app = App(ctx, feats)
    app.geometry("+0+0")
    dl = by_id["download"]

    covers = {}
    for i in range(1, 13):
        covers[i] = tmp / f"cover{i}.png"
        make_cover(covers[i], (i * 0.083 + 0.02) % 1, round(40 * S))
    dl._cover = lambda index, path: ctx.track_event("cover", index=index, path=str(covers[index]))

    def settle(n=8):
        for _ in range(n):
            ctx.pump()
            app.update()
            time.sleep(0.12)

    def snap(name):
        settle(10)
        x, y, w, h = app.winfo_rootx(), app.winfo_rooty(), app.winfo_width(), app.winfo_height()
        return ImageGrab.grab(bbox=(x, y, x + w, y + h), xdisplay=os.environ["DISPLAY"]).convert("RGB")

    def reset(mode):
        theme.apply_appearance(mode)
        app.show_page("main")
        app.logp.clear()
        app.tracks.reset()
        app.set_progress(0); app._shown = 0; app.progress.set(0)
        app.set_counter_text(""); app.set_status("ready"); app.set_dot(theme.C_GREEN)
        app.set_footer(f"v{VERSION}  ·  up to date")
        dl.entry.delete(0, "end"); dl.entry.insert(0, URL)
        dl.busy = False
        dl.btn.configure(state="normal", text="Download")
        settle(4)

    def stream(lines):
        return _stream_proc(FakeProc(lines), app.log, lambda p: None, lambda c, t: None, dl._on_track)

    shots = {}

    # 1 ── dark, mid-download: covers, skip, live row with speed/ETA
    reset("dark")
    dl.busy = True
    dl.btn.configure(state="disabled", text="Downloading…")
    app.set_status("downloading"); app.set_dot(theme.C_WARNING)
    app.log("[sys] ffmpeg ready\n", "success"); app.log(f"{URL}\n\n", "info")
    stream(ytdlp_lines(upto=7, partial_pct=62.0))
    settle(8)                                      # apply the queued events first, in order
    # the fake stream ends here, which would mark item 7 done; show it as still downloading
    app.track_event("progress", index=7, pct=62.0, speed="2.40MiB/s", eta="00:01")
    app.set_progress((6 + 0.62) / 12 * 100)
    settle(14)
    shots["01-download"] = snap("01")

    # 2 ── light, finished
    reset("light")
    app.log(f"{URL}\n\n", "info")
    stats = stream(ytdlp_lines())
    app.log("\ndownload complete\n", "success")
    dl._done(stats)
    settle(16)
    shots["02-complete"] = snap("02")

    # 3 ── dark, settings page (folder, cookies, theme, notifications)
    reset("dark")
    by_id["appearance"].seg.set("Dark")
    app.show_page("settings")
    shots["03-settings"] = snap("03")

    # 4 ── dark, Details drawer + duplicate checker on real (tiny) MP3 files
    reset("dark")
    music = tmp / "Music"; music.mkdir()
    for artist, title in TRACKS[:6]:
        make_mp3(music / f"{artist} - {title}.mp3", artist, title)
    for artist, title in (TRACKS[1], TRACKS[4]):
        make_mp3(music / f"{artist} - {title} (1).mp3", artist, title)
    app.logp.toggle()
    app.set_status("scanning")
    check_duplicates(str(music), app.log, lambda n: app.set_status(f"{n} duplicate(s) moved"))
    shots["04-details"] = snap("04")

    # presentation versions: window frame + gradient + headline
    title = f"{APP_NAME}  v{VERSION}"
    framed = {k: _gfx.window_frame(v, title) for k, v in shots.items()}
    heads = {
        "01-download": ("Every track, live", "Cover art, speed and ETA for each song as it downloads."),
        "02-complete": ("Light, dark, or yours", "Follows your system theme and tells you when it's done."),
        "03-settings": ("Settings, out of the way", "Folder, cookies, theme and notifications live behind the gear."),
        "04-details": ("Details when you need them", "A collapsible log and a duplicate checker, kept out of the main view."),
    }
    for key, (h1, h2) in heads.items():
        canvas = presentation(1, 2000, 1580, h1, h2)
        _gfx.place(canvas, framed[key], 380, 330, 1240)
        canvas.convert("RGB").save(OUT / f"{key}.png", optimize=True)

    hero = presentation(0, 2800, 1800, "Music Downloader", "Playlists to tagged MP3s. One window. Windows and Linux.")
    _gfx.place(hero, framed["02-complete"], 1500, 560, 1100)
    _gfx.place(hero, framed["01-download"], 260, 470, 1380)
    hero.convert("RGB").save(OUT / "hero.png", optimize=True)
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
    os._exit(0)                                   # skip Tk teardown noise


def presentation(variant, w, h, headline, sub):
    c = _gfx.gradient_bg(w, h)
    blobs = [[(0.12, 0.2, 0.30, (35, 131, 226), 150), (0.88, 0.35, 0.34, (124, 92, 255), 120), (0.5, 1.0, 0.40, (25, 195, 178), 70)],
             [(0.85, 0.15, 0.32, (35, 131, 226), 140), (0.1, 0.8, 0.34, (124, 92, 255), 110), (0.6, 1.0, 0.3, (25, 195, 178), 60)]][variant]
    for fx, fy, fr, col, a in blobs:
        _gfx.blob(c, int(w * fx), int(h * fy), int(w * fr), col, a)
    d = ImageDraw.Draw(c)
    big = _gfx.font(["InterDisplay-Bold.otf", "Inter-Bold.otf", "DejaVuSans-Bold.ttf"], int(w * (0.052 if variant == 0 else 0.044)))
    small = _gfx.font(["Inter-Regular.otf", "DejaVuSans.ttf"], int(w * 0.0165))
    y = int(h * (0.085 if variant == 0 else 0.07))
    d.text((w / 2, y), headline, font=big, fill=(255, 255, 255), anchor="mt")
    d.text((w / 2, y + big.size * 1.35), sub, font=small, fill=(168, 180, 204), anchor="mt")
    return c


if __name__ == "__main__":
    main()
