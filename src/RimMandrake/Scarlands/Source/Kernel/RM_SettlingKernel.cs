// Verse-free kernel of the Settling (MapComponent_Settling): the calm / wind hysteresis counters and the
// buried-ordnance reveal rule. Compiled alone by SelfTest/ScarlandsFuzz.cs; keep it free of Verse/RimWorld/UnityEngine.
namespace RimMandrake.Scarlands
{
    public static class RM_SettlingKernel
    {
        public const int SampleInterval = 250;
        public const int TicksPerHour = 2500;

        // No Settling yet: consecutive calm samples accumulate, any non-calm sample resets.
        public static int NextCalm(int calmTicks, float wind, float calmThreshold)
        {
            return wind < calmThreshold ? calmTicks + SampleInterval : 0;
        }
        public static bool ShouldStart(int calmTicks, float calmHours) { return calmTicks >= calmHours * TicksPerHour; }

        // Settling active: consecutive strong-wind samples accumulate, any other sample resets.
        public static int NextWindy(int windyTicks, float wind, float endWind)
        {
            return wind > endWind ? windyTicks + SampleInterval : 0;
        }
        public static bool ShouldEnd(int windyTicks, float endHours) { return windyTicks >= endHours * TicksPerHour; }

        // A buried cell shows as a clean spot when the film settled round it but not on it: strict wants 60% of the
        // open neighbours filmed, the last look (relaxed) any one. No open neighbour never reveals.
        public static bool RevealOk(int open, int film, bool relaxed)
        {
            if (open == 0) return false;
            return relaxed ? film >= 1 : film >= (int)System.Math.Ceiling(open * 0.6f);
        }
    }
}
