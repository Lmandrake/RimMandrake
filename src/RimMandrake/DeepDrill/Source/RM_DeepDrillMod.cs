using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.DeepDrill
{
    // Mod Settings. The deep-drill home-biome filter, and the world-tile resource mutators ported from VEE
    // (VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR). Scan-time settings apply to every later scan; map-generation ones to maps generated afterwards.
    public class RM_DeepDrillSettings : ModSettings
    {
        public static bool homeFilterEnabled = true;
        public static bool deepOreFactorsEnabled = true;   // RM_DeepOreRich / RM_DeepOreDevoid
        public static float richDeepOreFactor = 1.25f;     // PROVISIONAL (VEE's x1.25); range 1-2
        public static bool mineralDevoidEnabled = true;    // RM_MineralDevoid; affects map generation
        public static bool spacerDepositsEnabled = true;   // RM_MineableComponentSpacer; affects map generation
        public static float spacerDepositScale = 1f;       // PROVISIONAL; range 0-3

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref homeFilterEnabled, "homeFilterEnabled", true);
            Scribe_Values.Look(ref deepOreFactorsEnabled, "deepOreFactorsEnabled", true);
            Scribe_Values.Look(ref richDeepOreFactor, "richDeepOreFactor", 1.25f);
            Scribe_Values.Look(ref mineralDevoidEnabled, "mineralDevoidEnabled", true);
            Scribe_Values.Look(ref spacerDepositsEnabled, "spacerDepositsEnabled", true);
            Scribe_Values.Look(ref spacerDepositScale, "spacerDepositScale", 1f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        public static void Draw(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard();
            list.Begin(inRect);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            list.CheckboxLabeled("Deep deposits follow the biome", ref homeFilterEnabled,
                "On: a deep drill finds iron anywhere, and every other deep deposit only in its home biome. "
              + "Off: vanilla - any deposit anywhere. Applies to every later scan, on any map.");
            list.GapLine();
            list.Label("World-tile resources [applies now]");
            list.CheckboxLabeled("Deep-ore-rich and deep-ore-poor places", ref deepOreFactorsEnabled,
                "On: on a 'deep ore rich' tile every deposit a ground-penetrating scanner finds holds more; on a 'no deep ores' tile "
              + "the scanner finds nothing (drilling plain rock still works). Off: every tile is ordinary.");
            if (deepOreFactorsEnabled)
            {
                list.Label("Deep ore on rich tiles: x" + richDeepOreFactor.ToString("0.00"), tooltip: "Provisional; tuned live later.");
                richDeepOreFactor = Mathf.Round(list.Slider(richDeepOreFactor, 1f, 2f) * 20f) / 20f;
            }
            list.GapLine();
            list.Label("World-tile resources [WORLDGEN-AFFECTING: new maps only]");
            list.CheckboxLabeled("Mineral-devoid places have no ore veins", ref mineralDevoidEnabled,
                "On: on a 'mineral devoid' tile, ore veins in the rock are plain rock when the map is generated (compacted machinery stays). "
              + "Off: ordinary ore. Affects only maps generated afterwards.");
            list.CheckboxLabeled("Advanced component deposits", ref spacerDepositsEnabled,
                "On: an 'advanced component deposits' tile has lumps of advanced compacted machinery in its rock. "
              + "Off: none. Affects only maps generated afterwards.");
            if (spacerDepositsEnabled)
            {
                list.Label("Advanced component deposit amount: x" + spacerDepositScale.ToString("0.00"), tooltip: "Provisional; tuned live later.");
                spacerDepositScale = Mathf.Round(list.Slider(spacerDepositScale, 0f, 3f) * 20f) / 20f;
            }
            if (list.ButtonText("Reset to defaults"))
            {
                homeFilterEnabled = true;
                deepOreFactorsEnabled = true;
                richDeepOreFactor = 1.25f;
                mineralDevoidEnabled = true;
                spacerDepositsEnabled = true;
                spacerDepositScale = 1f;
            }
            list.End();
        }
    }

    public class RM_DeepDrillMod : Mod
    {
        public static RM_DeepDrillSettings settings;

        public RM_DeepDrillMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_DeepDrillSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.deepdrill"), typeof(RM_DeepDrillMod).Assembly, "RimMandrake.DeepDrill");
        }

        public override string SettingsCategory() { return "Deep Drill"; }

        public override void DoSettingsWindowContents(Rect inRect) { RM_DeepDrillSettings.Draw(inRect); }
    }
}
