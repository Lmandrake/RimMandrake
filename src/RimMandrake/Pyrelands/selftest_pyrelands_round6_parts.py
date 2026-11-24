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
     ("ashfallAccumulationEnabled", "ambientAshEnabled", "ashground_noon", "R6_HALF_DAY", "is_standing_water(",
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
     # RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN: the Rain lock is weather_set's, the decider's roll is read,
     # and the control is the same site with the mechanics off (no vanilla control map)
     ("jawa/weather_set", "lockWeather", "jawa/weather_roll_next", "jawa/storyteller_swap", "GameCondition_ForceWeather",
      "jawa/weather_get", "Rain", "pyrelandsEnabled", "_unmeasured(")),
    ("sc_heat_dome", "heat_dome", False,
     ("bodyGraphic", "domeTexPath", "domeArt", "ppc=", "Burn", "DOME_HOLD_TICKS")),
    ("sc_furnace_giant", "ullai_and_giant", False,
     ("jawa/biome_probe", "biome_probe_animals(", "baseBodySize", "lifeStages", "drawSize",
      "R6_ROSTER_MIN", "giant_margin(", "_unmeasured(")),
    ("sc_burn_line_walks", "burn_line", False,
     ("ProbeOpeningFront", "R6_FRONT_HOURS", "_ten_hour(", "ppc=", "burn_line_walking", "rimworld/save_game",
      "front_walks(", "burnLineEnabled", "_r6_guard(",
      # RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES: the burned share of open plantable ground at each day end
      # over R6_SHARE_DAYS, and the same start save reloaded with windCarriesFireEnabled off as the flood control
      "CountBurnedOutside", "open_ground_outside(", "R6_SHARE_DAYS", "R6_SHARE_SAVE", "_load_site_save(",
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
        # visit 2 (2026-11-21): the control muffalo died by game hour 5 on the 50 C site; a 72 h SUM of falls compared the
        # ullai's three days with the muffalo's few hours. The rate per live hour is the measure.
        live = [[0.80, 0.80], [0.745, 0.745], [None, None], [None, None]]          # muffalo: one live hour, then gone
        slow = [[0.2697, 0.2698], [0.2685, 0.2686], [0.2673, 0.2674], [0.2662, 0.2663]]  # ullai: 0.0012 an hour
        r = V.thirst_fall_rates({"Muffalo": live, "RM_Ullai": slow})
        out.append(("thirst_fall_rates: a control that dies early is judged on its live hours",
                    r["Muffalo"] is not None and r["RM_Ullai"] < V.R6_THIRST_RATIO * r["Muffalo"]))
        r = V.thirst_fall_rates({"Muffalo": slow, "RM_Ullai": live})
        out.append(("thirst_fall_rates: ullai falling as fast as the control is over the ratio",
                    r["RM_Ullai"] > V.R6_THIRST_RATIO * r["Muffalo"]))
        r = V.thirst_fall_rates({"Muffalo": [[None], [None]], "RM_Ullai": slow})
        out.append(("thirst_fall_rates: a control with no live hour reads None", r["Muffalo"] is None))
        r = V.thirst_fall_rates({"Muffalo": [[0.5, 0.4], [0.6, 0.3]], "RM_Ullai": slow})
        out.append(("thirst_fall_rates: a drink (a rise) is not a fall", abs(r["Muffalo"] - 0.05) < 1e-9))
        # visit 2: herds_of links natives transitively, days after the stagger; two staggered herds read as one "far
        # apart" herd. The spawned ullai herd, read just after the stagger, is the measure.
        out.append(("one_herd_level: four ullai on one level pass", V.one_herd_level([0.4371, 0.4372, 0.4370, 0.4371])[0] is True))
        out.append(("one_herd_level: two levels in one herd fail", V.one_herd_level([0.84, 0.7275, 0.7275, 0.84])[0] is False))
        out.append(("one_herd_level: an unstaggered herd (FlowWorks' 0.8 start) fails",
                    V.one_herd_level([0.8, 0.8, 0.8, 0.8])[0] is False))
        out.append(("one_herd_level: an unreadable animal is None", V.one_herd_level([0.5, None])[0] is None))
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
        # _r6_shore_ring: standing water only (visit 2, 2026-11-20: a mud relic with no water passed the water assert)
        relic = {(0, 0): "Mud", (1, 0): "RM_FE_Ground_Soil", (2, 0): "RM_FE_Ash_Deep"}
        out.append(("shore ring: mud with no water beside it is no water", V._r6_shore_ring(relic)[0] == set()))
        pond = {(0, 0): "WaterShallow", (1, 0): "Mud", (2, 0): "RM_FE_Ground_SoilRich", (0, 1): "Marsh"}
        w, ring = V._r6_shore_ring(pond)
        out.append(("shore ring: shallow water and marsh are water, mud is their ring",
                    w == {(0, 0), (0, 1)} and ring.get((1, 0)) == "Mud" and (2, 0) not in ring))
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
        if tool == "jawa/static_call" and kw.get("method") == "RearmOpeningFront":
            return {"success": True, "result": "1"}
        if tool == "jawa/map_comp_set":   # _stage_quiet puts the quiet counter near its end
            return {"success": True, "after": kw.get("value")}
        if tool == "jawa/mod_settings_field" and kw.get("action") == "get":   # the off-control reads what it holds
            return {"success": True, "value": str(self.settings.get(kw.get("field"), True))}
        return {"success": True}


def run_fake_burn_line(V, game, real_fires=False):
    """_r6_burn_line against `game` with the harness around it stubbed -> {component: verdict}, the share note. With
    `real_fires` the fires are read by validation.py's own reader from `game`'s jawa/list_things rows (and the opening
    front from its ProbeOpeningFront), not by the stub: the stub hid a reader that dropped every row (visit 2)."""
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
             "_ten_static": lambda t, ty, m, args=None: "done=True;lit=4;litTick=%d" % game.tick,
             "_ten_hour": lambda t: (game.tick / 2500.0) % 24,
             "_r6_guard": lambda t: {}, "_r6_guard_changes": lambda a, b: [], "_r6_fires": fires,
             "_note": lambda t, label, data: notes.__setitem__(label, data)}
    if real_fires:
        for k in ("_r6_fires", "_ten_static"):
            del stubs[k]
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

CS_ROWS = os.path.join(HERE, "..", "bridgetools", "JawaBench.BridgeTools", "JawaBenchTerrainTools.cs")


def list_things_row_keys():
    """The field names of one jawa/list_things row, read from the bridge's own ThingListRow (the shape the live reader gets)."""
    text = open(CS_ROWS, encoding="utf-8").read()
    m = re.search(r"static object ThingListRow\(Thing thing, IntVec3 pos\)(.*?)\n        \}", text, re.S)
    if not m:
        return None
    return re.findall(r"^\s*(\w+)\s*=", m.group(1).split("new", 1)[1], re.M)


def bridge_fire_row(keys, i, x, z):
    """A Fire row with exactly the bridge's keys."""
    vals = {"id": "Fire%d" % (9000 + i), "def": "Fire", "label": "Fire", "x": x, "z": z, "spawned": True, "rot": 0,
            "stackCount": 1, "hitPoints": -1, "maxHitPoints": -1}
    return dict((k, vals.get(k)) for k in keys)


def blind_reader(rows):
    """PLANTED FAULT: the reader as visit 2 ran it: a dict `position` first, so a row with x and z and no position read
    (None, None) and was dropped."""
    out = []
    for f in rows:
        if f.get("parent"):
            continue
        p = f.get("position") or {}
        x, z = (p.get("x"), p.get("z")) if isinstance(p, dict) else (f.get("x"), f.get("z"))
        if x is not None and z is not None:
            out.append((int(x), int(z)))
    return out


class _WalkGame(_FakeGame):
    """_FakeGame with fires a reader must find: jawa/list_things answers rows in the bridge's shape. Nothing burns until
    RearmOpeningFront (fire clock on) lights the opening front on the next watch interval; it walks one cell east an hour
    and burns until the map is extinguished. mode: "walk" (as shipped), "still" (a front that does not move), "dark"
    (no fire at hour 6), "unlit" (the re-arm lights nothing), "noxz" (rows with no cell), "offleak" (fire with
    burnLineEnabled off after an extinguish: the off control must see it)."""

    def __init__(self, V, keys, mode="walk"):
        _FakeGame.__init__(self, V, [0.01, 0.01, 0.02, 0.03, 0.05], [0.01, 0.15, 0.40, 0.60, 0.81])
        self.keys, self.mode = keys, mode
        self.settings["fireClockEnabled"] = False
        self.lit_tick, self.rearm_tick, self.lit_reads = -1, None, []
        self.reseed = [(50 + i, 60) for i in range(12)]   # burn_line_present's reseeded line, still burning

    def fire_cells(self):
        if self.mode == "offleak" and not self.settings["burnLineEnabled"]:
            return [(5, 5)]
        if self.lit_tick < 0 or self.tick < self.lit_tick:
            return list(self.reseed)
        h = (self.tick - self.lit_tick) // 2500
        if self.mode == "dark" and h == 6:
            return []
        x = 10 if self.mode == "still" else 10 + h
        return list(self.reseed) + [(x, 10 + k) for k in range(4)]

    def call(self, tool, **kw):
        if tool == "jawa/map_fire" and kw.get("action") == "extinguish":
            self.reseed, self.lit_tick = [], -1
            return {"success": True}
        if tool == "jawa/static_call" and kw.get("method") == "RearmOpeningFront":
            self.rearm_tick = self.tick
            if self.settings["fireClockEnabled"] and self.mode != "unlit":
                self.lit_tick = self.tick + 60
            return {"success": True, "result": "1"}
        if tool == "jawa/static_call" and kw.get("method") == "ProbeOpeningFront":
            lit = self.lit_tick >= 0 and self.tick >= self.lit_tick
            self.lit_reads.append(lit)
            return {"success": True, "result": "done=%s;lit=%d;litTick=%d;mapAge=900000;now=%d"
                    % (lit, 5 if lit else 0, self.lit_tick if lit else 620039, self.tick)}
        if tool == "jawa/list_things" and kw.get("defName") == "Fire":
            cells = self.fire_cells()
            if self.mode == "noxz":
                return {"success": True, "things": [{"id": "Fire1", "def": "Fire"}] if cells else []}
            return {"success": True, "things": [bridge_fire_row(self.keys, i, x, z) for i, (x, z) in enumerate(cells)]}
        return _FakeGame.call(self, tool, **kw)


def fire_reader_checks():
    """RIMMANDRAKE_REORDER_PYRE_BURN_WALK_BEFORE_ITS_FRONT_DIES: visit 2's walk read 0 fires at all 24 hours, 2 of 2 runs,
    while burn_line_present had just counted 12 through the same tool. The reader looked for `position`; the bridge's row
    has x and z. Here the reader meets rows in the bridge's own shape, and the walk runs on a front it must find."""
    out = []
    try:
        V = load_validation()
        keys = list_things_row_keys()
        out.append(("bridge row: ThingListRow carries x and z, no position or parent (%s)" % keys,
                    bool(keys) and "x" in keys and "z" in keys and "position" not in keys and "parent" not in keys))
        rows = [bridge_fire_row(keys or ["x", "z"], i, 40 + i, 12) for i in range(12)]
        cells, unplaced = V.fire_cells(rows)
        out.append(("fire_cells: 12 bridge rows read as 12 cells", cells == [(40 + i, 12) for i in range(12)] and not unplaced))
        out.append(("PLANTED FAULT the position-first reader reads 0 of the same 12", blind_reader(rows) == []))
        out.append(("fire_cells: a dict or list position is read too",
                    V.fire_cells([{"position": {"x": 3, "z": 4}}, {"position": [5, 0, 6]}])[0] == [(3, 4), (5, 6)]))
        out.append(("fire_cells: no rows is an empty read", V.fire_cells([]) == ([], [])))
        out.append(("fire_cells: an attached fire (parent) is not the burn line",
                    V.fire_cells([{"x": 1, "z": 1, "parent": "Ullai12"}]) == ([], [])))
        c, bad = V.fire_cells([{"id": "Fire1", "def": "Fire"}, {"x": 2, "z": 3}])
        out.append(("fire_cells: a row with no cell is returned as unplaced, never dropped", c == [(2, 3)] and len(bad) == 1))
    except Exception as ex:   # noqa: BLE001 - a crash is a FAIL
        out.append(("fire reader checks crashed: %r" % ex, False))
    try:
        V = load_validation()
        keys = list_things_row_keys()

        def walk(mode):
            g = _WalkGame(V, keys or ["x", "z"], mode)
            res, _ = run_fake_burn_line(V, g, real_fires=True)
            return g, res
        g, res = walk("walk")
        out.append(("walk, real reader: the re-armed opening front is found and walks (PASS)",
                    res.get("burn_line_walks_hourly") == "PASS" and g.rearm_tick is not None
                    and g.settings["fireClockEnabled"] is True))
        out.append(("walk, real reader: burn_line_present's reseed is put out before the re-arm (the watch reads the front)",
                    g.reseed == []))
        out.append(("walk, real reader: the burn-line-off control reads a cleared map (PASS)",
                    res.get("burn_line_off_control") == "PASS"))
        out.append(("walk, real reader: a front that does not move FAILS", walk("still")[1].get("burn_line_walks_hourly") == "FAIL"))
        out.append(("walk, real reader: an hour with no fire FAILS", walk("dark")[1].get("burn_line_walks_hourly") == "FAIL"))
        g, res = walk("unlit")
        out.append(("walk, real reader: a re-arm that lights nothing is UNMEASURED before the day is spent",
                    res.get("burn_line_walks_hourly") == "UNMEASURED"
                    and g.tick - g.rearm_tick == V.OPENING_WAIT_TICKS + 2 * V.BURN_WATCH_TICKS + V.OFF_CONTROL_WAIT_TICKS))   # the off control's wait only (the staged quiet, then four reseed retries)
        out.append(("walk, real reader: rows with no cell are UNMEASURED, never 0 fires",
                    walk("noxz")[1].get("burn_line_walks_hourly") == "UNMEASURED"))
        out.append(("off control, real reader: fire with burnLineEnabled off FAILS",
                    walk("offleak")[1].get("burn_line_off_control") == "FAIL"))
        saved = V._r6_fires
        try:
            V._r6_fires = lambda t: blind_reader(V._things(t, "Fire", limit=2000))
            g, res = walk("walk")
        finally:
            V._r6_fires = saved
        out.append(("PLANTED FAULT the position-first reader FAILS the same walking front",
                    res.get("burn_line_walks_hourly") == "FAIL"))
    except Exception as ex:   # noqa: BLE001 - a crash is a FAIL
        out.append(("walk checks crashed: %r" % ex, False))
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
    res = checks(text, rewards) + pure_checks() + chain_checks() + fire_reader_checks()
    for what, ok in res:
        print("%s %s" % ("PASS" if ok else "FAIL", what))
    bad = sum(1 for _, ok in res if not ok)
    print("%s: %d of %d checks failed" % (NAME, bad, len(res)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
