#!/usr/bin/env python3
"""THROWAWAY (Maturation hand run beside the pilot, row 2, 2026-11-14): build GimmeSomeSlack 0.1.0's test-and-stage table.

Columns follow the pilot's design/concepts/ExplosiveKnockback/version/test_table.json so the mods read alike. Every offline
test is RUN here and its result recorded (runs_today is measured, not claimed). In-game tests are not run (offline-only
brief): their runnable flag is whether their named entry exists in code. The judgment (which test decides which bar) is
the MAP below, written by hand; nothing here edits a bar.

    python3 design/concepts/GimmeSomeSlack/version/make_test_table.py            # runs every offline test (~4.5 min)
    python3 design/concepts/GimmeSomeSlack/version/make_test_table.py --reuse    # re-render, keeping the last measured runs
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
C = "design/concepts/GimmeSomeSlack/"
G = "src/RimMandrake/GimmeSomeSlack/"
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, G, "northstar"))
import proof_leaves  # noqa: E402  (ROW_LEAVES: proof row -> leaves it is evidence for)

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
tree = json.load(open(C + "tree.json"))
rec = json.load(open(C + "record.json"))
scn = json.load(open(C + "scenes.json"))
verdict = json.load(open(C + "coverage_verdict.json"))
LEAF = {l["id"]: l for l in tree["leaves"]}
INV = {i["id"]: i for i in rec["inventory"]}
SCENE = {s["id"]: s for s in scn["scenes"]}
CORE = sorted(glob.glob(G + "Source/Core/*.cs"))
SELFTEST = sorted(glob.glob(G + "Source/SelfTest/*.cs"))
AERIAL = sorted(glob.glob(G + "Source/Aerial/*.cs"))

# ---- offline tests: built ones are run; specified ones are Stage 3's to build, failing first ----
OFF = {
    "T_CORE": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_gimmesomeslack.py",
                   observes="the C# SelfTest on the production core and aerial halves against the Python oracle: graph reduction, "
                            "planner, slack laying, shape no-two-alike, junction strips, dead/live end poses, style per run, theft "
                            "and tap window maths, aerial switch flips, determinism, rebuild slice budgets, seeded fuzz",
                   reads=CORE + AERIAL + SELFTEST + [G + "selftest_gimmesomeslack.py" if os.path.exists(G + "selftest_gimmesomeslack.py") else "src/RimMandrake/Utils/selftest_gimmesomeslack.py"]),
    # RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK (2026-11-16): the position-and-slope rule at every stubbed piece
    "T_STUB_JOINS": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_gimmesomeslack.py", args=["--no-export", "--joins-only"],
                         observes="Core/StubJoinAudit over 524 generated scenes (four looks x boxes, switches with 1-4 cords, wall/rock faces "
                                  "through and dead-ending, his stations 12 and 25): each cord on a stub passes its tip on its line and heading, "
                                  "no bare stub, the live end continues its cord over 90 frames, no loose end on a wall or rock dead end; "
                                  "planted kink, bare arm and pinched tail go red",
                         reads=[G + "Source/Core/StubJoinAudit.cs", G + "Source/SelfTest/StubJoinChecks.cs", G + "Source/Core/CordBuilder.cs"]),
    "T_STUB_ART_CENSUS": dict(stage="4-5", file=G + "selftest_gss_stub_art_census.py",
                              observes="every texture under Textures/ is classed in StubArt.Census (stubbed, position only, loose end, cord); "
                                       "a planted unknown texture goes red",
                              reads=[G + "Source/Core/StubJoinAudit.cs", G + "Textures"]),
    "T_GATE": dict(stage="2", file=G + "northstar/proof_all.py", args=["--offline-gate"],
                   observes="the offline tier O1-O8: mod files, csproj and DLL, the 26 shipped setting defaults, style art sanity "
                            "with planted faults, review-round art, GPT fix shapes, lamp mast register; plus the matrix and "
                            "proof_all selftests (O3 is T_CORE run again inside it)",
                   reads=[G + "validation.py", G + "About/About.xml", G + "Source/RimMandrake_GimmeSomeSlack.csproj"]),
    "T_MATRIX": dict(stage="4-5", file=G + "northstar_matrix/selftest.py",
                     observes="the scene matrix generator, oracle, placer and fake game: 57 checks, 17 negative controls",
                     reads=sorted(glob.glob(G + "northstar_matrix/*.py"))),
    "T_NO_HOSE": dict(stage="4-5", file=G + "northstar/selftest_gss_no_hose.py",
                      observes="the mod ships no hose, reel or pipe def, texture or class; a planted hose goes red",
                      reads=[G + "Defs", G + "Textures", G + "Source"]),
    "T_SHOCK_OUTLIVES": dict(stage="4-5", file=G + "selftest_gss_shock_outlives_wire.py",
                             observes="a fallen wire's shock cells die with the wire (GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE)",
                             reads=AERIAL),
    "T_SHOCK_OUTLIVES_BINDING": dict(stage="4-5", file=G + "selftest_gss_shock_outlives_wire_binding.py",
                                     observes="the live binding of the shock-outlives fix, compiled offline", reads=AERIAL),
    "T_SHOCK_BITES_BINDING": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_gss_shock_still_bites_binding.py",
                                  observes="a live fallen wire still shocks after the outlives fix (binding, offline)", reads=AERIAL),
    "T_END_HEAP": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_gss_end_heap_budget.py",
                       observes="long-run end heaps stay inside the loop budget", reads=CORE),
    "T_JUNCTION_ART": dict(stage="4-5", file=G + "selftest_gss_junction_necks.py",
                           observes="the Modern and Futuristic T/X junction PNGs: body wider than the cord, necks meet the cord",
                           reads=sorted(glob.glob(G + "Textures/**/*unction*.png", recursive=True))),
    "T_STRIP_ART": dict(stage="4-5", file=G + "selftest_gss_strip_art.py",
                        observes="the Modern power-strip PNGs have no black fringe (his 2026-11-08 sitting)",
                        reads=sorted(glob.glob(G + "Textures/**/*trip*.png", recursive=True))),
    "T_FW_PIT_DRAW_CENSUS": dict(stage="4-5", file="src/RimMandrake/FlowWorks/selftest_flowworks_pit_draw_census.py",
                                 observes="everything drawn outside the map-mesh print against FlowWorks' under-liquid law; GSS "
                                          "floor cords on a pit floor are faded by FloorSeen (CordUnderLiquid), overhead spans "
                                          "listed above everything",
                                 reads=[G + "Source/CordUnderLiquid.cs", G + "Source/SectionLayer_RM_MessyCords.cs",
                                        G + "Source/RM_MapComponent_CordGraph.cs"]),
    "T_PROOF_LEAVES": dict(stage="2", file=G + "northstar/selftest_gss_proof_leaves.py",
                           observes="every proof row cites a leaf of tree.json and every leaf has a row or a live item owing it",
                           reads=[G + "northstar/proof_leaves.py", C + "tree.json"]),
}
HARNESS = {  # tests of the instruments, not of the mod: they support a bar, never decide one
    "T_H_RESTRING_PROOF": (G + "selftest_gss_restring_proof.py", "the M15f re-string proof path's instruments", ["restring_cut_span"]),
    "T_H_KINETIC_SWAY": (G + "selftest_gss_kinetic_sway.py", "the M22 kinetic-sway proof rows, probe transport, launcher", ["spans_above_everything"]),
    "T_H_AERIAL_PROBE_BATCH": (G + "selftest_gss_aerial_probe_batch.py", "the aerial mod-settings probe batch", ["settings_switch_cleanly"]),
    "T_H_EXPLODE_PARSE": (G + "selftest_gss_explode_parse.py", "the explode probe's parsing against production AerialMath", ["fallen_span_on_ground"]),
    "T_H_NO_TWO_ALIKE_SHORT": (G + "northstar/selftest_gss_no_two_alike_short.py", "SC_no_two_cords_alike exempts cords under 3 cells", ["cords_never_repeat"]),
    "T_H_PLAYTEST_RUNNER": (G + "northstar/selftest_gss_playtest_runner.py", "the walk launcher's recipe expansion", ["walk_scavenger_base"]),
    "T_H_PROOF_DRIVERS": (G + "selftest_gss_proof_drivers.py", "the proof drivers' false-pass fixes", []),
    "T_H_REVIEW_LEFTOVERS": (G + "selftest_gss_review_leftovers.py", "post-approval proof-harness findings", []),
    "T_H_WEAKCLOSE_GUARDS": (G + "selftest_gss_weakclose_guards.py", "source-shape guards for Verse-bound findings", []),
    "T_H_HUMAN_REVIEW": (G + "selftest_human_review.py", "the review map layout", []),
    "T_H_PROOF_ALL": (G + "northstar/selftest_proof_all.py", "proof_all's durability on a fake bridge", []),
}
for k, (f, obs, _b) in HARNESS.items():
    OFF[k] = dict(stage="4-5", file=f, observes="harness: " + obs, reads=[f], support_only=True)

NEW = {  # specified at this lock; Stage 3 builds each and shows it red first
    "T_SETTINGS_SWEEP_OFFLINE": dict(
        stage="4-5", file=G + "selftest_gss_settings_sweep.py",
        observes="the settings sweep, moved out of the game: for each key of the shipped floor table (validation.SHIPPED, 26) "
                 "and each AerialSettings field, either an offline flip-and-return check whose outcome differs off and on and "
                 "returns on flip-back, or a listed reason it has no pure half and the live row that owns it; every "
                 "[HarmonyPatch] class in Source is gated by exactly one setting (source read), none ungated; planted: a call "
                 "site that drops its setting read, and a patch with no gate, each go red",
        reads=[G + "validation.py", G + "Source/GimmeSomeSlackMod.cs", G + "Source/Aerial/AerialSettings.cs",
               G + "Source/SelfTest/SwitchFlipChecks.cs"] + sorted(glob.glob(G + "Source/*.cs"))),
    "T_SHOCK_RULE_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/ShockRuleChecks.cs",
        observes="the who-is-shocked rule as a pure table: line kind (floor end, downed span, FlowWorks deck cord) x live by "
                 "power path at the last poll x setting (None, Only downed lines, All) x the pawn's job (fixing this line, "
                 "delivering to it, any other) x inside or outside the spark budget -> shocked or not; a cell two or more from "
                 "a live end and any dead end never shock; run by T_CORE",
        reads=[G + "Source/RM_MapComponent_CordGraph.cs"] + AERIAL),
    "T_CORD_GEOMETRY_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/CordGeometryChecks.cs",
        observes="on the oracle scenes and on the M2c junction-battery site as a lab world: every edge's drawn length is at "
                 "least 1.4 times its chord, every edge over four cells has an excursion of a cell or more, and no vertex turns "
                 "sharper than the bar unless a wall, building or socket forces it; a planted taut builder goes red; run by T_CORE",
        reads=CORE + [G + "Source/SelfTest/LabWorld.cs", G + "Source/SelfTest/oracle_scenes.json"]),
    # 0.1.1 (RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD): supports pole_buttons_show_icons, whose decider is the live log read
    "T_MAIN_THREAD_TEXTURES_OFFLINE": dict(
        stage="4-5", file=G + "selftest_gss_main_thread_textures.py",
        observes="no texture, material or graphic is fetched in a static field initializer, or in the static constructor of a class "
                 "without [StaticConstructorOnStartup], anywhere in Source (outside SelfTest); planted: the pre-fix icon fields go red",
        reads=sorted(glob.glob(G + "Source/**/*.cs", recursive=True))),
    "T_STATICS_CENSUS": dict(
        stage="4-5", file=G + "selftest_gss_statics_census.py",
        observes="every mutable static field in Source (outside SelfTest) is cleared in GssSessionReset.cs or listed immutable "
                 "with a reason; planted: a new static collection not reset goes red",
        reads=[G + "Source/GssSessionReset.cs"] + sorted(glob.glob(G + "Source/**/*.cs", recursive=True))),
    # 0.1.1 PATCH (his walk of 2026-11-20): transcribed from record.json proof_note of each new bar, nothing added
    "T_SWITCH_OFF_NODE_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/SwitchOffChecks.cs",
        observes="the mod selftest reads an off power switch as a node of the cord graph with both cords ending on its stubs: "
                 "no cut, live or dead end at the switch, on and off differing only in the powered look; planted: a switch "
                 "dropped from the graph when off goes red; run by T_CORE (bar switch_off_cords_stay_connected)",
        reads=[G + "Source/RM_MapComponent_CordGraph.cs"] + CORE),
    # added 2026-11-20 by his card (OWNER:1795244532644873616, "In 0.1.1"): RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED
    "T_SWITCH_LIGHT_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/SwitchLightChecks.cs",
        observes="the shipped lamp rule (Core/SwitchLight) over every side/power/state/setting case (4^4 sides x closed/open x setting) "
                 "and the brief's sequences (power lost while open, flick while unpowered, far side only, setting flip): green closed and "
                 "powered, red open and powered, dark unpowered or setting off; seven planted wrong rules (the base's no lamp, colours "
                 "swapped, open reads no side, one side only, setting ignored, hasPowerSource for active, unpowered open red) each caught "
                 "every run (bar switch_light_reads_state)",
        reads=[G + "Source/SwitchLightDraw.cs"] + CORE),
    # his walk of 2026-11-22 (station 3: "radical kinks ... it didn't have to bend that radically"): RIMMANDRAKE_SMOOTH_SLACK_GROUND_CORD_KINKS_AT_STATION_THREE
    "T_NO_KINK_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/KinkChecks.cs",
        observes="the production builder over the review map's ground-cord stations 1-4 (the probe's dump; station 3 is the build he walked) "
                 "and the region round station 3 (seeds x pile size x battery lead x lamp place x wall x pile look): no unforced kink "
                 "(a turn of 50 degrees or more within 0.12 cell that no wall, machine, art or cut end's curl excuses); planted: "
                 "the builder before CordShape.Unkink is caught at station 3, a planted hook reads as a kink and a 0.45 loop as none "
                 "(bar no_unforced_sharp_turn)",
        reads=CORE),
    "T_POLE_SOUTH_DRAWS_FRONT_OFFLINE": dict(
        stage="4-5", file=G + "selftest_gss_pole_south_draws_front.py",
        observes="over the SouthDrawsFront rule (MandrakePatches) and the mast def: the mast is drawn above every plant or "
                 "building north of it within its picture height and below one south of it; planted: the mast on its old "
                 "Building layer goes red (bar poles_draw_in_front_when_south)",
        reads=[G + "Defs/Aerial/RM_AerialAnchors.xml", G + "Source/Aerial/PoleGeometryTable.cs",
               "src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontKernel.cs",
               "src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontPatches.cs",
               "src/RimMandrake/MandrakePatches/selftest_south_draws_front.py"]
              + sorted(glob.glob(G + "Textures/RimMandrake/GimmeSomeSlack/Aerial/**/Aerial*Mast.png", recursive=True))),
    # ---- 0.2.0 MINOR (opened 2026-11-23, RIMMANDRAKE_OPEN_SLACK_NEXT_VERSION_SO_THREE_MODS_ADVANCE_TONIGHT): specified, Stage 3 builds each red first
    "T_LINE_RESTYLE_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/LineRestyleChecks.cs",
        observes="the run flood (ConduitStyles.Components over RM_MapComponent_ConduitRuns' neighbour rule) on generated lines of floor cords, "
                 "a power switch, two poles joined by an overhead span, a wall bracket, a hooked lamp and a FlowWorks pipe pole on the same "
                 "cells: All connected from each member kind takes every Gimme Some Slack member and no FlowWorks item; a cut span splits "
                 "the line in two; planted: a flood that stops at a pole, and one that takes the pipe pole, each go red (bar restyle_whole_line)",
        reads=[G + "Source/Aerial/ConduitStyles.cs", G + "Source/Aerial/RM_MapComponent_ConduitRuns.cs", G + "Source/Aerial/ConduitStylePicker.cs"]),
    "T_LOOK_ICONS_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/LookIconChecks.cs",
        observes="every look entry of the build menu's look choice and of the Restyle button takes its icon from the shared look-icon path "
                 "(UI/Looks/<Look>), the four pictures exist and differ; planted: a menu entry back on its strand art goes red (bar look_menu_icons)",
        reads=[G + "Source/Aerial/ConduitStylePicker.cs", G + "Source/Aerial/ConduitStyles.cs", G + "Textures/RimMandrake/GimmeSomeSlack/UI/Looks",
               G + "Source/SelfTest/Program.cs", "src/RimMandrake/Utils/selftest_gimmesomeslack.py"]),
    "T_WALL_LAMP_LOOKS_OFFLINE": dict(
        stage="4-5", file=G + "Source/SelfTest/WallLampLookChecks.cs",
        observes="WallLamp is a lamp def of the picker with one style def per look, each look's texture exists for every facing it draws, "
                 "the wall lamp follows its line as the standing lamp does, and the master switch off draws vanilla; planted: a look with a "
                 "missing facing goes red (bar wall_lamp_takes_looks)",
        reads=[G + "Source/Aerial/ConduitStyles.cs", G + "Source/Aerial/ConduitStylePicker.cs", G + "Source/Aerial/RM_MapComponent_ConduitRuns.cs",
               G + "Defs/Aerial/RM_ConduitStyles.xml", G + "Patches/RM_ConduitStyleable.xml"]
              + sorted(glob.glob(G + "Textures/RimMandrake/GimmeSomeSlack/Styles/*/WallLamp_*.png"))
              + [G + "Source/SelfTest/Program.cs", "src/RimMandrake/Utils/selftest_gimmesomeslack.py"]),
    "T_MAST_BEHIND_TALL_SOUTH_PICTURE_OFFLINE": dict(
        stage="4-5", file=G + "selftest_gss_mast_behind_tall_south_picture.py",
        observes="the reverse case of the south rule: a building whose picture reaches north into a mast just north of it draws in front of "
                 "the mast; the line APART BUILDING_LAYER_REACH of selftest_gss_pole_south_draws_front.py reads no pairs (1170 on "
                 "2026-11-22); planted: the building back on its own layer goes red (bar poles_draw_in_front_when_south; item "
                 "RIMMANDRAKE_ORDER_SLACK_MAST_BEHIND_TALL_SOUTHERN_PICTURES)",
        reads=[G + "selftest_gss_pole_south_draws_front.py", G + "Defs/Aerial/RM_AerialAnchors.xml",
               "src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/SouthDrawsFrontKernel.cs"]),
}

# the live checks of the three 0.2.0 scenes against a fake game (good game PASS, 8 planted wrong games FAIL, a blind probe never PASS)
OFF["T_LOOK_SCENES_FAKE_GAME"] = dict(stage="4-5", file=G + "selftest_gss_look_scenes.py", support_only=True,
    observes="sc_restyle_whole_line, sc_look_menu_icons and sc_wall_lamp_looks (northstar/scene_rows.py) on a fake game: every program-decided "
             "row PASS on the shipped behaviour; a flood stopping at the pole, a flood across the cut, lamps never following, a wall lamp "
             "not a lamp, a wall lamp on standing lamp art, the master switch ignored and a strand icon each read FAIL; a blind probe no PASS",
    reads=[G + "northstar/scene_rows.py", G + "validation.py"])

# ---- the judgment: which offline tests decide (or support) each bar ----
OFF_DECIDES = {
    "cords_lie_slack": ["T_CORE", "T_CORD_GEOMETRY_OFFLINE"], "no_unforced_sharp_turn": ["T_CORD_GEOMETRY_OFFLINE", "T_NO_KINK_OFFLINE"],
    "strip_at_every_junction": ["T_CORE"], "dense_block_tangle": ["T_CORE"], "cord_shape_variation_probe": ["T_CORE"],
    "cords_never_repeat": ["T_CORE"], "drawing_true_to_grid": ["T_CORE"], "cut_live_and_dead_ends": ["T_CORE"],
    "floor_end_shocks_crossers": ["T_SHOCK_RULE_OFFLINE"], "shock_reach_setting": ["T_SHOCK_RULE_OFFLINE"],
    "tap_steals_and_costs_goodwill": ["T_CORE"], "four_looks_one_run": ["T_CORE"],
    "settings_switch_cleanly": ["T_SETTINGS_SWEEP_OFFLINE"], "no_hose_in_gss": ["T_NO_HOSE"],
    # inventory rows
    "cord_slack_lay": ["T_CORE", "T_CORD_GEOMETRY_OFFLINE"], "junction_strips": ["T_CORE"], "connectivity_truth": ["T_CORE"],
    "break_ends_live_dead": ["T_CORE"], "power_theft": ["T_CORE"], "four_styles": ["T_CORE"],
    "mod_settings": ["T_SETTINGS_SWEEP_OFFLINE"], "pipe_pole_switch": ["T_CORE"], "no_hose": ["T_NO_HOSE"],
    "floor_end_shock": ["T_SHOCK_RULE_OFFLINE"],
    # added by his card 2026-11-14 (OWNER:1794693278631337978): T_CORE's slideunder "under" check (cord layer below Building)
    "cords_draw_under_things": ["T_CORE"],
    # added 2026-11-16 under the lock rule (RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK)
    "cords_join_stubs_on_position_and_slope": ["T_STUB_JOINS", "T_STUB_ART_CENSUS"],
    # 0.1.1 PATCH bars (record.json proof_note): the offline halves; the live halves are added with the scenes below
    "switch_off_cords_stay_connected": ["T_SWITCH_OFF_NODE_OFFLINE"],
    "poles_draw_in_front_when_south": ["T_POLE_SOUTH_DRAWS_FRONT_OFFLINE"],
    # added 2026-11-20 by his card (OWNER:1795244532644873616); the live half sc_switch_light is added with the scenes below
    "switch_light_reads_state": ["T_SWITCH_LIGHT_OFFLINE"],
    # 0.2.0 MINOR bars (record.json proof_note); the live halves are added with the scenes below
    "restyle_whole_line": ["T_LINE_RESTYLE_OFFLINE"],
    "look_menu_icons": ["T_LOOK_ICONS_OFFLINE"],
    "wall_lamp_takes_looks": ["T_WALL_LAMP_LOOKS_OFFLINE"],
}
OFF_DECIDES["poles_draw_in_front_when_south"].append("T_MAST_BEHIND_TALL_SOUTH_PICTURE_OFFLINE")
OFF_SUPPORTS = {
    "restyle_whole_line": ["T_LOOK_SCENES_FAKE_GAME"], "look_menu_icons": ["T_LOOK_SCENES_FAKE_GAME"],
    "wall_lamp_takes_looks": ["T_LOOK_SCENES_FAKE_GAME"],
    "conduit_invisible": ["T_GATE"], "cords_lie_slack": ["T_MATRIX", "T_END_HEAP"], "cords_meet_walls_at_face": ["T_CORE", "T_END_HEAP"],
    "strip_at_every_junction": ["T_JUNCTION_ART", "T_STRIP_ART"], "dense_block_tangle": ["T_MATRIX"],
    "drawing_true_to_grid": ["T_MATRIX"], "no_stall_on_rewire": ["T_CORE"], "spans_above_everything": ["T_CORE", "T_FW_PIT_DRAW_CENSUS"],
    "fallen_span_on_ground": ["T_CORE"], "fallen_wire_shocks_crossers": ["T_SHOCK_OUTLIVES", "T_SHOCK_OUTLIVES_BINDING",
                                                                         "T_SHOCK_BITES_BINDING", "T_SHOCK_RULE_OFFLINE"],
    "four_looks_one_run": ["T_GATE", "T_JUNCTION_ART"], "settings_switch_cleanly": ["T_CORE", "T_GATE"],
    "statics_clear_between_games": ["T_STATICS_CENSUS"], "game_statics_reset": ["T_STATICS_CENSUS"],
    "cord_slack_lay": ["T_END_HEAP", "T_MATRIX"], "junction_strips": ["T_JUNCTION_ART", "T_STRIP_ART"],
    "connectivity_truth": ["T_MATRIX"], "rebuild_cost": ["T_CORE"], "overhead_spans": ["T_CORE"], "downed_spans": ["T_CORE"],
    "fallen_wire_shock": ["T_SHOCK_OUTLIVES", "T_SHOCK_OUTLIVES_BINDING", "T_SHOCK_BITES_BINDING", "T_SHOCK_RULE_OFFLINE"],
    "mod_settings": ["T_CORE", "T_GATE"], "four_styles": ["T_GATE", "T_JUNCTION_ART"], "shock_reach_setting": [],
    "cords_draw_under_things": ["T_FW_PIT_DRAW_CENSUS"],
    "pole_buttons_show_icons": ["T_MAIN_THREAD_TEXTURES_OFFLINE"],
}
for k, (_f, _o, bars) in HARNESS.items():
    for b in bars:
        OFF_SUPPORTS.setdefault(b, []).append(k)

# held look statements (validation_holding), placed by hand
H = "design/RimMandrake/validation_holding/"
HELD = [
    dict(file=H + "owner_look_defects_2026-11-12.md", row=34,
         words="Here is a screenshot of a GSS connector unfortunately showing up through the battery it should be beneath in a pit.",
         bars=["cords_draw_under_things"], test="T_CORE (slideunder: under) + T_FW_PIT_DRAW_CENSUS + sc_cords_under_items (in scenes.json since 2026-11-14)",
         stage="4-5 then 6", kind="defect; offline checks (run today) + in-game draw-order read (owed); bar added by his card 2026-11-14"),
    dict(file=H + "owner_look_defects_2026-11-12.md", row=36,
         words="The wires are also above the items and furniture otherwise, likely all the same problem.",
         bars=["cords_draw_under_things"], test="T_CORE (slideunder: under) + sc_cords_under_items (in scenes.json since 2026-11-14)",
         stage="4-5 then 6", kind="as row 34"),
    dict(file=H + "owner_look_defects_2026-11-13.md", row=16,
         words="[Image #8] Also, the GSS cables are now correctly below the items.",
         bars=["cords_draw_under_things"], test="sc_cords_under_items (in scenes.json since 2026-11-14) keeps it so",
         stage="6", kind="approval: the regression the in-game read guards; bar added by his card 2026-11-14"),
    dict(file="infrastructure/state/ledger/events/OWNER.jsonl", row="OWNER:1795233641482676326",
         words="You know with respect to the switch issue with gss showing disconnection the switch should have some illuminated indicator on "
               "it showing whether it is open or closed but always powered (green Vs red) vs unpowered (no glow). That would help with the "
               "user awareness part. Please make that so.",
         bars=["switch_light_reads_state"], test="T_SWITCH_LIGHT_OFFLINE + sc_switch_light", stage="4-5 then 6",
         kind="request, 0.1.1: bar added by his card 2026-11-20 (OWNER:1795244532644873616)"),
    dict(file="infrastructure/state/ledger/events/OWNER.jsonl", row="OWNER:1795387443867018723",
         words="Both Flow Works need the \"change everything on this line\" (for flow works items) and GSS needs \"change everything on this "
               "line\" (for GSS items). They don't need to change each other's items though. Each mod can handle only its own, that's ok.",
         bars=["restyle_whole_line"], test="T_LINE_RESTYLE_OFFLINE + sc_restyle_whole_line", stage="4-5 then 6",
         kind="request, 0.2.0 MINOR: bar restyle_whole_line"),
]

W = H + "gss_walk_20261120.md"  # his walk of 2026-11-20, "His points" table; the class column is the walk record's
_WALK = [  # row, bars, kind
    (1, ["switch_off_cords_stay_connected"], "defect; 0.1.1 bar (RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT)"),
    (2, ["four_looks_one_run"], "approval"), (3, ["four_looks_one_run"], "approval"),
    (4, ["fallen_span_on_ground", "downed_spans"], "approval"),
    (5, [], "art of another mod: RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS (Explosive Knockback), no GSS bar"),
    (6, ["no_unforced_sharp_turn", "cords_lie_slack"], "approval"),
    (7, [], "request, next version: RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS (VERSION.json caveats)"),
    (8, ["junction_strips", "cords_join_stubs_on_position_and_slope"], "approval"),
    (9, ["pole_buttons_show_icons"], "defect; 0.1.1 bar (RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD)"),
    (10, ["look_menu_icons"], "request; 0.2.0 bar look_menu_icons (RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU)"),
    (11, [], "request; the battery's home is Machine Looks by the design pass (design/specs/2026-11-20-vanilla-electrical-art-home/design.md), not a GSS bar: RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP"),
    (12, [], "art, held by RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART"),
    (13, ["poles_draw_in_front_when_south"], "defect; 0.1.1 bar (RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH)"),
    (14, ["no_roof_over_pole"], "defect; 0.1.1 bar (RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT)"),
    (15, ["wall_lamp_takes_looks"], "request; the wall lamp is a 0.2.0 bar (wall_lamp_takes_looks); the other machines go to Machine Looks (RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART)"),
    (16, [], "approval of the whole mod: the 0.1.0 pass (e1d9c3c042)"),
]
for _r, _b, _k in _WALK:
    HELD.append(dict(file=W, row=_r, words="row %d of the walk record's His points table" % _r, bars=_b,
                     test=" + ".join(OFF_DECIDES.get(b, ["(the bar's own deciders)"])[0] for b in _b) if _b else "-",
                     stage="4-5 then 6" if _b else "-", kind=_k))

CORRECTIONS = [  # rm-coverage-judge-1794599377's five gaps; needles are text the fix put in scenes.json
    ("g1", "sc_floor_end_shock", ["at least two cells from its end"]),
    ("g2", "sc_floor_end_shock|sc_fuel_ignition|sc_shock_reach",
     ["the player stopped laying", "steel stacked out of the way", "chemfuel puddle", "maxSparkingEnds to 1", "FlowWorks"]),
    ("g3", "sc_no_sharp_turn", ["at least 1.4 times its chord"]),
    ("g4", "sc_owner_change", ["a fourth mast of ours spanned to the first"]),
    ("g5", "sc_statics_new_game", ["SectionLayer_RM_MessyCords.PrintedStatic", "RM_LiveWirePathCost"]),
]


def run(cmd, timeout=900):
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        lines = [l for l in (r.stdout + r.stderr).strip().splitlines() if not l.startswith("GATE_JSON")]
        return dict(ran=True, rc=r.returncode, seconds=round(time.time() - t, 2), last=(lines[-1][:200] if lines else ""),
                    at=NOW, result="PASS" if r.returncode == 0 else "FAIL")
    except subprocess.TimeoutExpired:
        return dict(ran=True, rc=None, seconds=round(time.time() - t, 2), last="timeout", at=NOW, result="FAIL")


PREV = {}
if "--reuse" in sys.argv:  # re-render from the last measured run instead of running every test again
    PREV = json.load(open(C + "version/test_table.json"))["tests"]
tests = {}
for k, t in OFF.items():
    cmd = [sys.executable, t["file"]] + t.get("args", [])
    row = dict(id=k, kind="offline", stage=t["stage"], file=t["file"], observes=t["observes"], reads=t["reads"],
               command="python3 " + " ".join([t["file"]] + t.get("args", [])))
    if t.get("support_only"):
        row["support_only"] = True
    row["runs_today"] = PREV[k]["runs_today"] if k in PREV else run(cmd)
    tests[k] = row
    print(k, row["runs_today"]["result"], row["runs_today"]["seconds"], flush=True)
# Stage 3 (2026-11-14) built all four: a .py runs on its own; a SelfTest .cs is run by T_CORE (or, known red, under --geometry)
NEW_CMD = {"T_CORD_GEOMETRY_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--geometry"],
           "T_SWITCH_OFF_NODE_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py"],
           "T_SWITCH_LIGHT_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--no-export", "--switchlight-only"],
           "T_NO_KINK_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--no-export", "--kinks-only"],
           "T_SHOCK_RULE_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py"],
           # 0.2.0: a SelfTest .cs is run by T_CORE once Stage 3 writes it
           "T_LINE_RESTYLE_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py"],
           # built 2026-11-23 (RIMMANDRAKE_FINISH_SLACK_ICON_LAMP_CHECKS_CAPPED_AT_HALF): both run alone under --looks-only
           "T_LOOK_ICONS_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--no-export", "--looks-only"],
           "T_WALL_LAMP_LOOKS_OFFLINE": ["src/RimMandrake/Utils/selftest_gimmesomeslack.py", "--no-export", "--looks-only"]}
for k, t in NEW.items():
    argv = NEW_CMD.get(k) or [t["file"]]
    row = dict(id=k, kind="offline", stage=t["stage"], file=t["file"], observes=t["observes"], reads=t["reads"], new=True,
               built_in_stage="3", command="python3 " + " ".join(argv))
    if not os.path.exists(t["file"]):
        row["runs_today"] = dict(ran=False, why="specified, not built: Stage 3 builds it failing first")
    elif k in PREV and PREV[k]["runs_today"].get("ran"):
        row["runs_today"] = PREV[k]["runs_today"]
    elif k == "T_SHOCK_RULE_OFFLINE" and "T_CORE" in tests:
        row["runs_today"] = dict(tests["T_CORE"]["runs_today"], via="T_CORE")
    else:
        row["runs_today"] = run([sys.executable] + argv)
    tests[k] = row
    print(k, row["runs_today"].get("result"), row["runs_today"].get("seconds"), flush=True)

# in-game scenes: entry named in scenes.json; exists only if the function is defined there
# the removal check loads a save WITHOUT GSS, so it runs on tier bridge (RIMMANDRAKE_PIN_SLACK_REMOVAL_CHECK_BRIDGE_TIER_NOT_GSS)
SCENE_TIER = {"sc_settings": "gimmesomeslack_flowworks", "sc_shock_reach": "gimmesomeslack_flowworks",
              "sc_removal_consequence": "bridge",
              # it reads SC_under_liquid_pit, which asks only with FlowWorks loaded, as sc_cords_under_items does
              "sc_true_to_grid": "gimmesomeslack_flowworks"}
TIER_STAGE = {"quicktest": "6", "live_minimal": "6", "live_full": "6", "offline": "4-5"}
TIER_KIND = {"quicktest": "live_minimal", "live_minimal": "live_minimal", "live_full": "live_full"}
for s in scn["scenes"]:
    ep = s.get("entry_point") or ""
    f, _, fn = ep.partition("::")
    exists = bool(fn) and os.path.exists(f) and re.search(r"^\s*def %s\(" % re.escape(fn), open(f).read(), re.M) is not None
    tiers = [LEAF[r]["tier_proposed"] for r in s.get("requirement") or [] if r in LEAF]
    tier = "live_full" if "live_full" in tiers else "live_minimal" if "live_minimal" in tiers else "quicktest"
    reasons = [LEAF[r]["tier_reason"] for r in s.get("requirement") or [] if r in LEAF and LEAF[r].get("tier_reason")]
    why = "; ".join(reasons) or {"sc_shock_restring": "pawn jobs, the re-string job and shock damage are live behaviour",
                                 "sc_removal_consequence": "removing a mod from a save needs the game to load that save"}.get(s["id"], "")
    row = dict(id=s["id"], kind=TIER_KIND[tier], stage=TIER_STAGE[tier], file=f, entry=fn, entry_exists=exists,
               observes=s.get("expect", "")[:300], reads=[f, C + "scenes.json"],
               command="python.exe %s --scene %s   (minimal list; entry ABSENT)" % (f.replace("/", "\\"), fn) if not exists else f,
               why_game=why, item=s.get("entry_point_item"),
               runs_today=dict(ran=False, why="live: this run is offline only; entry %s in the code" % ("exists" if exists else "ABSENT")))
    if tier == "live_full":
        row["why_full_list"] = why
    # the test mod list it runs on (modset_builder.TIERS); the two FlowWorks scenes run on GSS+FlowWorks (Stage 3, 2026-11-14)
    row["tier"] = SCENE_TIER.get(s["id"], "gimmesomeslack")
    tests[s["id"]] = row
tests["sc_cords_under_items"] = dict(
    id="sc_cords_under_items", kind="live_minimal", stage="6", tier="gimmesomeslack_flowworks", file=G + "validation.py", entry="scene_cords_under_items",
    entry_exists=True, new=True, observes="a floor cord under a battery, a shelf of items and furniture, dry and in a FlowWorks pit: "
    "the cord's draw altitude and queue read below the thing's, the junction piece too; the control is offline: planted reads (a cord over steel, a battery queued first) go red in northstar/selftest_gss_cords_under_items.py; a live debug flag only to prove the instrument is left out, as scene_rows does",
    reads=[G + "Source/CordUnderLiquid.cs", G + "Source/SectionLayer_RM_MessyCords.cs"], held=True,
    why_game="draw order is a property of the running renderer; the offline census proves the routing, not the drawn result",
    command="python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\proof_all.py --live --no-shots (tier gimmesomeslack_flowworks for its pit row), then "
            "python3 src/RimMandrake/GimmeSomeSlack/validation.py --scenes-from <proof result json>",
    runs_today=dict(ran=False, why="UNRUN: offline only, never the game in this run; entry built 2026-11-14 (scene_rows.cords_under_items, probe under:), "
                                   "its offline half northstar/selftest_gss_cords_under_items.py green, its pit row a Stage 6 driver"))
tests["sc_stub_joins"] = dict(
    id="sc_stub_joins", kind="live_minimal", stage="6", tier="gimmesomeslack", file=G + "northstar/live_stub_joins.py", entry="main",
    entry_exists=True, new=True, observes="on his review map (save GSS_OWNER_LOOK_20261116) the probe joins: runs Core/StubJoinAudit on the live "
    "pieces of every station: stubs off line or slope, bare stubs, live ends turning or pinched at the join, wall/rock dead ends drawn loose",
    reads=[G + "Source/GimmeSomeSlackProbe.cs", G + "Source/Core/StubJoinAudit.cs"],
    why_game="the drawn pieces come from the running map's graph, looks and settings, not a generated scene",
    command="python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_stub_joins.py (game up on the gimmesomeslack tier, bridge held)",
    runs_today=dict(ran=False, why="live: see the item's notes for its last run"))
# 0.1.1 PATCH live halves, from record.json proof_note; entries do not exist yet (Stage 3 builds each, red first)
NEW_LIVE = {
    "sc_switch_off_ends": ("switch_off_cords_stay_connected", "scene_switch_off_ends",
        "the AerialProbe ends:/endkind: probe on an off power switch finds no live or dead cut end within 1.5 cells of it",
        [G + "Source/Aerial/AerialProbe.cs", G + "Source/RM_MapComponent_CordGraph.cs"],
        "the cord pieces at a switch come from the running map's graph and its live power state"),
    "sc_pole_icons_loaded": ("pole_buttons_show_icons", "scene_pole_icons_loaded",
        "after a cold load Player.log holds no 'Tried to get a resource ... from a different thread' line for "
        "UI/Commands/TryReconnect, UI/Designators/Cancel or any Gimme Some Slack path, and the three pole button icons "
        "(Link wire, Unlink wire, Unlink all) are non-null",
        [G + "Source/Aerial/CompAerialAnchor.cs"],
        "the thread a texture loads on and the icon it yields exist only in the running game's load; Player.log after a "
        "cold load is the instrument"),
    "sc_pole_south_of_tree": ("poles_draw_in_front_when_south", "scene_pole_south_of_tree",
        "a capture of a pole south of a tree and one north of it: the south pole is drawn in front, the north one behind",
        [G + "Defs/Aerial/RM_AerialAnchors.xml"],
        "draw order is a property of the running renderer; the offline read proves the layer, not the drawn result"),
    "sc_no_roof_over_pole": ("no_roof_over_pole", "scene_no_roof_over_pole",
        "auto-roof and a build-roof designation over a mast cell form no roof and the refusal names the pole; a "
        "god-mode roof still cuts the spans",
        [G + "Defs/Aerial/RM_AerialAnchors.xml", G + "Source/Aerial/PlaceWorkers_Aerial.cs"],
        "auto-roof, the roof designator and a god-mode roof run in the live game's roof systems"),
    "sc_switch_light": ("switch_light_reads_state", "scene_switch_light",
        "two batteries, an in-line power switch: the GSS probe switchlights reads the lamp dark with no power, green closed and "
        "powered, red open and powered, dark after the power is lost while open, red with power on the far side only, and dark "
        "with the switchLight setting off (fake-game proof: selftest_gss_switch_light_scene.py)",
        [G + "Source/SwitchLightDraw.cs", G + "Source/GimmeSomeSlackProbe.cs"],
        "the lamp reads the running map's power nets (PowerNetManager rebuilds them on the tick after a flick or a battery change)"),
    # 0.2.0 MINOR (opened 2026-11-23): entries ABSENT until Stage 3 writes them; UNRUN until Stage 6
    "sc_restyle_whole_line": ("restyle_whole_line", "scene_restyle_whole_line",
        "a line of floor cords, a power switch, two poles with an overhead span, a wall bracket and a hooked lamp, all Industrial: "
        "All connected on the far pole to Futuristic; the GSS probe cstyles reads every piece, the span and the lamp Futuristic; then a "
        "cut span and All connected on one side to Modern leaves the other side Futuristic",
        [G + "Source/Aerial/ConduitStyleProbe.cs", G + "Source/Aerial/RM_MapComponent_ConduitRuns.cs", G + "northstar/scene_rows.py"],
        "a run is worked out from the running map (things, spans and their Up state); only the live map has them"),
    "sc_look_menu_icons": ("look_menu_icons", "scene_look_menu_icons",
        "a capture of the build menu's look choice and of the Restyle menu: each look shows its own icon, the same picture in both menus",
        [G + "Source/Aerial/ConduitStylePicker.cs", G + "Source/Aerial/ConduitStyleProbe.cs", G + "northstar/scene_rows.py"],
        "a float menu and its icons are drawn only by the running game's UI"),
    "sc_wall_lamp_looks": ("wall_lamp_takes_looks", "scene_wall_lamp_looks",
        "wall lamps on a wall in each look beside a standing lamp, captured at play zoom; a restyle of the line they hook to repaints "
        "them as it does the standing lamp; the master switch off draws vanilla wall lamps without a restart",
        [G + "Source/Aerial/ConduitStyles.cs", G + "Source/Aerial/ConduitStyleProbe.cs", G + "northstar/scene_rows.py"],
        "the drawn picture of a style def exists only in the running renderer"),
}
for sid, (bid, fn, obs, rd, why) in NEW_LIVE.items():
    f = G + "validation.py"
    exists = re.search(r"^\s*def %s\(" % re.escape(fn), open(f).read(), re.M) is not None
    tests[sid] = dict(id=sid, kind="live_minimal", stage="6", tier="gimmesomeslack", file=f, entry=fn, entry_exists=exists,
                      new=True, observes=obs, reads=rd, why_game=why, for_bar=bid,
                      command="python.exe %s --scene %s   (minimal list; entry %s)" % (f.replace("/", "\\"), fn, "exists" if exists else "ABSENT"),
                      runs_today=dict(ran=False, why="live: offline-only run; entry %s in the code" % ("exists" if exists else "ABSENT")))
    OFF_DECIDES.setdefault(bid, []).append(sid)
tests["LOOK_STAGE8"] = dict(id="LOOK_STAGE8", kind="look", stage="8", file=None, entry=None, entry_exists=False,
                            observes="his walk of a scavenger base on his full list, with a mid-way reload",
                            reads=[C + "sheet.md", C + "version/vision.md"], why_game="his eye is the instrument",
                            runs_today=dict(ran=False, why="his walk"))

# proof_all rows: older live rows, evidence for leaves (proof_leaves.ROW_LEAVES); last full run 2026-11-13
LAST = "J20261113T075443Z-3da526 (SteveDesktop, 35aaf354ea, 2026-11-13): 156 rows, 154 PASS, FAIL M2c_no_sharp_bends and SC_no_two_cords_alike (ledger, BENCH shard)"
LAST_FAIL = {"M2c_no_sharp_bends", "SC_no_two_cords_alike"}
PY = {p: open(p).read() for p in glob.glob(G + "*.py") + glob.glob(G + "northstar/*.py") + glob.glob(G + "northstar_matrix/*.py")}
OFFLINE_ROWS = {"O1_mod_files", "O2_settings_defaults", "O3_core_selftest", "O3n_selftest_can_fail", "O4_python_oracle",
                "O5_style_art_sane", "O6_review_round1", "O7_gpt_read_fixes", "O8_lamp_mast_vanilla_register", "selftest_gss_no_hose"}
for rid, leaves in proof_leaves.ROW_LEAVES.items():
    if rid in OFFLINE_ROWS:
        continue
    key = rid[3:] if rid.startswith("MX_") else rid
    where = [p for p, s in PY.items() if key in s and p != G + "northstar/proof_leaves.py"]
    gs = rid.startswith("GS1_")
    tests["P_" + rid] = dict(
        id="P_" + rid, kind="live_minimal", stage="6", file=(where[0] if where else None), entry=rid, entry_exists=bool(where),
        observes="older proof row, evidence for %s (proof_leaves.ROW_LEAVES), not the scene contract" % ", ".join(leaves),
        reads=where[:3], support_only=True, leaves=leaves,
        command="python3 %snorthstar/%s" % (G, "gravship_scene.py" if gs else "proof_all.py --live"),
        why_game="a live state read through the bridge on the gimmesomeslack tier",
        runs_today=dict(ran=False, why="live: offline-only run", last_live=("FAIL" if rid in LAST_FAIL else "PASS") + " in " + LAST
                        if not gs else "PASS (gravship_scene on/off, same job)"))

# ---- carry: tests a later run added to the committed table by hand (this script does not make them) stay, with every
# bar's support of them; regenerating without this dropped six offline tests (2026-11-20, steward run of 0.1.1 preflight)
_committed = json.load(open(C + "version/test_table.json"))
CARRIED = sorted(k for k in _committed["tests"] if k not in tests)
for k in CARRIED:
    tests[k] = _committed["tests"][k]
for _b in _committed["bars"]:
    for _s in _b["supports"]:
        if _s in CARRIED:
            OFF_SUPPORTS.setdefault(_b["id"], []).append(_s)
    for _d in _b["decides"]:
        if _d in CARRIED:
            OFF_DECIDES.setdefault(_b["id"], []).append(_d)
print("carried from the committed table:", ", ".join(CARRIED) or "none", flush=True)

# ---- bars ----
checklist = {r["id"]: r for r in verdict["checklist"]}
scenes_for_leaf = {}
for s in scn["scenes"]:
    for r in s.get("requirement") or []:
        scenes_for_leaf.setdefault(r, []).append(s["id"])
for s in scn["scenes"]:  # interaction / exploration scenes support the bars the verdict cites them for
    pass
rows_for_leaf = {}
for rid, leaves in proof_leaves.ROW_LEAVES.items():
    if "P_" + rid in tests:
        for l in leaves:
            rows_for_leaf.setdefault(l, []).append("P_" + rid)


def runnable(tid):
    t = tests[tid]
    if t["kind"] == "offline":
        return t["runs_today"].get("ran", False)
    return bool(t.get("entry_exists"))


def held_for(bid):
    return ["%s#%s" % (os.path.basename(h["file"]), h["row"]) for h in HELD if bid in h["bars"]]


bars = []
ids = list(dict.fromkeys([i["id"] for i in rec["inventory"]] + [l["id"] for l in tree["leaves"]]))
for bid in ids:
    is_leaf = bid in LEAF
    src = "tree.json" + (" + record.json" if bid in INV else "") if is_leaf else "record.json"
    kind = LEAF[bid]["leaf_kind"] if is_leaf else "inventory"
    if is_leaf:
        sc = scenes_for_leaf.get(bid, [])
    else:
        # a judge's `scene` may be free text ("workshop showcase sc_cords_slack"): the scene ids it names
        sc = list(dict.fromkeys(s for p in checklist.get(bid, {}).get("parts", [])
                                for s in re.findall(r"\bsc_[a-z0-9_]+", p.get("scene") or "") if s in SCENE))
    decides = list(dict.fromkeys(OFF_DECIDES.get(bid, []) + sc))
    if kind == "walk":
        decides.append("LOOK_STAGE8")
    if bid == "cords_draw_under_things":  # his card 2026-11-14: the in-game draw-order read decides, his walk supports
        decides.append("sc_cords_under_items")
    if bid == "cords_join_stubs_on_position_and_slope":  # 2026-11-16: the live read on his review map decides with the offline sweep
        decides.append("sc_stub_joins")
    leaves_here = [bid] if is_leaf else sorted({r for s in sc for r in (SCENE[s].get("requirement") or [])})
    sup = list(OFF_SUPPORTS.get(bid, []))
    for l in leaves_here:
        sup += rows_for_leaf.get(l, [])
    if bid in ("drawing_true_to_grid", "walk_scavenger_base"):
        sup.append("sc_cords_under_items")
    if bid == "cords_draw_under_things":
        sup.append("LOOK_STAGE8")
    sup = [s for s in dict.fromkeys(sup) if s not in decides]
    if not decides:
        decides = []
    stages = [tests[t]["stage"] for t in decides]
    order = {"2": 2, "4-5": 4, "6": 6, "8": 8}
    proves_at = max(stages, key=lambda s: order[s]) if stages else None
    off_dec = [t for t in decides if tests[t]["kind"] == "offline"]
    bars.append(dict(
        id=bid, source=src, kind=kind, proves_at=proves_at, decides=decides, supports=sup, held=held_for(bid),
        offline_decides=off_dec,
        offline_green_today=bool(off_dec) and all(tests[t]["runs_today"].get("result") == "PASS" for t in off_dec),
        every_decider_runnable_today=bool(decides) and all(runnable(t) for t in decides),
        any_test_runnable_today=any(runnable(t) for t in decides + sup),
        any_decider_runnable_today=any(runnable(t) for t in decides)))

corr = []
S_TXT = {s["id"]: json.dumps(s) for s in scn["scenes"]}
for gid, where, needles in CORRECTIONS:
    hay = " ".join(S_TXT.get(w, "") for w in where.split("|"))
    corr.append(dict(gap=gid, where=where, needles=needles, present=all(n in hay for n in needles),
                     status="applied 910f69411e (Designer run rm-role-designer-1794600246); no judge has read it since"))

out = dict(
    mod="GimmeSomeSlack", version=json.load(open(C + "version/VERSION.json"))["version"], made=NOW,
    made_by="rm-builder, Maturation hand run beside the pilot, row 2 (throwaway version/make_test_table.py)",
    stages={"2": "preflight (a program)", "4-5": "blind offline challenge and game-logic testing", "6": "in-game acceptance",
            "8": "his live walk"},
    rule="a bar passes when every test in decides passes; proves_at is the highest stage among them; supports add evidence "
         "but decide nothing",
    text_read="the bars as committed at 910f69411e (tree hash 5e3aa0d4), the text present at his lock word; bars.md pins "
              "237b791167 (journal question 1)",
    settings_move="settings_switch_cleanly and mod_settings: the flip-and-return of every switch and the patch-to-switch map "
                  "are decided offline by T_SETTINGS_SWEEP_OFFLINE (specified); T_CORE already flips the aerial switches and "
                  "the pipe-pole kind rule offline (SwitchFlipChecks). sc_settings keeps only what needs the renderer and the "
                  "live Harmony instance: master off and on restoring vanilla conduit and lamp art without a restart, and the "
                  "applied-patch list read at runtime. The leaf's text is not edited.",
    held_statements=HELD, corrections=corr, tests=tests, bars=bars)
json.dump(out, open(C + "version/test_table.json", "w"), indent=1)

# ---- read view ----
def rt(t):
    r = t["runs_today"]
    if r.get("ran"):
        return "%s rc=%s %ss" % (r["result"], r["rc"], r["seconds"])
    if t["kind"] == "offline":
        return "SPECIFIED"
    return "entry %s" % ("exists" if t.get("entry_exists") else "ABSENT")


n = len(bars)
off_built = [t for t in tests.values() if t["kind"] == "offline" and not t.get("new")]
scenes_t = [t for t in tests.values() if t["id"].startswith("sc_")]
prows = [t for t in tests.values() if t["id"].startswith("P_")]
cnt = [
    "bars: %d" % n,
    "with a deciding test runnable today (an offline test that ran, or an in-game scene whose entry exists): %d" % sum(b["any_decider_runnable_today"] for b in bars),
    "with every deciding test runnable today: %d" % sum(b["every_decider_runnable_today"] for b in bars),
    "with at least one test of any kind runnable today, supports included (proof rows whose code exists count): %d" % sum(b["any_test_runnable_today"] for b in bars),
    "with an offline deciding test, all green today: %d" % sum(b["offline_green_today"] for b in bars),
    "decided offline only (no game needed): %d" % sum(1 for b in bars if b["proves_at"] in ("2", "4-5")),
    "in-game scenes: %d named in scenes.json plus %d specified here; entry exists %d, absent %d" % (
        sum(not t.get("new") for t in scenes_t), sum(bool(t.get("new")) for t in scenes_t), sum(t["entry_exists"] for t in scenes_t),
        sum(not t["entry_exists"] for t in scenes_t)),
    "older proof rows (supports): %d mapped in proof_leaves.ROW_LEAVES (%d of them gravship_scene), code found for %d; last live "
    "run %s; mapped rows and run rows not reconciled one to one" % (len(prows), sum(t["id"].startswith("P_GS1") for t in prows),
                                                                    sum(t["entry_exists"] for t in prows), LAST),
    "offline tests: %d built before Stage 3 (ran today: %d PASS, %d FAIL); %d specified at the lock, built in Stage 3: %s" % (
        len(off_built), sum(t["runs_today"]["result"] == "PASS" for t in off_built),
        sum(t["runs_today"]["result"] != "PASS" for t in off_built), len(NEW),
        ", ".join("%s %s%s" % (k, tests[k]["runs_today"].get("result") or "NOT BUILT",
                               " (known red, %s)" % tests[k]["known_red"] if tests[k].get("known_red") else "") for k in NEW)),
]
L = ["# Gimme Some Slack %s: test-and-stage table" % out["version"], "",
     "Generated %s from `test_table.json` (the record; this is its read view) by the throwaway `make_test_table.py`. Stages: 2 "
     "preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes. Columns follow "
     "Explosive Knockback's table." % NOW, "", "## Counts (measured)", ""] + ["- " + c for c in cnt] + [
     "", "## Bars", "", "| bar | from | proves at | decides | supports (not proof rows) | proof rows | runnable today |", "|---|---|---|---|---|---|---|"]
for b in bars:
    sp = [s for s in b["supports"] if not s.startswith("P_")]
    pr = [s for s in b["supports"] if s.startswith("P_")]
    rn = "all" if b["every_decider_runnable_today"] else "some" if b["any_decider_runnable_today"] else "none"
    L.append("| `%s` | %s | %s | %s | %s | %d | %s |" % (b["id"], b["source"].split(".")[0] if "+" not in b["source"] else "both",
             b["proves_at"], ", ".join(b["decides"]) or "-", ", ".join(sp) or "-", len(pr), rn))
L += ["", "## Tests (offline and scenes; the %d proof rows are in the JSON)" % len(prows), "",
      "| test | stage | kind | file :: entry | runs today | observes |", "|---|---|---|---|---|---|"]
for t in tests.values():
    if t["id"].startswith("P_"):
        continue
    L.append("| `%s` | %s | %s | `%s`%s | %s | %s |" % (t["id"], t["stage"], t["kind"], t["file"], (" :: " + t["entry"]) if t.get("entry") else "",
             rt(t), t["observes"][:160].replace("|", "/")))
L += ["", "## Held look statements placed", ""]
for h in HELD:
    L.append("- `%s` row %s, \"%s\" -> bars %s; test %s (stage %s, %s)" % (h["file"], h["row"], h["words"], ", ".join(h["bars"]), h["test"], h["stage"], h["kind"]))
L += ["", "## The five judge corrections (rm-coverage-judge-1794599377), checked against the current text", ""]
for c in corr:
    L.append("- %s (%s): text present %s; %s" % (c["gap"], c["where"], c["present"], c["status"]))
L += ["", "## The settings sweep, moved offline", "", out["settings_move"], ""]
open(C + "version/test_table.md", "w").write("\n".join(L))
print("\n".join(cnt))
