# Cartoonish-era art census 2026-10-09 (read-only, nothing filed)

Item ART_PAINTERLY_RESTORATION_1: ruling edaa118f0 (2026-09-13 23:23); owed "examine and re-rule" for 2026-09-12 to 09-14 cartoonish-lawset renders.

## Window / marker used
The job specs (toyfig) were deleted by the 09-15 ruling, so the marker is by evidence: art-ledger variants (git) first committed in the pre-ruling cartoonish installs cea007c3a (95 gate-passed renders, 22:29), dde341c12 (Canon-5 lawset renders, 22:36), 61ee1dd08 (Iriaz/Nuna lawset, 22:57), 8d1099849 (Pyrelands invented-7, 21:26), plus artpipe variants dated 09-12..14 or job id containing toyfig. 219 distinct picture shas. A LIVE texture counts if the ledger's current live sha for that (mod, rel) equals one of them (byte match; a re-encoded copy would be missed).
Sanity probe: 59 artpipe variants in window incl. anooba_toyfig_a_east, boma_toyfig_a_east, pyrelands_*_v1/v2 named jobs; 8d1099849's 21 pyrelands renders all found but ZERO still live (already replaced), so probe sees supersession. MLIE_FAUNA port commits excluded (donor ports, not generated).

## Totals
- LIVE cartoonish-era textures: **85** across **57** subjects
- Owner "kept since" (trust=ruled keep naming this exact sha): **15** textures / 8 subjects. His keep stands.
- Still unruled: **70** textures / 49 subjects; of these canon creatures: 9; with a painterly re-render already existing (done job after 09-14, name match, heuristic): 28
- By group: {'BloodShrimpArtOverride': 3, 'FeverWood': 1, 'Greentide': 3, 'Miasma': 3, 'Pyrelands': 3, 'SWBestiary': 28, 'UtinniPatches': 44}
- Caveat: subject-level keeps without exact sha (prefill/legacy-unresolved) protect nothing; none counted as kept.

## Still owed a re-ruling (70)
| biome/mod | subject | texture | canon | painterly re-render |
|---|---|---|---|---|
| Miasma | RSW_AaroxisDendoria | `Things/Pawn/Animal/RM_Liliana/RM_Liliana_east.png` |  | none |
| Miasma | RSW_AaroxisDendoria | `Things/Pawn/Animal/RM_Liliana/RM_Liliana_north.png` |  | none |
| Miasma | RSW_AaroxisDendoria | `Things/Pawn/Animal/RM_Liliana/RM_Liliana_south.png` |  | none |
| Pyrelands | RM_FE_EmberGrass_LeaflessA | `Things/Plant/RM_FE_EmberGrass_Leafless/RM_FE_EmberGrass_LeaflessA.png` |  | Y gapall_rm_fe_plant_embergrass_v1 |
| Pyrelands | RM_FE_Quickgrass_LeaflessA | `Things/Plant/RM_FE_Quickgrass_Leafless/RM_FE_Quickgrass_LeaflessA.png` |  | Y gapall_rm_fe_plant_quickgrass_v1, pyre_quickgrass_leafless_v3 |
| Pyrelands | RM_FE_ScorchFruitYield | `Things/Item/Resource/RM_FE_ScorchFruit.png` |  | none |
| SWBestiary | RSW_AaroxisDendoria | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/AaroxisDendoria/AaroxisDendoria_east.png` |  | none |
| SWBestiary | RSW_AaroxisDendoria | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/AaroxisDendoria/AaroxisDendoria_north.png` |  | none |
| SWBestiary | RSW_AaroxisDendoria | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/AaroxisDendoria/AaroxisDendoria_south.png` |  | none |
| SWBestiary | RSW_BloodletterPetrel | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/BloodletterPetrel/BloodletterPetrel_east.png` |  | none |
| SWBestiary | RSW_BloodletterPetrel | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/BloodletterPetrel/BloodletterPetrel_north.png` |  | none |
| SWBestiary | RSW_BloodletterPetrel | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/BloodletterPetrel/BloodletterPetrel_south.png` |  | none |
| SWBestiary | RSW_Boma | `swanimals/Boma/Boma_east.png` | Y | Y canon_boma_v1_east, canon_boma_v1_north |
| SWBestiary | RSW_Boma | `swanimals/Boma/Boma_north.png` | Y | Y canon_boma_v1_east, canon_boma_v1_north |
| SWBestiary | RSW_Boma | `swanimals/Boma/Boma_south.png` | Y | Y canon_boma_v1_east, canon_boma_v1_north |
| SWBestiary | RSW_Borcatu | `swanimals/Borcatu/Borcatu_east.png` | Y | Y canon_borcatu_v1_east, canon_borcatu_v1_north |
| SWBestiary | RSW_Borcatu | `swanimals/Borcatu/Borcatu_north.png` | Y | Y canon_borcatu_v1_east, canon_borcatu_v1_north |
| SWBestiary | RSW_Borcatu | `swanimals/Borcatu/Borcatu_south.png` | Y | Y canon_borcatu_v1_east, canon_borcatu_v1_north |
| SWBestiary | RSW_CrestedDragon | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/CrestedDragon/CrestedDragon_east.png` |  | none |
| SWBestiary | RSW_CrestedDragon | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/CrestedDragon/CrestedDragon_north.png` |  | none |
| SWBestiary | RSW_CrestedDragon | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/CrestedDragon/CrestedDragon_south.png` |  | none |
| SWBestiary | RSW_Dactillion | `swanimals/Dactillion/Dactillion_east.png` | Y | none |
| SWBestiary | RSW_Dactillion | `swanimals/Dactillion/Dactillion_north.png` | Y | none |
| SWBestiary | RSW_Dactillion | `swanimals/Dactillion/Dactillion_south.png` | Y | none |
| SWBestiary | RSW_FoundryBeetle | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FoundryBeetle/FoundryBeetle_east.png` |  | none |
| SWBestiary | RSW_FoundryBeetle | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FoundryBeetle/FoundryBeetle_north.png` |  | none |
| SWBestiary | RSW_FoundryBeetle | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FoundryBeetle/FoundryBeetle_south.png` |  | none |
| SWBestiary | RSW_FungalMantis | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalMantis/FungalMantis_east.png` |  | none |
| SWBestiary | RSW_FungalMantis | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalMantis/FungalMantis_north.png` |  | none |
| SWBestiary | RSW_FungalMantis | `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/FungalMantis/FungalMantis_south.png` |  | none |
| SWBestiary | RSW_Screecher | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Screecher/Screecher_east.png` |  | none |
| SWBestiary | RSW_Screecher | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Screecher/Screecher_north.png` |  | none |
| SWBestiary | RSW_Screecher | `swanimals/BiomesTeam/BMT_PollutedLands/Things/Animal/Screecher/Screecher_south.png` |  | none |
| UtinniPatches | AB_AaklacA | `Things/Plants/AB_Aaklac/AB_AaklacA.png` |  | none |
| UtinniPatches | AB_AgaricusDomeCap | `Things/Plants/AB_AgaricusDomeCap.png` |  | Y rot_agaricusdomecap_v2 |
| UtinniPatches | AB_AgariluxPrime | `Things/Plants/AB_AgariluxPrime.png` |  | Y rot_agariluxprime_v2, rot_agariluxprime_v3 |
| UtinniPatches | AB_ArbuscularMycorrhizaA | `Things/Plants/AB_ArbuscularMycorrhiza/AB_ArbuscularMycorrhizaA.png` |  | Y rot_arbuscularmycorrhiza_v2 |
| UtinniPatches | AB_BloodBouquet | `Things/Plants/AB_BloodBouquet.png` |  | Y bloodbouquet_v2, bloodbouquet_v3 |
| UtinniPatches | AB_DribblingCapA | `Things/Plants/AB_DribblingCap/AB_DribblingCapA.png` |  | Y rot_dribblingcap_v2 |
| UtinniPatches | AB_FirevineTreeA | `Things/Plants/AB_FirevineTree/AB_FirevineTreeA.png` |  | Y gapbs_ab_firevinetree_v1 |
| UtinniPatches | AB_GiantAgariTox | `Things/Plants/AB_GiantAgariTox.png` |  | Y giantagaritox_v2, giantagaritox_v3 |
| UtinniPatches | AB_GiantAgariluxA | `Things/Plants/AB_GiantAgarilux/AB_GiantAgariluxA.png` |  | Y rot_giantagarilux_v2 |
| UtinniPatches | AB_GlobularPlant | `Things/Plants/AB_GlobularPlant.png` |  | none |
| UtinniPatches | AB_Gomphoeria | `Things/Plants/AB_Gomphoeria.png` |  | none |
| UtinniPatches | AB_GreenRockFern | `Things/Plants/AB_GreenRockFern.png` |  | none |
| UtinniPatches | AB_Iashiphus | `Things/Plants/AB_Iashiphus.png` |  | none |
| UtinniPatches | AB_KeeningCordaxA | `Things/Plants/AB_KeeningCordax/AB_KeeningCordaxA.png` |  | Y keeningcordax_v2, keeningcordax_v3 |
| UtinniPatches | AB_LargeSlimyTree | `Things/Plants/AB_LargeSlimyTree.png` |  | none |
| UtinniPatches | AB_LilacBeaconA | `Things/Plants/AB_LilacBeacon/AB_LilacBeaconA.png` |  | Y rot_lilacbeacon_v2 |
| UtinniPatches | AB_MangroveTreeA | `Things/Plants/AB_MangroveTree/AB_MangroveTreeA.png` |  | none |
| UtinniPatches | AB_OcularTreeA | `Things/Plants/AB_OcularTree/AB_OcularTreeA.png` |  | none |
| UtinniPatches | AB_PollutedAlienTree | `Things/Plants/AB_PollutedAlienTree.png` |  | none |
| UtinniPatches | AB_SugarFamewort | `Things/Plants/AB_SugarFamewort.png` |  | none |
| UtinniPatches | AB_ToxiGrass | `Things/Plants/AB_ToxiGrass.png` |  | none |
| UtinniPatches | AB_WildRadagast | `Things/Plants/AB_WildRadagast.png` |  | none |
| UtinniPatches | AgariluxA | `Things/Plant/Agarilux/AgariluxA.png` |  | Y rot_agariluxprime_v2, rot_agariluxprime_v3 |
| UtinniPatches | Ambrosia_A | `Things/Plant/Ambrosia/Ambrosia_A.png` |  | Y ambrosia_v2, sheet_redo_plant_ambrosia_v3 |
| UtinniPatches | Arpeau_A | `BMT_Caverns/Things/Plant/Arpeau/Arpeau_A.png` |  | Y arpeau_a_v1, arpeau_b_v1 |
| UtinniPatches | BMT_BleedingToothA | `BMT_Caverns/Things/Plant/BleedingTooth/BMT_BleedingToothA.png` |  | Y rot_bleedingtooth_v2 |
| UtinniPatches | BMT_SeadewA | `BMT_Caverns/Things/Plant/Seadew/BMT_SeadewA.png` |  | none |
| UtinniPatches | BrightbellsA | `Things/Plant/BMT_Brightbells/BrightbellsA.png` |  | none |
| UtinniPatches | BryoluxA | `Things/Plant/Bryolux/BryoluxA.png` |  | Y rot_bryolux_v2 |
| UtinniPatches | CrimsonCap_a | `BMT_Caverns/Things/Plant/CrimsonCap/CrimsonCap_a.png` |  | Y rot_crimsoncap_v2 |
| UtinniPatches | FireweedA | `Things/Plant/Fireweed/FireweedA.png` |  | Y gapfin_plant_fireweed_v1 |
| UtinniPatches | FruitingBodyA | `BMT_Caverns/Things/Plant/FruitingBodies/FruitingBodyA.png` |  | none |
| UtinniPatches | GU_AlienGrassA | `Things/Plants/GU_AlienGrass/GU_AlienGrassA.png` |  | none |
| UtinniPatches | GlowstoolA | `Things/Plant/Glowstool/GlowstoolA.png` |  | Y rot_glowstool_v2 |
| UtinniPatches | GreyLadyGrownA | `BMT_Caverns/Things/Plant/GreyLady/GreyLadyGrown/GreyLadyGrownA.png` |  | Y greyladygrown_a_v1, greyladygrown_b_v1 |
| UtinniPatches | IronScruff_BindweedA | `Things/Plants/IronScruff_Bindweed/IronScruff_BindweedA.png` |  | Y gapall_ironscruff_bindweed_v1 |
| UtinniPatches | RM_SaltCameo | `Things/Plants/AB_CrystalHorn/AB_CrystalHornA.png` |  | none |

## Kept since (15)
| biome/mod | subject | texture | canon | painterly re-render |
|---|---|---|---|---|
| BloodShrimpArtOverride | AA_BloodShrimp | `Things/Pawn/Animal/AA_BloodShrimp/AA_BloodShrimp_east.png` |  | none |
| BloodShrimpArtOverride | AA_BloodShrimp | `Things/Pawn/Animal/AA_BloodShrimp/AA_BloodShrimp_north.png` |  | none |
| BloodShrimpArtOverride | AA_BloodShrimp | `Things/Pawn/Animal/AA_BloodShrimp/AA_BloodShrimp_south.png` |  | none |
| FeverWood | RM_GiantLeaf | `Things/Plant/RM_GiantLeaf/RM_GiantLeaf_a.png` |  | none |
| Greentide | RM_Ghemmel | `Things/Plant/RM_Ghemmel/RM_Ghemmel_a.png` |  | none |
| Greentide | RM_Nemmer | `Things/Plant/RM_Nemmer/RM_Nemmer_a.png` |  | none |
| Greentide | RM_Veluthar | `Things/Plant/RM_Veluthar/RM_Veluthar_a.png` |  | none |
| SWBestiary | RM_NiimCatch | `Things/Plant/RSW_Plant_Bloddle/RSW_Plant_BloddleB.png` |  | none |
| UtinniPatches | AB_GiantGammaA | `Things/Plants/AB_GiantGamma/AB_GiantGammaA.png` |  | none |
| UtinniPatches | AB_ToxicGamma | `Things/Plants/AB_ToxicGamma.png` |  | none |
| UtinniPatches | RM_Ghemmel | `swplants/HydenockTree/HydenockTreeA.png` |  | none |
| UtinniPatches | RM_GiantLeaf | `BMT_Caverns/Things/Plant/GiantLeaf/GiantLeafA.png` |  | none |
| UtinniPatches | RM_GiantLeaf | `Things/Plant/GiantLeaf/GiantLeaf_a.png` |  | none |
| UtinniPatches | RM_NiimCatch | `swplants/Bloddle/BloddleA.png` |  | none |
| UtinniPatches | RM_Veluthar | `Things/Plants/AB_JungleTree/AB_JungleTreeA.png` |  | none |
