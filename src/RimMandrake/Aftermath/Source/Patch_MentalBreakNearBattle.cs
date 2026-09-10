using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Aftermath
{
    // design/Jawa/proposals/plot_mechanisms_wave.md Part 2, rule 6 ("Zizzik's
    // aftermath"): "a mental break within 2 days after a battle while Zizzik
    // >= Content." Own postfix on the SAME vanilla seam Ninefold's own
    // Patch_MentalBreakStarted already patches (Verse.AI.MentalStateHandler.
    // TryStartMentalState, verified via rimsage) -- two independent Harmony
    // ids patching one vanilla method is the standard, safe way unrelated
    // mods share a seam; this file never touches Ninefold's own patch.
    //
    // Filtered exactly the way Ninefold's own hook is (see
    // Ninefold/Source/Patch_MentalBreakStarted.cs's MentalBreakUtility.
    // ApplyBreakDelta): player humanlike colonists only -- a raider's
    // berserk or a wild animal's manhunter state is not "our" mental break,
    // and this rule only cares whether OUR crew is fraying near a battle.
    [HarmonyPatch(typeof(MentalStateHandler), nameof(MentalStateHandler.TryStartMentalState))]
    public static class Patch_MentalBreakNearBattle
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, Pawn ___pawn)
        {
            if (!__result) return;
            if (___pawn == null || ___pawn.RaceProps == null || !___pawn.RaceProps.Humanlike) return;
            if (___pawn.Faction != Faction.OfPlayer) return;

            AftermathRuleRunner.Instance?.OnMentalBreakNearBattle(___pawn);
        }
    }
}
