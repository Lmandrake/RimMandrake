# Aerosol wave 3 (2026-10-07), WARSCAR_AEROSOL_SCREEN_1 part 3 remainder

Files changed
- src/RimMandrake/Scarlands/Source/RM_AerosolScreen.cs: `calibrated` prop, calibration pass, haze prefix, Wasteland bridge.
- src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs: `calibrationEnabled` setting (default true), scribed, checkbox.
- csproj unchanged (no new .cs).
- Rebuilt DLL: src/RimMandrake/Scarlands/Assemblies/RimMandrake.Warscar.dll (+ srchash).

(1) Wasteland ash fall: Wasteland does NOT reference Scarlands, so no direct call. Startup-only Harmony bridge
(`RM_AerosolScreenWastelandBridge`, [StaticConstructorOnStartup]) resolves RM_MapComponent_WastelandStorms via
AccessTools.TypeByName and silently skips if the type or private DoFall is missing. DoFall prefix records the map in a
[ThreadStatic], finalizer clears it; PollutionGrid.SetPolluted prefix refuses polluting a screened cell only while that
flag is set. Cinderfelt freshFall memory is not suppressed (germination can still land in a dome).
(2) Haze: it is vanilla Biotech; thought, plant growth, stat part and meditation all funnel through
NoxiousHazeUtility.IsExposedToNoxiousHaze(Thing,IntVec3,Map). One prefix returns false in screened cells (static patch,
PatchAll). Cauldron/Miasma weathers use the vanilla overlay/doToxicBuildup, already covered by the earlier prefixes.
(3) Calibrated: `calibrated` bool default false; live + calibrationEnabled: every 250 ticks (CompTick hash gate, or
CompTickRare for Rare-ticker defs) scrubs 12/255 ToxGas per cell via map.gasGrid.SetDirect, and un-pollutes one random
polluted cell in radius via pollutionGrid.SetPolluted(false). No RM_AerosolScreen_Calibrated def added.

Build: succeeded, 0 warnings, 0 errors.
Unverified: all of it in game; haze prefix actually catching the thought/plant paths; Wasteland bridge firing (log warns
only on exception, silent skip otherwise); scrub/un-pollute rates feel; Harmony resolving private DoFall by name.
