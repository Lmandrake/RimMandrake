#!/usr/bin/env python3
"""Throwaway: place every FlowWorks held look row on a bar and a test (or name why it has no bar). -> /tmp/fw_pilot/held_place.json"""
import json, glob, os
ROOT = "/home/mandrake/rm/relentless/clones/RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT.det"
HD = "design/RimMandrake/validation_holding/"
LAW = ["fill_level_legible", "inv_looks"]
UL = "T_UNDERLIQUID + OL_OWNER_LOOK_READS"
OVL = "OL_OWNER_LOOK_READS (OL_overlays_hidden; blocked on the overlay proof hook)"
P = {  # (file-tag, row): (bars, test, stage, kind)
 ("2026-11-12", "1"): (LAW + ["inv_liquid_roster"], UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "2"): (LAW, UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "3"): (LAW, UL, "6", "approval kept for re-check: in-game state read"),
 ("2026-11-12", "4"): (LAW + ["ways_in_and_out"], UL, "6", "in-game state read"),
 ("2026-11-12", "5"): (LAW + ["sluice_drains_on_command"], UL, "6", "approval kept for re-check: in-game state read"),
 ("2026-11-12", "6"): (LAW, UL, "6", "in-game state read"),
 ("2026-11-12", "7"): ([], "none: his question, answered by row 13 of the same file", "-", "question (answered)"),
 ("2026-11-12", "8"): (LAW + ["ways_in_and_out"], UL, "6", "in-game state read"),
 ("2026-11-12", "9a"): (LAW, UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "9b"): (LAW, UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "9c"): (LAW, "T_UNDERLIQUID + LOOK_STAGE8", "4-5 and 8", "offline parity + look only (wash colour has no reader)"),
 ("2026-11-12", "9d"): (LAW, UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "9e"): (LAW, "T_UNDERLIQUID (PY_FLOWWORKS_UNDERLIQUID_PARITY: one law for every drawer)", "4-5", "offline selftest"),
 ("2026-11-12", "10a"): (LAW + ["pit_reads_as_hole"], "OL_OWNER_LOOK_READS (brim_no_shade_outside capture row)", "6", "in-game capture"),
 ("2026-11-12", "10b"): (LAW + ["pit_reads_as_hole"], UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "11a"): (["covered_pit_springs"], "T_PIT_COVER + OL_OWNER_LOOK_READS", "6", "approval kept for re-check: in-game state read"),
 ("2026-11-12", "11b"): (["covered_pit_springs", "inv_pits"], "T_PIT_COVER (PitCover_rests_on_two_banks)", "4-5", "offline selftest"),
 ("2026-11-12", "12"): (["canal_reads_as_dug", "inv_dig_depth"], "OL_OWNER_LOOK_READS + LOOK_STAGE8 (swale texture is art)", "6 and 8", "in-game state read + look only"),
 ("2026-11-12", "13"): (LAW + ["pit_reads_as_hole"], UL, "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "14"): (["inv_looks"], "big pit review scene (northstar/selftest_big_pit_scene.py offline; the scene itself feeds LOOK_STAGE8)", "6 and 8", "staging for his look"),
 ("2026-11-12", "15"): (["inv_looks"], "big pit review scene (BP*_furn rows) + OL_OWNER_LOOK_READS (OL_buildings_covered)", "6", "in-game state read"),
 ("2026-11-12", "16"): ([], "harness: src/RimMandrake/Utils/selftest_validation_core_site.py (open-sky site)", "4-5", "harness, no FlowWorks bar (floor line test_isolation)"),
 ("2026-11-12", "17"): ([], "harness: as row 16", "4-5", "harness, no FlowWorks bar"),
 ("2026-11-12", "18"): (["inv_looks"], "big pit review scene (per-thing rows, HP against spawn_baseline.json)", "6", "staging for his look"),
 ("2026-11-12", "19"): (["inv_looks"], "as row 14", "6 and 8", "staging for his look"),
 ("2026-11-12", "20"): (["pit_reads_as_hole"], "T_PIT_LABEL (offline) + on-screen label text BLOCKED (RIMMANDRAKE_ADD_PIT_LABEL_STATE_READER_MOUSEOVER_HAS_NONE)", "4-5 and 6", "offline selftest + blocked in-game read"),
 ("2026-11-12", "21"): (["inv_map_controls"], "T_MAP_CONTROLS (GodLiquid_*)", "4-5", "offline selftest"),
 ("2026-11-12", "22"): (LAW, "T_UNDERLIQUID (parity: shallow end) + LOOK_STAGE8", "4-5 and 8", "approval kept for re-check: offline parity + look"),
 ("2026-11-12", "23"): (LAW, "T_UNDERLIQUID (parity: deep opacity; replaced by row 41)", "4-5", "offline parity"),
 ("2026-11-12", "24"): (LAW, "T_UNDERLIQUID + LOOK_STAGE8", "4-5 and 8", "offline parity + look only (taste)"),
 ("2026-11-12", "25"): (LAW + ["pit_reads_as_hole"], "T_UNDERLIQUID (dry floor = wet floor ground) + LOOK_STAGE8", "4-5 and 8", "offline parity + look only"),
 ("2026-11-12", "26"): ([], "harness: big pit scene wildlife_none_left rows", "6", "harness staging (and his question, answered)"),
 ("2026-11-12", "27"): (["inv_looks"], "big pit review scene (pack_layout, BP*_inside_margin)", "4-5 and 6", "staging for his look"),
 ("2026-11-12", "28"): (LAW, UL + " (OL_buildings_covered)", "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "29"): (LAW, UL + " (OL_no_surface_shadow)", "4-5 and 6", "offline law + in-game state read"),
 ("2026-11-12", "30"): ([], "process: capture_list.json puts the deepest copy first (Stage 7 pre-human check)", "7", "process instruction, no bar"),
 ("2026-11-12", "31"): ([], "harness: src/RimMandrake/Utils/selftest_screenshot_mode_restored.py + OL_screenshot_mode_off", "4-5 and 6", "harness, no FlowWorks bar"),
 ("2026-11-12", "32"): ([], "harness: as row 31", "4-5 and 6", "harness, no FlowWorks bar"),
 ("2026-11-12", "33a"): ([], "T_GEYSER_TUB", "4-5 (live owed)", "offline selftest; NO 0.1.0 BAR: geyser hot tub (question for him)"),
 ("2026-11-12", "33b"): ([], "T_GEYSER_TUB + LOOK_STAGE8 (bubble art)", "4-5 and 8", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-12", "33c"): ([], "T_GEYSER_TUB", "4-5 (live owed)", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-12", "34"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "35"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "36"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "37"): (["inv_map_controls"], "T_MAP_CONTROLS (specified case GodLiquid_no_god_mode_in_names)", "2 and 4-5", "offline text check (specified)"),
 ("2026-11-12", "38"): (["inv_map_controls"], "T_MAP_CONTROLS (specified case GodLiquid_pour_over_brim_overflows_never_no_room) + OL_OWNER_LOOK_READS (OL_pour_never_no_room)", "4-5 and 6", "offline (specified) + in-game read"),
 ("2026-11-12", "39"): (["fill_flows_along_canal"], "LOOK_STAGE8 (motion over time)", "8", "look only"),
 ("2026-11-12", "40"): (LAW, "T_UNDERLIQUID (specified parity: blue share rises with depth) + LOOK_STAGE8", "4-5 and 8", "offline (specified) + look"),
 ("2026-11-12", "41"): (LAW, "T_UNDERLIQUID (specified parity: 4 m hides >= DeepOpacity) + LOOK_STAGE8", "4-5 and 8", "offline (specified) + look"),
 ("2026-11-12", "42"): ([], "capture ring-luminance row of the geyser pit (specified)", "6", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-12", "43"): (LAW, UL + " (OL_corpses_covered) + overlay hook", "6", "in-game state read + blocked hook"),
 ("2026-11-12", "44"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "45"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "46"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-12", "47"): (LAW, UL + " (OL_opaque_hides on item Novel)", "6", "in-game state read (seen by the Conductor, not his words)"),
 ("2026-11-12", "48"): ([], "rule: the holding store itself (README.md)", "-", "rule, no bar"),
 ("2026-11-13", "1"): ([], "T_GEYSER_TUB + LOOK_STAGE8", "8", "approval; NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-13", "2"): ([], "T_GEYSER_TUB (vent, plume and pool square share one cell)", "4-5", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-13", "3"): ([], "process: every scene reads as its caption (Stage 7 pre-human check)", "7", "look only, process"),
 ("2026-11-13", "4"): ([], "T_GEYSER_TUB + T_UNDERLIQUID (vent seen at its depth)", "4-5", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-13", "5"): (["ways_in_and_out"], "T_PIT_ACCESS + staging reachability read", "4-5 and 6", "offline + in-game read"),
 ("2026-11-13", "6"): (["ways_in_and_out"], "T_PIT_ACCESS (LadderClimb_*)", "4-5", "approval kept for re-check: offline selftest"),
 ("2026-11-13", "7"): (["ways_in_and_out"], "T_PIT_ACCESS (PY_FLOWWORKS_DRAFTED_MOVE_PIT) + sc_ways_out", "4-5 and 6", "offline + in-game read"),
 ("2026-11-13", "8"): ([], "none until designed (filed to the Designer)", "-", "NO 0.1.0 BAR: liquid coating on pawns (question for him)"),
 ("2026-11-13", "9"): (["ways_in_and_out"], "pit exposure thought math (specified offline case in T_PIT_ACCESS)", "4-5", "offline (specified)"),
 ("2026-11-13", "10"): ([], "none until designed (filed to the Designer)", "-", "NO 0.1.0 BAR: liquid coating on pawns"),
 ("2026-11-13", "11"): ([], "none until designed (filed to the Designer)", "-", "NO 0.1.0 BAR: washing off a coating"),
 ("2026-11-13", "12"): ([], "T_GEYSER_TUB (selftest_flowworks_geyser_tub.py encodes the old radius rule; needs the edit)", "4-5", "NO 0.1.0 BAR: geyser hot tub"),
 ("2026-11-13", "13"): (LAW, "LOOK_STAGE8", "8", "approval, look only (taste)"),
 ("2026-11-13", "14"): (LAW, OVL, "6", "approval kept for re-check"),
 ("2026-11-13", "15"): (LAW, OVL, "6", "blocked on a proof hook"),
 ("2026-11-13", "16"): (LAW, OVL, "6", "approval kept for re-check"),
 ("2026-11-13", "17"): (["ways_in_and_out", "pit_reads_as_hole"], "T_PIT_ACCESS (PY_FLOWWORKS_DRAFTED_MOVE_PIT checks only the destination remap; the release ring and the pit's top rows are unchecked) + sc_ways_out", "4-5 and 6", "offline (partly specified) + in-game read"),
 ("2026-11-13", "18"): ([], "harness: tier_cut_creature_check.py against proof-scene creatures", "2", "harness staging, no FlowWorks bar"),
 ("2026-11-13_dig_interface", "1"): (["canal_reads_as_dug", "inv_dig_depth"], "T_DIG_TIME_ARITHMETIC (specified; his target not set)", "4-5", "offline arithmetic (specified); Problem-or-Divergent is his open call"),
 ("2026-11-13_dig_interface", "2"): ([], "none until the design is ruled (RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION)", "-", "NO 0.1.0 BAR yet: dig interface consolidation, his open call"),
 ("2026-11-13_evening", "1"): ([], "T_GEYSER_TUB (fleck count, size, alpha in bounds; offline)", "4-5", "NO 0.1.0 BAR: geyser bubbles"),
 ("2026-11-13_evening", "2"): (LAW, "T_UNDERLIQUID (things lying flat draw under the sheet)", "4-5", "offline law"),
 ("2026-11-13_evening", "3"): (LAW + ["pit_reads_as_hole"], "T_UNDERLIQUID (every draw path enumerated; sprite inside the pit)", "4-5", "offline law"),
 ("2026-11-13_evening", "4"): (LAW, "T_UNDERLIQUID (overlays follow the depth rule) + OL_OWNER_LOOK_READS", "4-5 and 6", "offline law + in-game read"),
 ("2026-11-13_evening", "5"): (LAW, "T_UNDERLIQUID (NeedsPower and PowerOff fade with depth)", "4-5", "offline law"),
}
out = []
os.chdir(ROOT)
for f in sorted(glob.glob(HD + "owner_look_defects_2026-11-1*.md")):
    if "explosive" in f:
        continue
    tag = os.path.basename(f)[19:-3]
    hdr = None
    for line in open(f):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "#":
            hdr = cells
            continue
        if set(cells[0]) <= set("-"):
            continue
        d = dict(zip(hdr, cells))
        words = d.get("his words (verbatim)") or d.get("his words")
        k = (tag, cells[0])
        if k in [(o["tag"], str(o["row"])) for o in out]:
            continue
        bars, test, stage, kind = P[k]
        out.append({"file": f, "tag": tag, "row": cells[0], "words": words[:300], "bars": bars, "test": test, "stage": stage, "kind": kind})
missing = [k for k in P if k not in {(o["tag"], o["row"]) for o in out}]
assert not missing, missing
json.dump(out, open("/tmp/fw_pilot/held_place.json", "w"), indent=1)
print(len(out), "placed;", sum(1 for o in out if o["bars"]), "on a bar;", sum(1 for o in out if "NO 0.1.0 BAR" in o["kind"]), "with no 0.1.0 bar")
