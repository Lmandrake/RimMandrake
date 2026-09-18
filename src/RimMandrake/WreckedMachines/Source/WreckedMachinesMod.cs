using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WreckedMachines
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — WRECKEDMACHINES_MOD_SETTINGS_1.
    //
    // WreckedMachines shipped as pure XML (three ThingDef tiers, one
    // ResearchProjectDef, one hide-the-donor patch) with no assembly and no
    // settings screen at all — a violation of MOD_OPTIONS_RETROFIT_1's
    // every-mod-ships-settings ruling (owner, 2026-09-12) called out
    // explicitly by that item's own progress notes. The apparent conflict
    // with RAKATAN_ARCHOTECH_MACHINES_1's "pure-XML protection" was resolved
    // the same sitting it was raised: ruling 5 there REVERSES the XML-only
    // exemption outright ("Every mod ships superb Mod Settings, no
    // exceptions" wins), so this assembly is owed, not optional.
    //
    // Pattern copied from the established in-repo precedent
    // (RimMandrake/GelatinousSlime/Source/SlimeMod.cs): a ModSettings class
    // with static fields (read from anywhere, including the
    // [StaticConstructorOnStartup] patcher below, which runs before any Mod
    // instance necessarily exists), a thin Mod subclass, and
    // Listing_Standard for the window body.
    //
    // Every default below reproduces the current shipped (no-settings)
    // behaviour byte-for-byte — turning this mod's settings window off
    // changes nothing.
    //
    // None of these toggles touch worldgen or map generation: the mod places
    // no biome, terrain or map-gen worker, so none needs the "affects new
    // maps only" label MOD_OPTIONS_RETROFIT_1 requires for worldgen-affecting
    // options.
    // ════════════════════════════════════════════════════════════════════
    public class WreckedMachinesSettings : ModSettings
    {
        // Shipped default: OFF. The donor's own VFEFactory_AutomatedSmelter
        // stays hidden from the Architect menu (WreckedMachines_
        // HideDonorSmelter.xml, WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1), so
        // the wreck ladder is the only way onto the factory floor.
        public static bool allowDonorSmelter = false;

        // Shipped default: 1.0x — the recorded baseCost (2000) on
        // RM_WM_AutomatedSmelterRestoration, untouched.
        public static float researchCostFactor = 1f;

        // Shipped default: 1.0x — the recorded costList Steel/
        // ComponentIndustrial amounts on the Kludged and Repaired tiers,
        // untouched.
        public static float materialCostFactor = 1f;

        // Shipped default: OFF. Repaired still requires
        // RM_WM_AutomatedSmelterRestoration to be finished first.
        public static bool skipRestorationResearch = false;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref allowDonorSmelter, "allowDonorSmelter", false, true);
            Scribe_Values.Look(ref researchCostFactor, "researchCostFactor", 1f, true);
            Scribe_Values.Look(ref materialCostFactor, "materialCostFactor", 1f, true);
            Scribe_Values.Look(ref skipRestorationResearch, "skipRestorationResearch", false, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled(
                "Allow the original VFE automated smelter to be built",
                ref allowDonorSmelter,
                "Off (shipped default): the donor mod's own Automated Smelter is "
                + "hidden from the Architect menu, so the wreck-restoration ladder "
                + "is the only way onto the factory floor. On: the donor building "
                + "reappears in the Architect menu alongside our three tiers, "
                + "restoring the old testing arrangement. Not worldgen-affecting, "
                + "but the Architect menu caches its buttons at startup, so this "
                + "takes full effect after your next game load.");
            list.GapLine();

            list.Label("Restoration research cost: " + researchCostFactor.ToString("0.00") + "x");
            list.Label(
                "Scales the research needed to unlock the Repaired tier. 1.0x is "
                + "the shipped cost.");
            researchCostFactor = list.Slider(researchCostFactor, 0.25f, 4f);
            list.GapLine();

            list.Label("Rebuild material cost: " + materialCostFactor.ToString("0.00") + "x");
            list.Label(
                "Scales the steel and components spent stepping a wreck up to "
                + "Kludged or Repaired. 1.0x is the shipped cost.");
            materialCostFactor = list.Slider(materialCostFactor, 0.25f, 4f);
            list.GapLine();

            list.CheckboxLabeled(
                "Skip the restoration research for the Repaired tier",
                ref skipRestorationResearch,
                "Off (shipped default): stepping a wreck up to Repaired needs the "
                + "Automated Smelter Restoration research project finished first. "
                + "On: any colony can build straight to Repaired with materials "
                + "alone, no research gate.");

            list.End();
        }
    }

    public class WreckedMachinesMod : Mod
    {
        public static WreckedMachinesSettings settings;

        public WreckedMachinesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WreckedMachinesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Wrecked Machines";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            // Re-derive live def state from the settings the player just
            // closed the window with, so the number/tuning sliders take
            // effect without a restart (the Architect-menu toggle is the
            // one exception — see its tooltip above).
            WreckedMachinesPatcher.Apply();
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // WIRES THE SETTINGS ABOVE INTO THE REAL DEFS.
    //
    // Defs are fully loaded and cross-reference-resolved before any
    // [StaticConstructorOnStartup] class runs (PlayDataLoader finishes its
    // def pass before LoadedModManager.CreateModClasses / StaticConstructor-
    // OnStartup execute), so reading/writing DefDatabase entries here is
    // safe — same timing precedent as RimMandrake.GelatinousSlime.SlimeDefs.
    //
    // GetNamedSilentFail, not [DefOf]: VFEFactory_AutomatedSmelter is a hard
    // modDependency so it is always present, but silent-fail keeps this
    // patcher inert rather than log-spamming if a future load order ever
    // drops it, matching this codebase's established convention.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class WreckedMachinesPatcher
    {
        private static readonly ThingDef DonorSmelter =
            DefDatabase<ThingDef>.GetNamedSilentFail("VFEFactory_AutomatedSmelter");

        private static readonly DesignationCategoryDef FactoryCategory =
            DefDatabase<DesignationCategoryDef>.GetNamedSilentFail("VFEFactory_Factories");

        private static readonly ResearchProjectDef RestorationResearch =
            DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_WM_AutomatedSmelterRestoration");

        private static readonly ThingDef KludgedTier =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_WM_AutomatedSmelter_Kludged");

        private static readonly ThingDef RepairedTier =
            DefDatabase<ThingDef>.GetNamedSilentFail("RM_WM_AutomatedSmelter_Repaired");

        // Shipped baselines, captured once before any settings-driven edit,
        // so every Apply() re-derives its scalar from the true v1 numbers
        // instead of compounding a factor onto an already-scaled value.
        private static readonly float BaseResearchCost =
            RestorationResearch != null ? RestorationResearch.baseCost : 0f;

        private static readonly List<ResearchProjectDef> RepairedResearchPrereq =
            RepairedTier != null && RepairedTier.researchPrerequisites != null
                ? new List<ResearchProjectDef>(RepairedTier.researchPrerequisites)
                : null;

        private static readonly Dictionary<ThingDef, List<ThingDefCountClass>> BaseCosts =
            new Dictionary<ThingDef, List<ThingDefCountClass>>();

        static WreckedMachinesPatcher()
        {
            CaptureBaseCost(KludgedTier);
            CaptureBaseCost(RepairedTier);
            Apply();
        }

        private static void CaptureBaseCost(ThingDef def)
        {
            if (def == null || def.costList == null) return;
            var copy = new List<ThingDefCountClass>();
            foreach (var entry in def.costList)
                copy.Add(new ThingDefCountClass(entry.thingDef, entry.count));
            BaseCosts[def] = copy;
        }

        public static void Apply()
        {
            if (DonorSmelter != null)
            {
                DonorSmelter.designationCategory =
                    WreckedMachinesSettings.allowDonorSmelter ? FactoryCategory : null;
            }

            if (RestorationResearch != null)
            {
                RestorationResearch.baseCost =
                    Mathf.Max(1f, BaseResearchCost * WreckedMachinesSettings.researchCostFactor);
            }

            RescaleCost(KludgedTier);
            RescaleCost(RepairedTier);

            if (RepairedTier != null && RepairedResearchPrereq != null)
            {
                RepairedTier.researchPrerequisites = WreckedMachinesSettings.skipRestorationResearch
                    ? new List<ResearchProjectDef>()
                    : new List<ResearchProjectDef>(RepairedResearchPrereq);
            }
        }

        private static void RescaleCost(ThingDef def)
        {
            if (def == null || !BaseCosts.TryGetValue(def, out var baseline)) return;
            var scaled = new List<ThingDefCountClass>();
            foreach (var entry in baseline)
            {
                int count = Mathf.Max(1, Mathf.RoundToInt(entry.count * WreckedMachinesSettings.materialCostFactor));
                scaled.Add(new ThingDefCountClass(entry.thingDef, count));
            }
            def.costList = scaled;
        }
    }
}
