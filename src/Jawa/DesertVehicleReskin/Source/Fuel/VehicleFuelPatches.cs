using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Vehicles;
using Vehicles.World;
using Verse;
using Verse.AI;

namespace DesertVehicleReskin
{
    /// <summary>
    /// Harmony bootstrap. Deliberately mentions no Vehicles type: if Vehicle
    /// Framework is absent the JIT never has to resolve one, so this mod
    /// degrades to its textures instead of throwing a TypeLoadException at
    /// startup. VehicleFuelPatches is only touched once the assembly is known
    /// to be loaded.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DesertVehicleReskinMod
    {
        static DesertVehicleReskinMod()
        {
            bool vehiclesLoaded = AppDomain.CurrentDomain.GetAssemblies()
                .Any(assembly => assembly.GetName().Name == "Vehicles");
            if (!vehiclesLoaded)
            {
                Log.Warning("[DesertVehicleReskin] Vehicles (Vehicle Framework) is not loaded; "
                    + "fuel widening skipped. Textures are unaffected.");
                return;
            }

            try
            {
                VehicleFuelPatches.Apply(new Harmony("mandrake.desertvehiclereskin"));
            }
            catch (Exception ex)
            {
                Log.Error("[DesertVehicleReskin] Failed to widen vehicle fuel types: " + ex);
            }
        }
    }

    /// <summary>
    /// Widens Alpha Vehicles - Neolithic's single-def fuel lookup to any
    /// vegetable-type food, without editing SmashPhil's mod.
    ///
    /// WHY HARMONY AND NOT A SUBCLASS. Of the members that read
    /// CompProperties_FueledTravel.fuelType, only ClosestFuelAvailable is
    /// virtual. WorkGiver_RefuelVehicle.CanRefuel and
    /// CompFueledTravel.AllFuelFromInventory are static and Refunds is a
    /// non-virtual property, so an override reaches none of them - and a
    /// subclassed comp would additionally require rewriting the donor's own
    /// vehicle defs to name it.
    ///
    /// WHY A PREFIX AND NOT A WIDER CLOSURE. ClosestFuelAvailable narrows the
    /// search with ThingRequest.ForDef(Props.fuelType) BEFORE its validator
    /// closure ever runs, so widening only the closure is a silent no-op. The
    /// prefix replaces the method and searches ThingRequestGroup.HaulableEver -
    /// the same request vanilla's own ThingFilter.BestThingRequest returns for a
    /// multi-def fuel filter.
    /// </summary>
    public static class VehicleFuelPatches
    {
        public static void Apply(Harmony harmony)
        {
            MethodInfo closestFuel = AccessTools.Method(typeof(CompFueledTravel),
                nameof(CompFueledTravel.ClosestFuelAvailable));
            MethodInfo inventoryFuel = AccessTools.Method(typeof(CompFueledTravel),
                nameof(CompFueledTravel.AllFuelFromInventory));

            if (closestFuel == null || inventoryFuel == null)
            {
                Log.Error("[DesertVehicleReskin] Vehicle Framework's fuel API has moved: "
                    + "ClosestFuelAvailable=" + (closestFuel != null)
                    + " AllFuelFromInventory=" + (inventoryFuel != null)
                    + ". Fuel widening not applied.");
                return;
            }

            harmony.Patch(closestFuel,
                prefix: new HarmonyMethod(typeof(VehicleFuelPatches),
                    nameof(ClosestFuelAvailable_Prefix)));
            harmony.Patch(inventoryFuel,
                postfix: new HarmonyMethod(typeof(VehicleFuelPatches),
                    nameof(AllFuelFromInventory_Postfix)));
        }

        /// <summary>
        /// Full replacement for CompFueledTravel.ClosestFuelAvailable. Same
        /// search parameters as the donor - the donor passed only compiler
        /// defaults past the validator, so omitting them here reproduces it
        /// exactly - with the one-def ThingRequest swapped for a haulables
        /// sweep filtered by VegetableFuel.
        /// </summary>
        public static bool ClosestFuelAvailable_Prefix(CompFueledTravel __instance, Pawn pawn,
            ref Thing __result)
        {
            CompProperties_FueledTravel props = __instance.Props;
            if (props == null || props.ElectricPowered || pawn == null || pawn.Map == null)
            {
                __result = null;
                return false;
            }

            ThingDef declared = props.fuelType;

            __result = GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.ClosestTouch,
                TraverseParms.For(pawn),
                9999f,
                thing => VegetableFuel.Accepts(declared, thing.def)
                    && !thing.IsForbidden(pawn)
                    && pawn.CanReserve(thing));
            return false;
        }

        /// <summary>
        /// CompFueledTravel.AllFuelFromInventory is a static iterator that
        /// yields only things whose def == fuelType, so there is nothing to add
        /// to its result - the postfix discards it unenumerated and substitutes
        /// the widened walk over the same two sources, in the same order.
        /// </summary>
        public static void AllFuelFromInventory_Postfix(VehiclePawn vehicle,
            ref IEnumerable<Thing> __result)
        {
            __result = WidenedFuelFromInventory(vehicle);
        }

        private static IEnumerable<Thing> WidenedFuelFromInventory(VehiclePawn vehicle)
        {
            CompFueledTravel comp = vehicle?.CompFueledTravel;
            if (comp?.Props == null)
            {
                yield break;
            }
            ThingDef declared = comp.Props.fuelType;

            VehicleCaravan caravan = vehicle.GetVehicleCaravan();
            if (caravan != null)
            {
                foreach (Thing thing in caravan.AllThings)
                {
                    if (VegetableFuel.Accepts(declared, thing.def))
                    {
                        yield return thing;
                    }
                }
                yield break;
            }

            if (!vehicle.Spawned)
            {
                yield break;
            }

            List<Thing> carried = vehicle.inventory.innerContainer.InnerListForReading;
            for (int i = 0; i < carried.Count; i++)
            {
                if (VegetableFuel.Accepts(declared, carried[i].def))
                {
                    yield return carried[i];
                }
            }
        }

        // NOT PATCHED, DELIBERATELY:
        //
        // WorkGiver_RefuelVehicle.CanRefuel - measured against the decompile, its
        //   only fuel-def gate is the call to ClosestFuelAvailable, which the
        //   prefix above already answers. Its remaining use of Props.fuelType is
        //   the "NoFuelToRefuel" failure message, which is cosmetic.
        //
        // CompFueledTravel.Refunds and EjectFuel - fuel is stored as one float
        //   with no record of which def filled the tank, so there is no honest
        //   widened answer to "what comes back out". Both keep returning the
        //   declared fuelType, exactly as they do today. A cart fed potatoes and
        //   then dismantled refunds hay; that is a pre-existing property of a
        //   scalar fuel tank, not something this change introduces.
    }
}
