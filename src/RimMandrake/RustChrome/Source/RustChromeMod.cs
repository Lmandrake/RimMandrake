using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.RustChrome
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for RustChrome.
    //
    // This mod has exactly one mechanic: a one-time (well, live-togglable)
    // reflection recolour of a handful of Widgets/InspectPaneUtility UI
    // fields. There is no rate/chance/threshold to tune — the only honest
    // control is on/off, restoring the game's own stock colours when off.
    public class RustChromeSettings : ModSettings
    {
        public bool themeEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref themeEnabled, "themeEnabled", true);
        }


        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();  // instance settings: read from a fresh instance

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new RustChromeSettings();
            foreach (FieldInfo f in typeof(RustChromeSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RustChromeSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10).</summary>
        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 200f;

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            bool before = themeEnabled;
            // Scope audited: RustChromeColors.Apply swaps the stock colours live, so the toggle (and a reset) land now.
            if (Group(list, "Rust & Chrome UI theme", RimMandrake.Shared.SettingScope.Now, new[] { "themeEnabled" }))
            {
                list.CheckboxLabeled("Rust & Chrome UI theme", ref themeEnabled,
                    "Recolours a handful of menu/window backgrounds to a rusted brown-and-chrome "
                  + "palette. Off restores the game's own stock colours immediately.");
                list.GapLine();
            }
            if (themeEnabled != before)
            {
                RustChromeColors.Apply(themeEnabled);
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RustChromeMod : Mod
    {
        public static RustChromeSettings settings;

        public RustChromeMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RustChromeSettings>();
        }

        public override string SettingsCategory()
        {
            return "Rust & Chrome";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
