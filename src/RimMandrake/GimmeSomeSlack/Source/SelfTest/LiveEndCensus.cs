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

        internal sealed class End
        {
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
              .Append(",\"fartype\":\"").Append(x.FarType).Append("\",\"laykind\":\"").Append(x.LayKind).Append('"');
            if (mode == "raw")
                sb.Append(",\"ties\":[").Append(string.Join(",", x.TieArcs.Select(t => "[" + F(t[0]) + "," + F(t[1]) + "]"))).Append(']')
                  .Append(",\"blocked\":[").Append(string.Join(",", x.Blocked.Select(b => "[" + b[0] + "," + b[1] + "," + b[2] + "]"))).Append(']')
                  .Append(",\"pts\":[").Append(string.Join(",", x.Pts.Select(q => "[" + F(q.X) + "," + F(q.Z) + "]"))).Append(']');
            sb.Append('}');
            f.WriteLine(sb.ToString());
        }

        internal static IEnumerable<(string src, string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> Worlds(int familySeeds, int fuzzSeeds, List<JsonElement> scenes)
        {
            foreach (var x in Family(familySeeds)) yield return ("family", x.name, x.w, x.opt, x.live);
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
        public static int Run(string outPath, int fuzzSeeds, int familySeeds, List<JsonElement> scenes)
        {
            int worlds = 0, ends = 0, bad = 0;
            using (var f = new StreamWriter(outPath, false, new UTF8Encoding(false)))
                foreach (var x in Worlds(familySeeds, fuzzSeeds, scenes))
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
