import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("jawa/world_stats", {})

hist = None
for k in ("biomes", "biomeHistogram", "byBiome", "biomeCounts"):
    if k in st:
        hist = st[k]
        break

if hist is None:
    print("NO HISTOGRAM. top-level keys:", sorted(st.keys()))
    sys.exit(1)

if isinstance(hist, dict):
    rows = sorted(hist.items(), key=lambda kv: -kv[1])
else:
    rows = sorted(((r.get("biome") or r.get("defName"), r.get("tiles") or r.get("count")) for r in hist),
                  key=lambda kv: -kv[1])

total = sum(c for _, c in rows)
print("biomes: %d distinct, %d tiles total" % (len(rows), total))
print()
for name, c in rows:
    print("%6d  %5.2f%%  %s" % (c, 100.0 * c / total, name))
