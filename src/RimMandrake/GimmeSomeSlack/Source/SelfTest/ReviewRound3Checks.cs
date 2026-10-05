// Owner human review round 3 (2026-10-04, typed notes on stations 9 and 11 plus the switch and the wall connectors): the
// offline, load-bearing checks of the floor-cord side. Each check carries a planted fault that must turn it red.
//   switch   the cords go BENEATH the power switch: the draw-stack rule (Transparent switch painted over, Cutout not)
//   wall     wall connector plates are foreshortened (face out of the wall), never a square looking up at the sky
//   lead     a short device link (wall stub -> lamp, station 9) is ONE cord, never a 2-3 cord bundle
//   tap      the power tap is a NODE both grids' cables run into: no free sparking end on the bitten conduit
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ReviewRound3Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review3: " + msg);

        private static MachineInfo M(CordWorld w, string id, MachineKind k, int x, int z, params Cell[] hooks)
        {
            w.SetBlocked(new Cell(x, z), BlockKind.Device);
            var m = new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, Hookups = hooks.ToList() };
            w.Machines.Add(m);
            return m;
        }

        public static void Run()
        {
            // ---- switch: draw order. Plugs (3001) and strands (3000) against the vanilla Transparent switch vs our Cutout one
            bool vanillaOver = DrawStack.CordsPaintOver(DrawStack.TransparentQueue, false, 3001) && DrawStack.CordsPaintOver(DrawStack.TransparentQueue, false, 3000);
            bool oursUnder = !DrawStack.CordsPaintOver(DrawStack.CutoutQueue, true, 3000) && !DrawStack.CordsPaintOver(DrawStack.CutoutQueue, true, 3001);
            Check(vanillaOver && oursUnder, "switch: cords paint over a Transparent (vanilla) switch, go beneath a Cutout one (ours)");
            Check(DrawStack.CordsPaintOver(DrawStack.TransparentQueue, false, DrawStack.TransparentQueue), "can fail: the vanilla shader would put the cords on top");

            // ---- station 9 in miniature: a wall with a buried conduit, the lamp inside, a battery outside
            var w = new CordWorld(20, 12);
            for (int x = 2; x <= 12; x++) w.SetBlocked(new Cell(x, 6), BlockKind.Wall);
            foreach (Cell c in new[] { new Cell(6, 8), new Cell(6, 7), new Cell(6, 6), new Cell(6, 5), new Cell(6, 4) }) w.SetConduit(c);
            M(w, "bat", MachineKind.Battery, 6, 9, new Cell(6, 8));
            M(w, "lamp", MachineKind.Consumer, 6, 3, new Cell(6, 4));
            for (int x = 14; x <= 18; x++) w.SetConduit(new Cell(x, 1));       // a loose run (two conduit ends): may bundle
            var b = new CordBuilder();
            var opt = new BuildOptions();
            opt.Lay.CordsMax = 3;
            List<LaidPiece> ps = b.Build(w, opt, c => true);
            List<CordDecal> plates = ps.SelectMany(p => p.Decals).Where(d => d.Kind == DecalKind.StubWall).ToList();
            ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
            Check(plates.Count >= 2 && r.FlatWallPlates == 0 && r.StubFaults == 0,
                  $"wall: {plates.Count} wall plates, {r.FlatWallPlates} not mounted ON the wall, {r.StubFaults} off the face");
            var flat = ps.Select(p => new LaidPiece { Key = p.Key, EndA = p.EndA, EndB = p.EndB, Strands = p.Strands,
                Decals = p.Decals.Select(d => d.Kind == DecalKind.StubWall ? new CordDecal(d.Kind, d.Pos - new V2(Math.Cos(d.Angle), Math.Sin(d.Angle)) * 0.18, d.Angle, d.Scale) { Squash = 0.5 } : d).ToList() }).ToList();
            Check(CordAudit.ArtFit(b.Graph, flat, c => true).FlatWallPlates == plates.Count, "can fail: planted round-3 plates (centred on the face line, half on the floor) are counted");
            List<LaidPiece> leads = ps.Where(p => (p.EndA ?? "").StartsWith("consumer") || (p.EndB ?? "").StartsWith("consumer") ||
                                                  (p.EndA ?? "").StartsWith("battery") || (p.EndB ?? "").StartsWith("battery")).ToList();
            Check(leads.Count >= 2 && leads.All(p => p.Strands.Count == 1),
                  $"lead: {leads.Count} device leads, cords each: {string.Join(",", leads.Select(p => p.Strands.Count))} (want 1: one cord into one plug)");
            // can fail: the same graph with the device-lead rule switched off lays a bundle somewhere (seeded 1-3)
            int bundles = 0;
            for (ulong seed = 1; seed <= 8; seed++)
            {
                var o2 = new BuildOptions { Seed = seed };
                o2.Lay.CordsMax = 3;
                List<LaidPiece> q = new CordBuilder().Build(w, o2, c => true);
                bundles += q.Count(p => p.Strands.Count > 1 && !(p.Key ?? "").StartsWith("tangle:"));
            }
            Check(bundles > 0,
                  $"sanity probe: non-device edges still lay bundles across 8 seeds ({bundles} pieces with > 1 cord)");

            // ---- station 11 in miniature: THEIR battery -> conduit, the tap, OUR conduit -> lamp
            var t = new CordWorld(16, 10);
            foreach (Cell c in new[] { new Cell(3, 4), new Cell(4, 4) }) t.SetConduit(c);
            foreach (Cell c in new[] { new Cell(7, 4), new Cell(8, 4) }) t.SetConduit(c);
            M(t, "theirbat", MachineKind.Battery, 2, 4, new Cell(3, 4));
            M(t, "lamp", MachineKind.Consumer, 9, 4, new Cell(8, 4));
            M(t, "tap", MachineKind.Consumer, 5, 4, new Cell(7, 4), new Cell(4, 4));     // CordWorldAdapter.AddTapNodes: ours + bitten
            var bt = new CordBuilder();
            List<LaidPiece> pt = bt.Build(t, new BuildOptions(), c => true);
            VId tapV = VId.Mach("tap");
            List<CordEdge> tapEdges = bt.Graph.CordEdges().Where(e => e.A == tapV || e.B == tapV).ToList();
            bool theirSide = tapEdges.Any(e => e.Chain().Contains(VId.C(new Cell(4, 4))));
            bool ourSide = tapEdges.Any(e => e.Chain().Contains(VId.C(new Cell(7, 4))));
            int intoTap = tapEdges.Count;
            int freeEnds = pt.Sum(p => p.Ends.Count);
            int terminals = bt.Graph.Nodes.Values.Count(n => n.Type == NodeType.Terminal);
            Check(theirSide && ourSide && freeEnds == 0 && terminals == 0,
                  $"tap: their cable and ours both run into the tap node ({intoTap} edges; their side {theirSide}, ours {ourSide}); {terminals} conduit ends, {freeEnds} sparking free ends (want 0)");
            // can fail: the round-2 tap (hooked to OUR conduit only) leaves their conduit a dead end with a free end
            var t2 = new CordWorld(16, 10);
            foreach (Cell c in new[] { new Cell(3, 4), new Cell(4, 4), new Cell(7, 4), new Cell(8, 4) }) t2.SetConduit(c);
            M(t2, "theirbat", MachineKind.Battery, 2, 4, new Cell(3, 4));
            M(t2, "lamp", MachineKind.Consumer, 9, 4, new Cell(8, 4));
            M(t2, "tap", MachineKind.Consumer, 5, 4, new Cell(7, 4));
            var bt2 = new CordBuilder();
            List<LaidPiece> pt2 = bt2.Build(t2, new BuildOptions(), c => true);
            Check(pt2.Sum(p => p.Ends.Count) > 0, "can fail: a tap that is not a node of THEIR graph leaves a free sparking end on their conduit");
            Console.WriteLine($"  review3: wall plates {plates.Count} (on-face rule WallMount); leads {leads.Count}; tap pieces {intoTap}; bundle probe {bundles}");
        }
    }
}
