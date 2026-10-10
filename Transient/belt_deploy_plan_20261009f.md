# Belt deploy plan 20261009f (dry runs only, game UP, nothing applied)

Dry-run: `python3 src/RimMandrake/Utils/deploy_custom_mods.py ...`. No refusals in any run. DEPLOY_HOLD: UtinniPatches 12 held (VentForge/Kiln/Smelter, TibannaGas, FoundryTowerEntrance/Scatter/Floor + their patches; all repo-only by design), SWBestiary 96 held (art/ mockups, source only). None of the fixes below touch a held file.

## Webwork (hook fix 756cf2812)
`--mod Webwork` refuses: folded into RimMandrake.Biomes, use `--compose biomes`. The compose plan shows NO Webwork drift: game DLL `Biomes/Webwork/Assemblies/RimMandrake.Webwork.dll` is byte-identical to repo (66048 B, already deployed 09:41). Nothing to do.

## UtinniPatches (RUT_DyingCreep ConfigErrors fix)
Write: `Defs/ThingDefs_Plants/RUT_DyingCreep.xml` (the only drift). Delete: none. Note mod reads "not enabled in ModsConfig" in the plan header.

## SWBestiary (two Silooth files)
`Patches/Silooth/Silooth_Warbeast.xml` and `Defs/AbilityDefs/RSW_SiloothAcidSpit.xml` are byte-identical in the game copy: already deployed, no drift. Only drift: `Assemblies/RimMandrakeBeastMechanicsRSW.dll` + `.dll.srchash` (companion DLL; game must be DOWN to write).

## TerminalBiomes (RUT_FoundrySalvageCache move)
`--mod TerminalBiomes` refuses (folded into Biomes). Game copy `RimMandrake.Biomes/Biomes/TerminalBiomes/Defs/ThingDefs_Buildings/RUT_FoundrySalvageCache.xml` already present (08:51). Old UtinniPatches copy `Defs/ThingDefs_Buildings/RUT_FoundrySalvageCache.xml`: NOT in game folder, nothing to delete (remaining UtinniPatches files with that name are the texture png and Patches/RUT_FoundrySalvageCache_SpunstoneStudy.xml, intended). Biomes compose drift for TerminalBiomes: DLL+srchash, RM_TwilightFloraProducts.xml, RM_TwilightUnderstorey.xml, 2 Keyed xml, 10 new Twilight plant PNGs, RM_TollhornCore.png.

## Compose biomes drift (total beyond the above)
Write `+`: Greentide 4 PNG, LongShade RM_EggGulloth.png, _Kits/EnvironmentalHazards RM_DecoyShadeTarp.png. Update `~`: DLL+srchash for DivingInteraction, FeverWood, Stillsand, TerminalBiomes, Warscar, _Kits/CreatureBehaviors, _Kits/EnvironmentalHazards; XML: DivingInteraction RM_SeaDiveGenStepDefs + RM_SeabedGenerators, Greentide RM_GreatboleHarvest_Items + RM_GreatboleGrub, LongShade RM_LongShade_FaunaSupport, Stillsand RM_StilledWater, EnvironmentalHazards RM_DecoyShadeTarp. No deletes (`-`) anywhere.

## Apply commands, in order, at next game-down
```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod UtinniPatches --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod SWBestiary --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply
```
Webwork and TerminalBiomes ride the compose apply. Re-run each without --apply afterwards to confirm no drift.
