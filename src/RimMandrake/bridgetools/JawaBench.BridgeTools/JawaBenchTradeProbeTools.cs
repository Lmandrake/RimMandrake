// JawaBenchTradeProbeTools.cs - read a live trade's ACTUAL prices without a dialog.
//
// WHY THIS EXISTS. Nothing on the bridge could open or read a trade. Trade
// prices are computed in TradeUtility.GetPricePlayerBuy/Sell, cached into
// Tradeable, and only ever surfaced through Dialog_Trade - a modal, and nothing
// on the bridge can answer a modal. So any claim about a price factor (a mod's,
// a stat's, a Harmony patch's) was previously unfalsifiable from here.
// DROID_PROTOCOL_TRADE_ADVANTAGE_1 (packet C4) needed "prices measured both
// ways" and this is what measures them.
//
// FACTS READ FROM 1.6 SOURCE, which shape every line below:
//  * TradeSession is a STATIC. Setting it up while a real Dialog_Trade is open
//    would destroy that session's deal, so this refuses when one is active.
//  * TradeSession.SetupWith(trader, negotiator, giftMode) builds a TradeDeal,
//    which is what actually materialises Tradeables; Tradeable.GetPriceFor runs
//    the private InitPriceDataIfNeeded on first call and caches. So the prices
//    read here are the same floats the dialog would print.
//  * Tradeable.GetPriceFor is the ONLY price accessor; there is no side channel.
//  * TradeSession.Close() only nulls `trader` - exactly what vanilla does when
//    the dialog closes - so this leaves no state a later real trade can trip on.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/trade_price_probe",
            Description =
                "Open a headless TradeSession against a trader pawn on the current map and report the " +
                "REAL buy/sell price of each tradeable, plus both trading parties' rosters. REFUSES when " +
                "a trade dialog is already open (TradeSession is a static and would be clobbered), when no " +
                "map is loaded, when no trader pawn is on the map, and when the colony has no eligible " +
                "negotiator. Read-only in effect: the session is closed again before returning, exactly as " +
                "vanilla closes it. Prices come from Tradeable.GetPriceFor, the same accessor the dialog " +
                "uses, so any mod price factor is included.",
            ResultDescription =
                "success, traderName/traderKind/traderFaction, negotiatorName, " +
                "negotiatorTradePriceImprovement, playerParty[] and traderParty[] " +
                "(defName, label, faction, droidChassisClass), tradeableCount, and prices[] " +
                "(defName, label, baseMarketValue, buy, sell), capped by maxRows.")]
        public static async Task<object> TradePriceProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Trader pawn id, bare or Thing_-prefixed. Default: the first non-player trader pawn spawned on the current map.")] string traderPawnId = null,
            [ToolParameter(Description = "Player negotiator pawn id, bare or Thing_-prefixed. Default: the free colonist with the highest TradePriceImprovement.")] string negotiatorPawnId = null,
            [ToolParameter(Description = "Semicolon-separated ThingDef names to report. Default: every tradeable, capped by maxRows.")] string defNames = null,
            [ToolParameter(Description = "Maximum price rows returned. Default 40.")] int maxRows = 40)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                if (TradeSession.Active)
                {
                    return Fail("A TradeSession is already active - a trade dialog is open. "
                        + "Close it before probing; this tool will not clobber a live deal.");
                }

                Pawn trader = ResolveProbePawn(map, traderPawnId,
                    p => p.trader != null && p.trader.traderKind != null && p.Faction != Faction.OfPlayer);
                if (trader == null)
                {
                    return Fail("No trader pawn found on the current map.",
                        new { traderPawnId, hint = "Fire a trade caravan arrival first (jawa/fire_incident TraderCaravanArrival)." });
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

                HashSet<string> wanted = null;
                if (!string.IsNullOrEmpty(defNames))
                {
                    wanted = new HashSet<string>(
                        defNames.Split(';').Select(s => s.Trim()).Where(s => s.Length > 0),
                        StringComparer.OrdinalIgnoreCase);
                }
                if (maxRows <= 0) maxRows = 40;

                var rows = new List<object>();
                int tradeableCount = 0;
                object playerParty, traderParty;
                float negotiatorImprovement;

                try
                {
                    TradeSession.SetupWith(trader, negotiator, false);
                    negotiatorImprovement = negotiator.GetStatValue(StatDefOf.TradePriceImprovement);

                    // Rosters are captured INSIDE the session, mirroring exactly how a
                    // price-side patch would see them (caravan first, else the map's
                    // player-faction pawns; trader's Lord, else the trader alone).
                    playerParty = DescribeParty(ProbePlayerParty(negotiator));
                    traderParty = DescribeParty(ProbeTraderParty(trader));

                    List<Tradeable> all = TradeSession.deal?.AllTradeables;
                    if (all != null)
                    {
                        tradeableCount = all.Count;
                        foreach (Tradeable t in all)
                        {
                            if (rows.Count >= maxRows) break;
                            if (!t.HasAnyThing) continue;
                            string dn = t.ThingDef?.defName;
                            if (dn == null) continue;
                            if (wanted != null && !wanted.Contains(dn)) continue;
                            rows.Add(new
                            {
                                defName = dn,
                                label = t.Label,
                                baseMarketValue = t.BaseMarketValue,
                                buy = t.GetPriceFor(TradeAction.PlayerBuys),
                                sell = t.GetPriceFor(TradeAction.PlayerSells)
                            });
                        }
                    }
                }
                finally
                {
                    TradeSession.Close();
                }

                return (object)new
                {
                    success = true,
                    traderName = trader.LabelShort,
                    traderId = trader.ThingID,
                    traderKind = trader.trader?.traderKind?.defName,
                    traderFaction = trader.Faction?.def?.defName,
                    negotiatorName = negotiator.LabelShort,
                    negotiatorId = negotiator.ThingID,
                    negotiatorTradePriceImprovement = negotiatorImprovement,
                    playerParty,
                    traderParty,
                    tradeableCount,
                    prices = rows,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        /// <summary>Bare or Thing_-prefixed id, else the first pawn matching the fallback predicate.</summary>
        private static Pawn ResolveProbePawn(Map map, string id, Func<Pawn, bool> fallback)
        {
            IReadOnlyList<Pawn> spawned = map.mapPawns.AllPawnsSpawned;
            if (!string.IsNullOrEmpty(id))
            {
                string bare = id.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) ? id.Substring(6) : id;
                return spawned.FirstOrDefault(p =>
                    string.Equals(p.ThingID, bare, StringComparison.OrdinalIgnoreCase));
            }
            return spawned.FirstOrDefault(fallback);
        }

        private static List<Pawn> ProbePlayerParty(Pawn negotiator)
        {
            Caravan caravan = negotiator.GetCaravan();
            if (caravan != null) return caravan.PawnsListForReading;
            Map map = negotiator.MapHeld;
            if (map != null && Faction.OfPlayer != null) return map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer);
            return new List<Pawn> { negotiator };
        }

        private static List<Pawn> ProbeTraderParty(Pawn trader)
        {
            Lord lord = trader.GetLord();
            if (lord != null && lord.ownedPawns != null && lord.ownedPawns.Count > 0) return lord.ownedPawns;
            return new List<Pawn> { trader };
        }

        /// <summary>
        /// Roster with the droid chassis class read REFLECTIVELY off any modExtension
        /// whose type is named DroidworksExtension. Reflective on purpose: the
        /// companion must not take a hard reference on a mod assembly, and reading the
        /// same signal by different code is the independent instrument.
        /// </summary>
        private static object DescribeParty(List<Pawn> party)
        {
            var rows = new List<object>();
            if (party == null) return rows;
            foreach (Pawn p in party)
            {
                if (p == null) continue;
                rows.Add(new
                {
                    defName = p.def?.defName,
                    label = p.LabelShort,
                    faction = p.Faction?.def?.defName,
                    dead = p.Dead,
                    downed = p.Downed,
                    droidChassisClass = DroidChassisClassOf(p)
                });
            }
            return rows;
        }

        private static int? DroidChassisClassOf(Pawn p)
        {
            var exts = p?.def?.modExtensions;
            if (exts == null) return null;
            int? found = null;
            foreach (DefModExtension ext in exts)
            {
                if (ext == null) continue;
                if (ext.GetType().Name != "DroidworksExtension") continue;
                var field = ext.GetType().GetField("chassisClass");
                if (field == null) continue;
                try { found = Convert.ToInt32(field.GetValue(ext)); }
                catch { /* reported as null below rather than swallowed silently in a caller */ }
            }
            return found;   // LAST wins: XML inheritance APPENDS modExtensions
        }
    }
}
