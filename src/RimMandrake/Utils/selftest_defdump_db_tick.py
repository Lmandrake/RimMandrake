#!/usr/bin/env python3
"""Selftest of defdump_db_tick.py. One test per promise on design/specs/2026-11-26-defdump-db-tick/boundary.md.

The real `measure build` runs against small fake captures in a temp root, so the staleness verdict is the skill's own,
not a copy. Exit 0 all pass; 1 a test failed; 2 the measure skill is not installed (could not look).
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import defdump_db_tick as T  # noqa: E402
import dump_manifest  # noqa: E402


def capture(root, cid, names=("X",)):
    d = os.path.join(root, "captures", cid)
    os.makedirs(os.path.join(d, "defs"))
    recs = [{"defName": n, "defType": "T", "defTypeFull": "T", "label": n.lower(), "shortHash": 1,
             "modName": "Core", "packageId": "ludeon.rimworld", "fields": {}} for n in names]
    with open(os.path.join(d, "defs", "T.json"), "w") as fh:
        json.dump({"defType": "T", "defTypeFull": "T", "defs": recs, "count": len(recs)}, fh)
    with open(os.path.join(d, "manifest.json"), "w") as fh:
        json.dump({"tool": "RimDefDump", "mode": "all", "capturedUtc": cid[:13] + ":" + cid[14:16] + ":" + cid[17:],
                   "gameVersion": "1.6.test", "modCount": 1,
                   "mods": [{"loadOrder": 1, "name": "Core", "packageId": "ludeon.rimworld"}],
                   "defCounts": {"T": len(recs)}}, fh)
    return d


def recent_id(ago_s=60):
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime(time.time() - ago_s))


class Counting:
    def __init__(self, inner=T.run_build):
        self.inner, self.calls = inner, 0

    def __call__(self, root):
        self.calls += 1
        return self.inner(root)


def t_a_stale_db_is_rebuilt(root):
    capture(root, "2026-01-01T00-00-00Z")
    b = Counting()
    rc, r = T.tick(root, builder=b)                 # absent -> built
    assert rc == 0 and r["state"] == "rebuilt" and b.calls == 1, r
    new = recent_id()
    capture(root, new, names=("X", "Y"))            # a newer capture: the db is now stale
    assert T.db_state(root)[0] == "stale", T.db_state(root)
    rc, r = T.tick(root, builder=b)
    assert rc == 0 and r["state"] == "rebuilt" and b.calls == 2, r
    assert r["newest_capture"] == new and new in r["build"], r
    assert T.db_state(root)[0] == "current"


def t_a_current_db_is_left_alone(root):
    capture(root, "2026-01-01T00-00-00Z")
    T.tick(root)
    b = Counting()
    rc, r = T.tick(root, builder=b)
    assert rc == 0 and r["state"] == "current" and b.calls == 0, r


def t_no_capture_builds_nothing(root):
    b = Counting()
    rc, r = T.tick(root, builder=b)
    assert rc == 0 and r["state"] == "no_capture" and b.calls == 0, r
    assert not os.path.exists(os.path.join(root, T.DB_NAME))
    rc, _ = T.tick(os.path.join(root, "nowhere"), builder=b)
    assert rc == T.COULD_NOT_LOOK and b.calls == 0, "an unreadable root must be could-not-look, not no-capture"


def t_a_failed_build_is_named(root):
    capture(root, "2026-01-01T00-00-00Z")
    rc, r = T.tick(root, builder=lambda _r: (False, "measure build exit 3, no MEASURED line: boom"))
    assert rc == 1 and r["state"] == "build_failed" and "boom" in r["why"], r
    # a builder that claims success yet leaves the db stale is a failure too
    rc, r = T.tick(root, builder=lambda _r: (True, "MEASURED 0 defs (a lie)"))
    assert rc == 1 and r["state"] == "build_failed" and "absent" in r["why"], r
    # the real build on a capture it cannot read prints no MEASURED line and exits non-zero
    bad = os.path.join(root, "captures", "2026-02-01T00-00-00Z")
    os.makedirs(bad)
    open(os.path.join(bad, "manifest.json"), "w").write("{not json")
    ok, line = T.run_build(root)
    assert not ok and "no MEASURED line" in line, line


def t_check_tells_the_cases_apart(root):
    rc, line = T.check(root)
    assert rc == 1 and "never run" in line, line
    open(T.reading_path(), "w").write("{torn")
    rc, line = T.check(root)
    assert rc == 2, line
    capture(root, "2026-01-01T00-00-00Z")
    T.tick(root)
    rc, line = T.check(root)
    assert rc == 0 and "current" in line, line
    rc, line = T.check(root, now=time.time() + T.FRESH_S + 60)
    assert rc == 1 and "not running" in line, line
    capture(root, recent_id(T.GRACE_S + 600))         # a newer capture, older than the grace: red
    rc, line = T.check(root)
    assert rc == 1 and "stale" in line and "grace" in line, line
    capture(root, recent_id(60))                      # a newer one inside the grace: not yet red
    rc, line = T.check(root)
    assert rc == 0 and "grace" in line, line
    os.remove(os.path.join(root, T.DB_NAME))
    rc, line = T.check(root)
    assert rc == 1 and "absent" in line, line
    rc, line = T.check(os.path.join(root, "nowhere"))
    assert rc == 2, line


def main():
    if dump_manifest.skill_scripts() is None:
        print("UNMEASURED: the measuring-large-artifacts skill is not installed, so the real build cannot run")
        return 2
    bad = 0
    tests = (t_a_stale_db_is_rebuilt, t_a_current_db_is_left_alone, t_no_capture_builds_nothing,
             t_a_failed_build_is_named, t_check_tells_the_cases_apart)
    for fn in tests:
        root = tempfile.mkdtemp(prefix="ddbt_")
        os.environ["RM_DEFDUMP_DB_DIR"] = os.path.join(root, "_state")
        os.makedirs(os.environ["RM_DEFDUMP_DB_DIR"])
        try:
            fn(root)
            print("ok    %s" % fn.__name__)
        except Exception as exc:                      # noqa: BLE001
            bad += 1
            print("FAIL  %s: %r" % (fn.__name__, exc))
        finally:
            shutil.rmtree(root, ignore_errors=True)
    print("%d of %d passed" % (len(tests) - bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
