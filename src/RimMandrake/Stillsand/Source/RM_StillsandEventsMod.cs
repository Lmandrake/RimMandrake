using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_EVENT_CREATURES_1 §8 — Mod Settings for the event creatures:
    // a toggle and an odds slider per sand-leviathan incident, and the
    // muurrok's mirror beam. Its own Mod class (RimWorld instantiates every
    // Mod subclass in an assembly, each with its own settings file), so the
    // biome's RM_StillsandSettings stays separate.
    //
    // The list is built from the def database: every IncidentDef whose worker
    // is RM_IncidentWorker_SandLeviathan, so the krayt attack (an XML-only
    // consumer in mandrake.rut.patches) gets its row here with no code of its own.
    // Defaults are shipped behaviour: on, odds ×1.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillsandEventsSettings : ModSettings
    {
        public static bool mirrorBeamEnabled = true;
        // PROVISIONAL (auto-decided 2026-10-09, MIRROR_BEAM_SUN_POLICY_1): the muurrok's beam reads the same sun as
        // the sun lance and sun tables (pinned sun, shade grid, roof, gale). Off: vanilla celestial glow, as before.
        public static bool mirrorBeamSharedSun = true;

        // STILLSAND_EVENT_CREATURES_REMAINDER_1: the horn, its answer chance, and the den quest.
        public static bool hornEnabled = true;
        public static float hornAnswerChance = 0.15f;
        public static bool denQuestEnabled = true;

        private static Dictionary<string, bool> disabled = new Dictionary<string, bool>();
        private static Dictionary<string, float> odds = new Dictionary<string, float>();

        public static bool EnabledFor(IncidentDef def)
        {
            return def != null && !(disabled.TryGetValue(def.defName, out bool off) && off);
        }

        public static float OddsFor(IncidentDef def)
        {
            return def != null && odds.TryGetValue(def.defName, out float f) ? Mathf.Max(0f, f) : 1f;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref mirrorBeamEnabled, "mirrorBeamEnabled", true);
            Scribe_Values.Look(ref mirrorBeamSharedSun, "mirrorBeamSharedSun", true);
            Scribe_Values.Look(ref hornEnabled, "hornEnabled", true);
            Scribe_Values.Look(ref hornAnswerChance, "hornAnswerChance", 0.15f);
            Scribe_Values.Look(ref denQuestEnabled, "denQuestEnabled", true);
            Scribe_Collections.Look(ref disabled, "leviathanDisabled", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref odds, "leviathanOdds", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                disabled = disabled ?? new Dictionary<string, bool>();
                odds = odds ?? new Dictionary<string, float>();
            }
        }

        /// <summary>One toggle and one odds slider per leviathan incident, built from the def database.</summary>
        private static void DrawIncidentRows(Listing_Standard list)
        {
            List<IncidentDef> incidents = DefDatabase<IncidentDef>.AllDefsListForReading
                .Where(d => d.workerClass != null && typeof(RM_IncidentWorker_SandLeviathan).IsAssignableFrom(d.workerClass))
                .ToList();
            if (incidents.Count == 0)
            {
                list.Label("No leviathan incidents are loaded.");
            }
            foreach (IncidentDef d in incidents)
            {
                bool on = EnabledFor(d);
                list.CheckboxLabeled(d.LabelCap + " incident", ref on,
                    "Off: this incident never fires. Leviathans already on the map finish their visit.");
                disabled[d.defName] = !on;
                float f = OddsFor(d);
                f = list.SliderLabeled(d.LabelCap + " odds: x" + f.ToString("0.00"), f, 0f, 3f,
                    tooltip: "Multiplies the incident's base chance. 1 is the shipped value.");
                odds[d.defName] = Mathf.Round(f * 20f) / 20f;
                list.Gap(6f);
            }
        }

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(RM_StillsandEventsSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                if (n == "leviathanDisabled") { disabled.Clear(); continue; }
                if (n == "leviathanOdds") { odds.Clear(); continue; }
                FieldInfo f = typeof(RM_StillsandEventsSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the leviathan incident toggles are read in CanFireNowSub and the odds in BaseChanceThisGame (storyteller rolls, NextPulse); the den quest is read when the quest script is tested for an offer (NextPulse); the beam and horn are read per use (Now).</summary>
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
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            list.Label("Event creatures: the leviathans that come up out of the sand on a Stillsand map. "
                       + "Each comes as an incident, warns first (a letter and a growing rumble), and "
                       + "leaves a funnel or a drag mark for everything it takes.");
            list.GapLine();

            if (Group(list, "Leviathan incidents", RimMandrake.Shared.SettingScope.NextPulse, new[] { "leviathanDisabled", "leviathanOdds" }))
            {
                DrawIncidentRows(list);
                list.GapLine();
            }

            if (Group(list, "Muurrok mirror beam", RimMandrake.Shared.SettingScope.Now, new[] { "mirrorBeamEnabled", "mirrorBeamSharedSun" }))
            {
                list.CheckboxLabeled("Muurrok mirror beam", ref mirrorBeamEnabled,
                    "The muurrok reflects the sun off its crest as a sweeping heat beam (never fire). "
                    + "It needs sun: none at night, under a roof, or in a sand gale. Off: it only strikes from under.");
                if (mirrorBeamEnabled)
                {
                    list.CheckboxLabeled("  Muurrok beam uses the sun-lance sun", ref mirrorBeamSharedSun,
                        "On: the beam's strength follows the same sun as the sun lance and sun tables (this map's sun "
                        + "height, shade from walls and dunes, roof, gale). Off: it follows the plain day/night light level.");
                }
                list.GapLine();
            }

            if (Group(list, "Krayt horn", RimMandrake.Shared.SettingScope.Now, new[] { "hornEnabled", "hornAnswerChance" }))
            {
                list.CheckboxLabeled("Krayt horn", ref hornEnabled,
                    "A horn that can be blown to rout smaller predators and tribal raiders nearby. Off: it cannot be used.");
                hornAnswerChance = list.SliderLabeled("Chance the call is answered: " + (hornAnswerChance * 100f).ToString("0") + "%",
                    hornAnswerChance, 0f, 1f,
                    tooltip: "Every blow rolls this; on a hit the krayt attack is queued a few hours out. 0 means never.");
                hornAnswerChance = Mathf.Round(hornAnswerChance * 100f) / 100f;
                list.GapLine();
            }

            if (Group(list, "Krayt den quest", RimMandrake.Shared.SettingScope.NextPulse, new[] { "denQuestEnabled" }))
            {
                list.CheckboxLabeled("Krayt den quest", ref denQuestEnabled,
                    "Tribes and a Jawa crew ask you to clear a greater krayt's den, when your map has one with the dragon still inside. Off: the quest is never offered.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_StillsandEventsMod : Mod
    {
        public static RM_StillsandEventsSettings settings;

        public RM_StillsandEventsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_StillsandEventsSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand: event creatures";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
