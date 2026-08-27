#!/usr/bin/env python3
"""
apply_wall_stuff.py - colour the hull with MATERIAL instead of paint.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

🔴 WHY THIS EXISTS. The dev `T: Set Color` tool has a per-GAME-SESSION budget of
roughly 380 invocations. Measured: 759 painted on the first run of the session,
then 384, then 384, then 250+134+0 across fresh PROCESSES - so it is the game that
degrades, not the client, and no reconnect clears it. After that every menu misses
and `execute_debug_action` still answers success.

The way round it is not to paint at all. `GravshipHull` takes any Metallic stuff,
and stuff carries colour: DinoChitin renders a rich warm brown, Bioferrite a dark
plum-brown. So the Corrosion Halo idea - deep colour at the wounds, warmer where
the plating is sound - is expressed in MATERIAL. One call per material, permanent,
survives a reload, and needs no dev tool.

⚠️ Rebuilding a wall cell WIPES what shares it. The ship's conduits run under the
hull line, so every PowerConduit / HiddenConduit / VGE_AstrofuelPipe on a wall cell
is re-placed afterwards from the layout, which is the authority for where they were.
"""
import argparse, collections, io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gravship_layout import Layout
from rimbridge_client import RimBridge, resolve_endpoint

# only the DEEPEST three of the hot ramp become plum - taking all six put dark
# plating on 60% of the hull and swamped the halo it was supposed to draw.
HOT = {"Structure_UmberBurnt", "ReddishBrown"}
# ⚠️ First attempt made BOTH materials brown and the ship lost its silhouette
# entirely - hull and deck merged into one mass at map zoom. The hull's job is to
# DRAW THE SHAPE, so the sound plating has to stay lighter than the deck. MegaBone
# is a warm grey that reads light without going back to cold steel.
STUFF_HOT, STUFF_COLD = "DinoChitin", "MA_MegaBone"
CONDUIT = {"PowerConduit", "HiddenConduit", "VGE_AstrofuelPipe"}

ap = argparse.ArgumentParser()
ap.add_argument("--plan", required=True)
ap.add_argument("--layout", required=True)
ap.add_argument("--offset", default="82,58")
ap.add_argument("--apply", action="store_true")
a = ap.parse_args()
ox, oz = [int(v) for v in a.offset.split(",")]
plan = json.load(open(a.plan))
groups = collections.defaultdict(list)
for col, cells in plan["wallColor"].items():
    for c in cells:
        groups[STUFF_HOT if col in HOT else STUFF_COLD].append(tuple(c))

lay = Layout.load(a.layout)
conduits = collections.defaultdict(list)
for z in range(lay.height):
    for x in range(lay.width):
        cl = lay.cell(x, z)
        if not cl:
            continue
        for t in cl.things:
            if t.defName in CONDUIT:
                conduits[t.defName].append((x + ox, z + oz))
wallset = {c for v in groups.values() for c in v}
overlap = {d: [c for c in v if c in wallset] for d, v in conduits.items()}
print("walls %d -> %s" % (len(wallset), {k: len(v) for k, v in groups.items()}))
print("conduits on wall cells that will be wiped and restored: %s"
      % {k: len(v) for k, v in overlap.items()})
if not a.apply:
    sys.exit(0)

host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=900.0) as rb:
    for stuff, cells in groups.items():
        placed = 0
        for i in range(0, len(cells), 350):
            ops = ";".join("GravshipHull:%d,%d" % c for c in cells[i:i + 350])
            r = rb.call("jawa/build_batch", {"ops": ops, "stuff": stuff,
                                             "faction": "PlayerColony", "readBack": 0})
            placed += r.get("placed") or 0
        print("%-12s placed %d of %d" % (stuff, placed, len(cells)))
    for d, cells in overlap.items():
        if not cells:
            continue
        ops = ";".join("%s:%d,%d" % (d, c[0], c[1]) for c in cells)
        r = rb.call("jawa/build_batch", {"ops": ops, "faction": "PlayerColony", "readBack": 0})
        print("restored %-18s %s of %d" % (d, r.get("placed"), len(cells)))
    rb.call("jawa/map_commit", {})
    t = rb.call("jawa/list_things", {"rect": "83,59,86,133", "defName": "GravshipHull", "limit": 1200})
    print("hull cells on map now: %s" % t.get("countMatched"))
