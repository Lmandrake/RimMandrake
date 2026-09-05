using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1. design/Jawa/divine_satiation_engine.md:
    // "Complete a high-volume trade -> Mob'Unloo (large)" (§ trade/debt/bonds).
    // Volume-scaling the magnitude needs TradeDeal's internal currency total,
    // which TryExecute does not expose to a caller -- a flat Medium for any
    // completed trade is a deliberate first-pass simplification, matching
    // EventMagnitude's own "UNTUNED, first-pass ordering" status.
    //
    // Verified against decompiled source (RimSage): `TradeDeal.TryExecute(out
    // bool actuallyTraded)` is the single choke point both the normal trade
    // path and the gift-mode path funnel through; `actuallyTraded` is false
    // when the dialog closed with nothing exchanged, which this patch must
    // not count as a completed trade.
    [HarmonyPatch(typeof(TradeDeal), nameof(TradeDeal.TryExecute))]
    public static class Patch_TradeCompleted
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, bool actuallyTraded)
        {
            if (!__result || !actuallyTraded) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.MobUnloo, EventMagnitude.Medium, "trade completed");
        }
    }
}
