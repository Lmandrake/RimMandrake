# belt reviewFW2 2026-10-05
Scope: FlowWorks LiquidTypes, ManyWaters, Pits, SelfTest, Tools

## per-file
- 20 LiquidTypes: 18 already CLEAN (byte-identical to clean mark), skipped. ManyWaters RiverSteamHook/RiverSteamSettings CLEAN, skipped.
- LiquidTypes/RM_LiquidBodyDef.cs: reachable (csproj + Defs/LiquidTypes/LiquidBodyDefs/RM_LiquidBodyRegistry.xml, read by RM_WorldComponent_LiquidTags). Full review: no findings.
- LiquidTypes/RM_LiquidProperties.cs: reachable (csproj + RM_SlimeWhite/RM_WaterFrigid xml, read by LiquidCorrosion/LiquidIgnition). Null damageDef guarded at caller. No findings.
- ManyWaters/RM_NoRecreationalSwimExtension.cs: reachable (csproj + RM_DeepSand.xml, read by patch). Empty marker. No findings.
- ManyWaters/RM_Patch_NoRecreationalSandSwim.cs: reachable (csproj, Harmony PatchAll in RM_Patch_SuperdeepShooting.cs). Null-safe postfix; no findings.
- Pits/Building_PitCover.cs: reachable (csproj + Defs/Pits/ThingDefs/RM_PitCovers.xml thingClass x3, PlaceWorker, Harmony PathGrid postfix). Full review: sprung set before Destroy so path cost restores; pathCost 1 + Normal ticker. No significant findings.
- Pits/Trigger/CompPitCoverTrigger.cs: reachable (RM_PitCovers.xml comps). FIX: RunScan walked the deck twice per cover per scan (IsDeckLead BFS then Deck BFS) -> one flood fill. Perf only.
- Pits/Trigger/PitCoverTier.cs, CompProperties_PitCoverTrigger.cs: reachable (extension/comp in RM_PitCovers.xml). No findings.
- Pits/TerrainMimic/TerrainMimicPrinter.cs: reachable (Building_PitCover.Print fallback). No findings.
- SelfTest/Program.cs: reachable (SelfTest.csproj, runner Utils/selftest_flowworks_stock.py). Arithmetic in comments rechecked (0.52, 0.01/check, 10 checks/h). No findings.
- Tools/generate_liquid_suite.py: reachable (run by hand; cited by Scarlands/validation.py + items). Regenerated to scratch and diffed all 22 outputs: only RM_Propane.xml drifted. DEFECT: Chill flora tags (RM_TheChillShelf/Bed) existed only as a manual post-gen edit, so any regen dropped them and the Chill flora roster would stop spawning. FIX: per-row extra_tags_shallow/deep; regenerated output byte-identical bar stale comments (liquidtypes packageId, registry row list, false ConfigErrors note). ba846ee5c.
- Build: peer had uncommitted Source/ edits, so DLL built from a clean clone of 8856149a6; selftest 77/77; pushed 504640726.
- Marked CLEAN: 11 files (all DIRTY ones in scope). Note: Building_PitCover.IsDeckLead now has no caller (harmless).
