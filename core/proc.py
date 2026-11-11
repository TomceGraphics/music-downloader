"""The one way to start subprocesses: UTF-8 output, no console flash on Windows,
and a clean library path on frozen Linux builds."""
import os
import sys
import subprocess

from .paths import FROZEN, IS_WINDOWS

_FLAGS = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
_COMMON = dict(text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)


def _env() -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if FROZEN and not IS_WINDOWS:
        # PyInstaller prepends its own dir to LD_LIBRARY_PATH; children must not inherit it
        if "LD_LIBRARY_PATH_ORIG" in env:
            env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH_ORIG"]
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env


def popen(cmd: list[str]) -> subprocess.Popen:
    """Streaming process: stdout+stderr merged, line-buffered."""
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=1, env=_env(), creationflags=_FLAGS, **_COMMON)


def run(cmd: list[str], timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, timeout=timeout,
                          env=_env(), creationflags=_FLAGS, **_COMMON)


def open_path(path: str) -> None:
    """Open a folder or file in the OS file manager (best effort, never raises)."""
    try:
        if IS_WINDOWS:
            os.startfile(path)                                    # type: ignore[attr-defined]
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.Popen([opener, path], env=_env(), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
    except Exception:
        pass
