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
            Scribe_Collections.Look(ref disabled, "leviathanDisabled", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref odds, "leviathanOdds", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                disabled = disabled ?? new Dictionary<string, bool>();
                odds = odds ?? new Dictionary<string, float>();
            }
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
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
            list.End();
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
