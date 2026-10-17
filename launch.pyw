"""Weyland-Yutani boot animation launcher for DeepSeek Harness.

Plays an 8-second CRT boot sequence full screen, then hands off to the app.
Nothing inside the DeepSeek Harness install directory is touched.

  config.json            (optional -- everything has a working default)
    app            full path to the program to launch; ~ and %VARS% are
                   expanded, and if it is missing we search the usual
                   install locations instead
    duration_ms    length of the animation; must match splash/splash.css
    warm_start_ms  when to pre-launch the app so it is already up when the
                   animation ends; null to launch only after it finishes
    emblem         "circle" (the ring and monogram) or "corp" (the corporate
                   wedge); both ship in the markup, this picks one

Any failure -- missing WebView2, a broken config, an error in the page --
falls through to launching the app immediately, so the shortcut never
dead-ends.
"""

import json
import os
import pathlib
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SPLASH = os.path.join(HERE, "splash", "index.html")
CONFIG = os.path.join(HERE, "config.json")

# where DeepSeek Harness usually ends up; first hit wins
APP_CANDIDATES = (
    r"C:\deepseek harness\DeepSeek Harness.exe",
    r"~\deepseek harness\DeepSeek Harness.exe",
    r"%LOCALAPPDATA%\Programs\DeepSeek Harness\DeepSeek Harness.exe",
    r"%LOCALAPPDATA%\DeepSeek Harness\DeepSeek Harness.exe",
    r"%ProgramFiles%\DeepSeek Harness\DeepSeek Harness.exe",
    r"%ProgramFiles%\DeepSeek\DeepSeek Harness\DeepSeek Harness.exe",
    r"%ProgramFiles(x86)%\DeepSeek Harness\DeepSeek Harness.exe",
    r"%ProgramFiles(x86)%\DeepSeek\DeepSeek Harness\DeepSeek Harness.exe",
)

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

# seconds to keep waiting past the animation before giving up on the page
GRACE = 6.0

_lock = threading.Lock()
_state = {"app_launched": False, "window": None}


def resolve_app(configured):
    """Config first, then the usual install locations.

    `~` and %VARS% are expanded so the config file can stay machine
    independent instead of hard-coding one absolute path.
    """
    if configured:
        path = os.path.expanduser(os.path.expandvars(str(configured).strip()))
        if os.path.isfile(path):
            return path
    for candidate in APP_CANDIDATES:
        path = os.path.expanduser(os.path.expandvars(candidate))
        if os.path.isfile(path):
            return path
    return ""


def load_config():
    cfg = {}
    try:
        with open(CONFIG, "r", encoding="utf-8") as fh:
            cfg = json.load(fh) or {}
    except Exception:
        pass
    cfg["app"] = resolve_app(cfg.get("app"))
    try:
        cfg["duration_ms"] = int(cfg.get("duration_ms") or 8000)
    except Exception:
        cfg["duration_ms"] = 8000
    if cfg.get("warm_start_ms") is not None:
        try:
            cfg["warm_start_ms"] = int(cfg["warm_start_ms"])
        except Exception:
            cfg["warm_start_ms"] = None
    emblem = str(cfg.get("emblem") or "rotate").strip().lower()
    cfg["emblem"] = emblem if emblem in ("rotate", "circle", "corp") else "rotate"
    return cfg


def resolve_emblem(mode):
    """The emblem this launch shows.

    A pinned value wins. "rotate" takes turns by the same five-minute bucket
    the plugins use -- two-way here, since this launcher has no rival intro
    to hand a third slot to.
    """
    if mode in ("circle", "corp"):
        return mode
    value = int(time.time() // 300) & 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 2246822507) & 0xFFFFFFFF
    value ^= value >> 13
    value = (value * 3266489909) & 0xFFFFFFFF
    value ^= value >> 16
    return "circle" if value % 2 else "corp"


def launch_app(target):
    """Start the app detached so it outlives this launcher."""
    with _lock:
        if _state["app_launched"]:
            return
        _state["app_launched"] = True
    if not os.path.isfile(target):
        return
    try:
        subprocess.Popen(
            [target],
            cwd=os.path.dirname(target),
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
    except Exception:
        pass


def close_window():
    win = _state.get("window")
    if win is None:
        return
    try:
        win.destroy()
    except Exception:
        pass


def run_splash(cfg):
    import webview

    # No query string here: pywebview percent-encodes the whole URL, so a "?"
    # arrives as part of the file name and the load fails with an error page.
    window = webview.create_window(
        "WEYLAND-YUTANI",
        url=pathlib.Path(SPLASH).as_uri(),
        fullscreen=True,
        frameless=True,
        easy_drag=False,
        on_top=True,
        background_color="#000000",
    )
    _state["window"] = window

    # The page starts on the markup's default emblem; swap it as soon as the
    # page answers, which is before the mark is revealed at ~1s.
    emblem = resolve_emblem(cfg.get("emblem", "rotate"))
    if emblem != "circle":
        def apply_emblem():
            deadline = time.time() + 5
            while time.time() < deadline:
                try:
                    if window.evaluate_js("typeof window.__setEmblem === 'function'"):
                        window.evaluate_js("window.__setEmblem(%r)" % emblem)
                        return
                except Exception:
                    pass
                time.sleep(0.03)
        threading.Thread(target=apply_emblem, daemon=True).start()

    # start the app before the tube dies, so it is up by the time the
    # animation ends; our window is topmost, so it stays covered.
    warm = cfg.get("warm_start_ms")
    if warm is not None:
        threading.Timer(warm / 1000.0, launch_app, (cfg["app"],)).start()

    def watch():
        """Wait for the page to report the sequence is over, then hand off.

        Polling a flag beats the js_api bridge here: there is no injection
        timing to get wrong, and a page that throws cannot hang the hand-off.
        The deadline is the failsafe.
        """
        deadline = time.time() + cfg["duration_ms"] / 1000.0 + GRACE
        while time.time() < deadline:
            try:
                if window.evaluate_js("window.__splashFinished === true"):
                    break
            except Exception:
                pass
            time.sleep(0.12)
        launch_app(cfg["app"])
        close_window()

    threading.Thread(target=watch, daemon=True).start()
    webview.start(gui="edgechromium", debug=False)


def main():
    cfg = load_config()
    if not os.path.isfile(SPLASH):
        launch_app(cfg["app"])
        return
    try:
        run_splash(cfg)
    except Exception:
        # WebView2 missing, pywebview absent, anything else: the animation
        # is a nicety, the app is the point.
        pass
    launch_app(cfg["app"])


if __name__ == "__main__":
    sys.exit(main())
