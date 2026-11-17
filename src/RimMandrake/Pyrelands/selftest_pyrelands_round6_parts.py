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
      "front_walks(", "burnLineEnabled", "_r6_guard(",
      # RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES: the burned share of open plantable ground at each day end
      # over R6_SHARE_DAYS, and the same start save reloaded with windCarriesFireEnabled off as the flood control
      "CountBurnedOutside", "open_ground_outside(", "R6_SHARE_DAYS", "R6_SHARE_SAVE", "rimworld/load_game",
      "windCarriesFireEnabled", "burned_share_verdict(")),
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
        # burned_share_verdict(on, off): day-0..N shares of open plantable ground, wind on and the same save wind off
        line = [0.01, 0.01, 0.02, 0.03, 0.05]
        flood = [0.01, 0.15, 0.40, 0.60, 0.81]          # T_BURN_ECOLOGY's model, 250 map, bearing 90, seed 0
        out.append(("burned_share: a line against a flooding control passes", V.burned_share_verdict(line, flood)[0] is True))
        out.append(("burned_share: wind on taking most of the map fails",
                    V.burned_share_verdict([0.01, 0.2, 0.4, 0.55, 0.7], flood)[0] is False))
        out.append(("burned_share: most of the map on ONE day end fails",
                    V.burned_share_verdict([0.01, 0.2, 0.51, 0.51, 0.51], flood)[0] is False))
        out.append(("burned_share: exactly half is not most", V.burned_share_verdict([0.01, 0.1, 0.3, 0.5, 0.5], flood)[0] is True))
        out.append(("burned_share: a control that never floods is not judged",
                    V.burned_share_verdict(line, [0.01, 0.1, 0.2, 0.3, 0.45])[0] is None))
        out.append(("burned_share: a flood both ways fails, never 'the control floods'",
                    V.burned_share_verdict(flood, flood)[0] is False))
        out.append(("burned_share: a trail that never grows fails",
                    V.burned_share_verdict([0.02, 0.02, 0.02, 0.02, 0.02], flood)[0] is False))
        out.append(("burned_share: an unread day is not judged", V.burned_share_verdict([0.01, None, 0.02, 0.03, 0.05], flood)[0] is None))
        out.append(("burned_share: arms of different lengths are not judged", V.burned_share_verdict(line, flood[:3])[0] is None))
        out.append(("burned_share: no reads is not judged", V.burned_share_verdict([], [])[0] is None))
        cells = {(x, z): ("RM_FE_Ground_DeepAsh" if x < 8 else "WaterShallow") for x in range(10) for z in range(10)}
        cells[(0, 0)] = "Granite_Rough"
        fert = {"RM_FE_Ground_DeepAsh": 0.7, "WaterShallow": 0.0, "Granite_Rough": 0.0}
        out.append(("open_ground_outside: fertile land only", V.open_ground_outside(cells, fert, (), 18) == 79))
        out.append(("open_ground_outside: a pad's square is left out (as CountBurnedOutside does)",
                    V.open_ground_outside(cells, fert, ((2, 2),), 1) == 70))
        out.append(("open_ground_outside: a terrain with no fertility read is not ground", V.open_ground_outside(cells, {}, (), 18) == 0))
    except Exception as ex:   # noqa: BLE001
        out.append(("pure helpers crashed: %r" % ex, False))
    return out


class _FakeGame(object):
    """A scripted Pyrelands for _r6_burn_line: a clock, the two settings, saves, and a burned share that grows by day as
    `on_curve` with the wind carrying fire and as `off_curve` without (index = whole days since the start save)."""
    DAY = 60000

    def __init__(self, V, on_curve, off_curve, cut_hour=None):
        self.V, self.on_curve, self.off_curve, self.cut_hour = V, on_curve, off_curve, cut_hour
        self.tick, self.t0, self.saves = 1000, None, {}
        self.settings = {"burnLineEnabled": True, "windCarriesFireEnabled": True}
        self.share_reads, self.wind_at_reads, self.loads = [], [], []
        self.cells = dict(((x, z), "RM_FE_Ground_DeepAsh") for x in range(100) for z in range(100))
        self.ground = V.open_ground_outside(self.cells, {"RM_FE_Ground_DeepAsh": 0.7}, V.FIRE_PADS, V.R6_SHARE_PAD_RADIUS)

    def share(self):
        if self.t0 is None:
            return 0.01
        d = min((self.tick - self.t0) // self.DAY, len(self.on_curve) - 1)
        return (self.on_curve if self.settings["windCarriesFireEnabled"] else self.off_curve)[d]

    def call(self, tool, **kw):
        if tool == "rimworld/save_game":
            if kw.get("saveName") == self.V.R6_SHARE_SAVE:
                self.t0 = self.tick
            self.saves[kw.get("saveName")] = self.tick
            return {"success": True}
        if tool == "rimworld/load_game":
            self.loads.append(kw.get("saveName"))
            self.tick = self.saves[kw.get("saveName")]
            return {"success": True}
        if tool == "jawa/static_call" and kw.get("method") == "CountBurnedOutside":
            self.share_reads.append(self.tick - (self.t0 or self.tick))
            self.wind_at_reads.append(self.settings["windCarriesFireEnabled"])
            return {"success": True, "result": str(int(round(self.share() * self.ground)))}
        if tool == "jawa/get_terrain_batch":
            return {"success": True, "ops": "RM_FE_Ground_DeepAsh:0,0,100,100"}
        if tool == "jawa/get_defs":
            return {"success": True, "defs": [{"defName": "RM_FE_Ground_DeepAsh", "fields": {"fertility": 0.7}}]}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 100, "sizeZ": 100, "mapBiome": "RM_Pyrelands"}
        return {"success": True}


def run_fake_burn_line(V, game):
    """_r6_burn_line against `game` with the harness around it stubbed -> {component: verdict}, the share note."""
    import contextlib
    res, notes = {}, {}

    class T(object):
        upstream_failed = False
        components = []

        class session(object):
            @staticmethod
            def _ticks():
                return game.tick

        def bridge_call(self, tool, **kw):
            return game.call(tool, **kw)

        def screenshot(self, name=None, rect=None, ppc=None, padding=1):
            return "%s.png" % name

        def _record(self, *a):
            pass

    @contextlib.contextmanager
    def comp(t, name, **kw):
        try:
            yield t
            res[name] = "PASS"
        except V._Unmeasured:
            res[name] = "UNMEASURED"
        except V.ExpectationFailed:
            res[name] = "FAIL"
        t.upstream_failed = False

    def wait(t, n, fast=None):
        game.tick += n

    def fires(t):
        h = (game.tick - (game.t0 or game.tick)) // 2500
        if game.cut_hour is not None and h == game.cut_hour:
            raise V.ExpectationFailed("scripted: the hourly watch is cut at hour %d" % h)
        return [(10 + h, 10)] if game.settings["burnLineEnabled"] else []

    def set_(t, values):
        game.settings.update(values)

    stubs = {"_comp": comp, "_independent": lambda t: None, "_on_site": lambda t: None, "_wait": wait, "_set": set_,
             "_ten_static": lambda t, ty, m, args=None: "done=True;lit=4", "_ten_hour": lambda t: (game.tick / 2500.0) % 24,
             "_r6_guard": lambda t: {}, "_r6_guard_changes": lambda a, b: [], "_r6_fires": fires,
             "_note": lambda t, label, data: notes.__setitem__(label, data)}
    saved = dict((k, getattr(V, k)) for k in stubs)
    try:
        for k, v in stubs.items():
            setattr(V, k, v)
        V._GEN.pop("burn_share", None)
        V._r6_burn_line(T())
    finally:
        for k, v in saved.items():
            setattr(V, k, v)
    share = next((v for k, v in notes.items() if k.startswith("burned share")), None)
    return res, share


def chain_checks():
    """The share read wired into the chain (RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES), on a scripted game."""
    out = []
    try:
        V = load_validation()
        line, flood = [0.01, 0.01, 0.02, 0.03, 0.05], [0.01, 0.15, 0.40, 0.60, 0.81]
        day = _FakeGame.DAY
        g = _FakeGame(V, line, flood)
        res, note = run_fake_burn_line(V, g)
        out.append(("chain: a line with a flooding control passes burn_line_burned_share",
                    res.get("burn_line_burned_share") == "PASS"))
        out.append(("chain: each arm is read at the start's clock + 1..%d days" % V.R6_SHARE_DAYS,
                    g.share_reads == [0] + [d * day for d in range(1, V.R6_SHARE_DAYS + 1)] * 2))
        out.append(("chain: the wind-off arm is the start save reloaded, wind off at its reads, wind back on after",
                    g.loads == [V.R6_SHARE_SAVE] and g.wind_at_reads == [True] * (V.R6_SHARE_DAYS + 1) + [False] * V.R6_SHARE_DAYS
                    and g.settings["windCarriesFireEnabled"] is True))
        out.append(("chain: the note prints worst, limit and cases read",
                    bool(note) and abs((note.get("worstOn") or 0) - max(line)) < 1.0 / g.ground and note.get("limit") == V.R6_SHARE_MOST
                    and note.get("casesRead") == 2 * V.R6_SHARE_DAYS + 2))
        out.append(("chain: the front and burn-line-off rows still run",
                    res.get("burn_line_walks_hourly") == "PASS" and res.get("burn_line_off_control") == "PASS"))
        res, _ = run_fake_burn_line(V, _FakeGame(V, [0.01, 0.2, 0.4, 0.62, 0.8], flood))
        out.append(("chain: a wind-on flood FAILS burn_line_burned_share", res.get("burn_line_burned_share") == "FAIL"))
        res, _ = run_fake_burn_line(V, _FakeGame(V, line, [0.01, 0.05, 0.1, 0.2, 0.3]))
        out.append(("chain: a control that never floods is UNMEASURED, never PASS",
                    res.get("burn_line_burned_share") == "UNMEASURED"))
        g = _FakeGame(V, line, flood, cut_hour=5)
        res, _ = run_fake_burn_line(V, g)
        out.append(("chain: an hourly watch cut short still reads the full window",
                    res.get("burn_line_walks_hourly") == "FAIL" and res.get("burn_line_burned_share") == "PASS"
                    and g.share_reads[V.R6_SHARE_DAYS] == V.R6_SHARE_DAYS * day))
    except Exception as ex:   # noqa: BLE001 - a crash is a FAIL
        out.append(("chain checks crashed: %r" % ex, False))
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
    res = checks(text, rewards) + pure_checks() + chain_checks()
    for what, ok in res:
        print("%s %s" % ("PASS" if ok else "FAIL", what))
    bad = sum(1 for _, ok in res if not ok)
    print("%s: %d of %d checks failed" % (NAME, bad, len(res)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
