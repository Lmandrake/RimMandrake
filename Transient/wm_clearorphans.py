import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
d=json.load(open(r"D:\Luke\dev\Rimworld\Transient\orphan_rivers.json"))
tiles=",".join(str(t) for t in d["tiles"])
print("clearing river links on", len(d["tiles"]), "orphan tiles")
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb.call("jawa/world_links_clear", {"kind":"river", "tiles": tiles, "readBack": True})
    print("clear:", json.dumps(r)[:400]); print()
    # re-lay our authored set in case a shared endpoint lost a legitimate link
    i = rb.call("jawa/world_links_import", {
        "path": r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_links.csv", "apply": True})
    print("re-import:", json.dumps(i)[:260]); print()
    print("commit:", json.dumps(rb.call("jawa/world_commit", {}))[:120]); print()
    v = rb.call("jawa/world_links_validate", {"limit": 3})
    print("AFTER -> riverEntries:", v.get("riverEntries"), "(want 584)",
          " riverTiles:", v.get("riverTiles"), "(want 308)",
          " asym:", v.get("asymmetricCount"), " roads:", v.get("roadEntries"))
    print("csv match:", json.dumps(v.get("csv"))[:200])
