using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Miasma
{
    // WARDEN_MOTHER_TRAINABLE_GATE_1 (roster: miasma_fauna_roster_2026-09-23.md
    // §6a — "explicitly NOT Rescue and NOT general Haul ... an animal that fails
    // its own trained job is a bug wearing a feature").
    //
    // A pawn carrying RM_HediffComp_SelfTameOnRecord is water-bound, so it is
    // never offered Rescue or Haul in its training tab, and never counts as
    // having learned them (so the trained-job JobGivers never fire either).
    //
    // Targets, MEASURED via RimSage's decompile of 1.6 (2026-09-26), not guessed:
    //  - static Pawn_TrainingTracker.CanAssignToTrain(TrainableDef, ThingDef,
    //    out bool visible, Pawn pawn = null) — the per-pawn-per-def eligibility
    //    both instance overloads funnel into, and what the training tab reads.
    //    visible=false hides the row outright.
    //  - Pawn_TrainingTracker.HasLearned(TrainableDef) — what the trained-job
    //    JobGivers check; belt-and-braces for a pawn that learned either before
    //    this patch existed.
    // Rescue and Haul are NOT TrainableDefOf fields (1.6 TrainableDefOf holds
    // only Tameness/Obedience/Release + five Odyssey defs); they are Core
    // TrainableDefs, resolved by defName via DefDatabase.
    //
    // Blast radius: both postfixes return immediately unless td is one of those
    // two defs AND the pawn carries this one hediff comp. No other animal is
    // touched.
    [StaticConstructorOnStartup]
    public static class RM_WardenYoungTrainableGatePatch
    {
        private static readonly TrainableDef Rescue = DefDatabase<TrainableDef>.GetNamedSilentFail("Rescue");
        private static readonly TrainableDef Haul = DefDatabase<TrainableDef>.GetNamedSilentFail("Haul");

        static RM_WardenYoungTrainableGatePatch()
        {
            if (Rescue == null && Haul == null)
            {
                Log.Warning("[RM Miasma] warden-young trainable gate: neither Rescue nor Haul TrainableDef "
                    + "exists — gate NOT armed.");
                return;
            }

            MethodBase canAssign = AccessTools.Method(typeof(Pawn_TrainingTracker),
                nameof(Pawn_TrainingTracker.CanAssignToTrain),
                new[] { typeof(TrainableDef), typeof(ThingDef), typeof(bool).MakeByRefType(), typeof(Pawn) });
            MethodBase hasLearned = AccessTools.Method(typeof(Pawn_TrainingTracker),
                nameof(Pawn_TrainingTracker.HasLearned), new[] { typeof(TrainableDef) });
            if (canAssign == null || hasLearned == null)
            {
                Log.Error("[RM Miasma] warden-young trainable gate: Pawn_TrainingTracker.CanAssignToTrain/"
                    + "HasLearned not found — gate NOT armed. The engine signature has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.miasma");
                harmony.Patch(canAssign, postfix: new HarmonyMethod(
                    typeof(RM_WardenYoungTrainableGatePatch), nameof(CanAssignToTrain_Postfix)));
                harmony.Patch(hasLearned, postfix: new HarmonyMethod(
                    typeof(RM_WardenYoungTrainableGatePatch), nameof(HasLearned_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM Miasma] warden-young trainable gate: patch failed, gate NOT armed. " + e);
            }
        }

        private static bool IsGated(TrainableDef td, Pawn pawn)
        {
            if (td == null || pawn == null || (td != Rescue && td != Haul))
            {
                return false;
            }
            var hediffs = pawn.health?.hediffSet?.hediffs;
            if (hediffs == null)
            {
                return false;
            }
            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i].TryGetComp<RM_HediffComp_SelfTameOnRecord>() != null)
                {
                    return true;
                }
            }
            return false;
        }

        public static void CanAssignToTrain_Postfix(TrainableDef td, Pawn pawn, ref bool visible,
            ref AcceptanceReport __result)
        {
            if (IsGated(td, pawn))
            {
                visible = false;
                __result = false;
            }
        }

        public static void HasLearned_Postfix(Pawn_TrainingTracker __instance, TrainableDef td, ref bool __result)
        {
            if (__result && IsGated(td, __instance.pawn))
            {
                __result = false;
            }
        }
    }
}
