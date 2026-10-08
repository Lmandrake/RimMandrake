using System.Linq;
using HarmonyLib;
using RimMandrake.StarWars.Armoury;
using RimWorld;
using Verse;
using Verse.AI;

namespace InstantHealingDrug;

[HarmonyPatch(typeof(JobGiver_TakeCombatEnhancingDrug), "TryGiveJob")]
public static class TCED_TryGiveJob_Patch
{
    [HarmonyPrefix]
    private static void Prefix(Pawn pawn, ref bool __state, ref bool ___onlyIfInDanger, ref Job __result)
    {
        // MOD_OPTIONS_RETROFIT_1: __state must be captured even when the
        // mechanic is off — the postfix restores ___onlyIfInDanger from it
        // unconditionally, and a skipped capture would write a default
        // false back onto the vanilla job giver's own field.
        __state = ___onlyIfInDanger;
        if (!RSW_ArmourySettings.instantHealEnabled)
        {
            return;
        }
        Thing drug = pawn.inventory.FindCombatEnhancingDrug();
        CompDrug comp = drug?.TryGetComp<CompDrug>();
        ___onlyIfInDanger = RSW_CombatKernel.ForceOnlyInDanger(true, comp != null && comp.Props is CompProperties_DrugInstantHeal, ___onlyIfInDanger);
    }

    [HarmonyPostfix]
    private static void Postfix(Pawn pawn, ref bool __state, ref bool ___onlyIfInDanger, ref Job __result)
    {
        ___onlyIfInDanger = __state;
        if (!RSW_ArmourySettings.instantHealEnabled)
        {
            return;
        }
        bool plumbingOk = InstantHealingDrug.VerbSelfHediffType != null && InstantHealingDrug.VSH_inDangerField != null && pawn != null
            && pawn.equipment != null && pawn.apparel != null && pawn.VerbTracker?.AllVerbs != null;
        if (!plumbingOk || !RSW_CombatKernel.InstantHealDue(true, __result != null, true, Find.TickManager.TicksGame, pawn.mindState.lastHarmTick,
            RSW_ArmourySettings.InstantHealRecentHarmTicks, pawn.mindState.lastTakeCombatEnhancingDrugTick, RSW_ArmourySettings.InstantHealReuseTicks))
        {
            return;
        }
        Verb verb = pawn.equipment.AllEquipmentVerbs.Concat(pawn.apparel.AllApparelVerbs)
            .FirstOrDefault((Verb t) => InstantHealingDrug.VerbSelfHediffType.IsInstanceOfType(t)
                && (bool)InstantHealingDrug.VSH_inDangerField.GetValue(t.verbProps));
        if (verb != null)
        {
            Job job = JobMaker.MakeJob(JobDefOf.UseVerbOnThingStatic, pawn);
            job.verbToUse = verb;
            __result = job;
            pawn.mindState.lastTakeCombatEnhancingDrugTick = Find.TickManager.TicksGame;
        }
    }
}
