using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pits
{
    // Section 4 of covered_pit_traps_spec.md: "Escape is a struggle clock,
    // not a coin flip: each interval the occupant attempts a climb; odds
    // scale with (bodysize - pit depth tier), health %, and manipulation;
    // each failed attempt costs a little health/stamina (thrashing)."
    //
    // The spec names the three inputs and their DIRECTION (bigger body vs a
    // shallower pit is easier; more health is easier; more manipulation is
    // easier) but not a formula or curve. This is the one genuine open
    // design call in the escape mechanic - the formula below is a
    // placeholder that respects every stated direction and clamps to a
    // sane [0.02, 0.95] range, explicitly NOT a tuned value. The quicktest
    // matrix (squirrel/human/thrumbo/centipede x cover tiers) is where this
    // gets checked against the intended feel ("a healthy thrumbo in a
    // shallow pit is out in seconds and ANGRY; a wounded raider in a deep
    // pit is yours").
    public static class PitEscapeUtility
    {
        public const int StruggleIntervalTicks = 2500; // one in-game hour

        public static float EscapeChance(Pawn pawn, PitDepthTier depthTier)
        {
            float bodySize = pawn.BodySize;
            float depthPenalty = (float)depthTier; // Shallow=1, Deep=2, Chasm=3
            float bodyFactor = Mathf.Clamp01((bodySize - depthPenalty + 1.5f) / 3f);

            float healthPct = pawn.health?.summaryHealth?.SummaryHealthPercent ?? 1f;

            float manipulation = pawn.health?.capacities != null
                ? pawn.health.capacities.GetLevel(PawnCapacityDefOf.Manipulation)
                : 1f;

            float chance = 0.05f + 0.55f * bodyFactor + 0.25f * healthPct + 0.15f * manipulation;
            return Mathf.Clamp(chance, 0.02f, 0.95f);
        }

        // Cost of a FAILED attempt - "each failed attempt costs a little
        // health/stamina (thrashing)". A small direct pain/exertion hit
        // rather than real damage, so a long-held healthy occupant does not
        // simply bleed out from trying.
        public static void ApplyFailedAttemptCost(Pawn pawn)
        {
            HealthUtility.AdjustSeverity(pawn, RMPits_HediffDefOf.RM_PinnedInPit, 0.02f);
        }
    }
}
