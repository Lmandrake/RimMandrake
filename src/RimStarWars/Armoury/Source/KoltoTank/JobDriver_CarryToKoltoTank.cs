using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace KoltoTank;

public class JobDriver_CarryToKoltoTank : JobDriver
{
    private const TargetIndex TakeeInd = TargetIndex.A;

    private const TargetIndex DropPodInd = TargetIndex.B;

    protected Pawn Takee => (Pawn)job.GetTarget(TargetIndex.A).Thing;

    protected Building_KoltoTank DropPod => job.GetTarget(TargetIndex.B).Thing as Building_KoltoTank;

    public override bool TryMakePreToilReservations(bool errorOnFailed)
    {
        if (pawn.Reserve(Takee, job, 1, -1, null, errorOnFailed))
        {
            return pawn.Reserve(DropPod, job, 1, -1, null, errorOnFailed);
        }
        return false;
    }

    protected override IEnumerable<Toil> MakeNewToils()
    {
        this.FailOnDestroyedOrNull(TargetIndex.A);
        this.FailOnDestroyedOrNull(TargetIndex.B);
        this.FailOnAggroMentalState(TargetIndex.A);
        this.FailOn(() => !DropPod.Accepts(Takee));

        yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.OnCell)
            .FailOnDestroyedNullOrForbidden(TargetIndex.A)
            .FailOnDespawnedNullOrForbidden(TargetIndex.B)
            .FailOn(() => DropPod.GetDirectlyHeldThings().Count > 0)
            .FailOn(() => !Takee.Downed)
            .FailOn(() => !pawn.CanReach(Takee, PathEndMode.OnCell, Danger.Deadly))
            .FailOnSomeonePhysicallyInteracting(TargetIndex.A);

        yield return Toils_Haul.StartCarryThing(TargetIndex.A, subtractNumTakenFromJobCount: true);

        yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.InteractionCell);

        Toil prepare = Toils_General.Wait(500)
            .FailOnCannotTouch(TargetIndex.B, PathEndMode.InteractionCell)
            .WithProgressBarToilDelay(TargetIndex.B);
        yield return prepare;

        yield return new Toil
        {
            initAction = delegate
            {
                // TryAcceptThing can still refuse here (power cut / kolto ran dry
                // between the float-menu offer and arrival) even though
                // DropPod.Accepts(Takee) passed earlier - Accepts does not check
                // power or fuel. A discarded false silently ends the job with the
                // patient still in the carrier's arms and no drop.
                if (!DropPod.TryAcceptThing(Takee))
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _);
                }
            },
            defaultCompleteMode = ToilCompleteMode.Instant
        };
    }

    public override object[] TaleParameters()
    {
        return new object[] { pawn, Takee };
    }
}
