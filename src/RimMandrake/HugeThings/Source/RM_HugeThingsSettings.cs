using UnityEngine;
using Verse;

namespace RimMandrake.HugeThings
{
    // MOD_OPTIONS_RETROFIT_1 contract: one toggle per mechanic, tuning where a number is the experience, defaults = shipped behaviour,
    // all-off = vanilla. Owner 2026-10-07 (merge of Titanic Creatures into Huge Things): "Many configurations. Do you want giant
    // plants? Giant animals? Detailed behaviors. Etc." -> two master toggles, each with its detailed behaviours beneath. Every
    // field keeps the key it had in its old mod (Titanic Creatures' twelve came over unchanged). A behaviour is live through its
    // *Active property (HugeGates in the kernel): master AND its own toggle. "(restart)" marks what is read once at startup.
    public class RM_HugeThingsSettings : ModSettings
    {
        public const float MaxTrunkScale = 1.5f;

        // --- Giant plants -------------------------------------------------------------------------------------------------------
        public static bool giantPlantsEnabled = true;
        public static bool plantTrunkEnabled = true;
        public static bool plantSelectionEnabled = true;
        public static float plantTrunkScale = 1f;
        public static bool plantTrunkDamageEnabled = true;
        public static bool plantItemPushEnabled = true;

        // --- Giant animals ------------------------------------------------------------------------------------------------------
        public static bool giantAnimalsEnabled = true;
        public static bool pawnHitboxEnabled = true;
        public static float pawnHitboxScale = 1f;
        public static bool largePawnsFootprintEnabled = true;
        public static bool tierThresholdsCustom = false;
        public static float tierT1MinBodySize = 4f;
        public static float tierT2MinBodySize = 8f;
        public static float tierT3MinBodySize = 20f;
        public static bool wakeEnabled = true;
        public static float wakeCrushDamageMultiplier = 1f;
        public static float wakeFilthTrailChance = 0.35f;
        public static bool wakeRoofHolingEnabled = true;
        public static bool giantPlantSmashEnabled = true;
        public static int giantPlantSmashMinTier = 3;
        public static bool roofAvoidanceEnabled = true;
        public static bool yieldCurveEnabled = true;
        public static float yieldCurveMinFactor = 0.15f;
        public static bool corpseSiteEnabled = true;
        public static int corpseSiteHarvestMeatPerSession = 25;
        public static int corpseSiteHarvestLeatherPerSession = 10;
        public static float corpseSiteMeatSpoilagePerDay = 0.15f;
        public static float corpseSiteLeatherSpoilagePerDay = 0.08f;
        // 2500 ticks == 1 in-game hour (GenDate.TicksPerHour).
        public static float corpseSiteWorkHoursPerSession = 1f;

        // --- What is live (master AND detail) -----------------------------------------------------------------------------------
        public static bool PlantTrunkActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkEnabled);
        public static bool PlantSelectionActive => HugeGates.Plant(giantPlantsEnabled, plantSelectionEnabled);
        public static bool PlantTrunkDamageActive => HugeGates.Plant(giantPlantsEnabled, plantTrunkDamageEnabled);
        public static bool PlantItemPushActive => HugeGates.Plant(giantPlantsEnabled, plantItemPushEnabled);
        public static bool PawnHitboxActive => HugeGates.Animal(giantAnimalsEnabled, pawnHitboxEnabled);
        public static bool LargePawnsFootprintActive => HugeGates.Animal(giantAnimalsEnabled, largePawnsFootprintEnabled);
        public static bool TierThresholdsCustomActive => HugeGates.Animal(giantAnimalsEnabled, tierThresholdsCustom);
        public static bool WakeActive => HugeGates.Animal(giantAnimalsEnabled, wakeEnabled);
        public static bool RoofHolingActive => HugeGates.Wake(giantAnimalsEnabled, wakeEnabled, wakeRoofHolingEnabled);
        public static bool GiantPlantSmashActive => HugeGates.Smash(giantPlantsEnabled, giantAnimalsEnabled, wakeEnabled, giantPlantSmashEnabled);
        public static bool RoofAvoidanceActive => HugeGates.Animal(giantAnimalsEnabled, roofAvoidanceEnabled);
        public static bool YieldCurveActive => HugeGates.Animal(giantAnimalsEnabled, yieldCurveEnabled);
        public static bool CorpseSiteActive => HugeGates.Animal(giantAnimalsEnabled, corpseSiteEnabled);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref giantPlantsEnabled, "giantPlantsEnabled", true);
            Scribe_Values.Look(ref plantTrunkEnabled, "plantTrunkEnabled", true);
            Scribe_Values.Look(ref plantSelectionEnabled, "plantSelectionEnabled", true);
            Scribe_Values.Look(ref plantTrunkScale, "plantTrunkScale", 1f);
            Scribe_Values.Look(ref plantTrunkDamageEnabled, "plantTrunkDamageEnabled", true);
            Scribe_Values.Look(ref plantItemPushEnabled, "plantItemPushEnabled", true);
            Scribe_Values.Look(ref giantAnimalsEnabled, "giantAnimalsEnabled", true);
            Scribe_Values.Look(ref pawnHitboxEnabled, "pawnHitboxEnabled", true);
            Scribe_Values.Look(ref pawnHitboxScale, "pawnHitboxScale", 1f);
            Scribe_Values.Look(ref largePawnsFootprintEnabled, "largePawnsFootprintEnabled", true);
            Scribe_Values.Look(ref tierThresholdsCustom, "tierThresholdsCustom", false);
            Scribe_Values.Look(ref tierT1MinBodySize, "tierT1MinBodySize", 4f);
            Scribe_Values.Look(ref tierT2MinBodySize, "tierT2MinBodySize", 8f);
            Scribe_Values.Look(ref tierT3MinBodySize, "tierT3MinBodySize", 20f);
            Scribe_Values.Look(ref wakeEnabled, "wakeEnabled", true);
            Scribe_Values.Look(ref wakeCrushDamageMultiplier, "wakeCrushDamageMultiplier", 1f);
            Scribe_Values.Look(ref wakeFilthTrailChance, "wakeFilthTrailChance", 0.35f);
            Scribe_Values.Look(ref wakeRoofHolingEnabled, "wakeRoofHolingEnabled", true);
            Scribe_Values.Look(ref giantPlantSmashEnabled, "giantPlantSmashEnabled", true);
            Scribe_Values.Look(ref giantPlantSmashMinTier, "giantPlantSmashMinTier", 3);
            Scribe_Values.Look(ref roofAvoidanceEnabled, "roofAvoidanceEnabled", true);
            Scribe_Values.Look(ref yieldCurveEnabled, "yieldCurveEnabled", true);
            Scribe_Values.Look(ref yieldCurveMinFactor, "yieldCurveMinFactor", 0.15f);
            Scribe_Values.Look(ref corpseSiteEnabled, "corpseSiteEnabled", true);
            Scribe_Values.Look(ref corpseSiteHarvestMeatPerSession, "corpseSiteHarvestMeatPerSession", 25);
            Scribe_Values.Look(ref corpseSiteHarvestLeatherPerSession, "corpseSiteHarvestLeatherPerSession", 10);
            Scribe_Values.Look(ref corpseSiteMeatSpoilagePerDay, "corpseSiteMeatSpoilagePerDay", 0.15f);
            Scribe_Values.Look(ref corpseSiteLeatherSpoilagePerDay, "corpseSiteLeatherSpoilagePerDay", 0.08f);
            Scribe_Values.Look(ref corpseSiteWorkHoursPerSession, "corpseSiteWorkHoursPerSession", 1f);
            if (Scribe.mode == LoadSaveMode.PostLoadInit || Scribe.mode == LoadSaveMode.LoadingVars)
            {
                // a hand-edited or stale config must not outgrow the planning window (MaxKeys uses MaxTrunkScale) or go NaN
                plantTrunkScale = float.IsNaN(plantTrunkScale) ? 1f : Mathf.Clamp(plantTrunkScale, 0.5f, MaxTrunkScale);
                pawnHitboxScale = float.IsNaN(pawnHitboxScale) ? 1f : Mathf.Clamp(pawnHitboxScale, 0.5f, MaxTrunkScale);
                giantPlantSmashMinTier = Mathf.Clamp(giantPlantSmashMinTier, 1, 3);
            }
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1600f;
        private const float Indent = 24f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);

            // ===== Giant plants =====
            Text.Font = GameFont.Medium;
            list.Label("Giant plants");
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("Giant plants behave like their size", ref giantPlantsEnabled,
                "Master switch for everything below in this section. Off: every huge plant is an ordinary one-cell plant, as in "
              + "vanilla (a giant that is solid on its own cell stays so until a restart).");
            if (giantPlantsEnabled)
            {
                list.Indent(Indent);
                list.ColumnWidth -= Indent;
                list.CheckboxLabeled("Solid where they touch the ground", ref plantTrunkEnabled,
                    "A huge plant blocks the cells where its stem, roots or body meet the ground (measured from its art), "
                  + "so pawns walk around it and nothing can be built inside it; its overhanging cap stays walkable. "
                  + "A giant whose art touches the ground only in its own cell becomes solid on that cell (restart). "
                  + "Off: every plant is one walk-through cell, as in vanilla.");
                if (plantTrunkEnabled)
                {
                    list.Label("  Ground footprint size: " + plantTrunkScale.ToString("0.00") + "x");
                    plantTrunkScale = list.Slider(plantTrunkScale, 0.5f, MaxTrunkScale);
                    list.CheckboxLabeled("  Trunks give cover, and shots into them hurt the plant", ref plantTrunkDamageEnabled,
                        "A shot or blast that hits a trunk cell damages the giant once per projectile, beam or blast. Off: the "
                      + "trunk still gives partial cover but soaks the hit, and the plant is unharmed.");
                    list.CheckboxLabeled("  Push items out of a growing trunk", ref plantItemPushEnabled,
                        "When a trunk grows over a cell holding only items, the items are moved gently to the nearest free cell "
                      + "(their own stockpile first). Off: that cell simply stays open until it is clear.");
                }
                list.CheckboxLabeled("Click anywhere on a huge plant's picture to select it", ref plantSelectionEnabled,
                    "Off: a huge plant can only be selected on the one cell it grows from.");
                list.ColumnWidth += Indent;
                list.Outdent(Indent);
            }
            list.GapLine();

            // ===== Giant animals =====
            Text.Font = GameFont.Medium;
            list.Label("Giant animals");
            Text.Font = GameFont.Small;
            list.CheckboxLabeled("Giant animals behave like their size", ref giantAnimalsEnabled,
                "Master switch for everything below in this section: click hitboxes, size tiers, the destruction wake, roofs, "
              + "giant-plant smashing, butcher yield and the corpse site. Off: every creature behaves as in vanilla.");
            if (giantAnimalsEnabled)
            {
                list.Indent(Indent);
                list.ColumnWidth -= Indent;
                list.CheckboxLabeled("Click anywhere on a huge animal to select it", ref pawnHitboxEnabled,
                    "A huge creature can be selected by clicking anywhere on its drawn body. Off: only near its middle.");
                if (pawnHitboxEnabled)
                {
                    list.Label("  Hitbox size: " + pawnHitboxScale.ToString("0.00") + "x");
                    pawnHitboxScale = list.Slider(pawnHitboxScale, 0.5f, MaxTrunkScale);
                }
                list.CheckboxLabeled("Multi-cell footprint from Large Pawns (restart)", ref largePawnsFootprintEnabled,
                    "When Large Pawns is loaded, its size ladder is set to the tiers below so a titan occupies 2x2, 3x3 or 4x4 "
                  + "cells. Off: Large Pawns keeps its own settings. Without Large Pawns every titan is one cell either way.");
                list.CheckboxLabeled("Custom size tiers (restart)", ref tierThresholdsCustom,
                    "A creature is a titan by its body size: T1 heavy, T2 colossal, T3 titanic. Off: the shipped tiers (4 / 8 / 20). "
                  + "Which races carry the wake is decided at startup, so a race newly crossing T1 needs a restart.");
                if (tierThresholdsCustom)
                {
                    list.Label("  T1 from body size " + tierT1MinBodySize.ToString("0.0"));
                    tierT1MinBodySize = list.Slider(tierT1MinBodySize, 1f, 30f);
                    list.Label("  T2 from body size " + tierT2MinBodySize.ToString("0.0"));
                    tierT2MinBodySize = list.Slider(tierT2MinBodySize, 2f, 60f);
                    list.Label("  T3 from body size " + tierT3MinBodySize.ToString("0.0"));
                    tierT3MinBodySize = list.Slider(tierT3MinBodySize, 3f, 100f);
                    if (!(tierT1MinBodySize < tierT2MinBodySize && tierT2MinBodySize < tierT3MinBodySize))
                        list.Label("  These must rise T1 < T2 < T3; until they do, the shipped tiers are used.");
                }
                list.CheckboxLabeled("Destruction wake", ref wakeEnabled,
                    "A titan crushes crates and plants, breaches walls and leaves rubble as it walks. Off: it walks through "
                  + "everything harmlessly, and none of the wake options below apply.");
                if (wakeEnabled)
                {
                    list.Label("  Crush damage: " + wakeCrushDamageMultiplier.ToString("0.00") + "x");
                    wakeCrushDamageMultiplier = list.Slider(wakeCrushDamageMultiplier, 0.25f, 3f);
                    list.Label("  Rubble trail chance per step: " + (wakeFilthTrailChance * 100f).ToString("0") + "%");
                    wakeFilthTrailChance = list.Slider(wakeFilthTrailChance, 0f, 1f);
                    list.CheckboxLabeled("  Colossal titans hole thin roofs", ref wakeRoofHolingEnabled,
                        "T2 and larger tear out constructed and thin rock roofs as they pass. Overhead mountain is never removed.");
                    list.CheckboxLabeled("  The biggest titans smash giant plants", ref giantPlantSmashEnabled,
                        "A titan at or above the smash tier damages every giant plant whose trunk it brushes, once per step, until "
                      + "the plant falls and the way opens. Smaller titans treat giant trunks as walls and go around. Off: every "
                      + "titan goes around.");
                    if (giantPlantSmashEnabled)
                    {
                        list.Label("    Smash tier: T" + giantPlantSmashMinTier + " and larger");
                        giantPlantSmashMinTier = Mathf.Clamp(Mathf.RoundToInt(list.Slider(giantPlantSmashMinTier, 1f, 3f)), 1, 3);
                    }
                }
                list.CheckboxLabeled("Slowed under overhead mountain", ref roofAvoidanceEnabled,
                    "A titan crossing a cell under overhead mountain moves very slowly. Off: it moves like any other pawn.");
                list.CheckboxLabeled("Reduced butcher yield on titans", ref yieldCurveEnabled,
                    "A T1 or T2 titan butchers for somewhat less meat and leather per body size than a same-mass ordinary animal "
                  + "would. Off: full vanilla yield.");
                if (yieldCurveEnabled)
                {
                    list.Label("  Minimum yield floor: " + (yieldCurveMinFactor * 100f).ToString("0") + "% of normal");
                    yieldCurveMinFactor = list.Slider(yieldCurveMinFactor, 0.05f, 1f);
                }
                list.CheckboxLabeled("T3 corpse becomes a harvest site", ref corpseSiteEnabled,
                    "The largest tier's corpse becomes a standing landmark, harvested over several work sessions with the yield "
                  + "slowly spoiling, instead of being butchered at once. Off: it butchers like any ordinary corpse.");
                if (corpseSiteEnabled)
                {
                    list.Label("  Meat per harvest session: " + corpseSiteHarvestMeatPerSession);
                    corpseSiteHarvestMeatPerSession = (int)list.Slider(corpseSiteHarvestMeatPerSession, 5f, 100f);
                    list.Label("  Leather per harvest session: " + corpseSiteHarvestLeatherPerSession);
                    corpseSiteHarvestLeatherPerSession = (int)list.Slider(corpseSiteHarvestLeatherPerSession, 2f, 50f);
                    list.Label("  Work hours per session: " + corpseSiteWorkHoursPerSession.ToString("0.0"));
                    corpseSiteWorkHoursPerSession = list.Slider(corpseSiteWorkHoursPerSession, 0.25f, 6f);
                    list.Label("  Meat spoilage per day: " + (corpseSiteMeatSpoilagePerDay * 100f).ToString("0") + "%");
                    corpseSiteMeatSpoilagePerDay = list.Slider(corpseSiteMeatSpoilagePerDay, 0.02f, 0.5f);
                    list.Label("  Leather spoilage per day: " + (corpseSiteLeatherSpoilagePerDay * 100f).ToString("0") + "%");
                    corpseSiteLeatherSpoilagePerDay = list.Slider(corpseSiteLeatherSpoilagePerDay, 0.02f, 0.5f);
                }
                list.ColumnWidth += Indent;
                list.Outdent(Indent);
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
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
