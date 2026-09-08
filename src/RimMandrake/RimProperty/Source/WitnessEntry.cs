using Verse;

namespace RimMandrake.Property
{
    // One witnessed-and-not-yet-fully-propagated fact inside a
    // FactionRecord: "pawn X was suspected of act A against thing T, with
    // this much confidence, at this tick." Propagation itself is never
    // ticked — FactionRecord.GetSuspicion computes how much of this has
    // "reached the top" purely from elapsed time at query time (spec item
    // 6: "propagates upward ... at the faction's security-profile rate",
    // "Decay is computed lazily").
    public class WitnessEntry : IExposable
    {
        private ClaimantKind suspectKind;
        private Pawn suspectPawn;

        public float Confidence;
        public int TimestampTicks;

        public WitnessEntry()
        {
        }

        public WitnessEntry(ClaimantRef suspect, float confidence, int timestampTicks)
        {
            suspectKind = suspect.Kind;
            suspectPawn = suspect.Pawn;
            Confidence = confidence;
            TimestampTicks = timestampTicks;
        }

        // Only Pawn suspects are meaningful here — you cannot suspect "the
        // Commons" of a crime, only a specific actor.
        public ClaimantRef Suspect =>
            suspectKind == ClaimantKind.Pawn ? ClaimantRef.OfPawn(suspectPawn) : ClaimantRef.Unclaimed;

        public void ExposeData()
        {
            Scribe_Values.Look(ref suspectKind, "suspectKind", ClaimantKind.None);
            Scribe_References.Look(ref suspectPawn, "suspectPawn");
            Scribe_Values.Look(ref Confidence, "confidence", 0f);
            Scribe_Values.Look(ref TimestampTicks, "timestampTicks", 0);
        }
    }
}
