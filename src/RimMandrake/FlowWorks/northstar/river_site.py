#!/usr/bin/env python3
"""Make the CURRENT map a river site for the FlowWorks rivers extension chains (extensions_rivers.py).

    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py            # bridge held, a Playing game
    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py --dry      # the same, on a tile with NO river

The rivers chains read "UNMEASURED: the site map has no river current" on a quicktest map without a river. This founds a
colony on a flat MILD (14-20 C mean, 15 <= |lat| <= 32: map 5 at |lat| <= 25 hit frostbite at night; |lat| <= 15 is PermanentSummer, 42 C at noon on a 22 C-mean tile, heatstroke) tile that HAS a river (largest river first), generates its map, makes it current, removes every
non-colonist, spawns colonists and runs bland_world.reset() so the watch starts bland. Mild on purpose: on a 38 C
quicktest tile (MEASURED 2026-10-06) idle colonists took Heatstroke mid-chain and five components read UNMEASURED. bland_world.setup() is the same
recipe with the opposite tile filter (riverCount == 0). Prints the tile, its rivers and the reset problems; exit 0 only
when the new map is current and reports a river.
"""
import csv
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bland_world as BW  # noqa: E402


def river_candidates(rows):
    out = []
    for r in rows:
        try:
            if (r.get("hilliness") in ("Flat", "SmallHills") and float(r.get("swampiness") or 0) < 0.3
                    and 0 <= float(r.get("elevation") or -1) < 600 and 14 <= float(r.get("temperature") or -99) <= 20
                    and 15 <= abs(float(r.get("lat") or 90)) <= 32
                    and r.get("biome") not in ("Ocean", "Lake", "SeaIce", "IceSheet", "Desert", "ExtremeDesert", "AridShrubland")):
                out.append(int(r.get("tile") if r.get("tile") is not None else r.get("index")))
        except (TypeError, ValueError):
            continue
    return out


DRY = "--dry" in sys.argv     # the opposite site: NO river, for the plot/toggle chains. Their 40x30 Soil repaints cut a
# river and a river cut their plots (MEASURED 2026-10-06: confinement read river cells (122,87..89) as D=4 F=4 "liquid on
# un-dug ground"; the weir pooled over painted Soil). Rivers chains run on a river site, the rest on a dry one.


def main():
    from rimdrive import Session
    with Session(lock=None) as s:
        # the colonists left on the map we are leaving: vanished once the new site stands. Left alone they starve or
        # cook there, and their deaths are game-wide letters the watch reads as colonist_died in whatever chain is
        # running (MEASURED 2026-10-06: three chains UNMEASURED on deaths of map-0 quicktest colonists)
        old_cols = [p["id"] for p in (s.call("jawa/list_pawns", limit=500).get("pawns") or [])
                    if p.get("isPlayer") and not p.get("dead")]
        path = os.path.join(os.environ.get("TEMP") or tempfile.gettempdir(), "river_site_tiles.csv")
        r = s.call("jawa/world_tile_export", path=path)
        if not r.get("success") or not os.path.isfile(path):
            print("world_tile_export failed: %s" % r)
            return 2
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cands = river_candidates(rows)
        print("tiles", len(rows), "flat temperate candidates", len(cands))
        tile, info, river = None, None, []
        for i in range(0, len(cands), 100):           # world_tile_get caps a read at 100 rows
            got = s.call("jawa/world_tile_get", tiles=",".join(str(t) for t in cands[i:i + 100])).get("tiles") or []
            # no mutator/road filter: on 1.6 a river tile commonly carries a river mutator (0 of 7901 passed with it)
            river += [g for g in got if (int(g.get("riverCount") or 0) > 0) != DRY]
        print("river tiles among them", len(river))
        g, tries = None, 0
        for row in river:
            if tries >= 10:
                break
            t = int(row["tile"])
            cf = s.call("jawa/colony_found", tile=t, faction="Player", name=("NorthstarDry" if DRY else "NorthstarRiver"))
            if not cf.get("success"):
                continue
            tries += 1
            BW.close_naming_dialogs(s)
            g = s.call("jawa/world_tile_map_generate", tile=t, suggestedMapParent="Settlement")
            if not g.get("success") or g.get("mapIndex") is None:
                print("tile", t, "map generate refused: %s" % g.get("message"))
                continue
            BW.close_naming_dialogs(s)
            s.call("jawa/set_current_map", mapId=g["mapIndex"])
            # a tile's riverCount is not a promise of a CURRENT on its map (MEASURED 2026-10-06: tile 24, riverCount 2,
            # ProofGrid current=0): ask the mod's own grid and move on when it is empty
            grid = str((s.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofGrid",
                               args="-") or {}).get("result", ""))
            kv = dict(p.split("=", 1) for p in grid.split() if "=" in p)
            print("tile", t, row.get("biome"), "riverCount", row.get("riverCount"), "grid:", grid[:120])
            # a FAST lane too: ProofShove needs a 4-cell fast run (a creek with edge lanes only reads UNMEASURED)
            # no indestructible scenery under the extension plot grid (centred, ~ +-64 cells with buffers): a steam geyser
            # in plot D took the pump's cell and ProofPump read it as "no pump" (MEASURED 2026-10-06, tile 45)
            scenery = [d for d in BW.NATURAL_SCENERY
                       if s.call("jawa/list_things", defName=d, rect="61,61,130,130", limit=5).get("things")]
            if scenery:
                print("tile", t, "has", scenery, "inside the plot grid: next tile")
                continue
            if DRY or (int(kv.get("current", 0) or 0) > 0 and int(kv.get("fast", 0) or 0) > 0):
                tile, info = t, row
                break
        if tile is None:
            print("no river tile with a current among %d tried" % tries)
            return 2
        d = s.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        mi = s.call("jawa/map_info")
        # OFF the extension plot grid (centred on the map, +-~56 cells) and DRAFTED: colonists spawned at the centre
        # wandered into the plots' pits and read as colonist_damaged "Blunt by nobody" (the mod's fall damage) in five
        # components (MEASURED 2026-10-06, map 5).
        cx, cz = int(mi.get("sizeX", 250)) // 2, 30
        for i in range(3):
            sp = s.call("jawa/spawn_pawn", kindDef="Colonist", x=cx + 2 * i, z=cz, faction="player", count=1)
            for p in sp.get("pawns") or []:
                s.call("jawa/set_draft", pawnId=p.get("id"), drafted=True)
        BW.close_naming_dialogs(s)
        for pid in old_cols:
            s.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        rep = BW.reset(s)
        print("map", g["mapIndex"], "size", mi.get("sizeX"), "biome", mi.get("mapBiome"), "destroyed", d.get("matchedCount"),
              "reset problems", rep.get("problems"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
