using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1. What a bottle, bucket or barrel is made of, as far as
    /// holding a liquid is concerned. "Glass" is any stone (the stone only tints it); "Unknown" is a
    /// container with no stuff at all (an adopted vanilla item such as Chemfuel), which holds anything
    /// at its base capacity.</summary>
    public enum RM_ContainerMaterial
    {
        Unknown,
        Leather,
        Glass,
        Metal,
        Wood,
        Plasteel,
    }

    /// <summary>Why a container refuses a liquid. None = it holds it.</summary>
    public enum RM_HoldRefusal
    {
        None,
        Hot,
        Acid,
    }

    /// <summary>One material's rule on one container family -- the def field the owner's ruling asked
    /// for (decision taken by question card 2026-10-06 23:45: "Material changes what a container can
    /// hold -- full rules incl. capacity"). Authored per container family in
    /// RM_ContainerMaterialsExtension on RM_BottleItemBase / RM_BucketItemBase / RM_BarrelItemBase;
    /// the shipped numbers are documented there and asserted by the FlowWorks selftest.</summary>
    public class RM_ContainerMaterialRule
    {
        public RM_ContainerMaterial material = RM_ContainerMaterial.Unknown;

        /// <summary>Multiplies the liquid's units per container of this size (LiquidBottledForm.UnitsFor).</summary>
        public float capacityFactor = 1f;

        /// <summary>False = refuses hot liquids (LiquidDef.hot, e.g. boiling water).</summary>
        public bool holdsHot = true;

        /// <summary>False = refuses acid (LiquidDef.IsAcid).</summary>
        public bool holdsAcid = true;
    }

    /// <summary>Verse-free rules, compiled straight into the offline selftest.</summary>
    public static class RM_ContainerMaterialMath
    {
        /// <summary>Plasteel is checked by defName before the categories because vanilla files it under
        /// Metallic; leather before stone/metal/wood in case a modded stuff carries two categories.</summary>
        public static RM_ContainerMaterial Classify(string stuffDefName, IEnumerable<string> stuffCategories)
        {
            if (stuffDefName == null)
            {
                return RM_ContainerMaterial.Unknown;
            }
            if (stuffDefName == "Plasteel")
            {
                return RM_ContainerMaterial.Plasteel;
            }
            bool leathery = false, stony = false, metallic = false, woody = false;
            if (stuffCategories != null)
            {
                foreach (string c in stuffCategories)
                {
                    if (c == "Leathery") leathery = true;
                    else if (c == "Stony") stony = true;
                    else if (c == "Metallic") metallic = true;
                    else if (c == "Woody") woody = true;
                }
            }
            if (leathery) return RM_ContainerMaterial.Leather;
            if (stony) return RM_ContainerMaterial.Glass;
            if (metallic) return RM_ContainerMaterial.Metal;
            if (woody) return RM_ContainerMaterial.Wood;
            return RM_ContainerMaterial.Unknown;
        }

        /// <summary>Acid = corrodes apparel, burns with acid, or pH 4 and below.</summary>
        public static bool IsAcid(float pH, bool corrodesApparel, bool acidBurnDamage)
        {
            return corrodesApparel || acidBurnDamage || pH <= 4f;
        }

        /// <summary>Hot is checked first: the reason a player reads should name the most obvious hazard.
        /// A null rule (a material the def does not list) holds anything.</summary>
        public static RM_HoldRefusal CanHold(RM_ContainerMaterialRule rule, bool liquidHot, bool liquidAcid)
        {
            if (rule == null)
            {
                return RM_HoldRefusal.None;
            }
            if (liquidHot && !rule.holdsHot)
            {
                return RM_HoldRefusal.Hot;
            }
            if (liquidAcid && !rule.holdsAcid)
            {
                return RM_HoldRefusal.Acid;
            }
            return RM_HoldRefusal.None;
        }

        /// <summary>Units a container of this material holds: the liquid's base units for the size,
        /// times the factor, rounded half away from zero, never below 1 while the base is above 0.
        /// A 1-unit bottle therefore only changes at a factor of 1.5 or more.</summary>
        public static int ScaledUnits(int baseUnits, float capacityFactor)
        {
            if (baseUnits <= 0)
            {
                return 0;
            }
            int scaled = (int)Math.Round(baseUnits * capacityFactor, MidpointRounding.AwayFromZero);
            return scaled < 1 ? 1 : scaled;
        }

        /// <summary>Ruling 3: swap the first "stone-made" phrase in a label for the "glass-made" one
        /// ("granite empty bottle" -> "glass empty bottle", keeping any prefix/suffix such as a
        /// health percentage). Label unchanged when the phrase is absent.</summary>
        public static string RelabelAsGlass(string label, string stoneForm, string glassForm)
        {
            if (string.IsNullOrEmpty(label) || string.IsNullOrEmpty(stoneForm) || glassForm == null)
            {
                return label;
            }
            int at = label.IndexOf(stoneForm, StringComparison.Ordinal);
            return at < 0 ? label : label.Substring(0, at) + glassForm + label.Substring(at + stoneForm.Length);
        }

        public static RM_ContainerMaterialRule RuleFor(List<RM_ContainerMaterialRule> rules, RM_ContainerMaterial material)
        {
            if (rules == null)
            {
                return null;
            }
            for (int i = 0; i < rules.Count; i++)
            {
                if (rules[i] != null && rules[i].material == material)
                {
                    return rules[i];
                }
            }
            return null;
        }
    }
}
