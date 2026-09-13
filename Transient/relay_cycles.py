import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # lay each cycle edge lower-dist end first so max() bumps by at most 1
    g = rb.call("jawa/world_links_get", {"tiles": "2793,7653,14319,14323", "limit": 10})
    dist = {t['tile']: t['riverDist'] for t in g.get('tiles', [])}
    print("dists:", dist)
    for a, b in ((2793,7653),(14319,14323)):
        lo, hi = (a, b) if dist.get(a,0) <= dist.get(b,0) else (b, a)
        r = rb.call("jawa/world_links_set", {"kind": "river", "path": f"{lo},{hi}", "def": "Creek"})
        print(f"laid {lo}->{hi}:", r.get("success"), r.get("laid"))
    rb.call("jawa/world_commit", {})
    g2 = rb.call("jawa/world_links_get", {"tiles": "2793,7653,14319,14323", "limit": 10})
    for t in g2.get('tiles', []):
        print(t['tile'], "rivers:", len(t['potentialRivers']), "dist:", t['riverDist'])
