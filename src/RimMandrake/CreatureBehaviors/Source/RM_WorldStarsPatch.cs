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
    // A postfix on GlobalDrawLayer_Stars.Rotation. The stars aim at the PINNED sun, RM_WorldSunPatch.PinnedDirection()
    // (toward the substellar point; for Ash'karr's (0,0) that is (0,0,-1), the noon sun of day 0 that Alien Worlds'
    // prefix forces when its planet type is active), turned by the yearly drift. The sun disc and the planet's lit
    // side are pinned by RM_WorldSunPatch. The main menu's static starfield
    // (ProgramState.Entry) is left to vanilla. Settings: worldStarsPinned (off = vanilla), worldStarsYearlyDrift (off = frozen).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_WorldStarsPatch
    {
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

        public static void Postfix_Rotation(ref Quaternion __result)
        {
            if (!RM_CreatureBehaviorsSettings.worldStarsPinned || Current.ProgramState != ProgramState.Playing || Find.TickManager == null)
            {
                return;
            }
            float drift = RM_WorldStarsMath.DriftDegrees(Find.TickManager.TicksAbs, RM_CreatureBehaviorsSettings.worldStarsYearlyDrift);
            __result = Quaternion.AngleAxis(drift, Vector3.up) * Quaternion.LookRotation(RM_WorldSunPatch.PinnedDirection());
        }
    }
}
