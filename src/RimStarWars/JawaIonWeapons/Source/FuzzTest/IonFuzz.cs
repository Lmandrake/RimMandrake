// Approach B for JawaIonWeapons: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RSW_IonBuildupKernel.cs):
//   size   the body-size barrier: the divisor, and the third-party stat part composed with the engine's own 1/size (they must agree)
//   flesh  a pawn taking ion hits: buildup gates, severity maths, accumulation, the 25x / 1024x anchors, the strength slider
//   tiers  machines, droids, shields and vehicles taking the same hits: EMP amounts, stun ticks, footprint spreading
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.StarWars.JawaIonWeapons.Fuzz
{
    internal static class IonFuzz
    {
        public static long Cases, Steps, Deposits, Skipped, Machines, Droids, Vehicles, Shields, Composed;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double rel = 1e-4) { return Math.Abs(a - b) <= rel * Math.Max(1e-9, Math.Max(Math.Abs(a), Math.Abs(b))); }

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

        private struct Act
        {
            public int kind, a, b, c; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + "," + c + (f ? ",T" : "") + ")"; }
        }

        private static Act[] Gen(Random r, int len, int[] kindWeights)
        {
            int total = kindWeights.Sum();
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= kindWeights[kind]) { k -= kindWeights[kind]; kind++; }
                a[i] = new Act { kind = kind, a = r.Next(1 << 16), b = r.Next(1 << 16), c = r.Next(1 << 16), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static List<string> Family(string name, int n, int seed0, int[] weights, int minLen, int spread, Func<IList<Act>, int, bool, string> run)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = Gen(r, minLen + r.Next(spread), weights); Cases++;
                if (run(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => run(t, seed, false) != null);
                fails.Add($"{name} seed {seed}: {run(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        private static readonly float[] Sizes = { 0f, -1f, 0.05f, 0.2f, 0.5f, 1f, 1.5f, 3f, 8f, 32f };
        private static readonly float[] Exps = { 0f, 0.005f, 0.5f, 1f, 1.5f, 2f, 2.5f, 3f };

        // ════════════════════════ size ════════════════════════
        private static List<string> SizeCases(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    float size = r.Next(4) == 0 ? Sizes[r.Next(Sizes.Length)] : 0.05f + (float)r.NextDouble() * 40f;
                    float exp = r.Next(3) == 0 ? Exps[r.Next(Exps.Length)] : (float)r.NextDouble() * 3f;
                    float div = RSW_IonBuildupKernel.BodySizeDivisor(size, exp);
                    Check(div > 0f && !float.IsNaN(div) && !float.IsInfinity(div), $"divisor {div} for size {size}, exponent {exp}");
                    if (size <= 0f || exp <= 0f) Check(div == 1f, "a size or exponent of 0 must not scale");
                    else Check(Near(div, Math.Pow(size, exp)), $"divisor {div} vs size^exp {Math.Pow(size, exp)}");
                    if (exp == 2f && size > 0f) Check(div == size * size, "the shipped exponent must be size * size exactly");
                    if (size >= 1f && exp > 0f) Check(div >= 1f, "a big target divided buildup by less than 1");
                    if (size > 0f && size < 1f && exp > 0f) Check(div <= 1f, "a small target got a divisor over 1");
                    // monotone in size
                    if (size > 0f && exp > 0f) Check(RSW_IonBuildupKernel.BodySizeDivisor(size * 1.5f, exp) >= div, "divisor fell as the target grew");
                    // the stat part composed with the engine's own multiply must equal 1 / divisor
                    float part = RSW_IonBuildupKernel.InverseSizeValue(true, true, size, exp, 1f);
                    if (size > 0f)
                    {
                        double composed = (1.0 / size) * part;
                        Check(Near(composed, 1.0 / div, 2e-3), $"third-party path {composed} vs flesh path {1.0 / div} (size {size}, exponent {exp})");
                        Composed++;
                    }
                    else Check(part == 1f, "a non-positive size changed the stat");
                    Check(RSW_IonBuildupKernel.InverseSizeValue(false, true, size, exp, 7f) == 7f, "the stat part acted with third-party scaling off");
                    Check(RSW_IonBuildupKernel.InverseSizeValue(true, false, size, exp, 7f) == 7f, "the stat part acted on a non-pawn");
                    Steps++;
                }
                catch (Exception e) { fails.Add($"size seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            try
            {
                Check(RSW_IonBuildupKernel.BodySizeDivisor(2f, -1f) == 1f && RSW_IonBuildupKernel.BodySizeDivisor(5f, -0.5f) == 1f && RSW_IonBuildupKernel.BodySizeDivisor(2f, 0f) == 1f, "a negative or zero exponent (a hand-edited settings file) must not scale");
                Check(RSW_IonBuildupKernel.BodySizeDivisor(0.2f, 2f) == 0.2f * 0.2f && Near(1f / RSW_IonBuildupKernel.BodySizeDivisor(0.2f, 2f), 25.0) && Near(RSW_IonBuildupKernel.BodySizeDivisor(32f, 2f), 1024.0), "25x / 1024x anchors");
                Check(Near(RSW_IonBuildupKernel.InverseSizeValue(true, true, 32f, 2f, 1f), 1.0 / 32.0) && Near(RSW_IonBuildupKernel.InverseSizeValue(true, true, 0.2f, 2f, 1f), 5.0) && RSW_IonBuildupKernel.InverseSizeValue(true, true, 1f, 2f, 9f) == 1f, "stat part anchors at the shipped exponent");
                Check(RSW_IonBuildupKernel.InverseSizeValue(true, true, 0f, 2f, 9f) == 9f && RSW_IonBuildupKernel.InverseSizeValue(true, true, -2f, 2f, 9f) == 9f, "stat part leaves the value at a size of 0 or less");
            }
            catch (Exception e) { fails.Add("size tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ flesh ════════════════════════
        // kinds: 0 hit, 1 new target, 2 settings
        private static string RunFlesh(IList<Act> acts, int seed, bool count)
        {
            bool enabled = true; float strength = 1f, exp = 2f; float size = 1f; double total = 0; bool mech = false, dead = false, health = true, race = true, entries = true; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 1: size = Sizes[a.a % Sizes.Length]; mech = (a.b & 7) == 0; dead = (a.b & 56) == 0; health = (a.c & 7) != 0; race = (a.c & 56) != 0; entries = (a.c & 192) != 0; total = 0; break;
                        case 2: enabled = (a.a & 7) != 0; strength = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.b % 5]; exp = Exps[a.c % Exps.Length]; break;
                        default:
                            {
                                float fixedSev = new[] { 0f, 0.05f, 1f, 4f }[a.a % 4], perDamage = new[] { 0f, 0.01f, 0.5f }[a.b % 3], dmg = new[] { 0f, 5f, 20f }[a.c % 3];
                                bool applies = RSW_IonBuildupKernel.FleshBuildupApplies(enabled, true, dead, health, race, mech, entries);
                                Check(applies == (enabled && !dead && health && race && !mech && entries), "FleshBuildupApplies");
                                if (!applies) { if (count) Skipped++; break; }
                                float div = RSW_IonBuildupKernel.BodySizeDivisor(size, exp);
                                float sev = RSW_IonBuildupKernel.FleshSeverity(fixedSev, perDamage, dmg, strength, div);
                                double want = (fixedSev > 0 ? fixedSev : perDamage * dmg) * strength / div;
                                Check(Near(sev, want), $"FleshSeverity {sev} vs {want}");
                                if (fixedSev > 0f) Check(sev > 0f, "a positive fixed severity vanished");
                                if (sev > 0f) { total += sev; if (count) Deposits++; }
                                Check(total >= 0, "accumulated buildup went negative");
                                // the fixed amount wins over per-damage
                                if (fixedSev > 0f) Check(Near(sev, RSW_IonBuildupKernel.FleshSeverity(fixedSev, perDamage + 3f, dmg + 9f, strength, div)), "per-damage leaked into a fixed entry");
                                // double strength, double severity
                                Check(Near(RSW_IonBuildupKernel.FleshSeverity(fixedSev, perDamage, dmg, strength * 2f, div), sev * 2.0), "strength is not linear");
                                break;
                            }
                    }
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        // ════════════════════════ tiers ════════════════════════
        // kinds: 0 hit a pawn, 1 hit a vehicle, 2 settings
        private static string RunTiers(IList<Act> acts, int seed, bool count)
        {
            bool mEn = true, sEn = true, vEn = true; float mMult = 1f, vMult = 1f, exp = 2f; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 2: mEn = (a.a & 7) != 0; sEn = (a.a & 56) != 0; vEn = (a.b & 7) != 0; mMult = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.b % 5]; vMult = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.c % 5]; exp = Exps[a.c % Exps.Length]; break;
                        case 1:
                            {
                                int sx = 1 + a.a % 6, sz = 1 + a.b % 6; float emp = new[] { 0f, 6f, 24f, 60f }[a.c % 4];
                                bool absorbed = (a.a & 64) != 0 || a.f, ion = (a.b & 64) != 0 || a.f, handlers = (a.c & 64) != 0 || a.f, stunner = (a.c & 128) != 0 || a.f;
                                int ticks = RSW_IonBuildupKernel.VehicleStunTicks(absorbed, vEn, ion, handlers, stunner, emp, sx, sz, vMult);
                                bool gate = absorbed && vEn && ion && handlers && stunner && emp > 0f;
                                double wantAmt = emp / Math.Max(1, sx * sz) * vMult;
                                int want = gate ? Math.Max(0, (int)Math.Round(wantAmt * 30.0, MidpointRounding.ToEven)) : 0;
                                Check(Math.Abs(ticks - want) <= 1, $"VehicleStunTicks {ticks} vs {want}");
                                if (!gate) Check(ticks == 0, "a vehicle that should not stun was stunned");
                                // a bigger footprint never stuns longer
                                if (gate) { int bigger = RSW_IonBuildupKernel.VehicleStunTicks(absorbed, vEn, ion, handlers, stunner, emp, sx + 1, sz, vMult); Check(bigger <= ticks, "a bigger vehicle stunned longer"); if (ticks > 0 && count) Vehicles++; }
                                break;
                            }
                        default:
                            {
                                bool live = (a.a & 3) != 0, hasRace = (a.a & 12) != 0, flesh = (a.a & 48) == 0, ionDef = (a.a & 192) != 0 || a.f, machine = (a.b & 1) != 0;
                                float size = Sizes[a.b % Sizes.Length], eM = new[] { 0f, 30f, 60f }[a.c % 3], eD = new[] { 0f, 12f, 24f }[a.c / 3 % 3];
                                float div = RSW_IonBuildupKernel.BodySizeDivisor(size, exp);
                                float amt = RSW_IonBuildupKernel.MachineAmount(mEn, live, hasRace, flesh, ionDef, machine, eM, eD, mMult, div);
                                double baseAmt = machine ? eM : eD;
                                double want = mEn && live && hasRace && !flesh && ionDef && baseAmt > 0 ? baseAmt * mMult / div : 0;
                                Check(Near(amt, want), $"MachineAmount {amt} vs {want}");
                                Check(amt >= 0f, "negative EMP");
                                if (flesh) Check(amt == 0f, "flesh took the machine tier");
                                if (amt > 0f && count) { if (machine) Machines++; else Droids++; }
                                bool shield = RSW_IonBuildupKernel.ShieldBreaks(sEn, live, (a.b & 2) != 0, (a.b & 4) != 0);
                                Check(shield == (sEn && live && (a.b & 2) == 0 && (a.b & 4) != 0), "ShieldBreaks");
                                if (shield && count) Shields++;
                                // a bigger target never takes a bigger stun
                                if (amt > 0f && size > 0f) Check(RSW_IonBuildupKernel.MachineAmount(mEn, live, hasRace, flesh, ionDef, machine, eM, eD, mMult, RSW_IonBuildupKernel.BodySizeDivisor(size * 2f, exp)) <= amt + 1e-6f, "a bigger machine took a bigger stun");
                                break;
                            }
                    }
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> Tables()
        {
            var fails = new List<string>();
            try
            {
                for (int m = 0; m < 128; m++)
                    Check(RSW_IonBuildupKernel.FleshBuildupApplies((m & 1) != 0, (m & 2) != 0, (m & 4) != 0, (m & 8) != 0, (m & 16) != 0, (m & 32) != 0, (m & 64) != 0) == ((m & 1) != 0 && (m & 2) != 0 && (m & 4) == 0 && (m & 8) != 0 && (m & 16) != 0 && (m & 32) == 0 && (m & 64) != 0), $"FleshBuildupApplies({m})");
                for (int m = 0; m < 16; m++)
                    Check(RSW_IonBuildupKernel.ShieldBreaks((m & 1) != 0, (m & 2) != 0, (m & 4) != 0, (m & 8) != 0) == ((m & 1) != 0 && (m & 2) != 0 && (m & 4) == 0 && (m & 8) != 0), $"ShieldBreaks({m})");
                // a rat takes 25x a human's buildup and a behemoth 1/1024 at the shipped exponent
                float human = RSW_IonBuildupKernel.FleshSeverity(10f, 0f, 0f, 1f, RSW_IonBuildupKernel.BodySizeDivisor(1f, 2f));
                float rat = RSW_IonBuildupKernel.FleshSeverity(10f, 0f, 0f, 1f, RSW_IonBuildupKernel.BodySizeDivisor(0.2f, 2f));
                float behemoth = RSW_IonBuildupKernel.FleshSeverity(10f, 0f, 0f, 1f, RSW_IonBuildupKernel.BodySizeDivisor(32f, 2f));
                Check(Near(rat, 250.0) && Near(human, 10.0) && Near(behemoth, 10.0 / 1024.0), "the live-measured 250 / 10 / 0.0098 severities");
                // machine tier anchors: a droid at size 1 takes 24, a mech 60; a footprint of 3x3 spreads 24 over nine
                Check(RSW_IonBuildupKernel.MachineAmount(true, true, true, false, true, false, 60f, 24f, 1f, 1f) == 24f && RSW_IonBuildupKernel.MachineAmount(true, true, true, false, true, true, 60f, 24f, 1f, 1f) == 60f, "machine / droid amounts");
                Check(RSW_IonBuildupKernel.VehicleStunTicks(true, true, true, true, true, 24f, 1, 1, 1f) == 720 && RSW_IonBuildupKernel.VehicleStunTicks(true, true, true, true, true, 24f, 3, 3, 1f) == 80, "vehicle stun anchors (24 EMP: 720 ticks on 1x1, 80 on 3x3)");
                Check(RSW_IonBuildupKernel.VehicleStunTicks(true, true, true, true, true, 24f, 0, 0, 1f) == 720, "a degenerate footprint counts as one cell");
                Check(RSW_IonBuildupKernel.VehicleStunTicks(false, true, true, true, true, 24f, 1, 1, 1f) == 0 && RSW_IonBuildupKernel.VehicleStunTicks(true, false, true, true, true, 24f, 1, 1, 1f) == 0 && RSW_IonBuildupKernel.VehicleStunTicks(true, true, false, true, true, 24f, 1, 1, 1f) == 0 && RSW_IonBuildupKernel.VehicleStunTicks(true, true, true, false, true, 24f, 1, 1, 1f) == 0 && RSW_IonBuildupKernel.VehicleStunTicks(true, true, true, true, false, 24f, 1, 1, 1f) == 0, "each vehicle gate");
            }
            catch (Exception e) { fails.Add("tables: " + e.Message); }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            bool tables = !oneSeed.HasValue && scale > 0;
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("size", () => { var f = SizeCases(N(20000), S(1)); if (tables) f.AddRange(Tables()); return f; }),
                ("flesh", () => Family("flesh", N(5000), S(1), new[] { 80, 8, 12 }, 20, 120, RunFlesh)),
                ("tiers", () => Family("tiers", N(5000), S(1), new[] { 55, 30, 15 }, 20, 120, RunTiers)),
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
            Console.WriteLine($"reached: third-party/flesh compositions {Composed}, deposits {Deposits}, skipped hits {Skipped}, machine stuns {Machines}, droid stuns {Droids}, vehicle stuns {Vehicles}, shield breaks {Shields}");
            if (!oneSeed.HasValue && scale >= 1)
            {
                bool all = only == null;
                if ((all || only == "size") && Composed == 0) { Console.WriteLine("FAIL size fuzz never composed the two size paths (blind)"); ok = false; }
                if ((all || only == "flesh") && (Deposits == 0 || Skipped == 0)) { Console.WriteLine("FAIL flesh fuzz never deposited or never skipped a hit (blind)"); ok = false; }
                if ((all || only == "tiers") && (Machines == 0 || Droids == 0 || Vehicles == 0 || Shields == 0)) { Console.WriteLine("FAIL tiers fuzz never stunned a machine / droid / vehicle or broke a shield (blind)"); ok = false; }
            }
            Console.WriteLine($"jawaionweapons fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
