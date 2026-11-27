#!/usr/bin/env python3
"""selftest_canary.py - the vanilla canary's choice of cell (validity._empty_cell, validity.canary).

Page: design/specs/2026-11-27-canary-plant-only-cell/boundary.md; each promise there is a test of its name here.
Red before the fix: plant_only_cell_when_no_bare_cell (STEVE_LANE_CANARY_RED_F99275, _8A39DE: every cell within 12 of
the anchor held grass, the canary went red (HARNESS) on a healthy session and paused the SteveDesktop lane).
Offline, no game: a fake session holds the cells. The other canary cases stay in selftest_reuse.py (t_validity_module).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import validity  # noqa: E402

FAILS = []
GRASS = "Plant_Grass"


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


class Sess(object):
    """Cells (x, z) -> defNames; off-map cells raise like rimdrive's cell(). `plants` False refuses the plant read."""

    def __init__(self, cells, size=40, plants=True):
        self.cells, self.size, self.plants = {k: list(v) for k, v in cells.items()}, size, plants
        self.calls, self.destroyed, self.spawned, self.list_args = [], [], [], None

    @staticmethod
    def _xz(spec):
        x, z = spec.split(":")[-1].split(",")[:2]
        return int(x), int(z)

    def things_at(self, x, z):
        if not (0 <= x < self.size and 0 <= z < self.size):
            raise RuntimeError("get_cell_info(%d, %d) failed: out of bounds" % (x, z))
        return list(self.cells.get((x, z), []))

    def call(self, tool, **p):
        self.calls.append(tool)
        if tool == "rimworld/get_ui_state":
            return {"programState": "Playing"}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "c1", "isPlayer": True, "intelligence": "Humanlike"}]}
        if tool == "jawa/list_things":
            self.list_args = p
            if not self.plants:
                return {"success": False, "message": "No current map."}
            rx, rz, rw, rh = (int(v) for v in p["rect"].split(","))
            return {"success": True, "isCompleteList": True,
                    "things": [{"def": d, "x": x, "z": z} for (x, z), ds in self.cells.items() for d in ds
                               if d == GRASS and rx <= x < rx + rw and rz <= z < rz + rh]}
        if tool == "jawa/spawn_batch":
            c = self._xz(p["ops"])
            self.spawned.append(c)
            self.cells.setdefault(c, []).append("Steel")
            return {"success": True}
        if tool == "jawa/destroy_batch":
            # honours `categories` as jawa/destroy_batch does (its default is Plant), so "the grass stays" is the
            # canary's own Item-only cleanup, not this fake's: a cleanup that also names Plant, or drops the
            # categories, goes red here
            cats = set((p.get("categories") or "Plant").replace(" ", ",").split(",")) - {""}
            c = self._xz(p["rects"])
            self.destroyed.append(c)
            self.cells[c] = [d for d in self.cells.get(c, [])
                             if not (("Plant" if d == GRASS else "Filth" if d.startswith("Filth") else "Item") in cats)]
            return {"success": True}
        return {"success": True}


def grass(lo=0, hi=40):
    return {(x, z): [GRASS] for x in range(lo, hi) for z in range(lo, hi)}


def t_bare_cell_first():
    cells = grass()
    cells[(11, 10)] = []
    s = Sess(cells)
    r = validity.canary(s, (10, 10))
    ok(r["ok"] and s.spawned == [(11, 10)] and "jawa/list_things" not in s.calls,
       "bare-cell-first: a bare cell in the rings is taken, and no plant read is made", (r, s.spawned))


def t_plant_only_cell_when_no_bare_cell():
    s = Sess(grass())
    r = validity.canary(s, (10, 10))
    c = s.spawned[0] if s.spawned else None
    ok(r["ok"] and c == (10, 10) and s.destroyed == [c] and s.cells[c] == [GRASS]
       and (s.list_args or {}).get("group") == "Plant" and s.calls.count("jawa/list_things") == 1,
       "plant-only-cell-when-no-bare-cell: every cell grassy -> green on the first plant-only cell, one plant read, "
       "the grass stays", (r, s.spawned, s.list_args))


def t_never_on_a_non_plant_thing():
    cells = grass()
    for x in range(-2, 23):
        for z in range(-2, 23):
            if (x, z) in cells:
                cells[(x, z)] = [GRASS, "Steel"] if (x + z) % 2 else ["Filth_Dirt"]
    cells[(22, 22)] = [GRASS]          # the one plant-only cell, at the ring edge
    s = Sess(cells)
    r = validity.canary(s, (10, 10))
    ok(r["ok"] and s.spawned == [(22, 22)] and s.destroyed == [(22, 22)],
       "never-on-a-non-plant-thing: a cell with an item or filth beside its plant is passed over", (r, s.spawned))


def t_no_usable_cell_is_red():
    s = Sess({k: [GRASS, "Steel"] for k in grass()})
    r = validity.canary(s, (10, 10))
    ok(not r["ok"] and not s.spawned and not s.destroyed and any("plant-only" in p for p in r["problems"]),
       "no-usable-cell-is-red: every cell holds an item -> red, nothing spawned or destroyed", r)
    s = Sess(grass(), plants=False)
    r = validity.canary(s, (10, 10))
    ok(not r["ok"] and not s.spawned and not s.destroyed,
       "no-usable-cell-is-red: a refused plant read takes no cell -> red, nothing spawned or destroyed", r)


def t_plant_read_never_negative():
    s = Sess(grass())
    r = validity.canary(s, (3, 0))
    rect = [int(v) for v in (s.list_args or {}).get("rect", "-1,-1,0,0").split(",")]
    ok(r["ok"] and min(rect[:2]) >= 0 and rect[0] + rect[2] == 16 and rect[1] + rect[3] == 13
       and min(s.spawned[0]) >= 0,
       "plant-read-never-negative: near the low edge the plant rect is clamped at 0 and keeps its far edges",
       (r, rect, s.spawned))


def main():
    t_bare_cell_first()
    t_plant_only_cell_when_no_bare_cell()
    t_never_on_a_non_plant_thing()
    t_no_usable_cell_is_red()
    t_plant_read_never_negative()
    print("SELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
