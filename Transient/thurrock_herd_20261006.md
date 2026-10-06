# GREENTIDE_THURROCK_HERD_BUILD_1 progress 2026-10-06

## status
started

## findings
- Innate-hediff comp ALREADY BUILT: CreatureBehaviors/Source/RM_CompGrantHediff.cs (CompProperties_GrantHediff). Item §3 "new piece" is not new.
- Aura: EnvironmentalHazards HediffComp_PeriodicAreaAttack; buildingMultiplier is per-comp props, not per stage.
- Built: CreatureBehaviors/Source/RM_HediffComp_AggroSeverity.cs (+csproj), Greentide/Source/RM_ThurrockAuraApplier.cs (+csproj, +EH ref), settings in RM_GreentideMod.cs
- Rut fight: RimSage has NO rut field/behaviour in 1.6 -> §5 dropped
- Art: done in _artpipe/_artsrc/RM_Thurrock_{south,east,north}; not installed to Textures
- XML: parse OK, validate_patch 0 errors (3 warns = art texPath not installed). Roster row added. Building...
- winbuild CreatureBehaviors: OK 0 err (DLL includes peer's uncommitted CB files: RM_Building_TractionLance, RM_CompResearchSpecimens, RM_CompTetherPull, csproj/Mod.cs edits)
- winbuild Greentide: OK 0 err

## status
offline build done, uncommitted. Owed: art install (art ledger) for RM_Thurrock; live criteria run; §5 rut dropped (no vanilla rut).
