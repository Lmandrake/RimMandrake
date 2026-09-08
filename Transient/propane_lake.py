"""Paint RUT_PropaneLake: suspiciously precisely on the antipode, deliberately not round.

Owner, 2026-09-07: "It is supposed to be suspiciously precisely at the antipodal
point, but don't make it perfectly circular please."

Those two demands pull against each other, so they are satisfied by different parts
of the shape:

  PRECISION comes from a centred core (every non-sea tile within R0 of the antipode)
  plus a greedy balance pass that trims whichever fringe tile pulls the centre of
  mass furthest off, until the centroid sits within half a tile-width of the
  antipode tile. Tiles here average 1.37 deg apart, so "within 0.6 deg" is
  sub-tile: precise beyond what geology would do by itself, which is the point.

  IRREGULARITY comes from the ground. The fringe between R0 and R1 is admitted by
  ELEVATION, not radius: propane-lakes ground below the band median, crags ground
  below the band's lower quartile (a crags tile has to be markedly lower to count,
  so the lake mostly stays in propane ground and only bites into the crags where
  they are genuinely low). No RNG and no seed anywhere - a seed is a knob that
  could roll a second planet.

Depth runs from DEEP at the centre to SHALLOW at the margin so the def's own
terrain pairing works as authored: waterDeepTerrain (AB_PropaneLake, the liquid
centre) in the middle, waterShallowTerrain (AB_SolidPropane, the frozen crust) at
the cold edge - the phase-line lake the sheet describes.

Dry by default; --apply paints and commits.
"""
import sys, csv, json, math, statistics, collections, os

WSL = os.path.exists("/mnt/d")
ROOT = "/mnt/d/Luke/dev/Rimworld" if WSL else r"D:\Luke\dev\Rimworld"
J = (lambda *p: os.path.join(ROOT, *p))
sys.path.insert(0, J("src", "RimMandrake", "Utils"))

TARGET_OFF = 0.6      # degrees; half a tile width
R0, R1 = 5.0, 10.0
DEEP, SHALLOW = -210.0, -25.0
NOT_LAKE = {"RUT_TheScald", "RUT_GreySea", "RUT_TwilightSea", "SeaIce", "Lake",
            "RUT_NightsideIce", "RUT_PropaneLake"}

apply = "--apply" in sys.argv

T = {}
for r in csv.DictReader(open(J("Transient", "after_intent.csv"))):
    t = int(r["tile"])
    T[t] = dict(lat=float(r["lat"]), lon=float(r["long"]), biome=r["biome"],
                elev=float(r["elevation"]))


def vec(t):
    la, lo = math.radians(T[t]["lat"]), math.radians(T[t]["lon"])
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def sep_v(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))))


SEED = max(T, key=lambda t: sep_v(vec(t), (1.0, 0.0, 0.0)))
SV = vec(SEED)
d = {t: sep_v(SV, vec(t)) for t in T}

band = [t for t in T if R0 < d[t] <= R1 and T[t]["biome"] not in NOT_LAKE]
m_pro = statistics.median([T[t]["elev"] for t in band if T[t]["biome"] == "AB_PropaneLakes"])
m_cra = statistics.quantiles([T[t]["elev"] for t in band], n=4)[0]
CEIL = 900.0   # nothing above this becomes lake bed: an artificial basin, not a carved mountain
core = [t for t in T if d[t] <= R0 and T[t]["biome"] not in NOT_LAKE and T[t]["elev"] < CEIL]
fringe = [t for t in band
          if T[t]["elev"] < min(CEIL, m_pro if T[t]["biome"] == "AB_PropaneLakes" else m_cra)]

sel = set(core) | set(fringe)


def centroid_off(s):
    v = [sum(vec(t)[i] for t in s) / len(s) for i in range(3)]
    n = math.sqrt(sum(x * x for x in v))
    return sep_v(SV, tuple(x / n for x in v))


print("PROPANE LAKE — RUT_PropaneLake")
print("  antipode tile %d   (grid's closest to 180 deg; mean tile spacing 1.37 deg)" % SEED)
print("  core r<=%.0f: %d tiles   ragged fringe %.0f-%.0f: %d tiles"
      % (R0, len(core), R0, R1, len(fringe)))
print("  fringe admitted below %d m (propane ground) / %d m (crags)" % (m_pro, m_cra))
print("  centroid before balancing: %.3f deg off the antipode" % centroid_off(sel))

trimmed = 0
while centroid_off(sel) > TARGET_OFF and len(sel) > len(core):
    cand = [t for t in sel if t in fringe]
    if not cand:
        break
    best = min(cand, key=lambda t: centroid_off(sel - {t}))
    if centroid_off(sel - {best}) >= centroid_off(sel):
        break
    sel.discard(best)
    trimmed += 1

sel = sorted(sel)
rad = [d[t] for t in sel]
off = centroid_off(set(sel))
q1 = sorted(rad)[len(rad) // 4]
print("  balanced by trimming %d fringe tiles" % trimmed)
print()
print("  RESULT: %d tiles" % len(sel))
print("    centroid  %.3f deg off the antipode  (%.2f of a tile width)" % (off, off / 1.37))
print("    radius    min %.2f  max %.2f deg  -> reaches %.1fx further one way than another"
      % (min(rad), max(rad), max(rad) / max(0.01, q1)))
print("    ground    %s" % dict(collections.Counter(T[t]["biome"] for t in sel).most_common()))
print("    elevation %.0f..%.0f m before excavation" % (min(T[t]["elev"] for t in sel),
                                                       max(T[t]["elev"] for t in sel)))
mr = max(rad)
depth = {t: DEEP + (SHALLOW - DEEP) * (d[t] / mr) for t in sel}
print("    depth     %.0f m centre -> %.0f m margin (liquid centre, crust edge)" % (DEEP, SHALLOW))

json.dump(sel, open(J("Transient", "propane_lake_tiles.json"), "w"))

if not apply:
    print("\nDRY RUN. --apply to paint.")
    sys.exit(0)

from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_set",
                {"tiles": ",".join(str(t) for t in sel), "biome": "RUT_PropaneLake", "readBack": 3})
    print("\nSET biome RUT_PropaneLake -> success=%s" % r.get("success"))
    buckets = collections.defaultdict(list)
    for t in sel:
        buckets[round(depth[t] / 20) * 20].append(t)
    for dep, ts in sorted(buckets.items()):
        rb.call("jawa/world_tile_set", {"tiles": ",".join(str(x) for x in ts),
                                        "elevation": float(dep), "readBack": 1})
    print("SET elevation in %d depth bands (%d..%d m)" % (len(buckets), min(buckets), max(buckets)))
    c = rb.call("jawa/world_commit", {})
    print("COMMIT failedSteps=%s" % c.get("failedSteps"))
