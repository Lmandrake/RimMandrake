#!/usr/bin/env python3
"""selftest_alarm_closed_reopen.py -- OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT: closing an alarm's ticket cannot
silence an unfixed fault (design/RimMandrake/relentless_recovery_plan_2026-11-05.md step 3).

Real rules, real ops_watch.run_alarms: file an alarm, close its item, keep the reading crossed with nothing new and
nothing worse -> the alarm reopens that same item. Before the fix it returned at "nothing new" and stayed silent. Also:
an open item is not reopened, an unread ledger (open_ids None) judges nothing, a token alarm (no item) is untouched,
and a corrupt alarms.json holds filing (B4) and raises ONE fixed incident (ops_watch.alarm_state) in incident.readings.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_alarm_closed_reopen_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
(TMP / "ops").mkdir()
import ops_watch as OW          # noqa: E402
import incident as INC          # noqa: E402

FAILS = []
NOW = 1793050000.0
CLOG = TMP / "conductor_log.md"
RULES = OW.load_rules()
for _t in RULES["targets"]:     # never the real Conductor log
    if _t.get("conductor_log"):
        _t["conductor_log"] = str(CLOG)
OW.mint_name = lambda tag, known, prefix: prefix if prefix.count("_") >= 2 else prefix + "_TEST"
AID = "STEVE_STALL:steve.unowned_stall_min"
KEY = AID.split(":", 1)[1]


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def reset():
    p = OW.ops_dir() / "alarms.json"
    if p.exists():
        p.unlink()


class Bench:
    def __init__(self):
        self.t, self.sent, self.filed = NOW, [], set()

    def filer(self, todo, conf):
        self.sent = list(todo)
        self.filed |= {a["name"] for a in todo if not a.get("note_only")}
        return {a["name"]: None for a in todo}

    def read(self, point, open_ids):
        self.t += 900
        self.sent = []
        return OW.run_alarms({KEY: point}, RULES, self.t, self.filed | {"SOME_ITEM"}, self.filer, open_ids)


def test_closed_item_reopens():
    reset()
    b = Bench()
    cur = b.read(OW.M(45, "min"), None)[AID]
    ok(cur["state"] == "OPEN" and len(b.sent) == 1 and not b.sent[0].get("note_only"), "45 min crosses 30: filed")
    item = cur["item"]
    cur = b.read(OW.M(46, "min"), {item})[AID]
    ok(not b.sent and cur["state"] == "OPEN", "item open, nothing new: silent, as before")
    # the ticket is closed; the reading still stands crossed, no news, no worse
    cur = b.read(OW.M(46, "min"), set())[AID]
    filings = [a for a in b.sent if not a.get("note_only")]
    ok(len(filings) == 1 and filings[0]["name"] == item and filings[0].get("reopen"),
       "item closed, reading still crossed, nothing new: the same item is reopened (was: silent for good)")
    ok(cur["state"] == "OPEN" and cur["item"] == item, "after the reopen the alarm is OPEN on that item again")
    log = (OW.ops_dir() / "alarms_log.jsonl").read_text() if (OW.ops_dir() / "alarms_log.jsonl").exists() else ""
    ok("reopen_closed_still_crossed" in log, "the reopen is logged with its own reason")
    cur = b.read(OW.M(46, "min"), {item})[AID]
    ok(not b.sent, "reopened and open again: silent, no reopen loop")


def test_unread_ledger_judges_nothing():
    reset()
    b = Bench()
    b.read(OW.M(45, "min"), None)
    b.read(OW.M(46, "min"), None)
    ok(not b.sent, "open_ids None (ledger not read): nothing reopened")


def test_clear_after_close_does_not_reopen():
    reset()
    b = Bench()
    item = b.read(OW.M(45, "min"), None)[AID]["item"]
    st = b.read(OW.M(1, "min"), set())
    ok(not [a for a in b.sent if not a.get("note_only")], "closed and the reading cleared: no reopen")
    ok(AID not in st or st[AID].get("state") == "OPEN", "a clear reading takes the clear path, not the reopen")
    del item


def test_corrupt_state_holds_and_raises_one_incident():
    reset()
    (OW.ops_dir() / "alarms.json").write_text("[not an object")
    b = Bench()
    out = b.read(OW.M(45, "min"), None)
    ok(set(out) == {"_alarm_state"} and out["_alarm_state"]["state"] == "UNREADABLE" and not b.sent,
       "corrupt alarms.json: filing held, the state says UNREADABLE (B4)")
    table = INC.load_table()
    status = {"t": NOW, "points": {KEY: {"m": "MEASURED", "v": 45, "class": "sane"}}, "alarms": out}
    bad, fresh, seen = INC.readings(table, status, NOW)
    ok(fresh and "ops_watch.alarm_state" in bad, "incident.readings raises the fixed metric ops_watch.alarm_state")
    ok(sum(1 for k in bad if k.startswith("ops_watch.alarm")) == 1, "exactly one fixed incident metric, not one per alarm")
    rt = INC.route_of(table, "ops_watch.alarm_state")
    ok(rt is not None and rt.get("reader") == "Operations", "the fixed metric routes to Operations")
    status["alarms"] = {}
    bad, fresh, seen = INC.readings(table, status, NOW)
    ok("ops_watch.alarm_state" not in bad and seen.get("ops_watch.alarm_state") is True,
       "readable alarms.json: the fixed metric reads sane, so its incident can close")


if __name__ == "__main__":
    for fn in (test_closed_item_reopens, test_unread_ledger_judges_nothing, test_clear_after_close_does_not_reopen,
               test_corrupt_state_holds_and_raises_one_incident):
        fn()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
