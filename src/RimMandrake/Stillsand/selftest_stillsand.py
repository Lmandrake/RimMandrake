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
SAND_GLARE_FLOOR = V.sand_glare_floor()    # read from the biome def, as the harness reads it
ROUNDTRIP_FIELDS = ("yardangShapingEnabled", "torEnabled", "boneHarpEnabled", "ledgerEnabled",
                    "ledgerIncidentWeighting", "carryEnabled",
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
        self.wet, self.camera, self.serial, self.lastopen, self.oblig, self.believed = set(), None, 0, -999999, 0, False
        self.letters, self.log = [], []
        self.cond, self.sched = None, []
        self.lev_visits, self.unforced_armed = [], False   # RM_MapComponent_SandLeviathans.visits
        self._rb = _RB(self)
        # STILLSAND_GLASS_CHAIN_REMAINDER_1: other mods' settings the glass rows read, bills, drift
        self.ext = {(V.DUNES_SETTINGS, "clearYieldEnabled"): "True",
                    (V.FLOWWORKS_SETTINGS, "shovelRequired"): "True"}
        self.bills, self.pending, self.sand = {}, [], {}
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
        for r, on, _ in reversed(self.roofs):
            if inrect(x, z, r):
                return on
        return False

    def grid_roofed(self, x, z):
        """The roof as RM_MapComponent_ShadeGrid sees it: roofShade is filled only by Recompute, which runs
        when TicksGame % 2000 == 0, so a roof set at tick T enters the grid only once a multiple of 2000 lies
        in (T, now] (STILLSAND_ROOF_COVER_EXPOSURE_1: the live run read 1.00 in the roofing tick)."""
        for r, on, tick in reversed(self.roofs):
            if inrect(x, z, r) and self.ticks // 2000 > tick // 2000:
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
                if self.ticks < p.get("surf_until", -1):
                    p["h"].pop("RM_SandSubmerged", None)
                elif self.terr(p["x"], p["z"]) == "Sand" and not ("no_resubmerge" in b and "surf_until" in p):
                    p["h"]["RM_SandSubmerged"] = 1.0
                else:
                    p["h"].pop("RM_SandSubmerged", None)
                if "submerge_on_rock" in b and self.ticks >= p.get("surf_until", -1):
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

    def end_gale(self):
        b = self.b
        self.cond = None
        delta = "+0.0" if "dunes_still" in b else "+4.4"
        moved = 0 if "dunes_still" in b else 11
        self.log_info("[Stillsand] dune gale ended on Map-1-PlayerHome: dune field mass 3.2 -> 7.6 "
                      "(delta %s); cells moved past 0.20: %d; carried 0" % (delta, moved))
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
            if "bites_unwounded" in b:
                for p in self.pawns.values():
                    if p["kind"] != "RM_Zuurrik" and not p["dead"] and \
                            min(abs(p["x"] - z["x"]) + abs(p["z"] - z["z"]) for z in alive) <= 3:
                        p["h"]["Bite"] = 0.5
            near = [t for t in self.things.values() if t["def"] == "Filth_Blood" or t["def"].startswith("Corpse_")]
            near = [t for t in near if any((t["x"] - z["x"]) ** 2 + (t["z"] - z["z"]) ** 2 <= 14.9 ** 2
                                           for z in alive)]                  # HasWorkNear's WatchRadius
            if "no_strip" not in b and blood:
                del self.things[blood[0]["id"]]          # strips one stain per poll
                self.zquiet = 0
            elif near:
                self.zquiet = 0
            else:                                        # quiet: re-bury after 3 quiet polls (QuietPollsToBury)
                self.zquiet = getattr(self, "zquiet", 0) + 1
                if self.zquiet >= 3 and "no_bury" not in b:
                    for p in alive:
                        del self.pawns[p["id"]]
                    self.zquiet = 0
            return
        # the swarm wakes AT a cluster of >= thr stains within ClusterRadius 7.9 (TryWake), never at a stray stain
        dense = [c for c in blood if sum((o["x"] - c["x"]) ** 2 + (o["z"] - c["z"]) ** 2 <= 7.9 ** 2
                                         for o in blood) >= thr]
        if dense:
            for i in range(3):
                self.add_pawn("RM_Zuurrik", dense[0]["x"] + i, dense[0]["z"])

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
        if (typeName, field) in self.ext:
            if action == "set":
                self.ext[(typeName, field)] = str(value)
            return {"success": True, "value": self.ext[(typeName, field)]}
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
            elif (typ, name) == ("ThingDef", "RM_SolarOven"):
                f = {"comps": ["RimMandrake.Stillsand.RM_CompProperties_SunPowered"] +
                     (["CompProperties_Refuelable"] if "oven_fuel" in self.b else [])}
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
        # natural sand keeps the biome's glare floor even under a roof (ShadeGrid.Recompute applies
        # WithGlareFloor after the roof cover), as the real grid does
        floor = SAND_GLARE_FLOOR if self.terr(x, z) == "Sand" else 0.0
        if self.grid_roofed(x, z) and "roof_no_cover" not in self.b:
            return floor
        e = 0.3 if "low_exposure" in self.b else 0.7 if "open_exposure_dimmed" in self.b else 1.0
        # the real shadegrid_read returns ExposureAt(cell), which has no weather factor (that is applied in
        # ExposureFor(pawn) only), so the gale never changes a cell read here either
        return max(e, floor)

    def t_shadegrid_read(self, cells=None, **k):
        rows = []
        for tok in (cells or "").split(";"):
            if tok:
                x, z = [int(v) for v in tok.split(",")]
                shade = 1.0 if self.grid_roofed(x, z) and "roof_no_cover" not in self.b else 0.0
                rows.append({"x": x, "z": z, "inBounds": True, "shade": shade, "exposure": self.exposure(x, z)})
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
            was = self.weather
            self.weather = weather
            self.locked = bool(lockWeather)
            # STILLSAND_RETURN_REMAINDER_1: the gale wipes the wet sand; its end opens the Return (ledger tier only)
            if weather == "RM_DuneGale" and "gale_keeps_wet" not in self.b:
                self.wet = set()
            if was == "RM_DuneGale" and weather != "RM_DuneGale" and "rm_tier" not in self.b \
                    and "gale_no_opening" not in self.b and self.ticks - self.lastopen >= 30000:
                self.serial += 1
                self.lastopen = self.ticks
                if self.believed:
                    self.oblig = 1
        return {"success": True}

    def t_jump_camera_to_cell(self, x=0, z=0, **k):
        self.camera = (x, z)
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
        return True

    def t_fire_incident(self, incidentDef=None, dryRun=False, points=None, **k):
        if dryRun:
            cf = self.can_fire(incidentDef)   # the live tool answers success=False when it cannot fire
            return {"success": bool(cf), "canFireNow": cf, "ticksGame": 134661}
        if incidentDef == "RM_MuurrokEmergence":
            self.letter("A line of glare")
            self.fire_muurrok()
        elif incidentDef == "RM_SandBusterEruption":
            self.letter("Sand Buster Eruption")
            self.new("RM_SandBusterTunnel", 60, 60)
            if "no_mound" not in self.b:
                self.sched.append((self.ticks + 1000, lambda: self.new("RM_SandBusterMound", 60, 60)))
        return {"success": True}

    def fire_muurrok(self):
        """The real visit's timeline (RM_SandLeviathan.cs): pending 1500 ticks, then up at the entry cell, then down
        again 700 ticks later (gave up on the gravel pad: >600 off sand). A single census at +2600, the 2026-10-07
        harness, reads 0 here: STILLSAND_MUURROK_EMERGENCE_1."""
        visit = {}
        self.lev_visits.append(visit)
        if "muurrok_never_arrives" in self.b:
            return

        def arrive():
            if "no_muurrok" in self.b:              # turned back: no standable entry cell
                self.lev_visits.remove(visit)
                return
            pid = self.add_pawn("RM_Muurrok", 10, 10)

            def dive():
                self.pawns[pid]["gone"] = True      # DeSpawn + PassToWorld: list_pawns no longer sees it
                if visit in self.lev_visits:
                    self.lev_visits.remove(visit)
            self.sched.append((self.ticks + 700, dive))
        # muurrok_arrives_late: up at +3500, past criterion A2's 3000-tick bound; a watch longer than 3000 would
        # count it and read PASS, so this break pins MUURROK_WINDOW_TICKS to the item's bound.
        self.sched.append((self.ticks + (3500 if "muurrok_arrives_late" in self.b else 1500), arrive))

    def t_map_comp_read(self, comp=None, members=None, **k):
        if comp != "RM_MapComponent_SandLeviathans":
            return {"success": False, "message": "No map component matches '%s'." % comp}
        if "muurrok_spawns_unforced" in self.b and not self.unforced_armed:
            self.unforced_armed = True              # a leviathan visit nobody forced (the control must see it)
            self.fire_muurrok()
        if "muurrok_pawn_unforced_no_visit" in self.b and not self.unforced_armed:
            # an unforced RM_Muurrok on list_pawns with NO component visit: only the control's pawn check sees it
            self.unforced_armed = True
            self.add_pawn("RM_Muurrok", 12, 12)
        body = ", ".join(["RimMandrake.Stillsand.RM_LeviathanVisit"] * min(12, len(self.lev_visits)))
        tail = " (%d total)" % len(self.lev_visits) if len(self.lev_visits) > 12 else ""
        return {"success": True, "compType": comp, "values": {"visits": "[" + body + "]" + tail}, "missing": [],
                "ticksGame": self.ticks}

    def t_storyteller_fire(self, incidentDef=None, dryRun=True, **k):
        hours = float(self.settings["horizonWarningHours"])
        warn = self.on("horizonWarningsEnabled") or "horizon_ignores_toggle" in self.b
        if warn and "no_horizon_letter" not in self.b:
            self.letter("Dust on the horizon: north-west")
        if warn:
            self.warned_fires = getattr(self, "warned_fires", 0) + 1
        blocked = "traders_blocked" in self.b    # no trader group can generate here (the pre-carriers-fix site)
        if blocked and not warn:
            return {"success": False, "fired": False, "canFireNow": True, "blockedByDialog": False}
        if warn and self.warned_fires == 2:
            # the second warned fire is the turned-back path: this site's vanilla refuses the group at the
            # delayed fire (validation.py's note), so no one arrives and the retry window ends in a letter
            if self.on("dustSettledLetterEnabled") and "no_settled_letter" not in self.b:
                self.sched.append((self.ticks + int(hours * 2500) + 2500,
                                   lambda: self.letter("The dust settled: the caravan turned back")))
        elif warn and "horizon_instant" not in self.b:
            if not blocked:
                self.sched.append((self.ticks + int(hours * 2500), lambda: self.add_pawn("Trader", 5, 5, "Guild")))
        else:
            self.add_pawn("Trader", 5, 5, "Guild")
        return {"success": True, "fired": True, "blockedByDialog": False}

    def t_incident_queue_peek(self, **k):
        return {"success": True, "queue": []}

    def t_static_call(self, type=None, method=None, args=None, **k):
        if type.endswith("RM_StillsandTraderProbe") and method == "Report":   # HORIZON_CARAVAN_VANILLA_REFUSES_1
            n = 0 if "traders_blocked" in self.b else 3
            return {"success": True, "result": "TRADERS biome=RM_Stillsand entryCell=True source=%d desperate=0 "
                    "generable=%d | OutlanderCivil:src=True,desp=False,carrierAllowed=%s,gen=%s" % (3, n, n > 0, n > 0)}
        if type.endswith("RM_TrackGridDiag") and method == "WakeTroughReport":   # STILLSAND_SAND_SWIM_REMAINDER_1
            return {"success": True, "result": "WAKETROUGH prints=%d total=0 all=0" % getattr(self, "trough", {}).get(args, 0)}
        if type.endswith("RM_GaleTakenProof") and method == "Registered":
            return {"success": True, "result": "GALETAKEN registered=%s" % ("gale_not_taker" not in self.b)}
        if type.endswith("RM_WaterLedgerProof"):     # WATER_LEDGER_DOUBLE_CHARGE_1's row
            self.debt = getattr(self, "debt", 0.0)
            rm = "rm_tier" in self.b
            if method == "ProofLedger":
                if rm:
                    return {"success": True, "result": "LEDGER live=%s debt=none def=none enabled=True countsHere=False"
                            % ("rm_ledger_live" in self.b)}
                return {"success": True, "result": "LEDGER live=True debt=%.3f def=RUT_SunDebt enabled=True countsHere=True"
                        % self.debt}
            if method == "ProofWetSand":    # STILLSAND_RETURN_REMAINDER_1 A3
                seen = self.camera is not None and "line_not_drawn" not in self.b
                drawn = len(self.wet) if seen and (self.on("drawReturnLine") or "line_ignores_toggle" in self.b) else 0
                return {"success": True, "result": "WET cells=%d live=%d inView=%d drawn=%d drawTick=%d now=%d setting=%s"
                        % (len(self.wet), len(self.wet), len(self.wet) if self.camera else 0, drawn, self.ticks, self.ticks, self.on("drawReturnLine"))}
            if rm:
                return {"success": True, "result": "REFUSED: no ledger def with a believer precept (this tier ships none)"}
            if method == "ProofBelieve":
                added, self.believed = not self.believed, True
                return {"success": True, "result": "BELIEVE added=%s ideo=Sun-Debt precept=RUT_Ritual_TheReturn ritual=True"
                        % added}
            if method == "ProofReturnState":
                return {"success": True, "result": "RETURN serial=%d obligations=%d sinceOpen=%d gap=30000 debt=%.3f ritual=%s"
                        % (self.serial, self.oblig, self.ticks - self.lastopen, self.debt, self.believed)}
            x, z = [int(v) for v in str(args).split(",")[:2]]
            if method == "ProofStillCycle":
                brine = [i for i, t in self.things.items() if t["def"] == "RM_Brine" and (t["x"], t["z"]) == (x, z)]
                if not brine:
                    return {"success": True, "result": "CYCLE ran=False feed=none still=T0"}
                del self.things[brine[0]]
                self.debt += 2.0 if "still_books_wrong" in self.b else 3.0
                self.new("RM_StilledWater", x + 1, z, stackCount=3)
                return {"success": True, "result": "CYCLE ran=True feed=RM_Brine units=1 litres=3 water=RM_StilledWater still=T0"}
            if method == "ProofReturnOutcome":
                x, z = [int(v) for v in str(args).split(",")[:2]]
                if not [t for t in self.things.values() if t["def"] == "RUT_DebtStone" and (t["x"], t["z"]) == (x, z)]:
                    return {"success": True, "result": "NONE: no building at %d,%d" % (x, z)}
                d0, b0 = self.debt, len(self.of("RM_Hourbloom"))
                if "return_no_pay" not in self.b:
                    self.debt = max(0.0, self.debt - 9.0)
                if "return_no_ring" not in self.b:
                    for i in range(8):
                        self.new("RM_Hourbloom", x + 2, z + i - 4)
                return {"success": True, "result": "OUTCOME debt0=%.3f debt1=%.3f bloom0=%d bloom1=%d stone=RUT_DebtStone"
                        % (d0, self.debt, b0, len(self.of("RM_Hourbloom")))}
            if method == "ProofDrinkHook":
                at = [t for t in self.things.values() if (t["x"], t["z"]) == (x, z)]
                if at and at[0]["def"] == "RM_GuzzkaEggUnfertilized":
                    self.debt += 0.0 if "egg_drink_free" in self.b else 6.0
                    return {"success": True, "result": "DRINK item=RM_GuzzkaEggUnfertilized bookedAtSource=False by=P1"}
                twice = "drink_double_charge" in self.b
                if twice:
                    self.debt += 1.0
                return {"success": True, "result": "DRINK item=RM_StilledWater bookedAtSource=%s by=P1" % (not twice)}
        return {"success": False, "message": "fake: unknown static %s.%s" % (type, method)}

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
        self.finish_bills()
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

    def t_pawn_force_incapacitate(self, pawn=None, action=None, **k):
        if action == "vanish" and pawn in self.pawns:
            del self.pawns[pawn]
            return {"success": True, "destroyedAfter": True}
        return {"success": pawn in self.pawns}

    def t_destroy_batch(self, rects="", categories="All", **k):
        rr = rect(rects)
        if "Pawn" in str(categories):    # live: refused; and no category ever removes a pawn
            return {"success": False, "message": "destroy_batch never removes pawns (DESTROY_BATCH_NEVER_KILLS_PAWNS_1)"}
        for tid in [i for i, t in self.things.items() if inrect(t["x"], t["z"], rr)]:
            del self.things[tid]
        return {"success": True}

    def t_set_terrain_batch(self, ops="", layer=None, **k):
        for op in ops.split(";"):
            name, r = op.split(":")
            self.terrain.append((rect(r), name))
        return {"success": True}

    def t_set_roof_batch(self, ops="", roofDef=None, **k):
        self.roofs.append((rect(ops), roofDef != "None", self.ticks))
        return {"success": True}

    def t_pawn_flight(self, pawn=None, **k):
        return {"success": True, "pawns": [{"id": pawn, "canEverFly": "no_fly" not in self.b,
                                            "maxFlightTimeStat": 30.0}]}

    def t_damage(self, damageDef=None, amount=10, thingId=None, **k):
        p = self.pawns.get(thingId)
        if p and p["kind"] == "RM_Vekka" and "no_surface" not in self.b:
            p["surf_until"] = self.ticks + 300
            p["h"].pop("RM_SandSubmerged", None)
        return {"success": True}

    def t_fishing(self, action="read", x=-1, z=-1, pawn=None, **k):
        deep = self.terr(x, z) == "RM_DeepSand"
        body = {"hasBody": deep, "type": "Freshwater"} if deep else {"hasBody": False}
        if deep:
            body["commonFish"] = ["Fish_Tilapia"] if "wrong_fish" in self.b else ["RM_DuneCrawler"]
            body["uncommonFish"] = []
        fish = getattr(self, "fish", {})
        r = {"success": True, "body": body, "fishOnMap": [{"def": d, "count": n} for d, n in fish.items()]}
        if pawn and deep:
            r.update(fishCell={"x": x, "z": z}, standSpot={"x": x - 1, "z": z}, jobTicks=7500)
        return r

    def t_ordered_job(self, pawnId=None, jobDef=None, targetAId=None, **k):
        b = self.b
        if jobDef == "Goto":
            p = self.pawns.get(pawnId)
            if p:
                if p["h"].get("RM_SandSubmerged") and "no_trough" not in b:
                    self.trough = getattr(self, "trough", {})
                    self.trough[pawnId] = self.trough.get(pawnId, 0) + 20
                p["x"], p["z"] = k.get("targetAX", p["x"]), k.get("targetAZ", p["z"])
            return {"success": True, "accepted": True}
        if jobDef == "Fish":
            def land():
                if "no_catch" not in b:
                    self.fish = getattr(self, "fish", {})
                    d = "Fish_Tilapia" if "wrong_fish" in b else "RM_DuneCrawler"
                    self.fish[d] = self.fish.get(d, 0) + 3
            self.sched.append((self.ticks + 7000, land))
            return {"success": True, "accepted": True}
        if jobDef == "AttackMelee":
            def strike(pawn=pawnId, tgt=targetAId):
                v, c = self.pawns.get(pawn), self.pawns.get(tgt)
                if not v or not c or c["dead"]:
                    return
                if c["kind"].startswith("Mech_") and v["h"].get("RM_SandSubmerged") and "mech_hurt" not in b:
                    return                                    # §4: the swimmer drops an attack on a dry body
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
                if sand:
                    self.wet |= set((egg["x"] + i, egg["z"] + j) for i in range(-1, 3) for j in (-1, 0, 1))
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

    # ---- glass live rows (STILLSAND_GLASS_CHAIN_REMAINDER_1): bills worked through a WorkGiver, drift clears
    GIVERS = {"RM_DoBillsSunTables": ("RM_SunFurnace", "RM_LensBench"), "DoBillsCook": ("RM_SolarOven",)}
    PRODUCTS = {"RM_MeltSunGlass": ("RM_SunGlass", 10, 900), "RM_GrindPrecisionLens": ("RM_PrecisionLens", 1, 3000),
                "CookMealSimple": ("MealSimple", 1, 1600)}

    def t_set_pawn_skill(self, **k):
        return {"success": True}

    def t_set_work_priority(self, **k):
        return {"success": True}

    def t_bill_add(self, giverId=None, recipe=None, **k):
        self.bills.setdefault(giverId, []).append(recipe)
        return {"success": True}

    def t_bill_remove(self, thingId=None, billIndex=0, confirmRemove=False, **k):
        if confirmRemove and self.bills.get(thingId):
            self.bills[thingId].pop(int(billIndex))
        return {"success": True}

    def sun_ok(self, t):
        if t["def"] == "RM_SolarOven" and "oven_in_shade" in self.b:
            return True
        if self.cur_weather() in ("RM_DuneGale", "Sandstorm") and "gale_ignored" not in self.b:
            return False
        return not self.roofed(t["x"], t["z"])

    def t_do_bill_now(self, pawnId=None, billGiverId=None, workGiverDef=None, **k):
        t = self.things[billGiverId]
        usable = t["def"] in self.GIVERS.get(workGiverDef, ()) and "no_workgiver" not in self.b
        any_bill = bool(self.bills.get(billGiverId))
        fuel_ok = self.on(self.table_toggle(t["def"])) and self.sun_ok(t)
        d = {"isBillGiver": True, "usableBillGiver": usable, "anyBillShouldDoNow": any_bill,
             "usableAfterFueling": fuel_ok}
        if not (usable and any_bill and fuel_ok):
            return {"success": False, "message": "JobOnThing returned null", "details": d}
        prod, n, work = self.PRODUCTS[self.bills[billGiverId][0]]
        if prod == "RM_PrecisionLens" and "lens_double" in self.b:
            n = 2
        self.pending.append((self.ticks + work, prod, n, t["x"], t["z"] - 1))
        return {"success": True, "accepted": True}

    def finish_bills(self):
        for job in [j for j in self.pending if j[0] <= self.ticks]:
            self.pending.remove(job)
            self.new(job[1], job[3], job[4], stackCount=job[2])

    def t_set_weather_buildup(self, kind=None, mode=None, rect=None, depth=0.0, **k):
        r = globals()["rect"](rect)
        self.sand[(r[0], r[1])] = float(depth)
        return {"success": True}

    def t_paint_area(self, **k):
        return {"success": True}

    def t_prioritized_work(self, pawnId=None, jobDef=None, workGiverDef=None, targetAX=-1, targetAZ=-1, **k):
        c = (targetAX, targetAZ)
        if jobDef != "ClearSnow" or workGiverDef != "CleanClearSnow" or not self.sand.get(c):
            return {"success": False}
        blocked = self.ext[(V.FLOWWORKS_SETTINGS, "shovelRequired")] == "True"   # FlowWorks' FailOn: no shovel
        dug = self.sand.pop(c)
        if not blocked and self.ext[(V.DUNES_SETTINGS, "clearYieldEnabled")] == "True" and "drift_no_yield" not in self.b:
            self.new("RM_GlassSand", c[0], c[1], stackCount=int(round(dug * 6)))
        return {"success": True}

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
    settle = V._settle_shade
    if "roof_read_before_rebuild" in broken:
        # HARNESS break (STILLSAND_ROOF_COVER_EXPOSURE_1 A1): the roof row reads in the roofing tick, before
        # the 2000-tick grid rebuild, as the 2026-10-07 live run did; every other settle still runs
        def settle_skipping_roof_row(t):
            cur = getattr(t, "_current", None)
            if getattr(cur, "name", None) != "sun_roof_cover_above_55deg":
                settle(t)
        V._settle_shade = settle_skipping_roof_row
    try:
        return _run(game)
    finally:
        V._settle_shade = settle


def _run(game):
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
    # STILLSAND_GLASS_CHAIN_REMAINDER_1 live rows A1-A3
    "no_workgiver": ["glass.furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof", "glass.oven_cooks_in_sun_not_shade"],
    "gale_ignored": ["glass.furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof"],
    "lens_double": ["glass.furnace_and_bench_cycle_in_sun_stop_in_gale_and_roof"],
    "oven_in_shade": ["glass.oven_cooks_in_sun_not_shade"],
    "oven_fuel": ["glass.oven_cooks_in_sun_not_shade"],
    "drift_no_yield": ["glass.drift_clear_drops_glass_sand"],
    # STILLSAND_RETURN_REMAINDER_1 live rows A1 and A3 (A2 is the rm_tier run in _main)
    "line_not_drawn": ["water.wet_line_drawn_then_gale_wipes"],
    "line_ignores_toggle": ["water.wet_line_drawn_then_gale_wipes"],
    "gale_keeps_wet": ["water.wet_line_drawn_then_gale_wipes"],
    "gale_no_opening": ["water.return_sun_debt_gale_opens_good_outcome_pays"],
    "egg_drink_free": ["water.return_sun_debt_gale_opens_good_outcome_pays"],
    "return_no_pay": ["water.return_sun_debt_gale_opens_good_outcome_pays"],
    "return_no_ring": ["water.return_sun_debt_gale_opens_good_outcome_pays"],
    "still_books_wrong": ["water.still_water_charged_once"],
    "drink_double_charge": ["water.still_water_charged_once"],
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
    "roof_read_before_rebuild": ["sun.sun_roof_cover_above_55deg"],
    # 0.7 still clears the 0.6 glare-blind bar, so only A2's "an open cell reads 1.0" can catch it
    "open_exposure_dimmed": ["sun.sun_roof_cover_above_55deg"],
    "oorrik_nre": ["fauna.fauna_spawns"],
    "no_fly": ["fauna.soorrak_can_fly"],
    "set_plants_drops": ["flora.flora_spawns"],
    "no_submerge": ["sandswim.vekka_submerges_on_sand"],
    "submerge_on_rock": ["sandswim.vekka_submerges_on_sand"],
    "no_funnel": ["sandswim.vekka_take_leaves_funnel"],
    "no_surface": ["sandswim.vekka_surfaces_when_struck"],
    "no_resubmerge": ["sandswim.vekka_surfaces_when_struck"],
    "mech_hurt": ["sandswim.vekka_spares_a_mech"],
    "no_trough": ["sandswim.vekka_wake_trough_record"],
    "no_catch": ["sandswim.stillsand_catch"],
    "wrong_fish": ["sandswim.stillsand_catch"],
    "wakes_below_threshold": ["zuurrik.zuurrik_below_threshold_dormant"],
    "no_wake": ["zuurrik.zuurrik_wakes_on_blood"],
    "no_strip": ["zuurrik.zuurrik_strips_blood"],
    "zuurrik_ignores_toggle": ["zuurrik.zuurrik_toggle_off_no_wake"],
    "bites_unwounded": ["zuurrik.zuurrik_spares_unwounded"],
    "no_bury": ["zuurrik.zuurrik_reburies_when_quiet"],
    "loomma_ignores_shade": ["loomma.loomma_sunstruck_open_vs_roofed"],
    "soorrak_nre": ["soorrak.soorrak_no_exceptions"],
    "soorrak_stuck": ["soorrak.soorrak_not_stuck"],
    "roundtrip_ignored": ["settings.%s_roundtrip" % f for f in ROUNDTRIP_FIELDS],
    # the open cell then sits on the glare floor, level with the roofed one: the roof shows no cover either
    "low_exposure": ["sun.sun_open_sand_full_exposure", "sun.sun_roof_cover_above_55deg"],
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
    "no_muurrok": ["muurrok.muurrok_emergence_fires"],
    "muurrok_never_arrives": ["muurrok.muurrok_emergence_fires"],
    "muurrok_arrives_late": ["muurrok.muurrok_emergence_fires"],
    "muurrok_spawns_unforced": ["muurrok.muurrok_absent_unforced"],
    "muurrok_pawn_unforced_no_visit": ["muurrok.muurrok_absent_unforced"],
    "beam_no_damage": ["muurrok.beam_burns_target"],
    "beam_ignores_toggle": ["muurrok.beam_toggle_off_blocked"],
    "no_mound": ["eruption.eruption_tunnel_then_mound"],
    "no_horizon_letter": ["horizon.horizon_warns_then_arrives"],
    "horizon_instant": ["horizon.horizon_warns_then_arrives"],
    "horizon_ignores_toggle": ["horizon.horizon_toggle_off_vanilla"],
    "no_settled_letter": ["horizon.horizon_dust_settled_letter"],
    "traders_blocked": ["horizon.horizon_warns_then_arrives"],
    "gale_not_taker": ["gale.gale_carry_is_a_taker_of_the_shared_service"],
    "caves_ignore_toggle": ["caves.genstep_off_no_cave_line"],
    "skeleton_ignores_toggle": ["caves.skeleton_placement_off_none"],
    "log_error": ["log.log_clean"],
}


SWIM_CS = os.path.join(ROOT, "src", "RimMandrake", "CreatureBehaviors", "Source", "RM_CompSandSwim.cs")
VEKKA_XML = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Vekka.xml")
ROCK = ("Gravel",)


def vekka_swim_terrains(cs_text, xml_text):
    """The terrain names RM_Vekka submerges in, read from the mod (not from the fake): its RM_SandSwimExtension
    swimTerrains when it lists any, else RM_SandSwimUtility.EnsureDefaults' name array. None = unreadable."""
    ext = re.search(r'RM_SandSwimExtension">(.*?)</li>\s*</modExtensions>', xml_text, re.S)
    if ext is None:
        return None
    st = re.search(r"<swimTerrains>(.*?)</swimTerrains>", ext.group(1), re.S)
    own = re.findall(r"<li>\s*(\w+)\s*</li>", st.group(1)) if st else []
    if own:
        return own
    m = re.search(r"void EnsureDefaults\(\).*?new\[\]\s*\{([^}]*)\}", cs_text, re.S)
    return re.findall(r'"(\w+)"', m.group(1)) if m else None


def vekka_rock_rows(cs_text, xml_text):
    """STILLSAND_SANDSWIM_GRAVEL_SUBMERGE_1: the live FAIL on acc_biomes (2026-10-08) was the harness (the gravel vekka
    walked onto sand; fixed in 749d6a0d30). This pins the mod half offline: the vekka's swim set holds sand, never rock."""
    got = vekka_swim_terrains(cs_text, xml_text)
    if not got:
        return ["vekka swim terrains unreadable from %s / %s" % (os.path.basename(SWIM_CS), os.path.basename(VEKKA_XML))]
    out = []
    if "Sand" not in got:
        out.append("vekka swim set %s lacks Sand" % got)
    if set(got) & set(ROCK):
        out.append("vekka swim set %s includes rock %s: it would submerge on Gravel" % (got, sorted(set(got) & set(ROCK))))
    return out


def vekka_rock_check(bad):
    cs, xml = open(SWIM_CS, encoding="utf-8").read(), open(VEKKA_XML, encoding="utf-8").read()
    bad.extend(vekka_rock_rows(cs, xml))
    # instrument probes: the reader must see the real set, and Gravel planted in either source must redden
    if vekka_swim_terrains(cs, xml) != ["Sand", "SoftSand", "RM_DeepSand"]:
        bad.append("probe: expected the default set Sand/SoftSand/RM_DeepSand, read %s" % vekka_swim_terrains(cs, xml))
    if not vekka_rock_rows(cs.replace('"RM_DeepSand"', '"RM_DeepSand", "Gravel"'), xml):
        bad.append("probe: Gravel planted in EnsureDefaults did not redden")
    planted = xml.replace("<submergedHediff>", "<swimTerrains><li>Sand</li><li>Gravel</li></swimTerrains><submergedHediff>", 1)
    if not vekka_rock_rows(cs, planted):
        bad.append("probe: Gravel planted in RM_Vekka swimTerrains did not redden")


def main():
    bad = []
    real_err = sys.stderr
    sys.stderr = open(os.devnull, "w")              # the suite's progress lines are for live runs
    try:
        return _main(bad)
    finally:
        sys.stderr = real_err


def trader_check_verdicts(bad):
    """HORIZON_CARAVAN_VANILLA_REFUSES_1 A1: trader_probe_check.verdict reads the probe line strictly."""
    ts = importlib.util.spec_from_file_location("trader_probe_check", os.path.join(HERE, "trader_probe_check.py"))
    T = importlib.util.module_from_spec(ts)
    ts.loader.exec_module(T)
    ok = "TRADERS biome=RM_Stillsand entryCell=True source=3 desperate=0 generable=%d | x"
    cases = [({"success": True, "result": ok % 2}, T.PASS), ({"success": True, "result": ok % 0}, T.FAIL),
             ({"success": True, "result": (ok % 2).replace("entryCell=True", "entryCell=False")}, T.FAIL),
             ({"success": True, "result": (ok % 2).replace("RM_Stillsand", "AridShrubland")}, T.UNMEASURED),
             ({"success": True, "result": "REFUSED: no current map"}, T.UNMEASURED),
             ({"success": False}, T.UNMEASURED), (None, T.UNMEASURED)]
    for reply, want in cases:
        got = T.verdict(reply)[0]
        if got != want:
            bad.append("trader_probe_check.verdict(%r) = %d, want %d" % (reply, got, want))


def trader_probe_points(bad):
    """HORIZON_CARAVAN_VANILLA_REFUSES_1 A1, 2026-11-03 live FAIL: the probe built PawnGroupMakerParms with points left at
    IncidentParms' default -1f, so PawnGroupMaker.CanGenerateFrom refused every Trader group (minimum 0). The engine's
    SpawnPawns passes ensureCanGenerateAtLeastOnePawn: true; the probe must too, and read the TILE's biome as the engine does."""
    src = open(os.path.join(HERE, "Source", "RM_StillsandTraderProbe.cs"), encoding="utf-8").read()
    if "GetDefaultPawnGroupMakerParms(PawnGroupKindDefOf.Trader, parms, true)" not in src:
        bad.append("RM_StillsandTraderProbe: GetDefaultPawnGroupMakerParms without ensureCanGenerateAtLeastOnePawn=true "
                   "(points -1 < 0 refuses every Trader group)")
    if "Find.WorldGrid[map.Tile].PrimaryBiome" not in src:
        bad.append("RM_StillsandTraderProbe: carrier check must read the tile's PrimaryBiome, as Trader.CanGenerateFrom does")


def _main(bad):
    vekka_rock_check(bad)
    trader_check_verdicts(bad)
    trader_probe_points(bad)
    healthy = run()
    # gale_dims_sun_exposure is UNMEASURED by design: no tool reads pawn exposure (see validation.py)
    # glass.recipe_toggles_hide_recipes: no bridge tool reads RecipeDef.AvailableNow (not a live criterion)
    owed = ("glass.recipe_toggles_hide_recipes",
            # STILLSAND_EVENT_CREATURES_REMAINDER_1: RSW/RUT content, not on the driven tier
            "remainder.remainder_horn_routs_and_logs_roll",
            "remainder.remainder_seep_incident_refuses_other_maps_roots_at_seep",
            "remainder.remainder_den_quest_generates", "remainder.remainder_charged_thumper_is_loudest",
            # STILLSAND_RETURN_REMAINDER_1 A2 reads only without the Utinni layer: the rm_tier run below
            "water.rm_tier_has_no_ledger")
    for k in owed:
        if healthy.get(k, ("",))[0] != "UNMEASURED":
            bad.append("%s should read UNMEASURED: %s" % (k, healthy.get(k)))
    notpass = dict((k, v) for k, v in healthy.items()
                   if v[0] != "PASS" and k != "gale.gale_dims_sun_exposure" and k not in owed)
    if healthy.get("gale.gale_dims_sun_exposure", ("",))[0] != "UNMEASURED":
        bad.append("gale.gale_dims_sun_exposure should read UNMEASURED: %s" % (healthy.get("gale.gale_dims_sun_exposure"),))
    n_comp = len(healthy)
    if notpass:
        bad.append("healthy run: %d of %d components not PASS: %s" % (len(notpass), n_comp, notpass))
    rm = run(["rm_tier"])     # STILLSAND_RETURN_REMAINDER_1 A2: the RM tier (no Utinni layer) has no ledger
    for k, want in (("water.rm_tier_has_no_ledger", "PASS"), ("water.pour_blooms_on_sand", "PASS"),
                    ("water.return_sun_debt_gale_opens_good_outcome_pays", "UNMEASURED"),
                    ("water.wet_line_drawn_then_gale_wipes", "PASS")):
        if rm.get(k, ("",))[0] != want:
            bad.append("rm_tier run: %s should read %s: %s" % (k, want, rm.get(k)))
    if run(["rm_tier", "rm_ledger_live"]).get("water.rm_tier_has_no_ledger", ("",))[0] != "FAIL":
        bad.append("rm_tier run with a live ledger and no def did not turn water.rm_tier_has_no_ledger red")
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
