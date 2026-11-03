#!/usr/bin/env python3
"""biome_transitions_ab.py -- same-tile maps with and without Biome Transitions (BIOME_TRANSITIONS_JUDGE_VS_BAROQUE).

One SCRATCH quicktest world (never the campaign save, no worldgen shipped: scaffolding, discarded) gets four sites of
OUR biomes on land patches. `build` (under the list WITH the mod) paints them and saves BT_AB_base; each arm then
generates the same tiles from that save, so the arms differ only by the one mod in the list.

  python.exe src/RimMandrake/Utils/biome_transitions_ab.py run --arm on --out D:\\ClaudeWork\\rimmandrake\\scratch\\bt_judge
  python.exe src/RimMandrake/Utils/biome_transitions_ab.py run --arm off --out ...     (after swapping the list)
  python3    src/RimMandrake/Utils/biome_transitions_ab.py analyze --out /mnt/d/ClaudeWork/rimmandrake/scratch/bt_judge

Sites: border (two pairs: centre and north half biome A, south half biome B), mixed (a border site that also carries
Odyssey's MixedBiome, the mutator R3 holds on RM_ tiles), control (every neighbour the same biome).
"""
import argparse
import collections
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAP_SIZE = 200
SITES = [("border_rot_blue", "RM_TheRot", "RM_BlueDesert", False),
         ("border_cauldron_rot", "RM_Cauldron", "RM_TheRot", False),
         ("mixed_rot_blue", "RM_TheRot", "RM_BlueDesert", True),
         ("control_rot", "RM_TheRot", "RM_TheRot", False)]
BASE_SAVE = "BT_AB_base"   # BT_AB_base_off: the same file with the mod's row cut from the header's three lists


def _save_name(arm):
    return "BT_AB_arm_" + arm


def _bridge():
    sys.path[:0] = [HERE, os.path.join(ROOT, "src", "RimMandrake", "Pyrelands")]
    import northstar_site as N
    from northstar_driver.session import FastSession
    return N, FastSession(strict=False)


def _pick(N, s, out):
    """Four far-apart clean land patches, chosen once, on raw tile fields."""
    tiles = os.path.join(out, "world_tiles_extended.csv")
    nbr = os.path.join(out, "world_neighbors.csv")
    e = N._call(s, "jawa/world_tile_export", path=tiles, format="csv", extended=True)
    n = N._call(s, "jawa/world_neighbors", path=nbr)
    rows = N.read_tile_csv(e.get("path") or tiles)
    nbrs = N.read_neighbor_csv(n.get("path") or nbr)
    chosen, used = [], set()
    for centre, patch in N.site_candidates(rows, nbrs, None):
        if set(N.ring(nbrs, centre, 5)) & used:
            continue
        mu = N._call(s, "jawa/world_mutators_get", tiles=",".join(map(str, patch)), limit=100)
        if any(r.get("landmark") for r in mu.get("tiles") or []):
            continue
        chosen.append((centre, patch))
        used |= set(patch)
        if len(chosen) == len(SITES):
            return rows, chosen
    raise N.SiteError("only %d clean patches" % len(chosen))


def _paint(N, s, rows, centre, patch, a, b, mixed):
    lat0 = rows[centre]["lat"]
    north = [t for t in patch if rows[t]["lat"] >= lat0]
    south = [t for t in patch if rows[t]["lat"] < lat0]
    for tiles, biome in ((north, a), (south, b)):
        r = N._call(s, "jawa/world_tile_set", tiles=",".join(map(str, tiles)), biome=biome, temperature=25.0,
                    rainfall=300.0, elevation=N.ELEVATION, hilliness=N.HILLINESS, swampiness=0.0,
                    readBack=len(tiles))
        bad = [t.get("tile") for t in r.get("tiles") or [] if t.get("biome") != biome]
        if bad or len(r.get("tiles") or []) != len(tiles):
            raise N.SiteError("paint read-back wrong: %s" % bad[:5])
    N._call(s, "jawa/world_mutators_set", action="clear", tiles=",".join(map(str, patch)))
    if mixed:
        N._call(s, "jawa/world_mutators_set", action="add", tiles=str(centre), mutators="MixedBiome")
    got = (N._call(s, "jawa/world_mutators_get", tiles=str(centre)).get("tiles") or [{}])[0].get("mutators")
    if got is None or (["MixedBiome"] if mixed else []) != [str(m if isinstance(m, str) else m.get("def"))
                                                           for m in got]:
        raise N.SiteError("centre %s mutators %s" % (centre, got))
    return {"north": north, "south": south}


def run(N, s, arm, out):
    os.makedirs(out, exist_ok=True)
    spec_path = os.path.join(out, "sites.json")
    if arm == "on":
        world = N.fresh_quicktest_world(s)
        rows, chosen = _pick(N, s, out)
        spec = {"world": world, "sites": []}
        for (name, a, b, mixed), (centre, patch) in zip(SITES, chosen):
            sides = _paint(N, s, rows, centre, patch, a, b, mixed)
            spec["sites"].append({"name": name, "a": a, "b": b, "mixed": mixed, "centre": centre, **sides})
        N._call(s, "jawa/world_commit")
        s.call("rimworld/save_game", saveName=BASE_SAVE)
        with open(spec_path, "w") as f:
            json.dump(spec, f, indent=1)
    else:
        with open(spec_path) as f:
            spec = json.load(f)
        print("load:", str(s.call("rimworld/load_game", saveName=BASE_SAVE + "_off"))[:400], flush=True)
        N._wait_state(s, "Playing", 200)
        for _ in range(60):             # Playing right after load_game can be a stale state: wait for the world
            if N._call(s, "jawa/world_mutators_get", tiles=str(spec["sites"][2]["centre"])).get("tiles"):
                break
            time.sleep(2)
    res = {"arm": arm, "sites": {}}
    biomes = sorted({x for st in spec["sites"] for x in (st["a"], st["b"])})
    probe = N._call(s, "jawa/biome_probe", biomes=",".join(biomes), plants=True, animals=True)
    res["probe"] = probe
    mods = s.call("jawa/mod_inventory") or {}
    res["mods"] = sorted(str(m.get("packageId", "")).lower() for m in mods.get("mods") or [])
    for st in spec["sites"]:
        res["sites"][st["name"]] = N.generate(s, st["centre"], size=MAP_SIZE)
    s.call("rimworld/save_game", saveName=_save_name(arm))
    with open(os.path.join(out, "arm_%s.json" % arm), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("arm", arm, {k: v for k, v in res["sites"].items()})


def _map_census(li):
    plants, kinds = collections.Counter(), collections.Counter()
    for th in li.find("things") if li.find("things") is not None else []:
        cls = th.get("Class", "")
        d = th.findtext("def") or ""
        if cls == "Plant" or d.startswith("Plant") or th.find("growth") is not None:
            plants[d] += 1
        k = th.findtext("kindDef")
        if k:
            kinds[k] += 1
    comp = None
    for c in li.find("components") or []:
        if c.get("Class") == "MixedBiomeMapComponent":
            g = c.find("biomeGrid")
            comp = {"biomeGridNull": g is None or g.get("IsNull") == "True",
                    "secondary": sorted({e.text for e in c.iter() if e.text and e.text.startswith(("RM_", "RUT_"))})}
    return {"plants": plants, "kinds": kinds, "mixedComp": comp, "tile": li.findtext("mapInfo/parent"),
            "biomeGridText": sum(len(e.text or "") for e in li.iter() if e.tag.lower().endswith("biomegriddeflate"))}


def analyze(out, saves):
    with open(os.path.join(out, "sites.json")) as f:
        spec = json.load(f)
    rep = {"sites": {}}
    for arm in [x for x in ("on", "off", "fix") if os.path.exists(os.path.join(out, "arm_%s.json" % x))]:
        with open(os.path.join(out, "arm_%s.json" % arm)) as f:
            res = json.load(f)
        roster = {b["defName"]: {p["defName"] for p in b.get("plants") or []} for b in res["probe"]["biomes"]}
        root = ET.parse(os.path.join(saves, _save_name(arm) + ".rws")).getroot()
        byid = {li.findtext("uniqueID"): li for li in root.find("game/maps")}
        for st in spec["sites"]:
            mid = str(res["sites"][st["name"]]["mapId"])
            c = _map_census(byid[mid])
            total = sum(c["plants"].values())
            mine = roster[st["a"]]
            other = roster[st["b"]] - mine
            r = rep["sites"].setdefault(st["name"], {"a": st["a"], "b": st["b"], "mixedMutator": st["mixed"]})
            r[arm] = {"plants": total,
                      "plantsOfCentreBiome": sum(n for d, n in c["plants"].items() if d in mine),
                      "plantsOnlyInBiomeB": sum(n for d, n in c["plants"].items() if d in other),
                      "plantsInNeither": sum(n for d, n in c["plants"].items() if d not in mine | other),
                      "topPlants": c["plants"].most_common(8), "mixedComp": c["mixedComp"],
                      "biomeGridChars": c["biomeGridText"]}
    with open(os.path.join(out, "report.json"), "w") as f:
        json.dump(rep, f, indent=1, default=str)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["run", "analyze"])
    ap.add_argument("--arm", choices=["on", "off", "fix"])
    ap.add_argument("--out", required=True)
    import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from game_paths import LOCALLOW  # noqa: E402
    ap.add_argument("--saves", default=LOCALLOW + "/Saves")
    a = ap.parse_args()
    if a.verb == "run":
        N, s = _bridge()
        with s:
            run(N, s, a.arm, a.out)
    else:
        print(json.dumps(analyze(a.out, a.saves), indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
