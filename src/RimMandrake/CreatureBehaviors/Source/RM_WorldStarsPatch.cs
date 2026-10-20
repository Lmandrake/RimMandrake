using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY. Owner 2026-10-20: "the stars still rotate around you as though the
    // planet is spinning"; by card: they drift slowly once a year.
    //
    // A postfix on GlobalDrawLayer_Stars.Rotation ONLY. It deliberately does not touch GenCelestial
    // .CurSunPositionInWorldSpace or SunPositionUnmodified, which Alien Worlds - Tidally Locked already patches (a second
    // patch there would stack on it). The stars aim at a FIXED sun (the noon sun of day 0, the same values Alien Worlds'
    // prefix forces when its planet type is active), turned by the yearly drift. The main menu's static starfield
    // (ProgramState.Entry) is left to vanilla. Settings: worldStarsPinned (off = vanilla), worldStarsYearlyDrift (off = frozen).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_WorldStarsPatch
    {
        private static Vector3? fixedSun;

        static RM_WorldStarsPatch()
        {
            try
            {
                MethodInfo target = AccessTools.PropertyGetter(typeof(GlobalDrawLayer_Stars), "Rotation");
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] world stars: GlobalDrawLayer_Stars.Rotation not found; the stars turn daily.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.worldstars").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_WorldStarsPatch), nameof(Postfix_Rotation)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] world stars: patch failed; the stars turn daily: " + e);
            }
        }

        /// <summary>The fixed sun direction the stars aim at: SunPositionUnmodified(day 0, noon, vanilla's start vector).</summary>
        private static Vector3 FixedSun()
        {
            if (fixedSun.HasValue) return fixedSun.Value;
            Vector3 v = new Vector3(0f, 0f, -1f);
            try
            {
                MethodInfo m = AccessTools.Method(typeof(GenCelestial), "SunPositionUnmodified");
                if (m != null) v = (Vector3)m.Invoke(null, new object[] { 0f, 0.5f, new Vector3(0f, 0f, -1f), 0f });
            }
            catch (Exception e)
            {
                Log.Warning("[RM CreatureBehaviors] world stars: fixed sun read failed, using the start vector: " + e.Message);
            }
            fixedSun = v.sqrMagnitude > 1e-6f ? v.normalized : new Vector3(0f, 0f, -1f);
            return fixedSun.Value;
        }

        public static void Postfix_Rotation(ref Quaternion __result)
        {
            if (!RM_CreatureBehaviorsSettings.worldStarsPinned || Current.ProgramState != ProgramState.Playing || Find.TickManager == null)
            {
                return;
            }
            float drift = RM_WorldStarsMath.DriftDegrees(Find.TickManager.TicksAbs, RM_CreatureBehaviorsSettings.worldStarsYearlyDrift);
            __result = Quaternion.AngleAxis(drift, Vector3.up) * Quaternion.LookRotation(FixedSun());
        }
    }
}
