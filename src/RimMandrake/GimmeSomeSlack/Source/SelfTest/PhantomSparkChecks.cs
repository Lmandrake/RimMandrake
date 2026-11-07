// GSS_CORD_SILENCE_PHANTOM_SPARK (owner 2026-10-16, FW station carry_tanks): a conduit run ending beside a pump that vanilla
// wired straight to the battery drew a second, free, sparking cord. Scene mirrors the station: pump (5,2), conduit (5,3..5),
// battery (6,5) 1x2. Each row carries its can-fail: the old wiring (pump linked to the battery) beside the new pick.
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class PhantomSparkChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "phantom-spark: " + msg);

        private static CordWorld Scene(out MachineInfo pump, out MachineInfo bat)
        {
            var w = new CordWorld(12, 12);
            for (int z = 3; z <= 5; z++) w.SetConduit(new Cell(5, z));
            w.SetBlocked(new Cell(5, 2), BlockKind.Device);
            w.SetBlocked(new Cell(6, 5), BlockKind.Device);
            w.SetBlocked(new Cell(6, 6), BlockKind.Device);
            bat = new MachineInfo { Id = "tbat", Kind = MachineKind.Battery, X0 = 6, Z0 = 5, W = 1, H = 2 };
            bat.Hookups.Add(new Cell(5, 5));
            w.Machines.Add(bat);
            pump = new MachineInfo { Id = "cpump", Kind = MachineKind.Consumer, X0 = 5, Z0 = 2, W = 1, H = 1 };
            return w;
        }

        private static int FreeEnds(CordWorld w) =>
            new CordBuilder().Build(w, new BuildOptions { Seed = 1 }, c => true).Sum(p => p.Ends.Count);

        /// <summary>A battery or generator takes one cord from a run alongside it, however many cells touch (seen in a lived-in colony 2026-11-07: seven into one solar panel).</summary>
        private static void CarrierHookups()
        {
            Dictionary<Cell, int> runs = null;
            var w = new CordWorld(30, 30);
            for (int x = 5; x <= 15; x++) w.SetConduit(new Cell(x, 9));
            var along = new List<Cell> { new Cell(8, 9), new Cell(9, 9), new Cell(10, 9), new Cell(11, 9) };
            Check(HookupPick.PickCarrier(w, along, ref runs).Count == 1, "four cells of one run along a solar panel: one cord");
            runs = null;
            var w2 = new CordWorld(30, 30);
            for (int x = 2; x <= 6; x++) w2.SetConduit(new Cell(x, 9));
            for (int x = 9; x <= 14; x++) w2.SetConduit(new Cell(x, 9));
            Check(HookupPick.PickCarrier(w2, new List<Cell> { new Cell(6, 9), new Cell(9, 9) }, ref runs).Count == 2, "two runs joined only by the battery between them: a cord each");
            runs = null;
            var w3 = new CordWorld(30, 30);
            for (int x = 2; x <= 9; x++) w3.SetConduit(new Cell(x, 9));
            for (int z = 9; z <= 14; z++) w3.SetConduit(new Cell(5, z));
            var pickEnd = HookupPick.PickCarrier(w3, new List<Cell> { new Cell(8, 9), new Cell(9, 9) }, ref runs);
            Check(pickEnd.Count == 1 && pickEnd[0] == new Cell(9, 9), "a run ending beside it hooks the end, so nothing sparks there");
            runs = null;
            var w4 = new CordWorld(30, 30);
            for (int x = 3; x <= 8; x++) w4.SetConduit(new Cell(x, 9));
            Check(HookupPick.PickCarrier(w4, new List<Cell> { new Cell(3, 9), new Cell(8, 9) }, ref runs).Count == 2, "both ends of one run beside it: both hook, neither is left a free end");
        }

        public static void Run()
        {
            CarrierHookups();
            // old: the pump is linked to the battery only -> the conduit end at (5,3) is free and sparks
            CordWorld wOld = Scene(out MachineInfo pOld, out MachineInfo bOld);
            CordWorldLinks.LinkToMachine(wOld, pOld, bOld);
            int oldEnds = FreeEnds(wOld);
            Check(oldEnds == 1, $"can-fail: battery-linked pump leaves the conduit end beside it free ({oldEnds} free ends, want 1)");

            // new: the pick hooks the same-net end beside the pump instead
            CordWorld wNew = Scene(out MachineInfo pNew, out MachineInfo bNew);
            List<Cell> pick = HookupPick.Pick(wNew, pNew, null, c => true);
            Check(pick != null && pick.Count == 1 && pick[0].Equals(new Cell(5, 3)), "pick hooks the conduit end (5,3) beside the pump");
            pNew.Hookups.AddRange(pick ?? new List<Cell>());
            wNew.Machines.Add(pNew);
            int newEnds = FreeEnds(wNew);
            Check(newEnds == 0, $"one cord battery -> conduit -> pump, no free end ({newEnds} free ends)");

            // a parent conduit already beside the pump: unchanged wiring
            CordWorld w2 = Scene(out MachineInfo p2, out _);
            Check(HookupPick.Pick(w2, p2, new Cell(5, 3), c => true) == null, "parent conduit beside the device keeps vanilla wiring");

            // other net: a conduit end beside the device on ANOTHER net stays free (a genuine loose end keeps its spark)
            CordWorld w3 = Scene(out MachineInfo p3, out _);
            Check(HookupPick.Pick(w3, p3, null, c => false) == null, "a different net's end beside the device is not adopted");

            // mid-run conduit beside the device (degree 2) is not an end: nothing to adopt
            CordWorld w4 = Scene(out MachineInfo p4, out _);
            w4.SetConduit(new Cell(4, 3)); w4.SetConduit(new Cell(6, 3));
            Check(HookupPick.Pick(w4, p4, null, c => true) == null, "a run passing beside the device (not an end) is not adopted");

            // a far parent conduit that is itself an end stays hooked beside the adopted end (never stranded)
            CordWorld w5 = Scene(out MachineInfo p5, out _);
            w5.SetConduit(new Cell(9, 9));
            List<Cell> pk5 = HookupPick.Pick(w5, p5, new Cell(9, 9), c => true);
            Check(pk5 != null && pk5.Count == 2 && pk5.Contains(new Cell(9, 9)), "a far parent end stays hooked beside the adopted end");

            // WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES: a ruin has no net, so sameNet is not asked; one cord per run touching it
            CordWorld r1 = Scene(out MachineInfo rp1, out _);
            List<Cell> rk1 = HookupPick.PickRuin(r1, rp1);
            Check(rk1 != null && rk1.Count == 1 && rk1[0] == new Cell(5, 3), "a conduit end beside a ruin hooks into it");
            CordWorld r2 = Scene(out MachineInfo rp2, out _);
            r2.SetConduit(new Cell(4, 3)); r2.SetConduit(new Cell(6, 3));
            List<Cell> rk2 = HookupPick.PickRuin(r2, rp2);
            Check(rk2 != null && rk2.Count == 1 && rk2[0] == new Cell(5, 3), "a run passing beside a ruin (no end there) still draws one cord");
            var far = new CordWorld(12, 12);
            far.SetConduit(new Cell(9, 9));
            Check(HookupPick.PickRuin(far, new MachineInfo { Id = "r", X0 = 2, Z0 = 2, W = 3, H = 2 }) == null, "can-fail: a conduit not touching the ruin draws nothing");
            var two = new CordWorld(12, 12);
            var wide = new MachineInfo { Id = "r", X0 = 4, Z0 = 4, W = 3, H = 2 };
            two.SetConduit(new Cell(3, 4)); two.SetConduit(new Cell(2, 4)); two.SetConduit(new Cell(7, 4)); two.SetConduit(new Cell(8, 4));
            List<Cell> rk3 = HookupPick.PickRuin(two, wide);
            Check(rk3 != null && rk3.Count == 2 && rk3.Contains(new Cell(3, 4)) && rk3.Contains(new Cell(7, 4)), "two separate runs ending at a ruin each draw in");
            var both = new CordWorld(12, 12);
            for (int x = 4; x <= 6; x++) both.SetConduit(new Cell(x, 6));
            List<Cell> rk4 = HookupPick.PickRuin(both, wide);
            Check(rk4 != null && rk4.Count == 1, "a run along a ruin's whole edge is one cord, not one per cell");
        }
    }
}
