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
    "T_STATICS_CENSUS": dict(
        stage="4-5", file=G + "selftest_gss_statics_census.py",
        observes="every mutable static field in Source (outside SelfTest) is cleared in GssSessionReset.cs or listed immutable "
                 "with a reason; planted: a new static collection not reset goes red",
        reads=[G + "Source/GssSessionReset.cs"] + sorted(glob.glob(G + "Source/**/*.cs", recursive=True))),
}

# ---- the judgment: which offline tests decide (or support) each bar ----
OFF_DECIDES = {
    "cords_lie_slack": ["T_CORE", "T_CORD_GEOMETRY_OFFLINE"], "no_unforced_sharp_turn": ["T_CORD_GEOMETRY_OFFLINE"],
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
}
OFF_SUPPORTS = {
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
}
for k, (_f, _o, bars) in HARNESS.items():
    for b in bars:
        OFF_SUPPORTS.setdefault(b, []).append(k)

# held look statements (validation_holding), placed by hand
H = "design/RimMandrake/validation_holding/"
HELD = [
    dict(file=H + "owner_look_defects_2026-11-12.md", row=34,
         words="Here is a screenshot of a GSS connector unfortunately showing up through the battery it should be beneath in a pit.",
         bars=["drawing_true_to_grid", "walk_scavenger_base"], test="T_FW_PIT_DRAW_CENSUS + sc_cords_under_items (specified)",
         stage="4-5 then 6", kind="offline census (runs today) + in-game draw-order read (specified; no bar of the 47 says it, see journal question 2)"),
    dict(file=H + "owner_look_defects_2026-11-12.md", row=36,
         words="The wires are also above the items and furniture otherwise, likely all the same problem.",
         bars=["drawing_true_to_grid", "walk_scavenger_base"], test="T_FW_PIT_DRAW_CENSUS + sc_cords_under_items (specified)",
         stage="4-5 then 6", kind="as row 34"),
    dict(file=H + "owner_look_defects_2026-11-13.md", row=16,
         words="[Image #8] Also, the GSS cables are now correctly below the items.",
         bars=["drawing_true_to_grid", "walk_scavenger_base"], test="sc_cords_under_items (specified) keeps it so",
         stage="6", kind="approval: the regression the in-game read guards"),
]

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
for k, t in NEW.items():
    tests[k] = dict(id=k, kind="offline", stage=t["stage"], file=t["file"], observes=t["observes"], reads=t["reads"], new=True,
                    command="python3 " + t["file"] if t["file"].endswith(".py") else "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py",
                    runs_today=dict(ran=False, why="specified, not built: Stage 3 builds it failing first"))

# in-game scenes: entry named in scenes.json; exists only if the function is defined there
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
    tests[s["id"]] = row
tests["sc_cords_under_items"] = dict(
    id="sc_cords_under_items", kind="live_minimal", stage="6", file=G + "validation.py", entry="scene_cords_under_items",
    entry_exists=False, new=True, observes="a floor cord under a battery, a shelf of items and furniture, dry and in a FlowWorks pit: "
    "the cord's draw altitude and queue read below the thing's, the junction piece too; control: a cord forced to the overhead queue reads above",
    reads=[G + "Source/CordUnderLiquid.cs", G + "Source/SectionLayer_RM_MessyCords.cs"], held=True,
    why_game="draw order is a property of the running renderer; the offline census proves the routing, not the drawn result",
    runs_today=dict(ran=False, why="specified for the held statements; not in scenes.json (journal question 2)"))
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
        sc = list(dict.fromkeys(p["scene"] for p in checklist.get(bid, {}).get("parts", []) if p.get("scene")))
    decides = list(dict.fromkeys(OFF_DECIDES.get(bid, []) + sc))
    if kind == "walk":
        decides.append("LOOK_STAGE8")
    leaves_here = [bid] if is_leaf else sorted({r for s in sc for r in (SCENE[s].get("requirement") or [])})
    sup = list(OFF_SUPPORTS.get(bid, []))
    for l in leaves_here:
        sup += rows_for_leaf.get(l, [])
    if bid in ("drawing_true_to_grid", "walk_scavenger_base"):
        sup.append("sc_cords_under_items")
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
    mod="GimmeSomeSlack", version="0.1.0", made=NOW,
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
    "offline tests: %d built (ran today: %d PASS, %d FAIL), %d specified for Stage 3" % (
        len(off_built), sum(t["runs_today"]["result"] == "PASS" for t in off_built),
        sum(t["runs_today"]["result"] != "PASS" for t in off_built), len(NEW)),
]
L = ["# Gimme Some Slack 0.1.0: test-and-stage table", "",
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
