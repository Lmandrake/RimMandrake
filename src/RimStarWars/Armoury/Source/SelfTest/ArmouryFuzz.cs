// Approach B for Armoury: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/RSW_ArmouryKernel.cs):
//   ion     the ion / stun damage workers: gate, victim kind, severity maths, hediff count, stun, stat probe laziness, on a pawn that accumulates hediffs
//   yield   the bonus mining yield: drop gate, weighted pick (exact on a roll grid, uniform at scale), stack size, miner credit
//   gear    the self-buff cooldown clock (use / tick sequences) and the mental-break blocker (exhaustive over causes, polarity and flags)
//   kolto   the kolto tank over a power / fuel / slider timeline: fill time, ejection, heal cadence, what a heal may remove
//   combat  jumppack gates (probe order), flank choice, emergency-heal timing, mine defusing, and the settings-derived numbers
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.StarWars.Armoury.SelfTest
{
    internal static class ArmouryFuzz
    {
        public static long Cases, Steps, Hediffs, Stuns, Drops, Picks, Heals, Ejects, Fills, Jumps, Flanks, Wicks, Defused, Cooldowns, Gated;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double rel = 1e-5) { return Math.Abs(a - b) <= rel * Math.Max(1.0, Math.Max(Math.Abs(a), Math.Abs(b))); }

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

        // ════════════════════════ ion ════════════════════════
        // kinds: 0 new pawn, 1 hit, 2 settings
        private static readonly float[] Fixeds = { 0f, 0.05f, 0.1f, 0.5f, 1f, 2f };
        private static readonly float[] Stats = { -0.5f, 0f, 0.25f, 0.5f, 1f, 1.5f };
        private static readonly float[] Sizes = { 0f, 0.1f, 0.5f, 1f, 1.5f, 3f, 8f };
        private static readonly float[] Strengths = { 0.25f, 0.5f, 1f, 1.5f, 2f, 3f };

        private static string RunIon(IList<Act> acts, int seed, bool count)
        {
            bool enabled = true; float strength = 1f;
            bool humanlike = false, animal = false, insect = false, mech = false, flesh = true, artificial = false; float size = 1f, stat = 0.5f;
            var added = new List<float>(); int stuns = 0, step = 0;
            try
            {
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    if (a.kind == 0)
                    {
                        int t = a.a % 6;
                        humanlike = t == 0; animal = t == 1; insect = t == 2; mech = t == 3 || t == 5; flesh = t <= 2; artificial = t == 4 || t == 5;
                        size = Sizes[a.b % Sizes.Length]; stat = Stats[a.c % Stats.Length]; added.Clear(); stuns = 0;
                        continue;
                    }
                    if (a.kind == 2) { enabled = (a.a & 7) != 0; strength = Strengths[a.b % Strengths.Length]; continue; }
                    int worker = a.a % 8;
                    bool ext = (a.b & 7) != 0, names = (a.b >> 3 & 7) != 0;
                    float fixedSev = Fixeds[a.c % Fixeds.Length]; bool resist = (a.c >> 4 & 3) != 0; float resistBase = (a.c >> 6 & 1) == 0 ? 1f : 0f;
                    bool bySize = (a.c >> 7 & 1) != 0, whole = (a.c >> 8 & 3) != 0; int parts = a.c >> 10 & 7;
                    bool applicable = worker == 0 ? humanlike : worker == 1 ? animal : worker == 2 ? insect : worker == 3 || worker == 5 ? mech : worker == 4 ? flesh : (mech || artificial);
                    bool stunWorker = worker == 5 || worker == 6;
                    int probes = 0;
                    RSW_IonKernel.Plan plan = RSW_IonKernel.Decide(enabled, ext, names, applicable, stunWorker, fixedSev, strength, resist, resistBase, () => { probes++; return stat; }, bySize, size, whole, parts);
                    // spec
                    bool gate = enabled && ext && names, applies = gate && applicable;
                    double sev = 0; int want = 0;
                    if (applies)
                    {
                        sev = (double)fixedSev * strength;
                        if (resist) sev = resistBase > 0 ? sev * stat : sev * (1.0 - stat);
                        if (sev > 0 && bySize && size > 0) sev /= size;
                        if (sev > 0) want = whole ? 1 : parts;
                    }
                    Check(plan.Gate == gate && plan.Applies == applies, $"gate/applies {plan.Gate}/{plan.Applies} vs {gate}/{applies}");
                    Check(plan.Hediffs == want, $"hediff count {plan.Hediffs} vs {want}");
                    Check(plan.Stun == (applies && stunWorker), $"stun {plan.Stun} vs {applies && stunWorker}");
                    if (applies) Check(Near(plan.Severity, Math.Max(0, sev)) || (sev <= 0 && plan.Severity <= 0f), $"severity {plan.Severity} vs {sev}");
                    else Check(plan.Severity == 0f && plan.Hediffs == 0 && !plan.Stun, "a victim that does not qualify got an effect");
                    Check(probes == (applies && resist ? 1 : 0), $"resistance stat read {probes} times (want {(applies && resist ? 1 : 0)})");
                    Check(!float.IsNaN(plan.Severity) && !float.IsInfinity(plan.Severity), "severity is not finite");
                    if (!enabled) Check(plan.Hediffs == 0 && !plan.Stun, "mechanic off but the hit disabled something");
                    if (plan.Hediffs > 0) Check(plan.Severity > 0f, "a hediff with severity <= 0");
                    for (int h = 0; h < plan.Hediffs; h++) added.Add(plan.Severity);
                    if (plan.Stun) stuns++;
                    if (count) { Hediffs += plan.Hediffs; if (plan.Stun) Stuns++; if (!gate) Gated++; }
                    Check(added.All(x => x > 0f), "pawn carries a non-positive hediff");
                    // a stronger setting never weakens the effect when the stat does not invert it
                    if (applies && plan.Severity > 0f && !resist)
                    {
                        RSW_IonKernel.Plan more = RSW_IonKernel.Decide(enabled, ext, names, applicable, stunWorker, fixedSev, strength * 2f, false, 1f, () => 0f, bySize, size, whole, parts);
                        Check(more.Severity >= plan.Severity, "doubling the strength lowered the severity");
                    }
                    Check(RSW_IonKernel.OrganicStun(enabled, flesh) == (enabled && flesh), "OrganicStun");
                    Check(RSW_IonKernel.PlasmaFires(enabled, flesh) == (enabled && flesh), "PlasmaFires");
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        // ════════════════════════ yield ════════════════════════
        // kinds: 0 mine, 1 settings, 2 new rock
        private static readonly float[] Chances = { 0f, 0.25f, 0.5f, 1f, 1.5f };
        private static readonly float[] ChanceScales = { 0f, 0.5f, 1f, 3f };
        private static readonly float[] Rolls = { 0f, 1f / 64, 0.25f, 0.5f, 33f / 64, 0.75f, 63f / 64, 1f };

        private static int SpecPick(int[] w, double r)
        {
            int s = w.Sum(); if (s <= 0) return -1;
            double t = r * s; int cum = 0, last = -1;
            for (int i = 0; i < w.Length; i++) { if (w[i] <= 0) continue; last = i; cum += w[i]; if (t < cum) return i; }
            return last;
        }

        private static int SpecRoundQuarters(int q) { int r = q / 4, rem = q % 4; return rem > 2 ? r + 1 : rem == 2 ? r + (r % 2) : r; }

        private static string RunYield(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x2545f491);
            int n = 1 + rr.Next(4);
            var w = new int[n]; for (int i = 0; i < n; i++) w[i] = rr.Next(5) == 0 ? 0 : 1 + rr.Next(6);
            var eff = new int[n]; var waste = new bool[n]; for (int i = 0; i < n; i++) { eff[i] = rr.Next(7); waste[i] = rr.Next(2) == 0; }
            float chance = 1f, cscale = 1f; int amountQ = 4; bool enabled = true; float yieldPct = 1f;
            var wf = w.Select(x => (float)x).ToList();
            int step = 0, drops = 0, expectedDrops = 0; var tally = new int[n];
            try
            {
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    if (a.kind == 1) { chance = Chances[a.a % Chances.Length]; cscale = ChanceScales[a.b % ChanceScales.Length]; amountQ = 1 + a.c % 12; yieldPct = (1 + a.a % 8) / 8f; enabled = (a.b & 8) != 0 || a.f; continue; }
                    if (a.kind == 2) { for (int i = 0; i < n; i++) { eff[i] = (a.a >> i) % 7; waste[i] = (a.b >> i & 1) != 0; } continue; }
                    float roll1 = Rolls[a.a % Rolls.Length], roll2 = Rolls[a.b % Rolls.Length];
                    // the postfix: setting gate first, then the drop gate, then the pick
                    bool dropped = enabled && RSW_YieldKernel.Drops(roll1, chance, cscale);
                    double p = (double)chance * cscale;
                    bool wantDrop = enabled && p > 0 && roll1 <= p;
                    Check(dropped == wantDrop, $"Drops({roll1}, {chance}x{cscale}) = {dropped} vs {wantDrop}");
                    if (!dropped) continue;
                    expectedDrops++;
                    int pick = RSW_YieldKernel.Pick(wf, roll2), want = SpecPick(w, roll2);
                    Check(pick == want, $"Pick(roll {roll2}, w [{string.Join(",", w)}]) = {pick} vs {want}");
                    if (pick < 0) { Check(w.Sum() == 0, "no pick although weight exists"); continue; }
                    Check(w[pick] > 0, "picked a zero-weight entry");
                    drops++; tally[pick]++; if (count) { Drops++; Picks++; }
                    float amount = amountQ / 4f;
                    var args = new List<float>();
                    int cnt = RSW_YieldKernel.Count(eff[pick], amount, waste[pick], yieldPct, x => { args.Add(x); return (int)Math.Floor(x) + (a.f ? 1 : 0); });
                    int baseCount = Math.Max(1, SpecRoundQuarters(eff[pick] * amountQ));
                    if (!waste[pick]) { Check(cnt == baseCount && args.Count == 0, $"Count {cnt} vs {baseCount}"); }
                    else
                    {
                        Check(args.Count == 1 && Near(args[0], baseCount * yieldPct), $"wasteable rounding got {(args.Count == 1 ? args[0].ToString() : "none")} vs {baseCount * yieldPct}");
                        Check(cnt == Math.Max(1, (int)Math.Floor(baseCount * yieldPct) + (a.f ? 1 : 0)) || cnt == Math.Max(1, (int)Math.Floor(args[0]) + (a.f ? 1 : 0)), $"wasteable count {cnt}");
                    }
                    Check(cnt >= 1, "a bonus find of fewer than one item");
                }
                Check(drops == expectedDrops || w.Sum() == 0, "drops lost between the gate and the pick");
                for (int i = 0; i < n; i++) if (w[i] == 0) Check(tally[i] == 0, "zero-weight entry was dropped");
                // credit gate: exhaustive
                for (int m = 0; m < 64; m++)
                {
                    bool got = RSW_YieldKernel.CreditsMiner((m & 1) != 0, (m & 2) != 0, (m & 4) != 0, (m & 8) != 0, (m & 16) != 0, (m & 32) != 0);
                    bool wantC = (m & 1) != 0 && (m & 2) == 0 && (m & 4) == 0 && (m & 8) != 0 && (m & 16) != 0 && (m & 32) != 0;
                    Check(got == wantC, $"CreditsMiner({m})");
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        private static List<string> YieldTables()
        {
            var fails = new List<string>();
            try
            {
                // exact pick over a grid of weights and rolls, monotone in the roll
                var rnd = new Random(7);
                for (int c = 0; c < 400; c++)
                {
                    int n = 1 + rnd.Next(6); var w = new int[n]; for (int i = 0; i < n; i++) w[i] = rnd.Next(4) == 0 ? 0 : 1 + rnd.Next(5);
                    var wf = w.Select(x => (float)x).ToList(); int prev = -1;
                    for (int k = 0; k <= 64; k++)
                    {
                        float r = k / 64f; int got = RSW_YieldKernel.Pick(wf, r), want = SpecPick(w, r);
                        Check(got == want, $"Pick grid w [{string.Join(",", w)}] roll {r}: {got} vs {want}");
                        Check(got >= prev || got < 0, "Pick not monotone in the roll"); if (got >= 0) prev = got; Steps++;
                    }
                    Check(RSW_YieldKernel.Pick(wf, 0f) >= 0 || w.Sum() == 0, "roll 0 found no entry although weight exists");
                    Check(RSW_YieldKernel.Pick(wf, 1f) >= 0 || w.Sum() == 0, "roll 1 found no entry although weight exists");
                }
                Check(RSW_YieldKernel.Pick(new float[0], 0.5f) == -1 && RSW_YieldKernel.Pick(new float[] { 0f, 0f }, 0.5f) == -1, "no weight, no pick");
                Check(RSW_YieldKernel.Pick(new float[] { 1f, -3f, 1f }, 0.9f) == 2 && RSW_YieldKernel.Pick(new float[] { 1f, -3f, 1f }, 0.1f) == 0, "a negative weight counts as zero");
                Check(RSW_YieldKernel.Pick(new float[] { -3f, 1f, 1f }, 0.1f) == 1 && RSW_YieldKernel.Pick(new float[] { -3f, 1f, 1f }, 0.6f) == 2 && RSW_YieldKernel.Pick(new float[] { -3f, -3f, 1f }, 0.5f) == 2, "a leading negative weight must not swallow the roll");
                // uniformity at scale: frequency tracks weight
                var weights = new float[] { 1f, 3f, 0f, 2f, 4f }; var cnt = new int[5]; int N = 300000; var rr = new Random(11);
                for (int k = 0; k < N; k++) { cnt[RSW_YieldKernel.Pick(weights, (float)rr.NextDouble())]++; Steps++; }
                for (int i = 0; i < 5; i++) Check(Math.Abs(cnt[i] / (double)N - weights[i] / 10.0) < 0.006, $"entry {i} chosen {cnt[i] / (double)N:F4} of the time, not {weights[i] / 10.0:F4}");
                // Drops: statistical and exact boundaries
                Check(!RSW_YieldKernel.Drops(0f, 0f, 3f) && !RSW_YieldKernel.Drops(0f, 1f, 0f) && !RSW_YieldKernel.Drops(1f, 0f, 1f), "a zero chance dropped");
                Check(RSW_YieldKernel.Drops(1f, 1f, 1f) && RSW_YieldKernel.Drops(0f, 1f, 1f) && RSW_YieldKernel.Drops(0.5f, 0.5f, 1f) && !RSW_YieldKernel.Drops(0.51f, 0.5f, 1f), "Drops boundaries");
                // Count anchors
                Check(RSW_YieldKernel.Count(0, 3f, false, 1f, null) == 1 && RSW_YieldKernel.Count(1, 0.25f, false, 1f, null) == 1 && RSW_YieldKernel.Count(10, 0.25f, false, 1f, null) == 2 && RSW_YieldKernel.Count(10, 1.5f, false, 1f, null) == 15 && RSW_YieldKernel.Count(2, 0.25f, false, 1f, null) == 1, "Count anchors (ties to even: 2.5 -> 2)");
                Check(RSW_YieldKernel.Count(1, 1f, true, 0f, x => 0) == 1, "wasteable yield of nothing still gives one");
            }
            catch (Exception e) { fails.Add("yield tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ gear ════════════════════════
        // kinds: 0 tick, 1 use attempt, 2 tick many, 3 slider
        private static string RunGear(IList<Act> acts, int seed, bool count)
        {
            int remain = RSW_GearKernel.Idle; int scaleQ = 4; int step = 0;
            int model = -1;     // independent model: -1 idle, else ticks still to wait
            try
            {
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    int ticks = a.kind == 0 ? 1 : a.kind == 2 ? 1 + a.a % 200 : 0;
                    for (int t = 0; t < ticks; t++) { remain = RSW_GearKernel.Tick(remain); if (model >= 0) model--; }
                    if (a.kind == 3) scaleQ = 1 + a.a % 12;
                    if (a.kind == 1)
                    {
                        int cd = new[] { 0, 1, 2, 60, 600, 2500, 12000 }[a.b % 7];
                        bool can = RSW_GearKernel.CanUse(remain);
                        Check(can == (model < 0), $"CanUse {can} at remain {remain} / model {model}");
                        if (can)
                        {
                            remain = RSW_GearKernel.AfterUse(cd, scaleQ / 4f);
                            model = Math.Max(0, SpecRoundQuarters(cd * scaleQ)); if (count) Cooldowns++;
                            Check(remain == model, $"AfterUse({cd}, {scaleQ / 4f}) = {remain} vs {model}");
                        }
                        else Check(remain == model, "a rejected use changed the clock");
                    }
                    Check(remain == model, $"clock {remain} vs model {model}");
                    Check(remain >= -1, "clock below idle");
                    Check(RSW_GearKernel.CanUse(remain) == (remain < 0), "CanUse disagrees with the clock");
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        private static List<string> GearTables()
        {
            var fails = new List<string>();
            try
            {
                for (int cause = 0; cause < 8; cause++)
                    for (int wl = 0; wl < 2; wl++)
                        for (int fl = 0; fl < 8; fl++)
                        {
                            bool mood = (fl & 1) != 0, dmg = (fl & 2) != 0, psy = (fl & 4) != 0;
                            bool hit = ((cause & 1) != 0 && mood) || ((cause & 2) != 0 && dmg) || ((cause & 4) != 0 && psy);
                            bool want = wl == 1 ? !hit : hit;
                            bool got = RSW_GearKernel.IsBlocked(cause, wl == 1, mood, dmg, psy);
                            Check(got == want, $"IsBlocked(cause {cause}, whitelist {wl == 1}, flags {fl}) = {got} vs {want}");
                            Check(got != RSW_GearKernel.IsBlocked(cause, wl != 1, mood, dmg, psy), "whitelist and blacklist are not complements");
                            Steps++;
                        }
                // the cooldown can never be negative, whatever a slider or a def says
                Check(RSW_GearKernel.AfterUse(60, -1f) == 0 && RSW_GearKernel.AfterUse(-5, 1f) == 0 && RSW_GearKernel.AfterUse(0, 3f) == 0 && RSW_GearKernel.AfterUse(60, 0.25f) == 15, "AfterUse bounds");
                // the shipped use: whitelist of mood+damage lets mood and damage breaks through, blocks the rest (psycast, drug, none)
                Check(!RSW_GearKernel.IsBlocked(3, true, true, false, false) && !RSW_GearKernel.IsBlocked(3, true, false, true, false) && RSW_GearKernel.IsBlocked(3, true, false, false, true) && RSW_GearKernel.IsBlocked(3, true, false, false, false), "shipped whitelist moodAndDamage");
                // enum value 'anyway' (0): blocks nothing as a blacklist and everything as a whitelist
                Check(!RSW_GearKernel.IsBlocked(0, false, true, true, true) && RSW_GearKernel.IsBlocked(0, true, true, true, true), "cause 0 behaviour");
            }
            catch (Exception e) { fails.Add("gear tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ kolto ════════════════════════
        // kinds: 0 enter, 1 tick burst, 2 power/fuel toggle, 3 sliders, 4 add hediff
        private enum HK { Fresh, Perm, Chronic, Blood, Implant, Uncurable }

        private static bool SpecCurable(HK k) { return k == HK.Fresh || k == HK.Chronic || k == HK.Blood; }

        private static bool KernelWill(HK k)
        {
            // how the comp maps a hediff onto the kernel's inputs
            bool injury = k == HK.Fresh || k == HK.Perm, perm = k == HK.Perm;
            return RSW_KoltoKernel.WillHeal(true, k != HK.Uncurable, k == HK.Implant, k == HK.Chronic, k == HK.Blood, injury, perm);
        }

        private static string RunKolto(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x51ed270b);
            float fillSpeed = new[] { 0.01f, 0.02f, 0.05f, 0.25f, 0.5f, 1f }[rr.Next(6)];
            float mult = new[] { 0f, 0.5f, 1f, 2.5f }[rr.Next(4)];
            int shipped = RSW_KoltoKernel.TicksBetweenHealing(mult);
            int mode = rr.Next(3);     // 0 power trader, 1 plain power comp, 2 neither
            bool powerOn = true, fuel = true, healOn = true, hasFuelComp = rr.Next(4) != 0; float speed = 1f;
            int state = RSW_KoltoKernel.Empty; float fill = 0f; bool occupant = false; int t = rr.Next(100000), sinceEnter = 0, step = 0;
            var hed = new List<HK>();
            try
            {
                Check(shipped == (mult > 0f ? (int)Math.Round(2500 * mult) : 2500), $"TicksBetweenHealing({mult}) = {shipped}");
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                // TryAcceptThing: refuses without power or fuel
                                bool power = mode == 2 || powerOn, ok = !occupant && power && (!hasFuelComp || fuel);
                                if (ok) { occupant = true; state = RSW_KoltoKernel.StartFilling; fill = 0f; sinceEnter = 0; hed.Clear(); for (int i = 0; i < a.b % 6; i++) hed.Add((HK)((a.b >> (3 + i)) % 6)); }
                                break;
                            }
                        case 2: powerOn = (a.a & 3) != 0; fuel = (a.b & 3) != 0; break;
                        case 3: speed = (1 + a.a % 12) / 4f; healOn = (a.b & 3) != 0; break;
                        case 4: hed.Add((HK)(a.a % 6)); break;
                        case 1:
                            {
                                int burst = 1 + a.a % 120;
                                for (int i = 0; i < burst; i++)
                                {
                                    t++;
                                    if (!occupant) continue;
                                    bool hasFuel = !hasFuelComp || fuel;
                                    bool hasPower = RSW_KoltoKernel.HasPower(mode == 0, powerOn, mode == 1, powerOn);
                                    Check(hasPower == (mode == 2 || powerOn), "HasPower disagrees with the three-way rule");
                                    int before = state; float fb = fill;
                                    var outcome = RSW_KoltoKernel.Step(ref state, ref fill, fillSpeed, hasFuel, hasPower);
                                    bool wantEject = !hasFuel || !hasPower;
                                    Check((outcome == RSW_KoltoKernel.Outcome.Eject) == wantEject, $"Step outcome {outcome} with fuel {hasFuel} power {hasPower}");
                                    if (wantEject)
                                    {
                                        Check(state == before && fill == fb, "a tank that ejects must leave its state to the ejector");
                                        occupant = false; state = RSW_KoltoKernel.Empty; fill = 0f; if (count) Ejects++;
                                        continue;
                                    }
                                    sinceEnter++;
                                    if (before == RSW_KoltoKernel.StartFilling)
                                    {
                                        if (state == RSW_KoltoKernel.Full) { Check(fill == 1f, "full tank not at fill 1"); Check(sinceEnter >= Math.Ceiling(1.0 / fillSpeed - 1e-3) - 1 && sinceEnter <= Math.Ceiling(1.0 / fillSpeed + 1e-3) + 1, $"filled in {sinceEnter} ticks at speed {fillSpeed}"); if (count) Fills++; }
                                        else Check(fill < 1f && fill > fb, "a filling tank did not advance, or overshot without becoming full");
                                    }
                                    else if (before == RSW_KoltoKernel.Full) Check(state == RSW_KoltoKernel.Full && fill == 1f, "a full tank changed");
                                    // heal only from a tank that was already full at the start of the tick
                                    int interval = RSW_KoltoKernel.HealInterval(shipped, speed);
                                    bool due = before == RSW_KoltoKernel.Full && RSW_KoltoKernel.HealDue(healOn, t, interval, occupant);
                                    Check(due == (before == RSW_KoltoKernel.Full && healOn && t % interval == 0), $"HealDue at tick {t} interval {interval}");
                                    if (due)
                                    {
                                        int idx = hed.FindIndex(KernelWill);
                                        int specIdx = hed.FindIndex(SpecCurable);
                                        Check(idx == specIdx, "the kernel's heal list disagrees with the spec's (first curable)");
                                        if (idx >= 0) { hed.RemoveAt(idx); if (count) Heals++; }
                                    }
                                    Check(hed.Count(k => k == HK.Implant || k == HK.Perm || k == HK.Uncurable) == hed.Count(k => !SpecCurable(k)), "bookkeeping");
                                }
                                break;
                            }
                    }
                    // invariants after every action
                    if (!occupant) Check(state == RSW_KoltoKernel.Empty && fill == 0f, "empty tank has a state or a fill");
                    else if (state == RSW_KoltoKernel.StartFilling) Check(fill >= 0f && fill < 1f, $"filling tank at fill {fill}");
                    else Check(state == RSW_KoltoKernel.Full && fill == 1f, $"occupied tank in state {state} at fill {fill}");
                    Check(RSW_KoltoKernel.HealInterval(shipped, speed) >= 1, "interval under a tick");
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        private static List<string> KoltoTables()
        {
            var fails = new List<string>();
            try
            {
                // WillHeal exhaustive over its 7 inputs against the written rule
                for (int m = 0; m < 128; m++)
                {
                    bool hasDef = (m & 1) != 0, curable = (m & 2) != 0, implant = (m & 4) != 0, chronic = (m & 8) != 0, blood = (m & 16) != 0, injury = (m & 32) != 0, perm = (m & 64) != 0;
                    bool want = hasDef && curable && !implant && (chronic || blood || (injury && !perm));
                    Check(RSW_KoltoKernel.WillHeal(hasDef, curable, implant, chronic, blood, injury, perm) == want, $"WillHeal({m})");
                    Steps++;
                }
                // intervals
                Check(RSW_KoltoKernel.TicksBetweenHealing(2.5f) == 6250 && RSW_KoltoKernel.TicksBetweenHealing(0f) == 2500 && RSW_KoltoKernel.TicksBetweenHealing(-1f) == 2500, "TicksBetweenHealing anchors (shipped tank: 6250)");
                Check(RSW_KoltoKernel.HealInterval(6250, 1f) == 6250 && RSW_KoltoKernel.HealInterval(6250, 2f) == 3125 && RSW_KoltoKernel.HealInterval(6250, 0.25f) == 25000 && RSW_KoltoKernel.HealInterval(1, 3f) == 1 && RSW_KoltoKernel.HealInterval(6250, 0f) == 625000, "HealInterval anchors");
                int prev = int.MaxValue;
                for (int q = 1; q <= 12; q++) { int v = RSW_KoltoKernel.HealInterval(6250, q / 4f); Check(v <= prev && v >= 1, "faster slider gave a longer interval"); prev = v; }
                Check(RSW_KoltoKernel.Fits(1f, 1f, 1f) && RSW_KoltoKernel.Fits(0.5f, 0.5f, 3f) && RSW_KoltoKernel.Fits(3f, 0.5f, 3f) && !RSW_KoltoKernel.Fits(3.01f, 0.5f, 3f) && !RSW_KoltoKernel.Fits(0.49f, 0.5f, 3f), "body size band is inclusive at both ends");
                // Step: only a filling tank fills; an empty or full one is left alone; power: the trader outranks the plain comp
                {
                    int st = RSW_KoltoKernel.Empty; float fl = 0f;
                    Check(RSW_KoltoKernel.Step(ref st, ref fl, 0.5f, true, true) == RSW_KoltoKernel.Outcome.None && st == RSW_KoltoKernel.Empty && fl == 0f, "an empty tank filled");
                    st = RSW_KoltoKernel.Full; fl = 1f;
                    Check(RSW_KoltoKernel.Step(ref st, ref fl, 0.5f, true, true) == RSW_KoltoKernel.Outcome.None && st == RSW_KoltoKernel.Full && fl == 1f, "a full tank changed");
                    Check(!RSW_KoltoKernel.HasPower(true, false, true, true) && RSW_KoltoKernel.HasPower(true, true, true, false) && RSW_KoltoKernel.HasPower(false, false, true, true) && !RSW_KoltoKernel.HasPower(false, true, true, false) && RSW_KoltoKernel.HasPower(false, false, false, false), "HasPower precedence");
                }
                Check(RSW_KoltoKernel.Empty == 0 && RSW_KoltoKernel.StartFilling == 1 && RSW_KoltoKernel.Full == 2, "state numbering");
                Check(!RSW_KoltoKernel.HealDue(false, 0, 10, true) && !RSW_KoltoKernel.HealDue(true, 0, 10, false) && RSW_KoltoKernel.HealDue(true, 20, 10, true) && !RSW_KoltoKernel.HealDue(true, 21, 10, true), "HealDue");
            }
            catch (Exception e) { fails.Add("kolto tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ combat ════════════════════════
        // kinds: 0 melee jump, 1 flank, 2 emergency heal, 3 defuse, 4 settings
        private static readonly float[] Blocks = { 0f, 0.1f, 0.29f, 0.3f, 0.31f, 0.7f, 1f };
        private static readonly float[] Dist = { 0f, 0.25f, 1f, 2f, 3f };

        private static string RunCombat(IList<Act> acts, int seed, bool count)
        {
            bool enabled = true, flank = true; float distF = 1f; float reuseH = 8f, harmH = 1f; float defTime = 1f; int step = 0;
            try
            {
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 4: enabled = (a.a & 7) != 0; flank = (a.a & 8) != 0 || a.f; distF = Dist[a.b % Dist.Length] == 0f ? 0.25f : Dist[a.b % Dist.Length]; reuseH = a.c % 25; harmH = 0.1f + (a.c >> 5 & 15) * 0.4f; defTime = (1 + a.b % 20) / 4f; break;
                        case 0:
                            {
                                bool human = (a.a & 1) != 0 || (a.a & 6) == 0, colonist = (a.a & 8) != 0 && (a.a & 48) == 0;
                                bool target = (a.a & 64) != 0 || (a.b & 3) != 0, melee = (a.b & 4) != 0 || a.f, reach = (a.b & 8) != 0 && (a.b & 48) == 0, jumpVerb = (a.b & 64) != 0 || (a.c & 1) != 0;
                                float shipped = (a.c & 2) != 0 ? RSW_CombatKernel.MeleeJumpMinDistSq : RSW_CombatKernel.PatchMeleeJumpMinDistSq;
                                float d = (a.c >> 2 & 63) * 2f;      // squared distance 0..126
                                var probes = new List<string>();
                                bool got = RSW_CombatKernel.MeleeJump(enabled, human, colonist, () => { probes.Add("t"); return target; }, () => { probes.Add("m"); return melee; }, () => { probes.Add("r"); return reach; },
                                    () => { probes.Add("d"); return d; }, shipped, distF, () => { probes.Add("j"); return jumpVerb; });
                                var want = new List<string>(); bool wantRes;
                                if (!enabled || !human || colonist) wantRes = false;
                                else
                                {
                                    want.Add("t");
                                    if (!target) wantRes = false;
                                    else { want.Add("m"); if (!melee) wantRes = false; else { want.Add("r"); if (reach) wantRes = false; else { want.Add("d"); if (d < shipped * distF * distF) wantRes = false; else { want.Add("j"); wantRes = jumpVerb; } } } }
                                }
                                Check(got == wantRes, $"MeleeJump {got} vs {wantRes}");
                                Check(probes.SequenceEqual(want), $"jump probes [{string.Join(",", probes)}] vs [{string.Join(",", want)}]");
                                if (got && count) Jumps++;
                                // a farther threshold never grants a jump a nearer one refused
                                if (got) Check(d >= shipped * distF * distF, "jumped from inside the minimum range");
                                break;
                            }
                        case 1:
                            {
                                bool human = (a.a & 1) != 0 || (a.a & 6) == 0, colonist = (a.a & 8) != 0 && (a.a & 48) == 0;
                                int n = (a.b & 7) == 7 ? -1 : (a.b & 7) % 5;
                                var chances = n < 0 ? null : Enumerable.Range(0, n).Select(i => Blocks[(a.c >> (i * 3)) % Blocks.Length]).ToList();
                                bool got = RSW_CombatKernel.FlankWorthIt(enabled, flank, human, colonist, chances);
                                bool wantRes = enabled && flank && human && !colonist && chances != null && chances.Any(c => c >= 0.3f);
                                Check(got == wantRes, $"FlankWorthIt {got} vs {wantRes}");
                                if (got && count) Flanks++;
                                Check(RSW_CombatKernel.FlankSpot(true, true) == 0 && RSW_CombatKernel.FlankSpot(false, true) == 1 && RSW_CombatKernel.FlankSpot(true, false) == 0 && RSW_CombatKernel.FlankSpot(false, false) == -1, "FlankSpot prefers behind");
                                break;
                            }
                        case 2:
                            {
                                int now = 1000 + a.a % 100000;
                                int recent = RSW_CombatKernel.InstantHealRecentHarmTicks(harmH), reuse = RSW_CombatKernel.InstantHealReuseTicks(reuseH);
                                int harmAge = (a.b % 3 == 0) ? recent + (a.b >> 2) % 3 - 1 : (a.b % 3 == 1 ? (a.b >> 2) % 5000 : now + 99999);
                                int drugAge = (a.c % 3 == 0) ? reuse + (a.c >> 2) % 3 - 1 : (a.c % 3 == 1 ? (a.c >> 2) % 30000 : now + 99999);
                                bool vanilla = (a.a & 1) != 0 && (a.b & 8) != 0, plumbing = (a.c & 8) != 0 || a.f;
                                bool got = RSW_CombatKernel.InstantHealDue(enabled, vanilla, plumbing, now, now - harmAge, recent, now - drugAge, reuse);
                                bool wantRes = enabled && !vanilla && plumbing && harmAge <= recent && drugAge >= reuse;
                                Check(got == wantRes, $"InstantHealDue {got} vs {wantRes} (harm age {harmAge} of {recent}, drug age {drugAge} of {reuse})");
                                Check(RSW_CombatKernel.ForceOnlyInDanger(enabled, true, false) == enabled && RSW_CombatKernel.ForceOnlyInDanger(enabled, false, true) == true && RSW_CombatKernel.ForceOnlyInDanger(enabled, false, false) == false && RSW_CombatKernel.ForceOnlyInDanger(false, true, false) == false, "ForceOnlyInDanger keeps the original unless the mechanic forces it");
                                break;
                            }
                        case 3:
                            {
                                float[] ms = { 0f, 0.3f, 0.59f, 0.5999f, 0.6f, 0.61f, 1f, 1.5f };
                                float manip = ms[a.a % ms.Length];
                                var d = RSW_CombatKernel.DefuseOutcome(manip);
                                bool clumsy = manip < 0.6f;
                                Check(d.Wick == clumsy && d.Spawn == !clumsy && d.Destroy == !clumsy, $"DefuseOutcome({manip})");
                                Check(!(d.Wick && d.Destroy) && (d.Wick || d.Destroy), "defusing must either light the wick or remove the mine, never both and never neither");
                                if (count) { if (d.Wick) Wicks++; else Defused++; }
                                int ticks = RSW_CombatKernel.DefuseTicks(new[] { 60, 0, 120 }[a.b % 3], defTime);
                                Check(ticks >= 1, "defuse in under a tick");
                                Check(RSW_CombatKernel.DefuseTicks(60, 4f) >= RSW_CombatKernel.DefuseTicks(60, 1f) && RSW_CombatKernel.DefuseTicks(60, 1f) >= RSW_CombatKernel.DefuseTicks(60, 0.25f), "defuse time not monotone in the slider");
                                break;
                            }
                    }
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        private static List<string> CombatTables()
        {
            var fails = new List<string>();
            try
            {
                Check(RSW_CombatKernel.InstantHealReuseTicks(8f) == 20000 && RSW_CombatKernel.InstantHealRecentHarmTicks(1f) == 2500, "shipped emergency-heal ticks (20000 / 2500)");
                Check(RSW_CombatKernel.InstantHealReuseTicks(0f) == 0 && RSW_CombatKernel.InstantHealRecentHarmTicks(0f) == 1 && RSW_CombatKernel.InstantHealRecentHarmTicks(0.1f) == 250, "emergency-heal slider ends");
                Check(RSW_CombatKernel.ScaleSquaredDistance(16f, 1f) == 16f && RSW_CombatKernel.ScaleSquaredDistance(25f, 1f) == 25f && RSW_CombatKernel.ScaleSquaredDistance(16f, 2f) == 64f && RSW_CombatKernel.ScaleSquaredDistance(16f, 0.25f) == 1f, "squared distance scales with the square of the factor");
                Check(RSW_CombatKernel.DefuseTicks(60, 1f) == 60 && RSW_CombatKernel.DefuseTicks(60, 5f) == 300 && RSW_CombatKernel.DefuseTicks(60, 0.25f) == 15 && RSW_CombatKernel.DefuseTicks(0, 1f) == 1, "DefuseTicks anchors");
                Check(RSW_CombatKernel.MeleeJumpMinDistSq == 25f && RSW_CombatKernel.PatchMeleeJumpMinDistSq == 16f && RSW_CombatKernel.CoverWorthFlanking == 0.3f && RSW_CombatKernel.DefuseManipulationFloor == 0.6f, "shipped constants");
                Check(RSW_Num.RoundToInt(0.5f) == 0 && RSW_Num.RoundToInt(1.5f) == 2 && RSW_Num.RoundToInt(2.5f) == 2 && RSW_Num.RoundToInt(-0.5f) == 0, "RoundToInt rounds ties to even, like Mathf");
                // flank cover edge: exactly 0.3 counts as worth it; every cover under 0.3 does not
                Check(RSW_CombatKernel.FlankWorthIt(true, true, true, false, new[] { 0.3f }) && !RSW_CombatKernel.FlankWorthIt(true, true, true, false, new[] { 0.29f, 0.1f }) && !RSW_CombatKernel.FlankWorthIt(true, true, true, false, new float[0]), "flank cover threshold");
            }
            catch (Exception e) { fails.Add("combat tables: " + e.Message); }
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
                ("ion", () => Family("ion", N(5000), S(1), new[] { 4, 80, 8 }, 20, 120, RunIon)),
                ("yield", () => { var f = Family("yield", N(5000), S(1), new[] { 80, 10, 5 }, 20, 160, RunYield); if (!oneSeed.HasValue && scale > 0) f.AddRange(YieldTables()); return f; }),
                ("gear", () => { var f = Family("gear", N(5000), S(1), new[] { 40, 30, 20, 10 }, 20, 160, RunGear); if (!oneSeed.HasValue && scale > 0) f.AddRange(GearTables()); return f; }),
                ("kolto", () => { var f = Family("kolto", N(3000), S(1), new[] { 12, 50, 14, 8, 10 }, 20, 120, RunKolto); if (!oneSeed.HasValue && scale > 0) f.AddRange(KoltoTables()); return f; }),
                ("combat", () => { var f = Family("combat", N(5000), S(1), new[] { 30, 20, 25, 15, 10 }, 20, 160, RunCombat); if (!oneSeed.HasValue && scale > 0) f.AddRange(CombatTables()); return f; }),
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
            Console.WriteLine($"reached: hediffs {Hediffs}, stuns {Stuns}, gated-off hits {Gated}, bonus drops {Drops}, picks {Picks}, cooldowns {Cooldowns}, heals {Heals}, fills {Fills}, ejects {Ejects}, jumps {Jumps}, flanks {Flanks}, wicks {Wicks}, defuses {Defused}");
            if (!oneSeed.HasValue && scale >= 1)
            {
                bool all = only == null;
                if ((all || only == "ion") && (Hediffs == 0 || Stuns == 0 || Gated == 0)) { Console.WriteLine("FAIL ion fuzz never added a hediff / stun or never hit a gated-off case (blind)"); ok = false; }
                if ((all || only == "yield") && (Drops == 0 || Picks == 0)) { Console.WriteLine("FAIL yield fuzz never dropped or picked (blind)"); ok = false; }
                if ((all || only == "gear") && Cooldowns == 0) { Console.WriteLine("FAIL gear fuzz never started a cooldown (blind)"); ok = false; }
                if ((all || only == "kolto") && (Heals == 0 || Fills == 0 || Ejects == 0)) { Console.WriteLine("FAIL kolto fuzz never healed / filled / ejected (blind)"); ok = false; }
                if ((all || only == "combat") && (Jumps == 0 || Flanks == 0 || Wicks == 0 || Defused == 0)) { Console.WriteLine("FAIL combat fuzz never jumped / flanked / lit a wick / defused (blind)"); ok = false; }
            }
            Console.WriteLine($"armoury fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
