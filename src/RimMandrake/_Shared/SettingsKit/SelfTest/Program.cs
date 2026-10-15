// Settings kit selftest: reset restores shipped defaults, search is case-insensitive, scope tag never changes a value;
// SettingsKitMasters: master-switch liveness (chains, several masters, independents, cycles refused) and reset-all.
using System;
using System.Collections.Generic;
using RimMandrake.Shared;

namespace RimMandrake.Shared.SelfTest
{
    internal enum Mode { Auto, CPU, Off }

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

            // SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST: master switches, chains, independents, reset-all
            var deps = new SettingDependencies()
                .Declare("enabled", "tapsEnabled", "sag")
                .Declare("tapsEnabled", "tapEvents", "tapRate")
                .Declare("tapEvents", "theftGoodwill")
                .Declare("theftGoodwill", "perDay")
                .Declare("breakReadout", "whip").Declare("enabled", "whip")
                .Independent("explosionsCut")
                .Name("enabled", "Aerial power lines");
            var on = new Dictionary<string, object> { { "enabled", true }, { "tapsEnabled", true }, { "tapEvents", true },
                { "theftGoodwill", true }, { "breakReadout", true }, { "sway", Mode.Auto } };
            Func<string, bool> isOn = k => SettingsKitMasters.IsOn(on.TryGetValue(k, out object x) ? x : null);
            Check(deps.IsLive("perDay", isOn), "chain all on: live");
            on["tapsEnabled"] = false;
            Check(!deps.IsLive("perDay", isOn) && !deps.IsLive("tapEvents", isOn), "a master off greys the whole chain under it");
            Check(deps.IsLive("sag", isOn) && deps.IsLive("tapsEnabled", isOn), "siblings and the master itself stay live");
            Check(deps.OffMasters("perDay", isOn).Count == 1 && deps.OffMasters("perDay", isOn)[0] == "tapsEnabled", "tooltip names the off master");
            on["tapsEnabled"] = true; on["enabled"] = false;
            Check(!deps.IsLive("perDay", isOn), "top master off greys three levels down");
            on["enabled"] = true; on["breakReadout"] = false;
            Check(!deps.IsLive("whip", isOn), "two masters: either off greys");
            on["breakReadout"] = true;
            Check(deps.IsLive("whip", isOn), "two masters both on: live");
            Check(deps.IsLive("explosionsCut", isOn) && deps.IsLive("notDeclared", isOn), "independent and undeclared keys are always live");
            Check(deps.IsMaster("tapEvents") && deps.IsDependent("tapEvents") && deps.IsIndependent("explosionsCut"), "classification");
            var unc = deps.Unclassified(new[] { "enabled", "sag", "explosionsCut", "forgotten" });
            Check(unc.Count == 1 && unc[0] == "forgotten", "a setting neither master, dependent nor independent is reported");
            Check(deps.NameOf("enabled") == "Aerial power lines" && deps.NameOf("tapsEnabled") == "tapsEnabled", "names");
            bool threw = false;
            try { deps.Declare("perDay", "enabled"); } catch (ArgumentException) { threw = true; }
            Check(threw, "a cycle is refused");
            threw = false;
            try { new SettingDependencies().Declare("a", "a"); } catch (ArgumentException) { threw = true; }
            Check(threw, "self-dependency refused");
            Check(SettingsKitMasters.IsOn(true) && !SettingsKitMasters.IsOn(false), "IsOn bool");
            Check(SettingsKitMasters.IsOn(Mode.Auto) && !SettingsKitMasters.IsOn(Mode.Off), "IsOn enum: Off is off");
            Check(SettingsKitMasters.IsOn(2) && !SettingsKitMasters.IsOn(0) && !SettingsKitMasters.IsOn(0f) && !SettingsKitMasters.IsOn(null), "IsOn numbers/null");

            // scope state: a sub-switch with its own dependents stays drawable while it is off; greyed only when nothing is live
            on["enabled"] = true; on["tapsEnabled"] = true; on["tapEvents"] = false;
            bool g = SettingsKitMasters.ScopeGreyed(deps, new[] { "tapEvents", "theftGoodwill", "perDay" }, isOn, out bool[] dead, out List<string> offM);
            Check(!g && !dead[0] && dead[1] && dead[2], "sub-switch off: scope drawable, the switch live, its dependents restored");
            g = SettingsKitMasters.ScopeGreyed(deps, new[] { "theftGoodwill", "perDay" }, isOn, out dead, out offM);
            Check(g && dead[0] && dead[1] && offM.Count == 1 && offM[0] == "tapEvents", "nested scope greyed, tooltip names the outside master");
            on["enabled"] = false;
            g = SettingsKitMasters.ScopeGreyed(deps, new[] { "tapsEnabled", "tapRate", "tapEvents" }, isOn, out dead, out offM);
            Check(g && offM.Contains("enabled") && !offM.Contains("tapsEnabled"), "top master off greys the block; scope keys are not named as causes");
            on["enabled"] = true; on["tapEvents"] = true;
            g = SettingsKitMasters.ScopeGreyed(deps, new[] { "tapsEnabled", "tapRate" }, isOn, out dead, out offM);
            Check(!g && !dead[0] && !dead[1], "all on: nothing greyed, nothing restored");
            g = SettingsKitMasters.ScopeGreyed(null, new[] { "x" }, isOn, out dead, out offM);
            Check(!g && dead.Length == 1 && !dead[0], "no declarations: a scope changes nothing");

            // reset all: every section, after a confirmation text that names the scope
            var secs = new List<SettingSection> { flow, other };
            var all = new Dictionary<string, object> { { "depth", false }, { "pulse", 1f }, { "budget", 1 }, { "rivers", false } };
            int na = SettingsKitMasters.ResetAll(secs, all);
            Check(na == 4, "reset all reports every control");
            Check((bool)all["depth"] && (bool)all["rivers"] && (float)all["pulse"] == 600f && (int)all["budget"] == 12, "reset all restores every section");
            Check(SettingsKitMasters.ResetAllConfirmText("Gimme Some Slack").Contains("Gimme Some Slack") && SettingsKitMasters.ResetAllConfirmText(null).Contains("cannot be undone"), "confirm text");
            Check(SettingsKitMasters.ResetAllLabel == "Reset all to defaults", "reset-all label");

            Console.WriteLine(fails == 0 ? "settings kit selftest: PASS" : "settings kit selftest: " + fails + " FAIL");
            return fails == 0 ? 0 : 1;
        }
    }
}
