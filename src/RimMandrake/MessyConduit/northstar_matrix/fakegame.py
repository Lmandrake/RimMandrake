"""Fake-game mode: execute a placement plan against an in-memory map, read the scene back, run the oracle.

This is the offline stand-in for the bridge. It interprets ONLY the step vocabulary placer.py emits, keyed on
game (x, z) cells, and re-derives every connector's hookup INDEPENDENTLY of the scene's declared one, by emulating
PowerConnectionMaker.BestTransmitterForConnector at the moment the connector spawns (decompiled 1.6, RimSage
2026-10-02: 13x13 square around the connector Position, wire-able transmitters only, squared distance to the
transmitter's Position, scan z-ascending then x-ascending, strict <). So a wrong build ORDER or an ambiguous
hookup in a plan shows up here as an oracle mismatch, before any game time is spent.
"""
import heapq
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import scenes as S  # noqa: E402

DEF_ROLE = {v["def"]: k for k, v in S.DEVICE_DEFS.items()}
CONDUITS = ("PowerConduit", "WaterproofConduit")
REEL = "RM_HoseReel"
WIRE_VISIBLE = 0.11 * 25.0 / 32.0          # HoseMath.WireVisibleWidth
FLAT_VISIBLE, PLUMP_EXTRA, MIN_BEND, MAX_LENGTH, TRANSITION = 0.38, 0.085, 1.2, 30.0, 30   # HoseMath / HoseSettings defaults


class FakeMap(object):
    def __init__(self):
        self.terrain = {}
        self.conduit = set()
        self.edifice = {}            # cell -> ("Wall"|"Door"|"Granite")
        self.things = []             # devices: dict(def, pos, rot, id, footprint, hookup, charged)
        self.plants = set()
        self.reels = {}              # (x, z) -> hose state (a crude stand-in for CompHoseReel + HoseProbe)
        self.next_id = 1
        self.log = []

    # ------------------------------------------------------------ emulated engine rules
    def wire_parents(self):
        """(position, thing or 'conduit') of every transmitter a connector may wire to."""
        out = [(c, "conduit") for c in self.conduit]
        for t in self.things:
            r = S.DEVICE_DEFS[DEF_ROLE[t["def"]]]
            if r["transmitter"] and r.get("wire_parent"):
                out.append((t["pos"], t))
        return out

    def best_transmitter(self, pos):
        best, bd = None, 1e18
        cand = {}
        for c, t in self.wire_parents():
            if abs(c[0] - pos[0]) <= 6 and abs(c[1] - pos[1]) <= 6:
                cand.setdefault(c, t)            # GetTransmitter: first transmitter in the cell
        for c in sorted(cand, key=lambda q: (q[1], q[0])):
            d = (c[0] - pos[0]) ** 2 + (c[1] - pos[1]) ** 2
            if d < bd:
                best, bd = (c, cand[c]), d
        return best

    # ------------------------------------------------------------ step interpreter
    def _ops(self, s):
        for op in s.split(";"):
            name, rest = op.split(":")
            nums = [int(v) for v in rest.split(",")]
            yield name, nums

    def run(self, steps):
        vars_ = {}
        for st in steps:
            k = st["kind"]
            if k == "tool":
                self.tool(st["tool"], st["args"], vars_)
            elif k == "resolve_thing":
                hit = [t for t in self.things if t["def"] == st["def"] and list(t["pos"]) == list(st["cell"])]
                vars_[st["as"]] = hit[0]["id"] if hit else None
            elif k == "hose_probe":
                self.hose_probe(st["cmd"])
            elif k == "hose_census":
                pass                                   # the census is read by whoever asks (hose_probe("census"))
            elif k == "cleanup":
                pass                                   # leave the map built: read_back() is taken after the run
        return self

    def tool(self, name, a, vars_):
        if name == "jawa/destroy_batch":
            x, z, w, h = [int(v) for v in a["rects"].split(",")]
            inside = lambda c: x <= c[0] < x + w and z <= c[1] < z + h  # noqa: E731
            self.conduit = {c for c in self.conduit if not inside(c)}
            self.edifice = {c: v for c, v in self.edifice.items() if not inside(c)}
            self.things = [t for t in self.things if not inside(t["pos"])]
            self.plants = {c for c in self.plants if not inside(c)}
            self.reels = {c: r for c, r in self.reels.items() if not inside(c)}
        elif name == "jawa/set_terrain_batch":
            for d, n in self._ops(a["ops"]):
                x, z, w, h = n
                for i in range(x, x + w):
                    for j in range(z, z + h):
                        self.terrain[(i, j)] = d
        elif name == "jawa/build_batch":
            for d, n in self._ops(a["ops"]):
                c = (n[0], n[1])
                if d in CONDUITS:
                    self.conduit.add(c)
                elif d in ("Wall", "Door", "Granite"):
                    self.edifice[c] = d
                elif d == REEL:
                    self.reels[c] = {"far": None, "laid": False, "flow": False, "on_ticks": 0, "lay": None}
                else:
                    self.spawn(d, c, n[2] if len(n) > 2 else 0)
        elif name == "rimworld/step_game_ticks":
            self.hose_tick(int(a.get("ticks", 0)))
        elif name == "jawa/battery_set":
            tid = vars_.get(a["thing"], a["thing"])
            for t in self.things:
                if t["id"] == tid:
                    t["charged"] = float(a["value"]) > 0
        elif name == "jawa/set_plants":
            for d, n in self._ops(a["ops"]):
                self.plants.add((n[0], n[1]))
        # every other tool (fog, roof, commit, camera, ticks, screenshot) changes nothing the graph reads

    # ------------------------------------------------------------ hose kit stand-in (HoseProbe vocabulary)
    def _blocked(self, c):
        return self.edifice.get(c) in ("Wall", "Door", "Granite")

    def _route(self, a, b):
        """Shortest 8-connected route length round walls (no diagonal squeeze past a blocked corner), or None."""
        dist, pq = {a: 0.0}, [(0.0, a)]
        lim = 80
        while pq:
            d, c = heapq.heappop(pq)
            if c == b:
                return d
            if d > dist.get(c, 1e18):
                continue
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (c[0] + dx, c[1] + dz)
                    if (dx, dz) == (0, 0) or self._blocked(n) or abs(n[0] - a[0]) > lim or abs(n[1] - a[1]) > lim:
                        continue
                    if dx and dz and (self._blocked((c[0] + dx, c[1])) or self._blocked((c[0], c[1] + dz))):
                        continue
                    nd = d + math.hypot(dx, dz)
                    if nd < dist.get(n, 1e18):
                        dist[n] = nd
                        heapq.heappush(pq, (nd, n))
        return None

    def hose_check(self, reel, far):
        if not (0 <= far[0] < 250 and 0 <= far[1] < 250):
            return "out of bounds"
        if math.hypot(far[0] - reel[0], far[1] - reel[1]) > MAX_LENGTH:
            return "too far"
        if self._blocked(far):
            return "target blocked"
        r = self._route(tuple(reel), tuple(far))
        return None if r is not None and r <= MAX_LENGTH else "no route"

    def hose_tick(self, n):
        for r in self.reels.values():
            if r["flow"]:
                r["on_ticks"] += n

    def hose_probe(self, cmd):
        verb, _, arg = cmd.partition(":")
        if verb in ("defaults", "census"):
            return self.hose_census() if verb == "census" else {"success": True}
        val = None
        if "=" in arg:
            arg, val = arg.split("=", 1)
        a = [int(v) for v in arg.split(",")]
        r = self.reels.get((a[0], a[1]))
        if r is None:
            return {"success": False, "error": "no hose reel at %d,%d" % (a[0], a[1])}
        if verb == "check":
            return {"success": True, "reason": self.hose_check((a[0], a[1]), (a[2], a[3]))}
        if verb == "lay":
            why = self.hose_check((a[0], a[1]), (a[2], a[3]))
            if why is None:
                path = self._route((a[0], a[1]), (a[2], a[3]))
                flat = max(path, math.hypot(a[2] - a[0], a[3] - a[1])) * 1.02
                r.update(far=(a[2], a[3]), laid=True, lay={"path": path, "flat": flat})
            return {"success": why is None, "reason": why, "layOk": r["lay"] is not None}
        if verb == "flow":
            r["flow"] = val in ("on", "true", "1")
            if not r["flow"]:
                r["on_ticks"] = 0
            return {"success": True}
        return {"success": False, "error": "unknown verb"}

    def hose_census(self):
        hoses = []
        for c, r in sorted(self.reels.items()):
            blend = min(1.0, r["on_ticks"] / float(TRANSITION))
            eased = blend * blend * (3 - 2 * blend)
            state = "Plump" if blend >= 1 else ("Filling" if blend > 0 else "Flat")
            vis = FLAT_VISIBLE + PLUMP_EXTRA * eased
            h = {"id": 1, "kind": "Hose", "reel": list(c), "far": list(r["far"] or c), "laid": r["laid"], "layOk": r["lay"] is not None,
                 "end": "Nozzle", "state": state, "transitions": 0 if state == "Flat" else 1, "blend": round(blend, 4),
                 "eased": round(eased, 4), "visibleWidth": round(vis, 4), "widthOverWire": round(vis / WIRE_VISIBLE, 4),
                 "provider": "debug", "signal": r["flow"], "debugFlowing": r["flow"], "history": []}
            if r["lay"]:
                f = r["lay"]["flat"]
                h.update(pathLen=round(f, 3), flatLen=round(f, 3), plumpLen=round(f * 0.98, 3), poseLen=round(f * (1 - 0.02 * eased), 3),
                         straight=round(math.hypot(r["far"][0] - c[0], r["far"][1] - c[1]), 3), minBendFlat=MIN_BEND, minBendPlump=MIN_BEND,
                         selfIntersects=False, couplings=2, joints=0, points=int(f) + 2,
                         fellBack=False, geometryHash="%016x" % (hash((c, r["far"])) & (2 ** 64 - 1)), unwalkablePoints=0)
            hoses.append(h)
        return {"success": True, "cmd": "census", "transitionTicks": TRANSITION, "minBendSetting": MIN_BEND,
                "wireVisibleWidth": round(WIRE_VISIBLE, 4), "texturesInstalled": True, "hoses": hoses}

    def spawn(self, d, pos, rot):
        role = DEF_ROLE[d]
        w, h = S.DEVICE_DEFS[role]["size"]
        if rot not in (0,):
            raise ValueError("fake game places rot North only, got %s" % rot)
        x0, z0 = pos[0] - (w - 1) // 2, pos[1] - (h - 1) // 2
        t = {"def": d, "pos": pos, "id": "Thing_%d" % self.next_id, "x0": x0, "z0": z0, "w": w, "h": h,
             "charged": False, "hookup": None}
        self.next_id += 1
        if not S.DEVICE_DEFS[role]["transmitter"]:
            b = self.best_transmitter(pos)
            t["hookup"] = b[0] if b and b[1] == "conduit" else None
            t["parent"] = "conduit" if b and b[1] == "conduit" else (b[1]["id"] if b else None)
        self.things.append(t)

    # ------------------------------------------------------------ read the scene back
    def read_back(self, plan, name):
        x0, z0, w, h = plan["site"]
        X0, Z0 = plan["origin"]
        H = h - 4
        W = w - 4

        def s(c):
            return [c[0] - X0, (H - 1) - (c[1] - Z0)]
        devs = []
        for t in self.things:
            role = DEF_ROLE[t["def"]]
            if not S.DEVICE_DEFS[role]["transmitter"] and t["hookup"] is None:
                continue                              # wired to nothing we draw: no node (adapter skips it)
            top = s((t["x0"], t["z0"] + t["h"] - 1))
            d = {"id": t["id"], "role": role, "x": top[0], "y": top[1], "w": t["w"], "h": t["h"],
                 "hookup": s(t["hookup"]) if t["hookup"] else None, "charged": t["charged"], "active": False,
                 "on": True}
            devs.append(d)
        return {"format": "mc_scene/1", "name": name, "topology": "readback", "w": W, "h": H,
                "conduit": sorted(s(c) for c in self.conduit),
                "walls": sorted(s(c) for c, v in self.edifice.items() if v == "Wall"),
                "doors": sorted(s(c) for c, v in self.edifice.items() if v == "Door"),
                "rock": sorted(s(c) for c, v in self.edifice.items() if v == "Granite"),
                "water": sorted(s(c) for c, v in self.terrain.items() if v == "WaterDeep"),
                "trees": sorted(s(c) for c in self.plants), "devices": devs,
                "aerial": None, "hose": None, "break_cell": None, "intended_dense": True, "notes": []}


def apply(plan, name="fake"):
    return FakeMap().run(plan["steps"]).read_back(plan, name)


def strip_ids(g):
    """Device ids differ between spec and read-back (Thing_N vs src/h1): compare graphs by device ROLE+cell."""
    import copy
    g = copy.deepcopy(g)
    g.pop("devices_live", None)

    def lab(e):
        return e if not (len(e) == 2 and str(e[1]).startswith("dev:")) else [e[0], "dev"]
    g["cord_ends"] = sorted((sorted([lab(a), lab(b)], key=repr) for a, b in g["cord_ends"]), key=repr)
    return g


def roundtrip(sc, case, origin=(150, 150)):
    """Spec -> plan -> fake game -> read-back -> oracle; returns (diff list, readback). [] = the oracle of what the
    plan BUILDS equals the oracle of what the scene MEANS (aerial/hose excluded: unbuilt)."""
    import oracle as O
    import placer as P
    pl = P.plan(sc, case, origin)
    rb = apply(pl, sc["name"])
    a = strip_ids(O.expect(dict(sc, aerial=None, hose=None), case["tangle"]))
    b = strip_ids(O.expect(rb, case["tangle"]))
    diffs = [(k, a[k], b[k]) for k in a if a[k] != b[k]]
    return diffs, rb
