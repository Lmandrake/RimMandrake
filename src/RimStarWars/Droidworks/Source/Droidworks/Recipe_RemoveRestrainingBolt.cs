using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Custom worker because the bolt is a whole-pawn hediff
    /// (targetsBodyPart false) - the same reason OuterRimDroids ships its own
    /// Recipe_RemoveBolt rather than vanilla Recipe_RemoveImplant
    /// (droid_ruling.md section 3 / restraining_bolt_technical.md section 2).
    /// Shaped exactly like Recipe_RebootDroid.cs's own
    /// GetPartsToApplyOn/ApplyOnPawn pair (this codebase's established
    /// pattern for a whole-pawn condition-gated surgery), reading
    /// recipe.removesHediff data-driven from the RecipeDef rather than a
    /// hardcoded DefOf, matching vanilla Recipe_RemoveImplant's own shape.
    /// Deliberately does NOT touch RSW_DW_BoltResentment - the whole point of
    /// that hediff is that it survives removal.
    ///
    /// DROIDWORKS_BOLT_PAYOFF_1 (packet B5): "resentment >= threshold ->
    /// rebellion MentalState on removal". RebellionThreshold and the reuse
    /// of vanilla's own Berserk are FOUNDRY's own call - the design doc
    /// names the consequence, not a number or a bespoke MentalStateDef.
    /// </summary>
    public class Recipe_RemoveRestrainingBolt : Recipe_Surgery
    {
        public const float RebellionThreshold = 0.6f;

        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            if (recipe.removesHediff != null && pawn.health.hediffSet.HasHediff(recipe.removesHediff))
                yield return null;
        }

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(recipe.removesHediff);
            if (h != null) pawn.health.RemoveHediff(h);

            Hediff resentment = pawn.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_BoltResentment);
            if (resentment != null && resentment.Severity >= RebellionThreshold
                && pawn.mindState?.mentalStateHandler != null
                && !pawn.InMentalState)
            {
                pawn.mindState.mentalStateHandler.TryStartMentalState(
                    RimWorld.MentalStateDefOf.Berserk, "freed from its restraining bolt after years of resentment");
            }
        }
    }
}
