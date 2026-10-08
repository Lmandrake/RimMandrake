// Approach B for GelatinousSlime: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   ladder   RM_SlimeLadder: the slimification severity rate, stage latch, dissolution, dose, antidote, drench, injection
//   titan    RM_TitanKernel: the titanoslime mass ladder with hysteresis, growth/reversibility gates, decay, engulf, shedding
//   world    RM_SlimeWorld: biome score, farm conversion, chunk shelf life and ground, archive payment plan
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.GelatinousSlime.SelfTest
{
    internal static class GelatinousSlimeFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(float a, float b, float eps) { return Math.Abs(a - b) <= eps; }

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


        // ════════════════════════ ladder ════════════════════════
        private static readonly string[] LadderNames = { "Time", "Env", "Eat", "Antidote", "Drench", "Inject", "Release", "Grows", "Clock", "Touch", "Resist" };
        public static long Dissolutions, Cures, Announces, FastLives, DryClears, DoseCaps, WipeOffs, Holds, CuresRefused;

        private static List<Act> GenLadder(Random r)
        {
            int n = 8 + r.Next(40);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 38 ? 0 : w < 52 ? 1 : w < 60 ? 2 : w < 68 ? 3 : w < 73 ? 4 : w < 80 ? 5 : w < 84 ? 6 : w < 88 ? 7 : w < 92 ? 8 : w < 97 ? 9 : 10;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = LadderNames });
            }
            return l;
        }

        private static float SpecRate(int env, float decay, bool grows, float days, bool fast, float sev)
        {
            float clock = 7f / Math.Max(0.5f, days);
            if (env == 2) return -Math.Abs(decay);
            if (env == 1) return grows ? (fast ? 1f / 3f : 1f / 7f) * clock : -0.5f;
            if (fast) return grows ? 1f / 3f * clock : -0.5f;
            return sev < 0.2f ? -0.5f : 0f;
        }

        private static string RunLadder(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x33);
            float decay = 0.1f + r.Next(5) * 0.1f;
            bool announceable = r.Next(3) != 0;
            int env = r.Next(3);
            bool grows = true, resistant = false, has = false, fast = false, dissolved = false;
            float days = 7f, sev = 0f; int hi = -1, lastAnn = -1;
            string where = "";

            void Add() { has = true; sev = 0.01f; fast = false; hi = -1; lastAnn = -1; }
            try
            {
                // the climb: on slime, from first touch, the dissolution arrives when the days setting says it does
                {
                    float d = new[] { 2f, 3.5f, 7f, 14f, 30f }[r.Next(5)]; bool f = r.Next(3) == 0; float s = 0.01f; int h = -1, checks = 0;
                    float rate = RM_SlimeLadder.RatePerDay(false, 0f, true, d, true, f, s);
                    bool done = false;
                    while (!done && checks < 200000)
                    {
                        checks++;
                        RM_SlimeLadder.Check(s, rate, false, ref h, out bool _, out bool dis, out float adj, out int _);
                        if (dis) done = true; else s = Math.Min(1f, s + adj);
                    }
                    double daysTaken = checks * 200.0 / 60000.0, want = (1 - 0.01) / (double)rate;
                    Check(done && Math.Abs(daysTaken - want) <= 0.05 * want + 0.02, $"on slime with the clock at {d} days (fast {f}) dissolution took {daysTaken:F2} days, expected {want:F2}");
                }
                int step = 0;
                foreach (var a in acts)
                {
                    if (dissolved) break;
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                int n = 1 + (a.b % 3 == 0 ? a.a % 400 : a.a % 12);
                                for (int t = 0; t < n && has && !dissolved; t++)
                                {
                                    float rate = RM_SlimeLadder.RatePerDay(env == 2, decay, grows, days, env == 1, fast, sev);
                                    Check(Near(rate, SpecRate(env, decay, grows, days, fast, sev), 1e-5f), $"rate {rate} but the ladder says {SpecRate(env, decay, grows, days, fast, sev)} (env {env}, grows {grows}, days {days}, fast {fast}, sev {sev})");
                                    if (env == 2) Check(rate < 0f, "a drying biome did not leach");
                                    if (env == 0 && !fast) { if (sev < 0.2f) WipeOffs++; else { Check(rate == 0f, "ordinary country moved a stage 2+ severity"); Holds++; } }
                                    float before = sev;
                                    RM_SlimeLadder.Check(sev, rate, announceable, ref hi, out bool endHostile, out bool dissolve, out float adj, out int ann);
                                    Check(endHostile == (before >= 0.5f), "hostile-state ending is not exactly stage 3+ (severity >= 0.5)");
                                    Check(dissolve == (before >= 1f), "dissolution at severity " + before);
                                    if (dissolve) { dissolved = true; Dissolutions++; break; }
                                    if (ann >= 0)
                                    {
                                        Check(announceable, "a letter went to a non-player or non-humanlike pawn");
                                        Check(ann == RM_SlimeLadder.StageIndex(before) && ann > lastAnn, $"announced stage {ann} after {lastAnn} at severity {before}");
                                        lastAnn = ann; Announces++;
                                    }
                                    if (!announceable) Check(hi == (hi < 0 ? -1 : hi) && ann < 0, "a silent pawn announced");
                                    Check(Math.Abs(adj - rate * 200f / 60000f) < 1e-7f, "adjustment is not rate per 200 ticks");
                                    sev = Math.Min(1f, Math.Max(0f, sev + adj));
                                    if (sev <= 0f) { has = false; if (env == 2) DryClears++; }
                                }
                                break;
                            }
                        case 1: env = a.a % 3; break;
                        case 2:
                            {
                                if (resistant) break;
                                if (!has) Add();
                                float before = sev;
                                sev = RM_SlimeLadder.DoseSeverity(sev, 1 + a.a % 4 - (a.b % 5 == 0 ? 1 : 0));
                                Check(sev >= before, $"eating slime LOWERED severity {before} -> {sev}");
                                Check(sev <= Math.Max(before, 0.99f) + 1e-6f, "a dose went past 0.99");
                                if (before < 1f) Check(sev < 1f, "a dose dissolved someone");
                                if (sev >= 0.99f - 1e-6f) DoseCaps++;
                                break;
                            }
                        case 3:
                            {
                                bool cures = RM_SlimeLadder.AntidoteCures(has, sev);
                                Check(cures == (has && sev < 1f), "antidote cure rule");
                                if (has && sev >= 1f) CuresRefused++;
                                if (cures) { has = false; fast = false; Cures++; }
                                break;
                            }
                        case 4:
                            {
                                if (resistant || !grows) break;
                                if (!has) Add();
                                float before = sev; sev = RM_SlimeLadder.Drench(sev);
                                Check(sev >= before && sev >= 0.55f, "drench lowered or under-drenched");
                                break;
                            }
                        case 5:
                            {
                                if (resistant) break;
                                if (!has) Add();
                                float before = sev; sev = RM_SlimeLadder.InjectedStart(sev, 0.4f); fast = true;
                                Check(sev >= before && sev >= 0.4f, "injection lowered severity or started under 0.4");
                                break;
                            }
                        case 6:
                            {
                                if (resistant) break;
                                if (!has) Add();
                                float before = sev; sev = RM_SlimeLadder.ReleasePenalty(sev);
                                Check(sev >= before && sev <= 1f, "release penalty out of range");
                                break;
                            }
                        case 7: grows = !grows; break;
                        case 8: days = new[] { 2f, 7f, 14f, 30f, 0.1f }[a.a % 5]; break;
                        case 9: if (env == 1 && !resistant && grows && !has) Add(); break;
                        case 10: resistant = !resistant; break;
                    }
                    if (has && fast && !dissolved) FastLives++;
                    Check(sev >= 0f && sev <= 1f, "severity out of [0,1]: " + sev);
                    Check(!has || sev > 0f, "a live hediff at severity 0");
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where + (e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? " " + e.StackTrace : ""); }
            return null;
        }

        private static List<string> Ladder(int n, int baseSeed) { return Family("ladder", n, baseSeed, seed => Drive(seed, GenLadder, RunLadder)); }

        private static string RunLadderProps(int seed)
        {
            var r = new Random(seed);
            // stage boundaries and monotonicity
            Check(RM_SlimeLadder.StageIndex(0.199f) == 0 && RM_SlimeLadder.StageIndex(0.2f) == 1 && RM_SlimeLadder.StageIndex(0.499f) == 1 && RM_SlimeLadder.StageIndex(0.5f) == 2
                && RM_SlimeLadder.StageIndex(0.899f) == 2 && RM_SlimeLadder.StageIndex(0.9f) == 3 && RM_SlimeLadder.StageIndex(1f) == 3, "stage boundaries");
            int prev = 0;
            for (int i = 0; i <= 100; i++) { int s = RM_SlimeLadder.StageIndex(i / 100f); Check(s >= prev, "StageIndex fell as severity rose"); prev = s; }
            // dissolve yield
            int p2 = 0;
            for (float b = 0f; b < 8f; b += 0.07f) { int n = RM_SlimeLadder.DissolveSlime(b); Check(n >= 5 && n <= 120 && n >= p2, "DissolveSlime out of [5,120] or not monotone"); p2 = n; }
            Check(RM_SlimeLadder.DissolveSlime(1f) == 25 && RM_SlimeLadder.DissolveSlime(0.5f) == 13, "DissolveSlime rounding (0.5 x 25 = 12.5 rounds away from zero to 13)");
            // resistance: any single route suffices
            for (int m = 0; m < 16; m++)
            {
                bool none = (m & 1) != 0, flesh = (m & 2) != 0, ext = (m & 4) != 0, gene = (m & 8) != 0;
                Check(RM_SlimeLadder.Resistant(none, flesh, ext, gene) == (none || !flesh || ext || gene), "Resistant truth table");
            }
            // poison classification
            string[] names = { "ToxicBuildup", "Plague", "Venomous", "RadiationSickness", "FoodPoisoning", "Anesthetic", "Gunshot", "ToxicLungs", "poisonedBlood" };
            foreach (var nm in names)
                for (int m = 0; m < 8; m++)
                {
                    bool inj = (m & 1) != 0, bad = (m & 2) != 0, tox = (m & 4) != 0;
                    bool got = RM_SlimeLadder.IsPoisonLike(inj, bad, tox, nm);
                    bool byName = nm.ToLowerInvariant().Contains("toxic") || nm.ToLowerInvariant().Contains("poison") || nm.ToLowerInvariant().Contains("venom") || nm.ToLowerInvariant().Contains("radiation");
                    Check(got == (!inj && bad && (tox || byName)), $"IsPoisonLike({inj},{bad},{tox},{nm}) = {got}");
                }
            // marks
            Check(RM_SlimeLadder.MarkIncrement(false, false) == 1f && RM_SlimeLadder.MarkIncrement(true, false) == 2f && RM_SlimeLadder.MarkIncrement(false, true) == 0f && RM_SlimeLadder.MarkIncrement(true, true) == 1f, "MarkIncrement");
            Check(RM_SlimeLadder.MarkStage(1f) == 0 && RM_SlimeLadder.MarkStage(2f) == 1 && RM_SlimeLadder.MarkStage(3.99f) == 1 && RM_SlimeLadder.MarkStage(4f) == 2 && RM_SlimeLadder.MarkStage(8f) == 2, "MarkStage thresholds");
            // dose sequence: a pawn that keeps eating climbs 0.06 per portion and stops below 1
            float sev = 0.01f; int portions = 0;
            while (sev < 0.99f - 1e-6f && portions < 100) { float nx = RM_SlimeLadder.DoseSeverity(sev, 1); Check(nx > sev, "a dose did not climb"); sev = nx; portions++; }
            Check(sev <= 0.99f + 1e-6f && portions >= 15, "dose ladder");
            Check(RM_SlimeLadder.DoseSeverity(0.995f, 1) == 0.995f && RM_SlimeLadder.DoseSeverity(1f, 3) == 1f, "a dose at or past the ceiling must not lower severity");
            return null;
        }

        private static List<string> LadderProps(int n, int baseSeed) { return Family("ladder-props", n, baseSeed, RunLadderProps); }

        // ════════════════════════ titan ════════════════════════
        private static readonly string[] TitanNames = { "Eat", "Absorb", "Shed", "Starve", "Dry", "MaxStage", "Grows", "Reversible", "Reload", "Slime" };
        public static long TitanStagesUp, TitanStagesDown, TitanLossBlocked, TitanFrozen, TitanLossApplied, TitanLetters, TitanSheds;

        private static List<Act> GenTitan(Random r)
        {
            int n = 10 + r.Next(60);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 22 ? 0 : w < 40 ? 1 : w < 52 ? 2 : w < 62 ? 3 : w < 72 ? 4 : w < 78 ? 5 : w < 83 ? 6 : w < 90 ? 7 : w < 94 ? 8 : 9;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = TitanNames });
            }
            return l;
        }

        private static string RunTitan(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x44);
            var up = new List<float> { 4f, 12f, 28f, 60f };
            if (r.Next(3) == 0) up = new List<float> { 2f, 5f, 9f, 20f };
            float hyst = new[] { 0f, 0.5f, 1f, 2f }[r.Next(4)], cap = new[] { 30f, 80f, 80f }[r.Next(3)];
            int settingMax = 1 + r.Next(5);
            bool grows = true, reversible = r.Next(2) == 0, onSlime = true; bool dirty = false;
            float mass = r.Next(3) == 0 ? 0f : RM_TitanKernel.RollMass(new List<float> { 0.6f, 0.3f, 0.1f }, new List<float> { 0f, 4f, 12f }, (float)r.NextDouble());
            int cur = 0, hi = -1, offTicks = 0; float damage = 0f;
            int MaxIdx() { return RM_TitanKernel.MaxStageIndex(up.Count, settingMax); }
            Func<bool, int> apply = announce =>
            {
                mass = RM_TitanKernel.Clamp(mass, 0f, cap);
                int t = RM_TitanKernel.StageFor(mass, cur, up, hyst, MaxIdx());
                if (t > cur) { TitanStagesUp++; Check(mass >= up[cur], $"rose from stage {cur} at mass {mass} below its threshold {up[cur]}"); }
                if (t < cur) { TitanStagesDown++; Check(t == MaxIdx() || mass < up[cur - 1] - hyst + 1e-4f, $"dropped from stage {cur} at mass {mass} while still inside the hysteresis band of {up[cur - 1]} - {hyst}"); }
                cur = t; dirty = false;
                if (RM_TitanKernel.Announce(t, ref hi, true, announce)) { TitanLetters++; Check(t > 0, "a letter for stage 0"); }
                return t;
            };
            Action<float> add = delta =>
            {
                float before = mass;
                bool did = RM_TitanKernel.TryAddMass(ref mass, delta, grows, reversible, cap);
                Check(did == (grows && !(delta < 0f && !reversible)), "TryAddMass gate");
                if (!did) { Check(mass == before, "a refused mass change moved the mass"); if (!grows) TitanFrozen++; else TitanLossBlocked++; return; }
                if (delta < 0f) { TitanLossApplied++; Check(mass <= before, "a loss raised mass"); }
                if (delta > 0f) Check(mass >= before - 1e-4f, "a gain lowered mass");
                apply(delta > 0f);
            };
            apply(false); hi = r.Next(2) == 0 ? -1 : cur;   // a fresh spawn latches its stage; a loaded save starts unannounced
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0: add((a.a % 40) * 0.25f * 0.25f + 0.05f); break;
                        case 1: add(0.2f + (a.a % 100) / 10f); break;
                        case 2:
                            {
                                float baseHealth = 0.5f + a.a % 5;
                                bool shed = RM_TitanKernel.ShedStep(ref damage, 1f + a.b % 60, baseHealth, 0.12f, a.a % 3, (a.b % 100) / 100f, cur, true);
                                Check(damage >= 0f && (shed ? damage == 0f : true), "ShedStep damage bookkeeping");
                                if (shed) { TitanSheds++; Check(cur >= 1, "stage 0 shed"); add(-1f); }
                                break;
                            }
                        case 3:
                            for (int i = 0, n = 1 + a.a % 30; i < n; i++)
                            {
                                float loss = RM_TitanKernel.DecayLoss(ref offTicks, onSlime, 2500, true, 1f, 0.5f);
                                Check(Near(loss, 2500f / 60000f + (offTicks >= 60000 ? 0.5f * 2500f / 60000f : 0f), 1e-6f), "starving loss");
                                if (loss > 0f) add(-loss);
                            }
                            break;
                        case 4:
                            for (int i = 0, n = 1 + a.a % 60; i < n; i++)
                            {
                                
                                float loss = RM_TitanKernel.DecayLoss(ref offTicks, onSlime, 2500, false, 1f, 0.5f);
                                Check(onSlime ? (offTicks == 0 && loss == 0f) : (offTicks > 0 && (offTicks >= 60000) == (loss > 0f)), $"dry loss starts only after a full day away (off {offTicks}, loss {loss}, onSlime {onSlime})");
                                if (loss > 0f) add(-loss);
                            }
                            break;
                        case 5: settingMax = 1 + a.a % 5; dirty = true; break;
                        case 6: grows = !grows; break;
                        case 7: reversible = !reversible; break;
                        case 8: apply(false); break;
                        case 9: onSlime = !onSlime; break;
                    }
                    Check(mass >= 0f && mass <= cap + 1e-4f, "mass out of range: " + mass);
                    if (!dirty)
                    {
                        Check(cur <= MaxIdx(), $"stage {cur} above the settings ceiling {MaxIdx()}");
                        float lo = cur == 0 ? 0f : up[cur - 1], nextT = cur < up.Count ? up[cur] : 1e9f;
                        Check(cur == 0 || mass >= lo - hyst - 1e-4f, $"stage {cur} held at mass {mass} below its threshold {lo} - hysteresis {hyst}");
                        Check(cur >= MaxIdx() || mass < nextT + 1e-4f, $"stage {cur} but mass {mass} reaches the next threshold {nextT}");
                        int again = RM_TitanKernel.StageFor(mass, cur, up, hyst, MaxIdx());
                        Check(again == cur, "StageFor is not idempotent (the stage flaps)");
                    }
                }
            }
            catch (Exception e) when (!(e is OutOfMemoryException)) { return e.Message + where + (e is IndexOutOfRangeException || e is ArgumentOutOfRangeException ? " " + e.StackTrace : ""); }
            return null;
        }

        private static List<string> Titan(int n, int baseSeed) { return Family("titan", n, baseSeed, seed => Drive(seed, GenTitan, RunTitan)); }

        public static long EngulfOk, EngulfNo, RollEdges;

        private static string RunTitanProps(int seed)
        {
            var r = new Random(seed);
            // capacity: monotone, at least one; the 1/2/4/6/10 ladder at 4 body size per thing
            int p = 0;
            for (float b = 0f; b < 45f; b += 0.37f) { int c = RM_TitanKernel.Capacity(b, 4f); Check(c >= 1 && c >= p, "Capacity fell or hit 0"); p = c; }
            Check(RM_TitanKernel.Capacity(3.99f, 4f) == 1 && RM_TitanKernel.Capacity(4f, 4f) == 1 && RM_TitanKernel.Capacity(8f, 4f) == 2 && RM_TitanKernel.Capacity(40f, 4f) == 10, "Capacity values");
            // engulf gate against a one-line spec
            for (int k = 0; k < 40; k++)
            {
                bool on = r.Next(5) != 0, sSp = r.Next(5) != 0, sDead = r.Next(6) == 0, sDown = r.Next(6) == 0, pSp = r.Next(5) != 0, pDead = r.Next(6) == 0, flesh = r.Next(4) != 0, same = r.Next(8) == 0, held = r.Next(6) == 0, sameDef = r.Next(3) == 0;
                float pb = (float)(r.NextDouble() * 6), sb = 1f + (float)(r.NextDouble() * 40), frac = 0.5f; int inside = r.Next(4), cap = 1 + r.Next(4);
                bool got = RM_TitanKernel.CanEngulf(on, sSp, sDead, sDown, pSp, pDead, flesh, same, pb, sb, frac, inside, cap, held, sameDef);
                bool want = on && !same && sSp && !sDead && !sDown && pSp && !pDead && flesh && !(pb > sb * frac) && !(inside >= cap) && !held && !(sameDef && pb >= sb);
                Check(got == want, $"CanEngulf disagrees with the gate (on {on}, flesh {flesh}, prey {pb:F2} vs {sb:F2}, held {inside}/{cap})");
                if (got) EngulfOk++; else EngulfNo++;
            }
            Check(RM_TitanKernel.CanEngulf(true, true, false, false, true, false, true, false, 5f, 10f, 0.5f, 0, 1, false, false) && !RM_TitanKernel.CanEngulf(true, true, false, false, true, false, true, false, 5.01f, 10f, 0.5f, 0, 1, false, false), "prey size boundary is at exactly half");
            // digestion, struggle, burst
            float pd = 0f;
            for (float s = 0f; s < 12f; s += 0.3f) { int d = RM_TitanKernel.DigestTicks(s * 40f); Check(d >= 60 && d >= pd, "DigestTicks under a second or not monotone"); pd = d; }
            Check(RM_TitanKernel.DigestTicks(75f) == 4500 && RM_TitanKernel.DigestTicks(0.001f) == 60 && RM_TitanKernel.DigestTicks(0.4f) == 60, "DigestTicks values");
            Check(RM_TitanKernel.StruggleDamage(true, 8, 1f) == 4f && RM_TitanKernel.StruggleDamage(false, 99, 1.5f) == 3f, "StruggleDamage");
            for (int k = 0; k < 20; k++)
            {
                float hb = (float)(r.NextDouble() * 9), sb = (float)(r.NextDouble() * 40);
                float c = RM_TitanKernel.BurstChance(hb, sb);
                Check(c >= 0f && c <= 0.10001f, "BurstChance out of [0, 10%]");
                Check(RM_TitanKernel.BurstChance(hb + 1f, sb) >= c - 1e-6f, "BurstChance fell as the prey grew");
            }
            // starting mass: partition, never a zero-weight value, boundaries
            var w = new List<float>(); var v = new List<float>(); int nw = 1 + r.Next(5);
            for (int i = 0; i < nw; i++) { w.Add(r.Next(3) == 0 ? 0f : 1 + r.Next(9)); v.Add(i * 10f); }
            float total = w.Sum();
            var probes = new List<float> { 0f, 1f, 0.5f };
            float cum = 0f; for (int i = 0; i < nw; i++) { cum += w[i]; if (total > 0) { probes.Add(cum / total); probes.Add(Math.Max(0f, cum / total - 1e-4f)); probes.Add(Math.Min(1f, cum / total + 1e-4f)); } }
            foreach (float pr in probes)
            {
                float got = RM_TitanKernel.RollMass(w, v, pr);
                if (total <= 0f) { Check(got == 0f, "an all-zero table rolled a mass"); continue; }
                float rr = pr * total, cc = 0f; float want = -1f;
                for (int i = 0; i < nw && want < 0f; i++) { if (w[i] <= 0f) continue; cc += w[i]; if (rr <= cc + 1e-4f * 0) { want = v[i]; } }
                if (want < 0f) want = v[w.FindLastIndex(x => x > 0f)];
                Check(got == want, $"RollMass({pr}) = {got}, the weighted table says {want} (weights {string.Join(",", w)})");
                int gi = (int)(got / 10f);
                Check(w[gi] > 0f, "RollMass picked a zero-weight entry"); RollEdges++;
            }
            Check(RM_TitanKernel.RollMass(new List<float>(), new List<float>(), 0.5f) == 0f && RM_TitanKernel.RollMass(new List<float> { 1f }, new List<float> { 1f, 2f }, 0.5f) == 0f, "malformed table");
            // max stage index
            for (int s = -2; s <= 8; s++) { int m = RM_TitanKernel.MaxStageIndex(4, s); Check(m >= 0 && m <= 4 && m == Math.Min(4, Math.Max(1, Math.Min(5, s)) - 1), $"MaxStageIndex(4,{s}) = {m}"); }
            return null;
        }

        private static List<string> TitanProps(int n, int baseSeed) { return Family("titan-props", n, baseSeed, RunTitanProps); }

        // ════════════════════════ world ════════════════════════
        public static long ScoresPositive, ScoresZero, ShelfExpiries, PayShort, PayExact;

        private static string RunWorld(int seed)
        {
            var r = new Random(seed); Steps += 140;
            // biome score vs a literal spec
            for (int k = 0; k < 30; k++)
            {
                bool water = r.Next(10) == 0, mtn = r.Next(8) == 0; float rarity = new[] { 0f, 0.001f, 0.5f, 1f, 3f }[r.Next(5)];
                float tMin = 8, tMax = 34, rMin = 1400, rMax = 6000, eMin = 0, eMax = 900;
                float temp = r.Next(-5, 40), rain = r.Next(1200, 6200), elev = r.Next(-50, 1000);
                if (r.Next(4) == 0) rain = new[] { rMin, rMax, rMax - 1f }[r.Next(3)];
                if (r.Next(4) == 0) temp = new[] { tMin, tMax }[r.Next(2)];
                float chance = new[] { 0.012f, 1f, 2f }[r.Next(3)]; bool gateOpen = r.Next(2) == 0; int gateCalls = 0;
                float got = RM_SlimeWorld.BiomeScore(water, rarity, temp, tMin, tMax, rain, rMin, rMax, elev, eMin, eMax, mtn, chance, g => { gateCalls++; return gateOpen; }, 36f, 0.25f, 400f);
                float want;
                if (water || rarity <= 0.001f) want = -100f;
                else if (temp < tMin || temp > tMax || rain < rMin || rain >= rMax || elev < eMin || elev > eMax || mtn) want = 0f;
                else if (chance * rarity < 1f && !gateOpen) want = 0f;
                else want = 36f + (temp - tMin) * 0.25f + (rain - rMin) / 400f;
                Check(Near(got, want, 1e-3f), $"BiomeScore {got} want {want} (water {water}, rarity {rarity}, temp {temp}, rain {rain}, elev {elev}, mtn {mtn}, gate {gateOpen})");
                if (chance * rarity >= 1f) Check(gateCalls == 0, "the seeded gate was rolled although it cannot fail");
                if (got > 0f) ScoresPositive++; else ScoresZero++;
            }
            // farm conversion
            for (int k = 0; k < 20; k++)
            {
                int area = r.Next(1, 90000); float rate = new[] { 0.25f, 1f, 4f }[r.Next(3)]; float roll = (float)r.NextDouble();
                int got = RM_SlimeWorld.ConversionAttempts(area, rate, 1000f, roll);
                float wanted = area / 1000f * rate;
                Check(got >= 1 && got >= (int)wanted && got <= (int)wanted + 1 || (int)wanted == 0 && got == 1, $"ConversionAttempts({area},{rate}) = {got}");
                Check(RM_SlimeWorld.ConversionAttempts(area, rate, 1000f, 0f) >= RM_SlimeWorld.ConversionAttempts(area, rate, 1000f, 0.999999f), "a lower roll gave fewer attempts");
            }
            // chunk shelf: sequence
            {
                int shelf = RM_SlimeWorld.ShelfTicks(new[] { 0.5f, 1.5f, 5f, 0.0f }[r.Next(4)], 60000f);
                Check(shelf >= 6000, "shelf life under 0.1 day");
                Check(RM_SlimeWorld.ShelfTicks(1.5f, 60000f) == 90000 && RM_SlimeWorld.ShelfTicks(0f, 60000f) == 6000, "ShelfTicks values");
                int born = -1, now = r.Next(1000); bool expired = false; int bornAt = -1;
                for (int s = 0; s < 60 && !expired; s++)
                {
                    now += 250 * (1 + r.Next(40));
                    bool was = born < 0;
                    expired = RM_SlimeWorld.ShelfSweep(ref born, now, shelf);
                    if (was) { Check(!expired && born == now, "an unstamped chunk was not stamped now (or expired at once)"); bornAt = now; }
                    else { Check(expired == (now - bornAt >= shelf), $"chunk expiry at age {now - bornAt} of {shelf}"); Check(born == bornAt, "born changed"); if (expired) ShelfExpiries++; }
                }
            }
            // burst ground
            for (int m = 0; m < 32; m++)
            {
                bool has = (m & 1) != 0, nat = (m & 2) != 0, water = (m & 4) != 0, slime = (m & 8) != 0, found = (m & 16) != 0;
                Check(RM_SlimeWorld.CanConvertGround(has, nat, water, slime, found) == (has && nat && !water && !slime && !found), "CanConvertGround truth table");
            }
            // archive
            for (int m = 0; m < 32; m++)
            {
                bool ex = (m & 1) != 0, dead = (m & 2) != 0, hl = (m & 4) != 0, named = (m & 8) != 0, col = (m & 16) != 0;
                Check(RM_SlimeWorld.ArchiveFiles(ex, dead, hl, named, col) == (ex && !dead && hl && named && col), "ArchiveFiles truth table");
            }
            for (int k = 0; k < 20; k++)
            {
                int n = r.Next(0, 7); var stacks = new List<int>(); var forb = new List<bool>();
                for (int i = 0; i < n; i++) { stacks.Add(1 + r.Next(80)); forb.Add(r.Next(4) == 0); }
                int need = r.Next(0, 300);
                int[] takes = RM_SlimeWorld.PayPlan(stacks, forb, need, out int shortfall);
                int avail = 0; for (int i = 0; i < n; i++) if (!forb[i]) avail += stacks[i];
                int paid = takes.Sum();
                Check(paid == Math.Min(need, avail) && shortfall == need - paid, $"PayPlan paid {paid} of {need} with {avail} available, shortfall {shortfall}");
                for (int i = 0; i < n; i++)
                {
                    Check(takes[i] >= 0 && takes[i] <= stacks[i], "PayPlan took more than a stack holds");
                    if (forb[i]) Check(takes[i] == 0, "PayPlan took from a forbidden stack");
                    if (takes[i] > 0 && takes[i] < stacks[i]) Check(takes.Skip(i + 1).All(t => t == 0), "PayPlan took from later stacks before emptying this one");
                }
                if (shortfall > 0) PayShort++; else PayExact++;
            }
            return null;
        }

        private static List<string> World(int n, int baseSeed) { return Family("world", n, baseSeed, RunWorld); }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("ladder", () => { var f = Ladder(N(3000), S(1)); f.AddRange(LadderProps(N(1000), S(1))); return f; }),
                ("titan", () => { var f = Titan(N(3000), S(1)); f.AddRange(TitanProps(N(1000), S(1))); return f; }),
                ("world", () => World(N(2000), S(1))),
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
            Console.WriteLine($"reached: ladder dissolutions {Dissolutions}, cures {Cures} (refused at 1.0: {CuresRefused}), announces {Announces}, fast-clock steps {FastLives}, dry-country clears {DryClears}, dose caps {DoseCaps}, wipe-offs {WipeOffs}, holds {Holds}");
            Console.WriteLine($"reached: titan stages up {TitanStagesUp} / down {TitanStagesDown}, letters {TitanLetters}, sheds {TitanSheds}, losses applied {TitanLossApplied} / blocked {TitanLossBlocked}, frozen {TitanFrozen}, engulf ok {EngulfOk} / no {EngulfNo}, roll edges {RollEdges}");
            Console.WriteLine($"reached: world scores >0 {ScoresPositive} / 0 {ScoresZero}, shelf expiries {ShelfExpiries}, pay short {PayShort} / exact {PayExact}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (Dissolutions == 0 || Cures == 0 || CuresRefused == 0 || Announces == 0 || FastLives == 0 || DryClears == 0 || DoseCaps == 0 || WipeOffs == 0 || Holds == 0
                    || TitanStagesUp == 0 || TitanStagesDown == 0 || TitanLetters == 0 || TitanSheds == 0 || TitanLossApplied == 0 || TitanLossBlocked == 0 || TitanFrozen == 0 || EngulfOk == 0 || EngulfNo == 0
                    || ScoresPositive == 0 || ScoresZero == 0 || ShelfExpiries == 0 || PayShort == 0 || PayExact == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"gelatinousslime fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
