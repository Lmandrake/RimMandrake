using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // CHILL_AIR_PUMP_1: on the Chill seabed RM_CompChillAirSupply makes Odyssey's oxygen pump draw the full
    // chillAirPumpWatts, overriding CompLowPowerInSpace's 10% "low power unless vacuum" mode (the seabed is never
    // a vacuum). Without this postfix vanilla's inspect line kept saying "Power consumption mode: Low" right under
    // "Power needed: 300 W". Here the line says High whenever our comp is the one setting the draw; every other
    // map and every other building keep vanilla's line untouched.
    [HarmonyPatch(typeof(CompLowPowerInSpace), nameof(CompLowPowerInSpace.CompInspectStringExtra))]
    public static class Patch_ChillAirPumpPowerMode
    {
        public static void Postfix(CompLowPowerInSpace __instance, ref string __result)
        {
            RM_CompChillAirSupply air = __instance.parent?.TryGetComp<RM_CompChillAirSupply>();
            if (air != null && air.DrawsFullPower)
            {
                __result = "PowerConsumptionMode".Translate() + ": " + ((string)"PowerConsumptionHigh".Translate()).CapitalizeFirst();
            }
        }
    }
}
