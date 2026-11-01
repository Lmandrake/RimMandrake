// BESKAR_ARMORER_QUEST_1 spec section 7. Defaults are the shipped behaviour.
using System.Collections.Generic;
using System.Reflection;
using RimMandrake.Shared;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public class BeskarArmorerSettings : ModSettings
    {
        public static bool modEnabled = true;
        public static bool routeOneEnabled = true;
        public static bool routeTwoEnabled = true;
        public static bool harmRaidEnabled = true;
        public static int tributeOneIn = 5;
        public static float smeltSteelRatio = 1f / 3f;
        public static int prisonBreakEarliestDay = 30;
        public static float prisonBreakRefireDays = 60f;
        public static int revealDelayMinDays = 2;
        public static int revealDelayMaxDays = 5;

        // shipped value of every public static setting. MUST stay the LAST public static field initialiser in this class.
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(BeskarArmorerSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(BeskarArmorerSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            PatchApplier.BeforeExpose(typeof(BeskarArmorerSettings));
            Scribe_Values.Look(ref modEnabled, "modEnabled", true);
            Scribe_Values.Look(ref routeOneEnabled, "routeOneEnabled", true);
            Scribe_Values.Look(ref routeTwoEnabled, "routeTwoEnabled", true);
            Scribe_Values.Look(ref harmRaidEnabled, "harmRaidEnabled", true);
            Scribe_Values.Look(ref tributeOneIn, "tributeOneIn", 5);
            Scribe_Values.Look(ref smeltSteelRatio, "smeltSteelRatio", 1f / 3f);
            Scribe_Values.Look(ref prisonBreakEarliestDay, "prisonBreakEarliestDay", 30);
            Scribe_Values.Look(ref prisonBreakRefireDays, "prisonBreakRefireDays", 60f);
            Scribe_Values.Look(ref revealDelayMinDays, "revealDelayMinDays", 2);
            Scribe_Values.Look(ref revealDelayMaxDays, "revealDelayMaxDays", 5);
            PatchApplier.AfterExpose(typeof(BeskarArmorerSettings));
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();
        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        private static bool Group(Listing_Standard list, string title, SettingScope scope, string[] names)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label(SettingsKitCore.ScopeTag(scope) + (scope == SettingScope.NextPulse
                ? " changes apply the next time it is rolled or offered" : " changes apply to what is on the map now"));
            SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static void IntSlider(Listing_Standard list, string label, ref int v, int min, int max, string tip)
        {
            Rect r = list.GetRect(Text.LineHeight);
            TooltipHandler.TipRegion(r, tip);
            v = Mathf.RoundToInt(Widgets.HorizontalSlider(r, v, min, max, false, label + ": " + v));
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            PatchApplier.DrawNotice(list);
            searchQuery = SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "The Armorer", SettingScope.Now, new[] { "modEnabled", "tributeOneIn", "smeltSteelRatio" }))
            {
                list.CheckboxLabeled("Beskar Armorer enabled", ref modEnabled,
                    "Off: beskar is salvage only. No bill gate, no steel-and-slag replacement, no quest, no raid. A covert already found stays on the map.");
                IntSlider(list, "She keeps one piece in", ref tributeOneIn, 2, 10,
                    "Her tribute on every melt. Shipped: one in five.");
                smeltSteelRatio = list.SliderLabeled("Steel per beskar when smelted: " + smeltSteelRatio.ToString("0.00"), smeltSteelRatio, 0f, 1f,
                    tooltip: "Smelting beskar yourself gives this much steel per beskar (rounded up) and one slag chunk, never beskar. Shipped: a third.");
                list.GapLine();
            }
            if (Group(list, "Route 1: free a Blackstar Mandalorian", SettingScope.NextPulse, new[] { "routeOneEnabled", "revealDelayMinDays", "revealDelayMaxDays" }))
            {
                list.CheckboxLabeled("Freeing a Mandalorian starts the quest", ref routeOneEnabled,
                    "Off: releasing a captured Blackstar Mandalorian starts nothing.");
                IntSlider(list, "Fewest days before her coordinates arrive", ref revealDelayMinDays, 1, 30, "Shipped: 2.");
                IntSlider(list, "Most days before her coordinates arrive", ref revealDelayMaxDays, 1, 30, "Shipped: 5.");
                if (revealDelayMaxDays < revealDelayMinDays) revealDelayMaxDays = revealDelayMinDays;
                list.GapLine();
            }
            if (Group(list, "Route 2: the Imperial prison break", SettingScope.NextPulse, new[] { "routeTwoEnabled", "prisonBreakEarliestDay", "prisonBreakRefireDays" }))
            {
                list.CheckboxLabeled("Blackstar can offer the prison break", ref routeTwoEnabled, "Off: the offer never fires.");
                IntSlider(list, "Earliest day of the offer", ref prisonBreakEarliestDay, 0, 120, "Shipped: 30.");
                prisonBreakRefireDays = list.SliderLabeled("Days between offers: " + prisonBreakRefireDays.ToString("0"), prisonBreakRefireDays, 1f, 180f,
                    tooltip: "Shipped: 60.");
                list.GapLine();
            }
            if (Group(list, "Harming her", SettingScope.Now, new[] { "harmRaidEnabled" }))
            {
                list.CheckboxLabeled("Blackstar raids at once when you harm her", ref harmRaidEnabled,
                    "Off: harming her still loses the covert for good and records the heat, but sends no raid.");
                list.GapLine();
            }
            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class BeskarArmorerMod : Mod
    {
        public static BeskarArmorerSettings settings;

        public BeskarArmorerMod(ModContentPack content) : base(content) { settings = GetSettings<BeskarArmorerSettings>(); }

        public override string SettingsCategory() { return "Beskar Armorer"; }

        public override void DoSettingsWindowContents(Rect inRect) { settings.DoWindowContents(inRect); }

        public override void WriteSettings()
        {
            base.WriteSettings();
            ArmorerStartup.ApplySettings();
        }
    }
}
