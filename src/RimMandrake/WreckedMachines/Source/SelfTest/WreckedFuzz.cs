// Approach B for WreckedMachines: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WreckedMachinesKernel.cs):
//   ladder    the capability ratios for any saved or hand-edited setting: ordered wrecked <= kludged <= refurbished, inside the slider ranges,
//             always below the original's 1.0, in-range input untouched
//   place     where an upper grade may be built (a lower grade of ITS OWN line underneath, reinstalls free, wrecks free) against a random cell
//   emanator  the soothe stage per grade and the strongest-in-range pick, never above the top stage, inert when wrecked
//   scale     power output (producers only, never above the original), emanator mood, material counts and research cost under their sliders
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL: ratios 0.001 / 0.2 / 0.75 are owner-ruled defaults;
// slider ranges (wrecked 0..0.05, kludged 0.05..0.6, refurbished 0.3..0.95) are the shipped UI.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.WreckedMachines;

namespace RimMandrake.WreckedMachines.SelfTest
{
    internal static class WreckedFuzz
    {
        public static long Cases, Steps, Allowed, Refused, Inverted, Producers;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        private static List<string> Ladder(int cases, int seed0)
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
                        // anywhere a config can land, including hand-edited nonsense
                        float w = i % 4 == 0 ? F(r, 0f, 0.05f) : F(r, -1f, 3f), k = i % 4 == 0 ? F(r, 0.05f, 0.6f) : F(r, -1f, 3f), rf = i % 4 == 0 ? F(r, 0.3f, 0.95f) : F(r, -1f, 3f);
                        var l = RM_WreckedMachinesKernel.Normalize(w, k, rf);
                        Check(l.wrecked >= 0f && l.wrecked <= l.kludged && l.kludged <= l.refurbished, $"ladder not ordered: {l.wrecked} {l.kludged} {l.refurbished} from {w} {k} {rf}");
                        Check(l.refurbished < 1f && l.refurbished <= 0.95f, $"refurbished {l.refurbished} reaches the original");
                        Check(l.kludged <= 0.6f && l.wrecked <= 0.05f, "a ratio left its slider range");
                        Check(RM_WreckedMachinesKernel.RatioFor(3, l) == 1f, "the original is not exactly 1");
                        for (int g = 0; g < 3; g++) Check(RM_WreckedMachinesKernel.RatioFor(g, l) <= RM_WreckedMachinesKernel.RatioFor(g + 1, l), $"grade {g} is above grade {g + 1}");
                        Check(RM_WreckedMachinesKernel.RatioFor(2, l) < RM_WreckedMachinesKernel.RatioFor(3, l), "refurbished reaches the original");
                        Check(RM_WreckedMachinesKernel.RatioFor(0, l) == l.wrecked && RM_WreckedMachinesKernel.RatioFor(1, l) == l.kludged && RM_WreckedMachinesKernel.RatioFor(2, l) == l.refurbished, "RatioFor mixes grades");
                        bool inRange = w >= 0 && w <= 0.05f && k >= 0.05f && k <= 0.6f && rf >= 0.3f && rf <= 0.95f && k <= rf && w <= k;
                        if (inRange) Check(l.wrecked == w && l.kludged == k && l.refurbished == rf, "an in-range, ordered config was altered");
                        else if (k > rf && k <= 0.6f && rf >= 0.3f && rf <= 0.95f) Inverted++;
                    }
                    var d = RM_WreckedMachinesKernel.Normalize(0.001f, 0.2f, 0.75f);
                    Check(d.wrecked == 0.001f && d.kludged == 0.2f && d.refurbished == 0.75f, "the shipped defaults are altered by Normalize");
                }
                catch (Exception e) { fails.Add($"ladder seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Place(int cases, int seed0)
        {
            var fails = new List<string>();
            string[] lines = { "smelter", "cell", "emanator" };
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 30; i++)
                    {
                        Steps++;
                        bool require = r.Next(5) != 0, reinstall = r.Next(6) == 0, hasExt = r.Next(8) != 0; int grade = r.Next(4); string line = lines[r.Next(3)];
                        int n = r.Next(0, 5); var ol = new List<string>(); var og = new List<int>();
                        for (int j = 0; j < n; j++) { ol.Add(lines[r.Next(3)]); og.Add(r.Next(4)); }
                        bool got = RM_WreckedMachinesKernel.AllowsPlacing(require, reinstall, hasExt, grade, line, ol, og);
                        bool lower = false; for (int j = 0; j < n; j++) if (ol[j] == line && og[j] < grade) lower = true;
                        bool want = !require || reinstall || !hasExt || grade == 0 || lower;
                        Check(got == want, $"AllowsPlacing(req {require}, reinstall {reinstall}, ext {hasExt}, grade {grade}, line {line}, cell {string.Join(",", ol.Select((x, q) => x + ":" + og[q]))}) = {got}, spec {want}");
                        if (got) Allowed++; else Refused++;
                        if (require && !reinstall && hasExt && grade > 0 && got) Check(lower, "an upper grade went on open ground / over another line / over an equal or higher grade");
                        if (require && !reinstall && hasExt && grade > 0 && n == 0) Check(!got, "an upper grade was allowed on an empty cell");
                        // a lower grade of ANOTHER line never counts
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { "other" }, new[] { 0 }), "a lower grade of another line allowed the build");
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { line }, new[] { grade }), "the same grade underneath allowed the build");
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { line }, new[] { 3 }), "a higher grade underneath allowed the build");
                    }
                }
                catch (Exception e) { fails.Add($"place seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Emanator(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int sc = 1; sc <= 4; sc++)
                    {
                        Steps++;
                        Check(RM_WreckedMachinesKernel.EmanatorStage(0, sc) == -1, "a wrecked emanator soothes");
                        for (int g = 1; g <= 3; g++)
                        {
                            int st = RM_WreckedMachinesKernel.EmanatorStage(g, sc);
                            Check(st >= 0 && st <= sc - 1, $"stage {st} outside 0..{sc - 1} for grade {g}");
                            Check(st == Math.Min(g - 1, sc - 1), "stage is not min(grade - 1, top)");
                            if (g > 1) Check(st >= RM_WreckedMachinesKernel.EmanatorStage(g - 1, sc), "a higher grade soothes less");
                        }
                    }
                    // strongest in range wins: a list of nearby grades, the best stage is the max of the stages
                    int n = r.Next(0, 6); var gs = new List<int>(); for (int i = 0; i < n; i++) gs.Add(r.Next(4));
                    int best = -1; foreach (int g in gs) best = Math.Max(best, RM_WreckedMachinesKernel.EmanatorStage(g, 2));
                    Check(best == (gs.Any(g => g > 0) ? Math.Min(gs.Max() - 1, 1) : -1), "strongest nearby emanator is not the highest grade's stage");
                    Check(RM_WreckedMachinesKernel.EmanatorStage(3, 2) == 1, "the original soothes beyond the top stage");
                }
                catch (Exception e) { fails.Add($"emanator seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Scale(int cases, int seed0)
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
                        float orig = i == 0 ? 0f : i % 3 == 0 ? F(r, 0f, 500f) : -F(r, 1f, 6000f);   // producers are negative draws
                        var l = RM_WreckedMachinesKernel.Normalize(F(r, 0f, 0.05f), F(r, 0.05f, 0.6f), F(r, 0.3f, 0.95f));
                        float? prev = null;
                        for (int g = 0; g < 4; g++)
                        {
                            float? o = RM_WreckedMachinesKernel.ScaledPowerOutput(orig, RM_WreckedMachinesKernel.RatioFor(g, l));
                            if (orig >= 0f) { Check(o == null, "a consumer's draw was rewritten"); continue; }
                            Producers++;
                            Check(o != null, "a producer was left unscaled");
                            Check(o.Value <= 0f && o.Value >= orig - 1e-3f, $"salvaged output {o} outside [original {orig}, 0]: a bodge out-produces the original");
                            Check(Math.Abs(o.Value - orig * RM_WreckedMachinesKernel.RatioFor(g, l)) <= 1e-3f + Math.Abs(orig) * 1e-5f, $"salvaged output {o} is not original {orig} x ratio {RM_WreckedMachinesKernel.RatioFor(g, l)}");
                            if (g < 3) Check(Math.Abs(o.Value) <= Math.Abs(orig) * 0.951f + 1e-3f, "a salvaged grade matches or nears the original");
                            if (prev != null) Check(Math.Abs(o.Value) >= Math.Abs(prev.Value) - 1e-3f, "a higher grade produces less");
                            prev = o;
                        }
                        float vm = F(r, 0.5f, 20f);
                        Check(RM_WreckedMachinesKernel.EmanatorMood(vm, l.kludged) < RM_WreckedMachinesKernel.EmanatorMood(vm, l.refurbished) + 1e-6f, "kludged emanator out-soothes refurbished");
                        Check(RM_WreckedMachinesKernel.EmanatorMood(vm, l.refurbished) < vm, "a refurbished emanator matches or beats the vanilla one");
                        int bc = r.Next(1, 200); float fac = F(r, 0.25f, 4f);
                        int sc2 = RM_WreckedMachinesKernel.ScaledCount(bc, fac);
                        Check(sc2 >= 1, "a material count fell below one");
                        Check(Math.Abs(sc2 - bc * (double)fac) <= 0.5 + 1e-4 || bc * fac < 1, $"count {bc} x {fac} = {bc * fac} became {sc2}");
                        Check(RM_WreckedMachinesKernel.ScaledCount(bc, 1f) == bc, "factor 1 changed a count");
                        Check(RM_WreckedMachinesKernel.ScaledResearch(2000f, 1f) == 2000f && RM_WreckedMachinesKernel.ScaledResearch(2000f, 0.25f) == 500f && RM_WreckedMachinesKernel.ScaledResearch(0.5f, 0.25f) == 1f, "research cost arithmetic");
                    }
                }
                catch (Exception e) { fails.Add($"scale seed {seed}: {e.Message}"); }
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
                ("ladder", () => Ladder(N(3000), S(1))),
                ("place", () => Place(N(4000), S(1))),
                ("emanator", () => Emanator(N(2000), S(1))),
                ("scale", () => Scale(N(3000), S(1))),
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
                Console.WriteLine($"reached: placements allowed {Allowed}, refused {Refused}, producers scaled {Producers}, inverted slider pairs repaired {Inverted}");
                if (Allowed == 0 || Refused == 0 || Producers == 0 || Inverted == 0) { Console.WriteLine("FAIL wrecked-machines fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"wreckedmachines fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
