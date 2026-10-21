"""python.exe _parity_apply_2026-10-20.py <u1|u2|u4|labels70> <outdir> [--apply]

Applies one world-parity fix plan (built by src/RimMandrake/Utils/parity_fix_plans.py) to the
LIVE world through the bridge. Dry run by default: reads the live world, checks every plan
`before` value, lints, stops. --apply writes, commits, reads back, lints.
Causes: design/Jawa/worldbuilding/parity_causes_2026-10-20.md.

  u1  region labels  : world_features_set maxDrawSizeInTiles + centerOnTile, per feature (by name)
  u2  tile mutators  : world_mutators_set remove (28,280) then add (123 stamp entries that never landed)
  labels70  region labels x0.70 displayed width (owner card 2026-10-20); needs u1 applied first
  u4  river flow     : world_links_import clearFirst on the mouth-first CSV (same edges, same defs)
"""
import sys, json, os
from collections import defaultdict
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

WORLD = r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\world"
PLANS = {"u1": "ASHKARR_PARITY_U1_labels_2026-10-20_plan.json",
         "u2": "ASHKARR_PARITY_U2_mutators_2026-10-20_plan.json",
         "u4": "ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json",
         "labels70": "ASHKARR_LABELS70_2026-10-20_plan.json"}
which, out = sys.argv[1], sys.argv[2]; APPLY = "--apply" in sys.argv
os.makedirs(out, exist_ok=True)
plan = json.load(open(os.path.join(WORLD, PLANS[which]), encoding="utf-8"))
host, port, token = resolve_endpoint()
def dump(name, obj): open(os.path.join(out, name), "w", encoding="utf-8").write(json.dumps(obj, default=str, indent=1))
def chunks(xs, n):
    for i in range(0, len(xs), n): yield xs[i:i + n]

with RimBridge(host, port, token) as rb:
    def lint(tag):
        l = rb.call("jawa/world_lint", {"limit": 50}); dump("lint_%s.json" % tag, l)
        print("lint %s:" % tag, {k: v for k, v in l.items() if not isinstance(v, (list, dict))})

    def features():
        r = rb.call("jawa/world_features_get", {"limit": 500})
        return {f["name"]: f for f in r.get("features") or []}

    def tile_rows(ts, tool="jawa/world_tile_get", extra=None):
        rows = []
        for c in chunks(ts, 200):
            args = {"tiles": ",".join(map(str, c)), "limit": 1000}
            args.update(extra or {})
            rows += rb.call(tool, args).get("tiles") or []
        return {int(r["tile"]): r for r in rows}

    def muts(row):
        return set((m or {}).get("def") if isinstance(m, dict) else m for m in (row.get("mutators") or []))

    mism = []
    if which in ("u1", "labels70"):
        live = features()
        for f in plan["features"]:
            l = live.get(f["name"]); b = f["before"]
            if l is None: mism.append((f["name"], "missing live")); continue
            dc = l["drawCenter"]; got = (dc["x"], dc["y"], dc["z"])
            if max(abs(a - c) for a, c in zip(got, b["drawCenter"])) > 0.01 or (b["size"] is not None and abs(l["maxDrawSizeInTiles"] - b["size"]) > 0.01):
                mism.append((f["name"], got, l["maxDrawSizeInTiles"]))
        print("%s: %d features, live != before on %d" % (which, len(plan["features"]), len(mism)), mism[:5])
    elif which == "u2":
        need = defaultdict(set)
        for m, ts in plan["remove"].items():
            for t in ts: need[t].add(("has", m))
        for m, ts in plan["restore"].items():
            for t in ts: need[t].add(("lacks", m))
        live = tile_rows(sorted(need), "jawa/world_mutators_get")
        for t, conds in need.items():
            have = muts(live.get(t, {}))
            for kind, m in conds:
                if (kind == "has") != (m in have): mism.append((t, kind, m))
        print("u2: %d tiles, %d remove, %d restore; live != before on %d"
              % (len(need), plan["counts"]["remove"], plan["counts"]["restore"], len(mism)), mism[:8])
    elif which == "u4":
        ts = sorted(int(t) for t in plan["before"])
        live = tile_rows(ts)
        mism = [t for t in ts if int(live.get(t, {}).get("riverDist", -1)) != plan["before"][str(t)]]
        print("u4: %d river tiles, live riverDist != before on %d" % (len(ts), len(mism)), mism[:10])
        dry = rb.call("jawa/world_links_import", {"path": os.path.join(WORLD, plan["linksCsv"]),
                                                  "apply": False, "expectTiles": 21872})
        print("u4 import dry:", {k: dry.get(k) for k in ("success", "rows", "rivers", "roads", "nonAdjacentRefused", "unknownDefs")})
        if not dry.get("success") or dry.get("rivers") != plan["counts"]["riverEdges"] or dry.get("roads") != plan["counts"]["roads"]:
            mism.append("dry import counts")
    dump("mismatch_%s.json" % which, mism)
    lint("before")
    if mism or not APPLY:
        sys.exit(0 if not mism else 2)

    if which in ("u1", "labels70"):
        live = features()
        for f in plan["features"]:
            a = f["after"]
            args = {"action": "update", "featureId": live[f["name"]]["uniqueID"], "centerOnTile": int(a["centerOnTile"])}
            if a["size"] is not None: args["maxDrawSizeInTiles"] = float(a["size"])
            r = rb.call("jawa/world_features_set", args)
            if not r.get("success"): print("set fail", f["name"], (r.get("message") or "")[:120])
    elif which == "u2":
        for m, ts in sorted(plan["remove"].items()):
            for c in chunks(ts, 1000):
                r = rb.call("jawa/world_mutators_set", {"action": "remove", "mutators": m, "tiles": ",".join(map(str, c)), "readBack": 0})
                if not r.get("success"): print("remove fail", m, (r.get("message") or "")[:120])
        for m, ts in sorted(plan["restore"].items()):
            r = rb.call("jawa/world_mutators_set", {"action": "add", "mutators": m, "tiles": ",".join(map(str, ts)), "readBack": 0})
            if not r.get("success"): print("add fail", m, (r.get("message") or "")[:120])
    elif which == "u4":
        r = rb.call("jawa/world_links_import", {"path": os.path.join(WORLD, plan["linksCsv"]), "apply": True,
                                                "expectTiles": 21872, "clearFirst": True})
        print("u4 import:", {k: r.get(k) for k in ("success", "rows", "rivers", "roads", "nonAdjacentRefused", "refused")})
    c = rb.call("jawa/world_commit", {}); print("commit", c.get("success"), (c.get("message") or "")[:200])

    bad = []
    if which in ("u1", "labels70"):
        live = features()
        for f in plan["features"]:
            l, a = live[f["name"]], f["after"]; dc = l["drawCenter"]
            if (a["size"] is not None and abs(l["maxDrawSizeInTiles"] - a["size"]) > 0.01) or max(abs(x - y) for x, y in zip((dc["x"], dc["y"], dc["z"]), a["drawCenter"])) > 0.05:
                bad.append(f["name"])
    elif which == "u2":
        need = defaultdict(set)
        for m, ts in plan["remove"].items():
            for t in ts: need[t].add(("gone", m))
        for m, ts in plan["restore"].items():
            for t in ts: need[t].add(("back", m))
        live = tile_rows(sorted(need), "jawa/world_mutators_get")
        for t, conds in need.items():
            have = muts(live.get(t, {}))
            for kind, m in conds:
                if (kind == "back") != (m in have): bad.append((t, kind, m))
    elif which == "u4":
        ts = sorted(int(t) for t in plan["after"])
        live = tile_rows(ts)
        bad = [t for t in ts if int(live.get(t, {}).get("riverDist", -1)) != plan["after"][str(t)]]
    dump("readback_bad_%s.json" % which, bad)
    print("readback mismatches", len(bad), bad[:10])
    lint("after")
