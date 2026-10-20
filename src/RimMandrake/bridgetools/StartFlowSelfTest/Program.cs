// Unit group for JawaBenchStartFlowCore (production file). Prints "U <name> ok" or
// "U <name> FAIL <why>" per case and "U-count <n>" last; driven by
// src/RimMandrake/Utils/selftest_start_flow_core.py.
using System;
using System.Collections.Generic;
using System.Linq;
using C = JawaBench.BridgeTools.JawaBenchStartFlowCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int n;

        static void U(string name, bool ok, string why = "")
        {
            n++;
            Console.WriteLine("U " + name + (ok ? " ok" : " FAIL " + why));
        }

        static string Ideos(string name) => @"C:\Users\X\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\" + name + ".rid";

        static int Main()
        {
            // ---------------- scenarios
            var list = new List<C.ScenarioEntry>
            {
                new C.ScenarioEntry("Crashlanded", "Crashlanded", "FromDef"),
                new C.ScenarioEntry("Scenario_Utinni", "Utinni!", "FromDef"),
                new C.ScenarioEntry("Scenario_UtinniHard", "Utinni! (hard)", "FromDef"),
                new C.ScenarioEntry(null, "My Custom", "CustomLocal"),
                new C.ScenarioEntry(null, "Twin", "CustomLocal"),
                new C.ScenarioEntry(null, "twin", "SteamWorkshop"),
            };
            string e;
            U("scen.defName_exact", C.MatchScenario(list, "Scenario_Utinni", out e) == 1, e);
            U("scen.defName_trimmed", C.MatchScenario(list, "  Scenario_Utinni ", out e) == 1, e);
            U("scen.defName_case_sensitive_falls_to_name", C.MatchScenario(list, "scenario_utinni", out e) == -1 && e.Contains("Near"), e);
            U("scen.name_case_insensitive", C.MatchScenario(list, "utinni!", out e) == 1, e);
            U("scen.custom_by_name", C.MatchScenario(list, "My Custom", out e) == 3, e);
            U("scen.ambiguous_name_refused", C.MatchScenario(list, "Twin", out e) == -1 && e.StartsWith("AMBIGUOUS"), e);
            U("scen.no_substring_pick", C.MatchScenario(list, "Utinni", out e) == -1 && e.Contains("Scenario_Utinni") && e.Contains("Scenario_UtinniHard"), e);
            U("scen.unknown_no_near", C.MatchScenario(list, "Zzz", out e) == -1 && e.Contains("none contain"), e);
            U("scen.empty_query", C.MatchScenario(list, " ", out e) == -1 && e.Contains("required"), e);
            U("scen.empty_list_is_instrument_failure", C.MatchScenario(new List<C.ScenarioEntry>(), "Crashlanded", out e) == -1 && e.Contains("EMPTY"), e);
            var dupDef = new List<C.ScenarioEntry> { new C.ScenarioEntry("A", "x", "FromDef"), new C.ScenarioEntry("A", "y", "FromDef") };
            U("scen.duplicate_defName_refused", C.MatchScenario(dupDef, "A", out e) == -1 && e.StartsWith("AMBIGUOUS"), e);
            U("scen.defName_beats_name", C.MatchScenario(new List<C.ScenarioEntry> { new C.ScenarioEntry(null, "Foo", "CustomLocal"), new C.ScenarioEntry("Foo", "Bar", "FromDef") }, "Foo", out e) == 1, e);

            // ---------------- .rid paths
            string r;
            r = C.ResolveRidPath(@"D:\Luke\dev\RimMandrake\src\Jawa\ideoligion\The Salvation.rid", Ideos, out e);
            U("rid.windows_abs", r == @"D:\Luke\dev\RimMandrake\src\Jawa\ideoligion\The Salvation.rid", r + "|" + e);
            r = C.ResolveRidPath("D:/Luke/dev/x/The Salvation.RID", Ideos, out e);
            U("rid.forward_slashes_and_case", r == @"D:\Luke\dev\x\The Salvation.RID", r + "|" + e);
            r = C.ResolveRidPath("/mnt/d/Luke/dev/RimMandrake/src/Jawa/ideoligion/The Salvation.rid", Ideos, out e);
            U("rid.wsl_drvfs", r == @"D:\Luke\dev\RimMandrake\src\Jawa\ideoligion\The Salvation.rid", r + "|" + e);
            r = C.ResolveRidPath("/home/mandrake/rm/foundry/src/Jawa/ideoligion/The Salvation.rid", Ideos, out e);
            U("rid.linux_only_refused", r == null && e.Contains("Linux-only"), r + "|" + e);
            r = C.ResolveRidPath("The Salvation", Ideos, out e);
            U("rid.bare_name", r == Ideos("The Salvation"), r + "|" + e);
            r = C.ResolveRidPath("The Salvation.rid", Ideos, out e);
            U("rid.bare_name_with_ext_not_doubled", r == Ideos("The Salvation"), r + "|" + e);
            r = C.ResolveRidPath("\"The Salvation\"", Ideos, out e);
            U("rid.quotes_stripped", r == Ideos("The Salvation"), r + "|" + e);
            r = C.ResolveRidPath("St. Kira", Ideos, out e);
            U("rid.dot_in_name_ok", r == Ideos("St. Kira"), r + "|" + e);
            r = C.ResolveRidPath("foo.xml", Ideos, out e);
            U("rid.bare_foreign_ext_refused", r == null && e.Contains(".xml"), r + "|" + e);
            r = C.ResolveRidPath(@"D:\x\foo.rws", Ideos, out e);
            U("rid.abs_non_rid_refused", r == null && e.Contains("not a .rid"), r + "|" + e);
            r = C.ResolveRidPath(@"ideoligion\The Salvation.rid", Ideos, out e);
            U("rid.relative_refused", r == null && e.Contains("relative"), r + "|" + e);
            r = C.ResolveRidPath("", Ideos, out e);
            U("rid.empty_refused", r == null && e.Contains("required"), r + "|" + e);
            r = C.ResolveRidPath(@"\\server\share\a.rid", Ideos, out e);
            U("rid.unc_ok", r == @"\\server\share\a.rid", r + "|" + e);
            r = C.ResolveRidPath(".rid", Ideos, out e);
            U("rid.empty_name_refused", r == null, r + "|" + e);

            // ---------------- tiles
            var t = C.ParseTileList("17007, 1621 ,17011", out e);
            U("tile.parse_list", t != null && t.SequenceEqual(new[] { 17007, 1621, 17011 }), e);
            U("tile.parse_single", C.ParseTileList("5", out e)?.SequenceEqual(new[] { 5 }) == true, e);
            U("tile.parse_negative_refused", C.ParseTileList("-3", out e) == null && e.Contains("-3"), e);
            U("tile.parse_garbage_refused", C.ParseTileList("17007,abc", out e) == null && e.Contains("abc"), e);
            U("tile.parse_empty_item_refused", C.ParseTileList("1,,2", out e) == null, e);
            U("tile.parse_duplicate_refused", C.ParseTileList("4,4", out e) == null && e.Contains("twice"), e);
            U("tile.parse_blank_refused", C.ParseTileList("", out e) == null && e.Contains("required"), e);

            var evaluated = new List<int>();
            var p = C.PickFirstAcceptable(new[] { 17007, 1621, 17011 }, id => { evaluated.Add(id); return id == 17007 ? "water" : null; });
            U("tile.pick_skips_with_reason", p.Chosen == 1621 && p.Refused.Count == 1 && p.Refused[0].Key == 17007 && p.Refused[0].Value == "water", "chosen " + p.Chosen);
            U("tile.pick_stops_at_first_good", evaluated.SequenceEqual(new[] { 17007, 1621 }), string.Join(",", evaluated));
            p = C.PickFirstAcceptable(new[] { 1, 2 }, id => "no");
            U("tile.pick_none", p.Chosen == -1 && p.Refused.Count == 2, "chosen " + p.Chosen);
            p = C.PickFirstAcceptable(new int[0], id => null);
            U("tile.pick_empty_candidates", p.Chosen == -1 && p.Refused.Count == 0, "chosen " + p.Chosen);

            // read-back re-assert (2026-10-20: selection read back -1 after skipped candidates)
            int writesMade = 0, sel = -1;
            int w = C.WriteUntilReadBack(() => { writesMade++; sel = 17011; }, () => sel == 17011);
            U("tile.readback_first_write", w == 1 && writesMade == 1, "w " + w);
            writesMade = 0; sel = -1;
            w = C.WriteUntilReadBack(() => { writesMade++; sel = writesMade >= 2 ? 17011 : -1; }, () => sel == 17011);
            U("tile.readback_second_write_reported", w == 2 && writesMade == 2, "w " + w);
            writesMade = 0;
            w = C.WriteUntilReadBack(() => writesMade++, () => false);
            U("tile.readback_never_fails_negative", w == -3 && writesMade == 3, "w " + w);
            writesMade = 0;
            w = C.WriteUntilReadBack(() => writesMade++, () => false, 0);
            U("tile.readback_min_one_write", w == -1 && writesMade == 1, "w " + w);

            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
