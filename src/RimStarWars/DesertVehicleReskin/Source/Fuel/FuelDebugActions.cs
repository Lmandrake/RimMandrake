using System.Collections.Generic;
using System.Linq;
using System.Text;
using LudeonTK;
using RimWorld;
using Vehicles;
using Verse;

namespace RimMandrake.DesertVehicleReskin
{
    /// <summary>
    /// The verify step for VEHICLE_FUEL_ACCEPTS_VEGETABLES_1: what does the
    /// widened lookup actually accept, on a real map, against the real def
    /// database with every mod's crops in it.
    /// </summary>
    public static class FuelDebugActions
    {
        // RawMeat is deliberately in the reject list even though no such def
        // exists: it is the name the item's verify line uses, and the action
        // reports "NO SUCH DEF" rather than a silent pass. Meat_Cow is the real
        // meat def standing in for it.
        private static readonly string[] MustAccept =
            { "Hay", "RawPotatoes", "RawCorn", "RawBerries", "RawFungus" };
        private static readonly string[] MustReject =
            { "RawMeat", "Meat_Cow", "Meat_Human", "Milk", "Beer" };

        [DebugAction("Vehicles", "List widened vehicle fuel",
            allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ListWidenedVehicleFuel()
        {
            List<ThingDef> accepted = DefDatabase<ThingDef>.AllDefsListForReading
                .Where(VegetableFuel.IsVegetableFood)
                .OrderBy(def => def.defName)
                .ToList();

            StringBuilder report = new StringBuilder();
            report.AppendLine("[RimMandrake.DesertVehicleReskin] widened vehicle fuel — "
                + accepted.Count + " ThingDefs pass the vegetable rule:");
            report.AppendLine(string.Join(", ", accepted.Select(def => def.defName)));

            report.AppendLine();
            report.AppendLine("Per vehicle, including its own declared fuelType:");
            foreach (VehicleDef vehicleDef in DefDatabase<VehicleDef>.AllDefsListForReading
                .OrderBy(def => def.defName))
            {
                CompProperties_FueledTravel props = vehicleDef.comps?
                    .OfType<CompProperties_FueledTravel>().FirstOrDefault();
                if (props == null || props.ElectricPowered)
                {
                    continue;
                }
                int count = DefDatabase<ThingDef>.AllDefsListForReading
                    .Count(def => VegetableFuel.Accepts(props.fuelType, def));
                report.AppendLine("  " + vehicleDef.defName
                    + " declares " + (props.fuelType?.defName ?? "null")
                    + " and now accepts " + count + " defs");
            }

            report.AppendLine();
            report.AppendLine("Verify line (>=6 accepted; Hay and RawPotatoes in; "
                + "meat and Beer out):");
            report.AppendLine("  count >= 6 : " + (accepted.Count >= 6));
            foreach (string defName in MustAccept)
            {
                report.AppendLine("  accepts " + defName + " : " + Verdict(defName, true));
            }
            foreach (string defName in MustReject)
            {
                report.AppendLine("  rejects " + defName + " : " + Verdict(defName, false));
            }

            Map map = Find.CurrentMap;
            if (map != null)
            {
                List<Thing> onMap = map.listerThings
                    .ThingsInGroup(ThingRequestGroup.HaulableEver)
                    .Where(thing => VegetableFuel.IsVegetableFood(thing.def))
                    .ToList();
                report.AppendLine();
                report.AppendLine("On this map: " + onMap.Count + " haulable stacks qualify ("
                    + string.Join(", ", onMap.Select(thing => thing.def.defName).Distinct()) + ")");
            }

            Log.Message(report.ToString());
        }

        private static string Verdict(string defName, bool shouldAccept)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null)
            {
                return "NO SUCH DEF (nothing proven)";
            }
            bool got = VegetableFuel.IsVegetableFood(def);
            return (got == shouldAccept ? "PASS" : "FAIL") + " (accepted=" + got + ")";
        }
    }
}
