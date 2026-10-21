using System;
using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LOCKED_SEASONS_DEPLOY_CALENDAR_GOES_FLAT. Owner, by card 2026-10-20: "Every tile swings ~15 C with the
    // seasons: what should seasons do?" -> "Remove the swing".
    //
    // Why an XML patch alone is not enough (measured live 2026-10-20, design/RimMandrake/world_physics_audit_2026-10-20.md §8):
    // with Worldbuilder loaded (the full list), GenTemperature.SeasonalShiftAmplitudeAt carries Worldbuilder's PREFIX
    // that returns false (the original body, where Alien Worlds' transpiler reads the planet type's curve, never runs)
    // and Worldbuilder's priority-MaxValue POSTFIX that sets the amplitude from its axial-tilt curve (Normal = vanilla's
    // 3/4/28 at DistanceFromEquatorNormalized). So RM_TidalLock_NoSeasons.xml (the PlanetTypeDef's curve -> 0) is
    // bypassed: home tile 17011 swung with amplitude 8.649 C = Normal at sin(15.92 deg) = 0.274, every sample.
    // BiomesCore adds a priority-400 postfix after it.
    //
    // This POSTFIX runs LAST (Priority.Last, after Worldbuilder and BiomesCore) and returns 0 while the planet is
    // tidally locked (RM_TidalSunGlowPatch.TidalLockActive: 7f.alienworlds.tidallylocked's patch is on
    // CelestialSunGlow, which the mod applies only while its planet type is active). Not locked, or setting off =>
    // whatever the other mods computed. The XML patch stays: it is what flattens seasons on the standalone backend.
    // Setting: tidalLockNoSeasons (default on).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TidalNoSeasonsPatch
    {
        static RM_TidalNoSeasonsPatch()
        {
            try
            {
                MethodBase target = AccessTools.Method(typeof(GenTemperature), nameof(GenTemperature.SeasonalShiftAmplitudeAt),
                    new[] { typeof(PlanetTile) });
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] tidal no-seasons: GenTemperature.SeasonalShiftAmplitudeAt(PlanetTile) not found; "
                        + "seasons stay as the other mods set them.");
                    return;
                }
                var postfix = new HarmonyMethod(typeof(RM_TidalNoSeasonsPatch), nameof(Postfix_SeasonalShiftAmplitudeAt))
                {
                    priority = Priority.Last
                };
                new Harmony("mandrake.rm.creaturebehaviors.tidalnoseasons").Patch(target, postfix: postfix);
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] tidal no-seasons: patch failed; seasons stay as the other mods set them: " + e);
            }
        }

        public static void Postfix_SeasonalShiftAmplitudeAt(ref float __result)
        {
            if (__result == 0f || !RM_CreatureBehaviorsSettings.tidalLockNoSeasons) return;
            if (RM_TidalSunGlowPatch.TidalLockActive()) __result = 0f;
        }
    }
}
