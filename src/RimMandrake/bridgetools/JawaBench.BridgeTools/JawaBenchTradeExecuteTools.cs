// JawaBenchTradeExecuteTools.cs - COMPLETE a trade headlessly, not just price it.
//
// WHY THIS EXISTS. NINEFOLD_MISSING_EVENT_HOOKS_1. Ninefold's Mob'Unloo hook is a
// Harmony postfix on TradeDeal.TryExecute gated on `actuallyTraded`, and nothing on
// the bridge could reach that choke point: the sibling tool in
// JawaBenchTradeProbeTools.cs opens a TradeSession and READS prices, and the vanilla
// debug actions only SPAWN a trader. Completing a deal was a human clicking
// Dialog_Trade. This tool is the missing synthetic driver.
//
// FACTS READ FROM 1.6 SOURCE (RimSage), each of which shapes a line below:
//  * TradeDeal.TryExecute(out bool actuallyTraded) is PUBLIC, and TradeSession.deal
//    is a public static - no reflection is needed anywhere in this file.
//  * 🔴 TryExecute's "colony cannot afford" branch calls
//      Find.WindowStack.WindowOfType<Dialog_Trade>().FlashSilver()
//    with NO null guard. Headless there is no Dialog_Trade, so an unaffordable deal
//    would NullReferenceException inside vanilla rather than returning false. That
//    single fact is why this tool replicates the affordability test ITSELF and
//    refuses BEFORE calling TryExecute. Do not remove that pre-check.
//  * `actuallyTraded` is true iff at least one Tradeable has ActionToDo != None -
//    i.e. a deal where every count stayed 0 returns true from TryExecute and still
//    must NOT count as a completed trade. Both flags are reported separately.
//  * In gift mode the branch is different again: actuallyTraded = goodwillChange > 0,
//    so a gift to a faction-less trader, or one worth no goodwill, reports false.
//  * Tradeable sign convention: ForceToDestination(n) => PlayerSells,
//    ForceToSource(n) => PlayerBuys (Transferable.CountToTransferTo*), and
//    ClampAmount bounds it by what each side actually holds. The requested and the
//    applied counts are BOTH reported, because a silent clamp to 0 is exactly the
//    "success that changed nothing" this bridge exists to expose.
//  * TradeSession.Close() only nulls `trader`, the same thing vanilla does when the
//    dialog closes, so this leaves no state a later real trade can trip on.
//
// NO tool-name prefixes in prose in this file: build.py scans the assembly for such
// literals and a mention in a description becomes a phantom tool that blocks deploy.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/trade_execute",
            Description =
                "Drive a real trade to completion headlessly: open a TradeSession against a trader pawn " +
                "on the current map, set one tradeable's transfer count, and call TradeDeal.TryExecute - " +
                "the same choke point the trade dialog uses, so every Harmony patch on a completed trade " +
                "fires. DESTRUCTIVE: goods and silver actually change hands. dryRun DEFAULTS TRUE and " +
                "reports the deal it would execute without executing it. REFUSES when a trade dialog is " +
                "already open (TradeSession is a static and would clobber the live deal), when no map is " +
                "loaded, when no trader pawn is present, when no eligible negotiator exists, when the " +
                "named def is not tradeable in this deal, when the transfer count clamps to zero, and - " +
                "critically - when the colony cannot afford the deal, because vanilla's own cannot-afford " +
                "branch dereferences the trade dialog and would throw with no dialog open. Read " +
                "actuallyTraded, not success: a deal where every count clamped to zero still returns a " +
                "true result from vanilla.",
            ResultDescription =
                "success, executed, tryExecuteResult, actuallyTraded, defName, action, requestedCount, " +
                "appliedCount, clampedBy, pricePerUnit, tradeableCount, cannotSellReasons[], " +
                "colonyStackBefore/colonyStackAfter and silverBefore/silverAfter (independent map " +
                "stack-count instruments, NOT read from the deal), traderName, negotiatorName, giftMode.")]
        public static async Task<object> TradeExecute(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingDef name to move, e.g. 'Silver' or 'Steel'. Default: the non-currency tradeable the colony holds most of (for a sale) or the trader holds most of (for a purchase).")] string defName = null,
            [ToolParameter(Description = "'sell' (colony -> trader) or 'buy' (trader -> colony). Default 'sell', which needs no colony silver.")] string action = "sell",
            [ToolParameter(Description = "Units to move. Clamped to what the source side actually holds; the clamp is reported, never silent. Default 1.")] int count = 1,
            [ToolParameter(Description = "Report the deal without executing it. DEFAULTS TRUE - pass false to actually move goods.")] bool dryRun = true,
            [ToolParameter(Description = "Run as a gift instead of a sale. In gift mode vanilla sets actuallyTraded from the goodwill change, so a gift worth no goodwill reports false. Default false.")] bool giftMode = false,
            [ToolParameter(Description = "Trader pawn id, bare or Thing_-prefixed. Default: the first non-player trader pawn spawned on the current map.")] string traderPawnId = null,
            [ToolParameter(Description = "Player negotiator pawn id, bare or Thing_-prefixed. Default: the free colonist with the highest TradePriceImprovement.")] string negotiatorPawnId = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (TradeSession.Active)
                {
                    return Fail("A TradeSession is already active - a trade dialog is open. "
                        + "Close it first; this tool will not clobber a live deal.");
                }

                bool sell;
                if (string.Equals(action, "sell", StringComparison.OrdinalIgnoreCase)) sell = true;
                else if (string.Equals(action, "buy", StringComparison.OrdinalIgnoreCase)) sell = false;
                else return Fail("action must be 'sell' or 'buy'.", new { action });

                if (count <= 0) return Fail("count must be >= 1.", new { count });

                Pawn trader = ResolveProbePawn(map, traderPawnId,
                    p => p.trader != null && p.trader.traderKind != null && p.Faction != Faction.OfPlayer);
                if (trader == null)
                {
                    return Fail("No trader pawn found on the current map.",
                        new { traderPawnId, hint = "Fire a trade caravan arrival first (fire_incident TraderCaravanArrival)." });
                }

                Pawn negotiator = ResolveProbePawn(map, negotiatorPawnId,
                    p => p.Faction == Faction.OfPlayer && !p.Dead && !p.Downed && p.IsFreeColonist);
                if (negotiator == null && negotiatorPawnId == null)
                {
                    negotiator = map.mapPawns.FreeColonistsSpawned
                        .Where(p => !p.Dead && !p.Downed)
                        .OrderByDescending(p => p.GetStatValue(StatDefOf.TradePriceImprovement))
                        .FirstOrDefault();
                }
                if (negotiator == null) return Fail("No eligible player negotiator on the current map.");

                if (giftMode && trader.Faction == null)
                {
                    return Fail("giftMode needs a trader with a faction - vanilla computes actuallyTraded "
                        + "from the goodwill change to that faction.");
                }

                object result = null;
                try
                {
                    TradeSession.SetupWith(trader, negotiator, giftMode);
                    TradeDeal deal = TradeSession.deal;
                    if (deal == null) return Fail("TradeSession.SetupWith produced no deal.");

                    List<Tradeable> all = deal.AllTradeables ?? new List<Tradeable>();
                    var cannotSell = deal.cannotSellReasons != null
                        ? new List<string>(deal.cannotSellReasons) : new List<string>();

                    Tradeable target = PickTradeable(all, defName, sell);
                    if (target == null)
                    {
                        return Fail(defName == null
                                ? "This deal has no non-currency tradeable the chosen side actually holds."
                                : "No tradeable in this deal matches that def, or the holding side has none of it.",
                            new
                            {
                                defName,
                                action,
                                tradeableCount = all.Count,
                                cannotSellReasons = cannotSell,
                                available = all.Where(t => t.HasAnyThing && t.ThingDef != null)
                                               .Take(40)
                                               .Select(t => new
                                               {
                                                   defName = t.ThingDef.defName,
                                                   colonyHas = t.CountHeldBy(Transactor.Colony),
                                                   traderHas = t.CountHeldBy(Transactor.Trader)
                                               })
                                               .ToList()
                            });
                    }

                    ThingDef td = target.ThingDef;
                    int stackBefore = MapStackCount(map, td);
                    int silverBefore = MapStackCount(map, ThingDefOf.Silver);

                    // Set the count the way the dialog would, then clamp to what the
                    // source side holds and REPORT the clamp rather than hiding it.
                    if (sell) target.ForceToDestination(count);
                    else target.ForceToSource(count);
                    int signedRequested = target.CountToTransfer;
                    int signedApplied = target.ClampAmount(signedRequested);
                    target.ForceTo(signedApplied);

                    int appliedUnits = Math.Abs(signedApplied);
                    string clampedBy = appliedUnits == count
                        ? null
                        : (sell ? "colony holds only " + target.CountHeldBy(Transactor.Colony)
                                : "trader holds only " + target.CountHeldBy(Transactor.Trader));

                    // The dialog recomputes the silver line on every adjustment; TryExecute's
                    // affordability test reads it BEFORE calling UpdateCurrencyCount itself.
                    deal.UpdateCurrencyCount();

                    float price = target.GetPriceFor(sell ? TradeAction.PlayerSells : TradeAction.PlayerBuys);
                    TradeAction actionToDo = target.ActionToDo;

                    if (appliedUnits <= 0 || actionToDo == TradeAction.None)
                    {
                        return Fail("Transfer count clamped to zero - nothing would change hands, and vanilla "
                            + "would still return a true result. Refusing rather than reporting a hollow trade.",
                            new
                            {
                                defName = td.defName,
                                action,
                                requestedCount = count,
                                appliedCount = 0,
                                clampedBy,
                                colonyHas = target.CountHeldBy(Transactor.Colony),
                                traderHas = target.CountHeldBy(Transactor.Trader)
                            });
                    }

                    // 🔴 Vanilla's own cannot-afford branch NREs headless (see file header).
                    // Replicate its test and refuse here instead of letting it throw.
                    if (!giftMode)
                    {
                        Tradeable currency = deal.CurrencyTradeable;
                        if (currency == null)
                        {
                            return Fail("This deal has no currency tradeable; vanilla's affordability branch "
                                + "would dereference the (absent) trade dialog and throw.");
                        }
                        if (currency.CountPostDealFor(Transactor.Colony) < 0)
                        {
                            return Fail("The colony cannot afford this deal - refused before TryExecute, whose "
                                + "cannot-afford branch dereferences the trade dialog and would throw headless.",
                                new
                                {
                                    defName = td.defName,
                                    action,
                                    appliedCount = appliedUnits,
                                    pricePerUnit = price,
                                    colonySilverPostDeal = currency.CountPostDealFor(Transactor.Colony)
                                });
                        }
                        if (!deal.DoesTraderHaveEnoughSilver())
                        {
                            return Fail("The trader cannot afford this deal (DoesTraderHaveEnoughSilver is false).",
                                new { defName = td.defName, action, appliedCount = appliedUnits, pricePerUnit = price });
                        }
                    }

                    if (dryRun)
                    {
                        result = new
                        {
                            success = true,
                            executed = false,
                            dryRun = true,
                            tryExecuteResult = (bool?)null,
                            actuallyTraded = (bool?)null,
                            defName = td.defName,
                            action = sell ? "sell" : "buy",
                            requestedCount = count,
                            appliedCount = appliedUnits,
                            clampedBy,
                            pricePerUnit = price,
                            actionToDo = actionToDo.ToString(),
                            tradeableCount = all.Count,
                            cannotSellReasons = cannotSell,
                            colonyStackBefore = stackBefore,
                            silverBefore,
                            traderName = trader.LabelShort,
                            negotiatorName = negotiator.LabelShort,
                            giftMode,
                            nextState = "pass dryRun=false to execute",
                            ticksGame = TicksGameSafe()
                        };
                    }
                    else
                    {
                        bool actuallyTraded;
                        bool ok = deal.TryExecute(out actuallyTraded);

                        int stackAfter = MapStackCount(map, td);
                        int silverAfter = MapStackCount(map, ThingDefOf.Silver);

                        result = new
                        {
                            success = true,
                            executed = true,
                            dryRun = false,
                            tryExecuteResult = ok,
                            actuallyTraded,
                            defName = td.defName,
                            action = sell ? "sell" : "buy",
                            requestedCount = count,
                            appliedCount = appliedUnits,
                            clampedBy,
                            pricePerUnit = price,
                            actionToDo = actionToDo.ToString(),
                            tradeableCount = all.Count,
                            cannotSellReasons = cannotSell,
                            colonyStackBefore = stackBefore,
                            colonyStackAfter = stackAfter,
                            colonyStackDelta = stackAfter - stackBefore,
                            silverBefore,
                            silverAfter,
                            silverDelta = silverAfter - silverBefore,
                            traderName = trader.LabelShort,
                            negotiatorName = negotiator.LabelShort,
                            giftMode,
                            ticksGame = TicksGameSafe()
                        };
                    }
                }
                finally
                {
                    TradeSession.Close();
                }

                return result;
            });
        }

        /// <summary>
        /// The named def, else the non-currency tradeable the SOURCE side holds most of.
        /// Returns null when nothing qualifies, so the caller reports a reason.
        /// </summary>
        private static Tradeable PickTradeable(List<Tradeable> all, string defName, bool sell)
        {
            Transactor source = sell ? Transactor.Colony : Transactor.Trader;
            IEnumerable<Tradeable> pool = all.Where(t => t != null && t.HasAnyThing && t.ThingDef != null);
            if (!string.IsNullOrEmpty(defName))
            {
                return pool.FirstOrDefault(t =>
                    string.Equals(t.ThingDef.defName, defName, StringComparison.OrdinalIgnoreCase)
                    && t.CountHeldBy(source) > 0);
            }
            return pool.Where(t => !t.IsCurrency && t.CountHeldBy(source) > 0)
                       .OrderByDescending(t => t.CountHeldBy(source))
                       .FirstOrDefault();
        }

        /// <summary>
        /// Total stack count of a def SPAWNED on the map - an instrument independent of
        /// TradeDeal entirely. Deliberately does NOT count pawn inventories or containers,
        /// so it under-reports rather than borrowing the deal's own bookkeeping.
        /// </summary>
        private static int MapStackCount(Map map, ThingDef def)
        {
            if (map == null || def == null) return -1;
            int total = 0;
            List<Thing> things = map.listerThings.ThingsOfDef(def);
            if (things == null) return 0;
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t == null || !t.Spawned) continue;
                total += t.stackCount;
            }
            return total;
        }
    }
}
