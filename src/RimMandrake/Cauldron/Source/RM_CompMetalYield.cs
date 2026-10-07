using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // CAULDRON_TREE_METAL_YIELD_1. The metal-infused old-growth trees (twisting
    // thornwood, martyr tree) drop a growth-scaled metal beside their wood.
    //
    // SEAM: ThingComp.GetAdditionalHarvestYield(), which JobDriver_PlantWork
    // calls on every comp of a plant that is HarvestableNow, right after the main
    // harvest, only when the harvest did not fail. No Harmony patch and no
    // ticking, so this mod's "no Harmony reference" stance holds and the Plant
    // TickLong-only trap never applies (nothing here ticks).
    //
    // SCALING: count lerps countAtMinGrowth -> countAtFullGrowth over the plant's
    // growth from def.plant.harvestMinGrowth to 1, then times the mod-settings
    // factor, then random-rounded so a small factor still pays out on average.
    // A young trunk yields a trace; a full-grown one yields the lode.
    public class RM_CompProperties_MetalYield : CompProperties
    {
        public ThingDef metalDef;
        public float countAtMinGrowth = 1f;
        public float countAtFullGrowth = 6f;

        public RM_CompProperties_MetalYield()
        {
            compClass = typeof(RM_CompMetalYield);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (metalDef == null) yield return "RM_CompProperties_MetalYield has no metalDef";
            if (parentDef.plant == null) yield return "RM_CompProperties_MetalYield on a non-plant def";
        }
    }

    public class RM_CompMetalYield : ThingComp
    {
        private RM_CompProperties_MetalYield Props => (RM_CompProperties_MetalYield)props;

        public int MetalCountNow()
        {
            if (!RM_CauldronSettings.metalYieldEnabled) return 0;
            if (Props.metalDef == null) return 0;
            if (!(parent is RimWorld.Plant plant)) return 0;

            float min = plant.def.plant.harvestMinGrowth;
            float t = Mathf.InverseLerp(min, 1f, plant.Growth);
            float count = Mathf.Lerp(Props.countAtMinGrowth, Props.countAtFullGrowth, t)
                          * RM_CauldronSettings.metalYieldFactor;
            return GenMath.RoundRandom(count);
        }

        public override IEnumerable<ThingDefCountClass> GetAdditionalHarvestYield()
        {
            int n = MetalCountNow();
            if (n > 0) yield return new ThingDefCountClass(Props.metalDef, n);
        }

        // CAULDRON_GPT_ENRICHMENT_1 part 4 (assay forestry): the inspect pane
        // reads the trunk's value before it is cut. The grade is the EXPECTED
        // metal count right now (same lerp as MetalCountNow, no rounding)
        // as a fraction of the full-growth count.
        // TUNED: tier cut points at 1/3 and 2/3 of the full-growth lode, plus
        // "lode" only at >= 95% so the top grade means a genuinely old stand.
        // Unripe trunks (below harvestMinGrowth) read "unripe": they yield nothing.
        public float ExpectedMetalNow()
        {
            if (Props.metalDef == null || !(parent is RimWorld.Plant plant)) return 0f;
            float min = plant.def.plant.harvestMinGrowth;
            if (plant.Growth < min) return 0f;
            float t = Mathf.InverseLerp(min, 1f, plant.Growth);
            return Mathf.Lerp(Props.countAtMinGrowth, Props.countAtFullGrowth, t)
                   * RM_CauldronSettings.metalYieldFactor;
        }

        // Expected metal now as a fraction of the full-growth lode (0 while unripe). The settings factor
        // scales both sides, so it cancels. Read by the inspect grade and by the assay flecks (V3).
        public float GradeFraction()
        {
            float full = Props.countAtFullGrowth * RM_CauldronSettings.metalYieldFactor;
            return full > 0f ? ExpectedMetalNow() / full : 0f;
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_CauldronSettings.metalYieldEnabled || !RM_CauldronSettings.assayGradeEnabled) return null;
            if (Props.metalDef == null || !(parent is RimWorld.Plant plant)) return null;
            if (plant.Growth < plant.def.plant.harvestMinGrowth)
                return "Assay grade: unripe (no " + Props.metalDef.label + " yet)";

            float expected = ExpectedMetalNow();
            float frac = GradeFraction();
            string grade = frac >= 0.95f ? "lode" : frac >= 2f / 3f ? "rich" : frac >= 1f / 3f ? "fair" : "trace";
            return "Assay grade: " + grade + " (~" + expected.ToString("0.#") + " " + Props.metalDef.label + " if cut now)";
        }
    }
}
