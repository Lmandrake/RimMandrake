// Identified-time accounting (MUST 15): replays the sampler's hook order (RootPre -> LongEventsUpdate ->
// RootPost -> TmuPrefix, decompiled 1.6) through the PRODUCTION JawaBenchTpsExplained.
using System;
using E = JawaBench.BridgeTools.JawaBenchTpsExplained;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static bool Near(double a, double b) => Math.Abs(a - b) < 1e-6;

        private static void T_ExplainedDirectSave()
        {
            // a mod calls SaveGame synchronously INSIDE the tick (outside any long event): 4 s identified
            var e = new E();
            e.RootPre(0.0); e.RootPost(false); e.Take(0.01);           // frame 1, TmuPrefix at 0.01
            e.SaveBegin(0.02); e.SaveEnd(4.02);                         // inside frame 1's tick work
            e.RootPre(4.03); e.RootPost(false);
            double ex = e.Take(4.04);                                   // frame 2's TmuPrefix
            Check(Near(ex, 4.0), "a direct save outside long-event coverage is explained: " + ex);
        }

        private static void T_ExplainedNestedOnce()
        {
            // autosave: a synchronous long event that runs SaveGame inside it: counted ONCE
            var e = new E();
            e.RootPre(0.0); e.RootPost(false); e.Take(0.0);
            e.RootPre(1.0);
            e.LongEventBegin(1.1); e.SaveBegin(1.2); e.SaveEnd(4.2); e.LongEventEnd(4.3);
            e.RootPost(false);
            double ex = e.Take(4.4);
            Check(Near(ex, 3.2), "a save nested in a long event is counted once (3.2 s): " + ex);
            // an asynchronous event: the whole waiting frame, with a long-event scope inside it, once
            e.RootPre(10.0); e.LongEventBegin(10.0); e.LongEventEnd(12.0); e.RootPost(true);
            e.RootPre(12.5); e.RootPost(false);
            double ex2 = e.Take(12.6);
            Check(Near(ex2, 2.5), "a waiting frame containing a long-event scope is counted once (2.5 s): " + ex2);
        }

        private static void T_ExplainedSplitAcrossIntervals()
        {
            // a long save straddling a TmuPrefix observation: each interval gets only its own part
            var e = new E();
            e.RootPre(0.0); e.RootPost(false); e.Take(0.0);
            e.SaveBegin(1.0);
            double a = e.Take(3.0);                                     // an observation while the save is still open
            e.SaveEnd(5.0);
            double b = e.Take(6.0);
            Check(Near(a, 2.0) && Near(b, 2.0), "an open scope is split at the observation (2 + 2 s): " + a + " + " + b);
        }
    }
}
