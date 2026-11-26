#!/usr/bin/env python3
"""Live census of TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE (design/RimMandrake/tree_shade_model_2026-10-19.md §6 T2,
live half): on a freshly generated map of each named biome, the share of unroofed ground that tree crowns shade.

For each biome it sets the current debug map's tile to that biome, regenerates the map (Actions > Regenerate Current Map,
the method of src/RimMandrake/bridgetools/prove_biome_quicktest.py), lets the grid rebuild, and reads every cell through
`jawa/shadegrid_read` (canopy, cause). Open ground = every cell whose cause is not roof or indoors and whose terrain (jawa/get_terrain_batch) is not water
by name (WATER; the run prints the top terrains and the names it took for water, so the rule can be checked).
covered = canopy >= 0.99 (the estimate's "covered"); any = canopy > 0. Each row prints MEASURED with the map's tile,
seed-free (a regenerated map differs run to run), and whether the grid cast with a sun vector (a day/night world casts
the disc under the crown: the same area, without the down-sun move).

Run on the machine that hosts the game, with that game's environment, a quicktest map loaded:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python.exe src/RimMandrake/CreatureBehaviors/live_canopy_census.py RM_Greentide RM_Miasma RM_Webwork [--hilliness=Flat]
Exit 0 every biome measured, 2 COULD NOT LOOK for one (named).
"""
import collections
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils")]

SETTLE_TICKS = 120   # the regenerated map's FinalizeInit recompute is enough; a few ticks more let plants settle


def wait_new_map(s, old_id, limit=300):
    t0 = time.time()
    while time.time() - t0 < limit:
        mi = s.call("jawa/map_info") or {}
        if mi.get("success") and mi.get("mapId") != old_id:
            return mi
        time.sleep(3)
    return None


WATER = re.compile(r"water|ocean|lake|river|bog|mire|marsh|swamp|brine|sea", re.I)


def terrain_map(s, w, h):
    """-> {(x, z): terrain defName} from jawa/get_terrain_batch (bands under its 70,000-cell cap), or None."""
    out = {}
    band = max(1, 70000 // w)
    for z0 in range(0, h, band):
        g = s.call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z0, w, min(band, h - z0))) or {}
        for op in (g.get("ops") or "").split(";"):
            if ":" not in op:
                continue
            d, rect = op.split(":", 1)
            q = [int(v) for v in rect.split(",")]
            x0, zz0, ww, hh = q if len(q) == 4 else (q[0], q[1], 1, 1)
            for z in range(zz0, zz0 + hh):
                for x in range(x0, x0 + ww):
                    out[(x, z)] = d
    return out if len(out) == w * h else None


def census(s, w, h, terrain):
    covered = anyc = open_ = 0
    species = {}
    cells = [(x, z) for z in range(h) for x in range(w)]
    for k in range(0, len(cells), 200):
        part = cells[k:k + 200]
        r = s.call("jawa/shadegrid_read", cells=";".join("%d,%d" % c for c in part)) or {}
        rows = r.get("cells") or []
        if len(rows) != len(part):
            return None
        for row in rows:
            cause = row.get("cause")
            if cause in ("roof", "indoors") or WATER.search(terrain.get((row["x"], row["z"]), "")):
                continue
            open_ += 1
            c = row.get("canopy")
            if c is None:
                return None
            if c > 0:
                anyc += 1
            if c >= 0.99:
                covered += 1
                if cause and cause.endswith(" canopy"):
                    species[cause[:-7]] = species.get(cause[:-7], 0) + 1
    return open_, covered, anyc, species


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    biomes = args or ["RM_Greentide", "RM_Miasma", "RM_Webwork"]
    extra = {"hilliness": flags["hilliness"]} if "hilliness" in flags else {}
    from northstar_driver.session import FastSession
    rc = 0
    with FastSession(strict=False, focus=False) as s:
        for b in biomes:
            mi0 = s.call("jawa/map_info") or {}
            tile, old = mi0.get("tile"), mi0.get("mapId")
            w = s.call("jawa/world_tile_set", tiles=str(tile), biome=b, **extra) or {}
            s.call("jawa/world_commit")
            g = s.call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map") or {}
            time.sleep(5)
            mi = wait_new_map(s, old)
            if not (w.get("success") and g.get("success") and mi and mi.get("mapBiome") == b):
                print("COULD NOT LOOK %s: tile_set %s, regen %s, map biome %s" % (
                    b, w.get("success"), g.get("success"), (mi or {}).get("mapBiome")), flush=True)
                rc = 2
                continue
            s.call("jawa/safe_advance", action="start", ticks=SETTLE_TICKS)
            gr = s.call("jawa/shadegrid_read") or {}
            sg = gr.get("shadeGrid") or {}
            terrain = terrain_map(s, mi["sizeX"], mi["sizeZ"])
            if terrain is None:
                print("COULD NOT LOOK %s: the terrain read came back short" % b)
                rc = 2
                continue
            tops = collections.Counter(terrain.values()).most_common(8)
            print("  terrain %s: %s (water by name: %s)" % (b, tops, sorted({t for t in terrain.values() if WATER.search(t)})), flush=True)
            res = census(s, mi["sizeX"], mi["sizeZ"], terrain)
            if res is None:
                print("COULD NOT LOOK %s: a shadegrid read came back short or without canopy (old companion?)" % b)
                rc = 2
                continue
            open_, covered, anyc, species = res
            top = sorted(species.items(), key=lambda kv: -kv[1])[:5]
            print("MEASURED %s tile %s %s: open cells %d, crown-covered %.3f, any crown shade %.3f, directional %s; top "
                  "crowns %s" % (b, tile, mi.get("tileInfo", {}).get("hilliness"), open_, covered / max(1, open_), anyc / max(1, open_), sg.get("isDirectional"),
                                 top), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
