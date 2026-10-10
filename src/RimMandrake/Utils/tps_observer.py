"""tps_observer.py - the STANDING external observer of the TPS record (BRIDGE_TPS_REVIEW2_FIXES_1 MUST 17).

belt_watchdog.py's `tps-observer` line only runs when someone runs belt_watchdog. This runs on its own: a
Windows scheduled task starts it under pythonw.exe (no console window, so it never steals the owner's focus)
every 2 minutes, from the read-only mirror D:\\Luke\\dev\\RimMandrake. Each pass does exactly what
belt_watchdog's tps section does from outside the game process and nothing else:

  * probe every running RimWorldWin64 with its START TIME (ctypes Toolhelp + GetProcessTimes; no console
    child, no PowerShell), so a reused pid is a different process
  * tps_record.observe() -> append silent / hb-stale-alive / exited-without-shutdown findings to
    observer.jsonl (open / update / ended, same rules as belt_watchdog; both may run, each reads the other's rows)
  * tps_record.preserve_prev_log() -> keep Player-prev.log before a relaunch rotates it
  * rewrite tps\\observer_last.json with this pass's time and result, so the observer's own coverage is visible

Install (once, as the owner's user; no elevation):
  schtasks.exe /Create /F /TN "RimMandrake\\TPS Observer" /SC MINUTE /MO 2 ^
    /TR "\"<pythonw.exe>\" D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\Utils\\tps_observer.py"
Remove:  schtasks.exe /Delete /F /TN "RimMandrake\\TPS Observer"
Run by hand (either OS):  python3 src/RimMandrake/Utils/tps_observer.py --print
Under WSL the process probe is unavailable (no Windows API), so nothing is declared exited there.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tps_record  # noqa: E402


def probe_games():
    """[{pid, startUtc}] for every RimWorldWin64.exe, or None when the probe is unavailable (not Windows)."""
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes as W
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class PE(ctypes.Structure):
        _fields_ = [("dwSize", W.DWORD), ("cntUsage", W.DWORD), ("th32ProcessID", W.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", W.DWORD), ("cntThreads", W.DWORD),
                    ("th32ParentProcessID", W.DWORD), ("pcPriClassBase", ctypes.c_long), ("dwFlags", W.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]
    k32.CreateToolhelp32Snapshot.restype = W.HANDLE
    k32.OpenProcess.restype = W.HANDLE
    snap = k32.CreateToolhelp32Snapshot(0x2, 0)            # TH32CS_SNAPPROCESS
    if not snap or snap == W.HANDLE(-1).value:
        return None
    out = []
    try:
        e = PE()
        e.dwSize = ctypes.sizeof(PE)
        ok = k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            if e.szExeFile.lower() == "rimworldwin64.exe":
                pid, start = int(e.th32ProcessID), None
                h = k32.OpenProcess(0x1000, False, pid)     # PROCESS_QUERY_LIMITED_INFORMATION
                if h:
                    c, x, kt, ut = W.FILETIME(), W.FILETIME(), W.FILETIME(), W.FILETIME()
                    if k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x), ctypes.byref(kt), ctypes.byref(ut)):
                        ft = (c.dwHighDateTime << 32) | c.dwLowDateTime
                        ep = ft / 1e7 - 11644473600.0
                        start = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ep)) + ".%03dZ" % int((ep % 1) * 1000)
                    k32.CloseHandle(h)
                out.append({"pid": pid, "startUtc": start})
            ok = k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    return out


def one_pass():
    d = tps_record.record_dir()
    res = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pid": os.getpid(), "host": os.name}
    try:
        procs = probe_games()
        res["games"] = procs
        rec = tps_record.read_record(d)
        found = []
        for f in tps_record.observe(rec["rows"], tps_record.read_heartbeats(d), procs):
            if f.get("persist"):
                tps_record.record_observation(f, d)
            found.append({k: f.get(k) for k in ("session", "finding", "state", "level")})
        res["findings"] = found
        kept = tps_record.preserve_prev_log()
        res["archivedLog"] = os.path.basename(kept) if kept else None
        res["ok"] = True
    except Exception as e:                                      # noqa: BLE001
        res["ok"] = False
        res["error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    try:
        tmp = os.path.join(d, "observer_last.json.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(res, fh)
        os.replace(tmp, os.path.join(d, "observer_last.json"))
    except OSError:
        pass
    return res


if __name__ == "__main__":
    r = one_pass()
    if "--print" in sys.argv:
        print(json.dumps(r, indent=1))
    sys.exit(0 if r.get("ok") else 1)
