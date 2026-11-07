#!/usr/bin/env python3
"""SLUICE_BOX_PROVE_THE_DAILY_WASH: the A2 live proof really reaches "on a FlowWorks river site". Offline, every call faked.

A2 ran with no site: the line lacked `--drivers on`, so the placer chain never settled northstar/river_site.py, ran on a
map with no river, and all 4 rows read UNMEASURED in 5 s with no box ever built. The sluice code never ran.

Reds on: the A2 line losing `--drivers on`, `--chains placer`, its row, or gaining --unmeasured-ok; the placer chain not
settling river_site.py before its first bridge call under the flag, on its own (no other river chain to settle it first);
the sluice row reading PASS on a wash that gave nothing, went off-pool, did not debit the stock by what landed, or washed
with its setting OFF, or on a site with no legal box or no placer mineral; row_verdict holding on anything but PASS.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(FW), "Utils")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FW)))
for _p in (os.path.join(UTILS, "modcheck", "live_queue"), os.path.join(UTILS, "modcheck"), UTILS, FW, HERE,
           os.path.join(ROOT, "src", "RimMandrake", "rimflow")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import drivers as D  # noqa: E402
import extensions_rivers as RIV  # noqa: E402
import relentless_live_round as R  # noqa: E402
import row_verdict as RV  # noqa: E402
import selftest_extensions as SE  # noqa: E402

ITEM = "SLUICE_BOX_PROVE_THE_DAILY_WASH"
ROW = "sluice_washes_pool_from_stock"
GOOD = {"poolCount": "2", "got": "3", "drawMatches": "True", "inPool": "True", "off": "sluice=off"}
NO_SITE = "UNMEASURED: no legal sluice site (shallow moving river beside solid bank) on this map | PLACER stock=8.8 cap=8.8"
FAILS = []


def ok(cond, msg):
    print("%s %s" % ("PASS" if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


def selfcheck_reply(kv):
    return " ".join("%s=%s" % (k, v) for k, v in sorted(kv.items()))


def game(reply, log=None):
    """A fake game whose RM_PlacerProof 'selfcheck' answers `reply`; `log` records that the bridge was reached."""
    def h(tool, params):
        if log is not None:
            log.append("bridge")
        if tool == "jawa/static_call" and params.get("method") == "ProofReport" and params.get("args") == "selfcheck":
            return {"success": True, "result": reply}
        return {"success": True, "result": "PLACER stock=8.8 cap=8.8 sluiced=0 panned=0 refills=0 pool=Jade:3,", "value": "1"}
    return h


def t_line_binds_the_site():
    with open(os.path.join(ROOT, "infrastructure", "state", "live_proofs", ITEM + ".txt"), encoding="utf-8") as f:
        text = f.read()
    line = R.proof_lines(text).get("A2", "")
    ok("--drivers on" in line, "A2 line settles the river site (--drivers on)")
    ok("--chains placer" in line and "run FlowWorks" in line, "A2 line runs the FlowWorks placer chain")
    ok("--row " + ROW in line, "A2 line reads the sluice row")
    ok("--unmeasured-ok" not in line, "A2 line accepts no UNMEASURED: a rock-less or river-less site is never a pass")


def t_placer_alone_settles_the_site_first():
    spec = importlib.util.spec_from_file_location("modcheck_validation_FlowWorks_sluice", os.path.join(FW, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    events, argvs = [], []

    def fake_call(argv, cwd, timeout_s):
        events.append("site")
        argvs.append(argv)
        return 0, "river site ready"
    real, env = D._call, os.environ.get(D.ENV)
    D._call = fake_call
    try:
        os.environ[D.ENV] = "1"
        D._DONE.clear()
        got = SE._ext_run(v, "placer", game(selfcheck_reply(GOOD), events))
        ok(events[:1] == ["site"] and events.count("site") == 1,
           "flag on, placer alone: the site is settled once, before the first bridge call (%s)" % events[:2])
        ok(bool(argvs) and any(str(a).endswith("river_site.py") for a in argvs[0]), "the settled site is river_site.py")
        ok(got.get(ROW) == "PASS", "the wrapped chain still reads its row (%s)" % got.get(ROW))
        del events[:]
        os.environ[D.ENV] = "0"
        D._DONE.clear()
        SE._ext_run(v, "placer", game(selfcheck_reply(GOOD), events))
        ok("site" not in events, "flag off: no site is settled (the run that read UNMEASURED in 5 s)")
    finally:
        D._call = real
        D._DONE.clear()
        if env is None:
            os.environ.pop(D.ENV, None)
        else:
            os.environ[D.ENV] = env


def t_row_refuses_a_bad_wash():
    def row(reply):
        return SE._ext_run(RIV, "placer", game(reply)).get(ROW)
    ok(row(selfcheck_reply(GOOD)) == "PASS", "control: a good wash reads PASS")
    for field, bad, want in (("got", "0", "FAIL"), ("drawMatches", "False", "FAIL"), ("inPool", "False", "FAIL"),
                             ("off", "sluice=RM_Goldx1", "FAIL"), ("poolCount", "0", "UNMEASURED")):
        got = row(selfcheck_reply(dict(GOOD, **{field: bad})))
        ok(got == want, "%s=%s reads %s (%s)" % (field, bad, want, got))
    got = row(NO_SITE)
    ok(got == "UNMEASURED", "no legal sluice site reads UNMEASURED, never a pass (%s)" % got)


def t_verdict_holds_only_on_pass():
    def holds(verdict):
        data = {"summary": {"chains": [{"components": [{"name": ROW, "verdict": verdict, "detail": NO_SITE}]}]}}
        return RV.judge(data, [ROW])[0]
    ok(holds("PASS"), "row_verdict holds on PASS")
    for v in ("FAIL", "UNMEASURED", "NOT_RUN"):
        ok(not holds(v), "row_verdict does not hold on %s" % v)
    ok(not RV.judge({"summary": {"chains": []}}, [ROW])[0], "row_verdict does not hold on a missing row")


def main():
    t_line_binds_the_site()
    t_placer_alone_settles_the_site_first()
    t_row_refuses_a_bad_wash()
    t_verdict_holds_only_on_pass()
    print("FAILS %d" % len(FAILS) if FAILS else "OK selftest_sluice_live_binding")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
