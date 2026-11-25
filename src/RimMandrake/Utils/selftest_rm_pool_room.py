#!/usr/bin/env python3
"""Selftest of infrastructure/stevedesktop/rm_ssd/rm_pool_room.py (RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_
EIGHTY_GIG): the hourly count of helper runs SteveDesktop's ~/rm disk still holds. A fake pool in a temp dir; the floor
is set relative to the real free space of that dir, so ROOM and SHORT are both reached. Exit 0 green, 1 a red."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "..", "..", "infrastructure", "stevedesktop", "rm_ssd", "rm_pool_room.py")
FAILS = []


def check(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def run(base, floor):
    env = dict(os.environ, RM_POOL_ROOM_DISK=base, RM_POOL_ROOM_CLONES=os.path.join(base, "clones"),
               RM_POOL_ROOM_KEPT=os.path.join(base, "kept"), RM_POOL_ROOM_STATE=os.path.join(base, "state"))
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


def main():
    base = tempfile.mkdtemp(prefix="poolroom-", dir=os.path.expanduser("~/.cache"))
    try:
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
        shutil.rmtree(os.path.join(base, "clones"))
        os.makedirs(os.path.join(base, "clones"))
        rc, rec, okf = run(base, 1)
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK", "an empty pool gives no size to count by: COULD NOT "
              "LOOK, never a count (%s)" % rec.get("why"))
        shutil.rmtree(os.path.join(base, "clones"))
        rc, rec, okf = run(base, 1)
        check(rc == 5 and rec.get("verdict") == "COULD_NOT_LOOK", "no pool folder: COULD NOT LOOK (%s)" % rec.get("why"))
    finally:
        shutil.rmtree(base, True)
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED, %d failing" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
