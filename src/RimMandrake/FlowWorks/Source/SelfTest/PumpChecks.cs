// Liquid networks build step L6 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.3, §6 L6): the
// pump as the only mover out of the world, on the PRODUCTION chooser (RM_LiquidNetKernel.PumpNext) and transfer service, then
// the production pump read from source. Gates: lake -> canal with no tank; a blocked outflow falls to tanks; pour ignores Store
// tanks; the budget is shared across intakes; a pond round trip conserves.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PumpChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>One pump cycle over fake world cells: sources (levels), outflow cells (room), tank room in units; returns the
        /// moves made, run exactly as Building_LiquidPump.Tick runs the chooser (budget levels, a used outflow takes no more).</summary>
        private static List<string> Cycle(int budget, int[] sourceLevels, int[] outflowRoom, ref int tankRoom, int cycle = 0)
        {
            var moves = new List<string>();
            var used = new HashSet<int>();
            var dead = new HashSet<int>();
            int room = tankRoom;
            for (int i = 0; i < budget; i++)
            {
                int[] src = sourceLevels, outr = outflowRoom;
                if (!RM_LiquidNetKernel.PumpNext(src.Length, s => !dead.Contains(s) && src[s] > 0, outr.Length, (o, s) => outr[o] > 0, used,
                        s => room >= RM_PumpMath.TankUnitsPerLevel, cycle, out int si, out int oi))
                    break;
                if (oi >= 0)
                {
                    // world -> world through the transfer service: the take is put back if the pour is refused
                    int s0 = si, o0 = oi;
                    RM_TransferLeg from = RM_TransferLeg.World(k => src[s0] > 0, k => { src[s0]--; return true; }, k => { src[s0]++; return true; });
                    RM_TransferLeg into = RM_TransferLeg.World(k => outr[o0] > 0, k => { outr[o0]--; return true; });
                    if (RM_LiquidTransfer.Move(1, from, into, out _) == 1) moves.Add("s" + si + ">o" + oi);
                    used.Add(oi);
                    continue;
                }
                src[si]--;
                room -= RM_PumpMath.TankUnitsPerLevel;
                moves.Add("s" + si + ">tank");
            }
            tankRoom = room;
            return moves;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Pump_lake_to_canal_with_no_tank", () =>
            {
                int noTank = 0;
                int[] lake = { 50 }, canal = { 3 };
                List<string> m = Cycle(1, lake, canal, ref noTank);
                Assert(m.SequenceEqual(new[] { "s0>o0" }) && lake[0] == 49 && canal[0] == 2, "an Intake in the lake and an Outflow in the canal move a level, no tank (" + string.Join(",", m) + ")");
                // can-fail: with no outflow and no tank the same pump moves nothing
                Assert(Cycle(1, new[] { 50 }, new int[0], ref noTank).Count == 0, "can-fail: no outflow and no tank: nothing moves");
            });

            Case("Pump_blocked_outflow_falls_to_tanks", () =>
            {
                int room = 100;
                List<string> m = Cycle(1, new[] { 50 }, new[] { 0 }, ref room);
                Assert(m.SequenceEqual(new[] { "s0>tank" }) && room == 95, "a blocked (full) outflow: the level goes to the tanks (" + string.Join(",", m) + ")");
                room = 100;
                Assert(Cycle(1, new[] { 50 }, new[] { 5 }, ref room).SequenceEqual(new[] { "s0>o0" }) && room == 100, "an open outflow outranks the tanks");
            });

            Case("Pump_budget_is_shared_across_intakes_and_outflows", () =>
            {
                int room = 100;
                List<string> m = Cycle(1, new[] { 50, 50, 50 }, new[] { 9, 9 }, ref room);
                Assert(m.Count == 1, "levelsPerCycle 1 with three intakes and two outflows: one level in total (" + string.Join(",", m) + ")");
                room = 0;
                List<string> m3 = Cycle(3, new[] { 50 }, new[] { 9, 9 }, ref room);
                Assert(m3.SequenceEqual(new[] { "s0>o0", "s0>o1" }), "each outflow takes at most one level per cycle; with no tank room the third level stays (" + string.Join(",", m3) + ")");
                room = 0;
                Assert(Cycle(1, new[] { 50 }, new[] { 9, 9 }, ref room, 1).SequenceEqual(new[] { "s0>o1" }), "outflows are rotated by cycle");
                room = 0;
                Assert(Cycle(1, new[] { 0, 50 }, new[] { 9 }, ref room).SequenceEqual(new[] { "s1>o0" }), "a dry source is skipped (reach first, then intakes)");
            });

            Case("Pump_world_to_world_refusal_puts_the_take_back", () =>
            {
                int lake = 10, canal = 2;
                RM_TransferLeg from = RM_TransferLeg.World(k => lake > 0, k => { lake--; return true; }, k => { lake++; return true; });
                RM_TransferLeg into = RM_TransferLeg.World(k => true, k => false);   // the pour refuses after the check
                Assert(RM_LiquidTransfer.Move(1, from, into, out RM_MoveOutcome o) == 0 && lake == 10 && canal == 2 && o.Lost == 0, "a refused pour puts the level back into the lake");
                RM_TransferLeg dry = RM_TransferLeg.World(k => false, k => true);
                Assert(RM_LiquidTransfer.Move(1, from, dry, out _) == 0 && lake == 10, "a destination that cannot take a level is checked BEFORE the take");
            });

            Case("Pump_pond_round_trip_conserves", () =>
            {
                // draw 4 levels from a pond into a tank, then pour them back: levels out == levels back, units in == units out
                int pond = 20, tank = 0;
                const int U = RM_PumpMath.TankUnitsPerLevel;
                for (int i = 0; i < 4; i++)
                    RM_LiquidTransfer.Move(U, RM_TransferLeg.World(k => pond > 0, k => { pond--; return true; }),
                        RM_TransferLeg.Store(k => true, k => { tank += k; return true; }, k => { tank -= k; return true; }), out _);
                Assert(pond == 16 && tank == 4 * U, "4 levels drawn = " + tank + " units");
                for (int i = 0; i < 4; i++)
                    RM_LiquidTransfer.Move(U, RM_TransferLeg.Store(k => tank >= k, k => { tank -= k; return true; }, k => { tank += k; return true; }),
                        RM_TransferLeg.World(k => true, k => { pond++; return true; }), out _);
                Assert(pond == 20 && tank == 0, "poured back: the pond is whole again (" + pond + ", " + tank + ")");
            });

            Case("Pump_production_world_mover", () =>
            {
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"if \(!RM_LiquidNetKernel\.PumpNext\(sources\.Count, i => !deadSources\.Contains\(i\), outflows\.Count, \(o, i\) => Outlet\(ex, outflows\[o\], null, sources\[i\]\.fluid, out _\) != RM_OutletKind\.Blocked, usedOutflows,",
                    "TryDraw chooses through PumpNext: outflows that can take the source's liquid, then the tanks");
                RiverSwitchFlipChecks.Has(pump, @"foreach \(IntVec3 c in ReachCells\(\)\) \{ if \(Drawable\(ex, c, out Source s\)\) \{ list\.Add\(s\); \} \} foreach \(RM_NetPort p in RM_LiquidNet\.PortsOf\(this, RM_FreeEndRole\.Intake\)\)",
                    "sources: the pump's own reach first, then its Intake ends");
                RiverSwitchFlipChecks.Has(pump, @"if \(ex\.IsExcavated\(c\) && ex\.FillAt\(c\) > 0\) \{[^}]*\} if \(ex\.IsSourceCell\(c\) && ex\.Stock\.CanSupply\(Map, c, ex\)\)",
                    "a source is a channel cell with fill or a body's source cell (never a dry nozzle cell, A13)");
                RiverSwitchFlipChecks.Has(pump, @"return p\?\.Cell is IntVec3 end \? RM_LiquidSpill\.Outlet\(Map, ex, end, liquid \?\? LiquidFor\(fluid\), fluid, out cell\) : RM_OutletKind\.Blocked;",
                    "an outflow's cell comes from RM_LiquidSpill.Outlet (CanPourLevel + PickPour within 1.5; OutflowChecks pins it)");
                RiverSwitchFlipChecks.Has(pump, @": kind == RM_OutletKind\.Channel \? RM_TransferLeg\.World\(k => ex\.CanPourLevel\(dest, f\), k => ex\.TryPourLevel\(dest, f\)\)", "world to world: the destination is checked first");
                RiverSwitchFlipChecks.Has(pump, @"\? RM_TransferLeg\.World\(k => ex\.IsExcavated\(cell\) && ex\.FillAt\(cell\) > 0, k => ex\.TryTakeLevel\(cell, out _\), k => ex\.TryPourLevel\(cell, f\)\)",
                    "world to world: a channel take is put back on a refusal");
                RiverSwitchFlipChecks.Has(pump, @"List<Building_LiquidTank> tanks = NetTanks\(\)\.Where\(t => !Hose\.RM_HoseSettings\.tankModesEnabled \|\| t\.EffectiveMode == RM_TankMode\.Dump\)\.ToList\(\);",
                    "pour drains Dump tanks only (Store tanks are never poured)");
                RiverSwitchFlipChecks.Has(pump, @"int levels = System\.Math\.Max\(1, Ext\?\.levelsPerCycle \?\? 1\); usedOutflows\.Clear\(\);", "one budget per cycle, outflows reset per cycle");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"public bool CanPourLevel\(IntVec3 c, FluidDef fluid\) \{[^}]*\} int f = FillAt\(c\); return f < DepthAt\(c\) && InputAllowed\(fluid\) && RM_StockMath\.FluidsCompatible\(f > 0, FluidAt\(c\), fluid\);",
                    "CanPourLevel is TryPourLevel's own test, read-only");
            });
        }
    }
}
