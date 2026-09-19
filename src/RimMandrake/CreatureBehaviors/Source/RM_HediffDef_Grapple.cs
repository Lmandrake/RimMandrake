using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. Tuning for RM_Hediff_Grappled — a custom
    // HediffDef subclass (not a DefModExtension) because this tuning belongs
    // to the HEDIFF itself, one per grapple "flavor" a content mod wants,
    // never to the grappler's race (a race can carry more than one grapple
    // hediff for different tools/severities without a shared tag scheme).
    //
    // Delivery is a single vanilla mechanism, zero Harmony, zero custom Verb:
    // a DamageDef's own <additionalHediffs> (Verse.DamageDefAdditionalHediff,
    // RimSage-verified this pass against Pawn_HealthTracker.PostApplyDamage)
    // adds this hediff to the victim the instant a grapple-capable tool lands
    // a hit — see RM_Grapple_ToolCapacity.xml / RM_Grapple_DamageDefs.xml for
    // the ToolCapacityDef/ManeuverDef/DamageDef trio a race's pincer tool
    // routes through, same shape as UtinniPatches' RUT_FlamefangBite trio.
    public class RM_HediffDef_Grapple : HediffDef
    {
        /// <summary>Severity added to the hold each round the victim isn't
        /// freed, scaled by the GRAPPLER's own Pawn.BodySize — a bodySize-4
        /// Grabber crushes harder per round than a bodySize-1 one would,
        /// with zero per-species tuning needed. INVENTED: 0.08 — a handful
        /// of rounds (see roundIntervalTicks) climbs through this hediff's
        /// own stages toward its lethalSeverity at a body size around 4,
        /// matching Grabber's own remade bodySize.</summary>
        public float severityGainPerRoundPerBodySize = 0.08f;

        /// <summary>Ticks between one crush "round" and the next. INVENTED:
        /// 300 (~5 seconds) — frequent enough to read as an ongoing crush,
        /// not a once-a-minute tick.</summary>
        public int roundIntervalTicks = 300;

        /// <summary>Chance the victim breaks free on any given round,
        /// checked BEFORE that round's severity gain (a successful escape
        /// skips the crush entirely). INVENTED: 0.05 — the hold is meant to
        /// be genuinely dangerous, not a coin-flip escape every few seconds.</summary>
        public float escapeChancePerRound = 0.05f;

        /// <summary>Cells the grappler is allowed to be from the victim
        /// before the hold breaks on its own — the grappler wandering,
        /// being hauled off, or the victim being carried away all end the
        /// hold without either side needing to "kill" anything. INVENTED:
        /// 1.5 — adjacent-only, matching a melee pincer's actual reach.</summary>
        public float releaseRadius = 1.5f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (severityGainPerRoundPerBodySize < 0f)
            {
                yield return "RM_HediffDef_Grapple severityGainPerRoundPerBodySize must be >= 0.";
            }

            if (roundIntervalTicks <= 0)
            {
                yield return "RM_HediffDef_Grapple roundIntervalTicks must be > 0.";
            }

            if (escapeChancePerRound < 0f || escapeChancePerRound > 1f)
            {
                yield return "RM_HediffDef_Grapple escapeChancePerRound must be between 0 and 1.";
            }

            if (releaseRadius <= 0f)
            {
                yield return "RM_HediffDef_Grapple releaseRadius must be > 0.";
            }
        }
    }
}
