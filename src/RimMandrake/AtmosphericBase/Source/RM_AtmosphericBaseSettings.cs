using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    // ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 settings (spec §5). Defaults = shipped behaviour. INSTANCE fields reached
    // through Cur, never public statics: the bridge's settings setter refuses a static field (Pits pilot, 2026-09-12).
    // Only switches that gate something built exist here; the sound channel, default scheme, group selection, showcase
    // and bed volume arrive with the phases that build them.
    public class RM_AtmosphericBaseSettings : ModSettings
    {
        public bool lightChannel = true;
        public bool playerTakeoverButton = true;

        private static readonly RM_AtmosphericBaseSettings Defaults = new RM_AtmosphericBaseSettings();

        public static RM_AtmosphericBaseSettings Cur => RM_AtmosphericBaseMod.settings ?? Defaults;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lightChannel, "lightChannel", true);
            Scribe_Values.Look(ref playerTakeoverButton, "playerTakeoverButton", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public instance bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            var fresh = new RM_AtmosphericBaseSettings();
            foreach (FieldInfo f in typeof(RM_AtmosphericBaseSettings).GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(fresh);
            return d;
        }

        public void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_AtmosphericBaseSettings).GetField(n, BindingFlags.Public | BindingFlags.Instance);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(this, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        private bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names)
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
            list.Label(RimMandrake.Shared.SettingsKitCore.ScopeTag(scope) + " changes apply to what is on the map now");
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

            // Scopes audited per read site: both switches are read every frame (map component) and on every button query.
            if (Group(list, "Light channel", RimMandrake.Shared.SettingScope.Now, new[] { "lightChannel" }))
            {
                list.CheckboxLabeled("Atmospheric Base may drive lights", ref lightChannel,
                    "Off: every light handed to Atmospheric Base is given back at once, at exactly the colour it had, "
                  + "and nothing can be handed over. With this off the game is lit as if the mod were absent.");
                list.GapLine();
            }

            if (Group(list, "Hand-over buttons", RimMandrake.Shared.SettingScope.Now, new[] { "playerTakeoverButton" }))
            {
                list.CheckboxLabeled("Show the hand-over buttons on lights", ref playerTakeoverButton,
                    "Selecting a lamp, wall light or floor light you own shows \"Hand glow to Atmospheric Base\" and "
                  + "\"Take glow back\". Off: the buttons are hidden; lights already handed over stay handed over, and "
                  + "scenarios and other mods can still hand lights over. Maps whose scenario decides never show them.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }
}
