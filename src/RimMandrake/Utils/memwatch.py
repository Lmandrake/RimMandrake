#!/usr/bin/env python3
"""Seat memory watchdog — phase 1 of SEAT_MEMORY_CLONES_DRIVES_1.

design/RimMandrake/memory_clones_drives_2026-10-08.md §3 item 6 and §7 phase 1:
"a 1-minute user timer reads memory.events and memory.stat of every seat; if oom_kill
increases or shmem > 2 GB it [alerts] naming the seat and the largest /tmp paths", plus
PSI and file_dirty/file_writeback (§8 #4) and swap / deleted-but-open files (§8 #6).

One run = one sample. Run by rm-memwatch.timer (src/RimMandrake/Utils/systemd/) every
minute; also safe by hand: `python3 src/RimMandrake/Utils/memwatch.py --print`.

What it reads, per cgroup: memory.events (high/max/oom/oom_kill/oom_group_kill — these are
HIERARCHICAL in cgroup v2, so a seat's count includes its tool cgroup's), memory.current,
memory.peak, memory.max, memory.swap.current, memory.stat (anon, file, shmem, file_dirty,
file_writeback) and memory.pressure (some/full avg10). Which cgroups: each watched root
(claude-seats.slice, rm.slice/rm-harness.slice), every *.scope under it, and each
scope's direct children (claude-code-bash = the tool cgroup, seat = Claude itself).

What it writes (outside git — a timer must not dirty a seat clone, see DEVIATION below):
  $STATE/state.json     last counters per cgroup + which shmem alerts are armed
  $STATE/samples.jsonl  one line per run, every watched cgroup (the "week of memory.peak
                        data" §7 asks for before seat caps change); rotated at 20 MB to .1
  $STATE/events.jsonl   one line per alert-worthy change
  stdout                one line per event -> the systemd journal (journalctl --user -u rm-memwatch)
  Windows toast         for oom_kill / oom_group_kill increments and shmem threshold
                        crossings under claude-seats.slice only; best effort, never fatal
  Windows host (phase 3, GPT objection #3): each sample line may carry "host" = committed
  bytes, commit limit, available MB, total/free physical, RimWorldWin64 working set / private /
  peak WS (null when not running), vmmemWSL working set; failure = {"unmeasured": reason}.
  Cadence: every ~5 min, every run (1 min) while RimWorldWin64 was running at the last sample.
  state.json["host"] holds peaks; `memwatch.py host` prints the summary. Never toasts.
$STATE defaults to ~/.local/state/rm-memwatch (XDG_STATE_HOME honoured).

Rules chosen where the design is silent (simplest thing):
- high/max/oom increments are RECORDED as events but do not toast: `max` ticks constantly
  on any cgroup at its limit (the slice read 878,652 on 2026-10-08) and would be noise.
  oom_kill is the one that means a process died.
- rm-harness.slice is recorded but never toasts: run_selftests.py already reports a test
  killed by its own cap as KILLED, and that is the cap working.
- shmem alert is edge-triggered per seat scope: fires on crossing --shmem-gb (default 2),
  re-arms once shmem falls below it.
- The very first run (no state.json) baselines silently; a cgroup first seen on a LATER
  run is compared against zero, so a seat that OOMs within its first minute still alerts.
- Top tmpfs files: the largest regular files by allocated blocks on the tmpfs mounts
  /tmp, /dev/shm and /run/user/<uid> (one filesystem each, no crossing), plus this user's
  deleted-but-still-open files on tmpfs (which hold memory and appear in no listing).
  `shmem` also counts shared anonymous mappings, so the files may not add up to it (§8 #7).

DEVIATION from the design: §3 says the watchdog "writes a RimFlow ledger event". It does
not. Ledger shards live in seat clones and are committed by their seat; an unattended
writer appending to one would ride along into whatever that seat commits next, or
collide with it. events.jsonl + the journal + the toast carry the same facts. Item owner
may wire `rimflow note` from events.jsonl if a ledger record is still wanted.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

UID = os.getuid()
USER_CG = Path(f"/sys/fs/cgroup/user.slice/user-{UID}.slice/user@{UID}.service")
DEFAULT_ROOTS = (USER_CG / "claude.slice/claude-seats.slice", USER_CG / "rm.slice/rm-harness.slice")
TOAST_ROOT_NAME = "claude-seats.slice"
DEFAULT_TMPFS = ("/tmp", "/dev/shm", f"/run/user/{UID}")
EVENT_KEYS = ("high", "max", "oom", "oom_kill", "oom_group_kill")
TOAST_KEYS = ("oom_kill", "oom_group_kill")
STAT_KEYS = ("anon", "file", "shmem", "file_dirty", "file_writeback")
SAMPLES_ROTATE_BYTES = 20 * 1024 * 1024
GB = 1024 ** 3
# Absolute: a systemd user service has no /mnt/c on PATH (measured: "powershell.exe: not found").
POWERSHELL = "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"


def state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state")
    return Path(base) / "rm-memwatch"


def _read(p: Path) -> str | None:
    try:
        return p.read_text()
    except OSError:
        return None


def _kv(text: str | None) -> dict[str, int]:
    out: dict[str, int] = {}
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("-").isdigit():
            out[parts[0]] = int(parts[1])
    return out


def _num(text: str | None):
    if text is None:
        return None
    t = text.strip()
    return t if t == "max" else (int(t) if t.isdigit() else None)


def _psi(text: str | None) -> dict[str, float]:
    out = {}
    for line in (text or "").splitlines():
        parts = line.split()
        if parts and parts[0] in ("some", "full"):
            for f in parts[1:]:
                if f.startswith("avg10="):
                    out[parts[0] + "_avg10"] = float(f[6:])
    return out


def read_cgroup(d: Path) -> dict | None:
    ev = _read(d / "memory.events")
    if ev is None:
        return None
    stat = _kv(_read(d / "memory.stat"))
    return {
        "events": {k: _kv(ev).get(k, 0) for k in EVENT_KEYS},
        "current": _num(_read(d / "memory.current")),
        "peak": _num(_read(d / "memory.peak")),
        "max": _num(_read(d / "memory.max")),
        "swap": _num(_read(d / "memory.swap.current")),
        "stat": {k: stat.get(k, 0) for k in STAT_KEYS},
        "psi": _psi(_read(d / "memory.pressure")),
    }


def watched(roots) -> dict[str, tuple[dict, bool]]:
    """name -> (reading, toastable). name is root-name/relative path."""
    out: dict[str, tuple[dict, bool]] = {}
    for root in roots:
        root = Path(root)
        r = read_cgroup(root)
        if r is None:
            continue
        toast = root.name == TOAST_ROOT_NAME
        out[root.name] = (r, toast)
        for scope in sorted(root.glob("*.scope")):
            s = read_cgroup(scope)
            if s is None:
                continue
            out[f"{root.name}/{scope.name}"] = (s, toast)
            for child in sorted(p for p in scope.iterdir() if p.is_dir()):
                c = read_cgroup(child)
                if c is not None:
                    out[f"{root.name}/{scope.name}/{child.name}"] = (c, toast)
    return out


def top_tmpfs_files(mounts, n: int = 5) -> list[dict]:
    """Largest files (allocated bytes) on each mount, staying on its filesystem, plus
    deleted-but-open tmpfs files held by this user's processes."""
    found: list[tuple[int, str]] = []
    for m in mounts:
        try:
            dev = os.stat(m).st_dev
        except OSError:
            continue
        stack = [m]
        while stack:
            d = stack.pop()
            try:
                it = os.scandir(d)
            except OSError:
                continue
            with it:
                for e in it:
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if st.st_dev != dev:
                        continue
                    if e.is_dir(follow_symlinks=False):
                        stack.append(e.path)
                    elif e.is_file(follow_symlinks=False):
                        found.append((st.st_blocks * 512, e.path))
    # Deleted-but-open files: only on mounts that really are tmpfs (an ext4 path's
    # deleted log holds disk, not memory).
    tmpfs_targets = set()
    for line in (_read(Path("/proc/self/mounts")) or "").splitlines():
        f = line.split()
        if len(f) >= 3 and f[2] == "tmpfs":
            tmpfs_targets.add(f[1])
    mount_devs = set()
    for m in mounts:
        if m not in tmpfs_targets:
            continue
        try:
            mount_devs.add(os.stat(m).st_dev)
        except OSError:
            pass
    for pid in (os.listdir("/proc") if mount_devs else ()):
        if not pid.isdigit():
            continue
        fd_dir = f"/proc/{pid}/fd"
        try:
            fds = os.listdir(fd_dir)
        except OSError:
            continue
        for fd in fds:
            p = f"{fd_dir}/{fd}"
            try:
                tgt = os.readlink(p)
                if not tgt.endswith(" (deleted)"):
                    continue
                st = os.stat(p)
            except OSError:
                continue
            if st.st_dev in mount_devs:
                found.append((st.st_blocks * 512, f"{tgt} [open by pid {pid}]"))
    found.sort(reverse=True)
    seen, out = set(), []
    for size, path in found:
        if path in seen:
            continue
        seen.add(path)
        out.append({"path": path, "gb": round(size / GB, 2)})
        if len(out) >= n:
            break
    return out


def toast(title: str, body: str) -> bool:
    """Windows toast via powershell.exe and the built-in WinRT notification API."""
    def q(s: str) -> str:
        return s.replace("'", "''").replace("&", "and").replace("<", "(").replace(">", ")")
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;"
        "[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]|Out-Null;"
        "$x=New-Object Windows.Data.Xml.Dom.XmlDocument;"
        f"$x.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>{q(title)}</text><text>{q(body)}</text></binding></visual></toast>');"
        "$app='{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe';"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($x))"
    )
    try:
        r = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


HOST_PS = (
    "$ErrorActionPreference='Stop';"
    "$os=Get-CimInstance Win32_OperatingSystem;"
    "$c=@{};(Get-Counter '\\Memory\\Committed Bytes','\\Memory\\Commit Limit','\\Memory\\Available MBytes').CounterSamples|"
    "ForEach-Object{$c[$_.Path.Split('\\')[-1]]=$_.CookedValue};"
    "$rw=Get-Process RimWorldWin64 -ErrorAction SilentlyContinue|Select-Object -First 1;"
    "$vm=Get-Process vmmem* -ErrorAction SilentlyContinue|Sort-Object WorkingSet64 -Descending|Select-Object -First 1;"
    "[pscustomobject]@{committed=$c['committed bytes'];limit=$c['commit limit'];avail_mb=$c['available mbytes'];"
    "total_kb=$os.TotalVisibleMemorySize;free_kb=$os.FreePhysicalMemory;"
    "rw_ws=$(if($rw){$rw.WorkingSet64});rw_private=$(if($rw){$rw.PrivateMemorySize64});rw_peak_ws=$(if($rw){$rw.PeakWorkingSet64});"
    "vmmem_ws=$(if($vm){$vm.WorkingSet64})}|ConvertTo-Json -Compress"
)
HOST_FIELDS = ("committed", "limit", "avail_mb", "total_kb", "free_kb", "rw_ws", "rw_private", "rw_peak_ws", "vmmem_ws")
HOST_IDLE_SECS = 290   # RimWorld not running: one Windows sample per ~5 min
HOST_BUSY_SECS = 55    # RimWorld running: every timer run (1 min), a cold load moves fast


def run_powershell(ps: str, timeout: int = 40) -> str | None:
    """stdout of a powershell command, CRLF stripped; None on any failure."""
    try:
        r = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace").replace("\r", "").strip()


def host_sample(runner=run_powershell) -> dict:
    """One Windows host reading. Failure -> {"unmeasured": reason}, never zeros."""
    out = runner(HOST_PS)
    if not out:
        return {"unmeasured": "powershell failed or timed out"}
    try:
        d = json.loads(out.splitlines()[-1])
        if not isinstance(d, dict) or not all(isinstance(d.get(k), (int, float)) for k in ("committed", "limit", "avail_mb")):
            return {"unmeasured": "counters missing in powershell output"}
    except ValueError:
        return {"unmeasured": "powershell output not JSON"}
    return {k: d.get(k) for k in HOST_FIELDS}


def host_due(hstate: dict, now: float) -> bool:
    gap = HOST_BUSY_SECS if hstate.get("rw_running") else HOST_IDLE_SECS
    return now - hstate.get("last_epoch", 0) >= gap


def host_update(hstate: dict, h: dict, now: float) -> dict:
    """Fold a sample into state: last attempt time, running flag, peaks (only from real readings)."""
    hs = dict(hstate)
    hs["last_epoch"] = now
    if "unmeasured" in h:
        return hs
    hs["rw_running"] = h.get("rw_ws") is not None
    hs["latest"] = h
    for key, src in (("peak_committed", "committed"), ("peak_rw_ws", "rw_peak_ws"),
                     ("peak_rw_private", "rw_private"), ("peak_vmmem_ws", "vmmem_ws")):
        v = h.get(src)
        if v is not None and v > hs.get(key, 0):
            hs[key] = v
    if h.get("rw_ws") is not None and h["rw_ws"] > hs.get("peak_rw_ws", 0):
        hs["peak_rw_ws"] = h["rw_ws"]
    if h.get("limit") and h.get("committed") is not None:
        room = h["limit"] - h["committed"]
        if "min_headroom" not in hs or room < hs["min_headroom"]:
            hs["min_headroom"] = room
    return hs


def host_summary(state: dict) -> str:
    hs = state.get("host") or {}
    h = hs.get("latest")
    if not h:
        return "no Windows host sample yet"
    g = lambda v: "n/a (not running)" if v is None else f"{v / GB:.2f} GB"
    room = h["limit"] - h["committed"]
    lines = [
        f"latest sample epoch {int(hs.get('last_epoch', 0))}  (RimWorld {'RUNNING' if hs.get('rw_running') else 'not running'})",
        f"commit      {g(h['committed'])} of {g(h['limit'])}   headroom {room / GB:.2f} GB   (lowest seen {hs.get('min_headroom', room) / GB:.2f} GB)",
        f"physical    total {h['total_kb'] * 1024 / GB:.2f} GB  free {h['free_kb'] * 1024 / GB:.2f} GB  available {h['avail_mb'] / 1024:.2f} GB",
        f"RimWorld    ws {g(h.get('rw_ws'))}  private {g(h.get('rw_private'))}  peak ws {g(h.get('rw_peak_ws'))}",
        f"vmmemWSL    ws {g(h.get('vmmem_ws'))}",
        f"PEAKS       committed {g(hs.get('peak_committed'))}   RimWorld ws {g(hs.get('peak_rw_ws'))}   RimWorld private {g(hs.get('peak_rw_private'))}   vmmemWSL {g(hs.get('peak_vmmem_ws'))}",
    ]
    return "\n".join(lines)


def seat_of(name: str) -> str:
    for part in name.split("/"):
        if part.startswith("claude-seat-"):
            return part[len("claude-seat-"):].rsplit("-", 1)[0]
    return name.split("/")[0]


def check(roots, tmpfs, sdir: Path, shmem_gb: float, do_toast: bool, now: float | None = None, host_fn=None) -> list[dict]:
    now = time.time() if now is None else now
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now))
    sdir.mkdir(parents=True, exist_ok=True)
    state_p = sdir / "state.json"
    first_run = not state_p.exists()
    try:
        prev = json.loads(state_p.read_text()) if not first_run else {}
    except (OSError, ValueError):
        prev, first_run = {}, True
    prev_cg = prev.get("cgroups", {})
    armed_over = set(prev.get("shmem_over", []))
    cur = watched(roots)
    events: list[dict] = []
    over_now = set()
    for name, (r, toastable) in cur.items():
        base = prev_cg.get(name, {}).get("events", {k: 0 for k in EVENT_KEYS})
        if not first_run:
            for k in EVENT_KEYS:
                d = r["events"][k] - base.get(k, 0)
                if d > 0:
                    events.append({"ts": ts, "kind": k, "cgroup": name, "seat": seat_of(name),
                                   "delta": d, "total": r["events"][k],
                                   "toast": toastable and k in TOAST_KEYS})
        is_scope = name.endswith(".scope")
        if is_scope and r["stat"]["shmem"] > shmem_gb * GB:
            over_now.add(name)
            if name not in armed_over and not first_run:
                events.append({"ts": ts, "kind": "shmem", "cgroup": name, "seat": seat_of(name),
                               "shmem_gb": round(r["stat"]["shmem"] / GB, 2),
                               "threshold_gb": shmem_gb, "toast": toastable})
    for e in events:
        r = cur[e["cgroup"]][0]
        e["snapshot"] = {"current_gb": round((r["current"] or 0) / GB, 2) if isinstance(r["current"], int) else r["current"],
                         "max": r["max"], "swap": r["swap"], "stat": r["stat"], "psi": r["psi"]}
    if any(e["kind"] in ("shmem", "oom_kill", "oom_group_kill") for e in events):
        top = top_tmpfs_files(tmpfs)
        for e in events:
            if e["kind"] in ("shmem", "oom_kill", "oom_group_kill"):
                e["top_tmpfs"] = top
    # persist
    hstate = prev.get("host", {})
    hsample = None
    if host_fn is not None and host_due(hstate, now):
        hsample = host_sample(host_fn)
        hstate = host_update(hstate, hsample, now)
    new_state = {"ts": ts, "cgroups": {n: {"events": r["events"]} for n, (r, _) in cur.items()},
                 "shmem_over": sorted(over_now), "host": hstate}
    tmp = state_p.with_suffix(".tmp")
    tmp.write_text(json.dumps(new_state))
    tmp.replace(state_p)
    samples = sdir / "samples.jsonl"
    try:
        if samples.stat().st_size > SAMPLES_ROTATE_BYTES:
            samples.replace(sdir / "samples.jsonl.1")
    except OSError:
        pass
    with samples.open("a") as f:
        rec = {"ts": ts, "cgroups": {n: r for n, (r, _) in cur.items()}}
        if hsample is not None:
            rec["host"] = hsample
        f.write(json.dumps(rec) + "\n")
    if events:
        with (sdir / "events.jsonl").open("a") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")
    for e in events:
        what = f"shmem {e['shmem_gb']} GB > {e['threshold_gb']} GB" if e["kind"] == "shmem" \
            else f"{e['kind']} +{e['delta']} (total {e['total']})"
        print(f"memwatch {e['seat']}: {what} in {e['cgroup']}")
    if do_toast:
        loud = [e for e in events if e.get("toast")]
        if loud:
            lines = []
            for e in loud[:4]:
                lines.append(f"{e['seat']}: shmem {e['shmem_gb']} GB" if e["kind"] == "shmem"
                             else f"{e['seat']}: {e['kind']} +{e['delta']}")
            top = loud[0].get("top_tmpfs") or []
            if top:
                lines.append("largest tmpfs: " + ", ".join(f"{t['path']} {t['gb']}G" for t in top[:3]))
            toast("Seat memory alert", "; ".join(lines))
    return events


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "host":
        hp = argparse.ArgumentParser(prog="memwatch.py host")
        hp.add_argument("--state-dir", type=Path, default=None)
        ha = hp.parse_args(argv[1:])
        try:
            st = json.loads((ha.state_dir or state_dir()).joinpath("state.json").read_text())
        except (OSError, ValueError):
            st = {}
        print(host_summary(st))
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", action="append", help="cgroup root to watch (repeatable); default: the two slices")
    ap.add_argument("--tmpfs", action="append", help="tmpfs mount to scan on alert (repeatable)")
    ap.add_argument("--state-dir", type=Path, default=None)
    ap.add_argument("--shmem-gb", type=float, default=2.0)
    ap.add_argument("--no-toast", action="store_true")
    ap.add_argument("--no-host", action="store_true", help="skip the Windows host sample")
    ap.add_argument("--print", action="store_true", help="also print the current reading of every cgroup")
    a = ap.parse_args(argv)
    roots = a.root or DEFAULT_ROOTS
    check(roots, a.tmpfs or DEFAULT_TMPFS, a.state_dir or state_dir(), a.shmem_gb, not a.no_toast,
          host_fn=None if a.no_host else run_powershell)
    if a.print:
        for name, (r, _) in watched(roots).items():
            cur = r["current"] / GB if isinstance(r["current"], int) else 0
            print(f"{name}: current {cur:.2f}G shmem {r['stat']['shmem'] / GB:.2f}G "
                  f"anon {r['stat']['anon'] / GB:.2f}G oom_kill {r['events']['oom_kill']} max {r['max']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
