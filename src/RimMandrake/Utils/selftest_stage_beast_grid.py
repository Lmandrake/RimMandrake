#!/usr/bin/env python3
"""Offline test of stage_beast_grid.py: layout invariants + the live stage against a fake bridge.

Checks: every cell is inside the rect and on a distinct square; pens never share a cell with a wall; the stage
REFUSES on a running clock and never calls set_time_speed; raids are set to 0 with the prior value saved; one
spawn per creature, a human per row; walls = 4 per creature.   python3 selftest_stage_beast_grid.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage_beast_grid as sg  # noqa: E402


def beasts(n):
    out = []
    for i in range(n):
        out.append({"def": "RM_T%d" % i, "kind": "RM_T%d" % i, "kinds": ["RM_T%d" % i], "label": "t%d" % i,
                    "pkg": "mandrake.rm.biomes" if i < n * 2 // 3 else "mandrake.rsw.swbestiary",
                    "mod": "m", "onTier": True, "draw": 0.5 + (i % 9), "body": 1.0, "intel": "Animal",
                    "flyer": False, "art": "none"})
    return out


class FakeBridge:
    def __init__(self, running=False):
        self.calls, self.pawns, self.walls, self.running = [], [], [], running
        self.tick = 100
        self.diff = {"threatScale": 1.0, "allowBigThreats": True}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def call(self, tool, params=None, check=True, **kw):
        params = dict(params or {}, **kw)
        self.calls.append((tool, params))
        if tool == "jawa/map_info":
            if self.running:
                self.tick += 50
            return {"success": True, "ticksGame": self.tick, "sizeX": 250, "sizeZ": 250, "mapId": 0, "mapBiome": "X"}
        if tool == "jawa/difficulty_tune":
            self.diff.update({k: v for k, v in params.items() if k in self.diff})
            return dict(self.diff, success=True)
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(p) for p in self.pawns]}
        if tool == "jawa/spawn_pawn":
            self.pawns.append({"id": len(self.pawns) + 1, "x": params["x"], "z": params["z"], "hostile": False, "dead": False})
            return {"success": True}
        if tool == "jawa/build_batch":
            for op in params["ops"].split(";"):
                x, z = op.split(":")[1].split(",")
                self.walls.append({"x": int(x), "z": int(z)})
            return {"success": True}
        if tool == "jawa/list_things":
            return {"success": True, "things": list(self.walls)}
        return {"success": True, "destroyedCount": 0, "clearedCount": 0}


def run(running):
    import types
    import rimbridge_client as rc
    fb = FakeBridge(running)
    rc.resolve_endpoint = lambda: ("h", 1, "t")
    rc.RimBridge = lambda **kw: fb
    sg.WORK = tempfile.mkdtemp()
    sg.PRIOR, sg.KEYMD, sg.LASTRUN = (os.path.join(sg.WORK, n) for n in ("p.json", "k.md", "l.json"))
    args = types.SimpleNamespace(at="", per_row=10, ground="Concrete", stuff="Steel", no_clear=False, force_clear=False)
    rc_ = sg.live_stage(args, {"built": "t", "source": "fake", "tierModsConfig": [], "activeCount": 0, "beasts": beasts(90)})
    return fb, rc_


def main():
    lay, used = sg.fit_layout(beasts(90), 10, (6, 6), 250, 250)
    ox, oz, w, h = lay["rect"]
    seen = set()
    for c in lay["cells"]:
        assert ox <= c["x"] < ox + w and oz <= c["z"] < oz + h, c
        assert (c["x"], c["z"]) not in seen
        seen.add((c["x"], c["z"]))
    walls = {(c["x"] + dx, c["z"] + dz) for c in lay["cells"] for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    assert all(ox <= x < ox + w and oz <= z < oz + h for x, z in walls), "a wall falls outside the cleared rect"
    assert not walls & seen, "a wall sits on a pen cell"
    humans = {(r["x"], r["z"]) for r in lay["rows"]}
    assert not walls & humans and not humans & seen

    fb, rcode = run(running=True)
    assert rcode == 3 and not [c for c in fb.calls if c[0] == "jawa/spawn_pawn"], "must refuse on a running clock"
    fb, rcode = run(running=False)
    assert rcode == 0, rcode
    tools = [c[0] for c in fb.calls]
    assert "rimworld/set_time_speed" not in tools, "touched game speed"
    spawns = [c for c in fb.calls if c[0] == "jawa/spawn_pawn"]
    assert len(spawns) == 90 + len(lay["rows"]), len(spawns)
    assert len(fb.walls) == 4 * 90, len(fb.walls)
    assert fb.diff["threatScale"] == 0 and fb.diff["allowBigThreats"] is False
    assert json.load(open(sg.PRIOR)) == {"threatScale": 1.0, "allowBigThreats": True}
    print("selftest_stage_beast_grid: OK (%d rows, per_row %d)" % (len(lay["rows"]), used))
    return 0


if __name__ == "__main__":
    sys.exit(main())
