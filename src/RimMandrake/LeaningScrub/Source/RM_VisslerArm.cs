using HarmonyLib;
using System;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1: the shed arm (RM_VisslerArm) is a vanilla ingestible
    // (foodType Meat, rottable), so the engine's own hunger AI finds and eats it. This file is only
    // the Mod Settings gate: with visslerArmFoodEnabled off the arm reports itself not ingestible.
    [StaticConstructorOnStartup]
    public static class RM_VisslerArmPatches
    {
        private static ThingDef armDef;

        static RM_VisslerArmPatches()
        {
            try
            {
                armDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_VisslerArm");
                var target = AccessTools.PropertyGetter(typeof(Thing), "IngestibleNow");
                if (target == null)
                {
                    Log.Error("[RM LeaningScrub] vissler-arm-food: Thing.IngestibleNow not found, rule NOT armed.");
                    return;
                }
                new Harmony("mandrake.rm.leaningscrub").Patch(target,
                    postfix: new HarmonyMethod(typeof(RM_VisslerArmPatches), nameof(IngestibleNow_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] vissler-arm-food: patch failed, rule NOT armed. " + e);
            }
        }

        public static void IngestibleNow_Postfix(Thing __instance, ref bool __result)
        {
            if (__result && armDef != null && __instance.def == armDef
                && !RM_WindCalendar.On(RM_LeaningScrubSettings.visslerArmFoodEnabled))
            {
                __result = false;
            }
        }
    }
}
