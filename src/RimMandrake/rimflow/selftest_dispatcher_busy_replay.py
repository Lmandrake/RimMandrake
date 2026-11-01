#!/usr/bin/env python3
"""BUSY_SEAT_FIX_WAITING_COUNTS_AS_WORK: replays FOUNDRY's 2026-11-01 stall, 14:26 to 19:16, through the real tx_summary
and decide(). selftest_dispatcher_busy_replay.jsonl is every main-chain record of session a4a9f1ca in that span with all
text removed (`--extract <transcript>` regenerates it): six quiet gaps, repeated ended turns, new work that resets the
clock, and two questions open to the owner. `claude agents` read busy throughout, because a helper lived. Old build: no
ring in the span. This build: each gap reads waiting from turn_s past its ended turn until new work, and is rung; no
other moment reads waiting. The questions are short of tool_s, so a second replay lowers tool_s and kills the helpers
to make the question exemption the only thing holding the reading, with a control that proves it holds it."""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispatcher as D      # noqa: E402
import seat_restart as SR   # noqa: E402

FIXTURE = os.path.join(HERE, "selftest_dispatcher_busy_replay.jsonl")
START, END = "14:25:59", "19:16:57"
# (the ended turn, the next work), read off the transcript by hand: the replay's answer key, not derived from the code
GAPS = [("14:26:04", "15:32:44"), ("15:35:51", "16:12:32"), ("16:24:58", "17:11:10"),
        ("17:11:48", "17:51:47"), ("17:51:52", "18:22:03"), ("18:22:08", "19:16:45")]
QUESTIONS = [("16:13:45", "16:16:20"), ("16:18:24", "16:24:33")]


def at(hms):
    return datetime.strptime("2026-11-01T%sZ" % hms, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def within(t, spans, lead=0):
    return any(at(a) + lead <= t < at(b) for a, b in spans)


def stamp(r):
    return datetime.strptime(r["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()


def scrub(r):
    """A record with its shape and no words: what tx_summary reads, and nothing anyone wrote."""
    out = {k: r[k] for k in ("type", "subtype", "operation", "timestamp", "isSidechain") if k in r}
    if isinstance(r.get("attachment"), dict):
        out["attachment"] = {"type": r["attachment"].get("type")}
    if isinstance(r.get("origin"), dict):
        out["origin"] = {"kind": r["origin"].get("kind")}
    m = r.get("message")
    if isinstance(m, dict):
        c = m.get("content")
        c = [{k: x[k] for k in ("type", "name") if k in x} for x in c if isinstance(x, dict)] if isinstance(c, list) else ""
        out["message"] = {k: m[k] for k in ("role", "stop_reason") if k in m}
        out["message"]["content"] = c
    return out


def extract(path):
    with open(path) as f, open(FIXTURE, "w") as o:
        for line in f:
            r = json.loads(line)
            if r.get("timestamp") and not r.get("isSidechain") and at(START) <= stamp(r) <= at(END):
                o.write(json.dumps(scrub(r), sort_keys=True) + "\n")


def load(rename=None):
    with open(FIXTURE) as f:
        recs = [json.loads(line) for line in f]
    if rename:
        for r in recs:
            for x in (r.get("message") or {}).get("content") or []:
                if x.get("name") == rename[0]:
                    x["name"] = rename[1]
    return recs


class Replay:
    """The transcript as the Dispatcher would have found it at time t: only the records already written."""

    def __init__(self, tmp, recs, block, alive=True):
        self.recs, self.path, self.upto = recs, os.path.join(tmp, "a4a9f1ca.jsonl"), 0
        open(self.path, "w").close()
        self.sch = D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json"))
        self.sch["seats"] = {"FOUNDRY": dict(self.sch["seats"]["FOUNDRY"], clone="/nonexistent")}
        self.sch.pop("seat_restart", None)
        self.sch.pop("busy_waiting", None)
        if block:
            self.sch["busy_waiting"] = block
        self.session = {"name": "AGENT FOUNDRY", "status": "busy", "sessionId": "a4a9f1ca", "kind": "interactive", "pid": 1}
        self.obs = {"paused": None, "agents": {"state": "MEASURED", "sessions": [self.session]},
                    "peek": lambda seat: {"id": "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT", "needs": "offline"},
                    # each ring is taken at once, so one gap's ring cannot hold the next gap's back
                    "events": lambda seat, since: [{"event": "lease", "action": "take", "id": "X", "ts": since}],
                    "consumed": lambda seat, rid: {"consumed_at": 1},
                    "armed": lambda seat: {"pid": 4242}, "alive": lambda pid: True,
                    "seat_restart": {"tx": lambda seat, s: SR.tx_summary(self.path, peers=[]),
                                     "helpers": lambda seat, s: [{"id": "agent-a8222e00902715286", "alive": alive}]}}

    def advance(self, t):
        with open(self.path, "a") as f:
            while self.upto < len(self.recs) and stamp(self.recs[self.upto]) <= t:
                f.write(json.dumps(self.recs[self.upto]) + "\n")
                self.upto += 1

    def rings(self):
        st, out, t = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, [], at("14:26:58")
        while t < at(END):
            self.advance(t)
            out += [(t, a) for a in D.decide(self.sch, st, self.obs, t, True) if a["do"] == "ring"]
            t += self.sch["tick_s"]
        return out

    def readings(self, step=15):
        out, t = [], at(START)
        while t < at(END):
            self.advance(t)
            out.append((t, bool(D.busy_waiting(self.sch, self.obs, "FOUNDRY", self.session, "busy", t))))
            t += step
        return out


def with_replay(fn, recs, block, alive=True):
    with tempfile.TemporaryDirectory() as tmp:
        return fn(Replay(tmp, recs, block, alive))


def main():
    live = D.load_schedule(os.path.join(HERE, "dispatcher_schedule.json"))["busy_waiting"]
    recs, turn = load(), live["turn_s"]
    old = with_replay(Replay.rings, recs, None)
    new = with_replay(Replay.rings, recs, live)
    reads = with_replay(Replay.readings, recs, live)
    # the exemption alone: questions past tool_s, no helper alive; the control calls the same calls Bash
    sharp = dict(live, tool_s=60)
    held = with_replay(Replay.readings, recs, sharp, False)
    ctrl = with_replay(Replay.readings, load(("AskUserQuestion", "Bash")), sharp, False)
    inq = [(t, w) for t, w in held if within(t, QUESTIONS, 60)]
    spells = sum(1 for (_, a), (_, b) in zip(reads, reads[1:]) if b and not a)
    wrong = [t for t, w in reads if w != within(t, GAPS, turn)]
    quiet_gap = [g for g in GAPS if not any(within(t, [g], turn) for t, _ in new)]
    span = at(GAPS[-1][1]) - at(GAPS[0][0])
    ok = True
    for good, what in ((len(recs) > 200 and span > 4.5 * 3600, "the fixture holds %d records over %d min" % (len(recs), span // 60)),
                       (not old, "without the rule the replay rings nobody (the defect reproduced)"),
                       (not wrong, "with the rule, %d of %d readings match the key: waiting only from turn_s past each "
                                   "ended turn until new work" % (len(reads) - len(wrong), len(reads))),
                       (spells == len(GAPS), "it reads waiting in %d spells, one per quiet gap, the clock reset by each "
                                             "new turn" % spells),
                       (not quiet_gap, "every quiet gap is rung"),
                       (new and new[0][0] - at(GAPS[0][0]) <= turn + 300, "the first ring comes within turn_s + 5 min of the ended turn"),
                       (new and all(within(t, GAPS, turn) for t, _ in new), "no ring during a turn or an open question"),
                       (new and new[0][1]["ticket"] == "WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT", "the ring names the ready item"),
                       (inq and not any(w for _, w in inq), "a question past tool_s with no helper alive reads nothing (%d readings)" % len(inq)),
                       (all(w for t, w in ctrl if within(t, QUESTIONS, 60)), "control: the same stretch as a Bash call reads waiting")):
        print("%s %s" % ("PASS" if good else "FAIL", what))
        ok = ok and bool(good)
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--extract"]:
        extract(sys.argv[2])
        sys.exit(0)
    sys.exit(main())
