using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // One recorded (exception-list) claim on a Thing: spec item 2's
    // "(claimant, strength 0-1, basis, timestamp)". Only ever created for
    // the exception bases (ClaimBasis Stolen/Purchased/ClaimFeePaid/Gifted/
    // Inherited/Looted/BattleLootOrigin) — Territorial/Situational claims
    // are virtual and never become a ClaimRecord (see ClaimEngine).
    //
    // Fields are flattened rather than embedding a ClaimantRef struct: Scribe
    // has no LookMode for a struct that itself carries reference fields, so
    // Kind/Pawn/Faction are saved directly and ClaimantRef is rebuilt by the
    // Claimant property, on demand, at read time.
    public class ClaimRecord : IExposable
    {
        private ClaimantKind claimantKind;
        private Pawn claimantPawn;
        private Faction claimantFaction;

        public float InitialStrength;
        public ClaimBasis Basis;
        public int TimestampTicks;

        public ClaimRecord()
        {
        }

        public ClaimRecord(ClaimantRef claimant, float initialStrength, ClaimBasis basis, int timestampTicks)
        {
            claimantKind = claimant.Kind;
            claimantPawn = claimant.Pawn;
            claimantFaction = claimant.Faction;
            InitialStrength = initialStrength;
            Basis = basis;
            TimestampTicks = timestampTicks;
        }

        public ClaimantRef Claimant =>
            claimantKind == ClaimantKind.Pawn ? ClaimantRef.OfPawn(claimantPawn) :
            claimantKind == ClaimantKind.Commons ? ClaimantRef.OfCommons(claimantFaction) :
            ClaimantRef.Unclaimed;

        public void ExposeData()
        {
            Scribe_Values.Look(ref claimantKind, "claimantKind", ClaimantKind.None);
            Scribe_References.Look(ref claimantPawn, "claimantPawn");
            Scribe_References.Look(ref claimantFaction, "claimantFaction");
            Scribe_Values.Look(ref InitialStrength, "initialStrength", 1f);
            Scribe_Values.Look(ref Basis, "basis", ClaimBasis.Situational);
            Scribe_Values.Look(ref TimestampTicks, "timestampTicks", 0);

            // PROPERTY_SCRIBE_AND_WITNESS_INVARIANTS_1: a ClaimRecord is only
            // ever constructed with one of the exception-list bases (see class
            // comment) - Situational is a VIRTUAL basis ClaimEngine computes
            // fresh and never assigns here. If a load ever resolves to it, the
            // save's own "basis" node was missing or corrupted; assert loudly
            // rather than silently treat a broken record as a legitimate one.
            if (Scribe.mode == LoadSaveMode.PostLoadInit && Basis == ClaimBasis.Situational)
            {
                Log.Error("[RimMandrake.Property] ClaimRecord loaded with Basis=Situational - " +
                          "this basis is virtual/computed and a ClaimRecord should never carry " +
                          "it. The save's 'basis' node was likely missing or corrupted for this " +
                          "record (claimant=" + Claimant + ").");
            }
        }
    }
}
