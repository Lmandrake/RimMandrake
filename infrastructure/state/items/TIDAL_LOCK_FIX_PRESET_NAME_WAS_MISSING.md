# TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING

Found by `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS`; facts and live readback in
`design/RimMandrake/world_physics_audit_2026-10-20.md` §1 and §5.

With `ferny.worldbuilder` loaded (every full list), Alien Worlds takes the planet type from the save's
`<worldPresetName>`, not its `<alienWorldsFrameworkPlanetType>`. `ASHKARR_DEV_START_2026-10-20.rws` was made on
PAINT (no Worldbuilder), has no preset name, and on the Wave 4 324 list loaded as `Default`: tidal-lock patches
absent, glow 0.68 → 1 → 0.68 → 0 across a day (MEASURED 2026-10-20). Autosave-1/2 and
`XENO_HEADS_REVIEW_2026-10-20.rws` already carry `alienWorldsFrameworkPlanetType = Default`. The live session was
fixed by hand and saved as `Saves\ASHKARR_DEV_START_2026-10-20_LOCKED.rws` (both fields TidallyLocked; original untouched).

## Do
1. Decide which save is the dev start from now on (the `_LOCKED` copy, or re-save the original from a locked session);
   update the pointers in `design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` S13/G12.
2. Make it impossible to forget: add a load-time guard in one of our assemblies (e.g. a postfix after
   AlienWorlds' `PostSaveLoadHook`): when Worldbuilder is the backend, `World_ExposeData_Patch.WorldPresetName`
   is empty and the save's `alienWorldsFrameworkPlanetType` read `TidallyLocked`, set the preset name and call
   `PlanetTypeManager.UpdateActive()`; log one line. Mod setting on by default. Ships with its script check:
   load the original dev save on the full list → `get_Current` = TidallyLocked, `HasAnyPatches` True.
3. Add the readback (`get_Current`, `HasAnyPatches 7f.alienworlds.tidallylocked`) to the post-load harvest so a
   moving sun is caught at load, not by eye.
## criteria
- original dev save loads TidallyLocked on the full list without manual calls (L1 read)
- no save written on the full list reads `alienWorldsFrameworkPlanetType = Default`
