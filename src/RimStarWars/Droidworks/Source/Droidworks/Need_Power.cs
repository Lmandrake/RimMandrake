using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// The droid power need. Minimal but necessary: falls at the race's
    /// cadence, refilled at charging buildings (phase 0: the RSW_DW_ChargeSocket
    /// bill/job). At zero the droid powers down (RSW_DW_PoweredDown hediff is
    /// applied by NeedInterval, not by death - state 3, an object, reboots
    /// only with outside help).
    /// </summary>
    public class Need_Power : Need
    {
        public const float PoweredDownAt = DroidworksKernel.PoweredDownAt;

        // The race's own (last) extension, not the first: XML inheritance APPENDS a child's modExtensions after the family
        // abstract's inherited copy, so GetModExtension (FirstOrDefault) would ignore any race-level powerFallPerDay.
        private DroidworksExtension Ext => DroidworksExtension.OfRace(pawn.def);

        public Need_Power(Pawn pawn) : base(pawn)
        {
            threshPercents = new System.Collections.Generic.List<float> { 0.1f, 0.3f };
        }

        public override int GUIChangeArrow => -1;

        public override void NeedInterval()
        {
            if (IsFrozen) return;
            // MOD_OPTIONS_RETROFIT_1: the need itself is switched off upstream, in
            // Patch_ShouldHaveNeed_Power - a droid with the option off never has
            // this need at all, so nothing here runs for it. The two knobs below
            // are the drain rate and whether an empty bar actually shuts a droid
            // down (off: the bar can sit at zero and the droid keeps working).
            float fall = DroidworksKernel.PowerFallPerInterval(Ext?.powerFallPerDay ?? 0.33f,
                RSW_DroidworksSettings.powerDrainRate); // NeedInterval = 150 ticks; 60000/150 = 400
            CurLevel = DroidworksKernel.PowerAfterFall(CurLevel, fall);
            if (!RSW_DroidworksSettings.powerDownWhenEmpty) return;
            if (DroidworksKernel.ShouldPowerDown(true, CurLevel, pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_PoweredDown)))
            {
                pawn.health.AddHediff(DroidworksDefOf.RSW_DW_PoweredDown);
            }
        }
    }
}
