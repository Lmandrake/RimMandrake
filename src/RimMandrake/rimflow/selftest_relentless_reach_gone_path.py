#!/usr/bin/env python3
"""A reach probe skips a read path gone from the host (CHECKER_REACH_FIX_OTHER_DARK_SECOND).

The instance: NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK, released as a waiter, inherited its owner ROT_KEPT_ART_JUDGE_FOR_OWNER_
DIGEST's read path /home/mandrake/rm/bench/infrastructure/state/items/ROT_KEPT_ART_JUDGE_FOR_OWNER_DIGEST.md. ROT_KEPT closed,
its file moved to items/closed/, and every probe of the `other` class said "item_prose exit 0: read ...; paths exit 3:
UNREADABLE <that path>": its item_prose grant read fine, yet two tickets were filed and three items stayed blocked. A path
absent on the host cannot be bound (a launch binds with '-' and skips it), so it is no reach the repair lacks. Rows:
  (1) a gone path beside a passing grant: the probe passes, runs no unit for the path, and says it skipped it;
  (2) a gone path alone: nothing was read, so the probe fails, and still runs no unit;
  (3) a present path still goes to the unit (the skip is for absent paths only).
Row 1 fails on the code before the fix (the gone path was read in the unit and came back UNREADABLE)."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R          # noqa: E402
import relentless_wall as W     # noqa: E402

FAILS = []
GONE = "/home/mandrake/rm/bench/infrastructure/state/items/ROT_KEPT_ART_JUDGE_FOR_OWNER_DIGEST_GONE_FIXTURE.md"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def main():
    fx = R.Effects.__new__(R.Effects)
    fx.books = HERE
    units = []
    real_run, real_items, real_profile = subprocess.run, R.Effects._probe_items, W.profile
    box_root = tempfile.mkdtemp(prefix="goneprobe")

    def fake_run(argv, *a, **k):
        if argv and argv[0] == "systemd-run":
            units.append(list(argv))
            # the old code's answer for an absent path, from inside the wall
            gone = [p for p in argv if p == GONE]
            return subprocess.CompletedProcess(argv, 3 if gone else 0, "UNREADABLE %s" % GONE if gone else "read ok", "")
        return real_run(argv, *a, **k)
    subprocess.run = fake_run
    R.Effects._probe_items = lambda self, r, values, store_root: (True, "item_prose exit 0: read tree/items/X.md")
    W.profile = lambda r: {"box_root": box_root}
    W_props = W.props
    W.props = lambda prof, box, extra=(), through_paths=(): []
    try:
        check("fixture path is absent on this host", not os.path.lexists(GONE), GONE)
        good, why = fx.reach_probe({}, [GONE], [], {"sha": "a" * 40}, "/nonexistent-store", grants=[W.ITEM_GRANT])
        check("(1) a gone path beside a passing item_prose grant: the probe passes", good, why)
        check("(1) no unit was run for the gone path", not units, units)
        check("(1) it says it skipped the gone path", "gone from the host" in why and GONE in why, why)
        units.clear()
        good, why = fx.reach_probe({}, [GONE], [], {"sha": "a" * 40}, "/nonexistent-store", grants=[])
        check("(2) a gone path alone: nothing read, the probe fails", not good and "nothing to probe" in why, why)
        check("(2) still no unit", not units, units)
        units.clear()
        good, why = fx.reach_probe({}, [HERE], [], {"sha": "a" * 40}, "/nonexistent-store", grants=[])
        check("(3) a present path goes to the unit", len(units) == 1 and HERE in units[0] and good, (units, why))
    except Exception as e:  # noqa: BLE001 - a crash is a red row
        check("no crash", False, "%s: %s" % (type(e).__name__, e))
    finally:
        subprocess.run, R.Effects._probe_items, W.profile, W.props = real_run, real_items, real_profile, W_props
        os.rmdir(box_root) if os.path.isdir(box_root) and not os.listdir(box_root) else None
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
