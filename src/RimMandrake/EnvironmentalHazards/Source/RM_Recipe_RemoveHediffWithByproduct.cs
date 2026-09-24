using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_GASLIGHT_1 (item spec §1, "the SAME reaction... is how the
    // cleaner works [cleaning tar converts it to gas]"). This is the wiring
    // SUMP_TAR_NASTINESS_1 explicitly deferred to this item: RUT_ScrubTarred
    // (Defs/RecipeDefs/RUT_Tarred_Surgery.xml, UtinniPatches) is repointed
    // from plain Recipe_RemoveHediff to this subclass in the same commit,
    // gaining a RUT_Sumpgas byproduct with no change to its own cure logic
    // (base.ApplyOnPawn, read in full — RimWorld/Recipe_RemoveHediff.cs —
    // is untouched, just called first).
    //
    // Success is read from hediff STATE rather than trusted from a return
    // value, because Recipe_RemoveHediff.ApplyOnPawn is void: capture
    // whether the pawn had the hediff before, call base, and only spawn the
    // byproduct if it is actually gone afterward. Covers both failure paths
    // for free — a failed surgery roll (CheckSurgeryFail) and "the pawn
    // didn't have it to begin with" (AvailableOnNow already gates the bill
    // from being offered at all, but a stray forced-apply call would
    // otherwise silently spawn free gas).
    public class RM_Recipe_RemoveHediffWithByproduct : Recipe_RemoveHediff
    {
        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer, List<Thing> ingredients, Bill bill)
        {
            bool hadHediffBefore = pawn.health.hediffSet.HasHediff(recipe.removesHediff);

            base.ApplyOnPawn(pawn, part, billDoer, ingredients, bill);

            if (!hadHediffBefore)
            {
                return;
            }

            if (pawn.health.hediffSet.HasHediff(recipe.removesHediff))
            {
                return; // surgery failed (CheckSurgeryFail) - hediff still present, nothing reacted
            }

            if (!(recipe is RM_RecipeDef_HediffByproduct byproductRecipe) || byproductRecipe.byproductDef == null)
            {
                return;
            }

            if (!Rand.Chance(byproductRecipe.byproductChance))
            {
                return;
            }

            Map map = pawn.MapHeld;
            if (map == null)
            {
                return;
            }

            int count = byproductRecipe.byproductCountRange.RandomInRange;
            if (count <= 0)
            {
                return;
            }

            Thing byproduct = ThingMaker.MakeThing(byproductRecipe.byproductDef);
            byproduct.stackCount = count;
            GenPlace.TryPlaceThing(byproduct, pawn.PositionHeld, map, ThingPlaceMode.Near);
        }
    }
}
