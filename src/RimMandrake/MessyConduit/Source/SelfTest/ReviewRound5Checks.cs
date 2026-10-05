// Owner human review round 5 (2026-10-04, typed notes on stations 1 and 4): the offline, load-bearing checks. Each carries
// a planted fault that must turn it red.
//   entry    "the cable entering the mass does not join with the rest": a cord into a pile ends ON one of the pile's
//            connector ports (junction arm tip / strip socket, with a plug on a strip), not on the pile's rim
//   scatter  "an unwelcome grid-like nature to the joining boxes sitting on the pile. Should be more randomly aligned":
//            the pile's boxes are off their cell centres, turned to free angles and of varied size
//   tee/plus "Make + and T connectors be relatively the same central size/center": a T and a + node junction are drawn at
//            the same scale with their arm-meeting point on the node
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class ReviewRound5Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review5: " + msg);

        private static bool IsConnector(DecalKind k) =>
            k == DecalKind.JunctionTin || k == DecalKind.JunctionTape || k == DecalKind.PowerStrip || k == DecalKind.PowerStripDark;

        /// <summary>For every cord entering the pile: the distance from its pile-side end to the nearest connector port tip.</summary>
        private static List<double> EntryGaps(List<LaidPiece> ps, out int plugsAtEntry)
        {
            plugsAtEntry = 0;
            LaidPiece pile = ps.First(p => p.Key.StartsWith("tangle:"));
            List<CordBuilder.PilePort> ports = CordBuilder.PortsOf(pile.Decals.Where(d => IsConnector(d.Kind)).ToList());
            var gaps = new List<double>();
            foreach (LaidPiece p in ps.Where(p => (p.EndA ?? "").StartsWith("tangle") || (p.EndB ?? "").StartsWith("tangle")))
                foreach (CordStrand s in p.Strands)
                {
                    bool atA = (p.EndA ?? "").StartsWith("tangle");
                    V2 t = atA ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    gaps.Add(ports.Count == 0 ? double.MaxValue : ports.Min(q => V2.Dist(q.Tip, t)));
                    if (p.Decals.Any(d => d.Kind == DecalKind.Plug && V2.Dist(d.Pos, t) < 0.02)) plugsAtEntry++;
                }
            return gaps;
        }

        /// <summary>Grid score of a pile's connectors: how many sit within 0.08 of their cell centre, how many are turned to a
        /// right angle (within 0.05 rad), and how many distinct scales they use.</summary>
        private static void GridScore(List<CordDecal> cons, out int centred, out int square, out int scales)
        {
            centred = cons.Count(d => V2.Dist(d.Pos, new V2(Math.Floor(d.Pos.X) + 0.5, Math.Floor(d.Pos.Z) + 0.5)) < 0.08);
            square = cons.Count(d =>
            {
                double r = d.Angle % (Math.PI / 2);
                if (r < 0) r += Math.PI / 2;
                return r < 0.05 || r > Math.PI / 2 - 0.05;
            });
            scales = cons.Select(d => Math.Round(d.Scale, 3)).Distinct().Count();
        }

        public static void Run()
        {
            // ---- entry: both pile arts
            foreach (PileArt art in new[] { PileArt.Junctions, PileArt.Strips })
            {
                List<LaidPiece> ps = new CordBuilder().Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Pile = art }, c => true);
                List<double> gaps = EntryGaps(ps, out int plugs);
                Check(gaps.Count >= 2 && gaps.All(g => g < 0.04),
                      $"entry ({art}): {gaps.Count} cords enter the pile, worst end {(gaps.Count > 0 ? gaps.Max() : -1):0.000} cells from a connector port (want <= 0.04)");
                if (art == PileArt.Strips)
                    Check(plugs >= gaps.Count, $"entry (strips): {plugs} plugs at the {gaps.Count} entering cord ends (want one each)");
            }
            // can fail: the round-4 end (the pile rim point the graph gives) is NOT on a port
            {
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Pile = PileArt.Junctions }, c => true);
                LaidPiece pile = ps.First(p => p.Key.StartsWith("tangle:"));
                List<CordBuilder.PilePort> ports = CordBuilder.PortsOf(pile.Decals.Where(d => IsConnector(d.Kind)).ToList());
                var rims = b.Graph.CordEdges().Where(e => b.Graph.Nodes[e.A].Type == NodeType.Tangle || b.Graph.Nodes[e.B].Type == NodeType.Tangle)
                    .Select(e => b.Graph.Nodes[e.A].Type == NodeType.Tangle ? e.PA : e.PB).ToList();
                Check(rims.Count >= 2 && rims.Any(r => ports.Min(q => V2.Dist(q.Tip, r)) > 0.04),
                      "can fail: the old rim end point is off every port (the bug this check guards)");
            }
            // ---- scatter: several seeds, so a lucky draw cannot pass
            int cTot = 0, cCentred = 0, cSquare = 0, minScales = int.MaxValue;
            for (ulong seed = 1; seed <= 6; seed++)
            {
                List<LaidPiece> ps = new CordBuilder().Build(ReviewRound1Checks.PileWorld(), new BuildOptions { Pile = PileArt.Junctions, Seed = seed }, c => true);
                List<CordDecal> cons = ps.First(p => p.Key.StartsWith("tangle:")).Decals.Where(d => IsConnector(d.Kind)).ToList();
                GridScore(cons, out int centred, out int square, out int scales);
                cTot += cons.Count; cCentred += centred; cSquare += square; minScales = Math.Min(minScales, scales);
            }
            Check(cTot >= 12 && cCentred * 4 <= cTot && cSquare * 4 <= cTot && minScales >= 2,
                  $"scatter: {cTot} pile boxes over 6 seeds, {cCentred} on a cell centre, {cSquare} square to the grid, >= {minScales} sizes per pile (want <= 1/4, <= 1/4, >= 2)");
            {
                var planted = new List<CordDecal> { new CordDecal(DecalKind.JunctionTin, new V2(7.5, 7.5), 0, 0.8), new CordDecal(DecalKind.JunctionTape, new V2(8.5, 8.5), Math.PI / 2, 0.8) };
                GridScore(planted, out int pc, out int pq, out int pscales);
                Check(pc == 2 && pq == 2 && pscales == 1, "can fail: a planted grid of boxes (cell centres, right angles, one size) scores as a grid");
            }
            // ---- tee/plus: a run with a T and a + node
            {
                var w = new CordWorld(24, 16);
                for (int x = 2; x <= 16; x++) w.SetConduit(new Cell(x, 8));
                for (int z = 4; z <= 7; z++) w.SetConduit(new Cell(6, z));                       // T at (6,8)
                for (int z = 4; z <= 12; z++) if (z != 8) w.SetConduit(new Cell(11, z));         // + at (11,8)
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions(), c => true);
                var tee = ps.FirstOrDefault(p => p.Key.StartsWith("node:") && p.Owner.X == 6 && p.Owner.Z == 8);
                var plus = ps.FirstOrDefault(p => p.Key.StartsWith("node:") && p.Owner.X == 11 && p.Owner.Z == 8);
                CordDecal? td = tee?.Decals.FirstOrDefault(), xd = plus?.Decals.FirstOrDefault();
                bool kinds = td.HasValue && xd.HasValue && td.Value.Kind == DecalKind.JunctionTape && xd.Value.Kind == DecalKind.JunctionTin;
                double tCentreErr = double.MaxValue, xCentreErr = double.MaxValue;
                if (kinds)
                {
                    V2 meet = td.Value.Pos + CordAudit.Rot(new V2(0, CordBuilder.TapeAnchorZ * td.Value.Scale), td.Value.Angle);
                    tCentreErr = V2.Dist(meet, new V2(6.5, 8.5));
                    xCentreErr = V2.Dist(xd.Value.Pos, new V2(11.5, 8.5));
                }
                Check(kinds && Math.Abs(td.Value.Scale - xd.Value.Scale) < 1e-9 && td.Value.Scale >= 1.1 && tCentreErr < 0.2 && xCentreErr < 0.2,
                      $"tee/plus: T and + drawn at scales {(kinds ? td.Value.Scale : -1):0.00} / {(kinds ? xd.Value.Scale : -1):0.00} (want equal, >= 1.1), arm-meeting point {tCentreErr:0.000} / {xCentreErr:0.000} from the node centre");
            }
        }
    }
}
