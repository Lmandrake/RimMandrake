using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // The claim-resolution step of the event spine: "whose claim is this,
    // how strong, decayed to what." Combines the recorded (exception-list)
    // claims from the ledger with the virtual claims computed fresh from
    // the Thing's current state, then picks a winner by spec item 4's
    // "resolution follows narrative proximity" rule: the most-resolved
    // party wins — approximated here as (decayed strength, then
    // specificity Pawn > Commons, then recency).
    public static class ClaimEngine
    {
        public static ClaimResolution? ResolveClaim(Thing thing, int nowTick)
        {
            if (thing == null) return null;

            var candidates = new List<ClaimResolution>();

            GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
            if (ledger != null && ledger.TryGetRecords(thing, out List<ClaimRecord> records))
            {
                float recognizability = RecognizabilityUtility.Score(thing);
                for (int i = 0; i < records.Count; i++)
                {
                    ClaimRecord rec = records[i];
                    if (IsGhost(rec.Claimant)) continue;
                    int age = nowTick - rec.TimestampTicks;
                    float strength = ClaimDecay.EffectiveStrength(rec.InitialStrength, age, recognizability);
                    if (strength <= 0f) continue;

                    candidates.Add(new ClaimResolution(rec.Claimant, strength, rec.Basis, isRecorded: true, timestampTicks: rec.TimestampTicks));
                }
            }

            ClaimResolution? virtualClaim = ResolveVirtualClaim(thing, nowTick);
            if (virtualClaim.HasValue) candidates.Add(virtualClaim.Value);

            if (candidates.Count == 0) return null;

            candidates.Sort((a, b) =>
            {
                int byStrength = b.EffectiveStrength.CompareTo(a.EffectiveStrength);
                if (byStrength != 0) return byStrength;

                int bySpecificity = Specificity(b.Claimant).CompareTo(Specificity(a.Claimant));
                if (bySpecificity != 0) return bySpecificity;

                return b.TimestampTicks.CompareTo(a.TimestampTicks);
            });

            return candidates[0];
        }

        // A recorded claim's Pawn/Faction reference can go null after the
        // record itself survives a save/load - a dead non-colonist raider
        // Discard()ed from the save, or (in principle) a faction removed
        // with a mod. Kind still says Pawn/Commons, so without this an
        // unresolvable claimant becomes a "ghost owner": it scores the
        // highest Specificity() of any claimant kind, so ClaimEngine picks
        // it as the winner, and PropertyEngine.IsAuthorized then compares
        // against it and finds no actor that ever equals it - the thing is
        // permanently unauthorized to use by anyone.
        private static bool IsGhost(ClaimantRef c) =>
            (c.Kind == ClaimantKind.Pawn && c.Pawn == null) ||
            (c.Kind == ClaimantKind.Commons && c.Faction == null);

        private static int Specificity(ClaimantRef c)
        {
            switch (c.Kind)
            {
                case ClaimantKind.Pawn: return 2;
                case ClaimantKind.Commons: return 1;
                default: return 0;
            }
        }

        // Territorial/Situational — spec item 3: computed, ZERO storage.
        // Situational: a specific Pawn currently possesses the Thing
        //   (equipped weapon, worn apparel, carried inventory item) —
        //   spec item 4's per-colonist claimant, and symmetrically any
        //   NPC's or guest's own gear.
        // Territorial: no specific possessor, but the Thing belongs to a
        //   faction (map-owned building/item/stockpile) — that faction's
        //   Commons claimant. This is the generic engine default for
        //   "everything faction-owned-but-unassigned"; refining which
        //   faction-owned items are actually personal (spec item 4: "the
        //   Clan claimant holds only the survival spine ... Everything
        //   else is someone's") needs campaign judgment this fabric
        //   cannot supply — see the status report's named design fork.
        private static ClaimResolution? ResolveVirtualClaim(Thing thing, int nowTick)
        {
            Pawn possessor = FindPossessor(thing);
            if (possessor != null)
            {
                return new ClaimResolution(
                    ClaimantRef.OfPawn(possessor), PropertyTuning.SituationalClaimStrength,
                    ClaimBasis.Situational, isRecorded: false, timestampTicks: nowTick);
            }

            if (thing.Faction != null)
            {
                return new ClaimResolution(
                    ClaimantRef.OfCommons(thing.Faction), PropertyTuning.TerritorialClaimStrength,
                    ClaimBasis.Territorial, isRecorded: false, timestampTicks: nowTick);
            }

            return null;
        }

        private static Pawn FindPossessor(Thing thing)
        {
            IThingHolder holder = thing.ParentHolder;
            if (holder is Pawn_EquipmentTracker eq) return eq.pawn;
            if (holder is Pawn_ApparelTracker ap) return ap.pawn;
            if (holder is Pawn_InventoryTracker inv) return inv.pawn;
            if (holder is Pawn_CarryTracker carry) return carry.pawn;
            return null;
        }
    }
}
