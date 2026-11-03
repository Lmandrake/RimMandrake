#!/usr/bin/env python3
"""Offline selftest of live_kit_art.py (GELATINOUSSLIME_KIT_ART_1 A2): the verdict logic on canned thing_graphic rows,
and the staging spec carrying every field Utils/modcheck/biome_site.choose_tile/retile read, aimed at our biome."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_kit_art as L  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


grass = {"defName": "RM_Plant_SlimeGrass", "id": "Plant1", "graphicPath": "Plants/RM_SlimeGrass"}
gel = {"defName": "RM_Gelatid", "id": "Gel1", "graphicPath": "Things/Pawn/Animal/RM_Gelatid/RM_Gelatid"}
clean_ex = {"appearance": {"bodyTexPath": "Things/Pawn/Animal/RM_Gelatid/RM_Gelatid",
                           "dessicatedTexPath": "Things/Pawn/Animal/RM_Gelatid/Dessicated_RM_Gelatid"}}
bad_ex = {"appearance": {"bodyTexPath": "x", "dessicatedTexPath": "Things/Pawn/Animal/Tortoise/Dessicated_Tortoise"}}

f, k, g, b = L.judge([grass, gel], lambda i: clean_ex)
check(L.verdict([grass, gel], f, k, g, b)[0] == 0, "a kit plant and a clean gelatid HOLD")
f, k, g, b = L.judge([grass, gel], lambda i: bad_ex)
check(L.verdict([grass, gel], f, k, g, b)[0] == 1, "a gelatid whose desiccated path is the tortoise FAILs")
dand = {"defName": "RM_Plant_Readerbloom", "id": "P2", "resolvedPath": "Things/Plant/Dandelion"}
f, k, g, b = L.judge([grass, dand], lambda i: {})
check(L.verdict([grass, dand], f, k, g, b)[0] == 1, "a dandelion resolvedPath FAILs")
var = {"defName": "Rock", "id": "R1", "variantPaths": ["a", "Tortoise_b"]}
f, k, g, b = L.judge([grass, var], lambda i: {})
check(L.verdict([grass, var], f, k, g, b)[0] == 1, "a tortoise in a variant list FAILs, any def")
bt = {"defName": "RM_SlimeBlock", "id": "B1", "graphicPath": "x", "badTex": True}
f, k, g, b = L.judge([grass, bt], lambda i: {})
check(L.verdict([grass, bt], f, k, g, b)[0] == 1, "an RM_ thing drawing BadTex FAILs")
f, k, g, b = L.judge([{"defName": "Sandstone", "id": "S1"}], lambda i: {})
check(L.verdict([{}], f, k, g, b)[0] == 2, "no kit plant on the map is UNMEASURED, never a pass")

f, k, g, b = L.judge([grass, gel], lambda i: {"success": False})
check(L.verdict([grass, gel], f, k, g, b)[0] == 2, "a failed gelatid explain is UNMEASURED, never a pass")
f, k, g, b = L.judge([grass, gel], lambda i: {})
check(L.verdict([grass, gel], f, k, g, b)[0] == 2, "an empty gelatid appearance is UNMEASURED, never a pass")

for field in ("BIOME", "LAT_MAX", "MAP_SIZE", "TILE"):
    check(hasattr(L.SPEC, field), "staging spec carries %s" % field)
site = open(os.path.join(HERE, "..", "Utils", "modcheck", "biome_site.py"), encoding="utf-8").read()
used = set(re.findall(r"spec\.([A-Z_]+)", site.split("def census")[0]))   # choose_tile + retile only
check(used <= set(vars(L.SPEC)), "spec covers every field choose_tile/retile read %s" % sorted(used))
used_t = set(re.findall(r't\["(\w+)"\]', site))
check(used_t <= set(L.SPEC.TILE), "TILE covers every tile key retile writes %s" % sorted(used_t))
check(L.SPEC.BIOME == "RM_GelatinousSlime" and L.BIOME == L.SPEC.BIOME, "staged biome is RM_GelatinousSlime")
check(L.SPEC.MAP_SIZE >= 100, "map is >= 100 (northstar_site.preflight's floor)")
biome_xml = open(os.path.join(HERE, "Defs", "BiomeDefs", "GelatinousSlime.xml"), encoding="utf-8").read()
check(all("<%s>" % p in biome_xml for p in L.KIT_PLANTS), "every kit plant is a wildPlants row of the BiomeDef")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
