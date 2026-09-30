# CAULDRON_TREE_METAL_YIELD_1 report

- Stubs: two XML comments in `src/RimMandrake/PoisonForest/Defs/ThingDefs_Plants/RM_PoisonForestFlora.xml` (RM_TwistingThornwood, RM_TreeMartyr).
- Seam: `ThingComp.GetAdditionalHarvestYield()`. `JobDriver_PlantWork` calls it on every comp of a `HarvestableNow` plant after the main yield, only when the harvest did not fail (RimSage-confirmed against decompiled 1.6). No Harmony, no ticking, so the mod's no-Harmony stance and the Plant TickLong trap both do not apply.
- Built: `RM_CompMetalYield.cs` (`RM_CompProperties_MetalYield` + comp), `<Compile Include>` added (csproj has EnableDefaultCompileItems false), settings toggle `metalYieldEnabled` + `metalYieldFactor` (0.1-3x) in `RM_PoisonForestMod.cs`, comps on both trees.
- Yield: Steel. Count lerps min->full over growth from harvestMinGrowth to 1, times factor, random-rounded. Thornwood 2->12, martyr 1->6 (wood is 25 / 15). Numbers are my pick; the ruling gave none.
- Build: Windows dotnet Release, 0 warnings, 0 errors; .srchash regenerated.
- Not verified: no live harvest test (no game/bridge by instruction); balance untested.
