# Donor-off L04_TEX_OURS: texture fixes and what is left (FOUNDRY offline, 2026-10-17)

Method: the 38-line round (`Transient/phase0_L1_result_20261016T085647.json`) kept only 10 examples and no Player.log copy, so the miss set was
rebuilt from SOURCE: every `texPath`/`immatureGraphicPath` on an RM_/RSW_/RUT_ ThingDef in `src/` checked against (our `Textures/` folders,
vanilla Core/DLC def texPaths, loose PNGs of ACTIVE mods in `ModsConfig.FULL.LATEST.xml`, via `art/gametex.py`). No bridge, no game.

## Already fixed before this pass (commit `0aba1c303`, 2026-10-16 09:51, after the round)
File-vs-folder mismatches: Hay stand-ins, RM_Salvessa, RM_Thrannagourd, RM_Murrowbulb, RM_CorriskTree, RM_Glasmaw, RM_DustveilEgg, eggs, raptor plates, etc.
Those lines were from the round's pre-fix state; the source scan finds none of them any more.
Correction to the brief: the vanilla `Hay` texPath is `Things/Item/Resource/PlantFoodRaw/Hay`, identical to ours; the miss was Random/StackCount on a file path, not a 1.6 move.

## Repointed now (6 defs; `immatureGraphicPath` pointed at an EMPTY folder `Things/Plant/RM_<X>`)
The mature art is the one owner-installed sprite at `Things/RM_<X>/RM_<X>.png`; immature now draws that same sprite (the field uses the def's own graphicClass, a folder).
Not a new picture: the only existing art, replacing a hard "No textures found" error. Revert = one line each if he wants separate seedling art.
RM_Glasmaw, RM_Thrannagourd, RM_CorriskTree, RM_Crimmelroot, RM_LumbrelTree, RM_Murrowbulb.
Validated: `validate_patch.py --live <dump 2026-10-16T09-47-54Z> --defs Data --defs workshop --defs Mods` = 0 errors on all 6.
`deploy_custom_mods.py --compose biomes` dry run lists exactly these 6 as drift (plus other seats' files); NOT applied.

## Remaining: needs a decision or new art (no unambiguous existing art)
Root cause: these point at **Vanilla Plants Expanded - Succulents** (`vanillaexpanded.vplantsesucculents`, workshop 2198652536), which is in neither the
donor-off tier nor `ModsConfig.FULL.LATEST.xml`. They are not vanilla 1.6 paths and no Core/DLC art stands in for them.

| def | texPath now | file | what it needs |
|---|---|---|---|
| RM_Rimebeard | Things/Plant/SnakePlant/SnakePlantA | TerminalBiomes/RM_GreySeaUnderstorey.xml | own art (artpipe: no job, no name match) |
| RM_Stillbloom | Things/Plant/PincushionPlant/PincushionPlantB | same | own art |
| RM_Simmerlace, RM_Kettlewick, RM_Threshreed | SnakePlant/SnakePlantA | TerminalBiomes/RM_ScaldUnderstorey.xml | own art x3 |
| RM_Vekkfan, RM_Thurlsponge, RM_Foamgorse, RM_Seepcandle | Echeveria/EcheveriaA | same | own art x4 |
| RM_NoothelmPlant | Echeveria/EcheveriaA | TerminalBiomes/RM_TwilightLightPlants.xml | artpipe has a NAME-MATCHED render (job token noothelmplant); needs his approve + `art install` |
| RM_Glasskelle | SnakePlant/SnakePlantA | DivingInteraction/RM_ScaldVentFlora.xml | own art |
| RM_Pulsebead | PincushionPlant/PincushionPlantA | same | own art |
| RM_LungerFry (item) | Echeveria/EcheveriaA | Greentide/RM_GreentideFish_Items.xml | own art (a fish item pointing at a plant) |
| RUT_LungerFry (item) | Echeveria/EcheveriaA | UtinniPatches/RUT_GreentideFish_Items.xml | reskin of the above; follows it |

One-step interim if he wants zero errors before art: point all 14 at a VANILLA plant folder (e.g. `Things/Plant/PincushionCactus`); cosmetic, so held for him.
Other unresolved: `RUT_FungalSoil` texPath `BMT_Caverns/Terrains/MycelialSoil` (a terrain texture of the retired caverns mod; needs art or a terrain stand-in).
Cauldron `RM_Dewfall/*_dew` extension paths (5 plants): not errors; `RM_CauldronDewfallVisuals.cs` probes with `Get(path,false)` and skips absent art. Art not made.
Not in the L04 set (dump rows from 10-16): RM_Pluurva, RM_Bezzul, RM_GiantCrownedSilkie folders resolve in source now.
