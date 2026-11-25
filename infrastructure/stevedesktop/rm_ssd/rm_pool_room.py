#!/usr/bin/env python3
"""rm_pool_room.py - how many helper runs can SteveDesktop's ~/rm disk still hold?
(RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG)

Run by rm-pool-room.timer (systemd --user, hourly), beside rm-ssd-check.timer. Reads the ~/rm disk: its free space,
the pool's disk floor (RM_POOL_FLOOR_GB, set by testcentre_env.sh, the one home of the number), the size of every pool
clone and of the machine's kept check trees (publish.py kept_root). The pool admits a new clone while
free - largest clone - floor >= 0 (scratch_clone.pool_admit), and each one it admits takes a new clone's size, so the
disk still holds
    more = floor(margin / new) + 1   (0 when margin < 0),   margin = free - floor - largest - owed
more clones. `new` is the smallest slim clone in the pool (a helper's clone is slim: detached_helper.clone_full), else
the largest clone. `owed` is the machine's kept check trees not made yet (KEPT_TREES of them, each the size of the largest
one there, else of the largest clone): the first publishes make them, and they stay.
Writes ~/.local/state/rm-ssd/pool_room.json on every run, with one verdict:
    ROOM            the clones there now plus `more` reach TARGET_RUNS
    SHORT           they do not
    COULD_NOT_LOOK  a reading could not be taken (the cause is in `why`): never a count
and writes pool_room_ok.json ONLY on ROOM, so the live promise
`unit=rm-pool-room.timer reading=/home/mandrake/.local/state/rm-ssd/pool_room_ok.json max_age=3h`
goes stale, and breaks, as soon as the disk cannot hold TARGET_RUNS. Exit 0 ROOM, 1 SHORT, 5 could not look.
Env overrides (the selftest): RM_POOL_ROOM_DISK, RM_POOL_ROOM_CLONES, RM_POOL_ROOM_KEPT, RM_POOL_ROOM_STATE.
"""
import json
import math
import os
import subprocess
import sys
import time

DISK = os.environ.get("RM_POOL_ROOM_DISK", "/home/mandrake/rm")
CLONES = os.environ.get("RM_POOL_ROOM_CLONES", os.path.join(DISK, "relentless", "clones"))
KEPT = os.environ.get("RM_POOL_ROOM_KEPT", os.path.join(DISK, "treecheck-kept"))
STATE = os.environ.get("RM_POOL_ROOM_STATE", os.path.expanduser("~/.local/state/rm-ssd"))
TARGET_RUNS = 10    # the owner's goal (2026-11-25): SteveDesktop's allocator allows 10 runs; the disk must hold them
KEPT_TREES = int(os.environ.get("RM_TREECHECK_SLOTS") or 2)     # publish.py kept_n(): one per tree-check slot
SLIM_HEAD = ["/*", "!*.png"]    # the first lines of scratch_clone.SLIM_PATTERNS, as a slim clone's sparse-checkout holds them
DU_TIMEOUT_S = 1800  # budget: danger=a du that never returns holds the timer's oneshot unit active, so no later run fires; evidence=Windows-side calls from SteveDesktop have hung (RUNBOOK); longest=1.2s (one measured run, du of a 1.45 GB slim clone on Archmagi, 2026-11-25); one du per clone, so 1800 s is far over 10 times any one


def is_slim(clone):
    try:
        with open(os.path.join(clone, ".git", "info", "sparse-checkout")) as f:
            return f.read().split()[:2] == SLIM_HEAD
    except OSError:
        return False


def du_bytes(path):
    """-> allocated bytes of path (du -s, hard links counted once), or raises."""
    r = subprocess.run(["du", "-s", "--block-size=1", path], capture_output=True, text=True, timeout=DU_TIMEOUT_S)
    if r.returncode != 0 or not r.stdout.split():
        raise RuntimeError("du %s rc=%d: %s" % (path, r.returncode, r.stderr.strip()[-200:]))
    return int(r.stdout.split()[0])


def measure():
    rec = {"schema": "steve.pool_room/1", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "disk": DISK,
           "target_runs": TARGET_RUNS}
    floor = os.environ.get("RM_POOL_FLOOR_GB", "").strip()
    try:
        rec["floor_gb"] = float(floor)
    except ValueError:
        return dict(rec, verdict="COULD_NOT_LOOK", why="RM_POOL_FLOOR_GB is %r, not a number: the unit sources "
                    "testcentre_env.sh, which sets it" % floor)
    try:
        st = os.statvfs(DISK)
    except OSError as e:
        return dict(rec, verdict="COULD_NOT_LOOK", why="statvfs %s: %s" % (DISK, e))
    rec["free_gb"] = round(st.f_bavail * st.f_frsize / 1e9, 2)
    rec["size_gb"] = round(st.f_blocks * st.f_frsize / 1e9, 2)
    try:
        names = sorted(n for n in os.listdir(CLONES) if os.path.isdir(os.path.join(CLONES, n, ".git")))
    except OSError as e:
        return dict(rec, verdict="COULD_NOT_LOOK", why="the pool %s cannot be listed: %s" % (CLONES, e))
    try:
        sizes = {n: du_bytes(os.path.join(CLONES, n)) for n in names}
        kept = sorted(n for n in os.listdir(KEPT) if not n.endswith(".lock")) if os.path.isdir(KEPT) else []
        rec["kept_trees"] = {n: round(du_bytes(os.path.join(KEPT, n)) / 1e9, 2) for n in kept}
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        return dict(rec, verdict="COULD_NOT_LOOK", why="a size could not be read: %s: %s" % (type(e).__name__, e))
    rec["clones"] = {n: round(b / 1e9, 2) for n, b in sizes.items()}
    rec["clones_now"] = len(names)
    largest = max(sizes.values()) / 1e9 if sizes else 0.0
    slim = [b / 1e9 for n, b in sizes.items() if is_slim(os.path.join(CLONES, n))]
    new = min(slim) if slim else largest
    tree = max(rec["kept_trees"].values()) if rec["kept_trees"] else largest
    owed = max(0, KEPT_TREES - len(rec["kept_trees"])) * tree
    rec.update(largest_clone_gb=round(largest, 2), new_clone_gb=round(new, 2), kept_trees_owed_gb=round(owed, 2))
    margin = rec["free_gb"] - rec["floor_gb"] - largest - owed
    if margin < 0:
        more = 0
    elif new <= 0:
        more = None     # no clone to size a new one by: the count is unknown, never infinite
    else:
        more = int(math.floor(margin / new)) + 1
    rec["more_clones"] = more
    if more is None:
        return dict(rec, verdict="COULD_NOT_LOOK", why="the pool holds no clone, so no clone size is known to count by "
                    "(free %.1f GB, floor %.1f GB)" % (rec["free_gb"], rec["floor_gb"]))
    rec["runs_it_holds"] = len(names) + more
    ok = rec["runs_it_holds"] >= TARGET_RUNS
    rec["verdict"] = "ROOM" if ok else "SHORT"
    rec["why"] = ("%d clones now + %d more = %d runs %s %d: %.1f GB free, floor %.1f GB, largest clone %.2f GB, a new "
                  "clone %.2f GB, machine check trees still owed %.1f GB"
                  % (len(names), more, rec["runs_it_holds"], ">=" if ok else "<", TARGET_RUNS, rec["free_gb"],
                     rec["floor_gb"], largest, new, owed))
    return rec


def write(name, rec):
    os.makedirs(STATE, exist_ok=True)
    tmp = os.path.join(STATE, name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=1)
    os.replace(tmp, os.path.join(STATE, name))


def main():
    rec = measure()
    write("pool_room.json", rec)
    if rec["verdict"] == "ROOM":
        write("pool_room_ok.json", rec)
    print("%s %s" % (rec["verdict"], rec.get("why", "")))
    return {"ROOM": 0, "SHORT": 1}.get(rec["verdict"], 5)


if __name__ == "__main__":
    sys.exit(main())
