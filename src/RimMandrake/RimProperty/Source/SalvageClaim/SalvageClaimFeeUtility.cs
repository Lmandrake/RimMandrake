using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Property;

namespace RimMandrake.SalvageClaim
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, salvage-law pass only. Item point 2, "Wreck
    /// rights — fee scaling": derives a claim-fee price purely from the
    /// fabric's own two already-published numbers for a Thing —
    /// RecognizabilityUtility.Score (0..1; spec item 2's decay-RATE driver)
    /// and ClaimEngine.ResolveClaim's resolved ClaimResolution.EffectiveStrength
    /// (0..1, already decayed by ClaimDecay) — rather than inventing a third,
    /// disconnected pricing model. No RimUtinni tuning data exists yet for
    /// this pass (ownership_settlement_spec.md's closing line reserves
    /// "claim-fee pricing" as later, campaign-authored data); the constants
    /// below are generic engine defaults, same spirit as RM_Property's own
    /// PropertyTuning.cs.
    /// </summary>
    public static class SalvageClaimFeeUtility
    {
        // A fully unrecognizable, fully unclaimed Thing (a steel bar with no
        // claim record at all) still costs a nominal admin fee — the gizmo
        // is deliberately never free (spec item 1 frames this whole family
        // as a GRAY ZONE, not a free-for-all).
        private const int MinFeeSilver = 5;

        // A maximally recognizable Thing (named/mechanoid/high-quality/
        // high-value — RecognizabilityUtility.Score saturating at 1.0) with
        // a fresh, undecayed prior claim (EffectiveStrength 1.0): the worst
        // case for "someone is going to notice this is missing."
        private const int MaxFeeSilver = 350;

        // Even at claimStrength 0 (fully decayed, or genuinely never
        // claimed), a highly recognizable Thing still carries this fraction
        // of its recognizability-driven ceiling — a named astromech's serial
        // plate never stops being a serial plate. Keeps a decayed claim on a
        // named droid from pricing identically to a decayed claim on a
        // steel bar; recognizability alone, not just claim strength, is
        // allowed to move the price.
        private const float UnclaimedStrengthFloor = 0.2f;

        public static int ComputeFeeSilver(Thing thing, ClaimResolution? priorClaim)
        {
            float recognizability = Mathf.Clamp01(RecognizabilityUtility.Score(thing));
            float claimStrength = Mathf.Clamp01(priorClaim?.EffectiveStrength ?? 0f);
            float strengthFactor = Mathf.Lerp(UnclaimedStrengthFloor, 1f, claimStrength);
            float riskFactor = recognizability * strengthFactor; // 0..1
            float fee = Mathf.Lerp(MinFeeSilver, MaxFeeSilver, riskFactor);
            return Mathf.Max(1, Mathf.RoundToInt(fee));
        }

        // v1 simplification, per the item spec's "keep it simple" steer: the
        // fee is drawn from the ACTING pawn's own carried silver only, never
        // searched across the whole colony's stockpiles. Vanilla's
        // TradeUtility.LaunchSilver/ColonyHasEnoughSilver pattern (RimWorld/
        // TradeUtility.cs) pulls from launchable colony stock for orbital
        // trade specifically — a different transaction shape (no actor pawn,
        // no "who is paying" concept) that doesn't fit "a player-selected
        // pawn pays a fee." A colony-stockpile draw is a reasonable
        // follow-up, not required for this pass's criteria.
        public static int CountSilverInInventory(Pawn pawn)
        {
            ThingOwner container = pawn?.inventory?.innerContainer;
            if (container == null) return 0;
            return container.TotalStackCountOfDef(ThingDefOf.Silver);
        }

        public static void RemoveSilverFromInventory(Pawn pawn, int amount)
        {
            ThingOwner container = pawn?.inventory?.innerContainer;
            if (container == null || amount <= 0) return;

            int remaining = amount;
            // Snapshot first — Take() mutates the container we're reading.
            List<Thing> silverStacks = container.Where(t => t.def == ThingDefOf.Silver).ToList();
            foreach (Thing stack in silverStacks)
            {
                if (remaining <= 0) break;
                int takeCount = Mathf.Min(remaining, stack.stackCount);
                Thing taken = container.Take(stack, takeCount);
                taken.Destroy();
                remaining -= takeCount;
            }
        }
    }
}
