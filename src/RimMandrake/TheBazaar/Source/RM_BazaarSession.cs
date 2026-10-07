using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// One open Bazaar trade. <see cref="Current"/> IS the session guard the
    /// price engine's <c>Tradeable.GetPriceFor</c> postfix checks: null =
    /// no Bazaar window is open = the postfix is a no-op and every price in
    /// the game is vanilla (design §2 "Session plumbing").
    ///
    /// Raised and lowered ONLY by <see cref="RM_Window_Bazaar"/>'s
    /// PostOpen/PostClose. Until the WindowStack.Add intercept lands
    /// (BAZAAR_WINDOW_GRID_1's next slice) nothing constructs that window,
    /// so <see cref="Current"/> stays null for the whole game — the engine
    /// is built and scribed but cannot move a price yet. That is the honest
    /// state, not a bug.
    /// </summary>
    public class RM_BazaarSession
    {
        public static RM_BazaarSession Current;

        /// <summary>The negotiator this session belongs to.</summary>
        public Pawn negotiator;

        /// <summary>The trader on the other side of the deal.</summary>
        public ITrader trader;

        public bool giftsOnly;

        /// <summary>The settlement tile whose economy prices this deal
        /// (<see cref="RM_BazaarEconomy.GlobalTile"/> for orbital/factionless).</summary>
        public int economyTile = RM_BazaarEconomy.GlobalTile;

        private readonly Dictionary<ThingDef, float> multiplierCache = new Dictionary<ThingDef, float>();

        /// <summary>Per-session cache: a multiplier cannot change while the
        /// window is open (drift is daily and the game is paused in trade),
        /// and GetPriceFor runs per row per frame.</summary>
        public float MultiplierFor(ThingDef def)
        {
            if (def == null) return 1f;
            float m;
            if (multiplierCache.TryGetValue(def, out m)) return m;
            RM_BazaarEconomy econ = RM_BazaarEconomy.Get();
            m = econ != null ? econ.MultiplierFor(economyTile, def) : 1f;
            multiplierCache[def] = m;
            return m;
        }

        public static RM_BazaarSession Open(Pawn negotiator, ITrader trader, bool giftsOnly)
        {
            RM_BazaarSession s = new RM_BazaarSession
            {
                negotiator = negotiator,
                trader = trader,
                giftsOnly = giftsOnly,
                economyTile = RM_BazaarEconomy.TileFor(trader),
            };

            // Observe BEFORE raising the guard, so history records vanilla
            // prices rather than our own multiplied output.
            if (!giftsOnly)
            {
                RM_BazaarEconomy econ = RM_BazaarEconomy.Get();
                econ?.RecordSessionOpen(trader, TradeSession.deal?.AllTradeables);
            }

            Current = s;
            return s;
        }

        public static void Close(RM_BazaarSession s)
        {
            if (Current == s) Current = null;
        }
    }
}
