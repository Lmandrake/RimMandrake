// Owner human review round 1 (2026-10-04, item MESSYCONDUIT_REVIEW_ROUND1_1): the offline, load-bearing checks of the
// floor-cord bars. Few checks, each proving a property the owner judged by eye, each with a planted fault that must
// turn it red (a check that cannot fail proves nothing).
//   B1/B15  Star Wars, Jawa and Cybertek piles carry NO power strip (strips are the modern extension-cord look only)
//   B2      that pile is a mass of cables plugged into MANY + and T junction boxes: every cable end on a box arm,
//           every box with >= 2 cables in it
//   B13     the modern pile's strips all have cables PLUGGED IN (a plug in each used socket, >= 2 cables per strip)
//   B4      rock-entry holes are drawn foreshortened (angled like the rock face), still on the face line
//   B10     a cord into a machine whose art stops short of its footprint edge (solar panel) runs on under the art
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class ReviewRound1Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review1: " + msg);

        private static MachineInfo M(CordWorld w, string id, MachineKind k, int x, int z, int wd, int h, Cell hook)
        {
            for (int i = 0; i < wd; i++) for (int j = 0; j < h; j++) w.SetBlocked(new Cell(x + i, z + j), BlockKind.Device);
            var m = new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, W = wd, H = h, Hookups = new List<Cell> { hook } };
            w.Machines.Add(m);
            return m;
        }

        /// <summary>Station 4 of the review map: battery, a run, a 3x3 conduit block (a tangle), a run, a heater.</summary>
        internal static CordWorld PileWorld()
        {
            var w = new CordWorld(30, 16);
            for (int x = 3; x <= 6; x++) w.SetConduit(new Cell(x, 8));
            for (int x = 7; x <= 9; x++) for (int z = 7; z <= 9; z++) w.SetConduit(new Cell(x, z));
            for (int x = 10; x <= 12; x++) w.SetConduit(new Cell(x, 8));
            M(w, "bat", MachineKind.Battery, 2, 8, 1, 1, new Cell(3, 8));
            M(w, "heat", MachineKind.Consumer, 13, 8, 1, 1, new Cell(12, 8));
            return w;
        }

        public static void Run()
        {
            // ---- B1/B2/B15: junction piles
            CordWorld w = PileWorld();
            var bj = new CordBuilder();
            List<LaidPiece> pj = bj.Build(w, new BuildOptions { Pile = PileArt.Junctions }, c => true);
            ArtFitResult rj = CordAudit.ArtFit(bj.Graph, pj, c => true);
            Check(rj.Piles == 1, $"junction look: {rj.Piles} piles in the 3x3 block (want 1)");
            Check(rj.Strips == 0, $"B1/B15: the Star Wars/Jawa/Cybertek look drew {rj.Strips} power strips (want 0)");
            Check(rj.PileJunctions >= 3, $"B2: the pile has {rj.PileJunctions} junction boxes (want many, >= 3)");
            Check(rj.PileLooseEnds == 0 && rj.PileIdleConnectors == 0,
                  $"B2: pile cables plugged in: {rj.PileLooseEnds} loose cable ends, {rj.PileIdleConnectors} boxes with < 2 cables");
            LaidPiece tj = pj.First(p => p.Key.StartsWith("tangle:"));
            Check(tj.Strands.Count >= 6, $"B2: the pile is a MASS of cables ({tj.Strands.Count} cables, want >= 6)");
            // ---- B13: strip piles (modern look)
            var bs = new CordBuilder();
            List<LaidPiece> ps = bs.Build(w, new BuildOptions { Pile = PileArt.Strips }, c => true);
            ArtFitResult rs = CordAudit.ArtFit(bs.Graph, ps, c => true);
            LaidPiece ts = ps.First(p => p.Key.StartsWith("tangle:"));
            int plugs = ts.Decals.Count(d => d.Kind == DecalKind.Plug);
            Check(rs.Strips >= 1 && rs.PileJunctions == 0, $"modern look: {rs.Strips} strips, {rs.PileJunctions} junction boxes in the pile");
            Check(rs.PileLooseEnds == 0 && rs.PileIdleConnectors == 0 && plugs >= 2 * rs.Strips,
                  $"B13: strips plugged in: {rs.PileLooseEnds} loose ends, {rs.PileIdleConnectors} strips with < 2 cables, {plugs} plugs for {rs.Strips} strips");
            // planted faults: a cable end pulled off its port, and an empty strip, must both be seen
            LaidPiece bad = new LaidPiece { Key = ts.Key, Decals = new List<CordDecal>(ts.Decals) };
            bad.Strands.AddRange(ts.Strands.Skip(1));
            var moved = new List<V2>(ts.Strands[0].Pts);
            moved[0] = moved[0] + new V2(0.3, 0);
            bad.Strands.Add(new CordStrand { Pts = moved });
            bad.Decals.Add(new CordDecal(DecalKind.PowerStrip, new V2(8.5, 8.5), 0, CordBuilder.StripScale));
            ArtFitResult rb = CordAudit.ArtFit(bs.Graph, ps.Where(p => p != ts).Concat(new[] { bad }).ToList(), c => true);
            Check(rb.PileLooseEnds >= 1 && rb.PileIdleConnectors >= 1, $"can fail: planted loose end -> {rb.PileLooseEnds}, planted empty strip -> idle {rb.PileIdleConnectors}");
            // determinism: same world, same pile
            List<LaidPiece> pj2 = new CordBuilder().Build(PileWorld(), new BuildOptions { Pile = PileArt.Junctions }, c => true);
            Check(pj2.First(p => p.Key.StartsWith("tangle:")).GeometryHash() == tj.GeometryHash(), "pile geometry not deterministic");
            if (Program.dumpDir != null) { Program.Dump("review1_pile_junctions", w, pj); Program.Dump("review1_pile_strips", w, ps); }
            Console.WriteLine($"  review1 piles: junction look {rj.PileJunctions} boxes / {tj.Strands.Count} cables / {rj.Strips} strips; modern {rs.Strips} strips / {plugs} plugs");

            // ---- B4: rock-entry holes foreshortened like the rock face
            var wr = new CordWorld(24, 12);
            for (int x = 3; x <= 15; x++) wr.SetConduit(new Cell(x, 5));
            for (int x = 8; x <= 10; x++) for (int z = 3; z <= 7; z++) wr.SetBlocked(new Cell(x, z), BlockKind.Rock);
            M(wr, "bat", MachineKind.Battery, 2, 5, 1, 1, new Cell(3, 5));
            M(wr, "heat", MachineKind.Consumer, 16, 5, 1, 1, new Cell(15, 5));
            var br = new CordBuilder();
            List<LaidPiece> pr = br.Build(wr, new BuildOptions(), c => true);
            ArtFitResult rr = CordAudit.ArtFit(br.Graph, pr, c => true);
            int holes = pr.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.StubRock));
            Check(holes >= 2 && rr.FlatRockHoles == 0 && rr.StubFaults == 0, $"B4: {holes} rock holes, {rr.FlatRockHoles} not mounted ON the rock face, {rr.StubFaults} off the face");
            var flat = pr.Select(p => new LaidPiece { Key = p.Key, EndA = p.EndA, EndB = p.EndB, Strands = p.Strands,
                Decals = p.Decals.Select(d => d.Kind == DecalKind.StubRock ? new CordDecal(d.Kind, d.Pos, d.Angle, d.Scale) : d).ToList() }).ToList();
            Check(CordAudit.ArtFit(br.Graph, flat, c => true).FlatRockHoles == holes, "can fail: planted square (unforeshortened) rock holes not counted");

            // ---- B10: the solar panel: the cord runs on under the art (inset 0.4 on its bottom edge)
            var ws = new CordWorld(24, 16);
            for (int x = 3; x <= 14; x++) ws.SetConduit(new Cell(x, 4));
            M(ws, "bat", MachineKind.Battery, 2, 4, 1, 1, new Cell(3, 4));
            MachineInfo sol = M(ws, "solar", MachineKind.Source, 10, 5, 4, 4, new Cell(11, 4));
            sol.InsetS = 0.4;
            var bsol = new CordBuilder();
            List<LaidPiece> psol = bsol.Build(ws, new BuildOptions(), c => true);
            ArtFitResult rsol = CordAudit.ArtFit(bsol.Graph, psol, c => true);
            List<V2> ends = psol.SelectMany(p => p.Strands).SelectMany(st => new[] { st.Pts[0], st.Pts[st.Pts.Count - 1] })
                                .Where(e => e.X > 10 && e.X < 14 && e.Z > 4.9 && e.Z < 9).ToList();
            double depth = ends.Count == 0 ? -1 : ends.Min(e => e.Z - sol.Z0);
            Check(ends.Count > 0 && depth >= 0.38, $"B10: cords into the solar panel end {depth:0.00} cell inside its bottom edge (want >= 0.38: under the panel art, not at its legs)");
            Check(rsol.PlugFaults == 0, $"B10: {rsol.PlugFaults} plug faults at the inset machine");
            if (rsol.PlugFaults > 0) Console.WriteLine("  " + string.Join("; ", rsol.Messages));
            Console.WriteLine($"  review1: rock holes {holes} (on-face rule WallMount); solar cord depth {depth:0.00}");
        }
    }
}
