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
