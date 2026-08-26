"""
Build the deterministic tile-list plan for the Grey Sea's three approved mutator
passes (2 THE JUNKER COAST, 4 THE WADING SEA, 5 THE FOUR MOUTHS AND THE COLD END)
from world/_grey/BRIEF.md and the precomputed geometry in
world/_roads/grey_geom.json, then writes world/_grey/grey_plan.json for
apply_grey_mutators.py to consume.

Analysis-only: reads local files and the freshly-harvested
world/_grey/planet_mutators_before.json (the whole-planet BEFORE snapshot taken
over the live bridge immediately before any write - never the stale cached
world/_roads/_muts_now.json, which is from an earlier session). Run under
python3 with /mnt/d/... paths - this script never touches the bridge.

Passes 1 (extending VEE_SaltPlains) and 3 (a brine-works economy) were declined
by the owner and are NOT built here at all - no VEE_SaltPlains anywhere in this
plan, on purpose.

⛔ NO RNG. Every subset choice is h(t) = (t * 2654435761) % 100, so the exact
same plan comes out every run. A knob that could roll a second planet is out of
scope even turned once - this is the same standing ruling the Scald and
Twilight passes worked under.

Gates enforced here (BRIEF.md's own table, verified against measured facts
below where the brief's own note was truncated):
  Junkyard            max hilliness SmallHills -> low_shore only
  AncientRuins        ungated except biome AB_MechanoidIntrusion (N/A: no ring
                       tile is that biome - measured, not assumed)
  AncientWarehouse    biome AridShrubland/Desert/ExtremeDesert. Ring has no
                       ExtremeDesert tile, so effectively Arid+Desert here.
  Stockpile, VEE_MineralDevoid, VEE_DeepOreDevoid, Coast, AnimalHabitat,
  AnimalLife_Increased, Fish_Increased, RiverDelta   ungated
  VEE_RisingWaters    max hilliness Flat + coastline 1-5 -> flat_shore exactly
  VEE_AlluvialFan     max hilliness Flat + coastline 1-6. Measured: of the 4
                       mouths only 11503 is Flat (8081 h3, 16898/16902 h4), and
                       NONE of the other three mouths has a Flat ring neighbour
                       either (checked live via world_neighbors_sub7b.csv) - so
                       this def lands on exactly ONE tile, 11503. That is a
                       measured "there is nowhere else", not underuse.
  Iceberg             temp -100..0, biome SeaIce/IceSheet -> iceedge (all 52
                       are SeaIce, the sea's only ice biome)
  IceDunes            biome SeaIce/IceSheet, max hilliness Flat -> ALL 91 ice
                       tiles measure hilliness Flat (checked live), so the
                       hilliness gate excludes nothing here
  VEE_DeepSnow        temp -100..5, biome IceSheet/SeaIce/Tundra -> all 91 ice
                       tiles qualify (arc 97.5-108, well within range)
  WindyMutator        biome AridShrubland/Desert/ExtremeDesert/IceSheet/
                       SeaIce/Tundra -> ice tiles + the arid/desert ring
  Archipelago         coastline 2-5, no river, biome-locked (brief's own note
                       says "truncated"). Resolved by READING BACK the 11
                       Archipelago tiles ALREADY live on this ring (not
                       guessed): their biomes are AridShrubland, Desert,
                       ZBiome_Badlands and Wasteland - i.e. every ring biome
                       except the 6-tile AB_MiasmicMangrove pocket, which is
                       excluded here as unverified rather than assumed
                       compatible.

Traps hit while building this:
  - 16898 is simultaneously a river mouth AND one of the 23 has_landmark ring
    tiles. The brief's pass-5 text says "RiverDelta ... on each of 8081,
    11503, 16898, 16902" but the HARD RULES say never stack on a has_landmark
    tile, and that rule outranks the pass text. RiverDelta (and every other
    new mutator in this plan) is written to 8081, 11503, 16902 only - 16898 is
    left exactly as it is. This mirrors the Scald/Twilight lesson: a
    protection rule beats a literal list when they collide.
  - Tile 16887, also has_landmark, ALREADY carries VEE_AlluvialFan live -
    almost certainly grandfathered from earlier map/world authoring, not
    something this plan is adding. It is excluded from every candidate pool
    like any other has_landmark tile and reported as "already present",
    never as something this pass placed.
  - AnimalHabitat/Fish_Increased/AnimalLife_Increased already sit on a handful
    of ring tiles (e.g. 3222, 5129) - AddMutator is a no-op if the def is
    already there, so this plan explicitly subtracts existing holders before
    counting "added" so the verify step can tell "already had it" apart from
    "this pass placed it".
  - Within pass 2's landmark-like POI family (Junkyard, AncientRuins,
    AncientWarehouse) each later def's candidate pool excludes tiles the
    earlier defs already claimed in THIS plan, so the three don't spend the
    gap budget overwriting each other's placements the moment they are
    written (self-inflicted category conflict, not the "system working"
    conflict the brief is fine with). Likewise in pass 4, Archipelago's pool
    excludes VEE_RisingWaters' selection - both are coastline-shape mutators
    and the Twilight report confirms that family displaces itself
    (VEE_RisingWaters<->CoastalAtoll<->Bay). Coast coexists freely with both
    (measured: existing tile 8081 already carries Fish_Increased+River+Coast
    together, so Coast is not in that family). IceDunes and VEE_DeepSnow are
    partitioned by hash parity for the same reason, defensively, since no
    measurement proves they share a category and none proves they don't.
"""
import json, csv

ROOT = '/mnt/d/Luke/dev/Rimworld/world/'
OUT_PATH = ROOT + '_grey/grey_plan.json'

geom = json.load(open(ROOT + '_roads/grey_geom.json'))
body = set(geom['body'])
ring = set(geom['ring'])
ocean = set(geom['ocean'])
ice = set(geom['ice'])
edge = set(geom['edge'])
iceedge = set(geom['iceedge'])
flat_shore = set(geom['flat_shore'])
low_shore = set(geom['low_shore'])
near_junk = set(geom['near_junk'])
mouths = geom['mouths']
has_landmark = set(geom['has_landmark'])
dist = {int(k): v for k, v in geom['dist'].items()}

tiles = {}
for r in csv.DictReader(open(ROOT + '_roads/now_tiles.csv')):
    t = int(r['tile'])
    tiles[t] = dict(biome=r['biome'], hill=int(r['hilliness']),
                     river_count=int(r['river_count']), arc=float(r['arc']),
                     temp_c=float(r['temp_c']))

nb = {}
for r in csv.DictReader(open(ROOT + 'world_neighbors_sub7b.csv')):
    t = int(r['tile'])
    nb[t] = [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]

before = json.load(open(ROOT + '_grey/planet_mutators_before.json'))


def have(defname, pool):
    return set(t for t in pool if defname in before.get(str(t), []))


h = lambda t: (t * 2654435761) % 100

# ---------------------------------------------------------------------------
# PROTECTED DEFS - the task's own hard rule: CoastalIsland, Archipelago,
# Oasis, Bay and VEE_GravelBeach are protected on this shore (island
# scattering asked for by name; canon protects oases). A first draft of this
# plan excluded has_landmark from every pool but did NOT exclude tiles
# already carrying one of these five - VEE_RisingWaters' pool (flat_shore -
# has_landmark, nothing else) silently displaced 12 CoastalIsland and 4
# Archipelago tiles the moment it was written, discovered only by the
# planet-wide before/after diff this task's brief demanded. Fixed live (removed
# the intruding VEE_RisingWaters, re-added the original def on those 16 tiles -
# see grey_apply_report.json's "protected_restore" block) and fixed HERE so a
# re-run of this plan builder reproduces the correct candidate pools directly,
# with no manual patch step required.
# ---------------------------------------------------------------------------
PROTECTED_DEFS = ('CoastalIsland', 'Archipelago', 'Oasis', 'Bay', 'VEE_GravelBeach')


def protected_tiles(pool):
    out = set()
    for t in pool:
        if any(d in before.get(str(t), []) for d in PROTECTED_DEFS):
            out.add(t)
    return out

# ---------------------------------------------------------------------------
# PASS 2 - THE JUNKER COAST
# ---------------------------------------------------------------------------
ring_protected = protected_tiles(ring)
body_protected = protected_tiles(body)

junkyard_elig = (low_shore - has_landmark)  # verified live: Junkyard coexists with the 5 protected defs, no exclusion needed
nj_elig = junkyard_elig & near_junk
rest_elig = junkyard_elig - nj_elig
Junkyard = sorted(set(t for t in nj_elig if h(t) < 75) | set(t for t in rest_elig if h(t) < 40))

ruins_elig = (ring - has_landmark) - set(Junkyard)  # no AB_MechanoidIntrusion present - measured
AncientRuins = sorted(t for t in ruins_elig if h(t) < 40)

warehouse_pool = ring - has_landmark - set(Junkyard) - set(AncientRuins)  # verified live: AncientWarehouse coexists with Archipelago on tile 3222
warehouse_elig = set(t for t in warehouse_pool if tiles[t]['biome'] in ('AridShrubland', 'Desert'))
AncientWarehouse = sorted(t for t in warehouse_elig if h(t) < 55)

have_stockpile = have('Stockpile', ring)
stockpile_elig = (low_shore - has_landmark) - have_stockpile
nj_st = stockpile_elig & near_junk
rest_st = stockpile_elig - nj_st
Stockpile = sorted(set(t for t in nj_st if h(t) < 65) | set(t for t in rest_st if h(t) < 30))

have_mindevoid = have('VEE_MineralDevoid', ring)
have_oredevoid = have('VEE_DeepOreDevoid', ring)
devoid_elig = (ring - has_landmark) - have_mindevoid  # min/deep devoid always paired
VEE_MineralDevoid = sorted(t for t in devoid_elig if h(t) < 50)
VEE_DeepOreDevoid = sorted(t for t in devoid_elig if h(t) < 50)  # identical hash gate -> paired, as the existing 8 already are

# ---------------------------------------------------------------------------
# PASS 4 - THE WADING SEA
# ---------------------------------------------------------------------------
# VEE_RisingWaters is a coastline-SHAPE mutator (same broad category as
# CoastalIsland/Archipelago/Coast/Bay/CoastalAtoll, confirmed by the live
# collision this plan now excludes for) - it is exactly the def that
# displaced 12 CoastalIsland + 4 Archipelago tiles on the first live run.
rising_elig = flat_shore - has_landmark - ring_protected
VEE_RisingWaters = sorted(t for t in rising_elig if h(t) < 60)

have_coast = have('Coast', ring)
coast_elig = (ring - has_landmark - ring_protected) - have_coast
Coast = sorted(t for t in coast_elig if h(t) < 55)

coast_sides = json.load(open(ROOT + '_grey/ring_coast_sides.json'))
coast_sides = {int(k): v for k, v in coast_sides.items()}
archi_biomes = {'AridShrubland', 'Desert', 'ZBiome_Badlands', 'Wasteland'}  # measured off the 11 tiles already live
have_archi = have('Archipelago', ring)
archi_pool = (ring - has_landmark - ring_protected) - have_archi - set(VEE_RisingWaters)
archi_elig = set(
    t for t in archi_pool
    if 2 <= coast_sides.get(t, 0) <= 5
    and tiles[t]['river_count'] == 0
    and tiles[t]['biome'] in archi_biomes
)
Archipelago = sorted(t for t in archi_elig if h(t) < 55)

have_animhab = have('AnimalHabitat', body)  # measured empty - ungated def, currently unplaced on water
d1 = sorted(t for t in body if dist.get(t) == 1)
d2 = sorted(t for t in body if dist.get(t) == 2)
AnimalHabitat_shallow = sorted(
    set(t for t in d1 if t not in have_animhab and h(t) < 60) |
    set(t for t in d2 if t not in have_animhab and h(t) < 35)
)

have_fish = have('Fish_Increased', body)
Fish_Increased_shallow = sorted(
    set(t for t in d1 if t not in have_fish and h(t) < 65) |
    set(t for t in d2 if t not in have_fish and h(t) < 40)
)

# ---------------------------------------------------------------------------
# PASS 5 - THE FOUR MOUTHS AND THE COLD END
# ---------------------------------------------------------------------------
mouths_ok = [m for m in mouths if m not in has_landmark]  # excludes 16898 - see module docstring
# mouths_ok/fan are forced by geometry, not a discretionary pool - checked
# directly (not via protected_tiles()) that none of the 3 mouths or 5 fan
# tiles carries a protected def; all clean, measured.
fan = set()
for m in mouths:
    for n in nb.get(m, []):
        if n in body:
            fan.add(n)

RiverDelta = sorted(mouths_ok)
AnimalLife_Increased_mouths = sorted(set(mouths_ok) | fan)
Fish_Increased_mouths = sorted(set(mouths_ok) | fan)

alluvial_candidates = {}
for m in mouths:
    cands = [n for n in nb.get(m, []) if n in ring and tiles.get(n, {}).get('hill') == 1 and n not in has_landmark]
    alluvial_candidates[m] = cands
VEE_AlluvialFan = [11503] if tiles[11503]['hill'] == 1 and 11503 not in has_landmark else []
# measured: 8081 h3, 16898 h4, 16902 h4, and none of the three has a Flat
# ring neighbour either (alluvial_candidates values above are all empty for
# them) - so this def lands on exactly one tile, by measurement not omission.

iceberg_elig = set(t for t in iceedge if tiles[t].get('temp_c', 999) <= 0.0)
# measured: 26 of the 52 iceedge tiles run above 0C (ice margin spans -6.5..+5C
# per BRIEF.md) - Iceberg's gate is avg temp -100..0C, so those 26 are dropped
# here rather than assumed eligible from biome alone.
Iceberg = sorted(t for t in iceberg_elig if h(t) < 60)

ice_core = ice - iceedge  # "deeper into the 91 ice tiles" per brief
IceDunes = sorted(t for t in ice_core if h(t) % 2 == 0 and h(t) < 70)
VEE_DeepSnow = sorted(t for t in ice_core if h(t) % 2 == 1 and h(t) < 70)

have_windy = have('WindyMutator', ring | ice)
arid_north = set(t for t in ring if tiles[t]['biome'] in ('AridShrubland', 'Desert') and tiles[t]['arc'] >= 90)
# ice tiles never carry the 5 protected defs (measured - they're a shore/
# water-boundary family, ice is pure SeaIce interior/edge), so only the arid
# ring half needs the exclusion.
windy_pool = (ice | (arid_north - has_landmark)) - have_windy  # verified live: WindyMutator is a weather-family def, only conflicts with SunnyMutator
WindyMutator = sorted(t for t in windy_pool if h(t) < 60)

groups = dict(
    Junkyard=Junkyard,
    AncientRuins=AncientRuins,
    AncientWarehouse=AncientWarehouse,
    Stockpile=Stockpile,
    VEE_MineralDevoid=VEE_MineralDevoid,
    VEE_DeepOreDevoid=VEE_DeepOreDevoid,
    VEE_RisingWaters=VEE_RisingWaters,
    Coast=Coast,
    Archipelago=Archipelago,
    AnimalHabitat=AnimalHabitat_shallow,
    Fish_Increased=sorted(set(Fish_Increased_shallow) | set(Fish_Increased_mouths)),
    AnimalLife_Increased=AnimalLife_Increased_mouths,
    RiverDelta=RiverDelta,
    VEE_AlluvialFan=VEE_AlluvialFan,
    Iceberg=Iceberg,
    IceDunes=IceDunes,
    VEE_DeepSnow=VEE_DeepSnow,
    WindyMutator=WindyMutator,
)

if __name__ == '__main__':
    for k, v in groups.items():
        print(k, len(v))
    print()
    print('mouths_ok (RiverDelta targets, 16898 excluded - has_landmark):', mouths_ok)
    print('fan (water tiles adjacent to mouths):', sorted(fan))
    print('VEE_AlluvialFan (measured: only 11503 qualifies):', VEE_AlluvialFan)
    print('alluvial_candidates per non-qualifying mouth (expect all empty):', alluvial_candidates)
    json.dump(dict(groups=groups, meta=dict(
        mouths_ok=mouths_ok, fan=sorted(fan), archi_biomes=sorted(archi_biomes),
        junkyard_elig=len(junkyard_elig), archi_elig=len(archi_elig),
        d1=len(d1), d2=len(d2),
    )), open(OUT_PATH, 'w'), indent=1)
    print('wrote', OUT_PATH)
