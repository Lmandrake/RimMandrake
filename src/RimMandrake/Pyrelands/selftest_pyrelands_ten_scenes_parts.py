#!/usr/bin/env python3
"""T_TEN_SCENES_PARTS (RIMMANDRAKE_BUILD_PYRELANDS_GAP_SCENE_PARTS_TEN_SCENES_OWED): the twelve scenes whose owed parts
that item builds have them in validation.py.

Static, offline. Per scene: its entry point is a registered @suite.chain; for an existing chain, the chain body calls its
`_ten_<chain>(t)` parts helper; and the parts (the helper bodies, or the new chain's own body) make the reads the item's
table row names. A read with no bridge tool must be recorded with `_unmeasured(...)`, never invented, so those scenes
check for the UNMEASURED call too. The live halves are each scene's `live_command`; this test does not run them.

  python3 <this file>     exit 0 = every check PASS, 1 = any FAIL
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATION = os.path.join(HERE, "validation.py")
NAME = "selftest_pyrelands_ten_scenes_parts"

DISALLOWED = ("AnimaTreeSpawn", "FarmAnimalsWanderIn", "GauranlenPodSpawn", "HarbingerTreeSpawn", "PoluxTreeSpawn",
              "ThrumboPasses")   # Patches/RM_Pyrelands_NoForeignArrivals.xml

# (scene, chain, new chain?, strings the parts must hold)
SCENES = (
    ("sc_foreign_arrivals", "foreign_arrivals", True,
     ("jawa/fire_incident", "canFireNow", "dryRun=True", "HerdMigration", "ManhunterPack", "ANIMAL_MANIFEST",
      "AridShrubland", "_ten_control_map(") + DISALLOWED),
    ("sc_populations", "plant_census", False,
     # the allowlist-off day and the same-seed gate-off map left (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN)
     ("RM_FireHawk", "RM_Ashwallow", "wildPlantAllowlistEnabled", "PLANT_MANIFEST", "_whole_map(")),
    ("sc_walk", "walk_season", False,
     ("jawa/make_empty_room", "RoofConstructed", "RM_FE_Plant_EmberGrass", "RM_Thirst", "RM_Dehydration", "Burn",
      "Malnutrition", "PyrelandsMechanicsGate", "_unmeasured(")),
    ("sc_ash_ground", "ground_deep_ash", False,
     ("ashground_noon", "rimworld/save_game", "_load_site_save(", "jawa/glow_at", "skyGlow", "_ash(", "ASHFALL",
      "RM_FE_Ground_SoilRich", "Mud")),
    ("sc_three_skies", "cinderfall", False,
     ("skies_noon", "_load_site_save(", "_ten_noon_hour(", "ASHFALL", "CINDERFALL", "BLACKRAIN", '"Rain"',
      "wash_verdict(", "screenshot")),
    ("sc_grass_regreens", "embergrass_regrow", False,
     ("RM_FE_Plant_EmberGrass", "Plant_Grass", "WaterShallow", "burnTick", "watered", "jawa/thing_read", "burst")),
    ("sc_furnace_bed", "furnace_sleep", False,
     ("RM_FurnaceBeast", "Muffalo", "ProbeSleep", "health=True", "burn_injuries(", "1,1")),
    ("sc_flamefang_venom", "flamefang_venom", False,
     ("TendPatient", "VENOM", "hediff_severity(", "immunity", "_unmeasured(")),
    ("sc_fire_sense", "fire_sense", True,
     ("RM_Pyrelands", "get_On", "RM_PyreStepAwayFromFire", "SafeClear", "Ingest", "BeatFire", "Firefighter",
      "UrgentlyHungry", "_unmeasured(")),
    ("sc_ash_watered", "ash_fertility_watered", False,
     ("jawa/cell_temperature", "maxOptimalGrowthTemperature", "GrowthRateFactor_Temperature", "Wet ash keeps its roots",
      "ashWaterFertilityEnabled", "_unmeasured(")),
    ("sc_firehawk", "firehawk", False,
     ("RM_FireHawk", "RM_FireHawkSeekBurn", "fireHawkSpreadEnabled", "54")),
    ("sc_ruins", "ruins", False,
     # the vanilla control map left (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN): RM_FE_Charred is ours alone
     ("jawa/list_things", "jawa/paint_building", "RM_FE_Charred")),
)


def _block(text, start):
    """From `start` (a decorator or def line): the decorators, the def line, then every following line that is blank,
    indented or a signature's closing paren, up to the next top-level line."""
    lines = text[start:].split("\n")
    out = []
    i = 0
    while i < len(lines) and lines[i].startswith("@"):
        out.append(lines[i])
        i += 1
    if i < len(lines):
        out.append(lines[i])
        i += 1
    for ln in lines[i:]:
        if ln and not ln[0].isspace() and not ln.startswith(")"):
            break
        out.append(ln)
    return "\n".join(out)


def chain_body(text, chain):
    m = re.search(r'^@suite\.chain\("%s"\)' % re.escape(chain), text, re.M)
    return _block(text, m.start()) if m else None


def func_bodies(text, prefix):
    """Every top-level `def <prefix>(` or `def <prefix>_...(` body, joined."""
    got = []
    for m in re.finditer(r"^def (%s(?:_\w+)?)\(" % re.escape(prefix), text, re.M):
        got.append(_block(text, m.start()))
    return "\n".join(got)


def checks(text):
    out = []
    for scene, chain, new, strings in SCENES:
        body = chain_body(text, chain)
        out.append(("%s: chain %s registered" % (scene, chain), body is not None))
        helper = "_ten_" + chain
        if new:
            parts = (body or "") + "\n" + func_bodies(text, helper)
        else:
            out.append(("%s: %s calls %s(t)" % (scene, chain, helper), bool(body) and (helper + "(t)") in body))
            parts = func_bodies(text, helper)
        missing = [s for s in strings if s not in parts]
        out.append(("%s: parts make the owed reads%s" % (scene, (" (missing %s)" % ", ".join(missing)) if missing else ""),
                    bool(parts.strip()) and not missing))
    cm = func_bodies(text, "_ten_control_map")
    need = ("jawa/world_tile_map_generate", "jawa/set_current_map", "jawa/map_drop", "mapBiome")
    out.append(("vanilla control map helper (%s)" % ", ".join(need), all(s in cm for s in need)))
    return out


def main():
    text = open(VALIDATION, encoding="utf-8").read()
    res = checks(text)
    for what, ok in res:
        print("%s %s" % ("PASS" if ok else "FAIL", what))
    bad = sum(1 for _, ok in res if not ok)
    print("%s: %d of %d checks failed" % (NAME, bad, len(res)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
