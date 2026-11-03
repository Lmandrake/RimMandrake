#!/usr/bin/env python3
"""selftest_ops_watch_tmp.py — the /tmp tmpfs reading and its alarm (TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP).

A temp dir stands in for /tmp through RM_OPS_DISKS; the alarm rows are the real ones in ops_watch_rules.json.
Proves: /tmp is a default disk; c_disk reads tmp free GB and used percent; both alarm rows exist under the one fixed
item id and are well formed; each crosses on its own line and clears below it; an unreadable /tmp holds, never clears.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    import ops_watch as ow
    saved = os.environ.pop("RM_OPS_DISKS", None)
    try:
        ok(ow.disk_mounts().get("tmp") == "/tmp", "/tmp is a default disk")
    finally:
        if saved is not None:
            os.environ["RM_OPS_DISKS"] = saved
    td = tempfile.mkdtemp(prefix="selftest_ops_watch_tmp_")
    os.environ["RM_OPS_DISKS"] = "tmp=%s" % td
    pts = ow.c_disk(0, {}, {})
    ok(ow.num(pts.get("disk.tmp_free_gb", {})) is not None, "tmp free GB is MEASURED")
    pct = ow.num(pts.get("disk.tmp_used_pct", {}))
    ok(pct is not None and 0 <= pct <= 100, "tmp used percent is MEASURED (%s)" % pct)
    os.environ["RM_OPS_DISKS"] = "tmp=/no/such/tmp_ops_watch"
    bad = ow.c_disk(0, {}, {})
    ok(bad["disk.tmp_used_pct"].get("m") != "MEASURED", "an unreadable /tmp is UNMEASURED")
    os.rmdir(td)

    rules = ow.load_rules()
    rows = [t for t in ow.good_targets(rules) if t["key"].startswith("disk.tmp_")]
    ok({t["key"] for t in rows} == {"disk.tmp_free_gb", "disk.tmp_used_pct"} and all(t.get("alarm") for t in rows),
       "both /tmp rows are well-formed alarms")
    ok({t.get("name") for t in rows} == {"OPS_TMP_DRAIN_RESTORE"}, "one fixed item id for both lines")

    def state(free, used):
        p = {"disk.tmp_free_gb": ow.M(free, "GB"), "disk.tmp_used_pct": ow.M(used, "%")}
        return ow.target_state(p, rules)
    ok(state(3.9, 50)["TMP_FULL:disk.tmp_free_gb"] is True, "under 4 GB free crosses")
    ok(state(10, 81)["TMP_FULL:disk.tmp_used_pct"] is True, "over 80% used crosses")
    s = state(10, 50)
    ok(s["TMP_FULL:disk.tmp_free_gb"] is False and s["TMP_FULL:disk.tmp_used_pct"] is False, "a roomy /tmp is clear")
    s = ow.target_state({"disk.tmp_free_gb": ow.U("unreadable"), "disk.tmp_used_pct": ow.U("unreadable")}, rules)
    ok(s["TMP_FULL:disk.tmp_free_gb"] is None and s["TMP_FULL:disk.tmp_used_pct"] is None, "UNMEASURED holds")
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
