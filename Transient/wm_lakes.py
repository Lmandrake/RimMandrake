import sys, json, csv, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

LAKES = [957, 1446, 4161, 4924, 9784, 12269, 12271, 13026, 13027, 16042]

auth = {int(r["tile"]): r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("%-7s %8s %9s %6s %8s %7s %7s  %-10s  %s" % (
        "tile", "lat", "lon", "arc", "elev", "temp", "rain", "region", "neighbours"))
    for t in LAKES:
        a = auth[t]
        nb = rb.call("jawa/world_neighbors", {"tile": t})
        ids = nb.get("neighbors") or nb.get("neighbours") or []
        ids = [n["tile"] if isinstance(n, dict) else n for n in ids]
        nbio = collections.Counter(auth[i]["biome"] for i in ids if i in auth)
        nel = [float(auth[i]["elev_m"]) for i in ids if i in auth]
        print("%-7d %8s %9s %6s %8s %7s %7s  %-10s  %s   nbr elev %.0f..%.0f" % (
            t, a["lat"], a["lon"], a["arc"], a["elev_m"], a["temp_c"], a["rain_mm"],
            a["region"], dict(nbio), min(nel), max(nel)))
