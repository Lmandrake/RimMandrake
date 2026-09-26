using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // BIOME_ARRIVAL_NARRATION_1. Same gen-step hook and gravship-arrival
    // detection RimMandrake.GravshipLanding already proved live
    // (src/RimMandrake/GravshipLanding/Source/Patch_GenStep_GravshipMarker.cs):
    // GenStep_GravshipMarker (order 1700) runs exactly once, only on a map
    // generated as a gravship's landing site, and GenStepParms.gravship is
    // non-null only then -- no other map type reaches this gen step with a
    // gravship. Hanging the letter off a postfix on the SAME gen step (rather
    // than inventing a second "was this a landing" signal) means one proven
    // detection drives both mods.
    //
    // Self-contained AccessTools.Method + try/catch shape, same as
    // RM_PollinationGatePatch/RM_Patch_LeachmossWildSpawnGate in this
    // assembly, rather than the central EnvironmentalHazardsMod hook in
    // BiomeGlowPatches.cs -- both patterns are live in this kit; this one
    // needs no shared cache or hot-path bail, so the smaller self-contained
    // shape is the better fit. GenStep_GravshipMarker is a core-assembly type
    // present whether or not Odyssey is active (same posture
    // GravshipLanding's own patch takes); the ModsConfig.OdysseyActive check
    // in the postfix is the runtime gate, not a compile guard, so this mod
    // carries no hard Odyssey dependency.
    [StaticConstructorOnStartup]
    public static class RM_Patch_GravshipArrivalLetter
    {
        static RM_Patch_GravshipArrivalLetter()
        {
            MethodBase target = AccessTools.Method(typeof(GenStep_GravshipMarker), nameof(GenStep_GravshipMarker.Generate));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] biome-arrival-letter: GenStep_GravshipMarker.Generate "
                    + "not found -- rule NOT armed. The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target, postfix: new HarmonyMethod(
                    typeof(RM_Patch_GravshipArrivalLetter), nameof(Generate_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] biome-arrival-letter: patch failed, rule NOT armed. " + e);
            }
        }

        public static void Generate_Postfix(Map map, GenStepParams parms)
        {
            if (!ModsConfig.OdysseyActive || parms.gravship == null || map == null)
            {
                return;
            }

            try
            {
                Current.Game?.GetComponent<RM_GameComponent_BiomeArrivalLetters>()?.Notify_GravshipLanded(map);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RM EnvironmentalHazards] biome-arrival-letter: " + e.Message, 0x8A11A1);
            }
        }
    }
}
