using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine: on/off per major
    // mechanic, tuning where a number is the experience, defaults = shipped
    // behavior. Follows the sibling Gelatinous Slime mod's exact pattern
    // (SlimeMod.cs): STATIC FIELDS, read from everywhere (the biome worker
    // runs during worldgen with no Mod instance handy; the map component
    // reads settings every flood-cycle check), written only through the
    // settings window and ExposeData.
    // ════════════════════════════════════════════════════════════════════
    public class RM_FloodedCanyonSettings : ModSettings
    {
        // Worldgen insertion. 0 = the biome never generates on a new
        // planet. 1 = the shipped default (rare patches, same "1-3 per
        // planet" order of magnitude as Gelatinous Slime's own slider).
        public static float biomeRarityFactor = 1f;

        // "canyon biome insertion vs feature-only in other biomes" — the
        // item's own spec line. When true, the flood cycle + chime + growth
        // coupling run on EVERY map's biome, not only RM_FloodedCanyon, so a
        // player can have the mechanic without the biome (mirrors the
        // Greentide standalone mod's per-feature cross-biome toggle).
        public static bool featureInOtherBiomes = false;

        // Master switch for the whole flood cycle (chime + wall + soil).
        public static bool floodCycleEnabled = true;

        // Average days between floods on a given map.
        public static float floodPeriodDays = 20f;

        // Warning lead time before the wall arrives, once the chime rings.
        public static float chimeLeadTimeHours = 2f;

        // How long the wall stands before it recedes to soil.
        public static float floodDurationHours = 6f;

        // Whether the wall of water can lightly hurt a pawn caught in it.
        // Capped low by design — a startle, never a killer (this mod never
        // promises the campaign's own injury-ceiling ruling; it ships its
        // own conservative default because nothing here should feel unfair
        // in a mod a player added for the biome, not the danger).
        public static bool floodDamageEnabled = true;

        // Soak-driven growth coupling: freshly-flooded ground carries a
        // temporary GrowthRate multiplier that decays back to normal.
        public static bool growthCouplingEnabled = true;
        public static float growthMultiplier = 6f;
        public static float soakDecayDays = 4f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref biomeRarityFactor, "biomeRarityFactor", 1f, true);
            Scribe_Values.Look(ref featureInOtherBiomes, "featureInOtherBiomes", false, true);
            Scribe_Values.Look(ref floodCycleEnabled, "floodCycleEnabled", true, true);
            Scribe_Values.Look(ref floodPeriodDays, "floodPeriodDays", 20f, true);
            Scribe_Values.Look(ref chimeLeadTimeHours, "chimeLeadTimeHours", 2f, true);
            Scribe_Values.Look(ref floodDurationHours, "floodDurationHours", 6f, true);
            Scribe_Values.Look(ref floodDamageEnabled, "floodDamageEnabled", true, true);
            Scribe_Values.Look(ref growthCouplingEnabled, "growthCouplingEnabled", true, true);
            Scribe_Values.Look(ref growthMultiplier, "growthMultiplier", 6f, true);
            Scribe_Values.Look(ref soakDecayDays, "soakDecayDays", 4f, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Biome rarity: " + RarityLabel());
            list.Label("At 0 the flooded canyon never generates on a new planet. "
                       + "The default places a handful of rare canyon patches. Affects "
                       + "planets generated afterwards, never one that already exists.");
            biomeRarityFactor = list.Slider(biomeRarityFactor, 0f, 8f);
            list.GapLine();

            list.CheckboxLabeled("Flood cycle enabled", ref floodCycleEnabled,
                "The chime warning, the wall of water, and the soil it leaves behind. "
                + "Off means the biome stays permanently dry.");
            list.CheckboxLabeled("Run the flood cycle in other biomes too", ref featureInOtherBiomes,
                "Applies the flood cycle to EVERY map's biome, not only the flooded "
                + "canyon — the mechanic without the biome.");

            list.Label("Days between floods: " + floodPeriodDays.ToString("0"));
            floodPeriodDays = list.Slider(floodPeriodDays, 6f, 60f);

            list.Label("Chime warning lead time: " + chimeLeadTimeHours.ToString("0.0") + " h");
            chimeLeadTimeHours = list.Slider(chimeLeadTimeHours, 0.5f, 6f);

            list.Label("Flood duration: " + floodDurationHours.ToString("0.0") + " h");
            floodDurationHours = list.Slider(floodDurationHours, 1f, 24f);

            list.CheckboxLabeled("The wall of water can hurt a caught pawn", ref floodDamageEnabled,
                "A single light, non-fatal hit when the wall first reaches a pawn's cell. "
                + "Never applied after that — standing water is just slow, not dangerous.");
            list.GapLine();

            list.CheckboxLabeled("Soak-driven growth coupling", ref growthCouplingEnabled,
                "Freshly-flooded ground grows plants faster for a few days, then decays "
                + "back to normal. A light coupling, not the full explosive-growth engine.");
            list.Label("Growth multiplier on soaked ground: " + growthMultiplier.ToString("0.0") + "x");
            growthMultiplier = list.Slider(growthMultiplier, 1f, 20f);
            list.Label("Soak decays over: " + soakDecayDays.ToString("0.0") + " days");
            soakDecayDays = list.Slider(soakDecayDays, 1f, 10f);

            list.End();
        }

        private static string RarityLabel()
        {
            if (biomeRarityFactor <= 0.001f) return "never generates";
            if (biomeRarityFactor < 0.6f) return "very rare (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 1.6f) return "default, a handful of patches (" + biomeRarityFactor.ToString("0.0") + "x)";
            if (biomeRarityFactor < 4f) return "uncommon (" + biomeRarityFactor.ToString("0.0") + "x)";
            return "common (" + biomeRarityFactor.ToString("0.0") + "x)";
        }
    }

    public class RM_FloodedCanyonMod : Mod
    {
        public static RM_FloodedCanyonSettings settings;

        public RM_FloodedCanyonMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_FloodedCanyonSettings>();
        }

        public override string SettingsCategory()
        {
            return "Flooded Canyon";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
