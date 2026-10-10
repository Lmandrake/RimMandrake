using System.Collections.Generic;
using System.Reflection;
// MOD_OPTIONS_RETROFIT_1 — Mod Settings for the Long Hunger.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static fields
// read from everywhere, Scribe_Values in ExposeData, DoWindowContents helper
// called from the Mod subclass).
//
// What is real here: a single quest-gated VAST creature (LongHungerThing) whose
// eruption/tremor/submerge numbers are hardcoded consts, fired by
// IncidentWorker_LongHungerSurfaces only from Quest_LongHunger.xml. Disabling the
// encounter does NOT fail the quest — the quest's own Delay/reward chain runs off
// its own timer signal (ContractDue), independent of whether the incident ever
// fires (see Quest_LongHunger.xml: QuestNode_CreateIncidents and QuestNode_Delay
// are parallel nodes, not sequenced on one another) — so "no encounter, contract
// still resolves" is a safe, graceful off-switch.
using RimWorld;
using UnityEngine;
using Verse;

namespace LongHunger
{
    public class LongHungerSettings : ModSettings
    {
        // Master switch for the creature itself. Off: the incident never spawns
        // RUT_LongHunger, but the quest's own contract fee still pays out on its
        // timer — nothing else in the quest depends on the encounter firing.
        public static bool encounterEnabled = true;

        // Scales EruptionDamage (90) and PulseDamage (45) together.
        public static float damageMultiplier = 1f;

        // Scales SurfacedDurationTicks (2500 = 1 in-game hour) and
        // PulseIntervalTicks (600 = 14 in-game minutes) together, so the pulse
        // cadence stays proportional to how long the creature stays surfaced.
        public static float durationMultiplier = 1f;

        // Scales the salvage value range (600-1400) dropped on submerging.
        public static float lootValueMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref encounterEnabled, "encounterEnabled", true);
            Scribe_Values.Look(ref damageMultiplier, "damageMultiplier", 1f);
            Scribe_Values.Look(ref durationMultiplier, "durationMultiplier", 1f);
            Scribe_Values.Look(ref lootValueMultiplier, "lootValueMultiplier", 1f);
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(LongHungerSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(LongHungerSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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

            if (Group(list, "Whether it surfaces", RimMandrake.Shared.SettingScope.NextPulse, new[] { "encounterEnabled" }))
            {
                list.CheckboxLabeled("The Long Hunger can surface", ref encounterEnabled,
                    "Off: the quest's salvage contract still pays out on its timer, but the "
                  + "creature never erupts onto your map. On by default.");
                list.GapLine();
            }

            if (Group(list, "Eruption, tremors and salvage", RimMandrake.Shared.SettingScope.Now, new[] { "damageMultiplier", "durationMultiplier", "lootValueMultiplier" }))
            {
                list.Label("Damage: " + damageMultiplier.ToString("0.00") + "x");
                list.Label("Scales both the initial eruption (90 damage, radius 4.5) and each "
                  + "tremor pulse (45 damage, radius 3) that follows.");
                damageMultiplier = list.Slider(damageMultiplier, 0.25f, 3f);
                list.Label("Surfaced duration: " + durationMultiplier.ToString("0.00") + "x");
                list.Label("Scales how long it stays up (default 1 in-game hour) and the gap "
                  + "between tremor pulses (default 14 in-game minutes) together.");
                durationMultiplier = list.Slider(durationMultiplier, 0.25f, 3f);
                list.Label("Salvage value: " + lootValueMultiplier.ToString("0.00") + "x");
                list.Label("Scales the value of the loot dropped when it submerges "
                  + "(default 600-1400 silver-equivalent).");
                lootValueMultiplier = list.Slider(lootValueMultiplier, 0f, 3f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class LongHungerMod : Mod
    {
        public static LongHungerSettings settings;

        public LongHungerMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LongHungerSettings>();
        }

        public override string SettingsCategory()
        {
            return "The Long Hunger";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
