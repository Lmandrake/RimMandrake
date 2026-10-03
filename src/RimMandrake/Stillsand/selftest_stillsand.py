#!/usr/bin/env python3
"""Offline selftest for Stillsand's validation.py: a scripted FAKE GAME that implements the mod's
behaviours, run (1) healthy -- every component must PASS -- and (2) once per mod behaviour broken -- the
named component must go FAIL and no other component may.

That second half is the proof every check can fail: each break is a mod defect (a patch that is not
armed, a toggle that gates nothing, an effect that never fires, a known past bug back again) and the
suite must see it. The fake encodes the response SHAPES validation.py assumes (read off the JawaBench
[Tool] descriptions and the 2026-10-01 live scripts in Transient/livesession2_20261001); it proves the
predicates and wiring, not the shapes -- those are UNPROVEN until the first live run of this script.

    python3 src/RimMandrake/Stillsand/selftest_stillsand.py
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

spec = importlib.util.spec_from_file_location("stillsand_validation", os.path.join(HERE, "validation.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
V.time.sleep = lambda s: None                      # the fast-wait and regen polls must not really sleep

from suite import TestContext                     # noqa: E402

SKELETON_DEFS = V.GIANT_SKELETONS
STILLSAND = "RM_Stillsand"
ROUNDTRIP_FIELDS = ("yardangShapingEnabled", "torEnabled", "boneHarpEnabled", "ledgerEnabled",
                    "ledgerIncidentWeighting", "abrasionEnabled", "carryEnabled", "staticEnabled",
                    "seedingEnabled")


def rect(s):
    return [int(v) for v in str(s).split(",")]


def inrect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class _RB(object):
    """What the suite reaches through session._rb (the one dict-form call: pawn_gear's `def`)."""

    def __init__(self, game):
        self.game = game

    def call(self, tool, params):
        return self.game.call(tool, **params)


class Fake(object):
    def __init__(self, broken=()):
        self.b = set(broken)
        self.ticks = 1000
        self.fast = False
        self.n = 0
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        if "setting_missing" in self.b:
            del self.settings["torChance"]
        self.biome, self.tile, self.tile_biome = "RimWorld_Temperate", 9000, None
        self.things, self.pawns = {}, {}
        self.terrain, self.roofs = [], []
        self.weather, self.locked = "Clear", False
        self.letters, self.log = [], []
        self.cond, self.sched = None, []
        self._rb = _RB(self)
        self.n_errors = 0
        self.regens = 0
        self.log_info("Initialising")
        if "log_saturated" in self.b:
            self.log_info("Reached max messages limit. Will stop printing.", "Error")
        if "log_error" in self.b:
            self.log_info("[Stillsand] precious cave carve failed: boom", "Error")

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
            raise RuntimeError("fake: unknown tool %s" % tool)
        return h(**p)

    # ------------------------------------------------------------ small model helpers
    def new(self, d, x, z, **kw):
        self.n += 1
        tid = "T%d" % self.n
        row = dict(id=tid, x=x, z=z, **kw)
        row["def"] = d
        self.things[tid] = row
        return tid

    def of(self, d):
        return [t for t in self.things.values() if t["def"] == d]

    def terr(self, x, z):
        for r, name in reversed(self.terrain):
            if inrect(x, z, r):
                return name
        return "Sand" if self.biome == STILLSAND else "Soil"

    def roofed(self, x, z):
        for r, on in reversed(self.roofs):
            if inrect(x, z, r):
                return on
        return False

    def on(self, f):
        return self.settings.get(f) == "True"

    def log_info(self, text, kind="Message"):
        self.log.append({"type": kind, "text": text, "repeats": 1})

    def letter(self, label, text=""):
        self.letters.append({"label": label, "arrivalTick": self.ticks, "text": text})

    def add_pawn(self, kind, x, z, faction="none"):
        self.n += 1
        pid = "P%d" % self.n
        self.pawns[pid] = dict(id=pid, kind=kind, x=x, z=z, faction=faction, dead=False, h={}, job="Wait",
                               gear=set(), born=self.ticks, path=0)
        return pid

    def cur_weather(self):
        if self.cond:
            span = self.cond["end"] - self.cond["start"]
            herald = "no_herald" not in self.b and self.ticks < self.cond["start"] + 0.15 * span
            return "RM_DuneGaleHerald" if herald else "RM_DuneGale"
        return self.weather

    # ------------------------------------------------------------ simulation
    def advance(self, n):
        while n > 0:
            d = min(250, n)
            n -= d
            self.ticks += d
            self.chunk(d)

    def chunk(self, d):
        b = self.b
        # scheduled events
        for ev in [e for e in self.sched if e[0] <= self.ticks]:
            self.sched.remove(ev)
            ev[1]()
        # gale end
        if self.cond and self.ticks >= self.cond["end"]:
            self.end_gale()
        for p in list(self.pawns.values()):
            if p["dead"]:
                continue
            k = p["kind"]
            # sand swimmer submerges on sand (never on gravel), surfaces when hurt
            if k == "RM_Vekka" and "no_submerge" not in b and self.ticks - p["born"] >= 100:
                if self.terr(p["x"], p["z"]) == "Sand":
                    p["h"]["RM_SandSubmerged"] = 1.0
                else:
                    p["h"].pop("RM_SandSubmerged", None)
                if "submerge_on_rock" in b:
                    p["h"]["RM_SandSubmerged"] = 1.0
            # loomma sun clock
            if k == "RM_Loomma":
                shaded = self.roofed(p["x"], p["z"]) and "loomma_ignores_shade" not in b
                p["h"]["RM_LoommaSunstruck"] = max(0.0, p["h"].get("RM_LoommaSunstruck", 0.01) +
                                                   (-0.0001 if shaded else 0.0001) * d)
            # soorrak: wander (or the stuck idle loop), some leave the map
            if k == "RM_Soorrak":
                if "soorrak_nre" in b:
                    self.log_info("Exception ticking RM_Soorrak: NullReferenceException at "
                                  "Pawn_FlightTracker.Notify_JobStarted", "Error")
                if "soorrak_stuck" in b:
                    p["job"] = "Wait_MaintainPosture"
                else:
                    p["job"] = "GotoWander"
                    p["x"] += 1
                    p["path"] += 1
                    if self.ticks - p["born"] > 700 and (int(p["id"][1:]) % 3):
                        p["dead"] = True
                        p["gone"] = True
            # glare-blind in open full sun, not behind goggles
            if p["faction"] == "player" and k == "Colonist" and "no_glare" not in b:
                protected = "RM_SunGoggles" in p["gear"] and "goggles_ignored" not in b
                if not self.roofed(p["x"], p["z"]) and not protected:
                    p["h"]["RM_GlareBlind"] = p["h"].get("RM_GlareBlind", 0.0) + 0.0002 * d
        # a giant's corpse becomes its skeleton after corpseToSkeletonDays
        for c in [t for t in self.things.values() if t["def"].startswith("Corpse_")]:
            on = self.on("corpseToSkeletonEnabled") or "skeleton_corpse_toggle_ignored" in b
            due = self.ticks - c["death"] >= float(self.settings["corpseToSkeletonDays"]) * 60000
            if on and due and "no_skeleton" not in b:
                del self.things[c["id"]]
                self.new(c["race"] + "Skeleton", c["x"], c["z"])
        # zuurrik poll
        if self.ticks // 600 != (self.ticks - d) // 600:
            self.zuurrik_poll()
        # dust devils
        for t in self.of("RM_DustDevil"):
            if "devil_still" not in b:
                t["x"] += 1
                t["z"] += 1
            if "devil_immortal" not in b and self.ticks - t["born"] >= 1500:
                del self.things[t["id"]]

    def end_gale(self):
        b = self.b
        self.cond = None
        delta = "+0.0" if "dunes_still" in b else "+4.4"
        moved = 0 if "dunes_still" in b else 11
        self.log_info("[Stillsand] dune gale ended on Map-1-PlayerHome: dune field mass 3.2 -> 7.6 "
                      "(delta %s); cells moved past 0.20: %d; carried 0, abraded 10, stunned 0" % (delta, moved))
        if "no_emergence" in b:
            return
        if self.on("emergenceEnabled") or "emergence_ignores_toggle" in b:
            self.letter(V.EMERGENCE_LABELS[2], "uncovered")

    def blood_cells(self):
        return [t for t in self.of("Filth_Blood")]

    def zuurrik_poll(self):
        b = self.b
        alive = [p for p in self.pawns.values() if p["kind"] == "RM_Zuurrik" and not p["dead"]]
        enabled = self.on("zuurrikEnabled") or "zuurrik_ignores_toggle" in b
        if not enabled or "no_wake" in b:
            return
        blood = self.blood_cells()
        thr = 2 if "wakes_below_threshold" in b else int(self.settings["zuurrikBloodThreshold"])
        if alive:
            if "no_strip" not in b and blood:
                del self.things[blood[0]["id"]]          # strips one stain per poll
            return
        if len(blood) >= thr:
            for i in range(3):
                self.add_pawn("RM_Zuurrik", blood[0]["x"] + i, blood[0]["z"])

    # ------------------------------------------------------------ the regenerated map
    def regen(self):
        b = self.b
        self.regens += 1
        self.pawns.clear()
        self.things.clear()
        self.terrain, self.roofs = [], []
        if self.tile_biome:
            self.biome = self.tile_biome
        # the Hive group the quicktest drops at the centre
        self.add_pawn("Megaspider", 125, 125, faction="Hive")
        if self.biome != STILLSAND:
            return
        if "no_cave_log" not in b and (self.on("genStepEnabled") or "caves_ignore_toggle" in b):
            self.log_info("[Stillsand] precious cave: a yardang north (412 cells, mouth faces away)")
            self.log_info("[Stillsand] precious cave roll: RM_PreciousCave_Seep (T2) in the north")
        if self.on("skeletonPlacementEnabled") or "skeleton_ignores_toggle" in b:
            for i in range(3 if "skeleton_overcap" in b else 1):
                self.new("RM_OommokSkeleton", 40 + 40 * i, 40)

    # ------------------------------------------------------------ tools
    def t_step_game_ticks(self, ticks=0, **k):
        self.advance(int(ticks))
        return {"success": True}

    def t_set_time_speed(self, speed=None, **k):
        self.fast = speed == "Ultrafast"
        return {"success": True}

    def t_time_clock(self, **k):
        return {"success": True, "ticksGame": self.ticks, "hour": (self.ticks // 2500) % 24}

    def t_time_set_ticks(self, ticks=0, **k):
        self.ticks = int(ticks)
        return {"success": True}

    def t_map_info(self, **k):
        return {"success": True, "tile": self.tile, "mapBiome": self.biome, "sizeX": 250, "sizeZ": 250,
                "latitude": 38.0}

    def t_world_tile_set(self, tiles=None, biome=None, temperature=None, **k):
        self.tile_biome = None if "regen_keeps_biome" in self.b else biome
        return {"success": True}

    def t_world_commit(self, **k):
        return {"success": True}

    def t_get_bridge_status(self, **k):
        return {"success": True, "state": {"currentMapReady": True}}

    def t_execute_debug_action(self, path=None, x=None, z=None, **k):
        if path.endswith("Regenerate Current Map"):
            self.regen()
        elif path.endswith("Destroy hostile pawns"):
            for pid in [i for i, p in self.pawns.items() if p["faction"] == "Hive"]:
                del self.pawns[pid]
        elif path.endswith("T: Kill"):
            for p in self.pawns.values():
                if not p["dead"] and (p["x"], p["z"]) == (x, z):
                    p["dead"] = True
                    self.new("Corpse_" + p["kind"], x, z, death=self.ticks, race=p["kind"])
                    break
        return {"success": True}

    def t_drain_log(self, contains=None, errorsOnly=False, limit=50, **k):
        rows = []
        for m in self.log:
            if errorsOnly and m["type"] not in ("Error", "Warning"):
                continue
            if contains and contains.lower() not in m["text"].lower():
                continue
            rows.append(dict(m))
        return {"success": True, "totalInBuffer": len(self.log), "messages": rows[-limit:]}

    def t_dlc_status(self, **k):
        return {"success": True, "RoyaltyActive": True, "IdeologyActive": True, "BiotechActive": True,
                "AnomalyActive": True, "OdysseyActive": True}

    def t_mod_settings_field(self, typeName=None, action=None, field=None, value=None, **k):
        if field not in self.settings or V.FIELD_TYPE.get(field) != typeName:
            return {"success": False, "message": "no such field"}
        if action == "set" and not ("roundtrip_ignored" in self.b and field in ROUNDTRIP_FIELDS):
            self.settings[field] = str(value)
        return {"success": True, "value": self.settings[field]}

    # ---- defs
    def t_get_defs(self, defs="", fields=None, limit=200, **k):
        want = [d for d in defs.split(";") if d]
        nf = [d for d in want if d.endswith("NoSuchDef_Probe")]
        if "missing_def" in self.b:
            nf += [d for d in want if d.endswith("/RM_KneelOllim")]
        if "custom_missing" in self.b:
            nf += [d for d in want if d.endswith("/RM_PreciousCave_Seep")]
        rows = []
        for d in want:
            if d in nf:
                continue
            typ, name = d.split("/", 1)
            f = {"defName": name}
            if (typ, name) == ("BiomeDef", STILLSAND):
                ext = ["RM_SunHeatExtension", "RM_PinnedSunExtension", "DuneFieldExtension",
                       "RM_SkeletonBiomeExtension", "RM_SandRemembersWaterExtension"]
                steps = ["RM_PreciousCaveCarve", "RM_PreciousCaveContents", "RM_GiantSkeletons"]
                if "no_ext" in self.b:
                    ext.remove("RM_SkeletonBiomeExtension")
                if "no_gensteps" in self.b:
                    steps.remove("RM_GiantSkeletons")
                f = {"animalDensity": 0.0 if "zero_density" in self.b else 0.1, "modExtensions": ext,
                     "extraGenSteps": steps}
            elif typ == "ThingDef" and name in V.GIANT_RACES:
                ext = ["RM_SkeletonRemainsExtension"]
                if "giant_unwired" in self.b and name == "RM_Oommok":
                    ext = []
                f = {"modExtensions": ext}
            elif (typ, name) == ("ThingDef", "RM_GuzzkaEggUnfertilized"):
                f = {"comps": ["CompProperties_Hatcher"] +
                     ([] if "egg_unpatched" in self.b else ["RM_CompProperties_WaterVolume"])}
            elif (typ, name) == ("IncidentDef", "RM_SandBusterEruption"):
                f = {"allowedBiomes": [] if "eruption_ungated" in self.b else [STILLSAND]}
            rows.append({"requested": d, "found": True, "defName": name, "fields": f})
        return {"success": True, "foundCount": len(rows), "notFound": nf, "malformed": [], "defs": rows}

    def t_biome_probe(self, biomes=None, find=None, **k):
        names = [n for n in (find or "").split(",") if n]
        rows = []
        for n in names:
            st = "spawning"
            if n == "RM_Stillsand_NoSuchProbe":
                st = "spawning" if "probe_blind" in self.b else "absent"
            if n == "RM_Siidda" and "roster_zeroed" in self.b:
                st = "zeroed"
            rows.append({"defName": n, "state": st})
        return {"success": True, "biomes": [{"defName": STILLSAND, "findResults": rows}]}

    # ---- sun
    def exposure(self, x, z):
        if self.roofed(x, z) and "roof_no_cover" not in self.b:
            return 0.0
        e = 0.3 if "low_exposure" in self.b else 1.0
        # the real shadegrid_read returns ExposureAt(cell), which has no weather factor (that is applied in
        # ExposureFor(pawn) only), so the gale never changes a cell read here either
        return e

    def t_shadegrid_read(self, cells=None, **k):
        rows = []
        for tok in (cells or "").split(";"):
            if tok:
                x, z = [int(v) for v in tok.split(",")]
                rows.append({"x": x, "z": z, "inBounds": True, "shade": 0.0, "exposure": self.exposure(x, z)})
        glow = 1.0
        if "night_falls" in self.b and (self.ticks // 30000) % 2 == 1:
            glow = 0.1
        return {"success": True, "present": True,
                "pinnedSun": {"present": True, "isActive": "no_pinned" not in self.b,
                              "sunElevationDegrees": 70.0},
                "skyGlow": glow, "cells": rows}

    # ---- weather and incidents
    def t_weather_set(self, weather=None, lockWeather=False, unlock=False, **k):
        if unlock:
            self.locked = False
        if weather:
            self.weather = weather
            self.locked = bool(lockWeather)
        return {"success": True}

    def t_weather_get(self, **k):
        return {"success": True, "weather": {"current": self.cur_weather()}}

    def t_letter_list(self, **k):
        return {"success": True, "letters": [dict(l) for l in self.letters]}

    def t_game_condition(self, action=None, condition=None, durationTicks=0, **k):
        if action == "start" and condition == "RM_DuneGale":
            self.cond = {"start": self.ticks, "end": self.ticks + int(durationTicks)}
        elif action == "end":
            self.cond = None
        return {"success": True}

    def can_fire(self, name):
        if name == "RM_DuneGale" and "gale_never_fires" in self.b:
            return False
        if name == "RM_DuneGale":
            return self.on("galeEnabled") or "gale_ignores_toggle" in self.b
        if name == "RM_DustDevil":
            return self.on("dustDevilsEnabled") or "devil_ignores_toggle" in self.b
        return True

    def t_fire_incident(self, incidentDef=None, dryRun=False, points=None, **k):
        if dryRun:
            cf = self.can_fire(incidentDef)   # the live tool answers success=False when it cannot fire
            return {"success": bool(cf), "canFireNow": cf, "ticksGame": 134661}
        if incidentDef == "RM_MuurrokEmergence":
            self.letter("A line of glare")
            if "no_muurrok" not in self.b:
                self.sched.append((self.ticks + 1500, lambda: self.add_pawn("RM_Muurrok", 10, 10)))
        elif incidentDef == "RM_SandBusterEruption":
            self.letter("Sand Buster Eruption")
            self.new("RM_SandBusterTunnel", 60, 60)
            if "no_mound" not in self.b:
                self.sched.append((self.ticks + 1000, lambda: self.new("RM_SandBusterMound", 60, 60)))
        return {"success": True}

    def t_storyteller_fire(self, incidentDef=None, dryRun=True, **k):
        hours = float(self.settings["horizonWarningHours"])
        warn = self.on("horizonWarningsEnabled") or "horizon_ignores_toggle" in self.b
        if warn and "no_horizon_letter" not in self.b:
            self.letter("Dust on the horizon: north-west")
        if warn and "horizon_instant" not in self.b:
            self.sched.append((self.ticks + int(hours * 2500), lambda: self.add_pawn("Trader", 5, 5, "Guild")))
        else:
            self.add_pawn("Trader", 5, 5, "Guild")
        return {"success": True, "fired": True, "blockedByDialog": False}

    def t_window_list_close(self, **k):
        return {"success": True}

    def t_spawn_thing(self, defName=None, x=0, z=0, **k):
        self.new(defName, x, z, born=self.ticks)
        return {"success": True}

    # ---- pawns and things
    def t_spawn_pawn(self, kindDef=None, x=0, z=0, faction="none", count=1, **k):
        if kindDef == "RM_Oorrik" and "oorrik_nre" in self.b:
            return {"success": False, "message": "NullReferenceException in pawn generation"}
        rows = [{"id": self.add_pawn(kindDef, x, z, faction), "ok": True} for _ in range(int(count))]
        return {"success": True, "pawns": rows}

    def t_list_pawns(self, rect=None, includeHealth=False, limit=500, includeCorpses=False, **k):
        rr = (lambda r: r)(globals()["rect"](rect)) if rect else None
        rows = []
        for p in self.pawns.values():
            if p.get("gone"):
                continue
            if rr and not inrect(p["x"], p["z"], rr):
                continue
            row = {"id": p["id"], "kindDef": p["kind"], "x": p["x"], "z": p["z"],
                   "faction": None if p["faction"] == "none" else p["faction"], "dead": p["dead"],
                   "isPlayer": p["faction"] == "player"}
            if includeHealth:
                row["health"] = {"hediffs": [{"def": h, "severity": s} for h, s in p["h"].items()]}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_site_state(self, **k):
        return {"success": True, "pawns": [{"id": p["id"], "job": p["job"]} for p in self.pawns.values()
                                           if not p["dead"]]}

    def t_list_things(self, defName=None, rect=None, limit=1, **k):
        rr = globals()["rect"](rect) if rect else None
        rows = [t for t in self.of(defName) if not rr or inrect(t["x"], t["z"], rr)]
        return {"success": True, "scanned": 100, "countMatched": len(rows), "isCompleteList": True,
                "things": [dict(t, stackCount=t.get("stackCount", 1)) for t in rows[:limit]]}

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
            if "set_plants_drops" in self.b and d == "RM_Glasscrust":
                continue
            self.new(d, n[0], n[1], stackCount=1)
        return {"success": True}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = rect(rects)
        if categories != "Pawn":
            for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
                del self.things[tid]
        if categories in ("Pawn", "All"):
            for pid in [i for i, p in self.pawns.items() if inrect(p["x"], p["z"], rr)]:
                del self.pawns[pid]
        return {"success": True}

    def t_set_terrain_batch(self, ops="", layer=None, **k):
        for op in ops.split(";"):
            name, r = op.split(":")
            self.terrain.append((rect(r), name))
        return {"success": True}

    def t_set_roof_batch(self, ops="", roofDef=None, **k):
        self.roofs.append((rect(ops), roofDef != "None"))
        return {"success": True}

    def t_pawn_flight(self, pawn=None, **k):
        return {"success": True, "pawns": [{"id": pawn, "canEverFly": "no_fly" not in self.b,
                                            "maxFlightTimeStat": 30.0}]}

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **k):
        b = self.b
        if jobDef == "AttackMelee":
            def strike(pawn=pawnId, tgt=targetAId):
                v, c = self.pawns.get(pawn), self.pawns.get(tgt)
                if not v or not c or c["dead"]:
                    return
                c["dead"] = True
                if "no_funnel" not in b:
                    self.new("RM_Filth_DisturbedSand", c["x"], c["z"])
                self.letter("Taken under: Pilot")
            self.sched.append((self.ticks + 300, strike))
        elif jobDef == "RM_PourWaterIntoSand":
            def pour(tgt=targetAId):
                egg = self.things.pop(tgt, None)
                if not egg:
                    return
                sand = self.terr(egg["x"], egg["z"]) == "Sand" or "bloom_on_gravel" in b
                if sand and "no_bloom" not in b and (self.on("bloomOnPour") or "bloom_ignores_toggle" in b):
                    for i in range(3):
                        self.new("RM_Hourbloom", egg["x"] + i, egg["z"])
            self.sched.append((self.ticks + 400, pour))
        return {"success": True, "accepted": True}

    def t_pawn_use_verb(self, pawn=None, action=None, verb=None, targetId=None, **k):
        if action != "cast" or targetId not in self.pawns:
            return {"success": True}
        usable = self.on("mirrorBeamEnabled") or "beam_ignores_toggle" in self.b
        if usable and self.cur_weather() == "Clear" and "beam_no_damage" not in self.b:
            self.pawns[targetId]["h"]["Burn"] = 1.0
        return {"success": True}

    def t_pawn_stats(self, pawn=None, stats=None, **k):
        p = self.pawns[pawn]
        v = 26.0 + (3.0 if "draught_wrong" in self.b else 8.0) * ("RM_CoolingDraught" in p["h"])
        return {"success": True, "stats": [{"defName": "ComfyTemperatureMax", "value": v}]}

    def t_pawn_health(self, pawn=None, action=None, hediff=None, severity=1.0, **k):
        p = self.pawns[pawn]
        if action == "add":
            p["h"][hediff] = severity
        elif action == "remove":
            p["h"].pop(hediff, None)
        return {"success": True}

    def t_pawn_gear(self, pawn=None, action=None, quality=None, **k):
        if "gear_fails" in self.b:
            return {"success": False, "message": "no such apparel"}
        self.pawns[pawn]["gear"].add(k.get("def"))
        return {"success": True}

    # ---- sun tables
    def table_toggle(self, d):
        return {"RM_SunFurnace": "sunFurnaceEnabled", "RM_LensBench": "lensBenchEnabled",
                "RM_SolarOven": "solarOvenEnabled"}[d]

    def t_inspect_string(self, thingIds=None, **k):
        t = self.things.get(thingIds)
        if t is None:
            return {"success": True, "things": []}
        lines = []
        if t["def"] in ("RM_SunFurnace", "RM_LensBench", "RM_SolarOven"):
            f = self.table_toggle(t["def"])
            short = t["def"][3:].lower()
            if not self.on(f) and (short + "_ignores_toggle") not in self.b:
                lines = ["Disabled in Mod Settings (Stillsand: glass and lenses)."]
            elif self.roofed(t["x"], t["z"]) and "no_roof_check" not in self.b:
                lines = ["Not working: under a roof (sun 0%, needs 30%)."]
            elif "table_no_sun_line" in self.b:
                lines = ["Idle."]
            else:
                lines = ["Sun: 77% (work speed x77%)"]
        return {"success": True, "things": [{"id": t["id"], "label": t["def"], "inspect": lines}]}

    def t_thing_stats(self, thing=None, stats=None, **k):
        t = self.things[thing]
        f = 0.05 if self.roofed(t["x"], t["z"]) else 0.8
        if "no_statpart" in self.b:
            f = 0.8
        if "mult_ignored" not in self.b:
            f *= float(self.settings["sunWorkSpeedMultiplier"])
        return {"success": True, "things": [{"stats": [{"defName": "WorkTableWorkSpeedFactor", "value": f}]}]}

    def t_stat_cache_bust(self, **k):
        return {"success": True}


# ------------------------------------------------------------------ the runner

def run(broken=()):
    V._STATE.clear()
    game = Fake(broken)
    results = {}
    for name, fn in V.suite.chains:
        t = TestContext(game, anchor=(125, 125))
        try:
            fn(t)
        except Exception as ex:            # a chain-level crash is a script bug
            results[name + ".<CRASH>"] = ("CRASH", "%s: %s" % (type(ex).__name__, ex))
            continue
        for c in t.components:
            results["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return results


# break -> the components that must go FAIL (and nothing else may)
BREAKS = {
    "regen_keeps_biome": ["site.site_stillsand_map"],
    "no_cave_log": ["site.site_cave_logged", "caves.gen_toggles_off_no_cave_no_skeleton"][:1],
    "skeleton_overcap": ["site.skeleton_gen_within_cap"],
    "missing_def": ["defs.defs_resolve"],
    "custom_missing": ["defs.custom_defs_resolve"],
    "zero_density": ["defs.biome_row"],
    "no_ext": ["defs.biome_row"],
    "no_gensteps": ["defs.biome_row"],
    "roster_zeroed": ["defs.biome_roster"],
    "probe_blind": ["defs.biome_roster"],
    "giant_unwired": ["defs.giants_skeleton_wired"],
    "egg_unpatched": ["defs.water_egg_patched"],
    "eruption_ungated": ["defs.eruption_biome_gate"],
    "setting_missing": ["settings.defaults"],
    "no_pinned": ["sun.sun_pinned_no_night"],
    "night_falls": ["sun.sun_pinned_no_night"],
    "roof_no_cover": ["sun.sun_roof_cover_above_55deg"],
    "oorrik_nre": ["fauna.fauna_spawns"],
    "no_fly": ["fauna.soorrak_can_fly"],
    "set_plants_drops": ["flora.flora_spawns"],
    "no_submerge": ["sandswim.vekka_submerges_on_sand"],
    "submerge_on_rock": ["sandswim.vekka_submerges_on_sand"],
    "no_funnel": ["sandswim.vekka_take_leaves_funnel"],
    "wakes_below_threshold": ["zuurrik.zuurrik_below_threshold_dormant"],
    "no_wake": ["zuurrik.zuurrik_wakes_on_blood"],
    "no_strip": ["zuurrik.zuurrik_strips_blood"],
    "zuurrik_ignores_toggle": ["zuurrik.zuurrik_toggle_off_no_wake"],
    "loomma_ignores_shade": ["loomma.loomma_sunstruck_open_vs_roofed"],
    "soorrak_nre": ["soorrak.soorrak_no_exceptions"],
    "soorrak_stuck": ["soorrak.soorrak_not_stuck"],
    "roundtrip_ignored": ["settings.%s_roundtrip" % f for f in ROUNDTRIP_FIELDS],
    "low_exposure": ["sun.sun_open_sand_full_exposure"],
    "table_no_sun_line": ["glass.sun_table_reads_sun_in_open"],
    "sunfurnace_ignores_toggle": ["glass.sunfurnace_toggle_off_disabled"],
    "lensbench_ignores_toggle": ["glass.lensbench_toggle_off_disabled"],
    "solaroven_ignores_toggle": ["glass.solaroven_toggle_off_disabled"],
    "gear_fails": ["glare.glare_site_ready"],
    "gale_never_fires": ["gale.gale_incident_fires"],
    "no_roof_check": ["glass.sun_table_roofed_idle"],
    "no_statpart": ["glass.furnace_work_speed_tracks_sun"],
    "mult_ignored": ["glass.sun_work_speed_multiplier_scales"],
    "no_bloom": ["water.pour_blooms_on_sand"],
    "bloom_ignores_toggle": ["water.pour_toggle_off_no_bloom"],
    "bloom_on_gravel": ["water.pour_on_gravel_no_bloom"],
    "no_skeleton": ["skeleton.corpse_becomes_skeleton"],
    "skeleton_corpse_toggle_ignored": ["skeleton.corpse_stays_when_toggle_off"],
    "no_glare": ["glare.glare_blind_gained_in_open_sun"],
    "goggles_ignored": ["glare.goggles_block_glare_blind"],
    "draught_wrong": ["cooling.cooling_draught_widens_comfort"],
    "gale_ignores_toggle": ["gale.gale_toggle_off_refuses"],
    "no_herald": ["gale.gale_phases_and_aftermath"],
    "dunes_still": ["gale.gale_phases_and_aftermath"],
    "emergence_ignores_toggle": ["gale.gale_emergence_off_quiet"],
    "devil_still": ["devil.devil_moves_and_expires"],
    "devil_immortal": ["devil.devil_moves_and_expires"],
    "devil_ignores_toggle": ["devil.devil_toggle_off_refuses"],
    "no_muurrok": ["muurrok.muurrok_emergence_fires"],
    "beam_no_damage": ["muurrok.beam_burns_target"],
    "beam_ignores_toggle": ["muurrok.beam_toggle_off_blocked"],
    "no_mound": ["eruption.eruption_tunnel_then_mound"],
    "no_horizon_letter": ["horizon.horizon_warns_then_arrives"],
    "horizon_instant": ["horizon.horizon_warns_then_arrives"],
    "horizon_ignores_toggle": ["horizon.horizon_toggle_off_vanilla"],
    "caves_ignore_toggle": ["caves.genstep_off_no_cave_line"],
    "skeleton_ignores_toggle": ["caves.skeleton_placement_off_none"],
    "log_error": ["log.log_clean"],
}


def main():
    bad = []
    real_err = sys.stderr
    sys.stderr = open(os.devnull, "w")              # the suite's progress lines are for live runs
    try:
        return _main(bad)
    finally:
        sys.stderr = real_err


def _main(bad):
    healthy = run()
    # gale_dims_sun_exposure is UNMEASURED by design: no tool reads pawn exposure (see validation.py)
    notpass = dict((k, v) for k, v in healthy.items()
                   if v[0] != "PASS" and k != "gale.gale_dims_sun_exposure")
    if healthy.get("gale.gale_dims_sun_exposure", ("",))[0] != "UNMEASURED":
        bad.append("gale.gale_dims_sun_exposure should read UNMEASURED: %s" % (healthy.get("gale.gale_dims_sun_exposure"),))
    n_comp = len(healthy)
    if notpass:
        bad.append("healthy run: %d of %d components not PASS: %s" % (len(notpass), n_comp, notpass))
    declared = len(V.suite.components_declared())
    if declared != n_comp:
        bad.append("declared %d components but the run produced %d" % (declared, n_comp))
    ok = 0
    for brk, targets in sorted(BREAKS.items()):
        res = run([brk])
        reds = sorted(k for k, v in res.items() if v[0] in ("FAIL", "CRASH"))
        if reds != sorted(targets):
            bad.append("break %-26s expected only %s FAIL, got %s" % (brk, sorted(targets), reds))
        else:
            ok += 1
    print("selftest Stillsand: %d components, healthy PASS %d/%d; %d of %d breaks each turn exactly "
          "their component red" % (n_comp, n_comp - len(notpass), n_comp, ok, len(BREAKS)))
    # a saturated game log must read UNMEASURED everywhere a log line is evidence, never red and never PASS
    sat = run(["log_saturated"])
    reds = sorted(k for k, v in sat.items() if v[0] in ("FAIL", "CRASH"))
    if reds:
        bad.append("log_saturated: expected no red component, got %s" % reds)
    for k in ("site.site_cave_logged", "soorrak.soorrak_no_exceptions", "log.log_clean",
              "gale.gale_phases_and_aftermath", "caves.caves_regen_both_off"):
        if sat.get(k, ("?",))[0] != "UNMEASURED":
            bad.append("log_saturated: %s should be UNMEASURED, is %s" % (k, sat.get(k, ("missing",))[0]))
    sys.stderr = sys.__stderr__
    for b in bad:
        print("  BAD:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
