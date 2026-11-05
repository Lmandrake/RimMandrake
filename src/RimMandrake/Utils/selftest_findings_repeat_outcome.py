#!/usr/bin/env python3
"""Guard for RELAPSE_FLOW_FIX_DIED_TWICE: a repeat of a finding signature already decided into an OPEN item is no new
untriaged finding.

The flow incident is the ops_watch alarm flow.untriaged_findings, whose whole answer is findings_fold.no_outcome. A
finding had an outcome only when it was no newer than its signature's decision, so every rerun of a standing failure
re-fired the alarm after an ack had routed it: FLOWWORKS_PUMP_POURS_BACK_FAILS_AA5B4B (2026-11-05T05:20Z) repeated
signature Se09b07... routed into FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS at 04:54Z, and the incident relapsed. The
class rule (findings_fold_rules.json _cover_why): a later finding of a signature whose latest decision handed it to an
item (work, merge, route, an item of the name) has its outcome when that item stood proposed, ready or doing at the
finding's own time; a failure seen once it is built, validated or terminal, or after a retire, memory, retype, undo or
a route to the never-closing lane item, alarms again.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import findings_fold as FF  # noqa: E402

FAILS = []
RULES = FF.load_rules()
SIG_TEXT = "liquid_pump/pump_pours_back FAIL on SteveDesktop: ExpectationFailed: pour mode did not raise the channel: 4.00 -> 4.00"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def fev(name, at):
    return {"id": "FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS", "why": SIG_TEXT, "ts": at,
            "from": "FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS/run-1@steve-targeted"}


FINDS = {"PUMP_FAILS_4E3E60": fev("PUMP_FAILS_4E3E60", "2026-11-05T04:43:41Z"),
         "PUMP_FAILS_AA5B4B": fev("PUMP_FAILS_AA5B4B", "2026-11-05T05:20:22Z")}
NOW = "2026-11-05T06:00:00Z"
DETAIL = SIG_TEXT.split(": ", 1)[1]


def rec(job, name, at):
    """A testq done record naming one finding, as ingest.py leaves it: the finding resolves and signs by its row."""
    return {"job": {"id": job, "mod": "FlowWorks", "item": "FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS"},
            "result": {"outcome": "DONE", "finished": at, "attempt": job + ".a1",
                       "rows": [{"chain": "liquid_pump", "row": "pump_pours_back", "verdict": "FAIL", "detail": DETAIL}]},
            "ingested": {"run": "FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS/run-1@steve-targeted", "findings": [name],
                         "at": at}}


RECS = [rec("J20261105T044341Z-4e3e60", "PUMP_FAILS_4E3E60", FINDS["PUMP_FAILS_4E3E60"]["ts"]),
        rec("J20261105T052022Z-aa5b4b", "PUMP_FAILS_AA5B4B", FINDS["PUMP_FAILS_AA5B4B"]["ts"])]


def outcomes(states, decisions=(), spawns=(), timeline=None):
    raw = FF.fold(FINDS, [], {}, RECS, [], RULES, NOW)["raw"]
    sig = raw["PUMP_FAILS_4E3E60"]["sig"]
    assert raw["PUMP_FAILS_AA5B4B"]["sig"] == sig, "the fixture must be one signature, as it was on the ledger"
    ds = [dict(d, sig=sig, by="BENCH", why="x") for d in decisions]
    try:
        t = FF.fold(FINDS, list(spawns), states, RECS, ds, RULES, NOW, **({"timeline": timeline} if timeline else {}))
    except TypeError as e:                      # a fold with no state timeline: a failed check, not a crash
        check(False, "fold takes the ledger's state timeline (%s)" % e)
        t = FF.fold(FINDS, list(spawns), states, RECS, ds, RULES, NOW)
    return {n: f["outcome"] for n, f in t["raw"].items()}, t["signatures"][sig], t


IT = "FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS"
ROUTE = {"as": "route", "into": IT, "ts": "2026-11-05T04:54:56Z"}
OPEN = {IT: "doing"}

o, s, T1 = outcomes(OPEN, [ROUTE])
check(o == {"PUMP_FAILS_4E3E60": True, "PUMP_FAILS_AA5B4B": True},
      "G1 the instance: AA5B4B repeats a signature routed into an open item, so it has its outcome (got %s)" % o)
check(s["failed_since_decision"] == 1 and s.get("covered_by") == IT,
      "G1 the repeat still counts as a failure since the decision, and the row names its cover")

o, _, _ = outcomes({IT: "done"}, [ROUTE])
check(o["PUMP_FAILS_AA5B4B"] is False and o["PUMP_FAILS_4E3E60"] is True,
      "G2 no timeline, the item terminal now: the repeat alarms (got %s)" % o)
TL_DOING = {IT: [("2026-11-01T00:00:00Z", "ready"), ("2026-11-02T00:00:00Z", "doing"), ("2026-11-05T05:50:00Z", "done")]}
o, _, _ = outcomes({IT: "done"}, [ROUTE], timeline=TL_DOING)
check(o["PUMP_FAILS_AA5B4B"] is True, "G2 a repeat seen while the item stood open keeps its cover after it closed")
TL_DONE = {IT: [("2026-11-02T00:00:00Z", "doing"), ("2026-11-05T05:00:00Z", "done")]}
o, _, _ = outcomes({IT: "done"}, [ROUTE], timeline=TL_DONE)
check(o["PUMP_FAILS_AA5B4B"] is False, "G2 a repeat seen after the item closed alarms: the fix died")
for st in ("built", "validated"):
    o, _, _ = outcomes({IT: st}, [ROUTE], timeline={IT: [("2026-11-02T00:00:00Z", st)]})
    check(o["PUMP_FAILS_AA5B4B"] is False, "G2 a repeat seen while the item stood %s alarms: the claimed fix fails" % st)

o, _, _ = outcomes({"PUMP_POUR_PROOF_FIX_TANK_NOT_DUMP": "ready"},
                   [dict(ROUTE, **{"as": "merge", "into": "PUMP_POUR_PROOF_FIX_TANK_NOT_DUMP"})])
check(o["PUMP_FAILS_AA5B4B"] is True, "G3 a merge into an open item covers the repeat")

o, _, _ = outcomes({}, [ROUTE])
check(o["PUMP_FAILS_AA5B4B"] is False, "G4 a target the ledger does not hold covers nothing")

o, _, _ = outcomes(OPEN, [dict(ROUTE, **{"as": "retire", "into": None})])
check(o["PUMP_FAILS_AA5B4B"] is False, "G5 a retire covers no later failure")

o, _, _ = outcomes(OPEN, [dict(ROUTE, **{"as": "memory", "into": "skills/x.md:1"})])
check(o["PUMP_FAILS_AA5B4B"] is False, "G6 a memory decision covers no later failure")

RETYPE = {"as": "retype", "from": "PUMP_FAILS_4E3E60", "name": "TRACKED", "seat": "BENCH", "ts": "2026-11-05T04:54:56Z",
          "why": "retyped"}
o, _, _ = outcomes(OPEN, spawns=[RETYPE])
check(o["PUMP_FAILS_AA5B4B"] is False and o["PUMP_FAILS_4E3E60"] is True,
      "G7 a retype is its own finding's outcome but covers no repeat (got %s)" % o)

SPAWN = {"as": "work", "from": "PUMP_FAILS_4E3E60", "name": "PUMP_FIX", "seat": "BENCH", "ts": "2026-11-05T04:54:56Z"}
o, _, _ = outcomes({"PUMP_FIX": "doing"}, spawns=[SPAWN])
check(o["PUMP_FAILS_AA5B4B"] is True, "G8 a spawn --from the finding covers repeats while the spawned item is open")

LANE = RULES["lane_item"]
o, _, _ = outcomes({LANE: "doing"}, [dict(ROUTE, into=LANE)])
check(o["PUMP_FAILS_AA5B4B"] is False, "G9 a route to the never-closing lane item covers no repeat")

o, _, _ = outcomes(OPEN, [ROUTE, dict(ROUTE, **{"as": "undo", "into": None, "ts": "2026-11-05T04:55:00Z"})])
check(o == {"PUMP_FAILS_4E3E60": False, "PUMP_FAILS_AA5B4B": False}, "G10 an undo takes the cover back (got %s)" % o)

ITEM = {"as": "item", "from": "PUMP_FAILS_4E3E60", "name": "PUMP_FAILS_4E3E60", "seat": "BENCH",
        "ts": "2026-11-05T04:54:56Z", "why": "an item of that name"}
o, _, _ = outcomes({"PUMP_FAILS_4E3E60": "ready"}, spawns=[ITEM])
check(o["PUMP_FAILS_AA5B4B"] is True, "G11 an open item of the first finding's name covers its repeats")

# end to end: the alarm's own answer over the published table, and an older table with no covered_by still reads
_d = tempfile.mkdtemp()
try:
    evs = [{"event": "finding", "type": "UNTRIAGED", "name": n} for n in FINDS]
    with open(os.path.join(_d, FF.REPORT), "w", encoding="utf-8") as f:
        f.write(FF.render_report(T1))
    check(FF.no_outcome(evs, _d) == set(), "G12 no_outcome over the published table: the covered repeat is not untriaged")
    old = json.loads(json.dumps(T1))
    for row in old["signatures"].values():
        row.pop("covered_by", None)
    with open(os.path.join(_d, FF.REPORT), "w", encoding="utf-8") as f:
        f.write(FF.render_report(old))
    check(FF.read_prev(os.path.join(_d, FF.REPORT))[0] is not None, "G12 a table written before covered_by still reads")
finally:
    shutil.rmtree(_d)

# the timeline read_ledger hands fold: every state an item reached, stamped by the event that moved it
sys.path.insert(0, FF.RIMFLOW)
import model as _m  # noqa: E402


class _It:
    def __init__(self, i, st):
        self.id, self.state = i, st


def _replay(events, observe=None, **k):
    w = type("W", (), {"items": {}})()
    for ev in events:
        if ev.get("event") == "spawn":
            w.items[ev["name"]] = _It(ev["name"], "proposed")
        if ev.get("event") in ("file", "start", "close"):
            w.items[ev["id"]] = _It(ev["id"], {"file": "ready", "start": "doing", "close": "done"}[ev["event"]])
        if observe:
            observe(ev, w, True)
    return w


_evs = [{"event": "file", "id": IT, "ts": "2026-11-01T00:00:00Z"}, {"event": "note", "id": IT, "ts": "2026-11-01T01:00:00Z"},
        {"event": "start", "id": IT, "ts": "2026-11-02T00:00:00Z"}, {"event": "close", "id": IT, "ts": "2026-11-06T00:00:00Z"},
        {"event": "spawn", "name": "PUMP_FIX", "from": "PUMP_FAILS_4E3E60", "ts": "2026-11-05T04:54:56Z"}]
_sr, _sp = _m.read, _m.replay
_m.read, _m.replay = (lambda: _evs), _replay
try:
    _rl = FF.read_ledger(RULES)
    _tl = _rl[3] if len(_rl) > 3 else None
finally:
    _m.read, _m.replay = _sr, _sp
check(_tl == {IT: [("2026-11-01T00:00:00Z", "ready"), ("2026-11-02T00:00:00Z", "doing"), ("2026-11-06T00:00:00Z", "done")],
              "PUMP_FIX": [("2026-11-05T04:54:56Z", "proposed")]},
      "G13 read_ledger's timeline keeps each state change once, with its event's time, a spawned item's too (got %s)" % _tl)
o, _, _ = outcomes({"PUMP_FIX": "proposed"}, spawns=[SPAWN], timeline=_tl or {})
check(o["PUMP_FAILS_AA5B4B"] is True, "G13 an item spawned from the finding and never touched since covers its repeats")

print("\n%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
