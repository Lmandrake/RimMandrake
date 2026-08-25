"""Paint the Rust Cathedral: ancient heat vents all over it, plus everything that
resonates with a mechanoid-haunted plateau.

Design constraints, all MEASURED against the live game 2026-08-25, not assumed:
  * Every vent (Odyssey's 3 + Alpha Biomes' 4) shares category 'AncientVent', and
    Tile.AddMutator EVICTS a same-category mutator. ONE vent per tile, always.
  * AncientGarrison/Warehouse/ChemfuelRefinery/LaunchSite share 'AncientStructure'.
    ONE structure per tile.
  * TerraformingScar and VEE_Volcano share 'Mountain'. Never both.
  * MineralRich is category 'VEE_Minerals' - alone in this palette, so free.
  * The other eight carry NO category and stack without limit.
  * AncientHeatVent's biomeWhitelist does NOT include AB_MechanoidIntrusion. That
    list is only read by TileMutatorDef.IsValidTile, which gates RANDOM SELECTION
    at worldgen; AddMutator never calls it and every map-gen GenStep just iterates
    map.TileInfo.Mutators. Hand-placed vents therefore function. Deliberate.

The region is shaped, not sprinkled: density falls off from the centre outward, so
the Cathedral reads as a structure with a nave and a rim rather than as noise.
"""
import sys, json, csv, io, collections, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

B = r'D:\Luke\dev\Rimworld\world' + '\\'
O = B + '_organic\\'
SEED = 20260825
CENTRE = 21547          # centroid tile of the Rust Cathedral; The Free Charge sits here
APPLY = "--apply" in sys.argv

T = {int(r['tile']): r for r in csv.DictReader(open(B + '_now7.csv'))}
NB = {int(r['tile']): [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]
      for r in csv.DictReader(open(O + 'neighbors.csv'))}
CATH = [t for t, r in T.items() if r['feature'] == 'Rust Cathedral']
CATHSET = set(CATH)

# hex distance from the centre, staying inside the region
dist = {CENTRE: 0}
frontier = [CENTRE]
while frontier:
    nxt = []
    for t in frontier:
        for n in NB[t]:
            if n in CATHSET and n not in dist:
                dist[n] = dist[t] + 1
                nxt.append(n)
    frontier = nxt
for t in CATH:
    dist.setdefault(t, 99)          # any lobe not reachable through the region
maxd = max(d for d in dist.values() if d < 99)

rng = random.Random(SEED)
plan = collections.defaultdict(list)     # tile -> [mutator, ...]

def band(t):
    """0 = nave, 1 = aisles, 2 = rim."""
    d = dist[t]
    if d <= maxd * 0.33: return 0
    if d <= maxd * 0.70: return 1
    return 2

# ---- the vents: one per tile, heat vent dominant, weirder ones toward the nave --
VENT_RATE   = [0.97, 0.88, 0.70]     # share of tiles in each band that vent at all
WEIRD_RATE  = [0.30, 0.16, 0.06]     # of those, share that vent something stranger
WEIRD = ["AB_AncientGreyPallVent", "AB_AncientDeathPallVent",
         "AB_AncientBloodRainVent", "AB_AncientFreezingVent"]
WEIRD_W = [0.40, 0.30, 0.22, 0.08]   # freezing vents are the rarest joke on a 62 C plateau

# ---- the stackables: density falls off outward -------------------------------
STACK_RATES = {
    "AB_DerelictClusters":     [0.92, 0.78, 0.55],   # built for this biome; the rust itself
    "AB_AmbientRadiation":     [0.72, 0.48, 0.26],
    "VEE_MechanoidShipChunks": [0.55, 0.38, 0.22],
    "AncientRuins":            [0.50, 0.38, 0.26],
    "Junkyard":                [0.42, 0.30, 0.18],
    "MineralRich":             [0.30, 0.22, 0.16],
    "AncientUplink":           [0.10, 0.05, 0.02],
}

for t in CATH:
    b = band(t)
    if rng.random() < VENT_RATE[b]:
        if rng.random() < WEIRD_RATE[b]:
            plan[t].append(rng.choices(WEIRD, weights=WEIRD_W)[0])
        else:
            plan[t].append("AncientHeatVent")
    for m, rates in STACK_RATES.items():
        if rng.random() < rates[b]:
            plan[t].append(m)

# ---- one ancient structure per tile, a handful in all ------------------------
pool = [t for t in CATH if dist[t] < 99]
rng.shuffle(pool)
def take(n, pred=lambda t: True):
    out = []
    for t in list(pool):
        if len(out) == n: break
        if pred(t):
            out.append(t); pool.remove(t)
    return out

SHOWPIECE = {}
SHOWPIECE[CENTRE] = "AncientLaunchSite"          # the enclaves' relic, dead centre
if CENTRE in pool: pool.remove(CENTRE)
for t in take(6):  SHOWPIECE[t] = "AncientGarrison"
for t in take(5):  SHOWPIECE[t] = "AncientWarehouse"
for t in take(4):  SHOWPIECE[t] = "AncientChemfuelRefinery"
for t in take(3):  SHOWPIECE[t] = "AncientInfestedSettlement"   # no category; stacks anyway
for t, m in SHOWPIECE.items():
    plan[t].append(m)

# ---- Mountain category: scars inland, one volcano on the rim ------------------
scars = take(5, lambda t: band(t) != 2)
for t in scars:
    plan[t].append("TerraformingScar")
volc = take(1, lambda t: band(t) == 2 and t not in scars)
for t in volc:
    plan[t].append("VEE_Volcano")

# ---- one-of-a-kind ------------------------------------------------------------
ARCH = 5072                                       # Second Speaker's tile
plan[ARCH].append("AB_DerelictArchonexus")

# ---- contradictions to clear: the plateau has no rivers -----------------------
KILL = ["River", "VEE_StagnantRivulet"]

# ---- report -------------------------------------------------------------------
cnt = collections.Counter(m for ms in plan.values() for m in ms)
print("Rust Cathedral: %d tiles, centre %d, radius %d hexes" % (len(CATH), CENTRE, maxd))
print("tiles receiving at least one mutator: %d" % len(plan))
print("mutators placed: %d" % sum(len(v) for v in plan.values()))
for m, n in cnt.most_common():
    print("   %-28s %4d" % (m, n))
per = collections.Counter(len(v) for v in plan.values())
print("tiles by mutator count:", sorted(per.items()))
print("showpieces:", {t: m for t, m in SHOWPIECE.items()}, "volcano:", volc, "archonexus:", ARCH)
json.dump({str(k): v for k, v in plan.items()}, open(O + '_cathedral_plan.json', 'w'), indent=0)

if not APPLY:
    print("\nDRY RUN. Re-run with --apply to write it to the live world.")
    sys.exit(0)

# ---- apply, one call per def -------------------------------------------------
h, p, tok = resolve_endpoint()
rb = RimBridge(h, p, tok); rb.connect()
b_ = lambda r: {k: v for k, v in r.items() if k != "operation"}

allc = ",".join(str(t) for t in CATH)
r = rb.call("jawa/world_mutators_set", {"action": "remove", "mutators": ",".join(KILL),
                                        "tiles": allc, "readBack": 1})
print("cleared river contradictions:", b_(r).get("removed"), "errors", b_(r).get("errors"))

bydef = collections.defaultdict(list)
for t, ms in plan.items():
    for m in ms:
        bydef[m].append(t)
for m, tiles in sorted(bydef.items()):
    r = b_(rb.call("jawa/world_mutators_set", {"action": "add", "mutators": m,
                                               "tiles": ",".join(map(str, tiles)), "readBack": 1}))
    print("  %-28s tiles=%4d added=%s removed=%s unknown=%s" %
          (m, len(tiles), r.get("added"), r.get("removed"), r.get("unknownDefs")))

print("commit:", json.dumps(b_(rb.call("jawa/world_commit", {})))[:80])

# ---- verify by reading the region back ---------------------------------------
res = rb.call("jawa/world_mutators_get", {"tiles": allc, "limit": 5000})
json.dump(res, open(O + '_cath_mutators_after.json', 'w'))
rows = res["tiles"]
got = collections.Counter()
nper = collections.Counter()
for r in rows:
    ms = [m if isinstance(m, str) else m.get("def") for m in (r.get("mutators") or [])]
    nper[len(ms)] += 1
    for m in ms: got[m] += 1
print("\nREAD BACK from the live world: %d tiles" % len(rows))
for m, n in got.most_common():
    flag = "" if got[m] == cnt.get(m, 0) else "   <-- expected %d" % cnt.get(m, 0)
    print("   %-28s %4d%s" % (m, n, flag))
print("tiles by mutator count:", sorted(nper.items()))
vent_cats = set(["AncientHeatVent"] + WEIRD)
bad = [r["tile"] for r in rows
       if len([m for m in [(x if isinstance(x, str) else x.get("def")) for x in (r.get("mutators") or [])]
               if m in vent_cats]) > 1]
print("tiles with more than one vent (must be 0):", len(bad))
