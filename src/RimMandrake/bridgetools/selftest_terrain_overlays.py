#!/usr/bin/env python3
"""HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK: a Soil paint must read back as Soil on a flooded, iced or substructured cell.

Run4 2026-10-25 (proof_hose style_hose + realflow): jawa/set_terrain_batch "Soil:<site>" left 4 and 231 cells that "did not
read back", and the blocks aborted SITE. Cause (Verse/TerrainGrid.cs, 1.6): TerrainAt(c) returns tempGrid (floodwater,
ThinIce, LavaShallow) first, then the foundation grid when underGrid is null, and only then topGrid; SetTerrain(Soil) writes
topGrid and nulls underGrid, so both overlays keep showing. The fix: set_terrain_batch's clearOverlays (top layer) strips
the foundation and the temp terrain AFTER SetTerrain, and every unread cell names what it read instead.

Checks:
  1. the C# tool: clearOverlays parameter, its write order (SetTerrain -> RemoveFoundation -> RemoveTempTerrain with no
     terrainOnRemoved), the guard (top layer, not a temporary/foundation def) and the got/temp/foundation diagnostics;
  2. an engine model of TerrainAt/SetTerrain/RemoveFoundation/RemoveTempTerrain drives validation_core._prepare_site over a
     site holding floodwater, thin ice and Substructure: ready (no SITE row); the same site with clearOverlays dropped
     reads "did not read back" and is UNMEASURED SITE (the run4 instance, so the check can fail);
  3. FlowWorks prep_site paints its plots and halo with clearOverlays.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))
CS = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchTerrainTools.cs")
sys.path.insert(0, os.path.join(SRC, "Utils"))
sys.path.insert(0, os.path.join(SRC, "FlowWorks", "northstar"))

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


# ---- 1. the C# source ---------------------------------------------------------------------------------------------------
def body_of(src, name):
    i = src.index("public static async Task<object> %s(" % name)
    j = src.index("[Tool(", i)
    return src[i:j]


def t_csharp():
    src = open(CS, encoding="utf-8").read()
    b = body_of(src, "SetTerrainBatch")
    check(re.search(r"bool\s+clearOverlays\s*=\s*false\)", b) is not None, "C#: set_terrain_batch takes clearOverlays (default false)")
    w = b.find("WriteLayer(grid, cell, def, layer);")
    f = b.find("grid.RemoveFoundation(cell, false)")
    t = b.find("grid.RemoveTempTerrain(cell, false, true)")
    check(0 <= w < f < t, "C#: SetTerrain, then RemoveFoundation (topGrid set first), then RemoveTempTerrain w/o terrainOnRemoved")
    g = b.rfind("if (clearOverlays", 0, f)
    guard = b[g:b.find("\n", g)]
    check(all(k in guard for k in ("clearOverlays", 'IsLayer(layer, "top")', "!def.temporary", "!def.isFoundation")),
          "C#: overlays cleared only for clearOverlays on the top layer with a plain def")
    e = b[b.find('error = "did not read back"'):][:600]
    check(all(k in e for k in ("got =", "temp =", "foundation =", "top =")), "C#: an unread cell names got/temp/foundation/top")


# ---- 2. engine model + validation_core._prepare_site ----------------------------------------------------------------------
TEMPORARY = {"ShallowFloodwater", "ThinIce", "LavaShallow"}
FOUNDATION = {"Substructure"}


class Grid(object):
    """Verse.TerrainGrid as decompiled (1.6): TerrainAt, SetTerrain for a non-layerable def, the two removers."""

    def __init__(self):
        self.top, self.under, self.found, self.temp = {}, {}, {}, {}

    def terrain_at(self, c):
        if self.temp.get(c):
            return self.temp[c]
        if self.under.get(c) is None and self.found.get(c):
            return self.found[c]
        return self.top.get(c) or "Soil"

    def set_terrain(self, c, d):
        if d in TEMPORARY:
            self.temp[c] = d
        elif d in FOUNDATION:
            self.found[c] = d
        else:
            self.under[c] = None        # Soil is not layerable
            self.top[c] = d


class FakeB(object):
    def __init__(self, grid, drop_flag=False):
        self.g, self.drop, self.calls = grid, drop_flag, []

    def call(self, tool, **kw):
        self.calls.append((tool, dict(kw)))
        if tool == "jawa/set_terrain_batch":
            clear = kw.get("clearOverlays") and not self.drop
            bad = 0
            for op in kw["ops"].split(";"):
                name, r = op.split(":")
                x, z, w, h = (int(v) for v in r.split(","))
                for cx in range(x, x + w):
                    for cz in range(z, z + h):
                        c = (cx, cz)
                        if self.g.terrain_at(c) != name:
                            self.g.set_terrain(c, name)
                            if clear and name not in TEMPORARY | FOUNDATION:
                                self.g.found.pop(c, None)
                                self.g.temp.pop(c, None)
                        bad += self.g.terrain_at(c) != name
            if bad:
                return {"success": False, "message": "Applied 1/1 op(s): WARNING %d did not read back." % bad}
            return {"success": True, "cellsFailedVerify": 0}
        if tool == "jawa/get_roof_batch":
            return {"success": True, "roofs": []}
        if tool == "jawa/list_things":
            return {"success": True, "things": []}
        return {"success": True}

    def ticks(self, n):
        return None


def dirty_grid():
    g = Grid()
    for x in range(10, 14):
        g.top[(x, 20)] = "WaterShallow"
        g.temp[(x, 20)] = "ShallowFloodwater"          # a flood over water
    g.temp[(15, 21)] = "ThinIce"                        # ice over soil: TerrainAt != Soil
    g.found[(16, 22)] = "Substructure"                  # gravship foundation, underGrid null
    return g


def t_prepare_site():
    import validation_core as V
    V.reveal = lambda B, rect, ticks=30: {"revealed": True, "fogTriggers": {}}
    rect = (10, 20, 8, 4)
    for drop, want in ((False, True), (True, False)):
        g = dirty_grid()
        B = FakeB(g, drop_flag=drop)
        rows = []
        ok = V._prepare_site(B, rect, rows, "R_site_ready")
        st = [c for c in B.calls if c[0] == "jawa/set_terrain_batch"]
        if not drop:
            check(bool(st) and st[0][1].get("clearOverlays") is True, "_prepare_site paints Soil with clearOverlays=True")
            check(ok is True and not rows, "flood + thin ice + Substructure site reads back Soil: ready, no SITE row")
            check(all(g.terrain_at((x, z)) == "Soil" for x in range(10, 18) for z in range(20, 24)), "every site cell reads Soil")
        else:
            blocked = rows and rows[0].get("status") == "UNMEASURED" and "did not read back" in str(rows[0])
            check(ok is False and bool(blocked), "without clearOverlays the run4 instance recurs: UNMEASURED SITE, did not read back")


# ---- 3. FlowWorks prep_site ---------------------------------------------------------------------------------------------
def t_prep_site():
    src = open(os.path.join(SRC, "FlowWorks", "northstar", "prep_site.py"), encoding="utf-8").read()
    calls = re.findall(r'call\("jawa/set_terrain_batch"[^\n]*', src)
    check(len(calls) == 2 and all("clearOverlays=True" in c for c in calls), "prep_site: both set_terrain_batch calls clear overlays")


def main():
    for t in (t_csharp, t_prepare_site, t_prep_site):
        try:
            t()
        except Exception as ex:  # noqa: BLE001
            check(False, "%s raised %r" % (t.__name__, ex))
    print("%d FAIL" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
