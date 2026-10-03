#!/usr/bin/env python3
"""Offline selftest for Cauldron's validation.py: a scripted FAKE GAME that implements the mod's
behaviours, run (1) healthy -- every component must PASS -- and (2) once per mod behaviour broken --
the named component must go FAIL and no other component may.

That second half is the proof every check can fail: each break is a mod defect (a def that did not
resolve, an effect that never fires, a toggle that gates nothing, a roof that is ignored) and the
suite must see it. The fake encodes the response SHAPES validation.py assumes (read off the JawaBench
[Tool] source and Pyrelands' live-measured helpers); it proves the predicates and wiring, not the
shapes -- those stay UNPROVEN until the first live run.

Also guards the script against drifting from the mod's source: every class named in TYPES exists in
Source/, and the Mod Settings defaults the suite parsed match the C# initialisers.

    python3 src/RimMandrake/Cauldron/selftest_cauldron.py
"""
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

spec = importlib.util.spec_from_file_location("cauldron_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait poll loop must not really sleep

from suite import TestContext                     # noqa: E402

NATIVE_KIND, NONNATIVE_KIND = "Deer", "Elk"        # the fake map's biome roster: Deer native, Elk not
COMP_ROWS = {
    V.SUUSH: ["CompProperties_Explosive"],
    V.VEXXISS: ["RM_CompProperties_VexxissBehaviour", "CompProperties_Shearable"],
}


def rect(s):
    return [int(v) for v in str(s).split(",")]


def inrect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class Fake(object):
    def __init__(self, broken=()):
        self.broken = set(broken)
        self.ticks = 1000
        self.fast = False
        self.n = 0
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        if "setting_missing" in self.broken:
            del self.settings["vexxissAttacksIgniter"]
        self.weather, self.wage = "RM_ScatterDusk", 99999     # wage: ticks since the weather last changed
        self.things, self.pawns, self.terrain = {}, {}, {}
        self.rooms, self.letters, self.fires, self.jobs = [], [], [], {}
        self.last_letter = {}

    # ------------------------------------------------------------ session surface
    def _ticks(self):
        if self.fast:
            self.advance(2000)
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

    # ------------------------------------------------------------ small helpers
    def new(self, d, x, z, **kw):
        self.n += 1
        tid = "T%d" % self.n
        row = dict(id=tid, **dict(kw, x=x, z=z))
        row["def"] = d
        if d == V.VENT:
            row.update(supp=0.0, sil=-1)
        self.things[tid] = row
        return tid

    def of(self, d):
        return [t for t in self.things.values() if t["def"] == d]

    def on(self, f, ignore=None):
        if ignore and ignore in self.broken:
            return True
        return self.settings.get(f) == "True"

    def factor(self, f):
        return float(self.settings[f])

    def roofed(self, p):
        return any(inrect(p["x"], p["z"], r) for r in self.rooms)

    def add_hediff(self, p, d, sev):
        for h in p["hediffs"]:
            if h["def"] == d:
                h["severity"] += sev
                return
        p["hediffs"].append({"def": d, "severity": sev})

    # ------------------------------------------------------------ the vent (CAULDRON_VENT_ENRICHMENT_HOOKS_1)
    FALTER, WMULT = 0.1, {"RM_ScatterDusk": 1.0, "RM_VentBloom": 2.5, "RM_VapourBank": 0.8, "RM_Dewfall": 0.6}

    def vent_mult(self):
        b = self.broken
        if "weather_mult_flat" in b:
            return 1.0
        if not self.on("ventWeatherEnabled", "weather_ignores_toggle"):
            return 1.0
        if self.weather == V.BLOOM and self.wage < 4000 and "no_falter" not in b:
            return self.FALTER
        return self.WMULT.get(self.weather, 1.0)

    def vent_recovery(self, v):
        if v["sil"] < 0:
            return 1.0
        if self.ticks < v["sil"] or "no_recovery" in self.broken:
            return 0.0
        return min(1.0, (self.ticks - v["sil"]) / 60000.0)

    def vent_silenced(self, v):
        return v["sil"] >= 0 and (self.ticks < v["sil"] or "no_recovery" in self.broken)

    def vent_output(self, v):
        return self.vent_mult() * self.vent_recovery(v)

    def exposure_weight(self, p):
        vents = self.of(V.VENT)
        if not vents or not self.on("ventLocalExposureEnabled", "local_ignores_toggle") \
                or "exposure_not_local" in self.broken:
            return 1.0
        best = 0.0
        for v in vents:
            d = ((v["x"] - p["x"]) ** 2 + (v["z"] - p["z"]) ** 2) ** 0.5
            prox = 1.0 if d <= 8 else 0.0 if d >= 45 else 1.0 - (d - 8) / 37.0
            best = max(best, prox * self.vent_recovery(v))
        return 0.1 + 0.9 * best

    def drink_vents(self, d):
        for v in self.of(V.VENT):
            v["supp"] = max(0.0, v["supp"] - d * 0.5 / 60000.0)
        if "no_drink" in self.broken:
            return
        for p in self.pawns.values():
            if p["kind"] != V.VEXXISS or p["dead"] or p["faction"] != "none":
                continue
            if not self.on("vexxissDrinksVentsEnabled", "drink_ignores_toggle") or self.ticks < p.get("nd", 0):
                continue
            for v in self.of(V.VENT):
                if abs(v["x"] - p["x"]) > 40 or abs(v["z"] - p["z"]) > 40:
                    continue
                if self.vent_silenced(v) or self.vent_output(v) <= 0.05:
                    continue
                self.jobs[p["id"]] = (V.DRINK_JOB, self.ticks + 900)
                p["nd"] = self.ticks + 2750
                v["supp"] += 900 / 6000.0
                if "never_silences" in self.broken:
                    v["supp"] = min(v["supp"], 0.9)
                else:
                    if v["supp"] >= 1.0:
                        v["supp"] = 0.0
                        v["sil"] = self.ticks + int(self.factor("ventSilenceDays") * 60000)
                break

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            old = self.ticks
            self.ticks += d
            self.wage += d
            self.chunk(d, old)

    def chunk(self, d, old):
        b = self.broken
        # --- vent bloom exposure at multiples of the interval, once the weather transition is done
        if old // V.BLOOM_INTERVAL != self.ticks // V.BLOOM_INTERVAL and self.weather == V.BLOOM \
                and self.wage >= 4000 and "no_exposure" not in b \
                and (self.settings["ventBloomExposureEnabled"] == "True" or "bloom_ignores_toggle" in b):
            for p in self.pawns.values():
                if p["dead"]:
                    continue
                if self.roofed(p) and "exposure_ignores_roof" not in b:
                    continue
                if p["kind"] == NATIVE_KIND and "exposure_hits_natives" not in b:
                    continue
                f = 1.0 if "factor_ignored_bloom" in b else self.factor("ventBloomExposureFactor")
                self.add_hediff(p, V.HEDIFF, 0.012 * f * self.exposure_weight(p))
                if "double_tax" in b:
                    self.add_hediff(p, "ToxicBuildup", 0.01)
        # --- the vexxiss: poisons the water it stands in, warns, wards fire
        for p in self.pawns.values():
            if p["kind"] != V.VEXXISS or p["dead"]:
                continue
            here = self.terrain.get((p["x"], p["z"]))
            if here == "WaterShallow" and "no_poison" not in b and \
                    self.on("vexxissPoisonsWater", "poison_ignores_toggle"):
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if self.terrain.get((p["x"] + dx, p["z"] + dz)) == "WaterShallow":
                            self.terrain[(p["x"] + dx, p["z"] + dz)] = "ToxicWaterShallow"
                colonist = any(q["faction"] == "player" for q in self.pawns.values())
                last = self.last_letter.get(p["id"], -10 ** 9)
                cooled = self.ticks - last >= 60000 or "no_cooldown" in b
                if colonist and cooled and "no_letter" not in b and \
                        self.on("vexxissWaterLetter", "letter_ignores_toggle"):
                    self.last_letter[p["id"]] = self.ticks
                    self.letters.append({"label": V.LETTER_LABEL, "defName": "NegativeEvent"})
            if self.fires and "no_warden" not in b and self.on("vexxissFireWardenEnabled", "warden_ignores_toggle"):
                if any(abs(f[0] - p["x"]) <= 14 and abs(f[1] - p["z"]) <= 14 for f in self.fires):
                    self.jobs[p["id"]] = ("BeatFire", self.ticks + 300)
        self.drink_vents(d)
        # --- the suush's wick
        for pid, p in list(self.pawns.items()):
            if p.get("wick") and self.ticks >= p["wick"]:
                del self.pawns[pid]
        # --- queued harvests
        for pid, job in list(self.jobs.items()):
            if job[0] == "Harvest" and self.ticks >= job[1]:
                del self.jobs[pid]
                tr = self.things.pop(job[2], None)
                if tr:
                    self.new("WoodLog", tr["x"], tr["z"], stackCount=25)
                    if "no_metal" not in b and self.on("metalYieldEnabled", "metal_ignores_toggle"):
                        f = 1.0 if "factor_ignored_yield" in b else self.factor("metalYieldFactor")
                        self.new("Steel", tr["x"], tr["z"], stackCount=int(round(6 * f)))
        # fires burn for a while
        self.fires = [f for f in self.fires if f[2] > self.ticks]

    # ------------------------------------------------------------ tools: clock, weather, settings
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_set_time_speed(self, speed=None, **k):
        self.fast = speed == "Ultrafast"
        return {"success": True}

    def t_time_set_ticks(self, ticks=0, **k):
        self.ticks = int(ticks)
        return {"success": True}

    def t_weather_set(self, weather=None, lockWeather=False, unlock=False, **k):
        if weather and weather != self.weather:
            if not ("weather_not_settable" in self.broken and weather == "RM_VapourBank"):
                self.weather, self.wage = weather, 0
        return {"success": True}

    def t_weather_get(self, **k):
        return {"success": True, "weather": {"current": self.weather}}

    def t_site_state(self, **k):
        rows = []
        for p in self.pawns.values():
            job = self.jobs.get(p["id"])
            rows.append({"id": p["id"], "job": job[0] if job and job[1] > self.ticks else "Wander"})
        return {"success": True, "pawns": rows,
                "weather": {"cur": self.weather, "transition": min(1.0, self.wage / 4000.0)},
                "storyteller": {"enabledAfter": False}}

    def t_mod_settings_field(self, typeName=None, action=None, field=None, value=None, **k):
        if field not in self.settings:
            return {"success": False, "message": "no such field"}
        if action == "set":
            self.settings[field] = str(value)
        return {"success": True, "value": self.settings[field]}

    def t_map_info(self, **k):
        return {"success": True, "sizeX": 250, "sizeZ": 250, "mapBiome": "TemperateForest"}

    # ------------------------------------------------------------ tools: defs
    def t_get_defs(self, defs="", fields=None, limit=200, deep=False, **k):
        want = [d for d in defs.split(";") if d]
        if want == ["BiomeDef/%s" % V.BIOME]:
            if fields == "workerClass":
                wc = "BiomeWorker_PoisonForest" if "worker_donor" in self.broken else "RM_BiomeWorker_Cauldron"
                return self._defs(V.BIOME, {"workerClass": wc})
            table = [{"weather": w, "commonality": c} for w, c in
                     (("RM_ScatterDusk", 60), ("RM_VapourBank", 20), ("RM_Dewfall", 12), ("RM_VentBloom", 8),
                      ("DryThunderstorm", 1), ("Fog", 0), ("Clear", 7 if "stock_weather" in self.broken else 0))]
            return self._defs(V.BIOME, {"baseWeatherCommonalities": table})
        if want and want[0].startswith("WeatherDef/"):
            out = []
            for w in want:
                n = w.split("/")[1]
                out.append({"defName": n, "fields": {
                    "rainRate": 0.4 if (n == "RM_Dewfall" and "weather_rains" in self.broken) else 0.0,
                    "snowRate": 0.0, "windSpeedFactor": 1.0,
                    "doToxicBuildup": n == V.BLOOM and "bloom_toxic_buildup" in self.broken,
                    "isBad": n in (V.BLOOM, "RM_VapourBank")}})
            return {"success": True, "foundCount": len(out), "notFound": [], "defs": out}
        if want == ["TerrainDef/RM_CauldronSoil", "TerrainDef/RM_CauldronSoilRich"]:
            return {"success": True, "foundCount": 2, "notFound": [], "defs": [
                {"defName": "RM_CauldronSoil", "fields": {"fertility": 0.85}},
                {"defName": "RM_CauldronSoilRich", "fields": {"fertility": 1.2}}]}
        if want == ["ThingDef/%s" % V.ZISSKA]:
            steel = [] if "no_zisska_steel" in self.broken else [{"thingDef": "Steel", "count": 3}]
            return self._defs(V.ZISSKA, {"butcherProducts": steel,
                                         "race": {"specificMeatDef": "RM_ZisskaMeat"}})
        if want == ["ThingDef/RM_ZisskaMeat"]:
            docs = [] if "meat_not_toxic" in self.broken else [{"hediffDef": "ToxicBuildup", "severity": 0.05}]
            return self._defs("RM_ZisskaMeat", {"ingestible": {"outcomeDoers": docs}})
        missing = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if "missing_def" in self.broken and want and want[0] in V.SHIPPED:
            missing.append(want[3])
        return {"success": True, "notFound": missing, "foundCount": len(want) - len(missing)}

    def _defs(self, name, fields):
        return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": name, "fields": fields}]}

    def t_get_def(self, defName=None, defType=None, **k):
        if defType == "BiomeDef":
            return {"success": True, "extra": {"terrainsByFertility": [
                {"terrain": "RM_CauldronSoil", "min": -999, "max": 0.87},
                {"terrain": "RM_CauldronSoilRich", "min": 0.87, "max": 999}]}}
        if defName == V.NETTLE:
            ext = [] if "nettle_ext_missing" in self.broken else ["RM_CondensateHabitatExtension"]
            return {"success": True, "extra": {"modExtensions": ext}, "comps": []}
        if defName in V.VENT_PLANTS:
            ext = [] if ("vent_ext_missing" in self.broken and defName == "RM_BloodBouquet") \
                else ["RM_CondensateHabitatExtension"]
            return {"success": True, "extra": {"modExtensions": ext}, "comps": []}
        if defName == V.VENT:
            return {"success": True, "extra": {"modExtensions": ["RM_VentExtension"]}, "comps": []}
        classes = list(COMP_ROWS.get(defName, []))
        if defName == V.VEXXISS and "vexxiss_explosive" in self.broken:
            classes.append("CompProperties_Explosive")
        comps = []
        for c in classes:
            row = {"class": c, "fields": {}}
            if c == "CompProperties_Shearable":
                row["fields"] = {"woolDef": "RM_Vexxith"}
            comps.append(row)
        return {"success": True, "comps": comps,
                "statBases": {"MaxFlightTime": 600} if defName == V.SUUSH else {}}

    def t_type_probe(self, typeName=None, **k):
        if typeName.endswith("NoSuchType_Probe"):
            return {"success": True, "resolved": False}
        gone = "type_unresolved" in self.broken and typeName.endswith("RM_CompMetalYield")
        return {"success": True, "resolved": not gone, "inAllTypesByIdentity": True,
                "mvidMatchesFile": "stale_dll" not in self.broken,
                "carryingMods": ["mandrake.rm.biomes"]}

    def t_biome_probe(self, biomes=None, find=None, plants=False, **k):
        names = [n for n in (find or "").split(",") if n]
        rows = []
        for n in names:
            if n.endswith("NoSuchBeast_Probe"):
                st = "absent"
            elif biomes == V.BIOME:
                st = "zeroed" if ("roster_zeroed" in self.broken and n == V.VEXXISS) else "spawning"
            else:
                st = "spawning" if n in (NATIVE_KIND, "Muffalo") else "absent"
            rows.append({"defName": n, "state": st})
        return {"success": True, "biomes": [{"defName": biomes, "animalDensity": 0.8, "findResults": rows}]}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=50, **k):
        msgs = []
        if "log_error" in self.broken and contains == "Cauldron":
            msgs = [{"type": "Error", "text": "[RM Cauldron] Config error in RM_Zisska: bad tool group"}]
        return {"success": True, "totalInBuffer": 321, "messages": msgs}

    def t_pawn_flight(self, pawn=None, **k):
        return {"success": True, "pawns": [{"id": pawn, "canEverFly": "suush_no_fly" not in self.broken,
                                            "maxFlightTimeStat": 600.0}]}

    # ------------------------------------------------------------ tools: pawns
    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", count=1, **k):
        self.n += 1
        pid = "P%d" % self.n
        if "kind_missing" in self.broken and kindDef == V.ESKITH:
            return {"success": True, "pawns": [{"id": pid}]}          # reported, never actually there
        self.pawns[pid] = dict(id=pid, kind=kindDef, x=x, z=z, faction=faction, dead=False, hediffs=[])
        return {"success": True, "pawns": [{"id": pid}]}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, **k):
        rr = V_rect(rect) if rect else None
        rows = []
        for p in self.pawns.values():
            if rr and not inrect(p["x"], p["z"], rr):
                continue
            row = {"id": p["id"], "kindDef": p["kind"], "x": p["x"], "z": p["z"], "dead": p["dead"],
                   "faction": None if p["faction"] == "none" else p["faction"]}
            if includeHealth:
                row["health"] = {"hediffs": [dict(h) for h in p["hediffs"]]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_pawn_need(self, **k):
        return {"success": True}

    def t_set_draft(self, **k):
        return {"success": True}

    def t_pawn_health(self, pawn=None, action=None, hediff=None, **k):
        p = self.pawns[pawn]
        if action == "remove":
            p["hediffs"] = [h for h in p["hediffs"] if h["def"] != hediff]
        return {"success": True}

    def t_damage(self, damageDef=None, amount=0, thingId=None, **k):
        p = self.pawns.get(thingId)
        if p and p["kind"] == V.SUUSH:
            hit = damageDef in ("Bullet", "Bomb") and "no_detonate" not in self.broken
            if damageDef == "Cut" and "melee_detonates" in self.broken:
                hit = True
            if hit:
                p["wick"] = self.ticks + 150
        return {"success": True}

    # ------------------------------------------------------------ tools: things and terrain
    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = V_rect(rect) if rect else None
        if defName == "Fire":
            rows = [{"id": "F%d" % i, "x": f[0], "z": f[1]} for i, f in enumerate(self.fires)
                    if not rr or inrect(f[0], f[1], rr)]
        else:
            rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows), "things": [dict(t) for t in rows[:limit]]}

    def t_spawn_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            self.new(d, n[0], n[1], stackCount=n[2] if len(n) > 2 else 1)
        return {"success": True}

    def t_set_plants(self, ops="", growth=1.0, **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            if "set_plants_drops" in self.broken and d == "RM_Xithess":
                continue
            for cx in range(n[0], n[0] + (n[2] if len(n) > 2 else 1)):
                for cz in range(n[1], n[1] + (n[3] if len(n) > 3 else 1)):
                    self.new(d, cx, cz, growth=growth, stackCount=1)
        return {"success": True}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = V_rect(rects)
        if categories != "Pawn":
            for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
                del self.things[tid]
            self.fires = [f for f in self.fires if not inrect(f[0], f[1], rr)]
        if categories in ("Pawn", "All"):
            for pid in [i for i, p in self.pawns.items() if inrect(p["x"], p["z"], rr)]:
                del self.pawns[pid]
        return {"success": True}

    def t_make_empty_room(self, rect=None, **k):
        r = V_rect(rect)
        self.rooms.append((r[0] + 1, r[1] + 1, r[2] - 2, r[3] - 2))
        return {"success": True}

    def t_get_roof_batch(self, rects=None, **k):
        return {"success": True, "roofedCells": 49}

    def t_set_terrain_batch(self, ops="", layer="top", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            x, z, w, h = [int(v) for v in nums.split(",")]
            for cx in range(x, x + w):
                for cz in range(z, z + h):
                    self.terrain[(cx, cz)] = d
        return {"success": True}

    def t_get_terrain_batch(self, rects=None, layer="top", **k):
        x, z, w, h = V_rect(rects)
        ops = []
        for cx in range(x, x + w):
            for cz in range(z, z + h):
                ops.append("%s:%d,%d,1,1" % (self.terrain.get((cx, cz), "Soil"), cx, cz))
        return {"success": True, "cellsRead": w * h, "cellsRequested": w * h, "ops": ";".join(ops)}

    def t_letter_list(self, **k):
        return {"success": True, "count": len(self.letters), "letters": list(self.letters)}

    def t_map_fire(self, action="start", rect=None, fireSize=0.5, **k):
        rr = V_rect(rect)
        if action == "extinguish":
            self.fires = [f for f in self.fires if not inrect(f[0], f[1], rr)]
            return {"success": True, "firesExtinguished": 0}
        started = 0
        for t in self.of("WoodLog"):
            if inrect(t["x"], t["z"], rr):
                self.fires.append((t["x"], t["z"], self.ticks + 3000))
                started += 1
        return {"success": True, "firesStarted": started}

    def t_designate_batch(self, **k):
        return {"success": True}

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **k):
        self.jobs[pawnId] = ("Harvest", self.ticks + 800, targetAId)
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        lines = []
        if t["def"] == V.THORN:
            g = t["growth"]
            shown = self.on("assayGradeEnabled", "assay_ignores_toggle") and self.on("metalYieldEnabled")
            if shown:
                f = 1.0 if "factor_ignored_assay" in self.broken else self.factor("metalYieldFactor")
                if g < 0.2:
                    lines = ["Assay grade: unripe (no steel yet)"]
                else:
                    tt = (g - 0.2) / 0.8
                    expected = (2 + tt * 10) * f
                    frac = expected / (12 * f)
                    grade = "lode" if frac >= 0.95 else "rich" if frac >= 2 / 3. else "fair" if frac >= 1 / 3. else "trace"
                    if "assay_wrong_grade" in self.broken:
                        grade = "lode"
                    lines = ["Assay grade: %s (~%s steel if cut now)" % (grade, ("%.1f" % expected).rstrip("0").rstrip("."))]
        if t["def"] == V.VENT:
            out = self.vent_output(t)
            if self.vent_silenced(t):
                st = "silenced"
            elif self.vent_recovery(t) < 1.0:
                st = "recovering"
            elif self.vent_mult() == self.FALTER:
                st = "faltering"
            else:
                st = "breathing"
            lines = ["Vent: stable", "Vent state: %s" % st, "Vent output: %.2fx" % out]
            if t["supp"] > 0.01 and st != "silenced":
                lines[-1] += "  (drunk %d%% of the way quiet)" % int(t["supp"] * 100)
        return {"success": True, "things": [{"id": t["id"], "label": t["def"], "inspect": lines}]}


def V_rect(s):
    return rect(s)


# ------------------------------------------------------------------ the runner

def run(broken=()):
    game = Fake(broken)
    results = {}
    real_err = sys.stderr
    sys.stderr = open(os.devnull, "w")             # the suite's per-component progress lines
    try:
        for name, fn in V.suite.chains:
            t = TestContext(game, anchor=(100, 100))
            try:
                fn(t)
            except Exception as ex:            # a chain-level crash is a script bug
                results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
                continue
            for c in t.components:
                results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    finally:
        sys.stderr.close()
        sys.stderr = real_err
    return results


# break -> the component that must go FAIL (and nothing else)
BREAKS = {
    "missing_def": "load.defs_resolve",
    "type_unresolved": "load.types_resolve",
    "stale_dll": "load.types_resolve",
    "stock_weather": "load.biome_weather_table",
    "roster_zeroed": "load.biome_roster",
    "worker_donor": "load.biome_worker_and_terrain",
    "nettle_ext_missing": "load.nettle_habitat_wired",
    "weather_rains": "weather.weather_defs_laws",
    "bloom_toxic_buildup": "weather.weather_defs_laws",
    "weather_not_settable": "weather.weathers_selectable",
    "setting_missing": "settings.defaults",
    "vexxiss_explosive": "items.suush_and_vexxiss_comps",
    "no_zisska_steel": "items.zisska_yields_and_toxic_meat",
    "meat_not_toxic": "items.zisska_yields_and_toxic_meat",
    "kind_missing": "fauna.fauna_spawns",
    "suush_no_fly": "fauna.suush_can_fly",
    "melee_detonates": "suush.suush_ignores_melee",
    "no_detonate": "suush.suush_detonates_when_shot",
    "set_plants_drops": "flora.flora_spawns",
    "assay_wrong_grade": "flora.assay_grades",
    "assay_ignores_toggle": "flora.assay_toggle_off",
    "factor_ignored_assay": "flora.assay_factor_scales",
    "no_metal": "yield.harvest_pays_metal",
    "factor_ignored_yield": "yield.yield_factor_scales",
    "metal_ignores_toggle": "yield.yield_toggle_off",
    "no_exposure": "bloom.bloom_loads_exposed",
    "double_tax": "bloom.bloom_no_double_tax",
    "exposure_ignores_roof": "bloom.bloom_spares_roofed",
    "exposure_hits_natives": "bloom.bloom_spares_natives",
    "bloom_ignores_toggle": "bloom.bloom_toggle_off",
    "factor_ignored_bloom": "bloom.bloom_factor_scales",
    "no_poison": "water.water_poison_on",
    "no_letter": "water.water_letter_arrives",
    "no_cooldown": "water.water_letter_cooldown",
    "letter_ignores_toggle": "water.water_letter_toggle_off",
    "poison_ignores_toggle": "water.water_poison_toggle_off",
    "no_warden": "fire.fire_warden_beats_fire",
    "warden_ignores_toggle": "fire.fire_warden_toggle_off",
    "vent_ext_missing": "load.vent_habitat_wired",
    "weather_mult_flat": "vents.vent_weather_multiplier",
    "weather_ignores_toggle": "vents.vent_weather_multiplier",
    "no_falter": "vents.vent_falter_precedes_bloom",
    "exposure_not_local": "vents.vent_exposure_is_local",
    "local_ignores_toggle": "vents.vent_exposure_is_local",
    "no_drink": "vents.vexxiss_drinks_vent",
    "drink_ignores_toggle": "vents.vexxiss_drinks_vent",
    "never_silences": "vents.vent_silences_and_recovers",
    "no_recovery": "vents.vent_silences_and_recovers",
    "log_error": "log.log_clean",
}

# A few breaks cascade by design: the component named is the FIRST red, later ones are UNMEASURED
# (not FAIL), which the runner records separately -- so only FAIL/CRASH are compared.


def source_checks():
    """The script must not drift from the mod's own source."""
    bad = []
    srcdir = os.path.join(HERE, "Source")
    blob = ""
    for fn in sorted(os.listdir(srcdir)):
        if fn.endswith(".cs"):
            with open(os.path.join(srcdir, fn), encoding="utf-8") as fh:
                blob += fh.read()
    for typ in V.TYPES:
        short = typ.rsplit(".", 1)[1]
        if not re.search(r"\bclass\s+%s\b" % short, blob):
            bad.append("TYPES names %s but Source/ declares no such class" % short)
    if len(V.DEFAULTS) != 18 or sum(1 for v in V.DEFAULTS.values() if isinstance(v, bool)) != 14:
        bad.append("parsed %d defaults / %d bools, expected 18 / 14" %
                   (len(V.DEFAULTS), sum(1 for v in V.DEFAULTS.values() if isinstance(v, bool))))
    for f in V.DEFAULTS:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), blob):
            bad.append("Mod Settings field %s is not scribed in ExposeData" % f)
    if len(V.SHIPPED) != 31 or len(V.FLORA) != 11 or len(V.KINDS) != 4:
        bad.append("def census drifted: %d shipped / %d flora / %d kinds (expected 31 / 11 / 4); update "
                   "the walk and this selftest together" % (len(V.SHIPPED), len(V.FLORA), len(V.KINDS)))
    return bad


def main():
    bad = source_checks()
    healthy = run()
    notpass = dict((k, v) for k, v in healthy.items() if v[0] != "PASS")
    n_comp = len(healthy)
    if notpass:
        bad.append("healthy run: %d of %d components not PASS: %s" % (len(notpass), n_comp, notpass))
    declared = len(V.suite.components_declared())
    if declared != n_comp:
        bad.append("declared %d components but the run produced %d" % (declared, n_comp))
    covered = set(c["toggle"] for c in V.suite.components_declared() if c["toggle"])
    if sorted(set(V.suite.toggles) - covered):
        bad.append("toggles with no component: %s" % sorted(set(V.suite.toggles) - covered))
    # every component must be proven able to fail by at least one break (except the site-setup ones)
    targeted = set(BREAKS.values())
    unproven = sorted(k for k in healthy if k not in targeted and not k.endswith("_site_ready")
                      and not k.endswith("_roundtrip"))
    if unproven:
        bad.append("components no break turns red (never seen failing): %s" % unproven)
    for brk, target in sorted(BREAKS.items()):
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != [target]:
            bad.append("break %-22s expected only %s FAIL, got %s" % (brk, target, reds))
    print("selftest Cauldron: %d components, healthy-PASS %d/%d; %d breaks, each turning exactly its own "
          "component red" % (n_comp, n_comp - len(notpass), n_comp,
                             len(BREAKS) - len([1 for b in bad if b.startswith("break ")])))
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
