// Approach B for SeaShores: seeded fuzz over RM_SeaKernel against brute-force restatements written from the mod's own comments.
//   keys     terrain -> sea map: only terrain exactly one sea lays and no vanilla/shared water uses; the order seas are listed in is irrelevant
//   primary  the sea a land tile faces: most neighbours wins, ties on the lower ordinal defName; neighbour order is irrelevant
//   cell     which sea a map cell's water is (own terrain key, else the faced sea only if the cell carries its deep/shallow water)
//   band     the empty-band fallback (RUT_TheScald): never null, never mutates its inputs
//   heal     the frozen-world healer, exhaustive over its five inputs, with its safety properties
//   coast    distinct coast directions in first-seen order
//   gates    catch-table / shore-suppression / fish-roll predicates, exhaustively
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.SeaShores.Fuzz
{
    internal static class SeaShoresFuzz
    {
        public static long Cases, Steps, Ambiguous, Exclusive, Ties, EmptyFallbacks, Replaces, Heals;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private sealed class Sea { public string name; public override string ToString() { return name; } }
        private sealed class Terr { public string name; public override string ToString() { return name; } }

        private static string Fmt<T>(IEnumerable<T> xs) { return "[" + string.Join(",", xs.Select(x => x == null ? "-" : x.ToString())) + "]"; }

        // ═════════════ keys ═════════════
        private static List<string> Keys(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    var terr = Enumerable.Range(0, rng.Next(2, 9)).Select(i => new Terr { name = "T" + i }).ToList();
                    var seas = new List<Sea>();
                    int nSeas = rng.Next(0, 6);
                    var rows = new List<RM_SeaKernel.SeaTerrains<Sea, Terr>>();
                    for (int i = 0; i < nSeas; i++)
                    {
                        var sea = new Sea { name = "S" + i };
                        seas.Add(sea);
                        rows.Add(new RM_SeaKernel.SeaTerrains<Sea, Terr> { Sea = sea, Deep = rng.Next(8) == 0 ? null : terr[rng.Next(terr.Count)], Shallow = rng.Next(8) == 0 ? null : terr[rng.Next(terr.Count)] });
                    }
                    var seeded = terr.Where(t => rng.Next(4) == 0).ToList();   // vanilla / shared water that may never be keyed
                    var got = RM_SeaKernel.BuildTerrainKeys(rows, seeded);
                    Steps += rows.Count + 1;
                    // brute force: a terrain is keyed iff some sea lays it, it is not seeded, and every sea that lays it is the same sea
                    foreach (Terr t in terr)
                    {
                        var layers = rows.Where(r => r.Deep == t || r.Shallow == t).Select(r => r.Sea).Distinct().ToList();
                        bool want = layers.Count == 1 && !seeded.Contains(t);
                        Check(got.ContainsKey(t) == want, "terrain " + t + " keyed=" + got.ContainsKey(t) + " want " + want + " (laid by " + Fmt(layers) + ", seeded " + seeded.Contains(t) + ")");
                        if (want) { Check(got[t] == layers[0], "terrain " + t + " keyed to the wrong sea"); Exclusive++; }
                        if (layers.Count > 1) Ambiguous++;
                    }
                    Check(got.Keys.All(t => terr.Contains(t)), "a key that is no terrain");
                    // order independence
                    var shuffled = rows.OrderBy(_ => rng.Next()).ToList();
                    var got2 = RM_SeaKernel.BuildTerrainKeys(shuffled, seeded.OrderBy(_ => rng.Next()).ToList());
                    Check(got2.Count == got.Count && got.All(kv => got2.ContainsKey(kv.Key) && got2[kv.Key] == kv.Value), "the map depends on the order the seas are listed in");
                }
                catch (Exception ex) { fails.Add("keys seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ primary ═════════════
        private static List<string> Primary(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    string[] names = { "RM_Aaa", "RM_Aab", "RUT_Zed", "RM_aaa", "Z", "RM_Mid" };
                    var pool = names.Take(rng.Next(1, names.Length + 1)).Select(nm => new Sea { name = nm }).ToList();
                    int k = rng.Next(0, 9);
                    var nb = new List<Sea>();
                    for (int i = 0; i < k; i++) nb.Add(rng.Next(3) == 0 ? null : pool[rng.Next(pool.Count)]);
                    Steps += k;
                    Sea got = RM_SeaKernel.PrimarySea(nb, x => x.name);
                    if (nb.All(x => x == null)) { Check(got == null, "a sea from a tile with no sea neighbours"); continue; }
                    var counts = nb.Where(x => x != null).GroupBy(x => x).Select(g => new { sea = g.Key, c = g.Count() }).ToList();
                    int max = counts.Max(c => c.c);
                    var top = counts.Where(c => c.c == max).Select(c => c.sea).ToList();
                    Sea want = top.OrderBy(x => x.name, StringComparer.Ordinal).First();
                    if (top.Count > 1) Ties++;
                    Check(got == want, "faced " + got + " but the most-neighbours / lowest-ordinal sea is " + want + " from " + Fmt(nb));
                    for (int r = 0; r < 4; r++)
                        Check(RM_SeaKernel.PrimarySea(nb.OrderBy(_ => rng.Next()).ToList(), x => x.name) == want, "the faced sea depends on neighbour order");
                }
                catch (Exception ex) { fails.Add("primary seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ cell ═════════════
        private static List<string> Cell()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                var a = new Sea { name = "A" }; var b = new Sea { name = "B" };
                foreach (Sea keyed in new Sea[] { null, a }) foreach (Sea faced in new Sea[] { null, b, a })
                    foreach (bool known in new[] { false, true }) foreach (bool deep in new[] { false, true }) foreach (bool shallow in new[] { false, true })
                    {
                        Steps++;
                        Sea got = RM_SeaKernel.CellSea(keyed, faced, known, deep, shallow);
                        Sea want = known && keyed != null ? keyed : (faced == null || !known) ? null : (deep || shallow) ? faced : null;
                        Check(got == want, "CellSea(keyed " + keyed + ", faced " + faced + ", known " + known + ", deep " + deep + ", shallow " + shallow + ") = " + got + " want " + want);
                        Check(got == null || got == keyed || got == faced, "CellSea invented a sea");
                        Check(known || got == null, "a cell with no terrain was given a sea");
                        if (keyed == null && !deep && !shallow) Check(got == null, "an inland pond beside a coast was mistaken for the sea");
                    }
                // the lazy vanilla rung: only touched when every earlier rung is empty
                int touched = 0;
                var t1 = new Terr { name = "x" }; var t2 = new Terr { name = "y" }; var t3 = new Terr { name = "z" }; var v = new Terr { name = "vanilla" };
                Func<Terr> van = () => { touched++; return v; };
                Check(RM_SeaKernel.FirstNonNull(t1, t2, t3, van) == t1 && touched == 0, "extension field must win without touching vanilla");
                Check(RM_SeaKernel.FirstNonNull(null, t2, t3, van) == t2 && touched == 0, "ocean pair second");
                Check(RM_SeaKernel.FirstNonNull(null, null, t3, van) == t3 && touched == 0, "water pair third");
                Check(RM_SeaKernel.FirstNonNull(null, null, null, van) == v && touched == 1, "vanilla last, touched once");
                Steps += 4;
            }
            catch (Exception ex) { fails.Add("cell: " + ex.Message); }
            return fails;
        }

        // ═════════════ band ═════════════
        private static List<string> Band(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    List<int> Mk() { int r = rng.Next(4); return r == 0 ? null : r == 1 ? new List<int>() : Enumerable.Range(0, rng.Next(1, 4)).Select(_ => rng.Next(100)).ToList(); }
                    var pref = Mk(); var fall = Mk(); var empty = new List<int>();
                    var snapP = pref == null ? null : pref.ToList(); var snapF = fall == null ? null : fall.ToList();
                    var got = RM_SeaKernel.BandFor(pref, fall, empty);
                    Steps++;
                    Check(got != null, "BandFor returned null");
                    bool prefOk = pref != null && pref.Count > 0;
                    if (prefOk) Check(ReferenceEquals(got, pref), "a populated preferred band was not used");
                    else if (fall != null) { Check(ReferenceEquals(got, fall), "the other pair did not answer an empty band"); if (fall.Count > 0) EmptyFallbacks++; }
                    else Check(ReferenceEquals(got, empty), "both missing must give the shared empty list");
                    Check((pref == null ? snapP == null : pref.SequenceEqual(snapP)) && (fall == null ? snapF == null : fall.SequenceEqual(snapF)), "BandFor changed an input list");
                }
                catch (Exception ex) { fails.Add("band seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ heal ═════════════
        private static List<string> Heal()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                var bools = new[] { false, true };
                foreach (bool build in bools) foreach (bool faces in bools) foreach (bool vanillaCoast in bools) foreach (bool oceanNb in bools) foreach (bool anyCoast in bools)
                {
                    Steps++;
                    var got = RM_SeaKernel.Heal(build, faces, vanillaCoast, oceanNb, anyCoast);
                    bool stale = vanillaCoast && !oceanNb;
                    var want = !build || !faces ? RM_SeaKernel.HealAction.Skip
                        : (anyCoast && !stale) ? RM_SeaKernel.HealAction.Already
                        : stale ? RM_SeaKernel.HealAction.Replace : RM_SeaKernel.HealAction.Heal;
                    Check(got == want, "Heal(" + build + "," + faces + "," + vanillaCoast + "," + oceanNb + "," + anyCoast + ") = " + got + " want " + want);
                    if (got == RM_SeaKernel.HealAction.Replace) { Replaces++; Check(vanillaCoast && !oceanNb, "replaced a vanilla coast that has a real ocean neighbour"); }
                    if (got == RM_SeaKernel.HealAction.Heal) { Heals++; Check(!vanillaCoast || oceanNb, "healed a tile with a stale vanilla coast instead of replacing it"); Check(!anyCoast || vanillaCoast && oceanNb, "added a second coast to a tile that already had one"); }
                    if (!build || !faces) Check(got == RM_SeaKernel.HealAction.Skip, "touched a tile that is not buildable land facing a sea");
                }
            }
            catch (Exception ex) { fails.Add("heal: " + ex.Message); }
            return fails;
        }

        // ═════════════ coast ═════════════
        private static List<string> Coast(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    int k = rng.Next(0, 9);
                    var dirs = Enumerable.Range(0, k).Select(_ => rng.Next(4)).ToList();
                    var flags = Enumerable.Range(0, k).Select(_ => rng.Next(3) != 0).ToList();
                    Steps++;
                    var got = RM_SeaKernel.CoastDirections(dirs, flags);
                    var want = new List<int>();
                    for (int i = 0; i < k; i++) if (flags[i] && !want.Contains(dirs[i])) want.Add(dirs[i]);
                    Check(got.SequenceEqual(want), "coast directions " + Fmt(got) + " want " + Fmt(want) + " from " + Fmt(dirs) + " / " + Fmt(flags));
                    Check(got.Distinct().Count() == got.Count && got.Count <= 4, "duplicate or surplus direction");
                }
                catch (Exception ex) { fails.Add("coast seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ gates ═════════════
        private static List<string> Gates()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                var bools = new[] { false, true };
                foreach (bool a in bools) foreach (bool b in bools) foreach (bool c in bools) foreach (bool d in bools) foreach (bool e in bools)
                {
                    Steps++;
                    Check(RM_SeaKernel.CatchTableApplies(a, b, c, d, e) == (a && b && c && d && e), "CatchTableApplies " + a + b + c + d + e);
                }
                foreach (bool setting in bools) foreach (bool known in bools) foreach (bool gen in bools)
                {
                    Steps++;
                    bool got = RM_SeaKernel.ShoreSuppressed(setting, known, gen);
                    Check(got == (!setting || (known && !gen)), "ShoreSuppressed " + setting + known + gen);
                    if (!setting) Check(got, "the master switch off must always suppress");
                    if (setting && !known) Check(!got, "an unknown sea (no extension) must keep vanilla's shore, not suppress it");
                }
                Check(RM_SeaKernel.RollShouldHaveFish(false) && !RM_SeaKernel.RollShouldHaveFish(true), "fish roll belongs to the sea only when the land biome has no fish table");
                Steps++;
            }
            catch (Exception ex) { fails.Add("gates: " + ex.Message); }
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
                ("keys", () => Keys(N(8000), S(1))),
                ("primary", () => Primary(N(8000), S(1))),
                ("cell", () => Cell()),
                ("band", () => Band(N(3000), S(1))),
                ("heal", () => Heal()),
                ("coast", () => Coast(N(3000), S(1))),
                ("gates", () => Gates()),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"reached: exclusive terrains {Exclusive}, ambiguous terrains {Ambiguous}, tied faced seas {Ties}, empty-band fallbacks {EmptyFallbacks}, heals {Heals}, replaces {Replaces}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Exclusive == 0 || Ambiguous == 0 || Ties == 0 || EmptyFallbacks == 0 || Heals == 0 || Replaces == 0)) { Console.WriteLine("FAIL fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"seashores fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
