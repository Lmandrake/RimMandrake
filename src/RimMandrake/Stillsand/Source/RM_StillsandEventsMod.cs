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

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 800f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);
            list.Label("Event creatures: the leviathans that come up out of the sand on a Stillsand map. "
                       + "Each comes as an incident, warns first (a letter and a growing rumble), and "
                       + "leaves a funnel or a drag mark for everything it takes.");
            list.GapLine();

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

            list.GapLine();
            list.CheckboxLabeled("Muurrok mirror beam", ref mirrorBeamEnabled,
                "The muurrok reflects the sun off its crest as a sweeping heat beam (never fire). "
                + "It needs sun: none at night, under a roof, or in a sand gale. Off: it only strikes from under.");
            list.GapLine();
            list.CheckboxLabeled("Krayt horn", ref hornEnabled,
                "A horn that can be blown to rout smaller predators and tribal raiders nearby. Off: it cannot be used.");
            hornAnswerChance = list.SliderLabeled("Chance the call is answered: " + (hornAnswerChance * 100f).ToString("0") + "%",
                hornAnswerChance, 0f, 1f,
                tooltip: "Every blow rolls this; on a hit the krayt attack is queued a few hours out. 0 means never.");
            hornAnswerChance = Mathf.Round(hornAnswerChance * 100f) / 100f;
            list.CheckboxLabeled("Krayt den quest", ref denQuestEnabled,
                "Tribes and a Jawa crew ask you to clear a greater krayt's den, when your map has one with the dragon still inside. Off: the quest is never offered.");
            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
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
