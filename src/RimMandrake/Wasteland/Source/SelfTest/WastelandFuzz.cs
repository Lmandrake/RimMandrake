// Approach B for Wasteland: seeded fuzz over the Verse-free kernels the Wasteland mod calls (../Kernel/*.cs):
//   cask     the waste cask + sealed cask bay (RM_WasteCaskKernel): breach, leak gating and pacing, seal charge, heat,
//            launch safety, the ship check, processing - action sequences against a spec ledger
//   storm    the named-storm phase machine and the storm layer gate (RM_StormKernel), the fresh-fall memory, fall and
//            germination counts
//   tipping  the Rite of Tipping contract (RM_TippingKernel): deliveries, misses, one-shot evidence / finance, discovery
//   dose     ambient dose falloff, gripper UnitsToTake, processor fullness (RM_DoseKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Wasteland.SelfTest
{
    internal static class WastelandFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        internal struct Act
        {
            public int kind, a, b;
            public string[] names;
            public override string ToString() { return (names != null && kind < names.Length ? names[kind] : "k" + kind) + "(" + a + "," + b + ")"; }
        }

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

        // Runs a generated action sequence; on failure shrinks it and returns "message | actions".
        private static string Drive(int seed, Func<Random, List<Act>> gen, Func<int, List<Act>, string> run)
        {
            var acts = gen(new Random(seed));
            string err = run(seed, acts);
            if (err == null) return null;
            var small = Shrink(acts, t => run(seed, t) != null);
            return run(seed, small) + " | " + string.Join(" ", small);
        }

        private static List<string> Family(string name, int n, int baseSeed, Func<int, string> one)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { string e = one(baseSeed + k); if (e != null) fails.Add($"{name} seed {baseSeed + k}: {e}"); }
                catch (Exception e) { fails.Add($"{name} seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }

        // ════════════════════════ cask ════════════════════════
        private static readonly string[] CaskNames = { "Tick", "BayDamage", "BayRepair", "Power", "AddCask", "RemoveCask", "CaskDamage", "Setting", "Process", "Ship", "Burst" };

        private sealed class CaskM { public float dose; public int hp, max; public int nextLeak = -1; public bool inBay; public int pulses; }

        public static long BayPulses, CaskPulses, Completions, Contained0;
        private static readonly float[] Drains = { 0.005f, 0.02f, 0.0625f, 0.125f, 0.25f };
        private static readonly float[] Regens = { 0.02f, 0.0625f, 0.125f, 0.5f };

        private static List<Act> GenCask(Random r)
        {
            int n = 10 + r.Next(60);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 40 ? 0 : w < 48 ? 1 : w < 54 ? 2 : w < 66 ? 3 : w < 76 ? 4 : w < 80 ? 5 : w < 86 ? 6 : w < 90 ? 7 : w < 94 ? 8 : w < 98 ? 9 : 10;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = CaskNames });
            }
            return l;
        }

        private static string RunCask(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x5a5a);
            float drain = Drains[r.Next(Drains.Length)], regen = Regens[r.Next(Regens.Length)];
            float thr = new[] { 0.25f, 0.5f, 0.75f }[r.Next(3)];
            float launchInt = thr + new[] { 0f, 0.25f }[r.Next(2)]; if (launchInt > 1f) launchInt = 1f;
            float hotLimit = new[] { 10f, 40f, 100f }[r.Next(3)];
            float pf = new[] { 0.25f, 0.5f, 1f }[r.Next(3)];
            float heatPerDose = new[] { 18f, 40f, 90f }[r.Next(3)];
            float leakFrac = new[] { 0.25f, 0.5f, 0.75f }[r.Next(3)];
            float dosePer = new[] { 0.05f, 0.1f, 0.25f }[r.Next(3)];
            int bayInterval = 2500, caskInterval = 2500;
            float perDay = new[] { 0.5f, 2f, 8f }[r.Next(3)];
            float sev = new[] { 0.5f, 1f, 2f }[r.Next(3)];
            int polCells = 1 + r.Next(8), gas = 20 * (1 + r.Next(9));

            int now = 1000, maxHp = 100, bayHp = 100;
            float charge = 1f, heat = 0f, procProgress = 0f; double specHeat = 0;
            int bayNext = -1;
            bool powered = true, wasteland = true, leaksOn = true, processing = false, processor = false;
            var casks = new List<CaskM>();
            int lastBayPulse = -1000000;
            string where = "";

            bool IsContained() { return RM_WasteCaskKernel.Contained(RM_WasteCaskKernel.SealIntegrity(charge, RM_WasteCaskKernel.HpFraction(bayHp, maxHp)), thr); }
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            for (int t = 0, nt = 1 + a.a % (a.b % 3 == 0 ? 160 : 8); t < nt; t++)
                            {
                                now += 250;
                                // each cask ticks
                                bool contained = IsContained();
                                foreach (var c in casks)
                                {
                                    bool breached = RM_WasteCaskKernel.Breached(true, c.hp, c.max, leakFrac, c.dose);
                                    bool leaking = RM_WasteCaskKernel.CaskLeaking(true, breached, wasteland, leaksOn, c.inBay, c.inBay && contained);
                                    // spec: leaks iff breached (hp below fraction, dose left) and the settings allow and no contained bay holds it
                                    bool specLeak = wasteland && leaksOn && c.hp < c.max * leakFrac && c.dose > 0f && !(c.inBay && contained);
                                    Check(leaking == specLeak, $"cask leak gate: kernel={leaking} spec={specLeak} (hp {c.hp}/{c.max} dose {c.dose} inBay={c.inBay} contained={contained})");
                                    if (c.inBay && contained) Check(!leaking, "a cask leaked inside a contained bay");
                                    Check(RM_WasteCaskKernel.LeakDue(c.nextLeak, now) == (c.nextLeak < 0 || now >= c.nextLeak), "cask LeakDue disagrees with nextLeak < 0 || now >= nextLeak");
                                    if (leaking && RM_WasteCaskKernel.LeakDue(c.nextLeak, now))
                                    {
                                        float before = c.dose;
                                        c.dose = RM_WasteCaskKernel.DoseAfterLeak(c.dose, dosePer);
                                        Check(c.dose >= 0f, "cask dose went negative");
                                        Check(c.dose == Math.Max(0f, before - dosePer), $"dose after leak {c.dose} != {Math.Max(0f, before - dosePer)}");
                                        Check(RM_WasteCaskKernel.PollutionCells(polCells, sev) >= 1, "a leak pulse polluted no cell");
                                        c.nextLeak = now + caskInterval; c.pulses++; CaskPulses++;
                                    }
                                }
                                // bay tick
                                float dose = 0f, heatTarget = 0f; int count = 0;
                                foreach (var c in casks) if (c.inBay) { count++; dose += RM_WasteCaskKernel.StoredDose(c.dose); heatTarget += RM_WasteCaskKernel.StoredDose(c.dose) * heatPerDose; }
                                float prevCharge = charge;
                                charge = RM_WasteCaskKernel.NextCharge(charge, powered, regen, drain);
                                float specCharge = powered ? (charge >= 1f && prevCharge + regen >= 1f ? 1f : Math.Min(1f, prevCharge + regen)) : Math.Max(0f, prevCharge - drain);
                                Check(charge == specCharge, $"seal charge {prevCharge} -> {charge}, spec {specCharge} (powered={powered})");
                                Check(charge >= 0f && charge <= 1f, "seal charge left [0,1]");
                                float target = RM_WasteCaskKernel.HeatTarget(heatTarget, powered, pf);
                                Check(target == (powered ? heatTarget * pf : heatTarget), $"heat target {target} != spec (powered={powered}, raw {heatTarget}, cooling {pf})");
                                float prevHeat = heat;
                                heat = RM_WasteCaskKernel.NextHeat(heat, target);
                                specHeat = specHeat + (target - specHeat) * 0.1;
                                // the float recurrence tracks the double one; compare to a tolerance
                                specHeat = heat; // re-anchor to the kernel's float so errors do not compound, then check one step from the previous
                                double stepSpec = prevHeat + (target - prevHeat) * 0.1;
                                Check(Math.Abs(heat - stepSpec) <= 1e-3 * Math.Max(1.0, Math.Abs(stepSpec)), $"heat {prevHeat} -> {heat}, one-step spec {stepSpec} (target {target})");
                                Check(heat >= 0f, "internal heat negative");
                                Check(heat <= Math.Max(prevHeat, target) + 1e-3f && heat >= Math.Min(prevHeat, target) - 1e-3f, "heat overshot between its previous value and its target");
                                Check(RM_WasteCaskKernel.PushesHeat(heat) == (heat > 1f), "PushesHeat disagrees with heat > 1");
                                bool contained2 = IsContained();
                                Check(RM_WasteCaskKernel.LeakDue(bayNext, now) == (bayNext < 0 || now >= bayNext), "bay LeakDue disagrees with nextLeak < 0 || now >= nextLeak");
                                bool specBay = wasteland && leaksOn && count > 0 && dose > 0f && !contained2;
                                bool bayLeaking = RM_WasteCaskKernel.BayLeaking(wasteland, leaksOn, count, dose, contained2);
                                Check(bayLeaking == specBay, $"bay leak gate: kernel={bayLeaking} spec={specBay} (count {count} dose {dose} contained={contained2})");
                                if (bayLeaking && RM_WasteCaskKernel.LeakDue(bayNext, now))
                                {
                                    Check(!contained2, "the bay pulsed while contained");
                                    Check(now - lastBayPulse >= bayInterval, $"bay pulses {now - lastBayPulse} ticks apart, interval {bayInterval}");
                                    lastBayPulse = now; bayNext = now + bayInterval; BayPulses++;
                                }
                                if (contained2) Contained0++;
                                // processing: a processor animal turns one cask into product when progress >= 1
                                if (wasteland && processing && count > 0 && processor)
                                {
                                    procProgress = RM_WasteCaskKernel.ProcessProgress(procProgress, perDay, 250, 60000);
                                    if (RM_WasteCaskKernel.ProcessDone(procProgress))
                                    {
                                        procProgress = 0f;
                                        var victim = casks.First(c => c.inBay);
                                        casks.Remove(victim); Completions++;
                                        Check(RM_WasteCaskKernel.ProcessedAmount(3f, 2f, 75) == 6, "processed amount of milk 3 x 2 is not 6");
                                    }
                                }
                                Check(procProgress >= 0f && procProgress < 1f + 1e-6f, "process progress out of range");
                            }
                            break;
                        case 1: bayHp = Math.Max(0, bayHp - a.a % (maxHp + 1)); break;
                        case 2: bayHp = maxHp; break;
                        case 3: powered = !powered; break;
                        case 4: if (casks.Count < 8) casks.Add(new CaskM { dose = (a.a % 21) / 20f, max = 100, hp = 20 + a.b % 81, inBay = a.b % 4 != 0 }); break;
                        case 5: if (casks.Count > 0) casks.RemoveAt(a.a % casks.Count); break;
                        case 6: if (casks.Count > 0) { var c = casks[a.a % casks.Count]; c.hp = Math.Max(0, c.hp - a.b % 80); } break;
                        case 7: if (a.a % 3 == 0) wasteland = !wasteland; else if (a.a % 3 == 1) leaksOn = !leaksOn; else sev = sev == 1f ? 2f : 1f; break;
                        case 8: if (a.a % 2 == 0) processing = !processing; else processor = !processor; break;
                        case 9: // ship check against an independent ladder
                            {
                                int bays = 1 + a.a % 3; var verdicts = new List<LaunchVerdict>();
                                var rr = new Random(a.a * 31 + a.b);
                                for (int i = 0; i < bays; i++)
                                {
                                    int cnt = rr.Next(3); bool pw = rr.Next(4) != 0; float integ = rr.Next(5) * 0.25f; float h = rr.Next(0, 130);
                                    var v = RM_WasteCaskKernel.LaunchSafety(cnt, pw, integ, launchInt, h, hotLimit);
                                    LaunchVerdict spec = cnt == 0 ? LaunchVerdict.Safe : !pw ? LaunchVerdict.NoPower : integ < launchInt ? LaunchVerdict.LowIntegrity : h > hotLimit ? LaunchVerdict.TooHot : LaunchVerdict.Safe;
                                    Check(v == spec, $"launch verdict {v} != spec {spec} (casks {cnt} powered {pw} integrity {integ}/{launchInt} heat {h}/{hotLimit})");
                                    if (v == LaunchVerdict.Safe && cnt > 0)
                                    {
                                        Check(pw && integ >= launchInt && h <= hotLimit, "Safe launch with casks aboard but an unmet condition");
                                        if (launchInt >= thr) Check(RM_WasteCaskKernel.Contained(integ, thr), "launch-safe bay would not be contained");
                                    }
                                    verdicts.Add(v);
                                }
                                int loose = rr.Next(3);
                                var sv = RM_WasteCaskKernel.CheckShip(verdicts, loose, out LaunchVerdict firstBad);
                                var firstSpec = verdicts.FirstOrDefault(v => v != LaunchVerdict.Safe);
                                ShipVerdict specShip = verdicts.Any(v => v != LaunchVerdict.Safe) ? ShipVerdict.UnsafeBay : loose > 0 ? ShipVerdict.LooseCask : ShipVerdict.Safe;
                                Check(sv == specShip, $"ship verdict {sv} != spec {specShip}");
                                if (sv == ShipVerdict.UnsafeBay) Check(firstBad == firstSpec, "ship check named the wrong first unsafe bay");
                                break;
                            }
                        case 10: // burst: a destroyed cask spills 4x pollution (>= 4 cells) and 3x gas, only when it has dose, a map and the settings
                            {
                                float d = (a.a % 3 == 0) ? 0f : (a.a % 21) / 20f;
                                bool bursts = RM_WasteCaskKernel.BurstsOnKill(a.b % 2 == 0, a.b % 5 != 0, d, wasteland, leaksOn);
                                bool spec = a.b % 2 == 0 && a.b % 5 != 0 && d > 0f && wasteland && leaksOn;
                                Check(bursts == spec, $"burst gate kernel={bursts} spec={spec}");
                                Check(RM_WasteCaskKernel.BurstCells(polCells, sev) >= 4, "burst polluted fewer than 4 cells");
                                Check(RM_WasteCaskKernel.BurstCells(polCells, sev) >= RM_WasteCaskKernel.PollutionCells(polCells, sev), "a burst polluted less than one leak pulse");
                                Check(RM_WasteCaskKernel.BurstGas(gas, sev) >= RM_WasteCaskKernel.GasAmount(gas, sev), "a burst released less gas than one leak pulse");
                                break;
                            }
                    }
                    foreach (var c in casks) { Check(c.dose >= 0f && c.dose <= 1f, "cask dose outside [0,1]"); Check(c.hp >= 0, "cask hp negative"); }
                }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        // Fixed unit truths of the cask kernel: rounding, capacity, liveness of the leak and the recovery.
        private static string CaskUnits(int seed)
        {
            // banker's rounding at exact halves (Mathf.RoundToInt semantics)
            foreach (var (cells, sev, want) in new[] { (1, 0.5f, 1), (3, 0.5f, 2), (5, 0.5f, 2), (7, 0.5f, 4), (4, 0.5f, 2), (1, 0.25f, 1), (3, 1f, 3) })
            {
                Steps++;
                int got = RM_WasteCaskKernel.PollutionCells(cells, sev);
                Check(got == Math.Max(1, want), $"PollutionCells({cells},{sev})={got}, want {Math.Max(1, want)}");
            }
            Check(RM_WasteCaskKernel.GasAmount(150, 0.5f) == 75 && RM_WasteCaskKernel.GasAmount(5, 0.5f) == 2, "GasAmount rounding");
            Check(RM_WasteCaskKernel.BurstCells(1, 1f) == 4 && RM_WasteCaskKernel.BurstCells(6, 2f) == 48 && RM_WasteCaskKernel.BurstCells(1, 0.5f) == 4, "BurstCells floor of 4");
            Check(RM_WasteCaskKernel.Capacity(2, 3, 0) == 6 && RM_WasteCaskKernel.Capacity(2, 3, 4) == 24, "Capacity min one per cell");
            for (int s = -3; s <= 9; s++) Check(RM_WasteCaskKernel.PerCell(s) == Math.Min(6, Math.Max(1, s)), $"PerCell({s})");
            Check(RM_WasteCaskKernel.HpFraction(5, 0) == 1f && RM_WasteCaskKernel.HpFraction(25, 100) == 0.25f, "HpFraction");
            Check(RM_WasteCaskKernel.CanRebury(true, true, false) && !RM_WasteCaskKernel.CanRebury(true, true, true) && !RM_WasteCaskKernel.CanRebury(true, false, false) && !RM_WasteCaskKernel.CanRebury(false, true, false), "CanRebury truth table");
            // breach boundary: strictly below the fraction, never without dose or hit points
            Check(!RM_WasteCaskKernel.Breached(true, 50, 100, 0.5f, 1f), "exactly at the leak fraction must not be breached");
            Check(RM_WasteCaskKernel.Breached(true, 49, 100, 0.5f, 1f), "just below the leak fraction must be breached");
            Check(!RM_WasteCaskKernel.Breached(true, 1, 100, 0.5f, 0f) && !RM_WasteCaskKernel.Breached(true, 1, 100, 0.5f, -0.5f), "an empty cask cannot be breached");
            Check(!RM_WasteCaskKernel.Breached(false, 1, 100, 0.5f, 1f), "a def with no hit points is never breached");
            // seal drain liveness: an unpowered full bay with casks must be leaking within ceil((1 - thr) / drain) + 1 ticks
            var r = new Random(seed);
            foreach (float drain in Drains) foreach (float thr in new[] { 0.25f, 0.5f, 0.75f })
            {
                float c = 1f; int ticks = 0;
                while (RM_WasteCaskKernel.Contained(RM_WasteCaskKernel.SealIntegrity(c, 1f), thr) && ticks < 100000) { c = RM_WasteCaskKernel.NextCharge(c, false, 0.02f, drain); ticks++; }
                Steps += ticks;
                int bound = (int)Math.Ceiling((1f - thr) / drain) + 2;
                Check(ticks <= bound && ticks >= 1, $"unpowered bay (drain {drain}, thr {thr}) took {ticks} ticks to lose containment, bound {bound}");
                Check(RM_WasteCaskKernel.BayLeaking(true, true, 1, 0.1f, false), "an uncontained bay with dose must leak");
                // recovery: a powered bay at 0 charge is contained again within ceil(thr / regen) + 1 ticks
                foreach (float regen in Regens)
                {
                    float c2 = 0f; int t2 = 0;
                    while (!RM_WasteCaskKernel.Contained(RM_WasteCaskKernel.SealIntegrity(c2, 1f), thr) && t2 < 100000) { c2 = RM_WasteCaskKernel.NextCharge(c2, true, regen, drain); t2++; }
                    Check(t2 <= (int)Math.Ceiling(thr / regen) + 1, $"powered bay (regen {regen}, thr {thr}) took {t2} ticks to recontain");
                }
            }
            return null;
        }

        public static List<string> CaskFam(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { string e = CaskUnits(baseSeed); if (e != null) fails.Add("cask units: " + e); } catch (Exception e) { fails.Add("cask units: " + e.Message); }
            fails.AddRange(Family("cask", n, baseSeed, s => Drive(s, GenCask, RunCask)));
            return fails;
        }

        // ════════════════════════ storm ════════════════════════
        private static readonly string[] StormNames = { "Weather", "Tick", "Toggle", "Worker", "Advance" };

        public static long Unleashes, Holdings, DoseRuns, FallAdds;

        private static List<Act> GenStorm(Random r)
        {
            int n = 8 + r.Next(60);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 18 ? 0 : w < 55 ? 1 : w < 62 ? 2 : w < 70 ? 3 : 4;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = StormNames });
            }
            return l;
        }

        // weather ids: -1 none, 0 plain (no scripts), 1 dose only, 2 named A, 3 named B (both dose + phase), 4 phase script only
        private static bool HasPhase(int w) { return w == 2 || w == 3 || w == 4; }
        private static bool HasDose(int w) { return w == 1 || w == 2 || w == 3; }

        private static string RunStorm(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x77);
            int warnA = r.Next(4) == 0 ? 0 : 1 + r.Next(300);
            int[] warn = { 0, 0, 0, warnA, 1 + r.Next(300), 30 };
            bool optedIn = r.Next(6) != 0;
            PhaseState s = PhaseState.Idle;
            // spec
            int oW = -1, oStart = -1; bool oUn = false;
            int cur = -1, now = 1000; bool enabled = true, wasteland = true;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    int warnTicks(int w) { return w >= 0 && HasPhase(w) ? warn[w + 1] : 0; }
                    switch (a.kind)
                    {
                        case 0: cur = a.a % 6 - 1; break;
                        case 3: // OnWeatherStart: BeginPhase for the new weather
                            {
                                var e = RM_StormKernel.Begin(ref s, cur, HasPhase(cur), enabled, warnTicks(cur), now);
                                if (!HasPhase(cur)) { oW = -1; oStart = -1; oUn = false; Check((e & PhaseEvent.Ended) != 0, "Begin with no script must end the phase"); }
                                else { oW = cur; oStart = now; oUn = !enabled || warnTicks(cur) <= 0; Check((e & PhaseEvent.Began) != 0, "Begin did not report Began"); Check(((e & PhaseEvent.Unleash) != 0) == oUn, "Begin Unleash flag disagrees with !enabled || warn<=0"); }
                                break;
                            }
                        case 2: if (a.a % 2 == 0) enabled = !enabled; else wasteland = !wasteland; break;
                        case 4: now += 1 + a.a % 200; break;
                        case 1:
                            {
                                now += 1 + (a.a % 4 == 0 ? a.b % 50 : 0);
                                int wt = warnTicks(cur);
                                var e = RM_StormKernel.Tick(ref s, cur, HasPhase(cur), enabled, wt, now, out float progress);
                                // spec
                                if (!HasPhase(cur)) { oW = -1; oStart = -1; oUn = false; }
                                else
                                {
                                    if (cur != oW) { oW = cur; oStart = now; oUn = !enabled || wt <= 0; }
                                    if (enabled && !oUn && now - oStart >= wt) oUn = true;
                                }
                                Check(s.weather == oW && s.startTick == oStart && s.unleashed == oUn, $"phase state ({s.weather},{s.startTick},{s.unleashed}) != spec ({oW},{oStart},{oUn})");
                                Check(s.weather == (HasPhase(cur) ? cur : -1), "phase weather does not follow the current weather");
                                if (!HasPhase(cur)) Check(e == PhaseEvent.None || e == PhaseEvent.Ended, "events with no phase script: " + e);
                                else
                                {
                                    Check(((e & PhaseEvent.Disabled) != 0) == !enabled, "Disabled flag disagrees with the setting");
                                    if (enabled)
                                    {
                                        Check(((e & PhaseEvent.Storm) != 0) == s.unleashed, "Storm event while not unleashed (or missing once unleashed)");
                                        Check(((e & PhaseEvent.Warn) != 0) == !s.unleashed, "Warn event after the hand-off (or missing before it)");
                                        Check(progress >= 0f && progress < 1f || s.unleashed, "warning progress outside [0,1)");
                                        if ((e & PhaseEvent.Unleash) != 0) { Unleashes++; Check(now - s.startTick >= wt || wt <= 0 || s.startTick == now, "unleashed before the warning elapsed"); }
                                    }
                                    else Check((e & (PhaseEvent.Storm | PhaseEvent.Warn)) == 0, "storm or warning events while the phases are switched off");
                                }
                                // the storm layer gate: dose and fall never run during a named storm's warning
                                bool holding = RM_StormKernel.IsHolding(enabled && wasteland ? enabled : enabled, cur >= 0, s, cur);
                                bool specHolding = enabled && cur >= 0 && s.weather == cur && !s.unleashed;
                                Check(holding == specHolding, $"IsHolding kernel={holding} spec={specHolding}");
                                bool runs = RM_StormKernel.LayerRuns(optedIn, wasteland, HasDose(cur), holding);
                                bool specRuns = optedIn && wasteland && HasDose(cur) && !(HasPhase(cur) && enabled && !oUn);
                                Check(runs == specRuns, $"LayerRuns kernel={runs} spec={specRuns} (optedIn {optedIn} dose {HasDose(cur)} holding {holding})");
                                if (HasPhase(cur) && enabled && !s.unleashed) Check(!runs, "the storm layer dosed or dropped fall during a named storm's quiet warning");
                                if (holding) Holdings++;
                                if (runs) DoseRuns++;
                                break;
                            }
                    }
                }
                // liveness: from idle, a named storm ticked every tick unleashes within warn ticks of starting
                foreach (int wt in new[] { 1, 17, warnA, 300 })
                {
                    if (wt <= 0) continue;
                    var st = PhaseState.Idle; int t0 = 5000; int ev = 0;
                    RM_StormKernel.Begin(ref st, 2, true, true, wt, t0);
                    for (int t = t0; t <= t0 + wt + 1; t++) { RM_StormKernel.Tick(ref st, 2, true, true, wt, t, out float _); Steps++; if (st.unleashed && ev == 0) ev = t; }
                    Check(ev == t0 + wt, $"a {wt}-tick warning unleashed at +{ev - t0}");
                }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string StormUnits(int seed)
        {
            var r = new Random(seed);
            // fresh fall: capped at 4000, a full list overwrites in place and never grows or reads out of range
            for (int round = 0; round < 3; round++)
            {
                var list = new List<int>(); int adds = round == 0 ? 100 : 4000 + r.Next(1, 3000); int rolls = 0;
                for (int i = 0; i < adds; i++)
                {
                    int before = list.Count; int lastRoll = -1;
                    RM_StormKernel.RememberFall(list, i, n => { rolls++; Check(n == RM_StormKernel.MaxFreshFall, $"randBelow asked for {n}, list is full at {RM_StormKernel.MaxFreshFall}"); lastRoll = r.Next(n); return lastRoll; });
                    Steps++; FallAdds++;
                    if (before < RM_StormKernel.MaxFreshFall) { Check(list.Count == before + 1 && list[before] == i && rolls == 0, "below the cap an add must append without rolling"); }
                    else { Check(list.Count == before && list[lastRoll] == i, "at the cap an add must overwrite the rolled cell and not grow"); }
                    Check(list.Count <= RM_StormKernel.MaxFreshFall, "fresh fall exceeded its cap");
                }
                Check(list.Count == Math.Min(adds, RM_StormKernel.MaxFreshFall), "fresh fall length != min(adds, cap)");
            }
            // per-batch fall count against a double oracle; scales with rate and map area
            for (int i = 0; i < 300; i++)
            {
                float cpd = r.Next(0, 4000) / 8f; int cells = 1 + r.Next(1, 90000); float refc = 62500f;
                float got = RM_StormKernel.FallPerBatch(cpd, 250, 60000, cells, refc);
                double want = (double)cpd * 250 / 60000 * ((double)cells / refc);
                Steps++;
                Check(Math.Abs(got - want) <= 1e-4 * Math.Max(1.0, want), $"FallPerBatch({cpd},{cells})={got}, want {want}");
                Check(got >= 0f, "negative fall count");
                if (cpd > 0) Check(RM_StormKernel.FallPerBatch(cpd * 2, 250, 60000, cells, refc) > got, "doubling the rate did not increase fall");
            }
            Check(Math.Abs(RM_StormKernel.FallPerBatch(240f, 250, 60000, 62500, 62500f) - 1f) < 1e-5, "240 cells/day on a 250x250 map is exactly one cell per 250-tick batch");
            // fall / dose gating truth tables
            for (int m = 0; m < 16; m++)
            {
                bool pol = (m & 1) != 0, rem = (m & 2) != 0; float rate = (m & 4) != 0 ? 3f : (m & 8) != 0 ? -1f : 0f;
                Check(RM_StormKernel.FallActive(rate, pol, rem) == (rate > 0f && (pol || rem)), $"FallActive row {m}");
                Check(RM_StormKernel.Pollutes((m & 1) != 0, (m & 2) != 0) == ((m & 1) != 0 && (m & 2) != 0), $"Pollutes row {m}");
                Check(RM_StormKernel.Remembers((m & 1) != 0, (m & 2) != 0) == ((m & 1) != 0 && (m & 2) != 0), $"Remembers row {m}");
                Check(RM_StormKernel.DoseActive((m & 1) != 0, (m & 2) != 0 ? 1f : 0f) == ((m & 1) != 0 && (m & 2) != 0), $"DoseActive row {m}");
            }
            Check(RM_StormKernel.DoseFactor(1.5f, 2f) == 3f && RM_StormKernel.DoseFactor(1.5f, 0f) == 0f, "DoseFactor");
            // germination: no remembered fall -> no draws; with a fraction in [0,1] draws stay within [0, count]
            Check(RM_StormKernel.GerminationDraws(0, 0.5f, x => 99) == 0, "germination with no fresh fall drew");
            for (int i = 0; i < 500; i++)
            {
                int cnt = r.Next(1, 4001); float fr = r.Next(0, 101) / 100f;
                int d = RM_StormKernel.GerminationDraws(cnt, fr, x => r.Next(2) == 0 ? (int)Math.Floor(x) : (int)Math.Ceiling(x));
                Steps++;
                Check(d >= 0 && d <= cnt, $"germination drew {d} from {cnt} cells at fraction {fr}");
                Check(d >= Math.Floor(cnt * fr) - 0 && d <= Math.Ceiling(cnt * fr) + 0, $"germination drew {d}, expected about {cnt * fr}");
            }
            // warning clock, click interval, hand-off
            Check(RM_StormKernel.WarningTicks(2500, 0.5f) == 1250 && RM_StormKernel.WarningTicks(2500, 0f) == 0 && RM_StormKernel.WarningTicks(5, 0.5f) == 2, "WarningTicks rounding");
            for (int i = 0; i <= 100; i++)
            {
                float p = i / 100f; int iv = RM_StormKernel.ClickInterval(240, 20, p);
                Check(iv <= 240 && iv >= 20, "click interval outside [end,start]");
                if (i > 0) Check(iv <= RM_StormKernel.ClickInterval(240, 20, (i - 1) / 100f), "click interval grew as the warning advanced");
            }
            Check(RM_StormKernel.ClickInterval(240, 20, 0f) == 240 && RM_StormKernel.ClickInterval(240, 20, 1f) == 20 && RM_StormKernel.ClickInterval(240, 20, 7f) == 20, "click interval endpoints");
            Check(RM_StormKernel.HandoffDelay(900) == 300 && RM_StormKernel.HandoffDelay(1800) == 600 && RM_StormKernel.HandoffDelay(2) == 0, "HandoffDelay");
            return null;
        }

        public static List<string> Storm(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { string e = StormUnits(baseSeed); if (e != null) fails.Add("storm units: " + e); } catch (Exception e) { fails.Add("storm units: " + e.Message); }
            fails.AddRange(Family("storm", n, baseSeed, s => Drive(s, GenStorm, RunStorm)));
            return fails;
        }

        // ════════════════════════ tipping ════════════════════════
        private static readonly string[] TipNames = { "Due", "Pad", "Hostile", "Bay", "Usable", "Faction", "Reburial" };

        public static long Delivered, Failed, Completed, Grants, Hints, EvidenceAsks, Misses, Discovered;

        private static List<Act> GenTip(Random r)
        {
            int n = 6 + r.Next(50);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 45 ? 0 : w < 60 ? 1 : w < 66 ? 2 : w < 76 ? 3 : w < 84 ? 4 : w < 90 ? 5 : 6;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = TipNames });
            }
            return l;
        }

        private static string RunTip(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x1234);
            int deliveries = 1 + r.Next(5), allowed = r.Next(3), goodwill = 1 + r.Next(10);
            int casks = 1 + r.Next(6), perCask = 10 * (1 + r.Next(20));
            var st = new TippingState { active = true };
            bool pad = true, hostile = false, hasBay = false, hasEv = true, hasFin = true, evUsable = true, finUsable = true, hasMap = true;
            // spec ledger
            int sDone = 0, sMissed = 0, sGood = 0, sAsks = 0, sGrants = 0, sHints = 0; bool sActive = true;
            int gwSum = 0, silverPaid = 0, now = 0, next = 100;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 1: pad = !pad; break;
                        case 2: hostile = !hostile; break;
                        case 3: hasBay = !hasBay; break;
                        case 4: if (a.a % 2 == 0) evUsable = !evUsable; else finUsable = !finUsable; break;
                        case 5: if (a.a % 2 == 0) hasEv = !hasEv; else hasFin = !hasFin; break;
                        case 6: // reburial discovery, exhaustive over chance
                            {
                                float chance = new[] { 0f, 0.5f, 1f, 1.5f, -1f }[a.a % 5]; float roll = a.b % 7 == 0 ? 1f : a.b / 1000f; int calls = 0;   // Rand.Value includes 1.0 int calls = 0;
                                bool d = RM_TippingKernel.Discovers(hasEv, evUsable, chance, () => { calls++; return roll; });
                                bool spec = hasEv && evUsable && (chance >= 1f || (chance > 0f && roll < chance));
                                Check(d == spec, $"Discovers(chance {chance}, roll {roll}) kernel={d} spec={spec}");
                                Check(calls == ((hasEv && evUsable) ? 1 : 0), "the discovery roll was consumed for an absent or unusable faction");
                                if (d) Discovered++;
                                break;
                            }
                        case 0: // a quest-part tick at the due moment
                            {
                                now = next + a.a % 3;
                                if (!sActive) { var before = st; var rr0 = RM_TippingKernel.Deliver(ref st, pad, hasEv, evUsable, hasFin, finUsable, hasBay, goodwill, deliveries, allowed); Check(!rr0.delivered && !rr0.failed && !rr0.completed && rr0.convoyGoodwill == 0 && st.deliveriesDone == before.deliveriesDone && st.missed == before.missed, "a finished contract still did something"); break; }
                                bool isVoid = RM_TippingKernel.ContractVoid(hasMap, true, hostile);
                                Check(isVoid == (!hasMap || hostile), "ContractVoid disagrees with !map || hostile");
                                if (isVoid) { st.active = false; sActive = false; Failed++; break; }
                                Check(RM_TippingKernel.DeliveryDue(now, next), "a delivery at/after its scheduled tick was not due");
                                Check(!RM_TippingKernel.DeliveryDue(next - 1, next), "a delivery before its scheduled tick was due");
                                var res = RM_TippingKernel.Deliver(ref st, pad, hasEv, evUsable, hasFin, finUsable, hasBay, goodwill, deliveries, allowed);
                                next = RM_TippingKernel.NextDelivery(now, 4f, 60000);
                                Check(next == now + 240000, "next delivery is not four days later");
                                gwSum += res.convoyGoodwill;
                                // spec
                                if (!pad)
                                {
                                    sMissed++; sGood += -5; Misses++;
                                    Check(!res.delivered && res.convoyGoodwill == -5, "a missed load must cost 5 goodwill and deliver nothing");
                                    Check(res.failed == (sMissed > allowed), $"failed={res.failed} but missed {sMissed} vs allowed {allowed}");
                                    if (res.failed) { sActive = false; Failed++; }
                                    Check(res.askEvidence == false && res.finance == FinanceStep.None && !res.completed, "a missed load asked for evidence, finance or completed");
                                }
                                else
                                {
                                    sDone++; sGood += goodwill; Delivered++;
                                    Check(res.delivered && res.convoyGoodwill == goodwill && !res.failed, "a licensed load did not deliver and pay goodwill");
                                    silverPaid += RM_TippingKernel.SilverPerDelivery(casks, perCask);
                                    bool wantAsk = sAsks == 0 && hasEv && evUsable;
                                    Check(res.askEvidence == wantAsk, $"askEvidence={res.askEvidence}, spec {wantAsk}");
                                    if (wantAsk) { sAsks++; EvidenceAsks++; }
                                    bool granted = sGrants > 0;
                                    FinanceStep wantFin = granted || !hasFin || !finUsable ? FinanceStep.None : hasBay ? FinanceStep.Grant : (sHints > 0 ? FinanceStep.None : FinanceStep.Hint);
                                    Check(res.finance == wantFin, $"finance step {res.finance}, spec {wantFin}");
                                    if (wantFin == FinanceStep.Grant) { sGrants++; Grants++; } else if (wantFin == FinanceStep.Hint) { sHints++; Hints++; }
                                    Check(res.completed == (sDone >= deliveries), $"completed={res.completed} with {sDone} of {deliveries} deliveries");
                                    if (res.completed) { sActive = false; Completed++; }
                                }
                                Check(st.deliveriesDone == sDone && st.missed == sMissed && st.active == sActive, $"state done {st.deliveriesDone}/{sDone} missed {st.missed}/{sMissed} active {st.active}/{sActive}");
                                break;
                            }
                    }
                    // ---- invariants after every step ----
                    Check(st.deliveriesDone <= deliveries, "more deliveries than the contract allows");
                    Check(st.missed <= allowed + 1, "missed beyond allowed + 1 (should have failed)");
                    Check(sGrants <= 1, "finance granted more than once");
                    Check(sAsks <= 1, "evidence asked more than once");
                    Check(sGrants == 0 || sHints <= 1, "hinted more than once");
                    Check(!(st.financeGranted && st.financeHinted && sGrants == 0), "hinted state inconsistent");
                    Check(silverPaid <= deliveries * RM_TippingKernel.SilverPerDelivery(casks, perCask), "paid more silver than deliveries x per-delivery");
                    Check(gwSum == sGood, $"convoy goodwill {gwSum} != spec {sGood}");
                    if (!st.active && st.deliveriesDone >= deliveries) Check(st.deliveriesDone == deliveries, "completed with a different count than the contract");
                }
                // liveness: a licensed, friendly contract completes in exactly `deliveries` loads and no sooner
                var t = new TippingState { active = true }; int n = 0;
                while (t.active && n < 100) { var rr = RM_TippingKernel.Deliver(ref t, true, true, true, true, true, true, goodwill, deliveries, allowed); n++; Steps++; if (rr.completed) break; }
                Check(n == deliveries && t.deliveriesDone == deliveries, $"a licensed contract needed {n} loads, expected {deliveries}");
                // and a pad that never appears fails on load allowed + 2... precisely when missed exceeds the allowance
                var u = new TippingState { active = true }; int m = 0; bool failed = false;
                while (u.active && m < 100) { var rr = RM_TippingKernel.Deliver(ref u, false, true, true, true, true, true, goodwill, deliveries, allowed); m++; failed = rr.failed; }
                Check(failed && m == allowed + 1, $"a padless contract failed after {m} misses, expected {allowed + 1}");
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string TipUnits()
        {
            Check(RM_TippingKernel.Chance(0f, 0f) == false && RM_TippingKernel.Chance(1f, 0.999f) && RM_TippingKernel.Chance(2f, 0.5f) && !RM_TippingKernel.Chance(-1f, 0f), "Chance bounds");
            Check(RM_TippingKernel.Chance(0.5f, 0.4999f) && !RM_TippingKernel.Chance(0.5f, 0.5f), "Chance is strictly below the value");
            Check(RM_TippingKernel.SilverPerDelivery(5, 55) == 275, "SilverPerDelivery");
            for (int m = 0; m < 32; m++)
            {
                bool granted = (m & 1) != 0, has = (m & 2) != 0, usable = (m & 4) != 0, bay = (m & 8) != 0, hinted = (m & 16) != 0;
                var got = RM_TippingKernel.FinanceOffer(granted, has, usable, bay, hinted);
                var want = granted || !has || !usable ? FinanceStep.None : bay ? FinanceStep.Grant : hinted ? FinanceStep.None : FinanceStep.Hint;
                Check(got == want, $"FinanceOffer row {m}: {got} != {want}"); Steps++;
            }
            return null;
        }

        public static List<string> Tipping(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { TipUnits(); } catch (Exception e) { fails.Add("tipping units: " + e.Message); }
            fails.AddRange(Family("tipping", n, baseSeed, s => Drive(s, GenTip, RunTip)));
            return fails;
        }

        // ════════════════════════ dose ════════════════════════
        public static long RimCells, MassCases;

        private static string DoseCase(int seed)
        {
            var r = new Random(seed);
            float toxic = r.Next(0, 17) / 8f, edge = r.Next(0, 17) / 8f, radius = 1 + r.Next(0, 80) / 4f, mult = r.Next(-2, 9) / 4f;
            Check(RM_DoseKernel.DoseActive(mult, toxic) == (mult > 0f && toxic > 0f), "DoseActive");
            float prev = float.NaN;
            for (int d = 0; d <= (int)(radius * radius) + 3; d++)
            {
                float f = RM_DoseKernel.OutdoorFactor(toxic, edge, d, radius); Steps++;
                if (d > radius * radius) { Check(f < 0f, $"dosed beyond the radius (d2 {d}, r {radius})"); continue; }
                Check(f >= 0f, $"in-range pawn got no dose (d2 {d}, r {radius}, factor {f})");
                double lo = toxic * Math.Min(1.0, edge) - 1e-5, hi = toxic * Math.Max(1.0, edge) + 1e-5;
                Check(f >= lo && f <= hi, $"factor {f} outside [{lo},{hi}] (toxic {toxic} edge {edge})");
                if (d == 0) Check(Math.Abs(f - toxic) <= 1e-6, "at the body the factor must be the full toxicFactor");
                if (!float.IsNaN(prev) && edge <= 1f) Check(f <= prev + 1e-5, "dose rose with distance though edgeFactor <= 1");
                if (!float.IsNaN(prev) && edge >= 1f) Check(f >= prev - 1e-5, "dose fell with distance though edgeFactor >= 1");
                prev = f;
                if ((double)d == (double)radius * radius) { RimCells++; Check(Math.Abs(f - toxic * edge) <= 1e-4 * Math.Max(1f, toxic * edge), $"rim factor {f} != toxic*edge {toxic * edge}"); }
            }
            Check(RM_DoseKernel.IndoorFactor(toxic, true) == toxic && RM_DoseKernel.IndoorFactor(toxic, false) < 0f, "IndoorFactor");
            Check(RM_DoseKernel.Applied(toxic, mult) == toxic * mult, "Applied");
            // gripper units
            for (int i = 0; i < 40; i++)
            {
                float mass = new[] { 0f, 0.00005f, 0.0001f, 0.00011f, 0.02f, 0.5f, 1f, 7.5f, 60f }[r.Next(9)];
                float cap = new[] { 0f, 0.5f, 5f, 35f, 1e6f, 3e9f }[r.Next(6)];
                int stack = r.Next(0, 500), maxU = r.Next(0, 80); bool legal = r.Next(5) != 0;
                int got = RM_DoseKernel.UnitsToTake(legal, mass, stack, maxU, cap); Steps++; MassCases++;
                long byMass = mass <= 0.0001f ? long.MaxValue : (long)Math.Floor((double)cap / mass);
                long want = !legal ? 0 : Math.Max(0L, Math.Min((long)stack, Math.Min((long)maxU, byMass)));
                Check(got == want, $"UnitsToTake(legal {legal}, mass {mass}, stack {stack}, maxUnits {maxU}, cap {cap}) = {got}, spec {want}");
                Check(got >= 0 && got <= stack && got <= maxU, "UnitsToTake outside [0, min(stack, maxUnits)]");
                if (legal && mass > 0.0001f) Check(got * (double)mass <= cap + 1e-3 * Math.Max(1.0, cap), "took more mass than the carry cap");
            }
            // processor fullness: reaches 1 in about days x ticksPerDay / growth ticks, slower off feed, never above 1
            float days = new[] { 0.5f, 1f, 4f }[r.Next(3)]; float growth = new[] { 0.5f, 1f, 1.5f }[r.Next(3)]; float off = new[] { 0.25f, 0.5f, 1f }[r.Next(3)];
            foreach (bool onFeed in new[] { true, false })
            {
                float rate = RM_DoseKernel.FullnessRate(days, 60000, growth, onFeed, off);
                Check(rate > 0f, "fullness rate not positive");
                double expectTicks = days * 60000.0 / (growth * (onFeed ? 1.0 : off));
                float full = 0f; long t = 0;
                while (full < 1f && t < 20000000) { full = RM_DoseKernel.NextFullness(full, rate); t++; }
                Steps += 1;
                Check(Math.Abs(t - expectTicks) <= expectTicks * 3e-2 + 2, $"fullness took {t} ticks, expected {expectTicks:F0} (onFeed {onFeed})");
                Check(RM_DoseKernel.NextFullness(0.9999f, rate * 1e6f) == 1f && RM_DoseKernel.NextFullness(1f, rate) == 1f, "fullness exceeded 1");
            }
            Check(RM_DoseKernel.FullnessRate(1f, 60000, 1f, false, 0.5f) < RM_DoseKernel.FullnessRate(1f, 60000, 1f, true, 0.5f), "off-feed is not slower");
            Check(Math.Abs(RM_DoseKernel.UnpolluteChance(1f, 250, 60000) - 250f / 60000f) < 1e-9, "UnpolluteChance");
            return null;
        }

        public static List<string> Dose(int n, int baseSeed)
        {
            return Family("dose", n, baseSeed, DoseCase);
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("cask", () => CaskFam(N(3000), S(1))),
                ("storm", () => Storm(N(3000), S(1))),
                ("tipping", () => Tipping(N(3000), S(1))),
                ("dose", () => Dose(N(2000), S(1))),
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
            Console.WriteLine($"reached: bay pulses {BayPulses}, cask pulses {CaskPulses}, contained ticks {Contained0}, processed casks {Completions}; storm unleashes {Unleashes}, holdings {Holdings}, layer runs {DoseRuns}, fall adds {FallAdds}");
            Console.WriteLine($"reached: tipping delivered {Delivered}, failed/void {Failed}, completed {Completed}, misses {Misses}, evidence asks {EvidenceAsks}, grants {Grants}, hints {Hints}, discoveries {Discovered}; dose rim cells {RimCells}, gripper cases {MassCases}");
            if (!oneSeed.HasValue && scale >= 1 && (only == null))
            {
                if (BayPulses == 0 || CaskPulses == 0 || Completions == 0 || Unleashes == 0 || Holdings == 0 || Completed == 0 || Failed == 0 || Grants == 0 || Hints == 0 || EvidenceAsks == 0 || Discovered == 0 || RimCells == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"wasteland fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
