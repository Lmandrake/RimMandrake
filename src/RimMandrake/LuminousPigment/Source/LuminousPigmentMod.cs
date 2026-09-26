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
    // Only the Chain is here. Painting, worn-item lighting, the status
    // engine, Ninefold and Cuisine settings groups ship with that work
    // (DEEPFIRE_PAINT_STATUS_CUISINE_1) -- a toggle for a mechanism that
    // does not exist yet would be a stub, which the standing Mod Settings
    // rule forbids.
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
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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

            list.End();
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
