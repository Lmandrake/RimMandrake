using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShokkweaveEconomy
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Shokkweave Economy.
    //
    // Pattern copied verbatim from
    // src/RimUtinni/FungalSoilTrade/Source/FungalSoilTradeOptions.cs — this
    // mod ships one runtime mechanic in Source: GenStep_ScatterWebworkSilk,
    // which scatters the two Webwork harvest nodes (RUT_Webwork_SilkKnot,
    // RUT_Webwork_Nest) onto RUT_Webwork maps only. WORLDGEN-AFFECTING (new
    // maps only, per that GenStep's own header). Default ON — matches
    // shipped behavior.
    public class ShokkweaveEconomySettings : ModSettings
    {
        public static bool scatterEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scatterEnabled, "scatterEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ShokkweaveEconomySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ShokkweaveEconomySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): scatterEnabled is read only by GenStep_ScatterWebworkSilk when a RUT_Webwork map is generated, so it is [new maps only] and labelled worldgen-affecting.</summary>
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
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

            if (Group(list, "Webwork silk nodes (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "scatterEnabled" }))
            {
                list.CheckboxLabeled("Scatter Webwork silk knots and nests", ref scatterEnabled,
                    "Off: no new RUT_Webwork map generates the harvestable silk-knot or nest "
                  + "scatter groups. A map that already exists is never retroactively changed. "
                  + "This does not touch the sole-source shokkweave/hyperweave campaign ruling "
                  + "itself (design/Jawa/worldbuilding/biomes/the_webwork.md section 6 ban 4) - it only "
                  + "gates whether this mod's own map-generation step runs.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class ShokkweaveEconomyMod : Mod
    {
        public static ShokkweaveEconomySettings settings;

        public ShokkweaveEconomyMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShokkweaveEconomySettings>();
        }

        public override string SettingsCategory() => "Shokkweave Economy";

        public override void DoSettingsWindowContents(UnityEngine.Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
