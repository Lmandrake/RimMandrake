// SLIME_CROSSING_BUILD_SLIPPERY_SLOPE: the slip numbers on the PRODUCTION RM_SlimeMath (compiled in by the .csproj), plus
// the shipped data that makes slime slip (FluidDef rows, fill pathCost) read from the XML, and the wiring read from source.
// Owner: "so slippery that it is nearly impossible to cross, and escape from the pit takes a great deal of time."
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SlimeChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot()
        {
            string d = AppContext.BaseDirectory;
            for (int i = 0; i < 10 && d != null; i++, d = Path.GetDirectoryName(d))
            {
                if (Directory.Exists(Path.Combine(d, "Defs", "Canals")) && File.Exists(Path.Combine(d, "Source", "RM_SlimeMath.cs")))
                    return d;
            }
            throw new Exception("FlowWorks mod root not found above " + AppContext.BaseDirectory);
        }

        private const float Stun = RM_SlimeMath.DefaultStunSeconds;
        private const float ClimbF = RM_SlimeMath.DefaultClimbOutFactor;

        public static void Run(Action<string, Action> Case)
        {
            Case("Slime_no_slip_where_it_should_not", () =>
            {
                Assert(RM_SlimeMath.SlipChance(0f, 2, 2, false, false, 1f, ClimbF) == 0f, "a non-slippery liquid slips");
                Assert(RM_SlimeMath.SlipChance(1f, 0, 2, false, false, 1f, ClimbF) == 0f, "a dry cell slips");
                Assert(RM_SlimeMath.SlipChance(1f, 2, 2, false, true, 1f, ClimbF) == 0f, "a flier slips");
                Assert(RM_SlimeMath.SlipChance(1f, 2, 2, false, false, 0f, ClimbF) == 0f, "multiplier 0 still slips");
            });
            Case("Slime_fuller_and_climbing_out_slip_more", () =>
            {
                float trace = RM_SlimeMath.SlipChance(1f, 1, 3, false, false, 1f, ClimbF);
                float brim = RM_SlimeMath.SlipChance(1f, 3, 3, false, false, 1f, ClimbF);
                float outBrim = RM_SlimeMath.SlipChance(1f, 3, 3, true, false, 1f, ClimbF);
                Assert(trace > 0f && trace < brim, "trace " + trace + " vs brim " + brim);
                Assert(Math.Abs(brim - RM_SlimeMath.BaseSlipChance) < 1e-6, "brim slip " + brim + " != base");
                Assert(outBrim > brim && outBrim <= RM_SlimeMath.MaxSlipChance, "climb-out " + outBrim);
                Assert(RM_SlimeMath.SlipChance(1f, 3, 3, true, false, 10f, 10f) == RM_SlimeMath.MaxSlipChance,
                    "never a certainty: capped at MaxSlipChance");
                Assert(RM_SlimeMath.IsClimbingOut(2, 0) && RM_SlimeMath.IsClimbingOut(3, 2) && !RM_SlimeMath.IsClimbingOut(2, 2)
                       && !RM_SlimeMath.IsClimbingOut(1, 2), "climbing out = toward shallower ground only");
                Assert(RM_SlimeMath.StunTicks(Stun) == 120 && RM_SlimeMath.StunTicks(0f) == 1, "stun ticks");
            });
            Case("Slime_nearly_uncrossable_in_time", () =>
            {
                // a brim-full D2 canal cell at the shipped pathCost 450: ~463 ticks of walking for a 13-tick pawn
                int walk = 450 + 13;
                float brim = RM_SlimeMath.SlipChance(1f, 2, 2, false, false, 1f, ClimbF);
                float perCell = walk / 60f + RM_SlimeMath.ExpectedStunSecondsPerCell(brim, walk, Stun);
                float tarCell = (300 + 13) / 60f;
                Assert(perCell > 2f * tarCell, "a slime cell (" + perCell + " s) is not much worse than tar (" + tarCell + " s)");
                Assert(perCell < 60f, "a slime cell takes " + perCell + " s: impossible, not nearly impossible");
            });
            Case("Slime_climb_out_takes_a_great_deal_of_time", () =>
            {
                float outC = RM_SlimeMath.SlipChance(1f, 2, 2, true, false, 1f, ClimbF);
                // the climb step off a D2 canal: surface ~0 + the dry D2 climb 45, ~58 ticks for a 13-tick pawn
                float clean = 58 / 60f;
                float slimy = RM_SlimeMath.ExpectedClimbOutSeconds(outC, 58, Stun);
                Assert(slimy > 3f * clean, "climbing out of slime (" + slimy + " s) barely slower than a dry climb (" + clean + " s)");
                Assert(slimy < 120f, "climbing out takes " + slimy + " s: never, not a great deal of time");
                Assert(RM_SlimeMath.ExpectedClimbOutSeconds(0f, 58, Stun) == clean, "no slip = the plain climb");
            });
            Case("Slime_natural_ground_slips_too", () =>
            {
                // owner 2026-10-16: "Natural slime should also be slippery." Natural ground has no fill ladder and no climb:
                // RM_SlimeSlip rolls SlipChance(s, 1, 1, climbingOut false) there, i.e. the brim chance.
                string root = ModRoot();
                Assert(Math.Abs(RM_SlimeMath.SlipChance(1f, 1, 1, false, false, 1f, 1f) - RM_SlimeMath.BaseSlipChance) < 1e-6,
                    "natural slime does not slip at the brim chance");
                string patch = File.ReadAllText(Path.Combine(root, "Patches", "Canals", "RM_SlipperySlimeGround.xml"));
                var targets = new System.Collections.Generic.SortedSet<string>();
                foreach (Match m in Regex.Matches(patch, @"<match Class=""PatchOperationAddModExtension"">\s*<xpath>/Defs/TerrainDef\[defName=""(\w+)""\]</xpath>"))
                    targets.Add(m.Groups[1].Value);
                var want = new System.Collections.Generic.SortedSet<string> { "RM_Slime_Liquid", "RM_Slime_Mud" };
                foreach (string col in new[] { "Red", "Green", "White", "Yellow" })
                {
                    want.Add("RM_Slime" + col + "Shallow");
                    want.Add("RM_Slime" + col + "Deep");
                }
                Assert(targets.SetEquals(want), "slippery ground set: " + string.Join(",", targets));
                Assert(Regex.Matches(patch, "Class=\"RimMandrake.FlowWorks.RM_SlipperyTerrain\"").Count == want.Count, "one RM_SlipperyTerrain per target");
                Assert(Regex.Matches(patch, "PatchOperationConditional").Count == want.Count, "every op guarded on its target");
                foreach (string col in new[] { "Red", "Green", "White", "Yellow" })
                {
                    string t = File.ReadAllText(Path.Combine(root, "Defs", "LiquidTypes", "TerrainDefs", "RM_Slime" + col + ".xml"));
                    var sh = Regex.Match(t, @"<defName>RM_Slime" + col + @"Shallow</defName>.*?<pathCost>(\d+)</pathCost>", RegexOptions.Singleline);
                    var dp = Regex.Match(t, @"<defName>RM_Slime" + col + @"Deep</defName>.*?<pathCost>(\d+)</pathCost>", RegexOptions.Singleline);
                    Assert(sh.Groups[1].Value == "200" && dp.Groups[1].Value == "450",
                        col + " natural pool walk cost " + sh.Groups[1].Value + "/" + dp.Groups[1].Value + " != canal 200/450");
                }
                string slip = File.ReadAllText(Path.Combine(root, "Source", "RM_SlimeSlip.cs"));
                Assert(slip.Contains("class RM_SlipperyTerrain : DefModExtension") && slip.Contains("NaturalSlime(map, c)"),
                    "RM_SlimeSlip does not read natural slime ground");
            });
            Case("Slime_shipped_data_and_wiring", () =>
            {
                string root = ModRoot();
                string fluids = File.ReadAllText(Path.Combine(root, "Defs", "Canals", "FluidDefs", "FlowWorks_Fluids.xml"));
                foreach (string col in new[] { "Red", "Green", "White", "Yellow" })
                {
                    var m = Regex.Match(fluids, @"<defName>RM_Fluid_Slime" + col + @"</defName>(.*?)</RimMandrake\.FlowWorks\.FluidDef>",
                        RegexOptions.Singleline);
                    Assert(m.Success && m.Groups[1].Value.Contains("<slipperiness>1</slipperiness>"), col + " slime does not slip");
                }
                Assert(!Regex.IsMatch(fluids, @"RM_Fluid_(Water|Tar)</defName>(?:(?!</RimMandrake\.FlowWorks\.FluidDef>).)*<slipperiness>",
                    RegexOptions.Singleline), "water or tar slips");
                string terr = File.ReadAllText(Path.Combine(root, "Defs", "Canals", "TerrainDefs", "FlowWorks_SlimeTerrain.xml"));
                foreach (Match t in Regex.Matches(terr, @"<defName>RM_Fill_Slime\w+_(Trace|Half|Brim|Superdeep)</defName>.*?<pathCost>(\d+)</pathCost>",
                    RegexOptions.Singleline))
                {
                    int want = t.Groups[1].Value == "Trace" ? 200 : t.Groups[1].Value == "Half" ? 300 : 450;
                    Assert(int.Parse(t.Groups[2].Value) == want, t.Value.Substring(0, 40) + " pathCost " + t.Groups[2].Value);
                }
                string fx = File.ReadAllText(Path.Combine(root, "Source", "RM_MapComponent_Excavation.cs"));
                Assert(fx.Contains("RM_SlimeSlip.Tick(map, this);"), "RM_SlimeSlip is never ticked");
                string slip = File.ReadAllText(Path.Combine(root, "Source", "RM_SlimeSlip.cs"));
                Assert(slip.Contains("MoteMaker.ThrowText") && slip.Contains("StunFor("), "a slip with no visible sign");
                Assert(slip.Contains("slimeSlipEnabled"), "the slip ignores its Mod Setting");
            });
        }
    }
}
