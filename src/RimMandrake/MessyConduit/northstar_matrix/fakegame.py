"""Fake-game mode: execute a placement plan against an in-memory map, read the scene back, run the oracle.

This is the offline stand-in for the bridge. It interprets ONLY the step vocabulary placer.py emits, keyed on
game (x, z) cells, and re-derives every connector's hookup INDEPENDENTLY of the scene's declared one, by emulating
PowerConnectionMaker.BestTransmitterForConnector at the moment the connector spawns (decompiled 1.6, RimSage
2026-10-02: 13x13 square around the connector Position, wire-able transmitters only, squared distance to the
transmitter's Position, scan z-ascending then x-ascending, strict <). So a wrong build ORDER or an ambiguous
hookup in a plan shows up here as an oracle mismatch, before any game time is spent.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import scenes as S  # noqa: E402

DEF_ROLE = {v["def"]: k for k, v in S.DEVICE_DEFS.items()}
CONDUITS = ("PowerConduit", "WaterproofConduit")


class FakeMap(object):
    def __init__(self):
        self.terrain = {}
        self.conduit = set()
        self.edifice = {}            # cell -> ("Wall"|"Door"|"Granite")
        self.things = []             # devices: dict(def, pos, rot, id, footprint, hookup, charged)
        self.plants = set()
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
                else:
                    self.spawn(d, c, n[2] if len(n) > 2 else 0)
        elif name == "jawa/battery_set":
            tid = vars_.get(a["thing"], a["thing"])
            for t in self.things:
                if t["id"] == tid:
                    t["charged"] = float(a["value"]) > 0
        elif name == "jawa/set_plants":
            for d, n in self._ops(a["ops"]):
                self.plants.add((n[0], n[1]))
        # every other tool (fog, roof, commit, camera, ticks, screenshot) changes nothing the graph reads

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
