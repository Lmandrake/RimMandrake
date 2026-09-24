using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// BACTA_REVIVAL_MECHANIC_1. Carries a fresh corpse to a bacta tank and hands it over.
    /// Same shape as vanilla's JobDriver_CarryToBuilding (RimWorld/JobDriver_CarryToBuilding.cs)
    /// — go to it, pick it up, carry it to the tank's interaction cell, hand it over — just
    /// generalised from a live Pawn takee to a Corpse one, because nothing here can walk.
    /// </summary>
    public class JobDriver_CarryCorpseToBactaTank : JobDriver
    {
        private const TargetIndex CorpseInd = TargetIndex.A;

        private const TargetIndex TankInd = TargetIndex.B;

        private Corpse Corpse => (Corpse)job.GetTarget(CorpseInd).Thing;

        private Building_BactaTank Tank => (Building_BactaTank)job.GetTarget(TankInd).Thing;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(Corpse, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(CorpseInd);
            this.FailOnDespawnedNullOrForbidden(TankInd);
            this.FailOn(() => !(bool)Tank.CanAcceptCorpse(Corpse));

            yield return Toils_Goto.GotoThing(CorpseInd, PathEndMode.OnCell);
            yield return Toils_Haul.StartCarryThing(CorpseInd);
            yield return Toils_Goto.GotoThing(TankInd, PathEndMode.InteractionCell);
            yield return Toils_General.WaitWith(TankInd, 60, useProgressBar: true);
            yield return Toils_General.Do(delegate
            {
                Tank.TryAcceptCorpse(Corpse);
            });
        }
    }
}
