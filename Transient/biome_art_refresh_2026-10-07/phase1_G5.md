# phase1_G5

## 1. Untracked textures
9 PNGs, all NOT-REFERENCED today. All 9 are in the art ledger (sha256 match, kind artpipe, dated 2026-10-06, not installed-from-ruling; no owner decision/art_ruling mentions found).
Method: index of every string in Defs/Patches XML and Source .cs of all src mods; no ref equals the texPath (any facing suffix), and no C# loads them by path.

| file (under src/RimMandrake/) | item | verdict | why |
|---|---|---|---|
| FlowWorks/Textures/Things/Building/FlowWorks/Doors/RM_Sluice_Mover.png | FLOWWORKS_DOOR_FAMILY_1 (closed 6359e69b5) | NOT-REFERENCED | FlowWorks_Doors.xml RM_Sluice uses texPath Things/Building/FlowWorks/Canals/RM_Sluice (Graphic_Single, DoorBase), uiIconPath same; no "Doors/" path anywhere |
| .../Doors/RM_Sluice_MenuIcon.png | same | NOT-REFERENCED | same; uiIconPath points at Canals/RM_Sluice |
| .../Doors/RM_SecurityGrateDoor_Mover.png | same | NOT-REFERENCED | RM_SecurityGrateDoor uses Canals/RM_SecurityGrateDoor |
| .../Doors/RM_SecurityGrateDoor_MenuIcon.png | same | NOT-REFERENCED | same. Would need a def edit (texPath/uiIconPath -> Doors/*) to take effect: art-ledger-only so far (install not done) |
| FlowWorks/.../Excavation/RM_WallFace_North.png | EXCAVATION_WALL_ART_1 (proposed) | NOT-REFERENCED | no def/C# path string; RM_ExcavationWalls.cs draws via vertex-colour quads (WhiteTex), RM_WallFaceMath is pure math. Commits 157482540 / a26e3d875 mention "wall art queued" only |
| .../Excavation/RM_WallFace_Side.png | same | NOT-REFERENCED | same |
| WreckedMachines/Textures/WreckedMachines/Modules/Distillation/Wrecked/RM_WM_Distillation.png | WRECKED_DISTILLATION_MODULE_1 (validated; built 3e473f37c) | NOT-REFERENCED | Patches/WreckedMachines_DistillationModule.xml defs use vanilla texPath Things/Building/Ruins/AncientGenerator (Graphic_Random, tinted); "RM_WM_Distillation" there is only a replaceTags key |
| .../Distillation/Kludged/RM_WM_Distillation.png | same | NOT-REFERENCED | same (Kludged and Repaired use vanilla Things/Building/Power/ChemfuelPoweredGenerator; confirmed all three defs) |
| .../Distillation/Repaired/RM_WM_Distillation.png | same | NOT-REFERENCED | same |

Note: all three Wrecked/Kludged/Repaired files share a basename (RM_WM_Distillation.png) in sibling folders; a def would reference e.g. WreckedMachines/Modules/Distillation/Wrecked/RM_WM_Distillation. None does. None of the 9 is COMMIT-by-reference; they are generated-and-awaiting-wiring (commit is harmless but inert until the defs are edited). UNSURE: none.

## 2. Dangling texPaths
Scope: 69 mods that own a biome sheet row, biome def, patch placement or live art (derived from census.json: TerminalBiomes, UtinniPatches, SWBestiary, ~35 RimMandrake biome mods, *ArtOverride mods, BiomesShell). Scanned every texPath / flyingAnimationFramePathPrefix(+Female) / uiIconPath / iconPath / fishIcon in their Defs+Patches XML (comments stripped): 4215 refs, 3634 resolve (exact, facing suffix _north/_south/_east/_west/m, folder for Random/Collection, prefix for flying frames) against textures of ALL src mods. SANITY PROBE: Things/Pawn/Animal/landopus/landopus resolves (True).
Unresolved: 581. Of those 428 are vanilla/donor paths (Things/Pawn/Animal/Thrumbo/..., Things/Item/Resource/..., UI/Icons/Genes/... - legit, not listed; note 3x swanimals/DesertPort/Zakkro/Zakkro_Dessicated in SWBestiary and 3x Animal/RockTroll/* in FloodedCanyon are donor-mod paths, unverified). 31 refs (24 distinct mod+path pairs) are OUR namespace (RM_/RSW_/RUT_/JOE_ in path) and find NO file in any src Textures. DANGLING-OWN:

| mod | def file (under Defs/) | missing texPath | note |
|---|---|---|---|
| Cauldron | ThingDefs_Plants/RM_CauldronFlora.xml | Things/Plant/RM_Dewfall/RM_CrystalFlower_dew, RM_BloodBouquet_dew, RM_RedBugloss_dew, RM_KeeningCordax_dew, RM_GiantToxicFlower_dew | folder Things/Plant/RM_Dewfall absent from every src mod (5 paths) |
| Greentide | ThingDefs_Plants/RM_Greentide_TreeRoster.xml | Things/Plant/RM_Kaddrath/RM_Kaddrath_a | Graphic_Random; no file/folder. Only Transient/biome_ffar/img/scale_RM_Kaddrath_* exist |
| Greentide | ThingDefs_Plants/RM_Greatbole.xml | Things/Plant/RM_Greatbole/RM_Greatbole_a | no file anywhere |
| Greentide | ThingDefs_Plants/RM_YearningFruit.xml | Things/Item/Plant/RM_YearningFruitHarvested | Things/Item/Plant holds only LongShade/WeepingStones/SWBestiary items |
| LeaningScrub | ThingDefs_Items/RM_SweetlineTree_Items.xml | Things/Item/Resource/RM_SweetlineToken | sibling rm_sweetlinewool exists, token does not |
| Miasma | ThingDefs_Plants/RM_Miasma_RainbowBlooms.xml | Things/Plant/RM_Ismerrow/RM_Ismerrow | only Transient scale_ renders |
| Miasma | ThingDefs_Plants/RM_Miasma_Predators.xml | Things/Plant/RM_Braskeen/RM_Braskeen | only Transient scale_ renders |
| LongShade | ThingDefs_Races/RM_LongShade_Fauna.xml | Things/Pawn/Animal/RM_GreatDevourer/RM_GreatDevourer2, RM_GreatDevourer3, RM_Dessicated_GreatDevourer | only RM_GreatDevourer_{n,e,s} exist; lifestage/corpse variants missing |
| LongShade | same | Things/Pawn/Animal/RM_Groundrunner/RM_GroundrunnerW, RM_Groundrunner2..5, RM_Dessicated_Groundrunner | only RM_Groundrunner_{n,e,s} exist |
| LongShade | ThingDefs_Races/RM_LongShade_Fillers.xml | Things/Pawn/Animal/RM_Dakkra/RM_Dakkra_rest | stationaryGraphicData (owner ruling LONGSHADE_SHEET_STRUCTURAL_RULINGS_1, 2026-10-04); rest art not made/installed. Note: the stationary graphic is only a fallback-safe field, a miss draws magenta at rest |
| Stillsand | ThingDefs_Races/RM_Drazzik.xml | Things/Pawn/Animal/RM_Drazzik/RM_Drazzik_Swimming | swimmingGraphicData; only RM_Drazzik_{n,e,s} |
| SWBestiary | ThingDefs_Items/RSW_ZakkroEgg.xml | swresource/RSW_ZakkroEgg | no swresource/RSW_Zakkro* texture |

Caveat: lifestage/corpse (Dessicated), W/2..5 variants may be Graphic_Multi bodies whose real path I could not resolve without the def's graphicClass; they resolve to nothing either way. Plants with Graphic_Random expect _a/_b... style names; folder absent so they cannot load. Defs not scanned in the 'ours' sense: any texPath built in C#.

## 3. Orphan textures
Scope: the same 69 mods (3923 PNGs). A PNG counts as referenced if its path (facing suffix, mask m, trailing a/b/digit variant, parent folder for Graphic_Random) equals any string in any src Defs/Patches XML or Source .cs. SANITY PROBE: 9 landopus files in UtinniPatches all found referenced. Result: 321 unreferenced PNGs in 19 mods (the other 50 scope mods: 0). Limits: C# that builds paths by concatenation is invisible; donor-namespace textures (swresource/, bmt_caverns/, things/plants/ab_*, aa_*, rotspecies/) normally override a donor mod's def BY PATH, so they are not provably orphaned from this repo.

Counts by class: donor-path override (probable) 225 | *ArtOverride mods, override-by-path 24 (8 mods x 3 facings: Agaripod, BloodShrimp, RaptorShrimp, Rimclaw, ShadowCharger, Thermadon, Thunderox, Wildpod) | unknown, own namespace 68 | likely-stale-replaced 4.

Per mod (own-namespace examples listed, max 30 each; nothing here is proposed for deletion). Also unlisted-in-tool but noticed from item prose: Contagion / FeverWood / Wasteland have 2 wreck-variant PNGs each (rm_*wreck*_a/_b: Contagion wreck fragment, FeverWood wreck carapace, Wasteland warcasket sarcophagus) = art made ahead of def wiring (Contagion note: "still on vanilla ShipChunk placeholder until its render lands"); LanternDeeps has rm_lanterndeeps/fauna/hydrocarbon/chiller_{n,e,s} unreferenced; Scarlands rm_totchakdormant; TerminalBiomes rm_ulkhoss_{n,e,s}; Pyrelands quickgrass: the 4 parent-folder files duplicate the Sprout/ and Half/ subfolder files that the PlantGrowthStages extension points at (so the parent-folder copies are the stale/duplicate ones).

- RimStarWars/SWBestiary: 192 orphan of 1694 PNGs - donor-path (probably overrides a donor def by path): 163; unknown (own namespace): 29
    donor-path (probably overrides a donor def by path) e.g. swresource/eggslime/eggslime_a, swresource/eggslime/eggslime_b, swresource/eggdapple/eggdapple_a
    [unknown (own namespace)] things/plant/rsw_dunegrass/rsw_dunegrassa
    [unknown (own namespace)] things/plant/rsw_dommotree/rsw_dommotree_a
    [unknown (own namespace)] things/plant/rsw_ultracactus/rsw_ultracactus_a
    [unknown (own namespace)] things/plant/rsw_sweetbarktree/rsw_sweetbarktreea
    [unknown (own namespace)] things/plant/rsw_ollim/rsw_ollima
    [unknown (own namespace)] things/plant/rsw_lightpipenub/rsw_lightpipenuba
    [unknown (own namespace)] things/item/plant/rsw_rawultracactus
    [unknown (own namespace)] things/item/resource/rsw_ollimwood
    [unknown (own namespace)] things/pawn/animal/rsw_cindermite/rsw_cindermite_east
    [unknown (own namespace)] things/pawn/animal/rsw_cindermite/rsw_cindermite_north
    [unknown (own namespace)] things/pawn/animal/rsw_cindermite/rsw_cindermite_south
    [unknown (own namespace)] things/pawn/animal/rsw_ossik/rsw_ossik_south
    [unknown (own namespace)] things/pawn/animal/rsw_ossik/rsw_ossik_north
    [unknown (own namespace)] things/pawn/animal/rsw_ossik/rsw_ossik_east
    [unknown (own namespace)] things/pawn/animal/rsw_vosska/rsw_vosska_north
    [unknown (own namespace)] things/pawn/animal/rsw_vosska/rsw_vosska_south
    [unknown (own namespace)] things/pawn/animal/rsw_vosska/rsw_vosska_east
    [unknown (own namespace)] things/pawn/animal/rsw_kudda/rsw_kudda_north
    [unknown (own namespace)] things/pawn/animal/rsw_kudda/rsw_kudda_south
    [unknown (own namespace)] things/pawn/animal/rsw_kudda/rsw_kudda_east
    [unknown (own namespace)] things/pawn/animal/rsw_thurra/rsw_thurra_north
    [unknown (own namespace)] things/pawn/animal/rsw_thurra/rsw_thurra_south
    [unknown (own namespace)] things/pawn/animal/rsw_thurra/rsw_thurra_east
    [unknown (own namespace)] things/pawn/animal/rsw_ulgga/rsw_ulgga_east
    [unknown (own namespace)] things/pawn/animal/rsw_ulgga/rsw_ulgga_north
    [unknown (own namespace)] things/pawn/animal/rsw_ulgga/rsw_ulgga_south
    [unknown (own namespace)] things/pawn/animal/rsw_ommok/rsw_ommok_south
    [unknown (own namespace)] things/pawn/animal/rsw_ommok/rsw_ommok_north
    [unknown (own namespace)] things/pawn/animal/rsw_ommok/rsw_ommok_east
- RimUtinni/UtinniPatches: 56 orphan of 191 PNGs - donor-path (probably overrides a donor def by path): 50; unknown (own namespace): 6
    donor-path (probably overrides a donor def by path) e.g. bmt_caverns/things/plant/seadew/bmt_seadewa, bmt_caverns/things/plant/arpeau/arpeau_a, bmt_caverns/things/plant/giantleaf/giantleafa
    [unknown (own namespace)] things/pawn/animal/rut_mortuarycrawler/rut_mortuarycrawler_south
    [unknown (own namespace)] things/pawn/animal/rut_mortuarycrawler/rut_mortuarycrawler_north
    [unknown (own namespace)] things/pawn/animal/rut_mortuarycrawler/rut_mortuarycrawler_east
    [unknown (own namespace)] things/building/wrecks/rut_falllinewreckcarapace/rut_falllinewreckcarapace_b
    [unknown (own namespace)] things/building/wrecks/rut_falllinewreckhull/rut_falllinewreckhull_b
    [unknown (own namespace)] things/building/wrecks/rut_falllinewreckhull/rut_falllinewreckhull_a
- RimMandrake/LongShade: 14 orphan of 83 PNGs - unknown (own namespace): 14
    [unknown (own namespace)] things/pawn/animal/rm_ossik/rm_ossik_north
    [unknown (own namespace)] things/pawn/animal/rm_ossik/rm_ossik_east
    [unknown (own namespace)] things/pawn/animal/rm_ossik/rm_ossik_south
    [unknown (own namespace)] things/pawn/animal/rm_maturefleshbeast/rm_maturefleshbeast_south
    [unknown (own namespace)] things/pawn/animal/rm_maturefleshbeast/rm_maturefleshbeast_east
    [unknown (own namespace)] things/pawn/animal/rm_maturefleshbeast/rm_maturefleshbeast_north
    [unknown (own namespace)] things/pawn/animal/rm_thurra/rm_thurra_north
    [unknown (own namespace)] things/pawn/animal/rm_thurra/rm_thurra_east
    [unknown (own namespace)] things/pawn/animal/rm_thurra/rm_thurra_south
    [unknown (own namespace)] things/pawn/animal/rm_kudda/rm_kudda_north
    [unknown (own namespace)] things/pawn/animal/rm_kudda/rm_kudda_east
    [unknown (own namespace)] things/pawn/animal/rm_kudda/rm_kudda_south
    [unknown (own namespace)] things/building/wrecks/rm_longshadewreckspeeder/rm_longshadewreckspeeder_a
    [unknown (own namespace)] things/building/wrecks/rm_longshadewreckspeeder/rm_longshadewreckspeeder_b
- RimMandrake/TheRot: 12 orphan of 205 PNGs - donor-path (probably overrides a donor def by path): 12
    donor-path (probably overrides a donor def by path) e.g. rotspecies/agarilux/agarilux_a, rotspecies/arbuscularmycorrhiza/arbuscularmycorrhiza_a, rotspecies/bryolux/bryolux_a
- RimMandrake/Stillsand: 6 orphan of 126 PNGs - unknown (own namespace): 6
    [unknown (own namespace)] things/pawn/animal/rm_ikee/rm_ikee_north
    [unknown (own namespace)] things/pawn/animal/rm_ikee/rm_ikee_south
    [unknown (own namespace)] things/pawn/animal/rm_ikee/rm_ikee_east
    [unknown (own namespace)] things/pawn/animal/rm_duumma/rm_duumma_surfaced_east
    [unknown (own namespace)] things/building/wrecks/rm_stillsandwrecktread/rm_stillsandwrecktread_b
    [unknown (own namespace)] things/building/wrecks/rm_stillsandwrecktread/rm_stillsandwrecktread_a
- RimMandrake/Pyrelands: 4 orphan of 99 PNGs - likely-stale-replaced: 4
    [likely-stale-replaced] things/plant/rm_fe_quickgrassstages/rm_fe_quickgrass_sprout_b   (referenced sibling: things/plant/rm_fe_quickgrassstages/sprout/rm_fe_quickgrass_sprout_a)
    [likely-stale-replaced] things/plant/rm_fe_quickgrassstages/rm_fe_quickgrass_half_a   (referenced sibling: things/plant/rm_fe_quickgrassstages/half/rm_fe_quickgrass_half_b)
    [likely-stale-replaced] things/plant/rm_fe_quickgrassstages/rm_fe_quickgrass_half_b   (referenced sibling: things/plant/rm_fe_quickgrassstages/half/rm_fe_quickgrass_half_b)
    [likely-stale-replaced] things/plant/rm_fe_quickgrassstages/rm_fe_quickgrass_sprout_a   (referenced sibling: things/plant/rm_fe_quickgrassstages/sprout/rm_fe_quickgrass_sprout_a)
- RimMandrake/LanternDeeps: 3 orphan of 154 PNGs - unknown (own namespace): 3
    [unknown (own namespace)] rm_lanterndeeps/fauna/hydrocarbon/chiller/chiller_east
    [unknown (own namespace)] rm_lanterndeeps/fauna/hydrocarbon/chiller/chiller_south
    [unknown (own namespace)] rm_lanterndeeps/fauna/hydrocarbon/chiller/chiller_north
- RimMandrake/TerminalBiomes: 3 orphan of 313 PNGs - unknown (own namespace): 3
    [unknown (own namespace)] things/pawn/animal/rm_ulkhoss/rm_ulkhoss_east
    [unknown (own namespace)] things/pawn/animal/rm_ulkhoss/rm_ulkhoss_north
    [unknown (own namespace)] things/pawn/animal/rm_ulkhoss/rm_ulkhoss_south
- RimUtinni/AgaripodArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_agaripod/aa_agaripod_north, things/pawn/animal/aa_agaripod/aa_agaripod_east, things/pawn/animal/aa_agaripod/aa_agaripod_south
- RimUtinni/BloodShrimpArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_bloodshrimp/aa_bloodshrimp_north, things/pawn/animal/aa_bloodshrimp/aa_bloodshrimp_east, things/pawn/animal/aa_bloodshrimp/aa_bloodshrimp_south
- RimUtinni/RaptorShrimpArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_raptorshrimp/aa_raptorshrimp_south, things/pawn/animal/aa_raptorshrimp/aa_raptorshrimp_north, things/pawn/animal/aa_raptorshrimp/aa_raptorshrimp_east
- RimUtinni/RimclawArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/regrowth/rimclaw/rimclaw_north, things/pawn/animal/regrowth/rimclaw/rimclaw_south, things/pawn/animal/regrowth/rimclaw/rimclaw_east
- RimUtinni/ShadowChargerArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_shadowcharger/aa_shadowcharger_north, things/pawn/animal/aa_shadowcharger/aa_shadowcharger_east, things/pawn/animal/aa_shadowcharger/aa_shadowcharger_south
- RimUtinni/ThermadonArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_thermadon/aa_thermadon_north, things/pawn/animal/aa_thermadon/aa_thermadon_east, things/pawn/animal/aa_thermadon/aa_thermadon_south
- RimUtinni/ThunderoxArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_thunderox/aa_thunderox_male_south, things/pawn/animal/aa_thunderox/aa_thunderox_male_north, things/pawn/animal/aa_thunderox/aa_thunderox_male_east
- RimUtinni/WildpodArtOverride: 3 orphan of 3 PNGs - override-by-path: 3
    override-by-path e.g. things/pawn/animal/aa_wildpod/aa_wildpod_south, things/pawn/animal/aa_wildpod/aa_wildpod_north, things/pawn/animal/aa_wildpod/aa_wildpod_east
- RimMandrake/Contagion: 2 orphan of 98 PNGs - unknown (own namespace): 2
    [unknown (own namespace)] things/building/wrecks/rm_contagionwreckfragment/rm_contagionwreckfragment_a
    [unknown (own namespace)] things/building/wrecks/rm_contagionwreckfragment/rm_contagionwreckfragment_b
- RimMandrake/FeverWood: 2 orphan of 91 PNGs - unknown (own namespace): 2
    [unknown (own namespace)] things/building/wrecks/rm_feverwoodwreckcarapace/rm_feverwoodwreckcarapace_b
    [unknown (own namespace)] things/building/wrecks/rm_feverwoodwreckcarapace/rm_feverwoodwreckcarapace_a
- RimMandrake/Wasteland: 2 orphan of 67 PNGs - unknown (own namespace): 2
    [unknown (own namespace)] things/building/wrecks/rm_wastelandwarcasketsarcophagus/rm_wastelandwarcasketsarcophagus_a
    [unknown (own namespace)] things/building/wrecks/rm_wastelandwarcasketsarcophagus/rm_wastelandwarcasketsarcophagus_b
- RimMandrake/Scarlands: 1 orphan of 77 PNGs - unknown (own namespace): 1
    [unknown (own namespace)] things/pawn/animal/rm_totchakdormant/rm_totchakdormant

Notes: LongShade rm_ossik/kudda/thurra/maturefleshbeast are the rows the LongShade sheet CUT (def comments: "CUT kudda, ossik, thurra and mature..."), so those 12 PNGs are likely-stale (subject cut), not "replaced". Same-subject RSW_ twins exist in SWBestiary (rsw_ossik, rsw_kudda, rsw_thurra), also unreferenced in-repo. Wreck _a/_b files across mods = awaiting wiring, not stale.

## 4. Misplaced art
Method: every ThingDef/PawnKindDef (1128) in the scope mods whose defName is on the biome sheets (census.json, 855 defNames); each texPath that resolves to a PNG in src but NOT in the def's own mod. SANITY: 2086 sheet-def texPaths resolved to some src PNG; 110 resolve only outside the def's own mod.
- 72 of the 110 are SWBestiary defs whose art sits in a *ArtOverride mod (Gizka, Anooba, Kinrath, PekoPeko, Hawkbat, Vornskyr, Nuna, Dragonsnake, Zeer, Grank, Horax, GreaterKraytDragon, Orray, Ronto, Zakkeg, Ollopom, Dewback, Shiro, Whisperbird, Fambaa, Kreetle) = the override-mod design (path override of a donor mod), NOT a defect.
- Remaining 38 rows (real cross-mod dependencies, def mod -> PNG-only-in mod):
  * Greentide -> UtinniPatches (7): RM_Zeev Things/Plant/AloeVera/AloeVeraA, RM_Uvva Peyote/PeyoteA, RM_Karrun PincushionPlant/PincushionPlantA, RM_Dubbol SweetheartPlant/SweetheartPlantA, RM_Lozh SnakePlant/SnakePlantA, RM_Saava Schlumbergera/SchlumbergeraA, RM_Tuun JadePlant/JadePlantA. Vanilla-named paths; without UtinniPatches active they draw VANILLA aloe/peyote/etc. (franchise-free RM_ tier would not match the campaign look; Q11a). Verdict: misplaced/tier-dependency.
  * TerminalBiomes -> UtinniPatches (3): RM_NoothelmPlant Things/Plant/Echeveria/EcheveriaA; RM_SorruthCatch Things/Item/ToxicMeat/ToxicMeat_b; RM_HolluCatch Things/Plant/JadePlant/JadePlantB.
  * TheSump -> UtinniPatches (1): RUT_Plant_Wick Things/Plant/Ambrosia (RUT_ def in an RM mod folder, art in the RUT mod).
  * LongShade -> SWBestiary (12 refs / 3 defs): RM_Bokka swanimals/BiomesTeam/BMT_Caverns/Things/Animal/Stoneback/Stoneback (x3), RM_Dunejelly .../Jellypot/Jellypot (x3), RM_TruffleMole .../TruffleMole/TruffleMole + Dessicated_TruffleMole (x3 each). These point at the BMT_Caverns donor tree; our RM_ defs depend on a copy living in the RimStarWars tier.
  * LongShade -> Armoury (3, RM_Bokka Things/Pawn/Animal/Iguana/Dessicated_Iguana) and WeepingStones -> Armoury (3, RM_Ssurr, same path): a vanilla-named corpse texture exists only in the Armoury mod folder (vanilla ships it, so likely harmless; flagged UNSURE).
No RM_-prefixed art was found sitting ONLY in a sibling RM_ mod other than the above; the 72 override rows are legitimate.
