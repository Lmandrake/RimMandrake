#!/usr/bin/env python3
"""Selftest of ROLES_FIX_REJECTED_STAGE_ROUTES_BY_CAUSE (WP-15): a REJECTED stage close routes by its cause class
(module -> builder re-chain with the reasons, check/bar -> the alarm stands for the checker's owner, environment ->
cause book attach, unknown/mixed -> builder) and a 2nd identical rejection is not looped again (its alarm stands).
RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED: the Setter and arbiter seams (Relentless-era exams,
stage_dispute) are gone from role_launch; check/bar and a repeat take the no-exam route. Before, every rejection chained
nothing and waited for a person to re-press the same role (incident roles-20261106083416, Designer on Pyrelands).
Pure: the real role_launch._supervise_one with fake obs and seams, no systemd, no git, no store."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []
T = 1793953915
C1 = "/tmp/concepts/Pyrelands"


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def designer_cfg():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    return dict(RL.ROLE_DEFAULTS, **row)


GOOD = {"subtype": "success", "usage": {k: 10 for k in RL.USAGE_KEYS},  # a real result names its model
        "modelUsage": {"claude-opus-5-5": {"inputTokens": 10, "outputTokens": 10, "cacheReadInputTokens": 10, "cacheCreationInputTokens": 10}}}


def harvest(rs, errs, res=GOOD, unit="rm-role-designer-1", seams=None, stage=4, stop_tries=0):
    """One finished Designer run on C1 whose close is REJECTED with `errs`; seams record what they were handed."""
    run = {"state": "running", "unit": unit, "at": T - 600, "day": RL.day_of(T), "budget": 90000, "mode": "run",
           "item": "PYRE_ITEM", "concept": C1, "scope": "S.scope", "marker": "M"}
    if stop_tries:
        run["stop_tries"] = stop_tries
    rs.setdefault("runs", []).append(run)
    calls = {"setter": [], "cause_book": [], "arbiter": []}
    s = dict({"setter": True, "cause_book": True, "arbiter": "dispute opened"}, **(seams or {}))
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
           "stage_close": lambda c, u, t: (not errs, list(errs)), "stage_land": lambda c, u: None,
           "stage_turn": lambda c: None, "stage_status": lambda c: {"stage": stage, "status": "ready"},
           # the seams decide only: an action for the Dispatcher to carry out, or None (no exam / no live cause)
           "setter": lambda item, reasons, now, role=None: (calls["setter"].append((item, list(reasons))), dict(
               do="role_setter_resit", role=role, item=item, resit_why="; ".join(reasons)) if s["setter"] else None)[1],
           "cause_book": lambda key, said, now, role=None: (calls["cause_book"].append(key), dict(
               do="role_cause_attach", role=role, key=key, said=said, at_s=now) if s["cause_book"] else None)[1],
           "arbiter": lambda role, concept, item, sig, reasons: (calls["arbiter"].append(sig), s["arbiter"])[1]}
    RL._supervise_one("Designer", rs, designer_cfg(), obs, T, lambda **kw: acts.append(kw), set())
    route = [a for a in acts if a.get("do") == "role_hold" and "rejection cause" in a.get("why", "")]
    return acts, calls, route


def rechained(rs):
    r = rs.get("run_now")
    return isinstance(r, dict) and r.get("concept") == C1


def test_classifier():
    c = RL.rejection_cause
    check(c(["[cause:check] clause c2 reads the wrong file"])[0] == "check", "a Marker check tag reads check")
    check(c(["[cause:bar] the item text asks two things"])[0] == "bar", "a bar tag reads bar")
    check(c(["x"], classes=["environment"])[0] == "environment", "an evidence marker `classes` label counts")
    check(c(["[cause:check] a", "[cause:module] b"])[0] == "mixed", "two labelled classes read mixed")
    check(c(["x"], {"state": "done"}, GOOD)[0] == "module", "a finished run refused by the program check is module")
    check(c(["no result.json"], {"state": "failed"}, {})[0] == "unknown",
          "a failed run with no result and no environment signal is unknown")
    check(c(["x"], {"state": "failed"}, {"is_error": True, "api_error_status": 429})[0] == "environment",
          "an account death is environment")
    check(c(["x"], {"state": "failed", "stop_tries": 2}, {})[0] == "environment", "a stopped run is environment")
    check(RL.rejection_sig(4, "module", ["result names run 'rm-role-designer-1', not the open run 'rm-role-designer-2'"])
          == RL.rejection_sig(4, "module", ["result names run 'rm-role-designer-7', not the open run 'rm-role-designer-8'"]),
          "run names are masked: the same fault on two runs is one signature")


def test_module_to_builder():
    rs = {}
    acts, calls, route = harvest(rs, ["decisions[d1]: OWNER:1793796507483890758 finds no event"])
    check(rechained(rs) and "OWNER:" in rs["run_now"]["why"] and "module" in rs["run_now"]["why"],
          "module -> the builder (the same role) is re-chained with the full reasons: %r" % rs.get("run_now"))
    check(route and "-> builder" in route[0]["why"] and not any(calls.values()), "the builder route is said, no seam called")
    check(any(a.get("kind") == "role:Designer:stage_rejected" and a.get("do") == "alarm" for a in acts),
          "the stage_rejected alarm still stands")


def test_check_and_bar_alarm_stands():
    for tag in ("check", "bar"):
        rs = {}
        acts, calls, route = harvest(rs, ["[cause:%s] clause c3 asserts the old schema" % tag])
        check(not [a for a in acts if a.get("do") == "role_setter_resit"] and not calls["setter"],
              "%s -> no Setter resit is decided or handed on" % tag)
        check(not rechained(rs) and route and "-> setter" in route[0]["why"] and "owes the fix" in route[0]["why"],
              "%s -> the alarm stands for the checker's owner, no builder loop: %r" % (tag, route[0]["why"] if route else None))
    check(not hasattr(RL, "to_setter") and not hasattr(RL, "setter_resit") and not hasattr(RL, "to_arbiter"),
          "the Setter and arbiter seams are gone from role_launch")


def test_environment_to_cause_book():
    dead = {"is_error": True, "api_error_status": 429, "usage": {k: 10 for k in RL.USAGE_KEYS}}
    rs = {}
    acts, calls, route = harvest(rs, ["no result.json (a closing message is not a result)"], res=dead)
    check([a.get("key", "")[:17] for a in acts if a.get("do") == "role_cause_attach"] == ["role-env|Designer"],
          "environment -> one role_cause_attach action for the Dispatcher to carry out")
    check(len(calls["cause_book"]) == 1 and calls["cause_book"][0].startswith("role-env|Designer|")
          and not rechained(rs) and not calls["setter"] and "attached to cause" in route[0]["why"],
          "environment -> attached to the live cause record, no re-chain, no item filed: %r" % calls)
    rs = {}
    _, calls, route = harvest(rs, ["no result.json"], res=dead, seams={"cause_book": False})
    check(not rechained(rs) and "no live cause record" in route[0]["why"],
          "environment with no live cause: the alarm stands for Operations to file once, no re-chain")


def test_unknown_and_mixed_to_builder():
    rs = {}
    _, calls, route = harvest(rs, ["no result.json (a closing message is not a result)"], res=None)
    check(rechained(rs) and "unknown" in route[0]["why"] and "-> builder" in route[0]["why"] and not any(calls.values()),
          "the Pyrelands shape (failed, no result, no environment signal) -> unknown -> builder with its reasons")
    rs = {}
    _, calls, route = harvest(rs, ["[cause:check] c1", "[cause:environment] box"])
    check(rechained(rs) and "mixed" in route[0]["why"] and not calls["setter"] and not calls["cause_book"],
          "mixed labels -> builder, not the Setter or the cause book")


def test_second_identical_not_looped():
    rs = {}
    harvest(rs, ["decisions[d1]: no event"], unit="rm-role-designer-1")
    rs.pop("run_now", None)
    _, calls, route = harvest(rs, ["decisions[d1]: no event"], unit="rm-role-designer-2")
    check(not calls["arbiter"] and not rechained(rs) and "-> arbiter" in route[0]["why"] and "alarm stands" in route[0]["why"],
          "a 2nd identical rejection is not looped again and hands nothing to an arbiter: %r" % route[0]["why"])
    rs = {}
    harvest(rs, ["decisions[d1]: no event"], unit="rm-role-designer-1")
    rs.pop("run_now", None)
    _, calls, route = harvest(rs, ["decisions[d2]: other"], unit="rm-role-designer-2")
    check(rechained(rs) and not calls["arbiter"], "a different 2nd rejection is a first again: builder")
    rs = {"rejections": {C1: [{"sig": RL.rejection_sig(4, "module", ["decisions[d1]: no event"])}]}}
    RL.forget_rejections(rs, C1)
    check("rejections" not in rs, "an accepted close forgets the concept's rejections")


def test_real_seams():
    """The real WP-05 calls, on a temp book: the cause-book seam decides an attach only for a live record; cause_attach
    writes it under the book lock."""
    import tempfile
    import cause_book as CB
    tmp = tempfile.mkdtemp(prefix="wp15-")
    old = os.environ.get("RM_OPS_WATCH_DIR")
    os.environ["RM_OPS_WATCH_DIR"] = tmp
    try:
        path = os.path.join(tmp, "causes.json")
        check(RL.to_cause_book("role-env|Designer|x", "said", T) is None and not os.path.exists(path),
              "cause book seam: no live record -> None and nothing written (no filing here)")
        book = {}
        CB.begin(book, "role-env|Designer|x", "lead", "REPAIR_ITEM", T)
        CB.filed(book, "role-env|Designer|x", "REPAIR_ITEM", T)
        CB.save(path, book)
        todo = RL.to_cause_book("role-env|Designer|x", "Designer run rejected", T, role="Designer")
        check(todo and todo["do"] == "role_cause_attach" and "role-stage" not in CB.load(path)["role-env|Designer|x"]["aids"],
              "cause book seam: decides the attach and writes nothing")
        ok = RL.cause_attach(todo["key"], todo["said"], todo["at_s"])
        rec = CB.load(path)["role-env|Designer|x"]
        check(ok is True and "role-stage" in rec["aids"] and rec["item"] == "REPAIR_ITEM"
              and rec["readings"][-1]["said"] == "Designer run rejected",
              "cause_attach: attached to the live record, its repair item unchanged: %r" % rec)
    finally:
        if old is None:
            os.environ.pop("RM_OPS_WATCH_DIR", None)
        else:
            os.environ["RM_OPS_WATCH_DIR"] = old


TESTS = (test_classifier, test_module_to_builder, test_check_and_bar_alarm_stands, test_environment_to_cause_book,
         test_unknown_and_mixed_to_builder, test_second_identical_not_looped, test_real_seams)


def main():
    for t in TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
