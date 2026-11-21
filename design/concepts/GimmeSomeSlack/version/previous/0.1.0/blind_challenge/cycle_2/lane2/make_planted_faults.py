import json, os, sys
M = "src/RimMandrake/GimmeSomeSlack/"
F = []
def f(id, file, old, new, bars, suites, why=""):
    F.append({"id": id, "file": file, "old": old, "new": new, "bars": bars, "suites": suites, "why": why})
NH = ["no_hose", "no_hose_in_gss"]
# --- the no-hose bars' "kernel": what ships (planted content) and the scan
f("NH_PLANT_HOSE_DEF", M+"Defs/ThingDefs_Buildings/RM_PlantedHoseReel.xml", None,
  '<?xml version="1.0" encoding="utf-8"?>\n<Defs>\n  <ThingDef ParentName="BuildingBase">\n    <defName>RM_HoseReel</defName>\n    <label>hose reel</label>\n  </ThingDef>\n</Defs>\n', NH, ["nohose", "lane1"], "a hose def ships")
f("NH_PLANT_REEL_TEXTURE", M+"Textures/RimMandrake/GimmeSomeSlack/Reel/Spool_south.png", None, "PNG", NH, ["nohose", "lane1"], "a reel texture in its own folder ships")
f("NH_PLANT_HOSE_CLASS", M+"Source/Core/PlantedHoseSegment.cs", None, "namespace RimMandrake.GimmeSomeSlack.Core { public class HoseSegment { } }\n", NH, ["nohose", "lane1"], "a C# hose class compiles in")
f("NH_PLANT_PIPE_DEF", M+"Defs/ThingDefs_Buildings/RM_PlantedPipe.xml", None,
  '<?xml version="1.0" encoding="utf-8"?>\n<Defs>\n  <ThingDef ParentName="BuildingBase">\n    <defName>RM_WaterPipe</defName>\n    <label>water pipe</label>\n  </ThingDef>\n</Defs>\n', NH, ["nohose", "lane1"], "a pipe def ships (the bar's words: no pipe)")
f("NH_TEST_CLASS_ATTR_BLIND", M+"northstar/selftest_gss_no_hose.py", "if cls and WORD.search(cls):", "if cls and False:", NH, ["nohose"], "the scan stops reading Class attributes; its own planted comp must go red")
f("NH_TEST_TEX_FOLDER_BLIND", M+"northstar/selftest_gss_no_hose.py", "if f.is_file() and WORD.search(str(f.relative_to(tex))):", "if f.is_file() and WORD.search(f.name):", NH, ["nohose"], "the scan reads file names only; its own Hose/ folder plant must go red")
# --- game-side callers: RM_FallenWireShock (changed), GssSessionReset, the pipe switch
SH = ["floor_end_shock", "shock_reach_setting", "fallen_wire_shock", "settings_switch_cleanly"]
W = M+"Source/Aerial/RM_FallenWireShock.cs"
f("FW_KIND_SWAPPED", W, "LineKind kind = dropped != null && dropped.Contains(kv.Key) ? LineKind.DroppedCord : LineKind.DownedSpan;",
  "LineKind kind = dropped != null && dropped.Contains(kv.Key) ? LineKind.DownedSpan : LineKind.DroppedCord;", SH, ["binding", "dropcord", "val", "settings"], "dropped cords and our spans swap kinds")
f("FW_STALE_SPAN_BITES", W, "if (kind == LineKind.DownedSpan && !AerialSettings.enabled) continue;",
  "if (kind == LineKind.DownedSpan && !AerialSettings.enabled) { }", SH, ["binding", "dropcord", "val", "settings"], "behaviour: a stale span contact bites with the master off; the guard's text is kept")
f("FW_OWN_SPANS_UNGATED", W, "if (AerialSettings.enabled)\n            foreach (CompAerialAnchor a in aerial.Anchors)",
  "if (true)\n            foreach (CompAerialAnchor a in aerial.Anchors)", SH, ["binding", "dropcord", "val", "settings"], "our own spans listed as contacts with the master off")
f("FW_EARLY_RETURN_BACK", W, "if (contacts.Count == 0 || AerialSettings.shockReach == ShockReach.None) return;",
  "if (contacts.Count == 0 || !AerialSettings.enabled || AerialSettings.shockReach == ShockReach.None) return;", SH, ["binding", "dropcord", "val", "settings"], "the cycle-1 bug put back")
f("RESET_TAP_LEDGER_DROPPED", M+"Source/GssSessionReset.cs", "            Aerial.TapRegistry.Clear();                         // C14: the tap ledger held the old game's transmitters\n", "", ["statics_clear_between_games", "game_statics_reset"], ["statics"], "the tap ledger outlives a game")
f("RESET_STEPTRACE_DROPPED", M+"Source/GssSessionReset.cs", "            Core.CordBuilder.StepTrace = null;", "            // planted", ["statics_clear_between_games", "game_statics_reset"], ["statics"], "this cycle's own fix undone")
f("PIPE_SWITCH_DEFAULT_OFF", M+"Source/Aerial/AerialLineProfiles.cs", "if (pipeOn == null) return true;", "if (pipeOn == null) return false;", ["pipe_pole_switch", "settings_switch_cleanly"], ["core_perdig", "settings", "val"], "pipe poles off when FlowWorks registers no switch")
f("PIPE_KIND_FOLLOWS_POWER", M+"Source/Aerial/AerialMath.cs", "public static bool KindOn(AerialLineKind k, bool powerOn, bool pipeOn) => CarriesPower(k) ? powerOn : pipeOn;",
  "public static bool KindOn(AerialLineKind k, bool powerOn, bool pipeOn) => CarriesPower(k) ? powerOn : powerOn;", ["pipe_pole_switch", "settings_switch_cleanly"], ["lane1", "settings", "binding"], "pipe poles hostage to the power master again")
f("AM_PIPE_TWO_STRANDS", M+"Source/Aerial/AerialMath.cs", "k == AerialLineKind.Pipe ? 1 : maxStrands;", "k == AerialLineKind.Pipe ? 2 : maxStrands;", ["pipe_pole_switch", "overhead_spans"], ["lane1", "binding"], "a pipe span draws two strands")
f("AM_RESTRING_SPEED_FLOOR", M+"Source/Aerial/AerialMath.cs", "RestringBaseTicks / Math.Max(0.1, constructionSpeed)", "RestringBaseTicks / Math.Max(1.0, constructionSpeed)", ["restring_cut_span", "restring_job"], ["lane1", "binding"], "a slow builder re-strings as fast as a normal one")
# --- CordBuilder / CordSlacken (changed): the floor-cord lay
CB = M+"Source/Core/CordBuilder.cs"; CS = M+"Source/Core/CordSlacken.cs"
f("CB_TWINS_UNSEEN", CB, "if (d < TwinApart) m = Math.Min(m, d);", "if (d < 0) m = Math.Min(m, d);", ["cords_never_repeat", "cord_shape_variation_probe"], ["core_geom"], "the twin detector is blind")
f("CB_TAUT_FAULT_HALVED", CB, "if (ch >= 2 && Geo.Length(s.Pts) < CordSlacken.Bar * ch) f++;", "if (ch >= 2 && Geo.Length(s.Pts) < CordSlacken.Bar * ch * 0.5) f++;", ["cords_lie_slack", "cord_slack_lay"], ["core_geom"], "a strand under the slack bar is no longer a fault")
f("CB_BEND_ALLOWANCE", CB, 'if (CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, R) > bad) { No("bend"); continue; }', 'if (CordShapeAudit.Unforced(w, piece.EndA, piece.EndB, R) > bad + 4) { No("bend"); continue; }', ["no_unforced_sharp_turn"], ["core_geom"], "re-lays accept four more unforced bends")
f("CS_LOOP_THROUGH_WALLS", CS, "foreach (V2 q in loop) if (!Open(w, q) || (clear != null && !clear(q))) { ok = false; break; }", "foreach (V2 q in loop) if (false) { ok = false; break; }", ["cords_draw_under_things", "drawing_true_to_grid"], ["core_geom"], "a varied loop may cross walls and things")
f("CS_FLAT_LONG_EDGE", CS, "if (longEdge && Stray(Q) < MinExcursion)", "if (longEdge && Stray(Q) < MinExcursion * 0.1)", ["cords_lie_slack", "cord_slack_lay"], ["core_geom"], "a long edge may lie flat on its chord")
f("CS_VARY_BENDS_FREE", CS, "CordShapeAudit.Unforced(w, endA, endB, Q) > uOld ||", "CordShapeAudit.Unforced(w, endA, endB, Q) > uOld + 3 ||", ["no_unforced_sharp_turn"], ["core_geom"], "a varied lead may add unforced bends")
# --- the changed tests themselves (blinding faults: caught only by their own controls or another suite)
G = M+"Source/SelfTest/CordGeometryChecks.cs"
f("CGC_RATIO_BAR_LOWERED", G, "public const double MinRatio = 1.4,", "public const double MinRatio = 1.0,", ["cords_lie_slack"], ["core_geom"], "the 1.4x bar becomes 1.0x; the planted taut builder control should go red")
f("CGC_PLANT_CONTROL_SKIPPED", G, "Check(plantedScenes > 0 && plantedCaught == plantedScenes,", "Check(true || plantedScenes > 0 && plantedCaught == plantedScenes,", ["cords_lie_slack"], ["core_geom"], "the negative control no longer asserts (pure weakening)")
P = M+"Source/SelfTest/Program.cs"
f("PROG_GEOMETRY_SKIPPED", P, "if (args.Contains(\"--geometry\")) CordGeometryChecks.Run(scenes);", "if (false) CordGeometryChecks.Run(scenes);", ["cords_lie_slack", "no_unforced_sharp_turn"], ["core_full_geom"], "T_CORD_GEOMETRY_OFFLINE's checks silently not run")
f("PROG_FUZZ_SKIPPED", P, "            GssFuzz.Run(args);             // approach B", "            // GssFuzz.Run(args);             // approach B", ["connectivity_truth", "drawing_true_to_grid"], ["core_full"], "the seeded fuzz silently not run")
S = M+"Source/SelfTest/SliceGateChecks.cs"
f("SGC_CALLER_REDUCE_UNCHECKED", S, "Program.Check(callerReduce == 0,", "Program.Check(callerReduce >= 0,", ["no_stall_on_rewire"], ["core_perdig"], "pure weakening of a stall check")
f("SGC_HANDOFF_BUDGET_x100", S, "internal const long HandoffBytes = 4096,", "internal const long HandoffBytes = 409600,", ["no_stall_on_rewire", "rebuild_cost"], ["core_perdig"], "pure weakening of an allocation budget")
U = "src/RimMandrake/Utils/selftest_gimmesomeslack.py"
f("WRAP_GEOMETRY_NOT_FORWARDED", U, '(["--geometry"] if "--geometry" in argv else [])', '[]', ["cords_lie_slack", "no_unforced_sharp_turn"], ["core_full_geom"], "the wrapper drops --geometry: T_CORD_GEOMETRY_OFFLINE would pass without geometry")
f("WRAP_RC_SWALLOWED", U, "        if r.returncode:\n            return r.returncode", "        if False:\n            return r.returncode", ["cords_lie_slack"], ["core_full"], "an export or build failure no longer stops the run")
V = M+"validation.py"
f("VAL_C2_SHAPE_BLIND", V, '"Aerial/RM_FallenWireShock.cs", "kind == LineKind.DownedSpan && !AerialSettings.enabled"),', '"Aerial/RM_FallenWireShock.cs", "AerialSettings"),', SH, ["val"], "pure weakening of a source-shape check")
f("VAL_SCENE_OWN_ROWS_EMPTY", V, 'SCENE_OWN_ROWS = {"sc_cords_under_items": "UNDER_ROWS"}', "SCENE_OWN_ROWS = {}", ["cords_draw_under_things"], ["under", "val"], "sc_cords_under_items decided by every row of its leaf again")
CU = M+"northstar/selftest_gss_cords_under_items.py"
f("CU_ONE_ENTRY_UNCHECKED", CU, 'check(len(mine) == 1, "scenes.json holds sc_cords_under_items once', 'check(len(mine) >= 0, "scenes.json holds sc_cords_under_items once', ["cords_draw_under_things"], ["under"], "pure weakening")
f("CU_CONTRACT_SKIPPED", CU, "errs = designer_stage.scene_errors(scn, concept_tree.load(concept), repo)", "errs = []", ["cords_draw_under_things"], ["under"], "pure weakening")
DC = M+"selftest_gss_dropped_cords_ignore_aerial_master.py"
f("DC_C4_ALWAYS_TRUE", DC, '"C4_checkpawns_skips_stale_span": (bool(re.search(', '"C4_checkpawns_skips_stale_span": (True or bool(re.search(', SH, ["dropcord"], "pure weakening of C4")
f("DC_EARLY_REGEX_BLIND", DC, 'EARLY = re.compile(r"if\\s*\\([^;{]*!\\s*AerialSettings\\.enabled[^;{]*\\)\\s*return\\s*;")', 'EARLY = re.compile(r"PLANTED_NEVER_MATCHES")', SH, ["dropcord"], "C1/C3 blind; its own mutants must go red")
bad = []
for x in F:
    if x["old"] is None:
        if os.path.exists(x["file"]): bad.append(x["id"] + " exists")
        continue
    n = open(x["file"], encoding="utf-8").read().count(x["old"])
    if n != 1: bad.append("%s: %d matches" % (x["id"], n))
print(len(F), "faults; bad:", bad)
json.dump(F, open(sys.argv[1], "w"), indent=1)
