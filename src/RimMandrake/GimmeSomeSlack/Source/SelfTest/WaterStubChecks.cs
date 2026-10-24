// GSS_WATER_STUB_FIX_PASSED_LAST_WEEK (bridge run 1, 2026-10-23): matrix MX_F60_T15_S0 (canal) found 0 of 2 water stubs once
// FlowWorks was co-loaded. FlowWorks R12 makes deep water walkable on the PATH GRID (swimming), and the snapshot read
// "walkable" as open ground before it looked at water. Scene mirrors t_canal: a run along z=3 crossing deep water at x 5-6,
// battery west, heater east. Each row carries its can-fail: the old rule beside the production rule (SnapshotBlock.Of).
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class WaterStubChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "water-stub: " + msg);

        /// <summary>The pre-fix adapter rule, kept here only as the can-fail.</summary>
        private static BlockKind? OldRule(bool walkable, bool hasEdifice, bool rock, bool powered, bool water, bool impassable)
        {
            if (walkable) return null;
            if (hasEdifice) return rock ? BlockKind.Rock : powered ? BlockKind.Device : BlockKind.Wall;
            return water ? BlockKind.Water : BlockKind.Wall;
        }

        private delegate BlockKind? Rule(bool walkable, bool hasEdifice, bool rock, bool powered, bool water, bool impassable);

        /// <summary>swim: FlowWorks deep swim on (deep water walkable on the path grid); deepDef: the water's def is Impassable.</summary>
        private static CordWorld Canal(Rule rule, bool swim, bool deepDef)
        {
            var w = new CordWorld(14, 8);
            for (int x = 0; x < 14; x++)
                for (int z = 0; z < 8; z++)
                {
                    bool water = (x == 5 || x == 6) && z <= 6;
                    bool walkable = !water || swim || !deepDef;
                    BlockKind? k = rule(walkable, false, false, false, water, water && deepDef);
                    if (k.HasValue) w.SetBlocked(new Cell(x, z), k.Value);
                }
            for (int x = 1; x <= 11; x++) w.SetConduit(new Cell(x, 3));
            w.SetBlocked(new Cell(0, 3), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "tbat", Kind = MachineKind.Battery, X0 = 0, Z0 = 3, Hookups = new List<Cell> { new Cell(1, 3) } });
            w.SetBlocked(new Cell(12, 3), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "cheat", Kind = MachineKind.Consumer, X0 = 12, Z0 = 3, Hookups = new List<Cell> { new Cell(11, 3) } });
            return w;
        }

        private static int WaterStubs(CordWorld w) => CordGraph.Reduce(w).Nodes.Values.Count(n => n.Type == NodeType.StubWater);

        public static void Run()
        {
            int oldVanilla = WaterStubs(Canal(OldRule, false, true));
            Check(oldVanilla == 2, $"old rule, no swim (the 2026-10-16 PASS): {oldVanilla} water stubs, want 2");
            int oldSwim = WaterStubs(Canal(OldRule, true, true));
            Check(oldSwim == 0, $"can-fail: old rule with deep-water swim on reads the canal as ground ({oldSwim} water stubs, want 0)");
            int newSwim = WaterStubs(Canal(SnapshotBlock.Of, true, true));
            Check(newSwim == 2, $"swimmable deep water still buries the waterproof run ({newSwim} water stubs, want 2)");
            int newVanilla = WaterStubs(Canal(SnapshotBlock.Of, false, true));
            Check(newVanilla == 2, $"no swim: unchanged, {newVanilla} water stubs, want 2");
            int shallow = WaterStubs(Canal(SnapshotBlock.Of, false, false));
            Check(shallow == 0, $"walkable shallow water (def passable) stays ground: {shallow} water stubs, want 0");

            Check(SnapshotBlock.Of(true, true, false, false, true, true) == null, "a walkable edifice on deep water keeps the old answer (ground)");
            Check(SnapshotBlock.Of(false, true, true, false, true, true) == BlockKind.Rock, "rock edifice on water is Rock");
            Check(SnapshotBlock.Of(false, false, false, false, false, true) == BlockKind.Wall, "impassable dry terrain is Wall");
            Check(SnapshotBlock.Of(true, false, false, false, false, false) == null, "walkable dry ground is open");
        }
    }
}
