using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // The event spine's orchestrator (design/Jawa/ownership_settlement_spec.md
    // "act -> TakingEvent -> claim resolution -> perception roll -> ...
    // -> faction record"), and the one entry point future verb code calls.
    //
    // Fire() covers the six adversarial-or-transactional acts (Take, Use,
    // Strip, Sabotage, Buy, Claim). Non-adversarial provenance transfers
    // that have no "victim" to witness anything (Gift, Inherit, Loot) skip
    // straight to RecordTransfer/RecordLoot — spec item 3 lists them as
    // exception-recorded claims, not spine acts.
    public static class PropertyEngine
    {
        // --- The event spine ------------------------------------------------

        public static TakingEvent Fire(TakingEvent evt)
        {
            if (evt?.Thing == null) return evt;

            GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
            if (ledger == null) return evt; // no active Game (e.g. main menu) - nothing to do

            evt.PriorClaim = ClaimEngine.ResolveClaim(evt.Thing, evt.Tick);
            evt.WasAuthorized = IsAuthorized(evt.Actor, evt.PriorClaim);

            switch (evt.Act)
            {
                case TakingAct.Buy:
                    RecordTransfer(evt.Thing, evt.Actor, ClaimBasis.Purchased, 1f, evt.Tick);
                    evt.WasAuthorized = true; // a completed sale is legitimate by definition
                    break;

                case TakingAct.Claim:
                    RecordTransfer(evt.Thing, evt.Actor, ClaimBasis.ClaimFeePaid, 1f, evt.Tick);
                    evt.WasAuthorized = true;
                    break;

                case TakingAct.Take:
                case TakingAct.Strip:
                    if (!evt.WasAuthorized && evt.PriorClaim.HasValue)
                    {
                        // Origin claim preserved at ~1.0 regardless of who now
                        // holds the Thing (spec item 5) - this IS that record.
                        RecordTransfer(evt.Thing, evt.PriorClaim.Value.Claimant, ClaimBasis.Stolen, 1f, evt.Tick);
                    }
                    break;

                case TakingAct.Use:
                case TakingAct.Sabotage:
                    // No ownership transfer - using or damaging someone's
                    // property doesn't change whose it is. Friction only.
                    break;
            }

            if (!evt.WasAuthorized)
            {
                RollPerceptionAndPropagate(evt);
            }

            return evt;
        }

        private static bool IsAuthorized(ClaimantRef actor, ClaimResolution? priorClaim)
        {
            if (!priorClaim.HasValue) return true; // unclaimed - free to take

            ClaimantRef claimant = priorClaim.Value.Claimant;
            if (claimant.Equals(actor)) return true;

            // Commons is implicitly usable by any member of the same faction
            // (spec item 4's "survival spine" - shared stuff, not fenced off
            // from the faction's own members).
            if (claimant.Kind == ClaimantKind.Commons && actor.Kind == ClaimantKind.Pawn
                && actor.Pawn?.Faction == claimant.Faction)
            {
                return true;
            }

            return false;
        }

        // --- Perception + propagation ---------------------------------------

        private static void RollPerceptionAndPropagate(TakingEvent evt)
        {
            Pawn actorPawn = evt.Actor.Kind == ClaimantKind.Pawn ? evt.Actor.Pawn : null;
            List<Pawn> witnesses = PerceptionUtility.RollWitnesses(evt.Thing, actorPawn);
            evt.Witnesses = witnesses;
            if (witnesses.Count == 0) return; // nobody saw it - costs nothing, spec item 6

            GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();

            Pawn ownerPawn = evt.PriorClaim.HasValue && evt.PriorClaim.Value.Claimant.Kind == ClaimantKind.Pawn
                ? evt.PriorClaim.Value.Claimant.Pawn
                : null;

            for (int i = 0; i < witnesses.Count; i++)
            {
                Pawn witness = witnesses[i];
                float confidence = PerceptionUtility.WitnessConfidence(witness, evt.Actor);

                // Each witness's observation is filed under THEIR OWN
                // faction, not the map's parent faction - a visiting trader
                // or guest who personally sees a theft tells their own
                // faction, not the player's. A witness with no faction has
                // nobody to file the observation with.
                if (witness.Faction != null)
                {
                    FactionRecord record = ledger?.GetOrCreateFactionRecord(witness.Faction);
                    record?.RegisterWitness(evt.Actor, confidence, evt.Tick);
                }

                // Colony-side friction hook (spec item 4/10): the wronged
                // party personally saw it happen.
                if (ownerPawn != null && witness == ownerPawn)
                {
                    PropertyEvents.RaiseUnauthorizedTakingWitnessedByOwner(evt, ownerPawn);
                }
            }
        }

        // --- Direct provenance writes (no spine, no perception) -------------

        public static ClaimRecord RecordTransfer(Thing thing, ClaimantRef newClaimant, ClaimBasis basis, float strength, int tick)
        {
            GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
            if (ledger == null || thing == null) return null;

            var record = new ClaimRecord(newClaimant, strength, basis, tick);
            ledger.RecordClaim(thing, record);
            PropertyEvents.RaiseClaimRecorded(thing, record);
            return record;
        }

        // Spec item 5: battlefield loot keeps a strong origin claim
        // (basis BattleLootOrigin, ~1.0) for the DEFEATED owner, alongside a
        // separate Looted record for whoever now carries it. Both persist in
        // the same Thing's claim set; ClaimEngine picks a winner per query,
        // recency/strength decide it, nothing is deleted.
        public static void RecordLoot(Thing thing, ClaimantRef looter, ClaimantRef originalOwner, int tick)
        {
            if (!originalOwner.IsUnclaimed)
            {
                RecordTransfer(thing, originalOwner, ClaimBasis.BattleLootOrigin, 1f, tick);
            }
            RecordTransfer(thing, looter, ClaimBasis.Looted, 1f, tick);
        }

        public static void RecordGift(Thing thing, ClaimantRef recipient, int tick)
            => RecordTransfer(thing, recipient, ClaimBasis.Gifted, 1f, tick);

        public static void RecordInheritance(Thing thing, ClaimantRef heir, int tick)
            => RecordTransfer(thing, heir, ClaimBasis.Inherited, 1f, tick);
    }
}
