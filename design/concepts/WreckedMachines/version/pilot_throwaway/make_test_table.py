#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline Stage 2, WreckedMachines 0.1.0): build the test table. No model.

Shape after design/concepts/LeaningScrub/version/pilot_throwaway/make_test_table.py and the fields that Pyrelands' and Gimme
Some Slack's tables carry today. Steward run RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE.

Every bar-to-test pair comes from the locked files by one of the rules in PAIR_RULES (written into the table as `pairs_from`).
No pair is typed by hand. Three kinds of text ARE written here, and the table marks each so that the Stage 4 challenger judges
it: `why_game` (the locked files give the reason once, in plan.md "offline simulation"; WHY_GAME names which machinery of the
game each scene needs), `cheaper_why` for the 17 scenes that scene_size.py reads as oversized, and the specified offline tests that the tree's checks name
(SPECIFIED: a proposed file for each, built in Stage 3, red first).

runs_today is MEASURED: each built offline test is run now (logs under the agent storage root). A scene's entry is looked up
with the Designer's own reader (designer_stage.entry_point_exists). A tier is looked up in modset_builder.TIERS.

Writes design/concepts/WreckedMachines/version/test_table.json and test_table.md.
Usage: python3 design/concepts/WreckedMachines/version/pilot_throwaway/make_test_table.py [--no-run]
  --no-run   reuse the runs_today of the table on disk (for a remake that changes no offline test)
"""
import ast
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
import designer_stage as D  # noqa: E402

CON = ROOT / "design/concepts/WreckedMachines"
VER = CON / "version"
WM = "src/RimMandrake/WreckedMachines"
VAL = WM + "/validation.py"
ITEM = "RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE"
STORE = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True).stdout.strip()
if not STORE:
    sys.exit("make_test_table: the agent storage root could not be read (agent_storage.py printed nothing)")
RUNS = Path(STORE) / "rimmandrake/scratch/wreckedmachines_preflight/runs"

tree = json.loads((CON / "tree.json").read_text())
LEAVES = {l["id"]: l for l in tree["leaves"]}
CHECKS = {c["id"]: c for c in tree["checks"]}
record = json.loads((CON / "record.json").read_text())
INV = {i["id"]: i for i in record["inventory"]}
scn = json.loads((CON / "scenes.json").read_text())
SCENES = {s["id"]: s for s in scn["scenes"]}
cov = json.loads((CON / "coverage_verdict.json").read_text())
COV_FULL_AT = "89b10e6f1a"
_p = subprocess.run(["git", "show", COV_FULL_AT + ":design/concepts/WreckedMachines/coverage_verdict.json"],
                    capture_output=True, text=True)
if _p.returncode != 0:
    sys.exit("make_test_table: could not read the full round's coverage verdict at git %s: %s" % (COV_FULL_AT, _p.stderr.strip()))
cov_full = json.loads(_p.stdout)
if cov_full.get("mode") != "full" or cov.get("mode") != "delta" or cov.get("against") != cov_full.get("judge"):
    sys.exit("make_test_table: the two coverage rounds are not the full round and the delta against it")
LOCKED = json.loads((VER / "locked_bars.json").read_text())["ids"]
SMALL = json.loads((VER / "small_list.json").read_text())["tier"]
VALSRC = (ROOT / VAL).read_text()

PAIR_RULES = [
    "R1 decides: each scene that the coverage judge names for the bar with ok true, in either round: the full round "
    "(rm-coverage-judge-1795778084, coverage_verdict.json at git 89b10e6f1a) and the signed delta round that closed its "
    "seven gaps (coverage_verdict.json at the lock). The delta round's checklist holds only what it read again",
    "R2 decides: each acceptance scene whose `requirement` in scenes.json names the bar",
    "R3 decides: each name in a coverage_rest `by` list for the bar: a scene decides; a leaf brings that leaf's deciders",
    "R4 an exploration scene accepts no bar (scenes.json: its `question` only): where R1 or R3 names one, the offline test "
    "that its question names by check id (C_...) decides in its place, and the exploration scene is a support",
    "R5 decides: T_ONBOARDED_SET and T_ONBOARDING_COMPLETE for each bar that a scene decides whose kind_note counts a machine "
    "only 'once its onboarding has landed' or 'once its machine's art is in' (the coverage judge's reason for its repair g3: "
    "those two checks fix the full list of machines, so the note cannot let a missing machine pass)",
    "R6 decides: the offline test of a check that a coverage_rest `why` names for the bar",
    "R7 decides: T_LATER_STAYS_OUT for an inventory bar whose scope is `later` and that no scene decides (delegated call, "
    "after Pyrelands' T_CUT_STAYS_CUT: the version's reading of such a bar is that 0.1.0 does not ship it half-built)",
    "R8 supports: the offline test of a check that the bar's leaf text, or a meeting whose members hold the bar, names; a "
    "showcase scene that exercises the bar; an interaction scene whose `features` name the bar; a built offline test whose "
    "file names the bar id or one of its deciding scenes",
    "R9 supports: LOOK_STAGE8 for a bar with a deciding scene that holds for his review (`hold: owner_review`)",
    "R10 supports, written by the steward with its ground (STEWARD_SUPPORTS): a check of the tree that no other rule pairs "
    "supports the bar whose locked text reads the same thing. A support decides nothing, so no bar moves",
]
# R10: (test, bar, the locked text that is the ground)
STEWARD_SUPPORTS = [
    ("T_KERNEL_FUZZ", "inv_grade_ladder", "record.json inv_grade_ladder proof_note: 'Offline today: the kernel fuzz is green "
                                          "(15000 cases) on the shipped kernel file'"),
    ("T_KERNEL_FUZZ", "levels_of_function", "the check reads 'the ratios stay ordered Wrecked, Kludged, Refurbished and below "
                                            "the Original'; the leaf says 'no repaired machine does it as well as the Original'"),
    ("T_FORGE_GATES_GONE", "inv_alloy_forge_gates", "record.json inv_alloy_forge_gates scope_note: 'the late plasteel project "
                                                    "and the two forge settings end with the forge's onboarding'"),
    ("sc_old_save", "only_by_repair", "the leaf's accept line 'A colony that loads an older save keeps the working factory "
                                      "machines that already stand in it'; floor.json line save_compat names check C_old_save"),
]

# ---- the tree's checks as tests. file None = the check is another row (alias). ----
# (check id, test id, file, command or None, built?, kind, observes-extra)
CHECK_TESTS = [
    ("C_kernel_fuzz", "T_KERNEL_FUZZ", "src/RimMandrake/Utils/selftest_wreckedmachines_fuzz.py", None, True, "offline"),
    ("C_salvage_rule_offline", "T_SALVAGE_RULE", WM + "/selftest_salvage_rule.py", None, True, "offline"),
    ("C_onboarded_set", "T_ONBOARDED_SET", WM + "/selftest_wm_onboarded_set.py", None, True, "offline"),
    ("C_onboarding_complete", "T_ONBOARDING_COMPLETE", WM + "/selftest_wm_onboarding_complete.py", None, True, "offline"),
    ("C_onboarding_table_offline", "T_ONBOARDING_TABLE_OFFLINE", WM + "/selftest_wm_onboarding_table.py", None, True, "offline"),
    ("C_level_numbers", "T_LEVEL_NUMBERS", WM + "/selftest_wm_level_numbers.py", None, True, "offline"),
    ("C_repair_state_walk", "T_REPAIR_STATE_WALK", "src/RimMandrake/Utils/selftest_wreckedmachines_repair_walk.py", None, True, "offline"),
    ("C_neighbour_names", "T_NEIGHBOUR_NAMES", WM + "/selftest_wm_neighbour_names.py", None, True, "offline"),
    ("C_forge_gates_gone", "T_FORGE_GATES_GONE", WM + "/selftest_wm_forge_gates_gone.py", None, True, "offline"),
    ("C_distillation_loads", "T_DISTILLATION_LOADS", WM + "/selftest_wm_distillation_loads.py", None, True, "offline"),
    ("C_old_save", "sc_old_save", VAL, None, False, "live_minimal"),
]
# What a check test that Stage 3 built reads beside its own file (the change relation reads `reads`).
BUILT_READS = {
    "T_FORGE_GATES_GONE": [WM + "/Defs", WM + "/Patches", WM + "/Source", "src/RimUtinni/ResearchRetag", "src/RimStarWars/Armoury/Patches"],
    "T_ONBOARDING_TABLE_OFFLINE": [WM + "/Defs", "src/RimStarWars/Armoury/Patches"],
    "T_LEVEL_NUMBERS": [WM + "/level_numbers.json", WM + "/Defs", WM + "/Patches", WM + "/Source/WreckedMachinesMod.cs", WM + "/Source/Kernel"],
    "T_NEIGHBOUR_NAMES": [WM + "/Defs", WM + "/Patches", WM + "/Source", WM + "/About", "src/RimMandrake/ColdStorage", "src/RimStarWars/Cuisine",
                          "src/RimStarWars/Armoury", "src/RimUtinni/ResearchRetag"],
    # the table is Defs/MachineLines and the judge's records are evidence/art; each is named by its parent here, which exists
    # before the first line and the first record do (the preflight refuses a path that is not there)
    "T_ONBOARDED_SET": [WM + "/Defs"],
    "T_ONBOARDING_COMPLETE": [WM + "/Defs", WM + "/Patches", WM + "/Textures", WM + "/Source/WreckedMachinesMod.cs",
                              "design/concepts/WreckedMachines/version/evidence"],
    "T_REPAIR_STATE_WALK": [WM + "/Source/Kernel", WM + "/Source/SelfTest"],
    "T_DISTILLATION_LOADS": [WM + "/Patches/WreckedMachines_DistillationModule.xml", "src/RimMandrake/FlowWorks/About/About.xml",
                             "src/RimMandrake/FlowWorks/Defs", "src/RimMandrake/FlowWorks/Patches",
                             "src/RimMandrake/FlowWorks/Source"],
}
CHECK_ALIAS = {"C_power_mark": ("sc_marks_agree", "the scene's kind_note: 'this scene re-reads the fault of the first look "
                                "(record contradiction c_bolt_on_powered_machine) and classes it'")}
CHECK_TO_TEST = {c: t for c, t, *_ in CHECK_TESTS}
CHECK_TO_TEST.update({c: t for c, (t, _) in CHECK_ALIAS.items()})

# built offline tests that the tree names by no check: the lint of the mod's defs and its planted-defect selftest
EXTRA_OFFLINE = [
    ("T_LINT_DEFS", "src/RimMandrake/Utils/lint_wreckedmachines_defs.py",
     "static clauses over the mod's defs as built (graded defs, lines, thought stages, sliders)",
     "reads the build before 0.1.0 (the ladder by replaceTags); the build of 0.1.0 changes its clauses with the ladder"),
    ("T_LINT_PLANTS", "src/RimMandrake/Utils/selftest_wreckedmachines_lint.py",
     "the lint's own planted-defect selftest: each clause goes red on its planted defect", None),
    ("T_STATIC", VAL,
     "validation.py static_checks(): the tier shapes of the build before 0.1.0 (process counts, canOverclock, shared replaceTags, "
     "research gate, every setting read)",
     "asserts the place rule PlaceWorker_BuildOverLowerGrade and replaceTags, which plan.md removes ('Changed'): the build of "
     "0.1.0 rewrites these clauses with the ladder; a red here after that change is the check's, not the mod's"),
]
# suites in the mod's folders that decide and support no bar: what each is, so that nobody registers it as a mod check
UNLISTED = {
    WM + "/selftest_wm_scenes.py": "proof-harness completeness: each scene of validation.py has its asserted start, its control "
                                   "and no forbidden act after the start, on a fake game; not a mod behaviour",
    "src/RimMandrake/bridgetools/selftest_wreck_reads.py": "the generic bridge reads that the scenes use (thing_set_sample, "
                                                           "install_blueprint, study record, processor_fill, reach_edge, caravan "
                                                           "reads), with planted faults; a test of the bridge, not of the mod",
    WM + "/prove_alloy_forge_offline.py": "the offline proof of the alloy forge's gates (--vfef <VFE Factory mod dir>): the gates "
                                          "leave the mod when the forge is onboarded (plan.md); its patch interpreter is what "
                                          "T_ONBOARDING_TABLE_OFFLINE is to reuse (tree check C_onboarding_table_offline)",
}

# ---- why the game is needed, from plan.md "offline simulation" (the one place the locked files give the reason) ----
PLAN_NO = ("plan.md, offline simulation: 'No: study, carrying, placement and the pictures. Each is the game's own machinery (a job "
           "on a building, the uninstall chain, map generation, the renderer), and a fake of it would be a copy that proves only "
           "itself.'")
MACHINERY = {
    "menu": "the build menu is made by the running game from the defs after every patch, this mod's startup edits and the research "
            "state; an XML read sees none of the three together",
    "generators": "the reward, loot and trader-stock generators are the loaded game's own (Core and the expansions), and a patch "
                  "that matches nothing logs nothing (plan.md, risks, 'The base game's hand-outs'): only the generators' output "
                  "shows what a colony can be handed",
    "placement": PLAN_NO + " This scene reads placement: the game's map generation with this mod's step in it",
    "carry": PLAN_NO + " This scene reads carrying: the game's uninstall, haul and install jobs on a carried form",
    "study": PLAN_NO + " This scene reads study: the base game's study comp as a job on a building",
    "repair": "plan.md, offline simulation: the offline walk (T_REPAIR_STATE_WALK) reads the repair's logic and 'leaves out "
              "colonist jobs and paths'; plan.md, risks: 'The offline walk reads the logic; sc_repair_on_machine reads the "
              "identity' (power connection, facing, the machine in sight while colonists haul and work)",
    "levels": "plan.md, offline simulation: the onboarding read (T_ONBOARDING_TABLE_OFFLINE) 'leaves out whether the part is useful "
              "and what the C# changes at startup'; the levels are applied by C# at startup onto the factory mod's processor, and "
              "the work, the power and the mood are read on the running machine",
    "pictures": PLAN_NO + " This scene reads the pictures: what the renderer draws at play zoom",
    "switch": "a Mod Settings line is applied to the loaded defs, the build menu and the generators at run time (the re-derivation "
              "of every def edit from the shipped def when a setting is applied, plan.md 'Kept as built'); only the loaded game "
              "shows the machine given back",
    "whole": "bar whole_journey asks for the run itself, 'nothing done by a command': colonists' jobs, the clock, a save and a "
             "reload; " + PLAN_NO,
    "ground": "plan.md, risks, 'Ground': read from the game's source and 'not yet seen in play'; the scene reads in play whether "
              "the game accepts factory floor under a standing wreck (GenConstruct.CanPlaceBlueprintOver)",
    "save": "floor.json line save_compat: the game's own save loader resolves an older save's machines against the defs with "
            "this mod added; no offline reader of a save applies the game's def resolution",
}
WHY_GAME = {
    "sc_menu_and_research": "menu", "sc_no_handouts": "generators", "sc_ruin_holds_wrecks": "placement",
    "sc_rare_wreck_ordinary_map": "placement", "sc_carry_wreck_home": "carry", "sc_caravan_wreck_home": "carry",
    "sc_study_opens_first_project": "study", "sc_second_study": "study", "sc_study_without_research_reinvented": "study",
    "sc_repair_on_machine": "repair", "sc_repair_cancelled": "repair", "sc_component_gate": "repair",
    "sc_uninstall_during_repair": "repair", "sc_repair_needs_ground": "ground",
    "sc_levels_do_their_work": "levels", "sc_levels_under_settings": "levels", "sc_forge_plasteel": "levels",
    "sc_cell_and_emanator": "levels", "sc_every_machine_onboarded": "levels", "sc_cannery_tier": "levels",
    "sc_three_looks_rows": "pictures", "sc_marks_agree": "pictures",
    "sc_switch_machine_off": "switch", "sc_all_switches_off": "switch",
    "sc_whole_journey": "whole", "sc_whole_second_order": "whole", "sc_old_save": "save",
    "sc_study_spike": "study", "sc_first_look_built_mod": "pictures",
}
# the dear scenes (designer_scene_contract.md, 'The cheapest scene that decides the bar'): why no cheaper scene decides the bar
CHEAPER_WHY = {
    "sc_whole_journey": "the bar is the whole run by colonists' work ('With every ancient machine on and nothing done by a "
                        "command'); each step alone has its own cheaper scene, and none of them reads that one colony gets from "
                        "a wreck in a ruin to a Refurbished machine. The scene splits at its mid-way save if one visit cannot "
                        "afford it (scenes.json kind_note)",
    "sc_whole_second_order": "the same run as sc_whole_journey read for its second machine; it shares that scene's start",
    "sc_caravan_wreck_home": "sc_carry_wreck_home reads carrying on one map; a wreck found on another tile comes home only by "
                             "caravan, and a carried form that no caravan can load fails 'carry it away' for every wreck that "
                             "is not at home (the coverage judge's repair, record decision d_stage5_judge_fix_read)",
    "sc_ruin_holds_wrecks": "the placement is the mod's decision under test (kind_note: Minimum Force, 'the scene forces nothing "
                            "in it'); a state read of the placement list is the scene's start, and only generated maps show "
                            "where the wrecks land",
    "sc_rare_wreck_ordinary_map": "random by design (kind_note): the chance is read only over generated maps; the control "
                                  "(ordinary placement off, no map holds a wreck) runs in the same pass",
}
# The 12 scenes that scene_size.py reads as oversized besides the five above (publish gate, 2026-11-27). Each reason is
# written from the scene's row and its script as read on that day; the Stage 4 challenger judges whether it is true.
CEILING = ("The span that scene_size.py reads is the sum of the scene's wait ceilings. Each long wait is a loop that ends at the "
           "reading it waits for, so the scene plays as long as the colonists' work takes at the shipped values, and that is "
           "not measured before the build. ")
STUDY = ("The bar refuses a study that 'took no time that a player would notice' (leaf study_opens_research, `lazy`), and the "
         "row expects a researcher who 'comes back to it on later days with no new order': a scene inside one day cannot show "
         "a return on a later day. ")
REPAIR = ("T_REPAIR_STATE_WALK decides the repair's logic offline. What is left for the game is the leaf's own sentence, "
          "'colonists bring the materials and work at it where it stands', and only the clock shows colonists' hauling and work. ")
CHEAPER_WHY.update({
    "sc_study_opens_first_project": CEILING + STUDY + "Its clauses are the steps of one study (locked, studied by himself, the "
                                    "text rising, open, finished at the bench); each step needs the state that the step before "
                                    "made, so a scene for each would play the same study again",
    "sc_second_study": CEILING + STUDY + "It holds a save and reload in the middle of a study, which needs a study in progress. "
                       "Its one fixed wait, two days, is its control: with no study of the Kludged machine, time alone opens "
                       "nothing",
    "sc_study_without_research_reinvented": CEILING + STUDY + "The coverage judge asked for this scene (record decision "
                                            "d_stage5_judge_fix_read): the mod's small list holds Research Reinvented, so no "
                                            "other scene shows the base game's study alone. It plays the flow of "
                                            "sc_study_opens_first_project on a list without that mod",
    "sc_repair_on_machine": CEILING + REPAIR + "Its clauses (the order on the machine, the haul and the work, the machine at its "
                            "cell at every read, the level and the facing at the end, the reload, the signal) are readings of "
                            "one repair; a scene for each would stage and play the same repair again",
    "sc_repair_cancelled": CEILING + REPAIR + "The three cancels come at three moments of a repair (before a delivery, after "
                           "part of the materials, during the work), and colonists' work must bring the repair to each. Its "
                           "longest wait is its control: a fourth, uncancelled repair completes, which shows that a repair "
                           "could complete in this scene",
    "sc_component_gate": CEILING + REPAIR + "Its clauses follow one Ancient Component through one Kludged smelter: the order "
                         "unavailable without it, the cancel that gives it back, the repair that uses it up, the Refurbished "
                         "machine that offers no more. Each needs the state that the one before made",
    "sc_repair_needs_ground": CEILING + "plan.md, risks, 'Ground': the rule is read from the game's source and 'not yet seen in "
                              "play'. The scene shows in play that a colonist lays factory floor under a standing wreck and "
                              "that a carried wreck installs on factory floor; both are colonists' jobs on the clock",
    "sc_levels_do_their_work": CEILING + "'takes longer for the same product' is a reading of the clock: the scene makes one "
                               "product at each level and counts its own waits until the product is out. The applied speed as a "
                               "state read is taken for every machine by sc_every_machine_onboarded; this scene shows on two "
                               "machines that the product comes at that speed. Its clauses are that one comparison on the "
                               "smelter and on the drill",
    "sc_carry_wreck_home": "one colonist and one order for each act (the third step of the cheap ladder): the uninstall, the "
                           "haul and the install are three acts of one carry, read as the colonist's own jobs. The other "
                           "clauses are a state read of every wreck def's carried form in the same pass, and the mass, which is "
                           "recorded and not judged",
    "sc_switch_machine_off": "a state read with no clock and no colonist's work: one line off, a read, the line on, a read. Its "
                             "clauses are the fields of those reads (build menu, projects, generators, the machines that stand, "
                             "the placement list, the labels), and 'the last read equals the first read field by field' needs "
                             "every field in one pass",
    "sc_cannery_tier": "the one scene on the list with Vanilla Cooking Expanded (plan.md: 'Each of the two tiers serves one "
                       "scene'). A load of that list is its cost, so every read of the cannery (build menu, placement list, "
                       "levels, orders, carried form) is taken on the one load. It is a state read with no clock and no "
                       "colonist's work",
    "sc_every_machine_onboarded": "a state read for every machine (scenes.json kind_note), with no clock and no colonist's work, "
                                  "so nothing in it can be spoiled. Its clauses are the fields of one read for each machine, "
                                  "and the loaded game is compared with the machine's onboarding row in the same pass",
})
# scenes on a tier of their own (plan.md: 'Each of the two tiers serves one scene'). The tier names are proposed here.
OWN_TIER = {
    "sc_study_without_research_reinvented": ("wreckedmachines_no_research_reinvented",
                                             "the small list without Research Reinvented (plan.md; small_list.json 'Tests may run "
                                             "on a smaller tier of their own')"),
    "sc_cannery_tier": ("wreckedmachines_cannery", "the small list plus Vanilla Cooking Expanded (plan.md; floor.json line "
                                                   "test_isolation)"),
}


def tiers_defined():
    """-> the tier names of modset_builder.TIERS, read as text (never imported: the module reads the live game's folders)."""
    src = (ROOT / "src/RimMandrake/Utils/modset_builder.py").read_text()
    return set(re.findall(r'^\s{4}"([a-z0-9_]+)":\s*\{', src, re.M))


TIERS = tiers_defined()
if SMALL not in TIERS:
    sys.exit("make_test_table: instrument probe failed: the mod's small list tier %r is not read from modset_builder.py" % SMALL)


def script_counts():
    """The counts the scenes say 'the tester writes in the test table before the first run', read from validation.py, where
    the builder wrote them before the scenes' first run (commit d8f8bd53b3)."""
    out = {}
    for name in ("GENERATOR_RUNS", "RUIN_MAPS", "FLOOD", "STUDY_DAYS"):
        m = re.search(r"^%s = (\d+)" % name, VALSRC, re.M)
        out[name] = int(m.group(1)) if m else None
    m = re.search(r"^ORDINARY_MAPS, ORDINARY_WANT = (\d+), (\d+)", VALSRC, re.M)
    out["ORDINARY_MAPS"], out["ORDINARY_WANT"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    return out


COUNTS = script_counts()
SCENE_COUNTS = {
    "sc_no_handouts": {"runs_per_generator": COUNTS["GENERATOR_RUNS"]},
    "sc_ruin_holds_wrecks": {"ruin_maps": COUNTS["RUIN_MAPS"], "flooded_above": COUNTS["FLOOD"]},
    "sc_rare_wreck_ordinary_map": {"ordinary_maps_in_one_run": COUNTS["ORDINARY_MAPS"],
                                   "maps_with_a_wreck_wanted": COUNTS["ORDINARY_WANT"]},
    "sc_study_opens_first_project": {"study_days": COUNTS["STUDY_DAYS"]},
    "sc_second_study": {"study_days": COUNTS["STUDY_DAYS"]},
}

T = {}
TEXT_CMD = ("python3 -c \"import sys; sys.path[:0]=['src/RimMandrake/WreckedMachines','src/RimMandrake/Utils',"
            "'src/RimMandrake/Utils/modcheck']; import validation as V; from suite import TestContext; t=TestContext(None); "
            "t.session=None; dict(V.suite.chains)['scene_text_names_no_setting'](t); "
            "rows=[(c.name,c.verdict,str(c.detail)[:300]) for c in t.components]; [print(*r) for r in rows]; "
            "bad=[r for r in rows if r[1]!='PASS']; print('sc_text_names_no_setting:', 'PASS' if rows and not bad else 'FAIL', "
            "len(rows), 'components,', len(bad), 'not PASS'); sys.exit(0 if rows and not bad else 1)\"")


def names_bar(text, ids):
    return [i for i in ids if re.search(r"\b%s\b" % re.escape(i), text)]


# ---- the checks ----
for cid, tid, f, cmd, built, kind in CHECK_TESTS:
    what = CHECKS[cid]["what"]
    row = dict(id=tid, kind=kind, stage="4-5" if kind == "offline" else "6", file=f, check=cid, observes=what,
               reads=([f] + BUILT_READS.get(tid, [])) if built else [WM], command=cmd or "python3 " + f)
    if cid == "C_old_save":
        row["floor_line"] = "save_compat (floor.json names this check for it)"
    if not built:
        row.update(new=True, built_in_stage="3",
                   runs_today={"ran": False, "why": "specified at the lock of 0.1.0 (tree check %s); Stage 3 builds it and "
                                                    "records it red first (maturation.py red-seen)" % cid},
                   file_note="the file is proposed by the table maker; the builder may place it elsewhere and remakes the table")
    if kind != "offline":
        row.update(tier=SMALL, entry="scene_old_save", entry_exists=D.entry_point_exists(".", VAL + "::scene_old_save"),
                   why_game=MACHINERY[WHY_GAME[tid]], why_game_by="steward, from the locked text it quotes", why_full_list=None,
                   command="python.exe src/RimMandrake/Utils/modcheck/cli.py run WreckedMachines --chains scene_old_save",
                   command_note="small list %s; entry ABSENT until written" % SMALL, test_kind="A")
    T[tid] = row
for tid, f, obs, note in EXTRA_OFFLINE:
    T[tid] = dict(id=tid, kind="offline", stage="4-5", file=f, observes=obs, reads=[f], command="python3 " + f,
                  support_only=True, **({"note": note} if note else {}))
T["T_LEVEL_NUMBERS"]["support_only"] = True
T["T_LEVEL_NUMBERS"]["note"] = "the tree: 'No number here passes or refuses a bar.' A baseline that can be diffed"


# ---- one test per scene ----
def scene_is_offline(sc):
    return "offline: no game is needed" in (sc.get("kind_note") or "")


for sid, sc in SCENES.items():
    ep = sc.get("entry_point")
    exp = sc.get("expect") or sc.get("question") or ""
    if sc["kind"] == "exploration":
        named = [c for c in CHECKS if c in (sc.get("question") or "")]
        T[sid] = dict(id=sid, kind="exploration", stage="4-5" if named else "6", scene_kind="exploration", file=None,
                      observes=sc["question"], reads=[], support_only=True,
                      read_by=[CHECK_TO_TEST[c] for c in named],
                      runs_today={"ran": False, "why": "an exploration accepts no bar (scenes.json); its question is read by "
                                                       + (", ".join(CHECK_TO_TEST[c] for c in named) if named else
                                                          "a look in the running game")})
        if not named:
            T[sid]["why_game"] = MACHINERY[WHY_GAME[sid]]
            T[sid]["why_game_by"] = "steward, from the locked text it quotes"
        continue
    f, entry = ep.split("::")
    exists = D.entry_point_exists(".", ep)
    if scene_is_offline(sc):
        cmd = "python3 " + f if entry == "main" else TEXT_CMD
        T[sid] = dict(id=sid, kind="offline", stage="4-5", scene_kind=sc["kind"], file=f, entry=entry, entry_exists=exists,
                      observes=exp, reads=[f, WM], command=cmd, item=sc.get("entry_point_item"), hold=sc.get("hold"),
                      kind_note=sc.get("kind_note"))
        if entry != "main":
            T[sid]["command_note"] = ("validation.py has no command line for one offline chain: this line calls the chain as "
                                      "selftest_wm_scenes.text_scene does and exits 1 unless every component reads PASS")
        continue
    tier, tier_why = OWN_TIER.get(sid, (SMALL, None))
    chain = entry
    T[sid] = dict(id=sid, kind="live_minimal", test_kind="A", stage="6", scene_kind=sc["kind"], tier=tier,
                  tier_defined=tier in TIERS, file=f, entry=entry, entry_exists=exists, observes=exp, reads=[f, WM],
                  why_game=MACHINERY[WHY_GAME[sid]], why_game_by="steward, from the locked text it quotes", why_full_list=None,
                  command="python.exe src/RimMandrake/Utils/modcheck/cli.py run WreckedMachines --chains " + chain,
                  command_note="tier %s%s" % (tier, "" if tier in TIERS else
                                              " (NOT DEFINED in modset_builder.TIERS: Stage 3 defines it; the name is proposed)"),
                  item=sc.get("entry_point_item"), hold=sc.get("hold"), kind_note=sc.get("kind_note"))
    if tier_why:
        T[sid]["tier_why"] = tier_why
    if sid in CHEAPER_WHY:
        T[sid]["cheaper_why"] = CHEAPER_WHY[sid]
        T[sid]["cheaper_why_by"] = "steward, from the scene's row and script as read on 2026-11-27"
    if sid in SCENE_COUNTS:
        T[sid]["counts_before_first_run"] = dict(SCENE_COUNTS[sid], source=VAL + " (the builder's constants, commit d8f8bd53b3, "
                                                 "written before the scenes' first run)")
    if sc["kind"] == "interaction":
        T[sid]["features"] = sc.get("features")
T["sc_rare_wreck_ordinary_map"]["kind_tag_note"] = (
    "no B tag is written here: scenes.json says 'random by design' and that the tester tags the kind on evidence. As scripted, "
    "one run of the scene holds its own sample (%s ordinary maps, at least %s with a wreck) and its control, so one run gives "
    "one verdict. A tester who tags it B writes tag_evidence, budget and x_of_y before the first counted run"
    % (COUNTS["ORDINARY_MAPS"], COUNTS["ORDINARY_WANT"]))
T["sc_ruin_holds_wrecks"]["kind_tag_note"] = "scenes.json kind_note: 'the tester tags the kind on evidence'; no tag is guessed here"

T["T_LATER_STAYS_OUT"] = dict(
    id="T_LATER_STAYS_OUT", kind="offline", stage="4-5", file=WM + "/selftest_wm_later_stays_out.py",
    observes="the two inventory rows that 0.1.0 leaves for a later version are not shipped half-built: no turret line (no def "
             "of the mod names a turret: record inv_turret_line search_scope) and no wealth exclusion (no WealthWatcher or "
             "MarketValue patch in the mod's C#: record inv_wealth_exclusion search_scope). Red first on a planted turret def "
             "and a planted wealth patch",
    reads=[WM + "/selftest_wm_later_stays_out.py", WM + "/Defs", WM + "/Patches", WM + "/Source"],
    command="python3 " + WM + "/selftest_wm_later_stays_out.py",
    delegated="delegated: evidence-for-ask: a locked bar of scope `later` with no scene is decided by an absence check, as "
              "Pyrelands' two cut bars are (T_CUT_STAYS_CUT); the other choice, his card to take the two ids out of the locked "
              "bars, has no recorded evidence for it")
T["LOOK_STAGE8"] = dict(id="LOOK_STAGE8", kind="look", stage="8", file=None, observes="the owner walks the mod: gameplay, fun, "
                        "theme, UI (his act); the scenes that hold for his review are staged for it", reads=[], support_only=True,
                        command="owner walk", runs_today={"ran": False, "why": "Stage 8: the owner's own walk"})

# ---- pairs ----
DEC, SUP, WHY = defaultdict(list), defaultdict(list), defaultdict(dict)


def add(d, bar, tid, rule):
    if tid not in T:
        sys.exit("make_test_table: rule %s pairs bar %s with %s, which is no test of the table" % (rule, bar, tid))
    if tid not in d[bar]:
        d[bar].append(tid)
        WHY[bar][tid] = rule


def decide_scene(bar, sid, rule):
    """R4: an exploration never decides; the offline test its question names does."""
    if SCENES[sid]["kind"] == "exploration":
        for t in T[sid].get("read_by") or []:
            add(DEC, bar, t, rule + "+R4")
        add(SUP, bar, sid, rule + "+R4")
    else:
        add(DEC, bar, sid, rule)


for rnd, name in ((cov_full, "R1 full round"), (cov, "R1 delta round")):          # R1
    for c in rnd["checklist"]:
        for p in c.get("parts", []):
            if p.get("scene") and p.get("ok") is True:
                decide_scene(c["id"], p["scene"], name)
for sid, sc in SCENES.items():                               # R2
    for r in sc.get("requirement") or []:
        decide_scene(r, sid, "R2")
REST_LEAF = []
for cr in scn.get("coverage_rest", []):                      # R3, R6
    for by in cr["by"]:
        if by in SCENES:
            decide_scene(cr["capability"], by, "R3")
        elif by in LEAVES:
            REST_LEAF.append((cr["capability"], by))
        else:
            sys.exit("make_test_table: coverage_rest %s names %s, which is no scene and no leaf" % (cr["capability"], by))
    for cid in names_bar(cr.get("why") or "", CHECKS):
        add(DEC, cr["capability"], CHECK_TO_TEST[cid], "R6")
ONBOARDED = [sid for sid, sc in SCENES.items() if re.search(r"once its onboarding has landed|once its machine's art is in",
                                                             sc.get("kind_note") or "")]
if sorted(ONBOARDED) != ["sc_every_machine_onboarded", "sc_three_looks_rows"]:
    sys.exit("make_test_table: rule R5 reads %s; the coverage judge's reason names two scenes" % ONBOARDED)
for bid in LOCKED:                                           # R5
    if any(s in DEC[bid] for s in ONBOARDED):
        add(DEC, bid, "T_ONBOARDED_SET", "R5")
        add(DEC, bid, "T_ONBOARDING_COMPLETE", "R5")
for cap, leaf in REST_LEAF:                                  # R3, a leaf: after R5, so that the leaf's deciders are whole
    for t in list(DEC[leaf]):
        add(DEC, cap, t, "R3")
for bid in LOCKED:                                           # R7
    if bid in INV and INV[bid].get("scope") == "later" and not DEC[bid]:
        add(DEC, bid, "T_LATER_STAYS_OUT", "R7")
# R8
for bid in LOCKED:
    text = json.dumps(LEAVES[bid]) if bid in LEAVES else ""
    for cid in names_bar(text, CHECKS):
        if CHECK_TO_TEST[cid] not in DEC[bid]:
            add(SUP, bid, CHECK_TO_TEST[cid], "R8 leaf text")
for m in tree["meetings"]:
    for cid in names_bar(json.dumps(m), CHECKS):
        for bid in m["members"]:
            if bid in LOCKED and CHECK_TO_TEST[cid] not in DEC[bid]:
                add(SUP, bid, CHECK_TO_TEST[cid], "R8 meeting %s" % m["thing"])
for sh in scn.get("showcases", []):
    for x in sh.get("exercises") or []:
        for sid in sh["scenes"]:
            if x in LOCKED and sid not in DEC[x]:
                add(SUP, x, sid, "R8 showcase %s" % sh["id"])
for sid, sc in SCENES.items():
    if sc["kind"] == "interaction":
        for b in sc.get("features") or []:
            if b in LOCKED and sid not in DEC[b]:
                add(SUP, b, sid, "R8 interaction")
for tid, t in list(T.items()):
    if t["kind"] == "offline" and not t.get("new") and not t.get("entry") and t.get("file") and (ROOT / t["file"]).exists():
        src = (ROOT / t["file"]).read_text(errors="replace")
        if t["file"] == VAL:
            continue        # the proof script names every scene; T_STATIC reads none of them
        for b in LOCKED:
            if tid not in DEC[b] and (re.search(r"\b%s\b" % re.escape(b), src) or any(
                    re.search(r"\b%s\b" % re.escape(s), src) for s in DEC[b] if s.startswith("sc_"))):
                add(SUP, b, tid, "R8 the file names the bar or its scene")
_paired = {t for b_ in LOCKED for t in DEC[b_] + SUP[b_]}      # R10: only a check that no other rule pairs
for tid, bid, ground in STEWARD_SUPPORTS:
    if tid in _paired:
        sys.exit("make_test_table: R10 names %s, which another rule already pairs: drop its lines" % tid)
    add(SUP, bid, tid, "R10 steward: " + ground)
for bid in LOCKED:                                           # R9
    if any(T[d].get("hold") == "owner_review" for d in DEC[bid]):
        add(SUP, bid, "LOOK_STAGE8", "R9")
# the tree's checks with no bar by any rule: named at the table's top, so that the builder still builds them
PAIRED = {t for b in LOCKED for t in DEC[b] + SUP[b]}
CHECKS_NO_BAR = {c: CHECK_TO_TEST[c] for c in CHECKS if CHECK_TO_TEST[c] not in PAIRED}


# ---- measure runs_today ----
def run_offline(t):
    RUNS.mkdir(parents=True, exist_ok=True)
    log = RUNS / (t["id"] + ".txt")
    t0 = time.time()
    p = subprocess.run(t["command"], shell=True, cwd=ROOT, capture_output=True, text=True)
    out = p.stdout + p.stderr
    log.write_text(out)
    lines = [l for l in out.splitlines() if l.strip()]
    return {"ran": True, "rc": p.returncode, "seconds": round(time.time() - t0, 1), "last": lines[-1][:300] if lines else "",
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "log": str(log),
            "result": "PASS" if p.returncode == 0 else "FAIL", "command": t["command"]}


OLD = {}
if "--no-run" in sys.argv and (VER / "test_table.json").exists():
    OLD = json.loads((VER / "test_table.json").read_text()).get("tests") or {}
for t in T.values():
    if t["kind"] == "offline" and not t.get("new"):
        prev = (OLD.get(t["id"]) or {}).get("runs_today")
        t["runs_today"] = prev if prev and prev.get("command") == t["command"] else run_offline(t)
        print("%-28s %s %ss" % (t["id"], t["runs_today"]["result"], t["runs_today"]["seconds"]), flush=True)
    elif t["kind"].startswith("live") and not t.get("new"):
        t["runs_today"] = {"ran": False, "entry_exists": t["entry_exists"],
                           "why": "a scene is run at its stage (Stage 6)" if t["entry_exists"] else "entry not written yet"}
if T["sc_text_names_no_setting"]["runs_today"].get("result") != "PASS":
    T["sc_text_names_no_setting"]["red_today"] = (
        "the read finds the setting's words in the mod's texts as built (the log names each hit). plan.md 'Changed': 'The "
        "setting words leave every text, and no text calls a level Repaired'. That is the build's work at Stage 3, and this "
        "check is its red-first reading")
for _tid, _why in (
        ("T_ONBOARDED_SET", "the onboarding table (Defs/MachineLines) does not hold a line for each of the 20 machines yet: the "
                            "check is built and red first; it goes green when the last machine is onboarded (plan.md, order, step 7)"),
        ("T_ONBOARDING_COMPLETE", "a machine on the table lacks a level def, a carried form, a studied project, a picture of its "
                                  "own, the art judge's record or its Mod Settings line: the check is built and red first; it "
                                  "goes green when every machine's onboarding is whole (plan.md, order, steps 4 to 7)")):
    if T[_tid]["runs_today"].get("result") != "PASS":
        T[_tid]["red_today"] = _why
T["sc_wreck_link_tags"]["partial"] = ("scenes.json kind_note: 'The script exists and is green on the smelter; the count line is "
                                      "new.' The count of Wrecked defs against the count of ancient machines is built with the "
                                      "onboarding (Stage 3)")


def runnable(tid):
    t = T[tid]
    if t.get("new"):
        return False
    if t["kind"] == "offline":
        return bool(t["runs_today"].get("ran")) and t["runs_today"].get("result") == "PASS"
    if t["kind"].startswith("live"):
        return bool(t["entry_exists"]) and bool(t.get("tier_defined", True))
    return False


ORDER = {"4-5": 1, "6": 2, "8": 3}
bars = []
for bid in LOCKED:
    src = "tree.json" if bid in LEAVES else "record.json"
    dec = DEC.get(bid, [])
    sup = [x for x in SUP.get(bid, []) if x not in dec]
    offd = [d for d in dec if T[d]["kind"] == "offline"]
    b = dict(id=bid, source=src,
             kind=("live" if LEAVES[bid].get("live_only") else "offline") if src == "tree.json" else "inventory",
             proves_at=max((T[d]["stage"] for d in dec), key=lambda s: ORDER[s]) if dec else None,
             decides=dec, supports=sup, pair_rules={k: v for k, v in WHY[bid].items()}, held=[],
             offline_decides=offd, offline_green_today=bool(offd) and all(runnable(d) for d in offd),
             every_decider_runnable_today=bool(dec) and all(runnable(d) for d in dec),
             any_decider_runnable_today=any(runnable(d) for d in dec),
             any_test_runnable_today=any(runnable(x) for x in dec + sup),
             not_runnable_today=[d for d in dec if not runnable(d)])
    if src == "record.json":
        b["scope"] = INV[bid].get("scope")
        b["impl"] = INV[bid].get("impl")
    bars.append(b)

HELD_GREP = r"wreck|kludg|refurbish|smelter|vanometric|emanator|ancient component|alloy forge"
held_hits = []
for f in sorted((ROOT / "design/RimMandrake/validation_holding").glob("*.md")):
    for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
        if re.search(HELD_GREP, line, re.I):
            held_hits.append("%s:%d" % (f.relative_to(ROOT), n))

KNOWN_NOT_OURS = ["design/RimMandrake/validation_holding/flowworks_walk_20261120.md:77",
                  "design/RimMandrake/validation_holding/flowworks_walk_20261120.md:164"]     # read 2026-11-27: RM_SuspensionWreck
if held_hits != KNOWN_NOT_OURS:
    sys.exit("make_test_table: the held look statements changed: the grep now finds %s. Read each new line; place a line of "
             "this mod on a bar and a test (held_statements), or add a line of another mod to KNOWN_NOT_OURS" % held_hits)

out = dict(
    mod="WreckedMachines", version="0.1.0", made=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    made_by="design/concepts/WreckedMachines/version/pilot_throwaway/make_test_table.py (throwaway, no model), steward run " + ITEM,
    stages={"2": "preflight (a program)", "4-5": "blind offline challenge and game-logic testing", "6": "in-game acceptance",
            "8": "his live walk"},
    rule="a bar passes when every test in decides passes; proves_at is the highest stage among them; supports add evidence but "
         "decide nothing",
    pairs_from=PAIR_RULES,
    written_by_the_steward=["tests.<id>.why_game (marked why_game_by)", "tests.<id>.cheaper_why (marked cheaper_why_by)", "the specified tests' files "
                            "and T_LATER_STAYS_OUT (rule R7)", "the two proposed tier names (tests.<id>.tier where tier_defined "
                            "is false)"],
    checks_map=dict({c: t for c, t, *_ in CHECK_TESTS}, **{c: "%s (%s)" % v for c, v in CHECK_ALIAS.items()}),
    checks_with_no_bar=dict({c: "%s: no rule pairs it with a bar; the tree names it as a check (%s)"
                             % (t, "specified: Stage 3 builds it" if T[t].get("new") else "built, and run above")
                             for c, t in CHECKS_NO_BAR.items()}),
    stage3_build_list={k: (v.get("check") or "rule R7") for k, v in T.items() if v.get("new")},
    stage3_also=["define the two tiers of the scenes that run on a tier of their own (tests.<id>.tier where tier_defined is "
                 "false) in src/RimMandrake/Utils/modset_builder.py",
                 "sc_text_names_no_setting is red today on the mod's texts as built: the build takes the setting's words out "
                 "(plan.md, 'Changed')",
                 "T_STATIC and T_LINT_DEFS read the build before 0.1.0: the build changes their clauses with the ladder",
                 "sc_wreck_link_tags: the count line is new (scenes.json kind_note)"],
    counts_before_first_run=dict(COUNTS, source=VAL),
    held_statements=[],
    held_note="0 held look statements name this mod: a grep of design/RimMandrake/validation_holding/*.md for %r finds %d "
              "line(s)%s, and each is FlowWorks' ruined bridge (RM_SuspensionWreck), not a machine of this mod"
              % (HELD_GREP, len(held_hits), (" (%s)" % ", ".join(held_hits)) if held_hits else ""),
    unlisted_suites=UNLISTED, tests=T, bars=bars)

if __name__ == "__main__":
    (VER / "test_table.json").write_text(json.dumps(out, indent=1) + "\n")
    off_built = [t for t in T.values() if t["kind"] == "offline" and not t.get("new")]
    new = [t for t in T.values() if t.get("new")]
    live = [t for t in T.values() if t["kind"].startswith("live") and not t.get("new")]
    md = ["# WreckedMachines 0.1.0 test table (read view of test_table.json)", "",
          "Made by `pilot_throwaway/make_test_table.py`, %s. A bar passes when every deciding test passes; a support adds "
          "evidence and decides nothing." % out["made"], "",
          "## How a pair is made", ""] + ["- " + r for r in PAIR_RULES] + [
          "", "## Counts", "",
          "- bars: %d (locked: %d)" % (len(bars), len(LOCKED)),
          "- tests: %d (%d built offline, %d live scenes with their entry written, %d specified for Stage 3, %d explorations, "
          "1 look)" % (len(T), len(off_built), len(live), len(new), sum(1 for t in T.values() if t["kind"] == "exploration")),
          "- built offline tests green today: %d, red: %d (%s)" % (
              sum(1 for t in off_built if t["runs_today"]["result"] == "PASS"),
              sum(1 for t in off_built if t["runs_today"]["result"] != "PASS"),
              ", ".join(t["id"] for t in off_built if t["runs_today"]["result"] != "PASS") or "none"),
          "- live scenes whose tier is not defined: %s" % (", ".join(t["id"] for t in live if not t.get("tier_defined", True)) or "none"),
          "- bars with every decider runnable today: %d of %d" % (sum(1 for b in bars if b["every_decider_runnable_today"]), len(bars)),
          "- bars with no deciding test: %d" % sum(1 for b in bars if not b["decides"]), "",
          "## Bars", "", "| bar | kind | proves at | decides | supports | runnable today | waits on |", "|---|---|---|---|---|---|---|"]
    for b in bars:
        md.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            b["id"], b.get("scope") and "inventory, " + b["scope"] or b["kind"], b["proves_at"] or "-",
            ", ".join(b["decides"]) or "**none**", ", ".join(b["supports"]) or "-",
            "yes" if b["every_decider_runnable_today"] else "no", ", ".join(b["not_runnable_today"]) or "-"))
    md += ["", "## Tests", "", "| test | kind | stage | file::entry | today |", "|---|---|---|---|---|"]
    for t in T.values():
        rt = t.get("runs_today", {})
        today = ("specified, Stage 3 builds it" if t.get("new") else rt.get("result") or (
            ("entry written" + ("" if t.get("tier_defined", True) else ", tier not defined")) if t.get("entry_exists")
            else rt.get("why", "")))
        md.append("| %s | %s | %s | %s | %s |" % (t["id"], t["kind"], t["stage"],
                  (t.get("file") or "-") + ("::" + t["entry"] if t.get("entry") else ""), today))
    md += ["", "## The tree's checks", "", "| check | test |", "|---|---|"] + [
        "| %s | %s |" % (c, v) for c, v in out["checks_map"].items()]
    md += ["", "## Suites that decide and support no bar", ""] + ["- `%s`: %s" % kv for kv in UNLISTED.items()]
    md += ["", "## Held look statements", "", out["held_note"]]
    (VER / "test_table.md").write_text("\n".join(md) + "\n")
    print("wrote", VER / "test_table.json", "and test_table.md;", len(bars), "bars,", len(T), "tests")
