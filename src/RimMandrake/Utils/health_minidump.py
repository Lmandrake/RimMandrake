#!/usr/bin/env python3
"""spike.minidump (design/RimMandrake/game_health_record.md): what was RimWorld doing during a hang?

MANUAL ONLY, one SMALL dump per incident, disk headroom checked first, retention capped. Never automatic
(AUTOMATIC = False): GPT review 1.9 requires a utility spike first - a dump that identifies a deliberately
blocked main thread, stacks that survive offline analysis, measured duration and size, proof the dumper cannot
strand the process suspended, and failures/partial dumps reported. None of that is measured yet.

    python.exe src\\RimMandrake\\Utils\\health_minidump.py --incident <key> [--pid N] [--dir D]

  * Windows python only (ctypes: kernel32 OpenProcess, psapi working set, dbghelp MiniDumpWriteDump).
  * Dump type: thread info + handle data + unloaded modules + process/thread data; NEVER full memory.
  * Headroom: refuses unless the target disk has >= 4 GB free AND at least the game's working set free (so even an
    unexpectedly large dump fits); unreadable headroom refuses (unavailable is never "enough").
  * One capture per incident key (an atomic claim file); a second request for the same incident is refused.
  * Output: <LocalLow>\\JawaBench\\health\\dumps\\rimworld_<pid>_<utc>.dmp plus a .json beside it holding the
    measured duration and size, or the error; a failed write leaves the file renamed .partial and says so.
  * Retention: newest 5 dumps, 4 GB total.
  * Hazard, UNMEASURED: MiniDumpWriteDump suspends the target's threads while it writes; if THIS process is
    killed mid-write the target may stay suspended. Do not kill it; if the game stays frozen after a dump,
    that is the first suspect.

Status: written, not deployed or run (2026-10-14); cost UNMEASURED.
"""
import argparse
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

AUTOMATIC = False
# MINIDUMP_TYPE (minidumpapiset.h)
MiniDumpNormal = 0x0
MiniDumpWithFullMemory = 0x2
MiniDumpWithHandleData = 0x4
MiniDumpWithUnloadedModules = 0x20
MiniDumpWithProcessThreadData = 0x100
MiniDumpWithThreadInfo = 0x1000
DUMP_FLAGS = MiniDumpWithThreadInfo | MiniDumpWithHandleData | MiniDumpWithUnloadedModules | MiniDumpWithProcessThreadData

MIN_FREE_BYTES = 4 * 1024 ** 3
KEEP = 5
CAP_BYTES = 4 * 1024 ** 3
GAME_EXE = "RimWorldWin64.exe"


def headroom_ok(free_bytes, working_set_bytes):
    """(ok, why). Unknown free space or working set refuses."""
    if free_bytes is None:
        return False, "free disk space unavailable: refused"
    if working_set_bytes is None:
        return False, "game working set unavailable: refused (cannot bound the dump)"
    need = max(MIN_FREE_BYTES, working_set_bytes)
    if free_bytes < need:
        return False, "only %.1f GB free; need %.1f GB (max of 4 GB and the working set)" % (free_bytes / 1024 ** 3, need / 1024 ** 3)
    return True, "%.1f GB free" % (free_bytes / 1024 ** 3)


def _safe(key):
    return re.sub(r"[^A-Za-z0-9_-]", "_", key or "")[:80] or "_"


def incident_claim(directory, key):
    """None when this call claimed the incident; else why not. Atomic (O_EXCL), so two callers cannot both win."""
    os.makedirs(directory, exist_ok=True)
    p = os.path.join(directory, "incident_%s.claim" % _safe(key))
    try:
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return "already captured (or claimed) for incident %r: %s" % (key, p)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps({"incident": key, "claimedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
    return None


def to_prune(files, keep=KEEP, cap_bytes=CAP_BYTES):
    """files: [(name, size, mtime)]. Keep the newest `keep` whose running total fits `cap_bytes`; the rest
    are returned oldest first."""
    newest = sorted(files, key=lambda f: f[2], reverse=True)
    kept, total = 0, 0
    prune = []
    for name, size, mtime in newest:
        if kept < keep and total + size <= cap_bytes:
            kept += 1
            total += size
        else:
            prune.append((mtime, name))
    return [n for _, n in sorted(prune)]


# ---------------------------------------------------------------------------------------------- Windows half
def _win():
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    dbg = ctypes.WinDLL("dbghelp", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    dbg.MiniDumpWriteDump.restype = wintypes.BOOL
    dbg.MiniDumpWriteDump.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

    class PMC(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    return ctypes, k32, psapi, dbg, PMC


def find_game_pids():
    import subprocess
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + GAME_EXE, "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    pids = []
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[0].strip('"').lower() == GAME_EXE.lower():
            try:
                pids.append(int(parts[1]))
            except ValueError:
                pass
    return pids


def capture(pid, incident, directory):
    """One small dump. Returns the record written beside it (also printed)."""
    if os.name != "nt":
        return {"status": "unavailable", "reason": "Windows python (python.exe) only"}
    why = incident_claim(directory, incident)
    if why:
        return {"status": "refused", "reason": why}
    ctypes, k32, psapi, dbg, PMC = _win()
    PROCESS_QUERY_INFORMATION, PROCESS_VM_READ = 0x0400, 0x0010
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        return {"status": "failed", "reason": "OpenProcess(%d) failed: error %d" % (pid, ctypes.get_last_error())}
    try:
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        ws = pmc.WorkingSetSize if psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb) else None
        try:
            free = shutil.disk_usage(directory).free
        except OSError:
            free = None
        ok, hw = headroom_ok(free, ws)
        rec = {"pid": pid, "incident": incident, "dumpFlags": DUMP_FLAGS, "headroom": hw, "workingSetBytes": ws}
        if not ok:
            rec.update(status="refused", reason=hw)
            return rec
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        path = os.path.join(directory, "rimworld_%d_%s.dmp" % (pid, stamp))
        GENERIC_WRITE, CREATE_NEW, FILE_ATTRIBUTE_NORMAL = 0x40000000, 1, 0x80
        fh = k32.CreateFileW(path, GENERIC_WRITE, 0, None, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, None)
        if not fh or fh == ctypes.c_void_p(-1).value:
            rec.update(status="failed", reason="CreateFileW failed: error %d" % ctypes.get_last_error())
            return rec
        t0 = time.perf_counter()
        try:
            wrote = dbg.MiniDumpWriteDump(h, pid, fh, DUMP_FLAGS, None, None, None)
            err = ctypes.get_last_error()
        finally:
            k32.CloseHandle(fh)
        rec["durationMs"] = round((time.perf_counter() - t0) * 1000, 1)
        if not wrote:
            os.replace(path, path + ".partial")
            rec.update(status="failed", reason="MiniDumpWriteDump failed: error %d (file kept as .partial)" % err, path=path + ".partial")
        else:
            rec.update(status="ok", path=path, sizeBytes=os.path.getsize(path))
        with open(path + ".json", "w") as f:
            json.dump(rec, f, indent=1)
        files = [(n, os.path.getsize(os.path.join(directory, n)), os.path.getmtime(os.path.join(directory, n)))
                 for n in os.listdir(directory) if n.endswith(".dmp")]
        for n in to_prune(files):
            try:
                os.remove(os.path.join(directory, n))
                rec.setdefault("pruned", []).append(n)
            except OSError:
                pass
        return rec
    finally:
        k32.CloseHandle(h)


def main(argv=None):
    ap = argparse.ArgumentParser(description="spike.minidump: one small dump of RimWorld per incident (manual only)")
    ap.add_argument("--incident", required=True, help="incident key (e.g. the TPS stall id); one dump per key")
    ap.add_argument("--pid", type=int, default=None)
    ap.add_argument("--dir", default=None)
    a = ap.parse_args(argv)
    directory = a.dir
    if directory is None:
        from game_paths import LOCALLOW
        directory = os.path.join(LOCALLOW, "JawaBench", "health", "dumps")
    pid = a.pid
    if pid is None:
        pids = find_game_pids() if os.name == "nt" else []
        if len(pids) != 1:
            print(json.dumps({"status": "refused", "reason": "found %d %s processes; pass --pid" % (len(pids), GAME_EXE)}))
            return 2
        pid = pids[0]
    rec = capture(pid, a.incident, directory)
    print(json.dumps(rec, indent=1))
    return 0 if rec.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
