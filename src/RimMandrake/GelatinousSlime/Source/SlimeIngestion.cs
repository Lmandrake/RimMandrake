using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // EATING THE BODY (spec §2).
    //
    // "The universal antitoxin: eating slime instantly cures poisons and most
    //  radiation-analog hediffs — and applies RM_Slimification at stage 1+
    //  severity bump. 🔴 THE WONDROUS AND THE FATAL ARE ONE MECHANISM."
    //
    // Both halves are in this one method on purpose. Split across two
    // outcomeDoers, somebody eventually patches one off and leaves the other,
    // and the mod's central bargain quietly becomes a free heal.
    //
    // 🔑 WHAT COUNTS AS "A POISON" IS READ OFF THE HEDIFF, NOT A defName LIST.
    // HediffDef.isBad plus a hediffClass of Hediff_Injury excluded, plus the
    // vanilla toxic/poison markers — so modded poisons clear too, which is
    // what "universal antitoxin" has to mean in a mod that ships to everyone.
    // ════════════════════════════════════════════════════════════════════
    public class IngestionOutcomeDoer_SlimeDose : IngestionOutcomeDoer
    {
        // [INVENTED] Severity added per ingestion. Roughly: eating enough raw
        // slime to cure yourself puts you a day or so up the ladder.
        private const float SeverityPerDose = 0.06f;

        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (pawn == null || pawn.health == null)
            {
                return;
            }

            try
            {
                CurePoisons(pawn);

                // ...and the fee.
                if (SlimeDefs.Slimification == null || SlimeUtility.IsResistant(pawn))
                {
                    return;
                }
                Hediff slim = pawn.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
                if (slim == null)
                {
                    slim = pawn.health.AddHediff(SlimeDefs.Slimification);
                }
                if (slim != null)
                {
                    slim.Severity = Mathf.Min(0.99f, slim.Severity + SeverityPerDose * Mathf.Max(1, ingestedCount));
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] slime dose: " + e.Message, 0x51A15);
            }
        }

        private static void CurePoisons(Pawn pawn)
        {
            List<Hediff> toRemove = new List<Hediff>();
            List<Hediff> all = pawn.health.hediffSet.hediffs;
            for (int i = 0; i < all.Count; i++)
            {
                Hediff h = all[i];
                if (h == null || h.def == null)
                {
                    continue;
                }
                if (h.def == SlimeDefs.Slimification || h.def == SlimeDefs.SlimeMarked)
                {
                    continue;
                }
                if (IsPoisonLike(h))
                {
                    toRemove.Add(h);
                }
            }
            for (int i = 0; i < toRemove.Count; i++)
            {
                pawn.health.RemoveHediff(toRemove[i]);
            }
        }

        private static bool IsPoisonLike(Hediff h)
        {
            if (h is Hediff_Injury || h is Hediff_MissingPart || h is Hediff_Addiction)
            {
                return false;
            }
            HediffDef def = h.def;
            if (!def.isBad)
            {
                return false;
            }
            // The vanilla toxic family, by def and by the chemical/toxin
            // markers rather than a name list.
            if (def == HediffDefOf.ToxicBuildup || def == HediffDefOf.FoodPoisoning)
            {
                return true;
            }
            if (def.defName.IndexOf("Toxic", StringComparison.OrdinalIgnoreCase) >= 0
                || def.defName.IndexOf("Poison", StringComparison.OrdinalIgnoreCase) >= 0
                || def.defName.IndexOf("Venom", StringComparison.OrdinalIgnoreCase) >= 0
                || def.defName.IndexOf("Radiation", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return true;
            }
            return false;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // THE ANTIDOTE (spec §6).
    //
    // "Clears RM_Slimification at any stage below 1.0, and costs the patient a
    //  short toxic malaise — the cure is honestly a poisoning."
    //
    // 🔴 IT MUST WORK ON A DOWNED OR COMATOSE PATIENT. That is §5d's whole
    // race. Riding CompTargetable_SinglePawn means the DOCTOR is the user and
    // the patient is the target, so nothing about the patient's consciousness
    // is in the way.
    // ════════════════════════════════════════════════════════════════════
    public class CompTargetEffect_SlimeAntidote : CompTargetEffect
    {
        // [INVENTED, spec §6] The honest poisoning.
        private const float ToxicBuildupCost = 0.14f;

        public override void DoEffectOn(Pawn user, Thing target)
        {
            Pawn patient = target as Pawn;
            if (patient == null || patient.Dead || patient.health == null)
            {
                return;
            }

            try
            {
                bool cured = false;
                if (SlimeDefs.Slimification != null)
                {
                    Hediff slim = patient.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
                    if (slim != null && slim.Severity < 1f)
                    {
                        patient.health.RemoveHediff(slim);
                        cured = true;
                    }
                }

                // The cost is paid whether or not there was anything to cure:
                // it is a deliberately toxic injection, and wasting one on a
                // clean patient should sting.
                if (HediffDefOf.ToxicBuildup != null && patient.RaceProps.IsFlesh)
                {
                    HealthUtility.AdjustSeverity(patient, HediffDefOf.ToxicBuildup, ToxicBuildupCost);
                }

                if (cured)
                {
                    Messages.Message(patient.LabelShortCap + " has been purged. The film is dead.",
                                     patient, MessageTypeDefOf.PositiveEvent, false);
                }
                else
                {
                    Messages.Message(patient.LabelShortCap + " was not converting. The antidote is "
                                     + "wasted and they are poisoned for nothing.",
                                     patient, MessageTypeDefOf.NeutralEvent, false);
                }

                parent.Destroy();
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.GelatinousSlime] antidote failed: " + e);
            }
        }
    }
}
