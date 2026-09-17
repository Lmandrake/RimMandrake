using RimWorld;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 slice 1 -- a forward-declared marker so the
    /// plugin worker signatures in Defs/ match design doc §2 exactly
    /// (`DrawCell(Rect, Tradeable, BazaarSession)` etc.) without inventing a
    /// throwaway `object` parameter that would need re-typing later.
    ///
    /// Empty on purpose. The real session state -- the price engine handle,
    /// the intel-layer gates currently unlocked, the haggle patience meter --
    /// lands in later slices (design §3-§5, items not yet filed under this
    /// one). Until then every worker sees a session with nothing on it,
    /// which is honest: there is no engine yet for it to carry.
    /// </summary>
    public class RM_BazaarSession
    {
        /// <summary>The negotiator this session belongs to. Set once a real
        /// window wires a session up (slice 2+); null here is not a bug.</summary>
        public Pawn negotiator;

        /// <summary>The trader on the other side of the deal.</summary>
        public ITrader trader;
    }
}
