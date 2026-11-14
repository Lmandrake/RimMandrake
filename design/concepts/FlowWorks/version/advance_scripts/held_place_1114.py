#!/usr/bin/env python3
"""Throwaway (FlowWorks Stage 3 reconcile, 2026-11-14): place the 20 held rows of owner_look_defects_2026-11-14.md that
Stage 1 had not placed, re-place dig_interface#2 as next-version work (his card 2026-11-13 10:12 PM PST), and add the
two tests the look-fix builder made today (C# PitLook1114_*, the live pit_look_1114_live.py, UNRUN). Judgment is in the
table below; a judge should challenge which bar each row sits on."""
import json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
os.chdir(ROOT)
P = "design/concepts/FlowWorks/version/test_table.json"
F = "design/RimMandrake/validation_holding/owner_look_defects_2026-11-14.md"
tab = json.load(open(P))
T, LV = "T_PIT_LOOK_1114", "PIT_LOOK_1114_LIVE"
tab["tests"][T] = {"id": T, "kind": "offline", "stage": "4-5", "file": "src/RimMandrake/Utils/selftest_flowworks_stock.py",
    "observes": "his look of 2026-11-14, fixed by RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE: pit floor walks full speed, Hot Tub "
                "on a sunk geyser pool, furniture never straddles a pit edge, a floor in a pit survives water and is named, a "
                "drowned body is covered by its own picture, pour steps in metres (C# PitLook1114_*)",
    "reads": ["src/RimMandrake/FlowWorks/Source/SelfTest"], "command": "python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only PitLook1114*",
    "runs_today": {"ran": False, "why": "added 2026-11-14 Stage 3; filled by the next run"}}
tab["tests"][LV] = {"id": LV, "kind": "live_minimal", "stage": "6", "file": "src/RimMandrake/FlowWorks/northstar/pit_look_1114_live.py",
    "entry": "__main__", "observes": "the same six fixes read in the running game on his sitting map (pit_floor WRITES to B2)",
    "reads": ["src/RimMandrake/FlowWorks/northstar/pit_look_1114_live.py"],
    "command": "python.exe src\\RimMandrake\\FlowWorks\\northstar\\pit_look_1114_live.py  (bridge held; FlowWorks deployed)",
    "why_game": "a mouse-over string, a placement refusal and a drawn body exist only in a played map",
    "owed_under": "RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE",
    "runs_today": {"ran": False, "entry_exists": True, "why": "UNRUN: offline only, never the game in this run"}}
NV = "next version (FlowWorks 0.2.0 Divergent)"
rows = {  # row: (bars, test, stage, kind)
 "1": (["ways_in_and_out", "inv_pit_access"], T + " (PitLook1114_pit_floor_walks_full_speed_readout_and_step) + " + LV, "4-5 and 6", "defect, fixed a9866498909a"),
 "2": ([], "none: not this mod's", "-", "other mod: shared interaction spots (RIMMANDRAKE_ALLOW_SHARED_INTERACTION_SPOTS_TWO_BENCHES_ONE_STOOL)"),
 "3": (["inv_pits"], T + " (PitLook1114_furniture_never_straddles_a_pit_edge) + " + LV, "4-5 and 6", "defect, fixed 7f25ff2060ea"),
 "4": ([], "specified: RM_Swale is a TerrainDef, not a Building (RIMMANDRAKE_REBUILD_SWALE_AS_SOAKING_FLOOR_NOT_FURNITURE)", "4-5",
       "NO 0.1.0 BAR yet: no bar names the swale; Problem (a new bar now) or Divergent is his call"),
 "5": (["inv_dig_depth"], "specified offline: a dig in sand, mud or loose snow is refused on every path (RIMMANDRAKE_REFUSE_PITS_IN_LOOSE_GROUND_EVEN_BY_BRIDGE)",
       "4-5", "defect, owed; the dig scenario's sand pad (tree.json canal_reads_as_dug) now contradicts his row: question"),
 "6": ([], "none: staging", "-", "harness: the staged pits lost their water at the save-format change (diagnosed on RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE)"),
 "7": (["inv_looks", "fill_level_legible"], "T_UNDERLIQUID (Submerge_overlays_follow_their_thing, Submerge_murk_keeps_rising_to_the_plateau) + LOOK_STAGE8",
       "4-5 and 8", "approval kept for re-check"),
 "7b": (["inv_looks"], T + " (PitLook1114_drowned_body_cover_is_the_pawns_own_picture) + " + LV, "4-5 and 6", "defect, fixed 3f774eb730"),
 "8": ([], "none: next version", "-", NV + ": RIMMANDRAKE_SHORT_DROWNED_ELECTRONICS_LIKE_RAIN_DOES, his own words"),
 "9": ([], "none: dev tooling", "-", "harness: approval of the debug Pour menu layout (dev tooling, no player bar)"),
 "9b": ([], T + " (PitLook1114_pour_steps_each_show_metres_on_one_tile, PitLook1114_no_fill_n_wording_in_visible_text)", "4-5",
        "harness: debug Pour menu wording (dev tooling), fixed 7acbbf887b"),
 "10": ([], "none until designed", "-", NV + ": RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE (row 10f's ruling)"),
 "10b": ([], "stage.py b2_drain_all row", "-", "harness: approval of the debug Drain option (dev tooling)"),
 "10c": ([], "none until designed", "-", NV + ": RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE (row 10f's ruling)"),
 "10d": (["inv_overflow_sheet"], "T_SHEET (soak-in, freeze and thaw) + LOOK_STAGE8", "4-5 and 8",
         "approval kept for re-check (evaporation); the wet ground left after is next version (row 10f)"),
 "10e": ([], "none: answered by row 10f", "-", "question, answered by row 10f"),
 "10f": ([], "none until designed", "-", NV + ": his ruling of 2026-11-14 12:01 PM PST, all wetness one thin film (RIMMANDRAKE_DESIGN_SPILLED_WATER_WET_GROUND_ONE_STATE)"),
 "11": (["inv_doors", "sluice_drains_on_command"], "specified offline: the cell under a sluice gate reads the pit's level (RIMMANDRAKE_SEAL_SLUICE_AT_ITS_PANEL_NOT_ITS_SQUARE)",
        "4-5", "defect, diagnosed not fixed"),
 "12": (["inv_pits"], T + " (PitLook1114_floor_on_a_pit_survives_water_and_is_named) + " + LV, "4-5 and 6", "defect, fixed f64db2c740"),
 "12b": ([], "none until designed", "-", NV + ": RIMMANDRAKE_LINE_PITS_WITH_FLOORS_AND_WALLS_ROCK_FREE, his own words"),
}
words = {}
for line in open(F):
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if line.startswith("| ") and c[0] != "#" and not set(c[0]) <= set("-"):
        words[c[0]] = c[1]
have = {(h["tag"], h["row"]) for h in tab["held_statements"]}
for r, (bars, test, stage, kind) in rows.items():
    assert r in words and ("2026-11-14", r) not in have, r
    tab["held_statements"].append({"file": F, "tag": "2026-11-14", "row": r, "words": words[r], "bars": bars, "test": test,
                                   "stage": stage, "kind": kind})
for h in tab["held_statements"]:
    if h["tag"] == "2026-11-13_dig_interface" and h["row"] == "2":
        h["kind"] = NV + ": the dig-interface redesign, his card 2026-11-13 10:12 PM PST (\"All in the next version\")"
        h["test"] = "none: next version (version/next_version/README.md)"
for b in tab["bars"]:
    if b["id"] in ("ways_in_and_out", "inv_pit_access", "inv_pits", "inv_looks"):
        for t in (T, LV):
            if t not in b["supports"]:
                b["supports"].append(t)
json.dump(tab, open(P, "w"), indent=1)
print(len(rows), "placed;", len(tab["held_statements"]), "held rows in the table")
