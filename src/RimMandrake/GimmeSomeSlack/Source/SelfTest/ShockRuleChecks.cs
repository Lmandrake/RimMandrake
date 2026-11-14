// T_SHOCK_RULE_OFFLINE (GimmeSomeSlack 0.1.0, bars floor_end_shock, floor_end_shocks_crossers, shock_reach_setting): the
// who-is-shocked rule as a pure table on the PRODUCTION ShockRule (../Aerial/ShockRule.cs), then the source binding that the
// game halves feed it (RM_FallenWireShock for downed spans and dropped cords, FloorEndShock for floor ends), so the table
// proven here is the rule the game runs. Item RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ShockRuleChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "shockrule: " + msg);

        public static void Run()
        {
            // 1. the whole table: kind x live x setting x job (fixing this line or not) x a pawn that can be shocked
            int rows = 0, wrong = 0;
            foreach (LineKind kind in Enum.GetValues(typeof(LineKind)))
                foreach (ShockReach reach in Enum.GetValues(typeof(ShockReach)))
                    foreach (bool live in new[] { false, true })
                        foreach (bool fixer in new[] { false, true })
                        {
                            bool bites = kind == LineKind.FloorEnd ? reach == ShockReach.All : reach != ShockReach.None;
                            bool want = live && bites && !fixer;
                            rows++;
                            if (ShockRule.Takes(reach, kind, live, true, false, false, fixer) != want)
                            {
                                wrong++;
                                Check(false, $"{kind} {reach} live={live} fixer={fixer}: want shocked={want}");
                            }
                        }
            Check(rows == 36 && wrong == 0, $"the 36-row table (3 kinds x 3 values x live x fixer): {wrong} wrong");

            // 2. the bar's own sentences, one check each (a row of the table read as the player would)
            Check(ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, true, true, false, false, false), "All: a hauler on a live floor end is shocked");
            Check(!ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, false, true, false, false, false), "All: a dead floor end never shocks");
            Check(!ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, true, true, false, false, true), "All: the constructor joining this end is safe");
            Check(!ShockRule.Takes(ShockReach.OnlyDownedLines, LineKind.FloorEnd, true, true, false, false, false), "Only downed lines: a floor end does not bite");
            Check(ShockRule.Takes(ShockReach.OnlyDownedLines, LineKind.DownedSpan, true, true, false, false, false), "Only downed lines: a fallen wire bites");
            Check(ShockRule.Takes(ShockReach.OnlyDownedLines, LineKind.DroppedCord, true, true, false, false, false), "Only downed lines: a dropped FlowWorks deck cord bites");
            Check(!ShockRule.Takes(ShockReach.None, LineKind.DownedSpan, true, true, false, false, false) &&
                  !ShockRule.Takes(ShockReach.None, LineKind.DroppedCord, true, true, false, false, false) &&
                  !ShockRule.Takes(ShockReach.None, LineKind.FloorEnd, true, true, false, false, false), "None: nothing bites");
            Check(ShockRule.KindBites(ShockReach.All, LineKind.FloorEnd) != ShockRule.KindBites(ShockReach.OnlyDownedLines, LineKind.FloorEnd),
                  "All and Only downed lines differ on a floor end (not an on/off box with a third label)");
            Check(!ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, true, false, false, false, false) &&
                  !ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, true, true, true, false, false) &&
                  !ShockRule.Takes(ShockReach.All, LineKind.FloorEnd, true, true, false, true, false),
                  "a mechanoid, a corpse and a pawn already knocked out are not shocked");

            // 3. the fixer's exemption is scoped to THIS end: its cell and its four neighbours, nothing further
            Check(ShockRule.TargetJoinsEnd(10, 10, 11, 10) && ShockRule.TargetJoinsEnd(10, 10, 10, 9) && ShockRule.TargetJoinsEnd(10, 10, 10, 10),
                  "a blueprint on the destroyed cell beside the end (or the end cell) joins it");
            Check(!ShockRule.TargetJoinsEnd(10, 10, 11, 11) && !ShockRule.TargetJoinsEnd(10, 10, 12, 10) && !ShockRule.TargetJoinsEnd(10, 10, 30, 4),
                  "an unrelated blueprint (diagonal, two away, far) does not: that constructor is shocked");

            // 4. only the end cell bites: a cell two or more back along the cord is not the end cell
            var ec = ShockRule.EndCell(10.36, 10.5);
            Check(ec == (10, 10) && ShockRule.EndCell(-0.2, 3.9) == (-1, 3), "the end cell is the cell the drawn tip lies in");

            // 5. the setting's names (saved and probe-set) and the shipped default
            Check(ShockRule.Parse("None") == ShockReach.None && ShockRule.Parse("OnlyDownedLines") == ShockReach.OnlyDownedLines &&
                  ShockRule.Parse("All") == ShockReach.All && ShockRule.Parse("all") == null && ShockRule.Parse("2") == null && ShockRule.Parse("True") == null,
                  "the three values parse by name; a bool or a number does not");

            SourceBinding();
        }

        /// <summary>The game halves feed ShockRule, from the setting, without the spark budget, and floor ends without the aerial
        /// master switch. A planted copy that drops any of these goes red (PlantedBindingIsCaught).</summary>
        private static void SourceBinding()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            Check(dir != null, "the production Aerial source folder is found");
            if (dir == null) return;
            string settings = File.ReadAllText(Path.Combine(dir, "AerialSettings.cs"));
            string fallen = File.ReadAllText(Path.Combine(dir, "RM_FallenWireShock.cs"));
            string floorPath = Path.Combine(dir, "FloorEndShock.cs");
            Check(File.Exists(floorPath), "FloorEndShock.cs exists (the floor-end game half)");
            string floor = File.Exists(floorPath) ? File.ReadAllText(floorPath) : "";
            Check(Regex.IsMatch(settings, @"public static ShockReach shockReach = ShockReach\.All;"), "the setting is one ShockReach value, shipped All");
            Check(Regex.IsMatch(settings, @"Scribe_Values\.Look\(ref shockReach, ""shockReach"", ShockReach\.All\)"), "the setting is saved, default All");
            Check(Regex.IsMatch(settings, @"shockReach = ShockReach\.All;") && Regex.Matches(settings, @"RadioButton\(").Count >= 2,
                  "reset restores All; the window draws radio buttons");
            foreach (string why in FloorBindingFaults(floor)) Check(false, "FloorEndShock: " + why);
            Check(FloorBindingFaults(floor).Length == 0, "FloorEndShock feeds ShockRule.Takes(shockReach, FloorEnd, ...) from every live end");
            Check(Regex.IsMatch(fallen, @"ShockRule\.Takes\(AerialSettings\.shockReach,"), "RM_FallenWireShock feeds ShockRule.Takes the setting");
            Check(Regex.IsMatch(fallen, @"LineKind\.DroppedCord") && Regex.IsMatch(fallen, @"LineKind\.DownedSpan"),
                  "RM_FallenWireShock tells a dropped FlowWorks cord from a fallen span");
            PlantedBindingIsCaught(floor);
        }

        internal static string[] FloorBindingFaults(string src)
        {
            var f = new System.Collections.Generic.List<string>();
            if (!Regex.IsMatch(src, @"ShockRule\.Takes\(AerialSettings\.shockReach, LineKind\.FloorEnd,")) f.Add("does not call ShockRule.Takes(AerialSettings.shockReach, LineKind.FloorEnd, ...)");
            if (src.Contains("SparkEnds(")) f.Add("reads the spark budget's SparkEnds(): an end outside maxSparkingEnds would not bite");
            if (src.Contains("maxSparkingEnds")) f.Add("reads maxSparkingEnds");
            if (Regex.IsMatch(src, @"AerialSettings\.enabled")) f.Add("reads the aerial master switch: floor ends must bite with it off");
            if (!Regex.IsMatch(src, @"EndLive\(")) f.Add("does not read the end's live flag from the last poll (EndLive)");
            if (!Regex.IsMatch(src, @"TargetJoinsEnd\(")) f.Add("does not scope the fixer's exemption with ShockRule.TargetJoinsEnd");
            return f.ToArray();
        }

        /// <summary>Watch the binding check fail: each planted copy of the real FloorEndShock source must be refused.</summary>
        private static void PlantedBindingIsCaught(string floor)
        {
            if (floor.Length == 0) return;
            string[] plants =
            {
                floor.Replace("ShockRule.Takes(AerialSettings.shockReach, LineKind.FloorEnd,", "ShockRule.Takes(ShockReach.All, LineKind.FloorEnd,"),
                floor.Replace("foreach (CordEnd e in g.AllEnds())", "foreach (CordEnd e in g.SparkEnds())"),
                floor + "\n// planted: if (!AerialSettings.enabled) return;",
                floor.Replace("TargetJoinsEnd(", "TargetJoinsAnything("),
            };
            int caught = 0;
            foreach (string p in plants) if (p != floor && FloorBindingFaults(p).Length > 0) caught++;
            Check(caught == plants.Length, $"planted binding faults caught: {caught}/{plants.Length}");
        }
    }
}
