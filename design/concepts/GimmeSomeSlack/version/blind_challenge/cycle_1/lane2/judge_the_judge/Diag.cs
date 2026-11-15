// gss_four diagnostic sweep: the lane-1 scene maker and oracles over many seeds, failures bucketed by lay and end kinds.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;
using RimMandrake.GimmeSomeSlack.Core;

static partial class BlindLane1
{
    static string K(string e) => e == null ? "pile" : e.Split(':')[0];
    static void Inc(Dictionary<string, int> d, string k) => d[k] = d.GetValueOrDefault(k) + 1;
    static string Top(Dictionary<string, int> d, int n = 12) => string.Join(", ", d.OrderByDescending(kv => kv.Value).Take(n).Select(kv => kv.Key + " " + kv.Value));

    static int DiagMain(string mode, int N, int b0)
    {
#if !BASE
        if (mode == "reptrace")
        {
            // two equal 4-cell runs side by side, build seed N: the gap between the two cords after each LayEdge stage
            int L = 4; var w = new CordWorld(16, 40);
            for (int r = 0; r < 2; r++)
            {
                int z = 4 + r * 4;
                for (int x = 5; x < 5 + L; x++) w.SetConduit(new Cell(x, z));
                var g = new MachineInfo { Id = "g" + r, DefName = "G", Kind = MachineKind.Source, X0 = 4, Z0 = z }; g.Hookups.Add(new Cell(5, z));
                var l = new MachineInfo { Id = "l" + r, DefName = "L", Kind = MachineKind.Consumer, X0 = 5 + L, Z0 = z }; l.Hookups.Add(new Cell(4 + L, z));
                w.Machines.Add(g); w.Machines.Add(l); w.SetBlocked(new Cell(4, z), BlockKind.Device); w.SetBlocked(new Cell(5 + L, z), BlockKind.Device);
            }
            var st = new Dictionary<string, List<List<V2>>>(); var order = new List<string>();
            CordBuilder.StepTrace = (s, ea, eb, P) => { if (!st.ContainsKey(s)) { st[s] = new List<List<V2>>(); order.Add(s); } st[s].Add(new List<V2>(P)); };
            var ps = Build(w, new BuildOptions { Seed = (ulong)N }).Where(p => p.EndA != null && p.Strands.Count > 0 && HasPts(p.Strands[0])).ToList();
            foreach (var s in order) if (st[s].Count >= 2) Console.WriteLine($"  {s}: gap {Gap(Frame(st[s][0]), Frame(st[s][1])):0.###} len {Geo.Length(st[s][0]):0.00}/{Geo.Length(st[s][1]):0.00}");
            Console.WriteLine($"  FINAL: gap {Gap(Frame(ps[0].Strands[0].Pts), Frame(ps[1].Strands[0].Pts)):0.###} lays {ps[0].Strands[0].Lay}/{ps[1].Strands[0].Lay}");
            return 0;
        }
        if (mode.StartsWith("trace"))
        {
            // trace<runs>_<maxLen>_<walls01>_<endA>: unforced count after each LayEdge stage for pieces whose EndA or EndB starts with endA
            var a = mode.Substring(5).Split('_');
            var sc = MakeScene(N, int.Parse(a[0]), int.Parse(a[1]), a[2] == "1");
            CordSlacken.Why = x => { if (a[3] == "NULL" ? x.StartsWith("|") : x.Contains(a[3])) Console.WriteLine("  slwhy: " + x.Substring(0, Math.Min(500, x.Length))); };
            CordBuilder.HopWhy = x => { if (x.Contains(a[3])) Console.WriteLine("  hopwhy: " + x.Substring(0, Math.Min(400, x.Length))); };
            CordBuilder.StepTrace = (st, ea, eb, P) => { if ((ea ?? "").StartsWith(a[3]) || (eb ?? "").StartsWith(a[3])) Console.WriteLine($"  {ea}|{eb} {st}: unforced {CordShapeAudit.Unforced(sc.W, ea, eb, P)} n {P.Count} len {Geo.Length(P):0.00} start {P[0]} heading {(P.Count > 3 ? Math.Atan2(P[3].Z - P[0].Z, P[3].X - P[0].X) * 180 / Math.PI : 0):0}"); if (Environment.GetEnvironmentVariable("PTS") == "1") Console.WriteLine("    pts " + string.Join(" ", Geo.Resample(P, 0.1).Select(q => $"{q.X:0.00},{q.Z:0.00}"))); };
            foreach (var p in Build(sc.W))
                foreach (var s in p.Strands.Where(HasPts))
                    if ((p.EndA ?? "").StartsWith(a[3]) || (p.EndB ?? "").StartsWith(a[3]))
                    {
                        Console.WriteLine($"FINAL {p.EndA}|{p.EndB} {s.Lay}: unforced {CordShapeAudit.Unforced(sc.W, p.EndA, p.EndB, s.Pts)} whip {s.WhipA}/{s.WhipB}");
                        if (Environment.GetEnvironmentVariable("PTS") == "1") { var r = Geo.Resample(s.Pts, 0.1); Console.WriteLine("  pts " + string.Join(" ", r.Take(45).Select(q => $"{q.X:0.00},{q.Z:0.00}"))); }
                    }
            return 0;
        }
#endif
        if (mode.StartsWith("one"))
        {
            // one<runs>_<maxLen>_<walls01>: build seed N, print slacken's why and every long edge's stray
            var a = mode.Substring(3).Split('_');
            CordSlacken.Why = x => Console.WriteLine("  why: " + x);
            var sc = MakeScene(N, int.Parse(a[0]), int.Parse(a[1]), a[2] == "1");
            foreach (var p in Build(sc.W))
            {
                if (p.EndA == null || p.Strands.Count == 0 || !HasPts(p.Strands[0])) continue;
                var chain = OwnChain(p.Key);
                foreach (var s in p.Strands.Where(HasPts))
                    Console.WriteLine($"{p.EndA}->{p.EndB} {s.Lay} chain {chain.Count} far {s.Pts.Max(q => DistToPolyline(q, chain)):0.##} ratio {CordSlacken.Ratio(s.Pts):0.##} whip {s.WhipA}/{s.WhipB} n {s.Pts.Count} key {(Environment.GetEnvironmentVariable("FULLKEY") == "1" ? p.Key : p.Key.Substring(0, Math.Min(160, p.Key.Length)))}");
            }
            return 0;
        }
        if (mode == "live")
        {
            // the SelfTest's RebuildPerDigChecks.LiveScene: a 37-cell conduit lattice every 6 cells, a lamp on every run's middle
            const int x0 = 56, z0 = 54, size = 37, step = 6, m = 3;
            CordWorld Mk()
            {
                var w = new CordWorld(325, 325);
                for (int z = z0; z < z0 + size; z++) for (int x = x0; x < x0 + size; x++) if ((z - z0) % step == 0 || (x - x0) % step == 0) w.SetConduit(new Cell(x, z));
                var lamps = new SortedSet<(int, int)>();
                for (int k = 0; k < size; k += step) for (int i = 0; i < size; i++) if (i % step == m) { lamps.Add((x0 + i, z0 + k)); lamps.Add((x0 + k, z0 + i)); }
                foreach (var (x, z) in lamps) w.Machines.Add(new MachineInfo { Id = "c" + (1000 + x * 400 + z), Kind = MachineKind.Lamp, X0 = x, Z0 = z, Hookups = new List<Cell> { new Cell(x, z) } });
                return w;
            }
            long best = long.MaxValue; List<LaidPiece> ps = null;
            for (int i = 0; i < Math.Max(1, N); i++) { var sw = System.Diagnostics.Stopwatch.StartNew(); ps = Build(Mk(), null, c => false); best = Math.Min(best, sw.ElapsedMilliseconds); }
            var lays = new Dictionary<string, int>(); foreach (var p in ps) foreach (var s in p.Strands) Inc(lays, s.Lay ?? "?");
            Console.WriteLine($"LIVE fresh Build best {best} ms, {ps.Count} pieces; lays {Top(lays, 14)}");
            return 0;
        }
        if (mode == "room")
        {
            // CordShapeChecks.Room: eight 25-cell runs, both ends cut (terminals), all live; kinks by lay over seeds 1,2,3,7,19
            var by = new Dictionary<string, int>(); int strands = 0, kinks = 0;
            foreach (ulong seed in new ulong[] { 1, 2, 3, 7, 19 })
            {
                var w = new CordWorld(40, 44);
                for (int k = 0; k < 8; k++) for (int x = 6; x <= 30; x++) w.SetConduit(new Cell(x, 6 + 4 * k));
                foreach (var p in Build(w, new BuildOptions { Seed = seed }, c => true)) foreach (var s in p.Strands)
                { strands++; int fk = CordShape.Kinks(s.Pts).Count; kinks += fk; if (fk > 0) Inc(by, s.Lay + " x" + fk); }
            }
            Console.WriteLine($"ROOM strands {strands} folds {kinks} :: {Top(by, 12)}");
            return 0;
        }
        if (mode == "bendpts")
        {
            // the judge's bend scenes (seeds as "bends"), every strand with an unforced bend: its bends, ends, lay and points (0.05 cell) as one JSON line
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 6000 + t + (walls ? 500 : 0) + (t >= 40 ? 100000 : 0), 6, 14, walls);
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
                {
                    if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) continue;
                    var bs = CordShapeAudit.Bends(s.Pts, s.Ties).Select(b => (b, why: CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b))).ToList();
                    if (!bs.Any(x => x.why == "unforced")) continue;
                    var inv = System.Globalization.CultureInfo.InvariantCulture;
                    string F(double d) => d.ToString("0.###", inv);
                    Console.WriteLine("{\"scene\":\"" + sc.Desc + "\",\"a\":\"" + p.EndA + "\",\"b\":\"" + p.EndB + "\",\"lay\":\"" + s.Lay + "\",\"whip\":[" + s.WhipA + "," + s.WhipB + "],\"bends\":["
                        + string.Join(",", bs.Select(x => "{\"why\":\"" + x.why + "\",\"s\":" + F(x.b.S) + ",\"turn\":" + F(x.b.Turn) + ",\"arc\":" + F(x.b.Arc) + ",\"round\":" + F(x.b.Round) + ",\"roundR\":" + F(x.b.RoundR) + ",\"fromEnd\":" + F(x.b.FromEnd) + "}"))
                        + "],\"pts\":[" + string.Join(",", s.Pts.Select(q => "[" + F(q.X) + "," + F(q.Z) + "]")) + "],\"blocked\":["
                        + string.Join(",", Enumerable.Range(0, sc.W.Width * sc.W.Height).Select(i => new Cell(i % sc.W.Width, i / sc.W.Width)).Where(c => !sc.W.IsWalkable(c)).Select(c => "[" + c.X + "," + c.Z + "]")) + "]}");
                }
            }
            return 0;
        }
        if (mode == "whyat")
        {
            // every bend the bar's instrument reads within 0.8 cell of AT=x,z on scene seed N (runs RUNS, default 6), open floor: what it calls each
            var at = Environment.GetEnvironmentVariable("AT").Split(','); var p0 = new V2(double.Parse(at[0], System.Globalization.CultureInfo.InvariantCulture), double.Parse(at[1], System.Globalization.CultureInfo.InvariantCulture));
            var sc = MakeScene(N, int.Parse(Environment.GetEnvironmentVariable("RUNS") ?? "6"), 14, b0 == 1);
            foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
            {
                if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) continue;
                foreach (var b in CordShapeAudit.Bends(s.Pts, s.Ties))
                    if (V2.Dist(b.Apex, p0) < 0.8 || s.Pts.Any(q => V2.Dist(q, p0) < 0.05))
                        Console.WriteLine($"{p.EndA}|{p.EndB} {s.Lay} apex {b.Apex} S {b.S:0.00} turn {b.Turn:0} arc {b.Arc:0.00} round {b.Round:0} R {b.RoundR:0.00} -> {CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b)}");
            }
            return 0;
        }
#if !BASE
        if (mode == "stagetime")
        {
            // where the lay time goes: ms between successive StepTrace stages (the stage named is the one that just ended), over the time mode's scenes
            var acc = new Dictionary<string, double>(); var swt = System.Diagnostics.Stopwatch.StartNew(); double last = 0; string prev = null;
            CordBuilder.StepTrace = (st, ea, eb, P) => { double now = swt.Elapsed.TotalMilliseconds; string k = (prev ?? "start") + "->" + st; acc[k] = acc.GetValueOrDefault(k) + now - last; last = now; prev = st; };
            var all = System.Diagnostics.Stopwatch.StartNew();
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true }) { prev = null; last = swt.Elapsed.TotalMilliseconds; Build(MakeScene(b0 + 6000 + t + (walls ? 500 : 0), 6, 14, walls).W); }
            Console.WriteLine($"STAGETIME total {all.ElapsedMilliseconds} ms over {2 * N} scenes; " + string.Join(", ", acc.OrderByDescending(kv => kv.Value).Take(14).Select(kv => $"{kv.Key} {kv.Value:0}")));
            return 0;
        }
#endif
        if (mode == "sharprow")
        {
            // L1_CORD_SHARP_TURN's own windows over its 40 scenes (all failures, not the first): what the bar's instrument calls the bend nearest each one
            var by = new Dictionary<string, int>(); var ex = new List<string>();
            for (int t = 0; t < N; t++)
            {
                var sc = MakeScene(6000 + t, 6, 14, false);
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands.Where(HasPts))
                {
                    var r = Geo.Resample(s.Pts, 0.05); if (r.Count < 25) continue;
                    double[] cum = Geo.CumLen(r);
                    var bends = CordShapeAudit.Bends(s.Pts, s.Ties);
                    var loops = bends.Where(b => b.IsLoop).Select(b => (b.S, half: Math.Max(b.Arc, 0.5 * b.Round * Math.PI / 180 * b.RoundR))).ToList();
                    for (int i = 1; i + 1 < r.Count; i++)
                    {
                        int j = i; double turn = 0;
                        while (j + 1 < r.Count && cum[j] - cum[i] < 1.0) { var u = (r[j] - r[j - 1]).Norm(); var v = (r[j + 1] - r[j]).Norm(); turn += Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z); j++; }
                        if (Math.Abs(turn) <= Math.PI / 2 + 0.05) continue;
                        double mid = cum[(i + j) / 2];
                        if (loops.Any(lp => Math.Abs(mid - lp.S) <= lp.half)) { i = j; continue; }
                        var at = r[(i + j) / 2];
                        bool forced = Near(sc.W, at, 1.0) || V2.Dist(at, r[0]) < 0.75 || V2.Dist(at, r[r.Count - 1]) < 0.75 || (s.Ties != null && s.Ties.Count > 0) || s.Lifted;
                        if (forced) { i = j; continue; }
                        var nb = bends.OrderBy(b => Math.Abs(b.S - mid)).FirstOrDefault();
                        string why = bends.Count == 0 ? "no bend" : CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, nb) + (Math.Abs(nb.S - mid) > 1.0 ? " (far)" : "");
                        Inc(by, why);
                        if (ex.Count < 8) ex.Add($"seed {6000 + t} {p.EndA}|{p.EndB} {s.Lay} {Math.Abs(turn) * 180 / Math.PI:0} deg at {at} mid {mid:0.00}/{cum[cum.Length - 1]:0.00} -> {why} (apex S {nb.S:0.00} fromEnd {nb.FromEnd:0.00})");
                        i = j;
                    }
                }
            }
            Console.WriteLine("SHARPROW " + Top(by)); foreach (var x in ex) Console.WriteLine("  " + x);
            return 0;
        }
        if (mode == "time")
        {
            var sw = System.Diagnostics.Stopwatch.StartNew(); int pieces = 0;
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true }) pieces += Build(MakeScene(b0 + 6000 + t + (walls ? 500 : 0), 6, 14, walls).W).Count;
            Console.WriteLine($"TIME {N * 2} scenes {sw.ElapsedMilliseconds} ms, {pieces} pieces");
            return 0;
        }
        if (mode == "slack" || mode == "all")
        {
            int n = 0, under = 0; var why = new Dictionary<string, int>(); double worst = 9; var ex = new List<string>();
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 3000 + t + (walls ? 50000 : 0), 7, 16, walls);
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands.Where(HasPts))
                {
                    if (p.EndA == null || p.EndB == null || s.OverFace || s.DiveA || s.DiveB) continue;
                    double ch = Chord(s.Pts); if (ch < 2) continue; n++;
                    double r = Geo.Length(s.Pts) / ch; worst = Math.Min(worst, r);
                    if (r < 1.4) { under++; string k = s.Lay + (s.WhipA > 0 || s.WhipB > 0 ? "+whip" : "") + " " + K(p.EndA) + "-" + K(p.EndB); Inc(why, k); if (ex.Count < 6) ex.Add($"{sc.Desc} {p.EndA}->{p.EndB} {r:0.###} ch {ch:0.##} {s.Lay}"); }
                }
            }
            Console.WriteLine($"SLACK strands {n} under {under} worst {worst:0.###} :: {Top(why)}"); foreach (var x in ex) Console.WriteLine("  " + x);
        }
        if (mode == "exc" || mode == "all")
        {
            int e = 0, miss = 0; var mw = new Dictionary<string, int>(); double low = 9; var ex = new List<string>();
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 4000 + t + (walls ? 50000 : 0), 5, 18, walls);
                foreach (var p in Build(sc.W))
                {
                    if (p.EndA == null || p.EndB == null || p.Strands.Count == 0 || !HasPts(p.Strands[0])) continue;
                    var chain = OwnChain(p.Key);
                    if (chain.Count < 6) continue; e++;
                    var s = p.Strands[0];
                    double f = s.Pts.Max(q => DistToPolyline(q, chain)); low = Math.Min(low, f);
                    if (f < 1.0) { miss++; Inc(mw, s.Lay + " " + K(p.EndA) + "-" + K(p.EndB) + (walls ? " W" : "")); if (ex.Count < 8) ex.Add($"{sc.Desc} {p.EndA}->{p.EndB} far {f:0.##} chordExc {CordSlacken.Excursion(s.Pts):0.##} ratio {CordSlacken.Ratio(s.Pts):0.##} {s.Lay} chain {chain.Count}"); }
                }
            }
            Console.WriteLine($"EXC edges {e} miss {miss} low {low:0.##} :: {Top(mw)}"); foreach (var x in ex) Console.WriteLine("  " + x);
        }
        if (mode == "bends" || mode == "all")
        {
            var rw = new Dictionary<string, int>();
            if (Environment.GetEnvironmentVariable("RO") == "1") CordBuilder.HopWhy = x => { if (x.StartsWith("RO ")) Inc(rw, System.Text.RegularExpressions.Regex.Replace(x, @"[0-9.]+", "#")); };
            var tally = new CordShapeAudit.BendTally(); var by = new Dictionary<string, int>(); var ex = new List<string>(); int strands = 0, bad = 0, kinks = 0;
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 6000 + t + (walls ? 500 : 0) + (t >= 40 ? 100000 : 0), 6, 14, walls);
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
                {
                    if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) continue; strands++; kinks += CordShape.Kinks(s.Pts).Count;
                    bool any = false;
                    foreach (var b in CordShapeAudit.Bends(s.Pts, s.Ties))
                    {
                        if (CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b) != "unforced") continue;
                        string near = b.NearFirst ? K(p.EndA) : K(p.EndB), far = b.NearFirst ? K(p.EndB) : K(p.EndA);
                        Inc(by, $"{s.Lay} near {near} far {far} {(b.FromEnd < 0.5 ? "end<0.5" : b.FromEnd < 1.5 ? "end<1.5" : "mid")}");
                        if (ex.Count < (Environment.GetEnvironmentVariable("ALLROWS") == "1" ? 999 : 10)) ex.Add($"{sc.Desc} {p.EndA}|{p.EndB} {s.Lay} n{p.Strands.Count} at {b.Apex} turn {b.Turn:0} arc {b.Arc:0.00} sharp {b.Sharp:0} fromEnd {b.FromEnd:0.00} len {Geo.Length(s.Pts):0.00}");
                        any = true;
                    }
                    if (any) bad++;
                }
            }
            int tot = by.Values.Sum();
            if (rw.Count > 0) Console.WriteLine("ROUNDOUT " + Top(rw, 20));
            Console.WriteLine($"BENDS strands {strands} kinks {kinks} badStrands {bad} unforced {tot} :: {Top(by, 20)}"); foreach (var x in ex) Console.WriteLine("  " + x);
        }
        if (mode == "repeat" || mode == "all")
        {
            foreach (int L in new[] { 3, 4, 5, 6, 9, 12 })
            {
                double min = 9; int under = 0, pairs = 0, kt = 0, kp = 0; var lays = new Dictionary<string, int>();
                for (int seed = 1; seed <= Math.Max(6, N / 5); seed++)
                {
                    var w = new CordWorld(L + 12, 40);
                    for (int r = 0; r < 8; r++)
                    {
                        int z = 4 + r * 4;
                        for (int x = 5; x < 5 + L; x++) w.SetConduit(new Cell(x, z));
                        var g = new MachineInfo { Id = "g" + r, DefName = "G", Kind = MachineKind.Source, X0 = 4, Z0 = z }; g.Hookups.Add(new Cell(5, z));
                        var l = new MachineInfo { Id = "l" + r, DefName = "L", Kind = MachineKind.Consumer, X0 = 5 + L, Z0 = z }; l.Hookups.Add(new Cell(4 + L, z));
                        w.Machines.Add(g); w.Machines.Add(l); w.SetBlocked(new Cell(4, z), BlockKind.Device); w.SetBlocked(new Cell(5 + L, z), BlockKind.Device);
                    }
                    var ps = Build(w, new BuildOptions { Seed = (ulong)seed }).Where(p => p.EndA != null && p.Strands.Count > 0 && HasPts(p.Strands[0])).ToList();
                    foreach (var p in ps) Inc(lays, p.Strands[0].Lay);
                    var fr = ps.Select(p => Frame(p.Strands[0].Pts)).ToList();
                    for (int i = 0; i < fr.Count; i++) for (int j = i + 1; j < fr.Count; j++) { double gg = Gap(fr[i], fr[j]); pairs++; min = Math.Min(min, gg); if (gg < 0.1) { under++; if (Environment.GetEnvironmentVariable("ALLROWS") == "1") Console.WriteLine($"  twin L{L} seed {seed} {ps[i].EndA} {ps[i].Strands[0].Lay} / {ps[j].EndA} {ps[j].Strands[0].Lay} gap {gg:0.###} pathlen {ps[i].PathLen:0.00}"); } }
                    foreach (var t in CordShape.Table(ps)) { kt += t.TooAlike; kp += t.Pairs; }
                }
                Console.WriteLine($"REPEAT L{L}: pairs {pairs} under0.1 {under} min {min:0.###} kernelTooAlike {kt}/{kp} lays {Top(lays)}");
            }
        }
        return 0;
    }
}
