"""water_scenes_mock.py -- an OFFLINE fake bridge for water_scenes_walk.py --mock.

WHY (WATER_SCENES_WALK_MEND_TRIPS_AFTER_S4, 2026-10-17): the first live walk stopped with bare "Traceback" lines after
S4.c and inside S5 and the bodies were lost. This fake lets the walk's OWN code paths (staging, every pulse loop, every
row, the crash handler) run to the end with no game, in seconds:

    python3 src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py all --mock --no-wait --pace 0 --no-shots
    python3 src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py all --mock --no-wait --pace 0 --no-shots --mock-fail S4

ProofReadout answers the real string shape ("Hole 0.5 m . Water 0.24 m (474 L)", or "OK -" for undug ground) and
ProofLevelSurface the real "OK n worst G m;x,z:squares:gap:min:max;" shape, so the walk's decilitre readers and level rows run.

It proves NOTHING about the game: the "water" here is a toy (a dug cell gains one level per pulse up to its depth), so
its MATCHES/DIFFERS words are meaningless. Only "every scene reached its end and printed its rows" and "a crash printed
its traceback and the next scene ran" are read from it.
"""
import json


class MockV(object):
    """Stands in for validation_core: the two helpers the walk calls."""

    def prepare_site(self, B, rect, rows, rid):
        return None

    def _wait_playing(self, B, budget_s=240, leave_s=30):
        return True, 0

    def sweep_at_start(self, B, made_map):
        r = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}
        return {"route": "destroy_bulk", "removed": r.get("matchedCount"), "left": [], "kept": 0, "snapshot": None}


class MockFailure(RuntimeError):
    pass


class MockBridge(object):
    def __init__(self, fail_scene=None):
        self.tick = 0
        self.pulse = 0
        self.depth = {}
        self.fill = {}
        self.terrain = {}
        self.mock_gap = "0.0000"          # ProofLevelSurface worst gap the toy reports (a test sets "0.0500" to prove the row can go red)
        self.fail_scene = (fail_scene or "").upper() or None
        self.scene = None
        self.ticks_in_scene = 0

    # ---------------------------------------------------------------- transport
    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            return self._static(kw.get("method"), kw.get("args") or "")
        if tool == "jawa/flowworks_engine_state":
            return {"success": True, "ticksGame": self.tick, "overflowDestroyedTotal": 0, "sinkTransferredTotal": 0,
                            "excavatedCellCount": 0, "superdeepCellCount": 0, "bodyCount": 21}
        if tool == "jawa/mod_settings_field":
            if kw.get("field") == "pulseIntervalTicks":
                return {"success": True, "value": "250"}
            st = self.__dict__.setdefault("settings", {})
            if kw.get("action") == "set":
                st[kw.get("field")] = kw.get("value")
            return {"success": True, "value": st.get(kw.get("field"), kw.get("value", "True"))}
        if tool == "jawa/flowworks_body_report":
            return {"success": True, "body": {"id": 1, "limitless": True, "stock": 48.0, "capacity": 48.0,
                                              "cellCount": 12, "recededCount": 0}}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            self.depth[c] = self.depth.get(c, 0) + int(kw.get("deepenLevels") or 0)
            if kw.get("fillInLevels"):
                self.depth[c] = max(0, self.depth[c] - int(kw["fillInLevels"]))
                self.fill[c] = min(self.fill.get(c, 0), self.depth[c])
            if int(kw.get("setFill", -1)) >= 0:
                self.fill[c] = int(kw["setFill"])
            return {"success": True}
        if tool == "jawa/set_terrain_batch":
            for op in str(kw.get("ops") or "").split(";"):
                name, nums = op.split(":")
                x, z, w, h = map(int, nums.split(","))
                for i in range(w):
                    for j in range(h):
                        self.terrain[(x + i, z + j)] = name
            return {"success": True}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": 7}]}
        if tool == "jawa/comp_read":
            return {"success": True, "values": {"heldUnits": 0, "freeEndRole": "Intake"}}
        if tool == "jawa/build_batch":
            return {"success": True, "survived": len(str(kw.get("ops") or "").split(";"))}
        if tool == "rimworld/get_ui_state":
            return {"success": True, "programState": "Playing"}
        if tool == "rimworld/list_selected_gizmos":
            return {"success": True, "gizmos": []}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 250, "sizeZ": 250}
        return {"success": True}

    def probe_of(self, probe_type, cmd, wait_s=20.0, poll_s=0.3):
        if cmd == "colonists":
            return {"success": True, "pawns": [{"id": 101, "pos": [120, 120]}, {"id": 102, "pos": [121, 120]}]}
        if cmd == "census":
            return {"success": True, "hoses": []}
        if cmd.startswith("pump:"):
            return {"success": True, "powered": True, "pourMode": False, "moved": self.pulse * 10000, "lastMovedUnits": 10000}
        if cmd.startswith("net:"):
            return {"success": True, "settledUnits": 0, "dumpedUnits": 0, "spilledUnits": 0, "hoseDrainedUnits": 0,
                    "moves": 0, "putBacks": 0}
        return {"success": True}

    def ticks(self, n):
        self.ticks_in_scene += 1
        if self.fail_scene and self.scene == self.fail_scene and self.ticks_in_scene == 12:
            raise MockFailure("injected by --mock-fail %s on the 12th clock step of the scene" % self.fail_scene)
        before = self.tick // 250
        self.tick += int(n)
        for _ in range(self.tick // 250 - before):
            self.pulse += 1
            for c, d in self.depth.items():
                if self.fill.get(c, 0) < d:
                    self.fill[c] = self.fill.get(c, 0) + 1
        return {"success": True, "advanced": n}

    # ---------------------------------------------------------------- proofs
    def _static(self, method, arg):
        if method == "ProofFluidRow":
            x, z, w, h = map(int, arg.split(","))
            cells = []
            for j in range(h):
                for i in range(w):
                    c = (x + i, z + j)
                    cells.append("%d,%d:%d/%d/%s/%s;" % (c[0], c[1], self.depth.get(c, 0), self.fill.get(c, 0),
                                                         "RM_Fluid_Water" if self.fill.get(c) else "none",
                                                         self.terrain.get(c, "Soil")))
            return {"success": True, "result": "ROW pulse=%d viscosity=True %s" % (self.pulse, "".join(cells))}
        if method == "ProofReadout":
            # the real strings (RM_Volume.Readout): "Hole 0.5 m · Water 0.24 m (474 L)"; the toy's water is whole notches
            x, z = map(int, arg.split(","))
            c = (x, z)
            d = self.depth.get(c, 0)
            if d <= 0:
                return {"success": True, "result": "OK -"}
            lit = self.fill.get(c, 0) * 1000 + getattr(self, "part_l", {}).get(c, 0)
            return {"success": True, "result": "OK Hole %s m \u00b7 Water %.2f m (%s L)" % (
                ("%g" % (d * 0.5)), lit / 2000.0, format(lit, ","))}
        if method == "ProofLevelSurface":
            wetc = [c for c, f in self.fill.items() if f > 0]
            if not wetc:
                return {"success": True, "result": "OK 0 worst 0.0000 m;"}
            c = wetc[0]
            return {"success": True, "result": "OK 1 worst %s m;%d,%d:%d:%s:-0.5000:-0.5000;" % (
                self.mock_gap, c[0], c[1], len(wetc), self.mock_gap)}
        if method == "ProofLiquid":
            return {"success": True, "result": "DOOR RM_Sluice open=False seals=True | mock"}
        return {"success": True, "result": "ok " + json.dumps(method)}
