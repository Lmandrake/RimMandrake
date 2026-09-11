"""WORLDMAP_FINAL_REVIEW_1 Phase 0 — fresh live exports, nothing trusted from disk.
Run with python.exe (bridge binds Windows loopback). Writes everything to
Transient/final_review/ with a manifest. Read-only against the world."""
import sys, json, time, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

OUT = r"D:\Luke\dev\Rimworld\Transient\final_review"
os.makedirs(OUT, exist_ok=True)
manifest = {"startedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "calls": {}}

def dump(name, data):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    manifest["calls"][name] = {"bytes": os.path.getsize(p)}
    print(name, os.path.getsize(p), "bytes")

h, p_, t = resolve_endpoint()

def call(tool, params=None, fresh=True):
    with RimBridge(h, p_, t) as rb:
        return rb.call(tool, params or {})

pr = call("jawa/load_stall_probe")
assert pr.get("programState") == "Playing", "NOT PLAYING: " + str(pr.get("programState"))

# whole-planet bulk export (tiles: biome/elevation/etc per tile)
dump("world_tile_export.json", call("jawa/world_tile_export", {}))
dump("world_info.json", call("jawa/world_info_get", {}))
dump("world_stats.json", call("jawa/world_stats", {}))
dump("world_features.json", call("jawa/world_features_get", {}))
dump("world_lint.json", call("jawa/world_lint", {}))
dump("world_mutators_audit.json", call("jawa/world_mutators_audit", {}))

# paginated reads (100-row cap per the skill) — page until short page
def paged(tool, key_guess=("rows", "links", "landmarks", "mutators", "objects")):
    pages, offset = [], 0
    while True:
        r = call(tool, {"offset": offset, "limit": 100})
        rows = None
        for k in key_guess:
            if isinstance(r.get(k), list):
                rows = r[k]; break
        if rows is None:
            return {"unpaged": r}
        pages.extend(rows)
        if len(rows) < 100:
            break
        offset += len(rows)
        if offset > 60000:
            break
    return {"rows": pages, "count": len(pages)}

for tool, fname in [("jawa/world_links_get", "world_links.json"),
                    ("jawa/world_mutators_get", "world_mutators.json"),
                    ("jawa/world_landmarks_get", "world_landmarks.json"),
                    ("jawa/world_objects_get", "world_objects.json")]:
    try:
        dump(fname, paged(tool))
    except Exception as e:
        manifest["calls"][fname] = {"error": str(e)[:200]}
        print(fname, "ERR", str(e)[:120])

manifest["finishedUtc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(os.path.join(OUT, "MANIFEST.json"), "w") as fh:
    json.dump(manifest, fh, indent=1)
print("PHASE0 DONE")
