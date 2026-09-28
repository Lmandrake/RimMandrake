using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_DEDICATED_GRAZER_1 — the burrow itself. Two toils: go to
    /// ground (apply the hediff), then hold until it is safe to come back up.
    ///
    /// "Underground" is represented mechanically, not visually — no new art
    /// or sprite state is owed by this pass (the item's own step 9: art is
    /// follow-up, not a build blocker). RM_Burrowed's statOffsets are what
    /// let "the fire pass over" the pawn instead of killing it, the same
    /// idiom RUT_FurnaceBeast's PERMANENT ArmorRating_Heat/Flammability
    /// stats use for total immunity — applied here only WHILE burrowed.
    /// RUT_Ashwallow's own ThingDef carries no such stats, so it is an
    /// ordinary vulnerable grazer the instant it is caught above ground,
    /// which is the whole point of the mechanic existing.
    ///
    /// Ends on whichever comes first: the fire clears (RM_JobGiver_
    /// BurrowOnFire.FireIsNear goes false — the identical query that started
    /// the job, just answered the other way) or the safety-cap tick count
    /// (RM_BurrowOnFireExtension.maxBurrowTicks). AddFinishAction removes the
    /// hediff on every exit path — safe emergence, timeout, the job being
    /// interrupted by damage or capture, or the pawn dying — so the hediff
    /// can never outlive the job that granted it.
    /// </summary>
    public class RM_JobDriver_Burrow : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Nothing reserved: burrowing is self-directed animal behaviour,
            // not a claim on a resource or a cell anyone else wants.
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => pawn.Dead);

            yield return Toils_General.Do(() => ApplyBurrowedHediff(pawn));

            RM_BurrowOnFireExtension ext = pawn.def.GetModExtension<RM_BurrowOnFireExtension>();
            int maxTicks = ext?.maxBurrowTicks ?? PyrelandsTuning.BurrowMaxTicks;
            float radius = ext?.detectionRadius ?? PyrelandsTuning.BurrowDetectionRadius;

            Toil hide = ToilMaker.MakeToil("RM_BurrowWait");
            hide.defaultCompleteMode = ToilCompleteMode.Never;
            int startTick = -1;
            hide.initAction = () => startTick = Find.TickManager.TicksGame;
            hide.tickAction = () =>
            {
                Map map = pawn.Map;
                bool timedOut = startTick >= 0
                    && Find.TickManager.TicksGame - startTick >= maxTicks;
                bool safeToEmerge = map == null
                    || !RM_JobGiver_BurrowOnFire.FireIsNear(pawn, map, radius);
                if (timedOut || safeToEmerge)
                {
                    ReadyForNextToil();
                }
            };
            hide.AddFinishAction(() => RemoveBurrowedHediff(pawn));
            yield return hide;
        }

        private static void ApplyBurrowedHediff(Pawn pawn)
        {
            if (pawn?.health?.hediffSet == null
                || pawn.health.hediffSet.HasHediff(PyrelandsMechanicsDefOf.RM_Burrowed))
            {
                return;
            }
            Hediff hediff = HediffMaker.MakeHediff(PyrelandsMechanicsDefOf.RM_Burrowed, pawn);
            pawn.health.AddHediff(hediff);
        }

        private static void RemoveBurrowedHediff(Pawn pawn)
        {
            if (pawn?.health?.hediffSet == null)
            {
                return;
            }
            Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(PyrelandsMechanicsDefOf.RM_Burrowed);
            if (hediff != null)
            {
                pawn.health.RemoveHediff(hediff);
            }
        }
    }
}
