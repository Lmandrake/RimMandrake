#!/usr/bin/env python3
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
        "RM_Fuzzrunner": 0.2, "RM_Vissler": 0.15, "Colonist": 1.0, "RM_Ribbonwhip": 0.25}
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
            self.creep_tick(self.ticks - d, self.ticks)
            self.chunk(d)
            self.ripple_pass()
            self.fire_pass()
            self.route_pass()

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
            p["job"] = "Wait_Wander" if frozen else "GotoWander"
            walled = any(inrect(p["x"], p["z"], r) for r in self.rooms)
            if not frozen and not walled:     # wander stays local (the scenes run thousands of ticks on one animal)
                p["x"] += 1 if (self.ticks // 250) % 2 else -1
        # --- Gale: deafen
        if self.weather == "RM_Gale":
            gate = self.on("galeDeafenEnabled") or "deafen_ignores_toggle" in b
            for p in self.pawns.values():
                if p["faction"] != "player" or "no_deafen" in b or not gate:
                    continue
                roofed = any(inrect(p["x"], p["z"], r) for r in self.rooms)
                if roofed and "deafen_ignores_roof" not in b:
                    continue
                if "RM_GaleDeafened" not in p["hediffs"]:
                    p["hediffs"].append("RM_GaleDeafened")
        # --- turbines (2500 boundary)
        if self.ticks // 2500 != self.tick_hist:
            self.tick_hist = self.ticks // 2500
            if (self.weather == "RM_Gale" and self.on("galeTurbineSurgeEnabled")
                    and 0 < float(self.settings["galeTurbineBreakdownMtbDays"]) < 0.1
                    and "no_breakdown" not in b):
                for t in self.of("WindTurbine"):
                    if t.get("faction") == "PlayerColony":    # listerBuildings.allBuildingsColonist only
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
                        if p["kind"] == "RM_Ribbonwhip":
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
        if want and all(w.startswith("WeatherDef/RM_Scrub") for w in want):
            rows = []
            for w in want:
                n = w.split("/", 1)[1]
                off = 0.0 if ("twin_calm" in self.broken and n == "RM_ScrubGrayPall") else 0.4
                rows.append({"defName": n, "fields": {"windSpeedOffset": off, "windSpeedFactor": 1.0}})
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
        if want == ["BiomeDef/%s" % V.CAST_CONTROL_BIOME]:
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": V.CAST_CONTROL_BIOME, "fields": {
                "wildPlants": [{"plant": "Plant_Grass", "commonality": 1.0}]}}]}
        if fields == "label" and want and all(w in V._pyre_shipped() for w in want):
            gone = {"pyre_def_discarded": "RM_CallingPyre_LastRite", "pyre_ritual_discarded": "RM_Ritual_CallingPyre"}
            drop = set(n for b, n in gone.items() if b in self.broken)
            rows = [{"defName": w.split("/", 1)[1], "fields": {"label": "x"}} for w in want if w.split("/", 1)[1] not in drop]
            return {"success": True, "foundCount": len(rows), "notFound": [], "defs": rows}
        if want == ["ThingDef/%s" % V.TREE]:
            return {"success": True, "foundCount": 1, "notFound": [],
                    "defs": [{"defName": V.TREE, "fields": {"label": "sweetline tree", "thingClass": "Plant", "comps": [
                        "RimMandrake.LeaningScrub.RM_CompProperties_SweetlineStation"]}}]}
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

    def t_harmony_patches(self, typeName=None, methodName=None, **k):
        for typ, meth, kind, patch in V.RULES:
            if (typ, meth) == (typeName, methodName):
                armed = not ("rule_unarmed" in self.broken and typ == "JobGiver_Wander")
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
            {"id": p["id"], "job": "Flee" if self.ticks < p.get("flee_until", 0) else p.get("job", "Wait_Wander")}
            for p in self.pawns.values()]}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        if self.cur_map in self.gen_maps:
            return {"success": True, "countMatched": self.gen_census(defName), "things": []}
        rr = V_rect(rect) if rect else None
        rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows),
                "things": [dict(t) for t in rows[:limit]]}

    def t_static_call(self, type=None, method=None, args="", **k):
        if type == "Verse.Log":
            self.log.append({"type": method, "text": args})
            return {"success": True}
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
        if method == "ProofLean":
            if args == "off":
                return {"success": True, "result": "FAIL faced with the toggle off east=0 west=40" if "lean_ignores_toggle" in self.broken
                        else "PASS east=0 west=0 rolled=12"}
            return {"success": True, "result": "FAIL mixed lean east=3 west=37" if "lean_mixed" in self.broken
                    else "PASS east=0 west=40 rolled=12 windWest=True"}
        if method == "ProofGale":
            if self.weather != "RM_Gale":
                return {"success": True, "result": "UNMEASURED the Gale is not the current weather"}
            return {"success": True, "result": "FAIL RM_Gale does not carry RM_WeatherOverlay_GaleDust" if "gale_no_overlay" in self.broken
                    else "PASS weather=RM_Gale art=PLACEHOLDER (vanilla fog sheet) drew=True"}
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
            self.new("Corpse_" + p["kind"], p["x"], p["z"], faction=p["faction"])
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
        for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
            del self.things[tid]
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
        if comp == "SandSwim" and thing in self.pawns:
            return {"success": True, "values": {"Submerged": "True"}}
        return {"success": False, "message": "no comp %s on %s" % (comp, thing)}

    def t_map_comp_read(self, comp=None, members=None, **k):
        if comp == "RM_MapComponent_VenomvineCreep":
            return {"success": True, "values": {"Applies": "True", "openCells": str(self.OPEN_CELLS),
                                                "vineCells": str(len(self.of(V.THICKET)))}}
        if comp == "RM_MapComponent_Lean":
            return {"success": True, "values": {"Downwind": "(1.00, 0.00)"}}
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
            if p.get("goto") and self.ticks >= p["moving_until"]:
                p["x"], p["z"] = p["goto"]
                p["goto"] = None
            wild = p["faction"] == "none" and p["kind"] != "Colonist" and p["kind"] != "RM_Surrik" and (
                not p.get("mental") or "ripple_hides_mental" in b)
            cover = (p["x"], p["z"]) in fuzz or "ripple_bare_hides" in b
            moving = self.ticks < p.get("moving_until", 0) and "ripple_stall_move_hidden" not in b
            hide = (on and wild and not p["dead"] and cover and BODY.get(p["kind"], 1.0) <= limit
                    and not (self.weather == "RM_Stall" and moving))
            hs = p["hediffs"]
            if hide and "RM_RippleHidden" not in hs:
                hs.append("RM_RippleHidden")
            elif not hide and "RM_RippleHidden" in hs:
                hs.remove("RM_RippleHidden")

    def t_map_info(self, **k):
        return {"success": True, "mapId": self.cur_map}

    def t_world_tile_map_generate(self, tile=None, biome=None, **k):
        mid = 10 + len(self.gen_maps) + len(self.saves)
        self.gen_maps[mid] = biome
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
        ids += ["brrainz.harmony", V.OUR_PACKAGES[1], V.SCANNER_PKG]
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
        self.saves[saveName] = copy.deepcopy((self.ticks, self.pawns, self.things))
        return {"success": True}

    def t_load_game_ready(self, saveName=None, **k):
        ticks, pawns, things = copy.deepcopy(self.saves[saveName])
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
        if "pursuit_forgets_on_reload" in self.broken:     # the saved maker relation does not survive the load
            self.pursuit = None
            for t in things.values():
                t.pop("instigator", None)
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
        if jobDef == "Goto":        # the scenes: an ordered walk arrives 300 ticks later and is "moving" until then
            p = self.pawns[pawnId]
            p["goto"], p["moving_until"] = (targetAX, targetAZ), self.ticks + 300
            if p["kind"] == "RM_Dustflutter":
                p["job"] = "Goto"
            if "trip_never_returns" in self.broken and p["kind"] == "Colonist" and targetAX < p["x"]:
                p["goto"] = None
            return {"success": True, "accepted": True}
        if jobDef in ("Ignite", "Wear", "RemoveApparel"):
            return self.instant_job(pawnId, jobDef, targetAId)
        kind = {"RM_SmotherVenomvine": "smother", "Refuel": "refuel", "Harvest": "harvest"}.get(jobDef)
        if kind == "refuel" and 20 - self.fuel(targetAId) < 1:   # JobDriver_Refuel ends on CompRefuelable.IsFull
            return {"success": False, "accepted": True, "afterJobDef": "Wait_MaintainPosture"}
        self.jobs[pawnId] = {"kind": kind, "a": targetAId, "b": targetBId, "left": 800}
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_order_pawn(self, pawnId=None, x=None, z=None, **k):
        self.walker_until, self.bloom_done = self.ticks + 400, False
        self.walker_z = self.pawns[pawnId]["z"]
        self.pawns[pawnId]["x"] += 0
        return {"success": True}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        lines, label = [], t["def"]
        d = t["def"]
        if d == "WindTurbine":
            lines = ["Broken down"] if t.get("broken") else [
                "Power output: %d W" % (round(1000 * (1.3 if self.weather == "RM_Gale" and
                                                      self.on("galeTurbineSurgeEnabled")
                                                      and "no_surge" not in self.broken else 1.0)))]
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

    def light(self, x, z, instigator=None):
        """A fire on a grass cell; it spreads to two neighbours 60 ticks later (RM_TheLean.TrySpread_Prefix: the
        bias share picks a downwind neighbour of the fake's east wind, the rest is vanilla's uniform eight)."""
        if any(t["def"] == "Fire" and (t["x"], t["z"]) == (x, z) for t in self.things.values()):
            return
        if not any(t["def"] == V.GRASS and (t["x"], t["z"]) == (x, z) for t in self.things.values()):
            return
        self.new("Fire", x, z, instigator=instigator, born=self.ticks)
        down = [(dx, dz) for dx, dz in zip(V.LEAN_DX, V.LEAN_DZ) if dx > 0]
        for _ in range(2):
            dx, dz = (self.rng.choice(down) if self.rng.random() < self.lean_bias()
                      else self.rng.choice(list(zip(V.LEAN_DX, V.LEAN_DZ))))
            self.pending_fire.append((self.ticks + 60, x + dx, z + dz, instigator))

    def t_map_fire(self, action="start", rect=None, fireSize=0.5, **k):
        rr = V_rect(rect)
        if action == "extinguish":
            for tid in [i for i, t in self.things.items() if t["def"] == "Fire" and inrect(t["x"], t["z"], rr)]:
                del self.things[tid]
            self.pending_fire = [p for p in self.pending_fire if not inrect(p[1], p[2], rr)]
            return {"success": True}
        for cx in range(rr[0], rr[0] + rr[2]):
            for cz in range(rr[1], rr[1] + rr[3]):
                self.light(cx, cz)
        return {"success": True}

    def blazes(self):
        """Fire clusters of 3 or more (RM_BlazeKernel.MinOpenFires): [(centre, instigator)]."""
        fires = [t for t in self.things.values() if t["def"] == "Fire"]
        out = []
        for f in fires:
            near = [g for g in fires if abs(g["x"] - f["x"]) <= 6 and abs(g["z"] - f["z"]) <= 6]
            if len(near) >= 3 and not any(abs(c[0] - f["x"]) <= 6 and abs(c[1] - f["z"]) <= 6 for c, _i in out):
                out.append(((f["x"], f["z"]), next((g.get("instigator") for g in near if g.get("instigator")), None)))
        return out

    def fire_pass(self):
        due = [p for p in self.pending_fire if p[0] <= self.ticks]
        self.pending_fire = [p for p in self.pending_fire if p[0] > self.ticks]
        for _t, x, z, who in due:
            self.light(x, z, who)
        herd = [p for p in self.pawns.values() if p["kind"] == V.STAMPER]
        if not herd:
            return
        cols = [p for p in self.pawns.values() if p["kind"] == "Colonist"]
        for centre, who in (self.blazes() if self.on("fireStampEnabled") else []):
            for i, p in enumerate(herd):
                if self.pursuit and p is herd[0]:
                    continue
                p["x"], p["z"] = centre[0] + i, centre[1]
            self.last_blaze = centre
            for tid in [i for i, t in self.things.items() if t["def"] == "Fire" and self.ticks - t["born"] >= 300
                        and abs(t["x"] - centre[0]) <= 6 and abs(t["z"] - centre[1]) <= 6]:
                del self.things[tid]
            if who and self.pursuit is None:
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
            self.light(t["x"], t["z"], pid)
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
    "no_weather_entry": "defs.biome_weather_table",
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
    "no_bloom": ("bloom.bloom_answers_a_walker", "scene_bloom.bloom_scene_walk_answers"),
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
    "stock_overcast": "defs.biome_weather_table",
    "twin_calm": "windlean.twins_carry_wind",
    "lean_mixed": "windlean.lean_faces_wind",
    "lean_ignores_toggle": "windlean.lean_toggle_off_vanilla",
    "gale_no_overlay": "windlean.gale_dust_overlay",
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
    "ripple_bare_hides": "scene_concealment.concealment_bare_lane_visible",
    "ripple_stall_move_hidden": "scene_concealment.concealment_stall_move_reveals",
    "ripple_gale_no_extend": "scene_concealment.concealment_gale_extends_size",
    "ripple_hides_mental": "scene_concealment.concealment_mental_state_not_hidden",
    "ripple_ignores_toggles": ("scene_concealment.concealment_toggle_off_nobody_hidden",
                               "scene_settings.settings_all_off_quiet"),
    "ripple_dead_after_master_off": "scene_settings.settings_reenabled_effect_returns",
    "cane_no_premium": "scene_cane_fuel.cane_more_burn_per_item",
    "cane_no_heat_bonus": "scene_cane_fuel.cane_heat_rate_higher",
    "cane_credit_lost_on_reload": "scene_cane_fuel.cane_credit_survives_reload",
    "fuel_meter_biased": "scene_cane_fuel.cane_wood_control_alike",
    "trip_never_returns": "scene_colony_walk.walk_order_a_trip_then_fuel",
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
    "blame_nearest": "scene_ix_fire_accountability.accountability_maker_not_innocent",
    "pursuit_forgets_on_reload": "scene_ix_fire_accountability.accountability_maker_not_innocent",
    "unwitnessed_pursues": "scene_ix_fire_accountability.accountability_unwitnessed_no_pursuit",
    "regrow_ignores_write": "scene_dripping.dripping_scene_write_off_one_shot",
    "felt_no_comfort": "scene_felt_comfort.felt_scene_seat_offset",
    "felt_thought_stacks": "scene_felt_comfort.felt_scene_single_thought",
    "felt_apparel_ignores_toggle": "scene_felt_comfort.felt_scene_toggles_independent",
    "walking_invades_developed": ("scene_home_routes.routes_maintained_carry_work",
                                  "scene_ix_route_growth.ixroutes_only_authorized_in_hazard"),
    "upkeep_never_cuts": "scene_home_routes.routes_maintained_carry_work",
    "auto_work_crosses_vine": "scene_ix_route_growth.ixroutes_only_authorized_in_hazard",
    "cancel_ignored": "scene_ix_route_growth.ixroutes_cancel_stops_expedition",
})
for _form, _plant in V.FORMS:
    BREAKS["%s_never" % _form] = "forms.%s_acts" % _form
    BREAKS["%s_ignores_toggle" % _form] = "forms.%s_toggle_off" % _form


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
