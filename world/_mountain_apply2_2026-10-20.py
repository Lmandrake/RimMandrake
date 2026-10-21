"""python.exe apply.py <plan.json> <outdir> [--apply] : verify live base == plan.before, lint, (apply, commit, lint, read back)."""
import sys, json, os
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from collections import Counter, defaultdict
plan = json.load(open(sys.argv[1])); out = sys.argv[2]; APPLY = "--apply" in sys.argv
NAMES = ["Undefined", "Flat", "SmallHills", "LargeHills", "Mountainous", "Impassable"]
host, port, token = resolve_endpoint()
def dump(name, obj): open(os.path.join(out, name), "w", encoding="utf-8").write(json.dumps(obj, default=str, indent=1))
with RimBridge(host, port, token) as rb:
    tiles = sorted(int(t) for t in plan["hilliness"]) 
    etiles = sorted(int(t) for t in plan["elevation"])
    def read(ts):
        rows = []
        for i in range(0, len(ts), 200):
            r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, ts[i:i+200]))})
            rows += r.get("tiles") or []
        return rows
    def hv(r):
        h = r.get("hilliness")
        return NAMES.index(h) if isinstance(h, str) and h in NAMES else int(h)
    live = read(tiles)
    print("read", len(live), "sample", json.dumps(live[0])[:300])
    mism = [r["tile"] for r in live if hv(r) != plan["before"][str(r["tile"])]]
    print("live hilliness != plan.before on", len(mism), "of", len(live), mism[:10])
    eb0 = read(etiles) if etiles else []
    emism = [r["tile"] for r in eb0 if abs(float(r["elevation"]) - plan.get("elevationBefore", {}).get(str(r["tile"]), float(r["elevation"]))) > 1]
    print("live elevation != plan.elevationBefore on", len(emism), "of", len(eb0), emism[:10]); mism = mism + emism
    lint0 = rb.call("jawa/world_lint", {"limit": 50}); dump("lint_before.json", lint0)
    print("lint before:", {k: v for k, v in lint0.items() if not isinstance(v, (list, dict))})
    if mism or not APPLY:
        sys.exit(0 if not mism else 2)
    setfail = 0
    groups = defaultdict(list)
    for t, v in plan["hilliness"].items(): groups[v].append(int(t))
    for v, ts in sorted(groups.items()):
        for i in range(0, len(ts), 1000):
            r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, ts[i:i+1000])), "hilliness": NAMES[v], "readBack": 0})
            print("set", NAMES[v], len(ts[i:i+1000]), r.get("success"), r.get("written"), (r.get("message") or "")[:120])
            setfail += not r.get("success")
    for t, e in plan["elevation"].items():
        r = rb.call("jawa/world_tile_set", {"tiles": t, "elevation": float(e), "readBack": 0})
        if not r.get("success"): print("elev fail", t, r.get("message")); setfail += 1
    if setfail:   # never commit a half-written plan
        print("ABORT: %d set call(s) failed; NOT committing (live world holds uncommitted partial edits)" % setfail); sys.exit(3)
    c = rb.call("jawa/world_commit", {}); print("commit", c.get("success"), (c.get("message") or "")[:200])
    back = read(tiles); bad = [r["tile"] for r in back if hv(r) != plan["hilliness"][str(r["tile"])]]
    eb = read(etiles); ebad = [r["tile"] for r in eb if abs(float(r["elevation"]) - plan["elevation"][str(r["tile"])]) > 1]
    print("readback hilliness mismatches", len(bad), bad[:10], "elevation mismatches", len(ebad))
    lint1 = rb.call("jawa/world_lint", {"limit": 50}); dump("lint_after.json", lint1)
    print("lint after:", {k: v for k, v in lint1.items() if not isinstance(v, (list, dict))})
