#!/usr/bin/env python3
"""Ash'karr's flora, ASSIGNED rather than inherited — one signature roster per biome.

🔴 **OWNER, 2026-08-23, verbatim:** *"I thought you had distributed the plants per biome for
me? If not, PLEASE do that right now. You, agent Decide, make those calls right now and do it…
Try to avoid using the same plant across different biome types. It's ok to draw from Tinctora,
Healroot, and other normally player-grown plants as you decorate the biomes."*
Plus, minutes later: *"We can set the appropriate temperatures later, don't worry about that as
a constraint"* ⇒ climate tolerance is `NORMALIZE_TEMPERATURE_TOLERANCES_1`, not a filter here.
**Assignment is by LOOK and LORE.**

🔑 **The rule that shapes every list below: no plant appears in two FAMILIES.** The eight
families are the design; inside one, a shared plant is deliberate kinship, across two it is the
zoo effect the owner objected to. `--check` fails the build if any plant crosses a family.

🔴 **`wildPlants` IS a `LoadDataFromXmlCustom` field and `<li>` DESTROYS THE DEF.** Read from
source, not assumed — `BiomePlantRecord.LoadDataFromXmlCustom` takes the **node NAME** as the
plant defName and the node's **value** as the commonality:

    <wildPlants>
      <Plant_TreeDrago>0.08</Plant_TreeDrago>     ✅
      <li><plant>Plant_TreeDrago</plant>…</li>    ⛔ discards the WHOLE BiomeDef, silently
    </wildPlants>

That is the same trap that cost 26 BiomeDefs and 101 CharacterDefs on 2026-08-23.

    python3 design/Jawa/mods/biome_flora.py --check     # families, overlaps, defNames resolve
    python3 design/Jawa/mods/biome_flora.py --write     # emit the patch
"""
import argparse, collections, csv, json, os, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
PATCH = os.path.join(ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches', 'BiomeFlora_Ashkarr.xml')

# ---------------------------------------------------------------- the design
# family -> biome -> {plant defName: commonality}
# Commonality scale, held consistent so one biome does not out-shout another:
#   2.0+  the ground cover you always see      0.5-1.0  the mid layer you notice
#   0.2-0.5  punctuation                       <0.2     trees and set pieces
FAMILIES = {

 'A. dayside desert': {
  'Desert': {                       # 4,648 tiles - the face of the planet
    'AB_HardyGrass': 2.2, 'Plant_PincushionCactus': 0.8, 'Plant_Agave': 0.6,
    'Plant_DesertDandelion': 0.45, 'AB_BrownBarrelCactus': 0.25,
    'Plant_PebbleCactus': 0.35,     # tree - walk list: reads correctly for desert ground
    'Plant_SaguaroCactus': 0.12,    # tree
    'Plant_TreeDrago': 0.08},       # tree - owner: "I love the strange drago tree"
  'ExtremeDesert': {                # 3,214 - plantDensity 0.008, all but sterile
    'AB_EuphorbiaRimworldia': 0.30, 'VCE_Plant_PincushionPlant': 0.25,
    'AB_GargantuanLithops': 0.20,   # living stones
    'AB_EuphorbiaDesiccata': 0.06}, # tree
  'AridShrubland': {                # 709 - scrub, and the planet's herb garden
    'Plant_ShrubLow': 1.4, 'VEE_Gorse': 0.7, 'VEE_Heather': 0.6,
    'VEE_Plant_JuniperBush': 0.5, 'Plant_Ripthorn': 0.3,
    'Plant_HealrootWild': 0.25},    # owner licensed player-grown flora
  'ZBiome_Badlands': {              # 545 - the cactus garden, kept whole in one place
    'VEE_Plant_ChollaCactus': 0.40, 'VEE_Plant_HedgehogCactus': 0.40,
    'VEE_Plant_BeavertailCactus': 0.35, 'VEE_Plant_BarrelCactus': 0.30,
    'VEE_Plant_OrganPipeCactus': 0.25,
    'Plant_Psychoid_Wild': 0.20},   # player-grown
  'ZBiome_DesertOasis': {           # 227 - the only place that reads WET on the dayside
    'Plant_Reeds': 1.2, 'Plant_Bulrush': 1.0, 'Plant_Alocasia': 0.6,
    'VEE_Plant_DatePalm': 0.35, 'AB_FanPalm': 0.30,
    'Plant_Smokeleaf_Wild': 0.20,   # player-grown
    'Plant_Ambrosia': 0.12},
  'ZBiome_Grasslands': {            # 233 - hot grass plain
    'Plant_YellowGrass': 2.4, 'Plant_YellowTallGrass': 2.0, 'Plant_Haygrass': 0.5,
    'Plant_Tinctoria_Wild': 0.30,   # owner named tinctoria by name
    'Plant_Cotton_Wild': 0.30},
 },

 'B. contamination': {              # §6c: the danger is the GROUND, not the wildlife
  'Wasteland': {                    # 1,721
    'RG_Plant_ToxiGrass': 2.0, 'RG_Plant_TallToxiGrass': 1.2,
    'BMT_Plant_GutterPlantain': 0.6, 'BMT_Plant_ToxicIvy': 0.5,
    'BMT_Plant_TwistedDandelion': 0.5, 'BMT_Plant_ScorchedStars': 0.30,
    'BMT_Plant_WildRashroot': 0.20, 'BMT_Plant_Doomsprout': 0.15},
  'AB_TarPits': {                   # 57
    'AB_TarPuddle': 1.5, 'BMT_Plant_BloomingCorpse': 0.30,
    'BMT_Plant_TreeSnakeWillow': 0.15, 'BMT_Plant_TreeSeepingEucalyptus': 0.12},
 },

 'C. mycoid belt': {                # 2,968 tiles, ZERO river tiles - watered by the terminator
  'AB_MycoticJungle': {             # 1,939 - Alpha Biomes' fungal set, kept intact
    'AB_Agarilux': 1.2, 'AB_GlowingAgarilux': 0.6, 'AB_AgaricusDomeCap': 0.5,
    'AB_RecurvedStropharia': 0.4, 'AB_SlimyPholiota': 0.4, 'AB_WitchesOyster': 0.35,
    'AB_GiantAgarilux': 0.30, 'AB_DribblingCap': 0.20,
    'AB_GiantAgariTox': 0.15,       # tree
    'Plant_Devilstrand': 0.10},     # player-grown, and it is genuinely a fungus
  'BMT_FungalForest': {             # 425 - Biomes! Caverns' set, kept intact
    'BMT_Wrinklecap': 1.0, 'BMT_Fibershroom': 0.8, 'BMT_Gleamtip': 0.6,
    'BMT_Chromacap': 0.5, 'BMT_Greatbulb': 0.4,
    'BMT_Shimbershroom': 0.25, 'BMT_Poptop': 0.20, 'BMT_Dishcap': 0.20,
    'BMT_Shinecap': 0.18},
  'PoisonForest': {                 # 604 - Polluted Lands' set
    'BMT_Plant_PaganThorns': 0.8, 'BMT_Plant_PlagueFans': 0.7,
    'BMT_Plant_Toxcaps': 0.6, 'BMT_Plant_Pestia': 0.5,
    'BMT_Plant_WeepingHagbloom': 0.30,
    'BMT_Plant_TreeTwistingThornwood': 0.18,  # owner: "I love the … twisting thornwood"
    'BMT_Plant_TreeBlotBirch': 0.15, 'BMT_Plant_TreeScalpedCypress': 0.12,
    'BMT_Plant_TreeMartyr': 0.10,   # owner: "I love the … martyr"
    'BMT_Plant_TreeWormoak': 0.10},
 },

 'D. river jungle': {               # 599 tiles, 233 of them river - it stands in water
  'AB_FeraliskInfestedJungle': {    # 534
    'AB_TallSlimyGrass': 1.8, 'AB_GreenRockFern': 0.7,
    'AB_JungleTree': 0.30, 'AB_JungleTree_Polluted': 0.15,
    'AB_KeeningCordax': 0.12, 'AB_GiantFlower': 0.10},
  'AB_MiasmicMangrove': {           # 65
    'BMT_Plant_SewerReed': 1.2, 'AB_ParasiticMangrove': 0.4,
    'AB_MangroveTree': 0.35, 'AB_MangrovePalm': 0.30,
    'BMT_Plant_TreeTanglerootMangrove': 0.20, 'VEE_Mangrove': 0.20},
 },

 'E. frozen nightside': {
  'AB_RockyCrags': {                # 3,816 - the dark. Sparse on purpose.
    'AB_FrostLeaf': 0.9, 'AB_RimeNodules': 0.6, 'BMT_RimeFlower': 0.4,
    'AB_FlashFrozenTree': 0.10},
  'AB_PropaneLakes': {              # 554 - an industrial accident, frozen
    'AB_CrystalFlower': 0.5, 'AB_CrystalHorn': 0.4, 'BMT_Crystal_BlueSowable': 0.30},
  'HorrorWastes': {                 # 468 - BIOWEAPON class. The danger is the wildlife.
    'HorrorWeb': 1.2,               # its own mod's plant, used by nothing until now
    'AB_BloodBouquet': 0.5, 'AB_GlobularPlant': 0.4, 'AB_TentacularPlant': 0.35,
    'AB_FleshTree': 0.12},          # ⛔ Plant_Agave is GONE - a desert succulent at -49 C
  'BMT_CrystalCaverns': {           # 127
    'CrystalSmall': 1.0, 'BMT_CrystaltipBrambles': 0.8, 'CrystalShard': 0.6,
    'CrystalBig': 0.30, 'BMT_Crystalcap': 0.30},
 },

 'F. volcanic': {
  'Volcano': {                      # 23 - owner ruled it needs NO wood, so no tree here
    'Plant_Fireweed': 0.9, 'GRimMagmaCactus': 0.6, 'BMT_Sagecrust': 0.4},
  'LavaField': {                    # 15
    'Plant_MagmaCactus': 0.7, 'BMT_FireLavender': 0.6, 'BMT_HeatsinkFungus': 0.20},
  'AB_PyroclasticConflagration': {  # 31
    'AG_Gamma': 0.5, 'AB_GiantGamma': 0.30, 'AB_FirevineTree': 0.20,
    'AB_ToxicGamma': 0.15},
 },

 'G. machine and scar': {
  'AB_MechanoidIntrusion': {        # 236 - contamination class, computronium ground
    'BMT_VoltaicFungus': 0.30, 'AB_TechnoTree': 0.15, 'AB_SessileMechanoid': 0.12,
    'AB_GoldenCubeTree': 0.08},
  'Scarlands': {                    # 90 - where a weapon was used and left
    'BMT_RustPuff': 0.8, 'BMT_BurnedMushroom': 0.6, 'AG_DarkGamma': 0.4,
    'BurnedTree': 0.20},
 },

 'H. alien': {                      # bioweapon class, but ENGINEERED LIFE rather than cold
  'AB_GelatinousSuperorganism': {   # 96
    'AB_SlimyFern': 0.9, 'AB_Slimecasia': 0.6, 'AB_SlimyTree': 0.30,
    'AB_LargeSlimyTree': 0.20},
  'AB_OcularForest': {              # 3 - it watches
    'AB_EyeGrass': 1.2, 'AB_RedLeaves': 0.7, 'AB_RedPlantsTall': 0.5,
    'AB_AlienTree': 0.4, 'AB_AlienTree_Polluted': 0.20, 'AB_HalfAlienTree': 0.15},
 },
}

PLANTLESS = {'Ocean', 'Lake', 'SeaIce', 'IceSheet'}   # by design, not by omission


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
    c = collections.Counter(r['biome'] for r in csv.DictReader(open(TILES, encoding='utf-8')))
    return c


def check(plants, biomes, tiles):
    bad = 0
    owner = {}                       # plant -> family
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`'); return 2
    plants, biomes = load()
    tiles = placed()
    bad, owner = check(plants, biomes, tiles)

    nb = sum(len(bs) for bs in FAMILIES.values())
    print(f"\n{len(FAMILIES)} families · {nb} biomes · {len(owner)} distinct plants · "
          f"{sum(len(r) for bs in FAMILIES.values() for r in bs.values())} assignments")
    print(f"{len(PLANTLESS)} biomes plantless by design: {', '.join(sorted(PLANTLESS))}")
    if bad:
        print(f"\n🔴 {bad} problem(s) — nothing written."); return 1
    print("✅ every defName resolves · no plant crosses a family · every placed biome covered")
    if not a.write:
        print("\n(pass --write to emit the patch)"); return 0

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
    out.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f"\nwrote {PATCH}  ({nb} operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
