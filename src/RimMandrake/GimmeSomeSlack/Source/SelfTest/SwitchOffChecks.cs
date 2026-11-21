// T_SWITCH_OFF_NODE_OFFLINE (bar switch_off_cords_stay_connected; RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT, his walk of 2026-11-20
// row 1): an off power switch is a node of the cord graph, so both cords run into its stubs and read connected without power.
// The shipped decision (Core/SwitchNode.JoinsGraph) decides here whether the switch joins the graph, exactly as CordWorldAdapter.AddPower
// asks it; the scenes are laid by the production CordBuilder.
//
// The range of situations (what the game can vary for this bar):
//   arms      which sides of the switch carry conduit: every non-empty subset of the four sides (15), each arm run 2-4 cells out,
//             then 1-3 cells aside (CordEndKindChecks.BoxScene, seeded), ending on a machine;
//   power     which conduit pieces have a live source when the switch is off: every subset of the pieces (an off switch splits one net
//             into up to four); on, the switch joins them into one net, live if any piece is;
//   chain     two switches side by side with no conduit between (HookupPick.ChainTransmitters), each on or off;
//   look      the four run looks (Modern strips, the junction looks);  seeds  two lay seeds a scene.
// Left out: a switch of another size (vanilla's is 1x1; SidePorts is set only for 1x1), a device wired straight to a switch (a switch
// is no wire parent: northstar_matrix/scenes.py DEVICE_DEFS), fog (an unfogged switch only), and the flick itself (the graph is rebuilt
// from the new state; the rebuild trigger is the live game's and is read by sc_switch_off_ends).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SwitchOffChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "switch off: " + msg);

        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
        private const double Near = 1.5;    // the bar's reach: "no cord end cuts, frays or sparks AT the switch" (proof_note: within 1.5 cells)

        private static BuildOptions Opt(string look, ulong seed) =>
            new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, Seed = seed, PlugBoot = CordBuilder.PlugBootU(look) };

        /// <summary>The conduit pieces of a world: 4-connected components of conduit cells.</summary>
        private static Dictionary<Cell, int> Pieces(CordWorld w, out int n)
        {
            var comp = new Dictionary<Cell, int>();
            n = 0;
            for (int z = 0; z < w.Height; z++)
                for (int x = 0; x < w.Width; x++)
                {
                    var s = new Cell(x, z);
                    if (!w.IsConduit(s) || comp.ContainsKey(s)) continue;
                    var st = new Stack<Cell>(); st.Push(s); comp[s] = n;
                    while (st.Count > 0)
                    {
                        Cell q = st.Pop();
                        foreach (Cell d in Dirs)
                        {
                            var r = new Cell(q.X + d.X, q.Z + d.Z);
                            if (r.X < 0 || r.Z < 0 || r.X >= w.Width || r.Z >= w.Height || !w.IsConduit(r) || comp.ContainsKey(r)) continue;
                            comp[r] = n; st.Push(r);
                        }
                    }
                    n++;
                }
            return comp;
        }

        /// <summary>What the adapter makes of a switch: a node with PickCarrier's hookups when SwitchNode.JoinsGraph says so, else nothing.</summary>
        private static void Seat(CordWorld w, MachineInfo sw, bool on)
        {
            w.Machines.RemoveAll(m => m.Id == sw.Id);
            if (!SwitchNode.JoinsGraph(inPowerNet: on, isPowerSwitch: true)) return;
            Dictionary<Cell, int> runs = null;
            var touching = new List<Cell>(sw.Hookups);
            sw.Hookups = HookupPick.PickCarrier(w, touching, ref runs);
            w.Machines.Add(sw);
        }

        internal sealed class Read
        {
            public int Scenes, Pieces, CutNear, FrayNear, Unjoined, ShapeDiffers;
            public double NearestEnd = double.MaxValue;
            public readonly List<string> Bad = new List<string>();
        }

        /// <summary>One off/on pair of a scene: the off lay is read for ends at the switch and arms joined; on and off are compared.</summary>
        private static void Pair(Read rd, Func<CordWorld> make, Cell[] switches, Func<Cell, bool> liveOff, Func<Cell, bool> liveOn,
                                 bool[] offState, BuildOptions opt, string name)
        {
            CordWorld wOff = make(), wOn = make();
            var hooksWanted = new Dictionary<string, int>();
            foreach (MachineInfo m in wOff.Machines.Where(m => m.Kind == MachineKind.Transmitter).ToList())
            {
                int k = Array.FindIndex(switches, c => c.X == m.X0 && c.Z == m.Z0);
                Seat(wOff, m, !offState[k]);
            }
            foreach (MachineInfo m in wOn.Machines.Where(m => m.Kind == MachineKind.Transmitter).ToList()) Seat(wOn, m, true);
            foreach (MachineInfo m in wOn.Machines.Where(m => m.Kind == MachineKind.Transmitter)) hooksWanted[m.Id] = m.Hookups.Count + m.MachineLinks.Count;
            HookupPick.ChainTransmitters(wOff.Machines.Where(m => m.Kind == MachineKind.Transmitter).ToList());
            HookupPick.ChainTransmitters(wOn.Machines.Where(m => m.Kind == MachineKind.Transmitter).ToList());

            var bOff = new CordBuilder(); List<LaidPiece> off = bOff.Build(wOff, opt, liveOff);
            var bOn = new CordBuilder(); List<LaidPiece> on = bOn.Build(wOn, opt, liveOn);
            rd.Scenes++; rd.Pieces += off.Count;
            foreach (Cell s in switches)
            {
                double D(double x, double z) => Math.Sqrt((x - (s.X + 0.5)) * (x - (s.X + 0.5)) + (z - (s.Z + 0.5)) * (z - (s.Z + 0.5)));
                foreach (LaidPiece p in off)
                {
                    foreach (CordEnd e in p.Ends)
                    {
                        double d = Math.Sqrt((e.NetCell.X - s.X) * (e.NetCell.X - s.X) + (e.NetCell.Z - s.Z) * (e.NetCell.Z - s.Z));
                        rd.NearestEnd = Math.Min(rd.NearestEnd, d);
                        if (d <= Near) { rd.CutNear++; if (rd.Bad.Count < 6) rd.Bad.Add($"{name}: cut end at {e.NetCell} ({d:0.00} cells from the switch at {s})"); }
                    }
                    foreach (CordDecal dc in p.Decals)
                        if ((dc.Kind == DecalKind.FrayDead || dc.Kind == DecalKind.FrayLive) && D(dc.Pos.X, dc.Pos.Z) <= Near + 0.5)
                        { rd.FrayNear++; if (rd.Bad.Count < 6) rd.Bad.Add($"{name}: {dc.Kind} at ({dc.Pos.X:0.00},{dc.Pos.Z:0.00}) beside the switch at {s}"); }
                }
                foreach (CordNode nd in bOff.Graph.Nodes.Values)
                    if (nd.Type == NodeType.Terminal && Math.Abs(nd.Cell.X - s.X) + Math.Abs(nd.Cell.Z - s.Z) <= 1)
                    { rd.CutNear++; if (rd.Bad.Count < 6) rd.Bad.Add($"{name}: terminal node at {nd.Cell} beside the switch at {s}"); }
            }
            // every cord the switch carries when on still ends on it when off
            foreach (var kv in hooksWanted)
            {
                VId sv = bOff.Graph.Nodes.FirstOrDefault(n => n.Value.Machine != null && n.Value.Machine.Id == kv.Key).Key;
                bool has = bOff.Graph.Nodes.Any(n => n.Value.Machine != null && n.Value.Machine.Id == kv.Key);
                int deg = has ? bOff.Graph.CordEdges().Count(e => e.A.Equals(sv) || e.B.Equals(sv)) : 0;
                VId sOn = bOn.Graph.Nodes.FirstOrDefault(n => n.Value.Machine != null && n.Value.Machine.Id == kv.Key).Key;
                int degOn = bOn.Graph.CordEdges().Count(e => e.A.Equals(sOn) || e.B.Equals(sOn));
                if (!has || deg != degOn || deg == 0)
                { rd.Unjoined++; if (rd.Bad.Count < 6) rd.Bad.Add($"{name}: switch {kv.Key} carries {deg} cords off, {degOn} on{(has ? "" : " (no node)")}"); }
            }
            // on and off differ only in the powered look: the same pieces, the same strand points
            var byEnds = on.GroupBy(p => p.EndA + "|" + p.EndB).ToDictionary(g => g.Key, g => g.ToList());
            bool same = off.Count == on.Count;
            foreach (LaidPiece p in off)
            {
                if (!same) break;
                if (!byEnds.TryGetValue(p.EndA + "|" + p.EndB, out List<LaidPiece> cand)) { same = false; break; }
                same = cand.Any(q => q.Strands.Count == p.Strands.Count && q.Strands.Zip(p.Strands, (a, b) =>
                    a.Pts.Count == b.Pts.Count && a.Pts.Zip(b.Pts, (u, v) => Math.Abs(u.X - v.X) < 1e-9 && Math.Abs(u.Z - v.Z) < 1e-9).All(x => x)).All(x => x));
            }
            if (!same) { rd.ShapeDiffers++; if (rd.Bad.Count < 6) rd.Bad.Add($"{name}: the off lay's cords differ in shape from the on lay"); }
        }

        /// <summary>Two switches side by side (west one at x=15, east at x=16), conduit west of the pair and east of it, a machine at each end.</summary>
        private static CordWorld ChainScene()
        {
            var w = new CordWorld(34, 34);
            for (int x = 9; x <= 14; x++) w.SetConduit(new Cell(x, 16));
            for (int x = 17; x <= 22; x++) w.SetConduit(new Cell(x, 16));
            w.SetBlocked(new Cell(8, 16), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "c_bat", Kind = MachineKind.Battery, X0 = 8, Z0 = 16, Hookups = new List<Cell> { new Cell(9, 16) } });
            w.SetBlocked(new Cell(23, 16), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "c_lamp", Kind = MachineKind.Consumer, X0 = 23, Z0 = 16, Hookups = new List<Cell> { new Cell(22, 16) } });
            foreach (int x in new[] { 15, 16 })
            {
                w.SetBlocked(new Cell(x, 16), BlockKind.Device);
                var hk = new List<Cell>();
                if (w.IsConduit(new Cell(x - 1, 16))) hk.Add(new Cell(x - 1, 16));
                if (w.IsConduit(new Cell(x + 1, 16))) hk.Add(new Cell(x + 1, 16));
                w.Machines.Add(new MachineInfo { Id = "t" + x, Kind = MachineKind.Transmitter, X0 = x, Z0 = 16, Hookups = hk, SidePorts = true });
            }
            return w;
        }

        public static void Run()
        {
            var rd = new Read();
            string[] looks = StubJoinChecks.Looks;
            var armSets = new List<Cell[]>();
            for (int mask = 1; mask < 16; mask++) armSets.Add(Dirs.Where((_, i) => (mask >> i & 1) != 0).ToArray());
            int splits = 0;
            foreach (string look in looks)
                for (int seed = 0; seed < 2; seed++)
                    foreach (Cell[] arms in armSets)
                    {
                        int sceneSeed = 300 + seed * 11 + arms.Length * 3 + Array.IndexOf(Dirs, arms[0]);
                        CordWorld probe = CordEndKindChecks.BoxScene(arms, sceneSeed, true);
                        Dictionary<Cell, int> comp = Pieces(probe, out int n);
                        if (n > 1) splits++;
                        for (int pm = 0; pm < 1 << n; pm++)
                        {
                            int powered = pm;
                            Func<Cell, bool> liveOff = c => comp.TryGetValue(c, out int k) && (powered >> k & 1) != 0;
                            Func<Cell, bool> liveOn = c => (comp.ContainsKey(c) || (c.X == 16 && c.Z == 16)) && powered != 0;
                            Pair(rd, () => CordEndKindChecks.BoxScene(arms, sceneSeed, true), new[] { new Cell(16, 16) }, liveOff, liveOn,
                                 new[] { true }, Opt(look, (ulong)(71 + seed)), $"{look} s{seed} arms[{string.Join(" ", arms)}] powered{pm:x}");
                        }
                    }
            // two switches side by side: each of the three off states, power on the battery side, the lamp side, or both
            foreach (string look in looks)
                foreach (bool[] st in new[] { new[] { true, false }, new[] { false, true }, new[] { true, true } })
                    foreach (int pm in new[] { 1, 2, 3 })
                    {
                        Func<Cell, bool> liveOff = c => c.Z == 16 && ((c.X <= 14 && (pm & 1) != 0) || (c.X >= 17 && (pm & 2) != 0));
                        Func<Cell, bool> liveOn = c => c.Z == 16 && c.X >= 9 && c.X <= 22;
                        Pair(rd, ChainScene, new[] { new Cell(15, 16), new Cell(16, 16) }, liveOff, liveOn, st, Opt(look, 81),
                             $"{look} chain off[{(st[0] ? "W" : "")}{(st[1] ? "E" : "")}] powered{pm}");
                    }

            Console.WriteLine($"  switch off: {rd.Scenes} off/on pairs ({splits} arm layouts split into 2+ nets when off), {rd.Pieces} pieces laid off; " +
                              $"cut ends within {Near} cells of a switch {rd.CutNear} (limit 0); fray/spark decals beside a switch {rd.FrayNear} (limit 0); " +
                              $"switches carrying fewer cords off than on {rd.Unjoined} (limit 0); off lays differing in shape from on {rd.ShapeDiffers} (limit 0); " +
                              $"nearest cut end to a switch {(rd.NearestEnd == double.MaxValue ? "none laid" : rd.NearestEnd.ToString("0.00"))}");
            foreach (string b in rd.Bad) Console.WriteLine("  switch off refused: " + b);
            Check(rd.Scenes >= 600, $"the range was read ({rd.Scenes} pairs)");
            Check(rd.CutNear == 0, $"no cut end at an off switch ({rd.CutNear} found)");
            Check(rd.FrayNear == 0, $"no fray or spark beside an off switch ({rd.FrayNear} found)");
            Check(rd.Unjoined == 0, $"an off switch carries every cord it carries on ({rd.Unjoined} short)");
            Check(rd.ShapeDiffers == 0, $"on and off lay the same cords, the powered look aside ({rd.ShapeDiffers} differ)");

            // the instrument can see the fault: the old graph (an off switch dropped) is read by the same counters and must show cut ends
            var old = new Read();
            CordWorld w0 = CordEndKindChecks.BoxScene(new[] { Dirs[1], Dirs[3] }, 301, true);
            w0.Machines.RemoveAll(m => m.Kind == MachineKind.Transmitter);
            List<LaidPiece> ps0 = new CordBuilder().Build(w0, Opt("Industrial", 71), _ => false);
            old.CutNear = ps0.SelectMany(p => p.Ends).Count(e => Math.Abs(e.NetCell.X - 16) + Math.Abs(e.NetCell.Z - 16) <= 1);
            Check(old.CutNear >= 2, $"instrument sanity: a switch dropped from the graph shows its cut ends ({old.CutNear} seen)");
        }
    }
}
