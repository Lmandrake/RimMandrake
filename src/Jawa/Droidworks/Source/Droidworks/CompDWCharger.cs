using RimWorld;
using Verse;

namespace Droidworks
{
    /// <summary>
    /// { chargeRatePerHour, radius } per DROIDWORKS_CHARGING_TRIO_1's spec.
    /// radius 0 (DW_ChargeSocket, DW_ChargeDock): the building only charges
    /// whichever droid is actively docked there via JobDriver_DWRecharge - this
    /// comp's own CompTick is a no-op for those, by design (see below).
    /// radius > 0 (DW_ChargeNimbus): ambient, room-wide, no job needed - every
    /// droid within range gets topped off passively by CompTick.
    /// </summary>
    public class CompProperties_DWCharger : CompProperties
    {
        public float chargeRatePerHour = 8f;
        public float radius = 0f;

        public CompProperties_DWCharger() => compClass = typeof(CompDWCharger);
    }

    /// <summary>
    /// Backs CompProperties_DWCharger. The active (job-driven) half of charging
    /// lives entirely in JobDriver_DWRecharge, which reads Props.chargeRatePerHour
    /// straight off the building it targets - a radius-0 charger never needs this
    /// comp to tick. The passive nimbus aura below is this comp's only job.
    /// No visuals (sparks/lightning/glow) - explicitly deferred per
    /// design/Jawa/droid_system_spec.md section 5.
    /// </summary>
    public class CompDWCharger : ThingComp
    {
        private const int ScanIntervalTicks = 60;

        public CompProperties_DWCharger Props => (CompProperties_DWCharger)props;

        public override void CompTick()
        {
            if (Props.radius <= 0f) return;
            if (!parent.IsHashIntervalTick(ScanIntervalTicks)) return;

            Map map = parent.Map;
            if (map == null) return;

            float gain = Props.chargeRatePerHour * ScanIntervalTicks / GenDate.TicksPerHour;
            foreach (Thing thing in GenRadial.RadialDistinctThingsAround(parent.Position, map, Props.radius, useCenter: true))
            {
                if (!(thing is Pawn pawn)) continue;
                Need_Power need = pawn.needs?.TryGetNeed<Need_Power>();
                if (need == null || need.CurLevel >= 1f) continue;
                need.CurLevel += gain;
            }
        }
    }
}
