"""SprinklerFakeBridge -- the offline stand-in sprinkler_live.py --mock runs against (no game, no bridge).

A small world model, NOT the mod: just enough pump / pipe / tank / sprinkler-pulse / power-switch timing for every row's
control flow to run. The timing that matters (2026-10-18, 58e9f914a5): a new head pulses at its first rare tick (phase
(tick + thingIDNumber) % 250 == 0, then every 2,500 ticks); vanilla PowerNet switches a NEW consumer on only when
TicksGame % 200 == 0. A pulse landing in that gap reads "No pressure" and holds for 2,500 ticks. Radius 2.9 = 29 cells,
5 dL a cell a pulse, wet for 2,750 ticks (RM_SprinklerKernel.WetUntil). A mock PASS proves the driver's logic, never the
mod; result files say mode "mock" so validation.py refuses them.

faults (name -> intended effect):
  pump_ignores_setting  liquidPumpEnabled=false does not stop the pump        -> sprinkler.no_pressure FAIL
  switch_ignored        sprinklersEnabled=false still sprays                    -> sprinkler_switch_flips FAIL
  free_spray            the tank is not drained                                 -> sprinkler.draws_and_wets FAIL
  soak_forever          wet cells never dry                                     -> sprinkler.dries_when_starved FAIL
  thick_sprays          tar is sprayed                                          -> sprinkler.thick_clogs FAIL
  wall_leak             walls do not stop the spray                             -> sprinkler.walls_stop_spray FAIL
  brine_sprays          brine is sprayed                                        -> T22_no_brine_spray FAIL
  acid_harmless         acid does no harm                                       -> sprinkler.acid_hurts_fuel_puddles FAIL
  no_filth              chemfuel leaves no filth                                -> sprinkler.acid_hurts_fuel_puddles FAIL
  no_reserve            the drinking reserve is ignored                         -> T21_drinking_reserve FAIL
  no_drink              a thirsty colonist never drinks at the tank             -> T21_drinking_reserve FAIL
  spawn_fail            jawa/spawn_pawn gives no pawn                           -> the driver RAISES (never a MOD verdict)
  no_biomes             mandrake.rm.biomes absent; IsSoaked unavailable         -> draws / dries / walls UNMEASURED SITE
"""
import re

SETTINGS0 = {"sprinklersEnabled": True, "sprinklerNonWaterEffects": True, "liquidPumpEnabled": True,
             "drinkingReserveLitres": 200.0}
PULSE = 2500
WET_FOR = PULSE + 250
SPRAYABLE = {"RM_Liquid_FreshWater": "fresh water", "RM_Liquid_AcidWater": "acid water", "RM_Liquid_Chemfuel": "chemfuel"}
THICK = ("RM_Liquid_Tar",)


def _rect(s):
    return tuple(int(v) for v in str(s).split(","))


def _in(r, x, z):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


class SprinklerFakeBridge(object):
    def __init__(self, faults=(), start_tick=2):
        self.faults = set(faults)
        self.tick = int(start_tick)
        self.nid = 0
        self.things = {}
        self.tanks = {}
        self.heads = {}
        self.powered = {}
        self.charged = set()
        self.soaked = {}
        self.pawns = {}
        self.settings = dict(SETTINGS0)
        self.counters = {"Pulses": 0, "SprayedUnits": 0}
        self.calls = []
        self.pulse_log = []

    # ------------------------------------------------------------ world
    def _thing(self, defn, x, z):
        self.nid += 1
        t = {"id": self.nid, "num": self.nid, "def": defn, "x": x, "z": z}
        self.things[t["id"]] = t
        if defn == "RM_LiquidTank":
            self.tanks[t["id"]] = {"liquid": "RM_Liquid_FreshWater", "units": 0}
        elif defn == "RM_SprinklerHead":
            self.heads[t["id"]] = {"next": -1, "line": "Not pulsed yet", "cells": 0}
        return t

    def _of(self, defn):
        return [t for t in self.things.values() if t["def"] == defn]

    def _cells_of(self, t):
        if t["def"] == "RM_LiquidTank":
            return [(t["x"] + i, t["z"] + j) for i in (0, 1) for j in (0, 1)]
        return [(t["x"], t["z"])]

    def _remove(self, t):
        self.things.pop(t["id"], None)
        self.tanks.pop(t["id"], None)
        self.heads.pop(t["id"], None)
        self.powered.pop(t["id"], None)

    # ------------------------------------------------------------ time
    def advance(self, n):
        for _ in range(n):
            self.tick += 1
            if self.tick % 200 == 0:        # vanilla PowerNet.PowerNetTick: a NEW consumer switches on only here
                for p in self._of("RM_LiquidPump"):
                    if self._has("PowerConduit", p["x"], p["z"] - 1) and any(b == (p["x"], p["z"] - 4) for b in self.charged):
                        self.powered[p["id"]] = True
            for hid, h in list(self.heads.items()):
                t = self.things[hid]
                if (self.tick + t["num"]) % 250 == 0 and (h["next"] < 0 or self.tick >= h["next"]):
                    h["next"] = self.tick + PULSE
                    self._pulse(t, h)

    def _has(self, defn, x, z):
        return any(t["def"] == defn and (t["x"], t["z"]) == (x, z) for t in self.things.values())

    def ticks(self, n):
        self.advance(int(n))
        return {"success": True, "advanced": int(n)}

    # ------------------------------------------------------------ the pulse
    def _net(self, hx, hz):
        pipes = set((t["x"], t["z"]) for t in self._of("RM_UniversalPipe"))
        seen, todo = set(), [(hx, hz)]
        while todo:
            c = todo.pop()
            if c in seen or c not in pipes:
                continue
            seen.add(c)
            todo += [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]
        pumps = [p for p in self._of("RM_LiquidPump") if (p["x"], p["z"]) in seen]
        tanks = []
        for t in self._of("RM_LiquidTank"):
            for (cx, cz) in self._cells_of(t):
                if any(abs(cx - sx) + abs(cz - sz) == 1 for (sx, sz) in seen):
                    tanks.append(t)
                    break
        return pumps, tanks

    def _covered(self, hx, hz):
        walls = set((t["x"], t["z"]) for t in self._of("Wall"))
        out = []
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if dx * dx + dz * dz > 9:
                    continue
                blocked = False
                n = max(abs(dx), abs(dz))
                for s in range(1, n):
                    px, pz = hx + int(round(dx * s / float(n))), hz + int(round(dz * s / float(n)))
                    if (px, pz) in walls and "wall_leak" not in self.faults:
                        blocked = True
                if not blocked:
                    out.append((hx + dx, hz + dz))
        return out

    def _pulse(self, t, h):
        self.counters["Pulses"] += 1
        hx, hz = t["x"], t["z"]
        if not self.settings["sprinklersEnabled"] and "switch_ignored" not in self.faults:
            h["line"] = "Sprinklers are off in Mod Settings"
            return
        pumps, tanks = self._net(hx, hz)
        pump_ok = any(self.powered.get(p["id"]) and (self.settings["liquidPumpEnabled"] or "pump_ignores_setting" in self.faults)
                      for p in pumps)
        if not pump_ok:
            h["line"] = "No pressure: no pump on this network"
            self.pulse_log.append((self.tick, "nopressure"))
            return
        res_units = int(self.settings["drinkingReserveLitres"] * 10) if "no_reserve" not in self.faults else 0
        ok = None
        thick = False
        for tk in tanks:
            st = self.tanks[tk["id"]]
            liq = st["liquid"]
            if liq in THICK and "thick_sprays" not in self.faults:
                thick = thick or st["units"] > 0
                continue
            sprayable = liq in SPRAYABLE or (liq == "RM_Liquid_Brine" and "brine_sprays" in self.faults) or \
                (liq in THICK and "thick_sprays" in self.faults)
            if not sprayable:
                continue
            avail = st["units"] - (res_units if liq == "RM_Liquid_FreshWater" else 0)
            if avail > 0 and (ok is None or (liq == "RM_Liquid_FreshWater" and self.tanks[ok["id"]]["liquid"] != liq)):
                ok = tk
        cells = self._covered(hx, hz)
        need = len(cells) * 5
        if ok is None:
            h["line"] = "Clogged: tar too thick to spray" if thick else "Dry: nothing in the tanks on this network"
            return
        st = self.tanks[ok["id"]]
        liq = st["liquid"]
        avail = st["units"] - (res_units if liq == "RM_Liquid_FreshWater" else 0)
        if avail < need:
            h["line"] = "Dry: nothing in the tanks on this network"
            return
        if "free_spray" not in self.faults:
            st["units"] -= need
        self.counters["SprayedUnits"] += need
        h["cells"] = len(cells)
        h["line"] = "Spraying %s on %d cells" % (SPRAYABLE.get(liq, liq), len(cells))
        self.pulse_log.append((self.tick, "spray"))
        for c in cells:
            self.soaked[c] = float("inf") if "soak_forever" in self.faults else self.tick + WET_FOR
        eff = self.settings["sprinklerNonWaterEffects"]
        if eff and liq == "RM_Liquid_AcidWater" and "acid_harmless" not in self.faults:
            for p in self.pawns.values():
                if (p["x"], p["z"]) in cells:
                    p["hediffs"].append({"def": "Burn", "severity": 0.3})
        if eff and liq == "RM_Liquid_Chemfuel" and "no_filth" not in self.faults:
            for c in cells[:6]:
                self._thing("Filth_Fuel", c[0], c[1])

    # ------------------------------------------------------------ bridge surface
    def call(self, tool, **kw):
        self.calls.append(tool)
        fn = getattr(self, "t_" + re.sub(r"[^a-z0-9]", "_", tool.lower()), None)
        if fn is None:
            return {"success": True}
        r = fn(**kw)
        return r if r is not None else {"success": True}

    def hp(self, cmd, wait_s=20.0):
        m = re.match(r"tank:(-?\d+),(-?\d+)", cmd)
        if m:
            x, z = int(m.group(1)), int(m.group(2))
            for t in self._of("RM_LiquidTank"):
                if (t["x"], t["z"]) == (x, z):
                    return {"success": True, "units": self.tanks[t["id"]]["units"]}
        return {"success": False, "error": "no tank"}

    def t_rimworld_get_game_info(self, **kw):
        return {"success": True, "ticksGame": self.tick}

    def t_jawa_running_mods(self, **kw):
        ids = ["ludeon.rimworld", "mandrake.rm.flowworks"] + ([] if "no_biomes" in self.faults else ["mandrake.rm.biomes"])
        return {"success": True, "packageIds": ids}

    def t_jawa_type_probe(self, **kw):
        return {"success": True, "mvidMatchesFile": True, "assemblyFileSha256": "00" * 32}

    def t_jawa_mod_settings_field(self, typeName="", action="get", field="", value=None, **kw):
        if field in self.counters:
            return {"success": True, "value": self.counters[field]}
        if action == "set":
            old = self.settings.get(field)
            if isinstance(old, bool):
                self.settings[field] = str(value).lower() == "true"
            else:
                self.settings[field] = float(value)
        return {"success": True, "value": self.settings.get(field)}

    def t_jawa_destroy_batch(self, rects="", **kw):
        r = _rect(rects)
        for t in list(self.things.values()):
            if any(_in(r, cx, cz) for cx, cz in self._cells_of(t)):
                self._remove(t)
        for c in [c for c in self.soaked if _in(r, *c)]:
            del self.soaked[c]
        for pid in [p for p, v in self.pawns.items() if _in(r, v["x"], v["z"])]:
            del self.pawns[pid]

    def t_jawa_build_batch(self, ops="", **kw):
        n = 0
        for op in str(ops).split(";"):
            if not op:
                continue
            d, rest = op.split(":", 1)
            xz = rest.split(",")
            self._thing(d, int(xz[0]), int(xz[1]))
            n += 1
        return {"success": True, "survived": n, "failed": 0}

    def t_jawa_gss_stage(self, ops="", **kw):
        kv = dict(p.split("=", 1) for p in str(ops).split("|"))
        if kv.get("kind") == "gss_charge":
            self.charged.add((int(kv["x"]), int(kv["z"])))

    def t_jawa_list_things(self, defName=None, rect=None, limit=100, **kw):
        r = _rect(rect) if rect else None
        out = [{"id": t["id"], "def": t["def"], "x": t["x"], "z": t["z"]} for t in self.things.values()
               if (defName is None or t["def"] == defName) and (r is None or _in(r, t["x"], t["z"]))]
        return {"success": True, "things": out[:int(limit)]}

    def t_jawa_inspect_string(self, thingIds=None, **kw):
        try:
            h = self.heads.get(int(thingIds))
        except (TypeError, ValueError):
            h = None
        return {"success": True, "things": [{"inspect": [h["line"]]}] if h else []}

    def t_jawa_static_call(self, type="", method="", args="", **kw):
        if method == "ProofTank":
            xz, _mode, liq, units = args.split(";")
            x, z = (int(v) for v in xz.split(","))
            for t in self._of("RM_LiquidTank"):
                if (t["x"], t["z"]) == (x, z):
                    self.tanks[t["id"]] = {"liquid": liq, "units": int(units)}
                    return {"success": True, "result": "tank %d,%d = %s %s" % (x, z, liq, units)}
            return {"success": True, "result": "no tank at %d,%d" % (x, z)}
        if method == "IsSoaked":
            if "no_biomes" in self.faults:
                return {"success": True, "result": None}
            x, z = (int(v) for v in args.split("|")[1].split(","))
            return {"success": True, "result": "True" if self.soaked.get((x, z), 0) > self.tick else "False"}
        return {"success": True, "result": None}

    def t_jawa_spawn_pawn(self, x=0, z=0, **kw):
        if "spawn_fail" in self.faults:
            return {"success": False, "pawns": []}
        self.nid += 1
        self.pawns[self.nid] = {"x": int(x), "z": int(z), "hediffs": [], "needs": {}}
        return {"success": True, "pawns": [{"id": self.nid}]}

    def t_jawa_pawn_get(self, pawn=None, **kw):
        p = self.pawns.get(int(pawn))
        return {"success": True, "pawns": [{"hediffs": list(p["hediffs"])}] if p else []}

    def t_jawa_pawn_need(self, pawn=None, need="", level=0, **kw):
        p = self.pawns.get(int(pawn))
        if p:
            p["needs"][need] = float(level)

    def t_rimworld_list_colonists(self, **kw):
        out = []
        for pid, p in self.pawns.items():
            job = None
            if p["needs"].get("RM_Thirst", 1.0) <= 0.3 and "no_drink" not in self.faults and any(
                    s["units"] > 0 and s["liquid"] == "RM_Liquid_FreshWater" for s in self.tanks.values()):
                job = "RM_DrinkFromTank"
            out.append({"pawnId": "Thing_%d" % pid, "job": job})
        return {"success": True, "colonists": out}
