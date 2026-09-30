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

        // Soak coupling: the flood hands every cell it wets to RimMandrake:
        // Explosive Plant Growth as SOAKED for the flood's duration plus
        // soakDecayDays. That mod owns the growth multiplier (its own
        // setting) and everything after; without it this does nothing.
        public static bool growthCouplingEnabled = true;
        public static float soakDecayDays = 4f;

        // CRACKEDLANDS_MECHANICS_BUILD_1 §3 — fossils in the walls.
        // WORLDGEN-AFFECTING: the seeding runs once, when a map is generated,
        // so these three only change maps generated afterwards.
        public static bool fossilSeamsEnabled = true;
        public static bool fossilSeamsInOtherBiomes = false;
        public static float fossilSeamDensity = 1f;

        // §3 — the flood re-cuts the ledger: fresh seams along the wetted
        // wall line at every recede. Runs wherever the flood cycle runs.
        public static bool floodRecutSeamsEnabled = true;
        public static int floodRecutSeamCount = 4;

        // §4 — the muttavaq: the flood wakes it (water reaching its pan), and
        // at the dry it digs in and seals where it stands. Off = the stock
        // behaviour the content def ships alone (sleeps until damaged).
        public static bool muttavaqWaterWakeEnabled = true;
        public static bool muttavaqDigInEnabled = true;

        // §5 — Peakstorm Light pulls the next flood forward (the chime
        // follows the storm on the peaks). The weather itself is a biome
        // weather commonality, not a setting.
        public static bool peakstormBiasEnabled = true;

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
            Scribe_Values.Look(ref soakDecayDays, "soakDecayDays", 4f, true);
            Scribe_Values.Look(ref fossilSeamsEnabled, "fossilSeamsEnabled", true, true);
            Scribe_Values.Look(ref fossilSeamsInOtherBiomes, "fossilSeamsInOtherBiomes", false, true);
            Scribe_Values.Look(ref fossilSeamDensity, "fossilSeamDensity", 1f, true);
            Scribe_Values.Look(ref floodRecutSeamsEnabled, "floodRecutSeamsEnabled", true, true);
            Scribe_Values.Look(ref floodRecutSeamCount, "floodRecutSeamCount", 4, true);
            Scribe_Values.Look(ref muttavaqWaterWakeEnabled, "muttavaqWaterWakeEnabled", true, true);
            Scribe_Values.Look(ref muttavaqDigInEnabled, "muttavaqDigInEnabled", true, true);
            Scribe_Values.Look(ref peakstormBiasEnabled, "peakstormBiasEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls: the CRACKEDLANDS_MECHANICS_BUILD_1 toggles pushed the
            // page past a settings window's height. viewHeight is measured
            // from the previous frame's listing (CurHeight), so it self-fits.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPosition, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

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

            list.CheckboxLabeled("Floods follow the peakstorm light", ref peakstormBiasEnabled,
                "When the far skyline flickers with a storm on the peaks, the next flood "
                + "may come sooner — within a day or so. The chime still rings first. "
                + "Never within half a flood period of the last one.");

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

            list.CheckboxLabeled("The flood soaks the ground it wets", ref growthCouplingEnabled,
                "Hands the flooded cells to RimMandrake: Explosive Plant Growth as soaked "
                + "ground — its plants swell, charge and reach their top. Needs that mod; "
                + "without it this does nothing. The growth multiplier is that mod's setting.");
            list.Label("Ground stays soaked for: " + soakDecayDays.ToString("0.0") + " days after the water recedes");
            soakDecayDays = list.Slider(soakDecayDays, 1f, 10f);
            list.GapLine();

            list.CheckboxLabeled("Fossil seams in the canyon walls (worldgen)", ref fossilSeamsEnabled,
                "Seeds fossil-bearing strata into the rock wall faces of newly generated "
                + "Cracked Lands maps — common impressions low on the faces, rarer "
                + "articulated seams, deep-stratum seams only well inside the walls. "
                + "Affects maps generated afterwards, never an existing one.");
            list.CheckboxLabeled("Fossil seams in other biomes too (worldgen)", ref fossilSeamsInOtherBiomes,
                "Seeds the same strata into the walls of every newly generated map, "
                + "not only the Cracked Lands.");
            list.Label("Fossil seam density: " + fossilSeamDensity.ToString("0.0") + "x");
            fossilSeamDensity = list.Slider(fossilSeamDensity, 0f, 4f);
            list.CheckboxLabeled("The flood cuts fresh fossil seams", ref floodRecutSeamsEnabled,
                "When the water recedes, a few rock wall cells along the wetted line "
                + "turn into freshly exposed fossil seams — walls near the water line "
                + "are worth walking after every flood.");
            list.Label("Fresh seams per flood: " + floodRecutSeamCount);
            floodRecutSeamCount = Mathf.RoundToInt(list.Slider(floodRecutSeamCount, 0f, 20f));
            list.GapLine();

            list.CheckboxLabeled("The flood wakes a sleeping muttavaq", ref muttavaqWaterWakeEnabled,
                "A muttavaq asleep under its pan wakes when water reaches it. Off means "
                + "it only wakes when hurt.");
            list.CheckboxLabeled("A muttavaq digs back in at the dry", ref muttavaqDigInEnabled,
                "After the flood is gone and its ground has dried, an awake muttavaq "
                + "seals itself in where it stands and sleeps until the next flood.");

            viewHeight = list.CurHeight + 24f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPosition = Vector2.zero;
        private static float viewHeight = 1200f;

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
