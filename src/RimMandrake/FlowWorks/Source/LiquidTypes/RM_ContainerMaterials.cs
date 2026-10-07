using System.Collections.Generic;
using System.Text;
using UnityEngine;
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

    /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1 rulings 3 and 4 (decisions taken by question card
    /// 2026-10-06 23:45), on every bottle/bucket/barrel via the ItemBases' comps:
    ///  3. a stone-made container is GLASS: "granite empty bottle" reads "glass empty bottle" -- the
    ///     stone only tints it (vanilla's own "ThingMadeOfStuffLabel" pattern is rebuilt with the glass
    ///     word, so it holds in any language that keeps that pattern; otherwise the label is untouched).
    ///  4. a FILLED container shows its liquid's colour (LiquidDef.color); an empty or dirty one, or a
    ///     liquid left white, falls through to vanilla's stuff colour -- the material. One Graphic: the
    ///     colour is chosen once when the Thing's graphic is built, and every fill/wash/pour already makes
    ///     a NEW Thing (RM_LiquidBottleUtility.MakeContainer), so no cached graphic ever goes stale.
    /// Plus an inspect line for what this material holds and refuses.</summary>
    public class RM_CompContainerMaterial : ThingComp
    {
        private const float WhiteEpsilon = 0.01f;

        private LiquidDef Contained => parent.def.GetModExtension<RM_BottledLiquidExtension>()?.liquid;

        public override Color? ForceColor()
        {
            LiquidDef liquid = Contained;
            if (liquid == null)
            {
                return null;
            }
            Color c = liquid.color;
            bool white = c.r > 1f - WhiteEpsilon && c.g > 1f - WhiteEpsilon && c.b > 1f - WhiteEpsilon;
            return white ? (Color?)null : c;
        }

        public override string TransformLabel(string label)
        {
            ThingDef stuff = parent.Stuff;
            if (stuff == null || label == null
                || RM_ContainerMaterials.MaterialOf(stuff) != RM_ContainerMaterial.Glass)
            {
                return label;
            }
            string stone = "ThingMadeOfStuffLabel".Translate(stuff.LabelAsStuff, parent.def.label);
            string glass = "ThingMadeOfStuffLabel".Translate("RM_ContainerMaterial_Glass".Translate(), parent.def.label);
            return RM_ContainerMaterialMath.RelabelAsGlass(label, stone, glass);
        }

        public override string CompInspectStringExtra()
        {
            RM_ContainerMaterialRule rule = RM_ContainerMaterials.RuleFor(parent);
            if (rule == null || (rule.holdsHot && rule.holdsAcid))
            {
                return null;
            }
            var sb = new StringBuilder();
            if (!rule.holdsHot)
            {
                sb.Append("RM_ContainerRefusesHotShort".Translate());
            }
            if (!rule.holdsAcid)
            {
                if (sb.Length > 0) sb.Append(", ");
                sb.Append("RM_ContainerRefusesAcidShort".Translate());
            }
            return "RM_ContainerCannotHold".Translate(sb.ToString());
        }
    }
}
