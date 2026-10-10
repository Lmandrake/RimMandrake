using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipMemory
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ShipMemory.
    //
    // One mechanism: GameComponent_ShipMemory reveals the Memory-Core
    // containment building the moment the clan ties down a live beast,
    // stockpiles enough Bioferrite, or the Assailant dungeon signals it. A
    // master toggle lets a player who doesn't want the automatic reveal turn
    // it off; the Bioferrite stockpile threshold is the one hardcoded number
    // worth a slider.
    public class ShipMemorySettings : ModSettings
    {
        public static bool shipMemoryEnabled = true;
        public static float bioferriteThreshold = 50f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shipMemoryEnabled, "shipMemoryEnabled", true);
            Scribe_Values.Look(ref bioferriteThreshold, "bioferriteThreshold", 50f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ShipMemorySettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ShipMemorySettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): GameComponentTick checks the switch and the Bioferrite threshold every few seconds and the dungeon signal handler checks the switch when it arrives; nothing is read at map or world generation, so both are [now].</summary>
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

            if (Group(list, "Memory-Core reveal", RimMandrake.Shared.SettingScope.Now, new[] { "shipMemoryEnabled" }))
            {
                list.CheckboxLabeled("Reveal the Memory-Core automatically", ref shipMemoryEnabled,
                    "Off: the containment building is never auto-discovered by this mod's triggers "
                  + "(taming a beast, stockpiling Bioferrite, or the Assailant dungeon signal).");
                list.GapLine();
            }

            if (Group(list, "Bioferrite stockpile trigger", RimMandrake.Shared.SettingScope.Now, new[] { "bioferriteThreshold" }))
            {
                list.Label("Bioferrite stockpile threshold: " + Mathf.RoundToInt(bioferriteThreshold));
                bioferriteThreshold = list.Slider(bioferriteThreshold, 10f, 200f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class ShipMemoryMod : Mod
    {
        public static ShipMemorySettings settings;

        public ShipMemoryMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShipMemorySettings>();
        }

        public override string SettingsCategory()
        {
            return "Ship Memory";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
