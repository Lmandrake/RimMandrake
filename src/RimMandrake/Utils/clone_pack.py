#!/usr/bin/env python3
"""clone_pack.py - git packs the timer clones in its own unit, never inside a timer's run.

Page: design/specs/2026-11-27-timer-clone-packing/boundary.md. Item: RIMMANDRAKE_UNHOOK_GIT_PACKING_FROM_TICK_TOOK_13_MIN.
A `git fetch` or `git commit` in a clone starts git's automatic packing when the clone has many loose objects or packs.
Inside the Maturation Pipeline tick's 1 GB unit that packing swapped 7.1 GB and one tick took 13 min 24 s
(2026-11-27 12:47 AM PST); systemd killed it at the unit's end and left tmp_pack_* behind.

    clone_pack.py show              the timer clones that the unit files name, with their counts; writes nothing
    clone_pack.py hold [ROOT ...]   write gc.auto=0 and maintenance.auto=false into each clone (none = every timer clone)
    clone_pack.py run [--apply]     each timer clone: hold, delete dead tmp_* files, pack when git itself would have;
                                    write reading.json. Plan unless --apply. Exit 0 all done, 1 a clone failed,
                                    3 no unit file named a clone (could not look at any)
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO_UNITS = HERE / "systemd"
USER_UNITS = Path.home() / ".config" / "systemd" / "user"
ROOT = Path(os.environ.get("RM_CLONE_ROOT", "/home/mandrake/rm"))

HOLD = (("gc.auto", "0"), ("maintenance.auto", "false"))
# git's own thresholds (gc.auto and gc.autoPackLimit defaults): run packs a clone exactly when git would have.
LOOSE_AT = 6700
PACKS_AT = 50
# The delta search of one pack: memory per thread (pack.windowMemory) times threads. Ends no work. Measured with these
# on 2026-11-27: the dispatch clone 172 s, peak 5 G with page cache, swap 78.6 M; bench 765 s and pulse-deploy 463 s in
# one run, peak 15.8 G with page cache (anon about 1.7 G sampled mid-pack), swap 373 M.
PACK_CONFIG = ("-c", "pack.threads=4", "-c", "pack.windowMemory=256m")
# A tmp_pack_*/tmp_obj_* that nobody wrote for this long is a killed git's leftover: a live writer writes it without a
# pause. Ends no work (it only decides what is garbage).
DEAD_TEMP_S = 6 * 3600
import time_budget as TB  # noqa: E402
CALL_S = TB.CALL_S       # the hang guard of one quick git call (config, rev-parse, count-objects)
# budget: danger=a hung repack holds the hourly unit, and no other clone is packed; evidence=the longest pack, bench's
# first (125769 loose objects, 670 packs), took 765 s on 2026-11-27; 10x rounded up
PACK_S = 9000

def state_dir():
    d = os.environ.get("RM_CLONE_PACK_STATE")
    if d:
        return Path(d)
    return Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "rimmandrake" / "clone_pack"


def git(root, *a, timeout=CALL_S, extra=()):
    return subprocess.run(["git", *extra, "-C", str(root), *a], capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)


def worktree_of(path, root):
    """-> the git work tree (a folder with a .git entry) that holds `path`, under `root`, or None. A bare repo has no
    .git entry, so it is never named."""
    p = Path(path)
    root = Path(root)
    while True:
        if p == root or root not in p.parents:
            return None
        if (p / ".git").exists() and p.is_dir():
            return p
        p = p.parent


def timer_clones(unit_dirs=None, root=None):
    """-> sorted work trees under root that a WorkingDirectory= or ExecStart*= line of a unit file names."""
    root = Path(root or ROOT)
    path_re = re.compile(re.escape(str(root)) + r"/[^\s'\";|&)]+")
    found = set()
    for d in unit_dirs if unit_dirs is not None else (REPO_UNITS, USER_UNITS):
        d = Path(d)
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*")):
            if not f.is_file() or f.suffix not in (".service", ".conf"):
                continue
            for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
                key = ln.split("=", 1)[0].strip()
                if key != "WorkingDirectory" and not key.startswith("ExecStart"):
                    continue
                for m in path_re.finditer(ln):
                    p = m.group(0)
                    w = worktree_of(p, root)
                    if w:
                        found.add(w)
    return sorted(found)


def hold(root, apply=True):
    """Write HOLD into the clone's own config where it differs. -> the keys written (or that a plan would write)."""
    wrote = []
    for k, v in HOLD:
        r = git(root, "config", "--local", "--get-all", k)
        if r.returncode not in (0, 1):
            raise RuntimeError("git config --get %s: %s" % (k, r.stderr.strip()))
        if r.stdout.split() == [v]:
            continue
        if apply:
            w = git(root, "config", "--local", "--replace-all", k, v)
            if w.returncode:
                raise RuntimeError("git config %s %s: %s" % (k, v, w.stderr.strip()))
        wrote.append(k)
    return wrote


def objects_dir(root):
    r = git(root, "rev-parse", "--git-path", "objects")
    if r.returncode:
        raise RuntimeError("git rev-parse: %s" % r.stderr.strip())
    p = Path(r.stdout.strip())
    return p if p.is_absolute() else Path(root) / p


def dead_temps(objects, now, idle_s=DEAD_TEMP_S):
    """-> the tmp_pack_* in pack/ and tmp_obj_* in ??/ that nobody wrote for idle_s seconds."""
    out = []
    for f in list((objects / "pack").glob("tmp_pack_*")) + list(objects.glob("[0-9a-f][0-9a-f]/tmp_obj_*")):
        try:
            if now - f.stat().st_mtime >= idle_s:
                out.append(f)
        except FileNotFoundError:
            pass
    return sorted(out)


def counts(root):
    r = git(root, "count-objects", "-v")
    if r.returncode:
        raise RuntimeError("git count-objects: %s" % r.stderr.strip())
    c = {}
    for ln in r.stdout.splitlines():
        k, _, v = ln.partition(":")
        v = v.strip()
        c[k.strip()] = int(v) if v.isdigit() else v
    return c


def needs_pack(c, loose_at=LOOSE_AT, packs_at=PACKS_AT):
    return c.get("count", 0) >= loose_at or c.get("packs", 0) >= packs_at


def pack(root):
    """Pack the loose objects and roll the small packs into one; the large pack stays; nothing is pruned."""
    r = git(root, "repack", "-d", "-q", "--geometric=2", timeout=PACK_S, extra=PACK_CONFIG)
    if r.returncode:
        raise RuntimeError("git repack exited %d: %s" % (r.returncode, r.stderr.strip()))


def one(root, apply, now, loose_at, packs_at):
    row = {"clone": str(root), "held": False, "deleted": [], "packed": False}
    try:
        row["hold_wrote"] = hold(root, apply=apply)
        row["held"] = apply or not row["hold_wrote"]
        objects = objects_dir(root)
        dead = dead_temps(objects, now)
        if apply:
            for f in dead:
                f.unlink(missing_ok=True)
        row["deleted" if apply else "would_delete"] = [str(f) for f in dead]
        row["before"] = counts(root)
        if needs_pack(row["before"], loose_at, packs_at):
            if apply:
                t0 = time.monotonic()
                pack(root)
                row["seconds"] = round(time.monotonic() - t0, 1)
                row["packed"] = True
                row["after"] = counts(root)
            else:
                row["would_pack"] = True
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        row["failed"] = "%s: %s" % (type(e).__name__, e)
    return row


def run(clones, apply=False, now=None, loose_at=LOOSE_AT, packs_at=PACKS_AT, state=None):
    now = time.time() if now is None else now
    reading = {"at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now)), "apply": apply,
               "clones": [one(Path(c), apply, now, loose_at, packs_at) for c in clones]}
    if apply:
        d = Path(state) if state else state_dir()
        d.mkdir(parents=True, exist_ok=True)
        tmp = d / "reading.json.tmp"
        tmp.write_text(json.dumps(reading, indent=1) + "\n", encoding="utf-8")
        tmp.replace(d / "reading.json")
    return reading


def exit_code(reading):
    if not reading["clones"]:
        return 3
    return 1 if any(r.get("failed") for r in reading["clones"]) else 0


def line(r):
    if r.get("failed"):
        return "FAILED %s: %s" % (r["clone"], r["failed"])
    b = r.get("before", {})
    s = "%s: loose %s, packs %s" % (r["clone"], b.get("count"), b.get("packs"))
    if r.get("packed"):
        a = r["after"]
        s += " -> loose %s, packs %s (%.0f s)" % (a.get("count"), a.get("packs"), r["seconds"])
    elif r.get("would_pack"):
        s += ", would pack"
    gone = r.get("deleted") or r.get("would_delete")
    if gone:
        s += ", %s %d dead tmp file(s)" % ("deleted" if r.get("deleted") else "would delete", len(gone))
    if r.get("hold_wrote"):
        s += ", hold %s %s" % ("wrote" if r["held"] else "would write", ",".join(r["hold_wrote"]))
    return s


def main(argv):
    cmd = argv[0] if argv else "show"
    if cmd == "show":
        clones = timer_clones()
        for c in clones:
            try:
                k = counts(c)
                print("%s: loose %s, packs %s, gc.auto=%s" % (c, k.get("count"), k.get("packs"),
                                                              git(c, "config", "--local", "gc.auto").stdout.strip()))
            except (RuntimeError, subprocess.SubprocessError) as e:
                print("%s: could not look: %s" % (c, e))
        if not clones:
            print("no unit file names a clone under %s (could not look)" % ROOT)
            return 3
        return 0
    if cmd == "hold":
        clones = [Path(p) for p in argv[1:]] or timer_clones()
        bad = 0
        for c in clones:
            try:
                print("%s: %s" % (c, ", ".join(hold(c)) or "held already"))
            except (RuntimeError, subprocess.SubprocessError) as e:
                bad += 1
                print("%s: FAILED %s" % (c, e))
        return 3 if not clones else (1 if bad else 0)
    if cmd == "run":
        reading = run(timer_clones(), apply="--apply" in argv)
        for r in reading["clones"]:
            print(line(r))
        rc = exit_code(reading)
        print({0: "OK", 1: "FAILED: a clone failed", 3: "COULD NOT LOOK: no unit file named a clone"}[rc])
        return rc
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
