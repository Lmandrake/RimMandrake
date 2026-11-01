using System;

namespace RimMandrake.Utinni.WasteRun.SelfTest
{
    // WASTE_RUN_STUBS_1: the pure half of the four consequences, against the real kernel.
    public static class Program
    {
        private static int failures, checks;

        private static void Check(string name, bool ok)
        {
            checks++;
            if (ok) return;
            failures++;
            Console.WriteLine("FAIL " + name);
        }

        private static bool Near(float a, float b) { return Math.Abs(a - b) < 0.0001f; }

        public static int Main()
        {
            // Flight gate: the whole truth table.
            Check("off is allowed anywhere", WasteRunKernel.GateFlight(false, true, false) == FlightGate.Allowed);
            Check("at target is allowed", WasteRunKernel.GateFlight(true, true, true) == FlightGate.Allowed);
            Check("away is refused", WasteRunKernel.GateFlight(true, true, false) == FlightGate.Away);
            Check("no such place is waived, not locked", WasteRunKernel.GateFlight(true, false, false) == FlightGate.Uncharted);
            Check("away may not commit", !WasteRunKernel.MayCommit(FlightGate.Away));
            Check("uncharted may commit", WasteRunKernel.MayCommit(FlightGate.Uncharted));
            Check("allowed may commit", WasteRunKernel.MayCommit(FlightGate.Allowed));
            foreach (WasteDestination d in Enum.GetValues(typeof(WasteDestination)))
            {
                Check("reason names flying: " + d, WasteRunKernel.AwayReason(d).StartsWith("fly "));
            }

            // Slime pollution: falloff, clamps, reach.
            Check("neutralize at centre", Near(WasteRunKernel.SlimePollution(0.8f, -0.5f, 0f, 12f), 0.3f));
            Check("bloom falls off", WasteRunKernel.SlimePollution(0f, 0.4f, 6f, 12f) < WasteRunKernel.SlimePollution(0f, 0.4f, 1f, 12f));
            Check("beyond reach untouched", Near(WasteRunKernel.SlimePollution(0.25f, 0.4f, 13f, 12f), 0.25f));
            Check("clamps at 0", Near(WasteRunKernel.SlimePollution(0.1f, -0.5f, 0f, 12f), 0f));
            Check("clamps at 1", Near(WasteRunKernel.SlimePollution(0.9f, 0.4f, 0f, 12f), 1f));

            // The third outcome.
            Check("low roll neutralizes", WasteRunKernel.ResolveUnknown(0.1f) == WasteEffect.SlimeNeutralized);
            Check("high roll blooms", WasteRunKernel.ResolveUnknown(0.9f) == WasteEffect.SlimeBloomed);
            Check("nothing pending is never due", !WasteRunKernel.UnknownDue(-1, 999999));
            Check("not yet", !WasteRunKernel.UnknownDue(100, 99));
            Check("due", WasteRunKernel.UnknownDue(100, 100));
            Check("delay is a real wait", WasteRunKernel.UnknownMinDays > 0 && WasteRunKernel.UnknownMaxDays >= WasteRunKernel.UnknownMinDays);

            // Effect keys and the slime set.
            Check("mood key", WasteRunKernel.MoodDefName(WasteEffect.Frozen) == "RUT_WasteRunMood_Frozen");
            Check("slime set", WasteRunKernel.IsSlime(WasteEffect.SlimeUnknown) && !WasteRunKernel.IsSlime(WasteEffect.PropaneIgnited));

            Console.WriteLine((failures == 0 ? "PASS " : "FAILED ") + (checks - failures) + "/" + checks);
            return failures == 0 ? 0 : 1;
        }
    }
}
