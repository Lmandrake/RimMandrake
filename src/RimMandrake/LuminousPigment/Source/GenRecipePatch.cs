using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §6.2: "The chef's skill at cook time is written onto the meal by
    // a postfix on GenRecipe.MakeRecipeProducts (the worker is in scope
    // there -- engine_feasibility.md §2)." RimSage-verified signature
    // (Verse/GenRecipe.cs): `public static IEnumerable<Thing>
    // MakeRecipeProducts(RecipeDef recipeDef, Pawn worker, List<Thing>
    // ingredients, Thing dominantIngredient, IBillGiver billGiver, ...)`.
    //
    // It is a yield-return (iterator) method, so the postfix takes the
    // returned IEnumerable<Thing> and itself yields a wrapped sequence --
    // the standard Harmony technique for postfixing an enumerable-returning
    // method, not a guess at engine internals: the method it wraps is
    // public API, and every product it changes is post-processed exactly
    // the same regardless of which family's recipe made it.
    [HarmonyPatch(typeof(GenRecipe), nameof(GenRecipe.MakeRecipeProducts))]
    public static class Patch_GenRecipe_WriteCookSkill
    {
        public static IEnumerable<Thing> Postfix(IEnumerable<Thing> values, RecipeDef recipeDef, Pawn worker)
        {
            SteeredFamilyExtension ext = recipeDef?.GetModExtension<SteeredFamilyExtension>();
            int cookSkill = worker?.skills?.GetSkill(SkillDefOf.Cooking)?.Level ?? 0;

            foreach (Thing t in values)
            {
                CompSkillSteeredOutcome comp = (t as ThingWithComps)?.TryGetComp<CompSkillSteeredOutcome>();
                if (comp != null)
                {
                    comp.intendedFamily = ext?.family;
                    comp.cookSkill = cookSkill;
                }
                yield return t;
            }
        }
    }
}
