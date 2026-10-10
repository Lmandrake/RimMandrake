using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ScavengerEvents
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ScavengerEvents.
    //
    // Seven incidents ship in this mod (RUT_SCAVENGEREVENTS_BUILD_1). Each
    // gets its own on/off toggle via IncidentWorker.CanFireNowSub, so a
    // disabled incident simply never fires again — StorytellerComp never
    // calls TryExecuteWorker, so this degrades with no NREs and no orphaned
    // defs. Three of the seven also carry a real tunable (a size/value/
    // threshold multiplier over the hardcoded number already in that
    // worker), exposed as a slider.
    public class ScavengerEventsSettings : ModSettings
    {
        public static bool migrationEnabled = true;
        public static bool survivalPodEnabled = true;
        public static bool podCrashTribalEnabled = true;
        public static bool insectEnabled = true;
        public static float insectSwarmSizeMultiplier = 1f;
        public static bool strokeEnabled = true;
        public static bool shipBreakEnabled = true;
        public static float shipBreakLootMultiplier = 1f;
        public static bool thanksgivingEnabled = true;
        public static float thanksgivingThresholdMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref migrationEnabled, "migrationEnabled", true);
            Scribe_Values.Look(ref survivalPodEnabled, "survivalPodEnabled", true);
            Scribe_Values.Look(ref podCrashTribalEnabled, "podCrashTribalEnabled", true);
            Scribe_Values.Look(ref insectEnabled, "insectEnabled", true);
            Scribe_Values.Look(ref insectSwarmSizeMultiplier, "insectSwarmSizeMultiplier", 1f);
            Scribe_Values.Look(ref strokeEnabled, "strokeEnabled", true);
            Scribe_Values.Look(ref shipBreakEnabled, "shipBreakEnabled", true);
            Scribe_Values.Look(ref shipBreakLootMultiplier, "shipBreakLootMultiplier", 1f);
            Scribe_Values.Look(ref thanksgivingEnabled, "thanksgivingEnabled", true);
            Scribe_Values.Look(ref thanksgivingThresholdMultiplier, "thanksgivingThresholdMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(ScavengerEventsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(ScavengerEventsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): all seven incidents are gated in CanFireNowSub / TryExecuteWorker and their size, loot and threshold multipliers are read when the incident fires, so every setting lands the next time that incident is rolled: [next pulse]. Nothing is read at map or world generation.</summary>
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
            list.Label("Each incident below can be turned off without affecting the others.");
            list.GapLine();
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Wildlife migration", RimMandrake.Shared.SettingScope.NextPulse, new[] { "migrationEnabled" }))
            {
                list.CheckboxLabeled("Wildlife migration", ref migrationEnabled,
                    "A small herd of biome-correct animals passes through the map.");
                list.GapLine();
            }

            if (Group(list, "Survival pod gift", RimMandrake.Shared.SettingScope.NextPulse, new[] { "survivalPodEnabled" }))
            {
                list.CheckboxLabeled("Survival pod gift", ref survivalPodEnabled,
                    "A drop pod with a survival outfit, meals, and a pistol.");
                list.GapLine();
            }

            if (Group(list, "Tribal pod crash (rescue)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "podCrashTribalEnabled" }))
            {
                list.CheckboxLabeled("Tribal pod crash (rescue)", ref podCrashTribalEnabled,
                    "A downed pawn from a friendly faction, dropped in a pod.");
                list.GapLine();
            }

            if (Group(list, "Insect swarm", RimMandrake.Shared.SettingScope.NextPulse, new[] { "insectEnabled", "insectSwarmSizeMultiplier" }))
            {
                list.CheckboxLabeled("Insect swarm", ref insectEnabled,
                    "Hostile Spelopedes and Megaspiders in permanent manhunter state.");
                list.Label("Swarm size: " + insectSwarmSizeMultiplier.ToString("0.00") + "x the normal count");
                insectSwarmSizeMultiplier = list.Slider(insectSwarmSizeMultiplier, 0.5f, 2f);
                list.GapLine();
            }

            if (Group(list, "Colonist stroke", RimMandrake.Shared.SettingScope.NextPulse, new[] { "strokeEnabled" }))
            {
                list.CheckboxLabeled("Colonist stroke", ref strokeEnabled,
                    "A random colonist collapses, downed, with a mood hit.");
                list.GapLine();
            }

            if (Group(list, "Ship break (cargo rain)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "shipBreakEnabled", "shipBreakLootMultiplier" }))
            {
                list.CheckboxLabeled("Ship break (cargo rain)", ref shipBreakEnabled,
                    "Loot drop plus a downed survivor and a corpse, each in their own pod.");
                list.Label("Ship break loot: " + shipBreakLootMultiplier.ToString("0.00") + "x the normal value");
                shipBreakLootMultiplier = list.Slider(shipBreakLootMultiplier, 0.5f, 2f);
                list.GapLine();
            }

            if (Group(list, "Emergency food relief (Thanksgiving)", RimMandrake.Shared.SettingScope.NextPulse, new[] { "thanksgivingEnabled", "thanksgivingThresholdMultiplier" }))
            {
                list.CheckboxLabeled("Emergency food relief (\"Thanksgiving\")", ref thanksgivingEnabled,
                    "Free meals dropped when the colony is close to running out of food.");
                list.Label("Fires when food is below " + thanksgivingThresholdMultiplier.ToString("0.00") + "x the normal hunger threshold");
                thanksgivingThresholdMultiplier = list.Slider(thanksgivingThresholdMultiplier, 0.5f, 2f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class ScavengerEventsMod : Mod
    {
        public static ScavengerEventsSettings settings;

        public ScavengerEventsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ScavengerEventsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Scavenger Events";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
