import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_validate", {"limit": 200})
    print("riverEntries", r.get("riverEntries"), "roadEntries", r.get("roadEntries"))
    print("asymmetric", r.get("asymmetricCount"), "nonAdjacent", r.get("nonAdjacentCount"),
          "hiddenByBiome", r.get("hiddenByBiomeCount"))
    hb = r.get("hiddenByBiome") or r.get("hidden") or []
    c=collections.Counter((x.get("biome"), x.get("kind")) for x in hb)
    for (b,k),n in c.most_common(12): print(f"   {n:5d}  {k or '?':6}  {b}")
    if not hb: print("   (no examples returned; keys:", list(r.keys()), ")")
