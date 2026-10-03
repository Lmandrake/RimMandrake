using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // PROPERTY_CLAIM_ERASE_API_1: a deterministic state proof the bridge can run with jawa/static_call
    // (type RimMandrake.Property.RM_ClaimEraseProof, method Run, no args). It builds its own unspawned items,
    // records claims, calls the API and reports; the items are destroyed afterwards so nothing leaks into a save.
    // Returns "PASS ..." or "FAIL <reason>"; never throws.
    public static class RM_ClaimEraseProof
    {
        public static string Run()
        {
            try
            {
                GameComponent_PropertyLedger ledger = GameComponent_PropertyLedger.Get();
                if (ledger == null)
                {
                    return "FAIL no ledger (no live Game)";
                }
                Faction player = Faction.OfPlayer;
                List<Faction> others = Find.FactionManager.AllFactionsListForReading.Where(f => f != player && !f.IsPlayer).Take(2).ToList();
                if (others.Count < 2)
                {
                    return "FAIL need two non-player factions on the world, found " + others.Count;
                }
                ClaimantRef colony = ClaimantRef.OfCommons(player);
                ClaimantRef x = ClaimantRef.OfCommons(others[0]);
                ClaimantRef y = ClaimantRef.OfCommons(others[1]);
                ThingDef gun = DefDatabase<ThingDef>.GetNamedSilentFail("Gun_Revolver");
                if (gun == null)
                {
                    return "FAIL Gun_Revolver def missing";
                }
                Thing a = ThingMaker.MakeThing(gun), b = ThingMaker.MakeThing(gun), c = ThingMaker.MakeThing(gun);
                int now = Find.TickManager.TicksGame;
                var made = new List<Thing> { a, b, c };
                try
                {
                    // Single-thing case: Stolen by X, BattleLootOrigin by Y, Purchased by the colony.
                    ledger.RecordClaim(a, new ClaimRecord(x, 1f, ClaimBasis.Stolen, now));
                    ledger.RecordClaim(a, new ClaimRecord(y, 1f, ClaimBasis.BattleLootOrigin, now));
                    ledger.RecordClaim(a, new ClaimRecord(colony, 1f, ClaimBasis.Purchased, now));
                    // Suspicion entry that must survive untouched.
                    FactionRecord fr = ledger.GetOrCreateFactionRecord(others[0]);
                    fr.RegisterWitness(x, 0.6f, now);
                    float suspBefore = fr.GetSuspicion(x, now);

                    int removed = ledger.ClearForeignClaims(a, colony);
                    if (removed != 2)
                    {
                        return "FAIL single: ClearForeignClaims returned " + removed + ", want 2";
                    }
                    if (!ledger.TryGetRecords(a, out List<ClaimRecord> left) || left.Count != 1 || left[0].Basis != ClaimBasis.Purchased || !left[0].Claimant.Equals(colony))
                    {
                        return "FAIL single: records left are not exactly the colony's Purchased one";
                    }

                    // Bulk case over mixed claimants: b = X Looted only; c = Y Gifted + colony Inherited.
                    ledger.RecordClaim(b, new ClaimRecord(x, 1f, ClaimBasis.Looted, now));
                    ledger.RecordClaim(c, new ClaimRecord(y, 1f, ClaimBasis.Gifted, now));
                    ledger.RecordClaim(c, new ClaimRecord(colony, 1f, ClaimBasis.Inherited, now));
                    List<WipedClaim> wiped = ledger.ClearForeignClaimsWhere(t => t == b || t == c, colony);
                    if (wiped.Count != 2)
                    {
                        return "FAIL bulk: wiped " + wiped.Count + ", want 2";
                    }
                    if (ledger.TryGetRecords(b, out List<ClaimRecord> bl) && bl.Count > 0)
                    {
                        return "FAIL bulk: b still holds records after its only claim was foreign";
                    }
                    if (!ledger.TryGetRecords(c, out List<ClaimRecord> cl) || cl.Count != 1 || cl[0].Basis != ClaimBasis.Inherited)
                    {
                        return "FAIL bulk: c should keep exactly the colony's Inherited record";
                    }
                    if (!ledger.TryGetRecords(a, out List<ClaimRecord> al) || al.Count != 1)
                    {
                        return "FAIL bulk: the filter excluded a, yet a changed";
                    }

                    float suspAfter = ledger.GetOrCreateFactionRecord(others[0]).GetSuspicion(x, now);
                    if (suspAfter != suspBefore)
                    {
                        return "FAIL FactionRecord suspicion moved: " + suspBefore + " -> " + suspAfter;
                    }
                    return "PASS single=2 bulk=2 suspicion=" + suspAfter.ToString("0.000") + " (unchanged)";
                }
                finally
                {
                    foreach (Thing t in made)
                    {
                        t.Destroy();
                    }
                }
            }
            catch (System.Exception e)
            {
                return "FAIL threw " + e.GetType().Name + ": " + e.Message;
            }
        }
    }
}
