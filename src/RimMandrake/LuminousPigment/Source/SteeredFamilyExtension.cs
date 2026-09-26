using Verse;

namespace RimMandrake.LuminousPigment
{
    // Tags one of the 14 steered RM_MealDeepfire_<Family> RecipeDefs with
    // which DeepfireFamilies key it aims for (Defs/RecipeDefs/
    // RM_RecipeDeepfireMeals.xml). Read by Patch_GenRecipe_WriteCookSkill at
    // cook time; RM_MealDeepfirePlain carries no extension, which is how the
    // doer tells "steered" from "plain" apart.
    public class SteeredFamilyExtension : DefModExtension
    {
        public string family;
    }
}
