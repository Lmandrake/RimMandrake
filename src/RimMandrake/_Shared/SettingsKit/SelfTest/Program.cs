// Settings kit selftest: reset restores shipped defaults, search is case-insensitive, scope tag never changes a value.
using System;
using System.Collections.Generic;
using RimMandrake.Shared;

namespace RimMandrake.Shared.SelfTest
{
    internal static class Program
    {
        private static int fails;
        private static void Check(bool ok, string what) { if (!ok) { fails++; Console.WriteLine("FAIL " + what); } }

        private static int Main()
        {
            var flow = new SettingSection("Excavation and flow")
                .Add("depth", "Depth engine", true)
                .Add("pulse", "Flow pulse ticks", 600f, SettingScope.NextPulse)
                .Add("budget", "Source budget", 12, SettingScope.NewMapsOnly);
            var other = new SettingSection("Rivers").Add("rivers", "River flow", true, SettingScope.NewPondsOnly);

            var v = new Dictionary<string, object> { { "depth", false }, { "pulse", 90f }, { "budget", 99 }, { "rivers", false } };
            Check(SettingsKitCore.IsModified(flow, v), "modified section reads modified");
            int n = SettingsKitCore.ResetSection(flow, v);
            Check(n == 3, "reset reports 3 controls");
            Check((bool)v["depth"] == true && (float)v["pulse"] == 600f && (int)v["budget"] == 12, "reset restores shipped defaults");
            Check((bool)v["rivers"] == false, "reset of one section leaves another section alone");
            Check(!SettingsKitCore.IsModified(flow, v) && SettingsKitCore.IsModified(other, v), "IsModified follows reset");

            Check(SettingsKitCore.Matches("Flow pulse ticks", "PULSE"), "search is case-insensitive");
            Check(SettingsKitCore.Matches("Flow pulse ticks", "  pulse "), "search trims the query");
            Check(!SettingsKitCore.Matches("Flow pulse ticks", "zzz"), "non-match filtered");
            Check(SettingsKitCore.Matches("anything", ""), "blank query matches all");
            Check(SettingsKitCore.Matches("anything", null), "null query matches all");
            Check(SettingsKitCore.Visible(flow, "budget").Count == 1, "visible filters to one control");
            Check(SettingsKitCore.Visible(flow, "EXCAVATION").Count == 3, "title match shows the whole section");
            Check(SettingsKitCore.Visible(flow, "").Count == 3, "no query shows all");
            Check(SettingsKitCore.Visible(other, "pulse").Count == 0, "section with no hit shows none");

            var before = new Dictionary<string, object>(v);
            foreach (SettingControl c in flow.Controls) { SettingsKitCore.ScopeTag(c.Scope); SettingsKitCore.TaggedLabel(c); }
            bool same = true;
            foreach (var kv in before) if (!Equals(v[kv.Key], kv.Value)) same = false;
            Check(same, "scope tag / tagged label never change a stored value");
            Check(SettingsKitCore.ScopeTag(SettingScope.Now) == "[now]", "tag now");
            Check(SettingsKitCore.ScopeTag(SettingScope.NewMapsOnly) == "[new maps only]", "tag new maps only");
            Check(SettingsKitCore.TaggedLabel(flow.Controls[1]) == "Flow pulse ticks [next pulse]", "tagged label text");

            Console.WriteLine(fails == 0 ? "settings kit selftest: PASS" : "settings kit selftest: " + fails + " FAIL");
            return fails == 0 ? 0 : 1;
        }
    }
}
