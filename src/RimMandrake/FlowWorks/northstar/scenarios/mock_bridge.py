"""scenarios/mock_bridge.py -- a MOCK RimBridge for the composite scenarios' --dry-run / --mock / selftest.

NOT A GAME. It records every call and keeps the little state the builder reads back (dug depth and fill per cell,
things by cell, pawns, labels, sign books, gizmo labels, the HoseProbe channel), so the builder's own verify can run
offline. Every answer carries "mock": True, there is no screenshot tool at all (2026-10-21: four days of hose-walk
shots turned out to be "MOCK SCREENSHOT" frames), and a def that def_index() cannot resolve is REFUSED the way the game
refuses an unknown def, so a typo fails here first.

What it cannot tell you: anything the game decides (flow, pathing, swimming, art, whether a proof surface accepts its
args). Those stay UNMEASURED until the live build.
"""
import json
import re

CYCLES = {
    "Job:": ["Job: Store", "Job: Fill", "Job: Empty", "Job: Dump"],
    "Free end:": ["Free end: Capped", "Free end: Intake", "Free end: Outflow"],
    "Ladder": ["Ladder down", "Ladder up"],
    "Pouring": ["Drawing into the tank", "Pouring into the channel"],
    "Drawing": ["Drawing into the tank", "Pouring into the channel"],
}
GIZMOS_OF = {"RM_LiquidTank": ["Job:"], "RM_LiquidTankTall": ["Job:"], "RM_UniversalCargoTank": ["Job:"],
             "RM_UniversalCargoTankXTall": ["Job:"], "RM_HoseReel": ["Free end:"], "RM_Ladder": ["Ladder"],
             "RM_LiquidPump": ["Drawing"]}
MARKER_DEF = {"PlaceMeter": "RM_FlowMeter", "PlaceSink": "RM_FlowSink", "PlaceSource": "RM_FlowSource",
              "PlaceLevelHolder": "RM_LevelHolder", "PlaceTimer": "RM_TimerSwitch", "PlaceEdgeSetter": "RM_MapEdgeSetter",
              "PlaceThermostat": "RM_LiquidThermostat", "PlacePainter": "RM_CurrentPainter"}


class MockBridge(object):
    def __init__(self, defs=None, size=250, terrain=None, swim_rule=None):
        self.swim_rule = swim_rule          # SIMULATION for the Stage 0 harness test: fill -> bool "a swimmer gets out"
        self.defs = defs                    # None = accept every def (dry-run); a set = refuse unknown ones
        self.size = size
        self.calls = []
        self.depth, self.fill, self.fluid = {}, {}, {}
        self.terrain = dict(terrain or {})
        self.things = []                    # dict(id, def, x, z, faction, stuff, style)
        self.pawns = {}                     # id -> dict(kind, x, z, faction, drafted)
        self.labels, self.signs = {}, []
        self.gz = {}                        # (x, z, prefix) -> label
        self.sel = None
        self.hp = dict(request="", result="", serial=0)
        self.tick = 0
        self.nid = 1000

    # ---------------------------------------------------------------------------------------------- plumbing
    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)

    def _ok(self, **kw):
        d = dict(success=True, mock=True)
        d.update(kw)
        return d

    def _known(self, d):
        return self.defs is None or d in self.defs

    def _new(self, d, x, z, faction=None, stuff=None):
        self.nid += 1
        t = dict(id=self.nid, defName=d, x=x, z=z, faction=faction, stuff=stuff, style=None)
        self.things.append(t)
        for pre in GIZMOS_OF.get(d, []):
            self.gz[(x, z, pre)] = CYCLES[pre][0]
        return t

    def _in(self, x, z, rect):
        rx, rz, rw, rh = rect
        return rx <= x < rx + rw and rz <= z < rz + rh

    @staticmethod
    def _rect(s):
        return tuple(int(v) for v in str(s).split(","))

    # ---------------------------------------------------------------------------------------------- the tools
    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        t = tool
        if t == "jawa/map_info":
            return self._ok(sizeX=self.size, sizeZ=self.size, longitude=0.0, uniqueID=0)
        if t == "jawa/time_clock":
            return self._ok(ticksAbs=self.tick, ticksGame=self.tick)
        if t in ("jawa/time_set_ticks",):
            self.tick = int(kw.get("ticks", self.tick))
            return self._ok()
        if t == "rimworld/step_game_ticks":
            self.tick += int(kw.get("ticks", 0))
            return self._ok(ticks=kw.get("ticks"))
        if t == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            self.depth[c] = max(0, self.depth.get(c, 0) + int(kw.get("deepenLevels", 0)) - int(kw.get("fillInLevels", 0)))
            if int(kw.get("setFill", -1)) >= 0:
                self.fill[c] = int(kw["setFill"])
            return self._ok(d=self.depth[c])
        if t == "jawa/flowworks_excavation_rect":
            rows = []
            for (x, z), d in self.depth.items():
                if d and self._in(x, z, (kw["x"], kw["z"], kw["w"], kw["h"])):
                    rows.append(dict(x=x, z=z, d=d, f=self.fill.get((x, z), 0), isExcavated=True,
                                     fluid=self.fluid.get((x, z))))
            return self._ok(rows=rows)
        if t == "jawa/static_call":
            return self._static(kw.get("type", ""), kw.get("method", ""), str(kw.get("args", "")))
        if t in ("jawa/build_batch", "jawa/spawn_batch"):
            return self._build(kw)
        if t == "rimworld/spawn_thing":
            if not self._known(kw["defName"]):
                return dict(success=False, mock=True, message="unknown def %s" % kw["defName"])
            self._new(kw["defName"], kw["x"], kw["z"])
            return self._ok()
        if t == "jawa/list_things":
            out = []
            rect = self._rect(kw["rect"]) if kw.get("rect") else None
            for th in self.things:
                if kw.get("defName") and th["defName"] != kw["defName"]:
                    continue
                if rect and not self._in(th["x"], th["z"], rect):
                    continue
                out.append(dict(id=th["id"], thingId=th["id"], defName=th["defName"], def_=th["defName"],
                                position=dict(x=th["x"], z=th["z"]), x=th["x"], z=th["z"]))
            for o in out:
                o["def"] = o.pop("def_")
            return self._ok(things=out[:int(kw.get("limit", 500))])
        if t == "jawa/get_defs":
            names = [d.split("/", 1)[-1] for d in str(kw.get("defs", "")).split(";") if d]
            miss = [n for n in names if not self._known(n)]
            return self._ok(foundCount=len(names) - len(miss), notFound=miss)
        if t == "jawa/spawn_pawn":
            if not self._known(kw["kindDef"]):
                return dict(success=False, mock=True, message="unknown pawn kind %s" % kw["kindDef"])
            self.nid += 1
            self.pawns[self.nid] = dict(kind=kw["kindDef"], x=kw["x"], z=kw["z"], faction=kw.get("faction"),
                                        drafted=False)
            return self._ok(pawns=[dict(id=self.nid)])
        if t == "jawa/list_pawns":
            rect = self._rect(kw["rect"]) if kw.get("rect") else None
            out = [dict(id=i, kind=p["kind"], kindDef=p["kind"], isPlayer=p["faction"] == "player",
                        intelligence="Humanlike" if p["kind"] in ("Colonist", "Pirate") else "Animal",
                        faction=p["faction"], position=dict(x=p["x"], z=p["z"]))
                   for i, p in self.pawns.items() if not rect or self._in(p["x"], p["z"], rect)]
            return self._ok(pawns=out)
        if t == "jawa/pawn_get":
            p = self.pawns.get(int(kw.get("pawn", -1)))
            return self._ok(pawns=[dict(position=dict(x=p["x"], z=p["z"]))] if p else [])
        if t == "jawa/order_pawn":
            p = self.pawns.get(int(kw.get("pawnId", -1)))
            if not p:
                return dict(success=False, mock=True)
            here = (p["x"], p["z"])
            dug = self.depth.get(here, 0)
            free = dug == 0 or (self.swim_rule is not None and self.swim_rule(self.fill.get(here, 0)))
            if free:
                p["x"], p["z"] = kw["x"], kw["z"]
            return self._ok(simulated=True, canReach=free, end=dict(x=p["x"], z=p["z"]))
        if t == "jawa/set_draft":
            p = self.pawns.get(int(kw.get("pawnId", -1)))
            if p:
                p["drafted"] = bool(kw.get("drafted"))
            return self._ok() if p else dict(success=False, mock=True)
        if t == "jawa/destroy_bulk":
            self.pawns = {i: p for i, p in self.pawns.items() if p["faction"] == "player"}
            return self._ok()
        if t == "jawa/review_label":
            tag = kw.get("tag", "")
            if kw.get("action") == "clear":
                self.labels.pop(tag, None)
                return self._ok()
            if kw.get("action") == "add":
                lines = [ln for ln in str(kw.get("ops", "")).split("\n") if ln]
                self.labels.setdefault(tag, []).extend(lines)
                return self._ok(added=len(lines), count=len(self.labels[tag]))
            return self._ok(labels=self.labels.get(tag, []))
        if t == "jawa/review_sign":
            if kw.get("action") == "clear":
                self.signs = []
                return self._ok()
            ops = [ln for ln in str(kw.get("ops", "")).split("\n") if ln]
            self.signs.extend(ops)
            return self._ok(placed=ops, refused=[], count=len(ops))
        if t == "rimworld/click_cell":
            self.sel = (kw["x"], kw["z"])
            return self._ok()
        if t == "rimworld/clear_selection":
            self.sel = None
            return self._ok()
        if t == "rimworld/list_selected_gizmos":
            out = []
            if self.sel:
                for (x, z, pre), lab in self.gz.items():
                    if (x, z) == self.sel:
                        out.append(dict(label=lab, gizmoId="%d,%d,%s" % (x, z, pre)))
            return self._ok(gizmos=out)
        if t == "rimworld/execute_gizmo":
            x, z, pre = str(kw.get("gizmoId")).split(",", 2)
            key = (int(x), int(z), pre)
            cyc = CYCLES[pre]
            self.gz[key] = cyc[(cyc.index(self.gz[key]) + 1) % len(cyc)]
            return self._ok()
        if t == "jawa/mod_settings_field" and str(kw.get("typeName", "")).endswith("HoseProbe"):
            f = kw.get("field")
            if kw.get("action") == "set" and f == "request":
                self.hp["request"] = kw.get("value")
                self.hp["serial"] += 1
                self.hp["result"] = json.dumps(dict(success=True, mock=True, cmd=kw.get("value")))
                return self._ok()
            return self._ok(value=self.hp.get(f))
        if t == "jawa/set_thing_props":
            th = next((x for x in self.things if str(x["id"]) == str(kw.get("thing"))), None)
            if th is None:
                return dict(success=False, mock=True)
            if "style" in kw:
                if not self._known(kw["style"]):
                    return dict(success=False, mock=True, message="unknown style %s" % kw["style"])
                th["style"] = kw["style"]
            return self._ok(changed=[k for k in kw if k != "thing"])
        if t == "jawa/battery_set":
            return self._ok(storedEnergyPctAfter=1.0)
        if t == "jawa/set_terrain_batch":
            for op in str(kw.get("ops", "")).split(";"):
                if ":" in op:
                    d, r = op.split(":", 1)
                    if not self._known(d):
                        return dict(success=False, mock=True, message="unknown terrain %s" % d)
                    x, z, w, h = self._rect(r)
                    for i in range(w):
                        for j in range(h):
                            self.terrain[(x + i, z + j)] = d
            return self._ok()
        if t == "jawa/get_terrain_batch":
            x, z, w, h = self._rect(kw["rects"])
            ops = ";".join("%s:%d,%d,1,1" % (self.terrain[(i, j)], i, j) for i in range(x, x + w) for j in range(z, z + h)
                           if (i, j) in self.terrain)
            return self._ok(ops=ops)
        return self._ok()

    def _build(self, kw):
        ops = str(kw.get("ops", ""))
        survived, failed = 0, []
        for op in ops.split(";"):
            if not op:
                continue
            d, rest = op.split(":", 1)
            nums = [int(v) for v in rest.split(",")]
            if not self._known(d) or (kw.get("stuff") and not self._known(kw["stuff"])):
                failed.append(op)
                continue
            self._new(d, nums[0], nums[1], kw.get("faction"), kw.get("stuff"))
            survived += 1
        return self._ok(survived=survived, failed=failed)

    def _static(self, typ, method, args):
        a = args.split("|")
        if method == "ProofFillWithFluid":
            x, z, f, fl = a[0].split(",")
            c = (int(x), int(z))
            if not self._known(fl):
                return self._ok(result="REFUSED: unknown fluid %s" % fl)
            self.fill[c], self.fluid[c] = int(f), fl
            return self._ok(result="OK fill=%s fluid=%s (mock)" % (f, fl))
        if method in MARKER_DEF:
            x, z = (int(v) for v in a[0].split(","))
            th = self._new(MARKER_DEF[method], x, z, "player")
            return self._ok(result="OK %d (mock)" % th["id"])
        if method == "ProofReadout":
            x, z = (int(v) for v in re.split(r"[,;]", args)[:2])
            return self._ok(result="READOUT depth=%d fill=%d (mock)" % (self.depth.get((x, z), 0), self.fill.get((x, z), 0)))
        return self._ok(result="OK %s (mock)" % method)
