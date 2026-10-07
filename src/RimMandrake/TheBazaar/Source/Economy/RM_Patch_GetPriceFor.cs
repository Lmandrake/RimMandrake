using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_PRICE_ENGINE_1 — design §2 "Session plumbing". The engine's ONE
    /// write into the game, and it is read-side: a postfix on the virtual
    /// <c>Tradeable.GetPriceFor(TradeAction)</c> (RimSage-verified 1.6
    /// signature). Vanilla <c>TradeDeal</c> execution reads prices through
    /// this method, so a multiplied price is the real price at execution with
    /// no rewrite of trade execution.
    ///
    /// Guard order, cheapest first. Outside a Bazaar window the very first
    /// check (<see cref="RM_BazaarSession.Current"/> == null) returns, so for
    /// every vanilla caller — wealth, caravan value, gift goodwill — this is
    /// one static null test and nothing else.
    ///
    /// Not hooked, on purpose: MarketValue, any StatWorker, TradeUtility.
    /// GetPricePlayerBuy/Sell (Droidworks' protocol-droid advantage lives
    /// there; composing on GetPriceFor multiplies on top of it rather than
    /// fighting it).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_Patch_GetPriceFor
    {
        public const string HarmonyId = "mandrake.rm.bazaar";

        static RM_Patch_GetPriceFor()
        {
            try
            {
                Harmony harmony = new Harmony(HarmonyId);
                var target = AccessTools.Method(typeof(Tradeable), nameof(Tradeable.GetPriceFor), new[] { typeof(TradeAction) });
                if (target == null)
                {
                    Log.Error("[The Bazaar] Tradeable.GetPriceFor(TradeAction) not found - settlement prices disabled, "
                        + "trade stays vanilla.");
                    return;
                }
                harmony.Patch(target, postfix: new HarmonyMethod(typeof(RM_Patch_GetPriceFor), nameof(Postfix)));
            }
            catch (Exception ex)
            {
                Log.Error("[The Bazaar] Failed to patch Tradeable.GetPriceFor - trade stays vanilla. " + ex);
            }
        }

        public static void Postfix(Tradeable __instance, TradeAction action, ref float __result)
        {
            RM_BazaarSession session = RM_BazaarSession.Current;
            if (session == null) return;
            if (!RM_BazaarSettings.economyEnabled) return;
            // Gifts are valued for goodwill, not traded; non-silver (favor) trades are royalty's own scale.
            if (!TradeSession.Active || TradeSession.giftMode || session.giftsOnly) return;
            if (TradeSession.TradeCurrency != TradeCurrency.Silver) return;
            if (__instance == null || __instance.IsCurrency) return;

            float m = session.MultiplierFor(__instance.ThingDef);
            if (m == 1f) return;
            __result = Mathf.Max(__result * m, TradeUtility.MinimumBuyPrice);
            if (__result > 99.5f) __result = Mathf.Round(__result);
        }
    }
}
