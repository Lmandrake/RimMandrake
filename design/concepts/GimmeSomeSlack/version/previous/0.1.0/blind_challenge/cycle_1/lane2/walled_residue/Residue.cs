// Walled-residue sweep (RIMMANDRAKE_SWEEP_GSS_WALLED_RESIDUE_TWO_THOUSAND_SCENES): the bends sweep's scenes, each strand the bar's instrument still counts,
// with the unforced count after every LayEdge stage, so each residual bend is charged to the stage that made it (or failed to remove it).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;
using RimMandrake.GimmeSomeSlack.Core;

static partial class BlindLane1
{
    static int ResidueMain(string mode, int N, int b0)
    {
        if (mode == "r_stages")
        {
            var tally = new Dictionary<string, int>(); int bad = 0, bends = 0;
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 6000 + t + (walls ? 500 : 0) + (t >= 40 ? 100000 : 0), 6, 14, walls);
                var tr = new Dictionary<string, List<string>>();
                CordBuilder.StepTrace = (st, ea, eb, P) => { string k = ea + "|" + eb; if (!tr.ContainsKey(k)) tr[k] = new List<string>(); tr[k].Add(st + "=" + CordShapeAudit.Unforced(sc.W, ea, eb, P)); };
                foreach (var p in Build(sc.W)) for (int si = 0; si < p.Strands.Count; si++)
                {
                    var s = p.Strands[si];
                    if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) continue;
                    int u = CordShapeAudit.Bends(s.Pts, s.Ties).Count(b => CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b) == "unforced");
                    if (u == 0) continue; bad++; bends += u;
                    var seq = tr.GetValueOrDefault(p.EndA + "|" + p.EndB) ?? new List<string>();
                    // per strand: the first loop's stages come in strand order (unfold..final), the second loop's (unbend, slack, vary) after them
                    int n = p.Strands.Count; var first = seq.Where(x => !x.StartsWith("unbend") && !x.StartsWith("slack") && !x.StartsWith("vary")).ToList();
                    var second = seq.Except(first).ToList();
                    int per1 = n > 0 ? first.Count / n : 0, per2 = n > 0 ? second.Count / n : 0;
                    var mine = first.Skip(si * per1).Take(per1).Concat(second.Skip(si * per2).Take(per2)).ToList();
                    string made = "untraced:" + s.Lay.Split('+')[0];
                    for (int k = 0; k < mine.Count; k++) { int c = int.Parse(mine[k].Split('=')[1]); if (c >= u || (k == mine.Count - 1)) { made = mine[k].Split('=')[0] + (c > 0 ? "" : "?"); break; } }
                    string key = s.Lay + " madeAt " + made;
                    tally[key] = tally.GetValueOrDefault(key) + u;
                    Console.WriteLine($"{sc.Desc} {p.EndA}|{p.EndB} s{si}/{n} {s.Lay} u{u} :: {string.Join(" ", mine)}");
                }
            }
            Console.WriteLine($"RSTAGES badStrands {bad} unforced {bends} :: " + string.Join(", ", tally.OrderByDescending(kv => kv.Value).Select(kv => kv.Key + " " + kv.Value)));
            return 0;
        }
        if (mode == "r_why")
        {
            // every failing strand's SmoothBends verdicts (HopWhy "smooth ..."), and each unforced bend's place: inside a cut end's kept 1.6 cells or not
            var tally = new Dictionary<string, int>();
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 6000 + t + (walls ? 500 : 0) + (t >= 40 ? 100000 : 0), 6, 14, walls);
                var hw = new List<string>();
                CordBuilder.HopWhy = x => { if (x.StartsWith("smooth ")) hw.Add(x); };
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
                {
                    if (s.Pts == null || s.Pts.Count < 3 || s.Lifted) continue;
                    double L = Geo.Length(s.Pts);
                    foreach (var b in CordShapeAudit.Bends(s.Pts, s.Ties))
                    {
                        if (CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b) != "unforced") continue;
                        string near = b.NearFirst ? p.EndA : p.EndB;
                        bool cutNear = near != null && near.StartsWith("terminal");
                        string place = s.Lay == "tangle" ? "heap" : cutNear && b.FromEnd < 1.6 ? "cutKeep<1.6" : L < 4 ? "short" : "body";
                        string k = s.Lay.Split('+')[0] + " " + place;
                        tally[k] = tally.GetValueOrDefault(k) + 1;
                        Console.WriteLine($"BEND {sc.Desc} {p.EndA}|{p.EndB} {s.Lay} {place} S {b.S:0.00}/{L:0.00} fromEnd {b.FromEnd:0.00} turn {b.Turn:0} R {b.RoundR:0.00}");
                    }
                    foreach (var x in hw.Where(x => x.StartsWith("smooth " + p.EndA + "|" + p.EndB + " "))) Console.WriteLine("   " + x.Substring(0, Math.Min(300, x.Length)));
                }
            }
            Console.WriteLine("RWHY " + string.Join(", ", tally.OrderByDescending(kv => kv.Value).Select(kv => kv.Key + " " + kv.Value)));
            return 0;
        }
        if (mode == "r_heapground")
        {
            // each heap cable end the bar still counts a bend at: its tip and leaving heading (the plug's first 0.2 cell), and the heap's ground sampled every 0.05 cell over its
            // box and 2.5 cells round, one JSON line, for heap_escape_search.py's bounded search
            var inv = System.Globalization.CultureInfo.InvariantCulture; string F(double d) => d.ToString("0.###", inv);
            for (int t = 0; t < N; t++) foreach (bool walls in new[] { false, true })
            {
                var sc = MakeScene(b0 + 6000 + t + (walls ? 500 : 0) + (t >= 40 ? 100000 : 0), 6, 14, walls);
                var grounds = new List<(V2 tip, Func<V2, bool> g)>();
                CordBuilder.HeapWalkTrace = (all, via, ok, g) => grounds.Add((all[0], g));
                foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
                {
                    if (s.Lay != "tangle" || s.Pts == null || s.Pts.Count < 3) continue;
                    foreach (var b in CordShapeAudit.Bends(s.Pts, s.Ties))
                    {
                        if (CordShapeAudit.Why(sc.W, p.EndA, p.EndB, s.Pts, b) != "unforced") continue;
                        var P = b.NearFirst ? s.Pts : Enumerable.Reverse(s.Pts).ToList();
                        V2 tip = P[0]; var r = Geo.Resample(P, 0.05); V2 h = r[4] - r[0];
                        var gr = grounds.Count == 0 ? null : grounds.OrderBy(x => Math.Min(V2.Dist(x.tip, s.Pts[0]), V2.Dist(x.tip, s.Pts[s.Pts.Count - 1]))).First().g;   // the walk of this heap (its ports lie together)
                        if (gr == null) { Console.WriteLine("{\"scene\":\"" + sc.Desc + "\",\"noground\":true}"); continue; }
                        double x0 = s.Pts.Min(q => q.X) - 2.5, z0 = s.Pts.Min(q => q.Z) - 2.5, x1 = s.Pts.Max(q => q.X) + 2.5, z1 = s.Pts.Max(q => q.Z) + 2.5;
                        var rows = new List<string>();
                        for (double z = z0; z <= z1; z += 0.05) { var sb = new System.Text.StringBuilder(); for (double x = x0; x <= x1; x += 0.05) sb.Append(gr(new V2(x, z)) ? '1' : sc.W.IsWalkable(new V2(x, z).Floor) ? '0' : 'W'); rows.Add(sb.ToString()); }
                        Console.WriteLine("{\"scene\":\"" + sc.Desc + "\",\"tip\":[" + F(tip.X) + "," + F(tip.Z) + "],\"h\":" + F(Math.Atan2(h.Z, h.X)) + ",\"turn\":" + F(b.Turn) + ",\"fromEnd\":" + F(b.FromEnd)
                            + ",\"x0\":" + F(x0) + ",\"z0\":" + F(z0) + ",\"rows\":[\"" + string.Join("\",\"", rows) + "\"],\"head\":[" + string.Join(",", r.Take(60).Select(q => "[" + F(q.X) + "," + F(q.Z) + "]")) + "]}");
                    }
                }
            }
            return 0;
        }
        if (mode == "r_heapone")
        {
            // one scene (seed N, walls b0): every heap walk attempt's unforced count, then each heap strand's
            var sc = MakeScene(N, 6, 14, b0 == 1);
            CordBuilder.HeapWalkTrace = (all, via, ok, g) => Console.WriteLine($"  walk from {all[0]} ok {ok} n {all.Count} via {via.Count} at {all[all.Count - 1]}");
            CordBuilder.HeapWalkWhy = x => Console.WriteLine("  why " + x);
            foreach (var p in Build(sc.W)) foreach (var s in p.Strands)
                if (s.Lay.StartsWith("tangle")) Console.WriteLine($"STRAND {s.Lay} from {s.Pts[0]} to {s.Pts[s.Pts.Count - 1]} unforced {CordShapeAudit.Unforced(sc.W, p.EndA, p.EndB, s.Pts)} len {Geo.Length(s.Pts):0.00}");
            return 0;
        }
        return -999;
    }
}
