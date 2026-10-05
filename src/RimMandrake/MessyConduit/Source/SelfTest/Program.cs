// Messy Conduit offline SelfTest: runs the PRODUCTION core (../Core/*.cs, compiled in directly)
// against the Python oracle's scenes (oracle_scenes.json, written by
// src/RimMandrake/Utils/mockups/messy_conduit/export_oracle.py) and compares the graph-level
// answers, then asserts the geometric properties phase 1a promises.
//
//   python3 src/RimMandrake/Utils/selftest_messyconduit.py           (builds on Windows, runs this)
//   ... --probe   flips one expected value per scene first: every scene must then FAIL (sanity probe)
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.SelfTest
{
    internal static class Program
    {
        private static int checks, fails;
        internal static string dumpDir;

        internal static void Dump(string name, CordWorld w, List<LaidPiece> pieces)
        {
            var o = new
            {
                name, w = w.Width, h = w.Height,
                strands = pieces.SelectMany(p => p.Strands).Select(s => new { over = s.OverFace, fell = s.FellBack, pts = s.Pts.Select(q => new[] { Math.Round(q.X, 3), Math.Round(q.Z, 3) }) }),
                decals = pieces.SelectMany(p => p.Decals).Select(d => new { kind = d.Kind.ToString(), x = d.Pos.X, z = d.Pos.Z, a = d.Angle, s = d.Scale }),
                ends = pieces.SelectMany(p => p.Ends).Select(e => new { x = e.Tip.X, z = e.Tip.Z, cell = new[] { e.NetCell.X, e.NetCell.Z }, wall = e.Wall })
            };
            File.WriteAllText(Path.Combine(dumpDir, name + ".laid.json"), JsonSerializer.Serialize(o));
        }

        internal static void Check(bool ok, string msg)
        {
            checks++;
            if (!ok) { fails++; Console.WriteLine("FAIL " + msg); }
        }

        private static int Main(string[] args)
        {
            bool probe = args.Contains("--probe");
            int di = Array.IndexOf(args, "--dump");
            if (di >= 0) { dumpDir = args[di + 1]; Directory.CreateDirectory(dumpDir); }
            string path = args.Where((a, i) => !a.StartsWith("--") && (i == 0 || args[i - 1] != "--dump")).FirstOrDefault() ?? Path.Combine(AppContext.BaseDirectory, "oracle_scenes.json");
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(path));
            var scenes = doc.RootElement.GetProperty("scenes").EnumerateArray().ToList();
            Console.WriteLine($"oracle: {path} ({scenes.Count} scenes)");
            int probeFails = 0;
            foreach (JsonElement s in scenes)
            {
                JsonElement sc = s.GetProperty("scene"), ex = s.GetProperty("expect");
                string name = sc.GetProperty("name").GetString();
                int before = fails;
                CompareScene(name, sc, ex, probe);
                if (probe && fails > before) probeFails++;
                if (!probe) GeometryChecks(name, sc);
            }
            if (probe)
            {
                Console.WriteLine($"PROBE: {probeFails}/{scenes.Count} scenes detected the planted mismatch");
                return probeFails == scenes.Count ? 0 : 1;
            }
            UnrelatedEditCheck(scenes.First(x => x.GetProperty("scene").GetProperty("name").GetString() == "nodal").GetProperty("scene"));
            LaneAChecks.Run(scenes);       // phase 1b lane A (rope settle, graph, live ends): LaneAChecks.cs
            AerialSelfTest.Run(Check);     // lane B (L5 aerial lines): AerialSelfTest.cs + ../Aerial/AerialMath.cs
            HoseSelfTest.Run(Check);       // lane D (L6 flexible hoses): HoseSelfTest.cs + ../Hose/HoseMath.cs
            ReviewRound1Checks.Run();      // owner human review round 1 (2026-10-04): ReviewRound1Checks.cs
            ReviewRound3Checks.Run();      // owner human review round 3 (2026-10-04): ReviewRound3Checks.cs
            ReviewRound4Checks.Run();      // owner human review round 4 (2026-10-04): ReviewRound4Checks.cs
            ReviewRound5Checks.Run();      // owner human review round 5 (2026-10-04): ReviewRound5Checks.cs
            StyleStage1Checks.Run();       // per-build style stage 1 (2026-10-04): StyleStage1Checks.cs + ../Aerial/AerialStyles.cs
            StyleStage2Checks.Run();       // per-build style stage 2, conduit runs (2026-10-04): StyleStage2Checks.cs + ../Aerial/ConduitStyles.cs
            StyleStage3Checks.Run();       // per-build style stage 3, hose reels (2026-10-04): StyleStage3Checks.cs + ../Hose/HoseStyles.cs
            DeterminismChecks.Run(Check, Path.Combine(AppContext.BaseDirectory, "matrix_det_scenes.json"));   // lane F: fresh == incremental
            Console.WriteLine($"{checks - fails}/{checks} checks passed");
            return fails == 0 ? 0 : 1;
        }

        // ------------------------------------------------------------------ scene -> world
        private static Cell C(JsonElement a) => new Cell(a[0].GetInt32(), a[1].GetInt32());

        internal static CordWorld World(JsonElement sc, Action<CordWorld> extra = null)
        {
            var w = new CordWorld(sc.GetProperty("w").GetInt32(), sc.GetProperty("h").GetInt32());
            foreach (JsonElement c in sc.GetProperty("conduit").EnumerateArray()) w.SetConduit(C(c));
            foreach (JsonElement b in sc.GetProperty("blocked").EnumerateArray())
            {
                string k = b[2].GetString();
                w.SetBlocked(C(b), k == "rock" ? BlockKind.Rock : k == "water" ? BlockKind.Water : k == "device" ? BlockKind.Device : BlockKind.Wall);
            }
            foreach (JsonElement d in sc.GetProperty("doors").EnumerateArray()) w.SetDoor(C(d));
            foreach (JsonElement t in sc.GetProperty("trees").EnumerateArray()) w.SetExtraCost(C(t), 1.5f);
            foreach (JsonElement m in sc.GetProperty("machines").EnumerateArray())
            {
                string k = m.GetProperty("kind").GetString();
                w.Machines.Add(new MachineInfo
                {
                    Id = m.GetProperty("id").GetString(),
                    Kind = k == "source" ? MachineKind.Source : k == "battery" ? MachineKind.Battery : k == "lamp" ? MachineKind.Lamp : MachineKind.Consumer,
                    X0 = m.GetProperty("x").GetInt32(), Z0 = m.GetProperty("y").GetInt32(),
                    W = m.GetProperty("w").GetInt32(), H = m.GetProperty("h").GetInt32(),
                    Hookups = new List<Cell> { C(m.GetProperty("hookup")) }
                });
            }
            extra?.Invoke(w);
            return w;
        }

        /// <summary>The oracle's live set: flood over conduit from every source's hookup cell.</summary>
        internal static HashSet<Cell> Live(CordWorld w, JsonElement sc)
        {
            var live = new HashSet<Cell>();
            var stack = new Stack<Cell>();
            foreach (JsonElement s in sc.GetProperty("sources").EnumerateArray()) if (w.IsConduit(C(s))) stack.Push(C(s));
            while (stack.Count > 0)
            {
                Cell c = stack.Pop();
                if (!live.Add(c)) continue;
                foreach (Cell d in Cell.Dirs4) if (w.IsConduit(c + d) && !live.Contains(c + d)) stack.Push(c + d);
            }
            return live;
        }

        private static Dictionary<Cell, int> Components(CordWorld w)
        {
            var comp = new Dictionary<Cell, int>();
            int k = 0;
            foreach (Cell c in w.ConduitCells().OrderBy(x => x))
            {
                if (comp.ContainsKey(c)) continue;
                var st = new Stack<Cell>();
                st.Push(c);
                comp[c] = k;
                while (st.Count > 0)
                {
                    Cell q = st.Pop();
                    foreach (Cell d in Cell.Dirs4)
                        if (w.IsConduit(q + d) && !comp.ContainsKey(q + d)) { comp[q + d] = k; st.Push(q + d); }
                }
                k++;
            }
            return comp;
        }

        private static string Cs(Cell c) => c.X + "," + c.Z;

        // ------------------------------------------------------------------ graph vs oracle
        private static void CompareScene(string name, JsonElement sc, JsonElement ex, bool probe)
        {
            CordWorld w = World(sc);
            HashSet<Cell> live = Live(w, sc);
            CordGraph g = CordGraph.Reduce(w);
            var types = g.Nodes.Values.Select(n => n.OracleName).OrderBy(x => x, StringComparer.Ordinal).ToList();
            var want = ex.GetProperty("types").EnumerateArray().Select(x => x.GetString()).OrderBy(x => x, StringComparer.Ordinal).ToList();
            if (probe) want[0] = "planted_mismatch";
            Check(types.SequenceEqual(want), $"{name}: node census\n   C# {string.Join(" ", types)}\n   py {string.Join(" ", want)}");
            int cord = g.CordEdges().Count(), hidden = g.Edges.Count(e => e.Hidden);
            Check(cord == ex.GetProperty("cord_edges").GetInt32() && hidden == ex.GetProperty("hidden_edges").GetInt32(),
                  $"{name}: edges C# {cord} cord/{hidden} hidden, py {ex.GetProperty("cord_edges").GetInt32()}/{ex.GetProperty("hidden_edges").GetInt32()}");
            // endpoint attachment: every cord edge joins the same (type, cell) pair as the oracle's
            var ends = g.CordEdges().Select(e =>
            {
                var a = g.Nodes[e.A].OracleName + ":" + Cs(g.Nodes[e.A].Cell);
                var b = g.Nodes[e.B].OracleName + ":" + Cs(g.Nodes[e.B].Cell);
                return string.CompareOrdinal(a, b) <= 0 ? a + "|" + b : b + "|" + a;
            }).OrderBy(x => x, StringComparer.Ordinal).ToList();
            var wantEnds = ex.GetProperty("cord_ends").EnumerateArray().Select(pair =>
            {
                var a = pair[0][0].GetString() + ":" + pair[0][1].GetInt32() + "," + pair[0][2].GetInt32();
                var b = pair[1][0].GetString() + ":" + pair[1][1].GetInt32() + "," + pair[1][2].GetInt32();
                return string.CompareOrdinal(a, b) <= 0 ? a + "|" + b : b + "|" + a;
            }).OrderBy(x => x, StringComparer.Ordinal).ToList();
            var missing = wantEnds.Except(ends).ToList();
            var extra = ends.Except(wantEnds).ToList();
            Check(missing.Count == 0 && extra.Count == 0 && ends.Count == wantEnds.Count,
                  $"{name}: cord endpoints differ; missing [{string.Join(" ", missing)}] extra [{string.Join(" ", extra)}]");
            int knots = g.CordEdges().Sum(e => e.Knots.Count);
            Check(knots == ex.GetProperty("knots").GetInt32() && g.SpurKnots.Count == ex.GetProperty("spurs").GetInt32(),
                  $"{name}: knots {knots} spurs {g.SpurKnots.Count}, py {ex.GetProperty("knots").GetInt32()}/{ex.GetProperty("spurs").GetInt32()}");
            string Term(IEnumerable<CordNode> ns) => string.Join(" ", ns.Select(n => Cs(n.Cell) + (live.Contains(n.Cell) ? "L" : "D")).OrderBy(x => x, StringComparer.Ordinal));
            string Want(string key) => string.Join(" ", ex.GetProperty(key).EnumerateArray()
                .Select(t => t[0].GetInt32() + "," + t[1].GetInt32() + (t[2].GetBoolean() ? "L" : "D")).OrderBy(x => x, StringComparer.Ordinal));
            Check(Term(g.Nodes.Values.Where(n => n.Type == NodeType.Terminal)) == Want("terminals"),
                  $"{name}: terminals C# [{Term(g.Nodes.Values.Where(n => n.Type == NodeType.Terminal))}] py [{Want("terminals")}]");
            Check(Term(g.Nodes.Values.Where(n => n.WallTerminal)) == Want("wall_terminals"),
                  $"{name}: wall terminals C# [{Term(g.Nodes.Values.Where(n => n.WallTerminal))}] py [{Want("wall_terminals")}]");
            // design §8.2.2 key property: cords only between nodes of the same conduit component
            var comp = Components(w);
            int cross = g.CordEdges().Count(e => comp[g.CellOf(e.A)] != comp[g.CellOf(e.B)]);
            Check(cross == 0, $"{name}: {cross} cord edges join different conduit components");
        }

        // ------------------------------------------------------------------ laid geometry
        /// <summary>Owner round 2 (2026-10-04): a cord into a machine runs on UNDER its art to the footprint centroid
        /// (CordBuilder.IntoArt), so its END run lies inside the machine's own (unwalkable) footprint by design. The floor
        /// and attachment checks judge the strand with that end run trimmed off; a vertex inside a footprint anywhere else
        /// in the strand still fails them.</summary>
        internal static List<V2> TrimUnderArt(CordWorld w, List<V2> pts)
        {
            // round 4: a cord into a wall/rock face runs on PastFaceDepth under the wall by design (CordBuilder.PastFace)
            bool PastFace(V2 p)
            {
                if (w.IsWalkable(p.Floor)) return false;
                double fx = p.X - Math.Floor(p.X), fz = p.Z - Math.Floor(p.Z);
                return Math.Min(Math.Min(fx, 1 - fx), Math.Min(fz, 1 - fz)) <= CordBuilder.PastFaceDepth + 0.005;
            }
            bool In(V2 p) => PastFace(p) || w.Machines.Any(m => p.X >= m.X0 && p.X < m.X0 + m.W && p.Z >= m.Z0 && p.Z < m.Z0 + m.H);
            int a = 0, b = pts.Count - 1;
            while (a < b && In(pts[a])) a++;
            while (b > a && In(pts[b])) b--;
            return pts.GetRange(a, b - a + 1);
        }

        private static void GeometryChecks(string name, JsonElement sc)
        {
            CordWorld w = World(sc);
            HashSet<Cell> live = Live(w, sc);
            var b1 = new CordBuilder();
            List<LaidPiece> p1 = b1.Build(w, new BuildOptions(), live.Contains);
            int strands = p1.Sum(p => p.Strands.Count);
            int fell = p1.Sum(p => p.Strands.Count(x => x.FellBack));
            Check(fell * 5 <= strands, $"{name}: {fell}/{strands} strands fell back to the bare centreline");
            if (dumpDir != null) Dump(name, w, p1);
            Check(strands > 0, $"{name}: no strands laid");
            int bad = 0, total = 0;
            foreach (LaidPiece p in p1)
                foreach (CordStrand s in p.Strands.Where(x => !x.OverFace))
                {
                    List<V2> q = TrimUnderArt(w, s.Pts);
                    for (int i = 1; i < q.Count - 1; i++)
                    {
                        total++;
                        if (!w.IsWalkable(q[i].Floor)) bad++;
                    }
                }
            Check(bad == 0, $"{name}: {bad}/{total} laid vertices in unwalkable cells");
            // endpoint attachment of the laid cord: first/last point = the planned endpoints
            CordGraph g = b1.Graph;
            int detached = 0;
            foreach (LaidPiece p in p1.Where(x => x.EndA != null))
                foreach (CordStrand s in p.Strands.Where(x => !x.OverFace))
                {
                    List<V2> q = TrimUnderArt(w, s.Pts);
                    V2 a = q[0], z = q[q.Count - 1];
                    // round 5: a junction end sits ArmTuck x JunctionScale out on its arm; a pile end plugs into a port INSIDE the pile
                    bool At(CordEdge e, bool atA, V2 pt)
                    {
                        CordNode nd = g.Nodes[atA ? e.A : e.B];
                        if (nd.Type == NodeType.Tangle && nd.Cells != null) return nd.Cells.Any(c => V2.Dist(c.Centre, pt) < 0.75);
                        return V2.Dist(atA ? e.PA : e.PB, pt) < 0.45 + CordBuilder.ArmTuck * (CordBuilder.JunctionScale - 1);
                    }
                    bool okA = g.CordEdges().Any(e => (At(e, true, a) && At(e, false, z)) || (At(e, false, a) && At(e, true, z)));
                    if (!okA) detached++;
                }
            Check(detached == 0, $"{name}: {detached} laid strands do not start and end at their edge's two nodes");
            // round 2: every cord end inside a machine's footprint sits exactly on that machine's centroid
            int mEnds = 0, centred = 0;
            foreach (CordStrand s in p1.SelectMany(p => p.Strands))
                foreach (V2 e in new[] { s.Pts[0], s.Pts[s.Pts.Count - 1] })
                    foreach (MachineInfo m in w.Machines.Where(m => e.X >= m.X0 && e.X <= m.X0 + m.W && e.Z >= m.Z0 && e.Z <= m.Z0 + m.H))
                    {
                        mEnds++;
                        if (V2.Dist(e, CordBuilder.Centroid(m)) < 1e-6) centred++;
                    }
            Check(mEnds == centred, $"{name}: {centred}/{mEnds} cord ends into a machine end on its centroid");
            Console.WriteLine($"  {name}: {centred}/{mEnds} machine cord ends on the centroid");
            ArtFitChecks(name, w, g, p1, live);
            // determinism: a fresh builder gives bit-identical geometry
            List<LaidPiece> p2 = new CordBuilder().Build(World(sc), new BuildOptions(), live.Contains);
            Check(p1.Count == p2.Count && p1.Zip(p2, (a, b) => a.Key == b.Key && a.GeometryHash() == b.GeometryHash()).All(x => x),
                  $"{name}: laying is not deterministic");
            // cache: rebuilding the unchanged map plans nothing
            b1.Build(World(sc), new BuildOptions(), live.Contains);
            Check(b1.LastPlanned == 0 && b1.LastReused == g.CordEdges().Count(), $"{name}: unchanged rebuild planned {b1.LastPlanned}, reused {b1.LastReused}");
            // slack is real: cords are longer than their path (owner: "everything is a too-long extension cord")
            var ratios = p1.Where(p => p.EndA != null && p.PathLen > 1.2 && !p.Unroutable).Select(p => p.LaidRatio).ToList();
            if (ratios.Count > 0)
            {
                ratios.Sort();
                double med = ratios[ratios.Count / 2];
                Check(med >= 1.2, $"{name}: median laid/path ratio {med:0.00} < 1.2 (not loopy)");
                Console.WriteLine($"  {name}: {g.Nodes.Count} nodes, {g.CordEdges().Count()} cord edges, {strands} strands ({fell} fell back), laid/path median {med:0.00}, unroutable {p1.Count(p => p.Unroutable)}");
            }
        }

        // ------------------------------------------------------------------ the real art fits the cords (polish pass 2026-10-02)
        private static void ArtFitChecks(string name, CordWorld w, CordGraph g, List<LaidPiece> ps, HashSet<Cell> live)
        {
            ArtFitResult r = CordAudit.ArtFit(g, ps, live.Contains);
            string msg = string.Join("; ", r.Messages.Take(4));
            Check(r.JunctionFaults == 0, $"{name}: junction art does not fit its cords ({r.JunctionFaults} faults over {r.Junctions} junctions): {msg}");
            Check(r.PlugFaults == 0, $"{name}: plugs do not enter their machines ({r.PlugFaults}/{r.PlugEnds}): {msg}");
            Check(r.StubFaults == 0, $"{name}: {r.StubFaults}/{r.Stubs} wall/rock stub decals not on the face along the cord: {msg}");
            Check(r.DeadFaults == 0, $"{name}: {r.DeadFaults}/{r.DeadEnds} dead ends not visibly limp (tip must fall >=0.22 cell off the conduit line and curl >=50deg)");
            Check(r.LiveFaults == 0, $"{name}: {r.LiveFaults}/{r.LiveEnds} live ends not straight out of the conduit end: {msg}");
            Console.WriteLine($"  {name}: art fit: {r.Junctions} junctions ({r.JunctionFaults} faults), {r.PlugEnds} plug ends ({r.PlugFaults}), {r.Stubs} stubs ({r.StubFaults}); " +
                              $"dead tip off-line [{string.Join(" ", r.DeadOffLine.Select(x => x.ToString("0.00")))}] live arrival deg [{string.Join(" ", r.LiveArrivalDeg.Select(x => x.ToString("0")))}]");
        }

        // ------------------------------------------------------------------ local invalidation (§8.2.5/§8.2.7)
        private static void UnrelatedEditCheck(JsonElement sc)
        {
            CordWorld w0 = World(sc);
            HashSet<Cell> live = Live(w0, sc);
            var b = new CordBuilder();
            List<LaidPiece> before = b.Build(w0, new BuildOptions(), live.Contains);
            // a new conduit run + heater in the far north-east corner, outdoors
            CordWorld w1 = World(sc, w =>
            {
                for (int x = 22; x <= 25; x++) w.SetConduit(new Cell(x, 0));
                w.Machines.Add(new MachineInfo { Id = "far", Kind = MachineKind.Consumer, X0 = 21, Z0 = 0, W = 1, H = 1, Hookups = new List<Cell> { new Cell(22, 0) } });
                w.SetBlocked(new Cell(21, 0), BlockKind.Device);
            });
            List<LaidPiece> after = b.Build(w1, new BuildOptions(), live.Contains);
            var lampBefore = before.Where(p => p.EndA != null && (p.EndA.StartsWith("lamp") || p.EndB.StartsWith("lamp"))).ToList();
            Check(lampBefore.Count > 0, "unrelated edit: the lamp cord exists");
            bool same = lampBefore.All(p => after.Any(q => q.Key == p.Key && q.GeometryHash() == p.GeometryHash()));
            Check(same, "unrelated edit: a far-away conduit run reshuffled the lamp cord");
            Check(b.LastReused >= before.Count(p => p.EndA != null) - 1,
                  $"unrelated edit re-planned more than the touched edge (planned {b.LastPlanned}, reused {b.LastReused})");
            Check(after.Count(p => p.EndA != null && (p.EndA.Contains("22,0") || p.EndB.Contains("22,0"))) >= 1, "unrelated edit: the new run got its cord");
        }
    }
}
