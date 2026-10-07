using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1 (design §3 "Seeding"). One row of the seed rule
    /// table: when a settlement's tags match, each target bucket's starting
    /// multiplier is drawn (deterministically, from the tile and key) from
    /// <see cref="RM_BazaarSeedTarget.multiplier"/>. Several matching rules
    /// on one key multiply; the result is clamped to the economy band.
    ///
    /// Tags come from <see cref="RM_BazaarTags"/>: <c>biome:X</c>,
    /// <c>climate:arid</c>/<c>climate:hot</c>/<c>climate:cold</c>,
    /// <c>liquid:X</c> (FlowWorks' authored liquid tags on the tile or its
    /// neighbours, when FlowWorks is loaded), <c>faction:X</c>, plus anything
    /// a registered provider (RimUtinni settlement tags) adds.
    /// </summary>
    public class RM_BazaarSeedRuleDef : Def
    {
        /// <summary>Every one of these must be present.</summary>
        public List<string> requiredTags;

        /// <summary>At least one of these must be present (ignored if empty).</summary>
        public List<string> anyTags;

        public List<RM_BazaarSeedTarget> targets;

        public bool Matches(HashSet<string> tags)
        {
            if (tags == null) return false;
            if (requiredTags != null)
            {
                for (int i = 0; i < requiredTags.Count; i++)
                {
                    if (!tags.Contains(requiredTags[i])) return false;
                }
            }
            if (!anyTags.NullOrEmpty())
            {
                for (int i = 0; i < anyTags.Count; i++)
                {
                    if (tags.Contains(anyTags[i])) return true;
                }
                return false;
            }
            return !requiredTags.NullOrEmpty();
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (requiredTags.NullOrEmpty() && anyTags.NullOrEmpty())
                yield return defName + ": needs requiredTags or anyTags, or it would match nothing.";
            if (targets.NullOrEmpty())
                yield return defName + ": has no targets.";
            else
            {
                for (int i = 0; i < targets.Count; i++)
                {
                    foreach (string e in targets[i].ConfigErrors()) yield return defName + " target " + i + ": " + e;
                }
            }
        }
    }

    /// <summary>
    /// One bucket a rule seeds. Exactly one of thingDef / tradeTag / category.
    /// <c>thingDef</c> is a defName STRING, resolved at use, so a rule may
    /// name another mod's item (FlowWorks' water barrels) without a
    /// cross-reference error when that mod is absent — the rule simply seeds
    /// a bucket nothing will ever look up.
    /// </summary>
    public class RM_BazaarSeedTarget
    {
        public string thingDef;
        public string tradeTag;
        public ThingCategoryDef category;
        public FloatRange multiplier = FloatRange.One;

        public string Key
        {
            get
            {
                if (!thingDef.NullOrEmpty()) return RM_BazaarPriceKeys.DefKey(thingDef);
                if (!tradeTag.NullOrEmpty()) return RM_BazaarPriceKeys.TagKey(tradeTag);
                if (category != null) return RM_BazaarPriceKeys.CategoryKey(category.defName);
                return null;
            }
        }

        public IEnumerable<string> ConfigErrors()
        {
            int set = (thingDef.NullOrEmpty() ? 0 : 1) + (tradeTag.NullOrEmpty() ? 0 : 1) + (category == null ? 0 : 1);
            if (set != 1) yield return "exactly one of thingDef, tradeTag, category must be set";
            if (multiplier.min <= 0f || multiplier.max < multiplier.min)
                yield return "multiplier range must be positive and min <= max";
            if (multiplier.max > RM_BazaarEconomy.BandMax || multiplier.min < RM_BazaarEconomy.BandMin)
                yield return "multiplier range outside the ×" + RM_BazaarEconomy.BandMin + "–×" + RM_BazaarEconomy.BandMax + " band";
        }
    }
}
