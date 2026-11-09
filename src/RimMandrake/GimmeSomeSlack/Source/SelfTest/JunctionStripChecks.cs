// d_modern_junction_strip (owner 2026-11-05, item GSS_MODERN_STRIP_BUILD_PLUGS_AT_LAST): a Modern 3-way or 4-way junction draws the
// long power strip, each cord plugged into a socket and the strip's own lead taking one arm; Industrial keeps its box.
// Every row reads the laid pieces through CordAudit (which poses from the decal alone) and carries a planted fault.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class JunctionStripChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "junction-strip: " + msg);

        /// <summary>A run with a T, a + and a 2-way bend, far apart; ten cells of slack room around each.</summary>
        internal static CordWorld Board()
        {
            var w = new CordWorld(44, 26);
            for (int x = 2; x <= 40; x++) w.SetConduit(new Cell(x, 12));
            for (int z = 4; z <= 11; z++) w.SetConduit(new Cell(10, z));                 // T at (10,12)
            for (int z = 4; z <= 20; z++) if (z != 12) w.SetConduit(new Cell(22, z));    // + at (22,12)
            for (int x = 30; x <= 36; x++) w.SetConduit(new Cell(x, 20));                // a separate run with a bend at (30,20)
            for (int z = 16; z <= 20; z++) w.SetConduit(new Cell(30, z));
            return w;
        }

        /// <summary>A small blob junction: a 2x2 block of conduit with cords leaving it on three sides.</summary>
        internal static CordWorld Blob()
        {
            var w = new CordWorld(30, 24);
            for (int x = 12; x <= 13; x++) for (int z = 10; z <= 11; z++) w.SetConduit(new Cell(x, z));
            for (int x = 3; x <= 11; x++) w.SetConduit(new Cell(x, 10));
            for (int x = 14; x <= 24; x++) w.SetConduit(new Cell(x, 11));
            for (int z = 12; z <= 20; z++) w.SetConduit(new Cell(13, z));
            return w;
        }

        /// <summary>A room: a run along the north wall with branches down to a machine, a two-wide block, a T on a wall stub.</summary>
        internal static CordWorld Base()
        {
            var w = new CordWorld(34, 26);
            for (int x = 4; x <= 28; x++) { w.SetBlocked(new Cell(x, 20), BlockKind.Wall); w.SetBlocked(new Cell(x, 4), BlockKind.Wall); }
            for (int z = 4; z <= 20; z++) { w.SetBlocked(new Cell(4, z), BlockKind.Wall); w.SetBlocked(new Cell(28, z), BlockKind.Wall); }
            for (int x = 6; x <= 26; x++) w.SetConduit(new Cell(x, 18));
            w.SetConduit(new Cell(10, 19)); w.SetConduit(new Cell(10, 20));                 // a T on a stub into the north wall
            foreach (int bx in new[] { 8, 13, 14, 20 })
                for (int z = 12; z <= 17; z++) w.SetConduit(new Cell(bx, z));               // branches; 13 and 14 side by side form a block
            for (int x = 15; x <= 25; x++) w.SetConduit(new Cell(x, 9));
            for (int z = 9; z <= 17; z++) w.SetConduit(new Cell(25, z));                    // a loop back to the run
            w.SetBlocked(new Cell(8, 10), BlockKind.Device); w.SetBlocked(new Cell(8, 11), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bench", Kind = MachineKind.Consumer, X0 = 8, Z0 = 10, W = 1, H = 2, Hookups = new List<Cell> { new Cell(8, 12) } });
            return w;
        }

        internal static BuildOptions Modern(ulong seed = 1) => new BuildOptions { Pile = PileArt.Strips, Seed = seed };

        private static int Count(List<LaidPiece> ps, params DecalKind[] kinds) => ps.Sum(p => p.Decals.Count(d => kinds.Contains(d.Kind)));
        private static readonly DecalKind[] Strip = { DecalKind.PowerStrip, DecalKind.PowerStripDark };
        private static readonly DecalKind[] Box = { DecalKind.JunctionTape, DecalKind.JunctionTin };

        public static void Run()
        {
            // every seed: one strip per junction, no box, every cord on a socket under its plug or on the lead, none on a bend
            int faults = 0, strips = 0;
            for (ulong seed = 1; seed <= 24; seed++)
            {
                CordWorld w = Board();
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, Modern(seed), c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                faults += r.JunctionFaults;
                if (r.JunctionFaults > 0) foreach (string m in r.Messages.Take(3)) Console.WriteLine("  seed " + seed + ": " + m);
                strips += Count(ps, Strip);
                Check(Count(ps, Strip) == 2 && Count(ps, Box) == 0, $"seed {seed}: T and + draw {Count(ps, Strip)} strips and {Count(ps, Box)} boxes (want 2, 0; a bend draws neither)");
                Check(r.JunctionStrips == 2, $"seed {seed}: audit read {r.JunctionStrips} junction strips");
                LaidPiece bend = ps.FirstOrDefault(p => p.Key.StartsWith("node:") && p.Owner == new Cell(30, 20));
                Check(bend == null, $"seed {seed}: a 2-way bend draws a joining piece");
            }
            Check(faults == 0, $"{faults} junction faults over 24 seeds of T and +");
            Console.WriteLine($"  junction strips: {strips} over 24 seeds, {faults} faults");

            // a machine right beside a strip takes the strip's own lead: sockets facing it sent a through cord along its edge, which read as two cords into it
            {
                int wrong = 0;
                for (ulong seed = 1; seed <= 12; seed++)
                {
                    var w = new CordWorld(30, 24);
                    for (int x = 3; x <= 24; x++) w.SetConduit(new Cell(x, 10));
                    for (int x = 12; x <= 13; x++) for (int z = 11; z <= 13; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
                    w.Machines.Add(new MachineInfo { Id = "battery", Kind = MachineKind.Battery, X0 = 12, Z0 = 11, W = 2, H = 3, Hookups = new List<Cell> { new Cell(12, 10) } });
                    var b = new CordBuilder();
                    b.Build(w, Modern(seed), c => true);
                    VId v = VId.C(new Cell(12, 10));
                    if (b.Graph.Nodes[v].Type != NodeType.Junction || !b.Graph.MachineArmsOf(v).Contains(new Cell(0, 1)) || CordBuilder.PoseStrip(b.Graph, v, seed).LeadArm != new Cell(0, 1)) wrong++;
                }
                Check(wrong == 0, $"a machine beside a strip takes its lead: {wrong} of 12 seeds did not");
            }

            // the arms: a T's three arms are two plugged cords and the lead; a +'s four are three plugged and the lead
            {
                CordWorld w = Board();
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions { Pile = PileArt.Strips, Seed = 3, Lay = { CordsMax = 1 } }, c => true);
                int PlugsAt(int x, int z) => ps.Where(p => p.EndA != null && (p.EndA.EndsWith(":" + x + "," + z) || p.EndB.EndsWith(":" + x + "," + z)))
                                               .Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PlugTop && V2.Dist(d.Pos, new V2(x + 0.5, z + 0.5)) < 0.6));
                Check(PlugsAt(10, 12) == 2, $"a T wears {PlugsAt(10, 12)} plugs (want 2 cords plus the lead)");
                Check(PlugsAt(22, 12) == 3, $"a + wears {PlugsAt(22, 12)} plugs (want 3 cords plus the lead)");
            }

            // a blob junction takes the strip too, and its cords reach it
            {
                CordWorld w = Blob();
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, Modern(5), c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                Check(b.Graph.Nodes.Values.Any(n => n.IsBlob), "the blob scene holds a blob junction");
                Check(r.JunctionStrips == 1 && r.JunctionFaults == 0, $"blob strip: {r.JunctionStrips} strips, {r.JunctionFaults} faults: {string.Join("; ", r.Messages.Take(3))}");
            }

            // the control: Industrial keeps its box at T, + and blob, each cord on an arm (the audit now covers blobs in every look)
            foreach (CordWorld w in new[] { Board(), Blob() })
            {
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions { Pile = PileArt.Junctions }, c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                Check(Count(ps, Strip) == 0 && Count(ps, Box) > 0 && r.JunctionFaults == 0, $"box look: {Count(ps, Strip)} strips, {Count(ps, Box)} boxes, {r.JunctionFaults} faults: {string.Join("; ", r.Messages.Take(3))}");
            }

            // one look per run: PileAt puts a strip in the Modern run's junction and a box in its neighbour's
            {
                CordWorld w = Board();
                var opt = new BuildOptions { PileAt = c => c.X < 16 ? PileArt.Junctions : PileArt.Strips };
                List<LaidPiece> ps = new CordBuilder().Build(w, opt, c => true);
                Check(ps.Count(p => p.Key.StartsWith("node:") && p.Decals.Any(d => Strip.Contains(d.Kind))) == 1 &&
                      ps.Count(p => p.Key.StartsWith("node:") && p.Decals.Any(d => Box.Contains(d.Kind))) == 1, "per-run look: one junction takes the strip and one the box");
            }

            // the LEDs read the net, on one kept graph, and the look's change is picked up with no re-reduce
            {
                CordWorld w = Board();
                var b = new CordBuilder();
                List<LaidPiece> lit = b.Build(w, Modern(), c => true);
                List<LaidPiece> dark = b.Build(w, Modern(), c => false);
                LaidPiece a = lit.First(p => p.Key.StartsWith("node:") && p.Owner == new Cell(10, 12));
                LaidPiece z = dark.First(p => p.Key.StartsWith("node:") && p.Owner == new Cell(10, 12));
                Check(a.Decals[0].Kind == DecalKind.PowerStrip && z.Decals[0].Kind == DecalKind.PowerStripDark, "a dead net's strip goes dark");
                Check(RebuildTail.PieceSig(a) != RebuildTail.PieceSig(z), "a flipped strip changes its section's signature, so it repaints");
                Check(V2.Dist(a.Decals[0].Pos, z.Decals[0].Pos) < 1e-9 && a.Decals[0].Angle == z.Decals[0].Angle, "the flip does not move the strip");
                Check(a.LiveKeys.Contains(new Cell(10, 12)), "the poll watches the strip's own cell");
                Check(b.Build(w, Modern(), c => true).Contains(a), "a strip is kept per LED state: an unchanged Build allocates no new piece");
            }

            // planted faults: the audit goes red on a strip whose cords stop short, and on a box where a strip's cords end
            {
                CordWorld w = Board();
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, Modern(2), c => true);
                ArtFitResult clean = CordAudit.ArtFit(b.Graph, ps, c => true);
                var moved = ps.Select(p =>
                {
                    if (!p.Key.StartsWith("node:") || !p.Decals.Any(d => Strip.Contains(d.Kind))) return p;
                    CordDecal d0 = p.Decals[0];
                    var q = new LaidPiece { Key = p.Key, Owner = p.Owner };
                    q.Decals.Add(new CordDecal(d0.Kind, d0.Pos, d0.Angle + Math.PI / 2, d0.Scale));      // turned, so no cord meets a socket
                    return q;
                }).ToList();
                Check(clean.JunctionFaults == 0 && CordAudit.ArtFit(b.Graph, moved, c => true).JunctionFaults > 0, "planted: a strip turned off its cords is a junction fault");
                var unplugged = ps.Select(p =>
                {
                    if (p.EndA == null) return p;
                    var q = new LaidPiece { Key = p.Key, Owner = p.Owner, EndA = p.EndA, EndB = p.EndB };
                    q.Strands.AddRange(p.Strands);
                    q.Decals.AddRange(p.Decals.Where(d => d.Kind != DecalKind.Plug && d.Kind != DecalKind.PlugTop));
                    return q;
                }).ToList();
                Check(CordAudit.ArtFit(b.Graph, unplugged, c => true).JunctionFaults > 0, "planted: cords on sockets with their plugs gone is a junction fault");
            }

            // no two-cord crossing, nothing on a wall: a T hard against a wall still draws inside its own open cell
            {
                var w = new CordWorld(30, 20);
                for (int x = 4; x <= 24; x++) w.SetConduit(new Cell(x, 9));
                for (int z = 3; z <= 8; z++) w.SetConduit(new Cell(14, z));
                for (int x = 0; x < 30; x++) if (x != 14) w.SetBlocked(new Cell(x, 10), BlockKind.Wall);
                w.SetBlocked(new Cell(14, 10), BlockKind.Wall);
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, Modern(4), c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                LaidPiece n = ps.First(p => p.Key.StartsWith("node:") && p.Owner == new Cell(14, 9));
                CordDecal d = n.Decals[0];
                V2 along = CordAudit.Dir(d.Angle), end1 = d.Pos + along * (0.46 * d.Scale), end2 = d.Pos - along * (0.46 * d.Scale);
                Check(end1.Floor == new Cell(14, 9) && end2.Floor == new Cell(14, 9), $"a strip beside a wall stays in its own cell: ends {end1} {end2}");
                Check(r.JunctionFaults == 0, $"T beside a wall: {string.Join("; ", r.Messages.Take(3))}");
            }

            // GSS_STRIP_LED_FIX_MISSED_REPAINT: a tangle's key is fixed, so the signature has to carry its strips' LED state
            {
                var w = new CordWorld(30, 30);
                for (int x = 8; x <= 14; x++) for (int z = 8; z <= 14; z++) w.SetConduit(new Cell(x, z));
                var b = new CordBuilder();
                LaidPiece a = b.Build(w, Modern(), c => true).First(p => p.Key.StartsWith("tangle:"));
                LaidPiece z2 = b.Build(w, Modern(), c => false).First(p => p.Key.StartsWith("tangle:"));
                Check(a.Key == z2.Key && a.Decals.Any(d => d.Kind == DecalKind.PowerStrip) && z2.Decals.Any(d => d.Kind == DecalKind.PowerStripDark), "a dead tangle's strips go dark under one key");
                Check(RebuildTail.PieceSig(a) != RebuildTail.PieceSig(z2), "a tangle's LED flip changes its section's signature");
            }

            // GSS_COLOUR_SEED_FIX_HIDDEN_CONDUIT_SPLIT: two runs joined through a wall are one net, one seed; a run not joined keeps its own
            {
                var w = new CordWorld(30, 12);
                for (int x = 2; x <= 26; x++) w.SetConduit(new Cell(x, 5));
                for (int z = 0; z < 12; z++) w.SetBlocked(new Cell(14, z), BlockKind.Wall);
                for (int x = 2; x <= 10; x++) w.SetConduit(new Cell(x, 9));
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions(), c => true);
                List<LaidPiece> west = ps.Where(p => p.EndA != null && p.Owner.Z == 5 && p.Owner.X < 14).ToList(), east = ps.Where(p => p.EndA != null && p.Owner.Z == 5 && p.Owner.X > 14).ToList();
                LaidPiece apart = ps.First(p => p.EndA != null && p.Owner.Z == 9);
                Dictionary<LaidPiece, int> bare = RebuildTail.NetSeeds(ps), joined = RebuildTail.NetSeeds(ps, b.Graph.HiddenLinks);
                Check(west.Count > 0 && east.Count > 0 && bare[west[0]] != bare[east[0]], "control: without the hidden link the two sides of a wall read two seeds");
                Check(joined[west[0]] == joined[east[0]], "the two sides of a wall share one seed");
                Check(joined[apart] != joined[west[0]], "a separate run keeps its own seed");
                Check(b.Graph.HiddenLinks.Count > 0, "the scene holds a hidden edge");
            }

            // GSS_CORD_AUDIT_FIX_REJECTS_WALL_PLUGS: a wall device's plug under its wall fits; a plug out on the floor does not
            {
                var w = new CordWorld(24, 16);
                for (int x = 2; x <= 10; x++) w.SetConduit(new Cell(x, 6));
                for (int x = 0; x < 24; x++) w.SetBlocked(new Cell(x, 8), BlockKind.Wall);
                w.SetBlocked(new Cell(11, 7), BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "wallLamp", Kind = MachineKind.Consumer, X0 = 11, Z0 = 7, W = 1, H = 1, HasHome = true, HomeX = 11, HomeZ = 8, Hookups = new List<Cell> { new Cell(10, 6) } });
                w.SetConduit(new Cell(11, 6));
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions { Lay = { CordsMax = 1 } }, c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                Check(ps.SelectMany(p => p.Decals).Any(d => d.Kind == DecalKind.Plug && d.Pos.Z >= 8), "control: the wall device's plug really lies past its own footprint, under the wall");
                Check(r.PlugEnds > 0 && r.PlugFaults == 0, $"wall device: {r.PlugEnds} plug ends, {r.PlugFaults} faults: {string.Join("; ", r.Messages.Take(2))}");
                var w2 = new CordWorld(24, 16);
                for (int x = 2; x <= 11; x++) w2.SetConduit(new Cell(x, 6));
                w2.SetBlocked(new Cell(11, 7), BlockKind.Device);
                w2.Machines.Add(new MachineInfo { Id = "floorLamp", Kind = MachineKind.Consumer, X0 = 11, Z0 = 7, W = 1, H = 1, Hookups = new List<Cell> { new Cell(11, 6) } });
                var b2 = new CordBuilder();
                List<LaidPiece> ps2 = b2.Build(w2, new BuildOptions { Lay = { CordsMax = 1 } }, c => true);
                MachineInfo moved = b2.Graph.Nodes.Values.First(n => n.Machine != null).Machine;
                moved.X0 = 3; moved.Z0 = 11;     // planted: the plug now lies outside the footprint, no home to excuse it
                Check(CordAudit.ArtFit(b2.Graph, ps2, c => true).PlugFaults > 0, "planted: a plug outside its device with no home is still a fault");
            }

            // a real base: branches off a run along a wall every few cells, Ts right beside each other, a T on a stub into the wall, a machine lead
            {
                CordWorld w = Base();
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, Modern(9), c => true);
                ArtFitResult r = CordAudit.ArtFit(b.Graph, ps, c => true);
                int fell = ps.Sum(p => p.Strands.Count(st => st.FellBack));
                // two true junctions: (10,18) on its wall stub and (20,18); the 13-14 block is a tangle and the run's ends are spurs
                Check(r.JunctionStrips == 2 && r.JunctionFaults == 0, $"base: {r.JunctionStrips} strips, {r.JunctionFaults} faults: {string.Join("; ", r.Messages.Take(4))}");
                Check(fell == 0, $"base: {fell} strands fell back to the centreline");
                if (Program.dumpDir != null) Program.Dump("junction_strip_base", w, ps);
            }

            if (Program.dumpDir != null)
            {
                CordWorld w = Board();
                Program.Dump("junction_strip_board", w, new CordBuilder().Build(w, new BuildOptions { Pile = PileArt.Strips, Seed = 11 }, c => c.X != 36 && c.Z != 20));
                CordWorld bl = Blob();
                Program.Dump("junction_strip_blob", bl, new CordBuilder().Build(bl, Modern(7), c => true));
                CordWorld w2 = Board();
                Program.Dump("junction_box_board", w2, new CordBuilder().Build(w2, new BuildOptions { Pile = PileArt.Junctions, Seed = 11 }, c => true));
            }
        }
    }
}
