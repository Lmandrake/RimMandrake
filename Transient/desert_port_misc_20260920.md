# Desert family port — MISC batch — 2026-09-20

## Batch
16 fauna + 8 flora listed in `Transient/desert_port_batches/MISC.json`.
`AB_GiantStikehr` EXCLUDED per `DESERT_FAMILY_PORT_EXECUTION_1`'s own note
(cut from Extreme Desert the same day as misplaced) — 7 flora actually ported.
23 of 24 species ported.

## Output files (owned, RSW_DesertPortMisc_* only)
- `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` — 16 ThingDef + 16 PawnKindDef
- `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Items.xml` — leather x3, meat x1, eggs x4
- `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml` — 7 ThingDef plants

## Naming (all DRAFTED, not ruled — old -> new)
Terrorworm -> RSW_Ashworm, AA_DesertAve -> RSW_Sandstrider, AA_Needleroll -> RSW_Spineroller,
AA_Cactipine -> RSW_Spinerat, AA_Eyeling -> RSW_Stareling, AA_Needlepost -> RSW_Barbthorn,
AA_Wildpawn -> RSW_Sporepaw, AA_Gigantelope -> RSW_Sandhorn, AA_SandProwler -> RSW_Dunestalker,
AA_Terramorph -> RSW_Ferroclaw, AA_BoulderMit -> RSW_Stoneback, AA_SandSquid -> RSW_Sandmaw,
AA_Wildpod -> RSW_Sporemass, AA_MammothWorm -> RSW_Tuskcoil, AA_TetraSlug -> RSW_Voltmaw,
VFEI2_Fuelmite -> RSW_Cindermite, AB_HardyGrass -> RSW_Dunegrass, RG_Plant_AridGrass -> RSW_Scrubgrass,
RG_Plant_CreepStern -> RSW_Starvine, RG_Plant_CrimsonCushion -> RSW_EmberCarpet,
RG_Plant_Dervish -> RSW_Whirlbloom, AB_Aaklac -> RSW_VellaraBloom, AB_DessertTree -> RSW_SweetbarkTree.

None of these 23 appear in `design/RimStarWars/canon_references/` — CONFIRMED (grepped for
worm/ave/rat/eye/cactus/slug/mite/squid/crab/antelope/prowler/pod/hive; only unrelated hit was
`kinrath`). All 23 are Alpha Animals/Alpha Biomes/ReGrowth/Horrors/VFEI2 invented creatures, not
Star Wars canon, so pseudo-SW naming is the correct track.

## Donor-framework comps DROPPED (per species, full rationale in each ThingDef's own
`<!-- comment -->` in RSW_DesertPortMisc_Races.xml)
Every `VEF.AnimalBehaviours.*`, `AlphaBehavioursAndEvents.*` and `VEF.Plants.*` comp/modExtension
is dropped — CompProperties_AnimalProduct, LightSustenance, InitialAbility, InitialHediff,
AsexualReproduction, HighlyFlammable, GraphicByTerrain, EatWeirdFood, NearbyEffecter,
TerrainChanger, Electrified, GraphicsRefresher, DualCropExtension, and every AnimalStatExtension
modExtension (info-card flavor text only). Three of these are real gameplay-mechanic losses, not
just framework noise, flagged for the owner:
- **RSW_Ferroclaw** loses its steel-eating/mineral-processing mechanic (was its whole point).
- **RSW_Voltmaw** loses its chemfuel-ejection ranged ability.
- **RSW_Cindermite** loses its chemfuel-ejection ability AND periodic chemfuel harvest (was its whole point).

## Custom body substitution (not a framework drop — a scope call, CONFIRMED not guessed)
5 species used Alpha Animals' own custom BodyDefs with their own BodyPartDef graph in a shared
file. Porting that whole graph was cut for scope. Substituted with the closest EXISTING vanilla
BodyDef, confirmed by reading that BodyDef's own part tree:
- Eyeling, SandSquid -> **Monkey** (HeadAttackTool + Teeth groups present; Monkey carries no "Arms"
  group tag despite having Arm/Hand parts, so Sandmaw's tentacle tool is left ungrouped).
- Needleroll, Needlepost -> **QuadrupedAnimalWithPawsAndTail** (same body already used by
  Cactipine/SandProwler; Teeth + HeadAttackTool confirmed present).
- MammothWorm -> **Snake** (HeadAttackTool on SnakeHead; group tag is "Mouth", not "SnakeMouth").
Custom ToolCapacityDefs (AA_ToxicSting, AA_ToxicBite, AA_SiegeBlunt, AA_ExtraDamageMechanoidsTusk)
substituted with vanilla Scratch/Bite/Blunt/Poke — drops each donor's poison/anti-mechanoid
DamageDef chain, a deliberate mechanic simplification, documented per species.

## Reference closure ported
Leather: RSW_CactusHide, RSW_BlackChitin, RSW_InsectChitin. Meat: RSW_CactusMeat (parent fixed to
vanilla `PlantFoodRawBase`, CONFIRMED present in Core — donor's own `AA_PlantFoodRawBase` abstract
not ported). Eggs: RSW_SandstriderEgg{Fert,Unfert}, RSW_TuskcoilEgg{Fert,Unfert}. Dangling
`useMeatFrom` refs substituted: DesertAve's AA_MeadowAve -> vanilla Cassowary; TetraSlug's
AA_Helixien -> Megaspider; Terramorph's AA_BoulderMit -> this batch's own RSW_Stoneback (sibling,
no dangling ref).

## Art
55 jobs filed via `fill_queue.py` (never hand-written) — 16 fauna × 3 facings (south/east/north) +
7 flora × 1 (single-view). `rimflow_item_id: DESERT_FAMILY_PORT_EXECUTION_1`. Canvas =
drawSize×128 rounded to next power of two, floor 256, per adult lifeStage / mature plant size.
0 duplicates, 0 row errors on file. Until renders land, texPaths point at donor textures as loud
placeholders — see validator findings below for the 5 that had no usable donor loose file.

## validate_patch.py
Run against `ModsConfig_full_plus_longhunger_2026-09-19.xml` with `--defs` on RimWorld's Data,
Mods and Workshop content roots. First pass found 2 real defects, both fixed:
1. `RSW_CactusMeat` ParentName `MeatBase` didn't resolve (not a real vanilla def) — fixed to
   `PlantFoodRawBase` (CONFIRMED present in Core, same base `RawFungus`/`RawPotatoes` use).
2. 4 plant texPaths errored as non-existent ("Things/" is this mod's own namespace, so nothing
   else can supply it) — `Grass_Leafless`, `RG_CreepStern`, `RG_TundraScrubsRed`, `RG_Dervish`.
   CONFIRMED by `find`: these ReGrowth/Alpha-Biomes textures are packed in a Unity AssetBundle,
   not a loose PNG — matches this batch's own MISC.json census note ("art UNRESOLVED — no loose
   PNG and no bundle_textures cache entry"). Fixed by pointing all 5 (plus RSW_Scrubgrass, whose
   identical defect the validator didn't flag — a validator gap, fixed on the same evidence) at
   Alpha Biomes' AB_Aaklac texture (CONFIRMED present on disk) as a deliberately mismatched but
   non-magenta placeholder, loudly commented at each site.
Second pass (re-run after both fixes): **OK TOTAL - 3 file(s), 0 error(s), 3 warning(s)**. All 3
remaining warnings are the same benign note on `RSW_Ashworm`'s PawnKindDef texPath (Terrorworm's
own donor texture — a WARN not an ERROR here since PawnKindDef texPaths are checked more loosely
than ThingDef graphicData.texPath; tool's own verdict: "nothing here fails... advisory").

## Could NOT port
- `AB_GiantStikehr` — excluded per the item's own ruling, not attempted.
- Full custom BodyDef/BodyPartDef graphs for Eyeling/SandSquid/Needleroll/Needlepost/MammothWorm —
  substituted with vanilla bodies instead (see above), not a full port of AA's body geometry.

## Absolute paths
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Items.xml`
- `/mnt/d/Luke/dev/Rimworld/src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml`
- `/mnt/d/Luke/dev/Rimworld/Transient/desert_port_batches/MISC.json` (source batch)
