#!/usr/bin/env python3
"""live_kit_art.py - live clause A2 of GELATINOUSSLIME_KIT_ART_1: a Slime map draws no tortoise and no dandelion.

    python3 src/RimMandrake/GelatinousSlime/live_kit_art.py [--timeout 120]

READ ONLY (jawa/map_info, jawa/thing_graphic, jawa/thing_explain). On the CURRENT map, which must be an RM_GelatinousSlime
map (a quicktest Slime map):
  * every thing on the map (one thing_graphic rect read, complete list required) has no graphicPath, resolvedPath or
    variant path naming Tortoise or Dandelion, and no RM_ thing draws BadTex;
  * at least one kit thing (slime grass, bellows, thumbstalk or readerbloom) is present, so the read is not blind;
  * every RM_Gelatid on the map (found as a thing in the same read) has no appearance texPath naming Tortoise
    (thing_explain lists the body AND desiccated graphic paths the def configures).
Exit 0 holds, 1 a stand-in is drawn, 2 UNMEASURED (no bridge, wrong map, truncated read, nothing of ours present).
Callers hold the bridge lock; this never takes it. Runs the client under Windows Python (python.exe), as
rimbridge_client.py requires.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.normpath(os.path.join(HERE, "..", "Utils", "rimbridge_client.py"))
FORBIDDEN = ("tortoise", "dandelion")
KIT_PLANTS = {"RM_Plant_SlimeGrass", "RM_Plant_Bellows", "RM_Plant_Thumbstalk", "RM_Plant_Readerbloom"}
BIOME = "RM_GelatinousSlime"


def bridge(tool, params, timeout):
    path = subprocess.run(["wslpath", "-w", CLIENT], capture_output=True, text=True, timeout=20).stdout.strip()
    r = subprocess.run(["python.exe", path, "--timeout", str(timeout), "--call", tool, "--json", json.dumps(params)],
                       capture_output=True, text=True, timeout=timeout + 30, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError(f"{tool} exit {r.returncode}: {(r.stderr or r.stdout)[-300:]}")
    return json.loads(r.stdout)


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def find_key(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str):
                yield v
            yield from find_key(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from find_key(v, key)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    try:
        info = bridge("jawa/map_info", {}, a.timeout)
        biomes = set(find_key(info, "biome"))
        if BIOME not in biomes:
            print(f"UNMEASURED: current map biome {sorted(biomes)} is not {BIOME}")
            return 2
        g = bridge("jawa/thing_graphic", {"rect": "0,0,1000,1000", "limit": 100000}, a.timeout)
        if not g.get("success") or not g.get("isCompleteList"):
            print(f"UNMEASURED: thing_graphic success={g.get('success')} complete={g.get('isCompleteList')}")
            return 2
        things = g.get("things") or []
        fails = []
        for t in things:
            hits = [s for s in strings({k: t.get(k) for k in ("graphicPath", "resolvedPath", "variantPath",
                                                               "variantPaths", "textureName")})
                    if any(w in s.lower() for w in FORBIDDEN)]
            if hits:
                fails.append(f"{t.get('defName')} {t.get('id')} draws {hits[0]}")
            if str(t.get("defName", "")).startswith("RM_") and t.get("badTex"):
                fails.append(f"{t.get('defName')} {t.get('id')} draws BadTex")
        kit = sorted({t.get("defName") for t in things} & KIT_PLANTS)
        gels = [t.get("id") for t in things if t.get("defName") == "RM_Gelatid"]
        for gid in gels:
            ex = bridge("jawa/thing_explain", {"id": gid}, a.timeout)
            for s in strings(ex.get("appearance")):
                if any(w in s.lower() for w in FORBIDDEN):
                    fails.append(f"RM_Gelatid {gid} appearance names {s}")
                    break
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
        print(f"UNMEASURED: {str(e)[:300]}")
        return 2
    print(f"map things read {len(things)}; kit plants present {kit}; gelatids {len(gels)}")
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    if not kit:
        print("UNMEASURED: no kit plant on the map; the read cannot speak for the kit")
        return 2
    print("HOLDS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
