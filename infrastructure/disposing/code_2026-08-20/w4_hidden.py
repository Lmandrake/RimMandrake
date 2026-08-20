import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
v = call("jawa/world_links_validate", limit=20)
print("hiddenByBiome cases found live:", v.get("hiddenByBiomeCount"))
for h in (v.get("hiddenByBiome") or []): print("  ", h)
# read one back in full to show potential vs visible
hb = (v.get("hiddenByBiome") or [])
if hb:
    tid = hb[0]["tile"]
    t = call("jawa/world_links_get", tiles=str(tid))["tiles"][0]
    print("\nFULL READ of tile", tid)
    print("  biome:", t["biome"], " allowRoads:", t["allowRoads"], " allowRivers:", t["allowRivers"])
    print("  potentialRoads:", t["potentialRoads"])
    print("  potentialRivers:", t["potentialRivers"])
    print("  visibleRoads:", t["visibleRoads"], " visibleRivers:", t["visibleRivers"])
    print("  hiddenByBiome:", t["hiddenByBiome"])
