// GSS_POWER_THEFT_FIX_WRONG_VICTIM (L0): the tap's event window charges each victim faction only for its own energy.
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class TapWindowChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "tapwindow: " + msg);

        private sealed class Fac { public string N; }

        public static void Run()
        {
            var A = new Fac { N = "A" }; var B = new Fac { N = "B" };
            var rec = new List<(Fac who, float wd, int ticks)>();
            void Raise(Fac who, float wd, int ticks) => rec.Add((who, wd, ticks));

            // drain A for 100 ticks at 2, the clamp switches to B for 50 ticks at 3, then the 250-tick event fires
            var w = new TapWindow<Fac, Fac>();
            for (int i = 0; i < 100; i++) w.Drain(A, A, 2f, Raise);
            for (int i = 0; i < 50; i++) w.Drain(B, B, 3f, Raise);
            w.Flush(Raise);
            float a = rec.Where(r => r.who == A).Sum(r => r.wd), b = rec.Where(r => r.who == B).Sum(r => r.wd);
            Check(a == 200f && b == 150f, "A charged 200 and B charged 150 (got A " + a + ", B " + b + ")");
            Check(rec.Where(r => r.who == A).Sum(r => r.ticks) == 100 && rec.Where(r => r.who == B).Sum(r => r.ticks) == 50,
                  "each faction gets its own draining ticks");
            Check(w.Wd == 0f && w.DrainTicks == 0, "the window is empty after the event");

            // can-fail: the old rule (one running sum raised against whoever is current at the event) charges B all 350
            float old = 100 * 2f + 50 * 3f;
            Check(old != b && old == 350f, "can-fail: the old rule would have charged B " + old + " for A's theft");

            // back-and-forth A,B,A keeps each total exact; idle ticks (0 stolen) neither switch nor count
            rec.Clear(); w = new TapWindow<Fac, Fac>();
            w.Drain(A, A, 1f, Raise); w.Drain(null, null, 0f, Raise); w.Drain(B, B, 4f, Raise); w.Drain(A, A, 1f, Raise); w.Flush(Raise);
            Check(rec.Where(r => r.who == A).Sum(r => r.wd) == 2f && rec.Where(r => r.who == B).Sum(r => r.wd) == 4f && rec.Count == 3,
                  "A,idle,B,A: A 2, B 4, one flush per switch");
            w.Flush(Raise);
            Check(rec.Count == 3, "flushing an empty window raises nothing");
        }
    }
}
