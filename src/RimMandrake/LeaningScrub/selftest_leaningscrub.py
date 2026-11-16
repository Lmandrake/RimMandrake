#!/usr/bin/env python3
# selftest-timeout: 600   (healthy + ~270 breaks run ~420 s alone; the 240 s default CRASHed it as [timeout])
"""Offline selftest for LeaningScrub's validation.py: a scripted FAKE GAME that implements the
mod's behaviours, run (1) healthy -- every component must PASS -- and (2) once per mod behaviour
broken -- the named component must go FAIL and no other component may.

That second half is the proof every check can fail: each break is a mod defect (a patch that is
not armed, a toggle that gates nothing, an effect that never fires) and the suite must see it.
The fake encodes the response SHAPES validation.py assumes (read off the JawaBench [Tool]
descriptions and Pyrelands' live-measured helpers); it proves the predicates and wiring, not the
shapes -- those are UNPROVEN until the first live run.

    python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py
"""
import copy
import math
import random
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

spec = importlib.util.spec_from_file_location("lscrub_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait poll loop must not really sleep
V.SCENE_RECORD = lambda *a: None                   # a fake scene must not write designer_stage's stage.json
V.OWNER_PRESENT = True                             # the eruptor arm runs here: this game is fake, nothing flies
V.CAST_TILES = (11, 12, 13)                        # sc_native_cast's three map-free fixture tiles
V.DRIP_STARTUP = "true"                            # sc_dripping's clean-start arm: the fake starts with regrowth saved on
V.BLIND_READ, V.ART_EVAL = "fake:blind", "fake:art"  # floor_visual's judge files: the fake answers both
V.EVIDENCE_HOOK = "RimMandrake.RimProperty.FakeEvidenceProof.ProofArm"   # sc_maker's store fixture (fake type)
V.RAID_WEIGHT_HOOK = "RimMandrake.LeaningScrub.FakeRaidWeight.ChanceFactorNow"   # sc_raid_weight's reader (fake type)
V.CAPACITY_HOOK = "RimMandrake.LeaningScrub.FakeCapacity.Level"      # sc_gale_exposure's live reader (fake)
V.HOLLOW_CRAWL_JOB = "RM_FakeHollowCrawl"           # sc_hollow's crawl job as the spec designs it (fake)
V.WIND_TILES = (21, 22)                            # sc_wind_plain's two fixture tiles (TILE_GEO: either side of lon 0)
V.WIND_HOOK = "RimMandrake.LeaningScrub.FakeWind.Speed"        # sc_wind_plain's live wind reader (fake type)
V.ISLAND_TILES = (31, 32, 33)                      # sc_island_land's three fixture tiles
V.ISLAND_START_HOOK = "RimMandrake.LeaningScrub.FakeIslandStart.Start"   # sc_island_land's start reader (fake)
V.MESSAGE_HOOK = "RimMandrake.LeaningScrub.FakeMessages.Count"       # sc_rearing's live Messages reader (fake)
V.REVEAL_HOOK = "RimMandrake.LeaningScrub.FakeReveal.Pawn"           # sc_rearing's conceal fixture + reader (fake)
V.PILLOW_HOOK = "RimMandrake.LeaningScrub.FakeWetness.At"            # sc_pillowmoss's wetness reader (fake)
FAKE_WIND = {"RM_ScrubWind": (1.0, 0.5), "RM_ScrubWindFog": (1.0, 0.4), "RM_ScrubOvercast": (1.0, 0.5),
             "RM_ScrubGrayPall": (1.0, 0.4), "RM_ScrubDryThunderstorm": (1.5, 1.25), "RM_Stall": (0.0, 0.0),
             "RM_Gale": (1.5, 1.5)}       # the loaded (factor, offset) of the seven, as RM_LeaningScrub_*.xml ship them
TILE_GEO = {21: (12.0, 35.0), 22: (-20.0, -50.0)}  # (latitude, longitude); every other map reads HOME_GEO
HOME_GEO = (5.0, 20.0)
ISLAND_START = (125, 125)

from suite import TestContext                     # noqa: E402

_CLASS_RE = re.compile(r"\n    (?:public |internal )?(?:static )?(?:sealed )?(?:partial )?class (\w+)")
_ARITY = {}


def cs_arities(type_name, method):
    """Parameter counts of every `public static` overload of `method` on the mod's own C# class `type_name` (read off
    Source/*.cs). The fake's static_call resolves through this exactly as jawa/static_call does live (args split on
    '|', the arg count picks the overload), so a caller passing "<form>|<mode>" to a one-parameter method fails here
    offline instead of live (LIVE 2026-10-16: twelve forms rows read 'No public static ProofForm with 2 params')."""
    key = (type_name, method)
    if key not in _ARITY:
        cls = type_name.rsplit(".", 1)[-1]
        found = set()
        for root, _dirs, files in os.walk(os.path.join(HERE, "Source")):
            for f in files:
                if not f.endswith(".cs"):
                    continue
                src = open(os.path.join(root, f), encoding="utf-8-sig").read()
                heads = [(m.start(), m.group(1)) for m in _CLASS_RE.finditer(src)]
                for i, (start, name) in enumerate(heads):
                    if name != cls:
                        continue
                    body = src[start:heads[i + 1][0] if i + 1 < len(heads) else len(src)]
                    for m in re.finditer(r"public static \w+(?:<[^>]*>)? %s\(([^)]*)\)" % re.escape(method), body):
                        a = m.group(1).strip()
                        found.add(0 if not a else a.count(",") + 1)
        _ARITY[key] = found
    return _ARITY[key]


BODY = {"RM_Thornhold": 0.4, "RM_Shirrel": 0.7, "RM_Dustflutter": 0.08, "RM_Crustweevil": 0.05,
        "RM_Fuzzrunner": 0.2, "RM_Vissler": 0.15, "Colonist": 1.0, "RM_Ribbonwhip": 0.25, "Muffalo": 2.4}
BLOOM = {"RM_Crustweevil", "RM_Fuzzrunner", "RM_Dustflutter", "RM_Vissler"}
MEAT_EATERS = ("RM_Surrik", "RM_Ribbonwhip")        # ProofArmScavengers' fake answer names these two
SMALL_SPAWN_ONLY = None


def _cs_cell(s):
    """IntVec3.ToString as the C# proof replies print a cell: "x,z" -> "(x, 0, z)"."""
    x, z = [int(v) for v in s.split(",")]
    return "(%d, 0, %d)" % (x, z)


def rect(s):
    return [int(v) for v in str(s).split(",")]


def inrect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class Fake(object):
    def __init__(self, broken=()):
        self.broken = set(broken)
        self.ticks = 1000
        self.n = 0
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        self.queued = []       # incidents a raid-weight read queued (it must queue none)
        if "setting_missing" in self.broken:
            del self.settings["leanFireBias"]
        self.weather, self.things, self.pawns = "RM_ScrubWind", {}, {}
        self.rooms, self.claims, self.jobs, self.log = [], {}, {}, []
        self.walker_until, self.bloom_done, self.tick_hist = -1, False, 0
        self.paths = {}
        self.polluted = set()
        self.saves, self.walker_z = {}, None
        self.cur_map, self.gen_maps, self.letters, self.scanner = 0, {}, [], {}
        self.master_was_off, self.save_count = False, 0
        self.crown_forgets, self.roofed, self.floors, self.zones = False, set(), set(), set()
        self.rng, self.pending_fire, self.pursuit, self.drip_applied = random.Random(7), [], None, True
        self.last_blaze, self.cut_now = (0, 0), False
        # batch 5: the base stamper the rehome owes (a fake franchise-free kind), the Gale overlay clock, the selection
        self.stamper_kinds = {V.STAMPER} | (set() if "no_base_stamper" in self.broken else {"RM_Thunderstep"})
        self.gale_last, self.selected, self.shots = None, None, {}
        # batch 8: live Messages, Pillowmoss wetness (cell -> last fog tick), the ProximityHatch settings, ribbon dice
        self.messages, self.wet, self.hatch, self.ribbon_rng = [], {}, {"enabled": "True"}, random.Random(11)
        self.scene = None
        self.about = "A flat, wind-scoured plain." + (" Two bark-wardens sleep on every tree." if "about_promises_wardens"
                                                       in self.broken else "")

    # ------------------------------------------------------------ session surface
    def _ticks(self):
        return self.ticks

    def track(self, *a, **k):
        pass

    def things_at(self, x, z):
        return []

    def call(self, tool, **p):
        h = getattr(self, "t_" + tool.split("/")[-1], None)
        if h is None:
            return {"success": True}
        return h(**p)

    def new(self, d, x, z, **kw):
        self.n += 1
        tid = "T%d" % self.n
        row = dict(id=tid, **dict(kw, x=x, z=z))
        row["def"] = d
        self.things[tid] = row
        return tid

    def of(self, d):
        return [t for t in self.things.values() if t["def"] == d]

    def on(self, f):
        return self.settings.get("modEnabled") == "True" and self.settings.get(f) == "True"

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            self.ticks += d
            self.last_d = d
            self.creep_tick(self.ticks - d, self.ticks)
            self.rear_pass()              # the 30-tick sweep sees a pawn where it spawned, and again where it walked
            self.chunk(d)
            self.ripple_pass()
            self.lure_pass(d)
            self.fire_pass()
            self.route_pass()
            self.viper_pass()
            self.rear_pass()
            self.quench_pass()
            self.hatch_pass()
            self.pillow_pass()
            self.ribbon_pass(d)

    def chunk(self, d):
        b = self.broken
        # --- jobs
        for pid, job in list(self.jobs.items()):
            job["left"] -= d
            if job["left"] > 0:
                continue
            del self.jobs[pid]
            if job["kind"] == "smother" and "no_smother_bank" not in b:
                st = self.things.get(job["a"])
                bl = self.things.get(job["b"])
                if st and bl and bl.get("stackCount", 0) > 0:
                    bl["stackCount"] -= 1
                    self.claims[st["id"]] = self.ticks
                    st["smother_start"] = self.ticks
            if job["kind"] == "refuel" and "fuel_unpatched" not in b:
                bl, fire = self.things.get(job["b"]), self.things.get(job["a"])
                if bl and fire:
                    c = self.credit(bl["def"])
                    n = min(bl["stackCount"], int(-(-(20 - self.fuel(fire["id"])) // c)))
                    bl["stackCount"] -= n
                    fire["fuel_level"], fire["fuel_at"] = min(20.0, self.fuel(fire["id"]) + n * c), self.ticks
                    fire["burning"] = bl["def"]
            if job["kind"] == "repair" and job["a"] in self.things and "repair_never_fixes" not in b:
                self.things[job["a"]]["broken"] = False
            if job["kind"] == "harvest" and job["a"] in self.things:
                pl = self.things.get(job["a"])
                if pl:
                    self.new("RM_RawVenom", pl["x"], pl["z"], stackCount=3)
                    if "regrow_broken" in b or not (self.drip_applied or "regrow_ignores_write" in b):
                        del self.things[pl["id"]]
                    else:
                        pl["growth"] = 1.0 if "regrow_full" in b else 0.3
        for pl in self.of("RM_DrippingVenomvine"):
            pl["growth"] = min(1.0, pl.get("growth", 1.0) + d / 4000.0)
        # --- the Stall freeze and wandering
        self.crown_pass()
        self.graze_pass(d)
        for p in self.pawns.values():
            if p["faction"] != "none" or p["dead"]:
                continue
            gate = self.on("stallFreezeEnabled")
            if "master_ignored" in b:
                gate = self.settings.get("stallFreezeEnabled") == "True"
            if "freeze_ignores_toggle" in b:
                gate = True
            frozen = (self.weather == "RM_Stall" and BODY.get(p["kind"], 1) <= 0.5
                      and "no_freeze" not in b and gate)
            if p["kind"] == "RM_Dustflutter" and (p.get("mob") or p.get("goto")):
                continue      # on the crown mob's Goto, settled at the stand, or on an ordered walk: keeps its job
            if p.get("job") == "Ingest":     # the scenes: a hungry animal walking to its meal does not wander
                continue
            if p.get("hold"):                # an ordered wait or walk holds its own job (the lee scene)
                continue
            p["job"] = "Wait_Wander" if frozen else "GotoWander"
            walled = any(inrect(p["x"], p["z"], r) for r in self.rooms)
            if not frozen and not walled:     # wander stays local (the scenes run thousands of ticks on one animal)
                p["x"] += 1 if (self.ticks // 250) % 2 else -1
        # --- Gale: deafen
        if self.weather == "RM_Gale":
            gate = self.on("galeDeafenEnabled") or "deafen_ignores_toggle" in b
            self.gale_last = self.ticks
            for p in self.pawns.values():
                if p["faction"] != "player" or "no_deafen" in b or not gate:
                    continue
                if p["kind"].startswith("Mech_") and "deafen_ignores_mech" not in b:     # RaceProps.IsMechanoid
                    continue
                roofed = any(inrect(p["x"], p["z"], r) for r in self.rooms)
                if roofed and "deafen_ignores_roof" not in b:
                    continue
                if "RM_GaleDeafened" not in p["hediffs"]:
                    p["hediffs"].append("RM_GaleDeafened")
        elif self.ticks - getattr(self, "gale_last", -10 ** 9) >= 2500 and "deafen_never_recovers" not in b:
            for p in self.pawns.values():      # severityPerDay -24: gone a day (2500 ticks) after the last refresh
                if "RM_GaleDeafened" in p["hediffs"]:
                    p["hediffs"].remove("RM_GaleDeafened")
        # --- batteries charge from a whole colony turbine; the hoard sweeps its 3x3
        if "battery_never_charges" not in b and any(t.get("faction") == "PlayerColony" and not t.get("broken")
                                                    for t in self.of("WindTurbine")):
            for t in self.of("Battery"):
                t["stored"] = t.get("stored", 0.0) + 0.1 * d
        self.hoard_pass()
        # --- turbines (2500 boundary)
        if self.ticks // 2500 != self.tick_hist:
            self.tick_hist = self.ticks // 2500
            if (self.weather == "RM_Gale" and self.on("galeTurbineSurgeEnabled")
                    and (0 < float(self.settings["galeTurbineBreakdownMtbDays"]) or "breaks_at_mtb_zero" in b)
                    and float(self.settings["galeTurbineBreakdownMtbDays"]) < 0.1
                    and "no_breakdown" not in b):
                for t in self.of("WindTurbine"):
                    if t.get("faction") == "PlayerColony" or "breaks_unowned" in b:    # allBuildingsColonist only
                        t["broken"] = True
            # smother maturation
            if self.on("smotherCraftEnabled") or "smother_ignores_toggle" in b:
                days = float(self.settings["smotherDays"])
                for sid, start in list(self.claims.items()):
                    if "no_mature" in b:
                        continue
                    if self.ticks >= start + days * 60000 and sid in self.things:
                        st = self.things.pop(sid)
                        del self.claims[sid]
                        self.new("RM_DeadVenomvine", st["x"], st["z"], stackCount=40)
        # --- ambient: a hot map gives a colonist whole-body heatstroke a while after spawning (LIVE 2026-10-07)
        for p in self.pawns.values():
            if p["faction"] == "player" and self.ticks - p.get("born", self.ticks) >= 150 \
                    and "Heatstroke" not in p["hediffs"]:
                p["hediffs"].append("Heatstroke")
        # --- lash
        for pl in self.of("RM_TwitcherVenomvine"):
            enabled = self.on("twitcherLashEnabled") or "lash_ignores_toggle" in b
            if "no_lash" in b or not enabled:
                continue
            if self.ticks < pl.get("ready", 0):
                continue
            for p in self.pawns.values():
                if p["faction"] == "player" and abs(p["x"] - pl["x"]) <= 1 and abs(p["z"] - pl["z"]) <= 1:
                    p["hediffs"].append("Cut")
                    pl["ready"] = self.ticks + (60 if "lash_repeats" in b else 3600)
                    break
        # --- runway bloom
        if self.ticks <= self.walker_until and not self.bloom_done:
            if self.on("runwayBloomEnabled") or "bloom_ignores_toggle" in b:
                if "no_bloom" not in b:
                    self.bloom_done = True
                    arms = 0
                    # cover: a bloom needs fuzz on the walker's row (the scenes' bare-ground control)
                    cover = self.walker_z is None or "bloom_bare_ground" in b or any(
                        t["def"] == "RM_Fuzz" and abs(t["z"] - self.walker_z) <= 2 for t in self.things.values())
                    for p in self.pawns.values():
                        if not cover or p["faction"] != "none":
                            continue
                        if p["kind"] == "RM_Ribbonwhip" and not ("ribbon_no_sway" in b and self.in_ribbon_scene()):
                            p["sway_until"] = self.ticks + (10 ** 9 if "sway_never_released" in b else 180)
                        if p["kind"] == "RM_Surrik" and "hole_never" not in b:
                            self.new(V.SURRIK_HOLE, p["x"], p["z"], stackCount=1)
                        if p["kind"] in BLOOM:
                            p["flee_until"] = self.ticks + 300
                            if p["kind"] == "RM_Dustflutter" and "eruptor_grounded" not in b:
                                p["flying"] = True
                            lost = p.setdefault("lost", [])
                            if p["kind"] == "RM_Vissler" and arms < 4 and (len(lost) < V.VISSLER_ARMS
                                                                          or "shed_without_loss" in b):
                                arms += 1
                                self.new("RM_VisslerArm", p["x"], p["z"], stackCount=1, born=self.ticks)
                                if "shed_without_loss" not in b:
                                    lost.append(self.ticks)
        # --- the scenes: a missing vissler arm regrows one 15-day season after its own loss
        season = V.SEASON_TICKS // (2 if "regrow_early" in b else 1)
        for p in self.pawns.values():
            if p.get("lost") and "regrow_never" not in b:
                p["lost"] = [l for l in p["lost"] if self.ticks < l + season]
        # --- the scenes: a hungry meat eater walks to a reachable vissler arm and eats it (the toggle gates it)
        for p in self.pawns.values():
            if p.get("food", 1.0) >= 0.3 or p["faction"] != "none" or "arm_never_eaten" in b:
                continue
            if not (p["kind"] in MEAT_EATERS or ("arm_herbivore_eats" in b and p["kind"] == "Muffalo")):
                continue
            if not (self.on("visslerArmFoodEnabled") or "arm_eaten_off" in b):
                continue
            arms = [t for t in self.of("RM_VisslerArm") if abs(t["x"] - p["x"]) + abs(t["z"] - p["z"]) <= 30 and (
                "arm_eaten_through_walls" in b or not any(inrect(t["x"], t["z"], r) != inrect(p["x"], p["z"], r)
                                                          for r in self.rooms))]
            if arms and p.get("job") == "Ingest":
                del self.things[arms[0]["id"]]
                p["food"], p["job"] = 0.8, "Wait_Wander"
            elif arms:
                p["job"] = "Ingest"
        # --- sweetline scratching (one ordered rub at a time)
        sc = getattr(self, "scratch", None)
        if sc and self.ticks >= sc["due"]:
            self.scratch = None
            trs = self.of(V.TREE)
            if trs and "no_scratch" not in b:
                self.new("WoolSheep", trs[0]["x"] + 1, trs[0]["z"], stackCount=36)
                trs[0]["felt"] = trs[0].get("felt", 0) + 2.25
        # --- sweetline wool
        for tr in self.of(V.TREE):
            tr.setdefault("wool", self.ticks + 3 * 60000)
            long_tick = self.ticks // 2000 != (self.ticks - d) // 2000
            if self.on("sweetlineStationsEnabled") and "no_wool" not in b and long_tick \
                    and self.ticks >= tr["wool"]:
                tr["wool"] = self.ticks + 5 * 60000
                self.new("RM_SweetlineWool", tr["x"], tr["z"], stackCount=5)
            tr.setdefault("visit", self.ticks + 8 * 60000)
            tr.setdefault("visits", 0)
            if self.on("sweetlineStationsEnabled") and long_tick and "no_visits" not in b \
                    and (self.on("sweetlineVisitorsEnabled") or "visitors_ignore_toggle" in b) \
                    and self.ticks >= tr["visit"]:
                tr["visit"] = self.ticks + 8 * 60000
                tr["visits"] += 1
                self.new("RM_SweetlineToken", tr["x"], tr["z"], stackCount=1)

    # ------------------------------------------------------------ tools
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_play_for(self, durationMs=0, speed=None, **k):
        # MODCHECK_ULTRAFAST_CLOCK_STALL_1: helpers.fast_advance drives play_for (~400 ticks/s at Ultrafast, MEASURED
        # 2026-10-09); rimworld/set_time_speed left the live game paused and is no longer called.
        self.advance(int(int(durationMs) * 0.4))
        return {"success": True}

    def t_set_game_speed(self, speed=None, **k):
        return {"success": True, "speedAfter": speed}

    def t_get_game_info(self, **k):
        return {"success": True, "ticksGame": self.ticks}

    def t_time_set_ticks(self, ticks=0, **k):
        self.ticks = int(ticks)
        return {"success": True}

    def t_weather_set(self, weather=None, lockWeather=False, unlock=False, **k):
        if weather:
            if weather == "RM_Gale" and self.weather != "RM_Gale":
                self.walk_onset()
            self.weather = weather
        return {"success": True}

    def t_weather_get(self, **k):
        return {"success": True, "weather": {"current": self.weather}}

    def t_mod_settings_field(self, typeName=None, action=None, field=None, value=None, **k):
        if typeName == V.HATCH_SETTINGS:
            if action == "set":
                self.hatch[field] = str(value)
            return {"success": True, "value": self.hatch.get(field)}
        if typeName == V.SCANNER_SETTINGS:
            if action == "set":
                self.scanner[field] = str(value)
            return {"success": True, "value": self.scanner.get(field)}
        if field not in self.settings:
            return {"success": False, "message": "no such field"}
        if action == "set":
            self.settings[field] = str(value)
        return {"success": True, "value": self.settings[field]}

    def t_get_defs(self, defs="", fields=None, limit=200, **k):
        want = [d for d in defs.split(";") if d]
        if want == ["BiomeDef/RM_LeaningScrub"]:
            table = [{"weather": w, "commonality": c} for w, c in
                     (("RM_ScrubWind", 28), ("RM_ScrubWindFog", 40), ("RM_Stall", 3), ("RM_Gale", 7),
                      ("RM_ScrubDryThunderstorm", 1), ("RM_ScrubGrayPall", 1), ("RM_ScrubOvercast", 5), ("Rain", 0))]
            if "no_weather_entry" in self.broken:
                table = [r for r in table if r["weather"] != "RM_Gale"]
            if "stock_overcast" in self.broken:
                table = [r for r in table if r["weather"] != "RM_ScrubOvercast"] + [{"weather": "Overcast", "commonality": 5}]
            plants = [{"plant": n, "commonality": 0.1} for n in
                      ("RM_Fuzz", "RM_VenomvineThicket", "RM_DrippingVenomvine", "RM_TwitcherVenomvine",
                       "RM_HollowVenomvine", "RM_CrownVenomvine", "RM_Whipfuzz", "RM_Cruststar")
                      + V.FORM_PLANTS]
            ext = [] if "no_lean_ext" in self.broken else ["RM_LeanExtension"]
            if "payload_not_attached" not in self.broken:
                ext.append("RimMandrake.AcousticScanner.RM_AcousticPayloadExtension")
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{
                "defName": "RM_LeaningScrub", "fields": {
                    "baseWeatherCommonalities": table, "animalDensity": 1.8, "wildPlants": plants,
                    "wildAnimals": [{"animal": "RM_Surrik", "commonality": 1.0}, {"animal": "RM_Ribbonwhip", "commonality": 0.5}],
                    "modExtensions": ext}}]}
        if want and sorted(w.split("/", 1)[1] for w in want) == sorted(V.WIND_WEATHERS):
            rows = dict(FAKE_WIND)
            if "stall_blows" in self.broken:
                rows["RM_Stall"] = (0.0, 0.3)
            if "lean_toggle_moves_weather" in self.broken and self.settings.get("leanPlantsEnabled") == "False":
                rows["RM_ScrubWind"] = (1.0, 0.2)
            return {"success": True, "foundCount": 7, "notFound": [], "defs": [
                {"defName": n, "fields": {"windSpeedFactor": f, "windSpeedOffset": o}} for n, (f, o) in sorted(rows.items())]}
        if want and all(w.startswith("WeatherDef/RM_Scrub") for w in want):
            rows = []
            for w in want:
                n = w.split("/", 1)[1]
                off = 0.0 if ("twin_calm" in self.broken and n == "RM_ScrubGrayPall") else 0.4
                rows.append({"defName": n, "fields": {"windSpeedOffset": off, "windSpeedFactor": 1.0}})
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
        if want == ["BiomeDef/%s" % V.CAST_CONTROL_BIOME]:
            wt = [{"weather": "Clear", "commonality": 18}, {"weather": "DryThunderstorm", "commonality": 1}]
            if "twins_global" in self.broken:
                wt.append({"weather": "RM_ScrubOvercast", "commonality": 2})
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": V.CAST_CONTROL_BIOME, "fields": {
                "wildPlants": [{"plant": "Plant_Grass", "commonality": 1.0}], "baseWeatherCommonalities": wt}}]}
        if fields == "label" and want and all(w in V._pyre_shipped() for w in want):
            gone = {"pyre_def_discarded": "RM_CallingPyre_LastRite", "pyre_ritual_discarded": "RM_Ritual_CallingPyre"}
            drop = set(n for b, n in gone.items() if b in self.broken)
            rows = [{"defName": w.split("/", 1)[1], "fields": {"label": "x"}} for w in want if w.split("/", 1)[1] not in drop]
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
        if want == ["ThingDef/%s" % V.TREE]:
            return {"success": True, "foundCount": 1, "notFound": [],
                    "defs": [{"defName": V.TREE, "fields": {"label": "sweetline tree", "thingClass": "Plant", "comps": [
                        "RimMandrake.LeaningScrub.RM_CompProperties_SweetlineStation"]}}]}
        if want == ["HediffDef/RM_GaleDeafened"]:      # the shipped stages: Hearing -0.5, Talking -0.35
            caps = [{"capacity": "Hearing", "offset": -0.5}, {"capacity": "Talking", "offset": -0.35}]
            if "deafen_cuts_nothing" in self.broken:
                caps = caps[1:]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": "RM_GaleDeafened",
                                                                                  "fields": {"stages": [{"capMods": caps}]}}]}
        if want == ["GenStepDef/RM_ScrubInjections"]:
            ff = "RM_Faction_CombHolds" if "farmer_camps_back" in self.broken else None
            return {"success": True, "foundCount": 1, "notFound": [],
                    "defs": [{"defName": "RM_ScrubInjections", "fields": {"genStep": {"farmerFaction": ff}}}]}
        if fields == "description,label,hidden":
            rows = [{"defName": w.split("/", 1)[1], "fields": {"description": "A plain thing.", "hidden": "False"}}
                    for w in want]
            if "guardian_text" in self.broken:
                rows[0]["fields"]["description"] = "A guardian sleeps in its branches."
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
        if want == [V.EG_ROSTER]:
            own = list(V.VINE_CLOCK_OWN)
            soak = [n for n in own if not ("no_exempt" in self.broken and n == V.THICKET)]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{
                "defName": "RM_LeaningScrub_VenomvineExempt", "fields": {"exemptPlants": soak, "bandExemptPlants": own}}]}
        missing = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if fields == "label":       # _resolves: the removal manifest as the shipped game should hold it
            man = V._save_manifest()
            missing += [d for d in want if d in man["aliases"] and "aliases_still_ship" not in self.broken]
            missing += [d for d in want if d in man["tombstones"] and "tombstone_ships" not in self.broken]
            if "egg_deleted" in self.broken:
                missing += [d for d in want if d == man["products"][0]]
        if "missing_def" in self.broken and want and want[0] in V.SHIPPED:
            missing.append(want[3])
        return {"success": True, "notFound": missing, "foundCount": len(want) - len(missing)}

    def t_get_def(self, defName=None, **k):
        if defName == "RM_VisslerArm":
            return {"success": True, "comps": ([] if "arm_not_rotting" in self.broken
                                               else [{"class": "RimWorld.CompProperties_Rottable"}])
                    or [{"class": "RimWorld.CompProperties_Forbiddable"}]}
        comps = [{"class": "RimMandrake.EnvironmentalHazards.RM_CompProperties_BodySizeBarrier"}]
        if "thicket_unpatched" not in self.broken:
            comps.append({"class": "RimMandrake.LeaningScrub.RM_CompProperties_Smotherable"})
        return {"success": True, "comps": comps}

    def through_plants(self, p, gx, gz):
        """A straight ordered walk through RM_HollowVenomvine / thicket cells: the body-size barrier (passFreely /
        block 1.5), the path cost, and the thicket's first-contact venom (MapComponent_ContactVenom)."""
        if gx != p["x"]:
            return
        lo, hi = sorted((p["z"], gz))
        cells = [t for t in self.things.values() if t["x"] == gx and lo < t["z"] < hi and t["def"] in (V.HOLLOW, V.THICKET)]
        if not cells:
            return
        b, d = self.broken, cells[0]["def"]
        hollow = d == V.HOLLOW
        if BODY.get(p["kind"], 1.0) >= 1.5 and not (hollow and "huge_passes_hollow" in b):
            p["goto"] = None      # no path: the pawn stays put
            return
        slow = 300 if (not hollow or "hollow_threads" in b) else 60
        p["moving_until"] += slow * len(cells)
        p["via"], p["via_at"], p["via_def"] = (gx, cells[0]["z"]), self.ticks + 150, d
        if (not hollow and "thicket_no_venom" not in b) or (hollow and "hollow_venoms" in b):
            p["hediffs"].append("RM_VenomvineVenom")

    def hoard_pass(self):
        """RM_CompHoard: every grown stand sweeps items (Item, EverHaulable) in its 3x3; an item is taken once it has
        been seen hoardGrowInHours; a corpse stays and its gear is kept (hoardKeepsDeadGear)."""
        b = self.broken
        if not (self.on("hoardEnabled") or "hoard_ignores_toggle" in b):
            return
        grow = float(self.settings["hoardGrowInHours"]) * 2500
        reach = 3 if "hoard_takes_far" in b else 1
        for st in self.of(V.HOARD):
            seen, held = st.setdefault("seen", {}), st.setdefault("held", [])
            for t in list(self.things.values()):
                if max(abs(t["x"] - st["x"]), abs(t["z"] - st["z"])) > reach or t is st:
                    continue
                corpse = t["def"].startswith("Corpse_")
                if t["def"] != "Steel" and not corpse:
                    continue
                if t["def"] == "Steel" and "hoard_never_takes" in b:
                    continue
                seen.setdefault(t["id"], self.ticks)
                if self.ticks - seen[t["id"]] < grow:
                    continue
                if corpse and "hoard_takes_corpse" not in b:
                    if self.on("hoardKeepsDeadGear"):
                        held += [dict(id="G%s_%s" % (t["id"], g), **{"def": g}) for g in t.get("gear") or []]
                        t["gear"] = []
                    continue
                held.append(dict(t))
                del self.things[t["id"]]
                del seen[t["id"]]

    def t_power_net(self, thing=None, **k):
        t = self.things.get(thing)
        if t is None:
            return {"success": False, "message": "no thing %r" % thing}
        live = any(w.get("faction") == "PlayerColony" and not w.get("broken") for w in self.of("WindTurbine"))
        return {"success": True, "connected": True, "net": {
            "batteryCompsCount": len(self.of("Battery")), "currentStoredEnergy": t.get("stored", 0.0),
            "currentEnergyGainRate": 0.1 if live and "battery_never_charges" not in self.broken else 0.0}}

    def t_incident_queue_peek(self, **k):
        return {"success": True, "count": len(self.queued), "queue": [{"defName": d} for d in self.queued]}

    def t_incident_journal(self, sinceSeq=-1, limit=200, **k):
        return {"success": True, "installed": True, "rows": [{"aseq": i, "def": d} for i, d in enumerate(self.queued)]}

    def t_harmony_patches(self, typeName=None, methodName=None, **k):
        for typ, meth, kind, patch in V.RULES:
            if (typ, meth) == (typeName, methodName):
                armed = not ("rule_unarmed" in self.broken and typ == "JobGiver_Wander") and not (
                    "raid_rule_unarmed" in self.broken and meth == "ChanceFactorNow")
                row = {"owner": V.HARMONY_OWNER, "patchMethod": "RimMandrake.LeaningScrub." + patch}
                m = {"method": meth, "prefixes": [], "postfixes": []}
                if armed:
                    m[kind].append(row)
                return {"success": True, "methods": [m]}
        return {"success": True, "methods": []}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=50, **k):
        msgs = []
        if "log_error" in self.broken and contains == "LeaningScrub":
            msgs = [{"type": "Error", "text": "[RM LeaningScrub] stall-freeze: rule NOT armed"}]
        if contains:
            msgs += [m for m in self.log if contains in m["text"] and (not errorsOnly or m["type"] == "Error")]
        else:       # the whole buffer, oldest first; a broken mod's error lands inside the latest window
            msgs = list(self.log)
            if "log_error" in self.broken and msgs:
                msgs.insert(len(msgs) - 1, {"type": "Error", "text": "[RM LeaningScrub] stall-freeze: rule NOT armed"})
        return {"success": True, "totalInBuffer": 321, "messages": msgs}

    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", count=1, **k):
        self.n += 1
        pid = "P%d" % self.n
        self.pawns[pid] = dict(id=pid, kind=kindDef, x=x, z=z, faction=faction, dead=False, hediffs=[],
                               flee_until=0, born=self.ticks)
        return {"success": True, "pawns": [{"id": pid}]}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, **k):
        if self.cur_map in self.gen_maps:
            n = 2 if self.gen_census("RM_Fuzz") and self.gen_maps[self.cur_map] == "RM_LeaningScrub" else 0
            return {"success": True, "pawns": [{"id": "G%d" % i, "kindDef": "RM_Surrik", "faction": None, "dead": False}
                                               for i in range(n)]}
        rr = V_rect(rect) if rect else None
        rows = []
        for p in self.pawns.values():
            if rr and not inrect(p["x"], p["z"], rr):
                continue
            row = {"id": p["id"], "kindDef": p["kind"], "x": p["x"], "z": p["z"],
                   "faction": None if p["faction"] == "none" else p["faction"], "dead": p["dead"],
                   "downed": False, "intelligence": "Humanlike" if p["kind"] == "Colonist" else "Animal"}
            if includeHealth:
                row["health"] = {"hediffs": [{"def": h, "part": "Torso" if h == "Cut" else None}
                                             for h in p["hediffs"]]
                                 + [{"def": "MissingBodyPart", "part": "front left leg"} for _l in p.get("lost") or []]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_site_state(self, **k):
        return {"success": True, "pawns": [
            {"id": p["id"], "job": V.HOLLOW_CRAWL_JOB if p.get("in_hollow") and "no_crawl_job" not in self.broken else
             "Flee" if self.ticks < p.get("flee_until", 0) else
             ("Goto" if p.get("goto") and self.ticks < p.get("moving_until", 0) and p["kind"] == "Colonist"
              and "order_ignored" not in self.broken else
              "Goto" if p.get("hold") and p.get("goto") and self.ticks < p.get("moving_until", 0) else
              p.get("job", "Wait_Wander"))}
            for p in self.pawns.values()]}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        if self.cur_map in self.gen_maps and "," in str(defName):
            rows = [dict(r, id="I%d" % i) for i, r in enumerate(self.island_cells()) if r["def"] in defName.split(",")]
            return {"success": True, "countMatched": len(rows), "isCompleteList": True, "things": rows}
        if self.cur_map in self.gen_maps:
            return {"success": True, "countMatched": self.gen_census(defName), "things": []}
        rr = V_rect(rect) if rect else None
        rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows),
                "things": [dict(t) for t in rows[:limit]]}

    def t_static_call(self, type=None, method=None, args="", **k):
        if type == "RimMandrake.LeaningScrub.FakeMessages":
            return {"success": True, "result": str(len([m for m in self.messages if args in m]))}
        if type == "RimMandrake.LeaningScrub.FakeReveal":
            pid, what = args.split("|")
            if what == "conceal":
                self.pawns[pid]["concealed"] = True
            return {"success": True, "result": str(bool(self.pawns[pid].get("concealed")))}
        if type == "RimMandrake.LeaningScrub.FakeWetness":
            return {"success": True, "result": "%.2f" % self.wetness(*[int(v) for v in args.split(",")])}
        if type == "Verse.Log":
            self.log.append({"type": method, "text": args})
            return {"success": True}
        if type == "RimMandrake.LeaningScrub.FakeCapacity":       # GetLevel: the shipped capMods on a deafened pawn
            pid, cap = args.split("|")
            off = {"Hearing": 0.5, "Talking": 0.35}[cap]
            deaf = "RM_GaleDeafened" in self.pawns[pid]["hediffs"] and "deafen_live_untouched" not in self.broken
            return {"success": True, "result": "%.2f" % (1.0 - off if deaf else 1.0)}
        if type == "RimMandrake.LeaningScrub.FakeWind":           # WindManager.WindSpeed after the transition, raw 0.5
            f, o = FAKE_WIND.get(self.weather, (1.0, 0.0))
            if "live_stall_blows" in self.broken and self.weather == "RM_Stall":
                o = 0.4
            return {"success": True, "result": "%.3f" % (0.5 * f + o)}
        if type == "RimMandrake.LeaningScrub.FakeIslandStart":     # the start the island step used
            return {"success": True, "result": "(%d, 0, %d)" % ISLAND_START}
        if type == "RimMandrake.LeaningScrub.FakeRaidWeight":     # ChanceFactorNow after the postfix, as shipped
            d, b = args.split("|")[0], self.broken
            raid = d == "RaidEnemy" or "raid_weights_all" in b
            gale = self.weather == "RM_Gale" or "raid_weight_ignores_gale" in b
            on = self.on("galeRaidWeightingEnabled") or "raid_weight_ignores_toggle" in b
            if "raid_hook_schedules" in b:
                self.queued.append(d)
            f = float(self.settings["galeRaidWeightFactor"]) if raid and gale and on else 1.0
            return {"success": True, "result": "%.4f" % (0.5 * f)}
        if type == "RimMandrake.RimProperty.FakeEvidenceProof":     # sc_maker's shared-store fixture, as designed
            bad = "store_reads_fire_as_taking" in self.broken and args == "fire_only_same_actor"
            return {"success": True, "result": "FAIL a fire record was read as taking evidence" if bad else "PASS " + args}
        n = 0 if not args else len(args.split("|"))
        if n not in cs_arities(type, method):
            return {"success": False, "message": "No public static %s with %d params." % (method, n),
                    "details": {"available": sorted(cs_arities(type, method))}}
        if method == "Apply":       # RM_RegrowingHarvest.Apply: the setting reaches the def
            self.drip_applied = self.on("drippingRegrowEnabled")
            return {"success": True, "result": None}
        if method == "ProofStamp":
            # The suite must name the pad it cleared ("mode@x,z"): LIVE 2026-10-16 the wooded run map held no ambient
            # clear 22-cell disc, so a bare mode is the UNMEASURED the live hook returned.
            if "@" not in args:
                return {"success": True, "result": "UNMEASURED: no unroofed, empty, fire-free 22-cell disc on this map"}
            args = args.split("@")[0]
            on = (args != "off" and "stamp_never" not in self.broken) or (args == "off" and "stamp_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": ("PASS sent=1 stamped=2" if on else
                                                     "FAIL: a six-fire blaze sent no stamper toward it")}
            return {"success": True, "result": ("FAIL: fireStampEnabled off but the herd answered" if on
                                                 else "PASS off sent=0 stamped=0")}
        if method == "CountOpen":
            return {"success": True, "result": "4000"}
        if method == "ProofLean" and self.cur_map in self.gen_maps and args == "on":
            west = math.cos(math.radians(self.heading())) < -V.LEAN_TIE_X
            if "lean_wrong_side" in self.broken:
                west = not west
            return {"success": True, "result": "PASS east=%d west=%d windWest=%s" % (0 if west else 40, 40 if west else 0, west)}
        if method == "ProofLean":
            if args == "off":
                return {"success": True, "result": "FAIL faced with the toggle off east=0 west=40" if "lean_ignores_toggle" in self.broken
                        else "PASS east=0 west=0 rolled=12"}
            return {"success": True, "result": "FAIL mixed lean east=3 west=37" if "lean_mixed" in self.broken
                    else "PASS east=0 west=40 rolled=12 windWest=True"}
        if method == "ProofGale":
            if self.weather == "RM_Gale" or "gale_keeps_ticking" in self.broken:
                self.gale_last = self.ticks
            art = "PLACEHOLDER (vanilla fog sheet)" if "gale_art_placeholder" in self.broken else \
                V._gale_art_expect(V._gale_files())
            drew = self.on("galeDustOverlayEnabled") or "gale_draws_when_off" in self.broken
            tail = " weather=%s art=%s dir=%s tickAge=%d drew=%s leanMap=True" % (
                self.weather, art, "(0.00, 1.00)" if "gale_across_wind" in self.broken else "(1.00, 0.00)",
                self.ticks - self.gale_last if self.gale_last is not None else -1, drew)
            if self.weather != "RM_Gale":
                return {"success": True, "result": "UNMEASURED the Gale is not the current weather" + tail}
            return {"success": True, "result": "FAIL RM_Gale does not carry RM_WeatherOverlay_GaleDust" if "gale_no_overlay" in self.broken
                    else "PASS" + tail}
        if method == "ProofHeading":
            return {"success": True, "result": "FAIL: the wind does not point at the sun heading=10.000 want=237.500"
                    if "wind_off_sun" in self.broken else "PASS sunBearing=212.500 heading=237.500 want=237.500"}
        if method == "ProofScent":
            if "@" not in args:     # the suite must name the pad it cleared (no person within 40 cells)
                return {"success": True, "result": "UNMEASURED: args must be on@x,z or off@x,z, got " + args}
            mode = args.split("@")[0]
            flees = (mode != "off" and "scent_never" not in self.broken) or (mode == "off" and "scent_ignores_toggle" in self.broken)
            if mode != "off":
                return {"success": True, "result": "PASS upwind=Flee downwind=none beyond=none" if flees else
                        "FAIL: no flee from a person 8 cells upwind upwind=none"}
            return {"success": True, "result": "FAIL: leanScentEnabled off but the animal fled an upwind person"
                    if flees else "PASS off upwind=none"}
        if method == "ProofFire":
            if "@" not in args:
                return {"success": True, "result": "UNMEASURED: args must be on@x,z or off@x,z, got " + args}
            return {"success": True, "result": "FAIL: fire does not favour downwind cells on 70/190 off 71/188 z=0.1"
                    if "fire_unbiased" in self.broken else "PASS on 131/190 downwind off 70/188 z=6.4"}
        if method == "ProofRipple":
            hides = (args != "off" and "ripple_never" not in self.broken) or (args == "off" and "ripple_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": "PASS wind=True stallStill=True" if hides else
                        "FAIL: small wild creature on fuzz in wind was not hidden"}
            return {"success": True, "result": "FAIL: rippleEnabled off but the creature hid" if hides else "PASS off wind=False"}
        if method == "ProofStallHunt":
            hunts = (args != "off" and "stallhunt_never" not in self.broken) or (args == "off" and "stallhunt_ignores_toggle" in self.broken)
            if args != "off":
                return {"success": True, "result": "PASS hunting=True" if hunts else "FAIL: a stall hunter did not hunt"}
            return {"success": True, "result": "FAIL: stallHuntEnabled off but the hawk hunted" if hunts else "PASS off hunting=False"}
        if method == "ProofManhunter":
            return {"success": True, "result": "FAIL: the manhunter was ordered to flee calmJob=Flee rageState=Manhunter rageJob=Flee"
                    if "bloom_scares_manhunter" in self.broken else
                    "PASS calmJob=Flee rageState=Manhunter rageJob=none"}
        if method == "ProofRefusesPawnCell":
            return {"success": True, "result": "FAIL: the refused cell lost its steel or grass planted=False steelKept=False"
                    if "genstep_tidies" in self.broken else "PASS planted=False steelKept=True grassKept=True"}
        if method == "ProofArmScavengers":
            on = args.startswith("on") or "arm_ignores_toggle" in self.broken
            drawn = on and "arm_draws_none" not in self.broken
            if args.startswith("on"):
                return {"success": True, "result": "PASS drawn=[RM_Surrik,RM_Ribbonwhip] notDrawn=[]" if drawn else
                        "FAIL: a hungry meat eater beside the arm chose something else drawn=[] notDrawn=[RM_Surrik]"}
            return {"success": True, "result": "FAIL: visslerArmFoodEnabled off but the arm drew drawn=[RM_Surrik]" if drawn
                    else "PASS off drawn=[] notDrawn=[RM_Surrik,RM_Ribbonwhip]"}
        if method == "ProofPyre" and args.startswith("thin@"):
            return {"success": True, "result": "FAIL: five fires as five islands read as a catch islandsThin=False clusterThin=False"
                    if "pyre_counts_fires" in self.broken else "PASS fires=5 gap=8 islandsThin=True clusterThin=False"}
        if method == "ProofPyre":
            if args == "defs":
                return {"success": True, "result": "FAIL: RM_CallingPyre_Venerated not gated on Ritualist"
                        if "pyre_ungated" in self.broken else "PASS defs"}
            if args == "off":
                return {"success": True, "result": "FAIL: callingPyreEnabled off but the gate said ok"
                        if "pyre_ignores_toggle" in self.broken else "PASS off: gate refuses"}
            if "@" not in args:     # the suite must name its crop patch: the scrub's own flora is fireproof (ban 9)
                return {"success": True, "result": "FAIL: the pyre lit fewer fires than the stamp threshold lit=0"}
            return {"success": True, "result": "FAIL: the pyre lit fewer fires than the stamp threshold lit=2"
                    if "pyre_no_fire" in self.broken else "PASS lit=6 came=3 raging=1"}
        if method == "ProofVaporator":
            return {"success": True, "result": "FAIL: no techprint for RM_WindVaporators"
                    if "vaporator_unlearnable" in self.broken else "PASS vaporator"}
        if method == "ProofInjections":
            wrecks = 0 if "no_farmstead" in self.broken else 3
            people = 0 if "no_camp_people" in self.broken else 4
            return {"success": True, "result": "PLACED sites=4 vaporatorWrecks=+%d campPeople=+%d farmers=True scavengers=False" % (wrecks, people)}
        if method == "ProofComfortDelta":
            on = self.on("sweetlineFeltComfortEnabled") or "comfort_ignores_toggle" in self.broken
            d = 0.10 if on and "no_comfort" not in self.broken else 0.0
            return {"success": True, "result": "DELTA %.2f" % d}
        if method in ("ProofDen", "ProofStand", "ProofOrderRoll", "ProofBite"):
            return self.dens_proof(type, method, args)
        if method == "ProofVisuals":
            on = self.on("runwayBloomEnabled")
            sway, under, holes, answered = (1, 1, 1, 2) if on else (0, 0, 0, 0)
            if "no_exit_hole" in self.broken:
                holes = 0
            return {"success": True, "result": "SWAYING %d UNDER %d HOLES +%d ANSWERED %d" % (sway, under, holes, answered)}
        if method == "ProofMapStep":
            chance = float(args.split("|")[1])
            n = 0
            if (chance > 0 or "map_step_ignores_chance" in self.broken) and "no_map_step" not in self.broken:
                n = 1
                self.new(V.TREE, 5, 5, growth=1.0, stackCount=1)
            return {"success": True, "result": "PLANTED %d" % n}
        if method == "ProofIslands":
            return {"success": True, "result": "FAIL: laid under half the target share islands=0" if "no_islands" in self.broken
                    else "PASS islands=40 planned=42 planted=8100 target=8250 rooms=70"}
        if method == "ProofCreep":
            if args == "on":
                return {"success": True, "result": "FAIL: a grown stand put no runner" if "no_creep" in self.broken
                        else "PASS mode=on laid=1 besideTestStand=1 runnerGrowth=0.05"}
            ran = (args == "off" and "creep_ignores_toggle" in self.broken) or (args == "cap" and "creep_ignores_cap" in self.broken)
            return {"success": True, "result": "FAIL: creep ran with %s" % args if ran else "PASS mode=%s laid=0" % args}
        if method == "ProofExempt":
            return {"success": True, "result": "FAIL: the venomvine exemption roster did not load" if "no_exempt" in self.broken
                    else "PASS roster RM_LeaningScrub_VenomvineExempt loaded"}
        if method == "ProofForm" and type and type.endswith("RM_FourFormsProof"):
            form, mode = args.split("|")
            on = self.on(dict(V.FOUR)[form])
            if mode == "on":
                acts = on and ("four_%s_never" % form) not in self.broken
                return {"success": True, "result": "PASS %s" % form if acts else "FAIL: %s did nothing" % form}
            acts = ("four_%s_ignores_toggle" % form) in self.broken
            return {"success": True, "result": "FAIL: %s off but it acted" % form if acts else "PASS off %s" % form}
        if method == "ProofForm":
            form, mode = args.split("|")
            on = self.on(V.FORM_TOGGLES[form])
            if mode == "on":
                acts = on and ("%s_never" % form) not in self.broken
                return {"success": True, "result": "PASS %s" % form if acts else "FAIL: %s did nothing" % form}
            acts = ("%s_ignores_toggle" % form) in self.broken      # the hook flips the setting off itself
            return {"success": True, "result": "FAIL: %s off but it acted" % form if acts else "PASS off %s" % form}
        if method != "ProofOrderScratch":
            return {"success": False, "message": "No public static " + str(method)}
        on = self.on("sweetlineStationsEnabled") and self.on("sweetlineScratchingEnabled")
        if not on and "scratch_ignores_toggle" not in self.broken:
            return {"success": True, "result": "REFUSED: scratching is off"}
        self.scratch = {"due": self.ticks + 700}
        return {"success": True, "result": "ORDERED P1 -> T1"}

    # ------------------------------------------------------------ den proofs (RM_ScrubDens.cs)
    def _pawn_at(self, kind, cell):
        """RM_CompVineDen.FindAt: the first pawn standing ON `cell` that carries the comp (kind stands in for the comp)."""
        x, z = [int(v) for v in cell.split(",")]
        for p in self.pawns.values():
            if p["kind"] == kind and (p["x"], p["z"]) == (x, z) and not p["dead"]:
                return p
        return None

    def t_damage(self, damageDef=None, amount=0, thingId=None, **k):
        p = self.pawns.get(thingId)
        if p is not None and amount >= 100 and not p["dead"]:
            p["dead"] = True
            self.new("Corpse_" + ("Human" if p["kind"] == "Colonist" else p["kind"]), p["x"], p["z"],
                     faction=p["faction"], gear=["Apparel_Pants", "Apparel_CollarShirt"] if p["kind"] == "Colonist" else [])
        return {"success": True}

    def dens_proof(self, type, method, args):
        """Replies in the exact shapes RM_ScrubDens.cs returns (ProofDen/ProofStand/ProofOrderRoll/ProofBite): the
        pawn is found only ON the named cell, so a spawn on the wrong cell reads 'REFUSED: no ... pawn at'."""
        b = self.broken
        parts = args.split("|")
        cell = parts[1]
        want = "RM_Rollbug" if method in ("ProofOrderRoll", "ProofBite") else "RM_Thornhold"
        p = self._pawn_at(want, cell)
        if "dens_empty" in b:
            return {"success": True, "result": ""}
        if "dens_blind" in b or p is None:
            if method == "ProofStand":     # RM_ScrubDens.cs ProofStand refuses a missing den pawn in its own words
                return {"success": True, "result": "REFUSED: need a vine-den pawn at %s and a pawn at %s"
                        % (_cs_cell(cell), _cs_cell(parts[2]))}
            what = "larder" if want == "RM_Rollbug" else "vine-den"
            return {"success": True, "result": "REFUSED: no %s pawn at %s" % (what, _cs_cell(cell))}
        x, z = p["x"], p["z"]
        if method == "ProofDen":
            if "den_never" in b or not self.on("thornholdDenEnabled") and "den_ignores_toggle" not in b:
                return {"success": True, "result": "REFUSED: " + ("no reachable den plant within 30 cells" if "den_never" in b
                                                                  else "thornhold dens are off")}
            dx, dz = (x - 2, z + 5) if "den_wrong_cell" in b else (x - 2, z)
            return {"success": True, "result": "DEN %s den=(%d, 0, %d) home=(%d, 0, %d)" % (p["id"], dx, dz, dx, dz)}
        if method == "ProofStand":
            tx, tz = [int(v) for v in parts[2].split(",")]
            att = [q for q in self.pawns.values() if (q["x"], q["z"]) == (tx, tz) and not q["dead"]]
            if not att:
                return {"success": True, "result": "REFUSED: need a vine-den pawn at %s and a pawn at %s"
                        % (_cs_cell(cell), _cs_cell(parts[2]))}
            off = not self.on("thornholdStandEnabled") and "stand_ignores_toggle" not in b
            if off or "stand_never" in b:
                return {"success": True, "result": "REFUSED: thornhold stand is off" if off else "REFUSED: TryStartMentalState refused"}
            who = "T0" if "stand_wrong_target" in b else att[0]["id"]
            return {"success": True, "result": "STAND %s state=RM_ThornholdStand target=%s" % (p["id"], who)}
        if method == "ProofOrderRoll":
            corpses = [c for c in self.things.values() if c["def"].startswith("Corpse_")]
            colony = [c for c in corpses if c.get("faction") == "player"]
            pool = corpses if self.on("rollbugTakesColonyCorpses") or "roll_ignores_toggle" in b else \
                [c for c in corpses if c.get("faction") != "player"]
            if "roll_never" in b or not self.on("rollbugCarrionEnabled") or not pool:
                return {"success": True, "result": "REFUSED: " + ("rollbug carrion is off" if "roll_never" not in b
                                                                  and not self.on("rollbugCarrionEnabled") else
                                                                  "no rollable corpse within 14 cells")}
            c = pool[0]
            lx, lz = x - 3, z
            if "roll_far" in b:
                lx, lz = x + 9, z      # the corpse is left where it lay: > 3 from the larder
            else:
                c["x"], c["z"] = lx + 1, lz
            if "roll_copies" in b:
                self.new(c["def"], c["x"], c["z"], faction=c.get("faction"))
            if "roll_loses" in b:
                del self.things[c["id"]]
            p["x"], p["z"] = lx, lz
            return {"success": True, "result": "ORDERED %s -> %s larder=(%d, 0, %d)" % (p["id"], c["id"], lx, lz)}
        if "bite_never" in b:
            return {"success": True, "result": "REFUSED: no ball in its larder"}
        return {"success": True, "result": "ATE BIT left hind leg (0.05 nutrition)"}

    def t_spawn_batch(self, ops="", stuff=None, **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            self.new(d, n[0], n[1], stackCount=n[2] if len(n) > 2 else 1, born=self.ticks, stuff=stuff)
        return {"success": True}

    def t_set_thing_props(self, thing=None, faction=None, **k):
        t = self.things.get(thing)
        if t is None:
            return {"success": False, "message": "no thing %r" % thing}
        if faction is not None:
            t["faction"] = None if faction.lower() in ("null", "none") else faction
        return {"success": True, "changed": ["faction"] if faction is not None else [], "skipped": []}

    def t_set_pollution(self, rect="", polluted=True, **k):
        x, z, w, h = [int(v) for v in rect.split(",")]
        cells = set((cx, cz) for cx in range(x, x + w) for cz in range(z, z + h))
        if "no_pollute" in self.broken:
            return {"success": True, "cellsRequested": len(cells), "cellsEverPollutable": len(cells), "cellsChanged": 0}
        self.polluted = (self.polluted | cells) if polluted else (self.polluted - cells)
        return {"success": True, "cellsRequested": len(cells), "cellsEverPollutable": len(cells),
                "cellsChanged": len(cells)}

    def t_set_plants(self, ops="", growth=1.0, **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            if d == "CLEAR":
                continue
            if "set_plants_drops" in self.broken and d == "RM_Cruststar":
                continue
            for cx in range(n[0], n[0] + (n[2] if len(n) > 2 else 1)):
                for cz in range(n[1], n[1] + (n[3] if len(n) > 3 else 1)):
                    # PlantUtility.CanEverPlantAt: a PollutedOnly plant is rejected on a clean cell (LIVE 2026-10-07)
                    if d in V.POLLUTED_ONLY and (cx, cz) not in self.polluted:
                        continue
                    tid = self.new(d, cx, cz, growth=growth, stackCount=1)
                    if d == V.TREE:
                        self.things[tid]["wool"] = self.ticks + 3 * 60000     # staggered first shed
        return {"success": True}

    def t_pawn_force_incapacitate(self, pawn=None, action=None, **k):
        if action == "vanish" and pawn in self.pawns:
            del self.pawns[pawn]
            return {"success": True, "destroyedAfter": True}
        return {"success": pawn in self.pawns}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = V_rect(rects)
        if "Pawn" in str(categories):    # live: refused; and no category ever removes a pawn
            return {"success": False, "message": "destroy_batch never removes pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1)"}
        self.rooms = [r for r in self.rooms if not (inrect(r[0], r[1], rr) and inrect(r[0] + r[2] - 1, r[1] + r[3] - 1, rr))]
        fallen = [t for t in self.things.values() if t["def"] == V.HOARD and inrect(t["x"], t["z"], rr)]
        for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
            del self.things[tid]
        for st in fallen:       # RM_CompHoard.PostDeSpawn: the held goods drop where the stand stood
            for _ in range(2 if "hoard_drops_twice" in self.broken else 1):
                for h in st.get("held") or []:
                    self.new(h["def"], st["x"], st["z"], stackCount=h.get("stackCount", 1))
        self.claims = dict((s, t) for s, t in self.claims.items() if s in self.things)
        return {"success": True}

    def t_make_empty_room(self, rect=None, **k):
        self.rooms.append(V_rect(rect))
        return {"success": True}

    def t_set_roof_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            if d in ("None", "Clear"):
                ROOF_STRIPS.append(tuple(int(v) for v in nums.split(",")))
                self.roofed -= self.cells(nums)
            if d == "RoofConstructed":
                self.roofed |= self.cells(nums)
            if d == "RoofConstructed":
                rr = tuple(int(v) for v in nums.split(","))
                for f in self.of("Campfire"):
                    if inrect(f["x"], f["z"], rr):
                        f["enclosed_at"] = self.ticks
        return {"success": True}

    def t_get_roof_batch(self, rects=None, **k):
        r = V_rect(rects) if rects and ";" not in rects else None
        if r and r[2] == 1 and r[3] == 1:      # one cell: the live answer shape, roofed only inside a made room
            inside = any(inrect(r[0], r[1], q) for q in self.rooms)
            return {"success": True, "cellsRead": 1, "roofs": ["RoofConstructed" if inside else "None"]}
        return {"success": True, "roofedCells": 49}

    def t_pawn_health(self, pawn=None, action=None, hediff=None, **k):
        p = self.pawns[pawn]
        if action == "remove" and hediff in p["hediffs"]:
            p["hediffs"].remove(hediff)
        return {"success": True}

    def t_pawn_flight(self, pawn=None, **k):
        return {"success": True, "pawns": [{"id": pawn, "canEverFly": "no_fly" not in self.broken,
                                            "maxFlightTimeStat": 6.0,
                                            "flying": bool((self.pawns.get(pawn) or {}).get("flying"))}]}

    # ------------------------------------------------------------ the acceptance scenes (scene_* chains)
    def t_pawn_need(self, pawn=None, action="list", need=None, level=0.5, **k):
        p = self.pawns.get(pawn)
        if p is None:
            return {"success": False, "message": "no pawn %s" % pawn}
        if action == "need" and need == "Food":
            p["food"] = float(level)
        f = p.get("food", 0.9)
        return {"success": True, "needs": [{"need": "Food", "level": f, "pct": f}]}

    def t_comp_read(self, thing=None, comp=None, members=None, **k):
        t = self.things.get(thing)
        if comp == "Rottable" and t:
            return {"success": True, "values": {"RotProgress": str(
                0 if "arm_never_rots" in self.broken else self.ticks - t.get("born", 0))}}
        if comp == "RM_CompHoard" and t and t["def"] == V.HOARD:
            held = t.get("held") or []
            return {"success": True, "missing": [], "values": {
                "held": "Count=%d [%s]" % (len(held), ", ".join(h["id"] for h in held)),
                "firstSeen": "Count=%d [%s]" % (len(t.get("seen") or {}), ", ".join(
                    "%s:%d" % kv for kv in sorted((t.get("seen") or {}).items()))), "HeldCount": str(len(held))}}
        if comp == "RM_CompRearing" and t and t["def"] == V.REARING:
            u = t.get("until", 0)
            return {"success": True, "missing": [], "values": {"rearedUntilTick": str(u), "Reared": str(self.ticks < u)}}
        if comp == "RM_CompQuench" and t and t["def"] == V.QUENCH:
            r = t.get("ready", 0)
            return {"success": True, "missing": [], "values": {"readyTick": str(r), "Ready": str(self.ticks >= r)}}
        if comp == "SandSwim" and thing in self.pawns:
            return {"success": True, "values": {"Submerged": "True"}}
        return {"success": False, "message": "no comp %s on %s" % (comp, thing)}

    def t_map_comp_read(self, comp=None, members=None, **k):
        if comp == "RM_MapComponent_VenomvineCreep":
            return {"success": True, "values": {"Applies": "True", "openCells": str(self.OPEN_CELLS),
                                                "vineCells": str(len(self.of(V.THICKET)))}}
        if comp == "RM_MapComponent_Lean":
            if self.cur_map in self.gen_maps:
                return {"success": True, "values": {"HeadingDegrees": "%.4f" % self.heading(), "SunBearingDegrees":
                                                    "%.4f" % ((90.0 - self.heading()) % 360.0)}}
            return {"success": True, "values": {"Downwind": "(1.00, 0.00)", "HeadingDegrees": "0.0000"}}
        n = len([p for p in self.pawns.values() if self.ticks < p.get("sway_until", 0)])
        return {"success": True, "values": {"swaying": "Count=%d" % n}}

    def save_bytes(self, name):
        self.save_count += 1
        return 1000 + 10 * len(self.things) + (100 * self.save_count if "save_grows" in self.broken else 0)

    # ------------------------------------------------------------ scenes batch 2 (native cast .. persistence)
    def ripple_pass(self):
        """RM_MapComponent_Ripple.ShouldHide over every pawn (RM_RippleKernel.Hidden)."""
        b = self.broken
        if self.settings.get("modEnabled") != "True" and self.settings.get("rippleEnabled") != "True":
            self.master_was_off = True     # every switch off together (sc_settings' all-off arm)
        on = self.on("rippleEnabled") or "ripple_ignores_toggles" in b
        if "ripple_dead_after_master_off" in b and self.master_was_off:
            on = False
        fuzz = set((t["x"], t["z"]) for t in self.of("RM_Fuzz"))
        limit = float(self.settings.get("rippleMaxBodySize", 0.6)) * (2 if self.weather == "RM_Gale"
                                                                       and "ripple_gale_no_extend" not in b else 1)
        for p in self.pawns.values():
            if p.get("via") and p.get("goto") and self.ticks >= p["via_at"]:
                p["x"], p["z"] = p["via"]
                p["in_hollow"] = p.get("via_def") == V.HOLLOW
            if p.get("goto") and self.ticks >= p["moving_until"]:
                p["x"], p["z"] = p["goto"]
                p["goto"], p["via"], p["in_hollow"] = None, None, False
            wild = p["faction"] == "none" and p["kind"] != "Colonist" and p["kind"] != "RM_Surrik" and (
                not p.get("mental") or "ripple_hides_mental" in b)
            cover = (p["x"], p["z"]) in fuzz or "ripple_bare_hides" in b
            moving = self.ticks < p.get("moving_until", 0) and "ripple_stall_move_hidden" not in b
            still = self.weather == "RM_Stall" or (cover and self.lee(p))
            hide = (on and wild and not p["dead"] and cover and BODY.get(p["kind"], 1.0) <= limit
                    and not (still and moving) and not ("ribbon_unhidden" in b and self.in_ribbon_scene()))
            hs = p["hediffs"]
            if hide and "RM_RippleHidden" not in hs:
                hs.append("RM_RippleHidden")
            elif not hide and "RM_RippleHidden" in hs:
                hs.remove("RM_RippleHidden")

    def t_map_info(self, **k):
        lat, lon = self.geo()
        return {"success": True, "mapId": self.cur_map, "latitude": lat, "longitude": lon}

    # ------------------------------------------------------------ batch 7: wind plain, lee, islands, ordered, lure
    def geo(self):
        tile = (getattr(self, "gen_tiles", {}).get(self.cur_map) or (None,))[0]
        return TILE_GEO.get(tile, HOME_GEO)

    def heading(self):
        """RM_MapComponent_Lean.HeadingDegrees as designed: 90 - the tile's sun bearing."""
        lat, lon = self.geo()
        if "heading_constant" in self.broken:
            return 90.0
        if "heading_reversed" in self.broken:
            return V._geo_heading(lon, lat, *V.SUBSTELLAR)
        return V._geo_heading(lat, lon, *V.SUBSTELLAR)

    def island_cells(self):
        """A fresh Scrub map's counted venomvine: six 10x10 islands away from the start, two holding a 2-cell hollow
        room (open ground 4000: share 0.15); none when the step was off."""
        tile, on = getattr(self, "gen_tiles", {}).get(self.cur_map, (None, False))
        b, out = self.broken, []
        if not on:
            return out
        centres = [(40, 40), (40, 200), (200, 40), (200, 200), (125, 30), (125, 220)]
        if "islands_share_low" in b:
            centres = centres[:2]
        if "islands_crowd_start" in b:
            centres[0] = ISLAND_START
        for k, (cx, cz) in enumerate(centres):
            for i in range(10):
                for j in range(10):
                    d = V.THICKET
                    if k < 2 and j == 0 and i < 2 or "islands_room_everywhere" in b:
                        d = V.HOLLOW
                    if "sworn_island" in b and k == 3 and (i, j) == (5, 5):
                        d = V.SWORN
                    out.append({"x": cx - 5 + i, "z": cz - 5 + j, "def": d})
        return out

    def lure_pass(self, d):
        """RM_CompLure as shipped: on each CompTickLong (2000 ticks) a grown stand drops one fruit beside it while fewer
        than the cap lie within reach; a hungry herbivore that can reach a fruit walks to it, then eats it."""
        b = self.broken
        if self.ticks // 2000 != (self.ticks - d) // 2000:
            cap = V.LURE_CAP + (3 if "lure_over_cap" in b else 0)
            for st in self.of(V.LURE):
                on = self.on("lureEnabled") or "lure_ignores_toggle" in b
                grown = st.get("growth", 1.0) >= V.LURE_MIN_GROWTH or "lure_young_drops" in b
                near = sum(f.get("stackCount", 1) for f in self.of(V.LURE_FRUIT)
                           if (f["x"] - st["x"]) ** 2 + (f["z"] - st["z"]) ** 2 <= V.LURE_REACH ** 2)
                if on and grown and near < cap:
                    self.new(V.LURE_FRUIT, st["x"], st["z"] + 1, stackCount=1)
        for p in self.pawns.values():
            if p["kind"] != V.LURE_EATER or p["faction"] != "none" or "lure_never_eaten" in b:
                continue
            if p.get("food", 0.9) >= 0.3 and "lure_fed_eats" not in b:
                continue
            meal = [f for f in self.of(V.LURE_FRUIT) if "lure_through_walls" in b or not any(
                inrect(f["x"], f["z"], r) != inrect(p["x"], p["z"], r) for r in self.rooms)]
            if meal and p.get("job") == "Ingest":
                m = meal[0]
                m["stackCount"] = m.get("stackCount", 1) - 1
                if m["stackCount"] <= 0:
                    del self.things[m["id"]]
                p["food"], p["job"] = 0.8, "Wait_Wander"
            elif meal:
                p["job"] = "Ingest"

    def lee(self, p):
        """RM_MapComponent_Ripple.InWindbreakLee as shipped, for the fake's east wind: a Wall within WakeLength cells west."""
        b = self.broken
        if not (self.on("leanWakesEnabled") or "lee_ignores_toggle" in b) or "lee_never_reveals" in b:
            return False
        walls = set((t["x"], t["z"]) for t in self.of("Wall"))
        wake = V.LEE_WAKE + (12 if "lee_too_long" in b else 0)
        ks = range(1, wake + 1)
        return any((p["x"] - k, p["z"]) in walls for k in ks) or (
            "lee_reversed" in b and any((p["x"] + k, p["z"]) in walls for k in ks))

    def t_world_tile_map_generate(self, tile=None, biome=None, **k):
        mid = 10 + len(self.gen_maps) + len(self.saves)
        self.gen_maps[mid] = biome
        self.gen_tiles = getattr(self, "gen_tiles", {})
        self.gen_tiles[mid] = (tile, self.on("venomvineIslandsEnabled") or "islands_ignore_toggle" in self.broken)
        return {"success": True, "mapId": mid, "wasAlreadyGenerated": False}

    def t_set_current_map(self, mapId=None, **k):
        self.cur_map = mapId
        return {"success": True}

    def t_map_drop(self, mapIndex=None, **k):
        self.gen_maps.pop(mapIndex, None)
        return {"success": True}

    def gen_census(self, defName):
        """countMatched of a rostered plant on a generated map: the Scrub grows its roster, the vanilla control none."""
        scrub = self.gen_maps.get(self.cur_map) == "RM_LeaningScrub"
        grows = scrub != ("cast_never_generates" in self.broken) if scrub else "cast_leaks_to_control" in self.broken
        return 30 if grows and defName.startswith("RM_") else 0

    def t_pawn_mental(self, pawn=None, action=None, state=None, **k):
        self.pawns[pawn]["mental"] = action == "start"
        return {"success": True}

    def t_thing_refuel(self, thingId=None, amount=0, **k):
        t = self.things.get(thingId)
        if t is None or t["def"] != "Campfire":
            return {"success": False, "message": "no CompRefuelable on %s" % thingId}
        bias = 1.2 if "fuel_meter_biased" in self.broken and t["x"] > 110 else 1.0
        return {"success": True, "fuelAfter": self.fuel(thingId) * bias, "capacity": 20}

    def t_cell_temperature(self, cell=None, **k):
        x, z = [int(v) for v in cell.split(",")]
        for f in self.of("Campfire"):
            if abs(f["x"] - x) <= 4 and abs(f["z"] - z) <= 4 and f.get("enclosed_at") is not None:
                rate = 6.0 if f.get("burning") == "RM_DeadVenomvine" and "cane_no_heat_bonus" not in self.broken else 4.0
                return {"success": True, "temperature": 20 + rate * (self.ticks - f["enclosed_at"]) / 1000.0}
        return {"success": True, "temperature": 20.0}

    def t_running_mods(self, **k):
        ids = [p for p in V.DLC_PACKAGES if not ("dlc_missing" in self.broken and p.endswith("odyssey"))]
        ids += ["brrainz.harmony", V.OUR_PACKAGES[1], V.SCANNER_PKG, V.HATCH_PKG]
        return {"success": True, "count": len(ids), "packageIds": ids}

    def t_list_selected_gizmos(self, **k):
        return {"success": True, "gizmos": [{"label": V.PULSE_LABEL + " (ready)", "gizmoId": "g1"}]}

    def t_execute_gizmo(self, gizmoId=None, **k):
        quiet, targets = V._payload()
        snd = self.of(V.SOUNDER)[0]
        near = lambda o: abs(o["x"] - snd["x"]) + abs(o["z"] - snd["z"]) <= 14
        lines = []
        for tg in targets:
            hit = any(near(p) for p in self.pawns.values() if p["kind"] in tg["pawnRaces"] and not p["dead"]) or any(
                near(t) for t in self.things.values() if t["def"] in tg["thingDefs"])
            if (hit and "pulse_reads_quiet" not in self.broken) or (
                    "pulse_reads_without_target" in self.broken and tg["label"] == "sweetline tree"):
                lines.append(tg["reading"])
        self.letters.append({"label": "Sounding reading", "text": "The pulse rolled out:\n" + ("\n".join(lines) or quiet)})
        return {"success": True}

    def t_list_letters(self, **k):
        return {"success": True, "letters": list(self.letters)}

    def t_map_comp_timing(self, ticks=300, **k):
        self.advance(int(ticks))
        calls = 0 if "timing_no_work" in self.broken else int(ticks) // 60 * (1 + len(self.pawns) // 10)
        return {"success": True, "ticksElapsed": int(ticks), "coverage": "ok", "components": [
            {"type": "RimMandrake.LeaningScrub.RM_MapComponent_Ripple", "packageId": V.OUR_PACKAGES[1], "calls": calls,
             "msPerTick": 0.01}]}

    # ------------------------------------------------------------ scenes batch 3 (crown .. recovery)
    OPEN_CELLS = 10000

    @staticmethod
    def cells(nums):
        n = [int(v) for v in nums.split(",")]
        w, h = (n[2], n[3]) if len(n) > 3 else (1, 1)
        return set((x, z) for x in range(n[0], n[0] + w) for z in range(n[1], n[1] + h))

    def crown_pass(self):
        """RM_MapComponent_CrownMob: residents and flutters already on their way count toward maxMobbers; only idle
        flutters are sent (a plain Goto arriving 500 ticks later), never one busy on another job."""
        b = self.broken
        stands = self.of("RM_CrownVenomvine")
        fl = sorted((p for p in self.pawns.values() if p["kind"] == "RM_Dustflutter" and not p["dead"]
                     and p["faction"] == "none"), key=lambda p: int(p["id"][1:]))
        for p in fl:
            if p.get("mob") == "transit" and self.ticks >= p["mob_at"] and stands:
                p["x"], p["z"], p["mob"], p["job"] = stands[0]["x"] + 2, stands[0]["z"], "held", "Wait_Wander"
            if p.get("job") == "Goto" and not p.get("goto") and not p.get("mob"):
                p["job"] = "Wait_Wander"      # an ordered walk ended
        on = (self.weather == "RM_Stall" and self.on("crownMobEnabled") and "no_crown" not in b) or "crown_ignores_toggle" in b
        if not on or not stands:
            return
        if "crown_hijacks_busy" in b:
            fl.sort(key=lambda p: not p.get("goto"))      # a hijacking mob reaches the busy flutter first
        blind = "crown_over_cap" in b or self.crown_forgets
        held = len([p for p in fl if p.get("mob") == "held" or (p.get("mob") == "transit" and not blind)])
        for p in fl:
            if held >= V.CROWN_CAP:
                break
            if p.get("mob") or (p.get("goto") and "crown_hijacks_busy" not in b):
                continue
            p["goto"], p["mob"], p["mob_at"], p["job"] = None, "transit", self.ticks + 500, "Goto"
            held += 1

    def graze_pass(self, d):
        """The designed cruststar ecology (not built in C# yet): a hungry crustweevil that can reach the patch grazes one
        cruststar (growth -0.8, food +0.6); a grazed cruststar regrows 0.01 per 250 ticks."""
        b = self.broken
        for c in self.of(V.CRUST):
            if c.get("growth", 1) < 1 and "cruststar_never_recovers" not in b:
                c["growth"] = min(1.0, c["growth"] + 0.01 * d / 250.0)
        for p in self.pawns.values():
            if p["kind"] != V.WEEVIL or p["dead"] or p.get("food", 0.9) >= 0.3:
                continue
            if any(inrect(p["x"], p["z"], r) for r in self.rooms) and "cruststar_through_walls" not in b:
                continue
            meal = [t for t in self.of(V.CRUST_ALT if "cruststar_never_grazed" in b else V.CRUST) if t.get("growth", 1) >= 0.5]
            if meal:
                meal[0]["growth"] -= 0.8
                if "cruststar_no_nutrition" not in b:
                    p["food"] = p.get("food", 0.9) + 0.6

    def creep_free(self, c, taken):
        if c in taken:
            return False
        if "creep_overruns_protection" in self.broken:
            return True
        return c not in self.roofed and c not in self.floors and c not in self.zones and not any(
            (t["x"], t["z"]) == c for t in self.things.values() if t["def"] in ("Wall", "Plant_TreeOak"))

    def creep_tick(self, t0, t1):
        """RM_MapComponent_VenomvineCreep: its sweep runs when (TicksGame + uniqueID*1777) % 15000 == 0. A runner is laid
        only at a compressed interval (venomvineCreepDays < 1, chance ~1), downwind (+x) first, young (growth 0.05)."""
        off = self.cur_map * 1777
        if (t0 + off) // V.CREEP_SWEEP == (t1 + off) // V.CREEP_SWEEP:
            return
        b = self.broken
        if not (self.on("venomvineCreepEnabled") or "creep_ignores_toggle" in b) or "no_creep" in b:
            return
        if float(self.settings.get("venomvineCreepDays", 10)) >= 1:
            return
        vine = self.of(V.THICKET)
        room = 99 if "creep_ignores_cap" in b else int(float(self.settings["venomvineCreepCap"]) * self.OPEN_CELLS) - len(vine)
        taken = set((t["x"], t["z"]) for t in vine)
        for e in [t for t in vine if t.get("growth", 0) >= 1.0]:
            if room <= 0:
                break
            free = [k for k in range(8) if self.creep_free((e["x"] + V.CREEP_DX[k], e["z"] + V.CREEP_DZ[k]), taken)]
            if not free:
                continue
            order = sorted(free, key=lambda k: V.CREEP_DX[k]) if "creep_no_downwind" in b else \
                [k for k in free if V.CREEP_DX[k] > 0] + [k for k in free if V.CREEP_DX[k] <= 0]
            c = (e["x"] + V.CREEP_DX[order[0]], e["z"] + V.CREEP_DZ[order[0]])
            self.new(V.THICKET, c[0], c[1], growth=0.6 if "creep_runner_armed" in b else 0.05, stackCount=1)
            taken.add(c)
            room -= 1

    def t_set_terrain_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":", 1)
            if d == "WoodPlankFloor":
                self.floors |= self.cells(nums)
            else:
                self.floors -= self.cells(nums)
        return {"success": True}

    def t_map_zones(self, action=None, rect=None, **k):
        if action == "createZone":
            self.zones |= self.cells(rect)
        return {"success": True}

    def t_time_perf(self, **k):
        return {"success": True, "meanTickTime": 4.2}

    def t_save_game(self, saveName=None, **k):
        if saveName.startswith("lscrub_sc_"):
            self.scene = saveName            # _scene's recovery save: which scene is on the map
        self.saves[saveName] = copy.deepcopy((self.ticks, self.pawns, self.things))
        return {"success": True}

    def t_load_game_ready(self, saveName=None, **k):
        ticks, pawns, things = copy.deepcopy(self.saves[saveName])
        if saveName == self.scene:
            self.scene = None
        if "hoard_forgets_on_reload" in self.broken:
            for t in things.values():
                if t["def"] == V.HOARD:
                    t["held"], t["seen"] = [], {}
        if "cane_credit_lost_on_reload" in self.broken:
            for t in things.values():
                if t.get("burning") == "RM_DeadVenomvine":
                    t["fuel_level"] = t.get("fuel_level", 20) / 2
        if "reload_loses_pawn" in self.broken:
            col = sorted((int(p[1:]), p) for p in pawns if pawns[p]["kind"] == "Colonist")
            if len(col) > 30:
                del pawns[col[-1][1]]      # the newest colonist: one of the walk's forty
        if "reload_adds_thing" in self.broken and any(t["def"] == "RM_Fuzz" for t in things.values()):
            self.n += 1
            things["T%d" % self.n] = dict(id="T%d" % self.n, x=100, z=145, stackCount=1, growth=1.0, **{"def": "RM_Fuzz"})
        if "missing_lost_on_reload" in self.broken:
            for p in pawns.values():
                p["lost"] = []
        if "probe" in saveName and "restore_drops_bystander" in self.broken:
            del pawns[min((p for p in pawns if pawns[p]["kind"] == V.RECOVERY_KIND), key=lambda p: int(p[1:]))]
        if "probe" in saveName and "restore_tick_drift" in self.broken:
            ticks += 1
        for t in things.values():
            if t["def"] == V.REARING and "rear_lost_on_load" in self.broken:
                t["until"] = 0
            if t["def"] == V.QUENCH and "quench_lost_on_load" in self.broken:
                t["ready"] = 0
        if "pursuit_forgets_on_reload" in self.broken:     # the saved maker relation does not survive the load
            self.pursuit = None
            for t in things.values():
                t.pop("instigator", None)
        for p in pawns.values():
            p["reloaded"] = True
        if "crown_reload_forgets" in self.broken:
            self.crown_forgets = True
        self.ticks, self.pawns, self.things = ticks, pawns, things
        return {"success": True}

    def t_get_terrain_batch(self, rects=None, **k):
        dried = "vaporator_dries" in self.broken and any(
            t["def"] == "RM_WindVaporator" and self.ticks - t.get("born", self.ticks) > 3000 for t in self.things.values())
        return {"success": True, "ops": "Soil:%s" % rects + (";Sand:0,0" if dried else "")}

    def fuel(self, tid):
        """Campfire fuel: spawned full (20), burns 10 per day (Core CompProperties_Refuelable); a refuel resets the
        level ("fuel_level" at "fuel_at")."""
        t = self.things.get(tid) or {}
        return max(0.0, t.get("fuel_level", 20) - 10.0 * (self.ticks - t.get("fuel_at", t.get("born", self.ticks))) / 60000)

    def credit(self, d):
        """Fuel per item: wood 1, dead venomvine 2 (the scenes' designed premium)."""
        return 2.0 if d == "RM_DeadVenomvine" and "cane_no_premium" not in self.broken else 1.0

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, targetBId=None, targetAX=-1, targetAZ=-1, **k):
        if jobDef == "Wait":        # an ordered wait: a wild animal holds still (no wander)
            p = self.pawns[pawnId]
            p["job"], p["hold"], p["goto"] = "Wait", True, None
            return {"success": True, "accepted": True}
        if jobDef == "Goto":        # the scenes: an ordered walk arrives 300 ticks later and is "moving" until then
            p = self.pawns[pawnId]
            if p["kind"] != "Colonist" and p.get("hold"):
                p["job"] = "Goto"
            vine = set((t["x"], t["z"]) for t in self.of(V.THICKET))
            if (p["x"], p["z"]) in vine:     # the ordered return out of the vine: this pawn has made a trip
                p["tripped"] = self.ticks
            if (targetAX, targetAZ) in vine:
                if BODY.get(p["kind"], 1.0) >= 1.5 and "huge_ordered_through" not in self.broken:
                    return {"success": True, "accepted": True}      # no path: it stays put
                if p["kind"] == "Colonist" and "ordered_trip_refused" in self.broken:
                    return {"success": True, "accepted": True}
            p["goto"], p["moving_until"] = (targetAX, targetAZ), self.ticks + 300
            self.through_plants(p, targetAX, targetAZ)
            if p["kind"] == "RM_Dustflutter":
                p["job"] = "Goto"
            if "trip_never_returns" in self.broken and p["kind"] == "Colonist" and targetAX < p["x"]:
                p["goto"] = None
            return {"success": True, "accepted": True}
        if jobDef == "FixBrokenDownBuilding":
            self.jobs[pawnId] = {"kind": "repair", "a": targetAId, "b": targetBId, "left": 600}
            return {"success": True, "accepted": True}
        if jobDef in ("Ignite", "Wear", "RemoveApparel"):
            return self.instant_job(pawnId, jobDef, targetAId)
        kind = {"RM_SmotherVenomvine": "smother", "Refuel": "refuel", "Harvest": "harvest"}.get(jobDef)
        if kind == "refuel" and 20 - self.fuel(targetAId) < 1:   # JobDriver_Refuel ends on CompRefuelable.IsFull
            return {"success": False, "accepted": True, "afterJobDef": "Wait_MaintainPosture"}
        self.jobs[pawnId] = {"kind": kind, "a": targetAId, "b": targetBId, "left": 800}
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    # ------------------------------------------------------------ batch 5: viper, graphics, selection, shots
    def viper_pass(self):
        """RM_Fuzzviper's run-wall ambush as designed: a viper within 6 cells of a wall takes the wall-side cell beside
        it and holds (Wait_Ambush); traffic passing within 3 cells is struck from there (PredatorHunt, a Bite)."""
        walls = set((t["x"], t["z"]) for t in self.of("Wall"))
        prey = [p for p in self.pawns.values() if p["kind"] == V.VIPER_PREY]
        for v in [p for p in self.pawns.values() if p["kind"] == V.VIPER]:
            near = sorted(w for w in walls if abs(w[0] - v["x"]) <= 6 and abs(w[1] - v["z"]) <= 6)
            if near and "viper_never_holds" not in self.broken:
                if "spot" not in v:
                    w = min(near, key=lambda c: abs(c[0] - v["x"]) + abs(c[1] - v["z"]))
                    v["spot"] = (w[0], w[1] + (1 if v["z"] > w[1] else -1))
                v["x"], v["z"] = v["spot"]
                v["job"] = "Wait_Ambush" if self.ticks >= v.get("strike_until", 0) else "PredatorHunt"
            for q in prey:
                gx = (q.get("goto") or (q["x"], q["z"]))[0]
                if abs(q["z"] - v["z"]) <= 3 and min(q["x"], gx) - 3 <= v["x"] <= max(q["x"], gx) + 3 \
                        and "viper_never_strikes" not in self.broken:
                    v["job"], v["strike_until"] = "PredatorHunt", self.ticks + 600
                    q["hediffs"].append("Bite")
                    break

    def t_thing_graphic(self, thing=None, **k):
        """The live shape (l1_donor_off_round.py): {"things": [{id, resolvedPath, textureName, badTex}]}."""
        rows = []
        for tid in str(thing or "").split(","):
            t = self.things.get(tid)
            if t is None:
                continue
            d = t["def"]
            if "state_graphics_swapped" in self.broken and d in ("RM_RearingVenomvine", "RM_QuenchVenomvine"):
                d = "RM_QuenchVenomvine" if d == "RM_RearingVenomvine" else "RM_RearingVenomvine"
            tex = (V._visual_manifest().get(d) or {}).get("texPath")
            rows.append({"id": tid, "resolvedPath": tex + "/" + tex.split("/")[-1] + "A", "badTex": False})
        return {"success": True, "things": rows}

    def t_clear_selection(self, **k):
        self.selected = None
        return {"success": True}

    def t_click_cell(self, x=None, z=None, **k):
        """A plant is selected by a click on its cell or on its drawn art: half its visualSizeRange above the root."""
        self.selected = None
        for t in self.things.values():
            size = (V._visual_manifest().get(t["def"]) or {}).get("size") or 0
            reach = 0 if "overhang_unselectable" in self.broken else (99 if "click_reads_column" in self.broken
                                                                       else int(size / 2))
            if t["x"] == x and 0 <= z - t["z"] <= reach:
                self.selected = t["id"]
        return {"success": True}

    def t_get_selection_semantics(self, **k):
        return {"selection": [{"thingId": "Thing_" + self.selected}] if self.selected else []}

    def t_screenshot_cell_rect(self, x=0, z=0, width=1, height=1, fileName="shot", **k):
        path = "D:\\ClaudeWork\\fake\\%s.png" % fileName
        self.shots[path] = fileName
        return {"success": True, "path": path}

    def blind_or_art(self, which):
        """The judge's files: a blind reader that names each shot's subject; the art pipeline's verdicts."""
        if which == V.ART_EVAL:
            return dict((d, "REGEN" if "art_eval_red" in self.broken and d == V.TREE else "GREEN")
                        for _s, d in V.VISUAL_SUBJECTS)
        names = dict((s, d) for s, d in V.VISUAL_SUBJECTS)
        out = {}
        for path, name in self.shots.items():
            m = re.match(r"lscrub_visual_(\w+?)_(normal|close)_", name)
            if m:
                d = names.get(m.group(1))
                out[path] = "RM_QuenchVenomvine" if "blind_misread" in self.broken and d == "RM_SleeperVenomvine" else d
        return out

    # ------------------------------------------------------------ batch 8: rearing, quench, hatch, pillowmoss, ribbon
    def rear_pass(self):
        """SweepRearing (every 30 ticks, so before a spawned pawn wanders off): a big body in a grown stand rears it
        (RearTicks, Stall-stretched; an outsider's alert unless Gale; a concealed pawn revealed)."""
        b = self.broken
        stood = {}
        for p in self.pawns.values():
            if not p["dead"]:
                stood.setdefault((p["x"], p["z"]), []).append(p)
        for st in self.of(V.REARING):
            if not (self.on("rearingEnabled") or "rear_ignores_toggle" in b) or st.get("growth", 1.0) < V.REAR_MIN_GROWTH:
                continue
            for p in stood.get((st["x"], st["z"]), []):
                if BODY.get(p["kind"], 1.0) < V.REAR_MIN_BODY and "rear_small_rears" not in b:
                    continue
                if self.weather == "RM_Gale" and "rear_gale_immune" in b:
                    continue
                was = self.ticks < st.get("until", 0)
                stall = self.weather == "RM_Stall" and "rear_stall_ignored" not in b
                st["until"] = self.ticks + V._rear_ticks(self.settings["rearingHours"], stall, V.REAR_STALL)
                if (not was and p["faction"] == "none" and p["kind"] == "Colonist"
                        and (self.weather != "RM_Gale" or "rear_gale_alerts" in b)):
                    self.messages.append(V.REAR_ALERT + ".")
                if "rear_no_reveal" not in b:
                    p["concealed"] = False

    def quench_pass(self):
        """SweepQuench: a ready grown stand with a fire in reach bursts once, foams, and is spent for the recovery."""
        b = self.broken
        fires = [f for f in self.things.values() if f["def"] == "Fire"]
        for st in self.of(V.QUENCH):
            if not (self.on("quenchEnabled") or "quench_ignores_toggle" in b) or st.get("growth", 1.0) < V.QUENCH_MIN_GROWTH:
                continue
            if self.ticks < st.get("ready", 0) and "quench_repeat_burst" not in b:
                continue
            if not any(math.hypot(f["x"] - st["x"], f["z"] - st["z"]) <= V.QUENCH_REACH for f in fires):
                continue
            box = (st["x"] - 4, st["z"] - 4, 9, 9)
            for tid in [f["id"] for f in fires if inrect(f["x"], f["z"], box)]:
                self.things.pop(tid, None)
            self.pending_fire = [q for q in self.pending_fire if not inrect(q[1], q[2], box)]
            if "quench_no_foam" not in b:
                for dx in (-1, 0, 1):
                    self.new(V.FOAM, st["x"] + dx, st["z"], stackCount=1)
            st["ready"] = self.ticks + int(float(self.settings["quenchRecoveryDays"]) * 60000)
            fires = [f for f in fires if f["id"] in self.things]

    def hatch_pass(self):
        """CompHatcher's clock, and ProximityHatch: an enabled engine hatches a fertilized egg with a pawn in reach."""
        b = self.broken
        engine = self.hatch.get("enabled") == "True" or "hatch_ignores_enabled" in b
        reach = V.HATCH_RADIUS + (5 if "hatch_far" in b else 0)
        for e in self.of(V.HATCH_EGG) + self.of(V.HATCH_INFERTILE):
            fert = e["def"] == V.HATCH_EGG
            due = fert and self.ticks - e.get("born", self.ticks) >= V.HATCH_DAYS * 60000
            near = engine and (fert or "hatch_infertile" in b) and "hatch_never" not in b and any(
                not p["dead"] and p["kind"] != V.HATCH_PAWN and math.hypot(p["x"] - e["x"], p["z"] - e["z"]) <= reach
                for p in self.pawns.values())
            if due or near:
                del self.things[e["id"]]
                for _ in range(2 if "hatch_twins" in b else 1):
                    self.t_spawn_pawn(kindDef=V.HATCH_PAWN, x=e["x"], z=e["z"])

    def pillow_pass(self):
        if self.weather == "RM_ScrubWindFog" and "pillow_dry" not in self.broken and (
                self.settings.get("modEnabled") == "True" or "pillow_ignores_toggle" in self.broken):
            for m in self.of(V.PILLOW):
                self.wet[(m["x"], m["z"])] = self.ticks

    def wetness(self, x, z):
        b = self.broken
        cells = [(x, z)] + ([(x + dx, z + dz) for dx in range(-3, 4) for dz in range(-3, 4)] if "pillow_unbounded" in b
                            else [])
        last = max([self.wet[c] for c in cells if c in self.wet] or [None], key=lambda v: -1 if v is None else v)
        if last is None:
            return 0.0
        if "pillow_never_dries" in b and any((m["x"], m["z"]) == (x, z) for m in self.of(V.PILLOW)):
            return 0.6
        return 0.6 if self.ticks - last < V.PILLOW_INTERVAL else 0.0

    def in_ribbon_scene(self):
        return (self.scene or "").startswith("lscrub_sc_ribbon_route_")

    def canopy_path(self, start, prey, fuzz):
        """A ribbonwhip's route over connected fuzz to a cell beside its prey: [cells after start], or None."""
        goal = set((prey["x"] + dx, prey["z"] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)) & fuzz
        back, frontier = {start: None}, [start]
        while frontier:
            nxt = []
            for c in frontier:
                if c in goal:
                    path = []
                    while c != start:
                        path.append(c)
                        c = back[c]
                    return path[::-1]
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        n = (c[0] + dx, c[1] + dz)
                        if n in fuzz and n not in back:
                            back[n] = c
                            nxt.append(n)
            frontier = nxt
        return None

    def ribbon_pass(self, d):
        """The ribbon pad's ribbonwhips: travel stays on fuzz; a hungry one hunts a hare only over connected canopy."""
        b = self.broken
        if not self.in_ribbon_scene():
            return
        fuzz = set((t["x"], t["z"]) for t in self.of("RM_Fuzz"))
        prey = [q for q in self.pawns.values() if q["kind"] == V.LURE_EATER and not q["dead"]]
        for p in self.pawns.values():
            if p["kind"] != V.RIBBON or p["dead"]:
                continue
            hungry = p.get("food", 0.9) < 0.3 and bool(prey)
            path = self.canopy_path((p["x"], p["z"]), prey[0], fuzz) if hungry else None
            p["blocked"] = hungry and path is None
            if path is not None:
                p["job"] = "PredatorHunt"
                if path:
                    p["x"], p["z"] = path[:max(1, d // 50)][-1]
            elif p["blocked"] and "ribbon_crosses_gap" in b:
                p["x"] = min(prey[0]["x"] - 1, p["x"] + max(1, d // 50))
            elif "ribbon_touches_ground" in b and not hungry:
                p["x"] += 1
            else:
                nb = [(p["x"] + dx, p["z"] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)
                      if (dx or dz) and (p["x"] + dx, p["z"] + dz) in fuzz]
                if nb:
                    p["x"], p["z"] = self.ribbon_rng.choice(nb)

    def t_order_pawn(self, pawnId=None, x=None, z=None, **k):
        if self.cur_map in self.gen_maps:      # a walk from the start: blocked east under the break
            blocked = "start_exit_blocked" in self.broken and x > ISLAND_START[0] + 20
            return {"success": True, "results": [{"canReach": not blocked}]}
        self.walker_until, self.bloom_done = self.ticks + 400, False
        self.walker_z = self.pawns[pawnId]["z"]
        self.pawns[pawnId]["x"] += 0
        return {"success": True}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None and thingIds in self.pawns:      # a ribbonwhip says when no canopy reaches its prey
            p = self.pawns[thingIds]
            lines = ["No canopy route to prey."] if p.get("blocked") and "ribbon_silent" not in self.broken else []
            return {"success": True, "things": [{"id": thingIds, "label": p["kind"], "inspect": lines}]}
        if t is None:
            return {"success": True, "things": []}
        lines, label = [], t["def"]
        d = t["def"]
        if d == "WindTurbine":
            f = 1.22 if "surge_wrong_factor" in self.broken else float(self.settings["galeTurbineSurgeFactor"])
            surge = (self.on("galeTurbineSurgeEnabled") and "no_surge" not in self.broken
                     and (self.weather == "RM_Gale" or "surge_in_clear" in self.broken))
            lines = ["Power output: %d W" % round(1000 * (f if surge else 1.0))]
            if t.get("broken"):
                lines = ["Broken down"] + (lines if "broken_still_surges" in self.broken else [])
        elif d == V.REARING:
            if self.ticks < t.get("until", 0) and "rear_art_only" not in self.broken:
                lines = ["Reared upright against the lean: settles in 1 hour."]
        elif d == V.QUENCH:
            ready = self.ticks >= t.get("ready", 0)
            lines = (["Knuckles swollen: will burst at fire."] if ready and t.get("growth", 1.0) >= V.QUENCH_MIN_GROWTH
                     else [] if ready else ["Spent, knuckles cracked: swells again in 3 days."])
        elif d == "RM_TwitcherVenomvine":
            if self.on("twitcherLashEnabled") or "lash_ignores_toggle" in self.broken:
                lines = ["Poised to strike." if self.ticks >= t.get("ready", 0)
                         else "Spent, drooping: strikes again in 1 hour."]
        elif d == "RM_HollowVenomvine" and t["id"] in self.claims:
            due = self.ticks >= self.claims[t["id"]] + float(self.settings["smotherDays"]) * 60000
            lines = ["Smothered: dead through, ready to fall." if due
                     else "Smothered under a blanket: dead wood in 2 days."]
        elif d == "RM_DrippingVenomvine":
            # vanilla Plant.GetInspectString: "<N>% grown" plus "Growth rate: <R>%" (the trap 4cdec5dd8 fixed: the old
            # regex read the RATE line and failed a correct 30% stand)
            lines = ["%d%% grown" % int(100 * t.get("growth", 1)), "Growth rate: 100%"]
        elif d in (V.CRUST, V.CRUST_ALT, V.THICKET):
            g = t.get("growth", 1)      # vanilla Plant.GetInspectString: "Mature." at full growth, never "100% grown"
            lines = (["Mature."] if g >= 1 else ["%d%% grown" % int(round(100 * g))]) + ["Growth rate: 100%"]
        elif d == "Campfire":
            lines = ["Fuel: %d / 20" % round(self.fuel(t["id"]))]
        elif d == V.TREE and (self.on("sweetlineStationsEnabled") or "station_ignores_toggle" in self.broken):
            if "no_name" not in self.broken:
                label = "Ashveil (sweetline tree)"
            lines = ["Loose sweetline felt falls in 4 days."]
            if t.get("felt", 0) >= 1:
                lines.append("Felted into the bark: %d (harvestable)." % int(t["felt"]))
            if t.get("visits") and (self.on("sweetlineVisitorsEnabled") or "visitors_ignore_toggle" in self.broken):
                lines.insert(0, "Visitors remembered: %d camps, 0 pilgrims." % t["visits"])
        elif d == V.TREE:
            label = "sweetline tree"
        return {"success": True, "things": [{"id": t["id"], "label": label, "inspect": lines}]}


    # ------------------------------------------------------------ scenes batch 4 (fire, dripping, felt, routes)
    def lean_bias(self):
        if not self.on("leanFireEnabled") or "fire_no_bias" in self.broken:
            return 0.0
        bias = float(self.settings.get("leanFireBias", 0))
        return 0.5 if bias == 0 and "fire_bias_ignores_zero" in self.broken else bias

    def light(self, x, z, instigator=None, size=1.0):
        """A fire on a grass cell; it spreads to two neighbours once above size 1 (vanilla Fire): 60 ticks later at
        size >= 1, 600 (growing first) below. RM_TheLean.TrySpread_Prefix: the bias share picks a downwind neighbour of
        the fake's east wind, the rest is vanilla's uniform eight."""
        if any(t["def"] == "Fire" and (t["x"], t["z"]) == (x, z) for t in self.things.values()):
            return
        if not any(t["def"] == V.GRASS and (t["x"], t["z"]) == (x, z) for t in self.things.values()):
            return
        self.new("Fire", x, z, instigator=instigator, born=self.ticks)
        down = [(dx, dz) for dx, dz in zip(V.LEAN_DX, V.LEAN_DZ) if dx > 0]
        for _ in range(2):
            dx, dz = (self.rng.choice(down) if self.rng.random() < self.lean_bias()
                      else self.rng.choice(list(zip(V.LEAN_DX, V.LEAN_DZ))))
            self.pending_fire.append((self.ticks + (60 if size >= 1.0 else 600), x + dx, z + dz, instigator))

    def t_map_fire(self, action="start", rect=None, fireSize=0.5, **k):
        rr = V_rect(rect)
        if action == "extinguish":
            for tid in [i for i, t in self.things.items() if t["def"] == "Fire" and inrect(t["x"], t["z"], rr)]:
                del self.things[tid]
            self.pending_fire = [p for p in self.pending_fire if not inrect(p[1], p[2], rr)]
            return {"success": True}
        for cx in range(rr[0], rr[0] + rr[2]):
            for cz in range(rr[1], rr[1] + rr[3]):
                self.light(cx, cz, size=float(fireSize))
        return {"success": True}

    def blazes(self):
        """Fire clusters of 5 or more (RM_BlazeKernel.MinOpenFires 5): [(centre, instigator)]."""
        fires = [t for t in self.things.values() if t["def"] == "Fire"
                 and ((t["x"], t["z"]) not in self.roofed or "stamp_roofed_fire" in self.broken)]
        if "stamp_subthreshold" in self.broken and fires and len(fires) < 5:
            return [((fires[0]["x"], fires[0]["z"]), fires[0].get("instigator"))]
        out = []
        for f in fires:
            near = [g for g in fires if abs(g["x"] - f["x"]) <= 6 and abs(g["z"] - f["z"]) <= 6]
            if len(near) >= 5 and not any(abs(c[0] - f["x"]) <= 6 and abs(c[1] - f["z"]) <= 6 for c, _i in out):
                out.append(((f["x"], f["z"]), next((g.get("instigator") for g in near if g.get("instigator")), None)))
        return out

    def fire_pass(self):
        due = [p for p in self.pending_fire if p[0] <= self.ticks]
        self.pending_fire = [p for p in self.pending_fire if p[0] > self.ticks]
        for _t, x, z, who in due:
            self.light(x, z, who)
        herd = [p for p in self.pawns.values() if p["kind"] in self.stamper_kinds]
        if not herd:
            return
        cols = [p for p in self.pawns.values() if p["kind"] == "Colonist"]
        for centre, who in (self.blazes() if self.on("fireStampEnabled") else []):
            for i, p in enumerate(herd):
                if self.pursuit and p is herd[0]:
                    continue
                gx, gz = centre[0] + i, centre[1]       # a jog: at most 8 cells a pass (a teleport is not an approach)
                if "stamper_teleports" in self.broken:
                    p["x"], p["z"] = gx, gz
                else:
                    d = max(abs(gx - p["x"]), abs(gz - p["z"]), 1)
                    f = min(1.0, 0.05 * self.last_d / d)     # a jog of 0.05 cells a tick
                    p["x"], p["z"] = int(round(p["x"] + (gx - p["x"]) * f)), int(round(p["z"] + (gz - p["z"]) * f))
            self.last_blaze = centre
            if "stamp_never_stamps" not in self.broken and any(abs(p["x"] - centre[0]) <= 6 and abs(p["z"] - centre[1]) <= 6
                                                                 for p in herd):
                for tid in [i for i, t in self.things.items() if t["def"] == "Fire" and self.ticks - t["born"] >= 300
                            and abs(t["x"] - centre[0]) <= 6 and abs(t["z"] - centre[1]) <= 6]:
                    del self.things[tid]
            if who:     # the newest maker's blaze names the pursuit
                self.pursuit = who
            if not who and "unwitnessed_pursues" in self.broken and cols:
                self.pursuit = min(cols, key=lambda c: abs(c["x"] - centre[0]) + abs(c["z"] - centre[1]))["id"]
        target = self.pursuit
        if target and "blame_nearest" in self.broken and cols:     # the nearest pawn to the blaze takes the blame
            lb = self.last_blaze
            target = min(cols, key=lambda c: (c["x"] - lb[0]) ** 2 + (c["z"] - lb[1]) ** 2)["id"]
        if target in self.pawns:
            herd[0]["x"], herd[0]["z"] = self.pawns[target]["x"] + 1, self.pawns[target]["z"]

    def instant_job(self, pid, job, target):
        p, t = self.pawns.get(pid), self.things.get(target)
        if p is None or (t is None and job != "RemoveApparel"):
            return {"success": False, "message": "no pawn %s or thing %s" % (pid, target)}
        if job == "Ignite":
            self.light(t["x"], t["z"], pid, size=0.1)      # an Ignite job's fire starts small
        elif job == "Wear":
            p.setdefault("worn", []).append(t)
            del self.things[target]
        else:
            p["worn"] = [w for w in p.get("worn") or [] if w["id"] != target]
        return {"success": True, "accepted": True}

    def t_pawn_gear(self, pawn=None, action=None, clearWhat="all", **k):
        if action == "clear" and pawn in self.pawns:
            self.pawns[pawn]["worn"] = []
        return {"success": True}

    def t_stat_explain(self, subject=None, stats=None, **k):
        t = self.things.get(subject)
        felt = (t or {}).get("stuff") == V.FELT and self.on("sweetlineFeltComfortEnabled") and "felt_no_comfort" not in self.broken
        v = 0.5 + (V.FELT_OFFSET if felt else 0.0)
        return {"success": True, "stats": [{"defName": "Comfort", "value": v, "explanation": "Base value: 0.50"
                                            + ("\nSweetline felt: +%.2f" % V.FELT_OFFSET if felt else "")}]}

    def t_pawn_thoughts(self, pawn=None, **k):
        felt = [w for w in self.pawns[pawn].get("worn") or [] if w.get("stuff") == V.FELT]
        on = self.on("sweetlineFeltApparelEnabled") or "felt_apparel_ignores_toggle" in self.broken
        n = 0 if not (on and felt) else (len(felt) if "felt_thought_stacks" in self.broken else 1)
        return {"success": True, "thoughts": [{"def": V.FELT_THOUGHT, "moodOffset": 2} for _ in range(n)]}

    def t_stop_job(self, pawnId=None, **k):
        if pawnId in self.pawns and "cancel_ignored" not in self.broken:
            self.pawns[pawnId]["goto"] = None
        return {"success": True}

    def route_geo(self):
        return V._route_geometry(100 + V.PADS["routes"][0], 100 + V.PADS["routes"][1])

    def t_designate_batch(self, action=None, designation=None, rect=None, **k):
        if designation == "CutPlant" and "upkeep_never_cuts" not in self.broken:
            rr = V_rect(rect)
            gone = [i for i, t in self.things.items() if t["def"] in (V.THICKET, V.WALKER) and inrect(t["x"], t["z"], rr)]
            for i in gone:
                del self.things[i]
            self.cut_now = bool(gone) or getattr(self, "cut_now", False)
        return {"success": True}

    def walk_onset(self):
        """RM_CompWalking on a Gale's onset: 8 runners east (downwind) along each stand's row, never onto a plant, a
        building or developed ground (zone, floor, roof)."""
        if not self.on("walkingEnabled"):
            return
        g = self.route_geo() if self.of(V.WALKER) else None
        for w in list(self.of(V.WALKER)):
            if w.get("runner"):
                continue
            for k in range(1, 9):
                c = (w["x"] + k, w["z"])
                if c in self.zones or c in self.floors or c in self.roofed:
                    continue
                if any((t["x"], t["z"]) == c for t in self.things.values()):
                    continue
                self.new(V.WALKER, c[0], c[1], growth=0.3, stackCount=1, runner=True)
            if g and "walking_invades_developed" in self.broken:
                self.new(V.WALKER, g["a"][0][0], g["a"][0][1], growth=0.3, stackCount=1, runner=True)

    def route_pass(self):
        """The colony's routine work on the route site: two logs a pass from the source pile to the stockpile while a
        safe route stands (A without a wall, or B without vine or wall); otherwise they wait. Jobs: a hauler, a
        researcher at a bench, a cutter while CutPlant work exists."""
        g = self.route_geo()
        src = [t for t in self.of("WoodLog") if inrect(t["x"], t["z"], g["source"])]
        pad = V_rect("%d,%d,%d,%d" % (100 - V.ROUTE_SIZE // 2, 100 - V.ROUTE_SIZE // 2, V.ROUTE_SIZE, V.ROUTE_SIZE))
        cols = [p for p in self.pawns.values() if p["kind"] == "Colonist" and inrect(p["x"], p["z"], pad)]
        if not cols or not (src or any(inrect(t["x"], t["z"], g["stock"]) for t in self.of("WoodLog"))):
            return
        blocked = set((t["x"], t["z"]) for t in self.things.values() if t["def"] in ("Wall", V.THICKET, V.WALKER))
        safe = not (blocked & set(g["a"])) or not (blocked & set(g["b"]))
        for p in cols:
            p["job"] = "Wait_Wander"
        if src and (safe or "auto_work_crosses_vine" in self.broken):
            for t in src[:2]:
                t["x"], t["z"] = g["stock"][0], g["stock"][1]
            cols[0]["job"] = "HaulToCell"
            if not safe:
                cols[0]["x"], cols[0]["z"] = sorted(blocked & set(g["b"]))[0]
        vine = sorted(blocked & set(g["b"]) - set((t["x"], t["z"]) for t in self.of("Wall")))
        for p in cols:
            if vine and p.get("tripped") is not None and self.ticks > p["tripped"] + 1000 and not p.get("goto") and (
                    "completed_order_authorizes" in self.broken or p.get("reloaded") and "reload_authorizes" in self.broken):
                p["x"], p["z"] = vine[0]
        if len(cols) > 1 and self.of("SimpleResearchBench"):
            cols[1]["job"] = "Research"
        if len(cols) > 2 and getattr(self, "cut_now", False):
            cols[2]["job"] = "CutPlant"
        self.cut_now = False

def V_rect(s):
    return rect(s)


# ------------------------------------------------------------------ the runner

ROOF_STRIPS = []    # rects the suite opened to the sky (modcheck4 2026-10-16: unsupported mountain roof crushed actors)


def run(broken=()):
    game = Fake(broken)
    V._about_text = lambda: game.about
    V._save_bytes = game.save_bytes
    V._load_json = game.blind_or_art
    V._stamper_kinds = lambda: {"base": sorted(game.stamper_kinds - {V.STAMPER}), "campaign": [V.STAMPER]}
    results = {}
    for name, fn in V.suite.chains:
        t = TestContext(game, anchor=(100, 100))
        try:
            fn(t)
        except Exception as ex:            # a chain-level crash is a script bug
            results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
            continue
        for c in t.components:
            results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return results


# break -> the component that must go FAIL
BREAKS = {
    "missing_def": ("defs.defs_resolve", "scene_floor_payload.payload_running_list_and_defs",
                    "scene_removed_save_preservation.saves_scene_current_products_kept"),
    "pyre_counts_fires": "edge_fixes.pyre_thin_line_follows_blaze",
    "bloom_scares_manhunter": ("edge_fixes.bloom_spares_manhunter", "scene_bloom.bloom_scene_manhunter_keeps_its_state"),
    "genstep_tidies": "edge_fixes.map_step_refuses_pawn_cell",
    "arm_draws_none": "edge_fixes.vissler_arm_draws_meat_eaters",
    "arm_ignores_toggle": "edge_fixes.vissler_arm_off_draws_none",
    "no_weather_entry": ("defs.biome_weather_table", "scene_wind_plain.windplain_weather_table"),
    "no_lean_ext": ("defs.biome_lean_extension", "scene_floor_payload.payload_base_effects_present"),
    "rule_unarmed": "patches.rules_armed",
    "thicket_unpatched": "patches.thicket_smotherable",
    "arm_not_rotting": "patches.vissler_arm_is_rotting_meat",
    "fuel_unpatched": ("patches.dead_venomvine_fuels_fire", "scene_cane_fuel.cane_accepted_by_wood_filter",
                       "scene_colony_walk.walk_order_a_trip_then_fuel"),
    "setting_missing": ("settings.defaults", "scene_settings.settings_census", "scene_fire_bias.fire_bias_beds_staged"),
    "set_plants_drops": "flora.flora_spawns",
    "no_pollute": "flora.flora_spawns",          # LIVE 2026-10-07: RM_Grellspine on a clean cell
    "no_fly": "fauna.dustflutter_can_fly",
    "no_freeze": "stall.stall_freezes_small",
    "freeze_ignores_toggle": "stall.stall_toggle_off_wanders",
    "master_ignored": "stall.stall_master_off_wanders",
    "no_deafen": "gale.gale_deafens_outdoors",
    "deafen_ignores_roof": "gale.gale_spares_roofed",
    "deafen_ignores_toggle": "gale.gale_deafen_toggle_off",
    "no_surge": "gale.gale_turbine_surge",
    "no_breakdown": "gale.gale_turbine_breakdown",
    "lash_ignores_toggle": "lash.lash_toggle_off_quiet",
    "no_lash": "lash.lash_strikes_once",
    "lash_repeats": "lash.lash_strikes_once",
    "no_smother_bank": "smother.smother_claims_stands",
    "smother_ignores_toggle": "smother.smother_off_holds_claims",
    "no_mature": "smother.smother_matures_to_dead_wood",
    "regrow_broken": ("dripping.dripping_survives_harvest", "scene_dripping.dripping_scene_startup_apply"),
    "regrow_full": ("dripping.dripping_survives_harvest", "scene_dripping.dripping_scene_startup_apply"),
    "crown_ignores_toggle": ("crown.crown_toggle_off_stays_away", "scene_crown.crown_scene_toggle_off_quiet"),
    "no_crown": ("crown.crown_mob_gathers", "scene_crown.crown_scene_arrivals_attributed"),
    "bloom_ignores_toggle": ("bloom.bloom_toggle_off_quiet", "scene_bloom.bloom_scene_toggle_off_quiet",
                             "scene_arm_regrowth.arm_regrowth_off_sheds_nothing"),
    "no_bloom": ("bloom.bloom_answers_a_walker", "scene_bloom.bloom_scene_walk_answers",
                 "scene_ribbon_route.ribbon_sway_preserved"),
    "no_exit_hole": "bloom.bloom_sway_and_exit_hole",
    "dens_empty": "dens.thornhold_dens_in_venomvine",
    "dens_blind": "dens.thornhold_dens_in_venomvine",
    "den_never": "dens.thornhold_dens_in_venomvine",
    "den_wrong_cell": "dens.thornhold_dens_in_venomvine",
    "stand_ignores_toggle": "dens.thornhold_stand_toggle_off_refused",
    "stand_never": "dens.thornhold_stands_at_den",
    "stand_wrong_target": "dens.thornhold_stands_at_den",
    "roll_ignores_toggle": "dens.rollbug_colony_corpse_toggle_off_refused",
    "roll_never": "dens.rollbug_rolls_any_corpse",
    "roll_copies": "dens.rollbug_rolls_any_corpse",
    "roll_loses": "dens.rollbug_rolls_any_corpse",
    "roll_far": "dens.rollbug_rolls_any_corpse",
    "bite_never": "dens.rollbug_bites_its_ball",
    "station_ignores_toggle": "sweetline.station_toggle_off_plain",
    "no_name": "sweetline.station_named_and_timed",
    "no_wool": "sweetline.station_sheds_wool",
    "no_scratch": "sweetline.scratch_drops_coat",
    "scratch_ignores_toggle": "sweetline.scratch_toggle_off_refused",
    "no_map_step": "sweetline.map_step_plants_one_or_two",
    "four_strangler_never": "four_forms.strangler_acts",
    "four_weeper_never": "four_forms.weeper_acts",
    "four_sleeper_never": "four_forms.sleeper_acts",
    "four_lure_never": "four_forms.lure_acts",
    "four_strangler_ignores_toggle": "four_forms.strangler_toggle_off",
    "four_weeper_ignores_toggle": "four_forms.weeper_toggle_off",
    "four_sleeper_ignores_toggle": "four_forms.sleeper_toggle_off",
    "four_lure_ignores_toggle": "four_forms.lure_toggle_off",
    "no_comfort": "sweetline.felt_furniture_comfort",
    "comfort_ignores_toggle": "sweetline.felt_comfort_toggle_off_plain",
    "map_step_ignores_chance": "sweetline.map_step_chance_zero_plants_none",
    "visitors_ignore_toggle": "sweetline.visitors_toggle_off_quiet",
    "no_visits": "sweetline.visitors_come_and_leave_marks",
    "log_error": ("log.log_clean", "scene_floor_recovery.recovery_log_window_clean"),
    "stamp_never": "stamp.stamp_answers_a_blaze",
    "stamp_ignores_toggle": "stamp.stamp_toggle_off_ignores_fire",
    "stallhunt_never": "stallhunt.stallhawk_hunts_in_the_stall",
    "stallhunt_ignores_toggle": "stallhunt.stallhawk_toggle_off_idle",
    "ripple_never": "ripple.ripple_hides_small_creatures",
    "wind_off_sun": "lean.lean_heading_from_sun",
    "scent_never": "lean.lean_scent_upwind_flees",
    "scent_ignores_toggle": "lean.lean_scent_toggle_off",
    "fire_unbiased": "lean.lean_fire_downwind",
    "ripple_ignores_toggle": "ripple.ripple_toggle_off_nobody_hides",
    "pyre_ungated": "pyre.pyre_beliefs_gated_on_memes",
    "pyre_no_fire": "pyre.pyre_lights_fields_and_calls_herd",
    "pyre_ignores_toggle": "pyre.pyre_toggle_off_refuses",
    "vaporator_unlearnable": "injections.vaporator_learned_from_farmstead",
    "no_farmstead": "injections.map_holds_ruins_and_camps",
    "no_camp_people": "injections.map_holds_ruins_and_camps",
    "no_islands": "islands.islands_laid_share",
    "no_creep": ("islands.creep_runner_unarmed", "scene_creep.creep_scene_runners_young_downwind"),
    "creep_ignores_toggle": ("islands.creep_toggle_off", "scene_creep.creep_scene_toggle_off_quiet"),
    "creep_ignores_cap": ("islands.creep_cap_stops", "scene_creep.creep_scene_cap_stops"),
    "no_exempt": ("islands.growth_exempt_from_explosive_growth", "scene_creep.creep_scene_explosive_growth_exempt"),
    "stock_overcast": ("defs.biome_weather_table", "scene_wind_plain.windplain_weather_table"),
    "twin_calm": "windlean.twins_carry_wind",
    "lean_mixed": "windlean.lean_faces_wind",
    "lean_ignores_toggle": ("windlean.lean_toggle_off_vanilla", "scene_wind_plain.windplain_lean_off_keeps_weather"),
    "gale_no_overlay": ("windlean.gale_dust_overlay", "scene_gale_drawing.gale_drawing_streams_downwind"),
}
# the acceptance scenes (scene_* chains, RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT)
BREAKS.update({
    "arm_never_eaten": "scene_arm_food.arm_food_meat_eater_eats_it",
    "arm_herbivore_eats": "scene_arm_food.arm_food_herbivore_leaves_it",
    "arm_eaten_off": "scene_arm_food.arm_food_toggle_off_uneaten",
    "arm_eaten_through_walls": "scene_arm_food.arm_food_unreachable_uneaten",
    "arm_never_rots": "scene_arm_food.arm_food_rots_on_real_ticks",
    "shed_without_loss": "scene_arm_regrowth.arm_shed_costs_one_arm_each",
    "missing_lost_on_reload": "scene_arm_regrowth.arm_missing_survives_reload",
    "regrow_early": "scene_arm_regrowth.arm_still_missing_before_the_season",
    "regrow_never": "scene_arm_regrowth.arm_regrows_after_one_season",
    "bloom_bare_ground": "scene_bloom.bloom_scene_bare_ground_quiet",
    "sway_never_released": "scene_bloom.bloom_scene_sway_released",
    "hole_never": "scene_bloom.bloom_scene_exit_hole_only_from_under",
    "eruptor_grounded": "scene_bloom.bloom_scene_eruptor_takes_off_owner_present",
    "guardian_text": ("scene_cuts.cuts_no_cut_content", "scene_floor_payload.payload_text_promises_nothing_cut"),
    "about_promises_wardens": ("scene_cuts.cuts_no_cut_content", "scene_floor_payload.payload_text_promises_nothing_cut"),
    "farmer_camps_back": "scene_cuts.cuts_no_cut_content",
    "vaporator_dries": "scene_cuts.cuts_vaporator_ground_kept",
    # scenes batch 2 (2026-11-16)
    "cast_never_generates": "scene_native_cast.cast_roster_generates",
    "cast_leaks_to_control": "scene_native_cast.cast_roster_generates",
    "pyre_def_discarded": "scene_pyre_beliefs.pyre_beliefs_characterized",
    "pyre_ritual_discarded": "scene_pyre_ritual.pyre_ritual_characterized",
    "payload_not_attached": "scene_acoustic_payload.acoustic_payload_attached",
    "pulse_reads_quiet": "scene_acoustic_payload.acoustic_pulses_read_their_target",
    "pulse_reads_without_target": "scene_acoustic_payload.acoustic_pulses_read_their_target",
    "ripple_bare_hides": ("scene_concealment.concealment_bare_lane_visible",
                          "scene_ribbon_route.ribbon_concealment_preserved"),
    "ripple_stall_move_hidden": ("scene_concealment.concealment_stall_move_reveals",
                                 "scene_lee_reveal.lee_moving_in_lee_revealed"),
    "ripple_gale_no_extend": "scene_concealment.concealment_gale_extends_size",
    "ripple_hides_mental": "scene_concealment.concealment_mental_state_not_hidden",
    "ripple_ignores_toggles": ("scene_concealment.concealment_toggle_off_nobody_hidden",
                               "scene_settings.settings_all_off_quiet"),
    "ripple_dead_after_master_off": ("scene_settings.settings_reenabled_effect_returns",
                                     "scene_lee_reveal.lee_still_in_lee_hidden",
                                     "scene_ribbon_route.ribbon_concealment_preserved"),
    "cane_no_premium": "scene_cane_fuel.cane_more_burn_per_item",
    "cane_no_heat_bonus": "scene_cane_fuel.cane_heat_rate_higher",
    "cane_credit_lost_on_reload": "scene_cane_fuel.cane_credit_survives_reload",
    "fuel_meter_biased": "scene_cane_fuel.cane_wood_control_alike",
    "trip_never_returns": ("scene_colony_walk.walk_order_a_trip_then_fuel",
                           "scene_ordered_travel.ordered_trip_carried_out"),
    "reload_loses_pawn": "scene_colony_walk.walk_save_reload_resumes",
    "timing_no_work": "scene_floor_runtime.runtime_work_counted",
    "save_grows": "scene_floor_persistence.persist_no_growth",
    "reload_adds_thing": "scene_floor_persistence.persist_three_cycles",
    # scenes batch 3 (2026-11-16)
    "crown_over_cap": "scene_crown.crown_scene_cap_held_across_reload",
    "crown_reload_forgets": "scene_crown.crown_scene_cap_held_across_reload",
    "crown_hijacks_busy": "scene_crown.crown_scene_busy_job_intact",
    "cruststar_never_grazed": "scene_cruststar.cruststar_scene_grazed_and_fed",
    "cruststar_no_nutrition": "scene_cruststar.cruststar_scene_grazed_and_fed",
    "cruststar_never_recovers": "scene_cruststar.cruststar_scene_resource_recovers",
    "cruststar_through_walls": "scene_cruststar.cruststar_scene_unreachable_untouched",
    "creep_runner_armed": "scene_creep.creep_scene_runners_young_downwind",
    "creep_no_downwind": "scene_creep.creep_scene_runners_young_downwind",
    "creep_overruns_protection": "scene_creep.creep_scene_protected_cells_kept",
    "aliases_still_ship": "scene_removed_save_preservation.saves_scene_no_preservation_ships",
    "tombstone_ships": "scene_removed_save_preservation.saves_scene_no_preservation_ships",
    "egg_deleted": ("scene_removed_save_preservation.saves_scene_current_products_kept",
                    "scene_floor_payload.payload_running_list_and_defs"),
    "dlc_missing": "scene_floor_payload.payload_running_list_and_defs",
    "restore_drops_bystander": "scene_floor_recovery.recovery_exact_state_returns",
    "restore_tick_drift": "scene_floor_recovery.recovery_exact_state_returns",
    # batch 4 (RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_NINETY_FIVE_BARS_LEFT)
    "fire_no_bias": "scene_fire_bias.fire_bias_downwind_lift",
    "fire_bias_ignores_zero": "scene_fire_bias.fire_bias_control_plain",
    "blame_nearest": ("scene_ix_fire_accountability.accountability_maker_not_innocent",
                      "scene_maker.maker_witnessed_identified"),
    "pursuit_forgets_on_reload": "scene_ix_fire_accountability.accountability_maker_not_innocent",
    "unwitnessed_pursues": ("scene_ix_fire_accountability.accountability_unwitnessed_no_pursuit",
                            "scene_maker.maker_no_event_no_pursuit"),
    "regrow_ignores_write": "scene_dripping.dripping_scene_write_off_one_shot",
    "felt_no_comfort": "scene_felt_comfort.felt_scene_seat_offset",
    "felt_thought_stacks": "scene_felt_comfort.felt_scene_single_thought",
    "felt_apparel_ignores_toggle": "scene_felt_comfort.felt_scene_toggles_independent",
    "walking_invades_developed": ("scene_home_routes.routes_maintained_carry_work",
                                  "scene_ix_route_growth.ixroutes_only_authorized_in_hazard"),
    "upkeep_never_cuts": "scene_home_routes.routes_maintained_carry_work",
    "auto_work_crosses_vine": ("scene_ix_route_growth.ixroutes_only_authorized_in_hazard",
                               "scene_ordered_travel.ordered_auto_work_avoids_vine"),
    "cancel_ignored": ("scene_ix_route_growth.ixroutes_cancel_stops_expedition",
                       "scene_ordered_travel.ordered_cancel_grants_nothing"),
    # batch 5 (RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_EIGHTY_SIX_BARS_LEFT)
    "gale_across_wind": "scene_gale_drawing.gale_drawing_streams_downwind",
    "gale_draws_when_off": "scene_gale_drawing.gale_drawing_overlay_off_control",
    "gale_keeps_ticking": "scene_gale_drawing.gale_drawing_clear_removes",
    "gale_art_placeholder": "scene_gale_drawing.gale_drawing_art_state",
    "stamper_teleports": "scene_stamping.stamping_campaign_binding",
    "stamp_never_stamps": "scene_stamping.stamping_campaign_binding",
    "stamp_roofed_fire": "scene_stamping.stamping_controls_quiet",
    "stamp_subthreshold": ("scene_stamping.stamping_controls_quiet", "scene_ix_fire_accountability.accountability_blaze_answered"),
    "no_base_stamper": "scene_stamping.stamping_base_binding",
    "store_reads_fire_as_taking": "scene_maker.maker_shared_evidence_store",
    "viper_never_holds": "scene_fuzzviper.fuzzviper_holds_run_wall",
    "viper_never_strikes": "scene_fuzzviper.fuzzviper_strikes_from_wall",
    "state_graphics_swapped": "scene_floor_visual.visual_textures_own_and_distinct",
    "blind_misread": "scene_floor_visual.visual_captures_blind_read",
    "art_eval_red": "scene_floor_visual.visual_art_eval_green",
    "overhang_unselectable": "scene_floor_visual.visual_overhang_selects_and_orders_ack",
    "click_reads_column": "scene_floor_visual.visual_overhang_selects_and_orders_ack",
    "order_ignored": "scene_floor_visual.visual_overhang_selects_and_orders_ack",
})
for _form, _plant in V.FORMS:
    BREAKS["%s_never" % _form] = "forms.%s_acts" % _form
    BREAKS["%s_ignores_toggle" % _form] = "forms.%s_toggle_off" % _form
# the five live scenes (sc_gale_exposure, sc_working_wind, sc_raid_weight, sc_hollow, sc_hoard): a defect the older
# chains already catch also turns the scene row that watches the same behaviour red
BREAKS.update({
    "no_deafen": ("gale.gale_deafens_outdoors", "scene_gale_exposure.exposure_unroofed_organic_deafened"),
    "deafen_ignores_roof": ("gale.gale_spares_roofed", "scene_gale_exposure.exposure_roof_spares"),
    "no_surge": ("gale.gale_turbine_surge", "scene_working_wind.wind_gale_ratio_matches_factor"),
    "no_breakdown": ("gale.gale_turbine_breakdown", "scene_working_wind.wind_breakdown_seeded"),
    "hoard_ignores_toggle": ("forms.hoard_toggle_off", "scene_hoard.hoard_toggle_off"),
    "deafen_ignores_mech": "scene_gale_exposure.exposure_mech_spares",
    "deafen_cuts_nothing": "scene_gale_exposure.exposure_def_cuts_hearing_talking",
    "deafen_live_untouched": "scene_gale_exposure.exposure_live_capacity_reduced",
    "deafen_ignores_toggle": ("gale.gale_deafen_toggle_off", "scene_gale_exposure.exposure_toggle_off"),
    "deafen_never_recovers": "scene_gale_exposure.exposure_recovers_after_gale",
    "surge_in_clear": "scene_working_wind.wind_ordinary_no_surge",
    "surge_wrong_factor": "scene_working_wind.wind_gale_ratio_matches_factor",
    "breaks_unowned": "scene_working_wind.wind_unowned_never_rolled",
    "broken_still_surges": "scene_working_wind.wind_broken_gets_no_surge",
    "battery_never_charges": "scene_working_wind.wind_battery_stores",
    "repair_never_fixes": "scene_working_wind.wind_repair_by_job",
    "raid_weight_ignores_gale": "scene_raid_weight.raid_weight_gale_only",
    "raid_weight_ignores_toggle": "scene_raid_weight.raid_weight_gale_only",
    "raid_weights_all": "scene_raid_weight.raid_nonraid_unchanged",
    "raid_hook_schedules": "scene_raid_weight.raid_nothing_scheduled",
    "raid_rule_unarmed": ("patches.rules_armed", "scene_raid_weight.raid_binding_armed"),
    "breaks_at_mtb_zero": "scene_working_wind.wind_mtb_zero_never_breaks",
    "no_crawl_job": "scene_hollow.hollow_crawl_job",
    "hollow_threads": "scene_hollow.hollow_free_pass_band",
    "hollow_venoms": "scene_hollow.hollow_no_contact_venom",
    "huge_passes_hollow": "scene_hollow.hollow_huge_blocked",
    "thicket_no_venom": "scene_hollow.thicket_keeps_hazards",
    "hoard_never_takes": "scene_hoard.hoard_stores_eligible",
    "hoard_takes_far": "scene_hoard.hoard_excludes_goods_and_bystander",
    "hoard_takes_corpse": "scene_hoard.hoard_corpse_stays_gear_kept",
    "hoard_forgets_on_reload": "scene_hoard.hoard_survives_reload",
    "hoard_drops_twice": "scene_hoard.hoard_returns_once_on_fall",
})

# batch 7 (RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_SEVENTY_BARS_LEFT): wind_plain, lee_reveal, island_land, ordered_travel, lure
BREAKS.update({
    "twins_global": "scene_wind_plain.windplain_weather_table",
    "stall_blows": "scene_wind_plain.windplain_wind_factors",
    "live_stall_blows": "scene_wind_plain.windplain_live_wind",
    "heading_constant": "scene_wind_plain.windplain_heading_geometry",
    "heading_reversed": "scene_wind_plain.windplain_heading_geometry",
    "lean_wrong_side": "scene_wind_plain.windplain_plant_facing_snap",
    "lean_toggle_moves_weather": "scene_wind_plain.windplain_lean_off_keeps_weather",
    "lee_never_reveals": "scene_lee_reveal.lee_moving_in_lee_revealed",
    "lee_too_long": "scene_lee_reveal.lee_moving_beyond_hidden",
    "lee_reversed": "scene_lee_reveal.lee_reversed_wall_no_lee",
    "lee_ignores_toggle": "scene_lee_reveal.lee_wakes_off_no_lee",
    "islands_share_low": "scene_island_land.island_share_meets_target",
    "islands_room_everywhere": "scene_island_land.island_rooms_rarer_no_sworn",
    "sworn_island": "scene_island_land.island_rooms_rarer_no_sworn",
    "islands_crowd_start": "scene_island_land.island_start_clear_exits_walkable",
    "start_exit_blocked": "scene_island_land.island_start_clear_exits_walkable",
    "islands_ignore_toggle": "scene_island_land.island_toggle_off_lays_none",
    "ordered_trip_refused": "scene_ordered_travel.ordered_trip_carried_out",
    "completed_order_authorizes": "scene_ordered_travel.ordered_completed_grants_nothing",
    "reload_authorizes": "scene_ordered_travel.ordered_reload_grants_nothing",
    "huge_ordered_through": "scene_ordered_travel.ordered_blocked_body_stays_out",
    "lure_over_cap": "scene_lure.lure_emits_to_cap",
    "lure_fed_eats": "scene_lure.lure_fed_not_attracted",
    "lure_through_walls": "scene_lure.lure_unreachable_uneaten",
    "lure_never_eaten": "scene_lure.lure_hungry_herbivore_eats_fruit",
    "lure_ignores_toggle": "scene_lure.lure_off_and_young_drop_none",
    "lure_young_drops": "scene_lure.lure_off_and_young_drop_none",
})

BREAKS.update({         # batch 8: rearing, quench, proximity_hatch, pillowmoss, ribbon_route
    "rear_art_only": "scene_rearing.rearing_rears_for_big_intruder",
    "rear_lost_on_load": "scene_rearing.rearing_rest_saved_and_settles",
    "rear_stall_ignored": "scene_rearing.rearing_stall_extends",
    "rear_gale_immune": "scene_rearing.rearing_gale_still_rears",
    "rear_gale_alerts": "scene_rearing.rearing_gale_masks_alert",
    "rear_no_reveal": "scene_rearing.rearing_reveals_concealed",
    "rear_small_rears": "scene_rearing.rearing_controls_do_not_rear",
    "rear_ignores_toggle": "scene_rearing.rearing_controls_do_not_rear",
    "quench_no_foam": "scene_quench.quench_bursts_once_at_fire",
    "quench_repeat_burst": "scene_quench.quench_spent_no_repeat",
    "quench_lost_on_load": "scene_quench.quench_recovery_saved",
    "quench_ignores_toggle": ("forms.quench_toggle_off", "scene_quench.quench_controls_hold"),
    "hatch_never": "scene_proximity_hatch.hatch_near_pawn_hatches_once",
    "hatch_twins": "scene_proximity_hatch.hatch_near_pawn_hatches_once",
    "hatch_far": "scene_proximity_hatch.hatch_controls_leave_egg",
    "hatch_infertile": "scene_proximity_hatch.hatch_controls_leave_egg",
    "hatch_ignores_enabled": "scene_proximity_hatch.hatch_timer_without_engine",
    "pillow_dry": "scene_pillowmoss.pillowmoss_wet_under_moss_in_fog",
    "pillow_unbounded": "scene_pillowmoss.pillowmoss_bounded",
    "pillow_never_dries": "scene_pillowmoss.pillowmoss_expires_dry",
    "pillow_ignores_toggle": "scene_pillowmoss.pillowmoss_controls_dry",
    "ribbon_touches_ground": "scene_ribbon_route.ribbon_ordinary_route_on_canopy",
    "ribbon_crosses_gap": "scene_ribbon_route.ribbon_hunt_refuses_bare_gap",
    "ribbon_silent": "scene_ribbon_route.ribbon_inability_readable",
    "ribbon_unhidden": "scene_ribbon_route.ribbon_concealment_preserved",
    "ribbon_no_sway": "scene_ribbon_route.ribbon_sway_preserved",
})


def main():
    bad = []
    healthy = run()
    notpass = dict((k, v) for k, v in healthy.items() if v[0] != "PASS")
    n_comp = len(healthy)
    if notpass:
        bad.append("healthy run: %d of %d components not PASS: %s" % (len(notpass), n_comp, notpass))
    declared = len(V.suite.components_declared())
    if declared != n_comp:
        bad.append("declared %d components but the run produced %d" % (declared, n_comp))
    # SITE guard (modcheck4 2026-10-16): every cleared pad must be opened to the sky before any tick, or a mountain
    # site's unsupported roof drops on the chain's actors (Koyo crushed in lash; the bloom cohort crushed).
    pads = set(re.findall(r'_prep\(t, "(\w+)"', open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()))
    centres = set((x + w // 2, z + h // 2) for x, z, w, h in ROOF_STRIPS)
    want = set((100 + V.PADS[p][0], 100 + V.PADS[p][1]) for p in pads if p in V.PADS)
    if want - centres:
        bad.append("pads cleared but never opened to the sky (roof strip): %s" % sorted(want - centres))
    for brk, target in sorted(BREAKS.items()):
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != sorted([target] if isinstance(target, str) else target):
            bad.append("break %-24s expected only %s FAIL, got %s" % (brk, target, reds))
    print("selftest LeaningScrub: %d components healthy-PASS %d/%d; %d breaks each turn exactly "
          "their component red" % (n_comp, n_comp - len(notpass), n_comp,
                                   len(BREAKS) - len([1 for b in bad if b.startswith("break ")])))
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
