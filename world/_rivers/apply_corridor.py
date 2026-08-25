"""Apply the corridor repair to the live world. Run under python.exe.

ORDER IS LOAD-BEARING:
  1. drainage links   - joins a tributary to its trunk; changes node degree
  2. biomes           - VEE_DryRiver is biome-locked, so the abandoned course must dry
                        FIRST or the mutator is refused/illegal
  3. mutators         - recomputed after 1 and 2, never from the stale plan
Nothing is visible until jawa/world_commit, which runs once at the end.
"""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

R = r"D:\Luke\dev\Rimworld\world\_rivers" + "\\"
DRY = "--apply" not in sys.argv
drain = json.load(open(R + "drain_plan.json"))
biome = json.load(open(R + "biome_plan.json"))
mutp = json.load(open(R + "mutator_plan.json"))

by_biome = {}
for e in biome:
    by_biome.setdefault(e["to"], []).append(e["tile"])

host, port, token = resolve_endpoint()
log = []
with RimBridge(host, port, token, timeout=300) as rb:
    def call(tool, args, what):
        if DRY:
            n = len((args.get("tiles") or args.get("path") or "").split(","))
            print("  would %-46s %4d tiles" % (what, n)); return
        r = rb.call(tool, args)
        ok = r.get("success")
        log.append((what, ok, r.get("written") or r.get("laid") or r.get("changed")
                    or r.get("added") or r.get("removed") or r.get("tilesTouched"), r.get("message")))
        print("  %-48s %s  %s" % (what, "ok" if ok else "FAILED", r.get("message") or ""))

    print("1. DRAINAGE — join each tributary to its trunk (%d links)" % len(drain))
    for d in drain:
        call("jawa/world_links_set",
             {"kind": "river", "path": "%d,%d" % (d["to"], d["from"]), "def": d["def"], "readBack": 0},
             "link %d -> %d (%s, %.0fm drop)" % (d["from"], d["to"], d["def"], d["drop"]))

    print("\n2. BIOMES — relay the corridor (%d tiles, %d target biomes)"
          % (len(biome), len(by_biome)))
    for b, ts in sorted(by_biome.items(), key=lambda kv: -len(kv[1])):
        call("jawa/world_tile_set",
             {"tiles": ",".join(str(t) for t in ts), "biome": b, "readBack": 0},
             "-> %s" % b)

    if "--stage12" in sys.argv:
        if not DRY:
            c = rb.call("jawa/world_commit", {})
            print("\ncommit:", c.get("success"))
            print("failed calls:", len([l for l in log if not l[1]]))
        sys.exit(0)

    print("\n3. MUTATORS")
    for defn, ts in sorted(mutp["remove"].items(), key=lambda kv: -len(kv[1])):
        call("jawa/world_mutators_set",
             {"action": "remove", "mutators": defn,
              "tiles": ",".join(str(t) for t in ts), "readBack": 0},
             "remove %s" % defn)
    for defn, ts in sorted(mutp["add"].items(), key=lambda kv: -len(kv[1])):
        call("jawa/world_mutators_set",
             {"action": "add", "mutators": defn,
              "tiles": ",".join(str(t) for t in ts), "readBack": 0},
             "add %s" % defn)

    if not DRY:
        c = rb.call("jawa/world_commit", {})
        print("\ncommit:", c.get("success"))
        bad = [l for l in log if not l[1]]
        print("failed calls:", len(bad))
        for b in bad: print("  ", b)
