"""Duplicate MP3 finder. Pure Python: no tkinter. Same behaviour as before:
key = (artist, title) lower-cased, the later file is moved to <folder>/Duplicates/."""
import shutil
from pathlib import Path


def check_duplicates(folder: str, log_cb, done_cb) -> None:
    try:
        from tinytag import TinyTag
    except ImportError:
        log_cb("tinytag not installed\n", "error"); done_cb(0); return

    out_dir = Path(folder)
    dup_dir = out_dir / "Duplicates"
    mp3s = list(out_dir.glob("*.mp3"))

    if not mp3s:
        log_cb("no MP3s found in output folder\n", "warning"); done_cb(0); return

    log_cb(f"scanning {len(mp3s)} file(s)...\n", "info")
    seen: dict[tuple, Path] = {}
    moved = 0

    for mp3 in mp3s:
        try:
            tag = TinyTag.get(str(mp3))
            title = (tag.title or "").strip().lower()
            artist = (tag.artist or "").strip().lower()
            # untagged files fall back to the filename so they are never lumped together
            key = (artist, title) if (artist or title) else (mp3.stem.lower(), "")
        except Exception:
            key = (mp3.stem.lower(), "")

        if key in seen:
            dup_dir.mkdir(exist_ok=True)
            dest = dup_dir / mp3.name
            if dest.exists():
                dest = dup_dir / (mp3.stem + f"_{moved}" + mp3.suffix)
            shutil.move(str(mp3), str(dest))
            log_cb(f"  moved  {mp3.name}\n", "warning")
            moved += 1
        else:
            seen[key] = mp3

    msg = f"{moved} duplicate(s) moved to Duplicates/" if moved else "no duplicates found"
    log_cb(msg + "\n", "success")
    done_cb(moved)
