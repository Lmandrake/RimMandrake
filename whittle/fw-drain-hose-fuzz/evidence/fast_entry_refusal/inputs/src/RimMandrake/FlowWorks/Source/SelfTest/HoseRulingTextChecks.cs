// HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD, text half (owner ruling 2026-10-11 #3: "intake needs a pump"), plus the hose
// leftovers handed over from Gimme Some Slack: the reel's player text must not claim a hose end draws from water, must not
// say there is "no pump yet" (FlowWorks has pumps), and a selected reel names what its free end lies on, including the
// faction of a tank it is coupled to. Reads PRODUCTION source. NOT proven here: the inspect pane on a live map (live row).
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseRulingTextChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseText_water_end_is_no_intake", () =>
            {
                string ends = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "HoseEnds.cs"));
                // can-fail: any string literal saying "intake in" (any case, any spacing) is the pre-ruling text back.
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(ends, "\"[^\"]*\\bintake\\s+in\\b",
                        System.Text.RegularExpressions.RegexOptions.IgnoreCase),
                    "the old 'intake in <water>' text is gone (ruling #3: no nozzle intake)");
                // rev 2 §3.6 (liquid networks L5): a water end is a pump intake only when set to Intake; it never draws by itself
                Assert(ends.Contains("(taking water in needs a pump: set this end to Intake)"), "a water end says intake needs a pump and the Intake role");
                Assert(ends.Contains("\"lying beside \""), "can-fail: an end that only touches water says 'beside', not 'in'");
                // Regression guard of text that predates the ruling (passes on its parent too): a coupled end names another faction's tank.
                Assert(ends.Contains("Port?.Faction != null && Port.Faction != Faction.OfPlayer"), "a coupled end names another faction's tank");
            });
            Case("HoseText_reel_inspect_names_free_end", () =>
            {
                string reel = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "CompHoseReel.cs"));
                Assert(reel.Contains("\"\\nFree end: \" + this.FreeEnd().Describe()"), "the laid reel's inspect text carries the free end's Describe()");
                Assert(reel.IndexOf("no pump yet", StringComparison.OrdinalIgnoreCase) < 0, "no 'no pump yet' text (FlowWorks has pumps)");
            });
        }
    }
}
