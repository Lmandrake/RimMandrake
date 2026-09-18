using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Property;

namespace RimMandrake.Pickpocket
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, crime-suite pass. Spec item 9's "pickpocket":
    /// finds something worth lifting out of a target pawn's own carried
    /// INVENTORY (<see cref="Pawn_InventoryTracker"/> only — never equipped
    /// weapons or worn apparel, same "no ripping slotted gear off a living
    /// body" simplification TheftHauler/SalvageClaim already apply to their
    /// own target kinds) and moves it to the acting pawn's own inventory.
    ///
    /// This is the one physical hand-off SETTLEMENT_VERBS_WAVE_1 actually
    /// performs instantly from a float-menu delegate — unlike the claim-fee
    /// and buy verbs (whose whole point is the provenance RECORD, not an
    /// inventory move), a pickpocket that doesn't move anything isn't a
    /// theft at all.
    /// </summary>
    public static class PickpocketUtility
    {
        // Below this MarketValue*stackCount, an item isn't worth the risk of
        // getting caught over — keeps a pawn from getting a "Pickpocket"
        // order over someone's single stray toothpick. Tunable in Mod
        // Settings (PropertySettings.pickpocketMinItemValueSilver).
        public static Thing FindStealableItem(Pawn target)
        {
            ThingOwner container = target?.inventory?.innerContainer;
            if (container == null || container.Count == 0) return null;

            Thing best = null;
            float bestValue = 0f;
            for (int i = 0; i < container.Count; i++)
            {
                Thing item = container[i];
                float value = Mathf.Max(0f, item.MarketValue) * Mathf.Max(1, item.stackCount);
                if (value < PropertySettings.pickpocketMinItemValueSilver) continue;
                if (value > bestValue)
                {
                    bestValue = value;
                    best = item;
                }
            }
            return best;
        }

        // canMergeWithExistingStacks: false is deliberate, not the API
        // default. GameComponent_PropertyLedger's own RecordClaim doc
        // explains why: the ledger keys claim records on the Thing INSTANCE,
        // and TryAbsorbStack merging the stolen stack into one the actor
        // already carries would Destroy() the just-stolen Thing and orphan
        // the Stolen record PropertyEngine.Fire recorded against it a moment
        // earlier in this same delegate. Keeping the same instance is what
        // makes the claim follow the item.
        public static bool TransferToActor(Thing item, Pawn target, Pawn actor)
        {
            ThingOwner source = target?.inventory?.innerContainer;
            ThingOwner dest = actor?.inventory?.innerContainer;
            if (source == null || dest == null || item == null) return false;

            return source.TryTransferToContainer(item, dest, item.stackCount, canMergeWithExistingStacks: false);
        }
    }
}
