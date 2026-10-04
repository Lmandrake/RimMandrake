#!/usr/bin/env python3
"""Offline selftest for BlueDesert's north-star suite (validation.py). No game, no bridge, no ModsConfig.

    python3 src/RimMandrake/BlueDesert/selftest_bluedesert.py

What it proves (BLUE_DESERT_FIRST_SCRIPT_1):
  1. HEALTHY: against a small fake game that behaves the way the mod's source and About.xml say it does,
     every component PASSes.
  2. MUTANTS: for each mechanic, switching ONE behaviour of the fake game off (or, for the one defect read
     out of the source, ON) makes the component that covers it FAIL, so each check can fail, and it breaks
     only its own chain. UNMEASURED cases (an order the bridge refuses, a settings dialog that never writes
     this mod's file) read UNMEASURED, never PASS and never FAIL.
  3. DEFAULTS: the suite's DEFAULTS table equals the C# field initialisers in RM_BlueDesertMod.cs.
  4. FLOOR: every declared toggle has a covering component.
  5. WALK: every `-> chain.component` arrow in the walk names a declared component and every component the
     suite declares (bar the site-setup ones) is cited by the walk.
  6. LINT: the static schema lint (northstar_driver/lint_calls.py) passes over this mod's script files.
The fake mirrors the SHAPES the suite assumes of the bridge; it cannot prove those shapes are what the live
bridge returns. That is the live run's job (the walk's anti-guessing notes list each assumed shape).
"""
import glob
import math
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                          # noqa: E402
from suite import _DeclarationProbe                                    # noqa: E402
from northstar_driver.session import FastSession                       # noqa: E402
from northstar_driver.transport import MockTransport, MockGame         # noqa: E402

FAILS = []
CFG = tempfile.mkdtemp(prefix="bdesert_cfg_")
os.environ["BLUEDESERT_CONFIG_DIR"] = CFG
time.sleep = lambda s: None            # the suite's Ultrafast poll sleeps 1 s per poll; the fake is instant


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


V = runner.load_validation(HERE)
import importlib.util                                                  # noqa: E402
_spec = importlib.util.spec_from_file_location("bd_validation_module", os.path.join(HERE, "validation.py"))
VM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VM)

AMB = 12.0                       # the fake site's outdoor temperature
NATIVE_KINDS = set(VM.NATIVES)
AUTHORED_WEATHER = {"Clear": 60.0, "RM_Haze": 15.0, "RM_IceSandDrift": 15.0, "RM_IceFog": 10.0, "Fog": 0.0,
                    "Rain": 0.0, "DryThunderstorm": 0.0, "RainyThunderstorm": 0.0, "FoggyRain": 0.0,
                    "SnowGentle": 0.0, "SnowHard": 0.0}


def _txt(v):
    return "True" if v is True else "False" if v is False else repr(float(v)) if isinstance(v, float) else str(v)


class FakeGame(MockGame):
    """Behaves the way the mod's source says unless `bugs` names a behaviour to break."""

    def __init__(self, bugs=()):
        MockGame.__init__(self, mods=("ludeon.rimworld",), sizex=250, sizez=250)
        self.bugs = set(bugs)
        self.settings = dict((k, _txt(v)) for k, v in VM.DEFAULTS.items())
        if "setting_default_wrong" in self.bugs:
            self.settings["masterEnabled"] = "False"
        self.weather_table = dict(AUTHORED_WEATHER)
        if "stock_rain" in self.bugs:
            self.weather_table["Rain"] = 10.0
        self.things = {}
        self.pawns_f = []
        self.rooms = []
        self.roads = set()
        self.conditions = []
        self.letters = []
        self.n = 100
        self.fast = False
        self.window = None
        self.cfg_t = 1000.0
        self.blocks = 0
        self.rolls = 0
        self.weather_now = "Clear"

    # ------------------------------------------------------------------ helpers
    def on(self, field):
        return self.settings[field] != "False"

    def num(self, field):
        return float(self.settings[field])

    @staticmethod
    def rect(s):
        x, z, w, h = [int(float(v)) for v in str(s).split(",")]
        return x, z, w, h

    @staticmethod
    def inr(px, pz, r):
        return r[0] <= px < r[0] + r[2] and r[1] <= pz < r[1] + r[3]

    def room_at(self, x, z):
        for r in self.rooms:
            if self.inr(x, z, r["rect"]):
                return r
        return None

    def roofed(self, x, z):
        for r in self.rooms:
            rx, rz, rw, rh = r["rect"]
            if rx < x < rx + rw - 1 and rz < z < rz + rh - 1:
                return True
        return False

    def new_thing(self, d, x, z, stack=1, **kw):
        self.n += 1
        th = dict(id="%s%d" % (d, self.n), d=d, x=x, z=z, stack=stack, acc=0, warm=0, growth=1.0)
        th.update(kw)
        self.things[th["id"]] = th
        return th

    def pawn(self, pid):
        return next((q for q in self.pawns_f if q["id"] == pid), None)

    def hed(self, q, d, sev=0.0001, part=None):
        q["health"]["hediffs"].append({"def": d, "label": d, "severity": sev, "part": part})

    def has(self, q, d):
        return next((h for h in q["health"]["hediffs"] if h["def"] == d), None)

    # ------------------------------------------------------------------ mechanics
    def blast(self, c, radius):
        for q in self.pawns_f:
            if q is c or q["dead"] or not q["spawned"]:
                continue
            if math.hypot(q["x"] - c["x"], q["z"] - c["z"]) <= radius:
                self.hed(q, "Burn", 0.3, "Torso")

    def kill(self, q, ddef, emp=False):
        if q["dead"]:
            return
        q["dead"] = True
        k, b = q["kindDef"], self.bugs
        master, native = self.on("masterEnabled"), self.on("nativeDetonationsEnabled")
        if k == "RM_Dorrak":
            self.blast(q, 3.9)
        elif k == "RM_Krissek" and "no_krissek_blast" not in b:
            if (native and master) or "krissek_toggle_ignored" in b:
                self.blast(q, 2.9)
        elif k == "RM_Vhaulk" and "vhaulk_never_blasts" not in b:
            ok = (native and master) or ("vhaulk_native_toggle_ignored" in b and master) \
                or ("vhaulk_master_ignored" in b and native)
            heat = ddef in ("Flame", "Burn")
            gate = emp or heat or "vhaulk_always_blasts" in b or \
                (not self.on("vhaulkHeatGateEnabled") and "heatgate_ignored" not in b)
            if ok and gate:
                self.blast(q, 15.0)

    def plant_blast_ok(self):
        if "no_plant_blast" in self.bugs:
            return False
        return (self.on("floraChainReactionsEnabled") or "plant_blast_ignores_toggle" in self.bugs) and \
            (self.on("masterEnabled") or "plant_blast_ignores_master" in self.bugs)

    def kill_plant(self, th):
        if th["id"] not in self.things:
            return
        del self.things[th["id"]]
        if self.plant_blast_ok():
            for o in [o for o in self.things.values() if o["d"] in VM.FLORA
                      and math.hypot(o["x"] - th["x"], o["z"] - th["z"]) <= 1.1]:
                self.kill_plant(o)

    def long_tick(self, th):
        b = self.bugs
        if not (self.on("floraChainReactionsEnabled") and self.on("masterEnabled")) and "warm_ignores_toggle" not in b:
            th["warm"] = 0
            return
        over = AMB > self.num("warmDetonationThresholdC") or "warm_ignores_threshold" in b
        if "warm_never" in b:
            over = False
        if over:
            th["warm"] += 1
            if th["warm"] >= 2:
                self.kill_plant(th)
        else:
            th["warm"] = 0

    def rare_tick(self, rack):
        b = self.bugs
        room = self.room_at(rack["x"], rack["z"])
        on = (self.on("coldSinkEnabled") and self.on("masterEnabled")) or "rack_ignores_toggle" in b
        if not (on and room and rack["fuel"] > 0 and room["temp"] > -5.0):
            return
        cap = max(0.01, self.num("coldSinkCapacityFactor"))
        if "rack_never_cools" not in b:
            room["temp"] -= 2.0
        if "rack_no_ice_use" not in b:
            blocks = 50.0 / (500.0 * cap)
            rack["fuel"] = max(0.0, rack["fuel"] - blocks)
            rack["melted"] += blocks
        while rack["melted"] >= 5.0 and "rack_no_drip" not in b:
            rack["melted"] -= 5.0
            self.new_thing("RM_BlueIceMeltwaterCan", rack["x"] + 1, rack["z"], 3)

    def mine_one(self, q):
        if not q["mine"]:
            return
        st = self.things.pop(q["mine"].pop(0), None)
        if not st:
            return
        b = self.bugs
        if "thaw_no_yield" not in b:
            self.new_thing("RM_BlueIce", st["x"], st["z"], 15)
        if ((self.on("thawRollEnabled") and self.on("masterEnabled")) or "thaw_ignores_toggle" in b) \
                and "thaw_never" not in b:
            self.blocks += 1
            if self.blocks % 3 == 0:
                self.rolls += 1
                if self.rolls % 3 != 0 or "thaw_ignores_toggle" in b:
                    self.new_thing("Steel", st["x"] + 1, st["z"], 20)

    def haze_cycle(self):
        b = self.bugs
        if not ((self.on("hazeExposureEnabled") and self.on("masterEnabled")) or "haze_ignores_toggle" in b):
            return
        for q in self.pawns_f:
            if q["dead"] or not q["spawned"] or "haze_never" in b:
                continue
            if q["kindDef"] in NATIVE_KINDS and "haze_hits_natives" not in b:
                continue
            if not self.has(q, VM.HAZE_FILM):
                self.hed(q, VM.HAZE_FILM, 0.0001)

    def haze_severity(self, dt):
        for q in self.pawns_f:
            f = self.has(q, VM.HAZE_FILM)
            if not f or q["dead"]:
                continue
            exposed = self.weather_now == "RM_Haze" and (not self.roofed(q["x"], q["z"]) or "haze_ignores_roof" in self.bugs)
            f["severity"] = max(0.0001, f["severity"] + (0.6 if exposed else -1.2) * dt / 60000.0)

    def sim(self, n):
        while n > 0:
            dt = min(n, 250)
            n -= dt
            self._step(dt)

    def _step(self, dt):
        b = self.bugs
        self.ticks += dt
        for th in list(self.things.values()):
            if th["id"] not in self.things:
                continue
            if th["d"] in VM.FLORA:
                th["acc"] += dt
                while th["acc"] >= 2000 and th["id"] in self.things:
                    th["acc"] -= 2000
                    self.long_tick(th)
            elif th["d"] == "RM_ColdWax":
                room = self.room_at(th["x"], th["z"])
                temp = room["temp"] if room else AMB
                if not th.get("ruined") and temp > -1.0:
                    th["ruin"] = th.get("ruin", 0.0) + (temp + 1.0) * 1e-5 * dt
                    if th["ruin"] >= 1.0:
                        th["ruined"] = True
                        if ((self.on("coldWaxWarmReactiveEnabled") and self.on("masterEnabled"))
                                or "wax_ignores_toggle" in b) and "wax_never_wicks" not in b:
                            th["wick"] = 100
                if th.get("wick") is not None:
                    th["wick"] -= dt
                    if th["wick"] <= 0:
                        del self.things[th["id"]]
            elif th["d"] == "RM_ColdSinkRack":
                th["acc"] += dt
                while th["acc"] >= 250:
                    th["acc"] -= 250
                    self.rare_tick(th)
        for r in self.rooms:
            r["temp"] += (AMB - r["temp"]) * 0.0004 * dt
        for q in self.pawns_f:
            if q["dead"] or not q["spawned"]:
                continue
            if q["mine"]:
                q["macc"] += dt
                while q["macc"] >= 450 and q["mine"]:
                    q["macc"] -= 450
                    self.mine_one(q)
            if q["kindDef"] == "RM_Vhaulk":
                self.vhaulk_step(q, dt)
        for c in self.conditions:
            c["acc"] += dt
            while c["acc"] >= 2500:
                c["acc"] -= 2500
                if c["def"] == VM.HAZE_CARRIER:
                    self.haze_cycle()
        self.haze_severity(dt)

    def vhaulk_step(self, q, dt):
        b = self.bugs
        if q.get("goto") is not None:
            gx, gz = q["goto"]
            step = min(abs(gx - q["fx"]), 0.02 * dt)
            q["fx"] += step if gx > q["fx"] else -step
            q["x"] = int(round(q["fx"]))
            q["racc"] += dt
            while q["racc"] >= 60:
                q["racc"] -= 60
                if (self.on("vhaulkRoadEnabled") and self.on("masterEnabled")) or "road_ignores_toggle" in b:
                    if "road_never" not in b:
                        for dx in range(-1, 2):
                            for dz in range(-1, 2):
                                self.roads.add((q["x"] + dx, q["z"] + dz))
                    for th in [o for o in self.things.values() if o["d"] in VM.FLORA
                               and math.hypot(o["x"] - q["x"], o["z"] - q["z"]) <= 2.9]:
                        if "crop_never" in b:
                            continue
                        if "crop_kills" in b:
                            del self.things[th["id"]]
                        else:
                            th["growth"] = min(th["growth"], 0.08)
        if q.get("depart") is not None and self.ticks >= q["depart"] and "never_departs" not in b \
                and (self.on("vhaulkDepartsEnabled") and self.on("masterEnabled")) and q["spawned"]:
            q["spawned"] = False
            if "silent_departure" not in b:
                self.letters.append({"label": VM.DEPARTURE_LABEL})

    # ------------------------------------------------------------------ handler
    def handle(self, tool, p):
        p = p or {}
        if tool == "rimworld/step_game_ticks":
            n = int(p.get("ticks") or 0)
            MockGame.handle(self, tool, dict(p, ticks=0))
            self.sim(n)
            return {"success": True}
        if tool == "rimworld/get_game_info":
            if self.fast:
                self.sim(3000)
            return MockGame.handle(self, tool, p)
        h = getattr(self, "t_" + re.sub(r"[^a-z_]", "_", tool.lower()), None)
        if h:
            return h(p)
        return MockGame.handle(self, tool, p)

    def t_rimworld_set_time_speed(self, p):
        self.fast = p.get("speed") == "Ultrafast"
        return {"success": True}

    def t_jawa_map_info(self, p):
        return {"success": True, "sizeX": 250, "sizeZ": 250, "mapBiome": "Tundra"}

    # -- defs
    def t_jawa_get_defs(self, p):
        known = set(VM.SHIPPED)
        if "def_missing" in self.bugs:
            known.discard("ThingDef/RM_Vhaulk")
        defs, nf = [], []
        for spec in str(p["defs"]).split(";"):
            if spec not in known:
                nf.append(spec)
                continue
            ty, nm = spec.split("/", 1)
            f = {}
            for fld in str(p.get("fields") or "").split(","):
                if not fld:
                    continue
                if ty == "BiomeDef" and fld == "baseWeatherCommonalities":
                    f[fld] = [{"weather": k, "commonality": v} for k, v in self.weather_table.items()]
                elif ty == "BiomeDef" and fld == "biomeMapConditions":
                    f[fld] = [] if "carrier_missing" in self.bugs else [VM.HAZE_CARRIER]
                elif ty == "IncidentDef" and fld == "allowedBiomes":
                    f[fld] = [] if "incident_ungated" in self.bugs else ["RM_BlueDesert"]
                elif ty == "WeatherDef" and fld == "modExtensions":
                    f[fld] = [] if "no_murrek_ext" in self.bugs else ["RimMandrake.BlueDesert.RM_MurrekReseedExtension"]
                elif fld == "defName":
                    f[fld] = nm
                else:
                    f[fld] = "(no such field)"
            defs.append({"defName": nm, "found": True, "fields": f})
        return {"success": True, "foundCount": len(defs), "notFound": nf, "defs": defs}

    def t_jawa_get_def(self, p):
        nm = p["defName"]
        comps = []
        if nm == "RM_BlueIceMineable":
            comps = ["RimMandrake.BlueDesert.RM_CompBlueIceThaw"]
        elif nm == "RM_ColdWax":
            comps = ["Verse.CompExplosive", "RimWorld.CompTemperatureRuinable",
                     "RimMandrake.BlueDesert.RM_CompRuinedDetonator"]
        elif nm == "RM_ColdSinkRack":
            comps = ["RimWorld.CompRefuelable", "RimWorld.CompTempControl", "RimMandrake.BlueDesert.RM_CompColdSink"]
            if "rack_powered" in self.bugs:
                comps.append("RimWorld.CompPowerTrader")
        elif nm in VM.FLORA and not (nm == "RM_Glassfern" and "plant_no_comp" in self.bugs):
            comps = ["RimMandrake.BlueDesert.CompPlantCharge"]
        else:
            comps = ["RimWorld.CompSomething"]
        return {"success": True, "defName": nm, "comps": [{"compClass": c} for c in comps]}

    def t_jawa_biome_probe(self, p):
        rows = []
        for q in str(p["find"]).split(","):
            state = "spawning"
            if q == "RM_Zhaaz" and "roster_hole" in self.bugs:
                state = "zeroed"
            if q == "AA_Thunderbeast":
                state = "absent"
            rows.append({"defName": q, "state": state, "present": state == "spawning"})
        return {"success": True, "biomes": [{"defName": "RM_BlueDesert", "findResults": rows,
                                             "animalDensity": 0.0 if "density_zero" in self.bugs else 0.5,
                                             "plantDensity": 0.33}]}

    # -- settings, weather, dialog
    def t_jawa_mod_settings_field(self, p):
        f = p.get("field")
        if f not in self.settings:
            return {"success": False, "message": "no such field"}
        if p.get("action") == "set":
            self.settings[f] = str(p["value"])
        return {"success": True, "value": self.settings[f]}

    def t_jawa_weather_set(self, p):
        if p.get("weather"):
            self.weather_now = p["weather"]
        return {"success": True}

    def t_jawa_weather_get(self, p):
        return {"success": True, "weather": {"current": self.weather_now},
                "conditions": [{"def": c["def"], "scope": "map"} for c in self.conditions]}

    def t_jawa_game_condition(self, p):
        if p.get("action") == "start":
            self.conditions.append({"def": p["condition"], "acc": 0})
        else:
            self.conditions = [c for c in self.conditions if c["def"] != p.get("condition")]
        return {"success": True}

    def t_rimworld_open_mod_settings(self, p):
        self.window = p.get("modId")
        return {"success": True}

    def t_jawa_window_list_close(self, p):
        w, self.window = self.window, None
        if not w or "dialog_unreachable" in self.bugs:
            return {"success": True}
        writes = (w == "mandrake.rm.biomes") if "first_id_wrong" not in self.bugs else (w == "mandrake.rm.bluedesert")
        if writes:
            path = os.path.join(CFG, "Mod_RimMandrake.Biomes_RM_BlueDesertMod.xml")
            open(path, "w").write("<x/>")
            self.cfg_t += 10.0
            os.utime(path, (self.cfg_t, self.cfg_t))
            if "apply_noop" not in self.bugs:
                on = self.on("masterEnabled") and self.on("ruledWeathersEnabled")
                for k in VM.RULED_WEATHERS:
                    self.weather_table[k] = AUTHORED_WEATHER[k] if on else 0.0
        return {"success": True}

    # -- things
    def t_jawa_list_things(self, p):
        wanted = set(d for d in str(p.get("defName") or "").split(",") if d)
        r = self.rect(p["rect"]) if p.get("rect") else None
        rows = [{"id": i["id"], "def": i["d"], "position": {"x": i["x"], "z": i["z"]}, "stackCount": i["stack"],
                 "hitPoints": 20, "maxHitPoints": 20}
                for i in self.things.values() if (not wanted or i["d"] in wanted) and (r is None or self.inr(i["x"], i["z"], r))]
        return {"success": True, "things": rows[:int(p.get("limit") or 200)], "countMatched": len(rows),
                "scanned": max(1, len(self.things)), "isCompleteList": True}

    def t_jawa_spawn_batch(self, p):
        for op in str(p["ops"]).split(";"):
            d, rest = op.split(":")
            a = [int(v) for v in rest.split(",")]
            kw = {"fuel": 0.0, "melted": 0.0} if d == "RM_ColdSinkRack" else {}
            self.new_thing(d, a[0], a[1], a[2] if len(a) > 2 else 1, **kw)
        return {"success": True}

    def t_jawa_set_plants(self, p):
        planted = 0
        for op in str(p["ops"]).split(";"):
            d, rest = op.split(":")
            a = [int(v) for v in rest.split(",")]
            w, h = (a[2] if len(a) > 2 else 1), (a[3] if len(a) > 3 else 1)
            for cx in range(a[0], a[0] + w):
                for cz in range(a[1], a[1] + h):
                    self.new_thing(d, cx, cz, 1, growth=float(p.get("growth") or 1.0))
                    planted += 1
        return {"success": True, "planted": planted}

    def t_jawa_destroy_batch(self, p):
        for rs in str(p["rects"]).split(";"):
            r = self.rect(rs)
            for i in [i for i in self.things.values() if self.inr(i["x"], i["z"], r)]:
                del self.things[i["id"]]
            self.rooms = [q for q in self.rooms if not (self.inr(q["rect"][0], q["rect"][1], r))]
        return {"success": True}

    def t_jawa_make_empty_room(self, p):
        r = self.rect(p["rect"])
        self.t_jawa_destroy_batch({"rects": p["rect"]})
        self.rooms.append({"rect": r, "temp": AMB})
        return {"success": True, "cellsWalled": 2 * (r[2] + r[3]) - 4}

    def t_jawa_get_roof_batch(self, p):
        r = self.rect(p["rects"])
        return {"success": True, "roofedCells": sum(1 for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])
                                                      if self.roofed(x, z))}

    def t_jawa_room_heat(self, p):
        room = self.room_at(p["x"], p["z"])
        if room is None:
            return {"success": False, "message": "no room"}
        room["temp"] = float(p["value"])
        return {"success": True}

    def t_jawa_cell_temperature(self, p):
        x, z = [int(v) for v in str(p["cell"]).split(",")]
        room = self.room_at(x, z)
        return {"success": True, "temperature": room["temp"] if room else AMB}

    def t_jawa_get_terrain_layers(self, p):
        r = self.rect(p["rect"])
        cells = [{"x": x, "z": z, "top": "Ice", "temp": "RM_RimeRoad" if (x, z) in self.roads else None}
                 for x in range(r[0], r[0] + r[2]) for z in range(r[1], r[1] + r[3])]
        return {"success": True, "count": len(cells), "cells": cells[:int(p.get("limit") or 200)]}

    def t_jawa_inspect_string(self, p):
        th = self.things.get(p["thingIds"])
        lines = []
        if th and th["d"] == "RM_ColdWax":
            lines = ["Ruined by temperature"] if th.get("ruined") else ["Ruining: %d%%" % (th.get("ruin", 0) * 100)]
        elif th and th["d"] == "RM_ColdSinkRack":
            held = th["fuel"] * self.num("coldSinkCapacityFactor")
            lines = ["Blue ice: %.1f / 30" % th["fuel"], "Ice: deep blue", "Cold held: %.2f h at full draw" % held]
        elif th and th["d"] in VM.FLORA:
            lines = ["Growth: %d%%" % round(th["growth"] * 100)]
        return {"success": True, "things": [{"id": p["thingIds"], "label": th["d"] if th else None, "inspect": lines}]}

    # -- pawns
    def t_jawa_spawn_pawn(self, p):
        self.n += 1
        k = p["kindDef"]
        q = {"id": "Pawn%d" % self.n, "x": p["x"], "z": p["z"], "fx": float(p["x"]), "kindDef": k, "kind": k,
             "faction": "PlayerColony" if p.get("faction") == "player" else None, "dead": False, "spawned": True,
             "health": {"hediffs": []}, "mine": [], "macc": 0, "racc": 0, "goto": None, "depart": None,
             "parts": {}, "intelligence": "Humanlike" if k == "Colonist" else "Animal"}
        if k in NATIVE_KINDS and not (k == "RM_Zhaaz" and "no_charge_hediff" in self.bugs):
            self.hed(q, VM.CHARGE_OF[k], 1.0)
        if k == "RM_Vhaulk":
            q["depart"] = self.ticks + max(0.1, self.num("vhaulkStayDaysFactor")) * 3.5 * 60000
        self.pawns_f.append(q)
        return {"success": True, "pawns": [{"id": q["id"]}]}

    def t_jawa_list_pawns(self, p):
        r = self.rect(p["rect"]) if p.get("rect") else None
        rows = []
        for q in self.pawns_f:
            if not q["spawned"] or (q["dead"] and not p.get("includeCorpses")):
                continue
            if r is not None and not self.inr(q["x"], q["z"], r):
                continue
            row = dict((k, q[k]) for k in ("id", "kindDef", "kind", "x", "z", "faction", "dead", "spawned", "intelligence"))
            if p.get("includeHealth"):
                row["health"] = {"hediffs": list(q["health"]["hediffs"])}
            rows.append(row)
        return {"success": True, "pawns": rows}

    def t_jawa_pawn_flight(self, p):
        return {"success": True, "pawns": [{"canEverFly": "vrisk_grounded" not in self.bugs}]}

    def t_jawa_damage(self, p):
        tid = p.get("thingId")
        ddef, amount, part = p["damageDef"], float(p["amount"]), p.get("bodyPart")
        th = self.things.get(tid)
        if th is not None:
            if th["d"] in VM.FLORA and amount >= 20:
                self.kill_plant(th)
            return {"success": True}
        q = self.pawn(tid)
        if q is None:
            return {"success": False, "message": "no such thing"}
        if q["dead"]:
            return {"success": True}
        if ddef == "EMP":
            ok = q["kindDef"] == "RM_Vhaulk" and (self.on("vhaulkEmpTrapEnabled") or "emp_toggle_ignored" in self.bugs) \
                and self.on("nativeDetonationsEnabled") and self.on("masterEnabled") and "emp_ignored" not in self.bugs
            if ok:
                self.kill(q, ddef, emp=True)
            return {"success": True}
        if part == "Brain" or part is None:
            self.kill(q, ddef)
            return {"success": True}
        q["parts"][part] = q["parts"].get(part, 0.0) + amount
        limit = {"Hump": 100.0, "Leg": 150.0}.get(part, 100.0)
        if q["parts"][part] >= limit and not any(h["def"] == "MissingBodyPart" and h["part"] == part
                                                  for h in q["health"]["hediffs"]):
            self.hed(q, "MissingBodyPart", 1.0, part)
            if part == "Hump" and "hump_no_kill" not in self.bugs and \
                    ((self.on("nativeDetonationsEnabled") and self.on("masterEnabled")) or "hump_ignores_toggle" in self.bugs):
                self.kill(q, ddef)
            if part == "Leg" and "leg_kills" in self.bugs:
                self.kill(q, ddef)
        return {"success": True}

    def t_jawa_ordered_job(self, p):
        if "no_ordered_job" in self.bugs:
            return {"success": False, "accepted": False}
        q = self.pawn(p.get("pawnId"))
        if q is None:
            return {"success": False, "accepted": False}
        job = p.get("jobDef")
        if job == "Refuel":
            rack, ice = self.things.get(p.get("targetAId")), self.things.get(p.get("targetBId"))
            if rack and ice:
                rack["fuel"] = min(30.0, float(ice["stack"]))
                del self.things[ice["id"]]
        elif job == "Mine":
            q["mine"].append(p["targetAId"])
        elif job == "Goto":
            q["goto"] = (p["targetAX"], p["targetAZ"])
        elif job == "Ingest":
            plant = self.things.pop(p.get("targetAId"), None)
            foreign = q["kindDef"] not in NATIVE_KINDS
            if plant and "butane_never" not in self.bugs and \
                    ((self.on("butaneGutEnabled") and self.on("masterEnabled")) or "butane_ignores_toggle" in self.bugs) \
                    and (foreign or "butane_native_not_exempt" in self.bugs):
                self.hed(q, "RM_ButaneGut", 0.25)
        return {"success": True, "accepted": True, "nowRunningRequested": True}

    def t_jawa_set_thing_props(self, p):
        return {"success": True, "changed": ["faction"]}

    def t_jawa_designate_batch(self, p):
        return {"success": True, "added": 1}

    def t_jawa_fire_incident(self, p):
        can = "incident_fires_anywhere" in self.bugs
        return {"success": can, "canFireNow": can, "fired": False}

    def t_jawa_static_call(self, p):
        """RM_BlueDesertSoundProof: a mini-model of RM_MapComponent_BlueDesertSoundscape.Rescan, judged with the
        same rules as the C# proof (which builds this answer live)."""
        b, mode, m = self.bugs, p.get("args"), p.get("method")
        if p.get("type") != "RimMandrake.BlueDesert.RM_BlueDesertSoundProof" or "proof_unanswered" in b:
            return {"success": False, "error": "no such type"}
        on = mode != "off"
        if m == "ProofChoir":
            gate = on or "choir_ignores_toggle" in b
            sing = gate and "choir_never_sings" not in b
            silenced = sing and "choir_not_silenced" not in b
            echo = sing and "choir_no_echo" in b
            st = "alone=%s silenced=%s echo=%s" % (sing, silenced, echo)
            if on:
                if not sing:
                    return {"success": True, "result": "FAIL: a lone pack of 4 does not sing " + st}
                if not silenced:
                    return {"success": True, "result": "FAIL: a muffalo 5 cells away did not silence the choir " + st}
                if echo:
                    return {"success": True, "result": "FAIL: no echo hold " + st}
                return {"success": True, "result": "PASS " + st}
            return {"success": True, "result": ("FAIL: off but sang " if sing else "PASS off ") + st}
        if m == "ProofVirr":
            if self.weather_now != "RM_IceSandDrift":
                return {"success": True, "result": "UNMEASURED: wind 0.10 below the singing threshold"}
            gate = on or "virr_ignores_toggle" in b
            sing = gate and "virr_never" not in b
            young, ripe = 0.85 + 0.0, (0.85 if "virr_pitch_flat" in b else 1.35)
            st = "young=%s@%.2f ripe=%s@%.2f" % (sing, young, sing, ripe)
            if on:
                if not sing:
                    return {"success": True, "result": "FAIL: does not sing " + st}
                if ripe <= young:
                    return {"success": True, "result": "FAIL: pitch does not climb with ripeness " + st}
                return {"success": True, "result": "PASS " + st}
            return {"success": True, "result": ("FAIL: off but sang " if sing else "PASS off ") + st}
        return {"success": False, "error": "no such method"}

    def t_jawa_letter_list(self, p):
        return {"success": True, "count": len(self.letters), "letters": list(self.letters)}

    def t_jawa_drain_log(self, p):
        msgs = []
        if p.get("contains") == "BlueDesert" and "log_error" in self.bugs:
            msgs = [{"text": "[BlueDesert] something went wrong"}]
        return {"success": True, "totalInBuffer": 50, "messages": msgs}


def run(bugs=()):
    g = FakeGame(bugs=bugs)
    s = FastSession(transport=MockTransport(g), strict=False)
    for f in glob.glob(os.path.join(CFG, "*.xml")):
        os.remove(f)
    with s:
        res = runner.run_suite(V, s, anchor=(126, 126), mod=None)
    return dict(("%s/%s" % (ch["name"], c["name"]), (c["verdict"], c.get("detail"))) for ch in res["chains"]
                for c in ch["components"])


def declared():
    out = []
    for name, fn in V.chains:
        p = _DeclarationProbe()
        p.upstream_failed = False
        fn(p)
        out.extend("%s/%s" % (name, c.name) for c in p.components)
    return out


# bug -> the component that must go FAIL for it
MUTANTS = {
    "def_missing": "defs/defs_resolve",
    "stock_rain": "defs/biome_weather_table",
    "carrier_missing": "defs/biome_carrier_condition",
    "roster_hole": "defs/biome_roster_and_density",
    "density_zero": "defs/biome_roster_and_density",
    "plant_no_comp": "defs/charge_comps_wired",
    "rack_powered": "defs/rack_needs_no_power",
    "incident_ungated": "defs/ablation_and_murrek_wired",
    "no_murrek_ext": "defs/ablation_and_murrek_wired",
    "setting_default_wrong": "settings/defaults",
    "no_charge_hediff": "fauna/natives_spawn_charged",
    "vrisk_grounded": "fauna/vrisk_can_fly",
    "hump_no_kill": "dorrak_hump/hump_hit_kills",
    "leg_kills": "dorrak_hump/leg_hit_does_not_kill",
    "hump_ignores_toggle": "dorrak_hump/hump_toggle_off_ordinary_part",
    "no_krissek_blast": "krissek_blast/krissek_death_blasts",
    "krissek_toggle_ignored": "krissek_blast/krissek_off_quiet",
    "no_plant_blast": "flora_chain/plant_death_chains",
    "plant_blast_ignores_toggle": "flora_chain/plant_death_toggle_off_no_chain",
    "plant_blast_ignores_master": "flora_chain/plant_death_master_off_no_chain",
    "warm_never": "flora_warm/warm_detonates_plants",
    "warm_ignores_threshold": "flora_warm/warm_threshold_above_keeps_plants",
    "warm_ignores_toggle": "flora_warm/warm_toggle_off_keeps_plants",
    "butane_never": "butane/foreign_grazer_takes_butane_gut",
    "butane_native_not_exempt": "butane/native_grazer_exempt",
    "butane_ignores_toggle": "butane/butane_toggle_off_clean",
    "wax_never_wicks": "cold_wax/wax_ruined_wicks_and_goes",
    "wax_ignores_toggle": "cold_wax/wax_toggle_off_ruined_but_inert",
    "rack_never_cools": "cold_rack/rack_cools_loaded_room_only",
    "rack_no_ice_use": "cold_rack/rack_spends_ice_and_drips",
    "rack_no_drip": "cold_rack/rack_spends_ice_and_drips",
    "rack_ignores_toggle": "cold_rack/rack_toggle_off_leaves_room_alone",
    "thaw_ignores_toggle": "thaw/thaw_toggle_off_mines_cleanly",
    "thaw_no_yield": "thaw/thaw_toggle_off_mines_cleanly",
    "thaw_never": "thaw/thaw_roll_finds_debris",
    "vhaulk_never_blasts": "vhaulk_gates/heat_kill_detonates",
    "vhaulk_always_blasts": "vhaulk_gates/kinetic_kill_does_not",
    "emp_ignored": "vhaulk_gates/emp_on_living_detonates",
    "heatgate_ignored": "vhaulk_gates/heat_gate_off_any_death_detonates",
    "emp_toggle_ignored": "vhaulk_gates/emp_trap_off_is_ordinary_damage",
    "vhaulk_native_toggle_ignored": "vhaulk_gates/native_toggle_off_no_blast",
    "vhaulk_master_ignored": "vhaulk_gates/master_off_no_blast",
    "road_never": "vhaulk_road/road_laid_and_flora_cropped",
    "crop_never": "vhaulk_road/road_laid_and_flora_cropped",
    "crop_kills": "vhaulk_road/road_laid_and_flora_cropped",
    "road_ignores_toggle": "vhaulk_road/road_toggle_off_walks_clean",
    "never_departs": "vhaulk_departs/vhaulk_walks_off_with_a_letter",
    "silent_departure": "vhaulk_departs/vhaulk_walks_off_with_a_letter",
    "haze_never": "haze/haze_film_on_outdoor_colonist",
    "haze_ignores_roof": "haze/haze_film_on_outdoor_colonist",
    "haze_hits_natives": "haze/haze_spares_natives",
    "haze_ignores_toggle": "haze/haze_toggle_off_new_arrival_clean",
    "apply_noop": "weather_apply/ruled_weathers_toggle_applies",
    "incident_fires_anywhere": "ablation_gate/ablation_only_in_blue_desert",
    "log_error": "log/log_clean",
    "choir_never_sings": "soundscape/choir_sings_and_falls_silent",
    "choir_not_silenced": "soundscape/choir_sings_and_falls_silent",
    "choir_no_echo": "soundscape/choir_sings_and_falls_silent",
    "choir_ignores_toggle": "soundscape/choir_toggle_off_silent",
    "virr_never": "soundscape/virr_sings_in_wind_pitch_climbs",
    "virr_pitch_flat": "soundscape/virr_sings_in_wind_pitch_climbs",
    "virr_ignores_toggle": "soundscape/virr_toggle_off_silent",
}

# bug -> {component: expected non-PASS verdict} for cases that must read UNMEASURED (never a pass or a fail)
UNMEASURED_CASES = {
    "proof_unanswered": {"soundscape/choir_sings_and_falls_silent": "UNMEASURED",
                         "soundscape/virr_toggle_off_silent": "UNMEASURED"},
    "dialog_unreachable": {"weather_apply/ruled_weathers_toggle_applies": "UNMEASURED"},
    "no_ordered_job": {"butane/foreign_grazer_takes_butane_gut": "UNMEASURED",
                       "cold_rack/rack_site_ready": "UNMEASURED", "thaw/thaw_toggle_off_mines_cleanly": "UNMEASURED",
                       "vhaulk_road/road_laid_and_flora_cropped": "UNMEASURED"},
}


def main():
    names = declared()
    check("the suite declares its components (sanity probe: the declaration scan saw them)", len(names) >= 55,
          str(len(names)))

    # --- 1 healthy
    h = run()
    bad = [(k, v) for k, v in h.items() if not v[0].startswith("PASS")]
    check("healthy: every component PASSes", not bad, str(bad)[:1500])
    check("healthy: the components ran at all (== declared)", sorted(h) == sorted(names),
          str(sorted(set(names) ^ set(h)))[:300])

    # --- the first-try dialog candidate being wrong must still PASS (the second candidate writes)
    r = run(bugs=("first_id_wrong",))
    check("first dialog candidate is the wrong page: the second one is tried and the check PASSes",
          r["weather_apply/ruled_weathers_toggle_applies"][0] == "PASS", str(r["weather_apply/ruled_weathers_toggle_applies"]))

    # --- 2 mutants: one behaviour off -> the covering component FAILs, and only its own chain is affected
    for bug, comp in sorted(MUTANTS.items()):
        r = run(bugs=(bug,))
        check("mutant %-30s -> %s FAILs" % (bug, comp), r[comp][0] == "FAIL", str(r[comp]))
        others = [k for k, v in h.items() if v[0].startswith("PASS") and r.get(k, ("",))[0] == "FAIL" and k != comp]
        if bug == "setting_default_wrong":
            # masterEnabled reading False is a site fault that really does stop every mechanic: the preflight
            # (northstar_site.preflight) refuses it before any chain runs; here only the defaults check must see it
            continue
        check("mutant %-30s breaks only its own chain" % bug,
              all(k.split("/")[0] == comp.split("/")[0] for k in others), str(others))

    # --- UNMEASURED cases never read PASS or FAIL
    for bug, want in sorted(UNMEASURED_CASES.items()):
        r = run(bugs=(bug,))
        for comp, verdict in sorted(want.items()):
            check("case %-20s -> %s reads %s" % (bug, comp, verdict), r[comp][0] == verdict, str(r[comp]))

    # --- 3 defaults == the C# initialisers, and every public static field is a declared setting
    cs = open(os.path.join(HERE, "Source", "RM_BlueDesertMod.cs"), encoding="utf-8").read()
    body = cs.split("class RM_BlueDesertSettings")[1].split("ExposeData")[0]
    fields = dict(re.findall(r"public static (?:bool|float) (\w+) = ([^;]+);", body))

    def val(s):
        s = s.strip()
        return True if s == "true" else False if s == "false" else float(s.rstrip("f"))
    cs_def = dict((k, val(v)) for k, v in fields.items())
    check("sanity probe: the C# scan saw >= 20 settings fields", len(cs_def) >= 20, str(len(cs_def)))
    check("the suite's DEFAULTS equal the C# field initialisers", cs_def == VM.DEFAULTS,
          str(dict((k, (cs_def.get(k), VM.DEFAULTS.get(k))) for k in set(cs_def) | set(VM.DEFAULTS)
                   if cs_def.get(k) != VM.DEFAULTS.get(k))))
    check("every settings field is a declared toggle", sorted(cs_def) == sorted(V.toggles),
          str(sorted(set(cs_def) ^ set(V.toggles))))

    # --- 4 floor
    decl = V.components_declared()
    covered = set(c["toggle"] for c in decl if c["toggle"])
    check("every declared toggle has a covering component", set(V.toggles) <= covered, str(sorted(set(V.toggles) - covered)))

    # --- 5 walk <-> suite
    walk = open(os.path.join(ROOT, "design", "validation_walks", "RimMandrake", "BlueDesert.md"), encoding="utf-8").read()
    must = walk.split("## must be true")[1].split("## the walk")[0]
    cited = set("%s/%s" % m for m in re.findall(r"→ (?:UNCOVERED:[^\n]*?→ )?([a-z_]+)\.([A-Za-z_0-9]+)", must))
    cited |= set("%s/%s" % m for m in re.findall(r"([a-z_]+)\.([A-Za-z_0-9]+)", " ".join(
        l for l in must.splitlines() if "→" in l)) if "/" not in m[0])
    cited = set(c for c in cited if c.split("/")[0] in set(n.split("/")[0] for n in names))
    missing = sorted(c for c in cited if c not in names)
    check("every arrow in the walk names a declared component", not missing, str(missing))
    site_setup = [n for n in names if n.split("/")[1].endswith("_site_ready")]
    uncited = sorted(n for n in names if n not in cited and n not in site_setup)
    check("every declared component (bar site setup) is cited by the walk", not uncited, str(uncited))
    lines = [l for l in must.splitlines() if l.startswith("- ")]
    noarrow = [l[:80] for l in lines if "→" not in l]
    check("every must-be-true line carries an arrow", not noarrow, str(noarrow))
    check("sanity probe: the walk has >= 40 must-be-true lines", len(lines) >= 40, str(len(lines)))

    # --- 5b the preflight's tool list covers every tool the suite calls
    sys.path.insert(0, HERE)
    import northstar_site                                              # noqa: E402
    used = set(re.findall(r'"((?:jawa|rimworld)/[a-z_]+)"', open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()))
    check("sanity probe: the tool scan saw >= 30 tools", len(used) >= 30, str(len(used)))
    check("northstar_site.TOOLS_NEEDED covers every tool validation.py calls", used <= set(northstar_site.TOOLS_NEEDED),
          str(sorted(used - set(northstar_site.TOOLS_NEEDED))))

    # --- 6 lint
    lint = os.path.join(UTILS, "northstar_driver", "lint_calls.py")
    p = subprocess.run([sys.executable, lint, "--summary", HERE], capture_output=True, text=True)
    check("the static schema lint passes over this mod's script files", p.returncode == 0, (p.stdout + p.stderr)[-400:])

    print("\n%s" % ("ALL OK" if not FAILS else "FAILED: %s" % FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
