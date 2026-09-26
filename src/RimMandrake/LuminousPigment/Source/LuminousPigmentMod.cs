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
    // The Chain (Phase 1, DEEPFIRE_PIGMENT_MOD_1) plus the three pieces of
    // DEEPFIRE_PAINT_STATUS_CUISINE_1 this build ships: Cuisine's 14
    // glow-hediff families, the Ninefold god-bridge's two wireable deltas,
    // and the sumptuary status engine's worn-goods thoughts. Painting and
    // worn-item lighting (spec §3) are NOT here -- deferred to
    // DEEPFIRE_PAINT_LIVE_VERIFY_1, which needs the spec's own live
    // proxy-glower quicktest first. Their settings ship with that follow-on;
    // a toggle for a mechanism that does not exist yet would be a stub,
    // which the standing Mod Settings rule forbids -- same reasoning also
    // keeps godDeltaIshko/godDeltaStatue and Cuisine's per-family weight
    // sliders and effectScale out of this pass (unwired numbers).
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

        // Gods (spec §7 "Gods" group) -- only the two constants this build's
        // two wired deltas actually use (dish-eaten Small, vermilion-III
        // Medium reused for Ishko's penalty).
        public static bool godsReact = true;
        public static float godDeltaLike = 3f;
        public static float godDeltaAdore = 8f;

        // Status -- the purple engine (spec §7 "Status" group)
        public static bool statusEnabled = true;
        public static int displayCap = 6;
        public static int offenceThreshold = 2;
        public static float opinionAboveStation = -15f;
        public static bool ranklessColoniesEnjoyIt = true;

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

            Scribe_Values.Look(ref statusEnabled, "statusEnabled", true);
            Scribe_Values.Look(ref displayCap, "displayCap", 6);
            Scribe_Values.Look(ref offenceThreshold, "offenceThreshold", 2);
            Scribe_Values.Look(ref opinionAboveStation, "opinionAboveStation", -15f);
            Scribe_Values.Look(ref ranklessColoniesEnjoyIt, "ranklessColoniesEnjoyIt", true);
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
            list.Label("Small reaction (a dish eaten): " + godDeltaLike.ToString("0.#"));
            godDeltaLike = list.Slider(godDeltaLike, 0f, 20f);
            list.Label("Medium reaction (the vermilion cannot be hidden): " + godDeltaAdore.ToString("0.#"));
            godDeltaAdore = list.Slider(godDeltaAdore, 0f, 30f);
            list.GapLine();

            list.Label("STATUS (the purple engine)");
            list.CheckboxLabeled("Sumptuary reactions", ref statusEnabled,
                "Off: no status thoughts from deepfire goods at all.");
            list.Label("Display score cap: " + displayCap.ToString());
            displayCap = Mathf.RoundToInt(list.Slider(displayCap, 1f, 12f));
            list.Label("Commoner display score that offends a titled pawn: " + offenceThreshold.ToString());
            offenceThreshold = Mathf.RoundToInt(list.Slider(offenceThreshold, 1f, 6f));
            list.Label("Opinion penalty for wearing above one's station: " + opinionAboveStation.ToString("0"));
            opinionAboveStation = list.Slider(opinionAboveStation, -40f, 0f);
            list.CheckboxLabeled("Colonies with no Royalty or Ideology still enjoy it", ref ranklessColoniesEnjoyIt,
                "On (default): with neither DLC active nobody can be titled, so the engine degrades " +
                "to a plain 'nice clothes' mood for everyone. Off: with neither DLC active, nobody " +
                "gets a thought at all.");

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

            ApplyCuisineSkillRequirements();
            ApplyCuisineRecipeVisibility();
            ApplyStatusThoughtNumbers();
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
            ApplyCuisineRecipeVisibilityTo(ThingDef.Named("ElectricStove"));
            ApplyCuisineRecipeVisibilityTo(ThingDef.Named("FueledStove"));
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
