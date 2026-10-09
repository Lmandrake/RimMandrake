using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    public enum PressGate
    {
        Research,
        Buildable,
        Unbuildable,
    }

    // Spec §7 ("Chain" group) -- Phase 1 of DEEPFIRE_PIGMENT_MOD_1. Every
    // number here is real: read live by CompMatVitality/GenStep_ShoreMats,
    // or applied to the loaded defs by ApplySettings() (called at startup
    // and again on WriteSettings, so a change while paused takes effect with
    // no restart -- SlimeMod's own precedent, src/RimMandrake/GelatinousSlime/
    // Source/SlimeMod.cs).
    //
    // The Chain (Phase 1, DEEPFIRE_PIGMENT_MOD_1), the Cuisine/god-bridge/
    // status pieces of DEEPFIRE_PAINT_STATUS_CUISINE_1, and -- as of
    // DEEPFIRE_MOD_SETTINGS_1 -- the whole "Painting" group (spec §7):
    // coats/radius/intensity, per-target costs, clustering, the five
    // paintable-target toggles, worn-item lighting, the styling-station
    // checkbox, the combat penalties and the first-coat/floor beauty
    // numbers, plus moodScale and goodwillPerImpressedVisit (Status) and
    // ishkoIdolPaintable (Gods). Still NOT wired here, and still real gaps
    // (Cuisine's per-family weight sliders and effectScale): those are not
    // among the numbers DEEPFIRE_FLOOR_PAINT_1/DEEPFIRE_FIRSTCOAT_BONUS_1/
    // DEEPFIRE_WORN_GLOW_1/DEEPFIRE_STATUS_THOUGHTS_1/DEEPFIRE_GOD_BRIDGE_
    // DELTAS_1 named as owed, so they stay out of this item's scope. The
    // god numbers are all wired (DEEPFIRE_GOD_BRIDGE_DELTAS_1).
    public class LuminousPigmentSettings : ModSettings
    {
        public static bool shoreMatsEnabled = true;
        public static float shoreMatChance = 0.006f;
        public static float matLifeDays = 1.0f;
        public static float matChillKillTemp = 10f;

        public static PressGate pressGate = PressGate.Research;
        public static float pressResearchCost = 800f;
        public static int pressYield = 2;
        public static float pressWorkAmount = 1800f;
        public static float pressPower = 150f;

        public static float deepfireMarketValue = 90f;
        public static bool deepfireStackGlows = true;

        public static bool glowTankEnabled = true;
        public static float tankGrowDays = 12f;
        public static int tankYield = 2;
        public static float tankPower = 180f;
        public static float tankPowerGraceHours = 6f;
        // DESIGN_PASS LP-2: with FlowWorks loaded, the tank drinks salt or boiling water from a liquid net.
        // PROVISIONAL: 4 units per day of running.
        public static bool tankNeedsWater = true;
        public static float tankWaterUnitsPerDay = 4f;

        // Painting (spec §3, §7 "Painting" group) -- DEEPFIRE_MOD_SETTINGS_1.
        // Every one of these is read LIVE at its point of use (the
        // established pattern for this file: statusEnabled/offenceThreshold/
        // godDeltaLike etc. are all read straight off this class, not baked
        // into a def), so a change while paused takes effect on the very
        // next call -- no def rewrite, no ApplySettings entry needed.
        public static bool paintingEnabled = true;
        public static int maxCoats = CompDeepfire.MaxCoats;
        public static float[] coatRadius = (float[])DeepfirePaintDefaults.CoatRadius.Clone();
        public static float[] coatIntensity = (float[])DeepfirePaintDefaults.CoatIntensity.Clone();
        public static float glowMinValue = DeepfirePaintDefaults.GlowMinValue;
        public static int costWallCell = 1;
        public static int costFloorCell = DeepfirePaintDefaults.CostFloorCell;
        public static int costFurnitureBase = 2;
        public static int costFurniturePerExtraCell = 1;
        public static int costFurnitureCap = 6;
        public static int costArt = 3;
        public static int costApparel = 3;
        public static int costWeapon = 3;
        public static int clusterBlock = DeepfirePaintDefaults.ClusterBlock;
        public static bool floorsPaintable = true;
        public static bool wallsPaintable = true;
        public static bool furniturePaintable = true;
        public static bool apparelPaintable = true;
        public static bool weaponsPaintable = true;
        public static bool wornLightEnabled = true;
        public static bool stylingStationLacquer = true;
        public static int wornLightTickInterval = DeepfirePaintDefaults.WornLightTickInterval;
        public static float glowTargetFactor = DeepfirePaintDefaults.GlowTargetFactor;
        public static float glowDodgePenalty = DeepfirePaintDefaults.GlowDodgePenalty;
        public static bool combatPenaltiesEnabled = true;
        public static bool artQualityBump = true;
        public static float beautyFlat = DeepfirePaintDefaults.FirstCoatBeautyFlat;
        public static float beautyPct = DeepfirePaintDefaults.FirstCoatBeautyPct;
        public static int beautySizeCap = DeepfirePaintDefaults.FirstCoatBeautySizeCap;
        public static float floorBeautyPerCell = DeepfirePaintDefaults.FloorBeautyPerCell;
        public static float floorRoomBonusPer10 = DeepfirePaintDefaults.FloorRoomBonusPer10;
        public static float floorRoomBonusCap = DeepfirePaintDefaults.FloorRoomBonusCap;

        // Cuisine (spec §6, §7 "Cuisine" group)
        public static bool cuisineEnabled = true;
        public static int steerMinSkill = 10;
        public static int vermilionMinSkill = 14;
        public static int maxFamiliesPerPawn = 3;
        public static bool hediffGlowEnabled = true;
        public static bool[] familyEnabled = NewFamilyEnabledArray();

        private static bool[] NewFamilyEnabledArray()
        {
            bool[] arr = new bool[DeepfireFamilies.All.Count];
            for (int i = 0; i < arr.Length; i++) arr[i] = true;
            return arr;
        }

        // Gods (spec §5.2 / §7 "Gods" group), every one read live by
        // DeepfireGodDeltas / the dish and vermilion hooks. Defaults are
        // Ninefold's EventMagnitude Small 3 / Medium 8 / Large 15.
        public static bool godsReact = true;
        public static float godDeltaLike = 3f;           // Small: every god, first coat; a dish eaten
        public static float godDeltaAdore = 8f;          // Medium: the trio's first coat; worn-coat Ishko; sold; vermilion
        public static float godDeltaIshko = 3f;          // Small: Ishko's dislike of a plain first coat
        public static float godDeltaStatue = 15f;        // Large: a god's own statue coated
        public static int godDeltaDiminishAfter = 10;    // first-coat events per def before deltas shrink to 1
        public static bool ishkoIdolPaintable = true;    // off = the designator refuses Ishko's own idol

        // Status -- the purple engine (spec §7 "Status" group)
        public static bool statusEnabled = true;
        public static int displayCap = 6;
        public static int offenceThreshold = 2;
        public static float moodScale = 1.0f;
        public static float opinionAboveStation = -15f;
        public static int goodwillPerImpressedVisit = DeepfireStatusDefaults.GoodwillPerImpressedVisit;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shoreMatsEnabled, "shoreMatsEnabled", true);
            Scribe_Values.Look(ref shoreMatChance, "shoreMatChance", 0.006f);
            Scribe_Values.Look(ref matLifeDays, "matLifeDays", 1.0f);
            Scribe_Values.Look(ref matChillKillTemp, "matChillKillTemp", 10f);
            Scribe_Values.Look(ref pressGate, "pressGate", PressGate.Research);
            Scribe_Values.Look(ref pressResearchCost, "pressResearchCost", 800f);
            Scribe_Values.Look(ref pressYield, "pressYield", 2);
            Scribe_Values.Look(ref pressWorkAmount, "pressWorkAmount", 1800f);
            Scribe_Values.Look(ref pressPower, "pressPower", 150f);
            Scribe_Values.Look(ref deepfireMarketValue, "deepfireMarketValue", 90f);
            Scribe_Values.Look(ref deepfireStackGlows, "deepfireStackGlows", true);
            Scribe_Values.Look(ref glowTankEnabled, "glowTankEnabled", true);
            Scribe_Values.Look(ref tankGrowDays, "tankGrowDays", 12f);
            Scribe_Values.Look(ref tankYield, "tankYield", 2);
            Scribe_Values.Look(ref tankPower, "tankPower", 180f);
            Scribe_Values.Look(ref tankPowerGraceHours, "tankPowerGraceHours", 6f);
            Scribe_Values.Look(ref tankNeedsWater, "tankNeedsWater", true);
            Scribe_Values.Look(ref tankWaterUnitsPerDay, "tankWaterUnitsPerDay", 4f);

            Scribe_Values.Look(ref paintingEnabled, "paintingEnabled", true);
            Scribe_Values.Look(ref maxCoats, "maxCoats", CompDeepfire.MaxCoats);
            List<float> coatRadiusList = new List<float>(coatRadius);
            Scribe_Collections.Look(ref coatRadiusList, "coatRadius", LookMode.Value);
            if (coatRadiusList != null && coatRadiusList.Count == coatRadius.Length) coatRadius = coatRadiusList.ToArray();
            List<float> coatIntensityList = new List<float>(coatIntensity);
            Scribe_Collections.Look(ref coatIntensityList, "coatIntensity", LookMode.Value);
            if (coatIntensityList != null && coatIntensityList.Count == coatIntensity.Length) coatIntensity = coatIntensityList.ToArray();
            Scribe_Values.Look(ref glowMinValue, "glowMinValue", DeepfirePaintDefaults.GlowMinValue);
            Scribe_Values.Look(ref costWallCell, "costWallCell", 1);
            Scribe_Values.Look(ref costFloorCell, "costFloorCell", DeepfirePaintDefaults.CostFloorCell);
            Scribe_Values.Look(ref costFurnitureBase, "costFurnitureBase", 2);
            Scribe_Values.Look(ref costFurniturePerExtraCell, "costFurniturePerExtraCell", 1);
            Scribe_Values.Look(ref costFurnitureCap, "costFurnitureCap", 6);
            Scribe_Values.Look(ref costArt, "costArt", 3);
            Scribe_Values.Look(ref costApparel, "costApparel", 3);
            Scribe_Values.Look(ref costWeapon, "costWeapon", 3);
            Scribe_Values.Look(ref clusterBlock, "clusterBlock", DeepfirePaintDefaults.ClusterBlock);
            Scribe_Values.Look(ref floorsPaintable, "floorsPaintable", true);
            Scribe_Values.Look(ref wallsPaintable, "wallsPaintable", true);
            Scribe_Values.Look(ref furniturePaintable, "furniturePaintable", true);
            Scribe_Values.Look(ref apparelPaintable, "apparelPaintable", true);
            Scribe_Values.Look(ref weaponsPaintable, "weaponsPaintable", true);
            Scribe_Values.Look(ref wornLightEnabled, "wornLightEnabled", true);
            Scribe_Values.Look(ref stylingStationLacquer, "stylingStationLacquer", true);
            Scribe_Values.Look(ref wornLightTickInterval, "wornLightTickInterval", DeepfirePaintDefaults.WornLightTickInterval);
            Scribe_Values.Look(ref glowTargetFactor, "glowTargetFactor", DeepfirePaintDefaults.GlowTargetFactor);
            Scribe_Values.Look(ref glowDodgePenalty, "glowDodgePenalty", DeepfirePaintDefaults.GlowDodgePenalty);
            Scribe_Values.Look(ref combatPenaltiesEnabled, "combatPenaltiesEnabled", true);
            Scribe_Values.Look(ref artQualityBump, "artQualityBump", true);
            Scribe_Values.Look(ref beautyFlat, "beautyFlat", DeepfirePaintDefaults.FirstCoatBeautyFlat);
            Scribe_Values.Look(ref beautyPct, "beautyPct", DeepfirePaintDefaults.FirstCoatBeautyPct);
            Scribe_Values.Look(ref beautySizeCap, "beautySizeCap", DeepfirePaintDefaults.FirstCoatBeautySizeCap);
            Scribe_Values.Look(ref floorBeautyPerCell, "floorBeautyPerCell", DeepfirePaintDefaults.FloorBeautyPerCell);
            Scribe_Values.Look(ref floorRoomBonusPer10, "floorRoomBonusPer10", DeepfirePaintDefaults.FloorRoomBonusPer10);
            Scribe_Values.Look(ref floorRoomBonusCap, "floorRoomBonusCap", DeepfirePaintDefaults.FloorRoomBonusCap);

            Scribe_Values.Look(ref cuisineEnabled, "cuisineEnabled", true);
            Scribe_Values.Look(ref steerMinSkill, "steerMinSkill", 10);
            Scribe_Values.Look(ref vermilionMinSkill, "vermilionMinSkill", 14);
            Scribe_Values.Look(ref maxFamiliesPerPawn, "maxFamiliesPerPawn", 3);
            Scribe_Values.Look(ref hediffGlowEnabled, "hediffGlowEnabled", true);
            List<bool> familyEnabledList = new List<bool>(familyEnabled);
            Scribe_Collections.Look(ref familyEnabledList, "familyEnabled", LookMode.Value);
            if (familyEnabledList != null && familyEnabledList.Count == familyEnabled.Length)
            {
                familyEnabled = familyEnabledList.ToArray();
            }

            Scribe_Values.Look(ref godsReact, "godsReact", true);
            Scribe_Values.Look(ref godDeltaLike, "godDeltaLike", 3f);
            Scribe_Values.Look(ref godDeltaAdore, "godDeltaAdore", 8f);
            Scribe_Values.Look(ref godDeltaIshko, "godDeltaIshko", 3f);
            Scribe_Values.Look(ref godDeltaStatue, "godDeltaStatue", 15f);
            Scribe_Values.Look(ref godDeltaDiminishAfter, "godDeltaDiminishAfter", 10);
            Scribe_Values.Look(ref ishkoIdolPaintable, "ishkoIdolPaintable", true);

            Scribe_Values.Look(ref statusEnabled, "statusEnabled", true);
            Scribe_Values.Look(ref displayCap, "displayCap", 6);
            Scribe_Values.Look(ref offenceThreshold, "offenceThreshold", 2);
            Scribe_Values.Look(ref moodScale, "moodScale", 1.0f);
            Scribe_Values.Look(ref opinionAboveStation, "opinionAboveStation", -15f);
            Scribe_Values.Look(ref goodwillPerImpressedVisit, "goodwillPerImpressedVisit", DeepfireStatusDefaults.GoodwillPerImpressedVisit);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

            list.Label("THE CHAIN");
            list.CheckboxLabeled("Wild crowncarpet on ocean shores", ref shoreMatsEnabled,
                "On (default): a rare wild patch of crowncarpet may appear on any ocean shore "
                + "when a new map generates. Off: crowncarpet only grows wherever a biome's own "
                + "roster places it (e.g. the Scald, with the Utinni patch). Affects new maps only.");
            list.Label("Shore mat rarity: " + shoreMatChance.ToString("0.000"));
            shoreMatChance = list.Slider(shoreMatChance, 0f, 0.05f);
            list.GapLine();

            list.Label("Fresh crowncarpet's clock: " + matLifeDays.ToString("0.00") + " days");
            list.Label("How long a harvested mat survives before it dies on its own.");
            matLifeDays = list.Slider(matLifeDays, 0.25f, 5f);
            list.Label("Dies at once below: " + matChillKillTemp.ToString("0") + "C");
            matChillKillTemp = list.Slider(matChillKillTemp, -20f, 20f);
            list.GapLine();

            list.Label("THE PRESS");
            list.Label("How the deepfire press (and its research) is unlocked.");
            if (list.RadioButton("Research (default) -- gated behind a hidden project, "
                    + "revealed once a mat is seen", pressGate == PressGate.Research))
            {
                pressGate = PressGate.Research;
            }
            if (list.RadioButton("Always buildable -- no research needed",
                    pressGate == PressGate.Buildable))
            {
                pressGate = PressGate.Buildable;
            }
            if (list.RadioButton("Unbuildable -- only where a scenario or quest places one",
                    pressGate == PressGate.Unbuildable))
            {
                pressGate = PressGate.Unbuildable;
            }
            list.Label("Deepfire per batch (4 fresh mat + fixative): " + pressYield.ToString());
            pressYield = Mathf.RoundToInt(list.Slider(pressYield, 1f, 6f));
            list.Label("Press power draw: " + pressPower.ToString("0") + " W");
            pressPower = list.Slider(pressPower, 50f, 600f);
            list.GapLine();

            list.Label("DEEPFIRE");
            list.Label("Market value per jar: " + deepfireMarketValue.ToString("0"));
            deepfireMarketValue = list.Slider(deepfireMarketValue, 10f, 500f);
            list.CheckboxLabeled("A deepfire stockpile glows", ref deepfireStackGlows,
                "On (default): a stack of refined deepfire gives off a faint light on its own -- "
                + "the mod's first tell in a dark room.");
            list.GapLine();

            list.Label("THE GLOWTANK");
            list.CheckboxLabeled("GlowTank buildable", ref glowTankEnabled,
                "Off: the GlowTank does not appear in the build menu. Existing tanks keep working.");
            list.Label("Power outage before it kills the culture: " + tankPowerGraceHours.ToString("0") + " h");
            tankPowerGraceHours = list.Slider(tankPowerGraceHours, 0f, 48f);
            list.CheckboxLabeled("Tank needs ocean water (FlowWorks)", ref tankNeedsWater,
                "On (default), with FlowWorks loaded: the tank drinks salt or boiling water from a FlowWorks "
                + "liquid tank beside it or on a hose run touching it. Dry, its crop stops growing until water "
                + "arrives; nothing dies of thirst. Brine and fresh water do not count. Without FlowWorks, or "
                + "off: power and a seed culture are enough.");
            list.Label("Ocean water drunk per day of running (units): " + tankWaterUnitsPerDay.ToString("0.0"));
            tankWaterUnitsPerDay = list.Slider(tankWaterUnitsPerDay, 0.5f, 20f);
            list.GapLine();

            list.Label("PAINTING");
            list.CheckboxLabeled("Painting enabled", ref paintingEnabled,
                "Off: the designator and WorkGiver stop accepting new deepfire jobs. Existing coats " +
                "keep glowing.");
            list.Label("Max coats: " + maxCoats.ToString());
            maxCoats = Mathf.RoundToInt(list.Slider(maxCoats, 1f, CompDeepfire.MaxCoats));
            for (int i = 1; i <= CompDeepfire.MaxCoats; i++)
            {
                list.Label("Coat " + i + " radius: " + coatRadius[i].ToString("0.0"));
                coatRadius[i] = list.Slider(coatRadius[i], 0.5f, 6f);
                list.Label("Coat " + i + " intensity: " + coatIntensity[i].ToString("0.00"));
                coatIntensity[i] = list.Slider(coatIntensity[i], 0.1f, 1f);
            }
            list.Label("Dark-dye value floor: " + glowMinValue.ToString("0.00"));
            glowMinValue = list.Slider(glowMinValue, 0f, 1f);
            list.GapLine();

            list.Label("Deepfire cost per target");
            list.Label("Wall cell: " + costWallCell.ToString());
            costWallCell = Mathf.RoundToInt(list.Slider(costWallCell, 1f, 20f));
            list.Label("Floor cell: " + costFloorCell.ToString());
            costFloorCell = Mathf.RoundToInt(list.Slider(costFloorCell, 1f, 20f));
            list.Label("Furniture, 1x1: " + costFurnitureBase.ToString());
            costFurnitureBase = Mathf.RoundToInt(list.Slider(costFurnitureBase, 1f, 20f));
            list.Label("Furniture, per extra cell: " + costFurniturePerExtraCell.ToString());
            costFurniturePerExtraCell = Mathf.RoundToInt(list.Slider(costFurniturePerExtraCell, 0f, 20f));
            list.Label("Furniture cap: " + costFurnitureCap.ToString());
            costFurnitureCap = Mathf.RoundToInt(list.Slider(costFurnitureCap, 1f, 20f));
            list.Label("Art item: " + costArt.ToString());
            costArt = Mathf.RoundToInt(list.Slider(costArt, 1f, 20f));
            list.Label("Apparel: " + costApparel.ToString());
            costApparel = Mathf.RoundToInt(list.Slider(costApparel, 1f, 20f));
            list.Label("Weapon: " + costWeapon.ToString());
            costWeapon = Mathf.RoundToInt(list.Slider(costWeapon, 1f, 20f));
            list.GapLine();

            list.Label("Light clustering: " + clusterBlock.ToString() + " cell(s) per group");
            list.Label("1 = one light per coated cell/thing (most accurate, most lights).");
            clusterBlock = Mathf.RoundToInt(list.Slider(clusterBlock, 1f, 5f));
            list.GapLine();

            list.Label("What can take deepfire");
            list.CheckboxLabeled("Floors", ref floorsPaintable);
            list.CheckboxLabeled("Walls", ref wallsPaintable);
            list.CheckboxLabeled("Furniture and art", ref furniturePaintable);
            list.CheckboxLabeled("Apparel", ref apparelPaintable);
            list.CheckboxLabeled("Weapons", ref weaponsPaintable);
            list.GapLine();

            list.CheckboxLabeled("Worn deepfire lights its wearer", ref wornLightEnabled,
                "Off: worn apparel/weapons keep their coats but only glow while sitting on the ground.");
            list.CheckboxLabeled("Styling-station lacquer checkbox", ref stylingStationLacquer,
                "Off: the styling station's deepfire checkbox is hidden. The press-fetch job still works.");
            list.Label("Worn-light cell poll: every " + wornLightTickInterval + " ticks");
            wornLightTickInterval = Mathf.RoundToInt(list.Slider(wornLightTickInterval, 5f, 60f));
            list.CheckboxLabeled("Combat penalties for glowing in the dark", ref combatPenaltiesEnabled,
                "Off: a glowing pawn is neither easier to hit at range nor easier to land a melee blow on.");
            list.Label("Ranged: x" + glowTargetFactor.ToString("0.00") + " target size in the dark");
            glowTargetFactor = list.Slider(glowTargetFactor, 1f, 2f);
            list.Label("Melee: -" + glowDodgePenalty.ToString("0.00") + " dodge chance in the dark");
            glowDodgePenalty = list.Slider(glowDodgePenalty, 0f, 0.3f);
            list.GapLine();

            list.CheckboxLabeled("First-coat quality bump on art items", ref artQualityBump,
                "Off: an art item's first coat charges Deepfire as normal but does not bump its quality.");
            list.Label("Beauty bonus (everything else): +" + beautyFlat.ToString("0.#")
                + " flat x size, +" + beautyPct.ToStringPercent() + " of base beauty");
            beautyFlat = list.Slider(beautyFlat, 0f, 20f);
            beautyPct = list.Slider(beautyPct, 0f, 1f);
            list.Label("Beauty size-factor cap: " + beautySizeCap.ToString());
            beautySizeCap = Mathf.RoundToInt(list.Slider(beautySizeCap, 1f, 9f));
            list.Label("Floor beauty per coated cell: " + floorBeautyPerCell.ToString("0.00"));
            floorBeautyPerCell = list.Slider(floorBeautyPerCell, 0f, 5f);
            list.Label("Room beauty per 10 coated floor cells: " + floorRoomBonusPer10.ToString("0.#")
                + ", capped at " + floorRoomBonusCap.ToString("0.#"));
            floorRoomBonusPer10 = list.Slider(floorRoomBonusPer10, 0f, 10f);
            floorRoomBonusCap = list.Slider(floorRoomBonusCap, 0f, 50f);
            list.GapLine();

            list.Label("CUISINE");
            list.CheckboxLabeled("Deepfire dishes", ref cuisineEnabled,
                "Off: every deepfire recipe disappears from the cookery bill list. Existing glow " +
                "hediffs on pawns who already ate one are unaffected.");
            list.Label("Steered-recipe skill requirement: " + steerMinSkill.ToString());
            steerMinSkill = Mathf.RoundToInt(list.Slider(steerMinSkill, 4f, 18f));
            list.Label("Vermilion (whole-body) recipe skill requirement: " + vermilionMinSkill.ToString());
            vermilionMinSkill = Mathf.RoundToInt(list.Slider(vermilionMinSkill, 10f, 20f));
            list.Label("Glow-hediff families a pawn can carry at once: " + maxFamiliesPerPawn.ToString());
            maxFamiliesPerPawn = Mathf.RoundToInt(list.Slider(maxFamiliesPerPawn, 1f, 14f));
            list.CheckboxLabeled("Glow-hediffs give off light", ref hediffGlowEnabled,
                "Off: the stat/mood effects of every glow-hediff family still apply, but none of " +
                "them light up.");
            list.Label("Families available to roll or steer toward:");
            for (int i = 0; i < DeepfireFamilies.All.Count; i++)
            {
                bool enabled = familyEnabled[i];
                list.CheckboxLabeled("  " + DeepfireFamilies.All[i].key, ref enabled);
                familyEnabled[i] = enabled;
            }
            list.GapLine();

            list.Label("GODS (Ninefold)");
            list.CheckboxLabeled("Gods react to deepfire", ref godsReact,
                "Off: no Ninefold satiation deltas from deepfire at all. Inert with Ninefold absent " +
                "regardless of this setting.");
            list.Label("Liking (every god on a first coat, a dish eaten): " + godDeltaLike.ToString("0.#"));
            godDeltaLike = list.Slider(godDeltaLike, 0f, 20f);
            list.Label("Adoration (Mob'Unloo, Rekko, Zizzik on a first coat; Mob'Unloo on a sale; "
                + "Ishko's anger at worn gear and the vermilion): " + godDeltaAdore.ToString("0.#"));
            godDeltaAdore = list.Slider(godDeltaAdore, 0f, 30f);
            list.Label("Ishko's dislike of a first coat: " + godDeltaIshko.ToString("0.#"));
            godDeltaIshko = list.Slider(godDeltaIshko, 0f, 20f);
            list.Label("A god's own statue coated: " + godDeltaStatue.ToString("0.#"));
            godDeltaStatue = list.Slider(godDeltaStatue, 0f, 40f);
            list.Label("Full reactions per kind of thing painted, then just 1: " + godDeltaDiminishAfter.ToString());
            godDeltaDiminishAfter = Mathf.RoundToInt(list.Slider(godDeltaDiminishAfter, 1f, 50f));
            list.CheckboxLabeled("Ishko's own idol can be painted", ref ishkoIdolPaintable,
                "Off: the designator refuses to mark Ishko's own idol for a coat.");
            list.GapLine();

            list.Label("STATUS (the purple engine)");
            list.CheckboxLabeled("Sumptuary reactions", ref statusEnabled,
                "Off: no status thoughts from deepfire goods at all.");
            list.Label("Display score cap: " + displayCap.ToString());
            displayCap = Mathf.RoundToInt(list.Slider(displayCap, 1f, 12f));
            list.Label("Commoner display score that offends a titled pawn: " + offenceThreshold.ToString());
            offenceThreshold = Mathf.RoundToInt(list.Slider(offenceThreshold, 1f, 6f));
            list.Label("Mood scale (multiplies every deepfire status thought): x" + moodScale.ToString("0.00"));
            moodScale = list.Slider(moodScale, 0f, 3f);
            list.Label("Opinion penalty for wearing above one's station: " + opinionAboveStation.ToString("0"));
            opinionAboveStation = list.Slider(opinionAboveStation, -40f, 0f);
            list.Label("Goodwill per impressed visitor: " + goodwillPerImpressedVisit.ToString());
            goodwillPerImpressedVisit = Mathf.RoundToInt(list.Slider(goodwillPerImpressedVisit, 0f, 10f));

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class LuminousPigmentMod : Mod
    {
        public static LuminousPigmentSettings settings;

        public LuminousPigmentMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<LuminousPigmentSettings>();
            LongEventHandler.ExecuteWhenFinished(ApplySettings);
        }

        public override string SettingsCategory()
        {
            return "Luminous Pigment";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            ApplySettings();
        }

        // Applies every def-level (non-live-read) setting. matLifeDays,
        // matChillKillTemp and shoreMatChance/shoreMatsEnabled are read
        // LIVE by their consumers and need no def rewrite.
        public static void ApplySettings()
        {
            ThingDef press = ThingDef.Named("RM_DeepfirePress");
            ThingDef tank = ThingDef.Named("RM_GlowTank");
            ThingDef deepfire = ThingDef.Named("RM_Deepfire");
            ThingDef crowncarpetCultured = ThingDef.Named("RM_CrowncarpetCultured");
            ResearchProjectDef research = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_DeepfireRefining");
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail("RM_RefineDeepfire");

            if (research != null)
            {
                research.baseCost = LuminousPigmentSettings.pressResearchCost;
                if (LuminousPigmentSettings.pressGate == PressGate.Buildable && !research.IsFinished)
                {
                    Find.ResearchManager?.FinishProject(research, doCompletionDialog: false);
                }
            }

            if (press != null)
            {
                press.designationCategory = (LuminousPigmentSettings.pressGate == PressGate.Unbuildable)
                    ? null
                    : DesignationCategoryDefOf.Production;
                CompProperties_Power powerProps = press.GetCompProperties<CompProperties_Power>();
                if (powerProps != null) SetBasePowerConsumption(powerProps, LuminousPigmentSettings.pressPower);
            }

            if (recipe != null)
            {
                recipe.workAmount = LuminousPigmentSettings.pressWorkAmount;
                if (deepfire != null && recipe.products != null)
                {
                    ThingDefCountClass entry = recipe.products.Find(p => p.thingDef == deepfire);
                    if (entry != null) entry.count = LuminousPigmentSettings.pressYield;
                }
            }

            if (deepfire != null)
            {
                deepfire.SetStatBaseValue(StatDefOf.MarketValue, LuminousPigmentSettings.deepfireMarketValue);
                CompProperties_Glower glowProps = deepfire.GetCompProperties<CompProperties_Glower>();
                if (glowProps != null)
                {
                    glowProps.glowRadius = LuminousPigmentSettings.deepfireStackGlows ? 1.5f : 0f;
                }
            }

            if (tank != null)
            {
                tank.designationCategory = LuminousPigmentSettings.glowTankEnabled
                    ? DesignationCategoryDefOf.Production
                    : null;
                CompProperties_Power tankPowerProps = tank.GetCompProperties<CompProperties_Power>();
                if (tankPowerProps != null) SetBasePowerConsumption(tankPowerProps, LuminousPigmentSettings.tankPower);
            }

            if (crowncarpetCultured != null)
            {
                crowncarpetCultured.plant.growDays = LuminousPigmentSettings.tankGrowDays;
                crowncarpetCultured.plant.harvestYield = LuminousPigmentSettings.tankYield;
            }

            RefreshBuildMenu();
            ApplyCuisineSkillRequirements();
            ApplyCuisineRecipeVisibility();
            ApplyStatusThoughtNumbers();
            ApplyStatusMoodScale();
            ApplyClusterBlockToMaps();
        }

        // The architect menu is NOT derived from BuildableDef.designationCategory at draw time:
        // DesignationCategoryDef builds its designator list once (private ResolveDesignators) and
        // draws that cache. Nulling or restoring designationCategory above therefore changed the
        // def but not the menu until the next launch, contradicting the setting's tooltip. Rebuild
        // the Production list whenever a game is running; before that the category resolves itself
        // after startup and reads the already-applied field.
        static void RefreshBuildMenu()
        {
            if (Current.ProgramState != ProgramState.Playing) return;
            try
            {
                MethodInfo resolve = typeof(DesignationCategoryDef).GetMethod("ResolveDesignators",
                    BindingFlags.Instance | BindingFlags.NonPublic);
                if (resolve == null)
                {
                    Log.Warning("[LuminousPigment] DesignationCategoryDef.ResolveDesignators not found; " +
                                "GlowTank/press build-menu toggles apply on next launch.");
                    return;
                }
                resolve.Invoke(DesignationCategoryDefOf.Production, null);
            }
            catch (System.Exception e)
            {
                Log.Warning("[LuminousPigment] could not refresh the build menu: " + e.Message);
            }
        }

        // clusterBlock's block indices are keyed off the block size, so a
        // live change leaves every map's existing cluster bookkeeping stale
        // (RM_MapComponent_DeepfireLights.Clusters.cs's own comment). Rebuild
        // every loaded map's clustering from scratch on every apply --
        // ApplySettings() already runs at startup (LongEventHandler) and on
        // every settings-window close (WriteSettings), so a menu-only visit
        // with no slider touched also pays this cost; that is cheap (a full
        // map scan, not per tick) and correctness-safe either way.
        private static void ApplyClusterBlockToMaps()
        {
            if (Current.Game == null || Find.Maps == null) return;
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                MapComponent_DeepfireLights.Get(maps[i])?.RebuildAllClustering();
            }
        }

        // The 14 steered recipes' skillRequirements (Cooking) track
        // steerMinSkill / vermilionMinSkill live -- spec §7 lists both as
        // Mod Settings, not fixed def numbers.
        private static readonly string[] SteeredRecipeDefNames =
        {
            "RM_MealDeepfire_Skin", "RM_MealDeepfire_Eyes", "RM_MealDeepfire_Cranial",
            "RM_MealDeepfire_Neural", "RM_MealDeepfire_Mouth", "RM_MealDeepfire_Products",
            "RM_MealDeepfire_Blood", "RM_MealDeepfire_Marrow", "RM_MealDeepfire_Hair",
            "RM_MealDeepfire_Gut", "RM_MealDeepfire_Nerves", "RM_MealDeepfire_Pulse",
            "RM_MealDeepfire_Lungs",
        };

        private static readonly string[] AllDeepfireRecipeDefNames =
        {
            "RM_MealDeepfirePlain",
            "RM_MealDeepfire_Skin", "RM_MealDeepfire_Eyes", "RM_MealDeepfire_Cranial",
            "RM_MealDeepfire_Neural", "RM_MealDeepfire_Mouth", "RM_MealDeepfire_Products",
            "RM_MealDeepfire_Blood", "RM_MealDeepfire_Marrow", "RM_MealDeepfire_Hair",
            "RM_MealDeepfire_Gut", "RM_MealDeepfire_Nerves", "RM_MealDeepfire_Pulse",
            "RM_MealDeepfire_Lungs", "RM_MealDeepfire_Vermilion",
        };

        private static void ApplyCuisineSkillRequirements()
        {
            foreach (string defName in SteeredRecipeDefNames)
            {
                SetCookingRequirement(defName, LuminousPigmentSettings.steerMinSkill);
            }
            SetCookingRequirement("RM_MealDeepfire_Vermilion", LuminousPigmentSettings.vermilionMinSkill);
        }

        private static void SetCookingRequirement(string recipeDefName, int level)
        {
            RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(recipeDefName);
            SkillRequirement req = recipe?.skillRequirements?.Find(r => r.skill == SkillDefOf.Cooking);
            if (req != null) req.minLevel = level;
        }

        // Spec §7: "cuisineEnabled ... all recipes hidden when off". A
        // RecipeDef has no visibility flag of its own -- vanilla wires a
        // meal recipe to a bench purely by listing it on the bench's
        // <recipes> (RimSage-verified, no recipeUsers field exists), so
        // toggling membership in that list IS the real, standing-rule-
        // compliant gate.
        private static void ApplyCuisineRecipeVisibility()
        {
            // LP-1: every bench that cooks fine meals (vanilla stoves, the Stillsand solar oven, any mod's),
            // found by the CookMealFine recipe it carries, not a hand-kept pair of names.
            RecipeDef fine = DefDatabase<RecipeDef>.GetNamedSilentFail("CookMealFine");
            if (fine == null) return;
            List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
            for (int i = 0; i < all.Count; i++)
            {
                ThingDef bench = all[i];
                if (bench.recipes != null && bench.recipes.Contains(fine)) ApplyCuisineRecipeVisibilityTo(bench);
            }
        }

        private static void ApplyCuisineRecipeVisibilityTo(ThingDef stove)
        {
            if (stove == null) return;
            if (stove.recipes == null) stove.recipes = new List<RecipeDef>();

            foreach (string defName in AllDeepfireRecipeDefNames)
            {
                RecipeDef recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(defName);
                if (recipe == null) continue;
                bool present = stove.recipes.Contains(recipe);
                if (LuminousPigmentSettings.cuisineEnabled && !present)
                {
                    stove.recipes.Add(recipe);
                }
                else if (!LuminousPigmentSettings.cuisineEnabled && present)
                {
                    stove.recipes.Remove(recipe);
                }
            }
        }

        // opinionAboveStation is the one status number baked into a def
        // (RM_WearsAboveStation's single stage) rather than read live by
        // SumptuaryUtility -- same reapply-at-startup shape as
        // deepfireMarketValue above.
        private static void ApplyStatusThoughtNumbers()
        {
            ThoughtDef aboveStation = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_WearsAboveStation");
            if (aboveStation != null && aboveStation.stages.Count > 0)
            {
                aboveStation.stages[0].baseOpinionOffset = LuminousPigmentSettings.opinionAboveStation;
            }
        }

        // DEEPFIRE_MOD_SETTINGS_1, spec §7 "moodScale ... multiplies every
        // thought stage". A ThoughtDef stage's baseMoodEffect is baked into
        // the def at load and read straight off it whenever mood is summed
        // (RimSage-verified: ThoughtWorker only picks a STAGE, it carries no
        // multiplier of its own) -- same shape as opinionAboveStation below,
        // just per-stage. Only mood thoughts are scaled; RM_WearsAboveStation
        // is opinion-based and already has its own dedicated setting.
        private static readonly float[] TitledMoodBase = { 3f, 5f, 8f };
        private static readonly float[] CommonMoodBase = { 1f, 2f, 3f };
        private static readonly float[] SawCommonerMoodBase = { -3f };
        private static readonly float[] BedroomMoodBase = { 4f, 6f };

        private static void ApplyStatusMoodScale()
        {
            ApplyMoodScaleTo("RM_WearingDeepfireTitled", TitledMoodBase);
            ApplyMoodScaleTo("RM_WearingDeepfireCommon", CommonMoodBase);
            ApplyMoodScaleTo("RM_SawCommonerInDeepfire", SawCommonerMoodBase);
            ApplyMoodScaleTo("RM_DeepfireBedroom", BedroomMoodBase);
        }

        private static void ApplyMoodScaleTo(string defName, float[] baseValues)
        {
            ThoughtDef def = DefDatabase<ThoughtDef>.GetNamedSilentFail(defName);
            if (def?.stages == null) return;
            for (int i = 0; i < def.stages.Count && i < baseValues.Length; i++)
            {
                if (def.stages[i] != null)
                {
                    def.stages[i].baseMoodEffect = baseValues[i] * LuminousPigmentSettings.moodScale;
                }
            }
        }

        // CompProperties_Power.basePowerConsumption is private with no public
        // setter (RimSage-verified) -- reflection is the only route to a
        // live-tunable power draw without patching the property's getter.
        private static readonly FieldInfo BasePowerConsumptionField =
            typeof(CompProperties_Power).GetField("basePowerConsumption",
                BindingFlags.NonPublic | BindingFlags.Instance);

        private static void SetBasePowerConsumption(CompProperties_Power props, float watts)
        {
            BasePowerConsumptionField?.SetValue(props, watts);
        }
    }
}
