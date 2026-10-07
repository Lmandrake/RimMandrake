using Verse;

namespace RimMandrake.ShipVermin
{
    /// <summary>
    /// SHIPVERMIN_FREE_TIER_BEASTS_1. Owner ruling (card, typed, 2026-10-07): "Make the free tier
    /// have its own beasts that get patched by the Star Wars bestiary when active. Same mechanics
    /// same mod otherwise."
    ///
    /// Sits on one of this mod's own free-tier PawnKindDefs (RM_Skivvik, RM_Rattagh, RM_Gorrud,
    /// RM_Fethrik). This mod never adds it: a franchise layer does, by patch, to say "in this slot,
    /// spawn my creature instead". ShipVerminSettings.Resolve reads it, so a wreck nest picks the
    /// canon kind in that slot and the slot's checkbox still governs it. If the named kind does
    /// not resolve the free kind is used, so a stale swap can never empty a slot.
    /// </summary>
    public class RM_ShipVerminCanonSwapExtension : DefModExtension
    {
        public string kind;
    }
}
