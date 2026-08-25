"""Apply plan.json to the live world. Run under python.exe - the bridge is Windows-side.

Order matters twice over:
  * each old segment is CLEARED by naming the exact pair, never the whole tile, so a
    junction shared with another chain keeps its other links;
  * each new path is LAID MOUTH FIRST, because OverlayRiver sets
    riverDist = max(riverDist, previous + 1).
Nothing is visible until jawa/world_commit.
"""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

DRY = "--apply" not in sys.argv
plan = json.load(open(r"D:\Luke\dev\Rimworld\world\_rivers\plan.json"))
host, port, token = resolve_endpoint()
cleared = laid = refused = 0
problems = []
with RimBridge(host, port, token, timeout=300) as rb:
    for e in plan:
        old, new, d = e["old"], e["new"], e["rdef"]
        if DRY:
            print("would clear %d pairs, lay %s along %d tiles (%s)"
                  % (len(old) - 1, d, len(new), "->".join(str(t) for t in new[:4]) + "..."))
            continue
        for i in range(len(old) - 1):
            r = rb.call("jawa/world_links_clear",
                        {"kind": "river", "tiles": str(old[i]), "to": old[i + 1], "readBack": 0})
            if not r.get("success"):
                problems.append(("clear", old[i], old[i + 1], r.get("message")))
            else:
                cleared += r.get("removedEntries", 0)
        r = rb.call("jawa/world_links_set",
                    {"kind": "river", "path": ",".join(str(t) for t in new),
                     "def": d, "readBack": 0})
        if not r.get("success"):
            problems.append(("set", new[0], new[-1], r.get("message")))
        else:
            laid += r.get("laid", 0)
            for x in (r.get("refused") or []):
                refused += 1; problems.append(("refused", x.get("from"), x.get("to"), x.get("why")))
    if not DRY:
        c = rb.call("jawa/world_commit", {})
        print("commit:", c.get("success"), c.get("message") or "")

print("\ncleared entries %d   laid segments %d   refused %d" % (cleared, laid, refused))
for p in problems[:20]:
    print("  PROBLEM", p)
