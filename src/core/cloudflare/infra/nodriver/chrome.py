import os
import sys

def get_posix_candidates() -> list[str]:
    posix_candidates = [
        os.path.join(path, subitem)
        for path in os.environ.get("PATH", "").split(os.pathsep)
        for subitem in (
            "google-chrome",
            "chromium",
            "chromium-browser",
            "chrome",
            "google-chrome-stable",
        )
    ]
    if "darwin" in sys.platform:
        posix_candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    return posix_candidates

def get_windows_candidates() -> list[str]:
    windows_candidates = []
    for item in map(
        os.environ.get,
        ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "PROGRAMW6432"),
    ):
        if item:
            for subitem in (
                "Google/Chrome/Application",
                "Google/Chrome Beta/Application",
                "Google/Chrome Canary/Application",
            ):
                windows_candidates.append(os.path.join(item, subitem, "chrome.exe"))
    return windows_candidates

def find_chrome_executable() -> str | None:
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        is_posix = sys.platform.startswith(("darwin", "cygwin", "linux", "linux2"))
    else:
        is_posix = os.name == 'posix'

    candidates = get_posix_candidates() if is_posix else get_windows_candidates()

    valid_candidates = [c for c in candidates if os.path.exists(c) and os.access(c, os.X_OK)]
    
    if valid_candidates:
        return os.path.normpath(min(valid_candidates, key=len))

    return None
