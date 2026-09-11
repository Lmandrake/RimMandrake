using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 3 — the flying half of the fire-hawk's
    /// twig (RUT_ruled_commissions_wave2.md §7c: "fly a short sortie and ignite
    /// one flammable cell N cells beyond the fire's edge").
    ///
    /// TargetA is the fire the ember comes FROM; TargetB is the cell it goes TO.
    /// Four toils: go to the fire's edge, take an ember, carry it out, drop it.
    ///
    /// The ember is not a Thing. Making it one would mean a def, a graphic, a
    /// carry-tracker interaction and a stack of failure cases (what happens when
    /// the hawk is downed mid-flight, does the ember burn the hawk, does it
    /// deteriorate) for a visual that lasts ninety ticks. The flecks thrown in the
    /// take toil are the visual; the job itself is the mechanism.
    ///
    /// FAILURE IS SILENT AND SAFE. If the source fire goes out before the hawk
    /// reaches it, the job fails and nothing is lit — the spread-only law holds on
    /// the way out as well as at the decision (§7c). If the destination has
    /// stopped being flammable by the time the hawk arrives, TryStartFireIn simply
    /// returns false. Either way the cooldown was already charged by the
    /// job-giver, so a hawk cannot thrash against a bad target.
    /// </summary>
    public class JobDriver_RUT_FireHawkCarryEmber : JobDriver
    {
        private const TargetIndex SourceFireInd = TargetIndex.A;
        private const TargetIndex IgniteCellInd = TargetIndex.B;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Nothing is reserved: a fire is not a claimable resource, the
            // destination cell is not owned, and reservations on a wild (or tamed,
            // undrafted) animal's self-directed job buy nothing.
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            // No source fire, no job — this is the spread-only law expressed as a
            // fail condition rather than a decision.
            this.FailOnDespawnedOrNull(SourceFireInd);

            yield return Toils_Goto.GotoThing(SourceFireInd, PathEndMode.Touch)
                                   .FailOnDespawnedOrNull(SourceFireInd);

            Toil takeEmber = Toils_General.Wait(PyrelandsTuning.FireHawkTakeEmberTicks, SourceFireInd);
            takeEmber.FailOnDespawnedOrNull(SourceFireInd);
            takeEmber.tickAction = delegate
            {
                if (pawn.IsHashIntervalTick(15))
                {
                    FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                }
            };
            yield return takeEmber;

            yield return Toils_Goto.GotoCell(IgniteCellInd, PathEndMode.OnCell);

            Toil dropEmber = ToilMaker.MakeToil("RUT_FireHawkDropEmber");
            dropEmber.defaultCompleteMode = ToilCompleteMode.Instant;
            dropEmber.initAction = delegate
            {
                IntVec3 cell = job.GetTarget(IgniteCellInd).Cell;
                if (!cell.IsValid || !cell.InBounds(pawn.Map))
                {
                    return;
                }

                // instigator: the hawk. That is what makes a TAMED hawk's
                // spreading show up as the colony's arson debt in
                // MapComponent_BurnLine — the ruled price of fire-falconry
                // (§7d: "the fire a tamed hawk spreads is still nobody's friend").
                CompFireHawkSpread comp = pawn.TryGetComp<CompFireHawkSpread>();
                float size = comp?.Props.startFireSize ?? PyrelandsTuning.SmoulderFireSize;

                if (FireUtility.TryStartFireIn(cell, pawn.Map, size, pawn))
                {
                    FleckMaker.ThrowFireGlow(cell.ToVector3Shifted(), pawn.Map, 1f);
                }
            };
            yield return dropEmber;
        }
    }
}
