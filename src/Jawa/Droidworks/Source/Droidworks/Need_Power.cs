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
        public const float PoweredDownAt = 0.02f;

        private DroidworksExtension Ext =>
            pawn.def.GetModExtension<DroidworksExtension>();

        public Need_Power(Pawn pawn) : base(pawn)
        {
            threshPercents = new System.Collections.Generic.List<float> { 0.1f, 0.3f };
        }

        public override int GUIChangeArrow => -1;

        public override void NeedInterval()
        {
            if (IsFrozen) return;
            float fall = (Ext?.powerFallPerDay ?? 0.33f) / 400f; // NeedInterval = 150 ticks; 60000/150 = 400
            CurLevel = Mathf.Max(0f, CurLevel - fall);
            if (CurLevel <= PoweredDownAt && !pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_PoweredDown))
            {
                pawn.health.AddHediff(DroidworksDefOf.RSW_DW_PoweredDown);
            }
        }
    }
}
