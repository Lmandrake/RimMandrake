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
import replay_watch as RW  # noqa: E402
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
    check("distressed: fresh Operations run at 60", r.inc()[0]["rung"] == 2, r.inc())
    r.tick(T0 + 239 * M, relentless__under_min=100)
    check("distressed stays from him until 4 h", r.inc()[0]["rung"] == 2 and not r.snap()["owner"], r.snap())
    r.tick(T0 + 240 * M, relentless__under_min=100)
    check("distressed reaches him at 4 h", r.inc()[0]["rung"] == 3 and len(r.snap()["owner"]) == 1, r.snap())


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
    r.tick(T0, arena__two_live=1)
    x = r.inc()
    check("a doorbell reader's incident opens", x and x[0]["reader"] == "FOUNDRY", x)
    inbox = doorbell.inbox_path("FOUNDRY")
    check("it rings the seat by doorbell", os.path.exists(inbox) and x[0]["id"] in open(inbox).read(), inbox)
    got = doorbell.take_ring("FOUNDRY")
    check("the doorbell delivers it", got and x[0]["id"] in json.dumps(got), got)
    r.tick(T0 + 5 * M, arena__two_live=1)
    check("a ring, a consume and a read write no ack", not r.evs("acked") and not r.inc()[0].get("acked_t"), r.rows())
    check("one ring only", not os.path.exists(inbox) and len(r.evs("opened")) == 1, r.evs("opened"))
    r.tick(T0 + 30 * M, arena__two_live=1)
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
"""


def source_kinds():
    """The census of the real tree, with what it could not read."""
    return AC.census(os.path.join(HERE, ".."))


def test_census_forms():
    k, bad = AC.of_source(FORMS)
    want = {"lit:one", "dead:x", "role:x:cap", "r:x:x", "fs:x:z", "var:one", "var:two", "module_k:v", "dict:one",
            "var:one:tail", "var:two:tail", "param:x", "appended:one"}
    check("the census reads every form a kind is written in", k == want and not bad, (sorted(k ^ want), bad))
    for src, name in (('def f(a):\n    act(do="alarm", kind=a["kind"])\n', "a subscript"),
                      ('def f(k):\n    act(do="alarm", kind=k)\n', "a parameter nobody passes"),
                      ('def f(q):\n    act(do="alarm", kind=g(q))\n', "a call"),
                      ('def f(a):\n    act(do="alarm", kind="%s" % a)\n', "a format with no literal")):
        check("the census fails loudly on " + name, AC.of_source(src)[1], src)


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
    w = object.__new__(RW.World)
    w.told("stalled:a1:abcd1234", "w", T0)
    check("a replay watch alarm joins the ledger", IN.read_rows()[-1].get("kind") == "stalled:a1:abcd1234", IN.read_rows()[-1])


def test_routes():
    found, unread, files = source_kinds()
    check("no alarm site in the tree is unreadable by the census", not unread, unread)
    named = {"publish:index_lock", "publish:stuck", "budget:failed", "dry:live_runs_unsupervised", "breaker_emergency", "jam",
             "understaffed", "books_stale", "step_raised", "lease_raised", "quarantine", "dead:x", "stalled:x:x"}
    check("the census sees the variable and dict forms, relentless and replay_watch", named <= found, sorted(named - found))
    check("the census walked every module that raises one", {os.path.basename(f) for f in files} >= {
        "dispatcher.py", "relentless.py", "helper_budget.py", "role_launch.py", "signal_watch.py", "login_watch.py",
        "seat_restart.py", "replay_watch.py"}, files)
    literal = set()
    for f in files:
        literal |= {m for m in re.findall(r'kind="([a-z_]+:[a-z_:]+)"', open(f, encoding="utf-8").read())
                    if not m.endswith(":")}
    check("every plain kind= literal is in the census", literal <= found, sorted(literal - found))
    kinds = found | {t["key"].replace("*", "x") for t in RULES["targets"] if t.get("alarm")} | set(OW.ranges_of(RULES))
    missing = [k for k in sorted(kinds) if IN.route_of(TABLE, k) is None]
    check("every alarm kind is in the routing table", not missing, missing)
    for kind in ("dead:x", "publish:stuck", "budget:failed", "jam"):
        t2 = dict(TABLE, routes=[x for x in TABLE["routes"] if not fnmatch.fnmatchcase(kind, x["match"])])
        check("%s dropped from the table is seen missing" % kind, kind in [k for k in sorted(kinds) if IN.route_of(t2, k) is None])
    bad = [x for x in TABLE["routes"] if x["route"] == "role" and x["reader"] not in TABLE["readers"]]
    check("every role route names a reader the table wakes", not bad, bad)
    check("every doorbell reader is really woken by the schedule",
          IN.reader_problem("FOUNDRY", json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))) is None)
    check("a seat with waking off is unwoken", "waking is off" in IN.reader_problem(
        "FOUNDRY", {"seats": {"FOUNDRY": {"wake": False}}}))
    led = os.path.join(TMP, "cli_ledger.jsonl")
    open(led, "w").close()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(RIMFLOW_LEDGER=led, RIMFLOW_ROUTES=IN.ROUTES, RIMFLOW_ITEMS=os.path.join(TMP, "items"), RIMFLOW_SEAT="BENCH")
    os.makedirs(env["RIMFLOW_ITEMS"], exist_ok=True)

    def cli(*a):
        return subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env, capture_output=True, text=True, timeout=120)
    p = cli("file", "GHOST_READER_PROBE_FIXTURE", "--for", "GHOST", "--title", "t")
    check("`rimflow file --for` an unwoken reader is refused", p.returncode != 0 and "wakes GHOST" in p.stderr + p.stdout, p.stderr + p.stdout)
    p = cli("file", "REAL_READER_PROBE_FIXTURE", "--for", "FOUNDRY", "--title", "t")
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


for t in (test_silent_reader, test_emergency_all_dead, test_ack_then_killed, test_ring_or_read_is_no_ack, test_one_outage,
          test_relapse, test_blind_and_signal, test_ledger_unwritable, test_census_forms, test_alarms_reach_ledger, test_routes):
    t()
print("selftest_incident: %s (%d fails)" % ("FAIL" if FAILS else "OK", len(FAILS)))
sys.exit(1 if FAILS else 0)
