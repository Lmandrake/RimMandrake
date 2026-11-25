#!/usr/bin/env python3
"""selftest_steve_idle_takeable.py - the Steve lane idle while in-game checks wait for it
(RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT; page design/specs/2026-11-22-steve-idle-takeable/boundary.md).

The incident (2026-11-22): SteveDesktop sat BRAKED, then on filler, from 21:14Z to 02:45Z (5.5 h) while 28 Pyrelands and
6 FlowWorks checks with a testq block waited, and no reading fired. Each promise of the page has a test of its name. The
fixtures are temp dirs: a testq queue, a dispatch reading, stage records, an owner hold file. Nothing live is read.
Every check prints its reading; the end prints how many cases were read and the worst (largest) reading against 30 min."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="steve_takeable_"))
os.environ.update({
    "TESTQ_QUEUE": str(TMP / "testq"),
    "RM_MATURATION_DISPATCH_DIR": str(TMP / "disp"),
    "RM_STREAMS_BENCH": str(TMP / "clone"),
    "RM_OPS_WATCH_DIR": str(TMP / "ops"),
    "RM_OWNER_HOLD_FILE": str(TMP / "hold" / "mod_owner_hold.json"),
    "RM_CONTROL_DB": str(TMP / "hold" / "control.db"),
})
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import warnings  # noqa: E402
warnings.simplefilter("ignore", SyntaxWarning)
import ops_watch as OW  # noqa: E402

FAILS, READ = [], []
KEY = "steve.idle_with_takeable_min"
NOW = 1795400000.0                      # 2026-11-23T02:13:20Z, a fixed clock
LINE = 30                               # the rule's line (owner brief: Steve lane stalled over 30 min)


def check(cond, msg):
    print("%s %s" % ("ok  " if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def wjson(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def reset():
    """A clean lane: empty queue dirs, no dispatch reading, two in-game stage records, an empty hold file."""
    import shutil
    for d in ("testq", "disp", "clone", "hold"):
        shutil.rmtree(TMP / d, ignore_errors=True)
    for s in ("running", "pending", "done"):
        (TMP / "testq" / s).mkdir(parents=True)
    wjson(TMP / "testq" / "steward.json", {"epoch": iso(NOW - 60), "state": "BRAKED", "fault": False,
                                          "reason": "day budget", "since": iso(NOW - 5.5 * 3600)})
    for m, st in (("Pyrelands", "in_game"), ("FlowWorks", "in_game"), ("CrackedLands", "offline_build")):
        wjson(TMP / "clone" / "design" / "concepts" / m / "version" / "stage_record.json", {"stage": st})
    wjson(os.environ["RM_OWNER_HOLD_FILE"], {"holds": []})
    facts()


FACTS = {"mods": ["brrainz.harmony", "brrainz.rimbridgeserver", "owlchemist.cherrypicker", "lwm.deepstorage"],
         "saves": ["NS_Pyrelands_site_1_417df172fdb5_visit5"], "python": {"numpy": True, "lxml": True, "PIL": True}}


def facts(at=None, **kw):
    """The host's facts (testq/host_facts.py): fresh and whole unless told otherwise."""
    wjson(TMP / "testq" / "host_facts.json", {"at": NOW - 600 if at is None else at, "facts": dict(FACTS, **kw)})


def job(jid, mod, chains, by="BENCH", **kw):
    j = {"id": jid, "mod": mod, "selector": {"chains": chains}, "requested_by": by, "lane": "stevedesktop",
         "owner_gate": None, "not_before": None, "schema": "testq.job/1"}
    j.update(kw)
    return j


def running(j):
    wjson(TMP / "testq" / "running" / (j["id"] + ".json"), {"attempt": j["id"] + ".a1", "job": j, "cancel": False})


def pending(j):
    wjson(TMP / "testq" / "pending" / (j["id"] + ".json"), j)


def done(j, outcome, fin):
    p = TMP / "testq" / "done" / (j["id"] + ".json")
    wjson(p, {"job": j, "result": {"outcome": outcome, "started": iso(fin - 300), "finished": iso(fin)}})
    os.utime(p, (fin, fin))


def entry(visit, opened, checks, owed="run", blocked=(), held=False, hold_unreadable=False):
    return {"visit": visit, "opened": iso(opened), "owed": owed, "blocked": list(blocked), "held": held,
            "hold_unreadable": hold_unreadable, "ran_in_visit": [], "checks": checks}


def today(opened=NOW - 6 * 3600):
    """Today's case: Pyrelands visit 6 with 28 waiting checks, FlowWorks visit 8 with 6."""
    return {"Pyrelands": entry(6, opened, {"p%02d" % i: ["pc%02d" % i] for i in range(28)}),
            "FlowWorks": entry(8, opened, {"f%d" % i: ["fc%d" % i] for i in range(6)})}


def one(checks=None):
    """Pyrelands visit 6 opened 1 h ago with one waiting check (p0: chain pc0, unless given); FlowWorks read, none."""
    return {"Pyrelands": entry(6, NOW - 3600, {"p0": ["pc0"]} if checks is None else checks),
            "FlowWorks": entry(8, NOW - 3600, {})}


def dispatch(block, age=60, drop=False):
    rd = {"schema": 1, "at": NOW - age, "mods": {}}
    if not drop:
        rd["ingame_testq"] = block
    wjson(TMP / "disp" / "reading.json", rd)


def read(label):
    ctx = {}
    out = OW.c_steve(NOW, OW.load_rules(), ctx)     # the family's own pass first: it fills ctx["steve_jobs"]
    p = OW.c_steve_takeable(NOW, OW.load_rules(), ctx).get(KEY)
    READ.append((label, p))
    x = (p or {}).get("x") or {}
    print("     %-44s %s v=%s state=%s waiting=%s why=%s" % (label, (p or {}).get("m"), (p or {}).get("v"),
                                                          x.get("state"), x.get("waiting"),
                                                          str((p or {}).get("why") or x.get("said") or "")[:90]))
    del out
    return p or {}


# ------------------------------------------------------------------------------------------------ the dispatch side
def t_the_dispatch_reading_names_each_waiting_check():
    import maturation_dispatch as MD
    import control
    control.init(os.environ["RM_CONTROL_DB"])
    root = TMP / "root"
    tests = {"a": {"kind": "live", "stage": "6", "testq": {"chains": ["ca"], "by": "testq_blocks.py"}},
             "b": {"kind": "live", "stage": "6", "testq": {"chains": ["cb1", "cb2"], "by": "testq_blocks.py"}},
             "c": {"kind": "live", "stage": "6"},
             "d": {"kind": "live", "stage": "6", "testq": {"chains": ["cd"], "by": "testq_blocks.py"}},
             "e": {"kind": "live", "stage": "6", "testq": {"chains": ["ce"], "by": "testq_blocks.py"}}}
    for m in ("Fx", "Hx"):
        wjson(root / "design" / "concepts" / m / "version" / "test_table.json", {"tests": tests})
    vd = root / "design" / "concepts" / "Fx" / "version" / "in_game"
    for k, t in ((1, "e"), (2, "d")):
        (vd / ("visit_%d" % k)).mkdir(parents=True, exist_ok=True)
        (vd / ("visit_%d" % k) / "rows.jsonl").write_text(json.dumps({"test": t, "verdict": "FAIL"}) + "\n")
    wjson(os.environ["RM_OWNER_HOLD_FILE"], {"holds": [{"mod": "Hx", "date": "2026-11-22", "said": "hold it"}]})
    f_in = {"stage": "in_game", "visit": 2, "opened": "2026-11-22T08:54:05-08:00", "owed": "run", "blocked": [],
            "to_run": ["a", "b", "c", "d", "e"], "testq": ["a", "b", "d", "e"], "live_units": []}
    facts = {"Fx": dict(f_in), "Hx": dict(f_in), "Ox": {"stage": "offline_build", "live_units": []}}
    saved = MD.decide

    def decide(cfg, st, facts, now, account=None, bridge=None, releases=None):
        return [], []
    try:
        MD.decide = decide
        rd = MD.tick(str(root), dict(MD.load_cfg(), advancing=["Fx", "Hx", "Ox"]), False,
                     fx={"autonomy": False, "facts": lambda: facts, "account": lambda: (True, ""),
                         "releases": lambda: [], "convergence": lambda r, d: d, "code": lambda: "tree"},
                     now=NOW, page=False)
    finally:
        MD.decide = saved
    b = rd.get("ingame_testq")
    print("     ingame_testq = %s" % json.dumps(b)[:400])
    check(isinstance(b, dict) and sorted(b) == ["Fx", "Hx"],
          "the-dispatch-reading-names-each-waiting-check: every in-game mod the tick read, no other (%s)"
          % (sorted(b) if isinstance(b, dict) else b))
    fx = (b or {}).get("Fx") or {}
    check(fx.get("checks") == {"a": ["ca"], "b": ["cb1", "cb2"], "e": ["ce"]},
          "the-dispatch-reading-names-each-waiting-check: to_run with a testq block, less the visit's own rows "
          "(d ran in visit 2; e's row is visit 1's): %s" % fx.get("checks"))
    check(fx.get("visit") == 2 and fx.get("opened") == f_in["opened"] and fx.get("owed") == "run"
          and fx.get("held") is False and fx.get("blocked") == [] and fx.get("ran_in_visit") == ["d"],
          "the-dispatch-reading-names-each-waiting-check: visit, opening, owed, hold, blocked, ran: %s"
          % {k: fx.get(k) for k in ("visit", "opened", "owed", "held", "blocked", "ran_in_visit")})
    check(((b or {}).get("Hx") or {}).get("held") is True,
          "the-dispatch-reading-names-each-waiting-check: the owner's hold is carried (%s)" % ((b or {}).get("Hx")))


# ------------------------------------------------------------------------------------------------ the ops_watch side
def t_idle_or_filler_with_takeable_waiting_alarms():
    # (1) today: braked, nothing running, 34 waiting, the last real job 5.5 h ago
    reset()
    dispatch(today())
    done(job("J-old", "FlowWorks", ["x"]), "DONE", NOW - 5.5 * 3600)
    p = read("braked, idle, 34 waiting")
    x = p.get("x") or {}
    check(p.get("m") == "MEASURED" and abs((p.get("v") or 0) - 330.0) < 0.2 and x.get("state") == "waiting"
          and x.get("waiting") == {"Pyrelands": 28, "FlowWorks": 6},
          "idle-or-filler-with-takeable-waiting-alarms: today's case reads 330 min waiting, 28 + 6 (%s)" % p)
    check(OW.target_state({KEY: p}, OW.load_rules()).get("STEVE_IDLE_TAKEABLE:" + KEY) is True,
          "idle-or-filler-with-takeable-waiting-alarms: the rule crosses on it")
    # (2) a filler job on another mod runs: still waiting (filler does not stop the clock)
    running(job("J-fill", "CrackedLands", ["claim_crew"], by="BENCH.filler"))
    p = read("filler on CrackedLands, 34 waiting")
    check(p.get("m") == "MEASURED" and abs((p.get("v") or 0) - 330.0) < 0.2
          and (p.get("x") or {}).get("state") == "waiting",
          "idle-or-filler-with-takeable-waiting-alarms: a filler job on another mod is idle (%s)" % p.get("v"))
    # (3) the clock starts at the visit's opening when that is later than the last real job
    reset()
    dispatch(today(opened=NOW - 45 * 60))
    done(job("J-old", "FlowWorks", ["x"]), "DONE", NOW - 5 * 3600)
    p = read("opened 45 min ago")
    check(abs((p.get("v") or 0) - 45.0) < 0.2, "idle-or-filler-with-takeable-waiting-alarms: counts from the opening "
          "(45 min; %s)" % p.get("v"))
    # (4) an INVALID run of a chain drains nothing; the lane took that work, so the idle clock restarts at its finish
    reset()
    dispatch(one())
    done(job("J-inv", "Pyrelands", ["pc0"], by="BENCH.filler"), "INVALID", NOW - 50 * 60)
    p = read("one check, its chain INVALID")
    check((p.get("x") or {}).get("state") == "waiting" and abs((p.get("v") or 0) - 50.0) < 0.2,
          "idle-or-filler-with-takeable-waiting-alarms: an INVALID run leaves the check waiting, the clock from that "
          "run's finish (50 min): %s" % p.get("v"))
    # (4b) a filler job on another mod's chain does not restart the clock
    reset()
    dispatch(one())
    done(job("J-other", "CrackedLands", ["claim_crew"], by="BENCH.filler"), "DONE", NOW - 20 * 60)
    p = read("filler on another mod ended 20 min ago")
    check((p.get("x") or {}).get("state") == "waiting" and abs((p.get("v") or 0) - 60.0) < 0.2,
          "idle-or-filler-with-takeable-waiting-alarms: filler elsewhere leaves the clock at the opening (60 min): %s"
          % p.get("v"))
    # (5) a commissioned job just ended: the clock restarts at its finish
    reset()
    dispatch(today())
    done(job("J-real", "Watchers", ["behaviour"]), "DONE", NOW - 10 * 60)
    p = read("commissioned job ended 10 min ago")
    check(abs((p.get("v") or 0) - 10.0) < 0.2 and (p.get("x") or {}).get("state") == "waiting",
          "idle-or-filler-with-takeable-waiting-alarms: the clock restarts at a real job's finish (%s)" % p.get("v"))
    check(OW.target_state({KEY: p}, OW.load_rules()).get("STEVE_IDLE_TAKEABLE:" + KEY) is False,
          "idle-or-filler-with-takeable-waiting-alarms: 10 min is under the line")
    # (6) one held mod, one not: only the unheld counts
    reset()
    b = today()
    b["Pyrelands"]["held"] = True
    dispatch(b)
    p = read("Pyrelands held, FlowWorks waiting")
    check((p.get("x") or {}).get("waiting") == {"FlowWorks": 6}, "idle-or-filler-with-takeable-waiting-alarms: a "
          "held mod's checks do not count, the other's do (%s)" % (p.get("x") or {}).get("waiting"))


def t_nothing_takeable_is_quiet():
    cases = []
    reset()
    dispatch({"Pyrelands": entry(6, NOW - 6 * 3600, {}), "FlowWorks": entry(8, NOW - 6 * 3600, {})})
    cases.append(("no check waits", read("no check waits")))
    reset()
    b = today()
    b["Pyrelands"]["held"] = True
    b["FlowWorks"]["held"] = True
    dispatch(b)
    cases.append(("both held by the owner", read("both held by the owner")))
    reset()
    b = today()
    b["Pyrelands"]["blocked"] = ["a Conductor hold stands on stage 6"]
    b["FlowWorks"]["owed"] = "exit met"
    dispatch(b)
    cases.append(("blocked / exit met", read("blocked / exit met")))
    reset()
    dispatch(one({"p0": ["pc0", "pc1"], "p1": ["pc2"]}))
    done(job("J-a", "Pyrelands", ["pc0", "pc2"], by="BENCH.filler"), "DONE", NOW - 40 * 60)
    done(job("J-b", "Pyrelands", ["pc1"]), "DONE", NOW - 20 * 60)
    cases.append(("every chain DONE since opening", read("every chain DONE since opening")))
    reset()
    dispatch(one())
    pending(job("J-gate", "Pyrelands", ["pc0"], owner_gate="his look first"))
    cases.append(("gated by the owner", read("gated by the owner")))
    reset()
    dispatch({})
    wjson(TMP / "clone" / "design" / "concepts" / "Pyrelands" / "version" / "stage_record.json", {"stage": "offline_build"})
    wjson(TMP / "clone" / "design" / "concepts" / "FlowWorks" / "version" / "stage_record.json", {"stage": "offline_build"})
    cases.append(("no mod at in_game", read("no mod at in_game")))
    for label, p in cases:
        check(p.get("m") == "MEASURED" and p.get("v") == 0 and (p.get("x") or {}).get("state") == "quiet",
              "nothing-takeable-is-quiet: %s reads 0 quiet (%s %s %s)" % (label, p.get("m"), p.get("v"),
                                                                       (p.get("x") or {}).get("state")))
    # the mutant's guard: a chain DONE BEFORE the opening drains nothing
    reset()
    dispatch(one())
    done(job("J-early", "Pyrelands", ["pc0"]), "DONE", NOW - 2 * 3600)
    p = read("chain DONE before the opening")
    check((p.get("x") or {}).get("state") == "waiting", "nothing-takeable-is-quiet: a run before the visit opened "
          "drains nothing (%s)" % (p.get("x") or {}).get("state"))


def t_commissioned_or_takeable_work_is_busy():
    cases = []
    reset()
    dispatch(today())
    running(job("J-real", "Watchers", ["behaviour"], by="BENCH"))
    cases.append(("a commissioned job runs", read("a commissioned job runs")))
    reset()
    dispatch(today())
    pending(job("J-q", "Watchers", ["behaviour"], by="BENCH"))
    cases.append(("a ready commissioned job waits", read("a ready commissioned job waits")))
    reset()
    dispatch(today())
    running(job("J-fillp", "Pyrelands", ["pc03"], by="BENCH.filler"))
    cases.append(("filler runs a waiting chain", read("filler runs a waiting chain")))
    # Steve2 (testq.STEVE2, the lane's second game) runs the visit's job: that is the lane's work too (live 2026-11-23:
    # the four FlowWorks visit jobs ran on stevedesktop.b while this read the lane as waiting)
    reset()
    dispatch(today())
    jb = job("J-b", "Pyrelands", ["pc03"], by="BENCH.visit")
    wjson(TMP / "testq" / "running" / "J-b.json", {"attempt": "J-b.a1", "job": jb, "cancel": False,
                                                    "host": "stevedesktop.b"})
    cases.append(("Steve2 runs the visit's job", read("Steve2 runs the visit's job")))
    for label, p in cases:
        check(p.get("m") == "MEASURED" and p.get("v") == 0 and (p.get("x") or {}).get("state") == "busy",
              "commissioned-or-takeable-work-is-busy: %s reads 0 busy (%s %s %s)" % (
                  label, p.get("m"), p.get("v"), (p.get("x") or {}).get("state")))
    # a pending job not ready (not_before in the future, another lane) is not work on the lane
    reset()
    dispatch(today())
    pending(job("J-later", "Watchers", ["behaviour"], not_before=iso(NOW + 3600)))
    pending(job("J-arch", "Watchers", ["behaviour"], lane="archmagi"))
    p = read("only a not-yet and an other-lane job")
    check((p.get("x") or {}).get("state") == "waiting", "commissioned-or-takeable-work-is-busy: a job not ready for "
          "the lane is not busy (%s)" % (p.get("x") or {}).get("state"))


def t_could_not_look_is_unmeasured():
    cases = []
    reset()
    cases.append(("no dispatch reading", read("no dispatch reading")))
    reset()
    dispatch(today(), age=OW.MATURATION_READING_MAX_AGE_S + 60)
    cases.append(("a stale dispatch reading", read("a stale dispatch reading")))
    reset()
    dispatch(today(), drop=True)
    cases.append(("no ingame_testq block", read("no ingame_testq block")))
    reset()
    b = today()
    for m in b:
        b[m].update(held=True, hold_unreadable=True)
    dispatch(b)
    cases.append(("the owner's hold unreadable", read("the owner's hold unreadable")))
    reset()
    dispatch(today())
    import shutil
    shutil.rmtree(TMP / "testq" / "running")
    cases.append(("the running dir unreadable", read("the running dir unreadable")))
    reset()
    dispatch({"Pyrelands": entry(6, NOW - 3600, {})})     # FlowWorks at in_game, missing from the reading
    cases.append(("an in-game mod missing, none known", read("an in-game mod missing, none known")))
    for label, p in cases:
        check(p.get("m") == "UNMEASURED" and p.get("v") is None,
              "could-not-look-is-unmeasured: %s (%s %s)" % (label, p.get("m"), str(p.get("why"))[:80]))
    # a missing mod beside a known wait still says the wait (a lower bound), naming what was not read
    reset()
    dispatch({"Pyrelands": today()["Pyrelands"]})
    p = read("FlowWorks missing, Pyrelands waits")
    check(p.get("m") == "MEASURED" and (p.get("x") or {}).get("state") == "waiting"
          and "FlowWorks" in str((p.get("x") or {}).get("unread")),
          "could-not-look-is-unmeasured: a known wait beside an unread mod alarms and names it (%s)"
          % (p.get("x") or {}).get("unread"))


def t_the_rule_alarms_to_the_conductor_log():
    rules = OW.load_rules()
    tg = [t for t in rules.get("targets") or [] if t.get("key") == KEY]
    print("     target = %s" % json.dumps(tg)[:300])
    check(len(tg) == 1, "the-rule-alarms-to-the-conductor-log: one target on %s (%d)" % (KEY, len(tg)))
    t = tg[0] if tg else {}
    check(t.get("op") == ">" and t.get("value") == LINE and t.get("alarm") is True and not OW.target_problem(t),
          "the-rule-alarms-to-the-conductor-log: over %d, an alarm, a well-formed row (%s)" % (LINE, OW.target_problem(t)))
    check(t.get("name") == "OPS_STEVE_FEED_IDLE_LANE" and t.get("tag") == "STEVE_IDLE_TAKEABLE",
          "the-rule-alarms-to-the-conductor-log: the fixed name OPS_STEVE_FEED_IDLE_LANE (%s)" % t.get("name"))
    check(t.get("conductor_log") == "/mnt/d/ClaudeWork/rimmandrake/conductor/log.md",
          "the-rule-alarms-to-the-conductor-log: the line reaches the Conductor log (%s)" % t.get("conductor_log"))
    why = str(t.get("why") or "")
    check("5.5 h" in why and "30 min" in why, "the-rule-alarms-to-the-conductor-log: the why names the danger and its "
          "evidence")


def t_an_owner_pause_is_quiet():
    """The steward PAUSED (the owner stopped work on the lane): idle is intended, so nothing is takeable (0 quiet)."""
    reset()
    dispatch(today())
    p = read("steward BRAKED, checks waiting")
    check((p.get("x") or {}).get("state") == "waiting", "owner-pause: the BRAKED control reads waiting")
    wjson(TMP / "testq" / "steward.json", {"epoch": iso(NOW - 60), "state": "PAUSED", "fault": False,
                                          "reason": "paused until later: owner: no new work", "since": iso(NOW - 3600)})
    p = read("steward PAUSED, checks waiting")
    check(p.get("m") == "MEASURED" and p.get("v") == 0 and (p.get("x") or {}).get("state") == "quiet",
          "owner-pause: a PAUSED lane reads 0 quiet (%s %s %s)" % (p.get("m"), p.get("v"), (p.get("x") or {}).get("state")))


def main():
    for t in (t_an_owner_pause_is_quiet, t_the_dispatch_reading_names_each_waiting_check, t_idle_or_filler_with_takeable_waiting_alarms,
              t_nothing_takeable_is_quiet, t_commissioned_or_takeable_work_is_busy, t_could_not_look_is_unmeasured,
              t_the_rule_alarms_to_the_conductor_log):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises is a red, named
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    import maturation_dispatch as MD
    print("modules: %s %s" % (OW.__file__, MD.__file__))     # mutate_steve_idle_takeable.py checks these are its copies
    vals = [p.get("v") for _, p in READ if isinstance(p.get("v"), (int, float))]
    print("cases read %d; worst reading %s min against the line %d" % (len(READ), max(vals) if vals else None, LINE))
    print("selftest_steve_idle_takeable: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
