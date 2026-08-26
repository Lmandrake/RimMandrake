# -*- coding: utf-8 -*-
import sys, json, io, os, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
OUT = r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t = rc.resolve_endpoint()
b = rc.RimBridge(host=h, port=p, token=t); b.connect()

def w(name, obj):
    with io.open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    print("wrote", name, len(json.dumps(obj)))

N = 21872
# 1 bulk tile export straight to disk
r = b.call('jawa/world_tile_export', {"path": OUT + r"\live_tiles.csv", "format":"csv", "extended": True})
print("tile_export", json.dumps(r)[:300])

# 2 stats / layers / features
w("stats.json",    b.call('jawa/world_stats', {"limit": 200}))
w("layers.json",   b.call('jawa/world_layers', {}))
w("features.json", b.call('jawa/world_features_get', {"limit": 500}))
w("objects.json",  b.call('jawa/world_objects_get', {"limit": 5000}))
w("landmarks.json",b.call('jawa/world_landmarks_get', {"limit": 30000}))

# 3 mutators in chunks
mut = []
step = 1000
for s in range(0, N, step):
    e = min(s+step, N) - 1
    rr = b.call('jawa/world_mutators_get', {"range": "%d-%d" % (s, e), "onlyWithMutators": True, "limit": 5000})
    rows = rr.get('tiles') or rr.get('rows') or []
    mut.extend(rows)
w("mutators.json", mut)

# 4 links in chunks
lk = []
for s in range(0, N, step):
    e = min(s+step, N) - 1
    rr = b.call('jawa/world_links_get', {"range": "%d-%d" % (s, e), "onlyLinked": True, "limit": 5000})
    rows = rr.get('tiles') or rr.get('rows') or []
    lk.extend(rows)
w("links.json", lk)
print("DONE")
