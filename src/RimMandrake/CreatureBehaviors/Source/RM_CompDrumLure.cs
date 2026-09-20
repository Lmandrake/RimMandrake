using System;
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// See RM_CompProperties_DrumLure for the mechanic and why it's new C#.
    ///
    /// Polling comp, not a ThinkTree JobGiver — same shape as this
    /// assembly's own RM_CompAquaticAmbusher / RM_CompHeatBurstPredator, and
    /// for the same reason: it needs to act on a pawn OTHER than the one it
    /// is attached to (forcing a job on the victim) without a Harmony patch,
    /// and this assembly ships no Harmony dependency.
    ///
    /// State machine, polled from CompTick at checkIntervalTicks:
    ///   no lured target  -> stay hidden (BecomeInvisible); scan for a
    ///                       hostile pawn within lureRadiusCells that isn't
    ///                       already carrying luredHediff (someone else's
    ///                       lure, or mid-compulsion already); roll
    ///                       lureChancePerScan — a miss is the sheet's own
    ///                       "appraised, and declined"; a hit applies
    ///                       luredHediff to the victim and forces a plain
    ///                       vanilla Goto job toward the predator's own
    ///                       cell, exactly the way this assembly's own
    ///                       RM_CompHeatBurstPredator.TryRetreatToShade
    ///                       forces a Goto on ITS OWN pawn — reused here on
    ///                       the TARGET instead. No new JobDriver.
    ///   lured target set -> if it died, despawned, left the map, or its
    ///                       marker hediff already expired on its own
    ///                       (HediffCompProperties_Disappears — the lure
    ///                       broke), drop it and go back to hidden/waiting;
    ///                       if it has closed to ambushRangeCells, surface
    ///                       and strike (forced AttackMelee, same idiom as
    ///                       CompProximityHatch.Aggro in the sibling
    ///                       ProximityHatch mod); otherwise keep waiting
    ///                       hidden — the compulsion job itself carries the
    ///                       victim the rest of the way, this comp does not
    ///                       re-issue it every tick.
    /// </summary>
    public class RM_CompDrumLure : ThingComp
    {
        private Pawn luredTarget;

        public RM_CompProperties_DrumLure Props => (RM_CompProperties_DrumLure)props;

        public override void CompTick()
        {
            base.CompTick();

            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Map == null || pawn.Downed)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }

            if (!RM_CreatureBehaviorsSettings.drumLureEnabled)
            {
                // mod option off: drop any in-progress lure (the victim keeps
                // walking wherever it was already headed) and stay visible —
                // the pawn hunts exactly like a normal vanilla predator from
                // here, same degrade-cleanly posture as aquaticAmbushEnabled.
                ClearLure(removeHediff: true);
                BecomeVisible(pawn);
                return;
            }

            if (luredTarget != null)
            {
                TickExistingLure(pawn);
                return;
            }

            TryStartLure(pawn);
        }

        private void TickExistingLure(Pawn pawn)
        {
            if (!StillLured(luredTarget, pawn))
            {
                ClearLure(removeHediff: true);
                BecomeInvisible(pawn);
                return;
            }

            float distSq = (luredTarget.Position - pawn.Position).LengthHorizontalSquared;
            if (distSq <= Props.ambushRangeCells * Props.ambushRangeCells)
            {
                Ambush(pawn, luredTarget);
                return;
            }

            BecomeInvisible(pawn); // still patient, still hidden, still waiting — the compulsion job is doing the work
        }

        private void TryStartLure(Pawn pawn)
        {
            BecomeInvisible(pawn);

            Pawn target = FindLureCandidate(pawn);
            if (target == null)
            {
                return;
            }

            if (!Rand.Chance(Props.lureChancePerScan * RM_CreatureBehaviorsSettings.drumLureChanceMultiplier))
            {
                return; // appraised, and declined — the sheet's own default
            }

            ApplyLuredHediff(target);
            ForceGotoLure(pawn, target);
            luredTarget = target;
        }

        private Pawn FindLureCandidate(Pawn pawn)
        {
            IReadOnlyList<Pawn> pawns = pawn.Map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestDistSq = Props.lureRadiusCells * Props.lureRadiusCells;

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == pawn || !CanBeLured(candidate, pawn))
                {
                    continue;
                }

                float distSq = (candidate.Position - pawn.Position).LengthHorizontalSquared;
                if (distSq <= bestDistSq)
                {
                    bestDistSq = distSq;
                    best = candidate;
                }
            }

            return best;
        }

        // Same targeting convention as RM_CompHeatBurstPredator/
        // RM_CompAquaticAmbusher in this assembly (HostileTo), for
        // consistency across the desert's ambush predators rather than a
        // fresh targeting rule invented for this one comp.
        private bool CanBeLured(Pawn candidate, Pawn pawn)
        {
            if (candidate == null || candidate.Dead || !candidate.Spawned || candidate.Downed || candidate.Map != pawn.Map)
            {
                return false;
            }

            if (!pawn.HostileTo(candidate))
            {
                return false;
            }

            if (Props.luredHediff != null && candidate.health?.hediffSet.GetFirstHediffOfDef(Props.luredHediff) != null)
            {
                return false; // already someone else's lure, or already mid-compulsion
            }

            return true;
        }

        private bool StillLured(Pawn candidate, Pawn pawn)
        {
            if (candidate == null || candidate.Dead || !candidate.Spawned || candidate.Map != pawn.Map)
            {
                return false;
            }

            if (Props.luredHediff == null)
            {
                return true; // no marker configured — trust our own field until ambush/clear
            }

            return candidate.health?.hediffSet.GetFirstHediffOfDef(Props.luredHediff) != null;
        }

        private void ForceGotoLure(Pawn pawn, Pawn target)
        {
            if (target.jobs == null)
            {
                return;
            }

            Job job = JobMaker.MakeJob(JobDefOf.Goto, pawn.Position);
            job.locomotionUrgency = LocomotionUrgency.Walk; // drawn in, not panicked — it thinks it found an easy meal
            target.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
        }

        private void ApplyLuredHediff(Pawn target)
        {
            if (Props.luredHediff == null || target.health == null)
            {
                return;
            }

            if (target.health.hediffSet.GetFirstHediffOfDef(Props.luredHediff) != null)
            {
                return;
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.luredHediff, target);
            target.health.AddHediff(hediff);
        }

        private void Ambush(Pawn pawn, Pawn target)
        {
            ClearLure(removeHediff: true);
            BecomeVisible(pawn);

            if (target.Spawned && pawn.Spawned && target.jobs != null && pawn.jobs != null)
            {
                Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, target);
                pawn.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
            }
        }

        private void ClearLure(bool removeHediff)
        {
            if (removeHediff && luredTarget?.health != null && Props.luredHediff != null)
            {
                Hediff hediff = luredTarget.health.hediffSet.GetFirstHediffOfDef(Props.luredHediff);
                if (hediff != null)
                {
                    luredTarget.health.RemoveHediff(hediff);
                }
            }

            luredTarget = null;
        }

        private void BecomeInvisible(Pawn pawn)
        {
            if (Props.submersionHediff == null || pawn.health == null)
            {
                return;
            }

            if (pawn.health.hediffSet.GetFirstHediffOfDef(Props.submersionHediff) != null)
            {
                return; // already submerged/invisible
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.submersionHediff, pawn);
            pawn.health.AddHediff(hediff); // HediffComp_Invisibility.CompPostPostAdd calls BecomeInvisible(instant: true) itself
        }

        private void BecomeVisible(Pawn pawn)
        {
            if (Props.submersionHediff == null || pawn.health == null)
            {
                return;
            }

            Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(Props.submersionHediff);
            if (hediff == null)
            {
                return; // already visible
            }

            pawn.GetInvisibilityComp()?.BecomeVisible(instant: true);
            pawn.health.RemoveHediff(hediff);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref luredTarget, "luredTarget");
        }
    }
}
