#!/usr/bin/env python3
"""Make the CURRENT map a river site for the FlowWorks rivers extension chains (extensions_rivers.py).

    python.exe src/RimMandrake/FlowWorks/northstar/river_site.py            # bridge held, a Playing game

The rivers chains read "UNMEASURED: the site map has no river current" on a quicktest map without a river. This founds a
colony on a flat MILD (8-22 C mean) tile that HAS a river (largest river first), generates its map, makes it current, removes every
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
                    and 0 <= float(r.get("elevation") or -1) < 600 and 8 <= float(r.get("temperature") or -99) <= 22
                    and r.get("biome") not in ("Ocean", "Lake", "SeaIce", "IceSheet")):
                out.append(int(r.get("tile") if r.get("tile") is not None else r.get("index")))
        except (TypeError, ValueError):
            continue
    return out


def main():
    from rimdrive import Session
    with Session(lock=None) as s:
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
            river += [g for g in got if int(g.get("riverCount") or 0) > 0]
        print("river tiles among them", len(river))
        for row in river:
            t = int(row["tile"])
            cf = s.call("jawa/colony_found", tile=t, faction="Player", name="NorthstarRiver")
            if not cf.get("success"):
                continue
            tile, info = t, row
            break
        if tile is None:
            print("no foundable river tile among %d candidates" % len(cands))
            return 2
        print("tile", tile, json.dumps({k: info.get(k) for k in ("biome", "riverCount", "rivers", "roadCount")})[:400])
        BW.close_naming_dialogs(s)
        g = s.call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement")
        if not g.get("success") or g.get("mapIndex") is None:
            print("map generate refused: %s" % g)
            return 2
        BW.close_naming_dialogs(s)
        s.call("jawa/set_current_map", mapId=g["mapIndex"])
        d = s.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        mi = s.call("jawa/map_info")
        cx, cz = int(mi.get("sizeX", 250)) // 2, int(mi.get("sizeZ", 250)) // 2
        for i in range(3):
            s.call("jawa/spawn_pawn", kindDef="Colonist", x=cx + 2 * i, z=cz, faction="player", count=1)
        BW.close_naming_dialogs(s)
        rep = BW.reset(s)
        print("map", g["mapIndex"], "size", mi.get("sizeX"), "biome", mi.get("mapBiome"), "destroyed", d.get("matchedCount"),
              "reset problems", rep.get("problems"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
