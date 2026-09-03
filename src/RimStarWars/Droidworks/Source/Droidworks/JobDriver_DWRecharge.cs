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
    /// CompProperties_DWCharger.chargePercentPerHour. Shaped like
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
                // Fixed 2026-09-02 (opus code review, re-review pass): this never
                // checked power/switch state either - the grid dropping or the
                // charger being flicked off mid-job kept charging for free. End
                // the job the same way a missing comp already does, so the
                // droid re-evaluates (JobGiver_DWRecharge's own IsUsableCharger
                // now excludes an unpowered charger from being picked again).
                if (!comp.IsOperational)
                {
                    ReadyForNextToil();
                    return;
                }
                // Fixed 2026-09-02 (opus code review, pass 3): was chargeRatePerHour
                // consumed as a raw fraction-of-bar-per-hour - a "rate" of 25 refilled
                // an empty droid in ~100 ticks. See CompProperties_DWCharger's own
                // header for the full writeup.
                need.CurLevel += comp.Props.chargePercentPerHour / 100f / GenDate.TicksPerHour;
                if (need.CurLevel >= 1f) ReadyForNextToil();
            };
            yield return charge;
        }
    }
}
