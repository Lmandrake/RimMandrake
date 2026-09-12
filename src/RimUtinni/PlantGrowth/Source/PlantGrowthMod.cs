// MOD_OPTIONS_RETROFIT_1 — Mod Settings for Jawa Plant Growth.
//
// House style: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs (static fields
// read from everywhere, Scribe_Values in ExposeData, DoWindowContents helper
// called from the Mod subclass).
//
// PRECEDENCE CHANGE, DOCUMENTED HERE AND IN PlantGrowthConfig.Rebuild(): before
// this pass, the four numeric bands (defaultMultiplier, treeMultiplier,
// terminatorMultiplier, minGrowDaysToBoost) were read from
// Defs/JawaPlantGrowthSettings.xml. They are now owned by THIS in-game Mod
// Settings screen instead — the XML def's own numeric fields are kept only for
// anyone hand-editing the file for reference, but Rebuild() no longer reads
// them. The terminator biome roster and exempt-plant list stay XML-configured
// (a list has no sensible slider). Every default below matches the shipped
// def's numbers exactly, so this changes nothing about day-one behavior.
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.PlantGrowth
{
    public class PlantGrowthSettings : ModSettings
    {
        // Master switch. Off: Patch_Plant_GrowthRate's postfix no-ops and every
        // plant grows at vanilla speed.
        public static bool growthEnabled = true;

        public static float defaultMultiplier = PlantGrowthConfig.DEFAULT_MULTIPLIER;
        public static float treeMultiplier = PlantGrowthConfig.TREE_MULTIPLIER;
        public static float terminatorMultiplier = PlantGrowthConfig.TERMINATOR_MULTIPLIER;
        public static float minGrowDaysToBoost = PlantGrowthConfig.MIN_GROW_DAYS_TO_BOOST;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref growthEnabled, "growthEnabled", true);
            Scribe_Values.Look(ref defaultMultiplier, "defaultMultiplier", PlantGrowthConfig.DEFAULT_MULTIPLIER);
            Scribe_Values.Look(ref treeMultiplier, "treeMultiplier", PlantGrowthConfig.TREE_MULTIPLIER);
            Scribe_Values.Look(ref terminatorMultiplier, "terminatorMultiplier", PlantGrowthConfig.TERMINATOR_MULTIPLIER);
            Scribe_Values.Look(ref minGrowDaysToBoost, "minGrowDaysToBoost", PlantGrowthConfig.MIN_GROW_DAYS_TO_BOOST);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Planetary fast growth enabled", ref growthEnabled,
                "Off: every plant grows at vanilla speed, everywhere. On by default.");
            list.GapLine();

            list.Label("Wild plants & crops: " + defaultMultiplier.ToString("0.0") + "x growth");
            defaultMultiplier = list.Slider(defaultMultiplier, 1f, 8f);
            list.Gap();

            list.Label("Trees: " + treeMultiplier.ToString("0.0") + "x growth");
            list.Label("Kept lower than crops on purpose — wood stays a decision.");
            treeMultiplier = list.Slider(treeMultiplier, 1f, 8f);
            list.Gap();

            list.Label("Terminator / poison-forest biomes: " + terminatorMultiplier.ToString("0.00") + "x growth");
            list.Label("The one place on this world where growth has stalled — kept below "
              + "1.0x by default. This is the multiplier, not a bonus: 1.0 means vanilla "
              + "speed in that biome, not vanilla plus a bonus.");
            terminatorMultiplier = list.Slider(terminatorMultiplier, 0.1f, 2f);
            list.GapLine();

            list.Label("Skip plants already faster than: " + minGrowDaysToBoost.ToString("0.0") + " grow-days");
            list.Label("A plant already this fast gains nothing from multiplying and can "
              + "produce silly per-tick values, so it is left untouched. Takes effect on "
              + "the next game load (it changes which plants are classified as exempt).");
            minGrowDaysToBoost = list.Slider(minGrowDaysToBoost, 0.1f, 5f);

            list.End();
        }
    }

    public class PlantGrowthMod : Mod
    {
        public static PlantGrowthSettings settings;

        public PlantGrowthMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<PlantGrowthSettings>();
        }

        public override string SettingsCategory()
        {
            return "Jawa Plant Growth";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        // Re-runs the classification pass so the sliders take effect immediately
        // rather than only after a restart, same as the def-driven path already
        // did (Rebuild() has always been safe to call more than once).
        public override void WriteSettings()
        {
            base.WriteSettings();
            PlantGrowthConfig.Rebuild();
        }
    }
}
