using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// { chargePercentPerHour, radius } per DROIDWORKS_CHARGING_TRIO_1's spec.
    /// radius 0 (RSW_DW_ChargeSocket, RSW_DW_ChargeDock): the building only charges
    /// whichever droid is actively docked there via JobDriver_DWRecharge - this
    /// comp's own CompTick is a no-op for those, by design (see below).
    /// radius > 0 (RSW_DW_ChargeNimbus): ambient, room-wide, no job needed - every
    /// droid within range gets topped off passively by CompTick.
    /// </summary>
    public class CompProperties_DWCharger : CompProperties
    {
        // Renamed from chargeRatePerHour 2026-09-02 (opus code review, pass 3):
        // Need.MaxLevel is 1f, and the old name/value pair (e.g. 25) was consumed
        // directly as fraction-of-bar-per-hour by the code below, which meant a
        // rate of "25" refilled an empty droid in 1/25th of an hour (~2.5 real
        // seconds at 1x speed) - the whole power need was decorative, and every
        // charger tier (25/40/15) was indistinguishable because all three were
        // instantaneous. The XML values (25, 40, 15) were always intended as
        // PERCENT per hour, matching the shipped description text ("slowly top
        // off") and the owner's ruling (combat droids once/day, protocol up to a
        // month) - the field is now named and divided accordingly.
        public float chargePercentPerHour = 8f;
        public float radius = 0f;

        public CompProperties_DWCharger() => compClass = typeof(CompDWCharger);
    }

    /// <summary>
    /// Backs CompProperties_DWCharger. The active (job-driven) half of charging
    /// lives entirely in JobDriver_DWRecharge, which reads Props.chargePercentPerHour
    /// straight off the building it targets - a radius-0 charger never needs this
    /// comp to tick. The passive nimbus aura below is this comp's only job.
    /// No visuals (sparks/lightning/glow) - explicitly deferred per
    /// design/Jawa/droid_system_spec.md section 5.
    /// </summary>
    public class CompDWCharger : ThingComp
    {
        private const int ScanIntervalTicks = 60;

        public CompProperties_DWCharger Props => (CompProperties_DWCharger)props;

        // Fixed 2026-09-02 (opus code review, re-review pass): the original fix
        // only guarded this comp's own CompTick (the radius>0 nimbus path).
        // RSW_DW_ChargeSocket/RSW_DW_ChargeDock (radius 0) are charged entirely
        // by JobDriver_DWRecharge, which consulted nothing about power - a
        // droid would path to and charge from an unpowered or switched-off
        // socket. Hoisted here so both paths share one answer.
        public bool IsOperational
        {
            get
            {
                CompPowerTrader powerComp = parent.GetComp<CompPowerTrader>();
                if (powerComp != null && !powerComp.PowerOn) return false;
                CompFlickable flickComp = parent.GetComp<CompFlickable>();
                if (flickComp != null && !flickComp.SwitchIsOn) return false;
                return true;
            }
        }

        public override void CompTick()
        {
            if (Props.radius <= 0f) return;
            if (!parent.IsHashIntervalTick(ScanIntervalTicks)) return;

            Map map = parent.Map;
            if (map == null) return;
            if (!IsOperational) return;

            float gain = Props.chargePercentPerHour / 100f * ScanIntervalTicks / GenDate.TicksPerHour;
            foreach (Thing thing in GenRadial.RadialDistinctThingsAround(parent.Position, map, Props.radius, useCenter: true))
            {
                if (!(thing is Pawn pawn)) continue;
                // Fixed 2026-09-02: no hostility filter meant a raiding battle droid
                // or a deliberately-starved prisoner got topped off for free.
                if (pawn.HostileTo(parent.Faction)) continue;
                Need_Power need = pawn.needs?.TryGetNeed<Need_Power>();
                if (need == null || need.CurLevel >= 1f) continue;
                need.CurLevel += gain;
            }
        }
    }
}
