// T_CORD_GEOMETRY_OFFLINE (GimmeSomeSlack 0.1.0, bars cords_lie_slack, cord_slack_lay, no_unforced_sharp_turn): the live rows'
// geometry read, offline, on the production builder over every oracle scene. Per laid floor strand (OverFace and lifted tails
// excluded, as the live read does): drawn length at least 1.4 times its chord; an excursion of a cell or more off the chord on
// strands whose chord is over four cells; and CordShapeAudit's bend tally (the live `bends` probe's own code) reads 0 unforced.
// A planted taut builder (every strand straightened to its chord) must fail the first two. The M2c junction-battery site of
// RIMMANDRAKE_UNBEND_GSS_LEAD_AT_JUNCTION_BATTERY_TWICE is read too when its lab capture exists (lab/m2c_site.json, a LabWorld
// rect capture of the live core site); until it is captured that half is reported NOT CAPTURED, and the live row decides it.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordGeometryChecks
    {
        public const double MinRatio = 1.4, MinExcursion = 1.0, LongChord = 4.0;
        private static void Check(bool ok, string msg) => Program.Check(ok, "geometry: " + msg);

        internal sealed class Read
        {
            public int Strands, Short, Long, Taut, Flat, Unforced;
            public double MinSeenRatio = double.MaxValue;
            public readonly List<string> Worst = new List<string>();
            /// <summary>Every refused strand, named with the lay that drew it (printed under GSS_GEOM_ALL=1).</summary>
            public readonly List<string> All = new List<string>();
        }

        private static double V2Len(List<V2> p) => Len(p);
        private static double Len(List<V2> p) { double s = 0; for (int i = 1; i < p.Count; i++) s += V2.Dist(p[i - 1], p[i]); return s; }

        private static double Excursion(List<V2> p)
        {
            V2 a = p[0], b = p[p.Count - 1], d = b - a;
            double L = Math.Sqrt(d.X * d.X + d.Z * d.Z), m = 0;
            if (L < 1e-9) return 0;
            foreach (V2 q in p) m = Math.Max(m, Math.Abs((q.X - a.X) * d.Z - (q.Z - a.Z) * d.X) / L);
            return m;
        }

        /// <summary>The read over one set of pieces. <paramref name="taut"/> plants the fault: each strand straightened.</summary>
        internal static Read Measure(CordWorld w, List<LaidPiece> pieces, bool taut)
        {
            var r = new Read();
            var tally = new CordShapeAudit.BendTally();
            foreach (LaidPiece p in pieces)
                foreach (CordStrand s in p.Strands)
                {
                    if (s.OverFace || s.Lifted || s.Pts == null || s.Pts.Count < 2) continue;
                    List<V2> pts = taut ? new List<V2> { s.Pts[0], s.Pts[s.Pts.Count - 1] } : s.Pts;
                    double chord = V2.Dist(pts[0], pts[pts.Count - 1]);
                    if (chord < 1.0) { r.Short++; continue; }   // a stub inside one cell has no chord to be slack against
                    r.Strands++;
                    double ratio = Len(pts) / chord;
                    r.MinSeenRatio = Math.Min(r.MinSeenRatio, ratio);
                    if (ratio < MinRatio) { r.Taut++; Note(r, $"{p.EndA}|{p.EndB} ratio {ratio:0.00} chord {chord:0.0} lay {s.Lay}"); }
                    if (chord > LongChord)
                    {
                        r.Long++;
                        if (Excursion(pts) < MinExcursion) { r.Flat++; Note(r, $"{p.EndA}|{p.EndB} excursion {Excursion(pts):0.00} chord {chord:0.0} lay {s.Lay}"); }
                    }
                    if (!taut)
                    {
                        int before = tally.Unforced;
                        tally.Add(w, p, s);
                        if (tally.Unforced > before)
                            Note(r, $"{p.EndA}|{p.EndB} unforced bends {tally.Unforced - before} chord {chord:0.0} lay {s.Lay}: " + string.Join(" ",
                                CordShapeAudit.Bends(s.Pts, s.Ties).Where(bd => CordShapeAudit.Why(w, p.EndA, p.EndB, s.Pts, bd) == "unforced")
                                    .Select(bd => $"at {bd.Apex} s {bd.S:0.00}/{V2Len(s.Pts):0.00} turn {bd.Turn:0} arc {bd.Arc:0.00} sharp {bd.Sharp:0} round {bd.Round:0} r {bd.RoundR:0.00}")));
                    }
                }
            r.Unforced = tally.Unforced;
            return r;
        }

        private static void Note(Read r, string x) { if (r.Worst.Count < 5) r.Worst.Add(x); r.All.Add(x); }

        public static void Run(List<JsonElement> scenes)
        {
            var all = new Read();
            if (Environment.GetEnvironmentVariable("GSS_GEOM_ALL") == "1") CordSlacken.Why = x => Console.WriteLine("  slacken kept: " + x);
            int plantedCaught = 0, plantedScenes = 0;
            foreach (JsonElement s in scenes)
            {
                JsonElement sc = s.GetProperty("scene");
                string name = sc.GetProperty("name").GetString();
                CordWorld w = Program.World(sc);
                HashSet<Cell> live = Program.Live(w, sc);
                var b = new CordBuilder();
                List<LaidPiece> pieces = b.Build(w, new BuildOptions(), live.Contains);
                Read r = Measure(w, pieces, false);
                all.Strands += r.Strands; all.Long += r.Long; all.Taut += r.Taut; all.Flat += r.Flat; all.Unforced += r.Unforced; all.Short += r.Short;
                all.MinSeenRatio = Math.Min(all.MinSeenRatio, r.MinSeenRatio);
                foreach (string x in r.Worst) if (all.Worst.Count < 8) all.Worst.Add(name + ": " + x);
                foreach (string x in r.All) all.All.Add(name + ": " + x);
                Read t = Measure(w, pieces, true);
                if (t.Strands > 0) { plantedScenes++; if (t.Taut > 0) plantedCaught++; }
            }
            Console.WriteLine($"geometry: {all.Strands} strands over {scenes.Count} oracle scenes ({all.Short} one-cell stubs skipped), " +
                              $"{all.Long} over {LongChord} cells; ratio min {all.MinSeenRatio:0.00}; taut {all.Taut}, flat {all.Flat}, unforced bends {all.Unforced}");
            foreach (string x in all.Worst) Console.WriteLine("  geometry worst: " + x);
            if (Environment.GetEnvironmentVariable("GSS_GEOM_ALL") == "1") foreach (string x in all.All) Console.WriteLine("  geometry refused: " + x);
            CordSlacken.Why = null;
            Check(all.Strands > 0, "the oracle scenes lay strands to measure");
            Check(all.Taut == 0, $"every strand's drawn length is at least {MinRatio} x its chord ({all.Taut} under)");
            Check(all.Flat == 0, $"every strand over {LongChord} cells strays a cell or more off its chord ({all.Flat} flat)");
            Check(all.Unforced == 0, $"no unforced sharp bend on any oracle scene ({all.Unforced})");
            Check(plantedScenes > 0 && plantedCaught == plantedScenes, $"planted taut builder refused on {plantedCaught}/{plantedScenes} scenes");
            M2cSite();
            RandomBases();
            TwinLeads();
        }

        // ------------------------------------------------------------------ random bases (GSS blind challenge cycle 1, gss_four 2026-11-15)
        // The oracle scenes alone hid four Problems the blind judge found on random bases. The judge's own scene maker and seeds (lane 1,
        // BlindLane1.MakeScene): runs of conduit as orthogonal random walks, a device beside most run ends, walls laid across some runs.
        private sealed class RandScene { public CordWorld W; public string Desc; }

        private static RandScene MakeScene(int seed, int runs, int maxLen, bool walls, int size = 48)
        {
            var rng = new Random(seed); var w = new CordWorld(size, size); var used = new HashSet<Cell>(); var ms = new List<MachineInfo>(); int mid = 0;
            for (int r = 0; r < runs; r++)
            {
                var c = new Cell(rng.Next(4, size - 4), rng.Next(4, size - 4)); var run = new List<Cell>();
                int len = rng.Next(3, maxLen + 1); Cell dir = Cell.Dirs4[rng.Next(4)];
                for (int i = 0; i < len; i++)
                {
                    if (c.X < 3 || c.Z < 3 || c.X >= size - 3 || c.Z >= size - 3) break;
                    run.Add(c); w.SetConduit(c);
                    if (rng.Next(4) == 0) dir = Cell.Dirs4[rng.Next(4)];
                    c = c + dir;
                }
                foreach (var x in run) used.Add(x);
                if (run.Count < 2) continue;
                foreach (Cell end in new[] { run[0], run[run.Count - 1] })
                {
                    if (rng.Next(4) == 0) continue;
                    foreach (Cell d in Cell.Dirs4.OrderBy(_ => rng.Next()))
                    {
                        Cell m = end + d;
                        if (!w.InBounds(m) || w.IsConduit(m) || used.Contains(m) || ms.Any(o => o.Hookups.Contains(end))) continue;
                        var kind = rng.Next(3) == 0 ? MachineKind.Source : rng.Next(5) == 0 ? MachineKind.Battery : MachineKind.Consumer;
                        var mi = new MachineInfo { Id = "m" + (mid++), DefName = kind.ToString(), Kind = kind, X0 = m.X, Z0 = m.Z };
                        mi.Hookups.Add(end); w.Machines.Add(mi); ms.Add(mi); used.Add(m);
                        w.SetBlocked(m, BlockKind.Device);
                        break;
                    }
                }
            }
            if (walls)
                for (int i = rng.Next(1, 4); i > 0; i--)
                {
                    bool horiz = rng.Next(2) == 0; int at = rng.Next(6, size - 6), from = rng.Next(2, size / 2), to = from + rng.Next(5, size / 2);
                    for (int k = from; k < Math.Min(to, size - 2); k++)
                    {
                        var c = horiz ? new Cell(k, at) : new Cell(at, k);
                        if (used.Contains(c) && !w.IsConduit(c)) continue;
                        w.SetBlocked(c, BlockKind.Wall);
                    }
                }
            return new RandScene { W = w, Desc = $"seed {seed} runs {runs} maxLen {maxLen} walls {walls}" };
        }

        /// <summary>The edge's own conduit chain from its piece key (the VId tokens after the first '#'; the node text after them names other nodes' cells).</summary>
        private static List<V2> OwnChain(string key)
        {
            var o = new List<V2>(); int h = key.IndexOf('#'); if (h < 0) return o;
            foreach (string tok in key.Substring(h + 1).Split(';'))
            {
                if (!System.Text.RegularExpressions.Regex.IsMatch(tok, @"^[cwmstk]:")) break;
                var m = System.Text.RegularExpressions.Regex.Match(tok, @"^[cw]:\((-?\d+),(-?\d+)\)$");
                if (m.Success) o.Add(new V2(int.Parse(m.Groups[1].Value) + 0.5, int.Parse(m.Groups[2].Value) + 0.5));
            }
            return o;
        }

        private static double DistToLine(V2 q, List<V2> l)
        {
            double best = double.MaxValue;
            for (int i = 1; i < l.Count; i++)
            {
                V2 a = l[i - 1], ab = l[i] - a; double L2 = ab.X * ab.X + ab.Z * ab.Z;
                double u = L2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((q.X - a.X) * ab.X + (q.Z - a.Z) * ab.Z) / L2));
                best = Math.Min(best, V2.Dist(q, a + ab * u));
            }
            return best;
        }

        private static double[] Frame(List<V2> pts, int n = 40)
        {
            List<V2> r = Geo.Resample(pts, Geo.Length(pts) / (n - 1)); while (r.Count < n) r.Add(r[r.Count - 1]);
            V2 a = r[0], b = r[r.Count - 1], ax = (b - a).Norm(), pe = ax.Perp; var o = new double[2 * n];
            for (int i = 0; i < n; i++) { V2 d = r[Math.Min(i, r.Count - 1)] - a; o[2 * i] = d.X * ax.X + d.Z * ax.Z; o[2 * i + 1] = d.X * pe.X + d.Z * pe.Z; }
            return o;
        }

        /// <summary>Mean point gap of two cords in their own frames, the least over either way round and mirrored (the blind judge's measure).</summary>
        private static double Gap(double[] a, double[] b)
        {
            int n = a.Length / 2; double best = double.MaxValue;
            foreach (bool rev in new[] { false, true })
                foreach (int mir in new[] { 1, -1 })
                {
                    double s = 0;
                    for (int i = 0; i < n; i++)
                    {
                        int j = rev ? n - 1 - i : i;
                        double bx = rev ? b[2 * (n - 1)] - b[2 * j] : b[2 * j], bz = mir * (rev ? b[2 * j + 1] - b[2 * (n - 1) + 1] : b[2 * j + 1]);
                        s += Math.Sqrt((a[2 * i] - bx) * (a[2 * i] - bx) + (a[2 * i + 1] - bz) * (a[2 * i + 1] - bz));
                    }
                    best = Math.Min(best, s / n);
                }
            return best;
        }

        /// <summary>The unforced bends left on the bend seeds (RIMMANDRAKE_UNBEND_GSS_RANDOM_BASES_SEVEN_SCENES_HID_IT: 82 before the fix, 4 after the first, 0 since the cut
        /// lead's join is blended, gss_last). A ratchet: it may only come down; at 0 it is the bar itself.</summary>
        private const int BendsRatchet = 0;

        private static void RandomBases()
        {
            Func<Cell, bool> live = c => true;
            // cords_lie_slack, 1.4x: every end-to-end strand with a chord of 2+ cells (lane 1 L1_CORD_SLACK_RATIO's seeds)
            int slackN = 0; var slackBad = new List<string>();
            for (int s = 0; s < 50; s++)
            {
                RandScene sc = MakeScene(3000 + s, 7, 16, false);
                foreach (LaidPiece p in new CordBuilder().Build(sc.W, new BuildOptions(), live))
                    foreach (CordStrand st in p.Strands)
                    {
                        if (p.EndA == null || p.EndB == null || st.Pts == null || st.Pts.Count < 2 || st.OverFace || st.DiveA || st.DiveB) continue;
                        double ch = V2.Dist(st.Pts[0], st.Pts[st.Pts.Count - 1]);
                        if (ch < 2) continue;
                        slackN++;
                        double ratio = Len(st.Pts) / ch;
                        if (ratio < MinRatio && slackBad.Count < 4) slackBad.Add($"{sc.Desc} {p.EndA}|{p.EndB} {ratio:0.00} lay {st.Lay}");
                    }
            }
            Check(slackN > 300 && slackBad.Count == 0, $"random bases: every cord with a chord of 2+ cells is drawn 1.4x it ({slackN} strands): {string.Join("; ", slackBad)}");
            // cords_lie_slack, the stray: an edge of more than four conduit cells strays a cell off its own conduit line (L1_CORD_EXCURSION's seeds)
            int excN = 0; var excBad = new List<string>();
            for (int s = 0; s < 40; s++)
            {
                RandScene sc = MakeScene(4000 + s, 5, 18, false);
                foreach (LaidPiece p in new CordBuilder().Build(sc.W, new BuildOptions(), live))
                {
                    if (p.EndA == null || p.EndB == null || p.Strands.Count == 0 || p.Strands[0].Pts == null || p.Strands[0].Pts.Count < 2) continue;
                    List<V2> chain = OwnChain(p.Key);
                    if (chain.Count < 6) continue;
                    excN++;
                    double far = p.Strands[0].Pts.Max(q => DistToLine(q, chain));
                    if (far < MinExcursion && excBad.Count < 4) excBad.Add($"{sc.Desc} {p.EndA}|{p.EndB} {far:0.00} lay {p.Strands[0].Lay}");
                }
            }
            Check(excN > 80 && excBad.Count == 0, $"random bases: every edge over four conduit cells strays a cell off its conduit line ({excN} edges): {string.Join("; ", excBad)}");
            // no_unforced_sharp_turn: the bar's own tally over the bend seeds, open floor and walled (L1_CORD_BENDS_TALLY's), ratcheted
            var tally = new CordShapeAudit.BendTally();
            foreach (bool walls in new[] { false, true })
                for (int s = 0; s < 40; s++)
                {
                    RandScene sc = MakeScene(6000 + s + (walls ? 500 : 0), 6, 14, walls);
                    foreach (LaidPiece p in new CordBuilder().Build(sc.W, new BuildOptions(), live)) foreach (CordStrand st in p.Strands) tally.Add(sc.W, p, st);
                }
            Check(tally.Strands > 500 && tally.Unforced <= BendsRatchet, $"random bases: unforced bends over 80 scenes {tally.Unforced} of {tally.Bends} in {tally.Strands} strands (ratchet {BendsRatchet}; 82 before the fix)");
            // cords_never_repeat: eight equal runs side by side, generator to consumer, lengths 4/6/9/12, build seeds 1..6 (L1_NO_REPEAT's room)
            double minGap = double.MaxValue; int pairs = 0, twins = 0;
            foreach (int L in new[] { 4, 6, 9, 12 })
                for (int seed = 1; seed <= 6; seed++)
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
                    List<double[]> fr = new CordBuilder().Build(w, new BuildOptions { Seed = (ulong)seed }, live)
                        .Where(p => p.EndA != null && p.Strands.Count > 0 && p.Strands[0].Pts != null && p.Strands[0].Pts.Count >= 2).Select(p => Frame(p.Strands[0].Pts)).ToList();
                    for (int i = 0; i < fr.Count; i++)
                        for (int j = i + 1; j < fr.Count; j++) { double gp = Gap(fr[i], fr[j]); pairs++; minGap = Math.Min(minGap, gp); if (gp < 0.1) twins++; }
                }
            Check(pairs > 600 && twins == 0, $"random bases: no two equal runs side by side draw one cord (mean point gap under 0.1 cell): {twins} of {pairs} pairs, closest {minGap:0.000}");
            Console.WriteLine($"geometry: random bases {slackN} strands slack-read, {excN} long edges, bends {tally.Unforced} unforced of {tally.Bends}, twins {twins} of {pairs} (closest {minGap:0.000})");
        }

        /// <summary>Eight equal runs of length <paramref name="L"/>, generator to consumer, three cells apart, the rows in <paramref name="rows"/> only.</summary>
        private static CordWorld EqualRuns(int L, IEnumerable<int> rows)
        {
            var w = new CordWorld(L + 12, 40);
            foreach (int r in rows)
            {
                int z = 4 + r * 4;
                for (int x = 5; x < 5 + L; x++) w.SetConduit(new Cell(x, z));
                var g = new MachineInfo { Id = "g" + r, DefName = "G", Kind = MachineKind.Source, X0 = 4, Z0 = z }; g.Hookups.Add(new Cell(5, z));
                var l = new MachineInfo { Id = "l" + r, DefName = "L", Kind = MachineKind.Consumer, X0 = 5 + L, Z0 = z }; l.Hookups.Add(new Cell(4 + L, z));
                w.Machines.Add(g); w.Machines.Add(l); w.SetBlocked(new Cell(4, z), BlockKind.Device); w.SetBlocked(new Cell(5 + L, z), BlockKind.Device);
            }
            return w;
        }

        /// <summary>
        /// cords_never_repeat across pieces (RIMMANDRAKE_PART_GSS_TWIN_LEADS_THIRD_FILING_SAME_SIX): the six rooms of equal short leads the walled_residue sweep
        /// found twinned before the twin pass (diag.py repeat 1000 --base at a264e7b55d: L3 seeds 122/141, L4 65/140, L5 176/189, gaps 0.031-0.098), each now
        /// parted; and the pass is a pure function of the base pieces: a builder that drops the twin's partner row and brings it back draws what a cold build
        /// draws, and the lone lead gets its base lay back.
        /// </summary>
        private static void TwinLeads()
        {
            Func<Cell, bool> live = c => true;
            var all = Enumerable.Range(0, 8).ToList();
            double minGap = double.MaxValue; int twins = 0, relaid = 0;
            foreach ((int L, int seed) in new[] { (3, 122), (3, 141), (4, 65), (4, 140), (5, 176), (5, 189) })
            {
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(EqualRuns(L, all), new BuildOptions { Seed = (ulong)seed }, live)
                    .Where(p => p.EndA != null && p.Strands.Count > 0 && p.Strands[0].Pts != null && p.Strands[0].Pts.Count >= 2).ToList();
                relaid += b.LastTwinRelays;
                List<double[]> fr = ps.Select(p => Frame(p.Strands[0].Pts)).ToList();
                for (int i = 0; i < fr.Count; i++)
                    for (int j = i + 1; j < fr.Count; j++) { double gp = Gap(fr[i], fr[j]); minGap = Math.Min(minGap, gp); if (gp < 0.1) twins++; }
            }
            Check(twins == 0 && relaid >= 6, $"twin leads: the six rooms that twinned draw no two leads under 0.1 cell apart: {twins} twins, closest {minGap:0.000}, {relaid} leads laid again (6+ expected)");
            // L5 seed 189 twinned rows 3 and 5 (source:5,16 / source:5,24)
            string Sig(IEnumerable<LaidPiece> ps) => string.Join(";", ps.Where(p => p.EndA != null).Select(p => p.Key + "=" + p.GeometryHash().ToString("x16")).OrderBy(x => x, StringComparer.Ordinal));
            var opt = new BuildOptions { Seed = 189 };
            var without = all.Where(r => r != 5).ToList();
            var inc = new CordBuilder();
            List<LaidPiece> lone = inc.Build(EqualRuns(5, without), opt, live);
            int loneRelays = inc.LastTwinRelays;
            List<LaidPiece> both = inc.Build(EqualRuns(5, all), opt, live);
            int bothRelays = inc.LastTwinRelays;
            List<LaidPiece> again = inc.Build(EqualRuns(5, without), opt, live);
            string cold = Sig(new CordBuilder().Build(EqualRuns(5, all), opt, live)), coldLone = Sig(new CordBuilder().Build(EqualRuns(5, without), opt, live));
            Check(bothRelays > 0 && Sig(both) == cold, $"twin leads: a builder that adds the twin's partner draws what a cold build draws ({bothRelays} laid again; equal {Sig(both) == cold})");
            Check(loneRelays == 0 && inc.LastTwinRelays == 0 && Sig(again) == Sig(lone) && Sig(again) == coldLone,
                  $"twin leads: with the partner gone the lead keeps its base lay, cold and incremental alike (relays {loneRelays}/{inc.LastTwinRelays}; equal {Sig(again) == Sig(lone)}/{Sig(again) == coldLone})");
            Console.WriteLine($"geometry: twin leads, six rooms closest {minGap:0.000}, {relaid} leads laid again");
        }

        /// <summary>The M2c junction-battery lead, from its lab capture when one exists.</summary>
        private static void M2cSite()
        {
            string path = Path.Combine(AppContext.BaseDirectory, "lab", "m2c_site.json");
            if (!File.Exists(path))
            {
                Console.WriteLine("geometry: M2c junction-battery site NOT CAPTURED (lab/m2c_site.json absent): the live row M2c_no_sharp_bends decides it");
                return;
            }
            using JsonDocument d = JsonDocument.Parse(File.ReadAllText(path));
            CordWorld w = LabWorld.Read(d.RootElement, out BuildOptions opt, out HashSet<Cell> live);
            List<LaidPiece> pieces = new CordBuilder().Build(w, opt, live.Contains);
            Read r = Measure(w, pieces, false);
            Console.WriteLine($"geometry: M2c site {r.Strands} strands, unforced bends {r.Unforced}, taut {r.Taut}, flat {r.Flat}");
            Check(r.Unforced == 0, $"M2c junction-battery site: no unforced sharp bend ({r.Unforced})");
        }
    }
}
