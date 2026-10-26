using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.TileFeatures
{
    // Mod Settings for the world-tile features ported from VEE (VEE_FLORA_VENTS_BUILD_XML_FIRST). Each group switch makes
    // its tile features inert (RM_TileFeatureApplier); poisonous flora, infestations and the rotten stench also check the
    // switch while they run, so on an existing map they stop at once. Everything else applies to maps generated afterwards.
    public class RM_TileFeaturesSettings : ModSettings
    {
        public static bool floraEnabled = true;        // the 13 flora/terrain/ship-chunk features
        public static bool weatherEnabled = true;      // sandstorms, dust storms, rotten stench
        public static bool ventsEnabled = true;        // toxic, rotstink and smoke vents
        public static bool diseasesEnabled = true;     // RM_IncreasedDiseases
        public static bool infestationsEnabled = true; // RM_IncreasedInfestations

        public static float diseaseMtbMultiplier = 0.75f;    // VEE's value; lower = diseases come sooner. Range 0.25-1
        public static float infestationFactor = 1.5f;        // PROVISIONAL; range 1-3
        public static float ventCountScale = 1f;             // PROVISIONAL; range 0-3, scales VEE's 6~12 vents per map
        public static float poisonSeverityPerHarvest = 0.05f; // PROVISIONAL; toxic buildup per wild plant harvested, range 0-0.2

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref floraEnabled, "floraEnabled", true);
            Scribe_Values.Look(ref weatherEnabled, "weatherEnabled", true);
            Scribe_Values.Look(ref ventsEnabled, "ventsEnabled", true);
            Scribe_Values.Look(ref diseasesEnabled, "diseasesEnabled", true);
            Scribe_Values.Look(ref infestationsEnabled, "infestationsEnabled", true);
            Scribe_Values.Look(ref diseaseMtbMultiplier, "diseaseMtbMultiplier", 0.75f);
            Scribe_Values.Look(ref infestationFactor, "infestationFactor", 1.5f);
            Scribe_Values.Look(ref ventCountScale, "ventCountScale", 1f);
            Scribe_Values.Look(ref poisonSeverityPerHarvest, "poisonSeverityPerHarvest", 0.05f);
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        private static float Slider(Listing_Standard list, string label, float value, float min, float max, string tip)
        {
            list.Label(label + value.ToString("0.00"), tooltip: tip);
            return Mathf.Round(list.Slider(value, min, max) * 100f) / 100f;
        }

        public static void Draw(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard();
            list.Begin(inRect);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);
            list.Label("[WORLDGEN-AFFECTING: new maps only] These features act on tiles that already carry them; this mod never places them on the world.");
            list.GapLine();
            list.CheckboxLabeled("Flora and terrain features", ref floraEnabled,
                "Wild cacti, red desert cacti, light-resistant mushrooms, overgrown and decimated plant life, no trees, poisonous flora, "
              + "reduced soil fertility, marine sanctuaries and crashed mechanoid ship chunks. Off: plain maps. "
              + "Poisonous flora stops at once; the rest applies to maps generated afterwards.");
            if (floraEnabled)
                poisonSeverityPerHarvest = Slider(list, "Toxic buildup per wild plant harvested on poisonous-flora tiles: ",
                    poisonSeverityPerHarvest, 0f, 0.2f, "Provisional; tuned live later. Reduced by toxic resistance.");
            list.GapLine();
            list.CheckboxLabeled("Weather features", ref weatherEnabled,
                "Sandstorms, dust storms and a permanent rotten stench. Off: the stench stops at once; storm frequency returns to the "
              + "biome's own on maps generated afterwards.");
            list.GapLine();
            list.CheckboxLabeled("Gas vents", ref ventsEnabled,
                "Toxic, rotstink and smoke vents that release gas on a cycle. Off: none on maps generated afterwards.");
            if (ventsEnabled)
                ventCountScale = Slider(list, "Vent count: x", ventCountScale, 0f, 3f, "Provisional; tuned live later.");
            list.GapLine();
            list.CheckboxLabeled("More diseases", ref diseasesEnabled, "Off: diseases come at the ordinary rate on 'increased diseases' tiles.");
            if (diseasesEnabled)
                diseaseMtbMultiplier = Slider(list, "Time between diseases: x", diseaseMtbMultiplier, 0.25f, 1f,
                    "Lower means diseases come sooner. Vanilla Exploration Expanded used 0.75.");
            list.CheckboxLabeled("More infestations", ref infestationsEnabled,
                "Off: infestations come at the ordinary rate on 'increased infestations' tiles. Applies at once.");
            if (infestationsEnabled)
                infestationFactor = Slider(list, "Infestation chance: x", infestationFactor, 1f, 3f, "Provisional; tuned live later.");
            list.GapLine();
            if (list.ButtonText("Reset to defaults"))
            {
                floraEnabled = weatherEnabled = ventsEnabled = diseasesEnabled = infestationsEnabled = true;
                diseaseMtbMultiplier = 0.75f;
                infestationFactor = 1.5f;
                ventCountScale = 1f;
                poisonSeverityPerHarvest = 0.05f;
            }
            list.End();
        }
    }

    public class RM_TileFeaturesMod : Mod
    {
        public static RM_TileFeaturesSettings settings;

        public RM_TileFeaturesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_TileFeaturesSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.tilefeatures"), typeof(RM_TileFeaturesMod).Assembly, "RimMandrake.TileFeatures");
        }

        public override string SettingsCategory() { return "Tile Features"; }

        public override void DoSettingsWindowContents(Rect inRect) { RM_TileFeaturesSettings.Draw(inRect); }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_TileFeatureApplier.Apply();
        }
    }
}
