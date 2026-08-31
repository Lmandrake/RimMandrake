using HarmonyLib;
using Verse;
using Verse.AI;

namespace MentalBreakBlocker;

[StaticConstructorOnStartup]
public class MentalBreakBlocker
{
    static MentalBreakBlocker()
    {
        Log.Message("[MentalBreakBlocker] Now active");
        new Harmony("kaitorisenkou.MentalBreakBlocker").Patch(
            AccessTools.Method(typeof(MentalStateHandler), "TryStartMentalState"),
            prefix: new HarmonyMethod(typeof(MentalBreakBlocker), nameof(Patch_TryStartMentalState)));
        Log.Message("[MentalBreakBlocker] Harmony patch complete!");
    }

    public static bool Patch_TryStartMentalState(ref bool __result, Pawn ___pawn, MentalStateDef stateDef, bool causedByMood, bool causedByDamage, bool causedByPsycast)
    {
        if (___pawn == null)
        {
            return true;
        }
        foreach (Hediff hediff in ___pawn.health.hediffSet.hediffs)
        {
            ModExtension_MentalBreakBlocker modExtension = hediff.def.GetModExtension<ModExtension_MentalBreakBlocker>();
            if (modExtension != null && modExtension.IsBlocked(causedByMood, causedByDamage, causedByPsycast))
            {
                __result = false;
                return false;
            }
        }
        return true;
    }
}
