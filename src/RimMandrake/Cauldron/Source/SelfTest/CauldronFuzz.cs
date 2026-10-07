// Approach B for Cauldron: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   vent    a vent through weather changes, drinking and time (falter / bloom, blowout memory, suppression, silence and
//           recovery, habitat), the exposure weight, generation counts and the stable/leaking mix, and which vent a vexxiss drinks
//   yield   the growth-scaled metal yield, assay grade and fleck band, the bloom's metal-load dose and eligibility, dewfall beads
//   prints  the vexxiss print ledger (order, cap, expiry, newest-per-cell, grid clearing) and the fire-warden / water-letter choices
//   units   exhaustive truth tables for the small decisions
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Cauldron.SelfTest
{
    internal static class CauldronFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double tol = 1e-5) { return Math.Abs(a - b) <= tol; }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        internal struct Act
        {
            public int kind, a, b, c;
            public string[] names;
            public override string ToString() { return names[kind] + "(" + a + "," + b + "," + c + ")"; }
        }

        private static List<string> RunFamily(string name, int n, int baseSeed, Func<int, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var acts = gen(seed);
                Cases++;
                string err = run(seed, acts);
                if (err == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add($"{name} seed {seed}: {run(seed, min)} | {string.Join(" ", min)}");
            }
            return fails;
        }

        // ════════════════════════ vent ════════════════════════
        private static readonly string[] VentNames = { "Tick", "Weather", "Drink", "ToggleWeather", "Habitat", "Exposure", "Generate", "Pick" };
        public static long Blowouts, Silences, Falters, Recoveries, ExposureProbes, Generations, Picks, LazyReachSaved;

        private static readonly float[] Lerps = { 0f, 0.3f, 0.99999f, 0.9999995f, 1f, 1.0000002f };
        private static readonly double[] SpecLerpIsOne = { 0, 0, 0, 1, 1, 1 };

        private static string RunVent(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            var rng = new Random(seed ^ 0x6a09e667);
            const int Bloom = 7, Rain = 1, Clear = 2;
            int[] rowIds = r.Next(3) == 0 ? new int[0] : new[] { Rain, -1, Bloom }.Take(r.Next(1, 4)).ToArray();
            float[] rowOuts = rowIds.Select(_ => r.Next(0, 9) * 0.25f).ToArray();
            float falterOut = new[] { 0f, 0.1f, 0.5f }[r.Next(3)], defaultOut = new[] { 0.5f, 1f, 2f }[r.Next(3)];
            int recoverTicks = new[] { 0, 1000, 60000 }[r.Next(3)], recentWindow = new[] { 100000, 600000 }[r.Next(2)];
            float decay = new[] { 0f, 0.9375f, 0.234375f, 0.05859375f }[r.Next(4)];
            float silenceDays = new[] { 0.5f, 4f, 10f }[r.Next(3)];
            float needed = new[] { 4f, 8f, 6000f }[r.Next(3)];
            var temperament = r.Next(2) == 0 ? RM_VentTemperament.Stable : RM_VentTemperament.Leaking;
            bool weatherOn = true, hasExt = true;
            int cur = Clear; float lerp = 1f; int lerpIdx = 4; int now = r.Next(0, 5) * 250;
            // vent state (kernel driven)
            int silencedUntil = -1, lastBlow = RM_VentKernel.NeverBlew; float supp = 0f; bool seen = false;
            // spec ledger
            double sSupp = 0; long sSilencedUntil = -1; int sEpisodes = 0; long sLastBlow = RM_VentKernel.NeverBlew; bool sInEpisode = false;
            int step = 0; string err = null;
            Func<bool> falter = () => RM_VentKernel.Faltering(weatherOn, true, hasExt, true, cur == Bloom, lerp);
            Func<bool> bloom = () => RM_VentKernel.Blooming(weatherOn, true, hasExt, true, cur == Bloom, lerp);
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0: // Tick(n * 250)
                            for (int k = 0; k < 1 + a.a % 30; k++)
                            {
                                now += 250;
                                bool bl = bloom(), fa = !bl && falter();
                                RM_VentKernel.BloomTick(ref seen, ref lastBlow, bl, fa, now);
                                // spec: an episode starts at the first blooming sample and ends at the first sample that neither blooms nor falters
                                bool sBl = weatherOn && hasExt && cur == Bloom && SpecLerpIsOne[lerpIdx] == 1;
                                bool sFa = weatherOn && hasExt && cur == Bloom && SpecLerpIsOne[lerpIdx] == 0;
                                Check(bl == sBl && (fa == sFa), $"bloom/falter flags ({bl},{fa}) != spec ({sBl},{sFa}) at weather {cur} lerp {lerp}");
                                Check(!(bl && falter()), "a vent both blooms and falters");
                                if (sBl) { if (!sInEpisode) { sInEpisode = true; sEpisodes++; sLastBlow = now; Blowouts++; } }
                                else if (!sFa) sInEpisode = false;
                                Check(lastBlow == sLastBlow && seen == sInEpisode, $"blowout memory {lastBlow}/{seen} != spec {sLastBlow}/{sInEpisode}");
                                if (sFa) Falters++;
                                supp = RM_VentKernel.Decay(supp, decay);
                                if (sSupp > 0) sSupp = Math.Max(0, sSupp - 250.0 * decay / 60000.0);
                                Check(Near(supp, sSupp, 1e-7), $"suppression {supp} != spec {sSupp} after decay");
                            }
                            break;
                        case 1:
                            cur = new[] { Bloom, Rain, Clear, -1 }[a.a % 4];
                            lerpIdx = a.b % Lerps.Length; lerp = Lerps[lerpIdx];
                            break;
                        case 2: // Drink: a vexxiss adds a few ticks of suppression
                            for (int k = 0; k < 1 + a.a % 8; k++)
                            {
                                float amount = new[] { 0.125f, 0.25f, 0.5f, 1f }[a.b % 4];
                                bool silenced = RM_VentKernel.IsSilenced(silencedUntil, now);
                                Check(silenced == (sSilencedUntil >= 0 && now < sSilencedUntil), "IsSilenced != spec");
                                bool full = RM_VentKernel.AddSuppression(ref supp, amount, silenced, hasExt);
                                // spec
                                bool sFull = false;
                                if (!(sSilencedUntil >= 0 && now < sSilencedUntil) && hasExt) { sSupp += amount; if (sSupp >= 1.0) { sSupp = 0; sFull = true; } }
                                Check(full == sFull, $"AddSuppression full={full} spec={sFull}");
                                Check(Near(supp, sSupp, 1e-7), $"suppression {supp} != spec {sSupp}");
                                Check(supp >= 0f && supp < 1f, "suppression left [0,1)");
                                if (full)
                                {
                                    float jitter = 0.85f + (float)rng.NextDouble() * 0.3f;
                                    int until = RM_VentKernel.SilenceUntil(now, silenceDays, jitter);
                                    Check(Math.Abs(until - (now + Math.Round((double)silenceDays * jitter * 60000.0))) <= 1.5, "silence duration != days * jitter * 60000");
                                    Check(until >= now + (long)(silenceDays * 0.85 * 60000) - 2 && until <= now + (long)(silenceDays * 1.15 * 60000) + 2, "silence outside 0.85..1.15 of the setting");
                                    silencedUntil = until; sSilencedUntil = until; Silences++;
                                }
                            }
                            break;
                        case 3: weatherOn = !weatherOn; break;
                        case 4: // habitat match vs a literal table
                            {
                                bool recent = RM_VentKernel.RecentlyBlewOut(now, lastBlow, recentWindow);
                                Check(recent == ((long)now - lastBlow < recentWindow), "RecentlyBlewOut != spec");
                                foreach (RM_VentHabitat h in Enum.GetValues(typeof(RM_VentHabitat)))
                                {
                                    bool want = h == RM_VentHabitat.StableRing ? temperament == RM_VentTemperament.Stable && !recent
                                        : h == RM_VentHabitat.ChronicLeak ? temperament == RM_VentTemperament.Leaking
                                        : h == RM_VentHabitat.RecentBlowout ? recent : false;
                                    Check(RM_VentKernel.Matches(h, temperament, recent) == want, $"Matches({h}) != spec");
                                }
                                if (temperament == RM_VentTemperament.Stable) Check(!(RM_VentKernel.Matches(RM_VentHabitat.StableRing, temperament, recent) && RM_VentKernel.Matches(RM_VentHabitat.RecentBlowout, temperament, recent)), "a stable ring vent that recently blew out is in two habitats");
                            }
                            break;
                        case 5: // output and recovery
                            {
                                float rec = RM_VentKernel.Recovery01(silencedUntil, now, recoverTicks);
                                bool silenced = silencedUntil >= 0 && now < silencedUntil;
                                double sRec = sSilencedUntil < 0 ? 1.0 : now < sSilencedUntil ? 0.0 : Math.Min(1.0, (now - sSilencedUntil) / (double)Math.Max(1, recoverTicks));
                                Check(Near(rec, sRec, 1e-5), $"Recovery01 {rec} != spec {sRec}");
                                Check(rec >= 0f && rec <= 1f, "recovery outside [0,1]");
                                if (silenced) Check(rec == 0f, "a silenced vent has recovery above 0");
                                bool fa = falter();
                                float mult = RM_VentKernel.WeatherMultiplier(hasExt, weatherOn, true, fa, falterOut, cur, rowIds, rowOuts, defaultOut);
                                double sMult;
                                if (!hasExt || !weatherOn) sMult = 1;
                                else if (weatherOn && hasExt && cur == Bloom && SpecLerpIsOne[lerpIdx] == 0) sMult = falterOut;
                                else { sMult = defaultOut; for (int i = 0; i < rowIds.Length; i++) if (rowIds[i] == cur) { sMult = rowOuts[i]; break; } }
                                Check(Near(mult, sMult), $"weather multiplier {mult} != spec {sMult} (weather {cur}, lerp {lerp})");
                                float output = RM_VentKernel.Output(mult, rec);
                                Check(output >= 0f && Near(output, sMult * sRec, 1e-4), "output != multiplier * recovery");
                                if (silenced) Check(output == 0f, "a silenced vent has output");
                                if (silencedUntil >= 0 && now >= silencedUntil && rec < 1f) Recoveries++;
                                Check(RM_VentKernel.PuffsAt(output) == (output > 0.05f) && RM_VentKernel.PuffChance(output) >= 0f && RM_VentKernel.PuffChance(output) <= 1f, "puff gate");
                            }
                            break;
                        case 6: // map generation: count and the stable/leaking mix
                            {
                                Generations++;
                                int area = 10000 + a.a * 300;
                                float jitter = 0.8f + (a.b % 51) / 100f;
                                int n = RM_VentKernel.VentCount(area, jitter);
                                int sN = (int)Math.Min(8, Math.Max(2, Math.Round(area / 14000.0 * jitter)));
                                Check(Math.Abs(n - sN) <= 1 && n >= 2 && n <= 8, $"VentCount({area}, {jitter}) = {n}, spec {sN}");
                                Check(RM_VentKernel.VentCount(area + 5000, jitter) >= n, "more area gave fewer vents");
                                var temps = new RM_VentTemperament[a.c % 9];
                                for (int i = 0; i < temps.Length; i++) temps[i] = r.Next(4) == 0 ? RM_VentTemperament.Leaking : RM_VentTemperament.Stable;
                                if (a.c % 3 == 0) for (int i = 0; i < temps.Length; i++) temps[i] = RM_VentTemperament.Stable;
                                if (a.c % 5 == 0) for (int i = 0; i < temps.Length; i++) temps[i] = RM_VentTemperament.Leaking;
                                var before = (RM_VentTemperament[])temps.Clone();
                                RM_VentKernel.MixTemperaments(temps);
                                if (temps.Length >= 2) Check(temps.Contains(RM_VentTemperament.Leaking) && temps.Contains(RM_VentTemperament.Stable), "a map lacks a stable vent or a chronic leak");
                                else Check(temps.SequenceEqual(before), "a lone vent was reassigned");
                                Check(Enumerable.Range(0, temps.Length).Count(i => temps[i] != before[i]) <= 1, "more than one vent reassigned");
                                var again = (RM_VentTemperament[])temps.Clone(); RM_VentKernel.MixTemperaments(again);
                                Check(again.SequenceEqual(temps), "the mix is not idempotent");
                            }
                            break;
                        case 7: // exposure weight and drink target
                            {
                                ExposureProbes++;
                                int nv = a.a % 7;
                                var dist = new float[nv]; var rec = new float[nv];
                                for (int i = 0; i < nv; i++) { dist[i] = (float)(r.NextDouble() * 70); if (r.Next(6) == 0) dist[i] = r.Next(2) == 0 ? 8f : 45f; rec[i] = r.Next(4) == 0 ? 0f : (float)r.NextDouble(); }
                                float w = RM_VentKernel.ExposureWeight(true, true, nv, dist, rec);
                                double best = 0;
                                for (int i = 0; i < nv; i++) { double pr = dist[i] <= 8 ? 1 : dist[i] >= 45 ? 0 : 1 - (dist[i] - 8.0) / 37.0; best = Math.Max(best, pr * rec[i]); }
                                double sW = nv == 0 ? 1.0 : 0.1 + 0.9 * best;
                                Check(Near(w, sW, 1e-4), $"ExposureWeight {w} != spec {sW}");
                                Check(w >= 0.1f - 1e-6f && w <= 1f + 1e-6f, "exposure weight outside [0.1, 1]");
                                Check(RM_VentKernel.ExposureWeight(false, true, nv, dist, rec) == 1f && RM_VentKernel.ExposureWeight(true, false, nv, dist, rec) == 1f, "exposure must be 1 when off or without the component");
                                if (nv > 0)
                                {
                                    var dist2 = dist.Concat(new[] { 1f }).ToArray(); var rec2 = rec.Concat(new[] { 1f }).ToArray();
                                    Check(RM_VentKernel.ExposureWeight(true, true, nv + 1, dist2, rec2) >= w - 1e-6f, "adding a live nearby vent lowered the exposure");
                                    var rec0 = rec.Select(_ => 0f).ToArray();
                                    Check(RM_VentKernel.ExposureWeight(true, true, nv, dist, rec0) == 0.1f, "all vents silenced must give the floor");
                                }
                                // the vexxiss' drink target
                                Picks++;
                                var dsq = new float[nv]; var sil = new bool[nv]; var outp = new float[nv]; var reach = new bool[nv];
                                for (int i = 0; i < nv; i++) { dsq[i] = (float)(r.NextDouble() * 400); sil[i] = r.Next(4) == 0; outp[i] = r.Next(5) == 0 ? 0.05f : (float)r.NextDouble() * 2; reach[i] = r.Next(4) != 0; }
                                float radius = new[] { 10f, 20f, 40f }[a.b % 3];
                                var asked = new List<int>();
                                int pick = RM_VentKernel.NearestDrinkable(dsq, sil, outp, i => { asked.Add(i); return reach[i]; }, radius);
                                int sPick = -1; double sBest = double.MaxValue;
                                for (int i = 0; i < nv; i++)
                                {
                                    if (sil[i] || outp[i] <= 0.05f || !reach[i] || dsq[i] >= radius * radius) continue;
                                    if (dsq[i] < sBest) { sBest = dsq[i]; sPick = i; }
                                }
                                Check(pick == sPick, $"NearestDrinkable {pick}, spec {sPick}");
                                // laziness: reachability only for a vent that could beat the best so far
                                double bestSoFar = radius * radius;
                                foreach (int i in asked) { Check(!sil[i] && outp[i] > 0.05f && dsq[i] < bestSoFar, $"reachability asked of vent {i}, which could not win"); if (reach[i]) bestSoFar = dsq[i]; }
                                LazyReachSaved += nv - asked.Count;
                            }
                            break;
                    }
                    Check(lastBlow <= now && sLastBlow <= now, "a blowout in the future");
                    if (sSilencedUntil >= 0) Check(silencedUntil == sSilencedUntil, "silencedUntil drifted");
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static List<Act> GenVent(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(40);
                int kind = k < 12 ? 0 : k < 18 ? 1 : k < 25 ? 2 : k < 26 ? 3 : k < 29 ? 4 : k < 34 ? 5 : k < 36 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), c = r.Next(1000), names = VentNames });
            }
            return l;
        }

        public static List<string> Vent(int n, int baseSeed)
        {
            return RunFamily("vent", n, baseSeed, seed => { var r = new Random(seed * 7919 + 23); return GenVent(r, r.Next(4, 80)); }, RunVent);
        }

        // ════════════════════════ yield ════════════════════════
        public static long YieldProbes, DoseProbes, BeadFlips, Remeshes, EligibleHits;

        private static string RunYield(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            int step = 0; string err = null;
            bool init = false, lastDew = false;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0: // yield sweep for one tree shape
                            {
                                YieldProbes++;
                                float min = new[] { 0f, 0.25f, 0.5f, 0.8f, 1f }[a.a % 5];
                                float cMin = new[] { 0f, 1f, 2f }[a.b % 3], cFull = new[] { 0f, 4f, 6f, 12f }[a.c % 4];
                                float factor = new[] { 0f, 0.5f, 1f, 2f }[(a.a + a.b) % 4];
                                float prev = -1f, prevFrac = -1f;
                                for (int g = 0; g <= 20; g++)
                                {
                                    float growth = g / 20f;
                                    float exp = RM_YieldKernel.Expected(growth, min, cMin, cFull, factor);
                                    if (growth < min) Check(exp == 0f, $"an unripe trunk (growth {growth} < {min}) yields {exp}");
                                    else
                                    {
                                        double t = min >= 1 ? 0 : Math.Min(1, Math.Max(0, (growth - min) / (1.0 - min)));
                                        Check(Near(exp, (cMin + (cFull - cMin) * t) * factor, 1e-4), $"Expected({growth}) = {exp}");
                                        if (prev >= 0 && cFull >= cMin) Check(exp >= prev - 1e-6f, "yield fell as the trunk grew");
                                        prev = exp;
                                    }
                                    float harvest = RM_YieldKernel.AtHarvest(true, true, growth, min, cMin, cFull, factor);
                                    if (growth >= min) Check(Near(harvest, exp, 1e-4), "AtHarvest != Expected once ripe");
                                    Check(RM_YieldKernel.AtHarvest(false, true, growth, min, cMin, cFull, factor) == 0f && RM_YieldKernel.AtHarvest(true, false, growth, min, cMin, cFull, factor) == 0f, "yield toggle off / no metal must give 0");
                                    float frac = RM_YieldKernel.GradeFraction(exp, cFull, factor);
                                    double sFrac = cFull * factor > 0 ? exp / (cFull * (double)factor) : 0.0;
                                    Check(Near(frac, sFrac, 1e-5), "GradeFraction != spec");
                                    if (cFull >= cMin && cFull * factor > 0) Check(frac >= 0f && frac <= 1f + 1e-5f, $"grade fraction {frac} outside [0,1]");
                                    int tier = RM_YieldKernel.GradeTier(frac);
                                    int sTier = frac >= 0.95 ? 3 : frac >= 2.0 / 3.0 ? 2 : frac >= 1.0 / 3.0 ? 1 : 0;
                                    Check(tier == sTier || Math.Abs(frac - 2f / 3f) < 1e-6 || Math.Abs(frac - 1f / 3f) < 1e-6 || Math.Abs(frac - 0.95f) < 1e-6, $"GradeTier({frac}) = {tier}, spec {sTier}");
                                    if (prevFrac >= 0 && cFull >= cMin) Check(tier >= RM_YieldKernel.GradeTier(prevFrac), "grade fell as the trunk grew");
                                    prevFrac = frac;
                                    // fleck band: heavy beats light, each falls back to the other, nothing without art or below the threshold
                                    foreach (bool hl in new[] { false, true }) foreach (bool hh in new[] { false, true })
                                    {
                                        var band = RM_YieldKernel.FleckBand(frac, 1f / 3f, 2f / 3f, hl, hh);
                                        if (frac < 1f / 3f || (!hl && !hh)) Check(band == RM_AssayBand.None, "a fleck band without art or below the light threshold");
                                        else if (frac >= 2f / 3f) Check(band == (hh ? RM_AssayBand.Heavy : RM_AssayBand.Light), $"heavy tier band {band} (heavy art {hh}, light art {hl})");
                                        else Check(band == (hl ? RM_AssayBand.Light : RM_AssayBand.Heavy), $"light tier band {band}");
                                    }
                                }
                                Check(RM_YieldKernel.FlecksOn(true, true, true) && !RM_YieldKernel.FlecksOn(false, true, true) && !RM_YieldKernel.FlecksOn(true, false, true) && !RM_YieldKernel.FlecksOn(true, true, false), "FlecksOn needs all three toggles");
                                // random rounding averages to its argument
                                float x = new[] { 0.3f, 1.5f, 4.75f }[a.a % 3]; int N = 4000; long sum = 0;
                                var rr = new Random(seed + 5);
                                for (int i = 0; i < N; i++) { int v = RM_YieldKernel.RoundRandom(x, (float)rr.NextDouble()); Check(v == (int)Math.Floor(x) || v == (int)Math.Floor(x) + 1, "RoundRandom left floor..floor+1"); sum += v; }
                                Check(Math.Abs(sum / (double)N - x) < 0.05, $"RoundRandom mean {sum / (double)N} != {x}");
                            }
                            break;
                        case 1: // the bloom's metal-load dose and who gets it
                            {
                                DoseProbes++;
                                float factor = new[] { 0f, 0.5f, 1f, 3f }[a.a % 4];
                                float tox = new[] { -0.5f, 0f, 0.4f, 1f, 1.5f }[a.b % 5], env = new[] { 0f, 0.25f, 1f, 2f }[a.c % 4];
                                float weight = new[] { 0.1f, 0.55f, 1f }[(a.a + a.c) % 3];
                                float dose = RM_YieldKernel.Dose(factor, tox, env, weight);
                                double sDose = 0.012 * factor * Math.Max(1 - tox, 0) * Math.Max(1 - env, 0) * weight;
                                Check(Near(dose, sDose, 1e-6), $"Dose {dose} != spec {sDose}");
                                Check(dose >= 0f, "a negative dose");
                                if (tox >= 1f || env >= 1f || factor == 0f) Check(dose == 0f, "full resistance or a zero factor still doses");
                                Check(RM_YieldKernel.Dose(factor, tox, env, weight) >= RM_YieldKernel.Dose(factor, tox + 0.1f, env, weight) - 1e-9f, "more resistance raised the dose");
                                // eligibility against a literal table, all 256 rows once per probe set
                                for (int m = 0; m < 256; m++)
                                {
                                    bool ex = (m & 1) != 0, dead = (m & 2) != 0, sp = (m & 4) != 0, imm = (m & 8) != 0, fl = (m & 16) != 0, roof = (m & 32) != 0, an = (m & 64) != 0, nat = (m & 128) != 0;
                                    bool want = ex && !dead && sp && !imm && fl && !roof && !(an && nat);
                                    Check(RM_YieldKernel.Eligible(ex, dead, sp, imm, fl, roof, an, nat) == want, $"Eligible row {m}");
                                    if (want) EligibleHits++;
                                }
                                Steps += 256;
                                // ticks: only on the 3451 cadence, with the toggle, the bloom as current weather and its transition finished
                                for (int tk = 0; tk < 10; tk++)
                                {
                                    int t = tk * 3451 + (a.a % 2);
                                    bool want = t % 3451 == 0;
                                    Check(RM_YieldKernel.BloomTicks(t, true, true, true) == want, "BloomTicks cadence");
                                }
                                Check(!RM_YieldKernel.BloomTicks(3451, false, true, true) && !RM_YieldKernel.BloomTicks(3451, true, false, true) && !RM_YieldKernel.BloomTicks(3451, true, true, false), "BloomTicks needs toggle, bloom and finished transition");
                            }
                            break;
                        case 2: // dewfall: weather flips, remesh once each way when the art is live
                            {
                                bool dew = a.a % 2 == 0, sat = a.b % 3 != 0, art = a.c % 4 != 0;
                                bool flipped = RM_YieldKernel.DewFlip(init, lastDew, dew);
                                Check(flipped == (init && dew != lastDew), "DewFlip != spec");
                                if (!init) { lastDew = dew; init = true; }
                                else if (flipped)
                                {
                                    lastDew = dew; BeadFlips++;
                                    bool remesh = RM_YieldKernel.RemeshOnFlip(true, sat, art);
                                    Check(remesh == (sat && art), "RemeshOnFlip != saturation && art");
                                    if (remesh) Remeshes++;
                                }
                                // bead budget
                                float density = new[] { -1f, 0f, 0.25f, 1f, 2.5f }[a.a % 5];
                                int cap = RM_YieldKernel.BeadCap_(density);
                                Check(cap == (int)Math.Round(400 * density), "bead cap != round(400 * density)");
                                int existing = (a.b * 7) % 900;
                                Check(RM_YieldKernel.BeadsSpawn(density, existing, cap) == (density > 0f && existing < cap), "BeadsSpawn gate");
                                // a bead cell: every refusal reason
                                for (int m = 0; m < 256; m++)
                                {
                                    bool roof = (m & 1) != 0, fog = (m & 2) != 0, stand = (m & 4) != 0, terr = (m & 8) != 0, wat = (m & 16) != 0, home = (m & 32) != 0, room = (m & 64) != 0, outd = (m & 128) != 0;
                                    bool want = !roof && !fog && stand && terr && !wat && !home && (!room || outd);
                                    Check(RM_YieldKernel.CanBead(roof, fog, stand, terr, wat, home, room, outd) == want, $"CanBead row {m}");
                                }
                                Steps += 256;
                            }
                            break;
                    }
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static readonly string[] YieldNames = { "Yield", "Dose", "Dew" };
        private static List<Act> GenYield(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
                l.Add(new Act { kind = r.Next(10) < 3 ? 0 : r.Next(2) == 0 ? 1 : 2, a = r.Next(1000), b = r.Next(1000), c = r.Next(1000), names = YieldNames });
            return l;
        }

        public static List<string> Yield(int n, int baseSeed)
        {
            return RunFamily("yield", n, baseSeed, seed => { var r = new Random(seed * 7919 + 29); return GenYield(r, r.Next(2, 12)); }, RunYield);
        }

        // ════════════════════════ prints ════════════════════════
        private sealed class PrintEntry { public int cell, laid, expires, id; }
        private static readonly string[] PrintNames = { "Add", "Tick", "Overwrite", "Reload", "Step" };
        public static long PrintsAdded, PrintsEvicted, PrintsExpired, GridCleared, GridKept;

        private static string RunPrints(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            int cap = r.Next(3, 30), life = new[] { 500, 2500, 60000 }[r.Next(3)], cells = r.Next(2, 12);
            var ledger = new RM_PrintLedger<int, PrintEntry>(e => e.cell, e => e.expires);
            var grid = new Dictionary<int, int>();   // cell -> laid tick of the print the footprint grid holds
            var spec = new List<PrintEntry>();
            int now = r.Next(0, 4) * 250, ids = 0, lastCell = -1;
            var specCleared = new HashSet<int>(); var specGridRemoved = new List<int>();
            int step = 0; string err = null;
            Action<PrintEntry> clear = e => { if (grid.TryGetValue(e.cell, out int g) && g == e.laid) { grid.Remove(e.cell); GridCleared++; } else GridKept++; };
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                now += a.b % 400;
                                int c = a.a % cells;
                                var e = new PrintEntry { cell = c, laid = now, expires = now + life, id = ids++ };
                                grid[c] = now; PrintsAdded++;
                                int evBefore = ledger.Evicted;
                                ledger.Add(e, cap, clear);
                                spec.Add(e);
                                while (spec.Count > cap) { spec.RemoveAt(0); PrintsEvicted++; }
                                Check(ledger.Evicted - evBefore == Math.Max(0, ledger.Entries.Count + (ledger.Evicted - evBefore) - cap), "eviction count");
                            }
                            break;
                        case 1:
                            {
                                now += (a.a % 12) * 125 + (a.b % 3 == 0 ? 250 - now % 250 : 0);
                                ledger.Tick(now, clear);
                                if (now % 250 == 0)
                                {
                                    while (spec.Count > 0 && spec[0].expires <= now) { spec.RemoveAt(0); PrintsExpired++; }
                                    Check(ledger.Entries.All(e => e.expires > now), "an expired print survived a check tick");
                                }
                            }
                            break;
                        case 2: // another walker or an eraser replaces the grid's record for a cell
                            {
                                int c = a.a % cells;
                                if (a.b % 2 == 0) grid.Remove(c); else grid[c] = now + 1000000 + a.b;
                            }
                            break;
                        case 3: // save and load: the index is rebuilt from the saved order
                            {
                                ledger.Entries.Add(null); ledger.Rebuild();
                                Check(ledger.Entries.All(e => e != null), "a null entry survived the rebuild");
                            }
                            break;
                        case 4: // the step rule
                            {
                                float stepCells = 1.5f;
                                bool valid = lastCell >= 0;
                                float dsq = a.a % 10 * 0.5f * (a.a % 10 * 0.5f);
                                bool far = RM_VexxissKernel.StepFarEnough(valid, dsq, stepCells);
                                Check(far == (!valid || dsq >= stepCells * stepCells), "StepFarEnough");
                                lastCell = a.a;
                            }
                            break;
                    }
                    // ---- invariants after every step ----
                    Check(ledger.Entries.Count <= cap, $"ledger holds {ledger.Entries.Count} above its cap {cap}");
                    Check(ledger.Entries.SequenceEqual(spec), "ledger order drifted from the spec");
                    for (int i = 1; i < ledger.Entries.Count; i++) Check(ledger.Entries[i - 1].laid <= ledger.Entries[i].laid, "entries out of laid order");
                    var newest = new Dictionary<int, PrintEntry>(); foreach (var e in spec) newest[e.cell] = e;
                    Check(ledger.ByCell.Count == newest.Count && ledger.ByCell.All(kv => ReferenceEquals(newest[kv.Key], kv.Value)), "the newest-per-cell index is wrong");
                    Check(ledger.Entries.Count == 0 || ledger.Entries.Select(e => e.cell).Distinct().Count() == ledger.ByCell.Count, "index size != distinct cells");
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static List<Act> GenPrints(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(30);
                l.Add(new Act { kind = k < 13 ? 0 : k < 22 ? 1 : k < 25 ? 2 : k < 27 ? 3 : 4, a = r.Next(1000), b = r.Next(1000), c = 0, names = PrintNames });
            }
            return l;
        }

        public static List<string> Prints(int n, int baseSeed)
        {
            var fails = RunFamily("prints", n, baseSeed, seed => { var r = new Random(seed * 7919 + 31); return GenPrints(r, r.Next(4, 90)); }, RunPrints);
            try { WardUnits(); } catch (Exception e) { fails.Add("ward units: " + e.Message); }
            Cases++;
            return fails;
        }

        private static void WardUnits()
        {
            for (int m = 0; m < 64; m++)
            {
                bool dn = (m & 1) != 0, aw = (m & 2) != 0, men = (m & 4) != 0, jobs = (m & 8) != 0, dr = (m & 16) != 0, busy = (m & 32) != 0;
                Check(RM_VexxissKernel.WardCanAct(dn, aw, men, jobs, dr, busy) == (!dn && aw && !men && jobs && !dr && !busy), $"WardCanAct row {m}"); Steps++;
            }
            for (int m = 0; m < 512; m++)
            {
                bool ex = (m & 1) != 0, self = (m & 2) != 0, sp = (m & 4) != 0, dead = (m & 8) != 0, dn = (m & 16) != 0, map = (m & 32) != 0, fac = (m & 64) != 0, far = (m & 128) != 0, reach = (m & 256) != 0;
                float dsq = far ? 31f * 31f : 30f * 30f;
                bool want = ex && !self && sp && !dead && !dn && map && !fac && !far && reach;
                Check(RM_VexxissKernel.IgniterAttackable(ex, self, sp, dead, dn, map, fac, dsq, 30f, reach) == want, $"IgniterAttackable row {m}"); Steps++;
            }
            Check(RM_VexxissKernel.IgniterAttackable(true, false, true, false, false, true, false, 900f, 30f, true), "an igniter exactly at the chase radius is attackable");
            for (int m = 0; m < 16; m++)
            {
                bool fire = (m & 1) != 0, set = (m & 2) != 0, att = (m & 4) != 0, verb = (m & 8) != 0;
                WardChoice want = !fire ? WardChoice.None : (set && att) ? WardChoice.AttackIgniter : verb ? WardChoice.BeatFire : WardChoice.None;
                Check(RM_VexxissKernel.Ward(fire, set, att, verb) == want, $"Ward row {m}"); Steps++;
            }
            var rr = new Random(9);
            for (int s = 0; s < 400; s++)
            {
                int n = rr.Next(0, 9);
                var dsq = new float[n]; var el = new bool[n]; var rc = new bool[n];
                for (int i = 0; i < n; i++) { dsq[i] = (float)(rr.NextDouble() * 400); el[i] = rr.Next(4) != 0; rc[i] = rr.Next(3) != 0; }
                float radius = 15f; var asked = new List<int>();
                int got = RM_VexxissKernel.NearestFire(dsq, el, i => { asked.Add(i); return rc[i]; }, radius);
                int want = -1; double bst = double.MaxValue;
                for (int i = 0; i < n; i++) { if (!el[i] || dsq[i] > radius * radius || !rc[i]) continue; if (dsq[i] < bst) { bst = dsq[i]; want = i; } }
                Check(got == want, $"NearestFire {got}, spec {want}");
                double b = double.MaxValue;
                foreach (int i in asked) { Check(el[i] && dsq[i] <= radius * radius && dsq[i] < b, "reachability asked of a fire that could not win"); if (rc[i]) b = dsq[i]; }
                Steps++;
            }
            Check(RM_VexxissKernel.WarnWater(true, true, true, 100000, 40000, 60000) && !RM_VexxissKernel.WarnWater(true, true, true, 99999, 40000, 60000)
                && !RM_VexxissKernel.WarnWater(false, true, true, 200000, 0, 60000) && !RM_VexxissKernel.WarnWater(true, false, true, 200000, 0, 60000) && !RM_VexxissKernel.WarnWater(true, true, false, 200000, 0, 60000), "WarnWater throttle boundary at exactly the cooldown");
            Check(RM_VexxissKernel.PrintableTerrain(true, false, true) && !RM_VexxissKernel.PrintableTerrain(false, false, true) && !RM_VexxissKernel.PrintableTerrain(true, true, true) && !RM_VexxissKernel.PrintableTerrain(true, false, false), "PrintableTerrain");
            Check(RM_VexxissKernel.PrintAllowed(false, false) && !RM_VexxissKernel.PrintAllowed(true, false) && !RM_VexxissKernel.PrintAllowed(false, true), "PrintAllowed");
        }

        // ════════════════════════ units ════════════════════════
        public static List<string> Units()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Check(RM_VentKernel.ApproximatelyOne(1f) && RM_VentKernel.ApproximatelyOne(0.9999995f) && RM_VentKernel.ApproximatelyOne(1.0000002f) && !RM_VentKernel.ApproximatelyOne(0.99999f) && !RM_VentKernel.ApproximatelyOne(0f), "ApproximatelyOne");
                // faltering / blooming need the setting, a map, the extension, a bloom weather, and the right transition state
                for (int m = 0; m < 128; m++)
                {
                    bool on = (m & 1) != 0, map = (m & 2) != 0, ext = (m & 4) != 0, set = (m & 8) != 0, cur = (m & 16) != 0, one = (m & 32) != 0;
                    float lerp = one ? 1f : 0.4f;
                    bool base_ = on && map && ext && set && cur;
                    Check(RM_VentKernel.Faltering(on, map, ext, set, cur, lerp) == (base_ && !one), $"Faltering row {m}");
                    Check(RM_VentKernel.Blooming(on, map, ext, set, cur, lerp) == (base_ && one), $"Blooming row {m}");
                    Steps++;
                }
                Check(RM_VentKernel.WeatherMultiplier(false, true, true, false, 0.1f, 1, new[] { 1 }, new[] { 3f }, 2f) == 1f && RM_VentKernel.WeatherMultiplier(true, false, true, false, 0.1f, 1, new[] { 1 }, new[] { 3f }, 2f) == 1f && RM_VentKernel.WeatherMultiplier(true, true, false, false, 0.1f, 1, new[] { 1 }, new[] { 3f }, 2f) == 1f, "no extension / switch off / no map = 1");
                Check(RM_VentKernel.WeatherMultiplier(true, true, true, true, 0.1f, 1, new[] { 1 }, new[] { 3f }, 2f) == 0.1f && RM_VentKernel.WeatherMultiplier(true, true, true, false, 0.1f, 1, new[] { 1, 1 }, new[] { 3f, 5f }, 2f) == 3f && RM_VentKernel.WeatherMultiplier(true, true, true, false, 0.1f, 9, new[] { 1 }, new[] { 3f }, 2f) == 2f, "falter beats rows, first row wins, default otherwise");
                Check(RM_VentKernel.Recovery01(-1, 5, 100) == 1f && RM_VentKernel.Recovery01(100, 99, 100) == 0f && RM_VentKernel.Recovery01(100, 150, 100) == 0.5f && RM_VentKernel.Recovery01(100, 500, 100) == 1f && RM_VentKernel.Recovery01(100, 100, 0) == 0f, "Recovery01 points");
                Check(RM_VentKernel.IsSilenced(100, 99) && !RM_VentKernel.IsSilenced(100, 100) && !RM_VentKernel.IsSilenced(-1, 0) && RM_VentKernel.IsSilenced(0, -1) == true, "IsSilenced boundary");
                Check(RM_VentKernel.InRing(2.5f, 2.5f, 8f) && RM_VentKernel.InRing(8f, 2.5f, 8f) && !RM_VentKernel.InRing(2.49f, 2.5f, 8f) && !RM_VentKernel.InRing(8.01f, 2.5f, 8f), "ring edges are inclusive");
                Check(RM_VentKernel.Proximity(8f) == 1f && RM_VentKernel.Proximity(45f) == 0f && Near(RM_VentKernel.Proximity(26.5f), 0.5), "Proximity");
                Check(RM_VentKernel.DrinkAllowed(true, false, true, false, true, 100, 100, false) && !RM_VentKernel.DrinkAllowed(true, false, true, false, true, 99, 100, false) && !RM_VentKernel.DrinkAllowed(false, false, true, false, true, 100, 0, false) && !RM_VentKernel.DrinkAllowed(true, false, true, false, true, 100, 0, true), "DrinkAllowed cooldown boundary and gates");
                Check(RM_VentKernel.DrinkRadius(true, 40f, 80f) == 80f && RM_VentKernel.DrinkRadius(false, 40f, 80f) == 40f && !RM_VentKernel.DrinkRollNeeded(true) && RM_VentKernel.DrinkRollNeeded(false), "a groan widens the scan and skips the roll");
                Check(Near(RM_VentKernel.Decay(0.5f, 0.9375f), 0.5 - 1 / 256.0, 1e-9) && RM_VentKernel.Decay(0.001f, 0.9375f) == 0f && RM_VentKernel.Decay(0f, 5f) == 0f, "Decay");
                Check(RM_VentKernel.DrinkPerTick(6000f) == 1f / 6000f, "DrinkPerTick");
                Check(!RM_VentKernel.PuffsAt(0.05f) && RM_VentKernel.PuffsAt(0.0501f) && !RM_VentKernel.Smokes(1.5f) && RM_VentKernel.Smokes(1.51f) && RM_VentKernel.PuffChance(10f) == 1f && RM_VentKernel.PuffChance(-1f) == 0f, "puff gates");
                Check(RM_VentKernel.TooClose(23.99f, 24f) && !RM_VentKernel.TooClose(24f, 24f), "vent spacing boundary");
                Check(RM_VentKernel.VentCount(250 * 250, 1f) == 4 && RM_VentKernel.VentCount(100, 1f) == 2 && RM_VentKernel.VentCount(100000000, 1.3f) == 8, "VentCount on a 250x250 map and the clamps");
                // yield units
                Check(RM_YieldKernel.InverseLerp(1f, 1f, 0.5f) == 0f && RM_YieldKernel.InverseLerp(0.5f, 1f, 0.75f) == 0.5f && RM_YieldKernel.InverseLerp(0.5f, 1f, 0.1f) == 0f, "InverseLerp");
                Check(RM_YieldKernel.GradeTier(0.95f) == 3 && RM_YieldKernel.GradeTier(0.949f) == 2 && RM_YieldKernel.GradeTier(2f / 3f) == 2 && RM_YieldKernel.GradeTier(0.66f) == 1 && RM_YieldKernel.GradeTier(1f / 3f) == 1 && RM_YieldKernel.GradeTier(0.33f) == 0, "grade tier cut points");
                Check(RM_YieldKernel.IsShore(false, true) && !RM_YieldKernel.IsShore(true, true) && !RM_YieldKernel.IsShore(false, false) && !RM_YieldKernel.IsShore(true, false), "a shore is land beside the named terrain");
                Check(RM_YieldKernel.PlantAllowed(false, false, true) && !RM_YieldKernel.PlantAllowed(true, false, true) && !RM_YieldKernel.PlantAllowed(false, true, true) && !RM_YieldKernel.PlantAllowed(false, false, false), "PlantAllowed");
                Check(RM_YieldKernel.RoundRandom(2.5f, 0.49f) == 3 && RM_YieldKernel.RoundRandom(2.5f, 0.5f) == 2 && RM_YieldKernel.RoundRandom(3f, 0.99f) == 3, "RoundRandom");
            }
            catch (Exception e) { fails.Add("units: " + e.Message); }
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
                ("vent", () => Vent(N(4000), S(1))),
                ("yield", () => Yield(N(3000), S(1))),
                ("prints", () => Prints(N(4000), S(1))),
                ("units", () => Units()),
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
            Console.WriteLine($"vent: blowouts {Blowouts}, falters {Falters}, silences {Silences}, recoveries {Recoveries}, exposure probes {ExposureProbes}, generations {Generations}, drink picks {Picks}, reachability asks saved by laziness {LazyReachSaved}");
            Console.WriteLine($"yield: tree sweeps {YieldProbes}, dose probes {DoseProbes}, eligible rows {EligibleHits}, dew flips {BeadFlips}, remeshes {Remeshes}; prints: added {PrintsAdded}, evicted {PrintsEvicted}, expired {PrintsExpired}, grid cleared {GridCleared}, grid kept {GridKept}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                var blind = new List<string>();
                if (Blowouts == 0 || Falters == 0 || Silences == 0 || Recoveries == 0 || Generations == 0 || Picks == 0) blind.Add("vent never blew out/faltered/silenced/recovered/generated/picked");
                if (YieldProbes == 0 || DoseProbes == 0 || BeadFlips == 0 || Remeshes == 0) blind.Add("yield never swept/dosed/flipped/remeshed");
                if (PrintsEvicted == 0 || PrintsExpired == 0 || GridCleared == 0 || GridKept == 0) blind.Add("prints never evicted/expired/cleared/kept a grid record");
                foreach (var b in blind) { Console.WriteLine("FAIL fuzz is blind: " + b); ok = false; }
            }
            Console.WriteLine($"cauldron fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
