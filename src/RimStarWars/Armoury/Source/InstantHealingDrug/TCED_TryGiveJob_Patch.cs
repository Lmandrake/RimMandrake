using System.Linq;
using HarmonyLib;
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
        __state = ___onlyIfInDanger;
        Thing drug = pawn.inventory.FindCombatEnhancingDrug();
        if (drug != null)
        {
            CompDrug comp = drug.TryGetComp<CompDrug>();
            if (comp != null && comp.Props is CompProperties_DrugInstantHeal)
            {
                ___onlyIfInDanger = true;
            }
        }
    }

    [HarmonyPostfix]
    private static void Postfix(Pawn pawn, ref bool __state, ref bool ___onlyIfInDanger, ref Job __result)
    {
        ___onlyIfInDanger = __state;
        if (__result != null || InstantHealingDrug.VerbSelfHediffType == null
            || InstantHealingDrug.VSH_inDangerField == null || pawn == null
            || pawn.equipment == null || pawn.apparel == null || pawn.VerbTracker?.AllVerbs == null
            || Find.TickManager.TicksGame - pawn.mindState.lastHarmTick > 2500
            || Find.TickManager.TicksGame - pawn.mindState.lastTakeCombatEnhancingDrugTick < 20000)
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
