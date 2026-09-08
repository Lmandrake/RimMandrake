using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROID_PROTOCOL_TRADE_ADVANTAGE_1 (packet C4). Owner ruling 2,
    /// 2026-09-06: "Many traders will come with protocol droids to help them
    /// with communication and trade advantage (there should be real trade
    /// advantage to having a protocol droid with you, dangerous not to)."
    ///
    /// Same [StaticConstructorOnStartup] + static Apply(Harmony) shape
    /// Patch_ShouldHaveNeed_Power.cs documents, on its own Harmony instance so
    /// a failure here cannot take the need gate down with it.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DroidworksTradeAdvantageMod
    {
        static DroidworksTradeAdvantageMod()
        {
            var harmony = new Harmony("mandrake.rsw.droidworks.tradeadvantage");
            try
            {
                Patch_ProtocolTradeAdvantage.Apply(harmony);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] Failed to apply the protocol-droid trade "
                    + "advantage - trade prices will simply be vanilla, no other harm. " + ex);
            }
        }
    }

    /// <summary>
    /// A protocol droid in a trading party shifts prices toward that party.
    ///
    /// WHY THESE TARGETS. RimWorld computes a trade price exactly twice:
    /// <c>TradeUtility.GetPricePlayerBuy</c> and
    /// <c>TradeUtility.GetPricePlayerSell</c>, both called once per
    /// <c>Tradeable</c> from the private <c>Tradeable.InitPriceDataIfNeeded</c>,
    /// which then caches into pricePlayerBuy/pricePlayerSell. Postfixing those
    /// two statics catches every route to a price - the trade dialog, the deal
    /// total, caravan and orbital trades alike - and composes MULTIPLICATIVELY
    /// on top of everything vanilla already did (negotiator Social skill,
    /// faction-base offset, trader price type, difficulty, SellPriceFactor)
    /// rather than replacing any of it. A prefix would have to reimplement all
    /// of that and was never a candidate.
    ///
    /// WHY NOT A StatPart ON TradePriceImprovement, which would have been
    /// tidier and self-documenting in the stat card: that StatDef declares
    /// <c>minValue 0</c> and <c>maxValue 0.395</c> (Stats_Pawns_Social.xml) and
    /// StatWorker.FinalizeValue clamps to them, so the PENALTY half of this
    /// ruling - the whole "dangerous not to" - would silently clamp to zero,
    /// and a high-Social negotiator's bonus half would clamp away too. Widening
    /// a vanilla stat's clamps would have changed the inspired-trader case for
    /// every pawn in the game. Rejected on both counts.
    ///
    /// THE SHAPE, per §3.2's "both sides, so traders without one are cheaper to
    /// fleece". Each side contributes one term of <see cref="PerSideAdvantage"/>:
    ///   player party HAS a protocol droid  -> +1   ; lacks one -> -1
    ///   trader party HAS a protocol droid  -> -1   ; lacks one -> +1
    /// Net is the sum, so both-or-neither cancels to zero exactly (the
    /// anti-exponential guardrail in §6: "symmetric: traders' droids work
    /// against you"). Net ranges -2..+2, i.e. -12%..+12%. Positive is good for
    /// the player: buy prices are multiplied by (1 - net), sell prices by
    /// (1 + net).
    ///
    /// The trader term applies ONLY when the trader's party is a real,
    /// enumerable group of pawns - a visiting trade caravan on the map, or a
    /// world caravan. An orbital TradeShip and a Settlement have no pawns to
    /// inspect, so they contribute nothing rather than being scored as
    /// "no droid" and handing the player a free +6% on every orbital trade.
    /// The PLAYER term always applies: it is always knowable, and the ruling
    /// puts the penalty squarely on the player's own side.
    /// </summary>
    public static class Patch_ProtocolTradeAdvantage
    {
        /// <summary>
        /// One side's contribution. 6% per side, so the full swing between the
        /// best case (your droid, theirs absent) and the worst (no droid of
        /// yours, theirs present) is 24 percentage points on any price. Chosen
        /// against vanilla's own scale: a settlement offsets 0.02, a maxed
        /// Social negotiator reaches ~0.30, the Inspired Trade inspiration
        /// gives 0.18. 0.06 per side is well clear of noise and well short of
        /// out-earning the negotiator himself. No number was ruled; this one is
        /// FOUNDRY's, recorded in the item file.
        /// </summary>
        public const float PerSideAdvantage = 0.06f;

        /// <summary>DroidworksExtension.chassisClass for the Protocol family.</summary>
        public const int ProtocolChassisClass = 1;

        // Recomputed at most once per trade session (see CurrentAdvantage):
        // InitPriceDataIfNeeded runs once per Tradeable, and a caravan trade can
        // hold hundreds, so an uncached party scan would run hundreds of times
        // for an answer that cannot change while the dialog is open.
        private static ITrader cachedTrader;
        private static Pawn cachedNegotiator;
        private static int cachedTick = int.MinValue;
        private static float cachedAdvantage;
        private static bool cachedPlayerHas;
        private static bool cachedTraderHas;
        private static bool cachedTraderKnown;

        public static void Apply(Harmony harmony)
        {
            var buy = AccessTools.Method(typeof(TradeUtility), nameof(TradeUtility.GetPricePlayerBuy));
            var sell = AccessTools.Method(typeof(TradeUtility), nameof(TradeUtility.GetPricePlayerSell));
            var tooltip = AccessTools.Method(typeof(Tradeable), nameof(Tradeable.GetPriceTooltip));

            if (buy == null || sell == null)
            {
                Log.Error("[RimMandrake.StarWars.Droidworks] TradeUtility.GetPricePlayerBuy/Sell not found "
                    + "by reflection - vanilla API has moved. Protocol-droid trade advantage NOT applied.");
                return;
            }

            harmony.Patch(buy, postfix: new HarmonyMethod(typeof(Patch_ProtocolTradeAdvantage), nameof(PostfixBuy)));
            harmony.Patch(sell, postfix: new HarmonyMethod(typeof(Patch_ProtocolTradeAdvantage), nameof(PostfixSell)));

            // Legibility only - the mechanic works without it. Without this the
            // effect is invisible: vanilla's tooltip enumerates every other
            // price factor by name, and an unexplained 12% swing reads as a bug.
            if (tooltip != null)
            {
                harmony.Patch(tooltip,
                    postfix: new HarmonyMethod(typeof(Patch_ProtocolTradeAdvantage), nameof(PostfixTooltip)));
            }
            else
            {
                Log.Warning("[RimMandrake.StarWars.Droidworks] Tradeable.GetPriceTooltip not found - the "
                    + "protocol-droid price shift will apply but will not be explained in the trade tooltip.");
            }
        }

        public static void PostfixBuy(ref float __result)
        {
            float adv = CurrentAdvantage();
            if (adv == 0f) return;
            // Re-apply vanilla's own floor and rounding tail, which our factor
            // would otherwise step through.
            __result = Mathf.Max(__result * (1f - adv), TradeUtility.MinimumBuyPrice);
            if (__result > 99.5f) __result = Mathf.Round(__result);
        }

        public static void PostfixSell(ref float __result)
        {
            float adv = CurrentAdvantage();
            if (adv == 0f) return;
            __result = Mathf.Max(__result * (1f + adv), TradeUtility.MinimumSellPrice);
            if (__result > 99.5f) __result = Mathf.Round(__result);
        }

        public static void PostfixTooltip(ref string __result)
        {
            if (string.IsNullOrEmpty(__result)) return;
            float adv = CurrentAdvantage();
            if (adv == 0f) return;

            __result += "\n\nProtocol droid negotiation"
                + "\n  Your party: " + (cachedPlayerHas ? "a protocol droid" : "none")
                + (cachedTraderKnown
                    ? "\n  Their party: " + (cachedTraderHas ? "a protocol droid" : "none")
                    : "")
                + "\n  Prices " + Mathf.Abs(adv).ToStringPercent()
                + (adv > 0f ? " in your favour" : " against you");
        }

        /// <summary>
        /// The net price shift for the trade session in progress, or 0 when
        /// there is no live silver trade to shift.
        /// </summary>
        public static float CurrentAdvantage()
        {
            // Order matters: TradeSession.TradeCurrency dereferences trader.
            if (!TradeSession.Active) return 0f;
            // A gift is not a trade. FactionGiftUtility.GetGoodwillChange calls
            // GetPricePlayerSell to value a gift, and goodwill must not move
            // because somebody brought a droid.
            if (TradeSession.giftMode) return 0f;
            if (TradeSession.TradeCurrency != TradeCurrency.Silver) return 0f;
            if (TradeSession.playerNegotiator == null) return 0f;

            int now = Find.TickManager?.TicksGame ?? 0;
            if (ReferenceEquals(cachedTrader, TradeSession.trader)
                && cachedNegotiator == TradeSession.playerNegotiator
                && Math.Abs(now - cachedTick) < 250)
            {
                return cachedAdvantage;
            }

            cachedPlayerHas = PartyHasProtocolDroid(PlayerParty());
            List<Pawn> traderParty = TraderParty();
            cachedTraderKnown = traderParty != null;
            cachedTraderHas = cachedTraderKnown && PartyHasProtocolDroid(traderParty);

            int net = cachedPlayerHas ? 1 : -1;
            if (cachedTraderKnown) net += cachedTraderHas ? -1 : 1;

            cachedAdvantage = net * PerSideAdvantage;
            cachedTrader = TradeSession.trader;
            cachedNegotiator = TradeSession.playerNegotiator;
            cachedTick = now;
            return cachedAdvantage;
        }

        /// <summary>
        /// The pawns standing with the player negotiator: his caravan on the
        /// world map, otherwise every player-faction pawn on his map.
        /// </summary>
        public static List<Pawn> PlayerParty()
        {
            Pawn negotiator = TradeSession.playerNegotiator;
            if (negotiator == null) return null;

            Caravan caravan = negotiator.GetCaravan();
            if (caravan != null) return caravan.PawnsListForReading;

            Map map = negotiator.MapHeld;
            if (map != null && Faction.OfPlayer != null)
            {
                return map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer);
            }
            return new List<Pawn> { negotiator };
        }

        /// <summary>
        /// The trader's own pawns, or null when the trader has no party that
        /// can be inspected (an orbital TradeShip, a Settlement's stock).
        /// </summary>
        public static List<Pawn> TraderParty()
        {
            if (TradeSession.trader is Pawn traderPawn)
            {
                Lord lord = traderPawn.GetLord();
                if (lord != null && !lord.ownedPawns.NullOrEmpty()) return lord.ownedPawns;
                return new List<Pawn> { traderPawn };
            }
            if (TradeSession.trader is Caravan traderCaravan) return traderCaravan.PawnsListForReading;
            return null;
        }

        public static bool PartyHasProtocolDroid(IEnumerable<Pawn> party)
        {
            if (party == null) return false;
            foreach (Pawn pawn in party)
            {
                if (IsAvailableProtocolDroid(pawn)) return true;
            }
            return false;
        }

        /// <summary>
        /// Protocol family, and actually able to talk for you: a dead, downed,
        /// powered-down or imprisoned droid negotiates for nobody.
        /// </summary>
        public static bool IsAvailableProtocolDroid(Pawn pawn)
        {
            if (pawn == null || pawn.Dead || pawn.Downed) return false;
            if (pawn.IsPrisoner) return false;
            if (pawn.health?.hediffSet?.HasHediff(DroidworksDefOf.RSW_DW_PoweredDown) ?? false) return false;

            // Same LastOrDefault reasoning as CompDWHeadDropper/CompDroidDetonation:
            // XML inheritance APPENDS modExtensions, so the race's own copy always
            // sorts after the family abstract's inherited one.
            DroidworksExtension ext = pawn.def?.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();
            return ext != null && ext.chassisClass == ProtocolChassisClass;
        }
    }
}
