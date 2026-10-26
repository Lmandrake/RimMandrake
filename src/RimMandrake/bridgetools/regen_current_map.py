"""Regenerate the current debug map in place (optionally as BIOME) so a bridge proof starts on a
clean map. Windows python.exe, repo root: python.exe src/RimMandrake/bridgetools/regen_current_map.py [BIOME]"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
mi0 = call("jawa/map_info"); tile, id0 = mi0.get("tile"), mi0.get("mapId")
if tile is None or tile == -1 or mi0.get("tileValid") is False or id0 is None:
    sys.exit("no current planet-tile map in jawa/map_info (%s) - nothing regenerated" % str(mi0)[:200])
if len(sys.argv) > 1:
    call("jawa/world_tile_set", tiles=str(tile), biome=sys.argv[1]); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); time.sleep(5)
# programState stays "Playing" through a regen, so polling it proved nothing; the regenerated map is a NEW Map
# with a new uniqueID. And mapBiome alone is no verdict either: Map.Biome reads the tile live, so it already
# reads the new biome straight after world_tile_set, regenerated or not.
mi = {}
for _ in range(100):
    mi = call("jawa/map_info")
    if mi.get("mapId") not in (None, id0): break
    time.sleep(3)
got = mi.get("mapBiome")
print("regenerated: mapId %s -> %s, biome %s" % (id0, mi.get("mapId"), got))
sys.exit(0 if mi.get("mapId") not in (None, id0) and (len(sys.argv) < 2 or got == sys.argv[1]) else 1)
