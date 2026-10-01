using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SKELETONS_TRACKS_1 §9 — Mod Settings for the skeletons and
    // the horizon. Its own Mod class (as RM_StillsandEventsMod), so the
    // biome's settings file stays out of this item's diff. Defaults are the
    // shipped behaviour; all off leaves the biome whole (no skeletons are
    // placed, corpses stay corpses, raids arrive unannounced as in vanilla).
    //
    // Track persistence is NOT here: the tracks ride FOOTPRINT_TRACK_GRID_1,
    // whose own settings carry the on/off switch (it is not built yet).
    // ════════════════════════════════════════════════════════════════════
    public class RM_SkeletonSettings : ModSettings
    {
        public static bool skeletonPlacementEnabled = true;
        public static int maxSkeletonsPerMap = 2;
        public static bool corpseToSkeletonEnabled = true;
        public static float corpseToSkeletonDays = 15f;
        public static bool boneHarpEnabled = true;
        public static bool horizonWarningsEnabled = true;
        public static float horizonWarningHours = 3f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref skeletonPlacementEnabled, "skeletonPlacementEnabled", true);
            Scribe_Values.Look(ref maxSkeletonsPerMap, "maxSkeletonsPerMap", 2);
            Scribe_Values.Look(ref corpseToSkeletonEnabled, "corpseToSkeletonEnabled", true);
            Scribe_Values.Look(ref corpseToSkeletonDays, "corpseToSkeletonDays", 15f);
            Scribe_Values.Look(ref boneHarpEnabled, "boneHarpEnabled", true);
            Scribe_Values.Look(ref horizonWarningsEnabled, "horizonWarningsEnabled", true);
            Scribe_Values.Look(ref horizonWarningHours, "horizonWarningHours", 3f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);
            list.Label("The giants' bones, and the empty horizon.");
            list.GapLine();

            list.CheckboxLabeled("Giant skeletons on new maps (map generation)", ref skeletonPlacementEnabled,
                "Each new Stillsand map carries a few giant skeletons: ribs that throw striped shade, a skull "
                + "you can shelter in, often an ollim growing among them. Affects map generation only.");
            if (skeletonPlacementEnabled)
            {
                list.Label("Most skeletons per map: " + maxSkeletonsPerMap);
                maxSkeletonsPerMap = (int)list.Slider(maxSkeletonsPerMap, 0, 2);
            }
            list.Gap(6f);

            list.CheckboxLabeled("Giant corpses become skeletons", ref corpseToSkeletonEnabled,
                "A giant that dies on the open sand dries out and, after a while, stands where it fell as "
                + "its skeleton. Off: its corpse stays a corpse.");
            if (corpseToSkeletonEnabled)
            {
                list.Label("Days until a corpse is a skeleton: " + corpseToSkeletonDays.ToString("0"));
                corpseToSkeletonDays = Mathf.Round(list.Slider(corpseToSkeletonDays, 1f, 60f));
            }
            list.Gap(6f);

            list.CheckboxLabeled("Bone harps", ref boneHarpEnabled,
                "Wind across a skeleton's ribs makes a low moan that rises with the wind, so you can find "
                + "one by ear. Off: skeletons are silent.");
            list.Gap(6f);

            list.CheckboxLabeled("Dust on the horizon", ref horizonWarningsEnabled,
                "On open sand nothing hides: raids and caravans are seen hours before they arrive, as a dust "
                + "plume at the map edge and a letter giving the bearing. Off: they arrive as in vanilla.");
            if (horizonWarningsEnabled)
            {
                list.Label("Hours of warning: " + horizonWarningHours.ToString("0.0"));
                horizonWarningHours = Mathf.Round(list.Slider(horizonWarningHours, 0.5f, 8f) * 2f) / 2f;
            }
            list.End();
        }
    }

    public class RM_SkeletonMod : Mod
    {
        public static RM_SkeletonSettings settings;

        public RM_SkeletonMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_SkeletonSettings>();
        }

        public override string SettingsCategory()
        {
            return "Stillsand: skeletons and horizon";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
