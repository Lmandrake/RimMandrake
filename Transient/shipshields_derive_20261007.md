# ShipShields derives from RM_CompAerosolScreen (2026-10-07)

Files changed (src/RimUtinni/ShipShields/):
- About/About.xml: modDependency + loadAfter mandrake.rm.warscar.
- Source/RimMandrake.Utinni.ShipShields.csproj: Reference RimMandrake.Warscar (..\..\..\RimMandrake\Scarlands\Assemblies\RimMandrake.Warscar.dll, Private=false).
- Source/CompProperties_ShieldParticulateScreen.cs: derives RM_CompProperties_AerosolScreen; radius inherited (ctor sets 9.9), drawDome=false.
- Source/CompShieldParticulateScreen.cs: derives RM_CompAerosolScreen; IsScreenLive = weather-negation setting && (Particulate mode, spawned, powered); Radius = 0 outside particulate mode else base.Radius; own ActiveScreens/IsPositionProtected/Spawn/DeSpawn removed; filth sweep and animal repulsion use Radius.
- Source/HarmonyPatches.cs: both ToxicUtility / ToxicFallout prefixes removed (CheckIntercept and PostGravshipLanded patches kept).
- Assemblies/RimMandrake.Utinni.ShipShields.dll(+.srchash) rebuilt.

Kept: nothing from the two prefixes (RM_AerosolScreenPatches covers both identically). ShieldHazardUtility had no prefixes; unchanged (HasParticulateHazard still toxic fallout + sandRate; RM_PollutionSense not wired in, spec item 2 "toxic half calls it" still owed).
Settings: all three particulate toggles still work.
Build: succeeded, 0 warnings, 0 errors.
Uncertain: base.Radius now also applies RM_WarscarSettings.aerosolScreenRadiusFactor and the global aerosolScreenEnabled switch to the shield; RM prefixes only install once Chotrix/Totchak static ctors run PatchAll (Warscar loaded). Never run in game.
