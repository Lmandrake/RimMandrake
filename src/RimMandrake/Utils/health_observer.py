"""health_observer.py - the standing EXTERNAL game-health collector (GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN).

Design and metrics ledger: design/RimMandrake/game_health_record.md. It injects no game code. It runs as one
long-lived Windows process (python.exe or pythonw.exe, stdlib + ctypes only) and appends its own ordered JSONL
stream beside the TPS record:

    <LocalLow>\\JawaBench\\health\\observer_<startUtc>_<collectorPid>_<seg>.jsonl     (outside git)
    <LocalLow>\\JawaBench\\health\\collector_last.json                                (last sample, atomic)
    <LocalLow>\\JawaBench\\health\\health_observer_settings.json                      (optional switches)

Every source has a stable id (SOURCES), its own on/off switch (settings file "sources": {id: false}, or
--off ID), and a measured cost on every row (costUs per probe, costMsTotal per source in the heartbeat,
and the collector's own CPU). A source that cannot be read says "unavailable" or "failed", never 0.

Run (Windows; cd to the repo first, python.exe misreads WSL absolute paths):
    python.exe src/RimMandrake/Utils/health_observer.py                 run until killed (one instance: lock)
    python.exe src/RimMandrake/Utils/health_observer.py --for 600       run ten minutes, print the cost line
    python.exe src/RimMandrake/Utils/health_observer.py --once --print  one sample, printed
Read (either OS):
    python3 src/RimMandrake/Utils/health_observer.py --read [--last N]
    python3 src/RimMandrake/Utils/tps_record.py --at "today 15:00" --health   joined to TPS incidents
Standing install (a scheduled task re-starts it every 5 min; the lock makes extra starts exit at once):
    schtasks.exe /Create /F /TN "RimMandrake\\Health Observer" /SC MINUTE /MO 5 /TR
      "\\"<pythonw.exe>\\" D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\Utils\\health_observer.py"
"""
import argparse
import hashlib
import json
import os
import socket
import sys
import time

SCHEMA = 1
SETTINGS_NAME = "health_observer_settings.json"
LOCK_NAME = "collector.lock"
LAST_NAME = "collector_last.json"
SEGMENT_BYTES = 4 << 20
RETENTION_DAYS = 14
RETENTION_CAP_BYTES = 256 << 20
LOG_READ_CAP = 1 << 20
FIRST_READ_CAP = 8 << 20
MB = 1024.0 * 1024.0

# Stable ids. Removing a metric = switch it off here (default) or in the settings file, then delete its probe.
SOURCES = {
    "obs.heartbeat": {"default": True, "question": "Was the observer itself running, on time, and what did it cost?"},
    "game.identity": {"default": True, "question": "Which RimWorld processes exist (pid + creation time), when did "
                                                   "each start and exit, with what exit code?"},
    "game.cpu": {"default": True, "question": "How many cores did the game process use (user+kernel, all threads)?"},
    "game.mainthread": {"default": True, "question": "How many cores did the (assumed) main thread use, and how "
                                                     "much did the other threads use?"},
    "game.memory": {"default": True, "question": "Game working set, peak working set, private bytes, pagefile use?"},
    "sys.memory": {"default": True, "question": "Is the machine short of physical memory or commit headroom?"},
    "log.growth": {"default": True, "question": "How fast is Player.log growing, and was it truncated or rotated?"},
    "log.milestones": {"default": True, "question": "When did startup landmarks appear, and did Verse.Log hit its "
                                                    "message cap (emission suppressed)?"},
}
ORDER = [k for k in SOURCES if k != "obs.heartbeat"]


class Unavailable(object):
    def __init__(self, reason):
        self.reason = reason


def utc(ep=None):
    ep = time.time() if ep is None else ep
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ep)) + ".%03dZ" % int((ep % 1) * 1000)


def epoch(s):
    import calendar
    base, _, frac = s.rstrip("Z").partition(".")
    return calendar.timegm(time.strptime(base, "%Y-%m-%dT%H:%M:%S")) + (float("0." + frac) if frac else 0.0)


def cores(prev, cur):
    """(cores, None) from two {ident, cpuS, mono} readings, or (None, reason). A different ident (same pid,
    different creation time) is a different process: no rate across it."""
    if prev is None:
        return None, "no-baseline"
    if prev["ident"] != cur["ident"]:
        return None, "identity-changed"
    dt = cur["mono"] - prev["mono"]
    if dt <= 0:
        return None, "clock"
    dc = cur["cpuS"] - prev["cpuS"]
    if dc < 0:
        return None, "counter-went-back"
    return round(dc / dt, 4), None


def pick_main_thread(threads):
    """[(tid, creation)] -> (tid, rule). Unity's player loop runs on the process's initial thread, so the
    earliest-created thread is TAKEN as the main thread. That is an assumption, not a measurement from inside."""
    if not threads:
        return None, "no threads"
    tid = min(threads, key=lambda t: (t[1], t[0]))[0]
    return tid, "earliest-created thread (assumed main thread; not verified from inside the game)"


# ------------------------------------------------------------------ single instance

def acquire_lock(directory):
    os.makedirs(directory, exist_ok=True)
    fh = open(os.path.join(directory, LOCK_NAME), "a+")
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fh
    except OSError:
        fh.close()
        return None


def release_lock(fh):
    if fh is None:
        return
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    fh.close()


# ------------------------------------------------------------------ Player.log tail

_K32 = {}


def _open_shared(path):
    """Read handle that never blocks Unity renaming/deleting the log (FILE_SHARE_DELETE on Windows)."""
    if os.name != "nt":
        return open(path, "rb")
    import ctypes
    import msvcrt
    from ctypes import wintypes as W
    k32 = _K32.get("k")
    if k32 is None:                      # bound once: re-binding ctypes on every poll cost ~6 ms (measured)
        k32 = _K32["k"] = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateFileW.restype = W.HANDLE
        k32.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
    h = k32.CreateFileW(path, 0x80000000, 0x7, None, 3, 0x80, None)   # GENERIC_READ, share R|W|D, OPEN_EXISTING
    if h is None or h == W.HANDLE(-1).value:
        err = ctypes.get_last_error()
        if err in (2, 3):
            raise FileNotFoundError(path)
        raise OSError(err, "CreateFileW failed", path)
    fd = msvcrt.open_osfhandle(h, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    return os.fdopen(fd, "rb")


class LogTail(object):
    """Incremental tail. Each poll opens, fstats, reads at most read_cap new bytes, closes. Identity is the
    file id (st_dev, st_ino) of the OPEN handle, so a stat/open race cannot mix two files."""

    def __init__(self, path, read_cap=LOG_READ_CAP, first_read_cap=FIRST_READ_CAP):
        self.path, self.read_cap, self.first_read_cap = path, read_cap, first_read_cap
        self.ident, self.offset, self.size_last, self.mono_last = None, 0, None, None

    def poll(self, mono):
        out = {"missing": False, "rotated": False, "truncated": False, "grewBytes": None, "bytesPerS": None,
               "newBytes": 0, "skippedBytes": 0, "size": None, "data": b"", "dataOffset": None}
        try:
            fh = _open_shared(self.path)
        except FileNotFoundError:
            out["missing"] = True
            if self.ident is not None:
                self.ident = ("gone",)
            self.size_last, self.mono_last = None, mono
            return out
        try:
            st = os.fstat(fh.fileno())
            ident, size = (st.st_dev, st.st_ino), st.st_size
            out["size"] = size
            if self.ident is None:
                out["firstSight"] = True                              # baseline, no rate; content predates us
            elif ident != self.ident:
                out["rotated"], self.offset = True, 0
            elif size < self.offset:
                out["truncated"], self.offset = True, 0
            elif self.size_last is not None:
                out["grewBytes"] = size - self.size_last
                dt = mono - self.mono_last if self.mono_last is not None else 0
                if dt > 0:
                    out["bytesPerS"] = round(out["grewBytes"] / dt, 1)
            pending = size - self.offset
            if pending > 0:
                fh.seek(self.offset)
                # a new file (first sight or rotation) is read further, once, so startup landmarks are found
                n = min(pending, self.first_read_cap if self.offset == 0 else self.read_cap)
                out["data"], out["dataOffset"] = fh.read(n), self.offset
                out["newBytes"] = len(out["data"])
                out["skippedBytes"] = pending - out["newBytes"]
            self.offset = size
            self.ident, self.size_last, self.mono_last = ident, size, mono
        finally:
            fh.close()
        return out


class Milestones(object):
    CARRY_MAX = 64 * 1024
    PATTERNS = [  # (id, needle, starts-line, once, meaning)
        ("engine.mono", b"Mono path[0]", True, True, "Unity/Mono runtime up (first log line of a launch)"),
        ("engine.init", b"Initialize engine version:", True, True, "Unity engine initialising"),
        ("game.version", b"RimWorld ", True, True, "RimWorld version line"),
        ("rimbridge.startup", b"[RimBridge] STARTUP_TIMING", True, True, "RimBridge began its startup"),
        ("jawabench.ready", b"[JawaBench] ready:", True, True, "JawaBench companion registered its tools"),
        ("bridge.token", b"[RimBridge] Bridge token:", True, True, "bridge listening"),
        ("unity.memstats", b"Memory Statistics:", True, True, "Unity printed shutdown memory statistics"),
        ("log.cap-reached", b"Reached max messages limit", False, False,
         "Verse.Log hit its 10,000-message cap: emission suppressed; error activity unknown until "
         "Log.ResetMessageCount"),
        ("log.cap-lifted", b"Message logging is now once again on.", False, False,
         "Verse.Log message count reset: emission resumed"),
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        self.seen, self.carry, self.dropped = set(), b"", 0

    def skip(self):
        self.carry = b""

    def feed(self, data, offset):
        buf = self.carry + data
        base = offset - len(self.carry)
        parts = buf.split(b"\n")
        self.carry = parts.pop()
        if len(self.carry) > self.CARRY_MAX:
            self.carry, self.dropped = b"", self.dropped + 1
        out, pos = [], base
        for line in parts:
            s = line.rstrip(b"\r")
            for mid, needle, starts, once, meaning in self.PATTERNS:
                if once and mid in self.seen:
                    continue
                hit = s.startswith(needle) if starts else needle in s
                if hit and mid == "game.version":
                    import re
                    hit = re.match(rb"^RimWorld \d+\.\d+\.\d+ rev\d+$", s) is not None
                if hit:
                    self.seen.add(mid)
                    out.append({"id": mid, "offset": pos, "line": s[:160].decode("utf-8", "replace"),
                                "meaning": meaning})
            pos += len(line) + 1
        return out


# ------------------------------------------------------------------ Windows probes (ctypes)

class Win(object):
    """Thin ctypes layer. Handles are HELD per game process: a held process handle also stops Windows
    recycling that pid while we watch it, and lets us read the exit code after it ends."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes as W
        self.c, self.W = ctypes, W
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        self.k = k
        H, D, P = W.HANDLE, W.DWORD, ctypes.POINTER

        class FT(ctypes.Structure):
            _fields_ = [("lo", D), ("hi", D)]

        class PE(ctypes.Structure):
            _fields_ = [("dwSize", D), ("cntUsage", D), ("th32ProcessID", D), ("th32DefaultHeapID", ctypes.c_size_t),
                        ("th32ModuleID", D), ("cntThreads", D), ("th32ParentProcessID", D),
                        ("pcPriClassBase", ctypes.c_long), ("dwFlags", D), ("szExeFile", ctypes.c_wchar * 260)]

        class TE(ctypes.Structure):
            _fields_ = [("dwSize", D), ("cntUsage", D), ("th32ThreadID", D), ("th32OwnerProcessID", D),
                        ("tpBasePri", ctypes.c_long), ("tpDeltaPri", ctypes.c_long), ("dwFlags", D)]
        S = ctypes.c_size_t

        class PMC(ctypes.Structure):
            _fields_ = [("cb", D), ("PageFaultCount", D), ("PeakWorkingSetSize", S), ("WorkingSetSize", S),
                        ("QuotaPeakPagedPoolUsage", S), ("QuotaPagedPoolUsage", S), ("QuotaPeakNonPagedPoolUsage", S),
                        ("QuotaNonPagedPoolUsage", S), ("PagefileUsage", S), ("PeakPagefileUsage", S),
                        ("PrivateUsage", S)]
        U = ctypes.c_ulonglong

        class MSX(ctypes.Structure):
            _fields_ = [("dwLength", D), ("dwMemoryLoad", D), ("ullTotalPhys", U), ("ullAvailPhys", U),
                        ("ullTotalPageFile", U), ("ullAvailPageFile", U), ("ullTotalVirtual", U),
                        ("ullAvailVirtual", U), ("ullAvailExtendedVirtual", U)]

        class PI(ctypes.Structure):
            _fields_ = [("cb", D), ("CommitTotal", S), ("CommitLimit", S), ("CommitPeak", S), ("PhysicalTotal", S),
                        ("PhysicalAvailable", S), ("SystemCache", S), ("KernelTotal", S), ("KernelPaged", S),
                        ("KernelNonpaged", S), ("PageSize", S), ("HandleCount", D), ("ProcessCount", D),
                        ("ThreadCount", D)]
        self.FT, self.PE, self.TE, self.PMC, self.MSX, self.PI = FT, PE, TE, PMC, MSX, PI
        k.CreateToolhelp32Snapshot.restype, k.CreateToolhelp32Snapshot.argtypes = H, [D, D]
        k.Process32FirstW.argtypes = k.Process32NextW.argtypes = [H, P(PE)]
        k.Thread32First.argtypes = k.Thread32Next.argtypes = [H, P(TE)]
        k.OpenProcess.restype, k.OpenProcess.argtypes = H, [D, W.BOOL, D]
        k.OpenThread.restype, k.OpenThread.argtypes = H, [D, W.BOOL, D]
        k.CloseHandle.argtypes = [H]
        k.GetProcessTimes.argtypes = [H, P(FT), P(FT), P(FT), P(FT)]
        k.GetThreadTimes.argtypes = [H, P(FT), P(FT), P(FT), P(FT)]
        k.WaitForSingleObject.restype, k.WaitForSingleObject.argtypes = D, [H, D]
        k.GetExitCodeProcess.argtypes = k.GetExitCodeThread.argtypes = [H, P(D)]
        k.K32GetProcessMemoryInfo.argtypes = [H, ctypes.c_void_p, D]
        k.GlobalMemoryStatusEx.argtypes = [P(MSX)]
        k.K32GetPerformanceInfo.argtypes = [P(PI), D]

    @staticmethod
    def ft(f):
        return (f.hi << 32) | f.lo

    def _bad(self, h):
        return not h or h == self.W.HANDLE(-1).value

    def processes(self, exe="rimworldwin64.exe"):
        snap = self.k.CreateToolhelp32Snapshot(0x2, 0)
        if self._bad(snap):
            raise OSError(self.c.get_last_error(), "process snapshot failed")
        out = []
        try:
            e = self.PE()
            e.dwSize = self.c.sizeof(self.PE)
            ok = self.k.Process32FirstW(snap, self.c.byref(e))
            while ok:
                if e.szExeFile.lower() == exe:
                    out.append((int(e.th32ProcessID), int(e.cntThreads)))
                ok = self.k.Process32NextW(snap, self.c.byref(e))
        finally:
            self.k.CloseHandle(snap)
        return out

    def open_process(self, pid):
        h = self.k.OpenProcess(0x1000 | 0x0010 | 0x00100000, False, pid)   # QUERY_LIMITED | VM_READ | SYNCHRONIZE
        if self._bad(h):
            h = self.k.OpenProcess(0x1000 | 0x00100000, False, pid)
        return None if self._bad(h) else h

    def times(self, h, thread=False):
        """(creation FILETIME int, cpu seconds user+kernel) or None."""
        a, b, kt, ut = self.FT(), self.FT(), self.FT(), self.FT()
        fn = self.k.GetThreadTimes if thread else self.k.GetProcessTimes
        if not fn(h, self.c.byref(a), self.c.byref(b), self.c.byref(kt), self.c.byref(ut)):
            return None
        return self.ft(a), (self.ft(kt) + self.ft(ut)) / 1e7

    def exited(self, h):
        """None while running, else the exit code."""
        if self.k.WaitForSingleObject(h, 0) != 0:
            return None
        code = self.W.DWORD()
        self.k.GetExitCodeProcess(h, self.c.byref(code))
        return int(code.value)

    def thread_alive(self, h):
        code = self.W.DWORD()
        return bool(self.k.GetExitCodeThread(h, self.c.byref(code))) and code.value == 259

    def threads(self, pid):
        snap = self.k.CreateToolhelp32Snapshot(0x4, 0)
        if self._bad(snap):
            raise OSError(self.c.get_last_error(), "thread snapshot failed")
        out = []
        try:
            e = self.TE()
            e.dwSize = self.c.sizeof(self.TE)
            ok = self.k.Thread32First(snap, self.c.byref(e))
            while ok:
                if e.th32OwnerProcessID == pid:
                    out.append(int(e.th32ThreadID))
                ok = self.k.Thread32Next(snap, self.c.byref(e))
        finally:
            self.k.CloseHandle(snap)
        return out

    def open_thread(self, tid):
        h = self.k.OpenThread(0x0800, False, tid)                           # THREAD_QUERY_LIMITED_INFORMATION
        return None if self._bad(h) else h

    def close(self, h):
        if h:
            self.k.CloseHandle(h)

    def memory(self, h):
        m = self.PMC()
        m.cb = self.c.sizeof(self.PMC)
        if not self.k.K32GetProcessMemoryInfo(h, self.c.byref(m), m.cb):
            return None
        return m

    def system(self):
        m = self.MSX()
        m.dwLength = self.c.sizeof(self.MSX)
        if not self.k.GlobalMemoryStatusEx(self.c.byref(m)):
            raise OSError(self.c.get_last_error(), "GlobalMemoryStatusEx failed")
        p = self.PI()
        p.cb = self.c.sizeof(self.PI)
        perf = p if self.k.K32GetPerformanceInfo(self.c.byref(p), p.cb) else None
        return m, perf


def _ftutc(ft):
    return utc(ft / 1e7 - 11644473600.0)


class Ctx(object):
    def __init__(self, interval):
        self.games = {}          # (pid, creationFT) -> state
        self.events = []
        self.log = None
        self.interval = interval


def default_probes(log_path):
    win = None
    if os.name == "nt":
        try:
            win = Win()
        except Exception:                                       # noqa: BLE001
            win = None
    tail = LogTail(log_path) if log_path else None
    ms = Milestones()
    no_win = Unavailable("Windows API not available on this host (run under python.exe on Windows)")

    def identity(ctx):
        if win is None:
            return no_win
        seen = win.processes()
        live = set()
        for pid, nthreads in seen:
            known = [k for k in ctx.games if k[0] == pid]
            if known:
                live.add(known[0])
                ctx.games[known[0]]["threads"] = nthreads
                continue
            h = win.open_process(pid)
            t = win.times(h) if h else None
            if not t:
                win.close(h)
                ctx.events.append({"event": "game-unopenable", "pid": pid})
                continue
            key = (pid, t[0])
            ctx.games[key] = {"h": h, "pid": pid, "startUtc": _ftutc(t[0]), "threads": nthreads}
            live.add(key)
            ctx.events.append({"event": "game-start", "pid": pid, "startUtc": _ftutc(t[0])})
        for key in list(ctx.games):
            g = ctx.games[key]
            code = win.exited(g["h"])
            if code is not None:
                ctx.events.append({"event": "game-exit", "pid": g["pid"], "startUtc": g["startUtc"],
                                   "exitCode": code, "observedWithinS": ctx.interval})
                win.close(g["h"])
                win.close(g.get("mainH"))
                del ctx.games[key]
        return {"procs": [{"pid": g["pid"], "startUtc": g["startUtc"], "threads": g.get("threads")}
                          for g in ctx.games.values()]}

    def cpu(ctx):
        if win is None:
            return no_win
        out = []
        for key, g in ctx.games.items():
            t = win.times(g["h"])
            if not t:
                out.append({"pid": g["pid"], "startUtc": g["startUtc"], "status": "failed"})
                g.pop("prevCpu", None)
                continue
            cur = {"ident": key, "cpuS": t[1], "mono": time.monotonic()}
            c, why = cores(g.get("prevCpu"), cur)
            g["prevCpu"], g["cores"] = cur, c
            out.append({"pid": g["pid"], "startUtc": g["startUtc"], "cpuS": round(t[1], 3), "cores": c,
                        "noRate": why})
        return {"procs": out}

    def mainthread(ctx):
        if win is None:
            return no_win
        out = []
        for key, g in ctx.games.items():
            if g.get("mainH") is None or not win.thread_alive(g["mainH"]):
                win.close(g.get("mainH"))
                g["mainH"], g["prevMain"] = None, None
                cand = []
                for tid in win.threads(g["pid"]):
                    th = win.open_thread(tid)
                    tt = win.times(th, thread=True) if th else None
                    win.close(th)
                    if tt:
                        cand.append((tid, tt[0]))
                tid, rule = pick_main_thread(cand)
                if tid is None:
                    out.append({"pid": g["pid"], "startUtc": g["startUtc"], "status": "unavailable",
                                "reason": "no thread readable"})
                    continue
                g["mainH"], g["mainTid"], g["mainRule"] = win.open_thread(tid), tid, rule
                ctx.events.append({"event": "main-thread-picked", "pid": g["pid"], "tid": tid, "rule": rule,
                                   "candidates": len(cand)})
            t = win.times(g["mainH"], thread=True) if g.get("mainH") else None
            if not t:
                out.append({"pid": g["pid"], "startUtc": g["startUtc"], "status": "failed"})
                g["prevMain"] = None
                continue
            cur = {"ident": (key, g["mainTid"], t[0]), "cpuS": t[1], "mono": time.monotonic()}
            c, why = cores(g.get("prevMain"), cur)
            g["prevMain"] = cur
            other = round(g["cores"] - c, 4) if c is not None and g.get("cores") is not None else None
            out.append({"pid": g["pid"], "startUtc": g["startUtc"], "tid": g["mainTid"], "cores": c, "noRate": why,
                        "otherThreadsCores": other, "rule": g["mainRule"]})
        return {"procs": out}

    def memory(ctx):
        if win is None:
            return no_win
        out = []
        for g in ctx.games.values():
            m = win.memory(g["h"])
            if m is None:
                out.append({"pid": g["pid"], "startUtc": g["startUtc"], "status": "failed"})
                continue
            out.append({"pid": g["pid"], "startUtc": g["startUtc"], "workingSetMB": round(m.WorkingSetSize / MB, 1),
                        "peakWorkingSetMB": round(m.PeakWorkingSetSize / MB, 1),
                        "privateMB": round(m.PrivateUsage / MB, 1)})
            # PagefileUsage is not reported: on current Windows it equals PrivateUsage (measured 2026-10-10), so it
            # would read as a second, independent number when it is not.
        return {"procs": out}

    def sysmem(ctx):
        if win is None:
            return no_win
        m, p = win.system()
        v = {"totalPhysMB": round(m.ullTotalPhys / MB), "availPhysMB": round(m.ullAvailPhys / MB),
             "memoryLoadPct": int(m.dwMemoryLoad)}
        if p is not None:
            ps = p.PageSize
            v.update({"commitTotalMB": round(p.CommitTotal * ps / MB), "commitLimitMB": round(p.CommitLimit * ps / MB),
                      "commitPeakMB": round(p.CommitPeak * ps / MB),
                      "commitHeadroomMB": round((p.CommitLimit - p.CommitTotal) * ps / MB)})
        else:
            v["commit"] = "unavailable"
        return v

    def growth(ctx):
        if tail is None:
            return Unavailable("no Player.log path")
        r = tail.poll(time.monotonic())
        ctx.log = r
        if r["rotated"]:
            ctx.events.append({"event": "log-rotated", "path": tail.path})
        if r["truncated"]:
            ctx.events.append({"event": "log-truncated", "path": tail.path})
        if r["skippedBytes"]:
            ctx.events.append({"event": "log-burst-skipped", "skippedBytes": r["skippedBytes"]})
        return {k: v for k, v in r.items() if k not in ("data", "dataOffset")}

    def milestones(ctx):
        r = ctx.log
        if r is None:
            return Unavailable("needs log.growth (switched off or failed)")
        ctx.log = None
        if r["rotated"] or r["truncated"]:
            ms.reset()
        found = ms.feed(r["data"], r["dataOffset"]) if r["data"] else []
        if r["skippedBytes"]:
            ms.skip()
        for f in found:
            if r.get("firstSight"):     # already in the log when the collector started: written at an unknown time
                ctx.events.append(dict(f, event="milestone", precisionS=None, timeUnknown="present at collector start"))
            else:
                ctx.events.append(dict(f, event="milestone", precisionS=ctx.interval))
        return {"seenThisLog": sorted(ms.seen), "new": [f["id"] for f in found], "carryDropped": ms.dropped}

    return {"game.identity": identity, "game.cpu": cpu, "game.mainthread": mainthread, "game.memory": memory,
            "sys.memory": sysmem, "log.growth": growth, "log.milestones": milestones}


# ------------------------------------------------------------------ collector

def _own_cpu():
    t = os.times()
    return t.user + t.system


def _version():
    try:
        with open(os.path.abspath(__file__), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:12]
    except OSError:
        return None


class Collector(object):
    def __init__(self, out_dir, probes=None, switches=None, interval=5.0, idle_interval=30.0,
                 segment_bytes=SEGMENT_BYTES, log_path=None):
        os.makedirs(out_dir, exist_ok=True)
        self.dir, self.interval, self.idle_interval, self.segment_bytes = out_dir, interval, idle_interval, segment_bytes
        settings, unknown = {}, []
        try:
            with open(os.path.join(out_dir, SETTINGS_NAME), encoding="utf-8") as f:
                settings = json.load(f)
        except (OSError, ValueError):
            settings = {}
        self.switch = {k: v["default"] for k, v in SOURCES.items()}
        for k, v in dict(settings.get("sources") or {}, **(switches or {})).items():
            if k not in SOURCES:
                unknown.append(k)
            elif k != "obs.heartbeat":
                self.switch[k] = bool(v)
        self.probes = probes if probes is not None else default_probes(log_path)
        self.ctx = Ctx(interval)
        t0 = time.time()
        self.ident = {"id": "%s-%d-%s" % (socket.gethostname(), os.getpid(), time.strftime("%Y%m%dT%H%M%SZ",
                                                                                          time.gmtime(t0))),
                      "pid": os.getpid(), "startUtc": utc(t0), "host": socket.gethostname(), "version": _version(),
                      "python": sys.executable}
        self.stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(t0))
        self.seq, self.seg, self.cur = 0, 0, None
        self.failed, self.cost_ms = {}, {}
        self.samples, self.late_count = 0, 0
        self.cpu0, self.mono0 = _own_cpu(), time.monotonic()
        self.last_mono, self.last_wall = None, None
        self.start_row = {"v": SCHEMA, "kind": "start", "utc": utc(t0), "switches": self.switch,
                          "unknownSettings": unknown, "interval": interval, "idleInterval": idle_interval,
                          "logPath": log_path, "collectorIdent": self.ident,
                          "sources": {k: v["question"] for k, v in SOURCES.items()}}
        self.write(self.start_row)

    def _segment(self, nbytes):
        if self.cur is None or (os.path.exists(self.cur) and os.path.getsize(self.cur) > 0
                                and os.path.getsize(self.cur) + nbytes > self.segment_bytes):
            self.seg += 1
            self.cur = os.path.join(self.dir, "observer_%s_%d_%03d.jsonl" % (self.stamp, os.getpid(), self.seg))
        return self.cur

    def write(self, row):
        row["seq"] = self.seq
        row["collector"] = {"id": self.ident["id"]}
        try:
            line = json.dumps(row, separators=(",", ":"), allow_nan=False) + "\n"
        except ValueError as e:
            line = json.dumps({"v": SCHEMA, "kind": "error", "utc": utc(), "seq": self.seq,
                               "collector": {"id": self.ident["id"]}, "error": "unserialisable row: %s" % e}) + "\n"
        data = line.encode("utf-8")
        with open(self._segment(len(data)), "ab") as f:
            f.write(data)
        self.seq += 1

    def sample(self):
        wall, mono = time.time(), time.monotonic()
        t_start = time.perf_counter()
        sources = {}
        for sid in ORDER:
            if not self.switch.get(sid):
                sources[sid] = {"status": "off"}
                continue
            p = self.probes.get(sid)
            if p is None:
                sources[sid] = {"status": "unavailable", "reason": "no probe for this source on this host"}
                continue
            t0 = time.perf_counter()
            try:
                v = p(self.ctx)
                cost = (time.perf_counter() - t0) * 1e6
                if v is None or isinstance(v, Unavailable):
                    sources[sid] = {"status": "unavailable", "reason": getattr(v, "reason", "no source")}
                else:
                    sources[sid] = {"status": "ok", "value": v}
            except Exception as e:                              # noqa: BLE001
                cost = (time.perf_counter() - t0) * 1e6
                self.failed[sid] = self.failed.get(sid, 0) + 1
                sources[sid] = {"status": "failed", "error": "%s: %s" % (type(e).__name__, str(e)[:200])}
            sources[sid]["costUs"] = round(cost, 1)
            self.cost_ms[sid] = self.cost_ms.get(sid, 0.0) + cost / 1000.0
        self.samples += 1
        hb = {"samples": self.samples, "failedProbes": dict(self.failed),
              "costMsTotal": {k: round(v, 3) for k, v in self.cost_ms.items()},
              "sampleMs": round((time.perf_counter() - t_start) * 1000, 3)}
        if self.last_mono is not None:
            gap = mono - self.last_mono
            due = self.interval if self.ctx.games else self.idle_interval
            hb["sinceLastS"] = round(gap, 3)
            hb["lateS"] = round(max(0.0, gap - due), 3)
            hb["wallMinusMonoS"] = round((wall - self.last_wall) - gap, 3)   # clock step or sleep accounting
            if gap > 3 * due:
                self.late_count += 1
        hb["missedDeadlines"] = self.late_count
        cpu = _own_cpu() - self.cpu0
        up = mono - self.mono0
        hb["collectorCpuS"] = round(cpu, 3)
        hb["collectorCores"] = round(cpu / up, 5) if up >= 30 else None   # os.times ticks ~15.6 ms on Windows
        self.last_mono, self.last_wall = mono, wall
        sources["obs.heartbeat"] = {"status": "ok", "value": hb}
        row = {"v": SCHEMA, "kind": "sample", "utc": utc(wall), "mono": round(mono, 3), "sources": sources}
        self.write(row)
        for ev in self.ctx.events:
            self.write(dict({"v": SCHEMA, "kind": "event", "utc": utc()}, **ev))
        self.ctx.events = []
        return row

    def publish_last(self, row):
        p = os.path.join(self.dir, LAST_NAME)
        try:
            with open(p + ".tmp", "w", encoding="utf-8") as f:
                json.dump(row, f)
            os.replace(p + ".tmp", p)
        except OSError:
            pass

    def stop(self, reason):
        cpu = _own_cpu() - self.cpu0
        up = time.monotonic() - self.mono0
        self.write({"v": SCHEMA, "kind": "stop", "utc": utc(), "reason": reason, "samples": self.samples,
                    "collectorCpuS": round(cpu, 3), "uptimeS": round(up, 1),
                    "collectorCores": round(cpu / up, 5) if up >= 30 else None,
                    "costMsTotal": {k: round(v, 3) for k, v in self.cost_ms.items()}})


def prune(directory, keep, now=None, days=RETENTION_DAYS, cap=RETENTION_CAP_BYTES):
    """Delete closed segments older than `days`, then oldest-first while over `cap`. Never `keep`."""
    now = time.time() if now is None else now
    fs = []
    for n in os.listdir(directory):
        p = os.path.join(directory, n)
        if n.startswith("observer_") and n.endswith(".jsonl") and p != keep:
            try:
                st = os.stat(p)
                fs.append((st.st_mtime, st.st_size, p))
            except OSError:
                pass
    fs.sort()
    total = sum(f[1] for f in fs)
    gone = []
    for mt, sz, p in fs:
        if now - mt > days * 86400 or total > cap:
            try:
                os.remove(p)
                total -= sz
                gone.append(p)
            except OSError:
                pass
    return gone


def default_dir():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from game_paths import LOCALLOW
    return os.path.join(LOCALLOW, "JawaBench", "health")


def default_log():
    from game_paths import LOCALLOW
    return os.path.join(LOCALLOW, "Player.log")


def run(out_dir, duration=None, once=False, interval=5.0, idle=30.0, switches=None, printing=False):
    lock = acquire_lock(out_dir)
    if lock is None:
        print("health_observer: another collector holds %s; exiting" % os.path.join(out_dir, LOCK_NAME))
        return 0
    c = Collector(out_dir, switches=switches, interval=interval, idle_interval=idle, log_path=default_log())
    prune(out_dir, c.cur)
    reason, last_prune = "end", time.monotonic()
    row = None
    try:
        nxt = time.monotonic()
        while True:
            row = c.sample()
            c.publish_last(row)
            if printing:
                print(json.dumps(row, indent=1))
            if once or (duration is not None and time.monotonic() - c.mono0 >= duration):
                break
            if time.monotonic() - last_prune > 3600:
                prune(out_dir, c.cur)
                last_prune = time.monotonic()
            nxt += interval if c.ctx.games else idle
            time.sleep(max(0.0, nxt - time.monotonic()))
            if time.monotonic() - nxt > 3 * interval:
                nxt = time.monotonic()                          # slept through (machine sleep): re-anchor
    except KeyboardInterrupt:
        reason = "interrupted"
    finally:
        c.stop(reason)
        release_lock(lock)
    hb = row["sources"]["obs.heartbeat"]["value"] if row else {}
    print("health_observer: %d samples, collector cpu %ss = %s cores; per-source ms %s; failed %s" % (
        c.samples, hb.get("collectorCpuS"), hb.get("collectorCores"), hb.get("costMsTotal"), hb.get("failedProbes")))
    return 0


# ------------------------------------------------------------------ reader

def read_stream(directory=None):
    d = directory or default_dir()
    rows, malformed, files = [], 0, 0
    try:
        names = sorted(n for n in os.listdir(d) if n.startswith("observer_") and n.endswith(".jsonl"))
    except OSError:
        names = []
    for n in names:
        files += 1
        try:
            with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        r = json.loads(line)
                        if not isinstance(r, dict) or "seq" not in r or "utc" not in r:
                            raise ValueError
                        r["_t"] = epoch(r["utc"])
                        rows.append(r)
                    except (ValueError, TypeError):
                        malformed += 1
        except OSError:
            pass
    rows.sort(key=lambda r: ((r.get("collector") or {}).get("id") or "", r["seq"]))
    return {"rows": rows, "malformed": malformed, "files": files, "dir": d}


def _proc_bits(src, key, fmt):
    if not src:
        return "%s no data" % key
    st = src.get("status")
    if st != "ok":
        return "%s %s%s" % (key, st, (" (%s)" % (src.get("reason") or src.get("error"))) if st != "off" else "")
    ps = src["value"].get("procs", [])
    if not ps:
        return "%s: no RimWorld process" % key
    return "; ".join(fmt(p) for p in ps)


def describe(row):
    """One evidence line for a sample. Values only, labelled with their scope; no causes."""
    s = row.get("sources", {})

    def cpu(p):
        if p.get("status"):
            return "pid %s cpu %s" % (p.get("pid"), p["status"])
        return "pid %s@%s %s (process total, all threads)" % (
            p.get("pid"), (p.get("startUtc") or "?")[11:19], "%s cores" % p["cores"] if p.get("cores") is not None
            else "no rate (%s)" % p.get("noRate"))

    def main(p):
        if p.get("status"):
            return "main thread %s" % p["status"]
        if p.get("cores") is None:
            return "main thread no rate (%s)" % p.get("noRate")
        return "main thread %s cores (assumed: earliest thread), other threads %s" % (
            p["cores"], p.get("otherThreadsCores") if p.get("otherThreadsCores") is not None else "no rate")

    def mem(p):
        if p.get("status"):
            return "memory %s" % p["status"]
        return "private %s MB, ws %s MB" % (p.get("privateMB"), p.get("workingSetMB"))
    parts = [_proc_bits(s.get("game.cpu"), "game cpu", cpu)]
    mt = s.get("game.mainthread")
    parts.append("main thread unavailable (%s)" % mt.get("reason") if mt and mt.get("status") == "unavailable"
                 else _proc_bits(mt, "main thread", main))
    parts.append(_proc_bits(s.get("game.memory"), "game memory", mem))
    sm = s.get("sys.memory") or {}
    parts.append("system avail %s MB, commit headroom %s MB" % (sm["value"].get("availPhysMB"),
                                                                 sm["value"].get("commitHeadroomMB", "unavailable"))
                 if sm.get("status") == "ok" else "system memory %s" % (sm.get("status") or "no data"))
    lg = s.get("log.growth") or {}
    if lg.get("status") == "ok":
        v = lg["value"]
        parts.append("log missing" if v.get("missing") else "log %s B/s%s%s" % (
            v.get("bytesPerS") if v.get("bytesPerS") is not None else "no rate",
            " ROTATED" if v.get("rotated") else "", " TRUNCATED" if v.get("truncated") else ""))
    else:
        parts.append("log growth %s" % (lg.get("status") or "no data"))
    hb = (s.get("obs.heartbeat") or {}).get("value") or {}
    parts.append("collector late %ss" % hb.get("lateS", "?"))
    return " | ".join(parts)


def join_incidents(incidents, rows, window_s=30):
    """For each TPS incident (needs _t), the nearest observer sample before and after it within window_s, and
    observer events in the window. Evidence only: simultaneity is coincidence, not cause."""
    samples = [r for r in rows if r.get("kind") == "sample"]
    for r in rows:
        if "_t" not in r and r.get("utc"):
            r["_t"] = epoch(r["utc"])
    out = []
    for inc in incidents:
        t = inc["_t"]
        out.append("%s  %s %s gap %ss" % (utc(t), (inc.get("kind") or "?").upper(), inc.get("type") or
                                          inc.get("gapKind") or "", inc.get("gapS", inc.get("silentS"))))
        before = [r for r in samples if t - window_s <= r["_t"] <= t]
        after = [r for r in samples if t < r["_t"] <= t + window_s]
        if not before and not after:
            out.append("    NO OBSERVER COVERAGE within +-%ds (observer not running, or its stream is elsewhere)"
                       % window_s)
        for label, sel in (("before", before[-1:]), ("after", after[:1])):
            for r in sel:
                out.append("    observer %+.1fs (%s): %s" % (r["_t"] - t, label, describe(r)))
        for e in rows:
            if e.get("kind") == "event" and abs(e["_t"] - t) <= window_s:
                out.append("    observer event %+.1fs: %s" % (e["_t"] - t, json.dumps(
                    {k: v for k, v in e.items() if k not in ("v", "kind", "seq", "collector", "_t", "utc")})[:200]))
        out.append("    (observations at the same time as the incident; no cause is established)")
    return out


def health_section(t0, t1, incidents, directory=None, window_s=30):
    st = read_stream(directory)
    rows = [r for r in st["rows"] if t0 - window_s <= r["_t"] <= t1 + window_s]
    samples = [r for r in rows if r.get("kind") == "sample"]
    out = ["-- external observer (health_observer.py) %s: %d samples in range, %d files, %d malformed --" % (
        st["dir"], len(samples), st["files"], st["malformed"])]
    prev = None
    for r in samples:
        hb = (r["sources"].get("obs.heartbeat") or {}).get("value") or {}
        if prev is not None and r["_t"] - prev > 3 * 30:
            out.append("%s  OBSERVER GAP %ds (no observer samples)" % (utc(prev), r["_t"] - prev))
        prev = r["_t"]
        if hb.get("failedProbes"):
            pass
    for e in rows:
        if e.get("kind") in ("event", "start", "stop") and t0 <= e["_t"] <= t1:
            out.append("%s  observer %s %s" % (e["utc"], e.get("kind"), json.dumps(
                {k: v for k, v in e.items() if k in ("event", "id", "pid", "startUtc", "exitCode", "reason", "line",
                                                     "meaning", "skippedBytes", "tid", "timeUnknown")})[:220]))
    if not samples:
        out.append("NO OBSERVER COVERAGE in this range: say nothing about process CPU, memory or log growth")
    out.extend(join_incidents(incidents, rows, window_s))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=None, help="stream directory (default <LocalLow>/JawaBench/health)")
    ap.add_argument("--for", dest="duration", type=float, default=None, help="run this many seconds, then stop")
    ap.add_argument("--once", action="store_true", help="one sample")
    ap.add_argument("--print", dest="printing", action="store_true")
    ap.add_argument("--interval", type=float, default=5.0, help="seconds between samples while a game runs")
    ap.add_argument("--idle", type=float, default=30.0, help="seconds between samples with no game")
    ap.add_argument("--off", action="append", default=[], metavar="ID", help="switch a source off (repeatable)")
    ap.add_argument("--read", action="store_true", help="read the stream and print the last samples")
    ap.add_argument("--last", type=int, default=10)
    a = ap.parse_args(argv)
    d = a.dir or default_dir()
    if a.read:
        st = read_stream(d)
        for r in [r for r in st["rows"] if r.get("kind") == "sample"][-a.last:]:
            print("%s  %s" % (r["utc"], describe(r)))
        print("%d rows, %d files, %d malformed [%s]" % (len(st["rows"]), st["files"], st["malformed"], d))
        return 0
    bad = [x for x in a.off if x not in SOURCES]
    if bad:
        print("health_observer: unknown source id(s) %s; known: %s" % (bad, ", ".join(SOURCES)), file=sys.stderr)
        return 2
    return run(d, duration=a.duration, once=a.once, interval=a.interval, idle=a.idle,
               switches={x: False for x in a.off}, printing=a.printing)


if __name__ == "__main__":
    sys.exit(main())
