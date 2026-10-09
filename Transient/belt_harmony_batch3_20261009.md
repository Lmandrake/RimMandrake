# Harmony batch 3 (HARMONY_PATCH_RESILIENCE_1)

Skeleton. Mods: RaidRedesigner, DivingInteraction, Aftermath, GizkaStowaway, ExplosiveGrowth, FeverWood. Plus guard check of DeepfireLightsOutCompat, RM_AerosolScreen.

## Status
- edits made to all 6 csproj+callers, Deepfire guarded (try/catch per Patch); Aerosol already try/catch-guarded (left). building
- RaidRedesigner, DivingInteraction, Aftermath, GizkaStowaway, ExplosiveGrowth, FeverWood: PatchAll -> PatchApplier.Apply (no PatchFeature tags, same as batch 2; lint reports NO_FEATURE for them, as for batch 2). All built via winbuild (GizkaStowaway csproj links ..\..\..\RimMandrake\_Shared). GizkaStowaway selftest GREEN; others have none.
- DeepfireLightsOutCompat: the two harmony.Patch calls were UNGUARDED (static ctor); each now try/catch + Log.Warning, flag stays false on failure. LuminousPigment rebuilt.
- RM_AerosolScreen: already inside try/catch with Log.Warning; left.
