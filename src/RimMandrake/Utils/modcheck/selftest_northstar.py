#!/usr/bin/env python3
"""Selftest for the north-star / visual-floor / judge machinery.

Owner rulings 2026-09-15 (design/RimMandrake/north_star_validation_spec.md).
Deterministic and offline: the judge is exercised through its `runner=`
injection point, so this never shells out to `claude -p` and never needs the
game, the bridge or a network.

Run: python3 src/RimMandrake/Utils/modcheck/selftest_northstar.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import floor          # noqa: E402
import judge          # noqa: E402
import northstar      # noqa: E402

FAILED = []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    if not cond:
        FAILED.append(label)


WALK = """\
# Demo — validation walk
subject: src/RimMandrake/Demo

## must be true
- something mechanical

## north star
state: %s
validated-hash: %s

### the experience  (OWNER'S WORDS)
It should feel like a hole.

### must show
- [ ] `reads_as_hole` — reads as a dark hole at play zoom
- [ ] `occupant_below_floor` — a captured pawn is not drawn at floor level

## anti-guessing notes
- none
"""


def write_walk(tmp, state="DRAFT", hash_=""):
    d = os.path.join(tmp, "design", "validation_walks", "RimMandrake")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "Demo.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(WALK % (state, hash_))
    return p


# --------------------------------------------------------------- parsing
def test_parse_and_ids():
    print("--- must-show ids parse out of the section ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp)
        ns = northstar.parse(p)
        ok(ns["present"], "section is found")
        ok(ns["must_show"] == ["reads_as_hole", "occupant_below_floor"],
           "both ids parsed, in file order")
        ok(ns["state"] == northstar.DRAFT, "an unvalidated section is DRAFT")
        ok(northstar.bar_for(p) == [],
           "a DRAFT section binds NOTHING -- cannot fail or green a mod")


def test_missing_section_is_todays_behaviour():
    print("--- a walk with no north star behaves exactly as before ---")
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "design", "validation_walks", "RimMandrake")
        os.makedirs(d)
        p = os.path.join(d, "Bare.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# Bare\n\n## must be true\n- x\n")
        ns = northstar.parse(p)
        ok(not ns["present"], "absent section reported absent")
        ok(ns["must_show"] == [] and northstar.bar_for(p) == [],
           "no visual bar, so the mod is unaffected by this system")


# ------------------------------------------------------ the validation gate
def test_validation_and_tamper_reversion():
    print("--- validating records a hash; ANY later edit reverts to DRAFT ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp)
        written = northstar.record_validation(p)
        ns = northstar.parse(p)
        ok(ns["state"] == northstar.VALIDATED, "validated after recording")
        ok(ns["recorded_hash"] == written == ns["current_hash"],
           "recorded hash matches the section on disk")
        ok(northstar.bar_for(p) == ["reads_as_hole", "occupant_below_floor"],
           "a VALIDATED section now BINDS both ids")

        # An agent edits a must-show line after he validated it.
        with open(p, "r", encoding="utf-8") as fh:
            text = fh.read()
        text = text.replace("reads as a dark hole at play zoom",
                            "reads as a hole, probably")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)

        ns = northstar.parse(p)
        ok(ns["state"] == northstar.DRAFT,
           "editing a validated line reverts the section to DRAFT")
        ok("edited since validation" in ns["reason"], "and says why")
        ok(northstar.bar_for(p) == [],
           "so it binds nothing until he validates again -- his judgement "
           "cannot be silently rewritten")


def test_declared_validated_without_hash_is_draft():
    print("--- claiming VALIDATED without a hash does not work ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp, state="VALIDATED", hash_="")
        ns = northstar.parse(p)
        ok(ns["state"] == northstar.DRAFT,
           "hand-written `state: VALIDATED` with no hash stays DRAFT")
        p2 = write_walk(tmp, state="VALIDATED", hash_="deadbeef" * 8)
        ns2 = northstar.parse(p2)
        ok(ns2["state"] == northstar.DRAFT, "a wrong hash stays DRAFT too")


def test_whitespace_reflow_does_not_invalidate():
    print("--- a reflow that changes no words keeps validation ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp)
        northstar.record_validation(p)
        with open(p, "r", encoding="utf-8") as fh:
            text = fh.read()
        # Trailing spaces and an extra blank line: no claim changed.
        text = text.replace("### must show", "### must show   \n")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        ok(northstar.parse(p)["state"] == northstar.VALIDATED,
           "cosmetic whitespace does not cost him a re-validation")


# --------------------------------------------------------- the visual floor
def test_visual_floor():
    print("--- uncovered EXPERIENCE is as fatal as an uncovered toggle ---")
    ids = ["reads_as_hole", "occupant_below_floor"]
    comps = [{"toggle": "pitsEnabled", "beyond_toggle": False,
              "shows": ["reads_as_hole"]}]
    ok(floor.uncovered_shows(ids, comps) == ["occupant_below_floor"],
       "a validated line no component claims is reported uncovered")
    comps.append({"toggle": None, "beyond_toggle": True,
                  "shows": ["occupant_below_floor"]})
    ok(floor.uncovered_shows(ids, comps) == [], "covered once claimed")
    ok(floor.uncovered_shows([], comps) == [],
       "no validated ids means no visual floor -- today's behaviour")


def test_orphan_shows_is_a_lint_error():
    print("--- claiming an id nobody asked for is caught ---")
    comps = [{"shows": ["reads_as_hole", "typo_id"]}]
    ok(floor.orphan_shows(["reads_as_hole"], comps) == ["typo_id"],
       "an id absent from the checklist is reported as orphaned")
    ok(floor.uncovered(["t1"], [{"toggle": None, "beyond_toggle": True}]) == ["t1"],
       "the original toggle floor still behaves as before")


# ---------------------------------------------------------------- the judge
def test_judge_parses_and_never_guesses():
    print("--- judge verdicts: parsing, and what is NOT a pass ---")
    img = None
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        img = fh.name
    try:
        text = {"reads_as_hole": "reads as a dark hole"}
        comp = {"name": "c", "shows": ["reads_as_hole"], "screenshots": [img]}

        r = judge.judge_component(
            comp, text,
            runner=lambda p: (True, '{"result": "{\\"verdict\\":\\"YES\\",\\"why\\":\\"it is a hole\\"}"}'))
        ok(r[0]["verdict"] == judge.YES, "a YES inside claude's JSON envelope parses")
        ok(judge.visual_all_green(r), "all-YES is green")

        r = judge.judge_component(
            comp, text,
            runner=lambda p: (True, '{"verdict":"NO","why":"an icon"}'))
        ok(r[0]["verdict"] == judge.NO, "bare JSON parses too")
        ok(not judge.visual_all_green(r), "a NO is not green")

        r = judge.judge_component(comp, text,
                                  runner=lambda p: (True, "I think it looks fine!"))
        ok(r[0]["verdict"] == judge.UNJUDGEABLE,
           "prose with no JSON is UNJUDGEABLE, never a pass")
        ok(not judge.visual_all_green(r), "UNJUDGEABLE is NOT green")

        r = judge.judge_component(comp, text,
                                  runner=lambda p: (False, "claude not found"))
        ok(r[0]["verdict"] == judge.UNJUDGEABLE and "could not run" in r[0]["why"],
           "a BROKEN judge reports itself broken and never fabricates a verdict")

        # Claims something, captured nothing.
        r = judge.judge_component({"name": "c", "shows": ["reads_as_hole"],
                                   "screenshots": []}, text,
                                  runner=lambda p: (True, '{"verdict":"YES","why":"x"}'))
        ok(r[0]["verdict"] == judge.UNJUDGEABLE,
           "claiming a visual line with no screenshot cannot pass")

        # Claims an id the checklist does not define.
        r = judge.judge_component({"name": "c", "shows": ["ghost"],
                                   "screenshots": [img]}, text,
                                  runner=lambda p: (True, '{"verdict":"YES","why":"x"}'))
        ok(r[0]["verdict"] == judge.UNJUDGEABLE and "not in the validated" in r[0]["why"],
           "an orphaned claim cannot pass")
    finally:
        os.unlink(img)


def test_judge_run_skips_unclaimed_components():
    print("--- a mod with no validated checklist is untouched ---")
    summary = {"chains": [{"components": [
        {"name": "a", "verdict": "PASS", "screenshots": ["x.png"]},
        {"name": "b", "verdict": "PASS", "screenshots": [], "shows": []},
    ]}]}
    res = judge.judge_run(summary, {}, runner=lambda p: (True, "{}"))
    ok(res == [], "components without `shows` are not judged at all")
    ok("visual" not in summary["chains"][0]["components"][0],
       "and are not annotated -- exactly pre-2026-09-15 behaviour")


def main():
    for t in (test_parse_and_ids,
              test_missing_section_is_todays_behaviour,
              test_validation_and_tamper_reversion,
              test_declared_validated_without_hash_is_draft,
              test_whitespace_reflow_does_not_invalidate,
              test_visual_floor,
              test_orphan_shows_is_a_lint_error,
              test_judge_parses_and_never_guesses,
              test_judge_run_skips_unclaimed_components):
        t()
    print()
    if FAILED:
        print("%d FAILED:" % len(FAILED))
        for f in FAILED:
            print("  -", f)
        return 1
    print("all north-star machinery checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
