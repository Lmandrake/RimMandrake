using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot
{
    // MOD_OPTIONS_RETROFIT_1 / KYBER_TRADE_PLOT_1 — Mod Settings for this mod. Two switches, one per feature: what a
    // kyber sale moves (Imperial Heat on the Colony Visibility meter, Hutt interest, Cartel goodwill), and the plot that
    // follows (the Homestead visit and the donation). Off, each simply stops; nothing else reads them. The numbers are
    // the ones the experience is made of; defaults are the shipped behaviour.
    public class KyberTradePlotSettings : ModSettings
    {
        public static bool kyberTradePlotEnabled = true;
        public static bool kyberSalesDrawHeat = true;
        public static float heatPerSale = 15f;
        public static float heatCapPerSale = 40f;
        public static float huttInterestPerCrystal = 3f;
        public static int cartelGoodwillPerSale = 4;
        public static int visitAfterSales = 2;
        public static float fixerInterest = 15f;
        public static int homesteadGoodwillForthright = 8;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref kyberTradePlotEnabled, "kyberTradePlotEnabled", true);
            Scribe_Values.Look(ref kyberSalesDrawHeat, "kyberSalesDrawHeat", true);
            Scribe_Values.Look(ref heatPerSale, "heatPerSale", 15f);
            Scribe_Values.Look(ref heatCapPerSale, "heatCapPerSale", 40f);
            Scribe_Values.Look(ref huttInterestPerCrystal, "huttInterestPerCrystal", 3f);
            Scribe_Values.Look(ref cartelGoodwillPerSale, "cartelGoodwillPerSale", 4);
            Scribe_Values.Look(ref visitAfterSales, "visitAfterSales", 2);
            Scribe_Values.Look(ref fixerInterest, "fixerInterest", 15f);
            Scribe_Values.Look(ref homesteadGoodwillForthright, "homesteadGoodwillForthright", 8);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(KyberTradePlotSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(KyberTradePlotSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
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
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts or a save loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 400f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Selling kyber", RimMandrake.Shared.SettingScope.NextPulse,
                    new[] { "kyberSalesDrawHeat", "heatPerSale", "heatCapPerSale", "huttInterestPerCrystal", "cartelGoodwillPerSale" }))
            {
                list.CheckboxLabeled("A kyber sale draws the Empire and the Hutts", ref kyberSalesDrawHeat,
                    "Selling kyber (or a mindstone) in any trade window raises Imperial attention on the Colony Visibility meter, "
                  + "raises Hutt interest, and pleases the Hutt Cartel when they are the buyer. Gifts, crafting and the donation "
                  + "quest are never sales. Off: kyber sells like any other good.");
                list.Label("Imperial attention for a one-crystal sale: " + heatPerSale.ToString("F0")
                    + " (larger sales grow with the square root of the count)");
                heatPerSale = list.Slider(heatPerSale, 1f, 40f);
                list.Label("Most attention one sale can draw: " + heatCapPerSale.ToString("F0") + " (the meter's bands are 20 wide)");
                heatCapPerSale = list.Slider(heatCapPerSale, 5f, 100f);
                list.Label("Hutt interest per crystal sold: " + huttInterestPerCrystal.ToString("F1"));
                huttInterestPerCrystal = list.Slider(huttInterestPerCrystal, 0f, 10f);
                list.Label("Hutt Cartel goodwill per sale to the Cartel: " + cartelGoodwillPerSale);
                cartelGoodwillPerSale = (int)list.Slider(cartelGoodwillPerSale, 0f, 20f);
                list.GapLine();
            }
            if (Group(list, "The kyber plot", RimMandrake.Shared.SettingScope.NextPulse,
                    new[] { "kyberTradePlotEnabled", "visitAfterSales", "fixerInterest", "homesteadGoodwillForthright" }))
            {
                list.CheckboxLabeled("The alleged Jedi and the donation", ref kyberTradePlotEnabled,
                    "Once per campaign, after enough kyber sales, Homestead moisture farmers come to ask how the kyber was obtained. "
                  + "An answer opens the door to one ask: donate kyber to a cause fighting somewhere else, smuggled offworld. "
                  + "If the visit goes nowhere, the Hutts' fixer passes the ask along once Hutt interest is high enough. "
                  + "Off: neither ever comes.");
                list.Label("Sales before the Homestead visit: " + visitAfterSales);
                visitAfterSales = (int)list.Slider(visitAfterSales, 1f, 10f);
                list.Label("Hutt interest at which the fixer passes the ask along: " + fixerInterest.ToString("F0"));
                fixerInterest = list.Slider(fixerInterest, 1f, 100f);
                list.Label("Homestead goodwill for a straight answer: " + homesteadGoodwillForthright);
                homesteadGoodwillForthright = (int)list.Slider(homesteadGoodwillForthright, 0f, 30f);
                list.GapLine();
            }
            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class KyberTradePlotMod : Mod
    {
        public static KyberTradePlotSettings settings;

        public KyberTradePlotMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<KyberTradePlotSettings>();
        }

        public override string SettingsCategory()
        {
            return "Kyber Trade Plot";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
