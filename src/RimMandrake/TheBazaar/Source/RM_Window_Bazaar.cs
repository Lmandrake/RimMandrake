using RimWorld;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1, slice 1. Dialog_Trade SUBCLASS (design §2), so
    /// any mod holding a `Dialog_Trade` reference still type-checks once
    /// this is substituted in. Deliberately a plain pass-through right now
    /// -- no DoWindowContents/PreOpen override -- so this class alone
    /// changes nothing about how a trade window behaves. The grid, tabs and
    /// haggle UI land in later slices as overrides here.
    ///
    /// 🔴 NOT WIRED IN. There is no Harmony patch on `WindowStack.Add` yet,
    /// so nothing ever constructs this class during play. Wiring it in is
    /// the next slice's job, and it has a real hazard to solve first, found
    /// while reading Dialog_Trade's constructor via RimSage (not guessed):
    ///
    ///   Dialog_Trade's ONE public constructor unconditionally calls
    ///   `TradeSession.SetupWith(trader, playerNegotiator, giftsOnly)` --
    ///   which creates a FRESH `TradeSession.deal = new TradeDeal()` and,
    ///   when `!giftMode &amp;&amp; deal.cannotSellReasons.Count &gt; 0`, shows the
    ///   "MessageCannotSellItemsReason" message. Because that constructor
    ///   already ran once (making the vanilla call site's own
    ///   `new Dialog_Trade(...)`) by the time a `WindowStack.Add` prefix
    ///   could see it, naively substituting with
    ///   `new RM_Window_Bazaar(negotiator, trader, giftsOnly)` calls
    ///   SetupWith A SECOND TIME -- discarding the first TradeDeal (probably
    ///   harmless, nothing has changed between the two constructions) but
    ///   DOUBLE-FIRING that message when its condition holds. Fix that
    ///   before shipping the intercept -- e.g. suppress Messages.Message for
    ///   the duration of the second SetupWith call, or patch earlier than
    ///   WindowStack.Add so the constructor only runs once. Not solved here;
    ///   this comment is the handoff.
    /// </summary>
    public class RM_Window_Bazaar : Dialog_Trade
    {
        public RM_Window_Bazaar(Pawn playerNegotiator, ITrader trader, bool giftsOnly = false)
            : base(playerNegotiator, trader, giftsOnly)
        {
        }
    }
}
