#!/usr/bin/env python3
"""Selftest: the ROPESIDES verdict of live_deck_art_picks.py --draw-order --rope-sides (pure functions, no game).

Item RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER. What covers a colonist on a bridge deck is the depth
test of each rope vertex's height against his drawn nodes (every section sub-mesh is drawn before him, its bounds at y 0). The
verdict reads the rope heights on the squares at him (jawa/cell_draw_census squareY; a section's whole rope sub-mesh mixes
bridges) against his drawn heights (jawa/pawn_render_nodes). The base build's live readings (SteveDesktop job
J20261127T132644Z-f03cad, every rope at PawnUnused 8.7805) must read FAIL; the fixed build's (J20261127T140548Z-4cd112: far
rope 7.6829, near 8.7805, his nodes 8.4357..8.4613 on ew4; on ew2 a square holds both sides) must read PASS.
Run: python3 src/RimMandrake/FlowWorks/northstar/selftest_live_deck_rope_sides.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_deck_art_picks as L  # noqa: E402

UNUSED, ROPE = 8.7805, 7.6829          # AltitudeLayer.PawnUnused and PawnRope, as the census reads them
EW4_NODES = (8.4055, 8.4311)           # ew4's colonist, drawn node by node (base live reading)

fails = []


def sq(*spans, vert=(ROPE, UNUSED)):
    """cable_ys rows: the rope on a square (squareY) and the whole sub-mesh it belongs to (vertY: every bridge of its section)."""
    return [{"square": s_, "vert": vert} for s_ in spans]


def check(name, ok, got=None):
    if not ok:
        fails.append("%s (got %r)" % (name, got))


def nodes(ys, path="nodes"):
    return {"success": True, "drawPath": path, "requests": [{"drawn": [0, y, 0], "renderQueue": 2900} for y in ys]}


def census(*spans, material="Custom/Cutout_RM_Cable_Chain", drawn=True):
    return {"success": True, "draws": [{"material": material, "drawn": drawn, "squareY": {"n": 4, "min": a, "max": b},
                                        "vertY": {"n": 4, "min": a, "max": b}} for a, b in spans]}


# the base build: every rope over him, the north one too -> FAIL (nothing behind him)
base = L.rope_sides(True, {"0,0": sq((UNUSED, UNUSED), vert=(UNUSED, UNUSED)), "0,1": sq((UNUSED, UNUSED), vert=(UNUSED, UNUSED))},
                    [EW4_NODES])
check("base live reading (every rope at PawnUnused) reads FAIL", base[0] == "FAIL" and "behind" in base[1], base)
# the fix on ew4: far rope 7.6829 north of him, near 8.7805 on his square -> PASS
fix = L.rope_sides(True, {"0,0": sq((ROPE, UNUSED)), "0,1": sq((ROPE, ROPE))}, [EW4_NODES])
check("rope behind and over him, rope below him north of him reads PASS", fix[0] == "PASS", fix)
# the fix on ew2: both squares hold both sides (far hanger feet south, near rope climbing north) -> still PASS
mixed = L.rope_sides(True, {"0,0": sq((ROPE, UNUSED)), "0,1": sq((ROPE, UNUSED))}, [EW4_NODES])
check("squares holding both sides read PASS", mixed[0] == "PASS", mixed)
# both sides lowered under him: nothing over him -> FAIL, though the sub-mesh (other bridges) still reaches over him
low = L.rope_sides(True, {"0,0": sq((ROPE, ROPE)), "0,1": sq((ROPE, ROPE))}, [EW4_NODES])
check("both sides under him read FAIL even when the shared sub-mesh reaches over him", low[0] == "FAIL" and "over" in low[1], low)
# sides swapped: the square north of him holds only rope over him -> FAIL
swap = L.rope_sides(True, {"0,0": sq((ROPE, ROPE)), "0,1": sq((UNUSED, UNUSED))}, [EW4_NODES])
check("rope north of him all over him (sides swapped) reads FAIL", swap[0] == "FAIL" and "north" in swap[1], swap)
# a rope level with his lowest node is not behind him
level = L.rope_sides(True, {"0,0": sq((UNUSED, UNUSED)), "0,1": sq((EW4_NODES[0], EW4_NODES[0]))}, [EW4_NODES])
check("a rope level with his lowest node reads FAIL", level[0] == "FAIL", level)
# no rope read north of him, no node read, a census that failed: UNMEASURED, never PASS
check("no rope north of him reads UNMEASURED", L.rope_sides(True, {"0,0": sq((ROPE, UNUSED)), "0,1": []}, [EW4_NODES])[0] == "UNMEASURED")
check("no node read reads UNMEASURED", L.rope_sides(True, {"0,0": sq((ROPE, UNUSED)), "0,1": sq((ROPE, ROPE))}, [None])[0] == "UNMEASURED")
check("a failed census reads UNMEASURED", L.rope_sides(True, {"0,0": None, "0,1": sq((ROPE, ROPE))}, [EW4_NODES])[0] == "UNMEASURED")
# north-south: the side ropes stay over him; the shared sub-mesh's lower ropes (an east-west bridge's) do not count
check("north-south side ropes over him read PASS though the shared sub-mesh holds lower rope",
      L.rope_sides(False, {"-1,0": sq((UNUSED, UNUSED)), "1,0": sq((UNUSED, UNUSED))}, [(8.418, 8.4619)])[0] == "PASS")
check("a north-south side rope under him reads FAIL",
      L.rope_sides(False, {"-1,0": sq((ROPE, ROPE)), "1,0": sq((UNUSED, UNUSED))}, [(8.418, 8.4619)])[0] == "FAIL")
# his drawn heights: requests with a material when drawn by node; the one quad when drawn as his cached atlas frame
check("node_span skips a node with no material",
      L.node_span({"success": True, "drawPath": "nodes", "requests": [{"drawn": [0, 8.40, 0], "renderQueue": 2900},
                                                                       {"drawn": [0, 8.50, 0], "renderQueue": -1}]}) == (8.40, 8.40))
check("node_span of a cached atlas frame is its quad, not the atlas render's requests near y 0",
      L.node_span({"success": True, "drawPath": "cachedAtlas", "cachedQuad": {"y": 8.4146},
                   "requests": [{"drawn": [0, 0.01, 0], "renderQueue": 2900}]}) == (8.4146, 8.4146))
check("node_span of a hidden or unread pawn is None",
      L.node_span(nodes([8.4], path="hidden")) is None and L.node_span({"success": False}) is None)
# the census: only drawn rope draws count
check("cable_ys keeps drawn rope draws only, with their square and whole-mesh spans",
      L.cable_ys({"success": True, "draws": census((ROPE, ROPE))["draws"]
                  + census((1.0, 1.0), material="Custom/Cutout_RM_SuspensionDeck_Heavy_Strip_mid")["draws"]
                  + census((UNUSED, UNUSED), drawn=False)["draws"]}) == [{"square": (ROPE, ROPE), "vert": (ROPE, ROPE)}])
check("cable_ys of a failed census is None", L.cable_ys({"success": False}) is None)
check("census_cells: east-west reads his square and the one north",
      L.census_cells((100, 5), (105, 5), (102, 5)) == {"0,0": (102, 5), "0,1": (102, 6)})
check("census_cells: north-south reads the squares beside him",
      set(L.census_cells((5, 100), (5, 105), (5, 102))) == {"-1,0", "1,0", "-1,1", "1,1"})

for f in fails:
    print("  FAIL " + f)
print("selftest_live_deck_rope_sides: %s (%d faults)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
