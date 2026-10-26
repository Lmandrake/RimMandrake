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
tile = call("jawa/map_info").get("tile")
if tile is None or tile == -1: sys.exit("no current map tile in jawa/map_info - nothing regenerated")
if len(sys.argv) > 1:
    call("jawa/world_tile_set", tiles=str(tile), biome=sys.argv[1]); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); time.sleep(5)
for _ in range(100):
    if call("rimworld/get_ui_state").get("programState") == "Playing": break
    time.sleep(3)
got = call("jawa/map_info").get("mapBiome")
print("regenerated:", got)
# the tile write is not checked above; the biome the new map actually has is the verdict
sys.exit(0 if len(sys.argv) < 2 or got == sys.argv[1] else 1)
