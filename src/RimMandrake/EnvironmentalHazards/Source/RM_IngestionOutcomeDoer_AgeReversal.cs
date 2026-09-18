using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, owner card 1 (RULED 2026-09-17): "5
    // biological years off on the first cup, but a pawn can benefit only
    // once per year."
    //
    // VERIFIED THIS PASS (RimSage, 1.6 source index): there is no vanilla
    // IngestionOutcomeDoer for age reversal — the only shipped user is
    // RimWorld/CompBiosculpterPod_AgeReversalCycle.CycleCompleted, whose
    // whole body is:
    //
    //     int num  = (int)(3600000f * pawn.ageTracker.AdultAgingMultiplier);
    //     long val = (long)(3600000f * pawn.ageTracker.AdultMinAge);
    //     pawn.ageTracker.AgeBiologicalTicks = Math.Max(val, pawn.ageTracker.AgeBiologicalTicks - num);
    //     pawn.ageTracker.ResetAgeReversalDemand(Pawn_AgeTracker.AgeReversalReason.ViaTreatment);
    //
    // This doer is that arithmetic with the year count as a field, which is
    // where card 1's "5 years" and "capped at adult" both come from:
    //
    //   * 3600000 ticks = one year (the engine's own constant, used in
    //     Pawn_AgeTracker.AgeBiologicalYears and everywhere else).
    //   * AdultAgingMultiplier scales the reversal for a race that ages at
    //     a different rate, exactly as the pod does — five YEARS to the
    //     player, not five raw years of ticks on a fast-ageing animal.
    //   * Math.Max against AdultMinAge is card 1's cap at adult: a tea can
    //     never make a child of anyone.
    //   * ResetAgeReversalDemand keeps an Ideology age-reversal-demanded
    //     precept honest — the pod does it, so a tea that achieves the same
    //     thing must too, or the colony stays in mood debt for a treatment
    //     it received.
    //
    // THE ONCE-A-YEAR GATE is satedHediff: given at full duration after a
    // successful cup, checked before any reversal. A pawn already carrying
    // it gets nothing — no partial effect, no diminishing scale (card 1
    // SUPERSEDES the "1 year, diminishing within a season" draft). The
    // hediff itself is content (RUT_AgeReversalSated) and carries its own
    // disappearance; this class only names the def its XML hands it.
    // ════════════════════════════════════════════════════════════════════
    public class RM_IngestionOutcomeDoer_AgeReversal : IngestionOutcomeDoer
    {
        private const float TicksPerYear = 3600000f;

        // Card 1: five biological years on the first cup.
        public float yearsReversed = 5f;

        // The "already benefited this year" marker. Null = no gate at all,
        // which card 1 forbids for the tea — ConfigErrors cannot reach an
        // IngestionOutcomeDoer, so a null here logs once at use time rather
        // than silently shipping an uncapped fountain of youth.
        public HediffDef satedHediff;

        // One in-game year. 60000 ticks/day * 60 days = 3,600,000.
        public int satedDurationTicks = 3600000;

        // Humanlikes only by default: the tea is a colonist ritual, and an
        // animal's age curve is a different design question nobody has
        // ruled on.
        public bool humanlikeOnly = true;

        // Shown to the player when a sated pawn drinks anyway, so the cup
        // reads as wasted rather than broken.
        public bool messageOnWasted = true;

        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (pawn?.ageTracker == null)
            {
                return;
            }

            if (humanlikeOnly && !pawn.RaceProps.Humanlike)
            {
                return;
            }

            if (satedHediff == null)
            {
                Log.ErrorOnce("[RM EnvironmentalHazards] RM_IngestionOutcomeDoer_AgeReversal has no "
                    + "satedHediff — the once-per-year gate owner card 1 requires is NOT armed on "
                    + (ingested?.def?.defName ?? "an unknown ingestible") + ".", 0x5A6E01);
            }
            else if (pawn.health?.hediffSet != null && pawn.health.hediffSet.HasHediff(satedHediff))
            {
                if (messageOnWasted && PawnUtility.ShouldSendNotificationAbout(pawn))
                {
                    Messages.Message(
                        pawn.LabelShortCap + " drank the brew, but their body is still saturated from "
                        + "the last cup — nothing happened.",
                        pawn, MessageTypeDefOf.NeutralEvent, historical: false);
                }
                return;
            }

            long before = pawn.ageTracker.AgeBiologicalTicks;
            long reversal = (long)(TicksPerYear * Math.Max(0f, yearsReversed) * pawn.ageTracker.AdultAgingMultiplier);
            long adultFloor = (long)(TicksPerYear * pawn.ageTracker.AdultMinAge);

            pawn.ageTracker.AgeBiologicalTicks = Math.Max(adultFloor, before - reversal);
            long actual = before - pawn.ageTracker.AgeBiologicalTicks;

            if (actual <= 0L)
            {
                // Already at or under the adult floor: the cup did nothing,
                // so it does not burn the pawn's once-a-year allowance
                // either.
                if (messageOnWasted && PawnUtility.ShouldSendNotificationAbout(pawn))
                {
                    Messages.Message(
                        pawn.LabelShortCap + " is already as young as the brew can make anyone.",
                        pawn, MessageTypeDefOf.NeutralEvent, historical: false);
                }
                return;
            }

            pawn.ageTracker.ResetAgeReversalDemand(Pawn_AgeTracker.AgeReversalReason.ViaTreatment);

            if (satedHediff != null)
            {
                Hediff sated = HediffMaker.MakeHediff(satedHediff, pawn);
                HediffComp_Disappears disappears = (sated as HediffWithComps)?.TryGetComp<HediffComp_Disappears>();
                if (disappears != null && satedDurationTicks > 0)
                {
                    // SetDuration, not a bare ticksToDisappear write: the
                    // comp keeps disappearsAfterTicks as the denominator for
                    // its own Progress/label, and setting only the countdown
                    // leaves the tooltip reading against the XML default.
                    disappears.SetDuration(satedDurationTicks);
                }
                pawn.health.AddHediff(sated);
            }

            if (PawnUtility.ShouldSendNotificationAbout(pawn))
            {
                Messages.Message(
                    pawn.LabelShortCap + " shed " + (actual / TicksPerYear).ToString("0.#")
                    + " years of biological age.",
                    pawn, MessageTypeDefOf.PositiveEvent, historical: false);
            }
        }

        public override IEnumerable<StatDrawEntry> SpecialDisplayStats(ThingDef parentDef)
        {
            yield return new StatDrawEntry(
                StatCategoryDefOf.BasicsNonPawn,
                "Biological age reversed",
                yearsReversed.ToString("0.#") + " years",
                "Subtracted from the drinker's biological age, never below adulthood. A drinker can "
                + "benefit only once per year; another cup inside that year does nothing.",
                4000);
        }
    }
}
