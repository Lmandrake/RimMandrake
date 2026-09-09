#!/usr/bin/env python3
"""Ash'karr's flora, ASSIGNED rather than inherited — one signature roster per biome.

🔴 **OWNER, 2026-08-23, verbatim:** *"I thought you had distributed the plants per biome for
me? If not, PLEASE do that right now. You, agent Decide, make those calls right now and do it…
Try to avoid using the same plant across different biome types. It's ok to draw from Tinctora,
Healroot, and other normally player-grown plants as you decorate the biomes."*
Plus, minutes later: *"We can set the appropriate temperatures later, don't worry about that as
a constraint"* ⇒ climate tolerance is `NORMALIZE_TEMPERATURE_TOLERANCES_1`, not a filter here.
**Assignment is by LOOK and LORE.**

🔴 **THE SOURCE MOVED, 2026-09-09.** `FAMILIES` is no longer authored here — it is written
from `design/Jawa/worldbuilding/biomes/rosters/*.json` (`flora` / `flora_purged`), which
BIOME_FAUNA_ASSIGNMENT_SITTING_1 landed on the owner's cards. A plant is in a biome because
that biome's sheet law admitted it; the roster row carries the argument. ⛔ Edit the ROSTER
and re-derive, never this dict — `--check` fails the build if the two disagree.

🔑 **The rule that shapes every list below: no plant appears in two FAMILIES.** Inside one
family a shared plant is deliberate kinship; across two it is the zoo effect the owner
objected to, and `--check` fails the build. The families are therefore no longer narrative
categories: they are the connected components of "shares a plant with", computed from the
rosters, which is the only grouping that can satisfy the rule without editing the design.
Five of them, where there used to be eight.

🔴 **`wildPlants` IS a `LoadDataFromXmlCustom` field and `<li>` DESTROYS THE DEF.** Read from
source, not assumed — `BiomePlantRecord.LoadDataFromXmlCustom` takes the **node NAME** as the
plant defName and the node's **value** as the commonality:

    <wildPlants>
      <Plant_TreeDrago>0.08</Plant_TreeDrago>     ✅
      <li><plant>Plant_TreeDrago</plant>…</li>    ⛔ discards the WHOLE BiomeDef, silently
    </wildPlants>

That is the same trap that cost 26 BiomeDefs and 101 CharacterDefs on 2026-08-23.

⛔ **FOUR PLANTS ARE CUT AND MUST NEVER APPEAR IN ANY ROSTER BELOW:**
`Plant_TreePine` · `Plant_TreeBirch` · `Plant_TreePoplar` · `RG_Plant_Raspberry`.
The owner cut them with Cherry Picker (`design/Jawa/mods/plant_decisions.json`, decision
`cut`), which DELETES the ThingDef at load. A BiomeDef that still names one throws
`Could not resolve cross-reference` — a red error on every load. Adding one back is a
defect, not a preference; `--check` cannot catch it because the def dump predates the cut.

    python3 design/Jawa/mods/biome_flora.py --check     # families, overlaps, defNames resolve
    python3 design/Jawa/mods/biome_flora.py --write     # emit the patch
    python3 design/Jawa/mods/biome_flora.py --doc       # regenerate the readable roster doc

⭐ `--doc` used to be a throwaway script that was written, run once and deleted, so the doc
went stale the moment anyone edited `FAMILIES`. It lives here now: one file owns the rosters,
the patch and the prose about them.
"""
import argparse, collections, csv, glob, json, os, sqlite3, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
from game_paths import DUMP_ROOT  # noqa: E402
DB = os.path.join(DUMP_ROOT, "defs.sqlite")
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
# ⚠️ This used to point at src/Jawa/Jawa_Patches/, which JAWA_PATCHES_SPLIT_1 retired.
# The deployed file has been under RimUtinni since that split; `--write` was silently
# creating a fresh dead directory instead of updating anything. Corrected 2026-09-09.
PATCH = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches',
                     'BiomeFlora_Ashkarr.xml')
ROSTERS = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biomes', 'rosters')
POOL = os.path.join(HERE, 'plant_pool.csv')
DOC = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biome_flora_rosters.md')

# ---------------------------------------------------------------- the design
# family -> biome -> {plant defName: commonality}
# Commonality scale, held consistent so one biome does not out-shout another:
#   2.0+  the ground cover you always see      0.5-1.0  the mid layer you notice
#   0.2-0.5  punctuation                       <0.2     trees and set pieces
FAMILIES = {
 'A. dayside desert, badlands and the river jungles': {
  'Desert': {   # 3,932 tiles · 5 plants
    'AB_HardyGrass': 0.6, 'Plant_Chakroot_Wild': 0.3, 'Plant_HubbaGourd_Wild': 0.2,
    'AB_Aaklac': 0.12, 'AB_DessertTree': 0.06},
  'AB_PropaneLakes': {   # 2,531 tiles · 4 plants
    'AB_CrystalHorn': 1.0, 'AB_CrystalFlower': 0.8, 'AB_FrostLeaf': 0.6,
    'AB_RimeNodules': 0.4},
  'ZBiome_Badlands': {   # 985 tiles · 6 plants
    'AB_HardyGrass': 1.0, 'GRimMoss': 0.8, 'BMT_Plant_TwistingThorngrass': 0.5,
    'BMT_Plant_TwistingThornweed': 0.4, 'BMT_Plant_TreeTwistingThornwood': 0.2,
    'AB_GargantuanLithops': 0.15},
  'PoisonForest': {   # 557 tiles · 9 plants
    'BMT_Plant_TreeTwistingThornwood': 0.6, 'AB_CrystalFlower': 0.5,
    'BMT_Plant_TreeMartyr': 0.5, 'AB_BloodBouquet': 0.4, 'AB_CrystalHorn': 0.4,
    'AB_RavenNettle': 0.4, 'AB_GiantAgariTox': 0.3, 'AB_RedBugloss': 0.3,
    'AB_KeeningCordax': 0.2},
  'BiomeCypreJungle': {   # 235 tiles · 11 plants
    'AB_JungleTree': 3.0, 'Plant_HydenockTree_Wild': 1.5, 'Plant_JoganTree_Wild': 1.2,
    'BMT_GiantLeaf': 1.0, 'Plant_MujaFruit_Wild': 1.0, 'Plant_HubbaGourd_Wild': 0.8,
    'AB_SugarFamewort': 0.6, 'Plant_FelucianGlowspore_Wild': 0.6,
    'Plant_Bubblespore_Wild': 0.5, 'Plant_Chakroot_Wild': 0.5, 'Plant_TookeTrap_Wild': 0.5},
  'ZBiome_Grasslands': {   # 222 tiles · 3 plants
    'Plant_YellowGrass': 2.4, 'Plant_YellowTallGrass': 2.0, 'AB_HardyGrass': 0.4},
  'AB_OcularForest': {   # 179 tiles · 10 plants
    'AB_AlienGrass': 1.0, 'AB_AlienTree': 1.0, 'AB_EyeGrass': 0.6, 'AB_RedLeaves': 0.6,
    'AB_HalfAlienTree': 0.5, 'AB_RedPlantsTall': 0.5, 'AB_GlobularPlant': 0.4,
    'AB_TentacularPlant': 0.4, 'AB_BloodBouquet': 0.3, 'AB_AlienTree_Polluted': 0.15},
  'AB_FeraliskInfestedJungle': {   # 161 tiles · 7 plants
    'AB_JungleTree': 1.1, 'RG_Plant_TropicalChokevine': 1.0, 'AB_TangleTea': 0.4,
    'Plant_TookeTrap_Wild': 0.3, 'AB_Gomphoeria': 0.15, 'AB_RedBugloss': 0.07,
    'AB_Aaklac': 0.05},
  'RUT_PropaneLake': {   # 57 tiles · 4 plants
    'AB_CrystalHorn': 1.0, 'AB_CrystalFlower': 0.8, 'AB_FrostLeaf': 0.6,
    'AB_RimeNodules': 0.4},
  'COMIGO_GreaterSwamp_Tropical': {   # 43 tiles · 7 plants
    'Plant_HydenockTree_Wild': 1.5, 'AB_KeeningCordax': 1.2, 'BMT_GiantLeaf': 0.8,
    'Plant_JoganTree_Wild': 0.6, 'AB_Iashiphus': 0.5, 'AB_Gomphoeria': 0.4,
    'Plant_Chakroot_Wild': 0.4},
 },

 'B. the mycoid and fire massif': {
  'ExtremeDesert': {   # 3,172 tiles · 2 plants
    'Plant_Bloddle': 0.05, 'AB_GiantStikehr': 0.04},
  'AB_MycoticJungle': {   # 2,258 tiles · 32 plants
    'AB_Bryolux': 10, 'AB_Glowstool': 3, 'AB_Agarilux': 2, 'AB_GiantAgarilux': 2,
    'AB_GlowingAgarilux': 1, 'AB_LilacBeacon': 0.5, 'AB_WitchesOyster': 0.5,
    'BMT_Dewshrooms': 0.5, 'BMT_FruitingBodies': 0.5, 'BMT_Nuitae': 0.5,
    'BMT_Wrinklecap': 0.5, 'BMT_Arpeau': 0.4, 'BMT_Nogtyl': 0.4,
    'AB_RecurvedStropharia': 0.3, 'BMT_FlakespireFungus': 0.3, 'BMT_Pusmelon': 0.3,
    'BMT_RustPuff': 0.3, 'BMT_Sagecrust': 0.3, 'AB_ArbuscularMycorrhiza': 0.2,
    'AB_SlimyPholiota': 0.2, 'BMT_BleedingTooth': 0.2, 'BMT_Brightbells': 0.2,
    'BMT_CrimsonCap': 0.2, 'BMT_GreyLady': 0.2, 'BMT_Shinecap': 0.2,
    'BMT_VioletWimple': 0.2, 'BMT_MortalMorelPlant': 0.15, 'AB_AgaricusDomeCap': 0.1,
    'AB_DribblingCap': 0.1, 'BMT_Skulltop': 0.1, 'BMT_Blastpod': 0.05,
    'AB_AgariluxPrime': 0.01},
  'AB_RockyCrags': {   # 1,170 tiles · 6 plants
    'AB_GlowingGrass': 1.0, 'AB_ToxicGamma': 0.6, 'AB_GiantGamma': 0.5,
    'AB_WildRadagast': 0.5, 'AB_GiantStikehr': 0.3, 'AB_GiantSeptimum': 0.2},
  'ZBiome_DesertOasis': {   # 223 tiles · 4 plants
    'Plant_Reeds': 1.0, 'AB_GreenRockFern': 0.4, 'BMT_Dewshrooms': 0.4,
    'Plant_Ambrosia': 0.12},
  'AB_GelatinousSuperorganism': {   # 96 tiles · 6 plants
    'AB_TallSlimyGrass': 1.0, 'AB_SlimyFern': 0.5, 'AB_SlimyTree': 0.5,
    'AB_Slimecasia': 0.4, 'AB_SlimyPholiota': 0.4, 'AB_LargeSlimyTree': 0.3},
  'AB_PyroclasticConflagration': {   # 31 tiles · 13 plants
    'Plant_Fireweed': 0.9, 'Plant_MagmaCactus': 0.7, 'BMT_FireLavender': 0.6,
    'AG_Gamma': 0.5, 'BMT_Sagecrust': 0.4, 'IronScruff_PrimordialGrass': 0.35,
    'AB_GiantGamma': 0.3, 'AB_TinkleGrass': 0.3, 'IronScruff_PrimordialTallGrass': 0.3,
    'AG_Septimum': 0.25, 'IronScruff_Bindweed': 0.25, 'AB_FirevineTree': 0.2,
    'BMT_HeatsinkFungus': 0.2},
  'LavaField': {   # 8 tiles · 13 plants
    'Plant_Fireweed': 0.9, 'Plant_MagmaCactus': 0.7, 'BMT_FireLavender': 0.6,
    'AG_Gamma': 0.5, 'BMT_Sagecrust': 0.4, 'IronScruff_PrimordialGrass': 0.35,
    'AB_GiantGamma': 0.3, 'AB_TinkleGrass': 0.3, 'IronScruff_PrimordialTallGrass': 0.3,
    'AG_Septimum': 0.25, 'IronScruff_Bindweed': 0.25, 'AB_FirevineTree': 0.2,
    'BMT_HeatsinkFungus': 0.2},
  'Volcano': {   # 5 tiles · 13 plants
    'Plant_Fireweed': 0.9, 'Plant_MagmaCactus': 0.7, 'BMT_FireLavender': 0.6,
    'AG_Gamma': 0.5, 'BMT_Sagecrust': 0.4, 'IronScruff_PrimordialGrass': 0.35,
    'AB_GiantGamma': 0.3, 'AB_TinkleGrass': 0.3, 'IronScruff_PrimordialTallGrass': 0.3,
    'AG_Septimum': 0.25, 'IronScruff_Bindweed': 0.25, 'AB_FirevineTree': 0.2,
    'BMT_HeatsinkFungus': 0.2},
 },

 'C. contamination': {
  'Wasteland': {   # 1,126 tiles · 25 plants
    'RG_Plant_ToxiGrass': 1.2, 'RG_Plant_TallToxiGrass': 0.8, 'AB_ToxiGrass': 0.6,
    'BMT_Plant_GutterPlantain': 0.5, 'BMT_Plant_ToxicIvy': 0.5,
    'BMT_Plant_TwistedDandelion': 0.5, 'PoisonPlantTallGrass': 0.4, 'Plant_GrayGrass': 0.35,
    'PoisonShrub': 0.35, 'BMT_Plant_ScorchedStars': 0.3, 'BMT_Plant_Snaketails': 0.3,
    'PoisonPlantBush': 0.3, 'BMT_Plant_PoxSorghum': 0.25,
    'BMT_Plant_TumorbulbHyacinth': 0.25, 'AB_WeepingToxberry': 0.2,
    'BMT_Plant_WildRashroot': 0.2, 'Plant_Toxipotato': 0.2, 'BMT_Plant_Doomsprout': 0.15,
    'BMT_Plant_EclipsusFlower': 0.15, 'BMT_Plant_EclipsusLeaves': 0.15,
    'BMT_RainbowTongue': 0.15, 'AB_ToxiBulb': 0.1, 'Plant_TreePolux': 0.1,
    'AB_GiantToxicFlower': 0.08, 'VRE_PoluxBush': 0.08},
  'AB_MiasmicMangrove': {   # 93 tiles · 7 plants
    'AB_MangroveTree': 25, 'AB_ParasiticMangrove': 8, 'AB_MangrovePalm': 6,
    'BMT_Plant_TreeTanglerootMangrove': 1.5, 'BMT_Plant_SewerReed': 0.8,
    'BMT_RainbowTongue': 0.6, 'BMT_Plant_Snaketails': 0.5},
  'Scarlands': {   # 90 tiles · 1 plants
    'BMT_Plant_ScorchedStars': 0.25},
 },

 'D. the shrub belt': {
  'AridShrubland': {   # 665 tiles · 10 plants
    'Plant_ShrubLow': 0.9, 'RG_Plant_AridGrass': 0.5, 'Plant_Brambles': 0.3,
    'Plant_Bush': 0.3, 'Plant_Ripthorn': 0.3, 'Plant_HealrootWild': 0.25,
    'Plant_Nysyllin_Wild': 0.22, 'RG_Plant_CreepStern': 0.2, 'RG_Plant_CrimsonCushion': 0.2,
    'RG_Plant_Dervish': 0.2},
 },

 'E. the tar': {
  'AB_TarPits': {   # 42 tiles · 1 plants
    'AB_TarPuddle': 0.6},
 },

 # ══════════════════════════════════════════════════════════════════════════════════════
 # DELIBERATELY UNPLACED, and this is now a SHORT list because the rule changed.
 # Until 2026-09-09 these rosters were a sweep of the whole plant pool and this block
 # explained every plant left out of it. The rosters replaced that: a plant is in a
 # biome because that biome's sheet law admitted it, and everything else is simply not
 # admitted. There is no longer a per-plant case to answer.
 #
 #   ⛔ CUT BY THE OWNER, and this one still bites:
 #     Plant_TreePine · Plant_TreeBirch · Plant_TreePoplar · RG_Plant_Raspberry
 #     Cherry Picker DELETES these ThingDefs at load. Naming one in a BiomeDef throws
 #     `Could not resolve cross-reference` on every single load, and the check below
 #     cannot catch it because the def dump predates the cut.
 #
 #   Anima, Gauranlen, the psychic lotus and the harbinger tree arrive by their own
 #   mechanisms - meditation focus, pods and Dryads, an event, an entity - never through
 #   wildPlants. A wildPlants entry would scatter them like weeds and break the mechanic
 #   that gives them meaning. No roster names one; none should.
 # ══════════════════════════════════════════════════════════════════════════════════════
}

# Painted defs that carry NO flora, each by a roster ruling rather than by omission.
#   RUT_NightsideIce   nightside_ice.json flora_purged "ALL": §6 admits no photosynthesis
#                      or photosynthetic tissue of any kind, no soil, nothing that reads
#                      as a plant.
#   RUT_BlueDesert     the_blue_desert.json lands zero flora rows (§6 ban 1).
#   AB_MechanoidIntrusion  the_rust_cathedral.json lands zero flora rows.
#   RUT_TwilightSea / RUT_GreySea / RUT_TheScald  the sea rosters name mats and giants,
#                      no wildPlants; the sea-bottom flora rides the deferred diving mods.
# Ocean/Lake/SeaIce/IceSheet are not painted on Ash'karr at all and are kept only so this
# set still answers for a world that carries them.
PLANTLESS = {'RUT_NightsideIce', 'RUT_BlueDesert', 'AB_MechanoidIntrusion',
             'RUT_TwilightSea', 'RUT_GreySea', 'RUT_TheScald',
             'Ocean', 'Lake', 'SeaIce', 'IceSheet'}

# 🔴 DECIDE'S DENSITY RULING, 2026-08-23 (`BARE_BIOMES_NEED_DENSITY_1`).
# A roster nobody sees fixes nothing. Two biomes ship a `plantDensity` so low that whatever
# we assign them reads as bare ground — together 4,935 tiles, 22.6% of the planet.
# ⛔ Only these two are touched. Density is a DIFFERENT lever from roster and it feeds the
# fire ecology (`hydrology_and_fire_ecology.md` R-H3 makes plant growth the fuel), so this
# is a named exception list, never a sweep.
DENSITY = {
  # biome: (new, shipped, why)
  'Wasteland': (0.12, 0.0099,
     "1,721 tiles of CONTAMINATION-class ground carrying an eight-plant toxic roster - "
     "toxigrass, gutter plantain, twisted dandelion, scorched stars - that exists to say "
     "THIS GROUND IS POISONED. At 0.0099 it says nothing. Poisoned ground reads more "
     "strongly with sick plants on it than with nothing. 12x up, still visibly barren."),
}
# ⛔ `ExtremeDesert` stays at its shipped 0.008 and that is a RULING, not an oversight.
# It is the lethal core of the dayside, median 48.2 C, and its four succulents are MEANT to
# be scarce. Bare ground there is the honest reading of the place; a player crossing 3,214
# tiles of genuinely dead sand is experiencing the planet, not a defect.


# ── the head-and-tail rule ────────────────────────────────────────────────────────
# 🔴 **DECIDE's ruling, 2026-08-23.** A biome whose plants all carry a similar weight has
# no dominant flora, and a biome with no dominant flora has no identity. The third pass
# ("the 84 leftovers land") fixed the zoo effect ACROSS biomes and quietly recreated it
# WITHIN the big ones: `BMT_FungalForest`'s top five carried 19.7% of 69 plants, against
# 84% for `HorrorWastes` — and HorrorWastes is the one you can name by looking at it.
#
# 🔑 **The ROSTER is not touched; only the WEIGHTS are.** Every plant keeps its home, so
# the no-crossing guarantee cannot reopen and no plant is made homeless. The transform is
# `w ** p`, which is monotone — it NEVER reorders two plants, it only widens the gap the
# author already wrote.
#
# ✅ **Fuel-neutral, and that was CHECKED, not assumed.** `WildPlantSpawner.cs:699` picks a
# plant with `GetCommonalityOfPlant(plant) / PlantsCommonalitiesSum` — a RELATIVE weight —
# while the NUMBER of plants comes from `GetDesiredPlantsCountAt(cell, plantDensityFactor)`.
# Rescaling commonalities cannot change plant MASS, so the fire-ecology rule R-H3 in
# `hydrology_and_fire_ecology.md` is not in play here.
HEAD_N      = 5      # "the flora you actually notice"
HEAD_FLOOR  = 0.50   # below this share the biome reads as soup — shape it
HEAD_TARGET = 0.60   # shape up to here and no further; a 95% head is a monoculture
TAIL_FLOOR  = 0.01   # ⛔ never 0 — a 0.0 commonality NEVER spawns (cf. Plant_TreeGrayPine)


def _head_share(ws, n=HEAD_N):
    ws = sorted(ws, reverse=True)
    tot = sum(ws)
    return sum(ws[:n]) / tot if tot else 0.0


def shape(roster):
    """Widen an over-flat roster until its top HEAD_N carry ~HEAD_TARGET of the weight.

    Returns (roster, exponent). An exponent of 1.0 means the roster was already shaped
    and nothing was changed.
    """
    if len(roster) <= HEAD_N or _head_share(roster.values()) >= HEAD_FLOOR:
        return roster, 1.0
    lo, hi = 1.0, 8.0
    for _ in range(50):                              # bisect for the gentlest exponent
        mid = (lo + hi) / 2
        if _head_share([w ** mid for w in roster.values()]) < HEAD_TARGET:
            lo = mid
        else:
            hi = mid
    top = max(roster.values())
    scale = top / (top ** hi)                        # keep the head's authored number
    return {k: max(TAIL_FLOOR, round((w ** hi) * scale, 4))
            for k, w in roster.items()}, hi


def load():
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    plants, biomes = {}, {}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        if d['fields'].get('plant'):
            plants[d['defName']] = d
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='BiomeDef'"):
        d = json.loads(j)
        biomes[d['defName']] = d
    return plants, biomes


def placed():
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    c = collections.Counter(r['biome'] for r in csv.DictReader(open(TILES, encoding='utf-8')))
    return c


def roster_flora():
    """biome -> {plant defName: commonality}, straight out of the roster JSONs.

    The rosters are the SOURCE for FAMILIES since 2026-09-09. This exists so `--check`
    can prove the dict still says what they say - a derived artifact that nothing
    compares back to its source is a copy waiting to go stale, and this repo has been
    bitten by exactly that (the cast patch and its CSV drifted by four biomes).
    """
    out = collections.defaultdict(dict)
    for fp in sorted(glob.glob(os.path.join(ROSTERS, '*.json'))):
        if os.path.basename(fp).startswith('_'):
            continue
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        for b in d.get('defNames') or []:
            for r in d.get('flora') or []:
                out[b][r['def']] = r['commonality']
    return out


def check(plants, biomes, tiles):
    bad = 0
    owner = {}                       # plant -> family

    # ── FAMILIES must still say exactly what the rosters say ──────────────────────
    want = roster_flora()
    have = collections.defaultdict(dict)
    for _fam, _bs in FAMILIES.items():
        for _b, _r in _bs.items():
            have[_b].update(_r)
    for b in sorted(set(want) | set(have)):
        if want.get(b, {}) != have.get(b, {}):
            only_r = {p: w for p, w in want.get(b, {}).items() if have.get(b, {}).get(p) != w}
            only_f = {p: w for p, w in have.get(b, {}).items() if want.get(b, {}).get(p) != w}
            print(f"🔴 FAMILIES DISAGREES WITH THE ROSTERS for {b}: "
                  f"roster-only/differs {only_r}, dict-only/differs {only_f}")
            bad += 1
    for fam, bs in FAMILIES.items():
        for b, roster in bs.items():
            if b not in biomes:
                print(f"🔴 BIOME NOT IN DEFS: {b}"); bad += 1
            if b not in tiles:
                print(f"🔴 BIOME NOT ON THE MAP: {b}"); bad += 1
            for p in roster:
                if p not in plants:
                    print(f"🔴 PLANT NOT IN DEFS: {p}  (biome {b})"); bad += 1
                prev = owner.get(p)
                if prev and prev != fam:
                    print(f"🔴 CROSS-FAMILY REUSE: {p}  in '{prev}' and '{fam}'"); bad += 1
                owner.setdefault(p, fam)
    covered = {b for bs in FAMILIES.values() for b in bs}
    missing = set(tiles) - covered - PLANTLESS
    for b in sorted(missing):
        print(f"🔴 PLACED BIOME WITH NO ROSTER: {b} ({tiles[b]} tiles)"); bad += 1
    return bad, owner


def _tile_temps():
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    t = collections.defaultdict(list)
    for r in csv.DictReader(open(TILES, encoding='utf-8')):
        t[r['biome']].append(float(r['temp_c']))
    return t


def doc(plants, biomes, tiles):
    """Regenerate design/Jawa/worldbuilding/biome_flora_rosters.md from FAMILIES."""
    temps = _tile_temps()
    nb = sum(len(bs) for bs in FAMILIES.values())
    ndistinct = len({p for bs in FAMILIES.values() for r in bs.values() for p in r})

    cold = pool = 0
    if os.path.exists(POOL):
        for r in csv.DictReader(open(POOL, encoding='utf-8')):
            pool += 1
            try:
                cold += float(r['minGrowthTemp']) >= 0   # >= : a plant whose floor IS 0 °C
                                                        # also will not grow below it
            except (TypeError, ValueError):
                pass

    o = ["# Ash'karr's flora — what grows where, and why", '',
         '> 🔴 **GENERATED** by `design/Jawa/mods/biome_flora.py --doc`. The rosters live in that',
         "> file's `FAMILIES` dict; edit there and regenerate, never here.", '',
         '**Owner\'s brief, 2026-08-23, verbatim:** *"distribute the plants per biome… You, agent Decide,',
         'make those calls right now… Try to avoid using the same plant across different biome types.',
         "It's ok to draw from Tinctora, Healroot, and other normally player-grown plants as you",
         'decorate the biomes."*', '',
         '🔑 **The rule that shapes everything below: no plant appears in two FAMILIES.** Inside one',
         'family a shared plant is kinship; across two it is the zoo effect he objected to. The',
         'generator refuses to build if any plant crosses.', '',
         '⭐ **His three named favourites all have a home** — `Plant_TreeDrago` in `Desert`,',
         '`BMT_Plant_TreeTwistingThornwood` and `BMT_Plant_TreeMartyr` in `PoisonForest`, where the',
         'rest of the Polluted Lands trees live.', '',
         '⛔ **Four plants are CUT and appear nowhere below** — `Plant_TreePine`, `Plant_TreeBirch`,',
         '`Plant_TreePoplar`, `RG_Plant_Raspberry`. The owner removed them with Cherry Picker, which',
         'deletes the ThingDef at load; a BiomeDef still naming one throws a red cross-reference error',
         'on every load. The full list of everything left unplaced ON PURPOSE — anima, Gauranlen,',
         'event-spawned and hydroponics-only flora — is the comment block at the foot of `FAMILIES`.', '']
    if pool:
        o += ['⚠️ **Climate was deliberately NOT a filter.** He ruled *"we can set the appropriate',
              f'temperatures later"* — {cold} of {pool} plants will not grow below 0 °C and half this planet is',
              'colder than that. Making these rosters actually live is `NORMALIZE_TEMPERATURE_TOLERANCES_1`.', '']
    o += [f'**{len(FAMILIES)} families · {nb} biomes · {ndistinct} plants, all distinct.** '
          f'{len(PLANTLESS)} biomes carry no flora by design: '
          + ', '.join(f'`{b}`' for b in sorted(PLANTLESS)) + '.', '']

    for fam, bs in FAMILIES.items():
        o += [f'## {fam}', '']
        for b, roster in sorted(bs.items(), key=lambda kv: -tiles.get(kv[0], 0)):
            f = biomes[b]['fields']
            dens = f.get('plantDensity') or 0.0
            ts = temps.get(b) or [0.0]
            med = sorted(ts)[len(ts) // 2]
            warn = ('  🔴 **`plantDensity` is near zero — this roster will almost never be seen**'
                    if dens < 0.05 else '')
            o.append(f'### `{b}` — {tiles.get(b, 0):,} tiles · {min(ts):.0f} … {max(ts):.0f} °C '
                     f'(median {med:.0f}) · plantDensity {dens:g}{warn}')
            o += ['', f'*was {len(f.get("wildPlants") or [])} inherited plants → '
                      f'now **{len(roster)}** assigned*', '',
                  '| commonality | plant | | mod |', '|---:|---|---|---|']
            for p, w in sorted(roster.items(), key=lambda kv: -kv[1]):
                d = plants[p]
                tree = '🌳' if (d['fields']['plant'].get('treeCategory') or 'None') != 'None' else ''
                o.append(f'| {w:g} | **{d["fields"].get("label") or p}** | {tree} | '
                         f'`{p}` · {d.get("modName") or "?"} |')
            o.append('')
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    open(DOC, 'w', encoding='utf-8').write('\n'.join(o).rstrip() + '\n')
    print(f'wrote {DOC}  ({nb} biomes, {ndistinct} plants)')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--doc', action='store_true')
    a = ap.parse_args()
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`'); return 2
    plants, biomes = load()
    tiles = placed()
    bad, owner = check(plants, biomes, tiles)

    shaped = []
    for _fam, _bs in FAMILIES.items():
        for _b in list(_bs):
            _new, _p = shape(_bs[_b])
            if _p != 1.0:
                _bs[_b] = _new
                shaped.append((_b, _p))

    nb = sum(len(bs) for bs in FAMILIES.values())
    print(f"\n{len(FAMILIES)} families · {nb} biomes · {len(owner)} distinct plants · "
          f"{sum(len(r) for bs in FAMILIES.values() for r in bs.values())} assignments")
    print(f"{len(PLANTLESS)} biomes plantless by design: {', '.join(sorted(PLANTLESS))}")
    if bad:
        print(f"\n🔴 {bad} problem(s) — nothing written."); return 1
    print("✅ every defName resolves · no plant crosses a family · every placed biome covered")
    if shaped:
        print(f"head-and-tail rule reshaped {len(shaped)} over-flat roster(s): "
              + ", ".join(f"{b} ^{p:.2f}" for b, p in sorted(shaped, key=lambda kv: -kv[1])))
    if a.doc:
        doc(plants, biomes, tiles)
    if not a.write:
        if not a.doc:
            print("\n(pass --write to emit the patch, --doc to regenerate the roster doc)")
        return 0

    out = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
           '  <!-- GENERATED by design/Jawa/mods/biome_flora.py - do not hand-edit.',
           '',
           "       Ash'karr's flora, ASSIGNED rather than inherited. Owner's brief 2026-08-23:",
           '       distribute the plants per biome, avoid using the same plant across different',
           '       biome types, and player-grown flora (tinctoria, healroot) may decorate.',
           '',
           '       🔴 wildPlants is a LoadDataFromXmlCustom field: the node NAME is the plant',
           '       defName and its VALUE is the commonality. An <li> here discards the whole',
           '       BiomeDef, silently. -->', '']
    for fam, bs in FAMILIES.items():
        out.append(f'  <!-- ============ {fam} ============ -->')
        for b, roster in sorted(bs.items(), key=lambda kv: -tiles.get(kv[0], 0)):
            # ⛔ NO MayRequire. The dump's packageId names the mod that last RETEXTURED a
            # def, not the one that defines it: Core's `Desert` reports GRiNDTerra, so a
            # MayRequire built from it would skip Core biomes whenever that mod is absent.
            # PatchOperationConditional is the correct guard and it is sufficient — a biome
            # that does not exist simply fails the xpath and the <match> never runs.
            out.append('  <Operation Class="PatchOperationConditional">')
            out.append(f'    <xpath>/Defs/BiomeDef[defName="{b}"]/wildPlants</xpath>')
            out.append('    <match Class="PatchOperationReplace">')
            out.append(f'      <xpath>/Defs/BiomeDef[defName="{b}"]/wildPlants</xpath>')
            out.append('      <value>')
            out.append('        <wildPlants>')
            for p, w in sorted(roster.items(), key=lambda kv: -kv[1]):
                lab = plants[p].get('label') or ''
                tree = ' - tree' if (plants[p]['fields']['plant'].get('treeCategory') or 'None') != 'None' else ''
                out.append(f'          <{p}>{w}</{p}> <!-- {lab}{tree} -->')
            out.append('        </wildPlants>')
            out.append('      </value>')
            out.append('    </match>')
            out.append('  </Operation>')
            out.append('')
    out.append('  <!-- ============ plantDensity - the named exception list ============ -->')
    for b, (new_d, old_d, why) in DENSITY.items():
        out.append(f'  <!-- {b}: {old_d} -> {new_d}.')
        for line in textwrap.wrap(why, 92):
            out.append(f'       {line}')
        out.append('  -->')
        out.append('  <Operation Class="PatchOperationConditional">')
        out.append(f'    <xpath>/Defs/BiomeDef[defName="{b}"]/plantDensity</xpath>')
        out.append('    <match Class="PatchOperationReplace">')
        out.append(f'      <xpath>/Defs/BiomeDef[defName="{b}"]/plantDensity</xpath>')
        out.append(f'      <value><plantDensity>{new_d}</plantDensity></value>')
        out.append('    </match>')
        out.append('  </Operation>')
        out.append('')
    out.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"\nwrote {PATCH}  ({nb} roster + {len(DENSITY)} density operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
