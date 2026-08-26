"""
Build the deterministic tile-list plan for the Twilight Sea's five mutator
passes (ICE MARGIN, DAY/NIGHT SHORE, SEA FOG, DROWNED COAST, SHIPPING LANE)
from the pre-computed geometry in twilight_geom.json / twilight_ice.json,
the live mutator/landmark snapshot in _muts_now.json, and the live mutator
roster's gate notes in _organic/_mutator_roster.json.

Analysis-only: reads local files, never touches the bridge. Run under python3
with /mnt/d/... paths, mirroring world/_scald/plan_scald_mutators.py which
this is modelled on almost line for line.

⛔ NO RNG. Every subset choice is h(t) = (t * 2654435761) % 100, a pure
function of the tile id, so the same plan comes out every run and nothing
here could roll a second planet.

Traps hit while building this:
  - VEE_SaltPlains's roster note reads "landlocked (0 coast sides required)",
    which looks like it forbids the coast -- but 19 already sit on isCoastal
    ring tiles today with world_mutators_audit offenderCount 0. The default
    audit's marine check only covers whatever `marineMutators` names (default
    just "Coast"), so that gate has never actually been exercised against
    VEE_SaltPlains. BRIEF.md's own GATES table omits the coastal clause for
    this def, so this plan follows BRIEF and does not filter on it -- then
    the apply script explicitly folds VEE_SaltPlains into `marineMutators` on
    the final audit, so if the game DOES enforce it, offenders show up and get
    removed rather than silently landing wrong.
  - Coast-side COUNT gates (Iceberg 3-5, CoastalAtoll 3-5, VEE_LoneIsland 3-5,
    Archipelago 2-5, Bay 1-5, VEE_GravelBeach 1-6, VEE_RisingWaters 1-5,
    VEE_MarineSanctuary 1-5, VEE_RelictDelta 1-6) have no exposed "coastSides"
    scalar anywhere the bridge or the CSVs give us (jawa/world_tile_get itself
    errors -- see apply script header). Read the ENGINE'S OWN check instead:
    `TileMutatorDef.IsValidTile` (RimWorld source, via the rimsage MCP) counts
    a neighbour ONLY if its PrimaryBiome is exactly Ocean or Lake -- SeaIce
    does NOT count, even though SeaIce is part of this sea's body. `coast_count()`
    below reproduces that exactly using now_tiles.csv's biome column (which
    covers all 21,872 tiles, so no proxy is needed at all -- this is exact,
    not approximate). Getting this wrong the other way (counting SeaIce as
    coastal) would have put Iceberg and the drowned-coast defs on the wrong
    side of the sea entirely, since dayside borders open Ocean and nightside
    mostly borders SeaIce -- and it would have made every "requires 3-5"
    population look far larger than it really is (checked: over the ring,
    coast_count of 3+ against real Ocean neighbours only is rare, most shore
    tiles measure 0-2).
  - `TileMutatorDef.IsValidTile` also proves `jawa/world_mutators_set`
    (Tile.AddMutator) bypasses ALL of this validation -- it is generation-time
    code, never called by the setter. That is BRIEF's "the setter does not
    enforce gates" made concrete: the C# proves it, not just the doc.
  - Nightside ring biome is NOT Tundra/IceSheet/SeaIce anywhere -- measured
    over all 122 nightside ring tiles, it is AridShrubland/AB_RockyCrags/
    AB_MycoticJungle/Desert/ZBiome_Badlands/AB_TarPits/PoisonForest. This
    planet's biome assignment is coarser than the per-tile temperature field,
    so IceDunes, VEE_DeepSnow and DryGround (all biome-locked to cold/boreal
    biomes BRIEF's prose implies for the night shore) have a real, measured
    ZERO eligible ring tiles -- not a bug in this plan, the same kind of
    honest empty world/_scald/plan_scald_mutators.py hit with VEE_AlluvialFan.
    WindyMutator still works there (its whitelist includes AridShrubland/
    Desert/Tundra/IceSheet/SeaIce, and the ring's actual biomes qualify).
  - VEE_RelictDelta "where a dry channel would reach it": every ring tile
    within 3 hops of the one real river mouth (18267) is AB_MiasmicMangrove
    or Wasteland, neither in VEE_RelictDelta's biome whitelist -- also a
    measured empty, not widened past the mouth's real neighbourhood, because
    doing so would misrepresent "where a dry channel would reach it".
  - The 28 CoastalIsland/Archipelago landmark tiles placed earlier today are
    excluded from EVERY pass here, not just pass 4 where BRIEF calls it out --
    simplest correct interpretation of "do not stack new work on those tiles".
    Only 18 of the 28 sit inside this sea's body|ring; the rest are elsewhere
    on the planet and never enter these candidate pools regardless.
  - "islands" in pass 5 ("AncientRuins / AncientWarehouse on islands as old
    harbour works") cannot literally mean the 28 excluded landmark tiles.
    Read instead as the same high-coast-count ring tiles pass 4 uses for
    CoastalAtoll / VEE_LoneIsland ("former seabed") -- island-like shore
    without being an actual CoastalIsland/Archipelago landmark tile.
  - Fixed-percentage hash cutoffs (h(t) < 60) work fine on large pools but
    can accidentally zero out or nearly-empty a SMALL gated-down pool just by
    which raw hash values happen to land in it (measured: VEE_LoneIsland's
    real candidate pool was 11 tiles and h(t)<60 kept literally none of them
    -- every one of the 11 happened to hash 70+). `pick()` below sorts by hash
    and takes a target fraction of whatever pool it is given, so "roughly
    half to two-thirds" holds at any pool size instead of being a coin flip
    on small ones.
"""
import json, csv, math

ROOT = '/mnt/d/Luke/dev/Rimworld/world/'
OUT_PATH = ROOT + '_twilight/twilight_plan.json'

geom = json.load(open(ROOT + '_roads/twilight_geom.json'))
body = set(geom['body'])
ring = set(geom['ring'])
dist = {int(k): v for k, v in geom['dist'].items()}
mouths = geom['mouths']

ice_geom = json.load(open(ROOT + '_roads/twilight_ice.json'))
ocean = set(ice_geom['ocean'])
ice = set(ice_geom['ice'])
edge = set(ice_geom['edge'])          # open water touching ice (39)
iceedge = set(ice_geom['iceedge'])    # ice touching open water (54)

tiles = {}
for r in csv.DictReader(open(ROOT + '_roads/now_tiles.csv')):
    t = int(r['tile'])
    tiles[t] = dict(biome=r['biome'], hill=int(r['hilliness']), arc=float(r['arc']),
                     temp=float(r['temp_c']), river_count=int(r['river_count']))

nb = {}
for r in csv.DictReader(open(ROOT + 'world_neighbors_sub7b.csv')):
    t = int(r['tile'])
    nb[t] = [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]

muts_now = {}
landmark_now = {}
for chunk in json.load(open(ROOT + '_roads/_muts_now.json')):
    for row in chunk['tiles']:
        muts_now[row['tile']] = set(m['def'] for m in row['mutators'] if m['def'])
        landmark_now[row['tile']] = row.get('landmark')

h = lambda t: (t * 2654435761) % 100


def pick(candidates, frac=0.6):
    """Deterministic ~frac subset: sort by hash, take the first frac of the
    pool. Robust at any pool size -- unlike a fixed h(t)<N cutoff, which can
    accidentally empty a small pool (see header)."""
    cs = sorted(candidates, key=h)
    n = max(1, math.ceil(len(cs) * frac)) if cs else 0
    return sorted(cs[:n])


def has_river_mut(t):
    ms = muts_now.get(t, set())
    return 'River' in ms or 'RiverDelta' in ms


def coast_count(t):
    """Exact match for TileMutatorDef.IsValidTile's coastSidesRange check:
    a neighbour counts only if its PrimaryBiome is Ocean or Lake -- SeaIce
    does NOT count, confirmed by reading the engine source directly."""
    return sum(1 for n in nb.get(t, []) if tiles.get(n, {}).get('biome') in ('Ocean', 'Lake'))


# ---- global exclusion: the 28 CoastalIsland/Archipelago landmark tiles ----
excluded_landmark_tiles = sorted(
    t for t in (body | ring)
    if landmark_now.get(t) in ('CoastalIsland', 'Archipelago')
)

dayside_ring = sorted(t for t in ring if tiles[t]['arc'] < 90)
nightside_ring = sorted(t for t in ring if tiles[t]['arc'] >= 90)
dayside_ring_free = [t for t in dayside_ring if t not in excluded_landmark_tiles]
nightside_ring_free = [t for t in nightside_ring if t not in excluded_landmark_tiles]

# =====================================================================
# PASS 1 -- THE ICE MARGIN
# =====================================================================

# Iceberg: iceedge tiles (ice touching open water), avg temp -100..0C,
# biome SeaIce (measured: all 54 iceedge tiles already are), needs no
# river, coast_count 3-5 (engine-exact).
iceberg_candidates = [
    t for t in sorted(iceedge)
    if tiles[t]['biome'] == 'SeaIce'
    and -100 <= tiles[t]['temp'] <= 0
    and not has_river_mut(t)
    and 3 <= coast_count(t) <= 5
]
iceberg = pick(iceberg_candidates, 0.6)

# Fish_Increased + AnimalLife_Increased: the 39 open-water edge tiles,
# ungated, minus any tile already carrying Fish_Decreased (category
# conflict).
edge_free = [t for t in sorted(edge) if 'Fish_Decreased' not in muts_now.get(t, set())]
edge_fish = pick(edge_free, 0.6)
edge_animal = pick(edge_free, 0.6)

# VEE_GravelBeach where the ice grounds ashore: ice tiles at shore
# distance 1 (directly touching the ring), coast_count 1-6. Measured:
# most dist==1 ice tiles border ONLY land/other ice, not Ocean biome
# itself, so the coast_count filter is NOT a no-op here -- 72 of 105
# read coast_count==0 and are correctly excluded.
ice_ashore_candidates = [t for t in ice if dist.get(t) == 1 and 1 <= coast_count(t) <= 6]
gravel_ice_margin = pick(ice_ashore_candidates, 0.6)

# =====================================================================
# PASS 2 -- THE DAY SHORE AND THE NIGHT SHORE
# =====================================================================

SALT_BIOMES = {'Desert', 'ExtremeDesert', 'Tundra', 'AridShrubland', 'Grasslands'}
OASIS_BIOMES = {'Desert', 'ExtremeDesert', 'Savanna'}
DRYGROUND_BIOMES = {'Scarlands', 'BorealForest', 'Tundra'}
ICEDUNES_BIOMES = {'SeaIce', 'IceSheet'}
DEEPSNOW_BIOMES = {'IceSheet', 'SeaIce', 'Tundra'}
WINDY_BIOMES = {'AridShrubland', 'Desert', 'ExtremeDesert', 'IceSheet', 'SeaIce', 'Tundra'}

day_salt_candidates = [
    t for t in dayside_ring_free
    if tiles[t]['biome'] in SALT_BIOMES and not has_river_mut(t)
]
day_salt = pick(day_salt_candidates, 0.65)

day_dryground_candidates = [t for t in dayside_ring_free if tiles[t]['biome'] in DRYGROUND_BIOMES]
day_dryground = pick(day_dryground_candidates, 0.6)   # measured empty -- see header

day_oasis_candidates = [
    t for t in dayside_ring_free
    if tiles[t]['biome'] in OASIS_BIOMES and 20 <= tiles[t]['temp'] <= 60
    and not has_river_mut(t)
]
day_oasis = pick(day_oasis_candidates, 0.6)

day_sunny = pick(dayside_ring_free, 0.55)

night_icedunes_candidates = [
    t for t in nightside_ring_free
    if tiles[t]['biome'] in ICEDUNES_BIOMES and tiles[t]['hill'] == 1
]
night_icedunes = pick(night_icedunes_candidates, 0.6)   # measured empty -- see header

night_deepsnow_candidates = [
    t for t in nightside_ring_free
    if tiles[t]['biome'] in DEEPSNOW_BIOMES and -100 <= tiles[t]['temp'] <= 5
]
night_deepsnow = pick(night_deepsnow_candidates, 0.6)   # measured empty -- see header

night_windy_candidates = [t for t in nightside_ring_free if tiles[t]['biome'] in WINDY_BIOMES]
night_windy = pick(night_windy_candidates, 0.55)

# =====================================================================
# PASS 3 -- THE SEA FOG (conditional on the live probe -- see apply script)
# =====================================================================

fog_probe_tiles = sorted(ocean, key=h)[:2]

# Fallback if FoggyMutator is refused on Ocean: WindyMutator on the SeaIce
# band (distinct pool from pass 1's Iceberg/GravelBeach tiles, so the two
# families read as separate features) and the arid dayside shores
# (disjoint from night_windy, which only ever touches nightside_ring).
windy_seaice_band_candidates = [t for t in sorted(ice) if tiles[t]['biome'] in WINDY_BIOMES]
windy_seaice_band = pick(windy_seaice_band_candidates, 0.55)

windy_arid_shore_candidates = [
    t for t in dayside_ring_free if tiles[t]['biome'] in {'AridShrubland', 'Desert', 'ExtremeDesert'}
]
windy_arid_shore = pick(windy_arid_shore_candidates, 0.55)

# =====================================================================
# PASS 4 -- THE DROWNED COAST
# =====================================================================

RELICTDELTA_BIOMES = {'Desert', 'ExtremeDesert', 'AridShrubland', 'Grasslands', 'TemperateForest'}
COASTALATOLL_BIOMES = {'AridShrubland', 'Desert', 'Grasslands', 'TemperateForest', 'TropicalRainforest'}
LONEISLAND_BIOMES = {'AridShrubland', 'BorealForest', 'ColdBog', 'Desert', 'ExtremeDesert', 'GlacialPlain'}

flat_ring = [t for t in (dayside_ring_free + nightside_ring_free) if tiles[t]['hill'] == 1]
rising_waters_candidates = [t for t in flat_ring if 1 <= coast_count(t) <= 5]
rising_waters = pick(rising_waters_candidates, 0.6)

# expand SaltPlains/DryGround coverage beyond pass 2's subset ("more" per
# BRIEF), same gates, wider fraction, still leaving real gaps.
day_salt_more = pick(day_salt_candidates, 0.8)
night_dryground_more_candidates = [
    t for t in nightside_ring_free if tiles[t]['biome'] in DRYGROUND_BIOMES
]
night_dryground_more = pick(night_dryground_more_candidates, 0.75)   # measured empty -- see header

# VEE_RelictDelta "where a dry channel would reach it": ring tiles within
# 3 graph-hops of the one real river mouth (18267, Blackstar Field),
# matching its own gate. Measured empty -- see header.
mouth = mouths[0]
near_mouth = {mouth}
frontier = {mouth}
for _ in range(3):
    nxt = set()
    for t in frontier:
        nxt |= set(nb.get(t, []))
    frontier = nxt - near_mouth
    near_mouth |= frontier
relictdelta_candidates = [
    t for t in sorted(ring & near_mouth)
    if t not in excluded_landmark_tiles
    and tiles[t]['biome'] in RELICTDELTA_BIOMES
    and tiles[t]['hill'] == 1
    and 1 <= coast_count(t) <= 6
]
relictdelta = pick(relictdelta_candidates, 0.7)

# "former seabed" chain: high-coast-count ring tiles (island-like shore),
# excluding the 28 landmark tiles. CoastalAtoll picked first (its gate is
# the tighter one -- max hilliness SmallHills, needs no river); LoneIsland
# then takes what CoastalAtoll left, since their biome lists overlap.
seabed_ring = dayside_ring_free + nightside_ring_free
atoll_candidates = [
    t for t in seabed_ring
    if tiles[t]['biome'] in COASTALATOLL_BIOMES and tiles[t]['hill'] <= 2
    and not has_river_mut(t) and 3 <= coast_count(t) <= 5
]
coastal_atoll = pick(atoll_candidates, 0.6)

loneisland_candidates = [
    t for t in seabed_ring
    if tiles[t]['biome'] in LONEISLAND_BIOMES and 3 <= coast_count(t) <= 5
    and t not in coastal_atoll
]
lone_island = pick(loneisland_candidates, 0.7)

former_seabed = sorted(set(coastal_atoll) | set(lone_island))

# =====================================================================
# PASS 5 -- THE SHIPPING LANE
# =====================================================================

SETTLEMENTS = {
    'Blackstar Field': 18267, 'Hardpan Yard': 7497,
    'Deepwater Hold': 9451, 'Boilquay': 17209,
    "Rulla the Deep's Palace": 15076, 'Seabarter': 13409,
    'Aquifer Station': 15051, 'Specimen Hall': 12082,
}


def sea_tiles_near(center, hops, pool):
    seen = {center}
    frontier = {center}
    for _ in range(hops):
        nxt = set()
        for t in frontier:
            nxt |= set(nb.get(t, []))
        frontier = (nxt - seen) & pool
        seen |= frontier
    return seen & pool


compact_sea = sea_tiles_near(SETTLEMENTS['Boilquay'], 4, body) | sea_tiles_near(SETTLEMENTS['Deepwater Hold'], 4, body)
compact_sea -= set(edge_fish) | set(edge_animal)  # keep pass-1's ice-margin fisheries visually distinct
lane_fish = pick(compact_sea, 0.6)
lane_marine_candidates = [t for t in compact_sea if 1 <= coast_count(t) <= 5]
lane_marine = pick(lane_marine_candidates, 0.55)

# AncientRuins / AncientWarehouse "on islands": the former-seabed chain
# from pass 4, split so the two flavours do not both land on one tile.
ANCIENTWAREHOUSE_BIOMES = {'AridShrubland', 'BorealForest', 'ColdBog', 'Desert', 'ExtremeDesert'}
ruins_pool = former_seabed
ancient_ruins = pick(ruins_pool, 0.4)  # ungated except AB_MechanoidIntrusion
ancient_warehouse_candidates = [
    t for t in ruins_pool if tiles[t]['biome'] in ANCIENTWAREHOUSE_BIOMES and t not in ancient_ruins
]
ancient_warehouse = pick(ancient_warehouse_candidates, 0.6)

blackstar_sea = sea_tiles_near(SETTLEMENTS['Blackstar Field'], 5, ring | body) | \
    sea_tiles_near(SETTLEMENTS['Hardpan Yard'], 5, ring | body)
BAY_BIOMES = {'AridShrubland', 'BorealForest', 'ColdBog', 'Desert', 'ExtremeDesert'}
bay_candidates = [
    t for t in (blackstar_sea & ring)
    if t not in excluded_landmark_tiles
    and tiles[t]['biome'] in BAY_BIOMES and 1 <= coast_count(t) <= 5
]
bay_chain = pick(bay_candidates, 0.65)

# =====================================================================

groups = dict(
    Iceberg=iceberg,
    Fish_Increased=sorted(set(edge_fish) | set(lane_fish)),
    AnimalLife_Increased=edge_animal,
    VEE_GravelBeach=gravel_ice_margin,
    VEE_SaltPlains=sorted(set(day_salt) | set(day_salt_more)),
    DryGround=sorted(set(day_dryground) | set(night_dryground_more)),
    Oasis=day_oasis,
    SunnyMutator=day_sunny,
    IceDunes=night_icedunes,
    VEE_DeepSnow=night_deepsnow,
    WindyMutator=sorted(set(night_windy) | set(windy_seaice_band) | set(windy_arid_shore)),
    VEE_RisingWaters=rising_waters,
    VEE_RelictDelta=relictdelta,
    CoastalAtoll=coastal_atoll,
    VEE_LoneIsland=lone_island,
    VEE_MarineSanctuary=lane_marine,
    AncientRuins=ancient_ruins,
    AncientWarehouse=ancient_warehouse,
    Bay=bay_chain,
)

# candidate-pool sizes, so "0 landed" can be told apart from "0 eligible"
candidate_pool_sizes = dict(
    Iceberg=len(iceberg_candidates), VEE_GravelBeach=len(ice_ashore_candidates),
    VEE_SaltPlains=len(day_salt_candidates), DryGround=len(day_dryground_candidates) + len(night_dryground_more_candidates),
    Oasis=len(day_oasis_candidates), IceDunes=len(night_icedunes_candidates),
    VEE_DeepSnow=len(night_deepsnow_candidates), VEE_RisingWaters=len(rising_waters_candidates),
    VEE_RelictDelta=len(relictdelta_candidates), CoastalAtoll=len(atoll_candidates),
    VEE_LoneIsland=len(loneisland_candidates), VEE_MarineSanctuary=len(lane_marine_candidates),
    AncientWarehouse=len(ancient_warehouse_candidates), Bay=len(bay_candidates),
)

meta = dict(
    excluded_landmark_tiles=excluded_landmark_tiles,
    fog_probe_tiles=fog_probe_tiles,
    windy_fallback=dict(seaice_band=windy_seaice_band, arid_shore=windy_arid_shore),
    dayside_ring=dayside_ring, nightside_ring=nightside_ring,
    settlements=SETTLEMENTS,
    former_seabed=former_seabed,
    candidate_pool_sizes=candidate_pool_sizes,
)

if __name__ == '__main__':
    for k, v in groups.items():
        print(k, len(v), '/ pool', candidate_pool_sizes.get(k, '-'))
    print('excluded landmark tiles:', len(excluded_landmark_tiles))
    print('fog probe tiles:', fog_probe_tiles)
    json.dump(dict(groups=groups, meta=meta), open(OUT_PATH, 'w'), indent=1)
    print('wrote', OUT_PATH)
