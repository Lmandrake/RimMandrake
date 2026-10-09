// Approach B for TitanicCreatures: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_TitanicKernel.cs), each family checked
// against an independent restatement of the ruled rules and against cross-function safety properties:
//   tier   body-size ladder, force-in / force-out, DefQualifies vs TierFor agreement, Large Pawns footprint projection
//   yield  sub-linear butcher factor: bounds, monotone in size, total yield never shrinks as the beast grows
//   crush  the crush table decision, wake damage monotone in tier, roof rule, T3 outright-destroy only for buildings
//   pool   T3 corpse-site pool: daily spoilage and per-session harvest conserve units and always terminate
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL numbers (tier floors 4/8/20, crush 20/60,
// spoilage 0.15/0.08, yield floor 0.15) are BENCH-draft tuning; the properties here hold for any value in the settings sliders.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.TitanicCreatures;

namespace RimMandrake.TitanicCreatures.SelfTest
{
    internal static class TitanicFuzz
    {
        public static long Cases, Steps, Tiered, Forced, Pools, Destroyed;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        private static void Ladder(Random r, out float t1, out float t2, out float t3)
        {
            t1 = F(r, 0.5f, 10f); t2 = t1 + F(r, 0.5f, 12f); t3 = t2 + F(r, 0.5f, 30f);
        }

        // independent spec: count the thresholds met
        private static int SpecTier(float b, float t1, float t2, float t3, int force)
        {
            if (force == -1) return 0;
            int n = (b >= t1 ? 1 : 0) + (b >= t2 ? 1 : 0) + (b >= t3 ? 1 : 0);
            return n == 0 && force == 1 ? 1 : n;
        }

        private static List<string> Tier(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float t1, t2, t3; Ladder(r, out t1, out t2, out t3);
                    Check(RM_TitanicKernel.ThresholdsValid(t1, t2, t3), "generated ladder not valid");
                    Check(!RM_TitanicKernel.ThresholdsValid(t2, t1, t3) && !RM_TitanicKernel.ThresholdsValid(0f, t2, t3) && !RM_TitanicKernel.ThresholdsValid(t1, t2, t2), "ThresholdsValid accepts a broken ladder");
                    int prev = 0; float prevB = -1f;
                    var sizes = new List<float> { 0f, t1, t2, t3, t1 - 0.001f, t2 - 0.001f, t3 - 0.001f, t3 + 100f };
                    for (int i = 0; i < 12; i++) sizes.Add(F(r, 0f, t3 * 1.5f));
                    sizes.Sort();
                    foreach (float b in sizes)
                    {
                        Steps++;
                        foreach (int force in new[] { -1, 0, 1 })
                        {
                            int got = RM_TitanicKernel.TierFor(b, t1, t2, t3, force);
                            Check(got == SpecTier(b, t1, t2, t3, force), $"TierFor({b},{t1},{t2},{t3},force {force}) = {got}, spec {SpecTier(b, t1, t2, t3, force)}");
                            Check(got >= 0 && got <= 3, "tier out of range");
                            if (force == 0 && b >= t1) Tiered++;
                            if (force != 0) Forced++;
                            // agreement with the def-level test the comp auto-attach uses: a pawn that can ever be tiered must have the comp
                            bool q = RM_TitanicKernel.DefQualifies(b, t1, force);
                            Check(!(got != 0 && !q), $"pawn tiered {got} at body {b} (force {force}) but DefQualifies false: it would never get the wake comp");
                            if (force == 0) Check(q == (got != 0), "auto: DefQualifies and TierFor disagree");
                            if (force == -1) Check(!q, "force-out race still qualifies for the wake comp");
                            if (force == 1) Check(q, "force-in race does not qualify");
                        }
                        // monotone in size (auto and force-in)
                        int a0 = RM_TitanicKernel.TierFor(b, t1, t2, t3, 0);
                        Check(a0 >= prev, $"tier fell as body size grew ({prevB} -> {b})");
                        prev = a0; prevB = b;
                        // footprint: never smaller than 1, never above Large Pawns' ceiling of 4, monotone in tier, force-out 1
                        int fp = RM_TitanicKernel.OverrideFootprint(b, t1, t2, t3, 0);
                        Check(fp >= 2 && fp <= 4, "auto footprint out of 2..4: " + fp);
                        Check(RM_TitanicKernel.OverrideFootprint(b, t1, t2, t3, -1) == 1, "force-out footprint not 1");
                        int fi = RM_TitanicKernel.OverrideFootprint(b, t1, t2, t3, 1);
                        Check(fi >= 2 && fi <= 4, "force-in footprint out of 2..4");
                        // the footprint tier must agree with the runtime tier wherever the pawn is tiered at all
                        int tierRun = RM_TitanicKernel.TierFor(b, t1, t2, t3, 1);
                        Check(RM_TitanicKernel.FootprintSize(tierRun) == fi, $"force-in footprint {fi} disagrees with runtime tier {tierRun} at body {b}: Large Pawns would draw a different size than the wake covers");
                    }
                    // ruled footprints: T1 2x2, T2 3x3, T3 4x4 (Large Pawns' hard ceiling); an untiered size never reaches Large Pawns
                    Check(RM_TitanicKernel.FootprintSize(1) == 2 && RM_TitanicKernel.FootprintSize(2) == 3 && RM_TitanicKernel.FootprintSize(3) == 4, "footprints are not 2/3/4");
                    // TITAN_WAKE_FIXES_1 (B3.18 / C3.4): base and life-stage factor fuzzed independently. Any pawn whose CURRENT size
                    // (base x a stage factor no larger than the race's max) is tiered must belong to a race that qualifies for the comp.
                    for (int k = 0; k < 16; k++)
                    {
                        float bse = F(r, 0.1f, t3 * 1.2f), maxF = r.Next(4) == 0 ? F(r, 0.1f, 1f) : F(r, 1f, 4f);
                        float stage = F(r, 0.05f, Math.Max(maxF, 1f));
                        if (stage > maxF && maxF >= 1f) stage = maxF;
                        if (maxF < 1f) stage = Math.Min(stage, 1f);
                        int now = RM_TitanicKernel.TierFor(bse * stage, t1, t2, t3, 0);
                        bool qual = RM_TitanicKernel.DefQualifies(bse, maxF, t1, 0);
                        Check(!(now != 0 && !qual), $"life stage x{stage} (max {maxF}) on base {bse} is tier {now} but the race does not qualify for the wake comp");
                        Check(qual == (bse * Math.Max(maxF, 1f) >= t1), "DefQualifies(base, factor) is not base x max(factor, 1) >= T1");
                        Check(RM_TitanicKernel.DefQualifies(bse, maxF, t1, -1) == false && RM_TitanicKernel.DefQualifies(bse, maxF, t1, 1), "force ignored with a life-stage factor");
                    }
                    // HUGETHINGS_SETTINGS_HARDENING_1 (B3.19 / C3.6 / D3.3): hostile Scribe values (NaN, +-inf, negative, zero, huge) end sane.
                    Check(!RM_TitanicKernel.ThresholdsValid(t1, t2, float.PositiveInfinity) && !RM_TitanicKernel.ThresholdsValid(float.NaN, t2, t3)
                          && !RM_TitanicKernel.ThresholdsValid(t1, float.PositiveInfinity, float.PositiveInfinity), "ThresholdsValid accepts an infinite or NaN rung");
                    foreach (float bad in new[] { float.NaN, float.PositiveInfinity, float.NegativeInfinity, -F(r, 0f, 1e6f), 0f, F(r, 0f, 1e9f) })
                    {
                        float lo = F(r, 0f, 5f), hi = lo + F(r, 0.01f, 50f), dflt = F(r, lo, hi);
                        float got = RM_TitanicKernel.SaneSetting(bad, lo, hi, dflt);
                        Check(RM_TitanicKernel.Finite(got) && got >= lo && got <= hi, $"SaneSetting({bad}) = {got} outside [{lo},{hi}]");
                        if (!RM_TitanicKernel.Finite(bad)) Check(got == dflt, $"non-finite {bad} did not fall back to the default");
                        Check(RM_TitanicKernel.Finite(RM_TitanicKernel.SaneSetting(bad, lo, hi, float.NaN)), "a NaN default escaped");
                        int ib = float.IsNaN(bad) ? 0 : (int)Math.Max(int.MinValue / 2, Math.Min(int.MaxValue / 2, bad));
                        int ig = RM_TitanicKernel.SaneSetting(ib, 1, 50);
                        Check(ig >= 1 && ig <= 50, $"int SaneSetting({ib}) = {ig}");
                    }
                }
                catch (Exception e) { fails.Add($"tier seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Yield(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    float t1, t2, t3; Ladder(r, out t1, out t2, out t3);
                    float minF = F(r, 0.05f, 1f);
                    foreach (int tier in new[] { 1, 2 })
                    {
                        float floor = RM_TitanicKernel.YieldFloor(tier, t1, t2);
                        Check(floor == (tier == 1 ? t1 : t2), "YieldFloor wrong");
                        float prevF = 2f, prevTotal = 0f, prevB = 0f;
                        for (int i = 0; i < 40; i++)
                        {
                            Steps++;
                            float b = floor + i * (t3 - floor) / 40f;
                            float f = RM_TitanicKernel.SubLinearFactor(b, floor, minF);
                            Check(!float.IsNaN(f) && f >= minF - 1e-6f && f <= 1f + 1e-6f, $"factor {f} outside [{minF},1] at body {b}");
                            Check(f <= prevF + 1e-6f, $"factor rose with size ({prevB} -> {b})");
                            double want = Math.Min(1.0, Math.Max(minF, Math.Sqrt(floor / b)));
                            Check(Math.Abs(f - want) < 1e-5, $"factor {f} is not clamp(sqrt(floor/size)) = {want} at body {b} (the curve is sqrt, not linear)");
                            double total = b * f;
                            Check(total >= prevTotal - 1e-4, $"total yield fell as the beast grew ({prevB} -> {b}): sub-linear must still be increasing");
                            Check(f * b <= b + 1e-4, "yield above vanilla");
                            prevF = f; prevTotal = (float)total; prevB = b;
                        }
                        Check(Math.Abs(RM_TitanicKernel.SubLinearFactor(floor, floor, minF) - 1f) < 1e-6f, "exactly at the floor the factor must be 1");
                        // a pawn below its floor (a lifestage swell the other way) must not amplify
                        float lo = RM_TitanicKernel.SubLinearFactor(floor * 0.1f, floor, minF);
                        Check(Math.Abs(lo - 1f) < 1e-6f, "below the floor the factor must be 1, got " + lo);
                    }
                }
                catch (Exception e) { fails.Add($"yield seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Crush(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int rule = 0; rule < 12; rule++)
                    {
                        bool crushable = r.Next(2) == 0; int minTier = r.Next(4);   // 0 is a malformed row; an untiered pawn must still crush nothing
                        bool wasAllowed = false;
                        for (int tier = 0; tier <= 3; tier++)
                        {
                            Steps++;
                            bool ok = RM_TitanicKernel.CrushAllowed(tier, crushable, minTier);
                            Check(ok == (tier != 0 && crushable && tier >= minTier), $"CrushAllowed({tier},{crushable},{minTier}) = {ok}");
                            Check(!(wasAllowed && !ok), "a bigger titan crushes less than a smaller one for the same row");
                            wasAllowed = ok;
                            if (tier == 0) Check(!ok, "an untiered pawn crushed something");
                        }
                    }
                    float mult = F(r, 0.25f, 3f);
                    float prev = 0f;
                    for (int tier = 1; tier <= 3; tier++)
                    {
                        float d = RM_TitanicKernel.CrushDamage(tier, mult);
                        Check(d > 0f, "crush damage not positive");
                        Check(d >= prev, $"T{tier} deals {d} < {prev} dealt by T{tier - 1}: a bigger titan hits softer than a smaller one");
                        prev = d;
                    }
                    for (int tier = 0; tier <= 3; tier++)
                    {
                        foreach (bool building in new[] { false, true })
                        {
                            bool d = RM_TitanicKernel.DestroysOutright(tier, building);
                            Check(d == (tier == 3 && building), "DestroysOutright wrong");
                            if (d) Destroyed++;
                        }
                        foreach (bool has in new[] { false, true })
                            foreach (bool thick in new[] { false, true })
                            {
                                bool holes = RM_TitanicKernel.HolesRoof(tier, has, thick);
                                Check(holes == (tier >= 2 && has && !thick), "HolesRoof wrong");
                                Check(!(thick && holes), "a thick roof (natural rock) was holed");
                                Check(!(!has && holes), "holed a roof that is not there");
                            }
                        Check(!RM_TitanicKernel.LeavesFilth(0, true), "an untiered pawn left rubble");
                        Check(RM_TitanicKernel.LeavesFilth(tier, true) == (tier >= 1), "LeavesFilth(true) wrong");
                        Check(!RM_TitanicKernel.LeavesFilth(tier, false), "rubble without a roll");
                    }
                    // TITAN_WAKE_FIXES_1 (B3.6): a multi-cell thing listed in every cell of the footprint is struck once per step.
                    {
                        int things = r.Next(1, 8), cellsN = r.Next(1, 17);
                        var objs = Enumerable.Range(0, things).Select(_ => new object()).ToList();
                        var cells = new List<List<object>>();
                        var want = new List<object>();
                        for (int ci = 0; ci < cellsN; ci++)
                        {
                            var cell = new List<object>();
                            foreach (object o in objs) if (r.Next(3) == 0) { cell.Add(o); if (!want.Contains(o)) want.Add(o); }
                            cells.Add(cell);
                        }
                        cells.Add(new List<object>(objs.Count > 0 ? new[] { objs[0], objs[0] } : new object[0]));
                        if (objs.Count > 0 && !want.Contains(objs[0])) want.Add(objs[0]);
                        List<object> got = RM_TitanicKernel.UniqueInOrder<object>(cells);
                        Check(got.Count == got.Distinct().Count(), "a multi-cell thing was struck more than once in one step");
                        Check(got.SequenceEqual(want), "UniqueInOrder lost a thing or changed first-seen order");
                    }
                }
                catch (Exception e) { fails.Add($"crush seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Pool(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Pools++;
                try
                {
                    int meat0 = r.Next(0, 4000), leather0 = r.Next(0, 1500);
                    float meatRate = F(r, 0.02f, 0.5f), leatherRate = F(r, 0.02f, 0.5f);
                    int meatSess = r.Next(5, 101), leatherSess = r.Next(2, 51);
                    int meat = meat0, leather = leather0; long harvestedM = 0, harvestedL = 0, lostM = 0, lostL = 0;
                    int days = 0;
                    while ((meat > 0 || leather > 0) && days < 5000)
                    {
                        Steps++;
                        // visits during the day, then the day's spoilage
                        int visits = r.Next(0, 4);
                        for (int v = 0; v < visits && (meat > 0 || leather > 0); v++)
                        {
                            int tm = RM_TitanicKernel.HarvestTake(meat, meatSess), tl = RM_TitanicKernel.HarvestTake(leather, leatherSess);
                            Check(tm >= 0 && tm <= meat && tm <= meatSess, "meat take out of range");
                            Check(tl >= 0 && tl <= leather && tl <= leatherSess, "leather take out of range");
                            Check(meat == 0 || tm > 0, "a session got no meat from a non-empty pool");
                            meat -= tm; leather -= tl; harvestedM += tm; harvestedL += tl;
                        }
                        int lm = RM_TitanicKernel.SpoilLoss(meat, meatRate), ll = RM_TitanicKernel.SpoilLoss(leather, leatherRate);
                        Check(lm >= 0 && lm <= meat && ll >= 0 && ll <= leather, "spoilage lost more than is there");
                        Check(meat == 0 || lm >= 1, "spoilage stalled with meat left (the site would never clear)");
                        Check(leather == 0 || ll >= 1, "spoilage stalled with leather left");
                        Check(lm <= Math.Ceiling(meat * (double)meatRate) + 1, "spoilage far above the configured fraction");
                        meat -= lm; leather -= ll; lostM += lm; lostL += ll;
                        Check(meat >= 0 && leather >= 0, "pool went negative");
                        days++;
                    }
                    Check(meat == 0 && leather == 0, "pool did not drain within 5000 days at rates >= 2%");
                    Check(harvestedM + lostM == meat0 && harvestedL + lostL == leather0, "units not conserved (harvested + spoiled != total)");
                    Check(RM_TitanicKernel.SpoilLoss(0, 0.5f) == 0 && RM_TitanicKernel.SpoilLoss(-3, 0.5f) == 0, "spoilage of an empty pool");
                    Check(RM_TitanicKernel.SpoilLoss(10, 0f) == 0, "zero spoilage rate lost units");
                    foreach (float wild in new[] { 1f, 1.5f, 7f }) Check(RM_TitanicKernel.SpoilLoss(10, wild) == 10, $"spoilage rate {wild} must lose exactly the whole pool, got {RM_TitanicKernel.SpoilLoss(10, wild)}");
                    Check(RM_TitanicKernel.HarvestTake(10, 0) == 0 && RM_TitanicKernel.HarvestTake(10, -5) == 0, "non-positive session size harvested");
                }
                catch (Exception e) { fails.Add($"pool seed {seed}: {e.Message}"); }
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
                ("tier", () => Tier(N(3000), S(1))),
                ("yield", () => Yield(N(2000), S(1))),
                ("crush", () => Crush(N(2000), S(1))),
                ("pool", () => Pool(N(1500), S(1))),
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
                Console.WriteLine($"reached: auto-tiered {Tiered}, forced {Forced}, pools {Pools}, outright destroys {Destroyed}");
                if (Tiered == 0 || Forced == 0 || Pools == 0 || Destroyed == 0) { Console.WriteLine("FAIL titanic fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"titaniccreatures fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
