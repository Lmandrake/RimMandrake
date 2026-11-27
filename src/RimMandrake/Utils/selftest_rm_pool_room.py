#!/usr/bin/env python3
"""Selftest of infrastructure/stevedesktop/rm_ssd/rm_pool_room.py (RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_
EIGHTY_GIG): the hourly count of helper runs SteveDesktop's ~/rm disk still holds. A fake pool in a temp dir; the floor
is set relative to the real free space of that dir, so ROOM and SHORT are both reached. Exit 0 green, 1 a red.
    python3 selftest_rm_pool_room.py --rev <sha>   the checks against rm_pool_room.py as commit <sha> holds it
                                                   (the class guard's instance: --rev 87c697b3a3^ is red)"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "infrastructure/stevedesktop/rm_ssd/rm_pool_room.py"
SCRIPT = os.environ.get("RM_POOL_ROOM_UNDER_TEST") or os.path.join(HERE, "..", "..", "..", REL)
FAILS = []


def check(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def run(base, floor):
    env = dict(os.environ, RM_POOL_ROOM_DISK=base, RM_POOL_ROOM_CLONES=os.path.join(base, "clones"),
               RM_POOL_ROOM_KEPT=os.path.join(base, "kept"), RM_POOL_ROOM_STATE=os.path.join(base, "state"),
               RM_POOL_ROOM_STORE=os.path.join(base, "store.git"))
    env.pop("RM_POOL_FLOOR_GB", None)
    if floor is not None:
        env["RM_POOL_FLOOR_GB"] = str(floor)
    r = subprocess.run([sys.executable, SCRIPT], env=env, capture_output=True, text=True, timeout=600)
    try:
        rec = json.load(open(os.path.join(base, "state", "pool_room.json")))
    except (OSError, ValueError):
        rec = {}
    ok_file = os.path.join(base, "state", "pool_room_ok.json")
    return r.returncode, rec, ok_file


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_store(base):
    """A bare store whose HEAD holds 12 MB of text and 30 MB of media: a slim checkout of it is about 12 MB."""
    work = os.path.join(base, "storework")
    os.makedirs(os.path.join(work, "Textures"))
    with open(os.path.join(work, "code.txt"), "wb") as f:
        f.write(os.urandom(12 * 10**6))
    for name in ("Textures/a.png", "b.wav"):
        with open(os.path.join(work, name), "wb") as f:
            f.write(os.urandom(15 * 10**6))
    g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", work]
    for cmd in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "s"]):
        subprocess.run(g + cmd, check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", "--bare", work, os.path.join(base, "store.git")], check=True, capture_output=True)
    shutil.rmtree(work)


def at_rev(rev):
    """Run the checks against rm_pool_room.py as commit `rev` holds it. -> the run's exit code."""
    r = subprocess.run(["git", "-C", HERE, "show", "%s:%s" % (rev, REL)], capture_output=True, text=True)
    if r.returncode:
        print("HARNESS BROKEN: git show %s:%s: %s" % (rev, REL, r.stderr.strip()))
        return 2
    fd, path = tempfile.mkstemp(prefix="poolroom-rev-", suffix=".py", dir=os.path.expanduser("~/.cache"))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(r.stdout)
        return subprocess.run([sys.executable, os.path.abspath(__file__)],
                              env=dict(os.environ, RM_POOL_ROOM_UNDER_TEST=path)).returncode
    finally:
        os.remove(path)


def main():
    if "--rev" in sys.argv:
        return at_rev(sys.argv[sys.argv.index("--rev") + 1])
    base = tempfile.mkdtemp(prefix="poolroom-", dir=os.path.expanduser("~/.cache"))
    try:
        mine = load(SCRIPT, "rm_pool_room")
        sc = load(os.path.join(HERE, "scratch_clone.py"), "scratch_clone")
        check(tuple(getattr(mine, "SLIM_MEDIA", ())) == tuple(sc.SLIM_MEDIA) and mine.SLIM_HEAD == list(sc.SLIM_PATTERNS[:2]),
              "the media a slim clone leaves out are scratch_clone's (SLIM_MEDIA, SLIM_PATTERNS)")
        for i, mb in enumerate((40, 10, 10)):
            c = os.path.join(base, "clones", "c%d.det" % i)
            os.makedirs(os.path.join(c, ".git", "info"))
            with open(os.path.join(c, "blob"), "wb") as f:
                f.write(os.urandom(mb * 10**6))
            if i:                                   # c1, c2: slim clones (scratch_clone.SLIM_PATTERNS), the size a new one is
                with open(os.path.join(c, ".git", "info", "sparse-checkout"), "w") as f:
                    f.write("/*\n!*.png\n!*.jpg\n")
        os.makedirs(os.path.join(base, "clones", "c0.det.lock"))           # a lock, not a clone
        os.makedirs(os.path.join(base, "kept", "rm-treecheck-kept-0"))
        with open(os.path.join(base, "kept", "rm-treecheck-kept-0", "blob"), "wb") as f:
            f.write(os.urandom(30 * 10**6))                                 # one of the 2 machine trees, 30 MB
        free = shutil.disk_usage(base).free / 1e9
        rc, rec, okf = run(base, None)
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK" and "more_clones" not in rec and not os.path.exists(okf),
              "no floor in the environment: COULD NOT LOOK, no count, no ok reading (%s)" % rec.get("why"))
        rc, rec, okf = run(base, round(free - 1.0, 3))
        # 1 GB over the floor, less the largest clone (40 MB) and the missing machine tree (30 MB): 0.93 GB of 10 MB slim
        # clones is about 93 more, never the 23 a count by the largest clone gives
        check(rc == 0 and rec.get("verdict") == "ROOM" and rec.get("clones_now") == 3 and 80 <= rec.get("more_clones", 0) <= 100
              and abs(rec.get("largest_clone_gb", 0) - 0.04) < 0.005 and abs(rec.get("new_clone_gb", 0) - 0.01) < 0.003
              and abs(rec.get("kept_trees_owed_gb", 0) - 0.03) < 0.005 and os.path.exists(okf),
              "1 GB over the floor: ROOM, each new clone counted at a slim clone's size, the second machine tree reserved, "
              "the lock not counted, the ok reading written (%s)" % rec.get("why"))
        os.remove(okf)
        rc, rec, okf = run(base, round(free - 0.1, 3))     # 100 MB above the floor: 3 or so more, short of 10
        check(rc == 1 and rec.get("verdict") == "SHORT" and rec.get("runs_it_holds", 99) < 10 and not os.path.exists(okf),
              "100 MB over the floor: SHORT and no ok reading (%s)" % rec.get("why"))
        rc, rec, okf = run(base, round(free + 1.0, 3))     # under the floor already: no more
        check(rc == 1 and rec.get("more_clones") == 0, "under the floor: 0 more clones (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "clones", "c1.det"))
        shutil.rmtree(os.path.join(base, "clones", "c2.det"))
        rc, rec, okf = run(base, round(free - 1.0, 3))
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK" and "more_clones" not in rec,
              "only a full clone and no store: no slim size to count by, COULD NOT LOOK, never a count by the full "
              "clone (%s)" % rec.get("why"))
        make_store(base)
        rc, rec, okf = run(base, round(free - 1.0, 3))
        # SteveDesktop 2026-11-26 18:58-20:58: the pool held one parked full warm spare (5.1 GB) and the check counted
        # every new clone at 5.1 GB (SHORT, 6 runs). A helper takes that spare and makes it slim (detached_helper.take_clone),
        # so a new clone is a slim checkout of the store's HEAD: about 12 MB here, never the 40 MB full clone
        check(rc == 0 and rec.get("verdict") == "ROOM" and abs(rec.get("new_clone_gb", 0) - 0.01) < 0.003
              and rec.get("new_clone_from") == "store" and 60 <= rec.get("more_clones", 0) <= 80,
              "only a full clone in the pool: a new clone counted at the store's slim checkout, ROOM (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "clones"))
        os.makedirs(os.path.join(base, "clones"))
        rc, rec, okf = run(base, round(free - 1.0, 3))
        # SteveDesktop 2026-11-26 17:57: an empty pool read COULD_NOT_LOOK, and the live promise aged
        check(rc == 0 and rec.get("verdict") == "ROOM" and rec.get("clones_now") == 0 and rec.get("largest_clone_gb") == 0
              and rec.get("new_clone_from") == "store", "an empty pool: counted by the store's slim checkout, ROOM (%s)"
              % rec.get("why"))
        new = (-(-12 * 10**6 // 4096) + 2) * 4096 / 1e9     # the slim checkout: code.txt and 2 folders, a 4 KiB block each
        free = shutil.disk_usage(base).free / 1e9
        rc, rec, okf = run(base, round(free - 0.03 - 9.5 * new, 4))
        # pool_admit subtracts the largest clone from each admission: an empty pool admits its first clone at margin >= 0,
        # then each next one only while margin - its predecessors >= that one, so margin / new of 9.5 admits 9, not 10
        check(rec.get("more_clones") == 9 and rec.get("verdict") == "SHORT",
              "an empty pool with room for 9.5 slim clones: 9 more, SHORT, never the 10 that +1 gives (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "kept"))
        rc, rec, okf = run(base, round(free - 1.0, 3))
        # with no kept tree to size them by, the 2 machine check trees still owed are full checkouts of the store's HEAD
        # (12 MB of text and 30 MB of media here), never the largest clone of an empty pool (0)
        check(rc == 0 and abs(rec.get("kept_trees_owed_gb", 0) - 0.084) < 0.005,
              "no kept tree and an empty pool: the 2 owed check trees reserved at a full checkout each (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "store.git"))
        rc, rec, okf = run(base, 1)
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK", "an empty pool and no store give no size to count by: "
              "COULD NOT LOOK, never a count (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "clones"))
        rc, rec, okf = run(base, 1)
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK", "no pool folder: COULD NOT LOOK (%s)" % rec.get("why"))
    finally:
        shutil.rmtree(base, True)
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED, %d failing" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
