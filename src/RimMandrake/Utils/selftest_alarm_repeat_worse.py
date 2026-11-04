#!/usr/bin/env python3
"""selftest_alarm_repeat_worse.py -- ALARM_REPEAT_FIX_BREAK_ON_WORSE: a repeat alarm breaks its suppression when it gets worse.

Plants a worsening on both real repeat paths, with the real rule files: ops_watch.run_alarms (an alarm stays silent while
crossed) under ops_watch_rules.json, and dispatcher.execute (one alarm per kind per alarm_every_s) under
dispatcher_schedule.json. Proves: a rise inside the step stays silent, one past it is told, a wobble is not told twice, a
severity rise needs no step, a failed delivery is retried, a deploy re-raises nothing, and Operations gets a fresh run.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_alarm_repeat_worse_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "state")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
(TMP / "ops").mkdir()
(TMP / "q").mkdir()
import ops_watch as OW          # noqa: E402
import dispatcher as D          # noqa: E402
import role_launch as RL        # noqa: E402

FAILS = []
NOW = 1793050000.0
H = 3600.0
CLOG = TMP / "conductor_log.md"
RULES = OW.load_rules()
for _t in RULES["targets"]:     # never the real Conductor log
    if _t.get("conductor_log"):
        _t["conductor_log"] = str(CLOG)
OW.mint_name = lambda tag, known, prefix: prefix if prefix.count("_") >= 2 else prefix + "_TEST"


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def M(v, **x):
    return OW.M(v, "min", **x)


class Bench:
    """One alarm on the real rules: each pass goes through run_alarms and records what the filer was handed."""

    def __init__(self, aid):
        self.aid, self.key = aid, aid.split(":", 1)[1]
        self.t, self.sent, self.fail, self.open, self.filed = NOW, [], False, None, set()

    def filer(self, todo, conf):
        self.sent = list(todo)
        self.filed |= {a["name"] for a in todo if not a.get("note_only") and not self.fail}
        return {a["name"]: ("note refused" if self.fail else None) for a in todo}

    def read(self, point):
        self.t += 900
        return OW.run_alarms({self.key: point}, RULES, self.t, self.filed | {"SOME_ITEM"}, self.filer, self.open)[self.aid]


def test_step_on_a_rising_alarm():
    b = Bench("STEVE_STALL:steve.unowned_stall_min")
    cur = b.read(M(45))
    ok(cur["state"] == "OPEN" and len(b.sent) == 1 and not b.sent[0].get("note_only"), "45 min crosses 30: filed once")
    ok(cur["told"]["v"] == 45, "the filing's reading is what later steps measure from")
    item = cur["item"]
    b.sent = []
    cur = b.read(M(80))
    ok(not b.sent and "worse_n" not in cur, "80 min is short of the stated doubling of 45: silent, as before")
    cur = b.read(M(90))
    ok(len(b.sent) == 1 and b.sent[0].get("note_only") and b.sent[0]["item"] == item, "90 min doubles 45: a note on the open item")
    ok("WORSE" in b.sent[0]["text"] and "45" in b.sent[0]["text"] and "90" in b.sent[0]["text"], "the note says from what to what")
    ok(cur["told"]["v"] == 90 and cur["worse_n"] == 1, "told moves to 90, worse_n counts it")
    b.sent = []
    b.read(M(50))
    cur = b.read(M(95))
    ok(not b.sent, "a wobble down and back is not told twice: told is the worst value said")
    cur = b.read(M(180))
    ok(len(b.sent) == 1 and cur["told"]["v"] == 180 and cur["worse_n"] == 2, "180 doubles 90: told again")
    keys = RL.alarm_keys({b.aid: cur})
    ok(keys == {"%s@worse2" % item}, "the alarm key changes, so Operations gets a fresh run: %s" % sorted(keys))
    ok(RL.alarm_keys({b.aid: dict(cur, worse_n=0)}) == {item}, "with no worsening the key is the plain item")
    ok(RL.alarm_keys({b.aid: dict(cur, worse_n="x")}) == {item}, "a bad saved count is no key change")
    for i in range(10):
        st = OW.run_alarms({b.key: M(0)}, RULES, b.t + 1800 + i, b.filed, b.filer, None)
    ok(b.aid not in st, "clearing forgets told: the next crossing starts over")


def test_downward_step():
    b = Bench("DISK_LOW:disk.root_free_gb")
    b.read(OW.M(200, "GB"))
    b.sent = []
    b.read(OW.M(151, "GB"))
    ok(not b.sent, "free GB 200 to 151 is short of the stated 50 further down")
    cur = b.read(OW.M(150, "GB"))
    ok(len(b.sent) == 1 and cur["told"]["v"] == 150, "free GB 200 to 150 passes it: a falling metric worsens downward")
    b.sent = []
    cur = b.read(OW.M(205, "GB"))
    ok(not b.sent and cur["told"]["v"] == 150, "a recovery is no news and moves nothing")


def test_severity_needs_no_step():
    b = Bench("RELENTLESS_DISTRESS:relentless.distressed")
    cur = b.read(OW.M(1, "flag", state="distressed", cause="breaker open"))
    ok(cur["told"]["class"] == "distressed", "the collector's judged class is the severity told")
    b.sent = []
    b.read(OW.M(1, "flag", state="distressed", cause="breaker open"))
    ok(not b.sent, "the same severity and value: silent")
    cur = b.read(OW.M(1, "flag", state="emergency", cause="breaker open"))
    ok(len(b.sent) == 1 and "distressed -> emergency" in b.sent[0]["text"], "a value that cannot step: severity alone re-raises it")
    ok(cur["told"]["class"] == "emergency", "told holds the worst severity")
    log = CLOG.read_text() if CLOG.exists() else ""
    ok("WORSE" in log and "distressed -> emergency" in log, "the rule's conductor_log gets the line an open incident would have held")
    b.sent = []
    b.read(OW.M(1, "flag", state="distressed", cause="x"))
    b.read(OW.M(1, "flag", state="emergency", cause="x"))
    ok(not b.sent, "severity falling and rising again is not told twice")
    p = {"class": "emergency", "x": {"state": "sane"}}
    ok(OW.severity_of(p) == "emergency", "the ranges class outranks the collector's")
    ok(OW.severity_of({"x": {"state": "lapsed"}}) is None, "a state that is no class is no severity")


def test_ranges_class_is_read():
    """The other severity road: a metric the ranges block classes, stamped as run() stamps it."""
    pt = M(45)
    pt["class"] = "distressed"
    b = Bench("STEVE_STALL:steve.unowned_stall_min")
    b.read(pt)
    b.sent = []
    pt = M(46)
    pt["class"] = "emergency"
    cur = b.read(pt)
    ok(len(b.sent) == 1 and cur["told"]["class"] == "emergency" and cur["told"]["v"] == 45,
       "a class rise alone re-raises and leaves the value's step where it was")


def test_failed_delivery_retries():
    b = Bench("STEVE_STALL:steve.unowned_stall_min")
    b.read(M(40))
    b.fail = True
    cur = b.read(M(80))
    ok(len(b.sent) == 1 and cur["told"]["v"] == 40 and "worse_n" not in cur, "a refused note tells nobody: told stays")
    b.fail = False
    b.sent = []
    cur = b.read(M(80))
    ok(len(b.sent) == 1 and cur["told"]["v"] == 80 and cur["worse_n"] == 1, "the next pass says it again")


def test_closed_item_reopens():
    b = Bench("STEVE_STALL:steve.unowned_stall_min")
    cur = b.read(M(40))
    item = cur["item"]
    b.open = set()      # closed, the condition standing: a note on a closed item reaches nobody
    b.sent = []
    cur = b.read(M(50))
    ok(not b.sent, "not yet worse: a closed item is left closed, as before")
    cur = b.read(M(80))
    ok(len(b.sent) == 1 and b.sent[0].get("reopen") and b.sent[0]["name"] == item and not b.sent[0].get("note_only"),
       "worse on a closed item reopens that same item")
    ok(cur["state"] == "OPEN" and cur["told"]["v"] == 80 and cur["worse_n"] == 1, "reopened, told is the new reading")


def test_deploy_re_raises_nothing():
    b = Bench("STEVE_STALL:steve.unowned_stall_min")
    b.read(M(40))
    state = json.loads((OW.ops_dir() / "alarms.json").read_text())
    del state[b.aid]["told"]
    (OW.ops_dir() / "alarms.json").write_text(json.dumps(state))
    b.sent = []
    cur = b.read(M(1000))
    ok(not b.sent and cur["told"]["v"] == 1000, "an alarm filed before this rule takes today's reading as its baseline")
    cur = b.read(M(2000))
    ok(len(b.sent) == 1, "and worsens from there")


def test_token_alarm_stays_operations():
    b = Bench("RUNWAY_LOW:accounts.A.runway")
    cur = b.read(OW.M(0.8, "x", ))
    ok(cur["state"] == "OPEN" and cur["item"] is None and cur["for"] == "Operations" and not b.sent, "a token alarm files no item")
    plain = RL.alarm_keys({b.aid: cur})
    cur = b.read(OW.M(0.4, "x"))
    ok(not b.sent and cur["worse_n"] == 1, "halved runway: no ledger note, a count on the entry")
    ok(RL.alarm_keys({b.aid: cur}) == {sorted(plain)[0] + "@worse1"}, "Operations sees it as a new alarm key")
    log = (OW.ops_dir() / "alarms_log.jsonl").read_text().splitlines()
    last = json.loads(log[-1])
    ok(last["event"] == "worse" and "said" not in last and "v" not in last, "the worse log line of a token alarm carries no value")


def test_rule_rows():
    rows = [t for t in RULES["targets"] if t.get("alarm") and t.get("worse")]
    ok(len(rows) >= 20, "the real rules state steps (%d rows)" % len(rows))
    ok(all(not OW.target_problem(t) for t in rows), "every stated step is well formed, so no row went OFF")
    keys = {t["key"] for t in rows}
    ok({"steve.unowned_stall_min", "steve.incident_unclaimed_min", "disk.root_free_gb"} <= keys, "Steve idle, the design's own example, has its step")
    for bad in ({"factor": 1}, {"add": 0}, {"factor": 2, "add": 1}, {"times": 2}, "2", {"add": True}, {"factor": 1e999}):
        ok(OW.step_problem(bad), "refused step %r" % (bad,))
    row = dict(rows[0], worse={"factor": 1})
    flags = OW.andon({}, {}, {}, dict(RULES, targets=[row]), NOW)
    ok(any(f["rule"] == "bad_target" for f in flags), "a bad step is said aloud as bad_target")
    ok(not OW.step_crossed(0, 5, ">", {"factor": 2}), "a factor cannot step from zero")
    ok(OW.step_crossed(0, 5, ">", {"add": 5}), "an add can")
    ok(not OW.step_crossed(1, 9, ">", None), "a row with no step never breaks on value")


def dsch(**kw):
    sch = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text())
    sch.update(ledger_notes=True, alarm_item="X_Y", publish=False, incident={"enabled": False},
               no_handoff={"conductor_log": str(TMP / "d_log.md")})
    sch.update(kw)
    return sch


def dfx(notes):
    def note(i, t):
        notes.append(t)
        return True, ""
    return {"lock": lambda: open(os.devnull), "publish": lambda n: None, "note": note, "conductor_log": lambda *x: "conductor log off"}


def test_dispatcher_breaks_on_worse():
    sch, st, notes, root = dsch(), {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, [], str(TMP / "d")
    os.makedirs(root, exist_ok=True)
    every = sch["alarm_every_s"]
    ok(every == 21600 and any(r["match"] == "long_helper:*" for r in sch["alarm_worse"]), "the real schedule's 6 h and its stated step")
    acts = []
    def act(**k):
        acts.append(k)
    D.long_helper_alarms(dict(sch, long_helper={"enabled": True, "alarm_after_s": 3600}), {"long_helpers": lambda: [{"id": "abc", "age_s": 4000.0}]}, NOW, act)
    ok(acts and acts[0].get("impact") == 4000.0 and acts[0]["kind"] == "long_helper:abc", "the real emitter carries its impact")
    def alarm(impact=None, severity=None, kind="long_helper:abc"):
        return [{"do": "alarm", "kind": kind, "why": "w", "note": True, "impact": impact, "severity": severity}]
    D.execute(alarm(4000.0), sch, st, root, True, NOW, dfx(notes))
    ok(st["alarms"]["long_helper:abc"] == NOW and len(notes) == 1, "the first raises")
    a = alarm(7000.0)
    D.execute(a, sch, st, root, True, NOW + 300, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and len(notes) == 1, "a rise short of the step stays inside the 6 h limit")
    a = alarm(8000.0)
    D.execute(a, sch, st, root, True, NOW + 600, dfx(notes))
    ok(len(notes) == 2 and "WORSE" in notes[-1] and "x2" in notes[-1], "doubled inside the window: raised, saying so")
    ok(st["alarms"]["long_helper:abc"] == NOW + 600 and st["alarm_told"]["long_helper:abc"]["impact"] == 8000.0, "the limit and the step restart from it")
    a = alarm(8100.0)
    D.execute(a, sch, st, root, True, NOW + 900, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and len(notes) == 2, "the next tick is limited again: one worsening, one raise")
    a = alarm(8100.0, kind="no_row_kind")
    D.execute(a, sch, st, root, True, NOW, dfx(notes))
    n = len(notes)
    a = alarm(99999.0, kind="no_row_kind")
    D.execute(a, sch, st, root, True, NOW + 60, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and len(notes) == n, "a kind with no stated step waits the 6 h")
    D.execute(alarm(severity="distressed", kind="sev"), sch, st, root, True, NOW, dfx(notes))
    a = alarm(severity="distressed", kind="sev")
    D.execute(a, sch, st, root, True, NOW + 60, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]), "the same severity is a plain repeat")
    a = alarm(severity="emergency", kind="sev")
    n = len(notes)
    D.execute(a, sch, st, root, True, NOW + 120, dfx(notes))
    ok(len(notes) == n + 1 and "distressed -> emergency" in notes[-1], "a severity rise breaks the limit with no row")
    # undelivered: nobody took it, so the old stamp and the told value stand and the next tick tries again
    D.execute(alarm(1.0, kind="dead:X"), sch, st, root, True, NOW, dfx(notes))
    fx = dict(dfx(notes), note=lambda *x: (_ for _ in ()).throw(OSError("disk")))
    a = alarm(5.0, kind="dead:X")
    D.execute(a, sch, st, root, True, NOW + 60, fx)
    ok(st["alarms"]["dead:X"] == NOW and st["alarm_told"]["dead:X"]["impact"] == 1.0, "a worse alarm nobody took keeps the old stamp and told")
    n = len(notes)
    D.execute(alarm(5.0, kind="dead:X"), sch, st, root, True, NOW + 120, dfx(notes))
    ok(len(notes) == n + 1 and st["alarm_told"]["dead:X"]["impact"] == 5.0, "the next tick says it")
    # a state saved before this rule: the stamp is there, told is not
    st2 = {"seats": {}, "wakes": [], "recovers": [], "alarms": {"dead:Y": NOW}}
    a = alarm(1e6, kind="dead:Y")
    D.execute(a, sch, st2, root, True, NOW + 60, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and st2["alarm_told"]["dead:Y"]["impact"] == 1e6, "a deploy re-raises nothing: baseline first")
    # a broken row is said on the journal record, and costs only itself
    a = alarm(9.0, kind="k:1")
    bad = dsch(alarm_worse=[{"match": "k:*"}])
    D.execute(a, bad, st2, root, True, NOW, dfx(notes))
    a = alarm(99.0, kind="k:1")
    D.execute(a, bad, st2, root, True, NOW + 60, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and "states no step" in a[0].get("worse_bad", ""), "a row with no step is off, said aloud")
    a = alarm(99.0, kind="k:1")
    D.execute(a, dsch(alarm_worse=[{"match": "k:*", "factor": 1}]), st2, root, True, NOW + 90, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and "states no step" in a[0].get("worse_bad", ""), "a factor of 1 would fire on every tick: off, said aloud")
    a = alarm(99.0, kind="k:1")
    D.execute(a, dsch(alarm_worse=7), st2, root, True, NOW + 95, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]), "a schedule field of the wrong shape costs no tick")


# Every target key that states a step today. Dropping one goes red; a new row with a step may be added freely.
STATED_STEPS = {
    "accounts.*.loan_runway", "accounts.*.runway", "arena.push_refused_24h", "codex.runway", "companion.grant_hours_left",
    "disk.c_free_gb", "disk.d_free_gb", "disk.pool_breach", "disk.root_free_gb", "disk.scratch_ok_age_h", "disk.tmp_free_gb",
    "disk.tmp_used_pct", "flow.untriaged_findings", "health.drifted_slis", "health.spent_slis", "queues.artpipe.stalled_min",
    "queues.testq.stalled_min", "relentless.books_behind_min", "relentless.game_hold_idle_min",
    "relentless.live_measured_pct", "steve.incident_unclaimed_min", "steve.invalid_streak", "steve.seats_absent_min",
    "steve.unowned_stall_min", "timers.failed_units", "tps.health_breaches"}


def test_every_stated_step_stays():
    keys = {t["key"] for t in RULES["targets"] if t.get("alarm") and t.get("worse")}
    lost = sorted(STATED_STEPS - keys)
    ok(not lost, "every rule that states a step still states it (lost: %s)" % lost)


def test_real_emitters_break_on_worse():
    """dead, seat_declined and idle_full_queue: the real decide emits the impact, the real schedule's row and 6 h decide."""
    import selftest_dispatcher as SD
    real = json.loads((HERE.parent / "rimflow" / "dispatcher_schedule.json").read_text())
    base = dict(ledger_notes=True, alarm_item="X_Y", publish=False, incident={"enabled": False},
                alarm_every_s=real["alarm_every_s"], alarm_worse=real["alarm_worse"])
    root = str(TMP / "emit")
    os.makedirs(root, exist_ok=True)
    # dead: the impact is how long the seat has been dead
    s = SD.sched(no_handoff={"conductor_log": str(TMP / "e_log.md")})
    s["seats"]["FOUNDRY"]["recover_dead"] = False
    s.update(base)
    st, notes, gone = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, [], []
    D.decide(s, st, SD.obs(), 1000.0, True)
    D.decide(s, st, SD.obs(sessions=gone), 1100.0, True)
    da, res = s["dead_after_s"], []
    for t in (1100.0 + da, 1100.0 + da + 300, 1100.0 + 2 * da + 60):
        a = [x for x in D.decide(s, st, SD.obs(sessions=gone), t, True) if x["do"] == "alarm" and x["kind"] == "dead:FOUNDRY"]
        ok(len(a) == 1 and isinstance(a[0].get("impact"), (int, float)) and a[0]["impact"] > 0,
           "dead at %+.0f s carries its impact %r" % (t - 1100.0 - da, a and a[0].get("impact")))
        n = len(notes)
        D.execute(a, s, st, root, True, t, dfx(notes))
        res.append(len(notes) - n)
    ok(res == [1, 0, 1] and "WORSE" in notes[-1], "dead: raised, limited, then raised WORSE inside the 6 h (%r)" % res)
    # the two ring alarms: the impact is the ring streak
    for ev, kind in (({"event": "note", "id": "PEEKED", "text": "held"}, "seat_declined"), (None, "idle_full_queue")):
        s = SD.sched(caps=D.load_schedule()["caps"],
                     no_handoff={"rering_s": [300, 900, 1800], "escalate_after": 3, "conductor_log": str(TMP / "e_log.md")})
        s.update(base)
        st, notes, imp = {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, [], []
        o = SD.obs(consumed={"consumed_at": 1.0}, events=[dict(ev, ts="2999-01-01T00:00:00Z")] if ev else [])
        now = 1000.0
        while now < 1000.0 + 5.9 * H:
            a = [x for x in D.decide(s, st, o, now, True) if x["do"] == "alarm" and x["kind"].startswith(kind + ":")]
            if a:
                imp += [x.get("impact") for x in a]
                D.execute(a, s, st, root, True, now, dfx(notes))
            now += s["tick_s"]
        ok(imp and all(isinstance(i, (int, float)) for i in imp) and imp[-1] > imp[0],
           "%s carries a rising ring streak (%s..%s)" % (kind, imp and imp[0], imp and imp[-1]))
        ok(len(notes) >= 2 and any("WORSE" in x for x in notes[1:]), "%s is raised WORSE inside the 6 h (%d notes)" % (kind, len(notes)))

    # a row stating an add, not a factor: short of +10 limited, at +10 raised
    sch, st, notes = dsch(alarm_worse=[{"match": "k:*", "add": 10}]), {"seats": {}, "wakes": [], "recovers": [], "alarms": {}}, []
    one = lambda v: [{"do": "alarm", "kind": "k:1", "why": "w", "note": True, "impact": v}]
    D.execute(one(5.0), sch, st, root, True, NOW, dfx(notes))
    a = one(14.0)
    D.execute(a, sch, st, root, True, NOW + 60, dfx(notes))
    ok("rate-limited" in str(a[0]["result"]) and len(notes) == 1, "an add step: +9 is short of +10")
    D.execute(one(15.0), sch, st, root, True, NOW + 120, dfx(notes))
    ok(len(notes) == 2 and "+10" in notes[-1], "an add step: +10 is raised WORSE, naming the step")


def test_operations_gets_a_fresh_run():
    """Through the real decide_roles: a worse alarm is a fresh key, and its run names the plain ledger item."""
    import selftest_dispatcher as SD
    op = SD.operations(alarm_runs=True, runs_local=["07:30"], economy_pass_local=None, alarm_run_gap_s=1000)
    now = SD.at_local("12:00")

    def decide(alarm, seen):
        acts = []
        st = {"roles": {"Operations": {"done": {}, "runs": [], "alarms_seen": seen}}}
        RL.decide_roles({"roles": [op]}, st, SD.robs(SD.ops_status(now, alarms={"a": alarm})), now, lambda **k: acts.append(k), set(), None)
        return [x for x in acts if x.get("do") == "role_launch"], st

    plain = {"state": "OPEN", "item": "OPS_STEVE_UNSTICK"}
    runs, _ = decide(plain, ["OPS_STEVE_UNSTICK"])
    ok(not runs, "an alarm a run already covered earns no second run")
    runs, st = decide(dict(plain, worse_n=1), ["OPS_STEVE_UNSTICK"])
    ok(len(runs) == 1, "the same alarm, worse: a fresh Operations run")
    ok(runs[0]["ticket"] == "OPS_STEVE_UNSTICK", "the run is on the plain ledger item")
    ok("@worse1" in runs[0]["slot"] and "@worse1" in runs[0]["why"], "and says which worsening it covers")
    runs, _ = decide(dict(plain, worse_n=1), ["OPS_STEVE_UNSTICK@worse1"])
    ok(not runs, "covered once: no run again until it worsens again")


def main():
    for t in (test_step_on_a_rising_alarm, test_downward_step, test_severity_needs_no_step, test_ranges_class_is_read,
              test_failed_delivery_retries, test_closed_item_reopens, test_deploy_re_raises_nothing,
              test_token_alarm_stays_operations, test_rule_rows, test_every_stated_step_stays, test_dispatcher_breaks_on_worse,
              test_real_emitters_break_on_worse,
              test_operations_gets_a_fresh_run):
        p = OW.ops_dir() / "alarms.json"
        if p.exists():
            p.unlink()
        print("--", t.__name__)
        t()
    print("RESULT: %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
