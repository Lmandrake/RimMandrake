"""Host collectors that telemetryd runs natively on Windows (design §5: no PowerShell, no focus steal).

- volumes: free/total per drive letter (shutil.disk_usage = GetDiskFreeSpaceExW). Absent = UNMEASURED.
- VHDX: logical size and the ALLOCATED size (GetCompressedFileSizeW: what the sparse file really holds).
- memory: GlobalMemoryStatusEx + GetPerformanceInfo (commit charge / limit).
- dirs: hourly recursive size of a short list of directories.
- deploys: ModsConfig.xml hash + per-mod newest mtime in the game's Mods folder, so a deploy shows up
  even when no tool reported one (event marked `detected`).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import time

from tcommon import IS_WIN, cfg


def volumes() -> dict:
    out = {}
    for letter in cfg()["volumes"]:
        root = f"{letter}:\\" if IS_WIN else f"/mnt/{letter.lower()}/"
        try:
            u = shutil.disk_usage(root)
            out[letter] = {"free": u.free, "total": u.total, "used": u.used}
        except OSError:
            out[letter] = None  # UNMEASURED: not mounted / not present
    return out


def allocated_size(path: str) -> int | None:
    if not os.path.exists(path):
        return None
    if IS_WIN:
        k = ctypes.windll.kernel32
        k.GetCompressedFileSizeW.restype = ctypes.c_uint32
        high = ctypes.c_uint32(0)
        low = k.GetCompressedFileSizeW(ctypes.c_wchar_p(path), ctypes.byref(high))
        if low == 0xFFFFFFFF and ctypes.GetLastError() != 0:
            return None
        return (high.value << 32) + low
    try:
        return os.stat(path).st_blocks * 512
    except OSError:
        return None


def vhdx() -> dict | None:
    p = cfg()["vhdx"]
    try:
        return {"size": os.path.getsize(p), "alloc": allocated_size(p)}
    except OSError:
        return None


def memory() -> dict | None:
    if not IS_WIN:
        return None

    class MEMSTAT(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32),
                    ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                    ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                    ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                    ("ullAvailExtendedVirtual", ctypes.c_uint64)]

    class PERFINFO(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_uint32), ("CommitTotal", ctypes.c_size_t), ("CommitLimit", ctypes.c_size_t),
                    ("CommitPeak", ctypes.c_size_t), ("PhysicalTotal", ctypes.c_size_t),
                    ("PhysicalAvailable", ctypes.c_size_t), ("SystemCache", ctypes.c_size_t),
                    ("KernelTotal", ctypes.c_size_t), ("KernelPaged", ctypes.c_size_t),
                    ("KernelNonpaged", ctypes.c_size_t), ("PageSize", ctypes.c_size_t),
                    ("HandleCount", ctypes.c_uint32), ("ProcessCount", ctypes.c_uint32),
                    ("ThreadCount", ctypes.c_uint32)]

    m = MEMSTAT()
    m.dwLength = ctypes.sizeof(MEMSTAT)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        return None
    out = {"load_pct": m.dwMemoryLoad, "phys_total": m.ullTotalPhys, "phys_avail": m.ullAvailPhys}
    p = PERFINFO()
    p.cb = ctypes.sizeof(PERFINFO)
    if ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(p), p.cb):
        pg = p.PageSize
        out.update({"commit_total": p.CommitTotal * pg, "commit_limit": p.CommitLimit * pg,
                    "commit_peak": p.CommitPeak * pg, "sys_cache": p.SystemCache * pg,
                    "processes": p.ProcessCount, "handles": p.HandleCount})
    return out


def dir_size(path: str, budget_s: float = 60.0) -> int | None:
    """Recursive bytes; None when absent or when the walk ran out of budget (never a partial number)."""
    if not os.path.isdir(path):
        return None
    t0 = time.time()
    total = 0
    stack = [path]
    while stack:
        if time.time() - t0 > budget_s:
            return None
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        else:
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def sample_host(E, ts: float) -> dict:
    """One host pass into Emit E. Returns the measured dict (for alerts and sparks)."""
    vols = volumes()
    for letter, v in vols.items():
        if v:
            lab = {"vol": letter, "role": cfg()["volumes"][letter]}
            E.point("rm_disk_free_bytes", lab, v["free"], ts)
            E.point("rm_disk_total_bytes", lab, v["total"], ts)
    vx = vhdx()
    if vx:
        E.point("rm_vhdx_size_bytes", {}, vx["size"], ts)
        E.point("rm_vhdx_alloc_bytes", {}, vx["alloc"], ts)
    mem = memory()
    if mem:
        E.point("rm_host_mem_load_pct", {}, mem["load_pct"], ts)
        E.point("rm_host_mem_avail_bytes", {}, mem["phys_avail"], ts)
        E.point("rm_host_mem_total_bytes", {}, mem["phys_total"], ts)
        for k in ("commit_total", "commit_limit", "commit_peak", "sys_cache"):
            if k in mem:
                E.point(f"rm_host_{k}_bytes", {}, mem[k], ts)
    out = {"ts": ts, "vols": vols, "vhdx": vx, "mem": mem}
    E.latest["host"] = out
    return out


def sample_dirs(E, ts: float) -> dict:
    out = {}
    for name, p in cfg()["dirs"].items():
        n = dir_size(p)
        out[name] = n
        if n is not None:
            E.point("rm_dir_bytes", {"dir": name}, n, ts)
    E.latest["dirs"] = {"ts": ts, "sizes": out}
    return out


# ------------------------------------------------------------------ deploy detection

def _mod_fingerprints(mods_dir: str) -> dict:
    """mod folder -> newest mtime of any file under it (cheap enough every 10 min: our Mods
    folder holds our deployed mods, not the Workshop)."""
    out = {}
    try:
        tops = [e for e in os.scandir(mods_dir) if e.is_dir()]
    except OSError:
        return out
    for t in tops:
        newest = 0.0
        stack = [t.path]
        while stack:
            d = stack.pop()
            try:
                with os.scandir(d) as it:
                    for e in it:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                stack.append(e.path)
                            else:
                                newest = max(newest, e.stat(follow_symlinks=False).st_mtime)
                        except OSError:
                            continue
            except OSError:
                continue
        out[t.name] = round(newest, 1)
    return out


def detect_changes(con, E, ts: float, prev: dict | None) -> dict:
    """Compare with the previous fingerprint; emit `deploy` (detected) and `modlist` events."""
    import store
    cur = {"mods": _mod_fingerprints(os.path.join(cfg()["rimworld"], "Mods")), "modsconfig": None}
    try:
        with open(cfg()["modsconfig"], "rb") as f:
            cur["modsconfig"] = hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        pass
    if prev:
        changed = sorted(m for m, t in cur["mods"].items() if prev.get("mods", {}).get(m) != t)
        if changed and prev.get("mods"):
            store.add_event(con, ts, "deploy", ",".join(changed)[:200],
                            {"mods": changed, "detected": True}, "detector", f"detector:deploy:{int(ts)}")
            E.events += 1
        if cur["modsconfig"] and prev.get("modsconfig") and cur["modsconfig"] != prev["modsconfig"]:
            store.add_event(con, ts, "modlist", cur["modsconfig"],
                            {"was": prev["modsconfig"], "now": cur["modsconfig"], "detected": True},
                            "detector", f"detector:modlist:{int(ts)}")
            E.events += 1
    return cur


# ------------------------------------------------------------------ processes (Windows, Toolhelp32)

def process_pids(names: set[str]) -> dict[str, list[int]]:
    """exe name (lower) -> pids, without spawning tasklist (no console flash from pythonw)."""
    out: dict[str, list[int]] = {}
    if not IS_WIN:
        return out
    from ctypes import wintypes

    class PE32(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]

    k = ctypes.windll.kernel32
    k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    snap = k.CreateToolhelp32Snapshot(0x2, 0)
    if not snap or snap == wintypes.HANDLE(-1).value:
        return out
    try:
        e = PE32()
        e.dwSize = ctypes.sizeof(PE32)
        ok = k.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            n = e.szExeFile.lower()
            if n in names:
                out.setdefault(n, []).append(e.th32ProcessID)
            ok = k.Process32NextW(snap, ctypes.byref(e))
    finally:
        k.CloseHandle(snap)
    return out
