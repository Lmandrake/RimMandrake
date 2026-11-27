#!/usr/bin/env python3
"""Selftest: stage_map.empty_map paints its one terrain with clearOverlays=True
(RIMMANDRAKE_FIX_STAGE_MAKE_WHEN_TERRAIN_DOES_NOT_READ_BACK_ON_NEW_TILE). TerrainAt reads floodwater/thin ice (tempGrid) and
Substructure (foundation) before the top grid, so a bare paint leaves those cells showing and set_terrain_batch refuses
(ArchSmall, 2026-11-25, tile 113515: 619 of 10000 cells did not read back). A fake client; no game, no bridge."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage_map  # noqa: E402


class Fake:
    def __init__(self):
        self.calls = []

    def call(self, tool, args, check=False):
        self.calls.append((tool, dict(args)))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": []}
        if tool == "jawa/set_terrain_batch":
            return {"success": True, "readBack": {"rows": 100, "ok": True}}
        return {"success": True}


def main():
    c = Fake()
    stage_map.empty_map(c, 100, 100, lambda s: None)
    paints = [a for t, a in c.calls if t == "jawa/set_terrain_batch"]
    if len(paints) != 1:
        print("FAIL: want one set_terrain_batch call, got %d" % len(paints))
        return 1
    if paints[0].get("clearOverlays") is not True:
        print("FAIL: empty_map's set_terrain_batch has no clearOverlays=True: %r" % paints[0])
        return 1
    if paints[0].get("ops") != "%s:0,0,100,100" % stage_map.TERRAIN:
        print("FAIL: the paint covers the wrong cells: %r" % paints[0])
        return 1
    print("PASS selftest_stage_map_terrain: 1 of 1 (empty_map paints with clearOverlays)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
