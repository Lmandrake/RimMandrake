using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // The whole fabric's persisted state, and ONLY the exception-list state
    // — spec item 3: "Claims are virtual by default, recorded by exception
    // ... zero storage. ... no comp on ten thousand rocks." This is a single
    // GameComponent (auto-instantiated by vanilla's Game.FillComponents via
    // reflection over GameComponent subclasses — no Harmony, no explicit
    // registration needed, same recipe as Ninefold's GameComponent_Ninefold)
    // holding two sparse dictionaries:
    //
    //   claimRecords    — Thing -> its recorded (exception-basis) claims.
    //                      A Thing with no entry here has ONLY virtual
    //                      claims; that is the overwhelmingly common case
    //                      and costs nothing.
    //   factionRecords  — Faction -> that faction's suspicion ledger
    //                      (WitnessEntry list inside FactionRecord).
    //
    // Both are populated lazily, on first write, never pre-seeded.
    public class GameComponent_PropertyLedger : GameComponent
    {
        private Dictionary<Thing, ClaimRecordList> claimRecords = new Dictionary<Thing, ClaimRecordList>();
        private Dictionary<Faction, FactionRecord> factionRecords = new Dictionary<Faction, FactionRecord>();

        // Scribe working lists (dictionary Look needs these as scratch space).
        private List<Thing> workingClaimKeys;
        private List<ClaimRecordList> workingClaimValues;
        private List<Faction> workingFactionKeys;
        private List<FactionRecord> workingFactionValues;

        public GameComponent_PropertyLedger(Game game)
        {
        }

        public static GameComponent_PropertyLedger Get()
        {
            return Current.Game?.GetComponent<GameComponent_PropertyLedger>();
        }

        // --- Claim records -----------------------------------------------

        public bool TryGetRecords(Thing thing, out List<ClaimRecord> records)
        {
            if (thing != null && claimRecords.TryGetValue(thing, out ClaimRecordList list))
            {
                records = list.Records;
                return true;
            }
            records = null;
            return false;
        }

        // Appends a new recorded claim for `thing`. Deliberately additive,
        // never replacing — spec item 5's origin-claim-plus-current-claim
        // shape (a looted item keeps BOTH the original owner's record and
        // the looter's) depends on old records staying in the set; decay
        // and ClaimEngine's resolution ordering are what make the newest/
        // strongest one win a query, not deletion.
        public void RecordClaim(Thing thing, ClaimRecord record)
        {
            if (thing == null || record == null) return;

            // The ledger keys on the Thing INSTANCE. A stackable item does not
            // preserve instance identity: TryAbsorbStack merges a hauled stack
            // into a resident one and Destroy()s the hauled Thing (the record
            // dies with it, then produces the destroyed-key warning this class
            // already purges for), and SplitOff mints a brand-new Thing with no
            // ledger entry at all (the split-off half is claim-free). Recording
            // a claim on a stackable item is therefore unreliable rather than
            // wrong, and unreliable-but-silent is worse than refused: a claim
            // basis worth recording (a theft, a purchase) is exactly the kind
            // of thing a player would notice going missing.
            if (thing.def.stackLimit > 1 && Prefs.DevMode)
            {
                Log.Warning("[RimMandrake.Property] Recording a claim on a stackable Thing (" + thing.def.defName
                    + ", stackLimit " + thing.def.stackLimit + ") - the claim will be lost on the next stack "
                    + "merge and will not follow a SplitOff. Known limitation, not yet solved.");
            }

            if (!claimRecords.TryGetValue(thing, out ClaimRecordList list))
            {
                list = new ClaimRecordList();
                claimRecords[thing] = list;
            }
            list.Records.Add(record);
        }

        // PROPERTY_CLAIM_ERASE_API_1: wipe other parties' stored claims. Generic, no rite knowledge: callers decide when.
        // Removes every stored record on `thing` whose claimant is not `keep` (the colony); returns how many went.
        // A Thing whose list empties drops its entry. FactionRecord suspicion is deliberately untouched.
        public int ClearForeignClaims(Thing thing, ClaimantRef keep)
        {
            if (thing == null || !claimRecords.TryGetValue(thing, out ClaimRecordList list))
            {
                return 0;
            }
            int removed = ClaimWipe.RemoveForeign(list.Records, keep, null);
            if (list.Records.Count == 0)
            {
                claimRecords.Remove(thing);
            }
            return removed;
        }

        // The same over every Thing the ledger holds records for that passes `filter` (null = all). Returns what was
        // wiped, one entry per removed record, so a caller can write the letter naming each item and whose claim went.
        public List<WipedClaim> ClearForeignClaimsWhere(System.Func<Thing, bool> filter, ClaimantRef keep)
        {
            var wiped = new List<WipedClaim>();
            var keys = new List<Thing>(claimRecords.Keys);
            for (int k = 0; k < keys.Count; k++)
            {
                Thing thing = keys[k];
                if (thing == null || (filter != null && !filter(thing)))
                {
                    continue;
                }
                var gone = new List<ClaimRecord>();
                ClearForeignClaimsInto(thing, keep, gone);
                for (int i = 0; i < gone.Count; i++)
                {
                    wiped.Add(new WipedClaim { Thing = thing, Claimant = gone[i].Claimant, Basis = gone[i].Basis });
                }
            }
            return wiped;
        }

        private void ClearForeignClaimsInto(Thing thing, ClaimantRef keep, List<ClaimRecord> removed)
        {
            if (!claimRecords.TryGetValue(thing, out ClaimRecordList list))
            {
                return;
            }
            ClaimWipe.RemoveForeign(list.Records, keep, removed);
            if (list.Records.Count == 0)
            {
                claimRecords.Remove(thing);
            }
        }

        // --- Faction records -----------------------------------------------

        public FactionRecord GetOrCreateFactionRecord(Faction faction)
        {
            if (faction == null) return null;

            if (!factionRecords.TryGetValue(faction, out FactionRecord record))
            {
                record = new FactionRecord(faction);
                factionRecords[faction] = record;
            }
            return record;
        }

        public bool TryGetFactionRecord(Faction faction, out FactionRecord record)
        {
            if (faction != null && factionRecords.TryGetValue(faction, out record)) return true;
            record = null;
            return false;
        }

        // Nothing else ever removes a destroyed Thing's key. Without this, a
        // stolen-and-then-eaten meal (or any claimed Thing that is later
        // destroyed) keeps its Dictionary<Thing,...> entry forever:
        // Scribe_References logs a warning saving a reference to a destroyed
        // thing, and the vanilla dictionary-rebuild on load logs an error and
        // drops that entry (silently losing the paired record) while keeping
        // the destroyed Thing rooted in memory in the meantime. Called on the
        // Saving pass only, before Scribe_Collections.Look runs.
        private void PurgeDestroyedThingKeys()
        {
            List<Thing> dead = null;
            foreach (Thing t in claimRecords.Keys)
            {
                if (t == null || t.Destroyed)
                {
                    (dead ??= new List<Thing>()).Add(t);
                }
            }
            if (dead == null) return;
            foreach (Thing t in dead) claimRecords.Remove(t);
        }

        public override void ExposeData()
        {
            base.ExposeData();

            if (Scribe.mode == LoadSaveMode.Saving)
            {
                PurgeDestroyedThingKeys();
            }

            Scribe_Collections.Look(
                ref claimRecords, "claimRecords", LookMode.Reference, LookMode.Deep,
                ref workingClaimKeys, ref workingClaimValues);

            Scribe_Collections.Look(
                ref factionRecords, "factionRecords", LookMode.Reference, LookMode.Deep,
                ref workingFactionKeys, ref workingFactionValues);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (claimRecords == null) claimRecords = new Dictionary<Thing, ClaimRecordList>();
                if (factionRecords == null) factionRecords = new Dictionary<Faction, FactionRecord>();
            }
        }
    }
}
