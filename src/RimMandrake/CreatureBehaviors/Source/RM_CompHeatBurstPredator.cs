using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// DESERT_BURST_PREDATOR_FLAGSHIP_1. desert.md §4/§10's "nearly native"
    /// burst-then-retreat behaviour: the trigger and the retreat are the two
    /// halves DESERT_SHADE_GRID_KEYSTONE_1 explicitly left for this item
    /// ("a future burst-predator's own attack JobDriver creates this with
    /// HediffMaker.MakeHediff... the same one-line AddHediff idiom
    /// GhoulFrenzy itself uses").
    ///
    /// Polling comp, not a ThinkTree JobGiver — same shape as this
    /// assembly's own RM_CompAquaticAmbusher, and for the same reason: it
    /// needs to fire mid-hunt (while the pawn's current job is vanilla's own
    /// JobDriver_PredatorHunt) without a Harmony patch on that job driver,
    /// and this assembly ships no Harmony dependency (RM_CreatureBehaviors.
    /// csproj's own header).
    ///
    /// Trigger half: no RM_HeatDrivenBurst hediff present + a hostile target
    /// within burstTriggerRangeCells -> HediffMaker.MakeHediff + Severity=1
    /// (the "bursting" stage) + AddHediff. Returns no job — the pawn's own
    /// ThinkTree/JobDriver_PredatorHunt keeps driving the chase, now boosted
    /// by the hediff's own statOffsets/statFactors.
    ///
    /// Retreat half: hediff present and its severity has decayed (via
    /// RM_HediffComp_ShadeDrivenSeverity, ShadeAt-driven) to or below
    /// heatFatigueSeverityThreshold -> if not already standing somewhere
    /// that clears retreatShadeThreshold, force a Goto job toward the
    /// nearest cell that does, within retreatSearchRadiusCells. This does
    /// not "heal" the hediff (both severityPerDayInSun and
    /// severityPerDayInShade are negative — it always decays) — reaching
    /// shade only lets the heat-fatigue tail burn off at the shade rate
    /// (faster) instead of the sun rate.
    /// </summary>
    public class RM_CompHeatBurstPredator : ThingComp
    {
        public RM_CompProperties_HeatBurstPredator Props => (RM_CompProperties_HeatBurstPredator)props;

        public override void CompTick()
        {
            base.CompTick();

            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Map == null || pawn.Downed)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }

            if (!RM_CreatureBehaviorsSettings.heatDrivenBurstEnabled || Props.hediffDef == null)
            {
                return; // mod option: the shared burst/retreat hediff is off — never trigger or retreat
            }

            Hediff burst = pawn.health.hediffSet.GetFirstHediffOfDef(Props.hediffDef);
            if (burst == null)
            {
                TryTriggerBurst(pawn);
                return;
            }

            if (burst.Severity <= Props.heatFatigueSeverityThreshold)
            {
                TryRetreatToShade(pawn);
            }
        }

        private void TryTriggerBurst(Pawn pawn)
        {
            Pawn target = FindHostileTarget(pawn);
            if (target == null)
            {
                return;
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.hediffDef, pawn);
            hediff.Severity = 1f;
            pawn.health.AddHediff(hediff);
        }

        private Pawn FindHostileTarget(Pawn pawn)
        {
            IReadOnlyList<Pawn> pawns = pawn.Map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestDistSq = Props.burstTriggerRangeCells * Props.burstTriggerRangeCells;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == pawn || candidate.Dead || !candidate.Spawned || !pawn.HostileTo(candidate))
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

        private void TryRetreatToShade(Pawn pawn)
        {
            RM_MapComponent_ShadeGrid grid = pawn.Map.GetComponent<RM_MapComponent_ShadeGrid>();
            if (grid == null || grid.ShadeAt(pawn.Position) >= Props.retreatShadeThreshold)
            {
                return; // already shaded enough — sit and let the fatigue tail burn off
            }

            if (pawn.jobs?.curJob != null && pawn.jobs.curJob.def == JobDefOf.Goto)
            {
                return; // already retreating — don't restart the goto every interval tick
            }

            bool found = CellFinder.TryFindRandomCellNear(pawn.Position, pawn.Map, (int)Props.retreatSearchRadiusCells,
                (IntVec3 c) => c.Standable(pawn.Map) && grid.ShadeAt(c) >= Props.retreatShadeThreshold
                    && pawn.Map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)),
                out IntVec3 dest);
            if (!found)
            {
                return;
            }

            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            pawn.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
        }
    }
}
