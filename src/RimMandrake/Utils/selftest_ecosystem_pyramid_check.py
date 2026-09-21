#!/usr/bin/env python3
"""selftest_ecosystem_pyramid_check.py — proves ecosystem_pyramid_check.py's
verdict logic, independent of whatever the live rosters currently look like.

Two halves, same shape as this repo's other db-backed selftests
(selftest_deployed_biome_refs.py):

  1. PURE LOGIC on synthetic (animal, commonality) lists — runs anywhere, no
     game, no dump, no network. This is the half that actually protects the
     law: a live-only test would pass today (26/28 PASS) and keep passing
     even if someone broke the small/large banding, because nothing forces
     the live rosters back through a known-bad shape.
  2. A LIVE SMOKE RUN against the real defs.sqlite, structure-only (never a
     fixed PASS/FAIL table — rosters legitimately drift). Prints the project's
     UNMEASURED phrase and exits non-zero-but-not-FAIL when the dump is
     unreachable (e.g. from the Mac, where DUMP_ROOT is a Windows path) —
     `run_selftests.py` reads that phrase, not a bare failure.

Run: bare `python3 selftest_ecosystem_pyramid_check.py`, from anywhere.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ecosystem_pyramid_check as epc                 # noqa: E402

UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


def t_all_small_passes_at_100pct():
    v = epc.evaluate([("A", 1.0), ("B", 0.5)], {"A": 0.2, "B": 0.9}, 50.0)
    assert v["verdict"] == "PASS", v
    assert close(v["small_pct"], 100.0), v


def t_all_large_fails_at_0pct_with_correct_shortfall():
    v = epc.evaluate([("A", 1.0), ("B", 2.0)], {"A": 1.0, "B": 3.5}, 50.0)
    assert v["verdict"] == "FAIL", v
    assert close(v["small_pct"], 0.0), v
    # large_c=3.0, small_c=0 -> at t=0.5 required small_c == large_c == 3.0
    assert close(v["shortfall"], 3.0), v


def t_exactly_at_floor_passes_ge_not_gt():
    # small=50, large=50 -> exactly 50.0% and the law is ">= 50%".
    v = epc.evaluate([("A", 50.0), ("B", 50.0)], {"A": 0.3, "B": 2.0}, 50.0)
    assert v["verdict"] == "PASS", v
    assert close(v["small_pct"], 50.0), v


def t_just_under_floor_fails_with_matching_shortfall():
    # small=40, large=60 -> 40%. At t=0.5, required small == large == 60,
    # so shortfall == 20 (60 - 40). Verify adding it lands exactly on 50%.
    v = epc.evaluate([("A", 40.0), ("B", 60.0)], {"A": 0.5, "B": 5.0}, 50.0)
    assert v["verdict"] == "FAIL", v
    assert close(v["small_pct"], 40.0), v
    assert close(v["shortfall"], 20.0), v
    lifted = epc.evaluate([("A", 40.0 + v["shortfall"]), ("B", 60.0)],
                          {"A": 0.5, "B": 5.0}, 50.0)
    assert lifted["verdict"] == "PASS", lifted
    assert close(lifted["small_pct"], 50.0), lifted


def t_unresolved_defnames_excluded_from_both_bands():
    # A ghost defName (no race.baseBodySize known) must NOT be guessed into
    # either band and must NOT enter the commonality totals at all — guessing
    # here is exactly what this codebase's "never guess a defName" rule bans,
    # and it would silently mis-grade a roster carrying a cut/mistyped animal.
    v = epc.evaluate([("Known", 1.0), ("Ghost", 99.0)], {"Known": 0.4}, 50.0)
    assert v["verdict"] == "PASS", v
    assert close(v["small_pct"], 100.0), v          # Ghost's 99.0 must not count
    assert [a for a, _ in v["unresolved"]] == ["Ghost"], v


def t_empty_roster_is_its_own_verdict_not_a_silent_pass_or_skip():
    v = epc.evaluate([], {}, 50.0)
    assert v["verdict"] == "EMPTY", v
    assert v["small_pct"] is None, v


def t_all_unresolved_roster_is_also_empty_not_a_silent_pass():
    # every entry ghosts out -> total commonality is 0, same failure shape as
    # a genuinely empty roster, and must be reported the same loud way.
    v = epc.evaluate([("Ghost1", 1.0), ("Ghost2", 2.0)], {}, 50.0)
    assert v["verdict"] == "EMPTY", v
    assert len(v["unresolved"]) == 2, v


def t_threshold_pct_comes_from_canon_yml_not_hardcoded():
    # Integration, deliberately: this is the one check that would catch a
    # future re-ruling landing in canon.yml without this checker noticing.
    pct = epc.load_threshold_pct()
    assert pct == 50.0, ("canon.yml ecosystem_laws.food_pyramid.threshold_pct "
                          "read as %r, expected 50.0 — either canon.yml or "
                          "this checker's assumption is stale" % pct)


UNIT_TESTS = [
    t_all_small_passes_at_100pct,
    t_all_large_fails_at_0pct_with_correct_shortfall,
    t_exactly_at_floor_passes_ge_not_gt,
    t_just_under_floor_fails_with_matching_shortfall,
    t_unresolved_defnames_excluded_from_both_bands,
    t_empty_roster_is_its_own_verdict_not_a_silent_pass_or_skip,
    t_all_unresolved_roster_is_also_empty_not_a_silent_pass,
    t_threshold_pct_comes_from_canon_yml_not_hardcoded,
]


def main():
    broken = []
    for fn in UNIT_TESTS:
        try:
            fn()
        except AssertionError as exc:
            broken.append("%s: %s" % (fn.__name__, exc))
        except Exception as exc:                       # noqa: BLE001
            broken.append("%s: %r (unexpected exception type)" % (fn.__name__, exc))

    if broken:
        print("%d of %d unit check(s) FAILED:" % (len(broken), len(UNIT_TESTS)))
        for line in broken:
            print("  FAIL " + line)
        return 1

    print("%d/%d pure-logic unit checks passed." % (len(UNIT_TESTS), len(UNIT_TESTS)))

    # Live smoke run — structure only, never a pinned PASS/FAIL table.
    try:
        verdicts, threshold_pct = epc.run()
    except RuntimeError as exc:
        msg = str(exc)
        if msg.startswith("UNMEASURED"):
            print(msg)
            print(UNMEASURED_PHRASE)
            return 2
        print("FAIL live run raised an unexpected error: %s" % msg)
        return 1

    if not verdicts:
        print("FAIL live run returned zero biome verdicts — owned_biome_rosters "
              "found nothing, which should have raised UNMEASURED instead of "
              "returning an empty, falsely-clean list.")
        return 1
    bad_shape = [v for v in verdicts if v.verdict not in ("PASS", "FAIL", "EMPTY")]
    if bad_shape:
        print("FAIL live run produced an unrecognised verdict: %r" % bad_shape)
        return 1
    for v in verdicts:
        if v.verdict == "EMPTY":
            continue
        recomputed_pass = v.small_pct >= threshold_pct
        if recomputed_pass != (v.verdict == "PASS"):
            print("FAIL %s: verdict %s disagrees with its own small_pct %.2f "
                  "against floor %.2f" % (v.biome, v.verdict, v.small_pct,
                                          threshold_pct))
            return 1

    print("live smoke run OK: %d owned biome roster(s) checked against a "
          "%.0f%% floor (%d PASS, %d FAIL, %d EMPTY)."
          % (len(verdicts), threshold_pct,
             sum(v.verdict == "PASS" for v in verdicts),
             sum(v.verdict == "FAIL" for v in verdicts),
             sum(v.verdict == "EMPTY" for v in verdicts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
