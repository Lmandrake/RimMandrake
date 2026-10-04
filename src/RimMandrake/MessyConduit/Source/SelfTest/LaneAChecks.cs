// Phase 1b lane A checks (rope settle, stiff-hose parameters, graph/builder additions, live-end
// schedule). Kept out of Program.cs on purpose: the oracle-parity block stays as it was, and these
// checks are the "clearly separated block" phase-2 doc §5.1 asks each lane for.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text.Json;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.SelfTest
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
            int liveTails = 0, deadTails = 0, badLen = 0, lifted = 0, badW = 0, fray = 0;
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
                        foreach (int cnt in new[] { st.WhipA, st.WhipB })
                        {
                            if (cnt <= 0) continue;
                            List<V2> tail = cnt == st.WhipA ? st.Pts.GetRange(0, cnt) : st.Pts.GetRange(st.Pts.Count - cnt, cnt);
                            double len = Geo.Length(tail);
                            if (len < 0.3 || len > 0.5) badLen++;
                        }
                        if (st.Lifted)
                        {
                            lifted++;
                            if (st.SwayW == null || st.SwayW.Length != st.Pts.Count || st.SwayW[0] != 0 || st.SwayW[st.SwayW.Length - 1] < 0.9) badW++;
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
            Check(badLen == 0, $"whip: {badLen} whip tails outside 0.3-0.5 cell");
            Check(fray > 0, "whip: no live fray decal rides the whip (OnWhip)");
            Check(lifted > 0 && badW == 0, $"sway: {lifted} lifted (wall-hanging) strands, {badW} with bad sway weights (0 at the hole, ~1 at the tip)");
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
            // downed-wire schedule
            var sch = new DownedWireSchedule(99, 0);
            var seen = new HashSet<DripState>();
            double gmin = 9, gmax = 0, now = 0;
            int sparks = 0;
            for (int k = 0; k < 200; k++)
            {
                now = sch.NextAt;
                seen.Add(sch.Advance(now));
                gmin = Math.Min(gmin, sch.LastGap); gmax = Math.Max(gmax, sch.LastGap);
                sparks += sch.Sparks;
            }
            Check(seen.Count == 4, $"drip: only {seen.Count}/4 states in 200 draws");
            Check(gmin >= 0.3 - 1e-9 && gmax <= 2.5 + 1e-9, $"drip: gaps {gmin:0.00}-{gmax:0.00} outside 0.3-2.5 s");
            double mean = now / 200;
            Check(mean > 0.6 && mean < 1.3, $"drip: mean gap {mean:0.00} s, want ~0.9");
            var s1 = new DownedWireSchedule(5, 0); var s2 = new DownedWireSchedule(5, 0);
            bool same = true;
            for (int k = 0; k < 50; k++) { s1.Advance(k); s2.Advance(k); same &= s1.State == s2.State && s1.LastGap == s2.LastGap; }
            Check(same, "drip: schedule not deterministic by seed");
            var flash = new DownedWireSchedule(1, 0);
            double peak = 0;
            for (int k = 0; k < 200 && peak < 1.9; k++) { flash.Advance(k); if (flash.State == DripState.Flash) peak = flash.Glow(k + 0.01); }
            Check(peak >= 1.9 && flash.Glow(flash.StateAt + 2.0) < 0.35, "drip: FLASH does not pop to 2x and fade to an ember");
            // sway
            var span = new List<V2>(); var wt = new List<double>();
            for (int i = 0; i < 16; i++) { span.Add(new V2(3, 3 - i * 0.025)); wt.Add(Math.Pow(i / 15.0, 1.3)); }
            List<V2> sw0 = CordMotion.Sway(span, wt, 3.0, 11, 0.12, 0), swA = CordMotion.Sway(span, wt, 3.0, 11, 0.12, 1), swB = CordMotion.Sway(span, wt, 3.5, 11, 0.12, 1);
            Check(sw0.Zip(span, (x, y) => V2.Dist(x, y)).Max() == 0, "sway: moves with no wind");
            Check(V2.Dist(swA[0], span[0]) == 0, "sway: the pinned point moved");
            Check(swA.Zip(swB, (x, y) => V2.Dist(x, y)).Max() > 1e-3, "sway: pose does not change with time");
            Check(swA.Zip(span, (x, y) => V2.Dist(x, y)).Max() <= 0.12 * 1.3 + 1e-9, "sway: displacement beyond 1.3 x amp at wind 1");
            // shader-path sway weights (B7 option 1): vertex alpha 0 at the pin, rising to the tip, all 0 under a roof
            byte[] al = CordMotion.ShaderSwayAlpha(wt, false, 0.35), alR = CordMotion.ShaderSwayAlpha(wt, true, 0.35);
            Check(al.Length == wt.Count && al[0] == 0 && al[al.Length - 1] == 89 && al.Max() == al[al.Length - 1],
                  $"shader sway: alpha pin {al[0]} tip {al[al.Length - 1]} (want 0 .. 89 = 255 x 0.35, max at the tip)");
            Check(alR.All(b => b == 0), "shader sway: a roofed lifted piece carries non-zero sway alpha");
            Check(CordMotion.ShaderSwayAlpha(wt, false, 9).Max() == 255, "shader sway: alpha not clamped to 255");
            // optional floor ripple: ends pinned, no wind no motion, bounded, moves with time, deterministic
            var floor = new List<V2>();
            for (int i = 0; i < 25; i++) floor.Add(new V2(2 + i * 0.25, 4 + 0.3 * Math.Sin(i * 0.4)));
            List<V2> r0 = CordMotion.Ripple(floor, 3.0, 7, CordMotion.RippleAmp, 0), rA = CordMotion.Ripple(floor, 3.0, 7, CordMotion.RippleAmp, 1),
                     rA2 = CordMotion.Ripple(floor, 3.0, 7, CordMotion.RippleAmp, 1), rB = CordMotion.Ripple(floor, 3.6, 7, CordMotion.RippleAmp, 1),
                     rW = CordMotion.Ripple(floor, 3.0, 7, CordMotion.RippleAmp, 9);
            double rMax = rA.Zip(floor, (x, y) => V2.Dist(x, y)).Max();
            Check(r0.Zip(floor, (x, y) => V2.Dist(x, y)).Max() == 0, "ripple: moves with no wind");
            Check(V2.Dist(rA[0], floor[0]) == 0 && V2.Dist(rA[24], floor[24]) == 0, "ripple: an end moved (ends are pinned)");
            Check(rMax > 1e-3 && rMax <= CordMotion.RippleAmp + 1e-9, $"ripple: displacement {rMax:0.0000} at wind 1 (want >0, <= amp)");
            Check(rW.Zip(floor, (x, y) => V2.Dist(x, y)).Max() <= 1.5 * CordMotion.RippleAmp + 1e-9, "ripple: wind not clamped to 1.5");
            Check(rA.Zip(rB, (x, y) => V2.Dist(x, y)).Max() > 1e-3, "ripple: pose does not change with time");
            Check(rA.Zip(rA2, (x, y) => V2.Dist(x, y)).Max() == 0, "ripple: pose not deterministic");
            Console.WriteLine($"  shader sway alpha tip {al[al.Length - 1]}; ripple max {rMax:0.0000} cells at wind 1");
            Console.WriteLine($"  motion: whip max {maxD:0.000}, snaps {snaps}/20 s; drip states {seen.Count}, gaps {gmin:0.00}-{gmax:0.00} mean {mean:0.00}, sparks {sparks}/200");
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
            Check(stretch < 0.03, $"{name}: settle: max segment stretch {stretch:0.000} >= 3% (seg {worst.WorstSeg}/{worst.Points}: {worst.WorstNote})");
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
        /// <summary>A 1000-conduit-cell field (density board D-1000 shape): a 34x34 plot holding a
        /// lattice (every 3rd row/column) in its south-west 18x18 and long runs elsewhere, plus a wall
        /// block and some consumers. Deterministic.</summary>
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
            Console.WriteLine($"  perf: {cells} conduit cells -> {b.Graph.Nodes.Count} nodes, {b.Graph.CordEdges().Count()} cord edges, {ps.Sum(p => p.Strands.Count)} strands, {pts} laid points, settle work {work}; cold {cold:0} ms, warm {warm:0} ms");
        }
    }
}
