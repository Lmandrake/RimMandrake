using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // SCARLANDS_STANDALONE_MOD_1 — Mod Settings for Warscar.
    //
    // This biome ships no bespoke mechanic of its own: its two duplicated
    // flora defs (RM_Glower/RM_ScorchedStars) are plain harvestable plants
    // with no comp yet (the frozen twin's own radiation-dose harvest loop is
    // still owed to SCARLANDS_MECHANICS_2), and the frozen twin's own
    // scaria-mark/pre-sprung-dressing mechanics deliberately did NOT move
    // into this mod (this item's own `## spec`: "don't invent extra scope").
    // So this screen ships only the standard worldgen-rarity slider every
    // biome-worker mod ships, plus the honestly-disclosed reserved
    // cross-biome section (MOD_OPTIONS_RETROFIT_1 doctrine), same shape as
    // RM_Miasma/RM_RustCathedral's own screens.
    //
    // STATIC FIELD, read from worldgen with no Mod instance handy.
    // ════════════════════════════════════════════════════════════════════
    public class RM_WarscarSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new planet.
        public static float biomeRarityFactor = 1f;

        // MOD_OPTIONS_RETROFIT_1: reserved fields for letting this biome's
        // (currently nonexistent) mechanics run on other biomes too.
        // Persisted and exposed here honestly as NOT YET WIRED to any
        // mechanic — there is no mechanic in this mod for it to gate yet.
        // WARSCAR_TURRETS_TRACK_1 toggles.
        public static bool turretTrackingEnabled = true;   // broken turrets' barrels follow movers
        public static bool turretRefitEnabled = true;      // wreck -> RM_OldLineTurret gizmo
        public static float oldLineDamageFactor = 1f;      // applied at game start
        public static float oldLineCooldownFactor = 1f;    // applied at game start

        // WARSCAR_TOTCHAK_WAKES_1 toggles.
        public static bool totchakEnabled = true;           // totchak spawns dormant in walls and wakes
        public static bool totchakEatsPlayerWalls = true;   // ruled default on
        public static float totchakWakeRadius = 12f;        // demolition wake radius (cells)
        public static float totchakBiteScale = 1f;          // wall-eating damage scale
        public static float totchakGrazeDays = 8f;          // awake days before it lies down again

        public static bool crossBiomeEnabled = false;
        public static bool crossBiomeEverywhere = false;
        public static string crossBiomeBiomeList = "";
        public static float crossBiomeCoverage = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref turretTrackingEnabled, "turretTrackingEnabled", true);
            Scribe_Values.Look(ref turretRefitEnabled, "turretRefitEnabled", true);
            Scribe_Values.Look(ref oldLineDamageFactor, "oldLineDamageFactor", 1f);
            Scribe_Values.Look(ref oldLineCooldownFactor, "oldLineCooldownFactor", 1f);
            Scribe_Values.Look(ref totchakEnabled, "totchakEnabled", true);
            Scribe_Values.Look(ref totchakEatsPlayerWalls, "totchakEatsPlayerWalls", true);
            Scribe_Values.Look(ref totchakWakeRadius, "totchakWakeRadius", 12f);
            Scribe_Values.Look(ref totchakBiteScale, "totchakBiteScale", 1f);
            Scribe_Values.Look(ref totchakGrazeDays, "totchakGrazeDays", 8f);
            Scribe_Values.Look(ref crossBiomeEnabled, "crossBiomeEnabled", false);
            Scribe_Values.Look(ref crossBiomeEverywhere, "crossBiomeEverywhere", false);
            Scribe_Values.Look(ref crossBiomeBiomeList, "crossBiomeBiomeList", "");
            Scribe_Values.Look(ref crossBiomeCoverage, "crossBiomeCoverage", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 Warscar never generates on a new planet. Affects planets "
                       + "generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.CheckboxLabeled("Broken turrets track movement", ref turretTrackingEnabled,
                "The barrel of a broken ancient turret turns to follow the nearest moving pawn. It never fires.");
            list.CheckboxLabeled("Allow refitting broken turrets", ref turretRefitEnabled,
                "Adds a Refit button to broken turrets that converts them into an old-line turret.");
            list.Label("Old-line turret damage: x" + oldLineDamageFactor.ToString("0.00") + " (applies after restart)");
            oldLineDamageFactor = list.Slider(oldLineDamageFactor, 0.25f, 3f);
            list.Label("Old-line turret cooldown: x" + oldLineCooldownFactor.ToString("0.00") + " (applies after restart)");
            oldLineCooldownFactor = list.Slider(oldLineCooldownFactor, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Totchak (wall colossus)", ref totchakEnabled,
                "A totchak sleeps in a run of ruin wall, wakes to demolition, eats walls, and lies down again. Affects new maps.");
            list.CheckboxLabeled("Totchak eats player walls", ref totchakEatsPlayerWalls,
                "When no ruin wall is in reach, a woken totchak eats your walls.");
            list.Label("Totchak wake radius: " + totchakWakeRadius.ToString("0") + " cells");
            totchakWakeRadius = list.Slider(totchakWakeRadius, 4f, 30f);
            list.Label("Totchak wall-eating damage: x" + totchakBiteScale.ToString("0.00"));
            totchakBiteScale = list.Slider(totchakBiteScale, 0.25f, 4f);
            list.Label("Totchak grazing days before it lies down: " + totchakGrazeDays.ToString("0.0"));
            totchakGrazeDays = list.Slider(totchakGrazeDays, 1f, 30f);
            list.GapLine();

            list.Label("Cross-biome (reserved — not yet wired to any mechanic in this build)");
            bool crossBiomeEnabledLocal = crossBiomeEnabled;
            list.CheckboxLabeled("Allow this mod's mechanics on other biomes", ref crossBiomeEnabledLocal,
                "Reserved for a future pass. No mechanic in this mod currently reads this switch.");
            crossBiomeEnabled = crossBiomeEnabledLocal;

            list.End();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_WarscarMod : Mod
    {
        public static RM_WarscarSettings settings;

        public RM_WarscarMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_WarscarSettings>();
        }

        public override string SettingsCategory()
        {
            return "Warscar";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
