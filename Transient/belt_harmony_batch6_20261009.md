# Harmony batch 6 (GimmeSomeSlack, Stillsand, NO_FEATURE tags)

- Stillsand: no [HarmonyPatch] classes and no PatchAll (manual Harmony.Patch in 3 files) -> nothing to convert, SKIP
- GimmeSomeSlack: PatchAll->PatchApplier.Apply + csproj link, built OK; no PatchFeature tags (no clear gating bool)
- NO_FEATURE tagging pass: scripted, candidates verified by class-body mention + public static bool decl
- tagged 10 clear-gated classes: Abyss FloodedCanyon KeelHoist TerminalBiomes(2) SWBestiary CathedralPass PlantGrowth RiverColors ShipShields; all built; rest of NO_FEATURE multi-setting/unclear, left
