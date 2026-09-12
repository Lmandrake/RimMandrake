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

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Each incident below can be turned off without affecting the others.");
            list.GapLine();

            list.CheckboxLabeled("Wildlife migration", ref migrationEnabled,
                "A small herd of biome-correct animals passes through the map.");
            list.CheckboxLabeled("Survival pod gift", ref survivalPodEnabled,
                "A drop pod with a survival outfit, meals, and a pistol.");
            list.CheckboxLabeled("Tribal pod crash (rescue)", ref podCrashTribalEnabled,
                "A downed pawn from a friendly faction, dropped in a pod.");

            list.Gap();
            list.CheckboxLabeled("Insect swarm", ref insectEnabled,
                "Hostile Spelopedes and Megaspiders in permanent manhunter state.");
            list.Label("Swarm size: " + insectSwarmSizeMultiplier.ToString("0.00") + "x the normal count");
            insectSwarmSizeMultiplier = list.Slider(insectSwarmSizeMultiplier, 0.5f, 2f);

            list.Gap();
            list.CheckboxLabeled("Colonist stroke", ref strokeEnabled,
                "A random colonist collapses, downed, with a mood hit.");

            list.Gap();
            list.CheckboxLabeled("Ship break (cargo rain)", ref shipBreakEnabled,
                "Loot drop plus a downed survivor and a corpse, each in their own pod.");
            list.Label("Ship break loot: " + shipBreakLootMultiplier.ToString("0.00") + "x the normal value");
            shipBreakLootMultiplier = list.Slider(shipBreakLootMultiplier, 0.5f, 2f);

            list.Gap();
            list.CheckboxLabeled("Emergency food relief (\"Thanksgiving\")", ref thanksgivingEnabled,
                "Free meals dropped when the colony is close to running out of food.");
            list.Label("Fires when food is below " + thanksgivingThresholdMultiplier.ToString("0.00") + "x the normal hunger threshold");
            thanksgivingThresholdMultiplier = list.Slider(thanksgivingThresholdMultiplier, 0.5f, 2f);

            list.End();
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
