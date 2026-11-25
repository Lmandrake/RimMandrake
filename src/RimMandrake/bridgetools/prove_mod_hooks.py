#!/usr/bin/env python3
"""Live proof of jawa/mod_hooks and of the run's mod sinks. Page: design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md. Item
RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION.

    python.exe prove_mod_hooks.py      on a TEST-profile game with a scratch quicktest map; changes nothing but the clock
    python3 prove_mod_hooks.py --selfcheck      the judges, good and planted; no game

Rows: 1 every RimMandrake assembly of the game is listed, each with a known build and no problem  2 admit: an exploring run is
admitted, and an acceptance run is refused for exactly the mods whose build is not RELEASE  3 after a run, no sink is set and none was
found stale at its arm (UNMEASURED while no loaded mod has a trace point: the first use is each mod's next version).
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_run_until as R  # noqa: E402
W = R.W


# ------------------------------------------------------------------------------------------------ the judges (pure)
def judge_list(rep):
    mods = rep.get("mods") if rep.get("success") else None
    if not mods:
        return None, "no list: %s" % R.brief(rep)
    bad = [m["mod"] for m in mods if m.get("build") not in ("none", "RELEASE", "PROOF") or m.get("problems")]
    return not bad, "%d mods, %d with hooks; not clean: %s" % (len(mods), sum(m.get("build") != "none" for m in mods), bad)


def judge_admit(mods, explore, accept):
    if not (explore.get("success") and accept.get("success")):
        return None, "admit not read: %s %s" % (R.brief(explore), R.brief(accept))
    want = sorted(m["mod"] for m in mods if m.get("build") not in ("none", "RELEASE"))
    got = sorted(r.split(" ", 2)[1] for r in accept.get("refusals") or [])
    return explore.get("admitted") is True and got == want, "explore admitted %s; acceptance refuses %s, want %s" % (explore.get("admitted"), got, want)


def judge_sinks(mods, ran, after):
    traced = [m["mod"] for m in mods if m.get("trace") == "yes"]
    if not traced:
        return None, "no loaded mod has a trace point yet"
    if not ran or not after.get("success"):
        return None, "the run or the list after it failed: %s %s" % (ran, R.brief(after))
    return after.get("armed") == 0 and after.get("staleAtArm") == 0, "trace points %d; after the run armed %s, stale at arm %s, said %s" % (
        len(traced), after.get("armed"), after.get("staleAtArm"), after.get("said"))


def selfcheck():
    ok = {"success": True, "mods": [{"mod": "RimMandrakeA", "build": "RELEASE", "problems": [], "trace": "yes"},
                                    {"mod": "RimMandrakeB", "build": "PROOF", "problems": [], "trace": "no trace point"},
                                    {"mod": "RimMandrakeC", "build": "none", "problems": [], "trace": "no trace point"}]}
    mods = ok["mods"]
    sick = {"success": True, "mods": [dict(mods[0], problems=["RMReset on X.Y: must be ..."])]}
    ex, ac = {"success": True, "admitted": True}, {"success": True, "refusals": ["PROOF_BUILD: RimMandrakeB is a PROOF build: ..."]}
    cases = [("list good", judge_list(ok)[0], True), ("a problem", judge_list(sick)[0], False), ("no list", judge_list({"success": False})[0], None),
             ("admit good", judge_admit(mods, ex, ac)[0], True), ("a PROOF build admitted", judge_admit(mods, ex, {"success": True, "refusals": []})[0], False),
             ("explore refused", judge_admit(mods, {"success": True, "admitted": False}, ac)[0], False),
             ("sinks good", judge_sinks(mods, True, {"success": True, "armed": 0, "staleAtArm": 0})[0], True),
             ("a sink left set", judge_sinks(mods, True, {"success": True, "armed": 1, "staleAtArm": 0})[0], False),
             ("a stale sink", judge_sinks(mods, True, {"success": True, "armed": 0, "staleAtArm": 1})[0], False),
             ("no trace point", judge_sinks(mods[1:], True, {"success": True, "armed": 0, "staleAtArm": 0})[0], None)]
    bad = [(n, got, want) for n, got, want in cases if got is not want]
    for n, got, want in cases:
        print("%s %s" % ("ok  " if got is want else "FAIL", n))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    W.connect()
    row = W.row
    if not R.start_map():
        return 2
    lst = W.call("jawa/mod_hooks", action="list")
    v, d = judge_list(lst)
    row("1 every RimMandrake assembly listed", v, d)
    mods = lst.get("mods") or []
    v, d = judge_admit(mods, W.call("jawa/mod_hooks", action="admit", purpose="explore"), W.call("jawa/mod_hooks", action="admit", purpose="acceptance"))
    row("2 admit by build", v, d)
    R.open_session()
    t0 = R.tick()
    rep = R.run(R.at_tick(t0 + 60), 400, request=R.req("hooks"), speed="Normal")
    R.end_session()
    v, d = judge_sinks(mods, rep.get("why") == "hit", W.call("jawa/mod_hooks", action="list"))
    row("3 every sink is clear after a run", v, d)
    vals = [w for _, w in W.ROWS]
    print(json.dumps({"rows": W.ROWS}))
    return 1 if "FAIL" in vals else (2 if "UNMEASURED" in vals else 0)


if __name__ == "__main__":
    sys.exit(main())
