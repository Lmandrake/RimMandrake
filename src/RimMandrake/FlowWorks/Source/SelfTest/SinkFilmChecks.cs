// RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM (FlowWorks in-game visit 3, 2026-11-21, sc_source_pays row
// SRC_flow_stops_when_empty): an unlimited RM_FlowSink drew the pond past its wet line, then its drained total stood still while
// 80 core squares kept 1 dL each. His ruling POND_PUMP_FIX_LAST_DROP_COUNTS ("ponds pump to last dL"): the draw reaches 0 dL.
// Cause: RM_LevelSolve lays a body's remainder dL one each in key order; a flow sink is not an edge sink, so its reach square was
// ranked by cell index (81st of the core band in the visit-3 pond), and once the body held fewer odd dL than that rank the
// square read 0 every pulse. Fix: RM_FlowKernel.drawCell seeds the sink hops as an edge sink does, and with a flow sink drawing
// the hops follow each square's deepest way to a sink (DeepestSinkHops): the sweep's first green run failed 74 cases where a
// shallow sink on the shelf row sat nearer than a deep one, and the core's last dL lay by the shallow one, out of its reach.
//
// Everything here is PRODUCTION code on plain arrays: the kernel (RM_FlowKernel via ArrayWorld) and the sink's own pulse
// (RM_MapControlMath.DrainReach, which Building_RM_FlowSink.FlowPulse runs). The judge is independent of the kernel: a square may
// keep only water below its drain bottleneck (the widest path, by dug depth, from any draw square), never a dL above it.
//
// The range swept (MapControl_sink_film_regime_sweep): pond shape (a 1-wide run, a square, the visit-3 core, the core with its 0.5 m shelf
// rows, the core with a deeper moat, a core with a sill pocket) x sink position (each side's first, middle and last square, and
// on a dug square) x film left (1, 5, N-1, N, N+1, 2N+3, 37N+11 dL; N = the pond's squares) x sink rate (unlimited, 1, 0.25 level
// a pulse) x one sink or two. Left out: fluids other than water (the sink's filter only changes which squares it takes, not the
// lay), sealed sluices (a sealed square is never a hop seed, as for an edge sink), rain, viscosity (water moves every pulse), and
// networks over the partition cap (NetworkSinkDrain, edge sinks only; a pond that size is not a sink scene).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.MapControls;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SinkFilmChecks
    {
        private const long U = RM_LevelSolve.U;
        /// <summary>Building_RM_FlowSink.UnlimitedCap (5 x 255 levels).</summary>
        private const int UnlimitedCap = 5 * 255;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private sealed class Sink
        {
            public int x, z;
            public bool unlimited;
            public float rate;
            public float carry;
        }

        private sealed class Scene
        {
            public ArrayWorld w;
            public List<int> dug = new List<int>();
            public List<Sink> sinks = new List<Sink>();
            public string name;
            public int Idx(int x, int z) => z * w.w + x;
            public void Dig(int x, int z, int d)
            {
                int c = Idx(x, z);
                if (w.k.depth[c] == 0) dug.Add(c);
                w.k.depth[c] = (byte)d;
            }
        }

        private struct Outcome
        {
            public long excess;      // worst dL a square holds above its drain bottleneck (0 = drained to the last dL)
            public int wetAbove;     // squares holding any dL above their bottleneck
            public int pulses;       // pulses until the drained total stood still
            public bool stalled;     // the drained total stood still (false: still drawing at the bound)
            public long drained;
            public string error;
        }

        /// <summary>Reach of a sink at (x, z): its own square, then N, E, S, W (in bounds), as Building_RM_MapControl.Reach.</summary>
        private static List<int> Reach(Scene s, Sink k)
        {
            var r = new List<int>();
            int[] dx = { 0, 0, 1, 0, -1 }, dz = { 0, 1, 0, -1, 0 };
            for (int i = 0; i < 5; i++)
            {
                int x = k.x + dx[i], z = k.z + dz[i];
                if (x >= 0 && z >= 0 && x < s.w.w && z < s.w.h) r.Add(s.Idx(x, z));
            }
            return r;
        }

        /// <summary>The independent judge: for each dug square joined to a draw square, the bottleneck B = the largest d such that
        /// a path of dug squares all at least d deep joins it to a draw square (the draw square's own depth counts). Water above
        /// -B notches can run to the sink, so a drained pond holds at most (depth - B) x U there.</summary>
        private static Dictionary<int, int> Bottlenecks(Scene s, IEnumerable<int> draws)
        {
            var best = new Dictionary<int, int>();
            var k = s.w.k;
            var open = new SortedSet<(int neg, int c)>();
            foreach (int c in draws)
            {
                if (k.depth[c] == 0) continue;
                best[c] = k.depth[c];
                open.Add((-k.depth[c], c));
            }
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                int b = -top.neg, c = top.c;
                if (best[c] != b) continue;
                int x = c % s.w.w, z = c / s.w.w;
                foreach (var (nx, nz) in new[] { (x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1) })
                {
                    if (nx < 0 || nz < 0 || nx >= s.w.w || nz >= s.w.h) continue;
                    int n = s.Idx(nx, nz);
                    if (k.depth[n] == 0) continue;
                    int nb = Math.Min(b, k.depth[n]);
                    if (best.TryGetValue(n, out int have) && have >= nb) continue;
                    if (best.ContainsKey(n)) open.Remove((-have, n));
                    best[n] = nb;
                    open.Add((-nb, n));
                }
            }
            return best;
        }

        /// <summary>The live pulse order (RM_MapComponent_Excavation.DoPulse): the map controls first (each sink draws its reach
        /// through the production DrainReach and names its draw squares), then the kernel with drawCell set.</summary>
        private static Outcome Run(Scene s, int bound)
        {
            var k = s.w.k;
            // When the sink may be called stopped: a solve domain is a body's wet squares and a one-square dry rim, so a film too
            // thin to cover its pond creeps a square a pulse (toward the sink: the remainder is laid nearest it). No path in the dig
            // is longer than its square count, so a draw that stays quiet that long (plus 5) has stopped, not paused in transit.
            // A first window of 20 pulses (measured, this case's own first green run) called 445 creeping films stuck.
            int still = s.dug.Count + 5;
            var o = new Outcome();
            var draws = new HashSet<int>();
            long start = s.dug.Sum(c => k.WaterOf(c));
            int quiet = 0;
            for (int p = 1; p <= bound; p++)
            {
                draws.Clear();
                long took = 0;
                foreach (Sink sk in s.sinks)
                {
                    int due = sk.unlimited ? UnlimitedCap : RM_MapControlMath.Due(ref sk.carry, sk.rate);
                    var reach = Reach(s, sk).Where(c => k.IsExcavated(c)).ToList();
                    if (RM_MapControlMath.SinkDraws(sk.unlimited, sk.rate)) foreach (int c in reach) draws.Add(c);
                    took += RM_MapControlMath.DrainReach(due * U, reach.Count, i => k.WaterOf(reach[i]),
                        (i, max) => { long w = k.WaterOf(reach[i]); long t = Math.Min(w, max); k.SetWaterOf(reach[i], w - t); return t; });
                }
                o.drained += took;
                k.drawCell = draws.Count == 0 ? null : (Func<int, bool>)draws.Contains;
                s.w.Pulse(s.dug);
                if (k.worstImbalance >= 0.001f && o.error == null) o.error = "pulse " + p + ": ledger: " + string.Join("; ", k.imbalanceReports);
                long held = s.dug.Sum(c => k.WaterOf(c));
                if (held != start - o.drained && o.error == null) o.error = "pulse " + p + ": holds " + held + " dL, started " + start + " - drained " + o.drained;
                quiet = took == 0 ? quiet + 1 : 0;
                o.pulses = p;
                if (quiet >= still) { o.stalled = true; break; }
            }
            var all = new List<int>();
            foreach (Sink sk in s.sinks) all.AddRange(Reach(s, sk).Where(c => k.IsExcavated(c)));
            var bn = Bottlenecks(s, all);
            foreach (var kv in bn)
            {
                long over = k.WaterOf(kv.Key) - Math.Max(0, k.depth[kv.Key] - kv.Value) * U;
                if (over > 0) { o.wetAbove++; o.excess = Math.Max(o.excess, over); }
            }
            return o;
        }

        /// <summary>The visit-3 pond (concept_scenes._source_pays): a 20 x 8 core dug 2 m in a 0.5 m shelf ring, a dry 3 m moat of 60
        /// squares joined to the core's east side, the sink on the undug square west of the core's row 5. Filled brim-full, the
        /// moat drawn for 200 pulses (and a tap-0 sink for 60), then an unlimited sink.</summary>
        private static Scene Visit3(out Sink sink)
        {
            int ox = 2, oz = 2;
            var s = new Scene { w = new ArrayWorld(ox + 82, oz + 12), name = "visit3" };
            s.w.k.viscosityEnabled = true;
            for (int i = 0; i < 20; i++)
            {
                s.Dig(ox + i, oz, 1); s.Dig(ox + i, oz + 9, 1);
                for (int j = 1; j <= 8; j++) s.Dig(ox + i, oz + j, 4);
            }
            foreach (int c in s.dug) { s.w.k.water[c] = s.w.k.depth[c] * (int)U; s.w.cellFluid[c] = ArrayWorld.Water; }
            for (int p = 0; p < 5; p++) s.w.Pulse(s.dug);
            for (int i = 0; i < 60; i++) s.Dig(ox + 20 + i, oz + 5, 6);
            for (int p = 0; p < 260; p++) s.w.Pulse(s.dug);
            sink = new Sink { x = ox - 1, z = oz + 5, unlimited = true };
            s.sinks.Add(sink);
            return s;
        }

        /// <summary>A pond for the sweep; returns its pond squares (the moat and pocket are not pond squares).</summary>
        private static Scene Shape(string shape, out int x0, out int z0, out int pw, out int ph, int coreD = 4, int shelfD = 1)
        {
            x0 = 2; z0 = 2;
            switch (shape)
            {
                case "run": pw = 12; ph = 1; break;
                case "square": pw = 3; ph = 3; break;
                default: pw = 20; ph = 8; break;
            }
            int extra = shape == "moat" ? 12 : 0;
            var s = new Scene { w = new ArrayWorld(x0 + pw + extra + 3, z0 + ph + 4), name = shape };
            s.w.k.viscosityEnabled = true;
            for (int i = 0; i < pw; i++)
                for (int j = 0; j < ph; j++)
                {
                    int d = coreD;
                    if (shape == "pocket" && i >= pw - 4) d = i == pw - 4 ? 1 : 6;   // a 0.5 m sill, then a 3 m pocket behind it
                    s.Dig(x0 + i, z0 + j, d);
                }
            if (shape == "shelf")
            {
                for (int i = 0; i < pw; i++) { s.Dig(x0 + i, z0 - 1, shelfD); s.Dig(x0 + i, z0 + ph, shelfD); }   // the visit-3 shelf rows
            }
            if (shape == "moat")
                for (int i = 0; i < extra; i++) s.Dig(x0 + pw + i, z0 + ph / 2, 6);
            return s;
        }

        private static IEnumerable<(string, int, int)> SinkSpots(int x0, int z0, int pw, int ph, bool shelf)
        {
            int m = shelf ? 1 : 0;     // the shelf rows sit one square out to the S and N
            int[] xs = { x0, x0 + pw / 2, x0 + pw - 1 }, zs = { z0, z0 + ph / 2, z0 + ph - 1 };
            string[] tag = { "first", "mid", "last" };
            for (int i = 0; i < 3; i++)
            {
                yield return ("W" + tag[i], x0 - 1, zs[i]);
                yield return ("E" + tag[i], x0 + pw, zs[i]);
                yield return ("S" + tag[i], xs[i], z0 - 1 - m);
                yield return ("N" + tag[i], xs[i], z0 + ph + m);
            }
            yield return ("on", x0 + pw / 2, z0 + ph / 2);
        }

        /// <summary>Lays <paramref name="dl"/> dL as a film: everything on the square farthest from the sinks, then leveled by
        /// the kernel with no sink drawing (what a body drawn down to its film looks like before the sink's next pulse).</summary>
        private static void LayFilm(Scene s, long dl, int farDepth = 4)
        {
            var k = s.w.k;
            foreach (int c in s.dug) { k.water[c] = 0; s.w.cellFluid[c] = ArrayWorld.Water; }
            int far = s.dug.Where(c => k.depth[c] <= farDepth).OrderByDescending(c => Math.Abs(c % s.w.w - s.sinks[0].x) + Math.Abs(c / s.w.w - s.sinks[0].z)).First();
            k.water[far] = (int)Math.Min(dl, k.depth[far] * U);
            long left = dl - k.water[far];
            foreach (int c in s.dug) { if (left <= 0) break; long put = Math.Min(left, k.depth[c] * U - k.water[c]); k.water[c] += (int)put; left -= put; }
            k.drawCell = null;
            for (int p = 0; p < 4; p++) s.w.Pulse(s.dug);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("MapControl_sink_film_visit3_drains_to_last_dL", () =>
            {
                var s = Visit3(out Sink sink);
                long moat = s.dug.Where(c => s.w.k.depth[c] == 6).Sum(c => s.w.k.WaterOf(c));
                Assert(moat > 0, "the moat took nothing: the visit-3 pond was not drawn");
                // the control: a tap-0 sink draws nothing and names no draw square
                Assert(!RM_MapControlMath.SinkDraws(false, 0f) && RM_MapControlMath.SinkDraws(false, 0.25f) && RM_MapControlMath.SinkDraws(true, 0f),
                    "SinkDraws: a tap-0 sink draws, or a drawing sink does not");
                var o = Run(s, 20000);
                var core = s.dug.Where(c => s.w.k.depth[c] == 4).ToList();
                int wetCore = core.Count(c => s.w.k.WaterOf(c) > 0);
                Console.WriteLine("      visit-3 pond: drained " + o.drained / (float)U + " levels in " + o.pulses + " pulses (stalled " + o.stalled
                    + "); core squares still wet " + wetCore + " of " + core.Count + ", max " + core.Max(c => s.w.k.WaterOf(c)) + " dL; worst over the bottleneck "
                    + o.excess + " dL on " + o.wetAbove + " squares (limit 0)");
                Assert(o.error == null, o.error);
                Assert(o.stalled, "the sink was still drawing after " + o.pulses + " pulses");
                Assert(wetCore == 0 && o.wetAbove == 0, "the sink stopped with " + wetCore + " core squares wet (max "
                    + core.Max(c => s.w.k.WaterOf(c)) + " dL): the film's last dL never reached the sink");
            });

            Case("MapControl_sink_film_regime_sweep", () =>
            {
                int cases = 0, fails = 0, worstPulses = 0;
                long worst = 0;
                var failed = new List<string>();
                foreach (string shape in new[] { "run", "square", "core", "shelf", "moat", "pocket" })
                {
                    Shape(shape, out int x0, out int z0, out int pw, out int ph);
                    int n = pw * ph;
                    foreach (var (spot, sx, sz) in SinkSpots(x0, z0, pw, ph, shape == "shelf"))
                        foreach (long film in new long[] { 1, 5, n - 1, n, n + 1, 2 * n + 3, 37L * n + 11 })
                            foreach (float rate in new[] { -1f, 1f, 0.25f })
                                foreach (bool two in new[] { false, true })
                                {
                                    if (film <= 0 || (two && rate != -1f)) continue;
                                    var s = Shape(shape, out _, out _, out _, out _);
                                    s.sinks.Add(new Sink { x = sx, z = sz, unlimited = rate < 0, rate = Math.Max(0f, rate) });
                                    if (two) s.sinks.Add(new Sink { x = x0 + pw, z = z0 + ph - 1, unlimited = true });
                                    if (s.sinks.All(k => Reach(s, k).All(c => !s.w.k.IsExcavated(c)))) continue;   // a spot outside the dig
                                    LayFilm(s, film);
                                    var o = Run(s, 50 * n + 3000);
                                    cases++;
                                    worst = Math.Max(worst, o.excess);
                                    worstPulses = Math.Max(worstPulses, o.pulses);
                                    if (o.error != null || !o.stalled || o.wetAbove > 0)
                                    {
                                        fails++;
                                        if (failed.Count < 6) failed.Add(shape + "/" + spot + "/film " + film + "/rate " + (rate < 0 ? "unl" : rate.ToString()) + (two ? "/two" : "")
                                            + ": " + (o.error ?? (!o.stalled ? "still drawing at " + o.pulses : o.wetAbove + " squares over, max " + o.excess + " dL")));
                                    }
                                }
                }
                Console.WriteLine("      sweep: " + cases + " cases, " + fails + " failed; worst over the bottleneck " + worst + " dL (limit 0); slowest stop "
                    + worstPulses + " pulses (quiet window included; bound 50 N + 3000)");
                Assert(cases >= 500, "the sweep read only " + cases + " cases");
                Assert(fails == 0, fails + " of " + cases + " cases kept film the sink could reach: " + string.Join(" | ", failed));
            });

            Case("MapControl_sink_film_shallow_beside_deep", () =>
            {
                // Dense around the regime the first fix failed (74 of 2184: a sink on the 0.5 m shelf row beside the core, a deep sink
                // across it). Shelf 0.5..1.5 m x core 2 or 3 m x the shallow sink at every second shelf square x the deep sink at the
                // east side's first, middle and last row, unlimited or 0.25 a pulse x film 1, N-1, N+1, 37N+11 dL.
                int cases = 0, fails = 0, worstPulses = 0;
                long worst = 0;
                var failed = new List<string>();
                foreach (int shelfD in new[] { 1, 2, 3 })
                    foreach (int coreD in new[] { 4, 6 })
                    {
                        Shape("shelf", out int x0, out int z0, out int pw, out int ph, coreD, shelfD);
                        int n = pw * ph;
                        for (int sx = x0; sx < x0 + pw; sx += 2)
                            foreach (int dz in new[] { z0, z0 + ph / 2, z0 + ph - 1 })
                                foreach (float rate in new[] { -1f, 0.25f })
                                    foreach (long film in new long[] { 1, n - 1, n + 1, 37L * n + 11 })
                                    {
                                        var s = Shape("shelf", out _, out _, out _, out _, coreD, shelfD);
                                        s.sinks.Add(new Sink { x = sx, z = z0 - 2, unlimited = true });
                                        s.sinks.Add(new Sink { x = x0 + pw, z = dz, unlimited = rate < 0, rate = Math.Max(0f, rate) });
                                        LayFilm(s, film, coreD);
                                        var o = Run(s, 50 * n + 3000);
                                        cases++;
                                        worst = Math.Max(worst, o.excess);
                                        worstPulses = Math.Max(worstPulses, o.pulses);
                                        if (o.error != null || !o.stalled || o.wetAbove > 0)
                                        {
                                            fails++;
                                            if (failed.Count < 6) failed.Add("shelf " + shelfD + "/core " + coreD + "/shallow x " + sx + "/deep z " + dz + "/rate " + rate + "/film " + film
                                                + ": " + (o.error ?? (!o.stalled ? "still drawing at " + o.pulses : o.wetAbove + " squares over, max " + o.excess + " dL")));
                                        }
                                    }
                    }
                Console.WriteLine("      shallow beside deep: " + cases + " cases, " + fails + " failed; worst over the bottleneck " + worst + " dL (limit 0); slowest stop "
                    + worstPulses + " pulses");
                Assert(cases >= 1000, "the dense sweep read only " + cases + " cases");
                Assert(fails == 0, fails + " of " + cases + " cases kept film the deep sink could reach: " + string.Join(" | ", failed));
            });

            Case("MapControl_sink_film_wiring", () =>
            {
                string d = AppContext.BaseDirectory, root = null;
                for (int i = 0; i < 10 && d != null && root == null; i++, d = Path.GetDirectoryName(d))
                    if (Directory.Exists(Path.Combine(d, "Source", "MapControls"))) root = d;
                Assert(root != null, "FlowWorks mod root not found above " + AppContext.BaseDirectory);
                string taps = File.ReadAllText(Path.Combine(root, "Source", "MapControls", "RM_FlowTaps.cs"));
                string sink = taps.Substring(taps.IndexOf("class Building_RM_FlowSink", StringComparison.Ordinal));
                Assert(sink.Contains("RM_MapControlMath.DrainReach(") && sink.Contains("ex.NoteSinkDrawCell(c)")
                    && sink.Contains("RM_MapControlMath.SinkDraws(unlimited, ratePerPulse)"),
                    "Building_RM_FlowSink does not draw through DrainReach or does not name its draw squares");
                string ex = File.ReadAllText(Path.Combine(root, "Source", "RM_MapComponent_Excavation.cs"));
                int clear = ex.IndexOf("sinkDrawCells.Clear();\n\t\t\tMapControls.RM_MapControls.PulseAll(map, this);", StringComparison.Ordinal);
                int set = ex.IndexOf("flowKernel.drawCell = sinkDrawCells.Count == 0 ? null", StringComparison.Ordinal);
                int begin = ex.IndexOf("flowKernel.BeginPulse(pulseSeeds, pulseCount);", StringComparison.Ordinal);
                Assert(clear >= 0 && set > clear && begin > set, "DoPulse does not clear the draw squares before the map controls and hand them to the kernel before BeginPulse");
            });
        }
    }
}
