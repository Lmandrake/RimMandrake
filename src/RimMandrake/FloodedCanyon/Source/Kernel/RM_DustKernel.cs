// Verse-free kernel of Peakstorm Light's reversing dust (RM_WeatherOverlay_PeakstormDust.cs): which way the dust
// drifts at a given game tick. SelfTest/Program.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.FloodedCanyon
{
    public static class RM_DustKernel
    {
        // CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1 (owner card 2026-10-08). All PROVISIONAL.
        public const int PeriodTicks = 2400;   // 40 s at 60 tps: one drift + one reversal
        public const int ReverseTicks = 300;   // 5 s of reversed flow at the end of every period
        public const int RampTicks = 60;       // 1 s to swing through zero at each edge

        // +1 = the normal drift, -1 = fully reversed; in between while swinging. 1 when the feature is off.
        public static float Factor(long ticks, bool enabled)
        {
            if (!enabled) return 1f;
            long phase = ticks % PeriodTicks;
            if (phase < 0) phase += PeriodTicks;
            long start = PeriodTicks - ReverseTicks;
            if (phase < start) return 1f;
            long t = phase - start;
            long e = Math.Min(t, ReverseTicks - t);
            float k = e >= RampTicks ? 1f : (float)e / RampTicks;
            return 1f - 2f * k;
        }

        public static bool Reversed(float factor) { return factor < 0f; }
    }
}
