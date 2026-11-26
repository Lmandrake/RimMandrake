#!/usr/bin/env python3
"""selftest_ops_escalate: the promises of design/specs/2026-11-26-ops-sonnet-revisits-escalate/boundary.md.

RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT (owner's card 2026-11-19, "Sonnet for follow-ups only"): an
incident revisit run launches on Sonnet; a first look, the daily deep read, the economy pass and a run that covers a
scheduled slot stay on Opus; a Sonnet run's `rimflow ops-escalate` asks exactly one Opus continuation carrying its
notes, and the continuation's own escalation asks nothing. Pure: dispatcher.incident_execute, role_launch.decide_roles,
launch_role and launch_argv on fixtures and the SHIPPED dispatcher_schedule.json; writes only under a temp dir.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_ops_escalate_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TZ"] = "UTC"
time.tzset()
os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "ops_core")]
import dispatcher as D  # noqa: E402
import incident as IN  # noqa: E402
import ops_escalate as OE  # noqa: E402
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

T0 = 1800000000.0
FAILED = set()
NOP = lambda *a: None  # noqa: E731


def check(promise, ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + promise + ": " + what + ("" if ok else "  %r" % (detail,)))
    if not ok:
        FAILED.add(promise)


def shipped():
    real = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    return dict(real, seats={}, ledger_notes=False, publish=False,
                roles=[dict(r, runs_local=[], quick_checks_local=[], economy_local=None) for r in real["roles"]
                       if r["name"] in ("Operations", "Conductor")])


def op_of(sch):
    return next(r for r in sch["roles"] if r["name"] == "Operations")


def ring(i, revisit=False, deep=False):
    r = {"how": "fresh_run", "id": i, "reader": "Operations:fresh", "seat": None, "text": "INCIDENT %s" % i}
    return dict(r, revisit=True, deep=deep) if revisit else r


def apass(rings):
    return {"rows": [], "rings": rings, "cursor": 0, "snapshot": {"t": T0, "at": IN.iso(T0), "fresh": True, "open": [],
                                                                  "owner": []}}


def asked(rings, sch=None, now=T0):
    """-> (the run_now the dispatcher asked for these rings, the model launch_role launches it on)."""
    sch = sch or shipped()
    st = {"roles": {}}
    D.incident_execute(apass(rings), sch, st, TMP, now, NOP, NOP)
    req = (st["roles"].get("Operations") or {}).get("run_now") or {}
    return req, RL.launch_role(op_of(sch), {"mode": req.get("mode", "run"), "run_now": req})["model"]


def t_a_revisit_only_run_launches_on_sonnet():
    p = "a-revisit-only-run-launches-on-sonnet"
    req, model = asked([ring("a-1", revisit=True), ring("b-1", revisit=True)])
    check(p, req.get("revisit") is True and model == "sonnet",
          "a batch of revisits only is asked as a revisit run and launches on the shipped model_by_mode revisit (sonnet)",
          (req, model))
    check(p, RL.job_model(op_of(shipped()), {"mode": "run", "manual": req}) == "sonnet",
          "the launcher's account reading and its log name the same model (job_model)")


def t_a_first_look_and_a_mixed_batch_stay_on_opus():
    p = "a-first-look-and-a-mixed-batch-stay-on-opus"
    req, model = asked([ring("a-1")])
    check(p, not req.get("revisit") and model == "opus", "an incident's first look launches on Opus", (req, model))
    req, model = asked([ring("a-1", revisit=True), ring("b-1")])
    check(p, not req.get("revisit") and model == "opus", "a batch holding one first look launches on Opus", (req, model))
    req, model = asked([ring("a-1", revisit=True, deep=True)])
    check(p, req.get("model") == "opus" and model == "opus", "the daily deep read of revisits stays on Opus", (req, model))


def t_the_economy_pass_and_a_covered_slot_stay_on_opus():
    p = "the-economy-pass-and-a-covered-slot-stay-on-opus"
    real = op_of(shipped())
    op = SD.operations(model=real["model"], model_by_mode=real["model_by_mode"], incident_token_cap=123000)
    for hh, mode in (("06:30", "economy"), ("19:00", "run")):
        t = SD.at_local(hh)
        rs = {"done": {}, "runs": []}
        rs["run_now"] = RL.run_now_request({"roles": [op]}, {"role": "Operations", "by": "DISPATCHER",
                                                             "why": "INCIDENTS a-1 revisit", "mode": "run"}, t - 30)
        rs["run_now"].update(covers_slot=True, ids=["a-1"], revisit=True)
        st, acts = {"roles": {"Operations": rs}}, []
        RL.decide_roles({"roles": [op]}, st, SD.robs(SD.ops_status(t)), t, lambda **kw: acts.append(kw), set(), None)
        la = [a for a in acts if a.get("do") == "role_launch"]
        got = RL.launch_role(op, la[0])["model"] if la else None
        check(p, la and la[0].get("mode") == mode and got == "opus",
              "a revisit run that covers the %s slot runs that slot (%s) on Opus" % (hh, mode),
              [(a.get("do"), a.get("mode"), a.get("why")) for a in acts])
    t = SD.at_local("07:30")
    st, acts = {"roles": {"Operations": {"done": {}, "runs": []}}}, []
    RL.decide_roles({"roles": [op]}, st, SD.robs(SD.ops_status(t)), t, lambda **kw: acts.append(kw), set(), None)
    la = [a for a in acts if a.get("do") == "role_launch"]
    check(p, la and la[0].get("mode") == "economy" and RL.launch_role(op, la[0])["model"] == "opus",
          "the scheduled 07:30 economy pass launches on Opus", [(a.get("do"), a.get("mode")) for a in acts])


def env(unit, model, cont=None):
    e = {"RM_ROLE_UNIT": unit, "RM_ROLE_MODEL": model}
    return dict(e, RM_ROLE_CONTINUATION=cont) if cont else e


def t_a_sonnet_escalation_launches_one_opus_continuation_with_its_notes():
    p = "a-sonnet-escalation-launches-one-opus-continuation-with-its-notes"
    try:
        OE.record("odd", "OPERATIONS", env={})
        refused = False
    except ValueError as e:
        refused = "inside a launched Operations run" in str(e)
    check(p, refused, "outside a launched run the verb refuses, naming the repair")
    OE.record("the runway fell 40% in an hour with no new run", "OPERATIONS", env=env("rm-role-operations-11", "sonnet"),
              incident="acct-1", now=T0)
    sch, st = shipped(), {"roles": {}}
    D.incident_execute(apass([]), sch, st, TMP, T0 + 60, NOP, NOP)
    req = (st["roles"].get("Operations") or {}).get("run_now") or {}
    m = RL.launch_role(op_of(sch), {"mode": req.get("mode", "run"), "run_now": req}) if req else {}
    notes = os.path.join(TMP, "roles", "rm-role-operations-11.json.last.txt")
    check(p, req.get("model") == "opus" and m.get("model") == "opus" and req.get("escalation_of") == "rm-role-operations-11"
          and "the runway fell 40%" in req.get("why", "") and notes in req.get("why", "") and "acct-1" in req.get("why", ""),
          "one Opus run is asked, carrying the Sonnet run's words and the path of its notes", req)
    argv = RL.launch_argv(dict(m, clone=TMP), "rm-role-operations-12", "msg", "/o", "/e", "/usr/bin/claude") if m else []
    check(p, "RM_ROLE_MODEL=opus" in argv and "RM_ROLE_CONTINUATION=rm-role-operations-11" in argv,
          "the continuation's unit carries its model and whose continuation it is", argv)
    st["roles"].setdefault("Operations", {}).pop("run_now", None)
    D.incident_execute(apass([]), sch, st, TMP, T0 + 120, NOP, NOP)
    check(p, not (st["roles"]["Operations"].get("run_now")), "the next tick asks no second run for the same row",
          st["roles"]["Operations"])
    OE.record("still odd", "OPERATIONS", env=env("rm-role-operations-11", "sonnet"), now=T0 + 130)
    D.incident_execute(apass([]), sch, st, TMP, T0 + 180, NOP, NOP)
    check(p, not (st["roles"]["Operations"].get("run_now")), "a second row from the same Sonnet run asks none",
          st["roles"]["Operations"])
    st2 = {"roles": {"Operations": {"run_now": {"by": "DISPATCHER", "why": "busy", "mode": "run"}}},
           "incident": {"esc_cursor": len(OE.read_rows())}}     # the rows above were read by an earlier pass
    OE.record("odd again", "OPERATIONS", env=env("rm-role-operations-21", "sonnet"), now=T0 + 200)
    D.incident_execute(apass([]), sch, st2, TMP, T0 + 240, NOP, NOP)
    st2["roles"]["Operations"].pop("run_now", None)
    D.incident_execute(apass([]), sch, st2, TMP, T0 + 300, NOP, NOP)
    req2 = st2["roles"]["Operations"].get("run_now") or {}
    check(p, req2.get("escalation_of") == "rm-role-operations-21",
          "a row met by a run already asked waits and is asked on a later tick, not lost", req2)


def t_a_continuation_escalation_launches_nothing():
    p = "a-continuation-escalation-launches-nothing"
    sch, st = shipped(), {"roles": {}, "incident": {"esc_cursor": len(OE.read_rows())}}
    OE.record("deeper still", "OPERATIONS", env=env("rm-role-operations-12", "opus", cont="rm-role-operations-11"), now=T0 + 400)
    OE.record("odd on opus", "OPERATIONS", env=env("rm-role-operations-31", "opus"), now=T0 + 410)
    D.incident_execute(apass([]), sch, st, TMP, T0 + 460, NOP, NOP)
    check(p, not (st["roles"].get("Operations") or {}).get("run_now") and st["incident"]["esc_cursor"] == len(OE.read_rows()),
          "a continuation's escalation and an Opus run's escalation ask no run, and are read once", st)
    check(p, OE.due({"model": "sonnet", "unit": "u", "continuation": "u0"}, set())[0] is False,
          "a continuation's row asks none even when its model reads sonnet")


def main():
    t_a_revisit_only_run_launches_on_sonnet()
    t_a_first_look_and_a_mixed_batch_stay_on_opus()
    t_the_economy_pass_and_a_covered_slot_stay_on_opus()
    t_a_sonnet_escalation_launches_one_opus_continuation_with_its_notes()
    t_a_continuation_escalation_launches_nothing()
    n = 5
    print("selftest_ops_escalate: %d of %d promises pass%s" % (n - len(FAILED), n,
                                                               "" if not FAILED else " (FAIL: %s)" % ", ".join(sorted(FAILED))))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
