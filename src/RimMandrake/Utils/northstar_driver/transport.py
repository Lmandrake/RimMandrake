"""Timed persistent transport + mock game.

TimedTransport wraps ONE RimBridge socket (opened once, reused for every call),
records per-call wall time, and offers call_many(): send N requests back-to-back,
then collect N responses by id. Pipelining is OPT-IN (pipeline=True) because the
bridge's behaviour under pipelined requests has NOT been proven live; with it off,
call_many is a plain loop on the same socket (still no spawn/reconnect cost).

MockTransport + MockGame implement the same `.call/.list_tools/.call_many` surface
over an in-memory game, so preflight/bars/selftests run with the game down.
The mock encodes the response shapes this package ASSUMES (see MockGame); they are
modelled on skills/rimbridge and rimdrive.session reads and are unproven against the
live bridge until the first live preflight.
"""
import json
import os
import sys
import time
import uuid

_UTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)


class CallLog(object):
    def __init__(self):
        self.rows = []          # (tool, ms, ok)

    def add(self, tool, ms, ok):
        self.rows.append((tool, ms, ok))

    def summary(self):
        ms = sorted(r[1] for r in self.rows)
        by = {}
        for t, m, ok in self.rows:
            d = by.setdefault(t, {"n": 0, "ms": 0.0, "err": 0})
            d["n"] += 1
            d["ms"] += m
            d["err"] += 0 if ok else 1
        n = len(ms)
        return {"n": n, "total_ms": round(sum(ms), 3),
                "mean_ms": round(sum(ms) / n, 4) if n else 0,
                "p50_ms": round(ms[n // 2], 4) if n else 0,
                "p95_ms": round(ms[min(n - 1, int(n * .95))], 4) if n else 0,
                "by_tool": {k: {"n": v["n"], "mean_ms": round(v["ms"] / v["n"], 4),
                                "errors": v["err"]} for k, v in by.items()}}


class TimedTransport(object):
    """Wrap a RimBridge (or anything with .call/.list_tools)."""

    def __init__(self, rb, pipeline=False):
        self.rb = rb
        self.pipeline = pipeline
        self.log = CallLog()

    def __enter__(self):
        self.rb.__enter__()
        return self

    def __exit__(self, *a):
        return self.rb.__exit__(*a)

    def list_tools(self):
        return self.rb.list_tools()

    def call(self, tool, params=None, check=True):
        t0 = time.perf_counter()
        ok = False
        try:
            r = self.rb.call(tool, params or {}, check)
            ok = True
            return r
        finally:
            self.log.add(tool, (time.perf_counter() - t0) * 1000.0, ok)

    def call_many(self, calls):
        """calls: [(tool, params)] -> [result | Exception]. Order preserved."""
        if not (self.pipeline and hasattr(self.rb, "_send")):
            out = []
            for tool, params in calls:
                try:
                    out.append(self.call(tool, params))
                except Exception as ex:   # reported per-call, never swallowed
                    out.append(ex)
            return out
        from rimbridge_client import GABP_VERSION, _retired, RetiredToolError
        t0 = time.perf_counter()
        ids = []
        for tool, params in calls:
            why = _retired(tool)
            if why is not None:
                raise RetiredToolError("%s is RETIRED: %s" % (tool, why))
            self.rb.check_params(tool, params)
            rid = str(uuid.uuid4())
            ids.append(rid)
            self.rb._send({"v": GABP_VERSION, "id": rid, "type": "request",
                           "method": "tools/call",
                           "params": {"name": tool, "arguments": params or {}}})
        got = {}
        while len(got) < len(ids):
            msg = self.rb._recv_raw()
            if msg.get("type") == "event":
                self.rb.events.append(msg)
                continue
            got[msg.get("id")] = msg
        per = (time.perf_counter() - t0) * 1000.0 / max(1, len(calls))
        out = []
        for (tool, _), rid in zip(calls, ids):
            m = got.get(rid)
            if m is None:
                out.append(RuntimeError("no response for %s" % tool))
                self.log.add(tool, per, False)
            elif m.get("error"):
                e = m["error"]
                out.append(RuntimeError("%s failed: %s" % (
                    tool, e.get("message") if isinstance(e, dict) else e)))
                self.log.add(tool, per, False)
            else:
                out.append(m.get("result"))
                self.log.add(tool, per, True)
        return out


# ---------------------------------------------------------------- the mock

class MockGame(object):
    """In-memory game answering the calls preflight/bars/rimdrive make.

    `faults` injects the failure classes preflight must catch:
      zombie (get_game_info lacks ticksGame), modal (a window open),
      running (not paused), pause_lies (pause_game succeeds, ticks keep moving), dev_off, god_off,
      dirty (stray thing/pawn in the test area), unfrozen (never advances ticks).
    """
    TOOLS = ["rimbridge/ping", "rimbridge/get_bridge_status", "rimworld/get_game_info",
             "rimworld/pause_game", "rimworld/set_god_mode", "rimworld/list_windows",
             "rimworld/get_cell_info", "jawa/map_info", "jawa/list_pawns",
             "jawa/list_things", "jawa/destroy_batch", "jawa/damage",
             "jawa/spawn_thing", "jawa/time_clock",
             "jawa/set_terrain_batch", "jawa/get_terrain_batch", "jawa/set_fog", "jawa/set_roof_batch",
             "jawa/get_roof_batch", "jawa/weather_set", "jawa/weather_get", "jawa/time_set_ticks",
             "jawa/spawn_batch", "jawa/spawn_pawn", "jawa/log_autoopen_suppress", "jawa/map_commit", "jawa/pawn_health", "jawa/pawn_need",
             "jawa/set_pawn_skill", "jawa/set_draft", "jawa/set_work_priority", "jawa/paint_area",
             "jawa/mod_settings_field", "jawa/dlc_status", "jawa/thing_stats", "jawa/clear_ui",
             "jawa/window_list_close", "jawa/get_defs", "jawa/pawn_force_mental_break", "jawa/pawn_get",
             "jawa/ordered_job", "rimworld/step_game_ticks", "rimworld/screenshot_cell_rect",
             "rimworld/get_camera_state", "rimworld/jump_camera_to_cell", "rimworld/take_screenshot"]

    def __init__(self, faults=(), mods=("ludeon.rimworld",), sizex=200, sizez=200):
        self.faults = set(faults)
        self.ticks = 1000
        self.paused = "running" not in self.faults
        self.dev = "dev_off" not in self.faults
        self.god = "god_off" not in self.faults
        self.windows = ["Dialog_NodeTree"] if "modal" in self.faults else []
        self.size = (sizex, sizez)
        self.things = {}                       # (x,z) -> [defName]
        self.next_id = 1
        self.pawns = []
        if "dirty" in self.faults:
            self.things[(100, 100)] = ["Wall"]
        self.mods = list(mods)
        self.terrain = {}                      # (x,z) -> terrain def
        self.weather = "Rain"
        self.hour = 6
        self.settings = {}                     # field -> str
        self.stuff = {}

    def _tick(self):
        if not self.paused and "unfrozen" not in self.faults:
            self.ticks += 60
        if "pause_lies" in self.faults:
            self.ticks += 60

    def handle(self, tool, p):
        p = p or {}
        self._tick()
        if tool == "rimbridge/ping":
            return {"success": True, "pong": True}
        if tool == "rimbridge/get_bridge_status":
            return {"success": True, "state": {"paused": self.paused, "timeSpeed": 0 if self.paused else 1}}
        if tool == "rimworld/get_game_info":
            if "zombie" in self.faults:
                return {"success": True}             # loaded-looking, no tick counter
            return {"success": True, "ticksGame": self.ticks,
                    "devModeEnabled": self.dev, "godMode": self.god}
        if tool == "rimworld/pause_game":
            self.paused = bool(p.get("pause"))
            return {"success": True, "paused": self.paused}
        if tool == "rimworld/set_god_mode":
            self.god = bool(p.get("enabled"))
            return {"success": True}
        if tool == "rimworld/list_windows":
            return {"success": True, "windows": list(self.windows)}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": self.size[0], "sizeZ": self.size[1]}
        if tool == "jawa/time_clock":
            return {"success": True, "ticksGame": self.ticks, "hour": self.hour}
        if tool == "rimworld/get_cell_info":
            x, z = p["x"], p["z"]
            if not (0 <= x < self.size[0] and 0 <= z < self.size[1]):
                return {"success": False, "message": "out of bounds"}
            return {"success": True, "cell": {"things": [{"defName": d} for d in self.things.get((x, z), [])]}}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": list(self.pawns)}
        if tool == "jawa/list_things":
            x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
            want = {d.strip() for d in str(p.get("defName") or "").split(",") if d.strip()}
            out = [{"defName": d, "def": d, "id": "%s#%d_%d" % (d, cx, cz), "x": cx, "z": cz, "position": {"x": cx, "z": cz}}
                   for (cx, cz), ds in self.things.items()
                   if x <= cx < x + w and z <= cz < z + h for d in ds if not want or d in want]
            return {"success": True, "things": out, "isCompleteList": True}
        if tool == "jawa/set_terrain_batch":
            for op in str(p["ops"]).split(";"):
                name, rect = op.split(":")
                x, z, w, h = [int(v) for v in rect.split(",")]
                for cx in range(x, x + w):
                    for cz in range(z, z + h):
                        self.terrain[(cx, cz)] = name
            return {"success": True}
        if tool == "jawa/get_terrain_batch":
            x, z, w, h = [int(v) for v in str(p["rects"]).split(",")]
            return {"success": True, "cells": [self.terrain.get((cx, cz), "Soil")
                                               for cx in range(x, x + w) for cz in range(z, z + h)]}
        if tool in ("jawa/log_autoopen_suppress", "jawa/map_commit"):
            return {"success": True}
        if tool == "jawa/pawn_force_mental_break":
            for q in self.pawns:
                if q["id"] == p.get("pawn"):
                    q["painting"] = True
                    return {"success": True, "started": True,
                            "mentalStateAfter": "RM_GraffitiPaintingSpreeState"}
            return {"success": False, "message": "no such pawn"}
        if tool == "jawa/pawn_get":
            return {"success": True, "job": "RM_PaintGraffitiJob"}
        if tool == "jawa/ordered_job":
            q = next((q for q in self.pawns if q["id"] == p.get("pawnId")), None)
            if q is None:
                return {"success": False}
            self._paint(q["x"], q["z"])
            return {"success": True, "accepted": True, "nowRunningRequested": True}
        if tool == "rimworld/step_game_ticks":
            n = int(p.get("ticks") or 0)
            self.ticks += n
            for q in self.pawns:
                if q.get("painting"):
                    for _ in range(max(1, n // 250)):
                        self._paint(q["x"], q["z"])
            return {"success": True}
        if tool in ("jawa/set_fog", "jawa/set_roof_batch", "jawa/set_draft", "jawa/set_work_priority",
                    "jawa/paint_area", "jawa/pawn_health", "jawa/pawn_need", "jawa/set_pawn_skill",
                    "jawa/clear_ui", "jawa/window_list_close",
                    "rimworld/jump_camera_to_cell"):
            return {"success": True}
        if tool == "jawa/get_roof_batch":
            return {"success": True, "roofedCells": 0}
        if tool == "jawa/weather_set":
            self.weather = p.get("weather")
            return {"success": True}
        if tool == "jawa/weather_get":
            return {"success": True, "weather": self.weather}
        if tool == "jawa/time_set_ticks":
            self.hour = (self.hour + (int(p["ticks"]) - self.ticks) / 2500.0) % 24
            self.ticks = int(p["ticks"])
            return {"success": True}
        if tool == "jawa/spawn_batch":
            for op in str(p["ops"]).split(";"):
                name, xy = op.split(":")
                x, z = [int(v) for v in xy.split(",")[:2]]
                self.things.setdefault((x, z), []).append(name)
            return {"success": True}
        if tool == "jawa/spawn_pawn":
            pid = "Pawn%d" % self._id()
            self.pawns.append({"id": pid, "x": p.get("x"), "z": p.get("z"), "painting": False})
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/mod_settings_field":
            key = p["field"]
            if p.get("action") == "set":
                self.settings[key] = p["value"]
            return {"success": True, "value": self.settings.get(key, "250" if key == "paintIntervalTicks" else "True")}
        if tool == "jawa/dlc_status":
            return {"success": True, "dlcs": ["Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]}
        if tool == "jawa/thing_stats":
            return {"success": True, "things": [{"id": p["thing"], "stats": [
                {"defName": p.get("stats"),
                "value": -15.0 if str(p["thing"]).startswith("RM_Graffiti_Vandal") else -3.0}]}]}
        if tool == "jawa/get_defs":
            return {"success": True, "foundCount": 1, "notFound": []}
        if tool == "rimworld/screenshot_cell_rect":
            return {"success": True, "path": "/nonexistent/mock.png"}
        if tool == "rimworld/get_camera_state":
            return {"success": True, "rootSize": 12.0}
        if tool == "jawa/spawn_thing":
            self.things.setdefault((p["x"], p["z"]), []).append(p["defName"])
            return {"success": True, "id": self._id()}
        if tool == "jawa/destroy_batch":
            x, z, w, h = [int(v) for v in str(p["rects"]).split(",")]
            cats = str(p.get("categories") or "Plant")
            if cats in ("All", "Filth", "Building"):
                for k in [k for k in self.things if x <= k[0] < x + w and z <= k[1] < z + h]:
                    del self.things[k]
            if cats in ("All", "Pawn"):
                self.pawns = [q for q in self.pawns
                              if not (q.get("x") is not None and x <= q["x"] < x + w and z <= q["z"] < z + h)]
            return {"success": True}
        if tool == "jawa/damage":
            self.pawns = [q for q in self.pawns if q.get("id") != p.get("thingId")]
            return {"success": True}
        raise RuntimeError("mock: unknown tool %s" % tool)

    MARKS = ["RM_Graffiti_Vandal", "RM_Graffiti_Tag_A", "RM_Graffiti_Tag_B", "RM_Graffiti_ThrowUp_A",
             "RM_Graffiti_Scratches", "RM_Graffiti_TallyMarks", "RM_Graffiti_WarningGlyph"]

    def _paint(self, px, pz):
        """Mock of JobDriver_PaintGraffiti: a mark on the floor cell cardinal to the nearest wall."""
        walls = [k for k, ds in self.things.items() if "Wall" in ds and abs(k[0] - px) <= 12 and abs(k[1] - pz) <= 12]
        if not walls:
            return
        wx, wz = min(walls, key=lambda k: abs(k[0] - px) + abs(k[1] - pz))
        for cz in (wz + 1, wz - 1):
            if "Wall" not in self.things.get((wx, cz), []):
                self.painted = getattr(self, "painted", 0) + 1
                self.things.setdefault((wx, cz), []).append(self.MARKS[self.painted % len(self.MARKS)])
                return

    def _id(self):
        self.next_id += 1
        return self.next_id


class MockTransport(object):
    """Same surface as TimedTransport, over a MockGame. Times calls too."""

    def __init__(self, game=None, latency_ms=0.0):
        self.game = game or MockGame()
        self.latency = latency_ms / 1000.0
        self.log = CallLog()
        self.pipeline = False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def list_tools(self):
        return [{"name": n} for n in self.game.TOOLS]

    def call(self, tool, params=None, check=True):
        t0 = time.perf_counter()
        ok = False
        try:
            if self.latency:
                time.sleep(self.latency)
            r = self.game.handle(tool, params)
            ok = True
            return r
        finally:
            self.log.add(tool, (time.perf_counter() - t0) * 1000.0, ok)

    def call_many(self, calls):
        out = []
        for tool, params in calls:
            try:
                out.append(self.call(tool, params))
            except Exception as ex:
                out.append(ex)
        return out
