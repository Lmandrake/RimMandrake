#!/usr/bin/env python3
"""Offline selftest for Contagion's validation.py: a scripted FAKE GAME that implements the mod's
behaviours (read off the C# in Source/ and the XML in Defs/), run (1) healthy -- every component must
PASS -- and (2) once per mod behaviour broken -- the named component must go FAIL and no other
component may.

That second half is the proof every check can fail: each break is a mod defect (a gate that ignores its
toggle, an effect that never fires, a patch that matched nothing) and the suite must see it.
The fake encodes the response SHAPES validation.py assumes (read off the JawaBench [Tool]
descriptions); it proves the predicates and wiring, not the shapes -- those are UNPROVEN until the
first live run (the walk lists them).

    python3 src/RimMandrake/Contagion/selftest_contagion.py
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

spec = importlib.util.spec_from_file_location("contagion_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait poll loop must not really sleep

from suite import TestContext                     # noqa: E402

_NULL = open(os.devnull, 'w')

NATIVES = set(V.WILD_ANIMALS) | {"RM_TheUnfinished"}
ARMORED = {"RM_Scaldhide", "RM_Crispling"}
LEAKERS = {"RM_Scorchpod"}
ORGANS = ["Kidney", "Liver", "Lung", "Heart", "RM_GrownLeg", "RM_GrownArm"]


def rect(s):
    return [int(v) for v in str(s).replace(";", ",").split(",")][:4]


def inrect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class Fake(object):
    def __init__(self, broken=(), start_biome="TemperateForest"):
        self.broken = set(broken)
        self.retiles = []
        self.ticks = 1000
        self.fast = False
        self.n = 0
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        if "setting_missing" in self.broken:
            del self.settings["coalescenceEnabled"]
        if "default_wrong" in self.broken:
            self.settings["burnFrequency"] = "2.0"
        self.weather, self.biome = "Clear", start_biome
        self.things, self.pawns, self.conds, self.roofs = {}, {}, [], []
        # SITE model of the round-4 quicktest tile (LIVE 2026-10-16, Mountainous): the whole map lies under an overhead
        # mountain roof. Clearing a pad (destroy_batch All) removes the roof holders, and on the next tick every cell of
        # it still roofed collapses and crushes what stands there (RoofCollapserImmediate: 99999 Crush). Only cells the
        # harness unroofed ('None:' set_roof_batch ops) are open sky.
        self.open_sky, self.collapse_pending, self.host_gone = [], [], False
        self.next_burn, self.bills = -1, set()

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

    def on(self, f):
        return self.settings.get(f) == "True"

    def num(self, f):
        return float(self.settings[f])

    def newid(self, p):
        self.n += 1
        return "%s%d" % (p, self.n)

    def new(self, d, x, z, **kw):
        tid = self.newid("T")
        self.things[tid] = dict(id=tid, x=x, z=z, stackCount=1, **dict(kw, **{"def": d}))
        return tid

    def of(self, *defs):
        return [t for t in self.things.values() if t["def"] in defs]

    def pawn(self, kind, x, z, faction):
        pid = self.newid("P")
        p = dict(id=pid, kind=kind, x=x, z=z, faction=faction, dead=False, hed=[], inv=[], mental=None,
                 vanished=False)
        self.pawns[pid] = p
        if kind == "RM_TheUnfinished":
            if "no_limbs" not in self.broken:
                for h in V.LIMB_POOL[:2]:
                    self.addh(p, h, 0.1)
            if "no_lifespan" not in self.broken:
                self.addh(p, "RM_UnfinishedUnraveling", 0.2)
        if kind == V.HOST:
            p["next_spawn"] = self.ticks + 36000
        return p

    def addh(self, p, d, sev):
        for h in p["hed"]:
            if h["def"] == d:
                h["severity"] += sev
                return h
        h = {"def": d, "severity": sev}
        p["hed"].append(h)
        return h

    def is_native(self, p):
        return p["kind"] in NATIVES

    def exposed(self, x, z):
        return any(inrect(x, z, r) for r in self.open_sky) and not any(inrect(x, z, r) for r in self.roofs)

    def roofed_by_mountain(self, x, z):
        return not any(inrect(x, z, r) for r in self.open_sky)

    def resolve_collapse(self):
        for rr in self.collapse_pending:
            for p in self.pawns.values():
                if not p["vanished"] and inrect(p["x"], p["z"], rr) and self.roofed_by_mountain(p["x"], p["z"]):
                    p["vanished"] = p["crushed"] = True       # a crushed pawn is a corpse: gone from list_pawns
            for tid in [i for i, t in self.things.items()
                        if inrect(t["x"], t["z"], rr) and self.roofed_by_mountain(t["x"], t["z"])]:
                del self.things[tid]
        self.collapse_pending = []

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            self.ticks += d
            self.resolve_collapse()
            for p in self.pawns.values():         # a patient ordered to its bed arrives on a later tick
                if p.get("walk_to") and not p["vanished"]:
                    p["x"], p["z"] = p.pop("walk_to")
            self.step()

    def cond(self, name):
        for c in self.conds:
            if c["def"] == name:
                return c
        return None

    def start_cond(self, name, dur):
        c = self.cond(name)
        if c:
            c["until"] = max(c["until"], self.ticks + dur)
            return c
        c = {"def": name, "start": self.ticks, "until": self.ticks + dur}
        self.conds.append(c)
        return c

    def step(self):
        b = self.broken
        contagion = self.biome == V.BIOME
        # --- Contagion-touched by contact (RM_MapComponent_ContagionTouch): a colonist on or beside a Coalescence
        if (self.on("touchedEnabled") or "touched_ignores_toggle" in b) and "touched_no_contact" not in b:
            for c in self.of(V.COALESCENCE):
                for p in self.pawns.values():
                    if p["kind"] == "Colonist" and not p["dead"] and not p["vanished"] \
                            and (("touched_bloom_only" in b) or (abs(p["x"] - c["x"]) <= 2 and abs(p["z"] - c["z"]) <= 2)):
                        self.addh(p, V.TOUCHED, 0.01)
        # --- the zhool's haze (CompZhoolHaze): one grass in reach turns per 250-tick step, on our biome only
        for z in [q for q in self.pawns.values() if q["kind"] == V.ZHOOL and not q["dead"] and not q["vanished"]]:
            on = self.on("zhoolConversionEnabled") or "haze_ignores_toggle" in b
            if not contagion or not on or "haze_no_convert" in b:
                continue
            for g in self.of(V.GRASS):
                if abs(g["x"] - z["x"]) <= 3 and abs(g["z"] - z["z"]) <= 3:
                    del self.things[g["id"]]
                    if "haze_deletes" not in b:
                        self.new(V.LASHGRASS, g["x"], g["z"])
                    break
        self.conds = [c for c in self.conds if self.ticks <= c["until"]]
        # --- the Cloud Repulsor
        for r in self.of(V.REPULSOR):
            enabled = self.on("cloudRepulsorEnabled") or "rep_ignores_toggle" in b
            if not enabled or not r.get("power"):
                r["warm"] = 0
                continue
            if r["warm"] < 2500:
                r["warm"] += 250
                continue
            if contagion:
                if "no_force_burn" not in b:
                    self.start_cond(V.BURN_COND, 750)
            elif "rep_no_clear" not in b:
                self.start_cond(V.CLEAR_COND, 750)
                if "rep_forces_burn_offbiome" in b:
                    self.start_cond(V.BURN_COND, 750)
            if "rep_sticky" in b and not contagion:
                self.start_cond(V.CLEAR_COND, 10 ** 9)
        # --- the sky clock (Contagion maps only)
        burn = self.cond(V.BURN_COND)
        if contagion:
            if burn:
                self.next_burn = -1
            else:
                on = self.on("burnEnabled") or "sched_ignores_toggle" in b
                if not on:
                    self.next_burn = -1
                elif self.next_burn < 0:
                    freq = 1.0 if "freq_ignored" in b else max(0.05, self.num("burnFrequency"))
                    self.next_burn = self.ticks + int(3 * 60000 / freq)
                elif self.ticks >= self.next_burn and "no_schedule" not in b:
                    self.start_cond(V.BURN_COND, 2000)
                    self.next_burn = -1
        burn = self.cond(V.BURN_COND)
        # --- weather the Burn forces
        if contagion and burn and self.ticks - burn["start"] >= 600:
            self.weather = "Clear" if "weather_not_burn" in b else V.BURN_WEATHER
        elif self.weather == V.BURN_WEATHER:
            self.weather = "RM_ContagionBloom"
        # --- Burn pressure on everything exposed
        if contagion and burn and self.weather == V.BURN_WEATHER and \
                (self.on("burnEnabled") or "harm_ignores_burn_toggle" in b):
            f = self.num("burnDamageFactor")
            if f > 0 or "zero_dmg_hurts" in b:
                for p in list(self.pawns.values()):
                    if p["dead"] or p["vanished"] or not self.exposed(p["x"], p["z"]):
                        continue
                    if self.is_native(p):
                        if p["kind"] in ARMORED and "armored_hurt" not in b:
                            continue
                        if "native_unhurt" not in b:
                            self.addh(p, "Burn", 3 * max(f, 0.5))
                        if p["kind"] not in LEAKERS and p["kind"] not in ARMORED and "no_dive" not in b and "wander_onto_patch" not in b:
                            roof = self.roofs[0]
                            p["x"], p["z"] = roof[0] + 2, roof[1] + 2
                            p["job"], p["job_t"] = "Goto", (roof[0] + 2, roof[1] + 2)   # the dive is a Goto to a roofed cell
                    elif "no_dose" not in b:
                        self.addh(p, "RM_BurnDose", 0.02 * max(f, 0.5))
            if "dose_roofed" in b:
                for p in self.pawns.values():
                    if p["kind"] == "Colonist" and not self.exposed(p["x"], p["z"]):
                        self.addh(p, "RM_BurnDose", 0.02)
        # --- the spawner (the host's own comp)
        for p in list(self.pawns.values()):
            if p["kind"] == V.HOST and not p["dead"] and not p["vanished"] and "next_spawn" in p:
                gate = self.on("unfinishedSpawnerEnabled") or "spawner_ignores_toggle" in b
                if gate and self.ticks >= p["next_spawn"] and "no_bud" not in b:
                    near = [q for q in self.pawns.values() if q["kind"] == "RM_TheUnfinished"
                            and abs(q["x"] - p["x"]) <= 20 and abs(q["z"] - p["z"]) <= 20
                            and not q["vanished"]]
                    if len(near) < 3 or "spawner_no_cap" in b:
                        for _ in range(4 if "spawner_no_cap" in b else 1):
                            self.pawn("RM_TheUnfinished", p["x"] + 1, p["z"], "none")
                    p["next_spawn"] = self.ticks + 36000
        # --- lifespans and gestation
        for p in list(self.pawns.values()):
            for h in list(p["hed"]):
                if h["def"] == "RM_UnfinishedUnraveling":
                    h["severity"] += 0.3 * 250 / 60000.0
                    if h["severity"] >= 1.0:
                        self.die(p)
                if h["def"] == "RM_AmoebaGestation":
                    h["severity"] += 0.25 * 250 / 60000.0
                    if h["severity"] >= 0.999:
                        self.complete_gestation(p, h)
        # --- the Coalescence
        for c in self.of(V.COALESCENCE):
            if self.cond(V.BURN_COND) and "no_collapse" not in b:
                self.collapse(c)
                continue
            if not (self.on("coalescenceEnabled") or "coal_ignores_toggle" in b):
                continue
            if self.ticks - c["last_growth"] >= 6000 and "no_passive" not in b:
                c["last_growth"] = self.ticks
                c["mass"] += 1
            # Building_RM_Coalescence.Absorb, per 250-tick pass: one inside the ring (footprint expanded by 1)
            # is eaten; one further out is ordered a step closer and eaten on a LATER pass. "slow_walkers"
            # (impaired Unfinished, live 2026-10-08) take three passes per step: the harness must still PASS.
            for p in list(self.pawns.values()):
                if p["kind"] == "RM_TheUnfinished" and not p["vanished"] and not p["mental"] \
                        and "no_absorb" not in b and abs(p["x"] - c["x"]) <= 18 and abs(p["z"] - c["z"]) <= 18:
                    if abs(p["x"] - c["x"]) <= 2 and abs(p["z"] - c["z"]) <= 2:
                        p["vanished"] = True
                        c["mass"] += 1
                    elif "slow_walkers" in b and p.setdefault("walk", 0) < 2:
                        p["walk"] += 1
                    else:
                        p["walk"] = 0
                        p["x"] += (c["x"] > p["x"]) - (c["x"] < p["x"])
                        p["z"] += (c["z"] > p["z"]) - (c["z"] < p["z"])
            st = self.stage(c)
            if self.ticks - c["last_emit"] >= (5000, 3000, 1800)[st] and "no_passive" not in b:
                c["last_emit"] = self.ticks
                live = [q for q in self.pawns.values() if q["kind"] == "RM_TheUnfinished" and q["mental"]]
                if len(live) < (2, 4, 6)[st]:
                    q = self.pawn("RM_TheUnfinished", c["x"] + 2, c["z"], "none")
                    q["mental"] = "Manhunter"

    def stage(self, c):
        s = 0
        for i, m in enumerate(V.STAGE_MASS):
            if c["mass"] >= m:
                s = i
        return s

    def die(self, p):
        if "corpse_persists" in self.broken:
            p["dead"] = True
            self.new("Corpse_" + p["kind"], p["x"], p["z"])
        else:
            p["vanished"] = True
        # DeathActionWorker_RM_VanishToMulch: a dead Unfinished leaves mulch
        if p["kind"] == V.UNFINISHED and self.on("mulchDropsEnabled") and "mulch_none" not in self.broken:
            self.new(V.MULCH, p["x"], p["z"])

    def collapse(self, c):
        st = self.stage(c)
        n = min(V.SAMPLES_MAX, V.SAMPLES_BASE + V.SAMPLES_PER_STAGE * st + c["mass"] // V.MASS_PER_SAMPLE)
        if "wrong_samples" in self.broken:
            n += 1
        del self.things[c["id"]]
        for _ in range(n):
            self.new(V.SAMPLE, c["x"] + 1, c["z"] + 1, monstrous="samples_not_monstrous" not in self.broken)

    def complete_gestation(self, p, h):
        if "host_survives" not in self.broken:
            p["vanished"] = True
        p["hed"].remove(h)
        x, z = p["x"], p["z"]
        if h.get("monstrous") and (self.on("grownLimbsEnabled") or "limbs_ignore_toggle" in self.broken) \
                and "monstrous_organs" not in self.broken:
            self.new(V.LIMB_ITEMS[0], x, z)
            return
        n = 1 if "organ_count" in self.broken else 3
        for i in range(n):
            self.new(ORGANS[i], x, z + 1)

    # ------------------------------------------------------------ tools
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_set_time_speed(self, speed=None, **k):
        self.fast = speed == "Ultrafast"
        return {"success": True}

    def t_time_set_ticks(self, ticks=0, **k):
        if "jump_noop" in self.broken:            # a no-op jump whose reply carries no ticksGameAfter
            return {"success": True}
        self.ticks = int(ticks)
        return {"success": True, "ticksGameAfter": self.ticks}

    def t_weather_set(self, weather=None, **k):
        if weather:
            self.weather = weather
        return {"success": True}

    def t_weather_get(self, **k):
        return {"success": True, "weather": {"current": self.weather}}

    def t_mod_settings_field(self, typeName=None, action=None, field=None, value=None, **k):
        if field not in self.settings:
            return {"success": False, "message": "no such field"}
        if action == "set":
            self.settings[field] = str(value)
        return {"success": True, "value": self.settings[field]}

    def t_get_defs(self, defs="", fields=None, limit=200, **k):
        want = [d for d in defs.split(";") if d]
        if want == ["BiomeDef/" + V.BIOME]:
            tab = [{"weather": "RM_ContagionBloom", "commonality": 70}, {"weather": "Rain", "commonality": 2}]
            if "burn_in_table" in self.broken:
                tab.append({"weather": V.BURN_WEATHER, "commonality": 1})
            ext = [] if "no_sky_ext" in self.broken else ["RimMandrake.Contagion.RM_ContagionSkyExtension"]
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": V.BIOME, "fields": {
                "baseWeatherCommonalities": tab, "animalDensity": 3.0, "modExtensions": ext,
                "wildAnimals": [{"animal": a, "commonality": 1} for a in V.WILD_ANIMALS],
                "wildPlants": [{"plant": a, "commonality": 1} for a in V.WILD_PLANTS]}}]}
        if want == ["ThingDef/RM_Rattlegrope", "ThingDef/RM_Gawpsack"]:
            tc = "Plant" if "tells_unwired" in self.broken else "RimMandrake.Contagion.RM_Plant_Rattlegrope"
            return {"success": True, "foundCount": 2, "notFound": [], "defs": [
                {"defName": "RM_Rattlegrope", "fields": {"thingClass": tc, "drawerType": "MapMeshAndRealTime"}},
                {"defName": "RM_Gawpsack", "fields": {"race": {"renderTree": "RM_GawpsackSink"}}}]}
        if want == ["FactionDef/" + V.HELIX_FACTION]:
            kinds = ["Caravan_Outlander_BulkGoods"] + ([] if "helix_trader_unwired" in self.broken else [V.HELIX_TRADER])
            return {"success": True, "foundCount": 1, "notFound": [], "defs": [{"defName": V.HELIX_FACTION,
                                                                                 "fields": {"caravanTraderKinds": kinds}}]}
        missing = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if "missing_def" in self.broken and want and want[0] in V.SHIPPED:
            missing.append(want[3])
        return {"success": True, "notFound": missing, "foundCount": len(want) - len(missing)}

    def t_get_def(self, defName=None, **k):
        comps = [{"class": "CompProperties_Forbiddable"}]
        if "organ_unpatched" not in self.broken or defName != "Liver":
            comps.append({"class": "RimMandrake.Contagion.CompProperties_GenomeMatched"})
        return {"success": True, "comps": comps}

    def t_map_info(self, **k):
        return {"success": True, "tile": 77, "tileValid": True, "mapBiome": self.biome,
                "sizeX": 250, "sizeZ": 250}

    def t_world_tile_set(self, biome=None, **k):
        self.retiles.append(biome)
        if "retile_noop" not in self.broken:
            self.biome = biome
        return {"success": True, "written": 1}

    def t_site_state(self, **k):
        return {"success": True, "conditions": {"map": [{"def": c["def"], "ticksLeft": c["until"] - self.ticks}
                                                        for c in self.conds], "world": []},
                "pawns": [{"id": p["id"], "job": "Wait_Wander"} for p in self.pawns.values()]}

    def t_game_condition(self, action="start", condition=None, durationTicks=0, **k):
        if action == "start":
            self.start_cond(condition, durationTicks or 60000)
            return {"success": True}
        c = self.cond(condition)
        if not c:
            return {"success": False, "message": "not active"}
        self.conds.remove(c)
        return {"success": True}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = rect(rects)
        bldg = (V.REPULSOR, V.COALESCENCE, "Bed")
        if "Pawn" in str(categories):    # live: refused; and no category ever removes a pawn
            return {"success": False, "message": "destroy_batch never removes pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1)"}
        for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)
                    and (categories == "All" or t["def"] not in bldg)]:
            del self.things[tid]
        self.roofs = [r for r in self.roofs if not (inrect(r[0], r[1], rr))]
        if categories == "All":
            # the rock that held the mountain roof is gone: support is lost up to ~6.9 cells beyond the cleared rect
            m = V.ROOF_MARGIN
            self.collapse_pending.append([rr[0] - m, rr[1] - m, rr[2] + 2 * m, rr[3] + 2 * m])
        return {"success": True}

    def t_pawn_force_incapacitate(self, pawn=None, action=None, **k):
        p = self.pawns.get(pawn)
        if p is None or p["vanished"]:
            return {"success": False}
        if action == "vanish":
            p["vanished"] = True
        else:
            self.die(p)
        return {"success": True}

    def t_get_roof_batch(self, rects="", **k):
        # the live tool's shape: one roof defName (or "None") per cell, row by row (validation reads roofs[0])
        out = []
        for r in rects.split(";"):
            rr = rect(r)
            for z in range(rr[1], rr[1] + rr[3]):
                for x in range(rr[0], rr[0] + rr[2]):
                    out.append("RoofConstructed" if any(inrect(x, z, q) for q in self.roofs) else "None")
        return {"success": True, "roofs": out}

    def t_set_roof_batch(self, ops="", **k):
        n = 0
        for op in ops.split(";"):
            name, rr = op.split(":")[0], rect(op.split(":")[1])
            n += rr[2] * rr[3]
            if name in ("None", "Clear"):
                if "unroof_noop" not in self.broken:
                    self.open_sky.append(rr)
                    self.roofs = [r for r in self.roofs if not inrect(r[0], r[1], rr)]
            elif "roof_patch_fails" in self.broken:
                return {"success": True, "cellsChanged": 0, "cellsFailedVerify": 0}
            else:
                self.roofs.append(rr)
        return {"success": True, "cellsChanged": n, "cellsFailedVerify": 0}

    def t_spawn_batch(self, ops="", **k):
        for op in ops.split(";"):
            d, nums = op.split(":")
            n = [int(v) for v in nums.split(",")]
            if d == V.REPULSOR:
                self.new(d, n[0], n[1], power=False, warm=0)
            elif d == V.COALESCENCE:
                self.new(d, n[0], n[1], mass=0, last_growth=self.ticks, last_emit=self.ticks)
            elif d == V.SAMPLE:
                self.new(d, n[0], n[1], monstrous=False)
            else:
                self.new(d, n[0], n[1])
        return {"success": True}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = globals()["rect"](rect) if rect else None
        want = set((defName or "").split(","))
        rows = [t for t in self.things.values() if t["def"] in want and (not rr or inrect(t["x"], t["z"], rr))]
        return {"success": True, "scanned": 100, "countMatched": len(rows), "isCompleteList": True,
                "things": [dict(t) for t in rows[:limit]]}

    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", **k):
        p = self.pawn(kindDef, x, z, faction)
        if kindDef == V.HOST and "host_vanishes" in self.broken and not self.host_gone:
            self.host_gone = True
            p["vanished"] = True                  # SITE: the spawner's host is gone before the arms read it
        return {"success": True, "pawns": [{"id": p["id"]}]}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, **k):
        rr = globals()["rect"](rect) if rect else None
        rows = []
        if "armored_wanders_off" in self.broken:      # SITE: an armored native walks off under the mountain roof
            for p in self.pawns.values():
                if p["kind"] in ARMORED and not p["vanished"]:
                    p["x"], p["z"] = p["x"] - 40, p["z"]
        for p in self.pawns.values():
            if p["vanished"] or (rr and not inrect(p["x"], p["z"], rr)):
                continue
            row = {"id": p["id"], "kind": p["kind"], "kindDef": p["kind"], "x": p["x"], "z": p["z"],
                   "dead": p["dead"]}
            if includeHealth:
                row["health"] = {"hediffs": [dict(h) for h in p["hed"]]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_pawn_get(self, pawn=None, **k):
        # The real jawa/pawn_get carries NO mental-state field (live 2026-10-08); the mock used to invent
        # one, which is how a validation that could never pass live passed here.
        return {"success": True, "pawns": [{"thingId": pawn}]}

    def t_pawn_mental(self, pawn=None, action="list", **k):
        return {"success": True, "action": action, "currentState": self.pawns[pawn]["mental"] or None}

    def t_set_draft(self, **k):
        return {"success": True}

    def t_order_pawn(self, pawnId=None, x=None, z=None, waitTicks=0, **k):
        # The real tool runs the clock for waitTicks while the pawn walks (live 2026-10-08: a visitor walked
        # 200 ticks under the Burn and was dosed before the toggle it was meant to test went off).
        self.advance(int(waitTicks or 0))
        self.pawns[pawnId]["x"], self.pawns[pawnId]["z"] = x, z
        return {"success": True}

    def t_power_net(self, thing=None, forcePowerOn=None, **k):
        t = self.things[thing]
        if forcePowerOn is not None:
            t["power"] = bool(forcePowerOn)
        return {"success": True, "powerOnAfter": t.get("power", False)}

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        d, lines = t["def"], []
        if d == V.REPULSOR:
            if not (self.on("cloudRepulsorEnabled") or "rep_ignores_toggle" in self.broken):
                lines = ["Disabled in Mod Settings."]
            elif not t.get("power"):
                lines = ["Unpowered."]
            elif t["warm"] < 2500:
                lines = ["Warming up: 1 hour"]
            elif self.biome == V.BIOME:
                lines = ["Holding the storm open: the Burn is forced."]
            else:
                lines = ["Holding the sky clear."]
        elif d == V.COALESCENCE:
            lines = ["Stage %d, absorbed mass %d." % (self.stage(t) + 1, t["mass"])]
        elif d == V.SAMPLE:
            lines = ["Grade: Monstrous (grows a single limb, unmatched to anyone)"] if t.get("monstrous") \
                else (["Genome source: %s" % t["source"]] if t.get("source") else [])
        return {"success": True, "things": [{"id": t["id"], "label": d, "inspect": lines}]}

    def t_set_pawn_skill(self, **k):
        return {"success": True}

    def t_damage(self, damageDef=None, amount=5, thingId=None, **k):
        p = self.pawns[thingId]
        f = self.num("sunbeamNativeFactor")
        if (self.is_native(p) and f > 1 and "uv_no_multiplier" not in self.broken) or \
                "uv_person_multiplied" in self.broken:
            amount = amount * f
        self.addh(p, "RM_UVSunburn", amount)
        # DamageWorker_RM_UV: a landed Sunbeam hit arrests Contagion-touched
        if damageDef == "RM_UVBeam" and (self.on("sunbeamArrestEnabled") or "arrest_ignores_toggle" in self.broken) \
                and "arrest_ignored" not in self.broken:
            p["hed"] = [h for h in p["hed"] if h["def"] != V.TOUCHED]
        return {"success": True}

    def t_pawn_severity_adjust(self, pawn=None, hediff=None, offset=0, **k):
        p = self.pawns[pawn]
        h = self.addh(p, hediff, offset) if not any(x["def"] == hediff for x in p["hed"]) \
            else self.addh(p, hediff, offset)
        if hediff == "RM_UnfinishedUnraveling" and h["severity"] >= 1.0:
            self.die(p)
        if hediff == "RM_AmoebaGestation" and h["severity"] >= 0.999:
            self.complete_gestation(p, h)
        return {"success": True, "severityChanged": True}

    def t_bill_add(self, giverId=None, recipe=None, **k):
        self.bills.add(giverId)
        # live (2026-10-16): a surgery on a pawn is made as a Bill_Medical
        return {"success": True, "billClass": "Bill_Medical"}

    def t_bill_list(self, thingId=None, **k):
        return {"success": True, "bills": [{"recipeDefName": "RM_ExtractGenomeSample"}] if thingId in self.bills else []}

    def t_do_bill_now(self, billGiverId=None, pawnId=None, **k):
        pat = self.pawns.get(billGiverId)
        if pat and not any(b["x"] == pat["x"] and b["z"] == pat["z"] for b in self.of("Bed")):
            # live: a surgery's giver is the patient, usable only while it lies IN the bed
            return {"success": False, "message": "WorkGiver_DoBill.JobOnThing(forced:true) returned null.",
                    "details": {"usableAfterFueling": False}}
        if billGiverId in self.bills:
            self.bills.discard(billGiverId)
            self.pawns[pawnId]["job"] = "DoBill"
            p = self.pawns[billGiverId]
            if self.on("genomeOrganGrowingEnabled") and "extract_nothing" not in self.broken:
                self.new(V.SAMPLE, p["x"] + 1, p["z"], monstrous=False, source="Patient")
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_inventory_transfer(self, pawn=None, mode=None, thing=None, **k):
        t = self.things.pop(thing, None)
        if t is None:
            return {"success": True, "movedCount": 0}
        self.pawns[pawn]["inv"].append(t)
        return {"success": True, "movedCount": 1}

    def t_pawn_census(self, ids="", **k):
        # job is the pawn's CURRENT job; the fake's jobs finish instantly, so only a lying patient has one
        rows = []
        for pid in str(ids).split(","):
            p = self.pawns.get(pid)
            if p is None:
                return {"success": False, "message": "no pawn %s" % pid}
            if self.is_native(p) and not p["dead"] and self.roofs and p["kind"] not in ARMORED:
                roof = self.roofs[0]
                if "wander_onto_patch" in self.broken and not p.get("job"):
                    # a native that WANDERS onto the patch (GotoWander) with no Burn order: standing there is not a dive
                    p["x"], p["z"] = roof[0] + 2, roof[1] + 2
                    p["wander"] = True
                if "dive_without_burn" in self.broken and not self.cond(V.BURN_COND):
                    p["job"], p["job_t"] = "Goto", (roof[0] + 2, roof[1] + 2)   # ordered to the roof with NO Burn
            job = None
            if p.get("job"):
                job = {"def": p["job"]}
                if p.get("job_t"):
                    job["targetA"] = {"thingId": None, "x": p["job_t"][0], "z": p["job_t"][1]}
            elif p.get("wander"):
                job = {"def": "GotoWander", "targetA": {"thingId": None, "x": p["x"], "z": p["z"]}}
            rows.append({"id": pid, "x": p["x"], "z": p["z"], "dead": p["dead"], "downed": False,
                         "inMentalState": bool(p["mental"]), "job": job})
            if p.get("job") == "DoBill":
                p["job"] = None              # the fake surgery is seen running once, then it is over
        return {"success": True, "pawns": rows}

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **k):
        if jobDef == "LayDown" and "patient_wont_lie" not in self.broken:
            bed = self.things.get(targetAId)
            if bed:
                p = self.pawns[pawnId]
                if "patient_walks_to_bed" in self.broken:
                    # LIVE 2026-10-16: the patient is read beside the bed, still walking, before it lies down
                    p["job"], p["x"], p["z"], p["walk_to"] = "LayDown", bed["x"] + 1, bed["z"] - 1, (bed["x"], bed["z"])
                else:
                    p["job"], p["x"], p["z"] = "LayDown", bed["x"], bed["z"]
        if jobDef == "RM_InjectGenomeSample":
            doer, host = self.pawns[pawnId], self.pawns.get(targetAId)
            if doer["inv"] and host and host["kind"] == V.HOST and "no_gestation" not in self.broken:
                s = doer["inv"].pop(0)
                h = self.addh(host, "RM_AmoebaGestation", 0.001)
                h["monstrous"] = bool(s.get("monstrous"))
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=1, **k):
        msgs = []
        if "log_error" in self.broken and contains == "Contagion":
            msgs = [{"text": "RM_Contagion: Could not resolve"}]
        if "xref_error" in self.broken and contains == "cross-reference":
            msgs = [{"text": "Could not resolve cross-reference to Verse.ThingDef named %s" % V.MULCH}]
        if "xref_flood" in self.broken and contains == "cross-reference":
            msgs = [{"text": "Could not resolve cross-reference to Verse.ThingDef named OtherMod_%d" % i} for i in range(100)]
        return {"success": True, "totalInBuffer": 100, "messages": msgs}


# ------------------------------------------------------------------ the runner

def run(broken=(), start_biome="TemperateForest", out=None):
    sys.stderr, keep = _NULL, sys.stderr
    try:
        return _run(broken, start_biome, out)
    finally:
        sys.stderr = keep


def _run(broken=(), start_biome="TemperateForest", out=None):
    game = Fake(broken, start_biome)
    if out is not None:
        out.append(game)
    V._STATE.clear()
    results = {}
    for name, fn in V.suite.chains:
        t = TestContext(game, anchor=(150, 150))
        try:
            fn(t)
        except Exception as ex:            # a chain-level crash is a script bug
            results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
            continue
        for c in t.components:
            results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return results


# break -> the component(s) that must go FAIL (and nothing else)
BREAKS = {
    "missing_def": ["defs.defs_resolve"],
    "burn_in_table": ["defs.biome_table_and_roster"],
    "no_sky_ext": ["defs.biome_table_and_roster"],
    "organ_unpatched": ["defs.organ_patch_comps"],
    "setting_missing": ["settings.defaults", "settings_coalescenceEnabled.coalescenceEnabled_roundtrip",
                        "coalescence.coalescence_off_absorbs_nothing", "touched.touched_site_ready"],
    "default_wrong": ["settings.defaults"],
    "rep_ignores_toggle": ["repulsor_clear.off_when_setting_off", "burn_forced.repulsor_off_lapses_burn"],
    "rep_no_clear": ["repulsor_clear.holds_sky_clear"],
    "rep_forces_burn_offbiome": ["repulsor_clear.holds_sky_clear"],
    "rep_sticky": ["repulsor_clear.lapses_without_power"],
    "spawner_ignores_toggle": ["spawner.spawner_off_buds_nothing"],
    "no_bud": ["spawner.spawner_buds_unfinished"],
    "spawner_no_cap": ["spawner.spawner_buds_unfinished"],
    "no_limbs": ["spawner.unfinished_rolls_limbs_and_lifespan"],
    "no_lifespan": ["spawner.unfinished_rolls_limbs_and_lifespan"],
    "corpse_persists": ["spawner.unfinished_dissolves_on_death"],
    "retile_noop": ["site.retile_to_contagion"],
    "no_force_burn": ["burn_forced.repulsor_forces_burn"],
    "weather_not_burn": ["burn_forced.repulsor_forces_burn"],
    "zero_dmg_hurts": ["burn_forced.burn_harmless_at_zero_damage"],
    "no_dose": ["burn_forced.burn_doses_the_exposed_visitor"],
    "dose_roofed": ["burn_forced.burn_doses_the_exposed_visitor"],
    "native_unhurt": ["burn_forced.burn_hurts_native_spares_armored"],
    "armored_hurt": ["burn_forced.burn_hurts_native_spares_armored"],
    "no_dive": ["burn_forced.native_dives_for_roof"],
    "wander_onto_patch": ["burn_forced.native_dives_for_roof"],   # stands on the patch via GotoWander, never ordered: position alone passed this
    "dive_without_burn": ["burn_forced.native_no_dive_without_burn"],
    "harm_ignores_burn_toggle": ["burn_forced.burn_off_means_no_harm"],
    "sched_ignores_toggle": ["burn_natural.burn_off_never_schedules"],
    "freq_ignored": ["burn_natural.slow_frequency_defers_burn"],
    "no_schedule": ["burn_natural.natural_burn_arrives_on_schedule"],
    "uv_no_multiplier": ["uv.uv_native_multiplier"],
    "uv_person_multiplied": ["uv.uv_native_multiplier"],
    "coal_ignores_toggle": ["coalescence.coalescence_off_absorbs_nothing"],
    "no_absorb": ["coalescence.coalescence_absorbs_and_grows_a_stage"],
    "slow_walkers": [],                       # stragglers miss a pass: the harness polls, nothing goes red
    "no_passive": ["coalescence.coalescence_emits_manhunters_and_grows_on_its_own"],
    "no_collapse": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "wrong_samples": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "samples_not_monstrous": ["coalescence.burn_collapses_it_into_monstrous_samples"],
    "extract_nothing": ["genome.extraction_surgery_yields_sample"],
    "patient_wont_lie": [],                   # SITE: the patient never lies down -> extraction UNMEASURED, never FAIL
    "patient_walks_to_bed": [],               # SITE timing: read beside the bed first; must still PASS (SITE_EXPECT)
    "host_vanishes": [],                      # SITE: no host -> the spawner arms UNMEASURED, never PASS (SITE_EXPECT)
    "unroof_noop": None,                      # SITE: the pad stays mountain-roofed -> fixtures crushed (SITE_EXPECT)
    "no_gestation": ["genome.inject_starts_gestation", "coalescence.monstrous_gestation_grows_one_limb"],
    "host_survives": ["genome.gestation_dies_producing_one_organ_batch"],
    "organ_count": ["genome.gestation_dies_producing_one_organ_batch", "coalescence.grown_limbs_off_grows_organs"],
    "monstrous_organs": ["coalescence.monstrous_gestation_grows_one_limb"],
    "limbs_ignore_toggle": ["coalescence.grown_limbs_off_grows_organs"],
    "log_error": ["log.log_clean"],
    "xref_error": ["log.log_clean"],
    "xref_flood": [],                         # a full page of other mods' errors: UNMEASURED (SITE_EXPECT)
    "jump_noop": None,                        # harness instrument: a jump that did not take (SITE_EXPECT)
    "roof_patch_fails": [],                   # SITE: the shelter fixture never landed -> UNMEASURED (SITE_EXPECT)
    "haze_ignores_toggle": ["zhool_haze.conversion_off_turns_nothing"],
    "haze_no_convert": ["zhool_haze.haze_turns_grass_in_place"],
    "haze_deletes": ["zhool_haze.haze_turns_grass_in_place"],
    "touched_ignores_toggle": ["touched.touched_off_doses_nothing"],
    "touched_no_contact": ["touched.touched_contact_doses"],
    "touched_bloom_only": ["touched.touched_contact_doses"],   # dosed everywhere alike: contact adds nothing
    "arrest_ignored": ["touched.sunbeam_hit_arrests"],
    "arrest_ignores_toggle": ["touched.sunbeam_hit_arrests"],
    "armored_wanders_off": [],                # SITE: the armored control leaves the open pad -> UNMEASURED (SITE_EXPECT)
    "mulch_none": ["spawner.unfinished_leaves_mulch"],
    "helix_trader_unwired": ["defs.helix_trader_wired"],
    "tells_unwired": ["defs.visible_tells_wired"],
}


# SITE breaks whose point is a verdict other than FAIL: {break: {component: verdict}}
SITE_EXPECT = {
    "patient_wont_lie": {"genome.extraction_surgery_yields_sample": "UNMEASURED"},
    "slow_walkers": {"coalescence.coalescence_absorbs_and_grows_a_stage": "PASS"},
    "armored_wanders_off": {"burn_forced.burn_hurts_native_spares_armored": "UNMEASURED"},
    "roof_patch_fails": {"burn_forced.burn_site_ready": "UNMEASURED",
                         "burn_forced.burn_doses_the_exposed_visitor": "UNMEASURED"},
    "xref_flood": {"log.log_clean": "UNMEASURED"},
    "jump_noop": {"spawner.spawner_off_buds_nothing": "FAIL", "burn_natural.burn_off_never_schedules": "FAIL"},
    "patient_walks_to_bed": {"genome.extraction_surgery_yields_sample": "PASS"},
    "host_vanishes": {"spawner.spawner_off_buds_nothing": "UNMEASURED",
                      "spawner.spawner_buds_unfinished": "UNMEASURED"},
    # the round-4 failure, reproduced: without the unroof the fake map crushes the pads exactly as live did
    "unroof_noop": {"repulsor_clear.off_when_setting_off": "FAIL",
                    "spawner.spawner_off_buds_nothing": "UNMEASURED",
                    "burn_forced.burn_harmless_at_zero_damage": "UNMEASURED",   # crushed visitor: no reading
                    "coalescence.coalescence_off_absorbs_nothing": "FAIL"},
}


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
    ok_breaks = 0
    for brk, want in sorted(SITE_EXPECT.items()):
        res = run([brk])
        got = dict((k, res.get(k, ("ABSENT",))[0]) for k in want)
        if got != want:
            bad.append("site break %-22s expected %s, got %s" % (brk, want, got))
        crashed = sorted(k for k, v in res.items() if v[0] == "CRASH")
        if crashed:                           # a site fault must never crash the script (BREAKS checks the [] reds)
            bad.append("site break %-22s crashed %s" % (brk, crashed))
    for brk, target in sorted(BREAKS.items()):
        if target is None:                    # checked by SITE_EXPECT only
            ok_breaks += 1
            continue
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != sorted(target):
            bad.append("break %-26s expected only %s FAIL, got %s" % (brk, target, reds))
        else:
            ok_breaks += 1
    # TWO STARTS (CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK): the saved Contagion site starts already RM_Contagion.
    # The whole suite must still go green there, take the map off the biome for the stock-map arm, and end on the
    # START biome (the saved site goes back to RM_Contagion, never to the off biome).
    games = []
    sick = run(start_biome=V.BIOME, out=games)
    sick_bad = dict((k, v) for k, v in sick.items() if v[0] != "PASS")
    if sick_bad:
        bad.append("sick start: %d of %d components not PASS: %s" % (len(sick_bad), len(sick), sick_bad))
    if len(sick) != n_comp:
        bad.append("sick start produced %d components, stock start %d" % (len(sick), n_comp))
    g = games[-1]
    if g.biome != V.BIOME or not g.retiles or g.retiles[0] != V.OFF_BIOME:
        bad.append("sick start: retiles %s, ended on %s (want first %s, end %s)" % (g.retiles, g.biome, V.OFF_BIOME,
                                                                                   V.BIOME))
    if run()["site.retile_to_contagion"][0] != "PASS":
        bad.append("stock start lost its retile")
    # a sick start whose off-retile does not take: the stock-map arm is UNMEASURED (no control), never PASS or FAIL
    noop = run(["retile_noop"], start_biome=V.BIOME)
    for k in ("repulsor_clear.site_ready_baseline", "site.retile_to_contagion"):
        if noop.get(k, ("ABSENT",))[0] != "UNMEASURED":
            bad.append("sick start + retile_noop: %s reads %s, want UNMEASURED" % (k, noop.get(k)))
    red = sorted(k for k, v in noop.items() if v[0] in ("FAIL", "CRASH"))
    if red:
        bad.append("sick start + retile_noop turned red: %s" % red)
    # the live preflight no longer refuses a sick map (it did, until this item)
    import northstar_site as NS                      # noqa: E402

    class _S(object):
        def call(self, verb, **k):
            if verb == "jawa/map_info":
                return {"success": True, "mapBiome": V.BIOME, "tileValid": True, "sizeX": 250, "sizeZ": 250}
            return {"success": True, "value": None}
    pf = [m for m in NS.preflight(_S()) if m.startswith(("map_biome", "map_size", "map_tile"))]
    if pf:
        bad.append("northstar_site.preflight refuses the saved Contagion site: %s" % pf)

    # the coalescence emit arm's declared disturbance: its own emissions only, never anything else
    em = V._unfinished_emission
    for trig, want in (({"kind": "hostile_arrival", "detail": "arrived: RM_TheUnfinished RM_TheUnfinished (animal)"}, True),
                       ({"kind": "hostile_arrival", "detail": "arrived: Megaspider Megaspider (animal)"}, False),
                       ({"kind": "mental", "severity": "info", "subjectId": 900, "detail": "mental state Manhunter"}, True),
                       ({"kind": "mental", "severity": "info", "subjectId": 7, "detail": "mental state Manhunter"}, False),
                       ({"kind": "mental", "severity": "damage", "subjectId": 900, "detail": "mental state Berserk"}, False),
                       ({"kind": "hurt", "detail": "health 1 -> 0.9; newest hediff Bite/Leg age 3 from RM_TheUnfinished"}, True),
                       ({"kind": "hurt", "detail": "health 1 -> 0.9; newest hediff Bruise/Leg age 3 from Human"}, False),
                       ({"kind": "downed", "detail": "downed (health 0.2)"}, False),
                       ({"kind": "colonist_hostile", "detail": "colonist turned hostile (Berserk)"}, False),
                       ({"kind": "hurt", "critical": True, "detail": "x from RM_TheUnfinished"}, False)):
        if bool(em(trig, frozenset([7]))) != want:
            bad.append("_unfinished_emission(%s) != %s" % (trig, want))
    print("selftest Contagion: %d components, healthy PASS %d/%d; %d/%d breaks each turn exactly "
          "their component red" % (n_comp, n_comp - len(notpass), n_comp, ok_breaks, len(BREAKS)))
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
