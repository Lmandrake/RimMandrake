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
             "jawa/spawn_thing", "jawa/time_clock"]

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
            return {"success": True, "ticksGame": self.ticks}
        if tool == "rimworld/get_cell_info":
            x, z = p["x"], p["z"]
            if not (0 <= x < self.size[0] and 0 <= z < self.size[1]):
                return {"success": False, "message": "out of bounds"}
            return {"success": True, "cell": {"things": [{"defName": d} for d in self.things.get((x, z), [])]}}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": list(self.pawns)}
        if tool == "jawa/list_things":
            x, z, w, h = [int(v) for v in str(p["rect"]).split(",")]
            out = [{"defName": d, "x": cx, "z": cz} for (cx, cz), ds in self.things.items()
                   if x <= cx < x + w and z <= cz < z + h for d in ds]
            return {"success": True, "things": out}
        if tool == "jawa/spawn_thing":
            self.things.setdefault((p["x"], p["z"]), []).append(p["defName"])
            return {"success": True, "id": self._id()}
        if tool == "jawa/destroy_batch":
            x, z, w, h = [int(v) for v in str(p["rects"]).split(",")]
            for k in [k for k in self.things if x <= k[0] < x + w and z <= k[1] < z + h]:
                del self.things[k]
            return {"success": True}
        if tool == "jawa/damage":
            self.pawns = [q for q in self.pawns if q.get("id") != p.get("thingId")]
            return {"success": True}
        raise RuntimeError("mock: unknown tool %s" % tool)

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
