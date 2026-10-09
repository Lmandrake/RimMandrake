"""RimFlow Pulse — the floating always-on-top widget (Windows side). AWAY_DASHBOARD_BUILD_1.

Runs under the Windows Store Python's pythonw.exe with pywebview (WebView2). The page and
all data come from the WSL spine (rm-pulse.service, http://127.0.0.1:8765), so a page
change ships the moment the service sees it; this launcher only owns the window.

  - frameless, on top, created with focus=False and re-pinned with SWP_NOACTIVATE: it never
    takes focus on start or on update (owner complaint 2026-10-08 about focus stealing).
  - if the spine is unreachable it shows its own "monitor down" page and retries; after
    60 s it asks WSL to start rm-pulse.service (no console window), at most every 5 min.
  - toasts for new red / amber incidents are raised HERE with CREATE_NO_WINDOW, never from
    a WSL service (a service-launched powershell.exe steals focus — memwatch note).
  - probes RimWorldWin64.exe every 30 s and posts it to the spine.
Autostart: the 'RimFlow Pulse' scheduled task (install_autostart.ps1, logon + every 10 min).
Single instance, with a watchdog: a new launch that finds the mutex held checks whether the
holder's window still answers (SendMessageTimeout WM_NULL); a hung or windowless holder is
killed by PID and replaced, a healthy one is left alone (exit 0, no flicker). The running
widget also watches itself: GUI thread unanswering for 60 s -> dump all stacks to the log and
relaunch (at most 3 times an hour).

🔴 js_api objects must keep every non-API attribute UNDERSCORED. pywebview's get_functions()
walks every public attribute of js_api recursively on a worker thread; a public `window`
attribute led it into the WinForms form's .NET object graph and wedged the GUI thread
(widget 'Not Responding', 2026-10-08, measured with py-spy).
"""
import faulthandler
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from ctypes import wintypes

import webview

URL = "http://127.0.0.1:8765/"
APPDIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "RimFlowPulse")
os.makedirs(APPDIR, exist_ok=True)
STATE = os.path.join(APPDIR, "window.json")
TOASTED = os.path.join(APPDIR, "toasted.json")
LOG = os.path.join(APPDIR, "lantern.log")
NOWIN = 0x08000000  # CREATE_NO_WINDOW
WIDTH = 580
EXPANDED_H = 400
COLLAPSED_H = 41
ALLOWED_PREFIXES = ("D:\\Luke\\dev\\", "C:\\Users\\Mandrake\\", "\\\\wsl.localhost\\Ubuntu\\",
                    "https://github.com/Lmandrake/", "https://claude.ai/")

user32 = ctypes.windll.user32
dwm = ctypes.windll.dwmapi
# 64-bit handles: declare types, or ctypes truncates HMONITOR/HWND to a 32-bit int
user32.MonitorFromWindow.restype = ctypes.c_void_p
user32.MonitorFromWindow.argtypes = [ctypes.c_void_p, ctypes.c_uint]
user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
user32.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
user32.GetDpiForWindow.argtypes = [ctypes.c_void_p]
user32.SetThreadDpiAwarenessContext.restype = ctypes.c_void_p
user32.SetThreadDpiAwarenessContext.argtypes = [ctypes.c_void_p]


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def load(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    os.replace(tmp, path)


TITLE = "RimFlow Pulse"
PIDFILE = os.path.join(APPDIR, "lantern.pid")
RELAUNCHES = os.path.join(APPDIR, "relaunches.json")
k32 = ctypes.windll.kernel32
k32.CreateMutexW.restype = ctypes.c_void_p
k32.OpenProcess.restype = ctypes.c_void_p
k32.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
k32.CloseHandle.argtypes = [ctypes.c_void_p]
k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint]
user32.FindWindowW.restype = ctypes.c_void_p
user32.SendMessageTimeoutW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user32.EnumWindows.argtypes = [EnumProc, ctypes.c_void_p]
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]


def window_of_pid(pid):
    """The widget's top-level window owned by `pid` (enumerated, never via .NET)."""
    found = []

    def cb(h, _):
        p = wintypes.DWORD()
        user32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            buf = ctypes.create_unicode_buffer(64)
            user32.GetWindowTextW(h, buf, 64)
            if buf.value == TITLE:
                found.append(h)
                return False
        return True
    user32.EnumWindows(EnumProc(cb), None)
    return found[0] if found else None


def answers(hwnd, ms=3000):
    """True if the window's thread pumps messages within `ms` (what Windows calls Responding)."""
    res = ctypes.c_size_t()
    # WM_NULL, SMTO_ABORTIFHUNG|SMTO_BLOCK
    return bool(user32.SendMessageTimeoutW(hwnd, 0, None, None, 0x0002 | 0x0001, ms, ctypes.byref(res)))


k32.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_void_p]


def kill(pid):
    """Kill by PID, only if that PID is still a python process (a recycled PID is left alone)."""
    h = k32.OpenProcess(0x0001 | 0x00100000 | 0x1000, False, pid)  # TERMINATE|SYNCHRONIZE|QUERY_LIMITED
    if not h:
        return False
    try:
        buf, n = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
        k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n))
        if not os.path.basename(buf.value).lower().startswith("python"):
            log(f"watchdog: pid={pid} is {buf.value!r}, not python: not killing")
            return False
        k32.TerminateProcess(h, 7)
        k32.WaitForSingleObject(h, 5000)
        return True
    finally:
        k32.CloseHandle(h)


def take_mutex():
    h = k32.CreateMutexW(None, False, "Local\\RimFlowPulseLantern")
    return h, k32.GetLastError() == 183  # ERROR_ALREADY_EXISTS


def single_instance():
    """Hold the mutex; replace a hung or windowless holder; leave a healthy one alone."""
    h, taken = take_mutex()
    if not taken:
        return h
    info = load(PIDFILE, {})
    pid, started = info.get("pid"), info.get("t", 0)
    hwnd = window_of_pid(pid) if pid else None
    if not hwnd:  # no/stale pid file: find the holder by its window title
        h2 = user32.FindWindowW(None, TITLE)
        if h2:
            p = wintypes.DWORD()
            user32.GetWindowThreadProcessId(h2, ctypes.byref(p))
            if p.value != pid:
                pid, hwnd, started = p.value, h2, 0
    if hwnd and answers(hwnd):
        sys.exit(0)  # healthy: the 10-minute task re-run is a no-op
    if not hwnd and time.time() - started < 90:
        log(f"holder pid={pid} has no window yet ({int(time.time() - started)} s old): leaving it")
        sys.exit(0)
    log(f"watchdog: holder pid={pid} {'is NOT RESPONDING' if hwnd else 'has no window'}: killing it")
    k32.CloseHandle(h)
    if pid:
        kill(pid)
    for _ in range(20):
        h, taken = take_mutex()
        if not taken:
            return h
        k32.CloseHandle(h)
        time.sleep(0.5)
    log("watchdog: mutex still held after kill; giving up this run")
    sys.exit(0)


def relaunch_self(reason):
    """Hung GUI thread: dump stacks, start a fresh copy, die. Capped at 3 an hour (no flicker loops)."""
    now = time.time()
    recent = [t for t in load(RELAUNCHES, []) if now - t < 3600]
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + f"self-watchdog: {reason}; stacks:\n")
            faulthandler.dump_traceback(file=fh, all_threads=True)
    except OSError:
        pass
    if len(recent) < 3:
        save(RELAUNCHES, recent + [now])
        log("self-watchdog: relaunching")
        subprocess.Popen([sys.executable, os.path.abspath(__file__)], creationflags=0x00000008 | 0x00000200,
                         close_fds=True)  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        log("self-watchdog: 3 relaunches this hour; exiting and leaving it to the scheduled task")
    os._exit(3)


FALLBACK = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:#140e0a;color:#b89c7c;font:12.5px/1.6 'IBM Plex Mono',Consolas,monospace;overflow:hidden}
#a{height:100%;border:1px solid #4a3524;border-radius:10px;display:flex;flex-direction:column}
.s{height:3px;background:#5e4a3a}.b{flex:1;padding:12px 14px}.r{color:#ff6a4a}
.t{display:flex;justify-content:space-between;height:36px;align-items:center;padding:0 14px;background:#1d140e;border-top:1px solid #4a3524}
.p{background:#3a2a20;color:#ff6a4a;padding:1px 9px;border-radius:9px;box-shadow:inset 0 0 0 1px #d2462e88}
</style></head><body><div id="a"><div class="s"></div><div class="b pywebview-drag-region">
<div class="r">✖ The WSL monitor is not answering on 127.0.0.1:8765.</div>
<div>Retrying every 5 s. After a minute this window asks WSL to start rm-pulse.service.</div>
<div id="n" style="color:#5e4a3a"></div></div>
<div class="t pywebview-drag-region"><span class="p">✖ monitor down</span><span id="c" style="color:#8a705a"></span></div></div>
<script>let n=0;setInterval(async()=>{n++;document.getElementById('c').textContent=new Date().toTimeString().slice(0,8);
document.getElementById('n').textContent='attempt '+n;try{const r=await fetch('http://127.0.0.1:8765/api/now',{cache:'no-store'});
if(r.ok)location.href='http://127.0.0.1:8765/';}catch(e){}},5000);</script></body></html>"""


class Api:
    # 🔴 every non-API attribute is _underscored: pywebview walks public attributes recursively
    def __init__(self):
        self._window = None
        self._toasted = load(TOASTED, {})
        self._lock = threading.Lock()

    def open(self, target):
        target = str(target or "")
        if not target.startswith(ALLOWED_PREFIXES):
            log(f"refused open: {target!r}")
            return False
        try:
            if target.startswith("http"):
                import webbrowser
                webbrowser.open(target)
            elif os.path.isdir(target):
                os.startfile(target)
            elif os.path.exists(target):
                subprocess.Popen(["explorer.exe", "/select,", target], creationflags=NOWIN)
            else:
                parent = os.path.dirname(target)
                if os.path.isdir(parent):
                    os.startfile(parent)
            return True
        except OSError as e:
            log(f"open failed {target}: {e}")
            return False

    def toast(self, key, title, body):
        with self._lock:
            if key in self._toasted:
                return False
            self._toasted[key] = time.time()
            cutoff = time.time() - 7 * 86400
            self._toasted = {k: v for k, v in self._toasted.items() if v > cutoff}
            save(TOASTED, self._toasted)
        threading.Thread(target=raise_toast, args=(str(title), str(body)), daemon=True).start()
        try:
            post("/api/metric", {"m": "toast", "key": str(key)})
        except Exception:
            pass
        return True

    def set_collapsed(self, collapsed):
        """The ONLY resize: his click on collapse/expand. Data updates never move or resize it."""
        hwnd = window_of_pid(os.getpid())
        st = load(STATE, {})
        st["collapsed"] = bool(collapsed)
        save(STATE, st)
        if hwnd:
            try:
                set_size(hwnd, WIDTH, COLLAPSED_H if collapsed else EXPANDED_H)
            except Exception as e:
                log(f"resize failed: {e}")


def raise_toast(title, body):
    def q(s):
        return (s.replace("&", "and").replace("<", "(").replace(">", ")")
                 .replace("'", "''").replace('"', "'"))[:220]
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;"
        "[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]|Out-Null;"
        "$x=New-Object Windows.Data.Xml.Dom.XmlDocument;"
        f"$x.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>{q(title)}</text><text>{q(body)}</text></binding></visual></toast>');"
        "$app='{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe';"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($x))"
    )
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps],
                       creationflags=NOWIN, capture_output=True, timeout=30)
    except Exception as e:
        log(f"toast failed: {e}")


def post(path, obj):
    req = urllib.request.Request(URL.rstrip("/") + path, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=4).read()


def alive():
    try:
        urllib.request.urlopen(URL + "api/now", timeout=3).read(64)
        return True
    except Exception:
        return False


HWND_TOPMOST = ctypes.c_void_p(-1)


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", ctypes.c_ulong)]


def physical():
    """All geometry in PHYSICAL pixels, whatever thread we are on (per-monitor v2)."""
    try:
        user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        pass


def scale(hwnd):
    try:
        return max(1.0, user32.GetDpiForWindow(hwnd) / 96.0)
    except Exception:
        return 1.0


def rect(hwnd):
    physical()
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r


def work(hwnd):
    physical()
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(user32.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
    return mi.rcWork


def set_size(hwnd, w_log, h_log):
    sc = scale(hwnd)
    r, wa = rect(hwnd), work(hwnd)
    w, h = int(w_log * sc), int(h_log * sc)
    x, y = r.left, r.top
    if y + h > wa.bottom:          # grew past the bottom of the screen: slide up, never off-screen
        y = max(wa.top, wa.bottom - h)
    # SWP_NOACTIVATE|SWP_NOOWNERZORDER, HWND_TOPMOST
    user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, w, h, 0x0010 | 0x0200 | 0x4000)  # +SWP_ASYNCWINDOWPOS


def place_initial(hwnd):
    st = load(STATE, {})
    wa, r = work(hwnd), rect(hwnd)
    w, h = r.right - r.left, r.bottom - r.top
    x, y = st.get("px"), st.get("py")
    if x is not None and wa.left - w // 2 < x < wa.right - 40 and wa.top <= y < wa.bottom - 40:
        if abs(r.left - x) <= 4 and abs(r.top - y) <= 4:
            log(f"restored at {r.left},{r.top} (size {w}x{h})")
            return                     # created where he left it: do not touch it
    else:
        x, y = wa.right - w - 24, wa.bottom - h - 24
    user32.SetWindowPos(hwnd, HWND_TOPMOST, int(x), int(y), 0, 0, 0x0001 | 0x0010 | 0x0200 | 0x4000)
    log(f"placed at {x},{y} (work area {wa.left},{wa.top},{wa.right},{wa.bottom}, size {w}x{h})")


def remember(hwnd):
    r = rect(hwnd)
    st = load(STATE, {})
    sc = scale(hwnd)
    if (st.get("px"), st.get("py"), st.get("scale")) != (r.left, r.top, sc):
        st.update({"px": r.left, "py": r.top, "scale": sc})
        save(STATE, st)


def pin(hwnd):
    # HWND_TOPMOST, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE|SWP_NOOWNERZORDER
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010 | 0x0200 | 0x4000)


def round_corners(hwnd):
    pref = ctypes.c_int(2)  # DWMWCP_ROUND
    dwm.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))


def background(window):
    """Worker thread. Touches the window only through Win32 (async SetWindowPos, SendMessageTimeout),
    never through pywebview/.NET properties, so it can neither block nor be blocked by the GUI thread."""
    log("stage: background thread up")
    hwnd = None
    t0 = time.time()
    down_since = None
    last_heal = 0
    last_probe = 0
    hung_since = None
    loaded_logged = False
    while True:
        try:
            if not hwnd:
                hwnd = window_of_pid(os.getpid())
                if hwnd:
                    log(f"stage: window hwnd={hwnd} after {time.time() - t0:.1f} s")
                    round_corners(hwnd)
                    place_initial(hwnd)
                elif time.time() - t0 > 90:
                    relaunch_self("no window after 90 s")
            if hwnd:
                if answers(hwnd, 2000):
                    if hung_since:
                        log(f"GUI thread answering again after {time.time() - hung_since:.0f} s")
                    hung_since = None
                else:
                    hung_since = hung_since or time.time()
                    log(f"GUI thread not answering ({time.time() - hung_since:.0f} s)")
                    if time.time() - hung_since > 60:
                        relaunch_self("GUI thread not answering for 60 s")
                if not loaded_logged and window.events.loaded.is_set():
                    loaded_logged = True
                    log(f"stage: page loaded + js api ready after {time.time() - t0:.1f} s")
                pin(hwnd)
                remember(hwnd)  # games and fullscreen apps drop topmost; re-pin without activating
            ok = alive()
            now = time.time()
            if ok:
                if down_since:
                    log("spine back")
                    if hung_since is None and (window.get_current_url() in (None, "", "about:blank") or "127.0.0.1" not in (window.get_current_url() or "")):
                        window.load_url(URL)
                down_since = None
                if now - last_probe > 30:
                    last_probe = now
                    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq RimWorldWin64.exe", "/NH"],
                                       capture_output=True, text=True, creationflags=NOWIN, timeout=15)
                    post("/api/probe", {"rimworld_running": "RimWorldWin64.exe" in (r.stdout or ""),
                                        "host": os.environ.get("COMPUTERNAME", "")})
            else:
                down_since = down_since or now
                if now - down_since > 60 and now - last_heal > 300:
                    last_heal = now
                    log("spine down >60 s: asking WSL to start rm-pulse.service")
                    subprocess.Popen(["wsl.exe", "-d", "Ubuntu", "--", "systemctl", "--user", "start",
                                      "rm-pulse.service"], creationflags=NOWIN,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            log(f"background: {type(e).__name__}: {e}")
        time.sleep(5)


def main():
    log(f"stage: launch pid={os.getpid()} exe={sys.executable}")
    _mutex = single_instance()  # noqa: F841 (held for the process lifetime)
    save(PIDFILE, {"pid": os.getpid(), "t": time.time()})
    try:
        faulthandler.enable(open(os.path.join(APPDIR, "crash.log"), "a", encoding="utf-8"), all_threads=True)
    except OSError:
        pass
    api = Api()
    st = load(STATE, {})
    h0 = COLLAPSED_H if st.get("collapsed") else EXPANDED_H
    sc = float(st.get("scale") or 1.0)
    pos = {}
    if st.get("px") is not None:   # restore where he left it, in the units pywebview takes (logical)
        pos = {"x": int(st["px"] / sc), "y": int(st["py"] / sc)}
    kw = dict(width=WIDTH, height=h0, **pos, frameless=True, easy_drag=False, on_top=True,
              focus=False, resizable=False, background_color="#140e0a", shadow=True, js_api=api)
    if alive():
        win = webview.create_window("RimFlow Pulse", URL, **kw)
    else:
        win = webview.create_window("RimFlow Pulse", html=FALLBACK, **kw)
    api._window = win

    log(f"stage: mutex held, window created (pos={pos or 'default'}, h={h0}); starting GUI loop")
    webview.start(background, (win,), private_mode=False,
                  storage_path=os.path.join(APPDIR, "webview"))


if __name__ == "__main__":
    main()
