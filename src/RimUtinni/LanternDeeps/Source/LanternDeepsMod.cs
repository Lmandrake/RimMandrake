using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.LanternDeeps
{
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Lantern Deeps.
    //
    // The mod's runtime mechanisms are GenStep_ScatterCavePortal and
    // GenStep_ScatterMineshaftPortal, both WORLDGEN-AFFECTING steps (new maps
    // only): each scatters its own entrance onto a qualifying ≤ -40°C biome
    // at a flat per-map chance (LANTERN_DEEPS_INJECTION_1's own comment:
    // "FOUNDRY's placeholder pick pending the owner's actual density call").
    // Exposed here as a master toggle plus a multiplier per entrance type,
    // default 1x = shipped rate. MapComponent_LanternDeepDarkness (spec item
    // 6, the darkness mechanic) runs only inside an already-generated Deep,
    // so it gets its own toggle rather than sharing either entrance's.
    public class LanternDeepsSettings : ModSettings
    {
        public static bool emergenceEnabled = true;
        public static float emergenceChanceMultiplier = 1f;
        public static bool mineshaftEnabled = true;
        public static float mineshaftChanceMultiplier = 1f;
        public static bool darknessMechanicEnabled = true;
        public static float darknessThresholdMultiplier = 1f;

        // CAVERNS_PARITY_BUILD_1 — the two features the mod now OWNS rather than
        // borrows from Biomes! Caverns, each gated per the standing rule
        // (every mod ships real Mod Settings; defaults = shipped behavior;
        // all-off degrades gracefully).
        //
        // Both are WORLDGEN-AFFECTING in the same sense the entrance scatters
        // are: they are read while a Deep's pocket map is being generated, so a
        // change applies to the NEXT Deep entered, never to one already made.
        // The Deeps remain persistent maps (sheet hard ban 5) either way.
        //
        // All-off behaviour: a Deep with formations off and flora off is still a
        // complete, enterable, mineable cavern — gravel, lanternstone shelves,
        // lanternstone walls in extraRockTypes, the darkness mechanic, and both
        // the pyrinth and kyber scatters. It loses its crystal field and its
        // fungal pasture, not its floor.
        public static bool lanternstoneFormationsEnabled = true;
        public static float lanternstoneDensityMultiplier = 1f;
        public static bool deepFloraEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref emergenceEnabled, "emergenceEnabled", true);
            Scribe_Values.Look(ref emergenceChanceMultiplier, "emergenceChanceMultiplier", 1f);
            Scribe_Values.Look(ref mineshaftEnabled, "mineshaftEnabled", true);
            Scribe_Values.Look(ref mineshaftChanceMultiplier, "mineshaftChanceMultiplier", 1f);
            Scribe_Values.Look(ref darknessMechanicEnabled, "darknessMechanicEnabled", true);
            Scribe_Values.Look(ref darknessThresholdMultiplier, "darknessThresholdMultiplier", 1f);
            Scribe_Values.Look(ref lanternstoneFormationsEnabled, "lanternstoneFormationsEnabled", true);
            Scribe_Values.Look(ref lanternstoneDensityMultiplier, "lanternstoneDensityMultiplier", 1f);
            Scribe_Values.Look(ref deepFloraEnabled, "deepFloraEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Lantern Deep emergence (affects new maps only)");
            list.CheckboxLabeled("Natural cave-mouth portal can emerge", ref emergenceEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a lanternstone-geode mouth. "
              + "A map that already exists is never retroactively changed.");
            if (emergenceEnabled)
            {
                list.Label("Emergence chance: " + emergenceChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 8% of qualifying maps)");
                emergenceChanceMultiplier = list.Slider(emergenceChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Ruined mineshaft entrance (affects new maps only)");
            list.CheckboxLabeled("Ruined-mineshaft portal can appear", ref mineshaftEnabled,
                "Off: no new map on a qualifying deep-cold biome ever grows a ruined-mineshaft mouth. "
              + "A map that already exists is never retroactively changed.");
            if (mineshaftEnabled)
            {
                list.Label("Mineshaft chance: " + mineshaftChanceMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 4% of qualifying maps)");
                mineshaftChanceMultiplier = list.Slider(mineshaftChanceMultiplier, 0f, 3f);
            }

            list.Gap();
            list.Label("Darkness (inside an already-generated Deep)");
            list.CheckboxLabeled("Bright light draws cave predators", ref darknessMechanicEnabled,
                "Off: colonists inside a Lantern Deep can light the place up freely with no consequence. "
              + "On (default): sustained bright light near colonists eventually draws a resident predator "
              + "into a manhunter attack. Working in the dark, or moving on before light lingers, avoids it.");
            if (darknessMechanicEnabled)
            {
                list.Label("Trigger threshold: " + darknessThresholdMultiplier.ToString("0.00")
                    + "x the base sensitivity (higher = more light tolerated before something notices)");
                darknessThresholdMultiplier = list.Slider(darknessThresholdMultiplier, 0.25f, 4f);
            }

            list.Gap();
            list.Label("Inside a Lantern Deep (affects newly generated Deeps only)");
            list.CheckboxLabeled("Lanternstone formations grow in the Deeps", ref lanternstoneFormationsEnabled,
                "Off: a newly entered Deep has bare gravel and lanternstone shelves but no standing crystal "
              + "formations to mine, light the place, or go off when shot. The cavern is still complete and "
              + "still has its lanternstone walls.");
            if (lanternstoneFormationsEnabled)
            {
                list.Label("Lanternstone density: " + lanternstoneDensityMultiplier.ToString("0.00")
                    + "x the base rate (shipped default: 15-30 clusters per 10,000 cells)");
                lanternstoneDensityMultiplier = list.Slider(lanternstoneDensityMultiplier, 0f, 3f);
            }

            list.CheckboxLabeled("Cave flora grows in the Deeps", ref deepFloraEnabled,
                "Off: a newly entered Deep has no mycelium carpet, no mushroom trees and no glow-fungi — "
              + "no forageable food and no cloth or wood from below. Bare rock and crystal.");

            list.End();
        }
    }

    public class LanternDeepsMod : Mod
    {
        public static LanternDeepsSettings settings;

        public LanternDeepsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LanternDeepsSettings>();
        }

        public override string SettingsCategory() => "Lantern Deeps";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
