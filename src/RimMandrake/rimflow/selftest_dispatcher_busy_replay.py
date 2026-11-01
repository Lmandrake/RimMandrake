#!/usr/bin/env python3
"""BUSY_SEAT_FIX_WAITING_COUNTS_AS_WORK: replays FOUNDRY's 2026-11-01 stall through the real tx_summary and decide().
The fixture keeps the record shapes of session a4a9f1ca: an end_turn, its stop-hook system records, a queued line, and
nothing else for the 66 minutes from 14:26 to 15:32. `claude agents` read busy all that time, because a helper lived.
Old build: no ring in the span. This build: the ring goes out, and the ops_watch idle clock would have a ring to read."""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispatcher as D      # noqa: E402
import seat_restart as SR   # noqa: E402


def at(hms):
    return datetime.strptime("2026-11-01T%sZ" % hms, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def iso(hms):
    return "2026-11-01T%s.000Z" % hms


RECORDS = [
    {"type": "user", "timestamp": iso("14:25:59"), "message": {"role": "user", "content": "<task-notification>"}},
    {"type": "assistant", "timestamp": iso("14:26:04"),
     "message": {"role": "assistant", "stop_reason": "end_turn", "content": [{"type": "text", "text": "done"}]}},
    {"type": "system", "subtype": "stop_hook_summary", "timestamp": iso("14:26:04")},
    {"type": "system", "subtype": "turn_duration", "timestamp": iso("14:26:04")},
]


def replay(block):
    sch = D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json"))
    sch["seats"] = {"FOUNDRY": dict(sch["seats"]["FOUNDRY"], clone="/nonexistent")}
    sch.pop("seat_restart", None)
    sch.pop("busy_waiting", None)
    if block:
        sch["busy_waiting"] = block
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "a4a9f1ca.jsonl")
        with open(path, "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in RECORDS)
        session = {"name": "AGENT FOUNDRY", "status": "busy", "sessionId": "a4a9f1ca", "kind": "interactive", "pid": 1}
        o = {"paused": None, "agents": {"state": "MEASURED", "sessions": [session]},
             "peek": lambda seat: {"id": "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT", "needs": "offline"},
             "events": lambda seat, since: [], "consumed": lambda seat, rid: None,
             "armed": lambda seat: {"pid": 4242}, "alive": lambda pid: True,
             "seat_restart": {"tx": lambda seat, s: SR.tx_summary(path, peers=[]),
                              "helpers": lambda seat, s: [{"id": "agent-a8222e00902715286", "alive": True}]}}
        st, rings, t = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, [], at("14:26:58")
        while t < at("15:32:44"):
            rings += [(t, a) for a in D.decide(sch, st, o, t, True) if a["do"] == "ring"]
            t += sch["tick_s"]
        return sch, rings


def main():
    live = D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json"))["busy_waiting"]
    _, old = replay(None)
    _, new = replay(live)
    ok = True
    for good, what in ((not old, "without the rule the replay rings nobody (the defect reproduced)"),
                       (len(new) >= 1, "with the shipped rule the window that read busy is rung"),
                       (new and new[0][0] - at("14:26:04") <= live["turn_s"] + 300,
                        "the first ring comes within turn_s + 5 min of the ended turn"),
                       (new and new[0][1]["ticket"] == "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT", "the ring names the ready item")):
        print("%s %s" % ("PASS" if good else "FAIL", what))
        ok = ok and bool(good)
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
