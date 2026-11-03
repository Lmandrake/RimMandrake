#!/usr/bin/env python3
"""test_site_river_edges -- LIVE read-only probe: the CURRENT map carries moving river water on at least
SITES[site]["minRiverEdges"] map edges (RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS A2).

test_site_saves.check_map reads no river; river edges were checked only inside make_river_site at build time, so a
v2 save with no river at all would load "verified". This probe closes that gap for the live A2 line, which runs it
right after `test_site_saves.py prove river` (a verified prove leaves the loaded site as the current map).

The instrument is the one river_site.py accepts candidates with: jawa/get_terrain_batch on the map's outer ring
(extensions_rivers.edge_rects) -> site_spec.parse_ops -> extensions_rivers.moving_edges. Touches nothing.

    python.exe src/RimMandrake/Utils/modcheck/test_site_river_edges.py river      # exit 0 holds, 1 does not
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
_NORTHSTAR = os.path.join(os.path.dirname(_UTILS), "FlowWorks", "northstar")
for _p in (_HERE, _UTILS, _NORTHSTAR):
    if _p not in sys.path:
        sys.path.append(_p)

import test_site_saves as T  # noqa: E402


def river_edge_problems(call, site):
    """-> (problems, reading). A site with no minRiverEdges is not a river site (refused, never a pass); an
    unreadable map or ring is a problem, never a zero."""
    import extensions_rivers as RIV
    import site_spec as S
    spec = T.SITES[site]
    want = spec.get("minRiverEdges")
    rd = {"site": site, "want": want}
    if not isinstance(want, int) or want < RIV.MIN_RIVER_EDGES:
        return ["site %s minRiverEdges %r is not a river requirement (>= %d)" % (site, want, RIV.MIN_RIVER_EDGES)], rd
    mi = call("jawa/map_info") or {}
    size = (mi.get("sizeX"), mi.get("sizeZ"))
    rd["size"] = size
    if not all(isinstance(v, int) and v > 0 for v in size):
        return ["map size unreadable: %s" % (str(mi)[:160],)], rd
    if spec.get("size") and size != (spec["size"], spec["size"]):
        return ["current map is %sx%s, want the %s site's %d" % (size[0], size[1], site, spec["size"])], rd
    tb = call("jawa/get_terrain_batch", rects=RIV.edge_rects(size)) or {}
    if not tb.get("success"):
        return ["map-edge terrain unreadable: %s" % (str(tb)[:160],)], rd
    terrain = S.parse_ops(tb.get("ops"))
    ring = 2 * (size[0] + size[1]) - 4
    rd["ringCellsRead"] = len(terrain)
    if len(terrain) < ring:
        return ["map-edge terrain read %d of %d ring cells" % (len(terrain), ring)], rd
    edges = RIV.moving_edges(terrain, size)
    rd["edges"] = edges
    if len(edges) < want:
        return ["moving river water on %d edge(s) %s, want >= %d" % (len(edges), edges, want)], rd
    return [], rd


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site", choices=sorted(k for k, v in T.SITES.items() if "minRiverEdges" in v))
    a = ap.parse_args(argv)
    from rimbridge_client import RimBridge, resolve_endpoint
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t, timeout=120.0) as rb:
        P, rd = river_edge_problems(lambda tool, **kw: rb.call(tool, kw), a.site)
    print("river edges %s: %s %s" % (a.site, "HOLDS" if not P else "FAILS", json.dumps({"problems": P, **rd}, default=str)))
    return 0 if not P else 1


if __name__ == "__main__":
    sys.exit(main())
