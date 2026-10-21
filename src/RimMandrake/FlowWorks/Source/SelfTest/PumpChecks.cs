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
            // FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE (bar pump_hose_joins_at_side_port; he typed 2026-10-20: "No. a HOSE must
            // connect at one of the four sides. A solid pipe must only be adjacent and is then drawn undernead to the center of
            // the object as ruled previously.")
            Case("PumpPorts_hose_at_a_side_port", () =>
            {
                Assert(RM_PumpPortMath.SideOf(0, 1) == 0 && RM_PumpPortMath.SideOf(1, 0) == 1 && RM_PumpPortMath.SideOf(0, -1) == 2
                    && RM_PumpPortMath.SideOf(-1, 0) == 3, "four ports, Rot4 order");
                Assert(RM_PumpPortMath.SideOf(1, 1) < 0 && RM_PumpPortMath.SideOf(0, 0) < 0 && RM_PumpPortMath.SideOf(0, 2) < 0, "a corner is no port");
                Assert(RM_PumpPortMath.HoseMayTake(2, 50, new int[0]), "a free port takes a hose");
                Assert(!RM_PumpPortMath.HoseMayTake(-1, 40, new int[0]), "can-fail: a hose on a corner is refused");
                Assert(!RM_PumpPortMath.HoseMayTake(2, 50, new[] { 40 }), "a second hose at a port is refused (lower id keeps it)");
                Assert(RM_PumpPortMath.HoseMayTake(2, 40, new[] { 50 }), "the first hose keeps its port");
            });
            Case("PumpPorts_pipes_join_adjacent_hoses_at_ports", () =>
            {
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                // a rigid pipe joins a machine (the pump included) 8-way or under, as ruled before (pipe_meets_building_centre)
                RiverSwitchFlipChecks.Has(net, @"IEnumerable<IntVec3> around = GenAdj\.CellsAdjacent8Way\(t\);",
                    "a pipe joins a pump wherever adjacent");
                Assert(!net.Contains("PipeJoins") && !net.Contains("RM_PumpPortMath"), "can-fail: no pump-only pipe rule in the net");
                string hp = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "HosePorts.cs"));
                RiverSwitchFlipChecks.Has(hp, @"if \(t is RimMandrake\.FlowWorks\.LiquidTypes\.Building_LiquidPump pump && !PumpSideTakes\(pump, ReelSideOn\(pump, r\), r\)\)",
                    "a reel couples to a pump only at a free side port");
                RiverSwitchFlipChecks.Has(hp, @"&& !PumpSideTakes\(pump, EndSideOn\(pump, end\),", "a hose end couples to a pump only at a free side port");
                RiverSwitchFlipChecks.Has(hp, @"return RimMandrake\.FlowWorks\.Machinery\.RM_PumpPortMath\.HoseMayTake\(side, id, others\.ToArray\(\)\);",
                    "the gate is the selftested rule");
                Assert(!hp.Contains("HasPipe("), "can-fail: a pipe never blocks a hose port");
                RiverSwitchFlipChecks.Has(hp, @"if \(RawFind\(o, out _, out _, out _\) == pump", "other hoses are read geometrically (no recursion)");
            });
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
                const int U0 = RM_PumpMath.TankUnitsPerLevel;
                int room = 20 * U0;
                List<string> m = Cycle(1, new[] { 50 }, new[] { 0 }, ref room);
                Assert(m.SequenceEqual(new[] { "s0>tank" }) && room == 19 * U0, "a blocked (full) outflow: the level goes to the tanks (" + string.Join(",", m) + ")");
                room = 20 * U0;
                Assert(Cycle(1, new[] { 50 }, new[] { 5 }, ref room).SequenceEqual(new[] { "s0>o0" }) && room == 20 * U0, "an open outflow outranks the tanks");
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
                int lake = 10;
                RM_TransferLeg from = RM_TransferLeg.World(k => lake > 0, k => { lake--; return true; }, k => { lake++; return true; });
                RM_TransferLeg into = RM_TransferLeg.World(k => true, k => false);   // the pour refuses after the check
                Assert(RM_LiquidTransfer.Move(1, from, into, out RM_MoveOutcome o) == 0 && lake == 10 && o.Lost == 0, "a refused pour puts the level back into the lake");
                RM_TransferLeg dry = RM_TransferLeg.World(k => false, k => true);
                Assert(RM_LiquidTransfer.Move(1, from, dry, out _) == 0 && lake == 10, "a destination that cannot take a level is checked BEFORE the take");
            });

            Case("Pump_pond_round_trip_production", () =>
            {
                // POND_RETURN_LEG_BUILD_WATER_GOES_HOME (G2): the old case poured back through a hand-written pond++ the game did
                // not have. Now both legs use PRODUCTION arithmetic (TryDebit's CanDebit, the return leg's CreditableLevels) and
                // the production call sites are pinned below. A 20-square deep pond = 80 levels, volumePerTile 1.
                float cap = 20 * RM_Volume.LevelsPerSquare, stock = cap; int tank = 0;
                const int U = RM_PumpMath.TankUnitsPerLevel;
                for (int i = 0; i < 4; i++)
                    RM_LiquidTransfer.Move(U, RM_TransferLeg.World(k => RM_StockMath.CanDebit(false, stock, 1f), k => { stock -= 1f; return true; }),
                        RM_TransferLeg.Store(k => true, k => { tank += k; return true; }, k => { tank -= k; return true; }), out _);
                Assert(stock == cap - 4 && tank == 4 * U, "4 levels drawn = " + tank + " units");
                RM_TransferLeg intoPond = RM_TransferLeg.World(k => RM_StockMath.CreditableLevels(false, stock, cap, 1, 1f) == 1, k => { stock += 1f; return true; });
                RM_TransferLeg fromTank = RM_TransferLeg.Store(k => tank >= k, k => { tank -= k; return true; }, k => { tank += k; return true; });
                for (int i = 0; i < 4; i++)
                    Assert(RM_LiquidTransfer.Move(U, fromTank, intoPond, out _) == U, "level " + i + " poured back");
                Assert(stock == cap && tank == 0, "poured back: the pond is whole again (" + stock + ", " + tank + ")");
                tank = U;
                Assert(RM_LiquidTransfer.Move(U, fromTank, intoPond, out RM_MoveOutcome full) == 0 && tank == U && stock == cap && full.DestRefused,
                    "a full pond refuses and the tank keeps the level");
                stock = cap - 0.5f;
                Assert(RM_LiquidTransfer.Move(U, fromTank, intoPond, out _) == 0 && tank == U, "half a level of room takes nothing: whole levels or none (GPT #5)");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"string viaPond = PourToPond\(ex, tanks, units\); if \(viaPond != null\) \{ return viaPond; \} // rev 2 §3\.3: the pour also leaves through Outflow ends",
                    "Pour: dug cells first, then a pond in reach, then outflow ends");
                RiverSwitchFlipChecks.Has(pump, @"if \(!c\.InBounds\(Map\) \|\| !ex\.CanReturnLevels\(c, fluid, 1\)\) \{ continue; \}", "a pond square in reach is checked read-only first");
                RiverSwitchFlipChecks.Has(pump, @"RM_LiquidSpill\.OutletLeg\(Map, ex, RM_OutletKind\.Body, cell, poured, fluid\), out _\) == units\)", "the pond pour is the one Body outlet leg, tank removed first");
                RiverSwitchFlipChecks.Has(pump, @"k => ex\.Stock\.CreditDl\(Map, cell, k, ex\) == k\);", "a refused world-to-world move puts back exactly what it took (GPT #5)");
                string sp = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidSpill.cs"));
                RiverSwitchFlipChecks.Has(sp, @"if \(c\.InBounds\(map\) && ex\.CanReturnLevels\(c, fluid, 1\)\) \{ cell = c; return RM_OutletKind\.Body; \}", "an outflow end over a pond or its bed returns the level (G1)");
                RiverSwitchFlipChecks.Has(sp, @"case RM_OutletKind\.Body: return RM_TransferLeg\.World\(k => BodyRoomDl\(ex, cell, fluid, k\) >= k, k => BodyTake\(ex, cell, fluid, k\)\);", "the Body leg");
                Assert(sp.IndexOf("return RM_OutletKind.Body;") < sp.IndexOf("end.GetTerrain(map).IsWater) { return RM_OutletKind.Blocked; }"),
                    "the pond check runs before water terrain is called Blocked");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(!RimMandrakeFlowWorksSettings\.pondReturnLegEnabled \|\| levels <= 0 \|\| fluid == null \|\| !c\.InBounds\(map\) \|\| IsExcavated\(c\)\) \{ return false; \} RM_LiquidBody body = stock\.IndexedBodyAt\(map, c\); if \(body == null \|\| \(body\.fluid \?\? ActiveFluid\) != fluid\) \{ return false; \} return RM_StockMath\.CreditableLevels\(body\.limitless, body\.stock, body\.capacity, levels, fluid\.volumePerTile\) == levels;",
                    "CanReturnLevels: never a dug cell, never forms a body, foreign fluid refused first (GPT #6), whole levels to capacity");
                RiverSwitchFlipChecks.Has(ex, @"int took = stock\.CreditLevels\(map, c, levels, fluid\.volumePerTile, this\);", "TryReturnLevels credits through CreditLevels, the one place stock rises");
            });

            Case("Pump_pour_is_faster_than_gravity", () =>
            {
                // PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY (ruling Q3, "Keep it as faster draining"): live, the basic pump poured a
                // Dump tank at 1 level = 5 units a cycle, exactly the 5-unit gravity drain (fw_live_checks L2b 20 vs L2a 25 / 1000 ticks)
                const int U = RM_PumpMath.TankUnitsPerLevel;
                foreach (int gravity in new[] { 0, 1, U / 5, U / 2, U - 1, U, U + 1, 2 * U, 5 * U })
                    foreach (int lv in new[] { 0, 1, 2, 4 })
                        Assert(RM_PumpMath.PourLevels(lv, gravity) * U > gravity && RM_PumpMath.PourLevels(lv, gravity) >= Math.Max(1, lv),
                            "pour beats gravity " + gravity + " and never slows a station of " + lv + " levels (" + RM_PumpMath.PourLevels(lv, gravity) + ")");
                // the default gravity drain is 1,000 L = one level (RM_HoseSettings.dumpLitresPerCycle)
                Assert(RM_PumpMath.PourLevels(1, U) == 2, "the basic pump at the default one-level gravity rate pours 2 levels (2,000 L)");
                Assert(RM_PumpMath.PourLevels(2, U) == 2 && RM_PumpMath.PourLevels(4, U) == 4, "the stations keep their own (already faster) budget");
                Assert(RM_PumpMath.PourLevels(1, -3) == 1, "a negative setting never zeroes the pump");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"if \(pourMode\) \{[^}]*levels = RM_PumpMath\.PourLevels\(levels, Hose\.RM_HoseSettings\.DumpUnitsPerCycle\);",
                    "Tick raises the Pour budget through PourLevels against the live gravity setting");
            });

            Case("Pump_production_world_mover", () =>
            {
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"if \(!RM_LiquidNetKernel\.PumpNext\(sources\.Count, i => !deadSources\.Contains\(Map\.cellIndices\.CellToIndex\(sources\[i\]\.cell\)\), outflows\.Count, \(o, i\) => Outlet\(ex, outflows\[o\], null, sources\[i\]\.fluid, out _\) != RM_OutletKind\.Blocked, usedOutflows,",
                    "TryDraw chooses through PumpNext: outflows that can take the source's liquid, then the tanks");
                RiverSwitchFlipChecks.Has(pump, @"foreach \(IntVec3 c in ReachCells\(\)\) \{ if \(Drawable\(ex, c, out Source s\)\) \{ list\.Add\(s\); \} \} foreach \(RM_NetPort p in RM_LiquidNet\.PortsOf\(this, RM_FreeEndRole\.Intake\)\)",
                    "sources: the pump's own reach first, then its Intake ends");
                RiverSwitchFlipChecks.Has(pump, @"if \(ex\.IsExcavated\(c\) && ex\.WaterDlAt\(c\) > 0\) // a thin sheet \(no whole notch\) is drawable too \{[^}]*\} if \(ex\.IsSourceCell\(c\) && ex\.Stock\.CanSupply\(Map, c, ex\)\)",
                    "a source is a channel cell with fill or a body's source cell (never a dry nozzle cell, A13)");
                RiverSwitchFlipChecks.Has(pump, @"return p\?\.Cell is IntVec3 end \? RM_LiquidSpill\.Outlet\(Map, ex, end, liquid \?\? LiquidFor\(fluid\), fluid, out cell\) : RM_OutletKind\.Blocked;",
                    "an outflow's cell comes from RM_LiquidSpill.Outlet (CanPourLevel + PickPour within 1.5; OutflowChecks pins it)");
                RiverSwitchFlipChecks.Has(pump, @": RM_LiquidSpill\.OutletLeg\(Map, ex, kind, dest, l, f\);", "world to world: the destination leg is the one outlet leg (checked first)");
                RiverSwitchFlipChecks.Has(pump, @"\? RM_TransferLeg\.World\(k => ex\.IsExcavated\(cell\) && ex\.WaterDlAt\(cell\) >= k, k => ex\.TryTakeDl\(cell, k, out _\) == k, k => ex\.TryPourDl\(cell, f, k\)\)",
                    "world to world: a channel take is put back on a refusal");
                RiverSwitchFlipChecks.Has(pump, @"List<Building_LiquidTank> tanks = NetTanks\(\)\.Where\(t => !Hose\.RM_HoseSettings\.tankModesEnabled \|\| t\.EffectiveMode == RM_TankMode\.Dump\)\.ToList\(\);",
                    "pour drains Dump tanks only (Store tanks are never poured)");
                RiverSwitchFlipChecks.Has(pump, @"int levels = System\.Math\.Max\(1, Ext\?\.levelsPerCycle \?\? 1\); usedOutflows\.Clear\(\);", "one budget per cycle, outflows reset per cycle");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"private bool CanPourLevelWhole\(IntVec3 c, FluidDef fluid\) \{[^}]*\} int i = map\.cellIndices\.CellToIndex\(c\); return RoomNotches\(i\) > 0 && InputAllowed\(fluid\) && RM_StockMath\.FluidsCompatible\(WetDug\(i\), FluidAt\(c\), fluid\);",
                    "CanPourLevel is TryPourLevel's own test, read-only (room in decilitres' truth: WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES)");
                RiverSwitchFlipChecks.Has(ex, @"if \(RoomNotches\(map\.cellIndices\.CellToIndex\(c\)\) <= 0\) \{ return false;",
                    "TryPourLevel refuses a part-filled top notch: no pour can push a cell past its brim");
            });
        }
    }
}
