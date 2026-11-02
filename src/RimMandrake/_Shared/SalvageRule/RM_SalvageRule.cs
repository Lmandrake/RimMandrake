// THE salvage-yield rule (SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY; design/RimMandrake/mod_deepdive_industry.md section 2.3).
//
// One rule, and it is vanilla's: an item that passes Thing.Smeltable returns Thing.SmeltProducts, which is 25% (RoundRandom) of each
// non-intricate smeltable cost entry plus the def's fixed smeltProducts (decompiled 1.6, Verse/Thing.cs). Calling the engine's own
// virtual, never a copy of its arithmetic, is what keeps the vanilla electric smelter on this rule without a patch and what lets
// RSW_BeskarSmelt's postfixes apply on every path. Any path that turns a finished item back into materials calls YieldOf, and nothing
// else. Link this file and RM_SalvageRuleKernel.cs into the mod that needs it.
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Shared
{
    internal static class RM_SalvageRule
    {
        /// <summary>What salvaging this item returns, as new unspawned stacks; every unit of a stack counts. Empty when it may not be salvaged.</summary>
        public static List<Thing> YieldOf(Thing item)
        {
            var result = new List<Thing>();
            if (item?.def == null || !item.Smeltable) return result;
            var order = new List<ThingDef>();
            var totals = new Dictionary<ThingDef, int>();
            for (int unit = 0; unit < item.stackCount; unit++)
            {
                foreach (Thing product in item.SmeltProducts(1f))
                {
                    if (!totals.ContainsKey(product.def))
                    {
                        totals[product.def] = 0;
                        order.Add(product.def);
                    }
                    totals[product.def] += product.stackCount;
                }
            }
            foreach (ThingDef def in order)
            {
                foreach (int count in RM_SalvageRuleKernel.Stacks(totals[def], def.stackLimit))
                {
                    Thing stack = ThingMaker.MakeThing(def);
                    stack.stackCount = count;
                    result.Add(stack);
                }
            }
            return result;
        }

        /// <summary>Puts a yielded stack near the cell; a crowded spot never loses it.</summary>
        public static void Place(Thing stack, IntVec3 cell, Map map)
        {
            if (!GenPlace.TryPlaceThing(stack, cell, map, ThingPlaceMode.Near)) GenSpawn.Spawn(stack, cell, map);
        }

        /// <summary>The same rule for an item known only by def and stuff (a factory process keeps no Thing). The item is built to be read and never spawned.</summary>
        public static List<Thing> YieldOf(ThingDef def, ThingDef stuff)
        {
            if (def == null) return new List<Thing>();
            ThingDef madeOf = def.MadeFromStuff ? stuff ?? GenStuff.DefaultStuffFor(def) : null;
            return YieldOf(ThingMaker.MakeThing(def, madeOf));
        }
    }
}
