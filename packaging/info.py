"""Print one value from core/version.py:  python packaging/info.py version|slug|name|repo"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.version import APP_NAME, APP_SLUG, GITHUB_REPO, VERSION  # noqa: E402

print({"version": VERSION, "slug": APP_SLUG, "name": APP_NAME, "repo": GITHUB_REPO}[sys.argv[1]])
