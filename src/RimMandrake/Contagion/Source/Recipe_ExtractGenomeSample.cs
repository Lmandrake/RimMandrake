using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1. Modeled directly on vanilla's
    // Recipe_ExtractHemogen (Source/RimWorld/Recipe_ExtractHemogen.cs,
    // read via RimSage) — the closest existing vanilla precedent for
    // "a surgery that draws something from a living colonist and spawns a
    // portable item," and the item's own question 3 ("how a genome is taken
    // from a colonist — an existing sampling operation, or something new")
    // is answered the same way that mechanism answers it: a bloodloss-cost
    // surgical bill, no anesthesia required, spawns a Thing near the pawn.
    public class Recipe_ExtractGenomeSample : Recipe_Surgery
    {
        private const float BloodlossSeverity = 0.12f;

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer, List<Thing> ingredients, Bill bill)
        {
            if (!RM_ContagionSettings.genomeOrganGrowingEnabled)
            {
                Messages.Message(
                    "The Contagion's genome-organ mechanic is disabled in Mod Settings.",
                    MessageTypeDefOf.RejectInput,
                    historical: false);
                return;
            }

            Hediff hediff = HediffMaker.MakeHediff(HediffDefOf.BloodLoss, pawn);
            hediff.Severity = BloodlossSeverity;
            pawn.health.AddHediff(hediff);

            Thing sample = ThingMaker.MakeThing(RM_ContagionDefOf.RM_GenomeSample);
            CompGenomeSample comp = sample.TryGetComp<CompGenomeSample>();
            string sourceName = pawn.Name != null ? pawn.Name.ToStringShort : pawn.LabelShort;
            comp?.SetSource(pawn.thingIDNumber, sourceName);

            if (!GenPlace.TryPlaceThing(sample, pawn.PositionHeld, pawn.MapHeld, ThingPlaceMode.Near))
            {
                Log.Error("RM_ExtractGenomeSample: could not place genome sample near " + pawn.PositionHeld);
            }

            Messages.Message(
                "A genome sample has been drawn from " + sourceName + ", ready to inject into a Contagion amoeba host.",
                pawn,
                MessageTypeDefOf.PositiveEvent,
                historical: false);
        }
    }
}
