using UnityEngine;
using Verse;

namespace RimMandrake.HugeThings
{
    // MOD_OPTIONS_RETROFIT_1 contract: one toggle per mechanic, tuning where a number is the experience,
    // defaults = shipped behaviour, all-off = vanilla.
    public class RM_HugeThingsSettings : ModSettings
    {
        public const float MaxTrunkScale = 1.5f;

        public static bool plantTrunkEnabled = true;
        public static bool plantSelectionEnabled = true;
        public static float plantTrunkScale = 1f;
        public static bool pawnHitboxEnabled = true;
        public static float pawnHitboxScale = 1f;

        /// <summary>Changes whenever a plant setting does (slider drags included), so caches can key on it.</summary>
        public static int Stamp() => (plantSelectionEnabled ? 1 : 0) | (plantTrunkEnabled ? 2 : 0)
                                 | (Mathf.RoundToInt(plantTrunkScale * 1000f) << 2);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref plantTrunkEnabled, "plantTrunkEnabled", true);
            Scribe_Values.Look(ref plantSelectionEnabled, "plantSelectionEnabled", true);
            Scribe_Values.Look(ref plantTrunkScale, "plantTrunkScale", 1f);
            Scribe_Values.Look(ref pawnHitboxEnabled, "pawnHitboxEnabled", true);
            Scribe_Values.Look(ref pawnHitboxScale, "pawnHitboxScale", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { maxOneColumn = true };
            list.Begin(inRect);
            list.CheckboxLabeled("Huge plants are solid where they touch the ground", ref plantTrunkEnabled,
                "A huge plant blocks the cells where its stem, roots or body meet the ground (measured from its art), "
              + "so pawns walk around it and nothing can be built inside it; its overhanging cap stays walkable. "
              + "Off: every plant is one walk-through cell, as in vanilla.");
            list.CheckboxLabeled("Click anywhere on a huge plant's picture to select it", ref plantSelectionEnabled,
                "Off: a huge plant can only be selected on the one cell it grows from.");
            list.Label("  Ground footprint size: " + plantTrunkScale.ToString("0.00") + "x");
            plantTrunkScale = list.Slider(plantTrunkScale, 0.5f, MaxTrunkScale);
            list.GapLine();
            list.CheckboxLabeled("Click anywhere on a huge animal to select it", ref pawnHitboxEnabled,
                "A huge creature can be selected by clicking anywhere on its drawn body. Off: only near its middle.");
            list.Label("  Hitbox size: " + pawnHitboxScale.ToString("0.00") + "x");
            pawnHitboxScale = list.Slider(pawnHitboxScale, 0.5f, MaxTrunkScale);
            list.End();
        }
    }

    public class RM_HugeThingsMod : Mod
    {
        public static RM_HugeThingsSettings settings;

        public RM_HugeThingsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_HugeThingsSettings>();
        }

        public override string SettingsCategory() => "Huge Things";

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);

        public override void WriteSettings()
        {
            base.WriteSettings();
            MapComponent_HugeFootprints.RefreshAllMaps();
        }
    }
}
