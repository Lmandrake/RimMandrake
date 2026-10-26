#!/usr/bin/env python3
"""Selftest for the daily metrics file (modcheck/metrics.py, MODCHECK_METRICS_BUILD_DAILY_WASTE; plan
design/RimMandrake/test_orchestration_two_machines_2026-10-25.md section 5). Offline: every file it reads or writes is
under a temp dir (gate.SHEET_DIR is pointed there for the duration).

Reds on: a would_skip chain under fix/guard not counted as waste, or under sweep not counted as budgeted; an offline
chain run live not counted as waste; a chain with no gate stamp counted as anything but unclassified; a skipped chain
counted as executed minutes or its record's body time not counted as saved; a run of another day counted in the day;
the 6 h targeted window ignoring its 20 classified-minute floor or missing the worst window; a testq result's wall
time, load overhead or request-to-decision minutes wrong; a sheet a result carries counted twice in its lane; a miss
in a fetched run not alarmed, not appended to SHEET_DIR's gate_misses.jsonl, or appended twice on a second pass; the
day-level alarms not firing just above their thresholds or firing at them; the file not landing at <out>/<day>.json.
"""
import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gate  # noqa: E402
import metrics  # noqa: E402

FAILS = []
DAY = datetime.date(2026, 10, 25)


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def _comp(name, verdict="PASS"):
    return {"name": name, "verdict": verdict, "detail": "", "execution": "ran", "validity": None}


def _g(action, why="", key="k", record=None, inputs_known=True):
    return {"action": action, "why": why, "key": key, "inputs_known": inputs_known, "record": record or {}}


def _w(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def build(root):
    local = os.path.join(root, "sheets")
    testq = os.path.join(root, "testq")
    remote = os.path.join(testq, "results", "J20261025T195000Z-ab12")
    rec_a = {"file": "ModA_20261024T100000Z.json", "body_s": 600}
    rec_d = {"file": "ModA_20261024T100000Z.json", "body_s": 120}
    _w(os.path.join(local, "ModA_20261025T180000Z.json"), {"mod": "ModA", "stamp": "20261025T180000Z", "summary": {
        "host": "lane1", "offline_chains": ["off"], "gate": {"purpose": "fix"}, "chains": [
            {"name": "a", "phase_s": {"body": 600.0}, "gate": _g(gate.WOULD, "known good", record=rec_a)},
            {"name": "b", "phase_s": {"hold": 200.0, "body": 1000.0}, "gate": _g(gate.RUN, "no record")},
            {"name": "c", "phase_s": {"body": 300.0}},
            {"name": "d", "phase_s": {"body": 0.0}, "gate": _g(gate.SKIP, "known good", record=rec_d)},
            {"name": "m", "phase_s": {"body": 120.0}, "gate": _g(gate.RUN, "manifest: reads files", key=None,
                                                                 inputs_known=False)},
            {"name": "off", "phase_s": {"body": 60.0}, "gate": _g(gate.RUN, "no record")}]}})
    _w(os.path.join(local, "ModA_20261024T120000Z.json"), {"mod": "ModA", "stamp": "20261024T120000Z", "summary": {
        "host": "lane1", "gate": {"purpose": "fix"}, "chains": [
            {"name": "a", "phase_s": {"body": 6000.0}, "gate": _g(gate.WOULD, "known good")}]}})
    _w(os.path.join(remote, "ModB_20261024T090000Z.json"), {"mod": "ModB", "stamp": "20261024T090000Z", "summary": {
        "chains": [{"name": "f", "components": [_comp("r1")]}, {"name": "e", "components": [_comp("r1")]}]}})
    rec_b = {"file": "ModB_20261024T090000Z.json", "body_s": 300}
    _w(os.path.join(remote, "ModB_20261025T200000Z.json"), {"mod": "ModB", "stamp": "20261025T200000Z", "summary": {
        "host": "steve", "gate": {"purpose": "sweep"}, "chains": [
            {"name": "e", "phase_s": {"body": 1800.0}, "components": [_comp("r1")],
             "gate": _g(gate.WOULD, "known good", record=rec_b)},
            {"name": "f", "phase_s": {"body": 300.0}, "components": [_comp("r1", "FAIL")],
             "gate": _g(gate.WOULD, "known good", key="kf", record=rec_b)}]}})
    _w(os.path.join(testq, "jobs", "J20261025T195000Z-ab12.json"),
       {"schema": "testq.job/1", "id": "J20261025T195000Z-ab12"})
    _w(os.path.join(remote, "result.json"), {
        "schema": "testq.result/1", "job": "J20261025T195000Z-ab12", "host": "steve", "outcome": "DONE",
        "started": "2026-10-25T19:55:00Z", "finished": "2026-10-25T20:00:00Z",
        "phase_s": {"sync": 30, "load": 90, "run": 180},
        "artifacts": [{"path": "results/J20261025T195000Z-ab12/ModB_20261025T200000Z.json"}]})
    _w(os.path.join(testq, "metrics", "2026-10-24.json"), {"schema": "testq.result/1", "job": "Jx"})
    return local, testq


def near(a, b):
    return a is not None and abs(a - b) < 0.051


def t_compute(root):
    local, testq = build(root)
    _, end = metrics.day_bounds(DAY)
    m = metrics.compute(DAY, sheet_dirs=[local], testq_root=testq, now=end)
    aw, tg = m["all_work"], m["targeted"]
    ok(sorted(m["runs"]) == ["ModA_20261025T180000Z.json", "ModB_20261025T200000Z.json"],
       "only the day's runs count (the 2026-10-24 run and the metrics folder are out)", m["runs"])
    ok(near(tg["minutes"]["waste"], 11.0) and near(tg["minutes"]["useful"], 20.0)
       and near(tg["minutes"]["unclassified"], 7.0) and near(tg["waste"], 0.355),
       "targeted: would_skip under fix (10) + offline run live (1) is waste; RUN no-record (20) useful; no stamp "
       "(5) + manifest gap (2) unclassified", tg)
    ok(near(aw["minutes"]["budgeted"], 35.0) and near(aw["waste"], round(11 / 66.0, 3))
       and near(aw["unclassified_share"], round(7 / 73.0, 3)),
       "all-work: would_skip under sweep (30 + 5) is budgeted, not waste", aw)
    ok(aw["untimed_chains"] == 0, "every chain here carries phase_s: none untimed", aw)
    ok(near(aw["minutes"]["saved"], 2.0) and m["gate"]["skipped"] == 1 and m["gate"]["would_skip"] == 3,
       "a skipped chain costs nothing and saves its record's body time", (aw["minutes"], m["gate"]))
    w = m["targeted_worst_6h"]
    ok(w is not None and near(w["waste"], 0.355) and w["classified_min"] >= 20,
       "the worst 6 h targeted window is found, above the 20-minute floor", w)
    kinds = [a["kind"] for a in m["alarms"]]
    ok("targeted_waste_6h" in kinds and "all_waste_day" not in kinds and "unclassified_day" not in kinds,
       "alarms: targeted 6 h fires (35% > 20%); all-work (17%) and unclassified (10%) do not", m["alarms"])
    ok(len(m["gate_misses"]) == 1 and m["gate_misses"][0]["detail"].startswith("f/r1: FAIL now")
       and kinds.count("gate_miss") == 1, "a would_skip chain that FAILs now is a miss and raises one alarm",
       m["gate_misses"])
    om = gate.open_misses([gate.SHEET_DIR])
    ok(list(om) == [("ModB", "f")] and om[("ModB", "f")]["key"] == "kf",
       "a miss in a fetched run is appended to this host's SHEET_DIR, so its gate stops skipping the chain", om)
    ok(m["gate"]["open_misses"] == ["ModB/f"], "the file lists the open misses", m["gate"])
    st = m["by_lane"].get("steve", {})
    l1 = m["by_lane"].get("lane1", {})
    ok(near(st.get("busy_min"), 5.0) and near(st.get("load_overhead_min"), 2.0) and st.get("attempts") == 1,
       "lane steve: the result's wall time (5 min, not its sheet's 35 chain minutes again) and load overhead", st)
    ok(near(l1.get("busy_min"), 38.0) and near(l1.get("utilisation"), round(38 / 1440.0, 3)),
       "lane lane1: an unlinked local sheet adds its chain minutes; utilisation over the day", l1)
    rd = m["request_to_decision_min"]
    ok(rd["n"] == 1 and near(rd["p50"], 10.0), "request to decision: job id stamp to result finished", rd)
    m2 = metrics.compute(DAY, sheet_dirs=[local], testq_root=testq, now=end)
    lines = [r for r in gate._all_miss_lines([gate.SHEET_DIR]) if r.get("event") == "miss"]
    ok(len(lines) == 1 and len(m2["gate_misses"]) == 1, "a second pass does not append the miss again", lines)
    p = metrics.write(m, os.path.join(testq, "metrics"))
    with open(p, encoding="utf-8") as f:
        back = json.load(f)
    ok(os.path.basename(p) == "2026-10-25.json" and back["schema"] == "modcheck.metrics/1",
       "the file lands at <out>/<day>.json", p)


def t_alarms():
    th = dict(metrics.THRESHOLDS)

    def mk(waste, uns, worst=None):
        return {"thresholds": th, "targeted_worst_6h": worst, "gate_misses": [],
                "all_work": {"waste": waste, "unclassified_share": uns, "classified_min": 100.0, "executed_min": 100.0,
                             "minutes": {"waste": 0.0, "unclassified": 0.0}}}
    ok(metrics.alarms(mk(0.25, 0.30, {"waste": 0.20, "end": "x", "classified_min": 20.0})) == [],
       "alarms: exactly at a threshold does not fire")
    got = [a["kind"] for a in metrics.alarms(mk(0.251, 0.301, {"waste": 0.201, "end": "x", "classified_min": 20.0}))]
    ok(got == ["targeted_waste_6h", "all_waste_day", "unclassified_day"], "alarms: just above each threshold fires",
       got)
    ok(metrics.alarms(mk(None, None)) == [], "alarms: a day with no classified minutes raises nothing")
    t = metrics.tally([{"class": "unclassified", "min": 0.0, "saved_min": 0.0, "untimed": True}])
    ok(t["untimed_chains"] == 1 and t["executed_min"] == 0.0, "a chain with no phase_s is counted as untimed", t)
    recs = [{"t": 1000.0 + i, "purpose": "fix", "class": "waste", "min": 1.0, "saved_min": 0.0} for i in range(19)]
    ok(metrics.worst_window(recs, 0, 1e9) is None, "the 6 h window needs 20 classified minutes (19 all-waste is none)")
    recs.append({"t": 2000.0, "purpose": "guard", "class": "useful", "min": 1.0, "saved_min": 0.0})
    w = metrics.worst_window(recs, 0, 1e9)
    ok(w is not None and near(w["waste"], 0.95), "20 classified minutes in the window: 19/20 waste", w)


def main():
    root = tempfile.mkdtemp(prefix="metrics_selftest_")
    old_sheet, old_env = gate.SHEET_DIR, os.environ.pop(gate.ENV_HISTORY, None)
    gate.SHEET_DIR = os.path.join(root, "own_sheets")
    os.makedirs(gate.SHEET_DIR)
    try:
        for t in (t_compute, t_alarms):
            try:
                t(root) if t is t_compute else t()
            except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
                import traceback
                traceback.print_exc()
                ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    finally:
        gate.SHEET_DIR = old_sheet
        if old_env is not None:
            os.environ[gate.ENV_HISTORY] = old_env
        shutil.rmtree(root, ignore_errors=True)
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
