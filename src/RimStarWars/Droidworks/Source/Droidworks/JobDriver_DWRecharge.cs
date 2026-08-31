using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// A droid stands at a RSW_DW_ChargeSocket/RSW_DW_ChargeDock (radius-0 chargers only
    /// - RSW_DW_ChargeNimbus charges passively via CompDWCharger.CompTick, no job)
    /// while Need_Power.CurLevel rises at the charger's
    /// CompProperties_DWCharger.chargeRatePerHour. Shaped like
    /// JobDriver_Refuel's goto-then-wait-and-tick pattern rather than
    /// JobDriver_LayDown's - no sleep, no bed thoughts, no posture machinery
    /// this system needs; standing at the interaction cell is enough for v1
    /// ("lies" - a bed-like animation - is a documented follow-up, not built
    /// here, since RSW_DW_ChargeDock ships as a plain Building, not a
    /// Building_Bed).
    /// </summary>
    public class JobDriver_DWRecharge : JobDriver
    {
        private const TargetIndex ChargerInd = TargetIndex.A;

        private Thing Charger => job.GetTarget(ChargerInd).Thing;

        private CompDWCharger ChargerComp => Charger?.TryGetComp<CompDWCharger>();

        private Need_Power PowerNeed => pawn.needs?.TryGetNeed<Need_Power>();

        public override bool TryMakePreToilReservations(bool errorOnFailed) =>
            pawn.Reserve(Charger, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(ChargerInd);

            yield return Toils_Goto.GotoThing(ChargerInd, PathEndMode.InteractionCell).FailOnForbidden(ChargerInd);

            Toil charge = ToilMaker.MakeToil("ChargeAtDock");
            charge.defaultCompleteMode = ToilCompleteMode.Never;
            charge.handlingFacing = true;
            charge.tickAction = delegate
            {
                pawn.rotationTracker.FaceTarget(Charger);
                Need_Power need = PowerNeed;
                CompDWCharger comp = ChargerComp;
                if (need == null || comp == null)
                {
                    ReadyForNextToil();
                    return;
                }
                need.CurLevel += comp.Props.chargeRatePerHour / GenDate.TicksPerHour;
                if (need.CurLevel >= 1f) ReadyForNextToil();
            };
            yield return charge;
        }
    }
}
