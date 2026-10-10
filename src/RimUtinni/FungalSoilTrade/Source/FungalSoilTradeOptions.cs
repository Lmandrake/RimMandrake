using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.FungalSoilTrade
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Fungal Soil Trade.
    //
    // Named *Options*Mod rather than *FungalSoilTradeMod* on purpose: that
    // name is already taken by the [StaticConstructorOnStartup] Harmony
    // bootstrap class in MapComponent_RotFungalDistress.cs.
    //
    // Gates the two real runtime mechanics found in this mod's Source:
    //   1. GenStep_ScatterFungalGround — WORLDGEN-AFFECTING (new maps only):
    //      whether a Rot map generates mineable fungal soil at all.
    //   2. MapComponent_RotFungalDistress — the distress-and-defenders loop
    //      that fires when a player mines that soil; master on/off plus the
    //      build/decay rate constants as sliders, defaults = shipped values.
    public class FungalSoilTradeSettings : ModSettings
    {
        public static bool scatterEnabled = true;
        public static bool distressEnabled = true;
        public static float distressBuildRateMultiplier = 1f;
        public static float distressDecayRateMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scatterEnabled, "scatterEnabled", true);
            Scribe_Values.Look(ref distressEnabled, "distressEnabled", true);
            Scribe_Values.Look(ref distressBuildRateMultiplier, "distressBuildRateMultiplier", 1f);
            Scribe_Values.Look(ref distressDecayRateMultiplier, "distressDecayRateMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(FungalSoilTradeSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(FungalSoilTradeSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Fungal ground on the Rot (WORLDGEN-AFFECTING)", RimMandrake.Shared.SettingScope.NewMapsOnly, new[] { "scatterEnabled" }))
            {
                list.CheckboxLabeled("Scatter mineable fungal ground", ref scatterEnabled,
                    "Off: no new Rot (Mycotic Jungle) map generates fungal soil knots to dig. "
                  + "A map that already exists is never retroactively changed.");
                list.GapLine();
            }

            if (Group(list, "Fungal distress (mining the Rot's soil)", RimMandrake.Shared.SettingScope.Now, new[] { "distressEnabled", "distressBuildRateMultiplier", "distressDecayRateMultiplier" }))
            {
                list.CheckboxLabeled("Distress and defenders enabled", ref distressEnabled,
                    "Off: digging fungal soil never angers the mycelial network - no distress builds "
                  + "and nothing is ever summoned to defend it.");
                list.Label("Distress build rate: " + distressBuildRateMultiplier.ToString("0.00") + "x");
                list.Label("How fast digging fungal soil builds distress toward a defender response.");
                distressBuildRateMultiplier = list.Slider(distressBuildRateMultiplier, 0f, 3f);
                list.Label("Distress decay rate: " + distressDecayRateMultiplier.ToString("0.00") + "x");
                list.Label("How fast distress fades away once digging stops.");
                distressDecayRateMultiplier = list.Slider(distressDecayRateMultiplier, 0.25f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class FungalSoilTradeOptionsMod : Mod
    {
        public static FungalSoilTradeSettings settings;

        public FungalSoilTradeOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<FungalSoilTradeSettings>();
        }

        public override string SettingsCategory() => "Fungal Soil Trade";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
