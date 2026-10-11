using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // PORTED_BEAST_MECHANICS_REBUILD_1 — see RM_CompMetalEater.cs for the header (moved from SWBestiary by KHORRAK_STEEL_DIET_TIER_1).
    //
    // A metal eater must not wander off and graze, or its diet is decoration.
    // The donor did exactly this, as a prefix on the same method; ours differs
    // only in reading the pawn's comp rather than a static registry, and in
    // being switchable from Mod Settings (both the global toggle and a per-def
    // blockNormalFood, so a future creature can eat metal AND food).
    //
    // Returning false skips the original; the method's Job return stays null,
    // which is exactly "this pawn found no ordinary food to seek". Applied by
    // hand at startup, the way this assembly's other patches are
    // (RM_PinnedSunPatches): a missing target is a warning, never a crash.
    [StaticConstructorOnStartup]
    public static class RM_MetalEaterPatches
    {
        static RM_MetalEaterPatches()
        {
            try
            {
                MethodInfo target = AccessTools.Method(typeof(JobGiver_GetFood), "TryGiveJob");
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] metal eater: JobGiver_GetFood.TryGiveJob not found; "
                        + "a metal eater will also graze ordinary food.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.metaleater").Patch(target,
                    prefix: new HarmonyMethod(typeof(RM_MetalEaterPatches), nameof(Prefix_GetFood)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] metal eater: patch failed; a metal eater will also graze ordinary food: " + e);
            }
        }

        public static bool Prefix_GetFood(Pawn pawn)
        {
            RM_CompMetalEater comp = RM_CreatureBehaviorsSettings.metalEatingEnabled ? pawn?.TryGetComp<RM_CompMetalEater>() : null;
            return !RM_MetalEaterKernel.BlocksNormalFood(RM_CreatureBehaviorsSettings.metalEatingEnabled, comp != null, comp != null && comp.Props.blockNormalFood);
        }
    }
}
