"""FakeFlowWorksGame -- the offline stand-in prep_site.py and preflight_flowworks.py are proven on.

Extends northstar_driver.transport.MockGame with the FlowWorks/site tools. Every response
shape mirrors the tool's own ResultDescription in JawaBench.BridgeTools (read 2026-10-01):
get_terrain_layers -> cells[{x,z,top,temp,baseTerrain}] + truncated; get_terrain_batch /
get_roof_batch -> run-length `ops`; weather_get -> weather + conditions[]; and so on. The
three NEEDED tools (site_spec.NEEDED_TOOLS) answer in their CONTRACT shape and can be
withheld with new_tools=False, which is today's live reality.

It starts DIRTY on purpose (rain, plants and colonists in plots, a marsh and a pond near
plots, a mountain roof, an incident queued) so prep has real work and preflight has real
failures. `faults` dirties a finished site the way the item's proof-it-can-fail asks:
  rain, prefilled (one plot cell D=1 F=1), stray_pawn, cold (one check cell at -5 C),
  settings_drift, condition (a cold snap), temp_terrain (mud overlay), modal, running.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
from northstar_driver.transport import MockGame  # noqa: E402

NEW = ("jawa/flowworks_body_report", "jawa/flowworks_engine_state")


class FakeFlowWorksGame(MockGame):
    def __init__(self, faults=(), size=(200, 200), new_tools=True, saves_dir=None, shots_dir=None,
                 season="Summer", identity=True):
        super().__init__(faults=[f for f in faults if f in ("modal", "running", "dev_off", "zombie")],
                         sizex=size[0], sizez=size[1])
        self.ff = set(faults)
        self.new_tools = new_tools
        self.identity = identity
        self.map_id, self.tile = 7, 4321
        self.season = season
        self.temp = {}                    # (x,z) -> temp terrain
        self.roof = {}                    # (x,z) -> roof def
        self.D, self.F = {}, {}
        self.bodies = {}                  # body id -> record; cell -> id in body_of
        self.body_of = {}
        self.conditions = []
        self.incidents = 2
        self.temps = {}                   # (x,z) -> C override
        self.saves_dir = saves_dir
        self.shots_dir = shots_dir
        self.weather = "Rain"
        self.settings = {}
        for t, fields in S.SETTINGS.items():
            for f, v in fields.items():
                self.settings[(t, f)] = str(v)
        self.next_pulse = 1250
        self._dirty_start()

    # ----------------------------------------------------------- initial dirt
    def _dirty_start(self):
        rng = random.Random(1)
        W, Z = self.size
        for _ in range(400):
            self.things.setdefault((rng.randrange(W), rng.randrange(Z)), []).append("Plant_Grass")
        for c in S.cells((60, 20, 6, 6)):
            self.terrain[c] = "Marsh"
        for c in S.cells((18, 20, 3, 3)):
            self.terrain[c] = "WaterShallow"
        for c in S.cells((10, 45, 30, 20)):
            self.roof[c] = "RoofRockThick"
        self.pawns = [{"id": "Colonist1", "x": 20, "z": 16, "faction": "PlayerColony"},
                      {"id": "Muffalo1", "x": 90, "z": 52, "faction": None}]

    def finish_site(self, plots):
        """Put the fake into the state a correct prep leaves (used to test preflight alone)."""
        for p in plots:
            for c, want in S.expected_cells(p, self.size).items():
                self.terrain[c] = want["base"]
                self.temp.pop(c, None)
                self.things.pop(c, None)
                if want["roof"] == "none":
                    self.roof.pop(c, None)
                else:
                    self.roof[c] = want["roof"]
            for b in p["bodies"]:
                self._classify(b["rect"][0], b["rect"][1])
        self.pawns, self.weather, self.conditions, self.incidents = [], "Clear", [], 0
        self.paused = True

    def dirty(self, plots):
        """Apply self.ff to a finished site (the item's 'deliberately dirtied working copy')."""
        a = S.plot_by_id(plots, "A")
        x, z = a["rect"][0], a["rect"][1]
        if "rain" in self.ff:
            self.weather = "Rain"
        if "prefilled" in self.ff:
            self.D[(x + 1, z)] = 1
            self.F[(x + 1, z)] = 1
        if "stray_pawn" in self.ff:
            self.pawns.append({"id": "Stray1", "x": x + 2, "z": z + 1, "faction": "PlayerColony"})
        if "cold" in self.ff:
            self.temps[(x, z)] = -5.0
        if "settings_drift" in self.ff:
            self.settings[("RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings", "refillEnabled")] = "False"
        if "condition" in self.ff:
            self.conditions = [{"def": "ColdSnap", "affectsThisMap": True, "permanent": False, "ticksLeft": 60000}]
        if "temp_terrain" in self.ff:
            self.temp[(x + 3, z)] = "Mud"

    # ----------------------------------------------------------- helpers
    def _rect(self, s):
        return [int(v) for v in str(s).split(",")[:4]]

    def _rle(self, grid, rect, skip=None):
        x, z, w, h = rect
        ops = []
        for cz in range(z, z + h):
            run, start = None, x
            for cx in range(x, x + w + 1):
                v = grid(cx, cz) if cx < x + w else object()
                if v != run:
                    if run is not None and run != skip:
                        ops.append("%s:%d,%d,%d,1" % (run, start, cz, cx - start))
                    run, start = v, cx
        return ";".join(ops)

    def _classify(self, x, z):
        c = (x, z)
        if c in self.body_of:
            return self.bodies[self.body_of[c]]
        t = self.terrain.get(c, "Soil")
        if "Water" not in t:
            return None
        seen, todo = {c}, [c]
        while todo:
            cx, cz = todo.pop()
            for n in ((cx + 1, cz), (cx - 1, cz), (cx, cz + 1), (cx, cz - 1)):
                if n not in seen and "Water" in self.terrain.get(n, "Soil") \
                        and 0 <= n[0] < self.size[0] and 0 <= n[1] < self.size[1]:
                    seen.add(n)
                    todo.append(n)
        edge = any(cx in (0, self.size[0] - 1) or cz in (0, self.size[1] - 1) for cx, cz in seen)
        bid = len(self.bodies) + 1
        cap = float(len(seen) * 4)
        self.bodies[bid] = {"id": bid, "limitless": edge and len(seen) >= 50, "stock": cap,
                            "capacity": cap, "cellCount": len(seen), "recededCount": 0, "truncated": False}
        for k in seen:
            self.body_of[k] = bid
        return self.bodies[bid]

    # ----------------------------------------------------------- tools
    def tool_names(self):
        names = set(self.TOOLS) | set(S.EXISTING_TOOLS)
        if self.new_tools:
            names |= set(NEW)
        return sorted(names)

    def handle(self, tool, p):
        p = p or {}
        if tool in NEW and not self.new_tools:
            raise RuntimeError("unknown tool %s" % tool)
        W, Z = self.size
        if tool == "jawa/map_info":
            self._tick()
            return {"success": True, "mapId": self.map_id, "tile": self.tile, "tileValid": True,
                    "sizeX": W, "sizeZ": Z, "season": self.season, "mapBiome": "TemperateForest",
                    "outdoorTempNow": 22.0, "tileInfo": {"biome": "TemperateForest"}}
        if tool == "jawa/get_terrain_layers":
            x, z, w, h = self._rect(p["rect"])
            lim = max(1, int(p.get("limit") or 200))
            cs = [{"x": cx, "z": cz, "top": self.temp.get((cx, cz)) or self.terrain.get((cx, cz), "Soil"),
                   "temp": self.temp.get((cx, cz)), "baseTerrain": self.terrain.get((cx, cz), "Soil")}
                  for cx in range(x, x + w) for cz in range(z, z + h)
                  if 0 <= cx < W and 0 <= cz < Z]
            return {"success": True, "count": min(lim, len(cs)), "cells": cs[:lim], "truncated": len(cs) > lim}
        if tool == "jawa/get_terrain_batch":
            ops = ";".join(self._rle(lambda cx, cz: self.terrain.get((cx, cz), "Soil"), self._rect(r))
                           for r in str(p["rects"]).split(";") if r.strip())
            return {"success": True, "ops": ops}
        if tool == "jawa/set_terrain_batch":
            for op in str(p["ops"]).split(";"):
                name, rect = op.split(":")
                for c in S.cells(self._rect(rect)):
                    self.terrain[c] = name
                    self.temp.pop(c, None)
            return {"success": True, "cellsFailedVerify": 0}
        if tool == "jawa/get_roof_batch":
            ops = ";".join(self._rle(lambda cx, cz: self.roof.get((cx, cz)), self._rect(r), skip=None)
                           for r in str(p["rects"]).split(";") if r.strip())
            return {"success": True, "ops": ops}
        if tool == "jawa/set_roof_batch":
            for r in str(p["ops"]).split(";"):
                rd = p.get("roofDef")
                if ":" in r:
                    rd, r = r.split(":")
                for c in S.cells(self._rect(r)):
                    if rd in (None, "None", "none", ""):
                        self.roof.pop(c, None)
                    else:
                        self.roof[c] = rd
            return {"success": True, "cellsFailedVerify": 0}
        if tool == "jawa/list_things":
            p = dict(p, rect=p.get("rect") or "0,0,%d,%d" % (W, Z))     # no rect = whole map
            r = super().handle(tool, p)
            if p.get("includePawns"):
                x, z, w, h = self._rect(p["rect"]) if p.get("rect") else (0, 0, W, Z)
                r["things"] += [{"def": q["id"], "defName": q["id"], "id": q["id"],
                                 "position": {"x": q["x"], "z": q["z"]}} for q in self.pawns
                                if x <= q["x"] < x + w and z <= q["z"] < z + h]
            return r
        if tool == "jawa/list_pawns":
            if p.get("rect"):
                x, z, w, h = self._rect(p["rect"])
                return {"success": True, "pawns": [q for q in self.pawns
                                                   if x <= q["x"] < x + w and z <= q["z"] < z + h]}
            return {"success": True, "pawns": list(self.pawns)}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": self.weather, "conditions": list(self.conditions),
                    "readErrors": []}
        if tool == "jawa/weather_set":
            self.weather = p.get("weather")
            return {"success": True}
        if tool == "jawa/game_condition":
            if p.get("action") == "end":
                self.conditions = [c for c in self.conditions if c["def"] != p.get("condition")]
            return {"success": True, "active": [c["def"] for c in self.conditions]}
        if tool == "jawa/incident_queue_clear":
            n, self.incidents = self.incidents, 0
            return {"success": True, "clearedCount": n, "cleared": []}
        if tool == "jawa/cell_temperature":
            x, z = [int(v) for v in str(p["cell"]).split(",")]
            return {"success": True, "ok": True, "temperature": self.temps.get((x, z), 22.0),
                    "outdoorTemp": 22.0}
        if tool == "jawa/time_perf":
            return {"success": True, "meanTickTime": 0.4, "curTimeSpeed": "Paused"}
        if tool == "jawa/time_clock":
            return {"success": True, "ticksGame": self.ticks, "paused": self.paused, "hour": self.hour}
        if tool == "jawa/time_set_ticks":
            if int(p["ticks"]) < self.ticks:
                return {"success": False, "message": "fake refuses backwards time"}
            seasons = ["Spring", "Summer", "Fall", "Winter"]
            for _ in range((int(p["ticks"]) - self.ticks) // 900000):
                self.season = seasons[(seasons.index(self.season) + 1) % 4]
            return super().handle(tool, p)
        if tool == "jawa/flowworks_excavation_report":
            c = (int(p["x"]), int(p["z"]))
            return {"success": True, "cell": {"x": c[0], "z": c[1]}, "depth": self.D.get(c, 0),
                    "fill": self.F.get(c, 0), "isExcavated": self.D.get(c, 0) > 0,
                    "isSourceCell": c in self.body_of, "isSinkCell": False,
                    "sinkTransferredTotal": 0.0, "overflowDestroyedTotal": 0.0,
                    "excavatedCellCount": sum(1 for v in self.D.values() if v > 0), "ticksGame": self.ticks}
        if tool == "jawa/flowworks_body_report":
            b = self._classify(int(p["x"]), int(p["z"]))
            if b is None:
                return {"success": True, "classified": False, "body": None, "activeFluid": "RM_Fluid_Water"}
            return {"success": True, "classified": True, "body": dict(b), "activeFluid": "RM_Fluid_Water",
                    "ticksGame": self.ticks}
        if tool == "jawa/flowworks_engine_state":
            return {"success": True, "nextPulseTick": self.next_pulse, "pulseIntervalTicks": 250,
                    "activeFluid": "RM_Fluid_Water", "rainAccumulator": 0.0,
                    "excavatedCellCount": sum(1 for v in self.D.values() if v > 0), "ticksGame": self.ticks}
        if tool == "rimworld/step_game_ticks":
            n = int(p.get("ticks") or 0)
            self.ticks += n
            while self.next_pulse <= self.ticks:
                self.next_pulse += 250
            return {"success": True}
        if tool == "jawa/mod_settings_field":
            key = (p["typeName"], p["field"])
            if key not in self.settings:
                return {"success": False, "message": "no field"}
            if p.get("action") == "set":
                before = self.settings[key]
                self.settings[key] = str(p["value"])
                return {"success": True, "valueBefore": before, "valueAfter": self.settings[key]}
            return {"success": True, "field": p["field"], "value": self.settings[key]}
        if tool == "jawa/type_probe":
            r = {"success": True, "typeName": p.get("typeName"), "resolved": True,
                 "assembly": "RimMandrakeFlowWorks"}
            if self.identity:
                r.update({"assemblyLocation": "C:/fake/Mods/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll",
                          "assemblyMvid": "00000000-0000-0000-0000-000000000001",
                          "assemblyFileSha256": getattr(self, "dll_sha", "0" * 64)})
            return r
        if tool == "jawa/research_bulk":
            return {"success": True, "mode": p.get("mode"), "finishedCountBefore": 3, "finishedCountAfter": 300}
        if tool == "jawa/destroy_batch":
            r = super().handle(tool, p)
            x, z, w, h = self._rect(p["rects"])
            if str(p.get("categories")) in ("All", "Pawn"):
                self.pawns = [q for q in self.pawns if not (x <= q["x"] < x + w and z <= q["z"] < z + h)]
            return r
        if tool == "jawa/set_pawn_faction":
            return {"success": True, "after": p.get("faction")}
        if tool == "jawa/destroy_bulk":
            n = len(self.pawns)
            if not p.get("dryRun", True):
                self.pawns = []
            return {"success": True, "matchedCount": n}
        if tool == "rimworld/save_game":
            path = os.path.join(self.saves_dir, p["saveName"] + ".rws")
            with open(path, "w", encoding="utf-8") as f:
                f.write("<savegame>fake %s tick %d</savegame>" % (p["saveName"], self.ticks))
            return {"success": True, "path": path}
        if tool == "rimworld/screenshot_cell_rect":
            from PIL import Image
            path = os.path.join(self.shots_dir, "shot_%d.png" % self._id())
            rng = random.Random(self.ticks)
            im = Image.new("RGB", (320, 240))
            im.putdata([(90 + rng.randrange(60), 80 + rng.randrange(40), 50) for _ in range(320 * 240)])
            im.save(path)
            return {"success": True, "path": path}
        return super().handle(tool, p)


class FakeTransport(object):
    """MockTransport surface over a FakeFlowWorksGame whose tool list varies by new_tools."""

    def __init__(self, game):
        from northstar_driver.transport import MockTransport
        self._t = MockTransport(game)
        self.game, self.log, self.pipeline = game, self._t.log, False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def list_tools(self):
        return [{"name": n} for n in self.game.tool_names()]

    def call(self, tool, params=None, check=True):
        return self._t.call(tool, params, check)

    def call_many(self, calls):
        return self._t.call_many(calls)
