# Scarlands code review — 2026-10-07 (FOUNDRY, offline, source-only; nothing run in game)

Files: `src/RimMandrake/Scarlands/Source/` RM_AerosolScreen.cs, RM_WarscarRings.cs, RM_WarscarSalvage.cs, RM_GlowerShield.cs

## Reachability
All four are listed in `RM_Warscar.csproj` `<Compile Include>` (lines 59-62). Each has live callers:
- AerosolScreen: XML `RM_AerosolScreen.xml` (comp), `RM_Warscar.xml` + `Patches/RM_AerosolScreen_PollutedBiomes.xml` (biome extension); C# `RM_Settling.cs:135`, `RM_GeigerChoir.cs:53-55`; Harmony patches via PatchAll.
- WarscarRings: `RM_WarscarProjectors.xml` (ring + analyzable comps), `GenStepDefs/RM_WarscarRings.xml`.
- WarscarSalvage: `JobDefs/RM_RingSalvageJobs.xml` (designations, jobs, workgivers); designations used by the ring gizmos.
- GlowerShield: `RM_GlowerShielding.xml` (comp, placeworker), `Patches/RM_GlowerShielding.xml` (stat part).

Engine signatures checked in RimSage: `ToxicUtility.DoAirbornePawnToxicDamage(Pawn p, float)`, `DoPawnToxicDamage(Pawn p, float extraFactor)`,
`GameCondition_ToxicFallout.DoCellSteadyEffects(IntVec3 c, Map map)`, `NoxiousHazeUtility.IsExposedToNoxiousHaze(Thing, IntVec3 cell, Map map)`,
`PollutionGrid.SetPolluted(IntVec3 cell, bool isPolluted, bool silent)`, `CanUnpollute`, `GasGrid.SetDirect(IntVec3, byte x4)`, `DensityAt(IntVec3, GasType)`,
`Pawn.GetInspectString` (declared override), `CompAnalyzableUnlockResearch.CanInteract(Pawn, bool)`. All match. Wasteland `DoFall` is private, exists, and calls `SetPolluted(c, true, silent: true)`.

## Cross-cutting (found while reviewing; fix is in RM_Totchak.cs)
**SIGNIFICANT, FIXED.** `RM_Chotrix.cs:128` and `RM_Totchak.cs:89` both ran `PatchAll` over the WHOLE assembly under two different Harmony ids. Harmony dedupes only per owner, so every `[HarmonyPatch]` in the assembly was applied twice. Effects in the reviewed files: the glower prefix multiplied `extraFactor` by 0.5 twice (x0.25, not x0.5), and the "Screened from airborne toxins" inspect line printed twice. Also doubles every older RM_WarscarPatches patch (any non-idempotent one there is affected too).
Fix: `RM_TotchakPatches` no longer patches (comment explains); RM_ChotrixPatches' single PatchAll covers the assembly. **This dirties RM_Totchak.cs**, which was not in scope.

## RM_AerosolScreen.cs
**SIGNIFICANT, FIXED: static `ActiveScreens` aliased across save loads.** `Thing.Map` is `Find.Maps[mapIndexOrState]` (RimSage, Thing.cs). Loading another save in the same session never despawns the old game's things, so their comps stay in the static list with `Spawned == true` and `Map` = the NEW game's map at the same index. `IsPositionScreened` then honoured phantom screens from the previous game (toxin/fallout/haze immunity at their old positions) and kept the old game alive in memory. (Removing a map mid-game is harmless: `Notify_MyMapRemoved` makes `Map` null.)
Fix: the comp records `registeredMap` at spawn; `IsPositionScreened` compares that reference; `PostSpawnSetup` prunes entries whose map is not in `Find.Maps` or whose parent is not spawned there.
Remaining, not significant: per-call `GetComp` lookups in `IsScreenLive` (few screens); Wasteland bridge's `[ThreadStatic]` flag is fine (main-thread only). Settings gating complete (`aerosolScreenEnabled` on every prefix, dome, calibration; `calibrationEnabled` on the scrub).
Verdict after fix: no remaining significant findings.

## RM_WarscarRings.cs
No significant findings. Ring condition and evaluated flag are scribed (`ringCond`, `ringEvaluated`); salvaged ring carries condition through the minified inner thing's ExposeData; `wakeCached` is derived and recomputed each TickRare (on load it may read false for up to 250 ticks if the engine spawns later; cosmetic). `ThingDefOf.GravEngine` null-checked. Gizmos guard `parent.Spawned` before touching the designation manager; designations have `removeIfBuildingDespawned`. Salvaged def has `minifiedDef`, so `MakeMinified` cannot return null. `shipWakesLine`, `ringSalvageEnabled` gated.

## RM_WarscarSalvage.cs
No significant findings. Jobs reserve targets, carry `FailOnDespawnedNullOrForbidden` + `FailOnCannotTouch`; salvage/repair also fail on `ringSalvageEnabled` off. Repair: `StartCarryThing(B, false, true, true)` with `job.count = 2` fails cleanly if the stack shrank; carried components destroyed on completion. Minor: workgivers call `DefDatabase<JobDef>.GetNamed` per call (cheap, not a defect); `Make` in RepairRing ignores `JobDefToUse` (same def).

## RM_GlowerShield.cs
**SIGNIFICANT, FIXED:** same cross-save static registry aliasing as the aerosol screen (`live` list; read by a StatPart constantly). Same fix (`registeredMap`, compare reference, prune on spawn).
The doubled damage prefix (x0.25) is the cross-cutting finding above, fixed in RM_Totchak.cs.
Otherwise fine: empty-registry fast exit; `glowerShieldingEnabled` gated in `For`; panel is Standable, so `GetRoom` resolves; the placeworker is sound.
Verdict after fix: no remaining significant findings.

## Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Scarlands/Source/RM_Warscar.csproj` → Build succeeded, 0 warnings, 0 errors.
DLL `src/RimMandrake/Scarlands/Assemblies/RimMandrake.Warscar.dll` (+ .srchash) left uncommitted. The stamp reads `b46ac5a8646f+dirty`, so rebuild after committing the source to get a clean stamp.

## mark-clean commands (run after the window commits the source)
```
python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/Scarlands/Source/RM_AerosolScreen.cs
python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/Scarlands/Source/RM_WarscarRings.cs
python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/Scarlands/Source/RM_WarscarSalvage.cs
python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/Scarlands/Source/RM_GlowerShield.cs
```
NOT for RM_Totchak.cs: only its patch class was touched, and the rest of that file has not been reviewed.
