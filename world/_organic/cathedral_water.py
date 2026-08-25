"""The Rust Cathedral is where the rivers come from.

Three things, all measured against the live game before writing:

  Headwater on 14564 - the tile where the HugeRiver arriving from the Anvil and the
    LargeRiver falling into the Scorch actually meet, at 639 m, the highest point on
    the plateau. Its worker is TileMutatorWorker_Headwater, no coast or biome gate.
    The ancient machine vents its own coolant and every river on this side starts here.

  VEE_SulfuricLake - stagnant volcanic pools. coastSidesRange is unset, so landlocked
    is fine (unlike VEE_RisingWaters, which demands 1-5 ocean neighbours and would be
    a coast worker with no coast). Weighted to LOW ground and to tiles near the river
    line, so the flooding follows where water would actually collect.
    ! canSpawnOnRiver is FALSE on this def, so the 8 river-carrying tiles are excluded.
    ! category 'Lake' collides with Headwater's ['River','Lake'], so 14564 is excluded
      too - and Headwater goes on FIRST, because its priority (-1) LOSES to the lake's
      (2) and AddMutator would log a conflict rather than resolve it.

  VEE_ToxicVents - no category, so it stacks on everything already there. Grown from
    seeds rather than sprinkled, so the fissures come in fields.
"""
import sys, json, csv, io, collections, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

B = r'D:\Luke\dev\Rimworld\world' + '\\'
O = B + '_organic\\'
SEED = 20260825
HEADWATER_TILE = 14564
APPLY = "--apply" in sys.argv

T = {int(r['tile']): r for r in csv.DictReader(open(B + '_now7.csv'))}
NB = {int(r['tile']): [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]
      for r in csv.DictReader(open(O + 'neighbors.csv'))}
CATH = [t for t, r in T.items() if r['feature'] == 'Rust Cathedral']
CATHSET = set(CATH)

# the river-carrying tiles inside the region, straight from the live link read
links = json.load(open(O + '_cath_links.json'))["tiles"]
RIVER = {r["tile"] for r in links if r["tile"] in CATHSET and (r.get("potentialRivers") or [])}

# hex distance from the river line, staying inside the region
rdist = {t: 0 for t in RIVER}
frontier = list(RIVER)
while frontier:
    nxt = []
    for t in frontier:
        for n in NB[t]:
            if n in CATHSET and n not in rdist:
                rdist[n] = rdist[t] + 1
                nxt.append(n)
    frontier = nxt
for t in CATH:
    rdist.setdefault(t, 99)

elevs = sorted(float(T[t]['elevation']) for t in CATH)
def elev_pct(t):
    e = float(T[t]['elevation'])
    return sum(1 for x in elevs if x < e) / len(elevs)

rng = random.Random(SEED)

# ---- sulfuric lakes: low ground, near the water ------------------------------
lakes = []
for t in CATH:
    if t in RIVER or t == HEADWATER_TILE:
        continue
    p = 0.10
    p += 0.42 * max(0.0, 1.0 - rdist[t] / 4.0)      # close to the hidden channel
    p += 0.34 * (1.0 - elev_pct(t))                  # and low in the basin
    if rng.random() < p:
        lakes.append(t)

# ---- toxic vents: grown from seeds so they come in fields ---------------------
pool = [t for t in CATH]
rng.shuffle(pool)
vents = set()
for s in pool[:16]:
    vents.add(s)
    for n in NB[s]:
        if n in CATHSET and rng.random() < 0.62:
            vents.add(n)
            for n2 in NB[n]:
                if n2 in CATHSET and rng.random() < 0.28:
                    vents.add(n2)
vents = sorted(vents)

print("Rust Cathedral: %d tiles, %d carrying hidden river links" % (len(CATH), len(RIVER)))
print("river tiles:", sorted(RIVER))
print("Headwater      -> 1 tile  [%d] at %s m" % (HEADWATER_TILE, T[HEADWATER_TILE]['elevation']))
print("VEE_SulfuricLake -> %d tiles" % len(lakes))
print("VEE_ToxicVents   -> %d tiles" % len(vents))
print("overlap lakes/vents: %d (fine - different categories)" % len(set(lakes) & set(vents)))
json.dump({"headwater": [HEADWATER_TILE], "lakes": lakes, "vents": vents},
          open(O + '_cathedral_water_plan.json', 'w'), indent=0)

if not APPLY:
    print("\nDRY RUN. Re-run with --apply.")
    sys.exit(0)

h, p_, tok = resolve_endpoint()
rb = RimBridge(h, p_, tok); rb.connect()
b_ = lambda r: {k: v for k, v in r.items() if k != "operation"}

# Headwater FIRST - see the note in the docstring about priority
for name, tiles in (("Headwater", [HEADWATER_TILE]),
                    ("VEE_SulfuricLake", lakes),
                    ("VEE_ToxicVents", vents)):
    r = b_(rb.call("jawa/world_mutators_set", {"action": "add", "mutators": name,
                                               "tiles": ",".join(map(str, tiles)), "readBack": 1}))
    print("  %-18s tiles=%4d added=%s removed=%s unknown=%s errors=%s" %
          (name, len(tiles), r.get("added"), r.get("removed"), r.get("unknownDefs"), r.get("errors")))

print("commit:", json.dumps(b_(rb.call("jawa/world_commit", {})))[:80])

res = rb.call("jawa/world_mutators_get", {"tiles": ",".join(map(str, CATH)), "limit": 5000})
json.dump(res, open(O + '_cath_mutators_after2.json', 'w'))
got = collections.Counter()
for r in res["tiles"]:
    for m in (r.get("mutators") or []):
        got[m if isinstance(m, str) else m.get("def")] += 1
print("\nREAD BACK, %d tiles:" % len(res["tiles"]))
for m, n in got.most_common():
    print("   %-28s %4d" % (m, n))
hw = [r["tile"] for r in res["tiles"]
      if any((m if isinstance(m, str) else m.get("def")) == "Headwater" for m in (r.get("mutators") or []))]
print("Headwater is on:", hw, "(want [%d])" % HEADWATER_TILE)
bad = [r["tile"] for r in res["tiles"] if r["tile"] in RIVER and
       any((m if isinstance(m, str) else m.get("def")) == "VEE_SulfuricLake" for m in (r.get("mutators") or []))]
print("sulfuric lakes sitting on a river tile (must be 0):", len(bad))
