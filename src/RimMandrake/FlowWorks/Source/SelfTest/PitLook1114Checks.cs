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

            // his 1: "It should be full speed while walking on the floor of the pit. Pits should only slow you down while you're
            // climbing up or down over the walls."
            Case("PitLook1114_pit_floor_walks_full_speed_readout_and_step", () =>
            {
                // the readout's walking cost for a dug square: a step along its floor from the same depth
                Assert(RM_PitTrapMath.FloorWalkCost(true, false, 300) == 0, "a dry 4 m floor reads its dry pit cost, not 100%");
                Assert(RM_PitTrapMath.FloorWalkCost(true, true, 42) == 42, "a wet floor reads the water's own wading cost");
                Assert(RM_PitTrapMath.FloorWalkCost(false, false, 300) == 300, "setting off: the old cost stands");
                // a walked step along a wet floor keeps the water's cost; a climb into or out of a wet pit is still priced as the pit
                Assert(RM_PitTrapMath.WalkedAlongFloor(8, 8), "along a 4 m floor is not 'along'");
                Assert(!RM_PitTrapMath.WalkedAlongFloor(0, 8) && !RM_PitTrapMath.WalkedAlongFloor(8, 4), "a climb counts as along the floor");
                Assert(!RM_PitTrapMath.WalkedAlongFloor(0, 0), "surface walking counts as a pit floor");
                // a dry equal-depth step was already free (RM_Patch_PitStepCost): unchanged
                Assert(RM_PitTrapMath.DryStepBaseCost(8, 8, 300) == 0, "a dry floor step is no longer free");
                string mouse = RiverSwitchFlipChecks.Src("RM_MouseoverDepth.cs");
                RiverSwitchFlipChecks.Has(mouse, @"RM_PitTrapMath\.FloorWalkCost\(", "the readout prices a dug square as its floor walk");
                string step = RiverSwitchFlipChecks.Src("Superdeep/RM_PitStepCost.cs");
                RiverSwitchFlipChecks.Has(step, @"Prefix\(PathGrid __instance, IntVec3 c, bool perceivedStatic, IntVec3 prevCell, ref int\? baseCostOverride\)[\s\S]*?RM_PitTrapMath\.WalkedAlongFloor\(",
                    "the wet-pit planning cost lets a walked step along the floor keep its wading cost");
            });

            // his second 8: "Geyser under water in pit ... it does not say Hot Tub currently even though it should"
            Case("PitLook1114_geyser_pool_says_hot_tub", () =>
            {
                Assert(RM_GeyserTubMath.TubWord(true, true, true, true, true, false) == "Hot tub", "an open pool does not say Hot tub");
                Assert(RM_GeyserTubMath.TubWord(true, true, true, true, false, false) == "Not a hot tub yet: the vent is not under 0.4 m of liquid",
                    "a shallow pool: " + RM_GeyserTubMath.TubWord(true, true, true, true, false, false));
                Assert(RM_GeyserTubMath.TubWord(true, true, true, true, true, true) == "Not a hot tub: the geyser is capped", "capped");
                Assert(RM_GeyserTubMath.TubWord(true, true, true, false, true, false) == "Not a hot tub: nobody bathes in this liquid", "unbathable");
                Assert(RM_GeyserTubMath.TubWord(false, true, true, true, true, false) == null, "the feature off still talks");
                Assert(RM_GeyserTubMath.TubWord(true, false, true, true, true, false) == null, "a surface geyser talks about tubs");
                Assert(RM_GeyserTubMath.TubWord(true, true, false, true, true, false) == null, "a dry sunk geyser talks about tubs");
                string mouse = RiverSwitchFlipChecks.Src("RM_MouseoverDepth.cs");
                RiverSwitchFlipChecks.Has(mouse, @"RM_GeyserPit\.TubReadoutAt\(map, c\)", "the readout names the hot tub");
                string pit = RiverSwitchFlipChecks.Src("Superdeep/RM_GeyserPit.cs");
                RiverSwitchFlipChecks.Has(pit, @"public static string TubReadoutAt\(Map map, IntVec3 c\)[\s\S]*?RM_GeyserTubMath\.TubWord\(",
                    "the hot tub word comes from the tub verdict");
                RiverSwitchFlipChecks.Has(pit, @"public static string TubReadoutAt\(Map map, IntVec3 c\)[\s\S]*?HeatedCells\(g, s\)\.Contains\(c\)",
                    "the hot tub is named on the heated cells, not only the vent");
            });

            // his 3: "It should not let you install furniture that overlaps with a pit edge. Right now I can install a butcher
            // table hanging over a pit in any configuration."
            Case("PitLook1114_furniture_never_straddles_a_pit_edge", () =>
            {
                Assert(RM_PitTrapMath.StraddleRefusal(new[] { 8, 8 }) == null, "a table on one 4 m floor was refused");
                Assert(RM_PitTrapMath.StraddleRefusal(new[] { 0, 0, 0 }) == null, "a table on the ground was refused");
                Assert(RM_PitTrapMath.StraddleRefusal(new[] { 8 }) == null && RM_PitTrapMath.StraddleRefusal(null) == null, "one square refused");
                string edge = RM_PitTrapMath.StraddleRefusal(new[] { 0, 8 });
                Assert(edge == "Cannot hang over a pit edge: part would stand on the ground, part 4.0 m down in the pit.", "edge: " + edge);
                string steps = RM_PitTrapMath.StraddleRefusal(new[] { 4, 8, 8 });
                Assert(steps == "Cannot straddle two pit floors (2.0 m and 4.0 m deep): every square must be on one floor.", "steps: " + steps);
                Assert(RM_PitTrapMath.StraddleRefusal(new[] { -1, 0 }) == null, "an unreadable square counts as a step");
                // which things the rule is for: a building of more than one square that is not FlowWorks' own pit work
                Assert(RM_PitTrapMath.StraddleRuleApplies(true, 2, false), "a two-square bench is exempt");
                Assert(!RM_PitTrapMath.StraddleRuleApplies(true, 1, false), "a one-square thing cannot straddle");
                Assert(!RM_PitTrapMath.StraddleRuleApplies(true, 3, true), "a ladder, ramp, bridge or sluice may not span an edge");
                Assert(!RM_PitTrapMath.StraddleRuleApplies(false, 4, false), "a plant or item is held to the furniture rule");
                string src = RiverSwitchFlipChecks.Src("Superdeep/RM_PitEdgePlacement.cs");
                RiverSwitchFlipChecks.Has(src, @"\[HarmonyPatch\(typeof\(GenConstruct\), nameof\(GenConstruct\.CanPlaceBlueprintAt_NewTemp\)\)\]",
                    "placement and install go through the refusal");
                RiverSwitchFlipChecks.Has(src, @"RM_PitTrapMath\.StraddleRefusal\(", "the refusal reads the production rule");
                RiverSwitchFlipChecks.Has(src, @"RM_PitTrapMath\.StraddleRuleApplies\(", "the exemption reads the production rule");
                RiverSwitchFlipChecks.Has(src, @"RimMandrakeFlowWorksSettings\.pitEdgeStraddleRefusedEnabled", "the rule has its Mod Setting");
                string mod = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(mod, @"Scribe_Values\.Look\(ref pitEdgeStraddleRefusedEnabled, ""pitEdgeStraddleRefusedEnabled"", true\)", "the setting is saved");
                RiverSwitchFlipChecks.Has(mod, @"CheckboxLabeled\(""[^""]+"", ref pitEdgeStraddleRefusedEnabled", "the setting has a checkbox");
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
