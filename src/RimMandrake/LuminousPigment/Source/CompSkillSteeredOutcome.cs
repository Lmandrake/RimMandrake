using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §6.2/§6.5: carries the cook's skill and intended family from cook
    // time (Patch_GenRecipe_WriteCookSkill, written while the RecipeDef and
    // worker are both in scope) to eating time (RM_IngestionOutcomeDoer_
    // SteeredFamily, which may run anywhere, anytime, on any pawn). Written
    // generic ("a general theme for Cuisine", spec §6.5) so a later Cuisine
    // dish can reuse the same comp+doer pair for its own steered outcome.
    public class CompProperties_SkillSteeredOutcome : CompProperties
    {
        public CompProperties_SkillSteeredOutcome()
        {
            compClass = typeof(CompSkillSteeredOutcome);
        }
    }

    public class CompSkillSteeredOutcome : ThingComp
    {
        // Null/empty = an unsteered dish (RM_MealDeepfirePlain): the doer
        // rolls a plain weighted-random family and ignores cookSkill.
        public string intendedFamily;
        public int cookSkill;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref intendedFamily, "intendedFamily");
            Scribe_Values.Look(ref cookSkill, "cookSkill", 0);
        }
    }
}
