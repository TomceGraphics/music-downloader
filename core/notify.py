"""Best-effort desktop notifications: notify-send on Linux, a PowerShell toast on Windows.
Never raises. Plain Python (no tkinter)."""
import shutil

from . import proc
from .paths import IS_WINDOWS, resource_dir
from .version import APP_NAME

# Uses PowerShell's own AppUserModelID so the toast is allowed without registering one.
_TOAST = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$x = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$t = $x.GetElementsByTagName('text')
$t.Item(0).AppendChild($x.CreateTextNode('__TITLE__')) | Out-Null
$t.Item(1).AppendChild($x.CreateTextNode('__BODY__')) | Out-Null
$n = [Windows.UI.Notifications.ToastNotification]::new($x)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe').Show($n)
"""


def send(title: str, body: str) -> None:
    try:
        if IS_WINDOWS:
            script = _TOAST.replace("__TITLE__", title.replace("'", "''")).replace("__BODY__", body.replace("'", "''"))
            proc.run(["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
                      "-Command", script], timeout=20)
        elif shutil.which("notify-send"):
            icon = resource_dir() / "assets" / "icon.png"
            proc.run(["notify-send", "-a", APP_NAME, "-i", str(icon), title, body], timeout=8)
    except Exception:
        pass
