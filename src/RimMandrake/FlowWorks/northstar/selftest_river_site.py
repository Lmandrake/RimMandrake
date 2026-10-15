"""Offline selftest of river_site: fish preference (RIVER_SITE_FIX_FISHLESS_ROT_RIVER), the downstream-edge rule and
the mapId fix (TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA), and no leftover candidate map
(TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ). No bridge: main() runs against a fake world."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0]]
import river_site as R  # noqa: E402

FAILS = []


def check(name, cond, why=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else why))
    if not cond:
        FAILS.append(name)


check("salt-only fish table is not river fish", R.biome_has_fish({"maxFishPopulation": 9, "fishTypes": {"saltwater_Common": {"a": 1}}}) is False)
check("fish biome", R.biome_has_fish({"maxFishPopulation": 540, "fishTypes": {"freshwater_Common": {"Fish_Bass": 1}}}) is True)
check("zero population is fishless", R.biome_has_fish({"maxFishPopulation": 0, "fishTypes": {"freshwater_Common": {"a": 1}}}) is False)
check("no field read is unknown, not fishless", R.biome_has_fish({}) is None and R.biome_has_fish(None) is None)
check("empty fish table is fishless", R.biome_has_fish({"maxFishPopulation": 50, "fishTypes": {}}) is False)

xml = """<Defs>
<BiomeDef><defName>A_Fishy</defName><maxFishPopulation>300</maxFishPopulation>
 <fishTypes><freshwater_Common><Fish_Bass>1</Fish_Bass></freshwater_Common></fishTypes></BiomeDef>
<BiomeDef><defName>A_Barren</defName><maxFishPopulation>0</maxFishPopulation></BiomeDef>
<BiomeDef><defName>A_SaltOnly</defName><maxFishPopulation>90</maxFishPopulation>
 <fishTypes><saltwater_Common><Fish_X>1</Fish_X></saltwater_Common></fishTypes></BiomeDef>
<BiomeDef ParentName="Base"><defName>A_Child</defName></BiomeDef></Defs>"""
fx = R.biome_fish_from_xml(xml)
check("xml: fishy / barren / salt-only / inherited skipped",
      fx == {"A_Fishy": True, "A_Barren": False, "A_SaltOnly": False}, str(fx))

rows = [{"tile": 1, "biome": "RM_TheRot"}, {"tile": 2, "biome": "TemperateForest"}, {"tile": 3, "biome": "Mystery"},
        {"tile": 4, "biome": "RM_TheRot"}]
order, rej = R.prefer_fish(rows, {"RM_TheRot": False, "TemperateForest": True, "Mystery": None})
check("fish tiles first, unknown next, fishless dropped", [r["tile"] for r in order] == [2, 3], str(order))
check("rejection is named with a count", rej == [("RM_TheRot", 2)], str(rej))
calls = []
def fake(tool, **kw):
    calls.append(kw["defs"])
    return {"defs": [{"fields": {"maxFishPopulation": 10, "fishTypes": {"freshwater_Common": {"f": 1}}}}]} if "Good" in kw["defs"] else {"defs": []}
fb = R.fish_by_biome(fake, ["Good", "Bad", None, "Good"])
check("fish_by_biome: one read per biome, unreadable is None", fb == {"Good": True, "Bad": None} and len(calls) == 2, str(fb))
fb2 = R.fish_by_biome(lambda tool, **kw: {"defs": []}, ["Z"], {"Z": False})
check("fish_by_biome falls back to the XML table when the live read is unknown", fb2 == {"Z": False}, str(fb2))
xf = R._xml_fish()
print("xml fallback biomes read:", len(xf))

# ------------------------------------------------------------------ TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA
import extensions_rivers as RIV  # noqa: E402

W = H = 20


def terrain(moving_edges_, sea_south=False):
    """A 20x20 ring: 'WaterMovingShallow' on the named edges' middle 4 cells, WaterOceanShallow along the south edge when
    the river ends in the sea, Soil elsewhere."""
    t = {}
    for x in range(W):
        for z in range(H):
            t[(x, z)] = "Soil"
    spans = {"north": [(x, H - 1) for x in range(8, 12)], "south": [(x, 0) for x in range(8, 12)],
             "west": [(0, z) for z in range(8, 12)], "east": [(W - 1, z) for z in range(8, 12)]}
    if sea_south:
        for x in range(W):
            t[(x, 0)] = "WaterOceanShallow"
    for e in moving_edges_:
        for c in spans[e]:
            t[c] = "WaterMovingShallow"
    return t


sea = terrain(["north"], sea_south=True)
check("moving_edges: a river ending in the sea reaches its inflow edge only (r7 tile 60145)",
      RIV.moving_edges(sea, (W, H)) == {"north": 4}, str(RIV.moving_edges(sea, (W, H))))
check("can-fail: edge_river_cells still finds cells there, so the old site test let it through",
      len(RIV.edge_river_cells(sea, (W, H))) > 0)
thru = terrain(["north", "west", "east"])
check("moving_edges: a through river reaches 3 edges (r7 tile 248: N, W, E)", sorted(RIV.moving_edges(thru, (W, H))) == ["east", "north", "west"])
kv = {"current": "1606", "fast": "796"}
check("river_reject: one moving edge is no downstream edge", "downstream" in (R.river_reject(kv, {"north": 14}, False) or ""))
check("river_reject control: two edges with a current and a fast lane accept", R.river_reject(kv, {"north": 12, "west": 29}, False) is None)
check("river_reject: no fast lane still rejects", "fast" in (R.river_reject({"current": "9", "fast": "0"}, {"north": 1, "south": 1}, False) or ""))
check("river_reject: unreadable edges reject, never accept", "unreadable" in (R.river_reject(kv, None, False) or ""))
check("river_reject: the current map must be the candidate's tile (read back)",
      "not 60146" in (R.river_reject(kv, {"north": 1, "west": 1}, False, tile=60146, map_tile=60145) or ""))
check("river_reject: a DRY site needs no river", R.river_reject({}, {}, True, tile=5, map_tile=5) is None)
check("generated_map_id reads mapId, never mapIndex", R.generated_map_id({"mapId": 9, "mapIndex": 8}) == 9)
check("generated_map_id: no mapId is a refusal, not an index fallback", R.generated_map_id({"mapIndex": 8}) is None)
check("leftover_maps: this run's other candidates go, the site and the home map stay",
      R.leftover_maps([{"mapId": 0, "tile": 5}, {"mapId": 3, "tile": 40368}, {"mapId": 9, "tile": 60146}], 9, [40368, 60146])
      == [{"mapId": 3, "tile": 40368}])


# ------------------------------------------------------------------ main() against a fake world
class FakeWorld(object):
    """Find.Maps with uniqueID != index (the r7 fixture world: uids 1..n at indexes 0..n-1, home uid 0 at index 0 here
    shifted to uid 1). Tiles: 101 the sea-ending river (fast lane, one edge), 102 a through river (3 edges)."""
    def __init__(self, tiles):
        self.tiles = tiles                          # {tile: (grid kv, moving edges, sea)}
        self.maps = [{"mapId": 1, "tile": 5, "biome": "Home"}]
        self.cur = 1
        self.next_uid = 2
        self.calls = []

    def _map(self, uid):
        return next((m for m in self.maps if m["mapId"] == uid), None)

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        cur = self._map(self.cur)
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": []}
        if tool == "jawa/world_tile_export":
            with open(kw["path"], "w", encoding="utf-8") as f:
                f.write("tile,hilliness,swampiness,elevation,temperature,lat,biome\n")
                for t in self.tiles:
                    f.write("%d,Flat,0,100,16,20,TemperateForest\n" % t)
            return {"success": True}
        if tool == "jawa/world_tile_get":
            return {"tiles": [{"tile": int(t), "riverCount": 2, "biome": "TemperateForest"} for t in kw["tiles"].split(",")]}
        if tool == "jawa/get_defs":
            return {"defs": [{"fields": {"maxFishPopulation": 9, "fishTypes": {"freshwater_Common": {"f": 1}}}}]}
        if tool == "jawa/colony_found":
            return {"success": True}
        if tool == "jawa/world_tile_map_generate":
            uid = self.next_uid
            self.next_uid += 1
            self.maps.append({"mapId": uid, "tile": kw["tile"], "biome": "TemperateForest"})
            return {"success": True, "mapId": uid, "mapIndex": len(self.maps) - 1}
        if tool == "jawa/set_current_map":
            m = self._map(kw["mapId"])
            if m is None:
                return {"success": False, "message": "no such map", "loadedMaps": [dict(x) for x in self.maps]}
            self.cur = m["mapId"]
            return {"success": True, "mapId": m["mapId"], "tile": m["tile"]}
        if tool == "jawa/settlement_remove":
            self.maps = [m for m in self.maps if m["tile"] != kw["tile"]]
            if self._map(self.cur) is None:
                self.cur = self.maps[0]["mapId"]
            return {"success": True}
        if tool == "jawa/static_call":
            kv = self.tiles.get(cur["tile"], ({}, [], False))[0]
            return {"result": "GRID " + " ".join("%s=%s" % i for i in kv.items())}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": W, "sizeZ": H, "tile": cur["tile"], "mapId": cur["mapId"]}
        if tool == "jawa/get_terrain_batch":
            _, edges, sea_ = self.tiles.get(cur["tile"], ({}, [], False))
            t = terrain(edges, sea_south=sea_)
            ring = [c for c in t if c[0] in (0, W - 1) or c[1] in (0, H - 1)]
            return {"success": True, "ops": ";".join("%s:%d,%d,1,1" % (t[c], c[0], c[1]) for c in ring)}
        if tool == "jawa/spawn_pawn":
            return {"pawns": [{"id": "Human%d" % len(self.calls)}]}
        return {"success": True}


class _Sess(object):
    def __init__(self, w):
        self.w = w

    def __enter__(self):
        return self.w

    def __exit__(self, *a):
        return False


class _QSFake(object):
    MAP_ONLY = ("threat_structures_cleared",)

    def __init__(self):
        self.calls = []

    def site_profile_receipt(self, s, row, controls=None):
        self.calls.append((row, controls))
        return {"controls": [{"name": "threat_structures_cleared", "readBack": 0}], "problems": []}


def run_main(world):
    import types
    import tempfile
    qs = _QSFake()
    fake_rd = types.ModuleType("rimdrive")
    fake_rd.Session = lambda lock=None: _Sess(world)
    saved = (sys.modules.get("rimdrive"), R.BW.reset, R.BW.close_naming_dialogs, R._QS, R._xml_fish, os.environ.get("TEMP"))
    sys.modules["rimdrive"] = fake_rd
    R.BW.reset = lambda s, expected_ids=(): {"problems": []}
    R.BW.close_naming_dialogs = lambda s: 0
    R._QS = lambda: qs
    R._xml_fish = lambda: {}
    os.environ["TEMP"] = tempfile.mkdtemp()
    try:
        rc = R.main()
    finally:
        if saved[0] is None:
            sys.modules.pop("rimdrive", None)
        else:
            sys.modules["rimdrive"] = saved[0]
        R.BW.reset, R.BW.close_naming_dialogs, R._QS, R._xml_fish = saved[1:5]
        if saved[5] is None:
            os.environ.pop("TEMP", None)
        else:
            os.environ["TEMP"] = saved[5]
    return rc, qs


FAST = {"current": 2803, "fast": 796}
w = FakeWorld({101: (FAST, ["north"], True), 102: (FAST, ["north", "west", "east"], False)})
rc, qs = run_main(w)
set_ids = [kw["mapId"] for t, kw in w.calls if t == "jawa/set_current_map" and kw["mapId"] != -1]
check("main: the sea-ending river (101) is rejected and the through river (102) is the site", rc == 0 and w._map(w.cur)["tile"] == 102,
      "rc %s cur %s" % (rc, w._map(w.cur)))
check("main: set_current_map gets the uniqueIDs (2, 3), never the Find.Maps indexes (1, 2)", set_ids[:2] == [2, 3], str(set_ids))
check("main: the rejected candidate's map is removed; only home + site stay loaded",
      sorted(m["tile"] for m in w.maps) == [5, 102], str(w.maps))
check("main: the site gets the shared map-only quiet-site profile", qs.calls and qs.calls[0][1] == _QSFake.MAP_ONLY, str(qs.calls))
w2 = FakeWorld({101: (FAST, ["north"], True)})
rc2, _ = run_main(w2)
check("main can-fail: a world whose only fast river ends in the sea yields no site (exit 2), its map removed",
      rc2 == 2 and sorted(m["tile"] for m in w2.maps) == [5], "rc %s maps %s" % (rc2, w2.maps))


class StickyWorld(FakeWorld):
    """settlement_remove of a candidate map silently does nothing (the leftover the guard must report)."""
    def call(self, tool, **kw):
        if tool == "jawa/settlement_remove":
            self.calls.append((tool, kw))
            return {"success": True}
        return FakeWorld.call(self, tool, **kw)


w3 = StickyWorld({101: (FAST, ["north"], True), 102: (FAST, ["north", "west", "east"], False)})
rc3, _ = run_main(w3)
check("main can-fail: a candidate map that will not go is read back and fails the site (exit 3)", rc3 == 3, "rc %s" % rc3)
print("selftest_river_site: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
