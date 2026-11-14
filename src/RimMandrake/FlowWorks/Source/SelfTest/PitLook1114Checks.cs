// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE: the owner's live look at the pits, 2026-11-14 (his numbers 1, 3, 9, 11, 12, second 8).
// Each case covers one fix: the Verse-free rule it decides by (compiled in by the .csproj) and, where the rule lives in a Harmony
// patch, the call site read from production source. What this cannot see: the live readout, a placement click, a pour, a draw.
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitLook1114Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>"fill 3", "fill level(s)", "fill tier", "fill-units": the retired Fill N way of counting liquid.</summary>
        internal static readonly Regex FillN = new Regex(@"\b[Ff]ill(ed)?[ -]?(\d|N\b|levels?\b|level\(s\)|tiers?\b|units?\b)");

        public static void Run(Action<string, Action> Case)
        {
            // his 9: "Provide that same fill example for all the different options ... Define instead how full a single tile would
            // be in terms of meters."
            Case("PitLook1114_pour_steps_each_show_metres_on_one_tile", () =>
            {
                Assert(RM_GodLiquidMath.StepLabel(100) == "100 L (one tile 0.05 m deep)", "100 L: " + RM_GodLiquidMath.StepLabel(100));
                Assert(RM_GodLiquidMath.StepLabel(1000) == "1 kL (one tile 0.5 m deep)", "1 kL: " + RM_GodLiquidMath.StepLabel(1000));
                Assert(RM_GodLiquidMath.StepLabel(RM_GodLiquidMath.FullPit16x16x4mLitres) == "2048 kL (one tile 1024 m deep)",
                    "the 16x16 step: " + RM_GodLiquidMath.StepLabel(RM_GodLiquidMath.FullPit16x16x4mLitres));
                foreach (long l in RM_GodLiquidMath.PourLitreSteps)
                {
                    string s = RM_GodLiquidMath.StepLabel(l);
                    Assert(s.Contains("(one tile ") && s.EndsWith(" m deep)"), "a step without its one-tile example: " + s);
                    Assert(!s.Contains("16x16") && !FillN.IsMatch(s), "a step still names a pit size or a fill count: " + s);
                }
            });

            Case("PitLook1114_no_fill_n_wording_in_visible_text", () =>
            {
                string root = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs"));
                string mod = Path.GetDirectoryName(root);
                var hits = new System.Collections.Generic.List<string>();
                var files = Directory.GetFiles(root, "*.cs", SearchOption.AllDirectories)
                    .Where(f => !f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)
                        && !f.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar));
                Regex literal = new Regex("\"(?:[^\"\\\\]|\\\\.)*\"");
                foreach (string f in files)
                {
                    foreach (string line in File.ReadAllLines(f))
                    {
                        string t = line.TrimStart();
                        if (t.StartsWith("//")) continue;
                        foreach (Match m in literal.Matches(line))
                        {
                            if (FillN.IsMatch(m.Value)) hits.Add(Path.GetFileName(f) + ": " + m.Value);
                        }
                    }
                }
                foreach (string sub in new[] { "Languages", "Defs" })
                {
                    string d = Path.Combine(mod, sub);
                    if (!Directory.Exists(d)) continue;
                    foreach (string f in Directory.GetFiles(d, "*.xml", SearchOption.AllDirectories))
                    {
                        foreach (Match m in Regex.Matches(File.ReadAllText(f), @"<(label|description|[A-Za-z_]+Desc|[A-Za-z_]+Label)>([^<]*)<"))
                        {
                            if (FillN.IsMatch(m.Groups[2].Value)) hits.Add(Path.GetFileName(f) + ": " + m.Groups[2].Value);
                        }
                    }
                }
                Assert(hits.Count == 0, "Fill N wording in text a player or dev reads: " + string.Join(" | ", hits.Take(8)));
                // the checker sees what it must: planted strings go red
                Assert(FillN.IsMatch("\"3.0 fill level(s) overflowed\"") && FillN.IsMatch("\"(42 fill-units)\"")
                    && FillN.IsMatch("\"Fill 3\"") && FillN.IsMatch("\"fill tier terrain\""), "the Fill N pattern went blind");
                Assert(!FillN.IsMatch("\"Fill in pit\"") && !FillN.IsMatch("\"fill containers\"") && !FillN.IsMatch("\"Fill tank: \""),
                    "the Fill N pattern flags plain English");
            });
        }
    }
}
