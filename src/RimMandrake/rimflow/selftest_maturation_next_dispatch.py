#!/usr/bin/env python3
"""selftest_maturation_next_dispatch.py: `maturation.py next` reads the Dispatch tick's own decision for the mod.

Item RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS. Measured 8:15 PM PST 2026-11-16: `maturation.py next
ExplosiveKnockback` printed "NEXT (automatic: the Dispatch tick launches it): blind cycle 5" while the tick's own reading
had paused it at the stage ceiling since 1:48 PM (decision ceiling, klass paused, "nothing more launches on it until the
Conductor reads the spend"); the Conductor read "automatic" and waited six hours for a launch that could not come.
`next` is a reading of the stage record alone; an "automatic" claim is the tick's to make, so it now names the tick's
decision, and a paused, held, stale or absent tick reading replaces the claim.

    python3 src/RimMandrake/rimflow/selftest_maturation_next_dispatch.py      exit 0 when every check prints PASS

Watched failing on the base 28f9104cc6 (the paused case still printed "automatic"), then passing. Offline: a temp copy of
the blind fixture (selftest_maturation.copy_blind) and a temp RM_MATURATION_DISPATCH_DIR; nothing in the repo is written.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import selftest_maturation as ST    # noqa: E402  its blind fixture: Gimme Some Slack at the blind challenge, cycle 1 owed

MOD = "GimmeSomeSlack"
FAILS = []
CEILING_WHY = ("≈39.1M weighted tokens spent at Blind challenge, tests first (Stages 4 and 5), at or past the "
               "≈35.0M weighted tokens ceiling (its release is spent); release it: python3 "
               "src/RimMandrake/rimflow/maturation_dispatch.py release %s --stage blind_challenge --read-tokens 39146360 "
               "--tokens 11209696 --why \"...\"" % MOD)


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def reading(ddir, mods, age_s=30):
    at = time.time() - age_s
    with open(os.path.join(ddir, "reading.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": 1, "at": at, "at_pac": time.strftime("%-I:%M %p", time.localtime(at)) + " PST",
                   "mods": mods}, f)


def run_next(root, ddir, *extra):
    env = dict(os.environ, RM_MATURATION_DISPATCH_DIR=ddir)
    env.pop("MATURATION_CLOCK", None)
    r = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "next", MOD] + list(extra),
                       capture_output=True, text=True, timeout=300, env=env)
    return r.returncode, r.stdout, r.stderr


def last_next(out):
    lines = [x for x in out.splitlines() if x.startswith("NEXT")]
    return lines[-1] if lines else ""


def main():
    before = ST.git_status()
    root = tempfile.mkdtemp(prefix="maturation_next_dispatch_")
    ddir = os.path.join(root, "dispatch")
    os.makedirs(ddir)
    try:
        ST.copy_blind(root)

        # the base case: no dispatch reading at all is the absent tick, never "automatic"
        rc, out, err = run_next(root, ddir)
        nl = last_next(out)
        ok(rc == 0, "next exits 0 with no tick reading (%s)" % err.strip()[-200:])
        ok("automatic" not in nl and "UNMEASURED" in nl and "reading" in nl,
           "no tick reading: the NEXT line says whether it launches is UNMEASURED, not automatic (%s)" % nl[:160])

        # the measured case of 2026-11-16: the tick paused the mod at the ceiling
        reading(ddir, {MOD: {"decision": "ceiling", "klass": "paused", "why": CEILING_WHY, "stage": "blind_challenge",
                             "for_min": 394}})
        rc, out, err = run_next(root, ddir)
        nl = last_next(out)
        ok(rc == 0, "next exits 0 with a paused tick reading (%s)" % err.strip()[-200:])
        ok(nl.startswith("NEXT (PAUSED by the Dispatch tick: ceiling") and "automatic" not in nl,
           "a ceiling pause replaces the automatic claim (%s)" % nl[:160])
        ok("maturation_dispatch.py release %s --stage blind_challenge" % MOD in nl and "394 min" in nl,
           "the paused NEXT line carries the tick's release command and how long it has been paused")
        ok("  dispatch tick" in out and "ceiling" in out.split("  dispatch tick", 1)[1].splitlines()[0],
           "a dispatch line names the tick's decision")
        rc, js, err = run_next(root, ddir, "--json")
        try:
            d = json.loads(js)
        except ValueError:
            d = {}
        ok((d.get("dispatch") or {}).get("decision") == "ceiling" and str(d.get("next", "")).startswith(
            "NEXT (PAUSED by the Dispatch tick: ceiling"), "--json carries the tick's decision and the replaced NEXT")

        # a held mod (the journal's kind hold, or his owner hold) is held, not automatic
        reading(ddir, {MOD: {"decision": "held", "klass": "held", "why": "a Conductor hold stands on stage 4+5"}})
        nl = last_next(run_next(root, ddir)[1])
        ok(nl.startswith("NEXT (HELD by the Dispatch tick: held") and "automatic" not in nl,
           "a held tick decision replaces the automatic claim (%s)" % nl[:160])

        # a waiting decision (a run live, settling, slots full) keeps the automatic claim and names what it waits on
        reading(ddir, {MOD: {"decision": "slots_full", "klass": "wait", "why": "4 live runs on advancing mods"}})
        rc, out, _ = run_next(root, ddir)
        nl = last_next(out)
        ok(nl.startswith("NEXT (automatic: the Dispatch tick launches it)") and "slots_full" in out,
           "a waiting tick keeps automatic and its dispatch line names the wait (%s)" % nl[:120])

        # a stale reading (the step is not ticking) is UNMEASURED
        reading(ddir, {MOD: {"decision": "slots_full", "klass": "wait", "why": "x"}}, age_s=3600)
        nl = last_next(run_next(root, ddir)[1])
        ok("automatic" not in nl and "UNMEASURED" in nl and "60 min old" in nl,
           "a reading an hour old makes the launch UNMEASURED (%s)" % nl[:160])

        # a mod the tick does not carry (not on its advancing list) is launched by nobody
        reading(ddir, {"SomeOtherMod": {"decision": "live", "klass": "wait", "why": "x"}})
        nl = last_next(run_next(root, ddir)[1])
        ok("automatic" not in nl and "not on the Dispatch tick's list" in nl,
           "a mod absent from the tick's reading is not automatic (%s)" % nl[:160])

        ok(ST.git_status() == before, "nothing under design/concepts in the repo was written")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
