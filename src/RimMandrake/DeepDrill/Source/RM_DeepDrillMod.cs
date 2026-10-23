using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.DeepDrill
{
    // Mod Settings. One feature: the deep-drill home-biome filter. Read at scan time, so a change applies to every later scan on any map.
    public class RM_DeepDrillSettings : ModSettings
    {
        public static bool homeFilterEnabled = true;

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref homeFilterEnabled, "homeFilterEnabled", true);
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
