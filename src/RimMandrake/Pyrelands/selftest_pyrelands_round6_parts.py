#!/usr/bin/env python3
"""T_ROUND6_PARTS (RIMMANDRAKE_BUILD_PYRELANDS_ROUND_SIX_PARTS_AFTER_THE_TEN): the thirteen scenes the round-6 gap fixes
owe parts to have them in validation.py (and firehawk_rewards_live.py).

Static, offline, in the shape of selftest_pyrelands_ten_scenes_parts. Per scene: its entry point is a registered
@suite.chain; an existing chain's body calls its `_r6_<chain>(t)` parts helper; the parts (helper bodies, or a new
chain's own body plus its `_r6_<chain>_*` helpers) make the reads the item's table row names. A read no bridge tool can
make is recorded `_unmeasured(...)`, never invented. The pure helpers the parts decide with are exercised on worked
inputs. The live halves are each scene's `live_command`; this test does not run them.

  python3 <this file>     exit 0 = every check PASS, 1 = any FAIL
"""
import importlib.util
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATION = os.path.join(HERE, "validation.py")
REWARDS = os.path.join(HERE, "firehawk_rewards_live.py")
NAME = "selftest_pyrelands_round6_parts"
sys.path.insert(0, HERE)
import selftest_pyrelands_ten_scenes_parts as TEN  # noqa: E402 - the same block reader

# (scene, chain, new chain?, strings the parts must hold)
SCENES = (
    ("sc_furnace_hide_bank", "furnace_hide_bank", True,
     ("Tundra", "IceSheet", "RM_FurnaceBeast", "ButcherSpot", "ButcherCorpseFlesh", "DoBillsButcherFlesh",
      "RM_FurnaceHide", "RM_FurnaceHideBank", "CompHeatPusher", "CompRefuelable", "CompPowerTrader", "costList",
      "jawa/cell_temperature", "outdoorTemp", "R6_BANK_HOURS", "R6_BANK_MARGIN", "R6_BANK_CEILING",
      "_ten_control_map(", "_ten_control_map_drop(")),
    ("sc_walk", "walk_season", False,
     ("pyrelandsEnabled", "ProbeBurnHistory", "_ash(", "ProbeSleep", "fireOnCell", "RM_FurnaceBeast", "PYRE_WALK")),
    ("sc_scorchfruit", "scorchfruit_fire_born", False,
     ("scorchFruitEnabled", "FRUIT_PLANT", "_fire(")),
    ("sc_ash_ground", "ground_deep_ash", False,
     ("ashfallAccumulationEnabled", "ambientAshEnabled", "ashground_noon", "R6_HALF_DAY", "is_water_family(",
      "AridShrubland", "_ten_control_map(", "ClearAsh", "LayAsh", "_ten_noon_hour(", "ppc=", "PyrelandsMechanicsGate",
      "_unmeasured(")),
    ("sc_roof_withers", "roof_withers", True,
     ("RoofConstructed", "jawa/get_roof_batch", "RM_FE_Plant_EmberGrass", "hitPoints", "RM_WithersUnderRoof",
      "jawa/inspect_string", "R6_WITHER_HOURS", "R6_WITHER_GONE_BY", "pyrelandsEnabled", "_ten_gate_on(", "Fire",
      "lockWeather=True", "_unmeasured(")),
    ("sc_herd_thirst", "herd_thirst", True,
     ("RM_Thirst", "RM_ThirstGrassWateredExtension", "MapComponent_PyrelandsHerdThirst", "RM_Ullai", "Muffalo",
      "herds_of(", "R6_THIRST_RATIO", "R6_DRINK_CELLS", "arrival_overlaps(", "RM_Dehydration", "_vitals(",
      "_r6_incidents(", "PyrelandsMechanicsGate", "_unmeasured(")),
    ("sc_no_rain", "no_ordinary_rain", False,
     ("jawa/game_condition", "WeatherController", "GameCondition_ForceWeather", "jawa/weather_get", "Rain",
      "TemperateForest", "_unmeasured(")),
    ("sc_heat_dome", "heat_dome", False,
     ("bodyGraphic", "domeTexPath", "domeArt", "ppc=", "Burn", "DOME_HOLD_TICKS")),
    ("sc_furnace_giant", "ullai_and_giant", False,
     ("jawa/biome_probe", "biome_probe_animals(", "baseBodySize", "lifeStages", "drawSize", "R6_GIANT_DRAW",
      "R6_ROSTER_MIN", "giant_margin(", "RestoreClassicFurnaceBeast", "_unmeasured(")),
    ("sc_burn_line_walks", "burn_line", False,
     ("ProbeOpeningFront", "R6_FRONT_HOURS", "_ten_hour(", "ppc=", "burn_line_walking", "rimworld/save_game",
      "front_walks(", "burnLineEnabled", "_r6_guard(")),
    ("sc_burn_compounds", "fresh_burn_bonus", False,
     ("_r6_guard(", "_r6_incidents(", "RM_FE_BlackRain", "freshBurnBonusEnabled", "R6_COMPOUND_DAYS", "_probe(",
      "RoofConstructed")),
    ("sc_grass_regreens", "embergrass_regrow", False,
     ("grass_census", "mutationsBefore", "plantDensity", "R6_CENSUS_MUTATORS", "_unmeasured(")),
)
REWARD_PARTS = (
    ("sc_firehawk_rewards letter words", "_r6_letter_words", ("rimworld/list_letters", "LabelShortCap",
                                                              "RM_FireHawkEmberFromPlant", "RM_FireHawkEmberFromBurn")),
    ("sc_firehawk_rewards trophy worth", "_r6_trophy_worth", ("MarketValue", "Beauty", "RM_FireHawk", "statBases")),
)


def load_validation():
    """validation.py with modcheck stubbed: enough to call its pure helpers."""
    mc = types.ModuleType("modcheck")

    class Suite(object):
        def __init__(self, name):
            self.chains = {}

        def chain(self, name):
            def deco(fn):
                self.chains[name] = fn
                return fn
            return deco

    class ExpectationFailed(Exception):
        pass

    mc.Suite, mc.Component, mc.ExpectationFailed = Suite, object, ExpectationFailed
    sys.modules.setdefault("modcheck", mc)
    spec = importlib.util.spec_from_file_location("pyre_validation_r6", VALIDATION)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pure_checks():
    out = []
    try:
        V = load_validation()
    except Exception as ex:   # noqa: BLE001 - a crash is a FAIL
        return [("validation.py imports with modcheck stubbed (%r)" % ex, False)]
    try:
        ok = (V.herds_of([("a", "RM_Ullai", 0, 0), ("b", "RM_Ullai", 5, 0), ("c", "RM_Ullai", 40, 0),
                          ("d", "RSW_Nuna", 1, 0)], 10)
              == [["a", "b"], ["c"], ["d"]])
        out.append(("herds_of groups same-kind animals within 10 cells", ok))
        out.append(("arrival_overlaps: two herds in one hour overlap",
                    V.arrival_overlaps({"h1": [3, 9], "h2": [9]}) == [9]))
        out.append(("arrival_overlaps: apart is no overlap", V.arrival_overlaps({"h1": [3], "h2": [4]}) == []))
        out.append(("arrival_overlaps: no arrival at all reads None", V.arrival_overlaps({"h1": [], "h2": []}) is None))
        ok, _ = V.giant_margin({"RM_FurnaceBeast": (9.0, 7.5), "RM_Ullai": (1.8, 3.0), "RM_Flamefang": (2.0, 2.5)})
        out.append(("giant_margin passes bs 9 over every kind", ok))
        bad, _ = V.giant_margin({"RM_FurnaceBeast": (9.0, 7.5), "RM_Ullai": (4.6, 3.0)})
        out.append(("giant_margin refuses a kind over half the beast", not bad))
        bad, _ = V.giant_margin({"RM_FurnaceBeast": (9.0, 3.0), "RM_Ullai": (1.8, 3.5)})
        out.append(("giant_margin refuses a draw size not above another kind's", not bad))
        walk = [{"hour": h, "fires": 5, "cx": 10 + h, "cz": 10} for h in range(24)]
        out.append(("front_walks: a moving centroid walks", V.front_walks(walk)[0] is True))
        still = [{"hour": h, "fires": 5, "cx": 10, "cz": 10} for h in range(24)]
        out.append(("front_walks: a still centroid does not", V.front_walks(still)[0] is False))
        gap = walk[:5] + [{"hour": 5, "fires": 0, "cx": None, "cz": None}] + walk[6:]
        out.append(("front_walks: an hour with no fire does not", V.front_walks(gap)[0] is False))
        out.append(("front_walks: no reads is not judged", V.front_walks([])[0] is None))
    except Exception as ex:   # noqa: BLE001
        out.append(("pure helpers crashed: %r" % ex, False))
    return out


def checks(text, rewards):
    out = []
    for scene, chain, new, strings in SCENES:
        body = TEN.chain_body(text, chain)
        out.append(("%s: chain %s registered" % (scene, chain), body is not None))
        helper = "_r6_" + chain
        if new:
            parts = (body or "") + "\n" + TEN.func_bodies(text, helper)
        else:
            out.append(("%s: %s calls %s(t)" % (scene, chain, helper), bool(body) and (helper + "(t)") in body))
            parts = TEN.func_bodies(text, helper)
        parts += "\n" + TEN.func_bodies(text, "_r6")   # shared _r6 helpers and constants named in the parts
        parts += "\n" + "\n".join(ln for ln in text.split("\n") if ln.startswith("R6_"))
        missing = [s for s in strings if s not in parts]
        out.append(("%s: parts make the owed reads%s" % (scene, (" (missing %s)" % ", ".join(missing)) if missing else ""),
                    not missing))
    for what, fn, strings in REWARD_PARTS:
        m = re.search(r"^    def %s\(" % fn, rewards, re.M)
        body = rewards[m.start():m.start() + 4000] if m else ""
        missing = [s for s in strings if s not in body]
        out.append(("%s: %s in firehawk_rewards_live.py%s" % (what, fn, (" (missing %s)" % ", ".join(missing))
                                                               if missing else ""), bool(m) and not missing))
        out.append(("%s: %s is called" % (what, fn), (fn + "(t") in rewards.replace(" def %s(t" % fn, "")))
    return out


def main():
    text = open(VALIDATION, encoding="utf-8").read()
    rewards = open(REWARDS, encoding="utf-8").read()
    res = checks(text, rewards) + pure_checks()
    for what, ok in res:
        print("%s %s" % ("PASS" if ok else "FAIL", what))
    bad = sum(1 for _, ok in res if not ok)
    print("%s: %d of %d checks failed" % (NAME, bad, len(res)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
