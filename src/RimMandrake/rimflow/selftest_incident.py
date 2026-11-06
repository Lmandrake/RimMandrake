#!/usr/bin/env python3
"""selftest_incident: OP3, OP4, RO4 by planted fault on the real path.

Each case plants readings through the real ops_watch.run (collectors stubbed, the shipped rules, ranges and alarm
pass real) into a throwaway status.json, then runs dispatcher.tick --apply under the shipped alarm_routes.json and the
shipped Operations and Conductor roles. Only launching a process is stubbed (recorded), so a "run" below is the
role_launch action the real decide_roles made. The real doorbell inbox, told.jsonl and incidents.json are in temp dirs.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_incident_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "pulse")]
import alarm_census as AC  # noqa: E402
import dispatcher as D  # noqa: E402
import doorbell  # noqa: E402
import incident as IN  # noqa: E402
import ops_watch as OW  # noqa: E402
import phone_push as PP  # noqa: E402
import relentless as RN  # noqa: E402
import role_launch as RL  # noqa: E402
import pulse_core as PC  # noqa: E402

os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
FAILS = []
H, M = 3600, 60
T0 = float(int(time.time()))
TABLE = IN.load_table()
RULES = OW.load_rules()
OPS_LOG = os.path.join(TMP, "ops_conductor.md")      # the rules' own conductor_log lines, counted: not the real log
for tg in RULES["targets"]:
    if tg.get("conductor_log"):
        tg["conductor_log"] = OPS_LOG
BASE = {"accounts.acct.runway": 9.0, "accounts.acct.week_left_pct": 90.0}
SANE = {"relentless.under_min": 0, "relentless.breaker_open_min": 0, "relentless.no_live_min": 0, "relentless.progress_age_min": 0,
        "relentless.blind": 0, "relentless.ready": 5, "relentless.why": "running", "relentless.distressed": 0,
        "seats.idle_with_work_min": 0, "seats.blind": 0, "seats.distressed": 0, "seats.paused": 0, "disk.pool_breach": 0}
# ops_watch.run writes a family's unmeasured blind key as 1, and this rig stubs every collector: a blind key landed later is sane here too
SANE.update({t["key"]: 0 for t in RULES["targets"] if t.get("alarm") and t["key"].endswith("blind")})
SEVERE = {"relentless.under_min": 150, "relentless.breaker_open_min": 150, "relentless.no_live_min": 150,
          "relentless.progress_age_min": 150, "relentless.blind": 1, "relentless.distressed": 1,
          "seats.idle_with_work_min": 200, "seats.blind": 1, "seats.distressed": 1, "disk.pool_breach": 1}


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


class Rig:
    def __init__(self, name):
        self.root = os.path.join(TMP, name)
        os.makedirs(self.root + "/ops")
        os.makedirs(self.root + "/state")
        os.environ["RM_OPS_WATCH_DIR"] = self.root + "/ops"
        os.environ["RM_DISPATCHER_STATE"] = self.root + "/state"
        D.state_root = lambda apply: self.root + "/state"
        self.runs, self.notes, self.log = [], [], self.root + "/conductor.md"
        open(self.log, "w").close()
        self.dead = False
        self.fx = {}
        real = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
        self.sch = dict(real, seats={}, ledger_notes=False, publish=False,
                        signal_watch={"enabled": False}, no_handoff={"conductor_log": self.log}, seat_restart={"enabled": False},
                        roles=[dict(r, runs_local=[], quick_checks_local=[], economy_local=None) for r in real["roles"]
                               if r["name"] in ("Operations", "Conductor")])     # no clock slot: only alarms launch here
        self.points, self.ledger = dict(SANE), []
        self.sch["ops_status"] = self.root + "/ops/status.json"
        self.sch.pop("account_pick", None)
        # the shipped schedule enables it; left on, every tick computes this machine's real token pacing and may ring
        self.sch["helper_budget"] = {"enabled": False}

    def plant(self, now, **points):
        vals = dict(BASE, **self.points)
        vals.update({k.replace("__", "."): v for k, v in points.items()})
        self.points = {k: v for k, v in vals.items() if k not in BASE}

        def one(n, r, c):
            c["known_ids"] = {"X"}
            return {k: (OW.M(v) if not isinstance(v, dict) else v) for k, v in vals.items()}
        for f in OW.ORDER:
            OW.COLLECTORS[f] = lambda n, r, c: {}
        OW.COLLECTORS[OW.ORDER[0]] = one
        OW.run(now=now, rules=RULES, filer=lambda todo, conf: {a["name"]: None for a in todo})

    def obs(self):
        ro = {"ops": lambda: IN.json.load(open(os.environ["RM_OPS_WATCH_DIR"] + "/status.json")), "account": lambda: "acct",
              "unit_state": lambda u: "inactive", "result": lambda r: None, "off": lambda p: None, "scope": lambda u: None,
              "procs": lambda u: [], "ledger": lambda: {"events": [], "world": None}, "pending_stores": lambda: None,
              "window_live": lambda n: (False, "")}
        inc = D.incident_obs(self.sch)
        inc["events"] = lambda: self.ledger
        return {"paused": None, "agents": {"state": "MEASURED", "sessions": []}, "peek": lambda s: None,
                "events": lambda s, since: [], "consumed": lambda s, r: None, "armed": lambda s: None, "alive": lambda p: False,
                "long_helpers": lambda: [], "roles": ro, "seat_restart": None, "login": None, "signals": None, "incident": inc}

    def tick(self, now, plant=True, **points):
        if plant:
            self.plant(now, **points)

        def launch(role, unit, message, root, exe):
            if self.dead:
                return False, "no agent can run", None
            return True, "launched", {}
        fx = {"role_launch": launch, "lock": lambda: None, "note": lambda *a: (True, ""), "publish": lambda n: None,
              "paused": lambda: None, "off": lambda p: None, "verdicts_append": lambda *a: None}
        fx.update(self.fx)
        acts = D.tick(self.sch, True, obs=self.obs(), now=now, fx=fx)
        self.runs += [a for a in acts if a["do"] == "role_launch"]
        return acts

    def rows(self):
        """Without the stubbed role runs' own alarms: a stub's overrun is not the fault planted here."""
        return [r for r in IN.read_rows() if r.get("cause") != "roles" and not str(r.get("kind")).startswith("role:")
                and not str(r.get("id")).startswith("roles-")]

    def inc(self):
        return list(IN.fold(self.rows())[0].values())

    def evs(self, ev):
        return [r for r in self.rows() if r.get("ev") == ev]

    def alarm_runs(self):
        return [r for r in self.runs if isinstance(r, dict) and r.get("mode") == "alarm"]

    def asked(self, role):
        st = json.load(open(self.root + "/state/state.json"))
        return (st.get("roles", {}).get(role) or {}).get("run_now")

    def snap(self):
        return json.load(open(IN.snapshot_path()))


def test_silent_reader():
    r = Rig("silent")
    r.tick(T0, relentless__under_min=40)              # distressed
    x = r.inc()
    check("a distressed reading opens one told row with cause, metric, reader, told_at, ack_due, recover_by",
          len(x) == 1 and x[0]["cause"] == "work_belt" and x[0]["metric"] and x[0]["reader"] == "Operations" and x[0]["told_at"]
          and x[0]["ack_due"] and "recover_by" in x[0], x)
    r.tick(T0 + 29 * M, relentless__under_min=69)
    check("still rung 0 before ack_within_min", r.inc()[0]["rung"] == 0, r.inc())
    r.tick(T0 + 30 * M, relentless__under_min=70)
    check("reader silent: Conductor on time at 30 min", r.inc()[0]["rung"] == 1, r.inc())
    log = open(r.log).read()
    check("the Conductor rung writes its log and asks a quick run", "INCIDENT" in log and (r.asked("Conductor") or r.runs), log)
    r.tick(T0 + 60 * M, relentless__under_min=100)
    check("Operations-read: no fresh Operations rung at 60, the Conductor holds it (same role not asked twice)",
          r.inc()[0]["rung"] == 1 and not [e for e in r.evs("escalated") if e.get("rung") == 2], r.evs("escalated"))
    r.tick(T0 + 239 * M, relentless__under_min=100)
    check("distressed stays from him until 4 h", r.inc()[0]["rung"] == 1 and not r.snap()["owner"], r.snap())
    r.tick(T0 + 240 * M, relentless__under_min=100)
    check("distressed reaches him at 4 h, straight from the Conductor", r.inc()[0]["rung"] == 3 and len(r.snap()["owner"]) == 1
          and [e["rung"] for e in r.evs("escalated")] == [1, 3], (r.snap(), r.evs("escalated")))


def test_chain_dedupe():
    """INCIDENT_CHAIN_DEDUPE_OPERATIONS_RUNG: the policy rung "Operations:fresh" asked an Operations-read route's role a
    second time; next after the reader is the Conductor, then him, at the ladder's own minutes."""
    t = IN.load_table()
    inc = lambda reader, rung, cls="distressed": {"id": "x", "reader": reader, "rung": rung, "rung_t": T0, "told_t": T0,
                                                  "ack_min": 30, "class": cls, "metrics": {"m": {}}}
    check("chain: an Operations reader goes Operations, Conductor, him",
          [IN.next_rung(t, inc("Operations", 0)), IN.next_rung(t, inc("Operations", 1))] == [1, IN.OWNER_RUNG])
    check("chain: a Conductor reader skips the Conductor rung, keeps the fresh Operations one",
          [IN.next_rung(t, inc("Conductor", 0)), IN.next_rung(t, inc("Conductor", 2))] == [2, IN.OWNER_RUNG])
    check("chain: a seat reader keeps every rung", [IN.next_rung(t, inc("BENCH", k)) for k in (0, 1, 2)] == [1, 2, 3])
    lad = t["policy"]["ladder"]
    check("the skip moves him no earlier: Operations reader at the Conductor rung is due at the owner minute",
          IN.next_due(t, inc("Operations", 1)) == T0 + lad["distressed"][1] * 60
          and IN.next_due(t, inc("Operations", 1, "emergency")) == T0 + lad["emergency"][1] * 60)
    check("a Conductor reader at rung 0 waits at least its ack minute", IN.next_due(t, inc("Conductor", 0)) == T0 + max(30, lad["distressed"][0]) * 60)
    ring = IN.ring_of(t, inc("Operations", 1), T0)
    check("the Conductor rung of an Operations route is the last agent: it is asked for his line",
          ring["reader"] == "Conductor" and ring["how"] == "quick_run" and "incident-line" in ring["text"], ring)
    check("a rung with an agent still above it is not asked for his line", "incident-line" not in IN.ring_of(t, inc("BENCH", 1), T0)["text"])
    # gen 5: the cases the first test could not see go red on their mutant
    slow = dict(inc("Conductor", 0), ack_min=lad["distressed"][0] + 30)
    check("a Conductor reader whose ack minute is past the ladder's still waits its ack minute (skip moves nothing earlier)",
          IN.next_due(t, slow) == T0 + slow["ack_min"] * 60, IN.next_due(t, slow))
    check("a seat reader keeps the ladder's own minutes on every rung",
          [IN.next_due(t, dict(inc("BENCH", k), rung_t=T0 - 3600)) for k in (0, 1, 2)]
          == [T0 + 30 * 60, T0 + lad["distressed"][0] * 60, T0 + lad["distressed"][1] * 60])
    check("the fresh Operations rung of a seat route is the last agent and is asked for his line",
          "incident-line" in IN.ring_of(t, inc("BENCH", 2), T0)["text"]
          and "incident-line" not in IN.ring_of(t, inc("Operations", 0), T0)["text"])
    r = Rig("dedupe_emergency")                       # Operations-read, emergency, every agent silent, through step()
    r.tick(T0, relentless__under_min=150)
    check("an emergency Operations-read incident opens with Operations as reader", r.inc()[0]["reader"] == "Operations", r.inc())
    for m in (30, 45, 59):
        r.tick(T0 + m * M, relentless__under_min=150)
    check("emergency: Conductor at its ack minute, no fresh Operations rung, not him before 60",
          r.inc()[0]["rung"] == 1 and not r.snap()["owner"] and [e["rung"] for e in r.evs("escalated")] == [1],
          (r.inc(), r.evs("escalated")))
    check("emergency: the Conductor rung asked for his line", r.asked("Conductor") or r.runs, r.runs)
    r.tick(T0 + 60 * M, relentless__under_min=150)
    check("emergency: him at 60, straight from the Conductor", r.inc()[0]["rung"] == IN.OWNER_RUNG and len(r.snap()["owner"]) == 1
          and [e["rung"] for e in r.evs("escalated")] == [1, IN.OWNER_RUNG], (r.snap(), r.evs("escalated")))


def test_emergency_all_dead():
    r = Rig("dead")
    r.dead = True
    PP.STATE = type(PP.STATE)(r.root + "/phone.json")
    r.tick(T0, relentless__under_min=150)
    for m in (30, 45):
        r.tick(T0 + m * M, relentless__under_min=150)
    check("no banner before 60", not r.snap()["owner"], r.snap())
    r.tick(T0 + 60 * M, relentless__under_min=150)
    own = r.snap()["owner"]
    check("all agents dead, emergency: the template on his banner at 60 min, marked unread",
          len(own) == 1 and own[0]["unread"] and "fixed template" in own[0]["line"], own)
    rows = PC.classify_incidents(r.snap(), {}, T0 + 60 * M)
    check("pulse shows it as a red row that sorts first", rows and rows[0]["kind"] == "red"
          and PC.order_rows(rows + [PC._row("z", "amber_soft", "w", "t", T0)])[0]["key"] == rows[0]["key"], rows)
    full = PC.collect_snapshot({"incidents": r.snap()}, {}, T0 + 60 * M)[0]["rows"]
    check("collect_snapshot keeps it at the top of the owner's view", full and full[0]["key"] == rows[0]["key"], full[:2])
    sent = []

    def t(a, b):
        sent.append((a, b))
    for _ in range(3):
        PP.send(rows[0], transport=t)
    check("one phone send per incident, red only", len(sent) == 1 and "UNREAD" in sent[0][1], sent)
    amber = dict(rows[0], kind="amber", key="other")
    check("amber never reaches the phone", PP.send(amber, transport=t) is False and len(sent) == 1, sent)
    r2 = Rig("line")
    r2.tick(T0, relentless__under_min=150)
    i = r2.inc()[0]["id"]
    for m in (30, 45):
        r2.tick(T0 + m * M, relentless__under_min=150)
    IN.write_line(i, "Operations", "Belt jammed on the pool, Operations restarting it.", now=T0 + 50 * M)
    check("his line is no ack", not r2.inc()[0].get("acked_t"), r2.inc())
    r2.tick(T0 + 60 * M, relentless__under_min=150)
    own = r2.snap()["owner"]
    check("the last agent's line is the one he sees, read", own and own[0]["line"].startswith("Belt jammed") and not own[0]["unread"], own)


def test_ack_then_killed():
    r = Rig("ack")
    r.tick(T0, relentless__under_min=40)
    i = r.inc()[0]["id"]
    IN.ack(i, "OPERATIONS", "investigating", now=T0 + 5 * M)
    r.tick(T0 + 31 * M, relentless__under_min=71)
    check("an ack holds the ack clock", r.inc()[0]["rung"] == 0 and r.inc()[0]["recover_by"], r.inc())
    r.dead = True                                       # reader killed; the fault stays
    r.tick(T0 + 64 * M, relentless__under_min=104)
    check("before recover_by it waits", r.inc()[0]["rung"] == 0, r.inc())
    r.tick(T0 + 66 * M, relentless__under_min=106)
    x = r.inc()[0]
    check("acked 'investigating', fault stays, reader killed: escalates anyway", x["rung"] == 1 and not x.get("acked_t"), x)
    e = r.evs("escalated")
    check("the row says it was acked", e and e[-1]["was_acked"] is True, e)


def test_ring_or_read_is_no_ack():
    r = Rig("noack")
    bell = os.path.join(r.root, "routes.json")      # a doorbell reader of its own: no live seat is one any more
    t = IN.load_table()
    t["readers"]["WORKER"] = {"by": "doorbell", "seat": "WORKER"}
    t["routes"] = [dict(x, reader="WORKER") if x["match"] == "queues.*" else x for x in t["routes"]]
    json.dump(t, open(bell, "w"))
    os.environ["RIMFLOW_ROUTES"] = bell
    r.sch["seats"] = {"WORKER": {"enabled": True, "wake": True}}
    try:
        _ring_or_read(r)
    finally:
        os.environ.pop("RIMFLOW_ROUTES", None)


def _ring_or_read(r):
    r.tick(T0, queues__blind=1)
    x = r.inc()
    check("a doorbell reader's incident opens", x and x[0]["reader"] == "WORKER", x)
    inbox = doorbell.inbox_path("WORKER")
    check("it rings the seat by doorbell", os.path.exists(inbox) and x[0]["id"] in open(inbox).read(), inbox)
    got = doorbell.take_ring("WORKER")
    check("the doorbell delivers it", got and x[0]["id"] in json.dumps(got), got)
    r.tick(T0 + 5 * M, queues__blind=1)
    check("a ring, a consume and a read write no ack", not r.evs("acked") and not r.inc()[0].get("acked_t"), r.rows())
    check("one ring only", not os.path.exists(inbox) and len(r.evs("opened")) == 1, r.evs("opened"))
    r.tick(T0 + 30 * M, queues__blind=1)
    check("so the next reader comes on time", r.inc()[0]["rung"] == 1, r.inc())
    r.ledger = [{"id": "NOPE", "event": "start", "seat": "FOUNDRY", "ts": IN.iso(T0 + H)}]
    check("item_acted reads named items only", IN.item_acted(r.ledger, ["OTHER"], IN.iso(T0)) is None)
    check("item_acted takes a seat's start", IN.item_acted(r.ledger, ["NOPE"], IN.iso(T0)) == ("NOPE", "FOUNDRY", "start"))
    check("a note is not an action; nor a program's start",
          IN.item_acted([{"id": "A", "event": "note", "seat": "FOUNDRY", "ts": IN.iso(T0)},
                         {"id": "A", "event": "start", "seat": "DISPATCHER", "ts": IN.iso(T0)}], ["A"], IN.iso(T0)) is None)


def test_one_outage():
    r = Rig("one")
    open(OPS_LOG, "w").close()
    r.tick(T0, **{k.replace(".", "__"): v for k, v in SEVERE.items()})
    x = r.inc()
    bad = sorted(x[0]["metrics"]) if x else []
    check("one outage tripping 10 metrics: one incident", len(x) == 1 and len(bad) >= 10, (len(x), bad))
    check("one run", len(r.alarm_runs()) == 1, r.alarm_runs())
    r.tick(T0 + 120, **{k.replace(".", "__"): v for k, v in SEVERE.items()})
    r.tick(T0 + 240, **{k.replace(".", "__"): v for k, v in SEVERE.items()})
    check("still one incident, one ring, one run", len(r.inc()) == 1 and len(r.evs("opened")) == 1 and len(r.alarm_runs()) == 1,
          (r.evs("opened"), r.alarm_runs()))
    lines = [x for x in open(OPS_LOG) if "ALARM" in x]
    filed = [a for a in json.load(open(os.environ["RM_OPS_WATCH_DIR"] + "/alarms.json")).values()
             if isinstance(a, dict) and a.get("state") == "OPEN"]
    check("the rules' conductor_log lines of that outage are one line, with several alarms filed",
          len(lines) == 1 and len(filed) >= 3, (lines, len(filed)))
    check("a later alarm of a cause with an open incident owes no line, another cause's does",
          not IN.line_owed("seats.blind", set()) and IN.line_owed("steve.seats_absent_min", set()))
    # the budget: many causes together spend at most runs_per_hour fresh and quick runs
    st = {"roles": {}}
    sch = r.sch
    said = [D.incident_run(sch, st, "Operations", "run", "w", T0 + i) for i in range(1)]
    said += [D.incident_run(sch, st, "Conductor", "quick", "w", T0 + 2)]
    st["roles"]["Operations"].pop("run_now"), st["roles"]["Conductor"].pop("run_now")
    said += [D.incident_run(sch, st, "Operations", "run", "w", T0 + 3)]
    check("the runs share a per-hour budget", "budget" in said[-1], said)


def test_batched_run_held_and_covers_slot():
    r = Rig("batch")
    sch = r.sch
    ring = lambda i: {"how": "fresh_run", "id": i, "reader": "Operations:fresh", "seat": None, "text": "INCIDENT %s" % i}
    a = lambda rings: {"rows": [], "rings": rings, "cursor": 0, "snapshot": {"t": T0, "at": IN.iso(T0), "fresh": True, "open": [], "owner": []}}
    nop = lambda *x: None
    st = {"roles": {}}
    D.incident_execute(a([ring("a-1"), ring("b-2"), ring("c-3")]), sch, st, "/nonexistent", T0, nop, nop)
    req = st["roles"]["Operations"]["run_now"]
    check("three incidents at once are ONE Operations run that names all three and covers the next slot",
          req["ids"] == ["a-1", "b-2", "c-3"] and req.get("covers_slot") and "b-2" in req["why"], req)
    st["roles"]["Operations"].pop("run_now")
    st["incident"]["runs"] = [T0, T0 + 1]
    D.incident_execute(a([ring("d-4")]), sch, st, "/nonexistent", T0 + 5, nop, nop)
    check("a run held by the hour budget is kept, not dropped", [h["id"] for h in st["incident"]["held"]] == ["d-4"], st["incident"])
    st["incident"]["runs"] = []
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 3700, nop, nop)
    check("the held run is asked once the hour has room",
          st["roles"]["Operations"].get("run_now", {}).get("ids") == ["d-4"], st)
    today = [("07:30", "economy", 1), ("19:30", "run", 1)]
    now = time.mktime(time.strptime("2026-11-01 14:00", "%Y-%m-%d %H:%M"))
    check("an incident run covers today's next slot still to come, not one already done",
          RL.covered_slot({"done": {}}, today, now, 86400) == "19:30"
          and RL.covered_slot({"done": {RL.slot_key(now, "19:30"): "done"}}, today, now, 86400) is None)
    # OPS_NIGHT_GAP_FILL_COVERED_SLOT: 11-01, a 14:16 incident run covered 19:30 and nothing judged for ~17 h
    t1416 = time.mktime(time.strptime("2026-11-01 14:16", "%Y-%m-%d %H:%M"))
    check("an incident run hours before the evening slot does not take its place (the 11-01 night gap)",
          RL.covered_slot({"done": {}}, today, t1416) is None, RL.covered_slot({"done": {}}, today, t1416))
    t1800 = time.mktime(time.strptime("2026-11-01 18:00", "%Y-%m-%d %H:%M"))
    check("an incident run within the cover window still covers the slot it stands in for",
          RL.covered_slot({"done": {}}, today, t1800) == "19:30")


def test_denied_goes_to_conductor_first():
    """OPS_REFUSAL_REWIRE_TO_CONDUCTOR: a refused Operations incident run goes to the Conductor first, never straight to
    his phone; on to the owner rung only when the Conductor role is off or its handed run is refused too."""
    r = Rig("denied")
    sch = r.sch
    a = lambda rings: {"rows": [], "rings": rings, "cursor": 0, "snapshot": {"t": T0, "at": IN.iso(T0), "fresh": True, "open": [], "owner": []}}
    nop = lambda *x: None
    rung = lambda i: IN.fold(IN.read_rows())[0][i]["rung"]

    def opened(iid):
        IN.append([{"ev": "opened", "id": iid, "at": IN.iso(T0), "t": T0, "state": "open", "rung": 2, "cause": iid,
                    "class": "distressed", "metrics": {iid + ".m": {"class": "distressed"}}, "items": [], "reader": "Operations",
                    "told_t": T0, "rung_t": T0, "acked_t": None}])

    def refuse(st, role, ids, t, outcome="refused: daily cap"):
        st["roles"].setdefault(role, {}).pop("run_now", None)
        st["roles"][role]["run_now_last"] = {"by": "DISPATCHER", "ids": ids, "decided": t, "outcome": outcome}

    opened("dn-1")
    st = {"roles": {}}
    pinged = []
    refuse(st, "Operations", ["dn-1"], T0 + 9)
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 10, nop, lambda sc, x, n: pinged.append(x))
    req = st["roles"].get("Conductor", {}).get("run_now") or {}
    check("a run refused on the daily cap goes to the Conductor first: its rung stands, a Conductor run names it",
          rung("dn-1") == 2 and req.get("ids") == ["dn-1"] and "dn-1" in req.get("why", "") and len(pinged) == 1,
          (IN.read_rows()[-1:], req, pinged))
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 11, nop, nop)
    check("the same refusal is read once", rung("dn-1") == 2 and len(st["incident"].get("held") or []) == 0, st["incident"])
    refuse(st, "Conductor", ["dn-1"], T0 + 20)
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 21, nop, nop)
    check("the Conductor's handed run refused too: the incident goes on to the owner rung", rung("dn-1") == IN.OWNER_RUNG,
          IN.read_rows()[-1:])
    opened("dn-2")
    st = {"roles": {}}
    refuse(st, "Operations", ["dn-2"], T0 + 30, outcome="refused: expired")
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 31, nop, nop)
    check("an expired ask is no refusal: nothing moves, no Conductor run", rung("dn-2") == 2
          and not st["roles"].get("Conductor", {}).get("run_now"), st)
    off = dict(sch, roles=[dict(x, enabled=False) if x["name"] == "Conductor" else x for x in sch["roles"]])
    refuse(st, "Operations", ["dn-2"], T0 + 40)
    D.incident_execute(a([]), off, st, "/nonexistent", T0 + 41, nop, nop)
    check("with the Conductor role off, a refused run goes to the owner rung now", rung("dn-2") == IN.OWNER_RUNG
          and not st["roles"].get("Conductor", {}).get("run_now"), IN.read_rows()[-1:])
    opened("dn-3")
    st = {"roles": {}, "incident": {"runs": [T0 + 49, T0 + 49]}}
    refuse(st, "Operations", ["dn-3"], T0 + 50)
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 51, nop, nop)
    check("a Conductor hand held by the hour budget waits in held, the incident unmoved",
          rung("dn-3") == 2 and [h.get("ids") for h in st["incident"]["held"]] == [["dn-3"]], st["incident"])
    st["incident"]["runs"] = []
    D.incident_execute(a([]), sch, st, "/nonexistent", T0 + 3700, nop, nop)
    check("the held hand is asked once the hour has room",
          (st["roles"].get("Conductor", {}).get("run_now") or {}).get("ids") == ["dn-3"], st)


def test_relapse():
    r = Rig("relapse")
    r.tick(T0, relentless__under_min=40)
    i = r.inc()[0]["id"]
    r.tick(T0 + 10 * M, relentless__under_min=0)
    check("sane is not closed", r.inc()[0]["state"] == "open" and r.inc()[0]["sane_since"], r.inc())
    r.tick(T0 + 40 * M, relentless__under_min=0)
    check("a rung does not move on sane readings", r.inc()[0]["rung"] == 0, r.inc())
    r.tick(T0 + 69 * M, relentless__under_min=0)
    check("not closed before sustain_min", r.inc()[0]["state"] == "open", r.inc())
    r.tick(T0 + 71 * M, relentless__under_min=0)
    check("closes on the sustained reading, no ack needed", r.inc()[0]["state"] == "closed", r.inc())
    r.tick(T0 + 2 * H, relentless__under_min=40)
    x = r.inc()
    check("relapse inside relapse_h: same incident reopens", len(x) == 1 and x[0]["id"] == i and x[0]["state"] == "open"
          and x[0]["reopens"] == 1 and x[0]["rung"] == 0, x)
    r.tick(T0 + 2 * H + 10 * M, relentless__under_min=0)
    r.tick(T0 + 2 * H + 15 * M, relentless__under_min=50)
    check("a dip does not reset the told time", r.inc()[0]["sane_since"] is None and len(r.inc()) == 1, r.inc())
    r.tick(T0 + 3 * H + 30 * M, relentless__under_min=0)
    r.tick(T0 + 4 * H + 40 * M, relentless__under_min=0)
    check("closed again", r.inc()[0]["state"] == "closed", r.inc())
    r.tick(T0 + 12 * H, relentless__under_min=40)
    check("past relapse_h it is a new incident", len(r.inc()) == 2, r.inc())


def test_blind_and_signal():
    r = Rig("blind")
    r.tick(T0)
    check("sane opens nothing, but stamps the snapshot", r.rows() == [] and r.snap()["t"] == T0, r.rows())
    r.tick(T0 + H, plant=False)
    x = r.inc()
    check("a status that stopped is itself an incident, emergency", len(x) == 1 and "ops_watch.blind" in x[0]["metrics"]
          and x[0]["class"] == "emergency", x)
    r.tick(T0 + H + 5 * M)
    r.tick(T0 + 3 * H)
    check("a status fresh again closes the blind incident", r.inc()[0]["state"] == "closed", r.inc())
    r = Rig("signal")
    r.tick(T0)
    with open(IN.told_path(), "a") as f:     # relentless.told's shape
        f.write(json.dumps({"class": "emergency", "cause": "relentless.breaker:k", "metric": "relentless.breaker_same_cause",
                            "reader": "Operations", "told_at": IN.iso(T0), "ack_due": IN.iso(T0), "recover_by": None}) + "\n")
    r.tick(T0 + 120)
    r.tick(T0 + 240)
    x = r.inc()
    check("relentless's own told row joins the ledger, once", len(x) == 1 and x[0]["class"] == "emergency"
          and len(r.evs("opened")) == 1 and len(r.evs("joined")) == 0, x)
    r.tick(T0 + 7 * H)
    check("not closed before its quiet time", r.inc()[0]["state"] == "open", r.inc())
    r.tick(T0 + 8 * H)
    check("a signal with no sane value closes after its quiet time", r.inc()[0]["state"] in ("closed",), r.inc())
    check("a Dispatcher alarm routed program writes nothing", IN.signal(r.sch, "cap:x", "w", T0) is False)
    check("a Dispatcher alarm routed to a role is a signal", IN.signal(r.sch, "dead:FOUNDRY", "w", T0) is True)
    r.tick(T0 + 8 * H + 120)
    check("the next tick opens on it", any(i["cause"] == "seats" for i in r.inc()), r.inc())


def test_ledger_unwritable():
    r = Rig("torn")
    r.tick(T0)
    if os.path.exists(IN.told_path()):
        os.remove(IN.told_path())
    os.mkdir(IN.told_path())                 # no file can be read or written there
    r.tick(T0 + 120, relentless__under_min=40)
    check("a ledger that does not read alarms by the Conductor log", "incident ledger is torn" in open(r.log).read(), open(r.log).read())
    r = Rig("snapfail")
    r.tick(T0)
    os.remove(IN.snapshot_path())
    os.mkdir(IN.snapshot_path())
    r.tick(T0 + 120, relentless__under_min=40)
    r.tick(T0 + 240, relentless__under_min=40)
    check("a pass that cannot write alarms on the next tick", "could not be written" in open(r.log).read(), open(r.log).read())


FORMS = """
K = "module_k:v"
def a(seat, kind, run, st):
    act(do="alarm", kind="lit:one")
    act(do="alarm", kind="dead:" + seat)
    act(do="alarm", kind="role:%s:cap" % run["n"])
    act(do="alarm", kind="r:%s:%s" % (seat, run))
    act(do="alarm", kind=f"fs:{seat}:z")
    key = "var:one" if st else "var:two"
    act(do="alarm", kind=key)
    act(do="alarm", kind=K)
    rec = {"do": "alarm", "kind": "dict:one", "why": "w"}
    return {"at": 1, "do": "alarm", "kind": key + ":tail"}
def b(x):
    def alarm(kind, why):
        acts.append({"do": "alarm", "kind": "%s:%s" % (kind, x)})
    alarm("param", "w")
    alarms.append({"kind": "appended:one", "why": "w"})
def c(fx, key):
    import incident as IN
    sig = getattr(fx, "alarm_signal", None)
    sig({"kind": "attention_" + key, "why": "w"})
    fx.alarm_signal({"kind": "direct:one"})
    IN.signal({}, "signalled:one", "w", 1)
    fx.told({"metric": "told.row", "told_at": 1})
    signal_alarm({}, {}, "forwarded:one", "w", 1)
    signal_alarm({}, {}, a["kind"], "w", 1)
def c2():
    c(None, "spend:%s" % who)
"""

POINTS = """
KEYS = ("a.one", "a.two")
MORE = KEYS + ("a.three",)
def c_q(rules):
    out, pts = {}, {}
    for q in rules:
        k = "queues.%s." % q["name"]
        out[k + "stalled_min"] = M(1, "min")
        out[k + "pending"] = U("blind") if q else M(1)
    key, m = "roles.%s.share" % q, {}
    pts[key] = M(1)
    out["f.%s" % q] = E(1)
    out.update({k: U("w") for k in ("c.one", "c.two")})
    for k in MORE:
        pts[k] = U("w")
    keep = {"plain": 1}
    return {"d.one": M(1), **{k: U("w") for k in KEYS}}
"""


def source_kinds():
    """The census of the real tree, with what it could not read."""
    return AC.census(os.path.join(HERE, ".."))


def test_census_forms():
    k, bad = AC.of_source(FORMS)
    want = {"lit:one", "dead:x", "role:x:cap", "r:x:x", "fs:x:z", "var:one", "var:two", "module_k:v", "dict:one",
            "var:one:tail", "var:two:tail", "param:x", "appended:one", "attention_spend:x", "direct:one", "signalled:one",
            "told.row", "forwarded:one"}
    check("the census reads every form a kind is written in", k == want and not bad, (sorted(k ^ want), bad))
    for src, name in (('def f(a):\n    act(do="alarm", kind=a["kind"])\n', "a subscript"),
                      ('def f(k):\n    act(do="alarm", kind=k)\n', "a parameter nobody passes"),
                      ('def f(q):\n    act(do="alarm", kind=g(q))\n', "a call"),
                      ('def f(a):\n    act(do="alarm", kind="%s" % a)\n', "a format with no literal")):
        check("the census fails loudly on " + name, AC.of_source(src)[1], src)
    for src, name in (('import incident as IN\ndef f(q):\n    IN.signal({}, q["kind"], "w", 1)\n', "a signal it cannot name"),
                      ('def f(x):\n    sig = getattr(x, "alarm_signal", None)\n    sig(g(x))\n', "a record it cannot name")):
        check("the census fails loudly on " + name, AC.of_source(src)[1], src)
    src = ('import inc as I\ndef f(q, kind=None):\n    act(do="alarm", kind=kind or ("or:one" if q else "or:two"))\n'
           'def g(q):\n    f(q, kind=I.K if q else None)\n')
    k, bad = AC.of_source(src, sibling=lambda m: 'K = "mod:k"\n' if m == "inc" else None)
    check("the census reads `a or b`, a sibling module's constant, and skips a None branch",
          k == {"or:one", "or:two", "mod:k"} and not bad, (sorted(k), bad))
    check("the census fails loudly on a module constant it cannot read", AC.of_source(src)[1], src)
    k, bad = AC.points_of_source(POINTS)
    want = {"queues.x.stalled_min", "queues.x.pending", "roles.x.share", "f.x", "c.one", "c.two", "a.one", "a.two", "a.three", "d.one"}
    check("the census reads every form a point name is built in", k == want and not bad, (sorted(k ^ want), bad))
    for src, name in (('def f(a):\n    out[a["k"]] = M(1)\n', "a point key from a record"),
                      ('def f(a):\n    out["%s" % a] = M(1)\n', "a point key with no literal")):
        check("the census fails loudly on " + name, AC.points_of_source(src)[1], src)
    k, _ = AC.of_source('def other():\n    k = "not:this"\ndef f(k):\n    act(do="alarm", kind=k)\n')
    check("another function's local is not a name's value", "not:this" not in k, k)


def test_alarms_reach_ledger():
    r = Rig("publish")
    r.sch["publish"], r.sch["publish_stuck_s"] = True, 0
    r.fx = {"lock": lambda: open(os.devnull), "publish": lambda n: "error: index.lock exists"}
    r.tick(T0)
    r.fx["publish"] = lambda n: "error: not fast-forward"
    r.tick(T0 + 120)
    got = {x.get("kind") for x in IN.read_rows()}
    check("a stuck publish reaches told.jsonl on its real path", {"publish:index_lock", "publish:stuck"} <= got, got)
    r.tick(T0 + 240)
    check("and opens one incident of its cause", [i["cause"] for i in r.inc()].count("publish") == 1, r.inc())
    r = Rig("budget")
    r.sch["helper_budget"] = {"enabled": True}
    real, D.HB.publish = D.HB.publish, lambda *a, **k: 1 / 0
    try:
        r.tick(T0)
        r.tick(T0 + 120)
    finally:
        D.HB.publish = real
    check("a failed helper budget reaches told.jsonl, once for one alarm",
          [x.get("kind") for x in IN.read_rows()].count("budget:failed") == 1, IN.read_rows())
    r = Rig("budget_off")
    called = []
    real, D.HB.publish = D.HB.publish, lambda *a, **k: called.append(a)
    try:
        r.tick(T0)
    finally:
        D.HB.publish = real
    check("a rig's tick never computes the machine's real helper budget", not called, called)
    r = Rig("relentless")
    s = RN.Store(r.root + "/rn")
    fx = RN.Effects(dict(RN.rules(), ops_watch_dir=r.root + "/ops"), s)
    s.on_alarm = fx.alarm_signal
    for rec in ({"kind": "jam", "why": "w"}, {"kind": "jam", "why": "again"}, {"kind": "step_raised", "why": "w"},
                {"kind": "breaker_emergency", "why": "w"}):
        s.journal(dict(rec, do="alarm", at="t"))
    s.journal({"do": "enrol", "kind": "jam"})
    check("relentless alarms join the ledger, a repeat inside the limit does not, breaker_emergency has its own row",
          [x.get("kind") for x in IN.read_rows()] == ["jam", "step_raised"], IN.read_rows())
    check("relentless's journalled alarms are the real sites: the journal keeps all four",
          open(s.p("journal.jsonl")).read().count('"do": "alarm"') == 4)
    r.tick(T0 + 60)
    check("they open the work_belt incident", any(i["cause"] == "work_belt" for i in r.inc()), r.inc())


def test_routes():
    found, unread, files = source_kinds()
    check("no alarm site in the tree is unreadable by the census", not unread, unread)
    named = {"publish:index_lock", "publish:stuck", "budget:failed", "dry:live_runs_unsupervised", "breaker_emergency", "jam",
             "understaffed", "books_stale", "step_raised", "lease_raised", "quarantine", "dead:x",
             "relentless_attention_day_spend_limit", "relentless_attention_item_spend_limit:x", "queues.x.stalled_min",
             "queues.x.pending", "queues.blind", "relentless.breaker_same_cause", "selftest_false_hit", "testing.red_x"}
    check("the census sees the variable and dict forms, relentless", named <= found, sorted(named - found))
    check("the census walked every module that raises one", {os.path.basename(f) for f in files} >= {
        "dispatcher.py", "relentless.py", "helper_budget.py", "role_launch.py", "signal_watch.py", "login_watch.py",
        "seat_restart.py"}, files)
    qd = os.path.join(TMP, "census_queue")
    os.makedirs(qd, exist_ok=True)
    built = set(OW.c_queues(T0, {"queues": [{"name": "censusprobe", "pending": qd, "active": qd}]}, {}))
    families = [k.replace(".x.", ".*.") for k in found]
    check("the census's queue family is what the collector really builds",
          built and all(any(fnmatch.fnmatchcase(k, q) for q in families) for k in built), sorted(built))
    literal = set()
    for f in files:
        literal |= {m for m in re.findall(r'kind="([a-z_]+:[a-z_:]+)"', open(f, encoding="utf-8").read())
                    if not m.endswith(":")}
    check("every plain kind= literal is in the census", literal <= found, sorted(literal - found))
    kinds = found | {t["key"].replace("*", "x") for t in RULES["targets"] if t.get("alarm")} | set(OW.ranges_of(RULES))
    missing = [k for k in sorted(kinds) if IN.route_of(TABLE, k) is None]
    check("every alarm kind is in the routing table", not missing, missing)
    for kind in ("dead:x", "publish:stuck", "budget:failed", "jam", "relentless_attention_item_spend_limit:x",
                 "relentless_attention_day_spend_limit", "queues.x.stalled_min", "queues.x.pending", "process.x"):
        t2 = dict(TABLE, routes=[x for x in TABLE["routes"] if not fnmatch.fnmatchcase(kind, x["match"])])
        check("%s dropped from the table is seen missing" % kind, kind in [k for k in sorted(kinds) if IN.route_of(t2, k) is None])
    seen = [x["match"] for x in TABLE["routes"]]
    twice = sorted({m for m in seen if seen.count(m) > 1})
    check("no route match appears twice (the second row is dead)", not twice, twice)
    bad = [x for x in TABLE["routes"] if x["route"] == "role" and x["reader"] not in TABLE["readers"]]
    check("every role route names a reader the table wakes", not bad, bad)
    live_sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    bells = [k for k, v in TABLE["readers"].items() if v.get("seat")]
    check("every doorbell reader is really woken by the schedule",
          all(IN.reader_problem(k, live_sch) is None for k in bells), bells)
    check("FOUNDRY is retired: no reader, nothing rings it (owner by card 2026-11-02)", "FOUNDRY" not in TABLE["readers"])
    bell = {"readers": dict(TABLE["readers"], WORKER={"by": "doorbell", "seat": "WORKER"})}   # a doorbell seat, fixture only
    check("a seat with waking off is unwoken", "waking is off" in IN.reader_problem(
        "WORKER", {"seats": {"WORKER": {"wake": False}}}, table=bell))
    # T2 (ALARMS_REWIRE_OFF_RETIRED_BENCH): who picks up an alarm item, asked by every program that files one
    rel = json.load(open(IN.RELENTLESS_RULES))
    on = {"enabled": True, "pool_seats": ["BENCH", "FOUNDRY"], "pool_needs": ["offline"]}
    check("T2: the live relentless rules drain BENCH offline, so ops_watch's alarm conf has a receiver",
          IN.receiver_problem("BENCH", "offline") is None and "BENCH" in rel["pool_seats"] and rel["enabled"])
    check("T2: an offline alarm for a pool seat is picked up", IN.receiver_problem("BENCH", "offline", relentless=on) is None)
    check("T2: with relentless off, BENCH (no doorbell) is no receiver",
          "relentless is off" in str(IN.receiver_problem("BENCH", "offline", relentless=dict(on, enabled=False))))
    check("T2: with relentless off, a doorbell seat is still woken",
          IN.receiver_problem("WORKER", "offline", table=bell, relentless={}) is None)
    check("T2: a non-offline alarm for BENCH has no receiver",
          "needs=live" in str(IN.receiver_problem("BENCH", "live", relentless=on)))
    check("T2: a needs=owner alarm goes to OWNER, and only OWNER",
          IN.receiver_problem("OWNER", "owner", relentless=on) is None
          and "goes to OWNER" in str(IN.receiver_problem("BENCH", "owner", relentless=on)))
    check("T2: a seat nobody names is no receiver", IN.receiver_problem("NOBODY", "offline", relentless=on) is not None)
    check("T2: a doorbell seat whose waking is off is no receiver", "waking is off" in str(IN.receiver_problem(
        "WORKER", "live", {"seats": {"WORKER": {"wake": False}}}, table=bell, relentless=on)))
    led = os.path.join(TMP, "cli_ledger.jsonl")
    open(led, "w").close()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(RIMFLOW_LEDGER=led, RIMFLOW_ROUTES=IN.ROUTES, RIMFLOW_ITEMS=os.path.join(TMP, "items"), RIMFLOW_SEAT="BENCH")
    os.makedirs(env["RIMFLOW_ITEMS"], exist_ok=True)

    def cli(*a):
        return subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env, capture_output=True, text=True, timeout=120)
    p = cli("file", "GHOST_READER_PROBE_FIXTURE", "--for", "GHOST", "--title", "t")
    check("`rimflow file --for` an unwoken reader is refused", p.returncode != 0 and "wakes GHOST" in p.stderr + p.stdout, p.stderr + p.stdout)
    p = cli("file", "REAL_READER_PROBE_FIXTURE", "--for", "BENCH", "--title", "t")
    check("a woken reader files", p.returncode == 0, p.stderr + p.stdout)
    p = cli("spawn", "--from", "REAL_READER_PROBE_FIXTURE", "--for", "GHOST", "--name", "GHOST_SPAWN_PROBE_FIXTURE", "--title", "t")
    check("spawn refuses it too", p.returncode != 0 and "wakes GHOST" in p.stderr + p.stdout, p.stderr + p.stdout)
    r = Rig("cliack")
    env.update(RM_OPS_WATCH_DIR=os.environ["RM_OPS_WATCH_DIR"], RM_DISPATCHER_STATE=os.environ["RM_DISPATCHER_STATE"])
    r.tick(T0, relentless__under_min=40)
    i = r.inc()[0]["id"]
    p = cli("ack", i, "--plan", "pool cleared next")
    check("rimflow ack is the real verb", p.returncode == 0 and r.inc()[0]["plan"] == "pool cleared next", p.stderr + p.stdout)
    p = cli("ack", "NO_SUCH", "--plan", "x")
    check("ack refuses an id that is not open", p.returncode != 0, p.stdout)
    p = cli("incidents")
    check("rimflow incidents lists it", i in p.stdout, p.stderr)
    check("the real ledger refuses a test process", _refuses())


def _refuses():
    try:
        IN.append([{"x": 1}], IN.REAL_OPS + "/told.jsonl")
    except RuntimeError:
        return True
    return False


def test_spend_alarms_do_not_buy_runs():
    # OPS_OVERSPEND_FIX_ALARM_FEEDS_ITS_METER: a spend alarm routed to an Operations incident buys more of the spend it reports
    for role in ("Operations", "Conductor", "Arbiter"):
        for kind in ("role:%s:overspend_day" % role, "role:%s:overbudget" % role):
            r = IN.route_of(TABLE, kind)
            check("%s routes program, the Conductor log only" % kind, r is not None and r.get("route") == "program", r)
    r = IN.route_of(TABLE, "role:Operations:ops")
    check("other role:* alarms still reach Operations", r is not None and r.get("route") == "role", r)


def test_owner_rung_revisited():
    """OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS: at his rung an incident never sat forever. Unacked it is revisited
    owner_revisit_min after it reached him; acked with a short recover_by it still waits that floor; acked longer, it
    waits the ack; each revisit clears the ack and plan and asks ONE fresh Operations run naming it; it never climbs."""
    rev = IN.load_table()["policy"]["owner_revisit_min"]
    r = Rig("revisit")
    r.tick(T0, relentless__under_min=40)
    for m in (30, 60, 240):
        r.tick(T0 + m * M, relentless__under_min=100)
    x = r.inc()[0]
    check("revisit: at his rung", x["rung"] == IN.OWNER_RUNG, x)
    st_path = r.root + "/state/state.json"

    def clear_ask():
        st = json.load(open(st_path))
        st.get("roles", {}).get("Operations", {}).pop("run_now", None)
        st.get("incident", {}).pop("runs", None)
        json.dump(st, open(st_path, "w"))
    clear_ask()
    r.tick(T0 + (240 + rev - 1) * M, relentless__under_min=100)
    check("revisit: not before owner_revisit_min", not r.evs("revisited"), r.evs("revisited"))
    r.tick(T0 + (240 + rev) * M, relentless__under_min=100)
    e = r.evs("revisited")
    ask = r.asked("Operations") or {}
    check("revisit: unacked at his rung, revisited at owner_revisit_min, still his rung",
          len(e) == 1 and r.inc()[0]["rung"] == IN.OWNER_RUNG and e[0]["revisits"] == 1, (e, r.inc()))
    check("revisit: one fresh Operations run is asked, naming it", x["id"] in str(ask.get("why")) and
          "revisit 1" in str(ask.get("why")) or any(x["id"] in str(a.get("why")) for a in r.runs), (ask, r.runs[-1:]))
    clear_ask()
    t1 = T0 + (240 + rev) * M
    IN.ack(x["id"], "OPERATIONS", "pool restore lands at 18:00", now=t1 + 5 * M)          # default recover_min 60
    r.tick(t1 + 70 * M, relentless__under_min=100)
    check("revisit: an ack shorter than the floor waits the floor", len(r.evs("revisited")) == 1, r.evs("revisited"))
    r.tick(t1 + rev * M, relentless__under_min=90)                                   # the clock went back: news
    e = r.evs("revisited")
    check("revisit: past the floor it is revisited again, ack and plan cleared, last_plan kept",
          len(e) == 2 and not r.inc()[0].get("acked_t") and r.inc()[0].get("plan") is None
          and e[-1]["last_plan"] == "pool restore lands at 18:00", (e, r.inc()))
    clear_ask()
    t2 = t1 + rev * M
    IN.ack(x["id"], "OPERATIONS", "Steve's desk is off until Monday", recover_min=3 * rev, now=t2 + 1 * M)
    r.tick(t2 + (rev + 5) * M, relentless__under_min=80)
    check("revisit: an ack longer than the floor is waited out", len(r.evs("revisited")) == 2, r.evs("revisited"))
    r.tick(t2 + (3 * rev + 2) * M, relentless__under_min=80)
    check("revisit: and revisited at its recover_by", len(r.evs("revisited")) == 3 and r.inc()[0]["rung"] == IN.OWNER_RUNG,
          r.evs("revisited"))
    check("revisit: never escalated past his rung", all(v["rung"] <= IN.OWNER_RUNG for v in r.evs("escalated")))


def at_his_rung(*iids, plan="waiting on the fix"):
    """Rows of these incidents at his rung, last revisited 4 min apart from T0, each metric's baseline reading 5."""
    table = IN.load_table()
    # these planted metrics stand, but on a program route: they open no incident of their own beside the planted one
    table["routes"] = [{"match": g, "route": "program"} for g in ("m.*", "r.*", "sig.*")] + table["routes"]
    rev = table["policy"]["owner_revisit_min"]
    t = T0
    rows = []
    for k, iid in enumerate(iids):
        tk = t + k * 4 * M
        rows.append(dict({"ev": "opened", "id": iid, "at": IN.iso(tk), "t": tk, "state": "open", "rung": IN.OWNER_RUNG, "rung_t": tk,
                          "told_t": tk - 9 * H, "told_at": IN.iso(tk - 9 * H), "cause": iid.split("-")[0], "class": "distressed",
                          "metrics": {"m.%s" % iid: {"class": "distressed", "event": False}}, "items": [], "reader": "Operations",
                          "ack_min": 30, "acked_t": tk + M, "recover_by_t": tk + H, "recover_by": IN.iso(tk + H), "ack_by": "OPERATIONS",
                          "plan": plan, "revisit_t": tk, "revisit_seen_t": tk, "revisits": 1,
                          "revisit_read": {"m.%s" % iid: [True, "distressed", 5, True, 0]}}))
    return table, rev, rows


def status_of(now, **vals):
    """Each metric is `m.<name with _ for ->`, read and standing: its OPEN alarm is what makes `bad` see it."""
    pts = {"m.%s" % k.replace("_", "-"): {"m": "MEASURED", "v": v, "class": "distressed"} for k, v in vals.items()}
    return {"t": now, "points": pts, "alarms": {}}


def test_revisits_batched():
    """INCIDENT_REVISIT_TAME_SAME_NEWS_HOURLY (1): revisits falling due minutes apart are one Operations run, and the
    incidents stay in step after it. Due inside the window is the only test, an ack's recover_by included."""
    table, rev, rows = at_his_rung("a-1", "b-1")
    now = T0 + rev * M + M
    moved = status_of(now, a_1=6, b_1=6)         # both have news; a-1 is due now, b-1 in 3 min
    res = IN.step(table, rows, moved, now)
    ids = [x["id"] for x in res["rows"] if x["ev"] == "revisited"]
    check("batch: a revisit due 4 min later goes out with the one due now", ids == ["a-1", "b-1"] and len(res["rings"]) == 2, res["rows"])
    r = Rig("revbatch")
    dst = {"roles": {}}
    D.incident_execute(dict(res), r.sch, dst, "/nonexistent", now, lambda *x: None, lambda *x: None)
    req = dst["roles"]["Operations"]["run_now"]
    check("batch: they are ONE Operations run naming both, one counted against the hour",
          req["ids"] == ["a-1", "b-1"] and len(dst["incident"]["runs"]) == 1 and "a-1" in req["why"] and "b-1" in req["why"], req)
    incs = IN.fold(rows + res["rows"])[0]
    check("batch: they stay in step, both next due together",
          IN.next_due(table, incs["a-1"]) == IN.next_due(table, incs["b-1"]) == now + rev * M, incs)
    far = [rows[0], dict(rows[1], rung_t=now - rev * M + (table["policy"]["revisit_batch_min"] + 5) * M)]
    res2 = IN.step(table, far, moved, now)
    check("batch: a revisit due outside the window waits for its own time",
          [x["id"] for x in res2["rows"] if x["ev"] == "revisited"] == ["a-1"], res2["rows"])
    acked = [rows[0], dict(rows[1], acked_t=now - M, recover_by_t=now + 10 * M)]
    res3 = IN.step(table, acked, moved, now)
    check("batch: an ack running out inside the window goes out with the run",
          [x["id"] for x in res3["rows"] if x["ev"] == "revisited"] == ["a-1", "b-1"], res3["rows"])
    long_ack = [rows[0], dict(rows[1], acked_t=now - M, recover_by_t=now + (table["policy"]["revisit_batch_min"] + 5) * M)]
    res3 = IN.step(table, long_ack, moved, now)
    check("batch: an ack running past the window is not cut short by another incident's run",
          [x["id"] for x in res3["rows"] if x["ev"] == "revisited"] == ["a-1"], res3["rows"])
    res4 = IN.step(table, rows, status_of(now, a_1=6, b_1=5), now)
    check("batch: an incident with no news is not pulled in; it waits and is re-armed at its own time",
          [x["id"] for x in res4["rows"]] == ["a-1"] and len(res4["rings"]) == 1, res4["rows"])


def test_revisit_quiet():
    """INCIDENT_REVISIT_TAME_SAME_NEWS_HOURLY (2): no news is a re-arm with no run, and the log says so. Everything that
    is news still launches; what cannot be compared is news."""
    table, rev, rows = at_his_rung("q-1")
    now = T0 + rev * M
    st = status_of(now, q_1=5)
    pt = st["points"]["m.q-1"]

    def run(rows, status=st, now=now, events=None):
        res = IN.step(table, rows, status, now, events=events)
        return res, [x for x in res["rows"] if x["ev"] in ("revisited", "revisit_quiet")]
    res, ev = run(rows)
    check("quiet: unchanged readings and plan launch nothing", not res["rings"], res)
    check("quiet: the incident log says so", [x["ev"] for x in ev] == ["revisit_quiet"] and "unchanged" in ev[0]["why"]
          and "no run" in ev[0]["why"], ev)
    x = IN.fold(rows + res["rows"])[0]["q-1"]
    check("quiet: re-armed for a whole floor, plan kept, count kept",
          x["rung_t"] == now and x["plan"] == "waiting on the fix" and x["quiet_revisits"] == 1
          and IN.next_due(table, x) == now + rev * M and x["revisits"] == 1, x)
    r = Rig("quietrun")
    dst = {"roles": {}}
    D.incident_execute(dict(res), r.sch, dst, "/nonexistent", now, lambda *x: None, lambda *x: None)
    check("quiet: no Operations run is asked", not (dst["roles"].get("Operations") or {}).get("run_now"), dst)
    res2, ev2 = run(rows + res["rows"], {"t": now + rev * M, "points": {"m.q-1": pt}, "alarms": {}}, now + rev * M)
    check("quiet: and quiet again a floor later", [x["ev"] for x in ev2] == ["revisit_quiet"] and not res2["rings"], ev2)

    def fires(name, rows_, status=st, now_=now, events=None, says=None):
        res, ev = run(rows_, status, now_, events)
        ok = [x["ev"] for x in ev] == ["revisited"] and [r["id"] for r in res["rings"] if r.get("revisit")] == ["q-1"] and (says is None or says in " ".join(ev[0]["news"]))
        check("quiet: %s launches" % name, ok, ev)
        return res, ev
    fires("a changed value", rows, {"t": now, "points": {"m.q-1": dict(pt, v=6)}, "alarms": {}}, says="readings moved")
    fires("a changed class", rows, {"t": now, "points": {"m.q-1": dict(pt, **{"class": "emergency"})}, "alarms": {}}, says="readings moved")
    fires("an unmeasured reading", rows, {"t": now, "points": {"m.q-1": dict(pt, m="UNMEASURED")}, "alarms": {}}, says="readings moved")
    fires("a reading gone from status", rows, {"t": now, "points": {}, "alarms": {}}, says="readings moved")
    fires("a blind status", rows, {"t": now - H, "points": {"m.q-1": pt}}, says="not fresh")
    fires("no earlier revisit (first look)", [dict(rows[0], revisit_read=None, revisit_seen_t=None)], says="no earlier")
    fires("no plan (the last run did not answer)", [dict(rows[0], plan=None, acked_t=None)], says="no run has answered")
    fires("only an auto-ack (an item action is not an answer)", [dict(rows[0], auto_ack=True, plan="start on X")], says="no run has answered")
    fires("a rewritten plan after a quiet look", rows + [{"ev": "revisit_quiet", "id": "q-1", "t": now - rev * M, "revisit_plan": "waiting on the fix",
                                                           "rung_t": now - rev * M, "revisit_seen_t": now - rev * M, "revisit_read": rows[0]["revisit_read"]},
                                                          {"ev": "acked", "id": "q-1", "t": now - H, "plan": "a new plan", "acked_t": now - H,
                                                           "recover_by_t": now - H + M}], says="the plan changed")
    rows_join = rows + [{"ev": "joined", "id": "q-1", "t": now - H, "metrics": {"m.q-1": {"class": "distressed", "event": False},
                                                                               "m.new": {"class": "distressed", "event": False}}}]
    fires("a metric that joined", rows_join, says="m.new")
    fires("a sane blip since the last look", rows + [{"ev": "sane", "id": "q-1", "t": now - 2 * H, "sane_since": now - 2 * H},
                                                     {"ev": "relapsing", "id": "q-1", "t": now - H, "sane_since": None}], says="state moved")
    ev_rows = [dict(rows[0], metrics={"sig.x": {"class": "distressed", "event": True}}, revisit_read={"sig.x": [False, None, None, False, 1]}),
               {"kind": "sig.x", "metric": "sig.x"}, {"kind": "sig.x", "metric": "sig.x"}]
    fires("a signal fired again", ev_rows, says="sig.x")
    ledger = [{"id": "OPS_X", "event": "close", "seat": "BENCH", "ts": IN.iso(now - H)}]
    fires("an action on a named item", [dict(rows[0], items=["OPS_X"])], events=lambda: ledger, says="close on OPS_X")
    fires("a day with no run", [dict(rows[0], revisit_t=now - (24 * H + M), revisit_seen_t=now - rev * M)], says="no run has read it")
    clock = dict(rows[0], metrics={"r.under_min": {"class": "distressed", "event": False}}, revisit_read={"r.under_min": [True, "distressed", 100, True, 0]})
    res, ev = run([clock], {"t": now, "points": {"r.under_min": dict(pt, v=340)}, "alarms": {}})
    check("quiet: a clock rising is only time passing", [x["ev"] for x in ev] == ["revisit_quiet"], ev)
    fires("a clock that went back", [clock], {"t": now, "points": {"r.under_min": dict(pt, v=40)}, "alarms": {}}, says="r.under_min")
    fires("a clock that re-aged, risen less than the time elapsed", [clock], {"t": now, "points": {"r.under_min": dict(pt, v=110)}, "alarms": {}}, says="r.under_min")
    fires("a clock risen more than the time elapsed", [clock], {"t": now, "points": {"r.under_min": dict(pt, v=500)}, "alarms": {}}, says="r.under_min")
    slack = IN.load_table()["policy"]["revisit_clock_slack_min"]
    res, ev = run([clock], {"t": now, "points": {"r.under_min": dict(pt, v=340 - slack)}, "alarms": {}})
    check("quiet: a clock within the slack only aged", [x["ev"] for x in ev] == ["revisit_quiet"], ev)
    fires("a clock just outside the slack", [clock], {"t": now, "points": {"r.under_min": dict(pt, v=340 - slack - 1)}, "alarms": {}}, says="r.under_min")
    for unit, per, name in ((3600, "h", "r.age_h"), (1, "s", "r.tick_s")):
        c = dict(rows[0], metrics={name: {"class": "distressed", "event": False}}, revisit_read={name: [True, "distressed", 7, True, 0]},
                 revisit_seen_t=now - 7200)
        res, ev = run([c], {"t": now, "points": {name: dict(pt, v=7 + 7200 / unit)}, "alarms": {}})
        check("quiet: a clock in %s ages in %s" % (per, per), [x["ev"] for x in ev] == ["revisit_quiet"], ev)
    # both readings' own times decide: a status 10 min older than the pass that read it is no reset
    lag = dict(clock, revisit_status_t=now - rev * M)
    res, ev = run([lag], {"t": now - 10 * M, "points": {"r.under_min": dict(pt, v=330)}, "alarms": {}})
    check("quiet: elapsed is status time, not pass time", [x["ev"] for x in ev] == ["revisit_quiet"], ev)
    fires("a clock that kept time by the pass but not by its status", [lag], {"t": now - 10 * M, "points": {"r.under_min": dict(pt, v=340)}, "alarms": {}}, says="r.under_min")
    # a suffix alone makes no clock: a peak and a rate that happen to rise by the time elapsed are plain values
    for name, v0, v1 in (("r.stall_max_s", 30, 30 + rev * 60), ("r.growth_mb_per_h", 50, 54)):
        plain = dict(rows[0], metrics={name: {"class": "distressed", "event": False}}, revisit_read={name: [True, "distressed", v0, True, 0]})
        fires("%s moving by exactly the time elapsed" % name, [plain], {"t": now, "points": {name: dict(pt, v=v1)}, "alarms": {}}, says=name)
    check("quiet: units", [IN.clock_unit_s(x) for x in ("a.b_min", "a.b_h", "a.b_s", "a.b_age", "a.b_per_h", "a.b_max_s", "a.b_24h")] == [60, 3600, 1, None, None, None, None])
    text = dict(rows[0], metrics={"m.w": {"class": "distressed", "event": False}}, revisit_read={"m.w": [True, "distressed", "down", True, 0]})
    fires("a text value changing", [text], {"t": now, "points": {"m.w": dict(pt, v="up")}, "alarms": {}}, says="m.w")
    sane = dict(rows[0], metrics=dict(rows[0]["metrics"], **{"m.z": {"class": "distressed", "event": False}}),
                revisit_read=dict(rows[0]["revisit_read"], **{"m.z": [False, "sane", 3, True, 0]}))
    res, ev = run([sane], {"t": now, "points": {"m.q-1": pt, "m.z": {"m": "MEASURED", "v": 4, "class": "sane"}}, "alarms": {}})
    check("quiet: a value moving with no alarm on it either time still launches", [x["ev"] for x in ev] == ["revisited"]
          and "m.z" in " ".join(ev[0]["news"]), ev)
    res, ev = run([sane], {"t": now, "points": {"m.q-1": pt, "m.z": {"m": "MEASURED", "v": 3, "class": "sane"}}, "alarms": {}})
    check("quiet: and the same value, sane, stays quiet", [x["ev"] for x in ev] == ["revisit_quiet"], ev)


def test_quiet_on_the_real_path():
    """Through dispatcher.tick --apply: a revisit launched, answered with a plan, then a floor of nothing: no run, one row."""
    rev = IN.load_table()["policy"]["owner_revisit_min"]
    r = Rig("quietpath")
    r.tick(T0, relentless__under_min=40)
    for m in (30, 60, 240):
        r.tick(T0 + m * M, relentless__under_min=100)
    st_path = r.root + "/state/state.json"

    def clear_ask():
        st = json.load(open(st_path))
        st.get("roles", {}).get("Operations", {}).pop("run_now", None)
        st.get("incident", {}).pop("runs", None)
        json.dump(st, open(st_path, "w"))
    clear_ask()
    t1 = T0 + (240 + rev) * M
    r.tick(t1, relentless__under_min=120)
    check("real path: the first revisit has nothing to compare with, and launches", len(r.evs("revisited")) == 1
          and r.asked("Operations"), r.evs("revisited"))
    clear_ask()
    x = r.inc()[0]
    IN.ack(x["id"], "OPERATIONS", "Steve's desk is off until Monday", now=t1 + 5 * M)
    r.tick(t1 + rev * M, relentless__under_min=360)
    check("real path: a floor later with the clock only risen: no revisit, no ask, a quiet row", len(r.evs("revisited")) == 1
          and len(r.evs("revisit_quiet")) == 1 and x["id"] not in (r.asked("Operations") or {}).get("ids", []), (r.evs("revisit_quiet"), r.asked("Operations")))
    check("real path: the snapshot counts it", [o for o in r.snap()["open"] if o["id"] == x["id"]][0].get("quiet_revisits") == 1, r.snap())
    clear_ask()
    r.tick(t1 + 2 * rev * M, relentless__under_min=50)
    check("real path: and that run names it", x["id"] in (r.asked("Operations") or {}).get("ids", []), r.asked("Operations"))
    check("real path: the reading moves and the next revisit launches", len(r.evs("revisited")) == 2
          and "relentless.under_min" in " ".join(r.evs("revisited")[-1]["news"]), r.evs("revisited")[-1:])


def chain(name, metric="m.q-1", items=()):
    """A told file at his rung, driven only by step() and ack(): every row after the first is what the code wrote."""
    table, rev, rows = at_his_rung("q-1")
    rows = [dict(rows[0], metrics={metric: {"class": "distressed", "event": False}}, items=list(items),
                 revisit_read={metric: [True, "distressed", 5, True, 0]})]
    path = os.path.join(TMP, name + ".jsonl")
    IN.append(rows, path)

    def inc():
        return IN.fold(IN.read_rows(path))[0]["q-1"]

    def look(now, v=5, events=None):
        res = IN.step(table, IN.read_rows(path), {"t": now, "points": {metric: {"m": "MEASURED", "v": v, "class": "distressed"}}, "alarms": {}},
                      now, events=events)
        IN.append(res["rows"], path)
        return res, [x["ev"] for x in res["rows"]]

    def due():
        return IN.next_due(table, inc())
    return path, inc, look, due


def test_escalation_clear_through_step():
    """INCIDENT_ACK_FIX_OLD_NEWS_REACKS, blind check 8d94a18c: step's OWN escalation must record the ack it clears, so the
    item action that auto-acked the incident before does not re-ack it on the next look. Every row after the first is
    what step() wrote; none is planted."""
    table = IN.load_table()
    table["routes"] = [{"match": "m.*", "route": "program"}] + table["routes"]
    told = T0
    path = os.path.join(TMP, "escclear.jsonl")
    IN.append([{"ev": "opened", "id": "e-2", "at": IN.iso(told), "t": told, "state": "open", "rung": 0, "rung_t": told, "told_t": told,
                "told_at": IN.iso(told), "cause": "e", "class": "distressed", "metrics": {"m.e-2": {"class": "distressed", "event": False}},
                "items": ["OPS_Z"], "reader": "Operations", "ack_min": 30, "acked_t": None, "ack_by": None, "plan": None}], path)
    ledger = [{"id": "OPS_Z", "event": "start", "seat": "BENCH", "ts": IN.iso(told + M)}]

    def inc():
        return IN.fold(IN.read_rows(path))[0]["e-2"]

    def look(now):
        res = IN.step(table, IN.read_rows(path), {"t": now, "points": {"m.e-2": {"m": "MEASURED", "v": 5, "class": "distressed"}},
                                                 "alarms": {}}, now, events=lambda: ledger)
        IN.append(res["rows"], path)
        return res, [x["ev"] for x in res["rows"]]
    res, evs = look(told + 2 * M)
    check("esc-chain: a new item action auto-acks the told incident", "acked" in evs and inc().get("auto_ack") is True
          and inc()["plan"] == "start on OPS_Z", res["rows"])
    t = IN.next_due(table, inc())
    check("esc-chain: the auto-ack's recover_by is the next move", t == inc()["recover_by_t"], inc())
    res, evs = look(t)
    x = inc()
    esc = [r for r in res["rows"] if r["ev"] == "escalated"]
    check("esc-chain: recover_by passes, step escalates and clears the ack", esc and esc[0]["was_acked"] is True
          and x["rung"] >= 1 and x.get("acked_t") is None, res["rows"])
    check("esc-chain: step's escalation row records the ack clearing", esc and esc[0].get("ack_cleared_t") == t
          and x.get("ack_cleared_t") == t and IN.ack_since(x) == IN.iso(t), (res["rows"], x))
    res, evs = look(t + M)
    check("esc-chain: the action that acked it before acks nothing on the next look", "acked" not in evs
          and inc().get("acked_t") is None and inc()["plan"] is None, res["rows"])
    ledger.append({"id": "OPS_Z", "event": "claim", "seat": "BENCH", "ts": IN.iso(t + 2 * M)})   # the instrument still sees new news
    res, evs = look(t + 3 * M)
    check("esc-chain: a new item action after the clearing auto-acks", "acked" in evs and inc().get("auto_ack") is True
          and inc()["plan"] == "claim on OPS_Z", res["rows"])


def test_chains_through_step():
    """Blind check 8c5731ec: the rows these clauses read must be the rows step() writes, never planted by hand."""
    # a plan rewritten after a quiet look: quiet must record the plan it saw
    path, inc, look, due = chain("planchain")
    t = due()
    res, evs = look(t, v=6)
    check("chain: a moved reading launches", "revisited" in evs and res["rings"], res["rows"])
    IN.ack("q-1", "OPERATIONS", "plan one", path=path, now=t + M)
    t = due()
    res, evs = look(t, v=6)
    check("chain: answered and unchanged is quiet", evs == ["revisit_quiet"] and not res["rings"], res["rows"])
    x = inc()
    check("chain: the quiet row stores what it saw: plan, reading, when", x["revisit_plan"] == "plan one" and x["revisit_seen_t"] == t
          and x["revisit_read"]["m.q-1"][2] == 6, x)
    IN.ack("q-1", "OPERATIONS", "plan one", path=path, now=t + M)
    t = due()
    res, evs = look(t, v=6)
    check("chain: the same plan said again is still quiet", evs == ["revisit_quiet"], res["rows"])
    IN.ack("q-1", "OPERATIONS", "plan two", path=path, now=t + M)
    t = due()
    res, evs = look(t, v=6)
    check("chain: a plan rewritten after a quiet look launches", evs == ["revisited"] and res["rings"]
          and res["rows"][0]["news"] == ["the plan changed"], res["rows"])
    check("chain: the ask names the news", "the plan changed" in res["rings"][0]["text"], res["rings"])

    # an item action with no run answering: step's own auto-ack must count as no answer
    path, inc, look, due = chain("autochain", items=["OPS_X"])
    ledger = [{"id": "OPS_X", "event": "close", "seat": "BENCH", "ts": IN.iso(T0 - H)}]   # after it was told, before the last look
    ev = lambda: ledger
    t = due()
    res, evs = look(t, v=6, events=ev)
    check("chain: launched, its plan cleared", "revisited" in evs and inc()["plan"] is None and inc().get("auto_ack") is False, res["rows"])
    # INCIDENT_ACK_FIX_OLD_NEWS_REACKS: the action read before this revisit is old news; it must not re-ack the incident
    res, evs = look(t + M, v=6, events=ev)
    check("chain: an action older than the revisit acks nothing", "acked" not in evs and inc().get("acked_t") is None
          and inc()["plan"] is None, res["rows"])
    ledger.append({"id": "OPS_X", "event": "start", "seat": "BENCH", "ts": IN.iso(t + 2 * M)})   # a new action after the revisit
    res, evs = look(t + 3 * M, v=6, events=ev)
    check("chain: a new item action auto-acks, marked as one", evs == ["acked"] and inc().get("auto_ack") is True
          and inc()["plan"] == "start on OPS_X", res["rows"])
    t = due()
    res, evs = look(t, v=6, events=ev)
    check("chain: an item action with no run answering launches", evs == ["revisited"] and res["rings"]
          and res["rows"][0]["news"] == ["no run has answered: no plan of its own", "start on OPS_X"], res["rows"])
    res, evs = look(t + M, v=6, events=ev)
    check("chain: a revisit with only old item actions stays unacked", "acked" not in evs and inc().get("acked_t") is None, res["rows"])
    t2 = due()
    res, evs = look(t2, v=6, events=ev)
    check("chain: and at its next due it is revisited (rung), not re-acked", "acked" not in evs and "revisited" in evs
          and any(r.get("revisit") for r in res["rings"]), res["rows"])
    row = IN.ack("q-1", "OPERATIONS", "a plan of its own", path=path, now=t2 + 2 * M)
    check("chain: a run's ack clears the auto mark", row.get("auto_ack") is False and inc().get("auto_ack") is False, inc())
    res, evs = look(due(), v=6, events=ev)
    check("chain: and then a floor of nothing is quiet", evs == ["revisit_quiet"] and not res["rings"], res["rows"])

    # an escalation that clears an ack below his rung: the action that acked it before acks nothing again
    told = T0 - 9 * H
    inc0 = {"ev": "opened", "id": "e-1", "t": told, "state": "open", "rung": 0, "rung_t": told, "told_t": told, "told_at": IN.iso(told),
            "cause": "e", "class": "distressed", "metrics": {"m.e-1": {"class": "distressed", "event": False}}, "items": ["OPS_Y"],
            "reader": "Operations", "ack_min": 30, "acked_t": None, "ack_by": None, "plan": None}
    esc = {"ev": "escalated", "id": "e-1", "t": T0, "rung": 1, "rung_t": T0, "acked_t": None, "ack_by": None, "plan": None,
           "recover_by": None, "recover_by_t": None, "ack_cleared_t": T0}
    x = IN.fold([inc0, esc])[0]["e-1"]
    check("escalation: ack_since moves to the ack clearing", IN.ack_since(x) == IN.iso(T0), IN.ack_since(x))
    check("escalation: an action from before the clearing is not found",
          IN.item_acted([{"id": "OPS_Y", "event": "start", "seat": "BENCH", "ts": IN.iso(T0 - H)}], x["items"], IN.ack_since(x)) is None)
    check("escalation: a never-revisited incident reads from told_at", IN.ack_since(IN.fold([inc0])[0]["e-1"]) == IN.iso(told))

    # the baseline moves with each quiet look: a clock going back from the LAST look is news
    path, inc, look, due = chain("clockchain", metric="r.under_min")
    res, evs = look(due(), v=245)
    check("chain: a clock rising by the floor is quiet", evs == ["revisit_quiet"], res["rows"])
    res, evs = look(due(), v=200)
    check("chain: a clock back from the last quiet look launches, though above the old baseline", evs == ["revisited"]
          and "r.under_min" in " ".join(res["rows"][0]["news"]), res["rows"])

    # blind check 60dac938: the real routes, two standing clocks; progress_age 60 to 70 over a floor means it reset and re-aged
    table = IN.load_table()
    rev = table["policy"]["owner_revisit_min"]
    def belt(age, under, name, t0=T0):
        path = os.path.join(TMP, name + ".jsonl")
        ms = {"relentless.progress_age_min": {"class": "distressed", "event": False}, "relentless.under_min": {"class": "distressed", "event": False}}
        IN.append([{"ev": "opened", "id": "work_belt-1", "at": IN.iso(t0), "t": t0, "state": "open", "rung": IN.OWNER_RUNG, "rung_t": t0, "told_t": t0 - 9 * H,
                    "told_at": IN.iso(t0 - 9 * H), "cause": "work_belt", "class": "distressed", "metrics": ms, "items": [], "reader": "Operations", "ack_min": 30,
                    "acked_t": t0 + M, "recover_by_t": t0 + H, "recover_by": IN.iso(t0 + H), "ack_by": "OPERATIONS", "plan": "waiting on the fix", "revisit_t": t0,
                    "revisit_seen_t": t0, "revisit_status_t": t0, "revisits": 1, "revisit_read": {"relentless.progress_age_min": [True, "distressed", 60, True, 0],
                                                                                                 "relentless.under_min": [True, "distressed", 100, True, 0]}}], path)
        now = t0 + rev * M
        pts = {"relentless.progress_age_min": {"m": "MEASURED", "v": age, "class": "distressed"}, "relentless.under_min": {"m": "MEASURED", "v": under, "class": "distressed"}}
        return IN.step(table, IN.read_rows(path), {"t": now, "points": pts, "alarms": {}}, now)
    res = belt(70, 100 + rev, "beltreset")
    ev = [x for x in res["rows"] if x["ev"] in ("revisited", "revisit_quiet")]
    check("chain: real routes, a standing clock that reset and re-aged launches though it reads higher, its pair only aged",
          [x["ev"] for x in ev] == ["revisited"] and [r["id"] for r in res["rings"] if r.get("revisit")] == ["work_belt-1"]
          and "relentless.progress_age_min" in " ".join(ev[0]["news"]) and "relentless.under_min" not in " ".join(ev[0]["news"]), res["rows"])
    res = belt(60 + rev, 100 + rev, "beltaged")
    ev = [x for x in res["rows"] if x["ev"] in ("revisited", "revisit_quiet")]
    check("chain: real routes, both clocks only aged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"] and not res["rings"], res["rows"])
    x = IN.fold(IN.read_rows(os.path.join(TMP, "beltaged.jsonl")) + res["rows"])[0]["work_belt-1"]
    check("chain: the quiet row keeps the status time it read", x["revisit_status_t"] == T0 + rev * M, x)


def test_each_field_of_a_reading():
    """Blind check b63b949a: each field reading_moved compares has a row where ONLY that field changes, reached through
    step(): the standing flag on a class-less key, the measured mark on a sane metric, the status time a launch stores."""
    rev = IN.load_table()["policy"]["owner_revisit_min"]

    def two(name, other):
        """q-1 stands throughout, so the incident stays open; `other` is the metric whose one field a row changes."""
        table, _, rows = at_his_rung("q-1")
        rows = [dict(rows[0], metrics=dict(rows[0]["metrics"], **{"m.z": {"class": "distressed", "event": False}}),
                     revisit_read={"m.q-1": [True, "distressed", 5, True, 0], "m.z": other})]
        path = os.path.join(TMP, name + ".jsonl")
        IN.append(rows, path)

        def look(now, z, alarms=None):
            res = IN.step(table, IN.read_rows(path), {"t": now, "points": {"m.q-1": {"m": "MEASURED", "v": 5, "class": "distressed"}, "m.z": z},
                                                      "alarms": alarms or {}}, now)
            IN.append(res["rows"], path)
            return res, [x for x in res["rows"] if x["ev"] in ("revisited", "revisit_quiet")]
        return look, lambda: IN.next_due(table, IN.fold(IN.read_rows(path))[0]["q-1"])

    def launched(name, res, ev):
        check(name, [x["ev"] for x in ev] == ["revisited"] and [r["id"] for r in res["rings"] if r.get("revisit")] == ["q-1"]
              and "m.z" in " ".join(ev[0]["news"]), res["rows"])

    # the standing flag alone: a class-less key has no class to change, its value and measured mark stay
    plain = {"m": "MEASURED", "v": 3}
    look, due = two("standingon", [False, None, 3, True, 0])
    res, ev = look(due(), plain)
    check("chain: a class-less key with no alarm, unchanged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"] and not res["rings"], res["rows"])
    res, ev = look(due(), plain, {"ops:m.z": {"state": "OPEN"}})
    check("chain: only its standing flag differs", IN.revisit_reads({"metrics": {"m.z": {}}}, {"points": {"m.z": plain}}, {"m.z": {}}, [])["m.z"] == [True, None, 3, True, 0])
    launched("chain: an alarm coming open on a class-less key launches, class, value and mark unchanged", res, ev)
    look, due = two("standingoff", [True, None, 3, True, 0])
    res, ev = look(due(), plain, {"ops:m.z": {"state": "OPEN"}})
    check("chain: a class-less key with its alarm still open, unchanged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"], res["rows"])
    res, ev = look(due(), plain)
    launched("chain: that alarm clearing launches, class, value and mark unchanged", res, ev)

    # the measured mark alone: a sane metric goes blind, standing no way, class and value as they were
    sane = {"m": "MEASURED", "v": 3, "class": "sane"}
    look, due = two("markoff", [False, "sane", 3, True, 0])
    res, ev = look(due(), sane)
    check("chain: a sane metric, unchanged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"] and not res["rings"], res["rows"])
    res, ev = look(due(), dict(sane, m="UNMEASURED"))
    launched("chain: a sane metric going UNMEASURED launches, standing, class and value unchanged", res, ev)
    look, due = two("markon", [False, "sane", 3, False, 0])
    res, ev = look(due(), dict(sane, m="UNMEASURED"))
    check("chain: a sane class stuck UNMEASURED, unchanged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"], res["rows"])
    res, ev = look(due(), sane)
    launched("chain: and it being measured again launches", res, ev)

    # the class alone, on a metric that stands neither time
    look, due = two("classonly", [False, "sane", 3, True, 0])
    res, ev = look(due(), dict(sane, **{"class": "idle"}))
    launched("chain: sane to idle launches, standing, value and mark unchanged", res, ev)

    # the status time a launch stores: quiet, launch, ack, then a floor of a clock that only aged since the LAUNCH
    path, inc, look, due = chain("launchstatus", metric="r.under_min")
    t = due()
    res, evs = look(t, v=5 + rev)
    check("chain: quiet first, so an older status time is on the row", evs == ["revisit_quiet"] and inc()["revisit_status_t"] == t, res["rows"])
    t = due()
    res, evs = look(t, v=10)
    check("chain: then the clock resets and it launches", evs == ["revisited"] and res["rings"], res["rows"])
    check("chain: the launch stores the status time it read", inc()["revisit_status_t"] == t and res["rows"][0]["revisit_status_t"] == t, res["rows"])
    IN.ack("q-1", "OPERATIONS", "watching it re-age", path=path, now=t + M)
    t2 = due()
    res, evs = look(t2, v=10 + (t2 - t) // M)
    check("chain: answered, then a floor of the clock only aging since the launch is quiet", evs == ["revisit_quiet"] and not res["rings"], res["rows"])
    res, evs = look(due(), v=10)
    check("chain: and a clock not aging after that launches", evs == ["revisited"], res["rows"])

    # the shipped slack is what the slack rows mean: a status tick off the floor must not launch
    table = IN.load_table()
    slack = table["policy"]["revisit_clock_slack_min"]
    check("quiet: the shipped table has a slack, a status is never read on the minute", slack >= 1, slack)
    path, inc, look, due = chain("slackchain", metric="r.under_min")
    res, evs = look(due(), v=5 + rev - 1)
    check("quiet: a clock a minute short of the floor, on the shipped table, only aged", evs == ["revisit_quiet"], res["rows"])

    # the pull-in look judges by status time too: a lagging status must not pull in a clock that only aged
    table, rev, rows = at_his_rung("a-1", "b-1")
    b_t = rows[1]["t"]
    rows[1] = dict(rows[1], metrics={"r.b_min": {"class": "distressed", "event": False}}, revisit_status_t=b_t,
                   revisit_read={"r.b_min": [True, "distressed", 5, True, 0]})
    now = T0 + rev * M + M
    st_t = now - 10 * M

    def pulled(b):
        res = IN.step(table, rows, {"t": st_t, "points": {"m.a-1": {"m": "MEASURED", "v": 6, "class": "distressed"},
                                                          "r.b_min": {"m": "MEASURED", "v": b, "class": "distressed"}}, "alarms": {}}, now)
        return [x["id"] for x in res["rows"] if x["ev"] == "revisited"]
    aged = 5 + (st_t - b_t) // M
    check("batch: under a lagging status, a clock that only aged by status time is not pulled in", pulled(aged) == ["a-1"], pulled(aged))
    check("batch: and one that moved is", pulled(aged + 30) == ["a-1", "b-1"], pulled(aged + 30))


def test_signal_through_step():
    """Blind check b666afff: 'a fired signal still launches' with the count step() itself stores. A standing metric and an
    event metric under one cause: launch, ack, quiet, then a signal fires -> the next due launches, news names it."""
    table, _, rows = at_his_rung("q-1")
    ms = {"m.q-1": {"class": "distressed", "event": False}, "sig.x": {"class": "distressed", "event": True}}
    rows = [dict(rows[0], metrics=ms, revisit_read={"m.q-1": [True, "distressed", 5, True, 0], "sig.x": [False, None, None, False, 0]})]
    path = os.path.join(TMP, "sigchain.jsonl")
    IN.append(rows, path)
    inc = lambda: IN.fold(IN.read_rows(path))[0]["q-1"]
    due = lambda: IN.next_due(table, inc())

    def look(now, v=6):
        res = IN.step(table, IN.read_rows(path), {"t": now, "points": {"m.q-1": {"m": "MEASURED", "v": v, "class": "distressed"}}, "alarms": {}}, now)
        IN.append(res["rows"], path)
        return res, [x for x in res["rows"] if x["ev"] in ("revisited", "revisit_quiet")]

    def fire(now):
        IN.append([{"kind": "sig.x", "metric": "sig.x", "why": "fired", "told_at": IN.iso(now), "class": "distressed"}], path)

    def launched(name, res, ev):
        check(name, [x["ev"] for x in ev] == ["revisited"] and [r["id"] for r in res["rings"] if r.get("revisit")] == ["q-1"]
              and "sig.x" in " ".join(ev[0]["news"]) and "m.q-1" not in " ".join(ev[0]["news"]), res["rows"])
    t = due()
    res, ev = look(t)
    check("chain: signal: the standing metric moved, it launches", [x["ev"] for x in ev] == ["revisited"] and res["rings"], res["rows"])
    IN.ack("q-1", "OPERATIONS", "waiting on the fix", path=path, now=t + M)
    res, ev = look(due())
    check("chain: signal: answered, nothing fired, unchanged: quiet", [x["ev"] for x in ev] == ["revisit_quiet"] and not res["rings"], res["rows"])
    fire(due() - M)
    t = due()
    res, ev = look(t)
    launched("chain: signal: a signal fired after a quiet look launches, the standing metric unchanged", res, ev)
    check("chain: signal: the launch stores the count step() read", inc()["revisit_read"]["sig.x"][4] == 1, inc()["revisit_read"])
    IN.ack("q-1", "OPERATIONS", "waiting on the fix", path=path, now=t + M)
    res, ev = look(due())
    check("chain: signal: answered, no new signal: quiet", [x["ev"] for x in ev] == ["revisit_quiet"] and not res["rings"], res["rows"])
    fire(due() - M)
    res, ev = look(due())
    launched("chain: signal: a second signal (count 1 to 2) launches again", res, ev)
    check("chain: signal: and the count is now 2", inc()["revisit_read"]["sig.x"][4] == 2, inc()["revisit_read"])


def test_news_each_state_event():
    table, rev, rows = at_his_rung("q-1")
    now = T0 + rev * M
    st = status_of(now, q_1=5)

    def evs(extra):
        return [x["ev"] for x in IN.step(table, rows + extra, st, now)["rows"]]
    for e in ("joined", "sane", "relapsing", "reopened", "escalated"):
        got = IN.step(table, rows + [{"ev": e, "id": "q-1", "t": now - H}], st, now)["rows"]
        check("news: %s since the last look launches" % e, [x["ev"] for x in got] == ["revisited"]
              and "state moved" in " ".join(got[0]["news"]), got)
    check("news: a state event before the last look is old news",
          evs([{"ev": "joined", "id": "q-1", "t": T0 - H}]) == ["revisit_quiet"], rows)


def test_batch_text_and_quiet_pulls_nothing():
    table, rev, rows = at_his_rung("a-1", "b-1")
    now = T0 + rev * M + M
    res = IN.step(table, rows, status_of(now, a_1=6, b_1=6), now)
    r = Rig("revtext")

    def why(rings):
        dst = {"roles": {}}
        D.incident_execute(dict(res, rings=rings, rows=[]), r.sch, dst, "/nonexistent", now, lambda *x: None, lambda *x: None)
        return dst["roles"]["Operations"]["run_now"]["why"]
    check("batch text: all revisits say so and name the ack", "revisits due together" in why(res["rings"]) and "rimflow ack" in why(res["rings"]), res["rings"])
    check("batch text: a revisit among other rings keeps the plain text",
          "all reach him next" in why([res["rings"][0], dict(res["rings"][1], revisit=False)]), res["rings"])
    check("batch text: one alone is its own text", why(res["rings"][:1]).startswith("INCIDENT a-1"), res["rings"])
    quiet = IN.step(table, rows, status_of(now, a_1=5, b_1=6), now)
    check("batch: a quiet look starts no run, so it pulls nothing in early", [x["ev"] for x in quiet["rows"]] == ["revisit_quiet"]
          and not quiet["rings"], quiet["rows"])


def test_incidents_verb_says_the_news():
    r = Rig("verb")
    table, rev, rows = at_his_rung("a-1")
    now = T0 + rev * M
    IN.append(rows + IN.step(table, rows, status_of(now, a_1=6), now)["rows"], IN.told_path())
    # seatless, as the nightly timer runs it: the verb only reads (NIGHTLY_COP_FIX_RED_HPZIOX_GMAU)
    env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    out = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "incidents"], env=env, capture_output=True, text=True, timeout=120)
    check("verb: rimflow incidents names a revisit's news", "news readings moved: m.a-1" in out.stdout, (out.stdout[-400:], out.stderr[-400:], r.root))


# The revisits told.jsonl held on 2026-11-03, before this change: the epochs of those 27 rows, so the replay stands
# where the machine's file does not.
RECORDED_REVISITS = [1793638866] * 6 + [1793653694] * 5 + [
    1793668178, 1793675613, 1793682583, 1793696859, 1793696997, 1793697266, 1793711469, 1793711719, 1793717552, 1793725932,
    1793726181, 1793726830, 1793732175, 1793740406, 1793740406, 1793748134]


def runs_through_step(ts):
    """Each revisit one incident falling due at its recorded time, its reading moved: step() decides who goes together.
    -> the passes that launched. One pass's fresh rings are one run (incident_execute)."""
    table, rev, _ = at_his_rung("x-1")
    iids = ["r%d-1" % k for k in range(len(ts))]
    _, _, rows = at_his_rung(*iids)
    waiting = {i: dict(row, rung_t=t - rev * M, revisit_t=t - rev * M, revisit_seen_t=t - rev * M, told_t=t - 9 * H, told_at=IN.iso(t - 9 * H),
                       acked_t=None, recover_by_t=None, plan="the old plan")
               for i, row, t in zip(iids, rows, ts)}
    runs = 0
    vals = {i.replace("-", "_"): 6 for i in iids}
    for t in sorted(set(ts)):
        if not waiting:
            break
        res = IN.step(table, list(waiting.values()), status_of(t, **vals), t)
        runs += 1 if res["rings"] else 0
        for x in res["rows"]:
            if x["ev"] == "revisited":
                waiting.pop(x["id"], None)
    return runs


class _Lock:
    def close(self):
        pass


def test_relapse_tamed():
    """INCIDENT_RELAPSE_TAME_STOP_FULL_READS on the real path (ops_watch.run, dispatcher.tick --apply). The 2026-11-01
    plan incident's shape first: opened, acked, recovered and closed, reopened, acked, sane, then bad again BEFORE it
    closed -- one relapse and a join, so nothing is tamed. Then it closes and comes back: the second relapse in 24 h buys
    no full Operations read, files one structural item quoting both acks, and still climbs its ladder."""
    import model
    r = Rig("tamed")
    filed = []
    r.sch["publish"] = True                      # the tick takes ingest.lock only to publish: the filer runs under it
    r.fx = {"lock": _Lock, "incident_file": lambda x: (filed.append(x), (True, "filed"))[1]}
    plans = ["drop done entries from the priority list", "drop done entries again, the list refilled"]
    r.tick(T0, relentless__under_min=40)
    i = r.inc()[0]["id"]
    IN.ack(i, "OPERATIONS", plans[0], now=T0 + 5 * M)
    for m in (10, 40, 71):
        r.tick(T0 + m * M, relentless__under_min=0)
    check("tame: the plan incident closed on its readings", r.inc()[0]["state"] == "closed", r.inc())
    r.tick(T0 + 2 * H, relentless__under_min=40)
    IN.ack(i, "OPERATIONS", plans[1], now=T0 + 2 * H + 5 * M)
    r.tick(T0 + 2 * H + 10 * M, relentless__under_min=0)
    r.tick(T0 + 2 * H + 15 * M, relentless__under_min=50)       # 15:38 on 11-01: bad again before it closed
    x = r.inc()[0]
    check("tame: closed-then-back is one relapse; acks and a dip before closing are none (plan-20261101164253)",
          len(r.evs("reopened")) == 1 and len(r.evs("relapsing")) + len(r.evs("joined")) == 1 and len(r.evs("acked")) == 2
          and not x.get("tamed") and not r.evs("tamed") and not r.evs("withheld") and not filed, ([e["ev"] for e in r.rows()], x))
    r.tick(T0 + 2 * H + 30 * M, relentless__under_min=0)
    r.tick(T0 + 3 * H + 31 * M, relentless__under_min=0)
    check("tame: closed again", r.inc()[0]["state"] == "closed", r.inc())
    before = IN.read_rows()
    runs0, ask0 = len(r.alarm_runs()), (r.asked("Operations") or {}).get("ids") or []
    t2 = T0 + 4 * H
    r.tick(t2, relentless__under_min=40)
    st2 = json.load(open(r.sch["ops_status"]))
    ctrl = json.loads(json.dumps(TABLE))
    ctrl["policy"]["tame_relapses"] = 3
    c = IN.step(ctrl, before, st2, t2)
    check("tame control: at three, the same pass makes its alarm-run key and rings the full read (the check can fail)",
          any(i in k for k in c["keys"]) and any(g["id"] == i and g["how"] in IN.FULL_READS for g in c["rings"])
          and not any(g["how"] == "structural" for g in c["rings"]), (c["keys"], c["rings"]))
    x = r.inc()[0]
    tm = r.evs("tamed")
    check("tame: the second relapse in 24 h tames it, and it stays open", x["state"] == "open" and x.get("tamed")
          and len(tm) == 1 and tm[0]["relapses"] == 2, (x, tm))
    p = IN.step(TABLE, before, st2, t2)
    check("tame: that pass makes no alarm-run key and rings no full read, a withheld row says so",
          not any(i in k for k in p["keys"]) and not any(g["how"] in IN.FULL_READS and g["id"] == i for g in p["rings"])
          and [w["withheld"] for w in r.evs("withheld")] == ["alarm_run"], (p["keys"], p["rings"], r.evs("withheld")))
    check("tame: no Operations run was bought", len(r.alarm_runs()) == runs0
          and (i not in ((r.asked("Operations") or {}).get("ids") or []) or i in ask0), (r.alarm_runs()[runs0:], r.asked("Operations")))
    name = x.get("structural")
    check("tame: one structural item filed, a valid new name, quoting both acks", len(filed) == 1 and filed[0]["item"] == name
          and not model.mint_problems(name, set()) and all(q in filed[0]["text"] for q in plans)
          and filed[0]["from"] == TABLE["policy"]["structural_from"] and x.get("structural_filed") == name, (filed, name, x))
    for m in range(15, 9 * 60, 15):
        r.tick(t2 + m * M, relentless__under_min=40)
    x = r.inc()[0]
    hows = [w["withheld"] for w in r.evs("withheld")]
    check("tame: filed once however many passes", len(filed) == 1, filed)
    check("tame: it still climbs its ladder to his rung, open, the Conductor rung rung and the fresh read withheld",
          x["state"] == "open" and x["rung"] >= IN.OWNER_RUNG and any(o["id"] == i for o in r.snap()["owner"])
          and "fresh_run" in hows and any(e.get("ev") == "escalated" and e.get("rung") == 1 for e in r.evs("escalated"))
          and i not in ((r.asked("Operations") or {}).get("ids") or []), (x, hows, r.asked("Operations")))
    w = [o for o in r.snap()["open"] if o["id"] == i]
    check("tame: the snapshot says it is tamed and names its item", w and w[0]["tamed"] and w[0]["structural"] == name, w)


def test_tamed_filer_waits_and_retries():
    """The structural ring outlives a pass with no ingest lock, and a failed filing: it is filed once, when it can be."""
    r = Rig("tame_retry")
    rows = [{"ev": "opened", "id": "c-1", "at": IN.iso(T0), "t": T0, "state": "open", "cause": "c", "rung": 1, "rung_t": T0,
             "told_t": T0, "told_at": IN.iso(T0), "class": "distressed", "metrics": {}, "items": [], "reader": "Operations",
             "ack_min": 30, "tamed": True, "structural": IN.structural_name("c"), "relapses": 2, "acks": ["a by B: p"]}]
    IN.append(rows)
    st = {}
    calls = []

    def go(now, do_file):
        res = IN.step(TABLE, IN.read_rows(), {"t": now, "points": {}, "alarms": {}}, now)
        return [g for g in res["rings"] if g["how"] == "structural"], D.incident_execute(
            dict(res), r.sch, st, "/nonexistent", now, lambda *a: None, lambda *a: None, do_file)
    g, said = go(T0 + M, None)
    check("tame retry: no lock, the ring waits and nothing is written", len(g) == 1 and "waits" in said
          and not [x for x in IN.read_rows() if x.get("ev") == "structural_filed"], said)
    g, said = go(T0 + 2 * M, lambda x: (calls.append(x), (False, "refused"))[1])
    check("tame retry: a failed filing writes no filed row", "FAILED" in said
          and not [x for x in IN.read_rows() if x.get("ev") == "structural_filed"], said)
    g, said = go(T0 + 3 * M, lambda x: (calls.append(x), (True, "filed"))[1])
    g2, _ = go(T0 + 4 * M, lambda x: (calls.append(x), (True, "filed"))[1])
    check("tame retry: filed on the pass it can be, then never again", len(g) == 1 and not g2 and len(calls) == 2, (calls, g2))
    names = {IN.structural_name(c) for c in ("work_belt", "ops_watch.blind", "x" * 60, "")}
    check("tame: every structural name a cause can make passes namecheck", all(
        not __import__("model").mint_problems(n, set()) for n in names), names)


def test_disjoint_reopen_is_new_incident():
    """RELAPSE_OPS_WATCH_FIX_DIED_TWICE: ops_watch-20261104035601 was tamed as a fix that died twice, but its three
    episodes were three different alarms under the catch-all cause ops_watch (a GAME_HEALTH filing refused by namecheck,
    dead token-talk flags, a SCRATCH_DIRTY_END filing on a retired item), each fixed and holding. A closed incident
    reopens only when a metric it held comes back; a disjoint one under the same cause is a new incident."""
    table = IN.load_table()
    pol = table["policy"]
    q = pol["event_quiet_min"] * M
    rows, cur = [], [0]

    def tick(now, *metrics):
        rows.extend({"metric": m, "class": "distressed", "at": IN.iso(now), "t": now} for m in metrics)
        res = IN.step(table, rows, {"t": now, "points": {}, "alarms": {}}, now, cur[0])
        rows.extend(res["rows"])
        cur[0] = len(rows)
        return res

    def episode(t, metric):         # bad, sane at once, closed after event_quiet_min: the instance's three episodes
        tick(t, metric)
        tick(t + M)
        tick(t + M + q + M)
        return t + M + q + M

    a, b, c = ("ops:file_failed:GAME_HEALTH:tps.health_breaches", "ops:flag:process.share_7d",
               "ops:file_failed:SCRATCH_DIRTY_END:disk.scratch_dirty_end")
    t = T0
    for m in (a, b, c):
        t = episode(t, m) + H       # each next alarm comes an hour after the last closed, inside relapse_h
    incs, _ = IN.fold(rows)
    evs = [r["ev"] for r in rows if "ev" in r]
    check("disjoint: three different ops_watch alarms, each back inside relapse_h, are three incidents",
          len(incs) == 3 and sorted(next(iter(x["metrics"])) for x in incs.values()) == sorted((a, b, c)), incs)
    check("disjoint: no reopened, tamed or structural row: no fix died", not {"reopened", "tamed"} & set(evs)
          and not any(x.get("tamed") for x in incs.values()), evs)
    t = episode(t, a)               # control: the FIRST alarm itself comes back, long past relapse_h of its close
    incs, _ = IN.fold(rows)
    check("disjoint control: a metric back past relapse_h of its incident's close opens a new incident",
          len(incs) == 4 and not any(x.get("reopens") for x in incs.values()), incs)
    tick(t + H, a)                  # and once more, an hour after that incident closed
    incs, _ = IN.fold(rows)
    back = [x for x in incs.values() if x.get("reopens")]
    check("disjoint control: the same metric back inside relapse_h reopens its own incident (the check can fail)",
          len(incs) == 4 and len(back) == 1 and a in back[0]["metrics"] and back[0]["state"] == "open", incs)


def test_standing_source_holds_incident_open():
    """RELAPSE_HELPERS_FIX_DIED_TWICE: helpers-20261101162643 closed 2026-11-02 11:29:28Z on event_quiet_min (a
    Dispatcher alarm has no sane value) after a 5.6 h tick gap, while helper_lost:3378fb18's receipt was still unacked;
    the same tick's repeat reopened it 2 min later, and that reopen was counted as an ack's fix dying. With the
    Dispatcher's standing reading a signal metric is read like any other: open while its source stands, closed on
    sustain_min once it is gone, and a stale reading is unknown, never quiet."""
    table = IN.load_table()
    pol = table["policy"]
    lost = "helper_lost:3378fb18"
    max_age = pol["status_max_age_min"] * M

    def run(standing_at, until, start=T0, step_s=5 * M, fire_at=(T0,)):
        rows, cur = [], 0
        t = start
        while t <= until:
            rows.extend({"metric": lost, "class": None, "at": IN.iso(t), "t": t} for f in fire_at if f == t)
            res = IN.step(table, rows, {"t": t, "points": {}, "alarms": {}}, t, cur, standing=standing_at(t))
            rows.extend(res["rows"])
            cur = len(rows)
            t += step_s
        return IN.fold(rows)[0], rows

    q = pol["event_quiet_min"] * M
    incs, _ = run(lambda t: None, T0 + q + 30 * M)
    check("standing control: with no reader the signal incident closes on event_quiet_min (the old rule; the check can fail)",
          [x["state"] for x in incs.values()] == ["closed"], incs)
    incs, _ = run(lambda t: {"helper_lost": {"t": t, "keys": [lost]}}, T0 + q + 3 * H)
    check("standing: an unacked receipt read fresh every tick holds its incident open past event_quiet_min",
          [x["state"] for x in incs.values()] == ["open"] and not any(x.get("sane_since") for x in incs.values()), incs)
    gap_end = T0 + 9.8 * H                          # the instance: last tick 05:52Z, next 11:29Z, reading from before
    incs, rows = run(lambda t: {"helper_lost": {"t": min(t, T0 + H), "keys": [lost]}}, gap_end, step_s=H / 5)
    check("standing: a reading staler than status_max_age_min is unknown, never quiet: no close across the tick gap",
          [x["state"] for x in incs.values()] == ["open"] and "closed" not in [r.get("ev") for r in rows], incs)
    acked = T0 + 2 * H
    incs, rows = run(lambda t: {"helper_lost": {"t": t, "keys": [lost] if t < acked else []}},
                     acked + pol["sustain_min"] * M + 10 * M)
    closed = [r for r in rows if r.get("ev") == "closed"]
    check("standing: once the receipt is acked the incident closes on sustain_min, not event_quiet_min",
          len(closed) == 1 and acked + pol["sustain_min"] * M <= closed[0]["t"] <= acked + pol["sustain_min"] * M + 5 * M,
          [(r.get("ev"), r.get("at")) for r in rows])
    check("standing_of: a <scope>:reader metric and an uncovered metric are not judged by any reading",
          IN.standing_of({"helper_lost": {"t": T0, "keys": []}}, "helper_lost:reader", T0, max_age) is None
          and IN.standing_of({"helper_lost": {"t": T0, "keys": []}}, "long_helper:abc", T0, max_age) is None
          and IN.standing_of({"budget:failed": {"t": T0, "keys": []}}, "budget:failed", T0, max_age) is False
          and IN.standing_of({"budget:failed": {"t": T0 - max_age - 1, "keys": []}}, "budget:failed", T0, max_age) == "stale")


def test_replay_recorded():
    n = runs_through_step(RECORDED_REVISITS)
    check("replay: the 27 recorded revisits are 12 runs through step()", n == 12, n)


def replay_batch():
    """Read-only: the real told.jsonl's revisits, as launched and as step() now groups them. A file that does not read is
    UNMEASURED, never zero; the recorded 27 are replayed either way."""
    print("replay: recorded 2026-11-03: %d revisits are %d runs through step()" % (len(RECORDED_REVISITS), runs_through_step(RECORDED_REVISITS)))
    path = os.path.join(IN.REAL_OPS, "told.jsonl")
    rows = IN.read_rows(path) if os.path.exists(path) else None
    if rows is None:
        print("replay: live told.jsonl UNMEASURED: %s does not read here" % path)
        return 0
    ts = sorted(r["t"] for r in rows if r.get("ev") == "revisited" and not r.get("news"))
    win = TABLE["policy"]["revisit_batch_min"]
    print("replay: live told.jsonl: %d revisits landed before this change; batched inside %d min they are %d runs (%d distinct launch ticks on record)"
          % (len(ts), win, runs_through_step(ts), len({int(t // 120) for t in ts})))
    return 0


# Role alarms reviewed as faults an Operations incident should hold (cause roles, via the role:* fallthrough).
# RELAPSE_ROLES_FIX_DIED_TWICE: a role_launch alarm kind not on this list and not routed by its own row fails below, so
# a new doorbell or self-retrying state cannot fall into cause roles unseen and reopen it as a "dead fix".
ROLE_INCIDENT_SUFFIXES = {"supervise", "unit", "overtime", "stop_failed", "stage_rejected", "stage_close", "stage_land", "failed",
                          "after", "schedule", "ops", "stage_refused"}


def test_role_relapse_kinds_do_not_reopen():
    """RELAPSE_ROLES_FIX_DIED_TWICE: roles-20261103041057 was tamed after reopens by role:Conductor:scope (a run's unit
    collected a tick before its scope or marked processes: re-checked every tick, a stuck one alarms as overtime) and
    role:Designer:waiting_owner (a doorbell raised first in the Conductor log). Neither is a fix that can die."""
    table = IN.load_table()
    for kind in ("role:Designer:waiting_owner", "role:Conductor:scope", "role:Operations:scope", "role:Designer:scope"):
        r = IN.route_of(table, kind)
        check("%s routes program" % kind, r is not None and r.get("route") == "program", r)
    for kind in ("role:Conductor:overtime", "role:Conductor:stop_failed", "role:Operations:failed"):
        r = IN.route_of(table, kind)
        check("%s still reaches an Operations incident" % kind, r is not None and r.get("route") == "role", r)
    src = open(os.path.join(HERE, "role_launch.py"), encoding="utf-8").read()
    emitted = set(re.findall(r'kind="role:%s:([a-z_]+)"', src))
    check("role_launch alarm kinds are read (sanity: scope, waiting_owner, overtime among them)",
          {"scope", "waiting_owner", "overtime"} <= emitted, sorted(emitted))
    fall = {x for x in emitted if (IN.route_of(table, "role:Any:" + x) or {}).get("match") == "role:*"}
    check("every role_launch alarm falling through to cause roles is a reviewed fault (new: %s; gone: %s)" % (
          sorted(fall - ROLE_INCIDENT_SUFFIXES), sorted(ROLE_INCIDENT_SUFFIXES - fall)), fall == ROLE_INCIDENT_SUFFIXES)
    pol = table["policy"]
    q = pol["event_quiet_min"] * M
    rows, cur = [], [0]

    def tick(now, *metrics):
        rows.extend({"metric": m, "class": "distressed", "at": IN.iso(now), "t": now} for m in metrics)
        res = IN.step(table, rows, {"t": now, "points": {}, "alarms": {}}, now, cur[0])
        rows.extend(res["rows"])
        cur[0] = len(rows)

    def episode(t, *metrics):
        tick(t, *metrics)
        tick(t + M)
        tick(t + M + q + M)
        return t + M + q + M + H

    t = episode(T0, "role:Conductor:scope")       # the instance: scope, scope, then a Designer ask, each inside relapse_h
    t = episode(t, "role:Conductor:scope", "role:Designer:waiting_owner")
    t = episode(t, "role:Designer:waiting_owner")
    evs = [r["ev"] for r in rows if "ev" in r]
    check("instance: the incident's relapse kinds open, reopen and tame nothing", not evs, evs)
    t = episode(t, "role:Conductor:overtime")      # control: a real role fault back inside relapse_h still reopens
    episode(t, "role:Conductor:overtime")
    evs = [r["ev"] for r in rows if "ev" in r]
    check("control: role:Conductor:overtime back inside relapse_h reopens its incident (the check can fail)",
          "opened" in evs and "reopened" in evs, evs)


if "--replay-batch" in sys.argv:
    sys.exit(replay_batch())
for t in (test_standing_source_holds_incident_open, test_silent_reader, test_chain_dedupe, test_emergency_all_dead, test_ack_then_killed, test_ring_or_read_is_no_ack, test_one_outage,
          test_batched_run_held_and_covers_slot, test_denied_goes_to_conductor_first, test_relapse, test_blind_and_signal, test_ledger_unwritable, test_census_forms, test_alarms_reach_ledger, test_routes, test_spend_alarms_do_not_buy_runs,
          test_owner_rung_revisited, test_revisits_batched, test_revisit_quiet, test_quiet_on_the_real_path,
          test_escalation_clear_through_step, test_chains_through_step, test_each_field_of_a_reading, test_signal_through_step, test_news_each_state_event, test_batch_text_and_quiet_pulls_nothing,
          test_incidents_verb_says_the_news, test_replay_recorded, test_relapse_tamed, test_tamed_filer_waits_and_retries,
          test_disjoint_reopen_is_new_incident, test_role_relapse_kinds_do_not_reopen):
    t()
print("selftest_incident: %s (%d fails)" % ("FAIL" if FAILS else "OK", len(FAILS)))
sys.exit(1 if FAILS else 0)
