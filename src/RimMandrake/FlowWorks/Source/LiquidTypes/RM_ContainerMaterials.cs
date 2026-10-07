using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1, ruling 2 (decision taken by question card 2026-10-06
    /// 23:45): material changes what a container can hold, capacity included. One per container family,
    /// on the abstract ItemBase so every empty/filled/dirty child inherits it (RimWorld merges a child's
    /// modExtensions list onto its parent's). The shipped numbers live in RM_LiquidBottles_Base.xml.</summary>
    public class RM_ContainerMaterialsExtension : DefModExtension
    {
        public List<RM_ContainerMaterialRule> materials;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }
            if (materials == null)
            {
                yield break;
            }
            for (int i = 0; i < materials.Count; i++)
            {
                if (materials[i] != null && materials[i].capacityFactor <= 0f)
                {
                    yield return "RM_ContainerMaterialsExtension: capacityFactor for " + materials[i].material
                        + " must be > 0.";
                }
            }
        }
    }

    /// <summary>The one place every fill/pour/drain site asks "can this container hold this liquid, and
    /// how much of it". Reads the container's Stuff and its def's RM_ContainerMaterialsExtension.</summary>
    public static class RM_ContainerMaterials
    {
        public static RM_ContainerMaterial MaterialOf(ThingDef stuff)
        {
            if (stuff == null)
            {
                return RM_ContainerMaterial.Unknown;
            }
            List<string> cats = null;
            if (stuff.stuffProps?.categories != null)
            {
                cats = new List<string>(stuff.stuffProps.categories.Count);
                for (int i = 0; i < stuff.stuffProps.categories.Count; i++)
                {
                    cats.Add(stuff.stuffProps.categories[i].defName);
                }
            }
            return RM_ContainerMaterialMath.Classify(stuff.defName, cats);
        }

        public static RM_ContainerMaterialRule RuleFor(Thing container)
        {
            if (container == null)
            {
                return null;
            }
            RM_ContainerMaterialsExtension ext = container.def.GetModExtension<RM_ContainerMaterialsExtension>();
            return RM_ContainerMaterialMath.RuleFor(ext?.materials, MaterialOf(container.Stuff));
        }

        public static RM_HoldRefusal Refusal(Thing container, LiquidDef liquid)
        {
            if (liquid == null)
            {
                return RM_HoldRefusal.None;
            }
            return RM_ContainerMaterialMath.CanHold(RuleFor(container), liquid.hot, liquid.IsAcid);
        }

        public static bool CanHold(Thing container, LiquidDef liquid)
        {
            return Refusal(container, liquid) == RM_HoldRefusal.None;
        }

        /// <summary>Player-readable reason, for JobFailReason (float menu) and the job's own message.
        /// Null when the container holds the liquid.</summary>
        public static string RefusalReason(Thing container, LiquidDef liquid)
        {
            RM_HoldRefusal refusal = Refusal(container, liquid);
            if (refusal == RM_HoldRefusal.None)
            {
                return null;
            }
            string material = ("RM_ContainerMaterial_" + MaterialOf(container.Stuff)).Translate();
            return (refusal == RM_HoldRefusal.Hot ? "RM_ContainerRefusesHot" : "RM_ContainerRefusesAcid")
                .Translate(material, liquid.label);
        }

        /// <summary>Units of <paramref name="liquid"/> this container moves at its size, scaled by its
        /// material's capacityFactor. Replaces a bare LiquidDef.UnitsFor at every tank site.</summary>
        public static int UnitsIn(Thing container, LiquidDef liquid, RM_ContainerSize size)
        {
            if (liquid == null)
            {
                return 0;
            }
            RM_ContainerMaterialRule rule = RuleFor(container);
            return RM_ContainerMaterialMath.ScaledUnits(liquid.UnitsFor(size), rule?.capacityFactor ?? 1f);
        }
    }
}
