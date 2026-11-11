// Liquid networks build step L7 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.5, §6 L7): Outflow
// ends and the Dump tank's slow drain with no pump, on the PRODUCTION kernel (RM_LiquidNetKernel.DumpTake, FilthCount) and
// transfer service, then the production outlet, spill and settle read from source. The live bars NS_canal_from_lake_no_tank,
// NS_dump_tank_drains_without_pump and NS_intake_needs_pump are owed to a bridge session.
using System;
using System.IO;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class OutflowChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Outflow_dump_drain_takes_levels_into_channels_any_units_onto_ground", () =>
            {
                Assert(RM_LiquidNetKernel.DumpTake(5, 40, 5, true) == 5 && RM_LiquidNetKernel.DumpTake(4, 40, 5, true) == 0 && RM_LiquidNetKernel.DumpTake(5, 3, 5, true) == 0,
                    "a channel takes whole levels only (budget and stock must both cover a level)");
                Assert(RM_LiquidNetKernel.DumpTake(5, 40, 5, false) == 5 && RM_LiquidNetKernel.DumpTake(5, 3, 5, false) == 3 && RM_LiquidNetKernel.DumpTake(0, 40, 5, false) == 0,
                    "dry ground takes what the budget and stock allow");
            });

            Case("Outflow_dump_drain_conserves_without_a_pump", () =>
            {
                // a Dump tank over many settles into an outflow on dry ground: tank + spilled is constant, nothing is created
                int tank = 23, spilled = 0, settles = 0;
                while (tank > 0 && settles < 100)
                {
                    int n = RM_LiquidNetKernel.DumpTake(5, tank, 5, false);
                    RM_LiquidTransfer.Move(n, RM_TransferLeg.Store(k => tank >= k, k => { tank -= k; return true; }, k => { tank += k; return true; }),
                        RM_TransferLeg.Sink(k => spilled += k), out _);
                    settles++;
                    Assert(tank + spilled == 23, "settle " + settles + ": tank " + tank + " + spilled " + spilled + " != 23");
                }
                Assert(tank == 0 && settles == 5, "23 units drain in 5 settles at 5 a settle (" + settles + ")");
                // a blocked end: nothing leaves (the drain is never taken from the tank when the outlet cannot take it)
                int t2 = 20;
                RM_LiquidTransfer.Move(5, RM_TransferLeg.Store(k => t2 >= k, k => { t2 -= k; return true; }, k => { t2 += k; return true; }),
                    RM_TransferLeg.World(k => false, k => true), out RM_MoveOutcome o);
                Assert(t2 == 20 && o.Refused == RM_MoveRefusal.DestCan, "a blocked outlet moves nothing");
            });

            Case("Outflow_spill_filth_count", () =>
            {
                Assert(RM_LiquidNetKernel.FilthCount(5, 2) == 3 && RM_LiquidNetKernel.FilthCount(1, 2) == 1 && RM_LiquidNetKernel.FilthCount(0, 2) == 0
                       && RM_LiquidNetKernel.FilthCount(10, 2) == 5 && RM_LiquidNetKernel.FilthCount(3, 0) == 3, "one filth per unitsPerFilth units, rounded up; any spill shows");
            });

            Case("Outflow_production_outlet_spill_and_drain", () =>
            {
                string sp = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidSpill.cs"));
                RiverSwitchFlipChecks.Has(sp, @"if \(c\.InBounds\(map\) && \(RM_MapComponent_Excavation\.LevelExact \? ex\.PourRoomDl\(c, fluid, 1\) > 0 : ex\.CanPourLevel\(c, fluid\)\)\)", "a channel outlet pours only where the cell can take the liquid");
                RiverSwitchFlipChecks.Has(sp, @"if \(RM_PumpMath\.PickPour\(tk, cd, out _, out int ci\)\) \{ cell = cells\[ci\]; return RM_OutletKind\.Channel; \}", "the best cell within 1.5 of the end (PickPour, A14)");
                RiverSwitchFlipChecks.Has(sp, @"if \(\(ex != null && ex\.IsExcavated\(end\)\) \|\| !end\.Standable\(map\) \|\| end\.GetTerrain\(map\)\.IsWater\) \{ return RM_OutletKind\.Blocked; \}",
                    "a full or foreign channel, a wall or water is blocked");
                RiverSwitchFlipChecks.Has(sp, @"ThingDef own = liquid\?\.spillFilth \?\? RimMandrakeFlowWorks_DefOf\.RM_Filth_LiquidSpill;", "the liquid's own spill filth, else the generic spill");
                RiverSwitchFlipChecks.Has(sp, @"int n = RM_LiquidNetKernel\.FilthCount\(units, RM_MachinerySettings\.UnitsPerFilth\);", "one piece per unitsPerFilth");
                RiverSwitchFlipChecks.Has(sp, @"Log\.WarningOnce\(""\[FlowWorks\] a spill of """, "a spill no cell takes is logged, never silent");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"RM_LiquidNetKernel\.DumpTake\(left, tank\.storedUnits, level, RM_LiquidSpill\.WholeLevels\(kind\)\)", "the Dump drain sizes each end's share by DumpTake (whole levels into a channel or a pond)");
                RiverSwitchFlipChecks.Has(net, @"int left = System\.Math\.Max\(0, RM_HoseSettings\.DumpUnitsPerCycle\);", "the slow rate is dumpUnitsPerCycle per tank per settle");
                RiverSwitchFlipChecks.Has(net, @"DumpDrain\(map, comps, dumps\);", "the settle runs the Dump drain");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @": RM_LiquidSpill\.OutletLeg\(Map, ex, kind, dest, l, f\);", "a pump's outflow goes through the one outlet leg");
                RiverSwitchFlipChecks.Has(sp, @"default: return RM_TransferLeg\.Sink\(k => Spill\(map, cell, liquid, k\)\);", "on dry ground the outlet leg spills the level");
                RiverSwitchFlipChecks.Has(pump, @"return PourToOutflow\(ex, tanks, units\) \?\? \(string\)""RMFlow_PumpNoChannelForm""", "a liquid with no channel form still leaves by an outflow spill (G10)");
                string reel = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "CompHoseReel.cs"));
                RiverSwitchFlipChecks.Has(reel, @"if \(freeEndRole == Machinery\.RM_FreeEndRole\.Intake && !pump\) return "" Intake needs a working pump on this network\.""", "an Intake end with no working pump says so (ruling #3)");
                string defs = File.ReadAllText(Path.Combine(ContainerMatFixture.Root(), "ThingDefs", "RM_Filth_LiquidSpill.xml"));
                Assert(defs.Contains("<defName>RM_Filth_LiquidSpill</defName>") && defs.Contains("<li>Unnatural</li>") && !defs.Contains("<li>Natural</li>") && defs.Contains("ParentName=\"BaseFilth\""),
                    "the generic spill is a cleanable filth that lands on natural ground too (placementMask Unnatural: vanilla NaturalTerrainBase accepts only Unnatural; Natural was refused on Soil, SPILL_FILTH_FIX_SOIL_SAYS_NO)");
            });
        }
    }
}
