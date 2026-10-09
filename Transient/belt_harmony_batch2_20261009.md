# Harmony batch 2 (HARMONY_PATCH_RESILIENCE_1)

Skeleton; filled per mod below.

## Chosen (by [HarmonyPatch] class count, unconverted, minus GimmeSomeSlack/Cauldron/Stillsand)
LuminousPigment 15, RustCathedral 13 (Hum+Walls assemblies), Scarlands 12, TerminalBiomes 10. HugeThings (11) skipped: already has its own per-class loop (PatchNamespace) that PatchApplier was promoted from.
Pattern: PatchAll -> PatchApplier.Apply(harmony, asm, tag) + csproj Compile Include link. No PatchFeature tags / settings hooks (behaviour preserved; failed class is reported by class name).
Left as-is: manual harmony.Patch(...) in DeepfireLightsOutCompat and RM_AerosolScreen (already inside try/guarded compat bridges).
## Status
- edits made, building
status: built all 5 assemblies OK (LuminousPigment, RustCathedral Hum+Walls, Scarlands, TerminalBiomes); C# selftests untouched (not Harmony-related).
