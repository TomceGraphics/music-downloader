"""Print one value from core/version.py:  python packaging/info.py version|slug"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.version import APP_SLUG, VERSION  # noqa: E402

print({"version": VERSION, "slug": APP_SLUG}[sys.argv[1]])
