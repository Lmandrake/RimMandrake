#!/usr/bin/env python3
"""selftest_tick_live_steward_card_brief: the promises of
design/specs/2026-11-20-tick-live-steward-and-card-brief/boundary.md, one test per promise, each named as the promise
is. The tick waits on its own steward run while that run is live (GimmeSomeSlack read steward_spent at preflight with
the unit running, 2026-11-20), and a brief the tick launches for a by-card item carries the picked option's description
(FlowWorks' fixer was refused three times by gate I3, 2026-11-20). Item
RIMMANDRAKE_FIX_FLOWWORKS_FAULT_LOOP_AND_SLACK_STEWARD_MISREAD. Offline, on temp roots; no claude, unit, bridge or
landing is touched."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="tick_live_card_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "_dispatch")   # never the live dispatcher's state
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
os.environ["RM_REFUSAL_DIR"] = os.path.join(TMP, "_refusals")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "_ops")
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN", "RM_ROLE_UNIT"):
    os.environ.pop(_k, None)
import maturation_autonomy as A     # noqa: E402
import maturation as M              # noqa: E402
import card_capture as CC           # noqa: E402
import detached_helper as DH        # noqa: E402

MOD, VER, UNIT = "GimmeSomeSlack", "0.1.1", "rm-detached-bench-rimmandrake-steward-x-prefl-1"
KEY = "%s|preflight" % VER
CFG = {"steward_cap_tokens": 2_000_000, "fix_cap_tokens": 1_250_000, "max_live": 2, "launch_tries": 3}
CARDED, PLAIN = "RIMMANDRAKE_REBUILD_X_PITS_AS_RELATIVE_TERRAIN", "RIMMANDRAKE_PLAIN_X_NO_CARD"
DESC = ("Why: you said \"That won't do\", and stepped digs are ordinary play. Buys: inner walls and shading at every "
        "height change.")
CARD = {"questions": [{"question": "Where does drawing pits as relative terrain belong?",
                       "picked": [{"label": "In 0.1.0, full rebuild (Recommended)", "description": DESC}],
                       "others": ["Next version entirely"]}]}
EV = os.path.join(TMP, "events")


def _events():
    os.makedirs(EV, exist_ok=True)
    with open(os.path.join(EV, "OWNER.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": CARDED, "verb": "file", "tsn": 1, "card": CARD}) + "\n")
        f.write(json.dumps({"id": PLAIN, "verb": "file", "tsn": 2}) + "\n")


def _booked():
    return {"steward": {KEY: {"item": "RIMMANDRAKE_STEWARD_X_PREFLIGHT_STAGE", "unit": UNIT, "at": 1.0, "cap": 8,
                              "failed": None, "tries": 1, "filed": True}}}


def _row():
    return {"mod": MOD, "aut": "steward", "steward_key": KEY, "steward_kind": "stage", "stage": "preflight"}


def t_live_booked_run_reads_live():
    go, why = A._gate(CFG, _booked(), _row(), 1, VER, live=[UNIT])
    return (not go and why[0] == "live" and UNIT in why[1]), (go, why)


def t_ended_booked_run_stays_spent():
    go, why = A._gate(CFG, _booked(), _row(), 0, VER, live=["rm-other-unit"])
    go2, why2 = A._gate(CFG, _booked(), _row(), 0, VER)
    return (not go and why[0] == "steward_spent" and not go2 and why2[0] == "steward_spent"), (why, why2)


def t_resolve_waits_on_live_steward_at_preflight():
    st = {"mods": {MOD: _booked()}}
    facts = {MOD: {"mod": MOD, "stage": "preflight", "version": VER, "live_units": [UNIT], "ended_runs": []}}
    rows = [{"mod": MOD, "stage": "preflight", "decision": "not_offline", "why": "stands at preflight"}]
    fx = {"open_items": lambda ids: [], "designer_state": lambda m: None, "version_locked": lambda m: True,
          "version_evidence": lambda m: None, "live_endings": lambda ids: {}, "version_bugs": lambda *a, **k: [],
          "exam_gate": lambda m: None}
    rows, la = A.resolve(TMP, CFG, st, facts, rows, [], 100.0, fx)
    A.classify(CFG, st, rows, 100.0)
    r = rows[0]
    return (r.get("decision") == "live" and not r.get("aut") and UNIT in str(r.get("waits_on"))
            and r.get("klass") == "wait" and MOD not in la), {k: r.get(k) for k in
                                                              ("decision", "aut", "waits_on", "klass", "why")}


def t_card_brief_carries_picked_description():
    _events()
    b = A.card_brief(CARDED, "# Road-back fix\n\nFix it.\n", events_dir=EV)
    return (CC.HEADING in b and CC.flatten(CARD, brief=True) in b
            and DH.card_refusal(CARDED, b, events_dir=EV) is None
            and DH.card_refusal(CARDED, "# Road-back fix\n\nFix it.\n", events_dir=EV) is not None), b[-400:]


def t_card_brief_leaves_other_briefs_alone():
    _events()
    plain = "# Road-back fix\n\nFix it.\n"
    carried = plain + "\nThe card: " + DESC + "\n"
    return (A.card_brief(PLAIN, plain, events_dir=EV) == plain
            and A.card_brief(CARDED, carried, events_dir=EV) == carried), "changed"


def t_launch_brief_writes_the_card():
    _events()
    seen = {}

    class R:
        returncode, stdout, stderr = 0, "DETACHED rm-x\n", ""

    def runner(argv, **kw):
        p = argv[argv.index("--brief-file") + 1]
        with open(p, encoding="utf-8") as f:
            seen["brief"] = f.read()
        return R()
    os.environ["MATURATION_BRIEF_DIR"] = os.path.join(TMP, "_briefs")
    was = CC.EVENTS
    CC.EVENTS = EV
    try:
        os.makedirs(M.brief_dir(), exist_ok=True)
        rc, _t, unit = A.launch_brief(CARDED, "# Road-back fix\n\nFix it.\n", "opus", 5, runner=runner)
    finally:
        CC.EVENTS = was
    b = seen.get("brief") or ""
    return (rc == 0 and unit == "rm-x" and DH.card_refusal(CARDED, b, events_dir=EV) is None), b[-300:]


def main():
    tests = [t_live_booked_run_reads_live, t_ended_booked_run_stays_spent, t_resolve_waits_on_live_steward_at_preflight,
             t_card_brief_carries_picked_description, t_card_brief_leaves_other_briefs_alone,
             t_launch_brief_writes_the_card]
    fails = []
    for fn in tests:
        try:
            good, got = fn()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure by name, never a pass
            good, got = False, "%s: %s" % (type(e).__name__, e)
        print("%s  %s%s" % ("PASS" if good else "FAIL", fn.__name__[2:].replace("_", "-"),
                            "" if good else "  got: %s" % str(got)[:600]))
        if not good:
            fails.append(fn.__name__)
    shutil.rmtree(TMP, ignore_errors=True)
    if fails:
        print("FAIL selftest_tick_live_steward_card_brief: %d of %d red" % (len(fails), len(tests)))
        return 1
    print("PASS selftest_tick_live_steward_card_brief: %d tests" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
