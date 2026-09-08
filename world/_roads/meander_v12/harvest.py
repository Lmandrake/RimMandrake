"""Full live harvest for meander_v12. Run with python.exe from the repo root."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

OUT = r"world\_roads\meander_v12" + "\\"
N = 21872
CH = 1500

host, port, token = resolve_endpoint()

chunks = []
lo = 0
while lo < N:
    hi = min(N - 1, lo + CH - 1)
    for attempt in range(3):
        try:
            with RimBridge(host, port, token) as rb:
                r = rb.call("jawa/world_links_get",
                            {"range": "%d-%d" % (lo, hi), "limit": CH + 10})
            break
        except Exception as e:
            print("  retry %d-%d attempt %d: %s" % (lo, hi, attempt, e))
            time.sleep(2)
    else:
        raise SystemExit("harvest failed at %d-%d" % (lo, hi))
    assert r.get("success"), r
    assert not r.get("limitHit"), ("limitHit", lo, hi, r.get("unexaminedAfterLimit"))
    chunks.append({"from": lo, "to": hi, "count": r["count"],
                   "hiddenByBiomeCount": r.get("hiddenByBiomeCount", 0),
                   "tiles": r["tiles"]})
    print("  %d-%d -> %d rows" % (lo, hi, r["count"]))
    lo = hi + 1

json.dump(chunks, open(OUT + "links_live_before.json", "w"))
tot = sum(c["count"] for c in chunks)
print("TILE ROWS %d" % tot)

with RimBridge(host, port, token) as rb:
    objs = rb.call("jawa/world_objects_get", {"limit": 5000})
    lms = rb.call("jawa/world_landmarks_get", {"limit": 5000})
    info = rb.call("jawa/world_info_get", {})
json.dump(objs, open(OUT + "objects_before.json", "w"))
json.dump(lms, open(OUT + "landmarks_before.json", "w"))
json.dump(info, open(OUT + "world_info.json", "w"), indent=1)
print("objects %d/%d  landmarks %d/%d" % (objs.get("returned", 0), objs["count"],
                                          lms.get("returned", 0), lms["count"]))
