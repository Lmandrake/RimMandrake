using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Aftermath
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Aftermath.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData).
    //
    // What this mod actually DOES at runtime: MapComponent_BattleRecorder
    // opens/closes BattleRecords (battle tracking + the ChronicleEvents.Raise
    // "battle.closed" publish other mods, e.g. Ninefold, subscribe to) and
    // AftermathRuleRunner turns a closed battle / a nearby mental break / a
    // long-held prisoner into a QUEUED follow-up incident (a forced raid-like
    // payload) against a target faction, subject to discipline caps.
    //
    // GATING CHOICE: the master switch below turns off only the QUEUEING of
    // aftermath incidents (AftermathRuleRunner's three trigger entry points).
    // It deliberately does NOT stop MapComponent_BattleRecorder itself —
    // that recorder is also the sole source of the "battle.closed"
    // ChronicleEvent other mods (Ninefold's ChronicleSubscriber) depend on
    // for their own, unrelated mechanics; killing it would silently break
    // a different mod's feature. All-off for Aftermath's OWN mechanic still
    // degrades cleanly: OnBattleClosed/OnMentalBreakNearBattle/
    // OnPrisonerHeldTooLong become no-ops, nothing is queued, no NREs.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AftermathSettings : ModSettings
    {
        // Master switch for AftermathRuleRunner's queued follow-up incidents.
        public static bool aftermathEnabled = true;

        // AftermathRuleRunner.PassesDiscipline's two shipped caps
        // (MaxPerFaction = 1, MaxTotal = 2 in the original hardcoded consts).
        public static int maxQueuedPerFaction = 1;
        public static int maxQueuedTotal = 2;

        // Rule 6's own window: "a mental break WITHIN 2 DAYS after a battle."
        public static float mentalBreakWindowDays = 2f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref aftermathEnabled, "aftermathEnabled", true);
            Scribe_Values.Look(ref maxQueuedPerFaction, "maxQueuedPerFaction", 1);
            Scribe_Values.Look(ref maxQueuedTotal, "maxQueuedTotal", 2);
            Scribe_Values.Look(ref mentalBreakWindowDays, "mentalBreakWindowDays", 2f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Battle aftermath switch", RimMandrake.Shared.SettingScope.NextPulse, new[] { "aftermathEnabled" }))
            {
                list.CheckboxLabeled("Battle aftermath enabled", ref aftermathEnabled,
                    "After a battle ends badly, a colonist has a mental break near one, or a prisoner "
                  + "is held too long, this can queue a follow-up raid-like event against the faction "
                  + "involved. Off: nothing is ever queued — battles are still tracked for other mods, "
                  + "but this mod's own follow-up events never fire.");
                list.GapLine();
            }

            if (Group(list, "Follow-up limits and windows", RimMandrake.Shared.SettingScope.NextPulse, new[] { "maxQueuedPerFaction", "maxQueuedTotal", "mentalBreakWindowDays" }))
            {
                list.Label("Max queued follow-ups for the same faction at once: " + maxQueuedPerFaction);
                maxQueuedPerFaction = (int)list.Slider(maxQueuedPerFaction, 1, 5);

                list.Label("Max queued follow-ups total, any faction: " + maxQueuedTotal);
                maxQueuedTotal = (int)list.Slider(maxQueuedTotal, 1, 8);

                list.Label("Mental-break window after a battle: " + mentalBreakWindowDays.ToString("0.0") + " days");
                list.Label("A colonist mental break this soon after a battle closes can also count as an aftermath trigger.");
                mentalBreakWindowDays = list.Slider(mentalBreakWindowDays, 0.5f, 7f);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 600f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field
        // initialisers. MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_AftermathSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(RM_AftermathSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
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
                ? " changes take effect the next time the game starts or loads"
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps (or planets) generated afterwards"
                : scope == RimMandrake.Shared.SettingScope.NextPulse ? " changes apply the next time it is rolled or offered"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class RM_AftermathMod : Mod
    {
        public static RM_AftermathSettings settings;

        public RM_AftermathMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_AftermathSettings>();
        }

        public override string SettingsCategory()
        {
            return "Battle Aftermath";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
