#!/usr/bin/env python3
"""Selftest: a repeated live failure calls a Test Pilot sitting as a pipeline step (TEST_PILOT_WIRE_INTO_THE_PIPELINE_EARLY).

Owner, 2026-11-04: "We may need Test Pilots to be able to be called in the Pipeline too, not just Relentless. Though I'd
want to know what Test Pilot did that we might teach Relentless' live testing mode." Before, a pilot sat only as the
approach ladder's late rung (after a redesign). Pins, on the supervisor's own transitions (Rig from selftest_relentless):
  * one live ending leaves the next worker a builder (rm-builder), briefed with the LIVE MOVES but no PILOT STEP;
  * the second live ending since the last sitting (rules.pilot_after_live_fails) makes the next worker an rm-testpilot sitting with
    the approach ladder untouched; its brief says PILOT STEP, asks for the explanation (`explain`), the TESTPILOT_SAT
    note and a TEACH line, and carries every one of the six LEANINGSCRUB moves; the journal and the attempt record it;
  * a pilot worker that dies sat nothing: the replacement is a pilot again;
  * the sitting's own ending (a snag, or `finish`) ends the step: the next worker is a builder, the item counts it;
  * an attributed re-entry of the same reading (fail(..., attributed=...)) is not a second live ending;
  * pilot_after_live_fails 0 switches the step off; a non-live ending never counts toward it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                       # noqa: E402
import selftest_relentless as SR             # noqa: E402

FAILS = []
I = "I0"


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def rig(**kw):
    rules = dict(n=1, share=1.0, max_workers=1, same_failure_limit=50, unchanged_returns_limit=500, snag_again_wait_h=0)
    rules.update(kw)
    x = SR.Rig(**rules)
    x.tick()
    x.run_one(I)
    return x


def end(x, klass="game_fail", detail=None):
    """The running worker's gen ends with `klass`; the next worker is leased. -> its launch (item, unit, prompt, agent, clone)."""
    st = x.st(I)
    if not st.get("contract"):
        R.contract(x.s, I, st["gen"], "python3 selftest_x.py")
    with x.s.lock():
        cur = x.s.load(I)
        R.fail(x.s, cur, klass, detail or "A2 FAIL on the running game (/l/%s.log)" % klass, x.r, x.now)
    x.w.up[x.st(I)["run"]["unit"]] = False
    x.tick()
    x.run_one(I)
    return [z for z in x.w.launches if z[0] == I][-1]


def die(x):
    """The running worker's process vanishes (worker_lost); the replacement is leased."""
    u = x.st(I)["run"]["unit"]
    x.now += 400
    x.w.up[u] = False
    x.tick()
    x.run_one(I)
    return [z for z in x.w.launches if z[0] == I][-1]


def t_step():
    x = rig()
    ok(x.w.launches[-1][3] == x.r["worker_agent"], "the first worker is a builder")
    first = end(x)
    ok(first[3] == x.r["worker_agent"], "one live ending: the next worker is still a builder (%s)" % first[3])
    ok("LIVE MOVES" in first[2] and "PILOT STEP" not in first[2], "one live ending: LIVE MOVES briefed, no pilot step")
    ok(x.st(I).get("live_since_pilot") == 1 and not x.st(I).get("pilot_step"), "one live ending counted, no step yet")

    second = end(x, "game_unmeasured", "B3 UNMEASURED on the running game")
    st = x.st(I)
    ok(second[3] == x.r["pilot_agent"] == "rm-testpilot", "two live endings: the next worker is an rm-testpilot "
       "sitting (%s)" % second[3])
    ok(st["approach"] == "build" and st["approach_changes"] == 0, "the step is not the ladder: approach stays %s"
       % st["approach"])
    b = second[2]
    ok("PILOT STEP" in b and "2 live endings since the last pilot sitting" in b and "game_unmeasured" in b and "B3 UNMEASURED" in b,
       "the brief says PILOT STEP with the count and the last ending")
    ok("cli.py pilot %s" % I in b and "explain --item %s" % I in b, "the brief sends it to the pilot brief and to `explain`")
    ok("TESTPILOT_SAT" in b and "TEACH" in b, "the brief asks for the TESTPILOT_SAT note and a TEACH line")
    ok(all(m in b for m in R.LIVE_MOVES) and len(R.LIVE_MOVES) == 6, "every LEANINGSCRUB live move is in the brief")
    ok(all(w in " ".join(R.LIVE_MOVES) for w in ("NOT REPRODUCED", "across items", "MOD / SITE / TOOL / HOST",
                                                "criterion is wrong", "pilot note", "change a decision")),
       "the six moves are the sitting's six")
    ok(st["pilot_step"].get("sat_gen") == st["gen"], "the step records the gen that sits")
    ok(any(a.get("pilot_step") and a.get("gen") == st["gen"] for a in x.s.attempts(I)), "the attempt line marks the sitting")
    with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
        ok('"pilot_step"' in f.read(), "the journal records the step")
    ok("Test Pilot sitting" in x.s.learned(I), "learned.md records why a pilot was called")

    again = die(x)
    ok(again[3] == x.r["pilot_agent"] and "PILOT STEP" in again[2], "a pilot that dies sat nothing: the replacement is a "
       "pilot again")
    ok(x.st(I)["pilot_step"].get("sat_gen") == x.st(I)["gen"], "the replacement's gen is the sitting")

    after = end(x, "instrument", "the bridge read the wrong map: BRIDGE_MAP_FIX_WRONG_MAP")
    st = x.st(I)
    ok(after[3] == x.r["worker_agent"] and "PILOT STEP" not in after[2], "the sitting's own ending ends the step: a builder "
       "follows (%s)" % after[3])
    ok(not st.get("pilot_step") and st.get("piloted") == 1, "the item counts the sitting")
    ok(st.get("live_since_pilot") == 0, "the count restarts after the step")
    x.done()


def t_finish_ends_it():
    st = {"item": I, "gen": 5, "approach": "build", "pilot_step": {"at": 1, "after": 2, "class": "game_fail", "sat_gen": 5}}
    ok(R.piloting(st), "a sitting gen is piloting")
    R.pilot_sat(st, "finish")
    ok(not st.get("pilot_step") and st["piloted"] == 1 and not R.piloting(st), "finish ends the sitting")
    st = {"item": I, "gen": 5, "approach": "build", "pilot_step": {"at": 1, "after": 2, "class": "game_fail"}}
    R.pilot_sat(st, "finish")
    ok(st.get("pilot_step") and R.piloting(st), "a step not yet sat is still owed")
    st = {"item": I, "gen": 6, "approach": "build", "pilot_step": {"at": 1, "after": 2, "class": "game_fail", "sat_gen": 5}}
    ok(not R.piloting(st), "a stale sat_gen is not a sitting")
    st = {"item": I, "gen": 6, "approach": "build", "pilot_step": {"at": 1, "after": 2, "class": "game_fail", "sat_gen": 6}}
    R.pilot_sat(st, "worker_lost")
    ok(st["pilot_step"] and "sat_gen" not in st["pilot_step"], "a lost worker leaves the step pending")


def t_attributed_and_off():
    x = rig()
    with x.s.lock():
        cur = x.s.load(I)
        R.fail(x.s, cur, "game_fail", "A2 FAIL (attributed PRODUCT)", x.r, x.now, attributed={"targets": ["PRODUCT"]})
    ok(not x.st(I).get("live_since_pilot"), "an attributed re-entry is not a second live ending")
    x.done()

    x = rig()
    for k in ("snag", "blind_fail_like_snag", "build_broke"):
        with x.s.lock():
            cur = x.s.load(I)
            R.fail(x.s, cur, k, "not a live reading", x.r, x.now)
    ok(not x.st(I).get("live_since_pilot") and not x.st(I).get("pilot_step"), "non-live endings never count")
    x.done()

    x = rig(pilot_after_live_fails=0)
    end(x)
    z = end(x)
    ok(z[3] == x.r["worker_agent"] and not x.st(I).get("pilot_step"), "pilot_after_live_fails 0 switches the step off")
    x.done()

    x = rig(pilot_after_live_fails=3)
    end(x)
    z = end(x)
    ok(z[3] == x.r["worker_agent"], "at 3, two live endings are not yet a step")
    z = end(x)
    ok(z[3] == x.r["pilot_agent"], "at 3, the third is")
    x.done()


def main():
    ok(SR.RULES.get("pilot_after_live_fails") == 2, "the shipped rules call a pilot on the second live ending")
    t_step()
    t_finish_ends_it()
    t_attributed_and_off()
    print("FAILED: %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
