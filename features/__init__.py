"""Feature registry. Adding a feature = import it here + add it to FEATURES.
Order = order on screen (within each slot). Explicit list so PyInstaller bundles everything."""
from .engine import EngineFeature
from .download import DownloadFeature
from .output_folder import OutputFolderFeature
from .cookies import CookiesFeature
from .appearance import AppearanceFeature
from .notify import NotifyFeature
from .open_folder import OpenFolderFeature
from .duplicates import DuplicatesFeature
from .update_check import UpdateCheckFeature

FEATURES = [
    EngineFeature,
    DownloadFeature,
    OutputFolderFeature,
    CookiesFeature,
    AppearanceFeature,
    NotifyFeature,
    OpenFolderFeature,      # footer buttons: first in the list = rightmost
    DuplicatesFeature,
    UpdateCheckFeature,
]
