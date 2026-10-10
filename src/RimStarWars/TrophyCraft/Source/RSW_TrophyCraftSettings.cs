using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.TrophyCraft
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Trophy Craft.
    // Precedent: src/RimStarWars/Shokk/Source/RSW_ShokkSettings.cs.
    //
    // One toggle (default ON, per the item's spec) plus one opinion
    // magnitude multiplier read by RSW_Thought_ObserverBraveFang.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_TrophyCraftSettings : ModSettings
    {
        public static bool socialConsequenceEnabled = true;
        public static float opinionMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref socialConsequenceEnabled, "socialConsequenceEnabled", true);
            Scribe_Values.Look(ref opinionMultiplier, "opinionMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RSW_TrophyCraftSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RSW_TrophyCraftSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the thought worker reads the switch and OpinionOffset reads the multiplier each time the thought is evaluated; nothing is read at map or world generation, so both are [now].</summary>
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

            if (Group(list, "Fang pendant social consequence", RimMandrake.Shared.SettingScope.Now, new[] { "socialConsequenceEnabled" }))
            {
                list.CheckboxLabeled("Fang pendant social consequence enabled", ref socialConsequenceEnabled,
                    "Observers whose faction is configured (the campaign's hunting tribes) form an "
                  + "opinion of anyone wearing the wyyyschokk fang pendant. Off: the pendant is a "
                  + "trade good and crafted item only, no social effect from anyone.");
                list.GapLine();
            }

            if (Group(list, "Opinion magnitude", RimMandrake.Shared.SettingScope.Now, new[] { "opinionMultiplier" }))
            {
                list.Label("Opinion magnitude: " + opinionMultiplier.ToString("0.00")
                    + "x (base +8 opinion)");
                opinionMultiplier = list.Slider(opinionMultiplier, 0f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RSW_TrophyCraftMod : Mod
    {
        public static RSW_TrophyCraftSettings settings;

        public RSW_TrophyCraftMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_TrophyCraftSettings>();
        }

        public override string SettingsCategory()
        {
            return "Trophy Craft";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
