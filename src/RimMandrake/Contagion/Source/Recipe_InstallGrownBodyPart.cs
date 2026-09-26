using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1. Vanilla's own
    // Recipe_InstallNaturalBodyPart (RimWorld/Recipe_InstallNaturalBodyPart.cs,
    // read via RimSage against the decompiled 1.6 source) is already generic
    // to ANY BodyPartRecord -- it is not organ-specific. Its ApplyOnPawn
    // calls MedicalRecipesUtility.RestorePartAndSpawnAllPreviousParts, which
    // simply restores whatever <appliedOnFixedBodyParts> names. That is why
    // grown limbs needed no new hediff or recipe mechanism of their own --
    // only new RecipeDefs/ThingDefs targeting Leg/Arm through this same
    // vanilla worker.
    //
    // This subclass adds exactly one thing on top of unchanged vanilla
    // behaviour: the install-match bonus the parent item
    // (CONTAGION_GENOME_ORGAN_GROWING_1) deliberately left out. It reads
    // CompGenomeMatched off the consumed ingredient BEFORE calling
    // base.ApplyOnPawn. By this point the ingredient Thing has already been
    // Destroy()-ed -- Toils_Recipe.FinishRecipeAndStartStoringProduct calls
    // ConsumeIngredients() (which Destroy()s each ingredient) BEFORE
    // Notify_IterationCompleted() (which is what finally calls
    // ApplyOnPawn) -- confirmed via RimSage against Verse/AI/Toils_Recipe.cs
    // and RimWorld/Bill_Medical.cs. That is harmless here: Thing.Destroy()
    // despawns and flags the Thing, it does not clear ThingComp field data,
    // and `ingredients` still holds the same live object references, so the
    // comp is still readable off them.
    //
    // Patched onto the four vanilla InstallNatural<Organ> RecipeDefs too
    // (Patches/OrganInstallGenomeMatch.xml), so the exact same bonus check
    // covers organs and limbs uniformly -- a complete no-op on any
    // organ/limb carrying no CompGenomeMatched data (every ordinary,
    // non-amoeba-grown organ transplant in the game).
    public class Recipe_InstallGrownBodyPart : Recipe_InstallNaturalBodyPart
    {
        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer, List<Thing> ingredients, Bill bill)
        {
            CompGenomeMatched matched = ingredients?
                .Select(t => t?.TryGetComp<CompGenomeMatched>())
                .FirstOrDefault(c => c != null && c.sourcePawnID >= 0);

            base.ApplyOnPawn(pawn, part, billDoer, ingredients, bill);

            if (matched == null || pawn == null)
            {
                return;
            }

            // Confirm the surgery actually succeeded (CheckSurgeryFail can
            // fail the whole operation inside base.ApplyOnPawn, in which
            // case the part stays missing even though the ingredient was
            // already consumed) before granting anything.
            if (pawn.health.hediffSet.PartIsMissing(part))
            {
                return;
            }

            if (matched.sourcePawnID == pawn.thingIDNumber)
            {
                GenomeMatchBonusUtility.ApplyMatchBonus(pawn, part);
            }
            // Mismatch (someone else's matched tissue): no bonus, and
            // deliberately no penalty either -- the item's own ruling
            // against punishing mismatched tissue on the recipient.
        }
    }
}
