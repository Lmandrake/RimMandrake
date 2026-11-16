// Owner human review round 4 (2026-10-04, typed notes on stations 6, 9, 19, 26 and the wall plates): the offline,
// load-bearing checks. Each carries a planted fault that must turn it red. The pixel proof of the same rules, against the
// real textures, is src/RimMandrake/Utils/mockups/messy_conduit/wall_mount_check.py (PNGs in Transient/mc_aerial_r4/).
//   plates   every cord wall plate / rock hole is mounted ON its wall face (nothing on the open floor, no deeper than the
//            face allows: the south band, a side bevel, a sliver of a hidden north face), printed without the art's own
//            curl of cord (station 6's hook)
//   loose    (owner 2026-11-16 replaced the round-4 hanging wire) a run ending inside a wall is one loose end on the floor at the
//            face: no plate, no wire hanging out of a hole
//   brackets each look x facing: the plate inside its wall face; the north-face bracket shows only its insulator over the
//            wall's top edge (the torch rule)
//   home     a wall-mounted device's cord ends beneath its WALL's centre, not short of it in the device's cell (station 19)
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ReviewRound4Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review4: " + msg);
        private static readonly string[] Rots = { "North", "East", "South", "West" };

        /// <summary>A walled 7x7 box (walls on its ring) with conduit runs into each of its four sides from outside, a granite
        /// block entered from the south, and one run ending INSIDE the west wall (a wall terminal).</summary>
        private static CordWorld FourFaces()
        {
            var w = new CordWorld(30, 30);
            for (int i = 8; i <= 14; i++)
            {
                w.SetBlocked(new Cell(i, 8), BlockKind.Wall); w.SetBlocked(new Cell(i, 14), BlockKind.Wall);
                w.SetBlocked(new Cell(8, i), BlockKind.Wall); w.SetBlocked(new Cell(14, i), BlockKind.Wall);
            }
            foreach (Cell c in new[] { new Cell(11, 4), new Cell(11, 5), new Cell(11, 6), new Cell(11, 7), new Cell(11, 8), new Cell(11, 9), new Cell(11, 10) }) w.SetConduit(c);   // in through the south wall
            foreach (Cell c in new[] { new Cell(11, 18), new Cell(11, 17), new Cell(11, 16), new Cell(11, 15), new Cell(11, 14), new Cell(11, 13), new Cell(11, 12) }) w.SetConduit(c); // through the north wall
            foreach (Cell c in new[] { new Cell(18, 11), new Cell(17, 11), new Cell(16, 11), new Cell(15, 11), new Cell(14, 11), new Cell(13, 11) }) w.SetConduit(c);   // through the east wall
            foreach (Cell c in new[] { new Cell(4, 11), new Cell(5, 11), new Cell(6, 11), new Cell(7, 11), new Cell(8, 11) }) w.SetConduit(c);   // ENDS in the west wall
            for (int x = 20; x <= 24; x++) for (int z = 20; z <= 22; z++) w.SetBlocked(new Cell(x, z), BlockKind.Rock);
            foreach (Cell c in new[] { new Cell(22, 17), new Cell(22, 18), new Cell(22, 19), new Cell(22, 20), new Cell(22, 21), new Cell(22, 22), new Cell(22, 23), new Cell(22, 24) }) w.SetConduit(c);
            void M(string id, MachineKind k, int x, int z, Cell hook)
            {
                w.SetBlocked(new Cell(x, z), BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, Hookups = new List<Cell> { hook } });
            }
            M("bS", MachineKind.Battery, 11, 3, new Cell(11, 4));
            M("bN", MachineKind.Battery, 11, 19, new Cell(11, 18));
            M("bE", MachineKind.Battery, 19, 11, new Cell(18, 11));
            M("bW", MachineKind.Battery, 3, 11, new Cell(4, 11));
            M("bR", MachineKind.Battery, 22, 16, new Cell(22, 17));
            M("lamp1", MachineKind.Consumer, 11, 11, new Cell(11, 10));
            M("lamp2", MachineKind.Consumer, 12, 12, new Cell(11, 12));
            M("lamp3", MachineKind.Consumer, 12, 11, new Cell(13, 11));
            M("lampR", MachineKind.Consumer, 22, 25, new Cell(22, 24));
            return w;
        }

        public static void Run()
        {
            // ---- plates: every wall plate / rock hole ON its face, cropped to the plate
            CordWorld w = FourFaces();
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, new BuildOptions(), c => true);
            ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
            List<CordDecal> faces = ps.SelectMany(p => p.Decals).Where(d => CordMaterialsIsFace(d.Kind)).ToList();
            var kinds = new HashSet<WallFaceKind>(b.Graph.Nodes.Values.Where(n => n.Type == NodeType.StubWall || n.Type == NodeType.StubRock).Select(n => WallMount.FaceOf(n.Into)));
            bool curlFree = faces.All(d => d.Cropped && d.U0 >= (d.Kind == DecalKind.StubRock ? WallMount.RockU0 : WallMount.WallU0) - 1e-9);
            Check(faces.Count >= 6 && kinds.Count == 3 && r.FlatWallPlates == 0 && r.FlatRockHoles == 0 && r.StubFaults == 0 && curlFree,
                  $"plates: {faces.Count} plates/holes on {kinds.Count} kinds of face, {r.FlatWallPlates + r.FlatRockHoles} not ON the wall, {r.StubFaults} off their cord, curl-free {curlFree}" +
                  (r.Messages.Count > 0 ? " | " + string.Join("; ", r.Messages.Take(3)) : ""));
            // can fail: the round-3 plate (whole canvas, squash 0.5, centred on the face line) pokes out onto the floor
            var r3 = ps.Select(p => new LaidPiece { Key = p.Key, EndA = p.EndA, EndB = p.EndB, Strands = p.Strands,
                Decals = p.Decals.Select(d => CordMaterialsIsFace(d.Kind) ? new CordDecal(d.Kind, d.Pos - new V2(Math.Cos(d.Angle), Math.Sin(d.Angle)) * (d.Pos - FaceOf(b, d)).Len, d.Angle, 0.7) { Squash = 0.5 } : d).ToList() }).ToList();
            ArtFitResult rr3 = CordAudit.ArtFit(b.Graph, r3, c => true);
            Check(rr3.FlatWallPlates + rr3.FlatRockHoles == faces.Count, $"can fail: round-3 plates centred on the face line are caught ({rr3.FlatWallPlates + rr3.FlatRockHoles}/{faces.Count})");

            // ---- loose: the round-4 loose wire hanging out of the wall terminal's hole is gone (owner 2026-11-16: "both a hanging out
            //      sparking end as well as the wire plugging into the same point on the wall. That's not ok"); the run that ends inside the
            //      west wall is ONE loose end on the floor against the face: no plate, no tail, its fray at the face (CordEndKindChecks)
            List<CordStrand> tails = ps.SelectMany(p => p.Strands).Where(s => s.OverFace && s.Lifted).ToList();
            CordNode wt = b.Graph.Nodes.Values.FirstOrDefault(n => n.WallTerminal);
            bool frayAtFace = wt != null && ps.Any(p => p.Decals.Any(d => (d.Kind == DecalKind.FrayLive || d.Kind == DecalKind.FrayDead) && V2.Dist(d.Pos, wt.Face) < 0.35));
            bool plate = wt != null && ps.Any(p => p.Decals.Any(d => CordMaterialsIsFace(d.Kind) && V2.Dist(d.Pos, wt.Face) < 0.35));
            Check(wt != null && tails.Count == 0 && frayAtFace && !plate,
                  $"loose: wall terminal {(wt == null ? "MISSING" : wt.Cell.ToString())}: {tails.Count} tails hanging out of a wall, fray at the face {frayAtFace}, plate {plate}");

            // ---- brackets: the generated per-look table under AerialMath's per-face inset
            Dictionary<string, P2> ins = BracketGeometryTable.Build();
            Dictionary<string, double> edge = BracketGeometryTable.PlateEdge(), depth = BracketGeometryTable.PlateDepth();
            var bad = new List<string>();
            int n = 0;
            foreach (string look in ins.Keys.Select(k => k.Split('/')[0]).Distinct())
                for (int rot = 0; rot < 4; rot++)
                {
                    string key = look + "/" + Rots[rot];
                    n++;
                    double e = edge[key], dp = depth[key];
                    P2 nrm = AerialMath.WallNormal(rot);
                    double off = AerialMath.Dot(AerialMath.BracketDrawOffset(rot, e, dp), nrm);
                    double wallSide = off + e - 0.5, plateOut = wallSide - dp;          // depth into the wall of the plate's two sides
                    if (rot == 2)
                    {
                        double insOver = 0.5 - (off + AerialMath.Dot(ins[key], nrm));   // insulator's height over the wall's top edge
                        if (dp != 0) bad.Add(key + " still draws a plate on the hidden north face");
                        if (wallSide > 0.06) bad.Add(key + $" cut line {wallSide:0.00} deep into the wall top");
                        if (!(insOver > 0 && insOver < 0.25)) bad.Add(key + $" insulator {insOver:0.00} over the wall edge (want 0..0.25)");
                    }
                    else
                    {
                        double lim = rot == 0 ? WallMount.SouthBand : WallMount.SideBevel;
                        if (plateOut < -1e-9) bad.Add(key + $" plate {-plateOut:0.00} OUT of the wall");
                        if (wallSide > lim + 1e-9) bad.Add(key + $" plate {wallSide:0.00} deep, past its face ({lim:0.00})");
                    }
                }
            Check(n >= 16 && bad.Count == 0, $"brackets: {n} look x facing mounted ON their wall face; north-face ones show only the insulator" + (bad.Count > 0 ? ": " + string.Join("; ", bad) : ""));
            // can fail: the round-3 rule (one inset 0.12 for every face) puts Industrial's 0.23-deep north plate out of the wall
            double ie = edge["Industrial/North"], idp = depth["Industrial/North"];
            Check(0.5 + 0.12 - idp < 0.5, $"can fail: round-3's flat 0.12 inset leaves the Industrial south-face plate {idp - 0.12:0.00} out of the wall");

            // ---- home: a wall lamp's cord ends under its wall's centre
            var h = new CordWorld(16, 12);
            for (int x = 2; x <= 12; x++) h.SetBlocked(new Cell(x, 8), BlockKind.Wall);
            foreach (Cell c in new[] { new Cell(3, 4), new Cell(4, 4), new Cell(5, 4), new Cell(6, 4) }) h.SetConduit(c);
            h.SetBlocked(new Cell(2, 4), BlockKind.Device);
            h.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 2, Z0 = 4, Hookups = new List<Cell> { new Cell(3, 4) } });
            var lamp = new MachineInfo { Id = "wl", Kind = MachineKind.Consumer, X0 = 8, Z0 = 7, Hookups = new List<Cell> { new Cell(6, 4) }, HasHome = true, HomeX = 8, HomeZ = 8 };
            h.SetBlocked(new Cell(8, 7), BlockKind.Device);
            h.Machines.Add(lamp);
            V2 wallC = new V2(8.5, 8.5);
            List<LaidPiece> hp = new CordBuilder().Build(h, new BuildOptions(), c => true);
            List<V2> ends = hp.SelectMany(p => p.Strands).Where(s => !s.OverFace).SelectMany(s => new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] }).ToList();
            bool underWall = ends.Any(e => V2.Dist(e, wallC) < 1e-6);
            Check(underWall, $"home: the wall lamp's cord ends under its wall's centre {wallC} (nearest end {ends.OrderBy(e => V2.Dist(e, wallC)).FirstOrDefault()})");
            lamp.HasHome = false;
            List<LaidPiece> hp2 = new CordBuilder().Build(h, new BuildOptions(), c => true);
            bool short2 = !hp2.SelectMany(p => p.Strands).Any(s => V2.Dist(s.Pts[s.Pts.Count - 1], wallC) < 0.3 || V2.Dist(s.Pts[0], wallC) < 0.3);
            Check(short2, "can fail: without a wall home the cord stops short in the lamp's own cell (round 3, station 19)");
            Console.WriteLine($"  review4: plates {faces.Count} on {kinds.Count} face kinds; loose wires {tails.Count}; brackets {n}; wall-home end {underWall}");
        }

        private static bool CordMaterialsIsFace(DecalKind k) => k == DecalKind.StubWall || k == DecalKind.StubRock;

        private static V2 FaceOf(CordBuilder b, CordDecal d)
        {
            CordNode nd = b.Graph.Nodes.Values.Where(x => x.Type == NodeType.StubWall || x.Type == NodeType.StubRock).OrderBy(x => V2.Dist(x.Face, d.Pos)).First();
            return nd.Face;
        }
    }
}
