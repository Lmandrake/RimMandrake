#!/usr/bin/env python3
"""HORRORS_RAIDING_FACTION_1 live proof: the Assailant horrors reach the nightside and nowhere else.

    python.exe src/RimUtinni/UtinniPatches/prove_night_horrors_live.py A2 < /dev/null
    python.exe src/RimUtinni/UtinniPatches/prove_night_horrors_live.py A3 < /dev/null

Runs under WINDOWS python: RimBridge binds Windows loopback. Needs a loaded game whose world has land on both sides of
the terminator (the Ash'karr world does; a low-coverage quicktest world may not, and then the clause FAILS, saying so).

  A2  on a freshly generated NIGHTSIDE player map (tile arc from the substellar point > nightsideBandMinArc + 5):
      at least one RUT_HorrorHive lair is on the map (the self-gating GenStep ran), and RUT_HorrorRaid, forced, fires
      and leaves pawns of the RUT_Horrors faction on the map.
  A3  on a freshly generated DAYSIDE player map (arc < terminatorBandMinArc - 5): no lair structure or crysalis of
      ours is on the map, and RUT_HorrorRaid, forced, reports canFireNow=false (dry run, nothing fires).

The arc uses the shipped geometry def (WeatherGeometryDefs_Ashkarr.xml) and the same formula as
RM_WeatherKernel.ArcDegrees, over the live world's own tile table (jawa/world_tile_export: tile indices belong to the
world that wrote them). Each run founds one player settlement, generates its map, and drops the map again at the end.
Exit 0 = the clause holds, 1 = it does not (or could not be measured)."""
import csv
import json
import math
import os
import random
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
GEOM = os.path.join(REPO, "src", "RimUtinni", "AshkarrWeatherSuite", "Defs", "WeatherGeometryDefs", "WeatherGeometryDefs_Ashkarr.xml")
LAIR = ["RUT_HorrorHive", "RUT_HorrorDen", "RUT_HorrorBurrow", "RUT_HorrorSinkhole", "RUT_HorrorMiteLarder",
        "RUT_HorrorCrysalis_Visceral", "RUT_HorrorCrysalis_Prowler", "RUT_HorrorCrysalis_Harvester", "RUT_HorrorCrysalis_Bulwark"]
FORMS = ["RM_Visceral", "RUT_HorrorBulwark", "RUT_HorrorHarvester", "RUT_HorrorProwler", "RUT_HorrorBroodLord"]
WATER = ("ocean", "lake", "sea", "water", "ice sheet")


class Game:
    def __init__(self):
        import rimbridge_client as rb
        host, port, token = rb.resolve_endpoint()
        self.s = rb.RimBridge(host=host, port=port, token=token, timeout=280.0)
        self.s.connect()

    def call(self, t, **p):
        r = self.s.call(t, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except ValueError:
                pass
        return r


def geometry():
    g = ET.parse(GEOM).getroot().find(".//*[substellarLat]")
    return {k: float(g.findtext(k)) for k in ("substellarLat", "substellarLon", "terminatorBandMinArc", "nightsideBandMinArc")}


def arc(lat, lon, lat0, lon0):
    r = math.radians
    c = math.sin(r(lat0)) * math.sin(r(lat)) + math.cos(r(lat0)) * math.cos(r(lat)) * math.cos(r(lon - lon0))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def candidates(g, geo, night):
    exp = g.call("jawa/world_tile_export")
    path = exp.get("path") or exp.get("pathWritten") or ""
    if not path or not os.path.isfile(path):
        return None, "world_tile_export wrote no readable file: %s" % str(exp)[:300]
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            b = (row.get("biome") or "").lower()
            if not b or any(w in b for w in WATER):
                continue
            a = arc(float(row["lat"]), float(row["long"]), geo["substellarLat"], geo["substellarLon"])
            if (night and a > geo["nightsideBandMinArc"] + 5) or (not night and a < geo["terminatorBandMinArc"] - 5):
                out.append((int(row["tile"]), round(a, 1), row.get("biome")))
    random.shuffle(out)
    return out, "%d %s land tiles in %s" % (len(out), "nightside" if night else "dayside", path)


def make_map(g, tiles):
    for tile, a, biome in tiles[:25]:
        f = g.call("jawa/colony_found", tile=tile, name="HorrorProbe")
        if not f.get("success"):
            continue
        m = g.call("jawa/world_tile_map_generate", tile=tile)
        if m.get("success") and m.get("mapId") is not None:
            g.call("jawa/set_current_map", mapId=m["mapId"])
            return {"tile": tile, "arc": a, "biome": biome, "mapId": m["mapId"], "mapIndex": m.get("mapIndex")}
    return None


def count(g, defs, pawns=False):
    r = g.call("jawa/list_things", defName=",".join(defs), includePawns=pawns, limit=500)
    things = r.get("things") or r.get("results") or []
    return things


def drop(g, m):
    info = g.call("jawa/map_info")
    if m and info.get("tile") == m["tile"] and m.get("mapIndex") is not None:
        g.call("jawa/map_drop", mapIndex=m["mapIndex"], notifyPlayer=False)


def run(clause):
    geo = geometry()
    g = Game()
    if g.call("rimworld/get_game_info").get("status") != "game_loaded":
        print("FAIL %s: no game loaded" % clause)
        return 1
    night = clause == "A2"
    tiles, note = candidates(g, geo, night)
    print(note)
    if not tiles:
        print("FAIL %s: no candidate tile on this world" % clause)
        return 1
    m = make_map(g, tiles)
    if not m:
        print("FAIL %s: could not found+generate a map on any of %d candidate tiles" % (clause, min(25, len(tiles))))
        return 1
    print("map:", m)
    ok = False
    try:
        lair = count(g, LAIR)
        hives = [t for t in lair if t.get("def") == "RUT_HorrorHive"]
        if night:
            fire = g.call("jawa/fire_incident", incidentDef="RUT_HorrorRaid", forced=True)
            time.sleep(1)
            facs = g.call("jawa/list_factions", includeHidden=True, defName="RUT_Horrors")
            forms = [t for t in count(g, FORMS, pawns=True) if "Horror" in str(t.get("faction", "")) or "Assailant" in str(t.get("faction", ""))]
            print("lair things %d (hives %d); raid fired=%s canFireNow=%s blockedByDialog=%s; faction rows %s; Horror-faction forms on map %d"
                  % (len(lair), len(hives), fire.get("fired"), fire.get("canFireNow"), fire.get("blockedByDialog"), str(facs)[:200], len(forms)))
            ok = len(hives) >= 1 and fire.get("canFireNow") is True and fire.get("success") is True and len(forms) >= 1
        else:
            dry = g.call("jawa/fire_incident", incidentDef="RUT_HorrorRaid", forced=True, dryRun=True)
            print("lair things %d; dry-run canFireNow=%s" % (len(lair), dry.get("canFireNow")))
            ok = len(lair) == 0 and dry.get("canFireNow") is False
    finally:
        drop(g, m)
    print(("PASS " if ok else "FAIL ") + clause)
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("A2", "A3"):
        print(__doc__)
        sys.exit(1)
    sys.exit(run(sys.argv[1]))
