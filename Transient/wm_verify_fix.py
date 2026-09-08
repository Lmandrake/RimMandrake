import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

LAKES = [957, 1446, 4161, 4924, 9784, 12269, 12271, 13026, 13027, 16042]
WANT = {957: "AB_TarPits", 4924: "AB_TarPits", 9784: "AB_TarPits",
        13026: "AB_TarPits", 13027: "AB_TarPits",
        1446: "ZBiome_Badlands", 4161: "ZBiome_Badlands",
        12269: "ZBiome_Badlands", 12271: "ZBiome_Badlands", 16042: "ZBiome_Badlands"}

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # 1. fresh export = raw live fields
    rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\live_after.csv"})

    # 2. mutator LOSSES diff
    r = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
    after = {x["tile"]: sorted(d["def"] for d in x["mutators"])
             for x in (r.get("tiles") or r.get("rows") or [])}
    before = {int(k): v for k, v in json.load(open(r"D:\Luke\dev\Rimworld\Transient\mutators_before.json")).items()}
    lost = collections.Counter()
    gained = collections.Counter()
    for t, b in before.items():
        a = after.get(t, [])
        for d in set(b) - set(a):
            lost[d] += 1
        for d in set(a) - set(b):
            gained[d] += 1
    print("== mutator diff over all 21872 tiles ==")
    print("  LOST:   ", dict(lost) or "NOTHING")
    print("  GAINED: ", dict(gained) or "NOTHING")

    # 3. the 10 ex-lake tiles, raw
    print("\n== the 10 ex-Lake tiles, read back raw ==")
    ok = True
    for t in LAKES:
        g = rb.call("jawa/world_tile_get", {"tiles": str(t)})
        row = (g.get("tiles") or g.get("rows") or [{}])[0]
        bio, el = row.get("biome"), row.get("elevation")
        muts = after.get(t, [])
        good = (bio == WANT[t]) and (el is not None and el > 0)
        ok &= good
        print("  %-6d %-18s %6.0f m  %-3s  mutators: %s"
              % (t, bio, el, "OK" if good else "BAD", ", ".join(muts)))

    # 4. no vanilla water biome left
    st = rb.call("jawa/world_stats", {})
    print("\n== world_stats ==")
    print("  " + st.get("message", ""))
    lv = rb.call("jawa/world_links_validate", {})
    print("  riverEntries=%s roadEntries=%s asymmetric=%s nonAdjacent=%s hiddenByBiome=%s"
          % (lv.get("riverEntries"), lv.get("roadEntries"), lv.get("asymmetricCount"),
             lv.get("nonAdjacentCount"), lv.get("hiddenByBiomeCount")))
    ln = rb.call("jawa/world_lint", {})
    ch = ln.get("checks", {})
    print("  world_lint total=%s  landBiomeSubmerged=%s  staleMarineMutators=%s  waterBiomeOnRaisedLand=%s"
          % (ln.get("totalFindings"), ch.get("landBiomeSubmerged", {}).get("count"),
             ch.get("staleMarineMutators", {}).get("count"),
             ch.get("waterBiomeOnRaisedLand", {}).get("count")))
    print("\nALL TEN TILES OK" if ok else "\n!! SOME TILES BAD")
