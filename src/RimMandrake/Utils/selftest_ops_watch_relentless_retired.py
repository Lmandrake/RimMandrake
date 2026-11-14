#!/usr/bin/env python3
"""selftest_ops_watch_relentless_retired.py — a retired Relentless belt reads retired, not blind.

The owner retired Relentless on 2026-11-13 ("stop those processes such that there's nothing to resume";
design/RimMandrake/retired_loops_2026-11-13.md): rm-relentless.timer is masked and listed in deadman_check's
live_retired.txt. Before this, ops_watch's c_relentless read the silent store as an outage: RELENTLESS_BLIND,
RELENTLESS_BOOKS_STALE, the churn-item alarms and the work_belt incident stayed OPEN for good (an absent key holds).
This test, on temp dirs and a temp live_retired.txt:
  - the real store with the timer listed retired: every relentless reading is UNMEASURED and judged_by relentless.retired,
    relentless.retired reads MEASURED 1, and an item whose churn alarm alarms.json holds gets its key too;
  - a real ops_watch pass on the REAL rules: the blind alarm a missing store raised clears after clear_passes retired
    passes (judged elsewhere is a clear reading, not a hold), and nothing new files;
  - not retired: a store elsewhere (a selftest's RELENTLESS_ROOT), or the line absent, or live_retired.txt unreadable;
  - incident.readings counts a judged_by point sane, so the incident on these metrics can close by readings.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
FAILS = []


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def main():
    import ops_watch as ow
    import incident
    tmp = Path(tempfile.mkdtemp(prefix="ow_rl_retired_"))
    root = tmp / "relentless"
    (root / "store").mkdir(parents=True)
    retired = tmp / "live_retired.txt"
    retired.write_text("unit=rm-other.timer\nunit=rm-relentless.timer   # retired, owner 2026-11-13\n")
    saved = {k: os.environ.get(k) for k in ("RELENTLESS_ROOT", "RM_OPS_WATCH_DIR")}
    saved_home, saved_file = ow.RL_HOME, ow.RL_RETIRED_FILE
    ops = tmp / "ops"
    ops.mkdir()
    os.environ["RM_OPS_WATCH_DIR"] = str(ops)
    os.environ.pop("RELENTLESS_ROOT", None)
    rules = ow.load_rules()
    for t in rules["targets"]:
        if t.get("conductor_log"):
            t["conductor_log"] = str(tmp / "conductor_log.md")
    filed = []

    def filer(todo, conf):
        filed.extend(a["name"] for a in todo)
        return {a["name"]: None for a in todo}

    def one_pass(now):
        return ow.run(now=now, rules=json.loads(json.dumps(rules)), filer=filer, families=["relentless"])["alarms"]

    try:
        ow.RL_HOME, ow.RL_RETIRED_FILE = str(root), str(retired)
        rules["relentless"]["root"] = str(root)
        now = ow.epoch("2026-11-13T23:00:00Z")

        # retired: the readings
        (ops / "alarms.json").write_text(json.dumps({"CHURN_ITEM:relentless.churn_item.WIDGET_ABCD": {"state": "OPEN"}}))
        pts = ow.COLLECTORS["relentless"](now, rules, {})
        p = pts.get(ow.RL_RETIRED) or {}
        ok(p.get("m") == "MEASURED" and p.get("v") == 1, "retired: relentless.retired reads MEASURED 1", p)
        b = pts.get("relentless.blind") or {}
        ok(b.get("m") == "MEASURED" and b.get("v") == 0 and b.get("judged_by") == ow.RL_RETIRED,
           "retired: relentless.blind reads 0 (no source is expected), judged by relentless.retired", b)
        rest = {k: v for k, v in pts.items() if k not in (ow.RL_RETIRED, "relentless.blind")}
        ok(rest and all(v.get("m") == "UNMEASURED" and v.get("judged_by") == ow.RL_RETIRED for v in rest.values()),
           "retired: every other relentless reading is UNMEASURED and judged by relentless.retired", rest)
        need = set(ow.RL_KEYS + ow.RL_RANGES + ow.CHURN_KEYS) | {"relentless.books_behind_min", "relentless.live_measured_pct",
                                                                 "relentless.churn_item.WIDGET_ABCD"}
        ok(need <= set(pts), "retired: the belt keys, the churn keys and the held churn item's key are all there",
           sorted(need - set(pts)))
        ok(not any(ow.target_state(pts, rules).values()), "retired: no alarm target on these readings crosses or holds",
           {k: v for k, v in ow.target_state(pts, rules).items() if v is not False})
        (ops / "alarms.json").unlink()

        # not retired
        retired.write_text("unit=rm-other.timer\n")
        ok(not ow.rl_retired(rules["relentless"]), "the timer not listed: not retired")
        retired.write_text("not a subject line\n")
        ok(not ow.rl_retired(rules["relentless"]), "live_retired.txt unreadable: not retired (an outage stays an outage)")
        retired.write_text("unit=rm-relentless.timer\n")
        os.environ["RELENTLESS_ROOT"] = str(tmp / "elsewhere")
        ok(not ow.rl_retired(rules["relentless"]), "a store elsewhere is never retired")
        os.environ.pop("RELENTLESS_ROOT", None)
        ok(ow.rl_retired(rules["relentless"]), "the real store with the line: retired")

        # a real pass: a missing store alarms blind; once retired it clears after clear_passes
        retired.write_text("unit=rm-other.timer\n")
        a = one_pass(now)
        blind = [aid for aid, s in a.items() if aid.endswith(":relentless.blind") and (s or {}).get("state") == "OPEN"]
        ok(blind, "not retired, empty store: the blind alarm opens", sorted(a))
        retired.write_text("unit=rm-relentless.timer\n")
        n = next(v["clear_passes"] for v in rules.values() if isinstance(v, dict) and "clear_passes" in v)
        before = len(filed)
        for i in range(1, n + 1):
            a = one_pass(now + 900 * i)
        still = [aid for aid in blind if (a.get(aid) or {}).get("state") in ("OPEN", "PENDING")]
        ok(blind and not still, "retired: the blind alarm clears after %d passes" % n, {b: a.get(b) for b in blind})
        ok(not [f for f in filed[before:] if not f.startswith("note:")], "retired: nothing new files (a clear note only)",
           filed[before:])

        # incident.readings: a judged_by point is sane
        status = {"t": now, "alarms": {}, "points": {
            "relentless.blind": {"m": "UNMEASURED", "class": None, "judged_by": ow.RL_RETIRED},
            ow.RL_RETIRED: {"m": "MEASURED", "v": 1},
            "relentless.why": {"m": "UNMEASURED", "class": None}}}
        table = {"policy": {"status_max_age_min": 60}}
        bad, fresh, seen = incident.readings(table, status, now)
        ok(fresh and seen.get("relentless.blind") is True and "relentless.blind" not in bad,
           "incident: a reading judged by relentless.retired is sane", (bad, seen))
        ok(seen.get("relentless.why") is False, "incident: an unmeasured reading judged by nothing is still not sane", seen)
    finally:
        ow.RL_HOME, ow.RL_RETIRED_FILE = saved_home, saved_file
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("FAIL %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
