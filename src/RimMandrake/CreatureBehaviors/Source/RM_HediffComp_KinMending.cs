using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_HEALTH_SHARING_1. "A passive hediff comp giving +50% natural-healing
    // severity adjustment while >=2 same-tag kin are within radius."
    //
    // Periodic-aura shape cribbed from this assembly's own
    // RM_HediffComp_LocalGrowthAura (CompPostTickInterval + a staggered
    // ticksUntilCycle counter) — same idiom, substituting an injury-severity
    // nudge on the CARRIER pawn for a plant-growth nudge on nearby cells.
    //
    // Kin identity comes from the carrier's own race RM_WoundLinkExtension
    // (tag/radius/kinMendingMinKin) — the same extension RM_CompWoundLink
    // reads — so a content author wires one extension, not two tagging
    // schemes, to get both mechanisms on a race.
    public class RM_HediffComp_KinMending : HediffComp
    {
        private int ticksUntilCycle;

        public CompProperties_KinMending Props => (CompProperties_KinMending)props;

        public override void CompPostMake()
        {
            base.CompPostMake();
            // Stagger so every kin-mending carrier on a map doesn't all
            // evaluate on the same tick.
            ticksUntilCycle = Rand.RangeInclusive(1, Mathf.Max(1, Props.tickIntervalTicks));
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            if (!RM_CreatureBehaviorsSettings.kinMendingEnabled)
            {
                return; // mod option: kin mending disabled
            }

            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null || pawn.health == null)
            {
                return;
            }

            ticksUntilCycle -= delta;
            if (ticksUntilCycle > 0)
            {
                return;
            }
            ticksUntilCycle = Mathf.Max(1, Props.tickIntervalTicks);

            if (!HasEnoughKinNearby(pawn))
            {
                return;
            }

            ApplyMendingBoost(pawn);
        }

        private static bool HasEnoughKinNearby(Pawn pawn)
        {
            RM_WoundLinkExtension ext = pawn.def.GetModExtension<RM_WoundLinkExtension>();
            if (ext == null || ext.tag.NullOrEmpty())
            {
                return false; // no kin tag configured on this race — never mends
            }

            int found = 0;
            float radiusSq = ext.radius * ext.radius;
            IReadOnlyList<Pawn> allPawns = pawn.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < allPawns.Count; i++)
            {
                Pawn candidate = allPawns[i];
                if (candidate == pawn || candidate.Dead || !candidate.Spawned)
                {
                    continue;
                }

                RM_WoundLinkExtension candidateExt = candidate.def.GetModExtension<RM_WoundLinkExtension>();
                if (candidateExt == null || candidateExt.tag.NullOrEmpty() || candidateExt.tag != ext.tag)
                {
                    continue;
                }

                float distSq = (candidate.Position - pawn.Position).LengthHorizontalSquared;
                if (distSq <= radiusSq)
                {
                    found++;
                    if (found >= ext.kinMendingMinKin)
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        private void ApplyMendingBoost(Pawn pawn)
        {
            float mult = Mathf.Max(0f, RM_CreatureBehaviorsSettings.kinMendingBoostMultiplier);
            float cycleFraction = Props.tickIntervalTicks / 60000f; // GenDate.TicksPerDay
            float healAmount = Props.extraSeverityHealedPerDay * cycleFraction * mult;
            if (healAmount <= 0f)
            {
                return;
            }

            // Hediff_Injury.Heal(float) confirmed via reflection against the
            // actual referenced Assembly-CSharp.dll this pass (RimSage
            // unreachable this session) — same call RM_CompWoundLink uses to
            // reduce the shared victim's own injury, so both mechanisms heal
            // through the identical, verified API.
            List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
            for (int i = hediffs.Count - 1; i >= 0; i--)
            {
                if (hediffs[i] is Hediff_Injury injury && !injury.IsPermanent() && injury.Severity > 0f)
                {
                    injury.Heal(healAmount);
                }
            }
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksUntilCycle, "ticksUntilCycle", 0);
        }
    }
}
