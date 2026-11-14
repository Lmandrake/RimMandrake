#!/usr/bin/env python3
"""run_tmp.py — every run a launcher starts gets its own TMPDIR, and the launcher's code deletes it when the run is over.

Owner, 2026-11-03 (TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP): asking an LLM agent to clean up after itself is an unsolved
assurance problem; cleanup must be a deterministic program that runs whether or not the agent remembers. /tmp (an 18 GB
tmpfs) filled with about 15 GB of agents' mutation scratch and the nightly selftests went red with ENOSPC.

    prepare(name)   make <root>/<name> (0700) and return it; the launcher passes env(dir) to the run
    env(dir)        {TMPDIR, TMP, TEMP} -> dir
    drop(name)      delete <root>/<name> now if its run is over (an end path calls it; refused while live)
    sweep()         delete every dir under <root> whose run is over (each Relentless tick, start and end; the hourly
                    scratch_reap run): the guarantee behind every end path, a killed engine and a restart included

<root> is ~/.seat-tmp/runs (env RM_RUN_TMP_ROOT): the ext4 disk, not the /tmp tmpfs, and inside scratch_reap's roots, so
anything kept here is still judged by the reaper. <name> is the run's systemd unit (rm-relentless-work-<h>-g3), or
pid-<pid>-<starttime>-<label> for a plain child process (pid_name()).

A run is LIVE, and its dir stays, when any of these holds (any doubt is live):
  * the dir was made or touched within GRACE_S (a launch between prepare() and the unit appearing);
  * systemd reports the unit active, activating, deactivating or reloading, or cannot say;
  * a pid-<pid>-<starttime> name's process still runs with that start time;
  * any process of ours carries TMPDIR/TMP/TEMP pointing into it, or has its cwd or an open file inside it (a child
    that left the unit's cgroup with setsid still carries its environment);
  * a process of ours cannot be inspected (then every dir stays this pass, and the summary says so).
A dead run's dir holding a git repo or a .rws save anywhere inside is KEPT, not deleted: it is under scratch_reap's roots,
which judges every clone there with its bundle-unique-first policy; when the clone is gone the next sweep takes the rest.
Deletion renames the dir aside to .reaping-<pid>-<name>, looks at /proc again, and only then removes it; a remainder a
crash leaves is removed by the next sweep once its pid is dead.

Stated limits: a process that names the dir only in a variable other than TMPDIR/TMP/TEMP, holds nothing open in it and
is not its unit, is not seen (a daemon a worker started with its own TMPDIR is that). Root-owned processes are not read.
A tool that ignores TMPDIR and writes literal /tmp paths is not this module's: scratch_reap's /tmp backstop takes those.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time

GRACE_S = 300
ACTIVE = {"active", "activating", "deactivating", "reloading", "refreshing"}
NONDUMPABLE = {"systemd", "(sd-pam)", "ssh-agent", "tailscaled"}     # ours by uid, unreadable by design, never a run (tailscaled: a Tailscale SSH session child, root-owned /proc)
NAME = re.compile(r"^[A-Za-z0-9@._-]{1,200}$")
PIN = re.compile(r"^\.reaping-(\d+)-(.+)$")
PID_NAME = re.compile(r"^pid-(\d+)-(\d+)-")
VARS = (b"TMPDIR=", b"TMP=", b"TEMP=")


def root() -> str:
    return os.environ.get("RM_RUN_TMP_ROOT") or os.path.expanduser("~/.seat-tmp/runs")


def path(name: str) -> str:
    if not NAME.match(name) or name.startswith("."):
        raise ValueError("run tmp name %r: want [A-Za-z0-9@._-], not leading dot" % name)
    return os.path.join(root(), name)


def env(d: str) -> dict:
    return {"TMPDIR": d, "TMP": d, "TEMP": d}


def prepare(name: str, runner=subprocess.run) -> str:
    """Make the run's dir (fresh: a reused name's leftovers are not inherited) and return it. Raises OSError.
    A reused name's old dir goes only through sweep()'s judgment: while its run is live (a duplicate launch systemd
    is about to refuse) it stays, and this raises FileExistsError instead of taking a live run's TMPDIR from it."""
    d = path(name)
    os.makedirs(root(), mode=0o700, exist_ok=True)
    if os.path.lexists(d):
        sweep(only=[name], now=time.time() + GRACE_S, runner=runner)
        if os.path.lexists(d):
            raise FileExistsError(17, "run tmp dir still in use (a live run of this name?)", d)
    os.mkdir(d, 0o700)
    return d


def start_time(pid: int) -> str | None:
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            return f.read().rsplit(b")", 1)[1].split()[19].decode()
    except (OSError, IndexError):
        return None


def pid_name(label: str, pid: int | None = None) -> str:
    """A name for a dir owned by a plain process (no unit): its pid and start time, so a reused pid is not it."""
    pid = os.getpid() if pid is None else pid
    return "pid-%d-%s-%s" % (pid, start_time(pid) or "0", re.sub(r"[^A-Za-z0-9_-]", "-", label)[:60])


def unit_states(names: list[str], runner=subprocess.run) -> dict:
    """{name: ActiveState}; "unknown" for every name when systemctl fails (which holds them all)."""
    units = [n for n in names if not PID_NAME.match(n)]
    if not units:
        return {}
    try:
        r = runner(["systemctl", "--user", "show", "-p", "Id", "-p", "ActiveState", "--", *[u if "." in u else u + ".service" for u in units]],
                   capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return {u: "unknown" for u in units}
    if r.returncode:
        return {u: "unknown" for u in units}
    blocks = r.stdout.strip().split("\n\n")
    out = {}
    for u, b in zip(units, blocks):
        kv = dict(ln.split("=", 1) for ln in b.splitlines() if "=" in ln)
        want = u if "." in u else u + ".service"
        out[u] = kv.get("ActiveState", "unknown") if kv.get("Id") == want else "unknown"
    for u in units:
        out.setdefault(u, "unknown")
    return out


def _top(p: str, rt: str) -> str | None:
    if p.startswith(rt + "/"):
        return p[len(rt) + 1:].split("/", 1)[0]
    return None


def _read(base: str):
    """(environ bytes, [cwd and fd link targets]); None when the process is gone; the OSError when unreadable."""
    try:
        with open(base + "/environ", "rb") as f:
            envb = f.read()
        links = [os.readlink(base + "/cwd")]
        for fd in os.listdir(base + "/fd"):
            try:
                links.append(os.readlink("%s/fd/%s" % (base, fd)))
            except FileNotFoundError:
                pass
        with open(base + "/maps", "rb") as f:       # a mapping outlives its fd: an mmap-only user still holds the dir
            for ln in f:
                parts = ln.split(None, 5)
                if len(parts) == 6 and parts[5].startswith(b"/"):
                    links.append(os.fsdecode(parts[5].rstrip(b"\n")))
        return envb, links
    except (FileNotFoundError, ProcessLookupError):
        return None
    except OSError as e:
        return e


def users(rt: str | None = None) -> tuple[set[str], list[str]]:
    """({top-level names under the root some process of ours uses}, [processes we could not read])."""
    rt = os.path.realpath(rt or root())
    roots = {rt, root()}
    used, blind = set(), []
    me, uid = os.getpid(), os.getuid()
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) == me:
            continue
        base = "/proc/" + pid
        try:
            if os.stat(base).st_uid != uid:
                continue
            with open(base + "/comm") as f:
                comm = f.read().strip()
        except (FileNotFoundError, ProcessLookupError):
            continue
        except OSError as e:
            blind.append("pid %s: %s" % (pid, e.strerror))
            continue
        got = _read(base)
        if isinstance(got, OSError):        # an exec or an exit in flight reads EACCES for a moment: look once more
            time.sleep(0.05)
            got = _read(base)
        if got is None:
            continue
        if isinstance(got, OSError):
            if comm in NONDUMPABLE:
                continue
            blind.append("pid %s (%s): %s" % (pid, comm, got.strerror))
            continue
        envb, links = got
        for kv in envb.split(b"\0"):
            for v in VARS:
                if kv.startswith(v):
                    val = os.fsdecode(kv[len(v):])
                    for r in roots:
                        n = _top(val, r)
                        if n:
                            used.add(n)
        for ln in links:
            for r in roots:
                n = _top(ln, r)
                if n:
                    used.add(n)
    return used, blind


WORK_WALK_CAP = 200_000        # entries; a tree bigger than this is kept for scratch_reap's capped judgment


def holds_work(d: str) -> bool:
    """A git repo (a .git, or a bare repo's HEAD+objects+refs) or a savegame anywhere inside, a mount point inside,
    a spot we cannot read, or a tree too big to walk here: scratch_reap judges it, not us."""
    bad, n = [], 0
    for _dp, dns, fns in os.walk(d, onerror=bad.append):
        n += len(dns) + len(fns)
        if ".git" in dns or ".git" in fns or any(f.endswith(".rws") for f in fns) \
                or ("HEAD" in fns and "objects" in dns and "refs" in dns) or n > WORK_WALK_CAP:
            return True
    return bool(bad) or bool(mounts_under(d))


def mounts_under(d: str) -> list[str]:
    """Mount points at or below d (a FUSE or bind mount a run left): rmtree would cross into it. Unreadable -> [d]."""
    d = os.path.realpath(d)
    try:
        with open("/proc/self/mountinfo", "rb") as f:
            pts = [os.fsdecode(ln.split()[4]).replace("\\040", " ") for ln in f if len(ln.split()) > 4]
    except OSError:
        return [d]
    return [m for m in pts if m == d or m.startswith(d + "/")]


def _remove(d: str):
    """Rename aside, then remove. A remainder is a .reaping-<pid>-<name> the next sweep takes."""
    pin = os.path.join(os.path.dirname(d), ".reaping-%d-%s" % (os.getpid(), os.path.basename(d)))
    os.rename(d, pin)
    shutil.rmtree(pin)


def restore(src: str, dst: str) -> bool:
    """Rename a pin back under its name ONLY if nothing holds that name now, in one atomic step (renameat2
    RENAME_NOREPLACE): a check-then-rename would let a file made in between be replaced. False when the name exists or
    the kernel or filesystem cannot promise no-replace; the pin then stays, judged again next sweep under both names."""
    import ctypes
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        fn = libc.renameat2
    except (OSError, AttributeError):
        return False
    return fn(-100, os.fsencode(src), -100, os.fsencode(dst), 1) == 0     # AT_FDCWD, RENAME_NOREPLACE


def _young(d: str, now: float) -> bool:
    try:
        st = os.lstat(d)
    except FileNotFoundError:
        return False
    return now - max(st.st_mtime, st.st_ctime) < GRACE_S


def sweep(only: list[str] | None = None, now: float | None = None, runner=subprocess.run, mine: bool = False) -> dict:
    """Delete the dirs of runs that are over. -> a summary for the caller's record; never raises for one dir."""
    now = time.time() if now is None else now
    rt = root()
    out = {"root": rt, "removed": [], "live": 0, "young": 0, "work": [], "errors": [], "blind": 0}
    try:
        names = sorted(os.listdir(rt))
    except FileNotFoundError:
        return out
    except OSError as e:
        out["errors"].append("%s: %s" % (rt, e.strerror))
        return out
    if only is not None:
        names = [n for n in names if n in set(only) or (PIN.match(n) and PIN.match(n)[2] in set(only))]
    pins = [n for n in names if PIN.match(n)]
    names = [n for n in names if not n.startswith(".")]
    used, blind = users(rt)
    if blind:
        out["blind"] = len(blind)
        out["errors"].append("cannot read %d process(es) of ours, every run dir kept: %s" % (len(blind), "; ".join(blind[:3])))
        return out
    states = unit_states(names, runner)
    for n in pins:                                  # a removal a crash interrupted: judged dead before its rename
        pid, orig = int(PIN.match(n)[1]), PIN.match(n)[2]
        # a child that survived the crash names the ORIGINAL dir in its TMPDIR: either name in use keeps the pin
        if (pid == os.getpid() or start_time(pid) is None) and n not in used and orig not in used \
                and not holds_work(os.path.join(rt, n)):
            try:
                shutil.rmtree(os.path.join(rt, n))
                out["removed"].append(n)
            except OSError as e:
                out["errors"].append("%s: %s" % (n, e.strerror))
    for n in names:
        d = os.path.join(rt, n)
        if os.path.islink(d) or not os.path.isdir(d):
            continue
        if _young(d, now):
            out["young"] += 1
            continue
        m = PID_NAME.match(n)
        if m:
            owner_done = mine and int(m[1]) == os.getpid()      # the owner itself ending: its own pid no longer holds it
            run_live = not owner_done and start_time(int(m[1])) == m[2]
        else:
            run_live = states.get(n, "unknown") in ACTIVE | {"unknown"}
        if n in used or run_live:
            out["live"] += 1
            continue
        if holds_work(d):
            out["work"].append(n)
            continue
        try:
            pin = os.path.join(rt, ".reaping-%d-%s" % (os.getpid(), n))
            os.rename(d, pin)
            again, blind2 = users(rt)
            if blind2 or n in again or os.path.basename(pin) in again or holds_work(pin):
                # something arrived between the look and the rename: it stays. A relaunch may have made a fresh dir
                # under the name meanwhile; a rename would replace it, so the pin stays to be judged next sweep
                restore(pin, d)
                out["live"] += 1
                continue
            shutil.rmtree(pin)
            out["removed"].append(n)
        except OSError as e:
            out["errors"].append("%s: %s" % (n, e.strerror))
    return out


def drop(name: str | None, runner=subprocess.run, mine: bool = False) -> dict | None:
    """An end path's call: delete this run's dir if it is over. None when there is nothing to do.
    mine=True: the calling process owns a pid-name dir and is done with it (its children still hold it via users())."""
    if not name or not NAME.match(name):
        return None
    if not os.path.lexists(os.path.join(root(), name)):
        return None
    return sweep(only=[name], now=time.time() + GRACE_S, runner=runner, mine=mine)


if __name__ == "__main__":
    import json
    print(json.dumps(sweep() if sys.argv[1:] == ["sweep"] else {"root": root()}, indent=1))
