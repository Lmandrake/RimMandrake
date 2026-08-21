using RimWorld;
using Verse;

namespace DesertVehicleReskin
{
    /// <summary>
    /// What a draught vehicle will eat.
    ///
    /// Alpha Vehicles - Neolithic gives each cart exactly ONE fuel ThingDef
    /// (Hay for Chariot / WarChariot / OxCart / CoveredCarriage, Kibble for
    /// DogSled) because Vehicles.CompProperties_FueledTravel has a single
    /// `ThingDef fuelType` field and no ThingFilter anywhere on it. There is no
    /// XML route to widen that; this class is the widened rule and
    /// VehicleFuelPatches is what makes the donor's code ask it.
    ///
    /// The rule (DECIDE, VEHICLE_FUEL_ACCEPTS_VEGETABLES_1): a nutrition-giving
    /// ingestible whose foodType intersects Plant | VegetableOrFruit | Meal,
    /// excluding Meat / AnimalProduct and excluding anything with a drugCategory.
    /// No defName is enumerated anywhere, so a modded crop qualifies the moment
    /// it is loaded.
    /// </summary>
    public static class VegetableFuel
    {
        /// <summary>Food classes a herbivore team will pull for.</summary>
        public const FoodTypeFlags Accepted =
            FoodTypeFlags.Plant | FoodTypeFlags.VegetableOrFruit | FoodTypeFlags.Meal;

        /// <summary>Food classes that disqualify a def outright.</summary>
        public const FoodTypeFlags Rejected =
            FoodTypeFlags.Meat | FoodTypeFlags.AnimalProduct;

        /// <summary>
        /// The full acceptance test for one comp: the widened vegetable rule, OR
        /// the comp's own declared fuelType.
        ///
        /// The second half is load-bearing and not merely polite. Kibble's
        /// foodType is the standalone FoodTypeFlags.Kibble flag - it does NOT
        /// carry Plant, so the vegetable rule rejects it - and Kibble is what
        /// DogSled declares. Accepting the declared type unconditionally is what
        /// guarantees nothing that fuels a vehicle today stops fuelling it.
        /// </summary>
        public static bool Accepts(ThingDef declaredFuelType, ThingDef candidate)
        {
            if (candidate == null)
            {
                return false;
            }
            if (declaredFuelType != null && candidate == declaredFuelType)
            {
                return true;
            }
            return IsVegetableFood(candidate);
        }

        /// <summary>
        /// The widened rule on its own, with no vehicle in hand. Public and
        /// static so the debug action - and any future test - can exercise
        /// exactly what the patches call.
        /// </summary>
        public static bool IsVegetableFood(ThingDef def)
        {
            if (def == null || !def.IsNutritionGivingIngestible)
            {
                return false;
            }

            IngestibleProperties ingestible = def.ingestible;
            if (ingestible == null)
            {
                return false;
            }

            // A bantha does not run on beer. Beer is excluded twice over - it is
            // Fluid|Processed|Liquor and carries no accepted flag - but a modded
            // psychoactive fruit would slip through on foodType alone.
            if (ingestible.drugCategory != DrugCategory.None)
            {
                return false;
            }

            FoodTypeFlags foodType = ingestible.foodType;
            if ((foodType & Rejected) != FoodTypeFlags.None)
            {
                return false;
            }
            return (foodType & Accepted) != FoodTypeFlags.None;
        }
    }
}
