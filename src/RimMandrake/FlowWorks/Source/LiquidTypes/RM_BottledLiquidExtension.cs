using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    // LIQUID_BOTTLE_LOOP_1. The bottle-side identity tag: which LiquidDef a
    // given bottle/bucket/barrel ThingDef holds, and whether it is the dirty
    // (post-use, pre-wash) variant of that same item.
    //
    // This is the ONE piece of per-liquid data a bottle ThingDef needs to
    // carry. It exists so the fill/use/dirty/wash job loop (owed — see the
    // item's own notes; no JobDriver/WorkGiver ships this pass) can work
    // GENERICALLY off any bottle ThingDef by reading this extension, rather
    // than needing one JobDriver subclass per liquid. That is also what
    // keeps a bottle "drinkable-agnostic" per the item's own watch-out: DBH
    // registration (LIQUID_THIRST_CHAIN_1) is a separate concern that reads
    // <see cref="liquid"/> too, never a base class a bottle must inherit.
    //
    // <see cref="LiquidTypes.LiquidDef.bottled"/> (LiquidBottledForm) is the
    // liquid-to-bottle direction (the registry row names its bottle
    // ThingDef); this extension is the bottle-to-liquid direction (the item
    // names its own content), so either side of the loop can resolve the
    // pairing without a scan.
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.FlowWorks.LiquidTypes.RM_BottledLiquidExtension">
    //       <liquid>RM_Liquid_FreshWater</liquid>
    //     </li>
    //   </modExtensions>
    public class RM_BottledLiquidExtension : DefModExtension
    {
        /// <summary>Which liquid this bottle/bucket/barrel currently holds.
        /// Null on <c>RM_BottleEmpty</c> and on <c>RM_BottleDirty</c> — an
        /// empty or dirty container has no content, it has a state.</summary>
        public LiquidDef liquid;

        /// <summary>True on the dirty (used, unwashed) variant of a filled
        /// container. A dirty bottle carries no <see cref="liquid"/> — the
        /// content was consumed; what is left to wash off is residue, not a
        /// liquid identity — so <c>dirty</c> and <c>liquid</c> are never both
        /// set together, per <see cref="ConfigErrors"/>.</summary>
        public bool dirty;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (dirty && liquid != null)
            {
                yield return "RM_BottledLiquidExtension: dirty is true but liquid is also set -- "
                    + "a dirty bottle has no content, only a state to wash off.";
            }
        }
    }
}
