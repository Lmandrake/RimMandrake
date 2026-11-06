#!/usr/bin/env python3
"""Selftest of the Designer's stage chain (DESIGNER_STAGES_WIRE_NOBODY_PRESSED_GO). A run-now runs ONE stage; before
this, a run that closed 'stage N done' left the concept ready and nothing launched stage N+1 until the
queues.designer.stalled_min alarm (OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV). Now the harvest
(role_launch._supervise_one -> chain_next) asks the next run-now itself, and the next decide launches it through the
run-now gates. Pure: fake obs, a temp dir, no systemd, no git."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as SD  # noqa: E402  (fixtures; its own tests do not run on import)

RL = SD.RL
FAILS = []
T = SD.at_local("13:00")             # no fixture slot (11:00, 17:00) is due: only a run-now can launch
C1, C2 = "/tmp/concepts/ModOne", "/tmp/concepts/ModTwo"


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def designer_row():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    return next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")


def harvest(rs, status, ok=True, concept=C1, unit="rm-role-designer-1", cfg=None):
    """One finished Designer run on `concept` through the real supervisor; status = the stage.json after its close."""
    rs.setdefault("runs", []).append({"state": "running", "unit": unit, "at": T - 600, "day": RL.day_of(T),
                                      "budget": 90000, "mode": "run", "item": "X_ITEM", "concept": concept,
                                      "scope": "S.scope", "marker": "M"})
    res = {"subtype": "success", "usage": {k: 10 for k in RL.USAGE_KEYS}}
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
           "stage_close": lambda c, u, t: (ok, [] if ok else ["bad result"]), "stage_land": lambda c, u: None,
           "stage_turn": lambda c: None, "stage_status": lambda c: status if not callable(status) else status(c)}
    RL._supervise_one("Designer", rs, cfg or dict(RL.ROLE_DEFAULTS, **designer_row()), obs, T,
                      lambda **kw: acts.append(kw), set())
    return acts


def test_row():
    row = designer_row()
    check(row.get("chain_stages") is True and "chain" in row.get("trigger", ""),
          "the Designer row sets chain_stages true and its trigger names the chain")
    check(not row.get("enabled") and not row.get("runs_local"), "the row still has no schedule (enabled false, no slots)")


def test_done_chains():
    rs = {}
    acts = harvest(rs, {"stage": 4, "status": "ready"})
    r = rs.get("run_now")
    check(isinstance(r, dict) and r.get("concept") == C1 and r.get("by") == "Dispatcher" and r.get("mode") == "run"
          and r.get("chained_from") == "rm-role-designer-1" and r.get("at") == T,
          "an accepted stage-3-done harvest on a ready concept asks a run-now for it: %r" % r)
    check(any(a["do"] == "role_hold" and "chained" in a["why"] for a in acts), "the chain is said on the ledger")
    # the next decide launches it (a disabled role, like the Designer), through the stage machine's open
    st = SD.fresh()
    st["roles"] = {"Arbiter": dict({"done": {}, "runs": []}, run_now=r)}
    opened = []
    ro = SD.lrobs(SD.ops_status(T), lambda: None)
    ro["stage_open"] = lambda c, u, b: (opened.append(c), ("PACKET", b))[1]
    ro["coverage_pre"] = lambda c: None
    la = [a for a in SD.role_acts(SD.rdecide([SD.arbiter(enabled=False)], st, ro, T + 60)) if a["do"] == "role_launch"]
    check(len(la) == 1 and opened == [C1] and "chain:" in la[0]["why"],
          "the next decide launches the chained run on that concept: %r %r" % (opened, [a["do"] for a in la]))


def test_no_chain_states():
    for status in ({"stage": 2, "status": "waiting_owner"}, {"stage": 2, "status": "blocked"},
                   {"stage": 5, "status": "locked"}):
        rs = {}
        harvest(rs, status)
        check("run_now" not in rs and not rs.get("run_now_queue"), "status %s chains nothing" % status["status"])
    rs = {}
    harvest(rs, {"stage": 3, "status": "ready"}, ok=False)
    # ROLES_FIX_REJECTED_STAGE_ROUTES_BY_CAUSE (WP-15): a module rejection goes back to the builder once, with its
    # reasons; the identical second one goes to the arbiter, never a second loop (selftest_role_launch_reject_routes)
    check("bad result" in str((rs.get("run_now") or {}).get("why")),
          "a REJECTED (module) result re-chains its role once with the reasons: %r" % rs.get("run_now"))
    rs.pop("run_now", None)
    harvest(rs, {"stage": 3, "status": "ready"}, ok=False, unit="rm-role-designer-2",
            cfg=dict(RL.ROLE_DEFAULTS, **dict(designer_row())))
    check("run_now" not in rs, "an identical 2nd REJECTED result chains nothing (the arbiter's, its alarm stands)")
    rs = {}
    harvest(rs, {"stage": 3, "status": "ready"}, cfg=dict(RL.ROLE_DEFAULTS, **dict(designer_row(), chain_stages=False)))
    check("run_now" not in rs, "a row without chain_stages chains nothing")

    def boom(c):
        raise RuntimeError("unreadable")
    rs = {}
    acts = harvest(rs, boom)
    check("run_now" not in rs and any(a.get("kind") == "role:Designer:chain" for a in acts),
          "an unreadable stage.json chains nothing and alarms")


def test_queue_behind_pending():
    hand = {"at": T - 30, "by": "BENCH", "why": "start ModTwo", "mode": "run", "concept": C2}
    rs = {"run_now": dict(hand)}
    harvest(rs, {"stage": 1, "status": "ready"})
    check(rs["run_now"] == hand and [q["concept"] for q in rs.get("run_now_queue") or []] == [C1],
          "a pending run-now keeps its slot; the chain waits behind it: %r" % rs.get("run_now_queue"))
    harvest(rs, {"stage": 2, "status": "ready"}, unit="rm-role-designer-2")
    check(len(rs["run_now_queue"]) == 1, "one queued entry per concept")
    rs2 = {"run_now": dict(hand, concept=C1)}
    harvest(rs2, {"stage": 1, "status": "ready"})
    check(rs2["run_now"]["by"] == "BENCH" and not rs2.get("run_now_queue"),
          "a pending run-now on the same concept already covers it")
    # the queued entry takes the slot once it frees, stamped at that moment
    rs.pop("run_now")
    RL.chain_pop(rs, T + 900)
    check(rs.get("run_now", {}).get("concept") == C1 and rs["run_now"]["at"] == T + 900 and "run_now_queue" not in rs,
          "a free slot takes the queued chain, its TTL starting now: %r" % rs.get("run_now"))
    st = SD.fresh()
    st["roles"] = {"Arbiter": {"done": {}, "runs": [], "run_now_queue": [dict(hand, concept=C1, at=T)]}}
    ro = SD.lrobs(SD.ops_status(T), lambda: None)
    ro["stage_open"] = lambda c, u, b: ("PACKET", b)
    ro["coverage_pre"] = lambda c: None
    la = [a for a in SD.role_acts(SD.rdecide([SD.arbiter(enabled=False)], st, ro, T + 60)) if a["do"] == "role_launch"]
    check(len(la) == 1 and "run_now_queue" not in st["roles"]["Arbiter"], "decide pops the queue and launches it")


def test_daily_cap():
    rs = {}
    cfg = dict(RL.ROLE_DEFAULTS, **dict(designer_row(), chain_max_per_day=2))
    for i in range(2):
        harvest(rs, {"stage": i + 1, "status": "ready"}, unit="u%d" % i, cfg=cfg)
        check(rs.pop("run_now", None) is not None, "chain %d of 2 asked" % (i + 1))
    acts = harvest(rs, {"stage": 1, "status": "ready"}, unit="u9", cfg=cfg)
    check("run_now" not in rs and [a.get("kind") for a in acts if a["do"] == "alarm"] == ["role:Designer:chain_cap"],
          "past chain_max_per_day the loop stops with one chain_cap alarm: %r" % [a.get("kind") for a in acts])
    other = harvest(rs, {"stage": 1, "status": "ready"}, unit="u10", concept=C2, cfg=cfg)
    check(rs.get("run_now", {}).get("concept") == C2 and not [a for a in other if a["do"] == "alarm"],
          "the cap is per concept")


def sweep_decide(rows, roles_state=None, cfg_over=None, now=None):
    """One Dispatcher decide over a Designer-shaped role (disabled, chain_stages) whose concepts reader returns rows
    (concept, stage.json, pending-since epoch or None). -> (state, acts, opened concepts)."""
    st = SD.fresh()
    st["roles"] = roles_state if roles_state is not None else {}
    opened = []
    ro = SD.lrobs(SD.ops_status(T), lambda: None)
    ro["stage_open"] = lambda c, u, b: (opened.append(c), ("PACKET", b))[1]
    ro["coverage_pre"] = lambda c: None
    ro["stage_concepts"] = rows if callable(rows) else (lambda: rows)
    role = SD.arbiter(enabled=False)
    role.update(dict({"chain_stages": True, "stage_machine": "designer_stage"}, **(cfg_over or {})))
    acts = SD.role_acts(SD.rdecide([role], st, ro, now if now is not None else T + 60))
    return st, acts, opened


def test_orphan_sweep():
    """OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV, 3rd recurrence: GimmeSomeSlack and Pyrelands closed ready before
    chain_stages existed, so no harvest ever chained them and the stall alarm rang for hours. The decide tick sweeps
    every concept the stall alarm counts as pending (ready, or waiting_owner he has answered) and asks its run."""
    old = T - 4 * 3600
    st, acts, opened = sweep_decide([(C1, {"stage": 2, "status": "ready", "results": [{"outcome": "return"}]}, old)])
    check(opened == [C1] and any(a["do"] == "role_launch" and "orphan" in a.get("why", "") for a in acts),
          "a ready concept nobody chained (closed before the chain, 4 h ago) is launched by the next decide: %r %r"
          % (opened, [(a["do"], a.get("why", "")[:80]) for a in acts]))
    st, acts, opened = sweep_decide([(C2, {"stage": 3, "status": "waiting_owner"}, old)])
    check(opened == [C2], "a waiting_owner concept he has answered (pending since his answer) is launched too")
    for why, row in (("rejected last result, parked", (C1, {"stage": 3, "status": "ready", "results": [
                         {"outcome": "rejected", "why": ["x: source path no/such/file.json does not exist"]}]}, old)),
                     ("still waiting on him", (C1, {"stage": 3, "status": "waiting_owner"}, None)),
                     ("blocked", (C1, {"stage": 3, "status": "blocked"}, None)),
                     ("running", (C1, {"stage": 3, "status": "ready", "running": {"run": "u"}}, old)),
                     ("under the grace", (C1, {"stage": 3, "status": "ready"}, T - 60))):
        st, acts, opened = sweep_decide([row])
        check(opened == [] and not st["roles"].get("Arbiter", {}).get("run_now"), "%s: nothing swept" % why)
    # a pending run-now on another concept keeps its slot; the orphan waits behind it, once, across ticks
    hand = {"at": T - 30, "by": "BENCH", "why": "start ModTwo", "mode": "run", "concept": C2}
    rows = [(C1, {"stage": 2, "status": "ready"}, old)]
    rs = {"done": {}, "runs": [], "run_now": dict(hand)}
    st, acts, opened = sweep_decide(rows, {"Arbiter": rs})
    q = st["roles"]["Arbiter"].get("run_now_queue") or []
    check(opened == [C2] and [x["concept"] for x in q] == [C1], "behind a pending run-now the orphan queues: %r" % q)
    n = dict(st["roles"]["Arbiter"].get("chain_day") or {})
    st["roles"]["Arbiter"]["run_now"] = dict(hand, concept="/tmp/concepts/ModThree")   # the slot is still taken
    st, acts, opened = sweep_decide(rows, st["roles"], now=T + 120)
    check(len(st["roles"]["Arbiter"].get("run_now_queue") or []) == 1
          and dict(st["roles"]["Arbiter"].get("chain_day") or {}) == n,
          "a queued orphan is not asked again on the next tick (no double count)")
    # the cap holds: a concept chained chain_max_per_day times today is not swept
    capped = {"done": {}, "runs": [], "chain_day": {"%s %s" % (RL.day_of(T + 60), C1): 2}}
    st, acts, opened = sweep_decide(rows, {"Arbiter": capped}, {"chain_max_per_day": 2})
    check(opened == [] and any(a.get("kind") == "role:Arbiter:chain_cap" for a in acts),
          "past chain_max_per_day the sweep stops with the chain_cap alarm")
    st, acts, opened = sweep_decide(rows, st["roles"], {"chain_max_per_day": 2}, now=T + 120)
    check(opened == [] and not any(a.get("kind") == "role:Arbiter:chain_cap" for a in acts),
          "the cap alarm is said once a day, not every tick")
    # no chain_stages: no sweep; an unreadable concepts dir alarms and launches nothing
    st, acts, opened = sweep_decide(rows, cfg_over={"chain_stages": False})
    check(opened == [], "a row without chain_stages sweeps nothing")

    def boom():
        raise OSError("concepts dir missing")
    st, acts, opened = sweep_decide(boom)
    check(opened == [] and any(a.get("kind") == "role:Arbiter:chain_sweep" for a in acts),
          "an unreadable concepts dir alarms (role:<name>:chain_sweep) and sweeps nothing")
    st, acts, opened = sweep_decide(boom, st["roles"], now=T + 120)
    check(not any(a.get("kind") == "role:Arbiter:chain_sweep" for a in acts), "the blind alarm is said once per outage")


def test_rejected_sweep():
    """RELAPSE_QUEUES_FIX_DIED_TWICE (incident queues-20261105210826, three acks whose fixes died): the sweep skipped
    EVERY rejected-last concept, so GSS stage 2, rejected 09:14Z and 10:13Z for a missing coverage_verdict.json, sat
    6 h after the file landed at 10:12Z while the stall alarm rang. Now the sweep and the stall reader share
    designer_stage.rejection_parked: parked = a retry cannot help; else the sweep re-chains with the reasons."""
    import shutil
    import tempfile
    import time
    import designer_stage as DS
    repo = tempfile.mkdtemp(prefix="selftest_rechain_")
    try:
        rel = "design/concepts/GimmeSomeSlack/coverage_verdict.json"
        at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 3600))
        why = ["asks[a_shock_floor_ends]: source path %s does not exist" % rel]
        gss = {"stage": 2, "status": "ready", "results": [
            {"at": at, "outcome": "rejected", "run": "rm-role-designer-1793956212", "stage": 2, "why": why},
            {"at": at, "outcome": "rejected", "run": "rm-role-designer-1793959835", "stage": 2, "why": why}]}
        old = T - 6 * 3600
        SD_ro = {"rejection_parked": lambda st: DS.rejection_parked(st, repo)}
        st, acts, opened = sweep_with(sweep_decide, [(C1, gss, old)], SD_ro)
        check(opened == [], "GSS before its file lands: parked (the cited path is missing), nothing swept")
        os.makedirs(os.path.dirname(os.path.join(repo, rel)))
        open(os.path.join(repo, rel), "w").write("{}")
        st, acts, opened = sweep_with(sweep_decide, [(C1, gss, old)], SD_ro)
        rn = (st["roles"].get("Arbiter") or {}).get("run_now_last") or {}
        check(opened == [C1] and any("cause gone" in a.get("why", "") for a in acts),
              "GSS after its file landed (two identical rejections before): the sweep re-chains it: %r %r" % (
                  opened, [(a["do"], a.get("why", "")[:90]) for a in acts]))
        check(rn.get("reasons") == why or any(why[0] in str(a) for a in acts),
              "the re-chained run carries the rejection's reasons: %r" % rn)
        sp = {"results": [{"outcome": "rejected", "why": ["x: source path design/My Notes/a b.json does not exist"]}]}
        check(bool(DS.rejection_parked(sp, repo)), "a cited path with spaces is read whole (still missing: parked)")
        os.makedirs(os.path.join(repo, "design/My Notes"))
        open(os.path.join(repo, "design/My Notes/a b.json"), "w").write("{}")
        check(DS.rejection_parked(sp, repo) is None, "and once it lands, the rejection is due a retry")
        one = {"stage": 4, "status": "ready", "results": [
            {"at": at, "outcome": "rejected", "run": "rm-role-designer-1", "stage": 4, "why": ["no result.json"]}]}
        st, acts, opened = sweep_with(sweep_decide, [(C1, one, old)], SD_ro)
        check(opened == [C1], "Pyrelands' shape (one unlabelled 'no result.json' rejection) is re-chained once")
        two = dict(one, results=one["results"] + [dict(one["results"][0], run="rm-role-designer-2")])
        st, acts, opened = sweep_with(sweep_decide, [(C1, two, old)], SD_ro)
        check(opened == [], "the same rejection twice in a row is parked (the arbiter's, not a third run)")
        env = dict(one, results=[dict(one["results"][0], why=["account died [cause:environment]"])])
        st, acts, opened = sweep_with(sweep_decide, [(C1, env, old)], SD_ro)
        check(opened == [], "a rejection labelled [cause:environment] is the cause book's: parked")
        check(DS.rejection_parked({"results": [{"outcome": "done"}]}, repo) is None
              and DS.rejection_parked({}, repo) is None, "no rejected last result: never parked")
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_parked_record():
    """DESIGNER_RECHAIN_FIX_REJECTS_WAIT_FOREVER: the sweep's parked branch was a silent skip and the stall reader skips
    the same concepts, so a parked concept had no line of its own. Each parking is now said once a day: ledger and the
    Conductor's log, naming the concept, the rule's reason and the rejection."""
    old = T - 6 * 3600
    rej = {"at": "2026-11-06T10:13:06Z", "outcome": "rejected", "run": "rm-role-designer-2", "stage": 4,
           "why": ["no result.json"]}
    two = {"stage": 4, "status": "ready", "results": [dict(rej, run="rm-role-designer-1"), rej]}
    parked_alarms = lambda acts: [a for a in acts if ":parked:" in str(a.get("kind"))]  # noqa: E731
    st, acts, opened = sweep_decide([(C1, two, old)])
    said = parked_alarms(acts)
    check(opened == [] and len(said) == 1, "the arbiter's identical rejection: nothing re-chained, one parked record: %r"
          % [a.get("kind") for a in acts])
    a = said[0] if said else {}
    check(a.get("do") == "alarm" and a.get("note") and a.get("conductor_log"), "the record reaches ledger and Conductor")
    check("rejected twice" in a.get("why", "") and "no result.json" in a.get("why", "")
          and os.path.basename(C1) in a.get("why", ""), "it names the concept, the rule's reason and the rejection: %r"
          % a.get("why"))
    st, acts, opened = sweep_decide([(C1, two, old)], st["roles"], now=T + 120)
    check(not parked_alarms(acts), "the next tick says nothing new")
    st, acts, opened = sweep_decide([(C1, two, old)], st["roles"], now=T + 86400 + 60)
    check(len(parked_alarms(acts)) == 1, "still parked a day later: said again, it has not gone away")
    other = {"stage": 4, "status": "ready", "results": [dict(rej, why=["x"]), dict(rej, why=["x"])]}
    st, acts, opened = sweep_decide([(C1, other, old), (C2, two, old)], st["roles"], now=T + 86400 + 120)
    kinds = [x["kind"] for x in parked_alarms(acts)]
    check(len(set(kinds)) == 2, "a new reason and another concept each get their own kind, past the repeat limit: %r"
          % kinds)
    st, acts, opened = sweep_decide([(C2, two, old)], st["roles"], now=T + 86400 + 180)
    check(C1 not in (st["roles"]["Arbiter"].get("parked_said") or {}), "unparked or gone: its mark leaves the book")
    miss = {"stage": 2, "status": "ready", "results": [
        {"at": rej["at"], "outcome": "rejected", "run": "r", "stage": 2, "why": ["source path no/such.json does not exist"]}]}
    st, acts, opened = sweep_decide([(C1, miss, old)])
    check(opened == [] and any("still missing" in x["why"] for x in parked_alarms(acts)),
          "a cited path still missing is parked with a record too")
    ok = {"stage": 2, "status": "ready", "results": [{"at": rej["at"], "outcome": "done", "stage": 1}]}
    st, acts, opened = sweep_decide([(C1, ok, old)])
    check(opened == [C1] and not parked_alarms(acts), "a concept not rejected is swept as before, no parked record")


def sweep_with(fn, rows, extra):
    """sweep_decide with extra obs (the parked rule pointed at a temp repo)."""
    real = SD.lrobs

    def lrobs(*a, **k):
        ro = real(*a, **k)
        ro.update(extra)
        return ro
    SD.lrobs = lrobs
    try:
        return fn(rows)
    finally:
        SD.lrobs = real


def main():
    for t in (test_row, test_done_chains, test_no_chain_states, test_queue_behind_pending, test_daily_cap,
              test_orphan_sweep, test_rejected_sweep, test_parked_record):
        t()
    print("selftest_designer_chain: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
