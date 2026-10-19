"""Sanity spawns on the current map: Steel, Plant_Grass, RM_TallSlimyGrass, RUT_Webwork_Nest; then thing_graphic read.
python.exe sanity_spawn.py <out.json>"""
import json, os, sys
UT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "RimMandrake", "Utils")
sys.path.insert(0, UT)
from rimbridge_client import RimBridge, resolve_endpoint
DEFS = ["Steel", "Plant_Grass", "RM_TallSlimyGrass", "RUT_Webwork_Nest"]
out = {"spawns": [], "cells": []}
h, p, t = resolve_endpoint()
with RimBridge(h, p, t, timeout=120.0) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    free = []
    for z in range(140, 220, 4):
        for x in range(140, 220, 4):
            ci = (c("rimworld/get_cell_info", x=x, z=z) or {}).get("cell") or {}
            if ci.get("walkable") and not ci.get("fogged") and ci.get("thingCount") == 0 and "Water" not in str(ci.get("terrainDefName")):
                free.append((x, z, ci.get("terrainDefName")))
            if len(free) >= len(DEFS):
                break
        if len(free) >= len(DEFS):
            break
    out["cells"] = free
    ids = []
    for d, (x, z, terr) in zip(DEFS, free):
        try:
            r = c("rimworld/spawn_thing", defName=d, x=x, z=z)
        except Exception as ex:  # noqa: BLE001
            out["spawns"].append({"def": d, "raised": "%s %s" % (type(ex).__name__, str(ex)[:300])}); continue
        eff = r.get("effects") or {}
        logs = eff.get("logs") or []
        after = (c("rimworld/get_cell_info", x=x, z=z) or {}).get("cell") or {}
        row = {"def": d, "cell": [x, z], "terrain": terr, "success": r.get("success"), "thingId": r.get("thingId"),
               "message": r.get("message"), "logCount": eff.get("logCount", len(logs)),
               "logs": [str(l)[:400] for l in logs[:5]], "cellDefsAfter": [th.get("defName") for th in after.get("things") or []]}
        out["spawns"].append(row)
        if r.get("thingId"):
            ids.append(str(r["thingId"]))
    if ids:
        g = c("jawa/thing_graphic", thing=",".join(ids))
        out["graphic"] = [{k: th.get(k) for k in ("defName", "graphicClass", "graphicPath", "resolvedPath", "textureName",
                                                  "textureSize", "badTex", "variantCount", "variantPath", "error")}
                          for th in g.get("things") or []]
        out["graphicRefused"] = g.get("refused")
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
for s in out["spawns"]:
    print(s.get("def"), s.get("success"), s.get("thingId"), "logs=%s" % s.get("logCount"), s.get("cellDefsAfter"), (s.get("logs") or [""])[:1], s.get("raised", ""))
for g in out.get("graphic", []):
    print("GFX", g)
