// Phase 1b lane A checks (rope settle, stiff-hose parameters, graph/builder additions, live-end
// schedule). Kept out of Program.cs on purpose: the oracle-parity block stays as it was, and these
// checks are the "clearly separated block" phase-2 doc §5.1 asks each lane for.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LaneAChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, msg);

        public static void Run(List<JsonElement> scenes)
        {
            foreach (JsonElement s in scenes)
            {
                JsonElement sc = s.GetProperty("scene");
                SettleChecks(sc.GetProperty("name").GetString(), sc);
            }
            HoseChecks();
            PerfChecks();
            StubMergeChecks();
            LongRunHeapChecks();
            StripLiveChecks(scenes);
            WhipTailChecks(scenes);
            MotionChecks();
        }

        // ------------------------------------------------------------------ L3: B3 whip tails split, B7 lifted tails
        private static void WhipTailChecks(List<JsonElement> scenes)
        {
            int liveTails = 0, deadTails = 0, badLen = 0, lifted = 0, fray = 0;
            foreach (JsonElement s in scenes)
            {
                JsonElement sc = s.GetProperty("scene");
                CordWorld w = Program.World(sc);
                HashSet<Cell> live = Program.Live(w, sc);
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(w, new BuildOptions(), live.Contains);
                foreach (LaidPiece p in ps)
                {
                    foreach (CordStrand st in p.Strands)
                    {
                        for (int side = 0; side < 2; side++)
                        {
                            int cnt = side == 0 ? st.WhipA : st.WhipB;
                            if (cnt <= 0) continue;
                            List<V2> tail = side == 0 ? st.Pts.GetRange(0, cnt) : st.Pts.GetRange(st.Pts.Count - cnt, cnt);
                            double len = Geo.Length(tail);
                            if (len < 0.7 || len > 1.15) badLen++;
                        }
                        if (st.Lifted)
                        {
                            lifted++;
                        }
                    }
                    fray += p.Decals.Count(d => d.Kind == DecalKind.FrayLive && d.OnWhip);
                }
                foreach (CordNode nd in b.Graph.Nodes.Values.Where(n => n.Type == NodeType.Terminal))
                {
                    int tails = ps.SelectMany(p => p.Strands).Count(st => (st.WhipA > 0 && V2.Dist(st.Pts[0], nd.Pos) < 0.45) || (st.WhipB > 0 && V2.Dist(st.Pts[st.Pts.Count - 1], nd.Pos) < 0.45));
                    if (live.Contains(nd.Cell)) liveTails += tails; else deadTails += tails;
                }
            }
            Check(liveTails > 0, $"whip: no live floor terminal strand has a whip tail ({liveTails})");
            Check(deadTails == 0, $"whip: {deadTails} DEAD terminal strands carry a whip tail (dead ends lie still)");
            Check(badLen == 0, $"whip: {badLen} whip tails outside 0.7-1.15 cell");
            Check(fray > 0, "whip: no live fray decal rides the whip (OnWhip)");
            // the wall terminal's hanging wire was its only lifted strand; owner 2026-11-16 ("both a hanging out sparking end as well as the wire
            // plugging into the same point on the wall. That's not ok") removed it, so none is expected now (the sway maths stays checked below)
            Check(lifted == 0, $"lifted: {lifted} lifted (wall-hanging) strands (none hang out of a wall since 2026-11-16)");
            Console.WriteLine($"  whip: {liveTails} live tails, {deadTails} dead, {fray} riding fray decals; lifted strands {lifted}");
        }

        private static void MotionChecks()
        {
            var tail = new List<V2>();
            for (int i = 0; i < 9; i++) tail.Add(new V2(5 + i * 0.05, 5));
            List<V2> a = CordMotion.Whip(tail, 1.0, 42, 0.12), a2 = CordMotion.Whip(tail, 1.0, 42, 0.12), b = CordMotion.Whip(tail, 1.37, 42, 0.12);
            double maxD = 0, diff = 0;
            for (int i = 0; i < tail.Count; i++) { maxD = Math.Max(maxD, V2.Dist(a[i], tail[i])); diff += V2.Dist(a[i], b[i]); }
            Check(V2.Dist(a[0], tail[0]) < 1e-12, "whip: the joint point moved");
            Check(maxD <= 0.12 * 1.9 + 1e-9, $"whip: displacement {maxD:0.000} beyond 1.9 x amp");
            Check(diff > 1e-3, "whip: pose does not change with time");
            Check(a.Zip(a2, (x, y) => V2.Dist(x, y)).Max() == 0, "whip: pose not deterministic");
            int snaps = 0;
            for (int k = 0; k < 400; k++)
            {
                double t = k * 0.05;
                double d1 = V2.Dist(CordMotion.Whip(tail, t, 7, 0.12)[8], CordMotion.Whip(tail, t + 0.05, 7, 0.12)[8]);
                if (d1 > 0.06) snaps++;
            }
            Check(snaps >= 3, $"whip: only {snaps} sharp snaps in 20 s (want the 0.6-2 s random kicks)");
            // owner 2026-11-16: wind moves no ground cord; the cords' motion kernel takes no wind and has no sway or ripple
            var windy = typeof(CordMotion).GetMethods(System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic)
                .Where(m => m.DeclaringType == typeof(CordMotion) && (m.GetParameters().Any(q => q.Name == "wind") || m.Name.Contains("Sway") || m.Name.Contains("Ripple")))
                .Select(m => m.Name).Distinct().ToList();
            Check(windy.Count == 0, "wind: CordMotion still moves a ground cord with the wind (" + string.Join(", ", windy) + ")");
            Check(typeof(CordMotion).GetMethods(System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic).Any(m => m.Name == "WhipInto"),
                  "can-fail: the reflection scan sees CordMotion's internal methods (WhipInto)");
            Console.WriteLine($"  motion: whip max {maxD:0.000}, snaps {snaps}/20 s");
        }

        // ------------------------------------------------------------------ L2: B2 stub merge (§8.7.3)
        /// <summary>A floor run along z=5 beside a wall row z=6 that carries its own buried conduit:
        /// without the merge every floor cell grows a stub into the wall (a comb).</summary>
        internal static CordWorld WallHugger(bool throughWall)
        {
            var w = new CordWorld(24, 14);
            for (int x = 2; x <= 14; x++) w.SetConduit(new Cell(x, 5));
            for (int x = 1; x <= 16; x++) w.SetBlocked(new Cell(x, 6), BlockKind.Wall);
            for (int x = 4; x <= 12; x++) w.SetConduit(new Cell(x, 6));
            if (throughWall)
            {
                // the run also goes straight through the wall at x=13 into the room north of it
                w.SetConduit(new Cell(13, 6));
                for (int z = 7; z <= 10; z++) w.SetConduit(new Cell(13, z));
                w.SetBlocked(new Cell(13, 11), BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Consumer, X0 = 13, Z0 = 11, Hookups = new List<Cell> { new Cell(13, 10) } });
            }
            w.SetBlocked(new Cell(1, 5), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 1, Z0 = 5, Hookups = new List<Cell> { new Cell(2, 5) } });
            return w;
        }

        private static void StubMergeChecks()
        {
            CordGraph g = CordGraph.Reduce(WallHugger(false));
            int stubs = g.Nodes.Values.Count(n => n.IsStub);
            Check(stubs == 1, $"stub merge: wall-hugging run shows {stubs} stubs (a comb), want 1");
            int junctions = g.Nodes.Values.Count(n => n.Type == NodeType.Junction);
            Check(junctions <= 1, $"stub merge: wall-hugging run has {junctions} junctions (one per merged stub left behind)");
            CordGraph g2 = CordGraph.Reduce(WallHugger(true));
            int stubs2 = g2.Nodes.Values.Count(n => n.IsStub);
            // the comb merges to one, and the through-wall pass keeps its own two openings
            Check(stubs2 >= 2 && stubs2 <= 3, $"stub merge: comb + through-wall shows {stubs2} stubs, want 2-3 (the wall pass must keep both faces)");
            bool northStub = g2.Nodes.Values.Any(n => n.IsStub && n.Cell == new Cell(13, 7));
            Check(northStub, "stub merge: the through-wall run lost its north-face stub (merged across the wall)");
            Console.WriteLine($"  stub merge: comb -> {stubs} stub(s), {junctions} junction(s); with a through-wall pass -> {stubs2} stubs");
        }

        // ------------------------------------------------------------------ L2: B2 long-run heaps (§8.7.6)
        private static void LongRunHeapChecks()
        {
            var w = new CordWorld(80, 12);
            for (int x = 3; x <= 66; x++) w.SetConduit(new Cell(x, 5));
            w.SetBlocked(new Cell(2, 5), BlockKind.Device);
            w.SetBlocked(new Cell(67, 5), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "a", Kind = MachineKind.Battery, X0 = 2, Z0 = 5, Hookups = new List<Cell> { new Cell(3, 5) } });
            w.Machines.Add(new MachineInfo { Id = "b", Kind = MachineKind.Consumer, X0 = 67, Z0 = 5, Hookups = new List<Cell> { new Cell(66, 5) } });
            List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions(), c => true);
            LaidPiece lp = ps.Single(p => p.EndA != null);
            int nearA = 0, nearB = 0;
            foreach (CordStrand s in lp.Strands.Where(x => x.Settle != null))
            {
                nearA += s.Settle.HeapsAt.Count(at => at <= 6.5);
                nearB += s.Settle.HeapsFromEnd.Count(at => at <= 6.5);
            }
            Check(nearA >= 1 && nearB >= 1, $"long run: a {lp.PathLen:0}-cell cord carries heaps near its ends A {nearA} B {nearB} (want >= 1 each)");
            // a short run never gets the end heaps
            var w2 = new CordWorld(30, 12);
            for (int x = 3; x <= 20; x++) w2.SetConduit(new Cell(x, 5));
            w2.SetBlocked(new Cell(2, 5), BlockKind.Device); w2.SetBlocked(new Cell(21, 5), BlockKind.Device);
            w2.Machines.Add(new MachineInfo { Id = "a", Kind = MachineKind.Battery, X0 = 2, Z0 = 5, Hookups = new List<Cell> { new Cell(3, 5) } });
            w2.Machines.Add(new MachineInfo { Id = "b", Kind = MachineKind.Consumer, X0 = 21, Z0 = 5, Hookups = new List<Cell> { new Cell(20, 5) } });
            LaidPiece sp = new CordBuilder().Build(w2, new BuildOptions(), c => true).Single(p => p.EndA != null);
            int endHeaps = sp.Strands.Where(x => x.Settle != null).Sum(x => x.Settle.EndHeaps);
            Check(endHeaps == 0, $"long run: an {sp.PathLen:0}-cell cord got {endHeaps} long-run end heaps");
            Console.WriteLine($"  long run: {lp.PathLen:0} cells, end heaps near A {nearA}, near B {nearB}; short run end heaps {endHeaps}");
        }

        // ------------------------------------------------------------------ L2: B6 tangle LEDs keyed to live
        private static void StripLiveChecks(List<JsonElement> scenes)
        {
            foreach (string nm in new[] { "tangle", "tangle_off" })
            {
                JsonElement sc = scenes.First(x => x.GetProperty("scene").GetProperty("name").GetString() == nm).GetProperty("scene");
                CordWorld w = Program.World(sc);
                HashSet<Cell> live = Program.Live(w, sc);
                List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions { Pile = PileArt.Strips }, live.Contains);   // LEDs: the modern strip look
                int lit = ps.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PowerStrip));
                int dark = ps.Sum(p => p.Decals.Count(d => d.Kind == DecalKind.PowerStripDark));
                bool wantLit = nm == "tangle";
                Check(wantLit ? (lit > 0 && dark == 0) : (dark > 0 && lit == 0), $"strips: {nm}: lit {lit} dark {dark}");
                LaidPiece tp = ps.FirstOrDefault(p => p.Key.StartsWith("tangle:"));
                Check(tp != null && tp.LiveKeys.Count > 0, $"strips: {nm}: the tangle piece registers no live key (a battery flip would not re-print it)");
                Console.WriteLine($"  strips: {nm}: lit {lit}, dark {dark}");
            }
        }

        // ------------------------------------------------------------------ B1 rope settle
        private static void SettleChecks(string name, JsonElement sc)
        {
            CordWorld w = Program.World(sc);
            HashSet<Cell> live = Program.Live(w, sc);
            List<LaidPiece> ps = new CordBuilder().Build(w, new BuildOptions(), live.Contains);
            bool anyLong = ps.Any(p => p.EndA != null && p.PathLen > 1.2 && !p.Unroutable);
            List<SettleStats> st = ps.SelectMany(p => p.Strands).Where(x => x.Settle != null).Select(x => x.Settle).ToList();
            if (!anyLong) return;
            Check(st.Count > 0, $"{name}: settle: no strand was rope-settled");
            if (st.Count == 0) return;
            double stretch = st.Max(x => x.MaxStretch);
            double lenDev = st.Max(x => Math.Abs(x.SettledLen / Math.Max(1e-9, x.RestLen) - 1));
            SettleStats worst = st.OrderByDescending(x => x.MaxStretch).First();
            Check(stretch < 0.04, $"{name}: settle: max segment stretch {stretch:0.000} >= 4% (seg {worst.WorstSeg}/{worst.Points}: {worst.WorstNote})");   // one 0.05-cell segment at 3.4% is 0.002 of a cell: the bar is for a stretched rope, and every re-lay draws a new worst
            Check(lenDev <= 0.05, $"{name}: settle: settled length off its budget by {lenDev:P1} (> 5%)");
            Check(st.All(x => x.Iters >= 20 && x.Iters <= 70), $"{name}: settle: iterations outside 20..70 ({string.Join(",", st.Select(x => x.Iters).Distinct())})");
            Check(st.All(x => x.Work <= Math.Max(new LayParams().SettleBudget, 20L * x.Points) + 32L * x.Points), $"{name}: settle: a strand exceeded the point-iteration budget");
            Console.WriteLine($"  {name}: settle: {st.Count} strands, max stretch {stretch:0.0000} (max compression {st.Max(x => x.MaxCompress):0.000}), max length dev {lenDev:P2}, iters {st.Min(x => x.Iters)}-{st.Max(x => x.Iters)}, points max {st.Max(x => x.Points)}");
        }

        // ------------------------------------------------------------------ stiff hose parameter set (§3.5)
        /// <summary>A 40x24 yard: a battery west, a pump-ish consumer north-east, the conduit run going
        /// east then north round a walled corner block.</summary>
        internal static CordWorld HoseYard()
        {
            var w = new CordWorld(40, 24);
            for (int x = 3; x <= 30; x++) w.SetConduit(new Cell(x, 5));
            for (int z = 6; z <= 18; z++) w.SetConduit(new Cell(30, z));
            for (int x = 25; x <= 28; x++) for (int z = 7; z <= 10; z++) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
            w.SetBlocked(new Cell(2, 5), BlockKind.Device);
            w.SetBlocked(new Cell(30, 19), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 2, Z0 = 5, Hookups = new List<Cell> { new Cell(3, 5) } });
            w.Machines.Add(new MachineInfo { Id = "pump", Kind = MachineKind.Consumer, X0 = 30, Z0 = 19, Hookups = new List<Cell> { new Cell(30, 18) } });
            return w;
        }

        internal static int SelfIntersections(List<V2> p)
        {
            int n = 0;
            for (int i = 0; i + 1 < p.Count; i++)
                for (int j = i + 2; j + 1 < p.Count; j++)
                    if (SegX(p[i], p[i + 1], p[j], p[j + 1])) n++;
            return n;
        }

        private static bool SegX(V2 a, V2 b, V2 c, V2 d)
        {
            double Cr(V2 o, V2 p, V2 q) => (p.X - o.X) * (q.Z - o.Z) - (p.Z - o.Z) * (q.X - o.X);
            double d1 = Cr(c, d, a), d2 = Cr(c, d, b), d3 = Cr(a, b, c), d4 = Cr(a, b, d);
            return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
        }

        private static void HoseChecks()
        {
            var opt = new BuildOptions { Tangles = false, NeedlessLoops = false, Lay = LayParams.Hose() };
            List<LaidPiece> hose = new CordBuilder().Build(HoseYard(), opt, c => true);
            var wireOpt = new BuildOptions { Tangles = false, NeedlessLoops = false };
            List<LaidPiece> wire = new CordBuilder().Build(HoseYard(), wireOpt, c => true);
            LaidPiece hp = hose.Single(p => p.EndA != null);
            LaidPiece wp = wire.Single(p => p.EndA != null);
            Check(hp.Strands.Count == 1, $"hose: {hp.Strands.Count} strands, want 1");
            CordStrand hs = hp.Strands[0];
            Check(hs.Settle != null, "hose: the strand was not settled");
            double minR = hs.Settle?.MinBendR ?? 0;
            Check(minR >= 1.2 * 0.95, $"hose: min bend radius on the settled free points {minR:0.00} < 1.2");
            int hx = SelfIntersections(hs.Pts), wx = wp.Strands.Sum(s => SelfIntersections(s.Pts));
            Check(hx == 0, $"hose: {hx} self-intersections (a hose never loops)");
            // sanity probe: the same counter finds the wire's loops on the same yard
            Check(wx > 0, $"hose: sanity probe failed, the wire laid on the same yard shows {wx} self-intersections (counter cannot see loops)");
            double extra = Geo.Length(hs.Pts) - hp.PathLen;
            Check(extra >= 0.5 && extra <= 6.5, $"hose: extra length {extra:0.00} outside the hose budget clamp(0.15-0.30 x path, 1, 6)");
            double wireMinR = wp.Strands.Where(s => s.Settle != null).Select(s => s.Settle.MinBendR).DefaultIfEmpty(9).Min();
            Check(wireMinR < minR, $"hose: hose min bend {minR:0.00} not stiffer than the wire's {wireMinR:0.00}");
            Console.WriteLine($"  hose yard: path {hp.PathLen:0.0}, hose laid {Geo.Length(hs.Pts):0.0} (+{extra:0.00}), min bend R {minR:0.00} (wire {wireMinR:0.00}), self-x hose {hx} wire {wx}, points {hs.Pts.Count}");
        }

        // ------------------------------------------------------------------ bounded cost (perf canary, §4.4)
        /// <summary>A ~1000-conduit-cell field (density board D-1000 shape; 1027 cells): a ~45x46 plot
        /// (x 3..47, z 3..48) holding a lattice (every 3rd row/column) in its south-west 25x25 and long
        /// runs elsewhere, plus a wall block and some consumers. Deterministic.</summary>
        internal static CordWorld DensityField(out HashSet<Cell> live)
        {
            var w = new CordWorld(52, 52);
            var set = new HashSet<Cell>();
            for (int x = 3; x < 28; x++) for (int z = 3; z < 28; z++) if (x % 3 == 0 || z % 3 == 0) set.Add(new Cell(x, z));
            for (int z = 30; z < 49; z += 2) for (int x = 3; x < 47; x++) set.Add(new Cell(x, z));
            for (int z = 3; z < 49; z++) { set.Add(new Cell(47, z)); }
            for (int x = 30; x < 47; x += 3) for (int z = 3; z < 28; z++) set.Add(new Cell(x, z));
            for (int x = 27; x < 47; x++) set.Add(new Cell(x, 28));
            set.Add(new Cell(27, 29)); set.Add(new Cell(28, 29));
            for (int x = 27; x <= 28; x++) set.Add(new Cell(x, 30));
            foreach (Cell c in set) w.SetConduit(c);
            for (int x = 34; x <= 38; x++) for (int z = 12; z <= 16; z++) if (!set.Contains(new Cell(x, z))) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
            w.SetBlocked(new Cell(2, 3), BlockKind.Device);
            w.Machines.Add(new MachineInfo { Id = "gen", Kind = MachineKind.Source, X0 = 2, Z0 = 3, Hookups = new List<Cell> { new Cell(3, 3) } });
            for (int k = 0; k < 8; k++)
            {
                var m = new Cell(48, 4 + k * 6);
                w.SetBlocked(m, BlockKind.Device);
                w.Machines.Add(new MachineInfo { Id = "c" + k, Kind = MachineKind.Consumer, X0 = m.X, Z0 = m.Z, Hookups = new List<Cell> { new Cell(47, m.Z) } });
            }
            live = new HashSet<Cell>(set);
            return w;
        }

        private static void PerfChecks()
        {
            CordWorld w = DensityField(out HashSet<Cell> live);
            int cells = w.ConduitCells().Count();
            var b = new CordBuilder();
            var sw = Stopwatch.StartNew();
            List<LaidPiece> ps = b.Build(w, new BuildOptions(), live.Contains);
            double cold = sw.Elapsed.TotalMilliseconds;
            sw.Restart();
            b.Build(DensityField(out _), new BuildOptions(), live.Contains);
            double warm = sw.Elapsed.TotalMilliseconds;
            int pts = ps.Sum(p => p.Strands.Sum(s => s.Pts.Count));
            long work = ps.SelectMany(p => p.Strands).Where(s => s.Settle != null).Sum(s => s.Settle.Work);
            Check(b.LastPlanned == 0, $"perf: warm rebuild of the 1000-cell field planned {b.LastPlanned} edges");
            Check(cold < 4000, $"perf: cold build of the {cells}-cell field took {cold:0} ms (> 4 s)");
            int bad = ps.SelectMany(p => p.Strands).Where(s => !s.OverFace).Sum(s => { List<V2> t = Program.TrimUnderArt(w, s.Pts); return t.Skip(1).Take(Math.Max(0, t.Count - 2)).Count(q => !w.IsWalkable(q.Floor)); });
            Check(bad == 0, $"perf: {bad} laid vertices in unwalkable cells on the density field");
            // a refusal names the cords: their ends, the lay that drew them and the first such vertex
            if (bad > 0)
                foreach (LaidPiece p in ps)
                    foreach (CordStrand s in p.Strands.Where(s => !s.OverFace))
                    {
                        List<V2> t = Program.TrimUnderArt(w, s.Pts);
                        List<V2> off = t.Skip(1).Take(Math.Max(0, t.Count - 2)).Where(q => !w.IsWalkable(q.Floor)).ToList();
                        if (off.Count > 0) Console.WriteLine($"    {p.EndA}|{p.EndB} lay {s.Lay}: {off.Count} vertices, first ({off[0].X:0.00},{off[0].Z:0.00})");
                    }
            Console.WriteLine($"  perf: {cells} conduit cells -> {b.Graph.Nodes.Count} nodes, {b.Graph.CordEdges().Count()} cord edges, {ps.Sum(p => p.Strands.Count)} strands, {pts} laid points, settle work {work}; cold {cold:0} ms, warm {warm:0} ms");
        }
    }
}
