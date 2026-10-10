using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.WasteRun
{
    // MOD_OPTIONS_RETROFIT_1 doctrine: independent toggles, defaults = shipped behavior.
    public class WasteRunSettings : ModSettings
    {
        public static bool masterEnabled = true;
        public static bool offerEnabled = true;
        public static bool dropOnEmpireEnabled = true;
        public static bool freezeColdSideEnabled = true;
        public static bool entombAssailantsEnabled = true;
        public static bool propaneLakeEnabled = true;
        public static bool slimeExperimentEnabled = true;
        // THROAT_CASK_ITEM_1 (numbers PROVISIONAL)
        public static bool throatCaskEnabled = true;
        public static bool throatRadiationEnabled = true;
        public static bool throatShipFaultsEnabled = true;
        public static bool throatBurstEnabled = true;
        public static bool throatDecayEnabled = true;

        public static bool DestinationEnabled(WasteDestination d)
        {
            switch (d)
            {
                case WasteDestination.DropOnEmpire: return dropOnEmpireEnabled;
                case WasteDestination.FreezeColdSide: return freezeColdSideEnabled;
                case WasteDestination.EntombAssailants: return entombAssailantsEnabled;
                case WasteDestination.IgnitePropaneLake: return propaneLakeEnabled;
                default: return slimeExperimentEnabled;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref masterEnabled, "masterEnabled", true);
            Scribe_Values.Look(ref offerEnabled, "offerEnabled", true);
            Scribe_Values.Look(ref dropOnEmpireEnabled, "dropOnEmpireEnabled", true);
            Scribe_Values.Look(ref freezeColdSideEnabled, "freezeColdSideEnabled", true);
            Scribe_Values.Look(ref entombAssailantsEnabled, "entombAssailantsEnabled", true);
            Scribe_Values.Look(ref propaneLakeEnabled, "propaneLakeEnabled", true);
            Scribe_Values.Look(ref slimeExperimentEnabled, "slimeExperimentEnabled", true);
            Scribe_Values.Look(ref throatCaskEnabled, "throatCaskEnabled", true);
            Scribe_Values.Look(ref throatRadiationEnabled, "throatRadiationEnabled", true);
            Scribe_Values.Look(ref throatShipFaultsEnabled, "throatShipFaultsEnabled", true);
            Scribe_Values.Look(ref throatBurstEnabled, "throatBurstEnabled", true);
            Scribe_Values.Look(ref throatDecayEnabled, "throatDecayEnabled", true);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(WasteRunSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(WasteRunSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1200f;
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
                ? " changes take effect the next time the game starts"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Waste run and destinations", RimMandrake.Shared.SettingScope.Now, new[] { "masterEnabled", "dropOnEmpireEnabled", "freezeColdSideEnabled", "entombAssailantsEnabled", "propaneLakeEnabled", "slimeExperimentEnabled" }))
            {
                list.CheckboxLabeled("Waste run enabled", ref masterEnabled,
                    "Master switch. Off: no waste-run quest is offered and the cask bay shows no destination commands.");
                list.CheckboxLabeled("Destination: drop it on the Empire", ref dropOnEmpireEnabled,
                    "Shipped default: ON. An act of war dressed as sanitation: Empire goodwill collapses.");
                list.CheckboxLabeled("Destination: freeze it on the cold side", ref freezeColdSideEnabled,
                    "Shipped default: ON. The honest coward's option. Costs nothing now.");
                list.CheckboxLabeled("Destination: entomb it on the Assailants", ref entombAssailantsEnabled,
                    "Shipped default: ON. The Rakatan solution, re-enacted. Buys decades; costs a conscience.");
                list.CheckboxLabeled("Destination: the propane lakes", ref propaneLakeEnabled,
                    "Shipped default: ON. A melt that ignites the nightside lake and marks the war lab breached (the lab itself is a stub until ANCIENT_WAR_LAB_1 ships).");
                list.CheckboxLabeled("Destination: the Slime experiment", ref slimeExperimentEnabled,
                    "Shipped default: ON. The only option that is an experiment rather than a verdict. Results are random and provisional.");
                list.GapLine();
            }

            if (Group(list, "Quest offers", RimMandrake.Shared.SettingScope.NextPulse, new[] { "offerEnabled" }))
            {
                list.CheckboxLabeled("Offer the waste-run quest", ref offerEnabled,
                    "Shipped default: ON. Once a cask bay holds waste, the Junkers' broker may offer the run. Off: no new offers (a quest already accepted still works). Read when the storyteller next rolls the offer.");
                list.GapLine();
            }

            if (Group(list, "Throat cask", RimMandrake.Shared.SettingScope.Now, new[] { "throatCaskEnabled", "throatRadiationEnabled", "throatShipFaultsEnabled", "throatBurstEnabled", "throatDecayEnabled" }))
            {
                list.CheckboxLabeled("Throat cask effects enabled", ref throatCaskEnabled,
                    "Shipped default: ON. Off: the Throat cask is inert cargo (all its numbers are provisional).");
                list.CheckboxLabeled("  Constant radiation", ref throatRadiationEnabled, "Shipped default: ON. A bay mutes the dose, never silences it.");
                list.CheckboxLabeled("  Gravship malfunctions while aboard", ref throatShipFaultsEnabled, "Shipped default: ON. One random system fault about every day.");
                list.CheckboxLabeled("  Bursts if the carrier is hurt or it burns", ref throatBurstEnabled, "Shipped default: ON.");
                list.CheckboxLabeled("  Slow armageddon nearby (die-off, mood)", ref throatDecayEnabled, "Shipped default: ON. Escalates the longer it stays.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class WasteRunMod : Mod
    {
        public static WasteRunSettings settings;

        public WasteRunMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WasteRunSettings>();
        }

        public override string SettingsCategory()
        {
            return "Waste Run";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
