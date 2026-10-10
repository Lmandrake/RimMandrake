// Attribution accounting (MUST 2, SHOULD 1, review item 12): hook sequences replayed through the PRODUCTION
// JawaBenchTpsStages that JawaBenchTpsProfiler's Harmony hooks call.
using S = JawaBench.BridgeTools.JawaBenchTpsStages;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private const double Freq = 10_000_000.0;   // Stopwatch ticks per second on Windows (QPC 10 MHz)
        private static long Tk(double seconds) => (long)(seconds * Freq);

        private static void T_StagesSkipSafe()
        {
            // a postfix/finalizer whose prefix never ran sees __state = 0: it must record NOTHING, and say so
            var s = new S(Freq);
            long now = Tk(86400);                       // a day of uptime
            s.End(S.CNormal, 0, now);
            s.TickBegin();
            s.TickEnd(0, now, 1000);
            Check(s.Total(S.CNormal) == 0 && s.Total(S.CTick) == 0,
                  "an End with no recorded start fabricated " + s.Total(S.CNormal) / Freq + " s (tl:Normal) / " +
                  s.Total(S.CTick) / Freq + " s (tick)");
            string f = s.TakeWindowFields(0);
            Check(f.Contains("\"profSkipped\":2"), "unstarted ends are counted as profSkipped: " + f);
            Emit("stages-skip", "{" + f + "}");
        }

        private static void T_StagesWorstTick()
        {
            var s = new S(Freq);
            s.TickBegin();
            long t0 = Tk(100);
            s.End(S.CNormal, t0 + Tk(0.001), t0 + Tk(0.041));      // 40 ms of tl:Normal inside the tick
            s.TickEnd(t0, t0 + Tk(0.050), 777);                       // a 50 ms tick, tick id 777
            Emit("stages-worst", "{" + s.TakeWindowFields(0) + "}");
        }

        private static void T_StagesInvalidNesting()
        {
            // children summing to more than their parent: the accounting is invalid and must say so
            var s = new S(Freq);
            s.TickBegin();
            long t0 = Tk(5);
            s.End(S.CNormal, t0, t0 + Tk(0.030));
            s.End(S.CRare, t0, t0 + Tk(0.030));
            s.TickEnd(t0, t0 + Tk(0.040), 9);
            Emit("stages-invalid", "{" + s.TakeWindowFields(0) + "}");
        }
    }
}
