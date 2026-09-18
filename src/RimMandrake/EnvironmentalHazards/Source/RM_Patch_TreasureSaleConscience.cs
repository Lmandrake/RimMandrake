using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, owner card 6. The trade seam for
    // RM_TreasureConscienceDef.
    //
    // SEAM, READ THIS PASS FROM THE 1.6 SOURCE INDEX (RimSage,
    // RimWorld/TradeDeal.cs lines 150-221):
    //
    //     public bool TryExecute(out bool actuallyTraded)
    //     ...
    //     foreach (Tradeable tradeable in tradeables) {
    //         if (tradeable.ActionToDo != TradeAction.None) actuallyTraded = true;
    //         if (tradeable.ActionToDo == TradeAction.PlayerSells) num += ...;
    //         tradeable.ResolveTrade();
    //     }
    //     Reset();
    //
    // TradeDeal.TryExecute is the ONE choke point every ordinary sale goes
    // through — the settlement trade dialog, an orbital trade beacon deal
    // and a visiting caravan's trader all resolve here. Two facts decide
    // the patch shape:
    //
    //   1. What was sold is only legible BEFORE the loop: ResolveTrade()
    //      moves the things and Reset() then clears every CountToTransfer,
    //      so a postfix alone sees an empty deal. Hence a PREFIX that only
    //      READS the deal into a thread-static scratch list.
    //   2. Whether the sale actually happened is only legible AFTER: the
    //      method returns false (and trades nothing) when the colony cannot
    //      afford the deal, and `actuallyTraded` is false for an empty one.
    //      Hence a POSTFIX that fires the thought only on
    //      __result && actuallyTraded.
    //
    // Giving in the prefix would hand the colony a guilt memory for a deal
    // the "cannot afford" branch then refused. Giving in the postfix from
    // the prefix's own snapshot is the only correct combination.
    //
    // Gift mode (TradeSession.giftMode) returns early from a different
    // branch above — giving a treasure away is not selling it, and card 6's
    // wording is about selling, so the prefix records nothing in gift mode.
    //
    // Nothing here is content: which defs are treasures and which hediffs
    // are symbionts is entirely RM_TreasureConscienceDef data.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_Patch_TreasureSaleConscience
    {
        // tag -> units sold in the deal currently resolving. Cleared by the
        // postfix, and again by the prefix, so a patch that throws mid-deal
        // cannot leak a count into the next one.
        private static readonly Dictionary<string, int> SoldByTag = new Dictionary<string, int>();

        static RM_Patch_TreasureSaleConscience()
        {
            MethodBase target = AccessTools.Method(typeof(TradeDeal), nameof(TradeDeal.TryExecute));
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] treasure-sale-conscience: TradeDeal.TryExecute not "
                    + "found — rule NOT armed. The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                Harmony harmony = new Harmony("mandrake.rm.environmentalhazards");
                harmony.Patch(target,
                    prefix: new HarmonyMethod(typeof(RM_Patch_TreasureSaleConscience), nameof(TryExecute_Prefix)),
                    postfix: new HarmonyMethod(typeof(RM_Patch_TreasureSaleConscience), nameof(TryExecute_Postfix)));
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] treasure-sale-conscience: patch failed, rule NOT armed. " + e);
            }
        }

        public static void TryExecute_Prefix(TradeDeal __instance)
        {
            SoldByTag.Clear();

            if (!RM_EnvironmentalHazardsSettings.treasureConscienceEnabled)
            {
                return;
            }

            if (TradeSession.giftMode)
            {
                return; // a gift is not a sale — card 6 is about selling
            }

            try
            {
                foreach (Tradeable tradeable in __instance.AllTradeables)
                {
                    if (tradeable == null || tradeable.ActionToDo != TradeAction.PlayerSells)
                    {
                        continue;
                    }

                    ThingDef def = tradeable.ThingDef;
                    if (def == null)
                    {
                        continue;
                    }

                    RM_TreasureMarkerExtension ext = def.GetModExtension<RM_TreasureMarkerExtension>();
                    if (ext == null || ext.treasureTag.NullOrEmpty())
                    {
                        continue;
                    }

                    // CountToTransfer is negative for a player sale
                    // (PositiveCountDirection is Source); the magnitude is
                    // what left the colony.
                    int count = Math.Abs(tradeable.CountToTransfer);
                    if (count <= 0)
                    {
                        continue;
                    }

                    SoldByTag.TryGetValue(ext.treasureTag, out int running);
                    SoldByTag[ext.treasureTag] = running + count;
                }
            }
            catch (Exception e)
            {
                SoldByTag.Clear();
                Log.Error("[RM EnvironmentalHazards] treasure-sale-conscience: failed reading the deal; "
                    + "no conscience applied to this trade. " + e);
            }
        }

        public static void TryExecute_Postfix(bool __result, ref bool actuallyTraded)
        {
            if (SoldByTag.Count == 0)
            {
                return;
            }

            // Snapshot and clear first: nothing below may leave state behind
            // for the next deal, whatever it throws.
            Dictionary<string, int> sold = new Dictionary<string, int>(SoldByTag);
            SoldByTag.Clear();

            if (!__result || !actuallyTraded)
            {
                return; // refused deal (e.g. colony cannot afford it) — nothing left the colony
            }

            try
            {
                List<RM_TreasureConscienceDef> consciences = DefDatabase<RM_TreasureConscienceDef>.AllDefsListForReading;
                for (int i = 0; i < consciences.Count; i++)
                {
                    RM_TreasureConscienceDef conscience = consciences[i];
                    if (conscience.thought == null || conscience.treasureTag.NullOrEmpty())
                    {
                        continue;
                    }

                    if (!sold.TryGetValue(conscience.treasureTag, out int count) || count < conscience.minCountSold)
                    {
                        continue;
                    }

                    ApplyConscience(conscience);
                }
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] treasure-sale-conscience: failed applying the "
                    + "conscience thought. " + e);
            }
        }

        private static void ApplyConscience(RM_TreasureConscienceDef conscience)
        {
            List<Pawn> colonists = PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_FreeColonists;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn pawn = colonists[i];
                if (pawn == null || pawn.Dead || pawn.needs?.mood?.thoughts?.memories == null)
                {
                    continue;
                }

                if (!conscience.affectsAllColonists && pawn.Map == null)
                {
                    continue;
                }

                if (!CarriesAny(pawn, conscience.carrierHediffs))
                {
                    continue;
                }

                pawn.needs.mood.thoughts.memories.TryGainMemory(conscience.thought);
            }
        }

        private static bool CarriesAny(Pawn pawn, List<HediffDef> hediffs)
        {
            if (hediffs == null || pawn.health?.hediffSet == null)
            {
                return false;
            }

            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i] != null && pawn.health.hediffSet.HasHediff(hediffs[i]))
                {
                    return true;
                }
            }

            return false;
        }
    }
}
