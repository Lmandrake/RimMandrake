// Approach B for WeatherSuite: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WeatherKernel.cs):
//   arc       great-circle arc against an independent haversine: range, symmetry, antipode, pole, longitude wrap, triangle inequality
//   bands     terminator / nightside band tests: the shipped 63..117 / 117 geometry never puts a tile in both, covers every arc from 63 up,
//             the invalid-tile sentinel is in neither; the exclusive nightside edge keeps that true for any geometry that shares an edge
//   tint      maximised-aurora channel arithmetic: never past white, never darker than vanilla at the shipped defaults (every channel 0..1),
//             monotone in brightness; reports (does not fail on) how many slider-range corners can dip below vanilla
//   forecast  the instrument's top-N shares: descending, tie-stable, over the total of all positive weights, never above 100% in sum
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL: the Ash'karr geometry (substellar 0,0; wall 63..117)
// and the default tint (sat 0.35, overlay 0.05, brightness 1.15) are design-draft numbers.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.StarWars.WeatherSuite;

namespace RimMandrake.StarWars.WeatherSuite.SelfTest
{
    internal static class WeatherFuzz
    {
        public static long Cases, Steps, InWall, InDark, Neither, CornerDark, CornerTotal;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        private static double Haversine(double lat1, double lon1, double lat2, double lon2)
        {
            double d2r = Math.PI / 180.0;
            double a = Math.Pow(Math.Sin((lat2 - lat1) * d2r / 2), 2) + Math.Cos(lat1 * d2r) * Math.Cos(lat2 * d2r) * Math.Pow(Math.Sin((lon2 - lon1) * d2r / 2), 2);
            return 2 * Math.Asin(Math.Min(1.0, Math.Sqrt(a))) / d2r;
        }

        private static List<string> Arc(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 30; i++)
                    {
                        Steps++;
                        float la = F(r, -90f, 90f), lo = F(r, -180f, 180f), la0 = i % 3 == 0 ? 0f : F(r, -90f, 90f), lo0 = i % 3 == 0 ? 0f : F(r, -180f, 180f);
                        float a = RM_WeatherKernel.ArcDegrees(la, lo, la0, lo0);
                        double h = Haversine(la, lo, la0, lo0);
                        Check(!float.IsNaN(a) && a >= 0f && a <= 180f, $"arc {a} outside 0..180");
                        Check(Math.Abs(a - h) < 0.06, $"arc({la},{lo} | {la0},{lo0}) = {a}, haversine {h}");
                        float back = RM_WeatherKernel.ArcDegrees(la0, lo0, la, lo);
                        Check(Math.Abs(a - back) < 0.06, "arc not symmetric");
                        float wrapped = RM_WeatherKernel.ArcDegrees(la, lo + 360f, la0, lo0);
                        Check(Math.Abs(a - wrapped) < 0.06, "arc changed under a 360 degree longitude wrap");
                        float lo3 = F(r, -180f, 180f), la3 = F(r, -90f, 90f);
                        float ab = a, bc = RM_WeatherKernel.ArcDegrees(la0, lo0, la3, lo3), ac = RM_WeatherKernel.ArcDegrees(la, lo, la3, lo3);
                        Check(ac <= ab + bc + 0.15f, "triangle inequality broken");
                    }
                    Check(Math.Abs(RM_WeatherKernel.ArcDegrees(0f, 0f, 0f, 0f)) < 0.05f, "arc of a point to itself");
                    Check(Math.Abs(RM_WeatherKernel.ArcDegrees(0f, 180f, 0f, 0f) - 180f) < 0.05f, "antipode is not 180");
                    Check(Math.Abs(RM_WeatherKernel.ArcDegrees(0f, 90f, 0f, 0f) - 90f) < 0.05f && Math.Abs(RM_WeatherKernel.ArcDegrees(0f, -90f, 0f, 0f) - 90f) < 0.05f, "terminator meridians are not 90");
                    Check(Math.Abs(RM_WeatherKernel.ArcDegrees(90f, 33f, 0f, 0f) - 90f) < 0.05f, "a pole is not 90 from an equatorial substellar point");
                }
                catch (Exception e) { fails.Add($"arc seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Bands(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    // shipped Ash'karr geometry
                    float tmin = 63f, tmax = 117f, nmin = 117f;
                    foreach (float arc in new[] { RM_WeatherKernel.NoArc, 0f, 62.999f, 63f, 90f, 116.999f, 117f, 117.001f, 180f })
                    {
                        Steps++;
                        bool w = RM_WeatherKernel.InTerminatorBand(arc, tmin, tmax), d = RM_WeatherKernel.InNightsideBand(arc, nmin);
                        Check(!(w && d), $"arc {arc} is in the storm wall AND the dark side");
                        if (arc >= 63f) Check(w || d, $"arc {arc} >= 63 is in neither band (a gap past the wall's inner edge)");
                        if (arc < 63f) Check(!w && !d, $"arc {arc} below the wall is in a band");
                        if (arc == RM_WeatherKernel.NoArc) Check(!w && !d, "the invalid-tile sentinel is in a band");
                    }
                    Check(RM_WeatherKernel.InTerminatorBand(117f, tmin, tmax) && !RM_WeatherKernel.InNightsideBand(117f, nmin), "the shared edge 117 must belong to the wall only");
                    // any geometry that shares an edge (nightsideMin == terminatorMax) stays disjoint
                    float lo = F(r, 0f, 150f), hi = lo + F(r, 0f, 30f); float edge = hi;
                    for (int i = 0; i < 40; i++)
                    {
                        float a = i < 4 ? new[] { lo, hi, edge, edge + 0.001f }[i] : F(r, -1f, 181f);
                        Steps++;
                        bool w = RM_WeatherKernel.InTerminatorBand(a, lo, hi), d = RM_WeatherKernel.InNightsideBand(a, edge);
                        Check(!(w && d), $"shared-edge geometry ({lo}..{hi}, dark > {edge}) puts arc {a} in both bands");
                        if (w) InWall++; else if (d) InDark++; else Neither++;
                    }
                }
                catch (Exception e) { fails.Add($"bands seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Tint(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 40; i++)
                    {
                        Steps++;
                        float ch = i < 4 ? new[] { 0f, 1f, 0.87f, 0.75f }[i] : F(r, 0f, 1f);
                        float sat = F(r, 0.075f, 1f), br = F(r, 0.73f, 2f);
                        float t = RM_WeatherKernel.TintChannel(ch, sat, br, 0.075f);
                        Check(t >= 0f && t <= 1f, $"tint {t} outside 0..1");
                        Check(RM_WeatherKernel.TintChannel(ch, sat, br * 1.2f, 0.075f) >= t - 1e-6f, "tint fell as brightness rose");
                        // the whole slider range is never darker than vanilla, any channel (sky and overlay)
                        float skyV = (1f + (ch - 1f) * 0.075f) * 0.73f, ovV = (1f + (ch - 1f) * 0.025f) * 0.73f;
                        Check(t >= skyV - 1e-6f, $"sky channel {ch} at sat {sat} brightness {br} -> {t} is darker than vanilla {skyV}");
                        float to = RM_WeatherKernel.TintChannel(ch, F(r, 0.025f, 0.5f), br, 0.025f);
                        Check(to >= ovV - 1e-6f, $"overlay channel {ch} -> {to} is darker than vanilla {ovV}");
                        Check(RM_WeatherKernel.TintChannel(1f, sat, br, 0.075f) == Math.Min(1f, br) || br < 0.73f, "a white channel must only be scaled by brightness (and capped)");
                        // outside the floor the tint is exactly lerp(white, channel, saturation) x brightness, capped at white
                        double raw = (1.0 + (ch - 1.0) * sat) * br;
                        if (raw >= skyV) Check(Math.Abs(t - Math.Min(1.0, raw)) < 1e-5, $"tint({ch},{sat},{br}) = {t}, spec {Math.Min(1.0, raw)}");
                        // the shipped defaults are above vanilla without needing the floor
                        float sky = (1f + (ch - 1f) * 0.35f) * 1.15f;
                        Check(Math.Min(1f, sky) >= skyV - 1e-6f, "default sky darker than vanilla before the floor");
                        // how often the floor engages inside the slider range (informational)
                        CornerTotal++;
                        if ((1f + (ch - 1f) * sat) * br < skyV - 1e-6f) CornerDark++;
                    }
                }
                catch (Exception e) { fails.Add($"tint seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Forecast(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    int n = r.Next(0, 14); var w = new List<float>();
                    for (int i = 0; i < n; i++) { int k = r.Next(6); w.Add(k == 0 ? 0f : k == 1 ? -1f : k == 2 && w.Count > 0 ? w[r.Next(w.Count)] : F(r, 0.01f, 10f)); }
                    int top = r.Next(1, 4);
                    var got = RM_WeatherKernel.TopShares(w, top);
                    var pos = Enumerable.Range(0, n).Where(i => w[i] > 0f).ToList();
                    Check(got.Count == Math.Min(top, pos.Count), $"returned {got.Count} rows for {pos.Count} positive weights, top {top}");
                    float total = pos.Sum(i => w[i]); float sumPct = 0f;
                    for (int i = 0; i < got.Count; i++)
                    {
                        Check(w[got[i].Key] > 0f, "a zero/negative weight was forecast");
                        Check(Math.Abs(got[i].Value - w[got[i].Key] / total * 100f) < 1e-3f, "share is not weight / total of all positive weights");
                        if (i > 0) Check(got[i - 1].Value >= got[i].Value - 1e-6f, "shares not descending");
                        if (i > 0 && Math.Abs(got[i - 1].Value - got[i].Value) < 1e-9f) Check(got[i - 1].Key < got[i].Key, "ties not index-stable");
                        sumPct += got[i].Value;
                    }
                    Check(sumPct <= 100.001f, $"top shares sum to {sumPct}%");
                    foreach (int j in pos) if (!got.Any(g => g.Key == j)) foreach (var g in got) Check(w[j] <= w[g.Key] + 1e-6f, "an omitted weather outweighs a shown one");
                    var again = RM_WeatherKernel.TopShares(w, top);
                    Check(again.Select(g => g.Key).SequenceEqual(got.Select(g => g.Key)), "forecast not deterministic");
                }
                catch (Exception e) { fails.Add($"forecast seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("arc", () => Arc(N(2500), S(1))),
                ("bands", () => Bands(N(1500), S(1))),
                ("tint", () => Tint(N(2500), S(1))),
                ("forecast", () => Forecast(N(4000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails.Take(8)) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: wall {InWall}, dark {InDark}, neither {Neither}; slider-range tints the vanilla floor lifted (informational): {CornerDark} of {CornerTotal}");
                if (InWall == 0 || InDark == 0 || Neither == 0) { Console.WriteLine("FAIL weather fuzz never reached a band (blind)"); ok = false; }
            }
            Console.WriteLine($"weathersuite fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
