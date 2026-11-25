#!/usr/bin/env python3
"""coverage_calibration.py - the coverage judge's planted cases (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS).

A gate is only a gate if its judge is trustworthy both ways (his card 2026-11-14, spec Q7 "Keep both"). This is the
`model_check` of the `coverage_judge` row in infrastructure/state/judge_calibration.json: it stages small planted concepts
in a temp tree (the real role files copied in), puts each to the coverage judge with its real prompt and schema
(coverage_judge.prompt, SCHEMA, MODEL), and writes one result row per case to $RM_CALIBRATION_RESULTS:

  good_lanterns           every capability and leaf has a contract scene and the flagship showcase is his pick ->
                          must pass. It also plants the noise kinds an independent read found in Pyrelands round 6
                          (g17, g18: a gap that asks for documentation or another showcase and names no wrong behaviour
                          a check would accept): the sheet does not restate each scene's thresholds and there is one
                          showcase only. A judge that refuses on those is not calibrated.
  good_lanterns_tuning    good_lanterns plus the pedantry the Contagion judge refused on (owner 2026-11-16, bar_rule.py):
                          an inventory row that pins a burn rate, a MarketValue and three graphic variants no scene
                          reads -> must pass: a judge that blocks on a tuning number or a variant count is not calibrated
  good_lanterns_no_reset  good_lanterns whose scenes put nothing back: no restore step, the burnt-out rooms stay on the
                          map -> must pass: resetting a test scene is harness housekeeping (save before, reload after),
                          never a coverage gap, Problem or Polish finding (owner 2026-11-17, standing_rulings.md)
  bad_leaf_no_scene       the oil leaf and its capability have no scene -> must be refused
  bad_scene_no_control    the light scene has no control and no asserted start -> must be refused
  bad_conflict_routing    his own words twice, with no precedence between them: "go out when it runs dry" (oil_out) and
                          "never goes dark, oil or none" (never_dark) -> must be refused AND routed to criteria review (a
                          flawed or unattainable criterion, the neutral fixer) or to his answer (return_to 2), never to
                          the Designer's rework. (First plant, 2026-11-17 run at 5f9fdb20: never_dark had no words of his,
                          so his words took precedence and the judge rightly sent the Designer to fix that leaf.)
  bad_mixed_row           an inventory row pinning numbers (3 oil, 120 ticks) beside an experience no scene tests (a pawn
                          refuels the lantern) -> must be refused on the experience; the number alone is waived
  bad_late_serious        a round-2 look after round 1 refused sc_light's missing control: the repair added it, and the
                          same repair rewrote sc_oil_out's expect into the leaf's own red (lit at zero oil) -> the new gap
                          quotes a passage a repair changed and must block, a serious Problem the second reader confirms
                          (the owner's trial of 2026-11-17, design/specs/2026-11-17-judge-flaws-not-polish/
                          7_same_problem_rule.md rule 4; it was an unchanged-material late gap, now advisory by that rule)
  good_round2_repaired    a round-2 look after round 1 refused the light scene's missing control, now repaired -> must
                          pass: later rounds only check named repairs (owner by card 2026-11-16, point 14)
  good_pyrelands_look8    Pyrelands look 8 replayed: the concept as that look judged it (commit PYRELANDS_LOOK8_AT) under
                          look 7's refusing verdict, judged as production judged it (the delta) -> must pass: its three
                          carried gaps were repaired and no claim form named them (owner by card 2026-11-17, rule 2)
  bad_fire_never_touched  his promise that a lantern knocked onto straw never lights it, tested only by a scene whose
                          lantern never touches straw -> must be refused: nobody would notice the promise broken (rule 1)
  good_one_kind_enough    his promise that a lit lantern keeps the beasts away, tested with one animal kind and a control
                          -> must pass: "test it against every roster kind" is advice, "test more cases" (rule 1)

Every refusal is routed as production routes it (owner by card 2026-11-16 on GPT's point 17, "Calibration must check
where a refusal goes"): the gaps the bar rule lets block go to the real second reader (coverage_judge.llm_reader), and
a refuse case counts as the planted refusal only when its route is the planted one (`outcome`): `designer` (a sound
criterion), `criteria` (the reader or the judge calls it flawed or unattainable) or `late` (a late gap the reader
confirmed serious). It spends (one Opus judge per case, each capped at CASE_BUDGET_USD, plus one reader per refusal): it runs only from
`refusal_contract.py calibrate --model coverage_judge`, never on a schedule.

    python3 src/RimMandrake/rimflow/coverage_calibration.py run        judge every case, print one line each
    python3 src/RimMandrake/rimflow/coverage_calibration.py stage <dir>  write the planted concepts there, judge none
"""
import effort as EF  # the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_judge as CJ  # noqa: E402
import concept_tree as CT  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ROLES = ("src/RimMandrake/rimflow/roles/designer_scene_contract.md", "src/RimMandrake/rimflow/roles/designer_lock.md")
CASE_BUDGET_USD = 1.25
CASE_BUDGET_USD_BIG = 4   # the Pyrelands replay: a real concept, as production's judge cap (BUDGET_USD 8) halved
PYRELANDS_LOOK8_AT = "e9b9067df1~1"   # look 8's input: look 7's verdict on file and the Designer's changes since
PYRELANDS = "design/concepts/Pyrelands"
PYRELANDS_FILES = ("sheet.md", "tree.json", "scenes.json", "floor.json", "exam.json", "record.json",
                   "coverage_verdict.json", "coverage_fixes.json", "stage.json")
# budget: danger=a judge call that never returns holds the calibration; longest=166s (119 case sessions, agent transcripts, 14
# budget: days to 2026-11-24)
CASE_TIMEOUT_S = 1800

LEAF = {"by": "concept", "root": ["lantern_root"], "leaf_kind": "experience", "clause_kind": "preserve",
        "tier_proposed": "live", "owner_part": "lantern_root"}
BASE = {
    "sheet.md": "# Lanterns: a hanging lantern lights a small room and needs oil\n\n## his words\n"
                "- 2026-11-01: \"A lantern should light the room around it, and go out when it runs dry.\" OWNER:1\n"
                "- 2026-11-02, the face: \"Show me a lantern lighting a dark room and then going out.\" OWNER:2\n\n"
                "## does\n- [leaf:light] At night a lit lantern lights the cells around it\n"
                "- [leaf:oil_out] A lantern nobody refuels goes dark when its oil is gone\n\n"
                "## does not\n- No colour, no heat, no fire risk: a lantern is light and an oil counter only\n",
    "tree.json": {"schema_version": 1, "subject": "Lanterns", "kind": "mod", "authored_by": "concept",
                  "root_ref": "design/validation_walks/RimMandrake/Lanterns.md#north-star", "root_state": "VALIDATED",
                  "waived": [], "advisory": [], "exam_waived": None,
                  "leaves": [dict(LEAF, id="light",
                                  experience="At night the player sees the cells within two of a lit lantern lit",
                                  scenario="a dark roofed room at midnight, one fuelled lantern hung in its centre",
                                  false_pass=["light measured in daylight or from another lamp"],
                                  red="a lantern that reads lit and leaves its cells dark"),
                             dict(LEAF, id="oil_out",
                                  experience="A lantern left unfuelled goes dark once its last oil is burnt",
                                  scenario="a lit lantern with exactly one oil left, a day passing",
                                  false_pass=["a lantern that goes dark at dawn whatever its oil"],
                                  red="a lantern that burns forever on an empty tank")]},
    "record.json": {"mod": "Lanterns", "packageId": "mandrake.rm.lanterns", "scope": [],
                    "decisions": [{"id": "d_flagship", "kind": "ruling", "speaker": "owner", "source": "OWNER:2",
                                   "date": "2026-11-02", "what": "the flagship: a lantern lighting a dark room, then going "
                                   "out", "flagship": "lantern_night"}],
                    "asks": [],
                    "inventory": [{"id": "inv_light", "what": "A lit lantern raises light to at least 50% on every cell "
                                   "within 2 cells of it", "impl": "present", "impl_evidence": [
                                       "src/RimMandrake/Lanterns/Source/CompLanternGlow.cs"], "proof": "current",
                                   "scope": "approved", "source": ["OWNER:1"]},
                                  {"id": "inv_oil", "what": "A lit lantern burns one oil per day; at zero oil it goes "
                                   "dark", "impl": "present", "impl_evidence": [
                                       "src/RimMandrake/Lanterns/Source/CompLanternFuel.cs"], "proof": "current",
                                   "scope": "approved", "source": ["OWNER:1"]}]},
    "scenes.json": {"scenes": [
        {"id": "sc_light", "kind": "acceptance", "requirement": ["light"], "staged_by": "script",
         "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_light",
         "start": ["quicktest map at midnight, a 7x7 roofed room with no other light source: glow 0 on every room cell "
                   "(asserted)", "one lantern with 3 oil hung at the room's centre, unlit (asserted)"],
         "action": "light the lantern and wait 60 ticks",
         "expect": "glow is at least 50% on every cell within 2 cells of the lantern and at most 10% at 3 cells",
         "control": {"case": "the same room with the same lantern hung but holding 0 oil, ordered lit",
                     "expect": "glow stays 0 on every room cell",
                     "rules_out": "light from the room, the time of day or another source rather than the burning lantern"},
         "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"},
        {"id": "sc_oil_out", "kind": "acceptance", "requirement": ["oil_out"], "staged_by": "script",
         "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_oil_out",
         "start": ["the sc_light room, the lantern lit with exactly 1 oil (asserted)",
                   "a second room alike with a lantern lit with 2 oil (asserted)"],
         "action": "advance one day and one hour",
         "expect": "the first lantern holds 0 oil and its cells read glow 0",
         "control": {"case": "the second lantern, advanced the same day and hour",
                     "expect": "it holds 1 oil and its cells still read at least 50% within 2 cells",
                     "rules_out": "the lantern going dark from elapsed time or the day cycle rather than an empty tank"},
         "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"}],
        "showcases": [{"id": "lantern_night", "scenes": ["sc_light", "sc_oil_out"], "exercises": ["inv_light", "inv_oil"],
                       "source": ["OWNER:2"], "decision": "d_flagship"}],
        "coverage_rest": []},
    "floor.json": {"lines": {"log": {"status": "applicable"}, "mod_settings": {"status": "applicable"},
                             "flight": {"status": "not_applicable", "evidence": "a lantern does not fly"},
                             "biome_scope": {"status": "not_applicable", "evidence": "the mod adds no BiomeDef"}}},
    "exam.json": {"scenarios": [
        {"id": "e1", "text": "A lit lantern in a dark room leaves the cell next to it dark.", "expect": "reject: leaf light",
         "expect_source": "leaf:light"},
        {"id": "e2", "text": "A lantern with oil left goes dark at dawn.", "expect": "reject: leaf oil_out",
         "expect_source": "leaf:oil_out"}],
        "reader_verdicts": {"reader1": {"e1": {"verdict": "reject", "leaf": "light"},
                                        "e2": {"verdict": "reject", "leaf": "oil_out"}}}},
}


def _no_oil_scene(c):
    s = c["scenes.json"]
    s["scenes"] = [x for x in s["scenes"] if x["id"] != "sc_oil_out"]
    s["showcases"][0].update(scenes=["sc_light"], exercises=["inv_light"])


def _no_control(c):
    sc = c["scenes.json"]["scenes"][0]
    sc.pop("control")
    sc["start"] = ["quicktest map", "one lantern hung at the room's centre"]


def _tuning_bait(c):
    """The Contagion pedantry kinds (RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS): numbers and a variant count
    that a renormalization or a new art variant changes, read by no scene. None of them is a bar."""
    c["record.json"]["inventory"].append({
        "id": "inv_lantern_def", "what": "The lantern def: fuel burn rate 1.0 per day, MarketValue 12, Mass 1.5, and "
        "three graphic variants (Lantern_a, Lantern_b, Lantern_c, Graphic_Random)", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Defs/ThingDefs/Lantern.xml"], "proof": "current",
        "scope": "approved", "source": ["OWNER:1"]})
    c["scenes.json"]["coverage_rest"].append({
        "capability": "inv_lantern_def", "by": ["sc_light"],
        "why": "the lantern is drawn and lit in sc_light; its numbers and variants are tuning, not an experience"})


def _no_reset(c):
    """RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE's ruling (owner 2026-11-17): "We shouldn't be judging Test Reset
    as a mod deliverable." Each scene puts nothing back: the map is left as the scene ends."""
    for sc in c["scenes.json"]["scenes"]:
        sc["restore"] = "none: the scene puts nothing back; the quicktest map is left as the scene ends"


def _never_dark(c):
    """Two leaves that cannot both hold, each his words (GPT point 17, "a genuinely incompatible criterion set"):
    oil_out says an unfuelled lantern goes dark, never_dark says it never does. No precedence settles it, so no Designer
    rework can pass both: a correct refusal goes to criteria review or to him."""
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does", "\n- 2026-11-03: \"A hung lantern never goes dark, oil or none: nobody wants a dark room.\" "
        "OWNER:3\n\n## does", 1)
    c["record.json"]["inventory"].append({
        "id": "inv_never_dark", "what": "A hung lantern never goes dark, whether or not it holds oil", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternGlow.cs"], "proof": "current",
        "scope": "approved", "source": ["OWNER:3"]})
    c["tree.json"]["leaves"].append(dict(
        LEAF, id="never_dark", experience="A hung lantern never goes dark: its cells stay lit at every hour for as long "
        "as it hangs, whether or not it holds any oil", scenario="a lit lantern with 0 oil, a day passing",
        source=["OWNER:3"],
        false_pass=["a lantern refuelled during the day"], red="a hung lantern whose cells go dark"))
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does not", "\n- [leaf:never_dark] A hung lantern never goes dark, oil or none\n\n## does not")
    c["scenes.json"]["scenes"].append({
        "id": "sc_never_dark", "kind": "acceptance", "requirement": ["never_dark"], "staged_by": "script",
        "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_never_dark",
        "start": ["the sc_light room, the lantern lit with 0 oil (asserted)"], "action": "advance one day",
        "expect": "the lantern's cells still read at least 50% within 2 cells",
        "control": {"case": "the same room with no lantern hung", "expect": "glow stays 0 on every room cell",
                    "rules_out": "light from the room rather than the lantern"},
        "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"})


def _refuel_row(c):
    """A mixed row (GPT point 17): an experience no scene tests (a pawn refuels a lantern) beside tuning numbers. The
    numbers are waived; the experience still blocks."""
    c["record.json"]["inventory"].append({
        "id": "inv_refuel", "what": "A pawn refuels a hung lantern from stockpiled oil, and the lantern lights again; "
        "each refuel adds 3 oil and takes 120 ticks", "impl": "present",
        "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternFuel.cs"], "proof": "current",
        "scope": "approved", "source": ["OWNER:1"]})


R1_JUDGE = "rm-coverage-judge-calibration-r1"


def _prior(gap, rows_ok):
    """A round-1 verdict that refused on `gap` and passed every other row (rows_ok: {id: scene})."""
    return {"verdict": "not_covered", "judge": R1_JUDGE, "round": 1, "gaps": [dict(gap, gid="g1", new_since="first")],
            "checklist": [{"id": i, "evidence": ["scenes.json", "tree.json"],
                           "parts": [{"what": "the %s experience" % i, "scene": sc, "ok": True}]}
                          for i, sc in rows_ok.items()]}


LIGHT_GAP = {"what": "sc_light has no control and its start asserts no dark", "where": "scenes.json sc_light",
             "ids": ["light", "inv_light"], "return_to": 3, "bar_kind": "experience", "severity": "problem",
             "evidence": ["scenes.json"], "observed": "sc_light has no `control`",
             "would_pass": "sc_light asserts a dark lamp-free room at midnight and a 0-oil control stays dark",
             "smallest_fix": {"what": "add a control and asserted start to sc_light", "attainable": "yes",
                              "cost": "edit"},
             "criterion_verdict": "sound", "criterion_why": "a lit room is checkable with a dark control"}


def _late_red(c):
    """Round 2 after round 1 refused sc_light's missing control (on BASE without it) and PASSED oil_out. The repair
    added sc_light's control and, in the same edit, rewrote sc_oil_out's expect into the leaf's own red (a lantern lit
    at zero oil): a passage a repair changed, and a Problem a player would reject."""
    sc = c["scenes.json"]["scenes"][1]
    sc["expect"] = "the first lantern holds 0 oil and its cells still read at least 50% within 2 cells"
    sc["control"]["expect"] = "it holds 1 oil and its cells still read at least 50% within 2 cells"
    c["coverage_verdict.json"] = _prior(LIGHT_GAP, {"oil_out": "sc_oil_out", "inv_oil": "sc_oil_out"})
    c["_before"] = _no_control   # the prior verdict's entry renderings are of BASE without sc_light's control


def _straw_unreached(c):
    """His promise that a knocked-over lantern never lights straw, proved by a scene whose lantern never touches
    straw: the test cannot fail, so nobody would notice the promise broken (rule 1, the fire-immunity kind)."""
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does", "\n- 2026-11-04: \"A lantern knocked onto a straw floor must never set it alight.\" OWNER:4"
        "\n\n## does", 1).replace("\n\n## does not", "\n- [leaf:straw_safe] A lantern knocked onto straw never "
                                   "lights it\n\n## does not", 1)
    c["record.json"]["inventory"].append({
        "id": "inv_straw", "what": "A lit lantern knocked onto a straw floor never sets the straw alight",
        "impl": "present", "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternFuel.cs"],
        "proof": "current", "scope": "approved", "source": ["OWNER:4"]})
    c["tree.json"]["leaves"].append(dict(
        LEAF, id="straw_safe", experience="A lit lantern knocked off its hook onto a straw floor lies there lit and "
        "the straw never catches", scenario="a lit lantern knocked onto straw", source=["OWNER:4"],
        false_pass=["a lantern that is never knocked down"], red="straw that catches under a fallen lantern"))
    c["scenes.json"]["scenes"].append({
        "id": "sc_straw_safe", "kind": "acceptance", "requirement": ["straw_safe"], "staged_by": "script",
        "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_straw_safe",
        "start": ["a stone-floored 7x7 room with no straw anywhere on the map (asserted)",
                  "one lit lantern with 3 oil hung at the room's centre (asserted)"],
        "action": "wait one day", "expect": "no fire anywhere on the map",
        "control": {"case": "the same room with the lantern unlit", "expect": "no fire anywhere on the map",
                    "rules_out": "fire from the room or the weather"},
        "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"})


def _one_kind(c):
    """His promise that a lit lantern keeps the beasts out of its light, tested with one animal kind and a control. A judge that
    wants every roster kind tried asks for "more cases": advice, never a refusal (rule 1)."""
    c["sheet.md"] = c["sheet.md"].replace(
        "\n\n## does", "\n- 2026-11-05: \"A lit lantern keeps the beasts out of its light at night.\" OWNER:5"
        "\n\n## does", 1).replace("\n\n## does not", "\n- [leaf:beasts_kept_off] Wild animals keep out of a lit "
                                   "lantern's light at night\n\n## does not", 1)
    c["record.json"]["inventory"].append({
        "id": "inv_beasts", "what": "A wild animal that would enter a lit lantern's 2-cell light at night turns away",
        "impl": "present", "impl_evidence": ["src/RimMandrake/Lanterns/Source/CompLanternGlow.cs"],
        "proof": "current", "scope": "approved", "source": ["OWNER:5"]})
    c["tree.json"]["leaves"].append(dict(
        LEAF, id="beasts_kept_off", experience="At night the player sees wild animals turn away at the edge of a lit "
        "lantern's light and never enter it", scenario="a hungry wild animal walking toward a lit lantern at night",
        source=["OWNER:5"], false_pass=["an animal that was never heading for the light"],
        red="a wild animal that walks into the lit cells"))
    c["scenes.json"]["scenes"].append({
        "id": "sc_beasts_kept_off", "kind": "acceptance", "requirement": ["beasts_kept_off"], "staged_by": "script",
        "entry_point": "src/RimMandrake/Lanterns/validation.py::scene_beasts_kept_off",
        "start": ["the sc_light room at midnight, its door open, the lantern lit with 3 oil (asserted)",
                  "a manhunting wolf spawned 8 cells from the door, pathing to a colonist inside (asserted)"],
        "action": "advance 2000 ticks", "expect": "the wolf never stands on a cell within 2 cells of the lantern",
        "control": {"case": "the same room and wolf with the lantern unlit",
                    "expect": "the wolf reaches a cell within 2 cells of the lantern",
                    "rules_out": "the wolf turning away for its own reasons rather than the light"},
        "restore": "destroy the quicktest map; nothing persistent changed", "hold": "immediate"})


def _repaired(c):
    """Round 2 after round 1 refused sc_light's missing control; the BASE scene now has it: a later round checks the
    repair and finishes."""
    c["coverage_verdict.json"] = _prior(LIGHT_GAP, {"oil_out": "sc_oil_out", "inv_oil": "sc_oil_out"})


# id, expect, mutation, the route a refusal must take (`outcome`), and whether it is a later round (a prior verdict)
CASES = (("good_lanterns", "pass", None, None), ("good_lanterns_tuning", "pass", _tuning_bait, None),
         ("good_round2_repaired", "pass", _repaired, None), ("good_lanterns_no_reset", "pass", _no_reset, None),
         ("bad_leaf_no_scene", "refuse", _no_oil_scene, "designer"),
         ("bad_scene_no_control", "refuse", _no_control, "designer"),
         ("bad_conflict_routing", "refuse", _never_dark, ("criteria", "owner")),
         ("bad_mixed_row", "refuse", _refuel_row, "designer"),
         ("bad_late_serious", "refuse", _late_red, "late"),
         ("good_pyrelands_look8", "pass", "pyrelands_look8", None),
         ("bad_fire_never_touched", "refuse", _straw_unreached, "designer"),
         ("good_one_kind_enough", "pass", _one_kind, None))
ROUTE = {cid: route for cid, _e, _m, route in CASES}
FAULTED = ("flawed", "unattainable")


def planted():
    """The registry row's `planted` list (refusal_contract.judge_cases)."""
    return [{"id": cid, "expect": exp} for cid, exp, _m, _r in CASES]


def route_of(g):
    """Where production sends one blocking gap: the criteria (the neutral fixer: coverage_judge's criteria_suspect), his
    answer (return_to 2: stage 2 asks him) or the Designer's rework."""
    if g.get("criterion_verdict") in FAULTED or g.get("judge_criterion_verdict") in FAULTED:
        return "criteria"
    return "owner" if g.get("return_to") == 2 else "designer"


def outcome(route, blocking):
    """-> "pass" with no blocking gap; "refuse" when a blocking gap takes the planted route (any route for a pass case:
    its refusal is wrong anyway; a tuple of routes accepts any of them); else "refuse, misrouted (<routes>)", which is
    not the planted refusal."""
    if not blocking:
        return "pass"
    routes = {route_of(g) for g in blocking}
    if any(g.get("new_since") == "late" and g.get("late_confirmed") is True for g in blocking):
        routes.add("late")
    if route is None or set(route if isinstance(route, tuple) else (route,)) & routes:
        return "refuse"
    return "refuse, misrouted (%s)" % ", ".join(sorted(routes))


def stage(root):
    """Write the role files and one concept per case under root. -> [(case id, expect, concept dir)]."""
    for rel in ROLES:
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(REPO, rel), os.path.join(root, rel))
    out = []
    for cid, exp, mut, _route in CASES:
        if mut == "pyrelands_look8":
            out.append((cid, exp, _stage_pyrelands(root, cid)))
            continue
        c = copy.deepcopy(BASE)
        if mut:
            mut(c)
        before = c.pop("_before", None)
        d = os.path.join(root, "design", "concepts", "Lanterns_%s" % cid)
        os.makedirs(d)
        _write(d, c)
        if before and "coverage_verdict.json" in c:
            # the prior verdict's renderings are of the concept before the repair (7_same_problem_rule.md rule 4)
            b = copy.deepcopy(BASE)
            before(b)
            b.pop("coverage_verdict.json", None)
            bd = tempfile.mkdtemp(prefix="rm-coverage-cal-before-")   # outside root: the judge must not find it
            try:
                _write(bd, b)
                v = dict(c["coverage_verdict.json"], entry_text=CJ.entry_texts(bd), hashes=CJ.entry_hashes(bd))
            finally:
                shutil.rmtree(bd, ignore_errors=True)
            _write(d, {"coverage_verdict.json": v})
        out.append((cid, exp, d))
    return out


def _write(d, files):
    for fn, body in files.items():
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            f.write(body if isinstance(body, str) else json.dumps(body, indent=1))


def _stage_pyrelands(root, cid):
    """Pyrelands' concept files as look 8 read them (git show PYRELANDS_LOOK8_AT). A file git cannot give is staged
    absent only when it was absent there too; any other failure raises, naming the file (the case could not stage)."""
    d = os.path.join(root, "design", "concepts", "Pyrelands_%s" % cid)
    os.makedirs(d)
    for fn in PYRELANDS_FILES:
        p = subprocess.run(["git", "-C", REPO, "show", "%s:%s/%s" % (PYRELANDS_LOOK8_AT, PYRELANDS, fn)],
                           capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            if "does not exist" in p.stderr or "exists on disk, but not in" in p.stderr:
                continue
            raise RuntimeError("could not stage %s/%s at %s: %s" % (PYRELANDS, fn, PYRELANDS_LOOK8_AT, p.stderr.strip()))
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            f.write(p.stdout)
    return d


def judge(root, d, route=None, reader="auto", _resume=None, _before=None):
    """One real coverage judge on a planted concept, its blocking gaps read by the real second reader. Refusal records
    the contract finds broken are re-asked once in the same session, as coverage_judge.run() re-asks them (_resume:
    (session, errors, cost so far)). The judge may fix scenes.json (coverage_judge.JUDGE_FIX_TEXT): as run() does, the
    entry texts and input hashes are read BEFORE it runs (_before), a gap it fixed still blocks, and its covered word
    over its own fix is not_covered (judge_fix). -> (got, detail)."""
    tree = json.load(open(os.path.join(d, "tree.json"), encoding="utf-8"))
    if _before is None:
        _before = (CJ.entry_texts(d), CJ.fresh_key(d, CT.load(d)))
    prior = CJ.prior_verdict(d)
    dp = CJ.delta_plan(d, prior) if prior else None   # as production: a re-judge with hashes and gap numbers is a delta
    text = (CJ.delta_prompt(d, root, dp, 2) if dp is not None
            else CJ.prompt(d, root, CJ.required_ids(d, tree), prior is not None, 2 if prior else 1))
    argv = [CJ.CLAUDE, "-p", text, "--model", CJ.MODEL, "--output-format", "json",
            "--json-schema", json.dumps(CJ.SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions",
            "--name", "COVERAGE CALIBRATION %s" % os.path.basename(d), *EF.effort_args(CJ.MODEL)]
    if _resume:
        argv = [CJ.CLAUDE, "-p", "Your verdict's refusal records do not meet the refusal contract:\n%s\nAnswer again "
                "with the whole verdict, every row and every gap, each gap a complete record."
                % "\n".join("- %s" % e for e in _resume[1]), "--resume", _resume[0]] + argv[3:]
    argv = CJ.spend_watchdog.wrap(argv, CASE_BUDGET_USD_BIG if "Pyrelands" in d else CASE_BUDGET_USD)   # from outside
    try:
        p = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=CASE_TIMEOUT_S)
        res = json.loads(p.stdout or "null")
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, {"error": "%s: %s" % (type(e).__name__, e)}
    so = (res or {}).get("structured_output") if isinstance(res, dict) else None
    detail = {"cost_usd": (res or {}).get("total_cost_usd") if isinstance(res, dict) else None}
    if _resume:     # a resumed result is the whole session so far: the case costs that total, once
        import detached_helper as DH
        stop = isinstance(res, dict) and res.get("stopped_by") == "spend_watchdog"
        detail.update(reasked=_resume[1][:6], cost_usd=DH.session_part(detail["cost_usd"], _resume[2], stop)[1])
    if p.returncode != 0 or not isinstance(so, dict) or so.get("verdict") not in ("covered", "not_covered"):
        detail["error"] = "no well-formed verdict (exit %s)" % p.returncode
        return None, detail
    gaps = [g for g in list(so.get("gaps") or []) if isinstance(g, dict)] + [
        dict(g, from_rows=True) for g in CJ.failed_part_gaps(so.get("checklist") or [], so.get("gaps") or [])]
    fixrec = {"judge": "calibration", "verdict": so["verdict"], "gaps": gaps}
    CJ.judge_fix(fixrec, None, CJ.moved_inputs(d, _before[1]))
    if fixrec.get("judge_fixed") or fixrec.get("judge_fix_refused"):
        detail.update(judge_fixed=fixrec.get("judge_fixed"), judge_fix_refused=fixrec.get("judge_fix_refused"))
        so = dict(so, verdict=fixrec["verdict"])
    adv = []
    owed = dp["ids"] if dp is not None else CJ.required_ids(d, tree)
    missing = CJ.missing_rows(owed, so.get("checklist") or [])
    if missing:   # production re-asks, then signs nothing: neither the planted pass nor the planted refusal
        detail.update(verdict=so["verdict"], missing_rows=missing[:12])
        return "incomplete (no row for %s)" % ", ".join(missing[:6]), detail
    if prior and prior.get("verdict") == "not_covered" and all(
            isinstance(g, dict) and g.get("gid") for g in prior.get("gaps") or []):
        # what run() does on a later look: the same-problem rule (coverage_judge._slots, classify_new)
        repairs = None if "repairs" not in so else so["repairs"] if isinstance(so["repairs"], list) else []
        rec = {"verdict": so["verdict"], "checklist": list(so.get("checklist") or []), "gaps": gaps}
        if dp is not None:
            CJ.delta_merge(rec, dp, repairs)
            back = [g for g in rec.get("dropped") or [] if not g.get("names_slot")]   # as coverage_judge.run()
            rec["gaps"] = list(rec["gaps"]) + [{k: v for k, v in g.items() if k != "dropped"} for g in back]
        else:
            CJ.rejudge_slots(rec, prior, repairs)
        CJ.classify_new(rec, prior.get("entry_text"), _before[0], prior.get("judge"))   # as run(): the texts it judged
        gaps, adv = rec["gaps"], list(rec.get("advisory_gaps") or [])
        detail["answered"] = [a.get("gid") for a in rec.get("answered") or []]
    # the gate run() applies: only a gap the bar rule lets block refuses (bar_rule.blocks), after the second reader
    gaps, adv0 = CJ.BR.split(gaps)
    adv += adv0
    unread = None
    if gaps:
        rec = {"gaps": gaps}
        ent, crit = CJ.entries(d), {CJ.REST_CLAUSE: CJ.REST_TEXT}   # the criterion texts, as contract_verdict gives them
        for i in {i for g in gaps for i in g.get("ids") or []}:
            e = ent.get("inv:%s" % i) or ent.get("leaf:%s" % i)
            if e is not None:
                crit[i] = json.dumps(e, sort_keys=True)
        if reader == "auto":
            reader = CJ.llm_reader(d, root, "calibration-%s" % os.path.basename(d), charge=False)
        unread = CJ.second_read(rec, crit, reader)
        gaps, adv2 = CJ.BR.split(rec["gaps"])
        adv += adv2
    detail.update(verdict=so["verdict"], gaps=[str(g.get("what")) for g in gaps][:8],
                  advisory=[str(g.get("what")) for g in adv][:8],
                  routes=[{"what": str(g.get("what")), "route": route_of(g), "new_since": g.get("new_since"),
                           "ids": g.get("ids"), "return_to": g.get("return_to"),
                           "judge_criterion_verdict": g.get("judge_criterion_verdict"),
                           "criterion_verdict": g.get("criterion_verdict"), "severity": g.get("severity"),
                           "late_confirmed": g.get("late_confirmed")} for g in gaps][:8])
    if unread:   # no second read: the refusal binds nothing in production, so it is not the planted refusal either
        detail["unread"] = unread
        return "refuse, unread", detail
    if not gaps and so["verdict"] != "covered" and not adv and not detail.get("answered"):
        return "refuse, names nothing", detail   # not_covered with no gap at all: routed nowhere, not the planted one
    mine = [g for g in gaps if not g.get("carried")]
    if mine:   # carried gaps were checked when first written, as in production
        try:
            _cv, _given, errs = CJ.contract_errors(d, {"gaps": gaps, "checklist": list(so.get("checklist") or []),
                                                       "mode": "delta" if dp is not None else "full"}, None)
        except Exception as e:  # noqa: BLE001 - could not check is its own answer, never a pass or a refusal
            detail["contract_error"] = "%s: %s" % (type(e).__name__, e)
            return "refuse, record check failed", detail
        if errs:
            session = (res or {}).get("session_id") if isinstance(res, dict) else None
            if session and not _resume:
                return judge(root, d, route, reader, _resume=(session, errs, detail.get("cost_usd")), _before=_before)
            detail["malformed"] = errs[:6]
            return "refuse, malformed records", detail
    return outcome(route, gaps), detail


def run():
    with tempfile.TemporaryDirectory(prefix="rm-coverage-cal-") as root:
        staged = stage(root)
        with ThreadPoolExecutor(len(staged)) as ex:
            got = list(ex.map(lambda s: judge(root, s[2], ROUTE.get(s[0])), staged))
    rows = [dict({"id": cid, "expect": exp, "got": g}, **det) for (cid, exp, _d), (g, det) in zip(staged, got)]
    path = os.environ.get("RM_CALIBRATION_RESULTS")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cases": rows}, f, indent=1)
    for r in rows:
        print("%-22s expect %-6s got %-6s %s" % (r["id"], r["expect"], r["got"], r.get("error") or
                                                 "; ".join(r.get("gaps") or []) or r.get("verdict")))
    return 0 if all(r["got"] is not None for r in rows) else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["run"]:
        return run()
    if argv[:1] == ["stage"] and len(argv) == 2:
        for cid, exp, d in stage(argv[1]):
            print(cid, exp, d)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
