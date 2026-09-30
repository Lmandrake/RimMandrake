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
    }
}
