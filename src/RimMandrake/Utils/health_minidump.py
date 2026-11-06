#!/usr/bin/env python3
"""spike.minidump (design/RimMandrake/game_health_record.md): what was RimWorld doing during a hang?

MANUAL ONLY on a live game, one SMALL dump per incident, disk headroom checked first, retention capped. Never
automatic on a game that is to keep running (AUTOMATIC = False): GPT review 1.9 requires a utility spike first - a
dump that identifies a deliberately blocked main thread, stacks that survive offline analysis, measured duration and
size, proof the dumper cannot strand the process suspended, and failures/partial dumps reported. The spike ran
offline on a stand-in target (health_minidump_spike.py, 2026-11-06, MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL; evidence
D:\\ClaudeWork\\rimmandrake\\minidump_spike\\spike_2026-11-06, `verify` PASS); its one live clause (a dump of the real
game, which must keep running) is still owed, and AUTOMATIC stays False until it passes.

The ONE automatic use is `--before-kill` (BEFORE_KILL_AUTOMATIC): a caller whose very next act kills the game
(FLOWWORKS_DIAGNOSE_FREEZE_AFTER_DRAWBRIDGE: the SteveDesktop worker's wedged-kept-game and hung-run restarts, where a
frozen game's evidence was lost to the kill). There the live-game hazard is moot (a game left suspended is killed
anyway), the cost is seconds and headroom-checked disk, and each dump's .json is a real-incident measurement of
duration and size for the spike. Its output is one JSON line.

    python.exe src\\RimMandrake\\Utils\\health_minidump.py --incident <key> [--pid N] [--dir D] [--before-kill]

  * Windows python only (ctypes: kernel32 OpenProcess, psapi working set, dbghelp MiniDumpWriteDump).
  * Dump type: thread info + handle data + unloaded modules + process/thread data; NEVER full memory.
  * Headroom: refuses unless the target disk has >= 4 GB free AND at least the game's working set free (so even an
    unexpectedly large dump fits); unreadable headroom refuses (unavailable is never "enough").
  * One capture per incident key (an atomic claim file); a second request for the same incident is refused.
    An attempt that never started a dump (refused headroom, OpenProcess/CreateFile failed) gives the claim back.
  * Output: <LocalLow>\\JawaBench\\health\\dumps\\rimworld_<pid>_<utc>.dmp plus a .json beside it holding the
    measured duration and size, or the error; a failed write leaves the file renamed .partial and says so.
  * Retention: newest 5 dumps (partials included), 4 GB total, over this tool's own rimworld_<pid>_<utc>.dmp names
    only; the dump just written is never pruned.
  * Mode `snapshot` (default): PssCaptureSnapshot clones the process (VA clone) and the dump is written from the
    clone, so the game pauses only while the clone is taken. MEASURED on the stand-in (64 MB / 1 GB working set):
    pause 4-6 / 37-58 ms, whole capture 21-25 / 58-78 ms, dump ~105 KB either way (three runs); `direct`
    (MiniDumpWriteDump on the live process, the control) 70-108 ms. A dumper killed mid-write left the target running in both modes. A failed
    snapshot (measured: error 1450 on the 1 GB target under memory pressure) falls back to direct; the record says
    `fallbackFrom` and `pssError`.
  * A dumper killed mid-write leaves a .dmp with no .json: the next capture in that folder reports it (`orphans`)
    and, once it is ORPHAN_AGE_S old, renames it .partial. A cancelled or failed write is recorded `failed`.
  * Offline reading: minidump_read.py (plain Python, any OS) names native frames by export from DLL copies of the
    dumped machine; Mono JIT frames are bare addresses.

Status: offline spike PASS 2026-11-06; live clause A1 (the real game) owed.
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
BEFORE_KILL_AUTOMATIC = True     # the sole automatic caller: a stop path that kills the game next
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


OURS = re.compile(r"^rimworld_\d+_\d{8}T\d{6}Z\.dmp(\.partial)?$")


def prune_dumps(directory, keep_path):
    """Apply retention to THIS tool's dumps only (`--dir` may be any folder: a Unity crash dump or someone else's
    .dmp there is never ours to delete). Partial dumps count against the cap too. `keep_path`, the dump just
    written, is never pruned: a single dump over the cap is reported, not deleted out from under its record.
    Each pruned dump takes its .json record with it. -> names pruned."""
    files = []
    for n in os.listdir(directory):
        p = os.path.join(directory, n)
        if not OURS.match(n) or os.path.abspath(p) == os.path.abspath(keep_path):
            continue
        try:
            files.append((n, os.path.getsize(p), os.path.getmtime(p)))
        except OSError:
            continue
    try:
        keep_size = os.path.getsize(keep_path)
    except OSError:
        keep_size = 0
    pruned = []
    for n in to_prune(files, keep=KEEP - 1, cap_bytes=max(CAP_BYTES - keep_size, 0)):
        p = os.path.join(directory, n)
        try:
            os.remove(p)
        except OSError:
            continue
        pruned.append(n)
        side = os.path.join(directory, n[:-len(".partial")] if n.endswith(".partial") else n) + ".json"
        try:
            os.remove(side)
        except OSError:
            pass
    return pruned


def incident_release(directory, key):
    """Give the incident back when no dump was attempted (refused headroom, OpenProcess/CreateFile failed): the
    one-per-incident rule bounds how often the game is suspended, and nothing was suspended."""
    try:
        os.remove(os.path.join(directory, "incident_%s.claim" % _safe(key)))
    except FileNotFoundError:
        pass


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
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.PssCaptureSnapshot.restype = wintypes.DWORD
    k32.PssCaptureSnapshot.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    k32.PssFreeSnapshot.restype = wintypes.DWORD
    k32.PssFreeSnapshot.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    return ctypes, k32, psapi, dbg, PMC


# MINIDUMP_CALLBACK_INPUT is pshpack4: ProcessId @0, ProcessHandle @4, CallbackType @12 (x64)
CB_TYPE_OFFSET = 12
CancelCallback, IsProcessSnapshotCallback = 6, 16
S_FALSE = 1
# PSS_CAPTURE_VA_CLONE | HANDLES | HANDLE_NAME/BASIC/TYPE_SPECIFIC/TRACE | THREADS | THREAD_CONTEXT(_EXTENDED)
PSS_FLAGS = 0x1 | 0x4 | 0x8 | 0x10 | 0x20 | 0x40 | 0x80 | 0x100 | 0x200
CONTEXT_ALL_AMD64 = 0x10001F
MODES = ("snapshot", "direct")
MODE = "snapshot"


def _callback_info(ctypes, snapshot, hook):
    """MINIDUMP_CALLBACK_INFORMATION answering IsProcessSnapshotCallback with S_FALSE (the handle is a PSS
    snapshot), and calling `hook(callback_type)` on every callback: the spike's slow-write and cancel cases. A hook
    returning 'cancel' cancels the dump at its CancelCallback. -> (info struct, keepalive) or (None, None)."""
    if not snapshot and hook is None:
        return None, None
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)

    def cb(_param, inp, outp):
        t = ctypes.c_ulong.from_address(inp + CB_TYPE_OFFSET).value
        if t == IsProcessSnapshotCallback and snapshot:
            ctypes.c_long.from_address(outp).value = S_FALSE
            return 1
        if hook is not None and hook(t) == "cancel" and t == CancelCallback:
            ctypes.c_int.from_address(outp).value = 1        # CheckCancel
            ctypes.c_int.from_address(outp + 4).value = 1    # Cancel
        return 1

    class INFO(ctypes.Structure):
        _fields_ = [("CallbackRoutine", ctypes.c_void_p), ("CallbackParam", ctypes.c_void_p)]
    fn = proto(cb)
    return INFO(ctypes.cast(fn, ctypes.c_void_p), None), fn


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


ORPHAN_AGE_S = 30


def _mark_partial(path, tries=10):
    """Rename a failed dump to .partial. A scanner (Defender) may hold a just-closed file for a moment (measured:
    WinError 32 on the spike's 1 GB case), so retry; if it never lets go the dump keeps its name and its record (status
    failed, written beside it either way) is what says it is partial. -> the path the dump now has."""
    for i in range(tries):
        try:
            os.replace(path, path + ".partial")
            return path + ".partial"
        except FileNotFoundError:
            return path
        except OSError:
            time.sleep(0.1 * (i + 1))
    return path


def orphans(directory, now=None):
    """Our .dmp files with no .json record: a dumper killed mid-write (or a crash) left them. One older than
    ORPHAN_AGE_S (no live writer) is renamed .partial, so its name says what it is. -> names reported."""
    now = time.time() if now is None else now
    out = []
    for n in sorted(os.listdir(directory)):
        p = os.path.join(directory, n)
        if not OURS.match(n) or n.endswith(".partial") or os.path.exists(p + ".json"):
            continue
        try:
            age = now - os.path.getmtime(p)
        except OSError:
            continue
        if age >= ORPHAN_AGE_S:
            try:
                os.replace(p, p + ".partial")
                n += ".partial"
            except OSError:
                pass
        out.append(n)
    return out


def capture(pid, incident, directory, mode=None, hook=None):
    """One small dump. Returns the record written beside it (also printed). mode 'snapshot' (default) dumps a PSS
    clone, so the game is suspended only while the clone is taken and a dumper killed mid-write strands nothing;
    'direct' is MiniDumpWriteDump on the live process (the spike's control). `hook` is the spike's test seam."""
    if os.name != "nt":
        return {"status": "unavailable", "reason": "Windows python (python.exe) only"}
    why = incident_claim(directory, incident)
    if why:
        return {"status": "refused", "reason": why}
    attempted = [False]
    try:
        rec = _capture(pid, incident, directory, attempted, mode or MODE, hook)
    finally:
        if not attempted[0]:
            incident_release(directory, incident)
    left = orphans(directory)
    if left:
        rec["orphans"] = left
    return rec


def _capture(pid, incident, directory, attempted, mode=MODE, hook=None):
    if mode not in MODES:
        return {"status": "failed", "reason": "unknown mode %r" % mode}
    ctypes, k32, psapi, dbg, PMC = _win()
    PROCESS_QUERY_INFORMATION, PROCESS_VM_READ = 0x0400, 0x0010
    PROCESS_DUP_HANDLE, PROCESS_CREATE_PROCESS = 0x0040, 0x0080
    want = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
    if mode == "snapshot":
        want |= PROCESS_DUP_HANDLE | PROCESS_CREATE_PROCESS
    h = k32.OpenProcess(want, False, pid)
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
        rec = {"pid": pid, "incident": incident, "mode": mode, "dumpFlags": DUMP_FLAGS, "headroom": hw, "workingSetBytes": ws}
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
        attempted[0] = True
        snap = None
        wrote, err, fail = False, 0, None
        try:
            src = h
            if mode == "snapshot":
                snap = ctypes.c_void_p()
                e = k32.PssCaptureSnapshot(h, PSS_FLAGS, CONTEXT_ALL_AMD64, ctypes.byref(snap))
                rec["suspendedMs"] = round((time.perf_counter() - t0) * 1000, 1)   # the game's only pause
                if e:
                    # MEASURED 2026-11-06: error 1450 (ERROR_NO_SYSTEM_RESOURCES) on a 1 GB target with ~3 GB commit
                    # free; a VA clone needs commit. Fall back to a direct dump (the kill test stranded nothing there
                    # either) rather than leave the hang unrecorded.
                    snap = None
                    rec.update(mode="direct", fallbackFrom="snapshot", pssError=e)
                else:
                    src = snap.value
            if fail is None:
                info, _keep = _callback_info(ctypes, snap is not None, hook)   # _keep holds the callback alive
                wrote = dbg.MiniDumpWriteDump(src, pid, fh, DUMP_FLAGS, None, None,
                                              ctypes.byref(info) if info is not None else None)
                err = ctypes.get_last_error()
        except Exception as e:                                       # noqa: BLE001 - recorded, never raised
            fail = "dump raised %r" % e
        finally:
            k32.CloseHandle(fh)                                      # closed BEFORE any rename (share mode 0)
            if snap is not None:
                k32.PssFreeSnapshot(k32.GetCurrentProcess(), snap)
        rec["durationMs"] = round((time.perf_counter() - t0) * 1000, 1)
        if rec["mode"] == "direct" and fail is None:
            rec["suspendedMs"] = rec["durationMs"]      # MiniDumpWriteDump holds the threads for the whole write
        if fail is not None:
            rec.update(status="failed", reason=fail + " (file kept as .partial)", path=_mark_partial(path))
        elif not wrote:
            rec.update(status="failed", reason="MiniDumpWriteDump failed: error %d (0x%08x) (file kept as .partial)"
                       % (err, err & 0xFFFFFFFF), path=_mark_partial(path))
        else:
            rec.update(status="ok", path=path, sizeBytes=os.path.getsize(path))
        with open(path + ".json", "w") as f:
            json.dump(rec, f, indent=1)
        pruned = prune_dumps(directory, rec["path"])
        if pruned:
            rec["pruned"] = pruned
        return rec
    finally:
        k32.CloseHandle(h)


def main(argv=None):
    ap = argparse.ArgumentParser(description="spike.minidump: one small dump of RimWorld per incident (manual only)")
    ap.add_argument("--incident", required=True, help="incident key (e.g. the TPS stall id); one dump per key")
    ap.add_argument("--pid", type=int, default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--before-kill", action="store_true",
                    help="the caller kills the game next (the only automatic use): one JSON line out")
    a = ap.parse_args(argv)
    out = (lambda r: json.dumps(r)) if a.before_kill else (lambda r: json.dumps(r, indent=1))
    directory = a.dir
    if directory is None:
        from game_paths import LOCALLOW
        directory = os.path.join(LOCALLOW, "JawaBench", "health", "dumps")
    pid = a.pid
    if pid is None:
        pids = find_game_pids() if os.name == "nt" else []
        if len(pids) != 1:
            print(out({"status": "refused", "reason": "found %d %s processes; pass --pid" % (len(pids), GAME_EXE)}))
            return 2
        pid = pids[0]
    rec = capture(pid, a.incident, directory)
    if a.before_kill:
        rec["beforeKill"] = True
    print(out(rec))
    return 0 if rec.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
