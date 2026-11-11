// Complete shipping Tick/TryDraw/source-selection methods are extracted at build time.
// Doubles below model engine boundaries only: fixed reach/adjacency, excavation/body ledgers,
// outlet capacity/refusal, tank capacity and hose storage. Production PumpNext, PumpMath and
// LiquidTransfer run unchanged. This does not simulate terrain, topology discovery, Unity or scheduling.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest.PumpHarness
{
    internal record struct IntVec3(int x, int z = 0)
    {
        public IntVec3(int x, int y, int z) : this(x, z) { }
        public Building GetFirstBuilding(Map map) => map.pump;
        public static readonly IntVec3 Invalid = new(-1);
        public bool InBounds(Map map) => x >= 0;
    }
    internal class CellIndices
    {
        public int CellToIndex(IntVec3 cell) => cell.x;
    }
    internal class Map
    {
        public Building_LiquidPump pump;
        public CellIndices cellIndices = new();
        public RM_MapComponent_Excavation engine = new();
    }
    internal class FluidDef
    {
        public string label = "water";
    }
    internal class LiquidDef
    {
        public FluidDef canalFluid;
        public string label = "water";
    }
    internal static class DefDatabase<T>
    {
        public static List<T> AllDefsListForReading = new();
    }
    internal static class Translation
    {
        public static string Translate(this string text, params object[] args) => text;
    }
    internal static class Find
    {
        public static Map CurrentMap;
        internal class Clock { public int TicksGame; }
        public static Clock TickManager = new();
    }
    internal class Building
    {
        protected virtual void Tick() { }
    }
    internal static class TickBoundary
    {
        public static bool IsHashIntervalTick(this Building_LiquidPump pump, int interval) => true;
    }
    internal static class RimMandrakeFlowWorksSettings
    {
        public static bool liquidPumpEnabled = true;
    }
    internal static class Hose
    {
        internal static class RM_HoseSettings
        {
            public static int DumpUnitsPerCycle;
        }
    }
    internal class Power
    {
        internal class Properties { public float PowerConsumption = 10; }
        public Properties Props = new();
        public float PowerOutput;
    }
    internal class Extension { public int levelsPerCycle = 1; }
    internal class RM_LiquidBody { public FluidDef fluid; }
    internal class Stock
    {
        public Dictionary<int, long> body = new();
        public FluidDef fluid;
        public long SupplyDl(Map map, IntVec3 cell, int units, RM_MapComponent_Excavation ex) => Math.Min(units, body.GetValueOrDefault(cell.x));
        public RM_LiquidBody BodyAt(Map map, IntVec3 cell, RM_MapComponent_Excavation ex) => null;
        public bool TryDebitDl(Map map, IntVec3 cell, int amount, RM_MapComponent_Excavation ex)
        {
            if (body.GetValueOrDefault(cell.x) < amount) return false;
            body[cell.x] -= amount;
            return true;
        }
        public long CreditDl(Map map, IntVec3 cell, int amount, RM_MapComponent_Excavation ex)
        {
            body[cell.x] = body.GetValueOrDefault(cell.x) + amount;
            return amount;
        }
    }
    internal class RM_MapComponent_Excavation
    {
        public static bool LevelExact;
        public Dictionary<int, long> water = new();
        public HashSet<int> refuseTake = new();
        public int takeCalls;
        public FluidDef ActiveFluid = new();
        public Stock Stock = new();
        public bool IsExcavated(IntVec3 cell) => water.ContainsKey(cell.x);
        public bool IsSourceCell(IntVec3 cell) => Stock.body.ContainsKey(cell.x);
        public long WaterDlAt(IntVec3 cell) => water.GetValueOrDefault(cell.x);
        public FluidDef FluidAt(IntVec3 cell) => ActiveFluid;
        public long TryTakeDl(IntVec3 cell, int amount, out FluidDef fluid)
        {
            fluid = ActiveFluid;
            takeCalls++;
            if (!LevelExact) amount -= amount % RM_PumpMath.TankUnitsPerLevel;
            if (amount <= 0) return 0;
            if (refuseTake.Contains(cell.x) || WaterDlAt(cell) < amount) return 0;
            water[cell.x] -= amount;
            return amount;
        }
        public bool TryPourDl(IntVec3 cell, FluidDef fluid, int amount)
        {
            water[cell.x] = WaterDlAt(cell) + amount;
            return true;
        }
    }
    internal static class RM_SuperdeepTrap
    {
        public static RM_MapComponent_Excavation EngineOf(Map map) => map.engine;
    }
    internal record TargetInfo(IntVec3 cell, Map map);
    internal static class GenAdj
    {
        public static IEnumerable<IntVec3> CellsAdjacent8Way(TargetInfo target) => Array.Empty<IntVec3>();
    }
    internal enum RM_FreeEndRole { Intake, Outflow }
    internal enum RM_OutletKind { Blocked, Channel, Body }
    internal class RM_NetPort
    {
        public IntVec3? Cell;
        public long room = 10000, received;
        public bool refuse;
    }
    internal class Building_LiquidTank
    {
        public int room, stored;
        public object mutationActor;
        public bool CanAccept(LiquidDef liquid, int amount) => room >= amount;
        public bool TryAddLiquid(LiquidDef liquid, int amount)
        {
            if (!CanAccept(liquid, amount)) return false;
            mutationActor = RM_LiquidTheft.Current;
            room -= amount;
            stored += amount;
            return true;
        }
        public bool TryRemoveLiquid(int amount)
        {
            mutationActor = RM_LiquidTheft.Current;
            stored -= amount;
            room += amount;
            return true;
        }
    }
    internal static class RM_LiquidSpill
    {
        public static Dictionary<int, RM_NetPort> ports = new();
        public static List<string> attempts = new();
        public static bool throwOnRoom;
        public static RM_OutletKind Outlet(Map map, RM_MapComponent_Excavation ex, IntVec3 end, LiquidDef liquid, FluidDef fluid, out IntVec3 cell)
        {
            cell = end;
            return RM_OutletKind.Channel;
        }
        public static long OutletRoomDl(RM_MapComponent_Excavation ex, RM_OutletKind kind, IntVec3 cell, FluidDef fluid, int units)
        {
            if (throwOnRoom) throw new InvalidOperationException("injected engine failure");
            attempts.Add("room:" + cell.x);
            return Math.Min(units, ports[cell.x].room);
        }
        public static bool WholeLevels(RM_OutletKind kind) => false;
        public static RM_TransferLeg OutletLeg(Map map, RM_MapComponent_Excavation ex, RM_OutletKind kind, IntVec3 cell, LiquidDef liquid, FluidDef fluid)
        {
            var port = ports[cell.x];
            return RM_TransferLeg.World(k => port.room >= k, k =>
            {
                if (port.refuse) return false;
                port.room -= k;
                port.received += k;
                return true;
            });
        }
    }
    internal static class RM_LiquidNet
    {
        public static List<RM_NetPort> PortsOf(Building_LiquidPump pump, RM_FreeEndRole role) => Machinery.RM_LiquidNet.PortsOf(pump, role);
        public static bool TooLarge(Building_LiquidPump pump) => false;
        public static int HoseNeed(Building_LiquidPump pump, IEnumerable<object> ports, LiquidDef liquid) => pump.hoseNeed;
        public static bool FillRoutes(Building_LiquidPump pump, object[] ports, LiquidDef liquid, int amount)
        {
            pump.hoseStored += amount;
            pump.hoseNeed = Math.Max(0, pump.hoseNeed - amount);
            return true;
        }
    }
    internal partial class Building_LiquidPump : Building
    {
        public Map Map = new();
        public List<IntVec3> reach = new();
        public List<RM_NetPort> intakes = new(), outflows = new();
        public Building_LiquidTank tank = new();
        public int Moved, lastMovedUnits, hoseNeed, hoseStored;
        public bool pourMode, on = true;
        private bool Running => on && RimMandrakeFlowWorksSettings.liquidPumpEnabled;
        private Power power = new();
        private Extension Ext = new();
        private readonly HashSet<int> usedOutflows = new(), deadSources = new();
        private int cycle;
        private bool filledPastOutflow, circle;
        private string lastLiquidLabel, lastStatus, warning;
        private IEnumerable<IntVec3> ReachCells() => reach;
        private List<Building_LiquidTank> NetTanks() => new() { tank };
        private void Stamp(int amount) => lastMovedUnits = amount;
        private void NoteNeighbours() { }
        private string TryPour() => throw new Exception("Draw-only harness");
        public void Pulse(int atCycle = 0, int levels = 1)
        {
            Ext.levelsPerCycle = levels;
            Find.TickManager.TicksGame = atCycle * RM_PumpMath.CycleTicks;
            Tick();
        }
        public void SeedRetirement()
        {
            cycle = 17;
            deadSources.Add(99);
            usedOutflows.Add(99);
        }
        public int CycleForTest => cycle;
        public string Candidates() => string.Join(",", Sources(Map.engine).Select(s => s.cell.x + ":" + Map.engine.WaterDlAt(s.cell)));
        public string Retired => "sources=" + string.Join(",", deadSources.Order()) + ";outflows=" + string.Join(",", usedOutflows.Order());
    }
    namespace Machinery
    {
        internal static class RM_LiquidNet
        {
            public static List<RM_NetPort> PortsOf(Building_LiquidPump pump, RM_FreeEndRole role) => role == RM_FreeEndRole.Intake ? pump.intakes : pump.outflows;
            public static int Room(Building_LiquidPump pump, LiquidDef liquid) => pump.tank.room;
            public static List<(Building_LiquidTank tank, int units)> FillPlan(Building_LiquidPump pump, LiquidDef liquid, int take) => new() { (pump.tank, take) };
            public static void CreditTo(Building_LiquidPump pump, object port, LiquidDef liquid, int amount, int ticks, object from = null) { }
            public static void Credit(Building_LiquidPump pump, object tank, LiquidDef liquid, int amount, int ticks) { }
            public static object FillFrom(object tank, LiquidDef liquid) => null;
        }
    }
    internal static class PumpOutflowChecks
    {
        static void Assert(bool ok, string message)
        {
            if (!ok) throw new Exception(message);
        }
        static Building_LiquidPump Site(long first = 900, long second = 20000, bool exact = false, params long[] rooms)
        {
            RM_MapComponent_Excavation.LevelExact = exact;
            RM_LiquidSpill.throwOnRoom = false;
            RM_LiquidSpill.ports.Clear();
            RM_LiquidSpill.attempts.Clear();
            var pump = new Building_LiquidPump();
            pump.Map.pump = pump;
            Find.CurrentMap = pump.Map;
            pump.Map.engine.water[0] = first;
            pump.Map.engine.water[1] = second;
            pump.reach.Add(new(0));
            pump.reach.Add(new(1));
            DefDatabase<LiquidDef>.AllDefsListForReading = new() { new() { canalFluid = pump.Map.engine.ActiveFluid } };
            foreach (long room in rooms.Length == 0 ? new long[] { 20000 } : rooms)
            {
                var port = new RM_NetPort { Cell = new IntVec3(10 + pump.outflows.Count), room = room };
                pump.outflows.Add(port);
                RM_LiquidSpill.ports[port.Cell.Value.x] = port;
            }
            return pump;
        }
        static long Total(Building_LiquidPump pump) => pump.Map.engine.water.Values.Sum() + pump.Map.engine.Stock.body.Values.Sum() + pump.tank.stored + pump.hoseStored + pump.outflows.Sum(p => p.received);
        static void CheckMove(Building_LiquidPump pump, int amount, long first, long second, int cycle = 0)
        {
            long total = Total(pump);
            string before = pump.Candidates();
            pump.Pulse(cycle);
            Console.WriteLine("    candidates=" + before + " cycle=" + cycle + " after=" + pump.Candidates() + " moved=" + pump.lastMovedUnits + " " + pump.Retired + " total=" + Total(pump));
            Assert(pump.Moved == (amount > 0 ? 1 : 0) && pump.lastMovedUnits == amount, "expected move " + amount + ", got " + pump.lastMovedUnits);
            Assert(pump.Map.engine.WaterDlAt(new(0)) == first && pump.Map.engine.WaterDlAt(new(1)) == second, "source deltas");
            Assert(Total(pump) == total, "conservation");
        }
        public static void Run(Action<string, Action> Case)
        {
            Case("TankTheft_actual_pump_entry_supplies_and_restores_actor", () =>
            {
                var p = Site(20000, 20000);
                p.outflows.Clear(); p.tank.room = 10000;
                var previous = new object();
                using (RM_LiquidTheft.As(previous))
                {
                    Building_LiquidPump.ProofDrawCycle("0,0;step");
                    Assert(p.Moved == 1 && p.tank.stored == 10000 && p.tank.mutationActor == p, "actual draw did not carry pump actor to tank mutation");
                    Assert(RM_LiquidTheft.Current == previous, "draw scope did not restore caller actor");
                }
                Assert(RM_LiquidTheft.Current == null, "outer scope leaked actor");
                p = Site(); RM_LiquidSpill.throwOnRoom = true;
                try { Building_LiquidPump.ProofDrawCycle("0,0;step"); } catch (InvalidOperationException) {}
                finally { RM_LiquidSpill.throwOnRoom = false; }
                Assert(RM_LiquidTheft.Current == null, "actual failing draw leaked actor");
            });
            Case("PumpOutflow_proof_arguments_and_state_restore", () =>
            {
                var p = Site();
                p.SeedRetirement();
                string retired = p.Retired;
                foreach (string arg in new[] { "", "bad;step", "0,0;bogus", "0,0;step;extra" })
                    Assert(Building_LiquidPump.ProofDrawCycle(arg).StartsWith("REFUSED"), "invalid argument must refuse");
                Assert(p.Moved == 0 && p.Retired == retired, "invalid args mutate nothing");
                string read = Building_LiquidPump.ProofDrawCycle("0,0;read");
                Assert(read.Contains("sources=[0,0:900;1,0:20000]") && p.Moved == 0, "read actual source ordering without transfer");
                p.on = false;
                Assert(Building_LiquidPump.ProofDrawCycle("0,0;step").Contains("units=0") && p.Moved == 0, "off control");
                p.on = true;
                string step = Building_LiquidPump.ProofDrawCycle("0,0;step");
                Assert(step.Contains("units=10000") && p.Moved == 1 && p.Retired == retired && p.CycleForTest == 17, "step actual draw and restore state");
                RM_LiquidSpill.throwOnRoom = true;
                try
                {
                    Building_LiquidPump.ProofDrawCycle("0,0;step");
                    throw new Exception("injection did not throw");
                }
                catch (InvalidOperationException)
                {
                    Assert(p.Retired == retired && p.CycleForTest == 17, "failure restores cycle and candidate state");
                }
                finally { RM_LiquidSpill.throwOnRoom = false; }
            });
            Case("PumpOutflow_body_rollback_and_contact_order", () =>
            {
                var p = Site(20000, 20000);
                p.Map.engine.water.Remove(0);
                p.Map.engine.Stock.body[0] = 20000;
                p.outflows[0].refuse = true;
                long total = Total(p);
                int putBacks = RM_LiquidTransfer.PutBacks;
                p.Pulse();
                Assert(p.Moved == 0 && p.Map.engine.Stock.body[0] == 20000 && Total(p) == total, "natural body credit rollback");
                Assert(RM_LiquidTransfer.PutBacks == putBacks + 1, "actual transfer rollback counter");
                p = Site(9999, 20000);
                p.Map.engine.water.Remove(0);
                p.Map.engine.Stock.body[0] = 9999;
                Assert(p.Candidates() == "1:20000", "exact-off natural short source is not drawable");
                CheckMove(p, 10000, 0, 10000);
                p = Site();
                p.reach.RemoveAt(1);
                p.intakes.Add(new RM_NetPort { Cell = new IntVec3(1) });
                CheckMove(p, 10000, 900, 10000);
                p = Site(900, 900);
                CheckMove(p, 0, 900, 900);
                Assert(p.Retired == "sources=;outflows=", "all short sources leave outlets unused without retry exhaustion");
                p = Site(900, 20000, false, 900, 20000);
                CheckMove(p, 10000, 900, 10000);
                Assert(p.outflows[0].received == 0 && p.outflows[1].received == 10000, "both short then subsequent outlet");
            });
            Case("PumpOutflow_live_driver_restoration_offline", () =>
            {
                string source = RiverSwitchFlipChecks.SrcPath("RM_PumpMath.cs");
                string driver = System.IO.Path.GetFullPath(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(source), "..", "northstar", "pump_outflow_live.py"));
                var start = new System.Diagnostics.ProcessStartInfo("python.exe")
                {
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false
                };
                start.ArgumentList.Add(driver);
                start.ArgumentList.Add("--selftest");
                using var process = System.Diagnostics.Process.Start(start);
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                Assert(process.WaitForExit(30000), "Python proof selftest timeout");
                Assert(process.ExitCode == 0 && output.Contains("PASS pump outflow"), output + error);
            });
            Case("PumpOutflow_short_first_real_TryDraw", () => CheckMove(Site(), 10000, 900, 10000));
            Case("PumpOutflow_room_short_and_rotation", () =>
            {
                var p = Site(20000, 20000, false, 900, 20000);
                CheckMove(p, 10000, 10000, 20000);
                Assert(p.outflows[0].received == 0 && p.outflows[1].received == 10000, "subsequent outlet");
                p = Site(20000, 20000, false, 20000, 20000);
                CheckMove(p, 10000, 10000, 20000, 1);
                Assert(p.outflows[1].received == 10000 && p.outflows[0].received == 0, "actual PumpNext cycle rotation");
            });
            Case("PumpOutflow_both_short_zero_and_exact", () =>
            {
                CheckMove(Site(900, 20000, false, 900), 0, 900, 20000);
                CheckMove(Site(0, 20000), 10000, 0, 10000);
                CheckMove(Site(900, 20000, true), 900, 0, 20000);
                CheckMove(Site(20000, 20000, true, 900), 900, 19100, 20000);
                CheckMove(Site(900, 20000, true, 500), 500, 400, 20000);
                CheckMove(Site(900, 20000, false, 0), 0, 900, 20000);
                var p = Site();
                p.reach.Add(new(0));
                CheckMove(p, 10000, 900, 10000);
            });
            Case("PumpOutflow_tank_fallback_and_hose_fill", () =>
            {
                var p = Site();
                p.tank.room = 900;
                CheckMove(p, 10000, 900, 10000);
                Assert(p.tank.stored == 0 && p.Map.engine.takeCalls == 2, "partial tank plan attempted and rolled back under actual exact-off rounding, then full source uses outflow");
                p = Site(900, 20000, true);
                p.outflows.Clear();
                p.tank.room = 500;
                CheckMove(p, 500, 400, 20000);
                Assert(p.tank.stored == 500, "exact partial tank fallback");
                p = Site(20000, 20000, false, 900);
                p.tank.room = 10000;
                CheckMove(p, 10000, 10000, 20000);
                Assert(p.tank.stored == 10000, "outlet room short falls back to tanks");
                p = Site(900, 20000, false, 0);
                p.hoseNeed = 10000;
                CheckMove(p, 10000, 900, 10000);
                Assert(p.hoseStored == 10000 && p.outflows[0].received == 0, "hose fill bypasses outlet room but not source supply");
            });
            Case("PumpOutflow_failure_rollback_and_cycle_reset", () =>
            {
                var p = Site(20000, 20000, false, 20000, 20000);
                p.outflows[0].refuse = true;
                CheckMove(p, 10000, 10000, 20000);
                Assert(p.outflows[0].received == 0 && p.outflows[1].received == 10000, "refused world destination rolled back then next outlet");
                p = Site(20000, 20000);
                p.Map.engine.refuseTake.Add(0);
                CheckMove(p, 0, 20000, 20000);
                p = Site();
                p.Pulse();
                Assert(p.Moved == 1, "first cycle");
                p.Map.engine.water[0] = 10000;
                p.Pulse(1);
                Assert(p.Moved == 2 && p.Map.engine.water[0] == 0 && p.outflows[0].received == 20000, "source/outflow retirement resets next cycle");
                p = Site();
                p.Pulse(0, 3);
                Assert(p.Moved == 1 && p.outflows[0].received == 10000, "one outflow turn per multi-level cycle");
                p = Site();
                p.on = false;
                CheckMove(p, 0, 900, 20000);
            });
        }
    }
}
