using System.Collections.Generic;

namespace RimMandrake.Property
{
    // PROPERTY_CLAIM_ERASE_API_1. The pure filtering rule behind GameComponent_PropertyLedger.ClearForeignClaims,
    // kept free of any live Game so the offline selftest can compile and run it. No rite knowledge lives here.
    public struct WipedClaim
    {
        public Verse.Thing Thing;
        public ClaimantRef Claimant;
        public ClaimBasis Basis;
    }

    public static class ClaimWipe
    {
        // "Keep" means the colony's own claims survive: the exact claimant, or - when `keep` is a faction's Commons -
        // any pawn claimant belonging to that faction (a colonist's purchase is the colony's claim).
        public static bool IsKept(ClaimantRef claimant, ClaimantRef keep)
        {
            if (claimant.Equals(keep))
            {
                return true;
            }
            return keep.Kind == ClaimantKind.Commons && keep.Faction != null
                && claimant.Kind == ClaimantKind.Pawn && claimant.Pawn != null && claimant.Pawn.Faction == keep.Faction;
        }

        // Removes every record whose claimant is not kept; the removed records are appended to `removed` when given.
        // Territorial and Situational claims are never stored as records, so they cannot appear here.
        public static int RemoveForeign(List<ClaimRecord> records, ClaimantRef keep, List<ClaimRecord> removed)
        {
            if (records == null)
            {
                return 0;
            }
            int count = 0;
            for (int i = records.Count - 1; i >= 0; i--)
            {
                if (!IsKept(records[i].Claimant, keep))
                {
                    removed?.Add(records[i]);
                    records.RemoveAt(i);
                    count++;
                }
            }
            return count;
        }
    }
}
