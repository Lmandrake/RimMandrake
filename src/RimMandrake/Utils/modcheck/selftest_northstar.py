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
import runner         # noqa: E402
import status         # noqa: E402
import suite as suite_mod  # noqa: E402

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


def test_zero_bar_section_cannot_be_validated():
    print("--- a present but misformatted section REFUSES validation ---")
    import contextlib
    import io

    import cli

    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "design", "validation_walks", "RimMandrake")
        os.makedirs(d)
        p = os.path.join(d, "Misformatted.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# Misformatted\n\n## north star\nstate: DRAFT\n"
                     "validated-hash:\n\n### must show\n"
                     "* not_the_bar_format - a bullet, not `- [ ] `id``\n")
        ns = northstar.parse(p)
        ok(ns["present"], "the section IS present -- which is why the old "
                          "`not present` guard let this through")
        ok(ns["must_show"] == [] and ns["cannot_show"] == [],
           "yet it parses to ZERO bars")

        real = northstar.find_walk
        northstar.find_walk = lambda root, mod: p
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli._validate("Misformatted", "yes go ahead")
            out = buf.getvalue()
        finally:
            northstar.find_walk = real

        ok(rc == 2, "validate REFUSES (rc=2) even with --owner-said")
        ok("REFUSED" in out and "ZERO bars" in out,
           "and says why, naming the zero")
        ok(northstar.parse(p)["state"] == northstar.DRAFT,
           "nothing was written -- the walk is still DRAFT, so the mod keeps "
           "being refused instead of silently greening")


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


# --------------------------------------------- the two checklists stay apart
CANNOT_WALK = """\
# Demo — validation walk

## north star
state: DRAFT
validated-hash:

### the experience  (OWNER'S WORDS)
It should feel like a hole.

- [ ] `not_a_claim` — a bullet in his prose is not a checklist line

### must show
- [ ] `reads_as_hole` — reads as a dark hole at play zoom, with its label
      hidden and no icon on the floor

### cannot show
- [ ] `snared_standing` — a pawn snared upright on a labelled tile

## anti-guessing notes
- none
"""


def _cannot_walk(tmp):
    d = os.path.join(tmp, "design", "validation_walks", "RimMandrake")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "Cannot.md")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(CANNOT_WALK)
    return p


def test_cannot_show_is_not_part_of_the_floor():
    print("--- `cannot show` is a separate checklist, not a must-show ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = _cannot_walk(tmp)
        ns = northstar.parse(p)
        ok(ns["must_show"] == ["reads_as_hole"],
           "only `### must show` lines are must-shows")
        ok(ns["cannot_show"] == ["snared_standing"],
           "`### cannot show` parses into its own list")
        ok("not_a_claim" not in ns["must_show"] + ns["cannot_show"],
           "a bullet under his prose is not silently promoted to a claim")
        ok(ns["must_show_text"]["reads_as_hole"].endswith("no icon on the floor"),
           "prose is joined across the wrapped continuation line")
        northstar.record_validation(p)
        ok(northstar.bar_for(p) == ["reads_as_hole"],
           "the FLOOR is must-show only -- no component is obliged to "
           "photograph a defect he would reject")
        must, cannot = northstar.text_for(p)
        ok(list(must) == ["reads_as_hole"] and list(cannot) == ["snared_standing"],
           "the judge is handed the two polarities separately")


def test_cannot_show_verdict_is_inverted():
    print("--- a YES on a `cannot show` line FAILS the mod ---")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        img = fh.name
    try:
        comp = {"name": "c", "shows": ["snared_standing"], "screenshots": [img]}
        cannot = {"snared_standing": "a pawn snared upright on a labelled tile"}

        r = judge.judge_component(comp, {}, cannot,
                                  runner=lambda p: (True, '{"verdict":"YES","why":"upright"}'))
        ok(r[0]["polarity"] == judge.CANNOT and not r[0]["pass"],
           "the defect IS on screen -- YES means red")
        ok(not judge.visual_all_green(r), "and the run is not green")

        r = judge.judge_component(comp, {}, cannot,
                                  runner=lambda p: (True, '{"verdict":"NO","why":"in a hole"}'))
        ok(r[0]["pass"] and judge.visual_all_green(r),
           "the defect is absent -- NO clears the line")

        r = judge.judge_component(comp, {}, cannot,
                                  runner=lambda p: (True, "no idea"))
        ok(r[0]["verdict"] == judge.UNJUDGEABLE and not r[0]["pass"],
           "UNJUDGEABLE clears neither polarity")
    finally:
        os.unlink(img)


# ------------------------------------------------------ runner-level wiring
def _suite_with(shows_per_component):
    """A real `Suite` whose components carry `shows=`, declared offline through
    the same no-op probe the floor check uses -- no session, no game."""
    s = suite_mod.Suite("Demo")

    def make(i, shows):
        def chain(t):
            with t.component("c%d" % i, beyond_toggle=True, shows=shows):
                t.screenshot()
        return chain

    for i, shows in enumerate(shows_per_component):
        s.chain("chain%d" % i)(make(i, shows))
    return s


def test_declared_components_carry_shows():
    print("--- the floor can be answered BEFORE a run ---")
    s = _suite_with([["reads_as_hole"]])
    declared = s.components_declared()
    ok(declared and declared[0].get("shows") == ["reads_as_hole"],
       "components_declared() reports `shows`, offline")


def test_runner_refuses_an_unclaimed_validated_line():
    print("--- REFUSED: a validated line no component claims ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp)
        northstar.record_validation(p)
        ns = northstar.parse(p)

        fl = runner.visual_floor(_suite_with([["reads_as_hole"]]), ns)
        ok(fl["uncovered"] == ["occupant_below_floor"], "names the uncovered id")
        ok("occupant_below_floor" in runner.refusal(fl),
           "and that is a refusal, not a warning")

        fl = runner.visual_floor(
            _suite_with([["reads_as_hole"], ["occupant_below_floor"]]), ns)
        ok(runner.refusal(fl) == "", "fully claimed: nothing refuses the run")

        fl = runner.visual_floor(
            _suite_with([["reads_as_hole", "occupant_below_floor", "typo_id"]]), ns)
        ok("typo_id" in runner.refusal(fl),
           "an orphaned `shows=` refuses too -- claiming what nobody asked for")


def test_a_draft_checklist_binds_nothing_at_runner_level():
    print("--- a DRAFT checklist cannot refuse a mod either ---")
    with tempfile.TemporaryDirectory() as tmp:
        ns = northstar.parse(write_walk(tmp))          # DRAFT
        fl = runner.visual_floor(_suite_with([[]]), ns)
        ok(fl == {"bar": [], "uncovered": [], "orphans": []},
           "no bar, no floor, no refusal -- today's behaviour for 17 of 18 mods")


def _summary(shows, verdict="PASS", shots=("x.png",)):
    return {"chains": [{"name": "ch", "components": [
        {"name": "c", "verdict": verdict, "shows": list(shows),
         "screenshots": list(shots)}]}], "all_green": verdict == "PASS",
        "findings": []}


def test_state_green_plus_judge_no_is_not_green():
    print("--- both halves are required, and neither substitutes ---")
    text = {"reads_as_hole": "reads as a dark hole"}
    yes = lambda p: (True, '{"verdict":"YES","why":"a hole"}')  # noqa: E731
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        img = fh.name
    try:
        s = _summary(["reads_as_hole"], shots=(img,))
        runner.apply_judgement(s, text, {},
                               judge_runner=lambda p: (True, '{"verdict":"NO","why":"an icon"}'))
        ok(s["state_all_green"] and not s["visual_all_green"] and not s["all_green"],
           "state passed, the judge said NO, the mod is RED -- the pit's exact case")

        s = _summary(["reads_as_hole"], shots=(img,))
        runner.apply_judgement(s, text, {},
                               judge_runner=lambda p: (True, '{"verdict":"UNJUDGEABLE","why":"wrong zoom"}'))
        ok(not s["all_green"], "UNJUDGEABLE is not a pass at runner level either")

        s = _summary(["reads_as_hole"], shots=(img,))
        runner.apply_judgement(s, text, {}, judge_runner=yes)
        ok(s["all_green"] and s["visual_all_green"], "both halves green is GREEN")

        s = _summary(["reads_as_hole"], verdict="FAIL", shots=(img,))
        runner.apply_judgement(s, text, {}, judge_runner=yes)
        ok(not s["all_green"],
           "a judge YES cannot rescue a failed state assertion")

        # The evidence the sheet points at must actually be on disk. Caught this
        # selftest's own first fixture, which claimed a screenshot named x.png.
        s = _summary(["reads_as_hole"], shots=("/nonexistent/x.png",))
        runner.apply_judgement(s, text, {}, judge_runner=yes)
        ok(not s["all_green"] and s["visual"][0]["verdict"] == judge.UNJUDGEABLE,
           "a claimed screenshot that is not on disk cannot pass, even on a YES")

        s = _summary([])
        runner.apply_judgement(s, {}, {}, judge_runner=lambda p: (True, "{}"))
        ok(s["all_green"] and s["visual"] == [],
           "a mod claiming nothing judges nothing and keeps its state verdict")
    finally:
        os.unlink(img)


# ------------------------------------------------------- what GREEN now means
def test_green_definition():
    print("--- the five conditions of GREEN (spec section 5) ---")
    with tempfile.TemporaryDirectory() as tmp:
        p = write_walk(tmp)                            # DRAFT
        ok(status.verdict_for(True, p) == "DRAFT-CHECKLIST",
           "an all-green run against a DRAFT bar is NOT green")
        northstar.record_validation(p)
        ok(status.verdict_for(True, p) == "PENDING-OWNER-REVIEW",
           "validated, but his own eyes have not been on a sheet yet")
        ok(status.verdict_for(True, p, reviewed=True) == "GREEN",
           "reviewed once -- now GREEN")
        ok(status.verdict_for(False, p, reviewed=True) == "RED",
           "a failed half is RED regardless of review")
        ok(status.verdict_for(True, p, refused="uncovered: x") == "REFUSED",
           "a refused run reports REFUSED, not RED -- it never ran")
        ok(status.verdict_for(True, None) == "GREEN",
           "a mod with no walk greens exactly as it did before this system")

        bare = os.path.join(tmp, "Bare.md")
        with open(bare, "w", encoding="utf-8") as fh:
            fh.write("# Bare\n\n## must be true\n- x\n")
        ok(status.verdict_for(True, bare) == "GREEN",
           "and so does a walk with no `## north star` section")


def test_record_run_writes_the_gated_verdict():
    print("--- the registry cannot record GREEN past the gate ---")
    with tempfile.TemporaryDirectory() as tmp:
        walk = write_walk(tmp)
        mod_dir = os.path.join(tmp, "mod")
        os.makedirs(mod_dir)
        with open(os.path.join(mod_dir, "About.xml"), "w") as fh:
            fh.write("<x/>")

        # Redirect the registry: this test must never touch the real one.
        keep = (status.LOG_PATH, status.LOCK_PATH)
        status.LOG_PATH = os.path.join(tmp, "modcheck_status.json")
        status.LOCK_PATH = status.LOG_PATH + ".lock"
        try:
            e = status.record_run("Demo", mod_dir, "r1", True, walk=walk)
            ok(e["status"] == "DRAFT-CHECKLIST",
               "an all-green run against a DRAFT checklist is not written GREEN")

            northstar.record_validation(walk)
            e = status.record_run("Demo", mod_dir, "r2", True, walk=walk)
            ok(e["status"] == "PENDING-OWNER-REVIEW",
               "validated, and still not green until he has read a sheet")

            e = status.record_owner_review("Demo", "yes, that's a pit", "r2")
            ok(e["status"] == "GREEN" and e["owner_review"]["run_id"] == "r2",
               "his review promotes it and records WHICH run he read")

            e = status.record_run("Demo", mod_dir, "r3", True, walk=walk)
            ok(e["status"] == "GREEN" and e["owner_review"]["run_id"] == "r2",
               "later runs green directly -- his review is required once, and "
               "survives a re-run naming the sheet he actually saw")

            e = status.record_run("Demo", mod_dir, "r4", False, walk=walk,
                                  refused="uncovered: occupant_below_floor")
            ok(e["status"] == "REFUSED" and e["refused"],
               "a refused run is recorded as REFUSED with its reason")
            ok(status.check("Demo", mod_dir).startswith("REFUSED"),
               "and `check` reports it as not-green, naming why")
        finally:
            status.LOG_PATH, status.LOCK_PATH = keep


def main():
    for t in (test_parse_and_ids,
              test_missing_section_is_todays_behaviour,
              test_zero_bar_section_cannot_be_validated,
              test_validation_and_tamper_reversion,
              test_declared_validated_without_hash_is_draft,
              test_whitespace_reflow_does_not_invalidate,
              test_visual_floor,
              test_orphan_shows_is_a_lint_error,
              test_judge_parses_and_never_guesses,
              test_judge_run_skips_unclaimed_components,
              test_cannot_show_is_not_part_of_the_floor,
              test_cannot_show_verdict_is_inverted,
              test_declared_components_carry_shows,
              test_runner_refuses_an_unclaimed_validated_line,
              test_a_draft_checklist_binds_nothing_at_runner_level,
              test_state_green_plus_judge_no_is_not_green,
              test_green_definition,
              test_record_run_writes_the_gated_verdict):
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
