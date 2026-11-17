// RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: every live cut end the builder lays, over the worlds the game can make near one (an
// enumerated family: what the cord comes from x how long the run is x where it last turns x what stands beside the end x look x seed; the oracle's
// scenes; the fuzz's random worlds), read by the three bars' own instruments. `--live-census OUT.jsonl [FUZZ_SEEDS]` writes one line per live end
// for the Python sweep (src/RimMandrake/Utils/mockups/messy_conduit/live_end_sweep.py); LiveEndSweepChecks gates the same family in the suite.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LiveEndCensus
    {
        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
        private static Cell Add(Cell c, Cell d, int k) => new Cell(c.X + d.X * k, c.Z + d.Z * k);
        private static Cell Left(Cell d) => new Cell(-d.Z, d.X);

        /// <summary>What the cord to the cut end comes from.</summary>
        internal static readonly string[] Froms = { "box", "boxX", "battery", "lamp", "big", "wall", "rock", "cut" };
        /// <summary>What stands beside the cut end: nothing, a wall across its mouth, a wall along one side, a dead-end pocket.</summary>
        internal static readonly string[] Besides = { "open", "ahead", "side", "pocket" };

        /// <summary>One world: a run of <paramref name="len"/> cells leaves its fitting along <paramref name="d"/>, turns (<paramref name="turn"/>: 0 none, 1 left, -1 right)
        /// and runs <paramref name="after"/> cells more to a cut end on the floor.</summary>
        internal static CordWorld Scene(string from, Cell d, int len, int turn, int after, string beside)
        {
            var w = new CordWorld(40, 40);
            Cell c = new Cell(20, 20), p = Left(d);
            if (from == "box" || from == "boxX")
            {
                // a through run across the fitting's cell, a battery one side and a lamp the other
                for (int k = -5; k <= 5; k++) w.SetConduit(Add(c, p, k));
                Cell bat = Add(c, p, -6), lamp = Add(c, p, 6);
                w.SetBlocked(bat, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = bat.X, Z0 = bat.Z, Hookups = new List<Cell> { Add(c, p, -5) } });
                w.SetBlocked(lamp, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = lamp.X, Z0 = lamp.Z, Hookups = new List<Cell> { Add(c, p, 5) } });
                if (from == "boxX")
                {
                    for (int k = 1; k <= 4; k++) w.SetConduit(Add(c, d, -k));
                    Cell l2 = Add(c, d, -5);
                    w.SetBlocked(l2, BlockKind.Device);
                    w.Machines.Add(new MachineInfo { Id = "lamp2", Kind = MachineKind.Lamp, X0 = l2.X, Z0 = l2.Z, Hookups = new List<Cell> { Add(c, d, -4) } });
                }
            }
            else if (from == "battery" || from == "lamp" || from == "big")
            {
                int sz = from == "big" ? 2 : 1;
                // the machine stands behind c; c is its hookup cell
                Cell m0 = Add(c, d, -1);
                int x0 = Math.Min(m0.X, m0.X - d.X * (sz - 1)), z0 = Math.Min(m0.Z, m0.Z - d.Z * (sz - 1));
                for (int x = x0; x < x0 + sz; x++) for (int z = z0; z < z0 + sz; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "m", Kind = from == "lamp" ? MachineKind.Lamp : MachineKind.Battery, X0 = x0, Z0 = z0, W = sz, H = sz, Hookups = new List<Cell> { c } });
                w.SetConduit(c);
            }
            else if (from == "wall" || from == "rock")
            {
                BlockKind kind = from == "wall" ? BlockKind.Wall : BlockKind.Rock;
                // a wall behind c; the conduit comes through it from a battery on the far side
                for (int t = -4; t <= 4; t++) w.SetBlocked(Add(Add(c, d, -1), p, t), kind);
                for (int k = 1; k <= 4; k++) w.SetConduit(Add(c, d, -k));
                w.SetConduit(c);
                Cell bat = Add(c, d, -5);
                w.SetBlocked(bat, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = bat.X, Z0 = bat.Z, Hookups = new List<Cell> { Add(c, d, -4) } });
            }
            else w.SetConduit(c);   // "cut": a loose run, cut at both ends
            Cell cur = c, dir = d;
            for (int k = 1; k <= len; k++) { cur = Add(c, d, k); w.SetConduit(cur); }
            if (turn != 0)
            {
                dir = turn > 0 ? p : new Cell(-p.X, -p.Z);
                Cell b = cur;
                for (int k = 1; k <= after; k++) { cur = Add(b, dir, k); w.SetConduit(cur); }
            }
            Cell q = Left(dir);
            if (beside == "ahead" || beside == "pocket") for (int t = -1; t <= 1; t++) Block(w, Add(Add(cur, dir, 1), q, t));
            if (beside == "side" || beside == "pocket") for (int k = -1; k <= 1; k++) Block(w, Add(Add(cur, dir, k), q, 1));
            if (beside == "pocket") for (int k = -1; k <= 1; k++) Block(w, Add(Add(cur, dir, k), q, -1));
            return w;
        }

        private static void Block(CordWorld w, Cell c) { if (!w.IsConduit(c) && w.IsWalkable(c)) w.SetBlocked(c, BlockKind.Wall); }

        /// <summary>The settings a player can turn that change a cut lead: as shipped; spurs never pruned to a hank; cords laid taut; cords laid at twice the slack.</summary>
        internal static readonly string[] Settings = { "shipped", "noprune", "taut", "loose" };

        /// <summary><paramref name="thin"/>: the suite's cut of the family, every region once (the look and the compass direction taken in turn; the
        /// two settings that only change short leads, on runs of a cell or less).</summary>
        internal static IEnumerable<(string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> Family(int seeds, string[] looks = null, bool thin = false)
        {
            int turnOf = 0;
            foreach (string setting in Settings)
                foreach (string look in looks ?? (thin ? new[] { "*" } : setting == "shipped" ? StubJoinChecks.Looks : new[] { "Industrial", "Modern" }))
                    foreach (string from in Froms)
                        foreach (Cell d in thin ? new[] { new Cell(0, 0) } : setting == "shipped" ? Dirs : new[] { Dirs[0], Dirs[1] })
                            foreach (int len in thin && (setting == "noprune" || setting == "loose") ? new[] { 0, 1 } : new[] { 0, 1, 2, 3, 4, 6 })
                                foreach (int turn in len == 0 ? new[] { 0 } : new[] { 0, 1, -1 })
                                    foreach (int after in turn == 0 ? new[] { 0 } : new[] { 1, 2, 3 })
                                        foreach (string beside in Besides)
                                            for (int seed = 0; seed < seeds; seed++)
                                            {
                                                CordWorld w;
                                                turnOf++;
                                                string lk = thin ? StubJoinChecks.Looks[turnOf % 4] : look;
                                                Cell dd = thin ? Dirs[(turnOf / 4 + turnOf) % 4] : d;
                                                try { w = Scene(from, dd, len, turn, after, beside); } catch (Exception) { continue; }
                                                var opt = new BuildOptions { Pile = lk == "Modern" ? PileArt.Strips : PileArt.Junctions, Seed = (ulong)(71 + seed * 13 + len), PlugBoot = CordBuilder.PlugBootU(lk) };
                                                if (setting == "noprune") opt.NeedlessLoops = false;
                                                if (setting == "taut") opt.Lay.SlackScale = 0;
                                                if (setting == "loose") opt.Lay.SlackScale = 2;
                                                yield return ($"{lk} {from} d{dd.X},{dd.Z} len{len} turn{turn} after{after} {beside} {setting} s{seed}", w, opt, _ => true);
                                            }
        }

        // ------------------------------------------------------------------ what the game can place beside a cut end
        // RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID (owner 2026-11-16: "WHY DID FABLE STOP IS THERE ARE STILL 21 awkward fitting poses
        // with no lay?!"). The first family put every fitting BEHIND its run. This one enumerates the placements the grid allows near a cut end:
        // the conduit's last one to three cells in every shape (straight, turning at the fitting's own cell, doubling back beside the end), and
        // at the far cell every fitting the mod draws, on every free side: a machine of 1, 2 or 3 cells a side at each offset along that side
        // (so its body may stand beside or ahead of the end), a wall or rock plate, a junction box, a power switch, a device stub, another cut
        // end; and a lone conduit cell at a machine on each side. Each in four rotations and mirrored.
        private static readonly Cell[][] Shapes =
        {
            new[] { new Cell(0, 0) },
            new[] { new Cell(0, 0), new Cell(-1, 0) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-2, 0) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-2, 0), new Cell(-3, 0) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-2, 0), new Cell(-2, 1) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1), new Cell(-1, 2) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1), new Cell(-2, 1) },
            // the conduit doubling back past the end, a cell clear of it: a fitting's body may then stand beside or ahead of the end
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1), new Cell(-1, 2), new Cell(0, 2) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1), new Cell(-1, 2), new Cell(0, 2), new Cell(1, 2) },
            new[] { new Cell(0, 0), new Cell(-1, 0), new Cell(-1, 1), new Cell(-1, 2), new Cell(0, 2), new Cell(1, 2), new Cell(2, 2), new Cell(2, 1) },
        };
        internal static readonly string[] Fits = { "battery", "lamp", "consumer", "source", "wall", "rock", "box", "boxX", "switch", "device", "cut" };

        /// <summary>One placement, or null when the grid cannot hold it (a body on the conduit, or the end no longer an end). Local cells: the cut
        /// end at (0, 0), the conduit running out of it toward +X.</summary>
        internal static CordWorld Placed(int shape, string fit, int side, int size, int offset, int rot, bool mirror)
        {
            var w = new CordWorld(44, 44);
            Cell W(Cell c)
            {
                int x = c.X, z = mirror ? -c.Z : c.Z;
                for (int k = 0; k < rot; k++) { int t = x; x = -z; z = t; }
                return new Cell(22 + x, 22 + z);
            }
            Cell[] path = Shapes[shape];
            var onPath = new HashSet<Cell>(path);
            Cell F = path[path.Length - 1], d = Dirs[side], perp = Left(d), body = Add(F, d, 1);
            var conduit = new HashSet<Cell>(path);
            var bodies = new List<Cell>();
            bool machine = fit == "battery" || fit == "lamp" || fit == "consumer" || fit == "source";
            if (fit == "cut") { if (path.Length < 2 || side != 0 || size != 1) return null; }
            else if (onPath.Contains(body)) return null;
            if (machine)
            {
                for (int i = 0; i < size; i++) for (int j = 0; j < size; j++) bodies.Add(Add(Add(F, d, 1 + i), perp, j - offset));
                if (bodies.Any(onPath.Contains)) return null;
            }
            else if (fit == "wall" || fit == "rock")
            {
                if (size != 1) return null;
                for (int t = -3; t <= 3; t++) bodies.Add(Add(body, perp, t));
                if (bodies.Any(onPath.Contains)) return null;
                for (int k = 1; k <= 4; k++) conduit.Add(Add(F, d, k));
            }
            else if (fit == "box" || fit == "boxX")
            {
                if (size != 1 || side != 0) return null;
                int want = fit == "box" ? 2 : 3, got = 0;
                foreach (Cell bd in Dirs)
                {
                    if (got >= want || onPath.Contains(Add(F, bd, 1))) continue;
                    for (int k = 1; k <= 3; k++) conduit.Add(Add(F, bd, k));
                    got++;
                }
                if (got < want) return null;
            }
            else if (fit == "switch" || fit == "device")
            {
                if (size != 1) return null;
                bodies.Add(body);
                if (fit == "device") conduit.Add(body);
            }
            // the end is still an end: its only conduit neighbour is the path's next cell
            foreach (Cell nb in Dirs)
            {
                Cell q = Add(path[0], nb, 1);
                if (conduit.Contains(q) && !(path.Length > 1 && q == path[1])) return null;
                if (bodies.Contains(q) && fit == "device") return null;
            }
            foreach (Cell c in conduit) w.SetConduit(W(c));
            if (machine)
            {
                List<Cell> wc = bodies.Select(W).ToList();
                foreach (Cell c in wc) w.SetBlocked(c, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "m", Kind = fit == "lamp" ? MachineKind.Lamp : fit == "source" ? MachineKind.Source : fit == "battery" ? MachineKind.Battery : MachineKind.Consumer,
                                                 X0 = wc.Min(c => c.X), Z0 = wc.Min(c => c.Z), W = size, H = size, Hookups = new List<Cell> { W(F) } });
            }
            else if (fit == "wall" || fit == "rock")
            {
                foreach (Cell c in bodies) w.SetBlocked(W(c), fit == "wall" ? BlockKind.Wall : BlockKind.Rock);
                Cell bat = W(Add(F, d, 5));
                w.SetBlocked(bat, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = bat.X, Z0 = bat.Z, Hookups = new List<Cell> { W(Add(F, d, 4)) } });
            }
            else if (fit == "box" || fit == "boxX")
            {
                int i = 0;
                foreach (Cell bd in Dirs)
                {
                    if (!conduit.Contains(Add(F, bd, 3)) || onPath.Contains(Add(F, bd, 1))) continue;
                    Cell m = W(Add(F, bd, 4));
                    w.SetBlocked(m, BlockKind.Device);
                    w.Machines.Add(new MachineInfo { Id = "m" + i, Kind = i == 0 ? MachineKind.Battery : MachineKind.Consumer, X0 = m.X, Z0 = m.Z, Hookups = new List<Cell> { W(Add(F, bd, 3)) } });
                    i++;
                }
            }
            else if (fit == "switch")
            {
                w.SetBlocked(W(body), BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "switch", Kind = MachineKind.Transmitter, X0 = W(body).X, Z0 = W(body).Z, Hookups = new List<Cell> { W(F) }, SidePorts = true });
            }
            else if (fit == "device") w.SetBlocked(W(body), BlockKind.Device);
            return w;
        }

        /// <summary>Every placement. <paramref name="thin"/>: the suite's cut, each placement once, its rotation, look and setting (as shipped /
        /// laid taut) taken in turn.</summary>
        internal static IEnumerable<(string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> Placements(bool thin)
        {
            int turnOf = 0;
            for (int shape = 0; shape < Shapes.Length; shape++)
                foreach (string fit in Fits)
                    for (int side = 0; side < 4; side++)
                        for (int size = 1; size <= 3; size++)
                            for (int offset = 0; offset < size; offset++)
                                foreach (bool mirror in new[] { false, true })
                                {
                                    if (size > 1 && (fit == "lamp" || fit == "source")) continue;
                                    if (Placed(shape, fit, side, size, offset, 0, mirror) == null) continue;
                                    turnOf++;
                                    foreach (int rot in thin ? new[] { turnOf % 4 } : new[] { 0, 1, 2, 3 })
                                        foreach (string setting in thin ? new[] { turnOf % 2 == 0 ? "shipped" : "taut" } : new[] { "shipped", "taut" })
                                            foreach (string look in thin ? new[] { StubJoinChecks.Looks[turnOf / 2 % 4] } : new[] { "Industrial", "Modern" })
                                            {
                                                CordWorld w = Placed(shape, fit, side, size, offset, rot, mirror);
                                                var opt = new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, Seed = (ulong)(91 + shape * 7 + side), PlugBoot = CordBuilder.PlugBootU(look) };
                                                if (setting == "taut") opt.Lay.SlackScale = 0;
                                                yield return ($"{look} placed shape{shape} {fit} side{side} size{size} off{offset} rot{rot} {(mirror ? "mirrored" : "plain")} {setting}", w, opt, _ => true);
                                            }
                                }
        }

        internal sealed class End
        {
            /// <summary>The far fitting's node, seen from the cut end: cells behind the conduit end along its own line (negative = behind), cells to
            /// its left; and whether that fitting's body lies on the end's own straight run (no cord could then be laid to it and whip).</summary>
            public double FarAlong, FarSide;
            public bool FarOnRun;
            /// <summary>How far the far fitting's body is from the end's straight run (a machine: its footprint; else its node's point), and how
            /// far its node is from the conduit end. -1: no fitting (a far cut end).</summary>
            public double FarBodyToRun = -1, FarToEnd = -1;
            public bool FarMachine;
            public string Scene, Cord, Lay, Far;
            public V2 Pos, Out;
            public List<V2> Pts;        // the strand, read toward the cut end
            public int Whip, Ties, Points;
            public double Len, Off, Arrive, Turn, Tail, MinR, StaticR;
            public bool StraightRead, Pinched, BadTail, NotStraight;
            public bool Bad => Pinched || BadTail || NotStraight;
            public List<double[]> TieArcs = new List<double[]>();   // tied loops, arcs along Pts
            public List<int[]> Blocked = new List<int[]>();      // cells near the end no cord may lie on (x, z, 1 = one of this cord's own machines)
            public string FarType;
            /// <summary>How CordLiveEnd laid it ("" when the lay was off), and the room it had for a tail.</summary>
            public string LayKind = "";
            public bool Device, Still, StillCouldWhip;
        }

        /// <summary>Every strand at every live floor cut end, read by the bars' own instruments: CordAudit's straight read (conduit end, 15 deg arrive and tip turn, on
        /// a lead of a cell or more), LaneAChecks' tail length (0.7-1.15), StubJoins.LiveEnds' bend radius over the whip's frames (0.10).</summary>
        internal static List<End> Read(string scene, CordGraph g, List<LaidPiece> ps, Func<Cell, bool> live, CordWorld w = null, ulong[] salts = null)
        {
            var o = new List<End>();
            foreach (CordNode nd in g.Nodes.Values.Where(n => n.Type == NodeType.Terminal && !n.Seam && live(n.Cell)))
                foreach (LaidPiece p in ps.Where(x => x.EndA != null))
                {
                    string me = nd.OracleName + ":" + nd.Cell.X + "," + nd.Cell.Z;
                    bool atA = p.EndA == me, atB = p.EndB == me;
                    if (!atA && !atB) continue;
                    foreach (CordStrand s in p.Strands.Where(x => !x.OverFace && x.Pts != null && x.Pts.Count > 1))
                    {
                        if ((atA && s.DiveA && !atB) || (atB && s.DiveB && !atA)) continue;
                        List<V2> q = CordAudit.EndAt(s.Pts, nd.Pos);
                        bool start = V2.Dist(s.Pts[0], nd.Pos) < V2.Dist(s.Pts[s.Pts.Count - 1], nd.Pos);
                        int cnt = start ? s.WhipA : s.WhipB;
                        V2 ov = new V2(nd.Out.X, nd.Out.Z).Norm(), e = q[q.Count - 1];
                        var one = new End { Scene = scene, Cord = p.EndA + "|" + p.EndB, Lay = s.Lay, Far = atA ? p.EndB : p.EndA, Pos = nd.Pos, Out = ov, Pts = q, Whip = cnt, Points = q.Count,
                                            Ties = s.Ties == null ? 0 : s.Ties.Count, Len = Geo.Length(q), Off = V2.Dist(e, nd.Pos) };
                        one.Arrive = CordAudit.AngDiff(CordAudit.Ang(e - CordAudit.PointBack(q, 0.1)), CordAudit.Ang(ov)) * 180 / Math.PI;
                        one.Turn = CordAudit.TipTurn(q) * 180 / Math.PI;
                        one.StraightRead = one.Len >= 1.0;
                        one.NotStraight = one.StraightRead && (one.Off > 0.08 || one.Arrive > 15 || one.Turn > 15);
                        CordLiveEnd.Result lr0 = start ? s.LiveLaidA : s.LiveLaidB;
                        if (lr0 != null)
                        {
                            one.LayKind = lr0.Kind.ToString() + (lr0.Kind == CordLiveEnd.Kind.Join || lr0.Kind == CordLiveEnd.Kind.TurnLoop ? " " + lr0.R.ToString("0.00", CultureInfo.InvariantCulture) : "");
                            one.Device = lr0.Device;
                            one.Still = lr0.Kind == CordLiveEnd.Kind.Still;
                            one.StillCouldWhip = one.Still && CordLiveEnd.WouldWhip(lr0, out List<V2> _, out int _);
                        }
                        one.MinR = 99;
                        if (cnt > 0)
                        {
                            one.Tail = Geo.Length(q.GetRange(q.Count - cnt, cnt));
                            one.BadTail = one.Tail < 0.7 || one.Tail > 1.15;
                            var lone = new LaidPiece { EndA = p.EndA, EndB = p.EndB, Strands = new List<CordStrand> { new CordStrand { Pts = q, WhipB = cnt } } };
                            foreach (ulong salt in salts ?? new ulong[] { 0 })
                            {
                                StubJoins.LiveRead lr = StubJoins.LiveEnds(new List<LaidPiece> { lone }, scene, salt: salt);
                                if (lr.Tails > 0) one.MinR = Math.Min(one.MinR, lr.MinR);
                                one.Pinched |= lr.Pinched > 0;
                            }
                        }
                        one.StaticR = StubJoins.MinRadius(q);
                        CordNode farNd = g.Nodes.Values.FirstOrDefault(n => n != nd && n.OracleName + ":" + n.Cell.X + "," + n.Cell.Z == (atA ? p.EndB : p.EndA));
                        if (farNd != null)
                        {
                            V2 rel = farNd.Pos - nd.Pos;
                            one.FarAlong = rel.X * ov.X + rel.Z * ov.Z;
                            one.FarSide = ov.X * rel.Z - ov.Z * rel.X;
                            bool cutFar = farNd.Type == NodeType.Terminal;
                            one.FarMachine = farNd.IsMachine && farNd.Machine != null;
                            if (!cutFar) { one.FarToEnd = rel.Len; one.FarBodyToRun = double.MaxValue; }
                            for (int k = 0; k <= 13 && !cutFar; k++)
                            {
                                V2 rp = nd.Pos - ov * (CordLiveEnd.Run * k / 13.0);
                                double bd = one.FarMachine ? CordShapeAudit.RectDist(farNd.Machine.X0, farNd.Machine.Z0, farNd.Machine.W, farNd.Machine.H, rp) : V2.Dist(rp, farNd.Pos);
                                one.FarBodyToRun = Math.Min(one.FarBodyToRun, bd);
                                if (one.FarMachine ? farNd.Machine.Contains(rp.Floor) : bd < CordBuilder.BoxKeepOff) one.FarOnRun = true;
                            }
                        }
                        if (s.Ties != null)
                            foreach (CordTie t in s.Ties) one.TieArcs.Add(start ? new[] { one.Len - t.S1, one.Len - t.S0 } : new[] { t.S0, t.S1 });
                        one.FarType = (atA ? g.Nodes.Values.FirstOrDefault(n => n.OracleName + ":" + n.Cell.X + "," + n.Cell.Z == p.EndB) : g.Nodes.Values.FirstOrDefault(n => n.OracleName + ":" + n.Cell.X + "," + n.Cell.Z == p.EndA))?.Type.ToString() ?? "?";
                        if (w != null)
                        {
                            List<MachineInfo> own = CordShapeAudit.OwnMachines(w, p.EndA, p.EndB);
                            Cell c0 = nd.Pos.Floor;
                            for (int dx = -5; dx <= 5; dx++)
                                for (int dz = -5; dz <= 5; dz++)
                                {
                                    var c = new Cell(c0.X + dx, c0.Z + dz);
                                    MachineInfo m = w.Machines.FirstOrDefault(x => x.Contains(c));
                                    if (m != null) one.Blocked.Add(new[] { c.X, c.Z, own.Contains(m) ? 1 : 0 });
                                    else if (!w.InBounds(c) || !w.IsWalkable(c) || w.IsFurniture(c) || w.IsDoor(c)) one.Blocked.Add(new[] { c.X, c.Z, 0 });
                                }
                        }
                        o.Add(one);
                    }
                }
            return o;
        }

        private static string F(double d) => d.ToString("0.######", CultureInfo.InvariantCulture);

        private static void Write(StreamWriter f, string source, string mode, End x)
        {
            var sb = new StringBuilder();
            sb.Append("{\"src\":\"").Append(source).Append("\",\"mode\":\"").Append(mode).Append("\",\"scene\":").Append(JsonSerializer.Serialize(x.Scene))
              .Append(",\"cord\":").Append(JsonSerializer.Serialize(x.Cord)).Append(",\"lay\":").Append(JsonSerializer.Serialize(x.Lay ?? "")).Append(",\"far\":").Append(JsonSerializer.Serialize(x.Far))
              .Append(",\"pos\":[").Append(F(x.Pos.X)).Append(',').Append(F(x.Pos.Z)).Append("],\"out\":[").Append(F(x.Out.X)).Append(',').Append(F(x.Out.Z)).Append(']')
              .Append(",\"whip\":").Append(x.Whip).Append(",\"ties\":").Append(x.Ties).Append(",\"len\":").Append(F(x.Len)).Append(",\"off\":").Append(F(x.Off))
              .Append(",\"arrive\":").Append(F(x.Arrive)).Append(",\"turn\":").Append(F(x.Turn)).Append(",\"tail\":").Append(F(x.Tail)).Append(",\"minr\":").Append(F(Math.Min(x.MinR, 99)))
              .Append(",\"staticr\":").Append(F(Math.Min(x.StaticR, 99))).Append(",\"bad\":\"").Append(x.NotStraight ? "S" : "").Append(x.Pinched ? "P" : "").Append(x.BadTail ? "T" : "").Append('"')
              .Append(",\"faralong\":").Append(F(x.FarAlong)).Append(",\"farside\":").Append(F(x.FarSide)).Append(",\"faronrun\":").Append(x.FarOnRun ? "true" : "false")
              .Append(",\"fartype\":\"").Append(x.FarType).Append("\",\"laykind\":\"").Append(x.LayKind).Append('"');
            if (mode == "raw" || source == "placed")
                sb.Append(",\"ties\":[").Append(string.Join(",", x.TieArcs.Select(t => "[" + F(t[0]) + "," + F(t[1]) + "]"))).Append(']')
                  .Append(",\"blocked\":[").Append(string.Join(",", x.Blocked.Select(b => "[" + b[0] + "," + b[1] + "," + b[2] + "]"))).Append(']')
                  .Append(",\"pts\":[").Append(string.Join(",", x.Pts.Select(q => "[" + F(q.X) + "," + F(q.Z) + "]"))).Append(']');
            sb.Append('}');
            f.WriteLine(sb.ToString());
        }

        internal static IEnumerable<(string src, string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> Worlds(int familySeeds, int fuzzSeeds, List<JsonElement> scenes, bool families = true)
        {
            if (families) foreach (var x in Family(familySeeds)) yield return ("family", x.name, x.w, x.opt, x.live);
            if (families) foreach (var x in Placements(false)) yield return ("placed", x.name, x.w, x.opt, x.live);
            if (scenes != null)
                foreach (JsonElement s in scenes)
                {
                    JsonElement sc = s.GetProperty("scene");
                    CordWorld w = Program.World(sc);
                    HashSet<Cell> lv = Program.Live(w, sc);
                    foreach (string look in StubJoinChecks.Looks)
                        yield return ("oracle", look + " " + sc.GetProperty("name").GetString(), w,
                                      new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, PlugBoot = CordBuilder.PlugBootU(look) }, lv.Contains);
                    yield return ("oracle", "default " + sc.GetProperty("name").GetString(), w, new BuildOptions(), lv.Contains);
                }
            foreach (var x in GssFuzz.CordWorlds(fuzzSeeds)) yield return ("fuzz", $"fuzz seed {x.seed} step {x.step}", x.w, x.opt, x.live);
        }

        /// <summary>--live-census OUT.jsonl [FUZZ_SEEDS [FAMILY_SEEDS]]: each world built as shipped ("now") and with the live-end lay off ("raw", the cord the lay is handed).</summary>
        public static int Run(string outPath, int fuzzSeeds, int familySeeds, List<JsonElement> scenes, bool placedOnly = false)
        {
            int worlds = 0, ends = 0, bad = 0;
            using (var f = new StreamWriter(outPath, false, new UTF8Encoding(false)))
                foreach (var x in placedOnly ? Placements(false).Select(q => (src: "placed", q.name, q.w, q.opt, q.live)) : Worlds(familySeeds, fuzzSeeds, scenes))
                {
                    worlds++;
                    foreach (string mode in new[] { "raw", "now" })
                    {
                        CordBuilder.LiveEndLayOff = mode == "raw";
                        try
                        {
                            var b = new CordBuilder();
                            List<LaidPiece> ps = b.Build(x.w, x.opt, c => x.live(c));
                            foreach (End e in Read(x.name, b.Graph, ps, x.live, x.w, new ulong[] { 0, 1, 5 }))
                            {
                                Write(f, x.src, mode, e);
                                if (mode == "now") { ends++; if (e.Bad) bad++; }
                            }
                        }
                        catch (Exception ex) { Console.WriteLine($"live census: {x.name} ({mode}) threw {ex.GetType().Name}: {ex.Message}"); }
                        finally { CordBuilder.LiveEndLayOff = false; }
                    }
                    if (worlds % 500 == 0) Console.WriteLine($"live census: {worlds} worlds, {ends} live ends, {bad} failing a bar");
                }
            Console.WriteLine($"live census: {worlds} worlds, {ends} live ends, {bad} failing a bar -> {outPath}");
            return 0;
        }
    }
}
