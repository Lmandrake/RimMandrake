using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Cuisine
{
    // Ported from badoaks.meatonastick's MeatOnAStick.NameGenComp (workshop 3435027361,
    // Source/MeatOnAStick_Naming/NameGenComp.cs) - same "Roasted <first ingredient>" label
    // transform, renamed into our own namespace per STICK_FOOD_INGEST_1. Moved here from
    // src/RimUtinni/StickCuisine/ (owner ruling 2026-09-05).
    public class NameGenComp : ThingComp
    {
        private List<ThingDef> Ingredients
        {
            get
            {
                CompIngredients comp = parent.TryGetComp<CompIngredients>();
                return comp == null ? null : comp.ingredients;
            }
        }

        public override string TransformLabel(string label)
        {
            List<ThingDef> ingredients = Ingredients;
            if (ingredients.NullOrEmpty() || ingredients[0].label.NullOrEmpty())
            {
                return base.TransformLabel(label);
            }

            return "Roasted " + ingredients[0].label.ToLower();
        }
    }

    public class CompProperties_NameGen : CompProperties
    {
        public CompProperties_NameGen()
        {
            compClass = typeof(NameGenComp);
        }
    }
}
