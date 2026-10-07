// Approach B for WeepingStones: seeded fuzz over the Verse-free kernels the WeepingStones mod calls (../Kernel/*.cs):
//   pool       the stocked-pool READ gauge, feed clock and per-pulse dice (RM_PoolKernel): action sequences vs a spec ledger
//   condenser  the walking condenser's phase machine, pool growth and drying schedule (RM_CondenserKernel) over a mock
//              terrain grid, plus the ancient condenser's water accumulator
//   claim      the condenser quests' exclusive claim over a mock quest manager (RM_ClaimKernel)
//   slot       the faction-slot resolution vs an explicit-scan oracle
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.WeepingStones.SelfTest
{
    internal static class WeepingStonesFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private const int Tpd = 60000;

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

        // ════════════════════════ pool ════════════════════════
        private static readonly string[] PoolNames = { "Pulse", "Feed", "Add", "Remove", "Time", "Cells", "Setting", "CullVhorrin" };
        public static long PStarve, PEmerge, PEscape, PPulses, PVhorrinStates, PCrashed;

        private static List<Act> GenPool(Random r)
        {
            int n = 10 + r.Next(70);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 45 ? 0 : w < 52 ? 1 : w < 70 ? 2 : w < 76 ? 3 : w < 88 ? 4 : w < 92 ? 5 : w < 97 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = PoolNames });
            }
            return l;
        }

        private static string RunPool(int seed, List<Act> acts)
        {
            var rng = new Random(seed ^ 0x3131);
            int normals = rng.Next(0, 6), vizhik = rng.Next(0, 3), vhorrin = rng.Next(0, 2) == 0 ? 0 : 1, cells = 1 + rng.Next(8);
            int now = 100000, lastFed = now;
            float odds = new[] { 1f, 0f, 3f, 100f }[rng.Next(4)], escape = new[] { 0.05f, 0f, 0.25f, 1f }[rng.Next(4)];
            int pulseNo = 0;
            string where = "";
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 1: lastFed = now; Check(!RM_PoolKernel.NeedsFeed(lastFed, now, Tpd) && RM_PoolKernel.UnfedDays(lastFed, now, Tpd) == 0, "a fed pen still needs feeding"); break;
                        case 2: if (a.a % 4 == 0) vizhik++; else normals++; break;
                        case 3: if (a.a % 3 == 0 && vizhik > 0) vizhik--; else if (normals > 0) normals--; break;
                        case 4: now += (a.a % 6 == 0 ? 250 : 1) * (1 + a.b % 70000); break;
                        case 5: cells = 1 + a.a % 12; break;
                        case 6: if (a.a % 2 == 0) odds = new[] { 1f, 0f, 3f, 100f }[a.b % 4]; else escape = new[] { 0.05f, 0f, 0.25f, 1f }[a.b % 4]; break;
                        case 7: if (vhorrin > 0 && a.a % 2 == 0) vhorrin--; break;
                        case 0:
                            {
                                pulseNo++; PPulses++;
                                int cand = normals + vizhik, population = normals + vizhik + vhorrin;
                                int unfed = RM_PoolKernel.UnfedDays(lastFed, now, Tpd);
                                int specUnfed = Math.Max(0, now - lastFed) / Tpd;
                                Check(unfed == specUnfed, $"UnfedDays {unfed} != spec {specUnfed}");
                                Check(RM_PoolKernel.NeedsFeed(lastFed, now, Tpd) == (now - lastFed >= Tpd), "NeedsFeed disagrees with a full day since the last feed");
                                int calls = 0; var drng = new Random(seed * 7919 + pulseNo);
                                var p = RM_PoolKernel.Decide(population, vhorrin, cells, unfed, cand, vizhik, odds, escape, () => { calls++; return (float)drng.NextDouble(); }, n => drng.Next(n));
                                // ---- spec: the gauge ----
                                RM_PoolStockState specState = vhorrin > 0 ? RM_PoolStockState.Vhorrin : population <= 0 ? RM_PoolStockState.Silent
                                    : (unfed >= 2 || population * 2 < cells) ? RM_PoolStockState.Thin : RM_PoolStockState.Healthy;
                                Check(p.state == specState, $"gauge {p.state} != spec {specState} (pop {population}, vhorrin {vhorrin}, cells {cells}, unfed {unfed})");
                                if (p.state == RM_PoolStockState.Vhorrin) PVhorrinStates++;
                                // ---- spec: which dice may fire, and how many rolls they consume ----
                                bool crowded = cells > 0 && population >= cells, crashed = unfed >= 3;
                                int expectCalls = 0;
                                if (unfed >= 3 && cand > 0) expectCalls++;                       // 0.03: always a roll
                                float ec = (crowded ? 0.02f : crashed ? 0.01f : 0f) * odds;
                                if (vhorrin <= 0 && cand > 0 && ec > 0f && ec < 1f) expectCalls++;
                                if (vizhik > 0 && escape > 0f && escape < 1f) expectCalls++;
                                Check(calls == expectCalls, $"dice consumed {calls} rolls, spec {expectCalls} (a roll is spent only for a chance strictly between 0 and 1)");
                                if (p.starveIdx >= 0) { PStarve++; Check(unfed >= 3 && p.starveIdx < cand, $"starvation idx {p.starveIdx} with unfed {unfed}, candidates {cand}"); }
                                if (p.emergeIdx >= 0) { PEmerge++; Check(vhorrin == 0 && cand > 0 && p.emergeIdx < cand && ec > 0f && (crowded || crashed) && odds > 0f, $"emergence at idx {p.emergeIdx} (vhorrin {vhorrin}, crowded {crowded}, crashed {crashed}, odds {odds})"); }
                                if (p.escapeIdx >= 0) { PEscape++; Check(vizhik > 0 && p.escapeIdx < vizhik && escape > 0f, "escape of a nonexistent vizhik"); }
                                if (unfed < 3 && !crowded) Check(p.starveIdx < 0 && p.emergeIdx < 0, "a fed, uncrowded pen decayed or bred a vhorrin");
                                if (crashed) PCrashed++;
                                // ---- apply, as the mod does (candidates are [normals..., vizhiks...]) ----
                                bool victimGone = false; int victimIdx = p.starveIdx;
                                if (p.starveIdx >= 0) { if (p.starveIdx < normals) normals--; else vizhik--; victimGone = true; }
                                int vBefore = vhorrin;
                                if (p.emergeIdx >= 0 && !(victimGone && p.emergeIdx == victimIdx))
                                {
                                    // the chosen resident is still standing: it turns into the vhorrin (it was never a vhorrin, by construction)
                                    if (p.emergeIdx < normals + (victimGone && victimIdx < normals ? 1 : 0)) normals--; else vizhik--;
                                    vhorrin++;
                                }
                                Check(vhorrin - vBefore <= 1, "more than one vhorrin in one pulse");
                                if (p.escapeIdx >= 0 && vizhik > 0) { vizhik--; }
                                Check(normals >= 0 && vizhik >= 0 && vhorrin >= 0, "negative population");
                                break;
                            }
                    }
                }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string PoolUnits(int seed)
        {
            // gauge truth: exhaustive
            for (int pop = 0; pop <= 6; pop++) for (int vh = 0; vh <= 1; vh++) for (int cells = 0; cells <= 9; cells++) for (int unfed = 0; unfed <= 4; unfed++)
            {
                Steps++;
                var got = RM_PoolKernel.ClassifyState(pop, vh, cells, unfed);
                var want = vh > 0 ? RM_PoolStockState.Vhorrin : pop <= 0 ? RM_PoolStockState.Silent : unfed >= 2 ? RM_PoolStockState.Thin
                    : (cells > 0 && pop * 2 < cells) ? RM_PoolStockState.Thin : RM_PoolStockState.Healthy;
                Check(got == want, $"ClassifyState({pop},{vh},{cells},{unfed})={got}, want {want}");
            }
            Check(RM_PoolKernel.UnfedDays(-1, 999999, Tpd) == 0 && RM_PoolKernel.NeedsFeed(-1, 0, Tpd), "an unrecorded feed reads as 0 unfed days but due");
            Check(RM_PoolKernel.UnfedDays(100, 50, Tpd) == 0, "a feed in the future must not read as negative days");
            Check(RM_PoolKernel.UnfedDays(0, Tpd - 1, Tpd) == 0 && RM_PoolKernel.UnfedDays(0, Tpd, Tpd) == 1 && RM_PoolKernel.UnfedDays(0, 3 * Tpd, Tpd) == 3, "UnfedDays day boundaries");
            Check(!RM_PoolKernel.NeedsFeed(0, Tpd - 1, Tpd) && RM_PoolKernel.NeedsFeed(0, Tpd, Tpd), "NeedsFeed boundary at exactly one day");
            Check(RM_PoolKernel.Chance(0f, () => throw new Exception("rolled for chance 0")) == false && RM_PoolKernel.Chance(1f, () => throw new Exception("rolled for chance 1")), "Chance must not roll at 0 or 1");
            Check(RM_PoolKernel.Chance(0.5f, () => 0.4999f) && !RM_PoolKernel.Chance(0.5f, () => 0.5f), "Chance is strictly below");
            // empirical rates (seeded): the stated per-pulse chances are what the dice deliver
            var r = new Random(seed);
            int N = 200000, starve = 0, emergeCrowd = 0, emergeCrash = 0, escapes = 0;
            for (int i = 0; i < N; i++)
            {
                Steps++;
                var pc = RM_PoolKernel.Decide(4, 0, 4, 4, 4, 1, 1f, 0.05f, () => (float)r.NextDouble(), n => r.Next(n));        // crowded AND crashed -> crowded wins (0.02)
                if (pc.starveIdx >= 0) starve++; if (pc.emergeIdx >= 0) emergeCrowd++; if (pc.escapeIdx >= 0) escapes++;
                var pk = RM_PoolKernel.Decide(2, 0, 8, 4, 2, 0, 1f, 0.05f, () => (float)r.NextDouble(), n => r.Next(n));         // crashed only -> 0.01
                if (pk.emergeIdx >= 0) emergeCrash++;
            }
            void Rate(string what, int hits, double p)
            {
                double sd = Math.Sqrt(N * p * (1 - p)), mean = N * p;
                Check(Math.Abs(hits - mean) <= 5 * sd, $"{what}: {hits} of {N} (expected {mean:F0} +-{5 * sd:F0})");
            }
            Rate("starvation 0.03", starve, 0.03); Rate("crowded emergence 0.02", emergeCrowd, 0.02); Rate("crashed emergence 0.01", emergeCrash, 0.01); Rate("vizhik escape 0.05", escapes, 0.05);
            Check(RM_PoolKernel.EmergenceChance(true, true, 1f) == 0.02f && RM_PoolKernel.EmergenceChance(false, true, 1f) == 0.01f && RM_PoolKernel.EmergenceChance(false, false, 3f) == 0f && RM_PoolKernel.EmergenceChance(true, false, 3f) == 0.02f * 3f, "EmergenceChance table");
            Check(!RM_PoolKernel.Crowded(0, 5) && RM_PoolKernel.Crowded(3, 3) && !RM_PoolKernel.Crowded(3, 2), "Crowded");
            return null;
        }

        public static List<string> Pool(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { string e = PoolUnits(baseSeed); if (e != null) fails.Add("pool units: " + e); } catch (Exception e) { fails.Add("pool units: " + e.Message); }
            fails.AddRange(Family("pool", n, baseSeed, s => Drive(s, GenPool, RunPool)));
            return fails;
        }

        // ════════════════════════ condenser ════════════════════════
        private static readonly string[] CondNames = { "Step", "Enable", "Guide", "Cut", "Die", "Interrupt", "Site" };
        public static long CWait, CWalk, CArrive, CNoSite, CDried, CGrown;

        private static List<Act> GenCond(Random r)
        {
            int n = 6 + r.Next(40);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 62 ? 0 : w < 70 ? 1 : w < 78 ? 2 : w < 80 ? 3 : w < 83 ? 4 : w < 92 ? 5 : 6;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = CondNames });
            }
            return l;
        }

        // lattice of disc offsets sorted by squared distance (index k of generation g is cell g*100000+k)
        private static readonly List<int> Disc = BuildDisc();
        private static List<int> BuildDisc()
        {
            var l = new List<int>();
            for (int x = -6; x <= 6; x++) for (int z = -6; z <= 6; z++) l.Add(x * x + z * z);
            l.Sort();
            return l;
        }

        private static string RunCond(int seed, List<Act> acts)
        {
            var rng = new Random(seed ^ 0x6161);
            int maxRadius = 1 + rng.Next(5); float growDays = new[] { 0.25f, 1f, 3f }[rng.Next(3)], dryDays = new[] { 0.5f, 1f, 4f }[rng.Next(3)];
            int seasonTicks = (int)(new[] { 0.25f, 0.5f, 1f, 2f }[rng.Next(4)] * Tpd);
            var st = new CondenserState { phase = RM_CondenserPhase.Settled, phaseStartTick = -1, settleTick = 1000, poolRadius = 0, dryStartCount = -1 };
            bool targetValid = false, enabled = true, siteAvail = true, hasGoto = false, alive = true;
            int now = 1000, gen = 0; double dist = 0; const double Speed = 12;
            // cells: id = gen*100000 + k ; eligible fixed per id
            var pool = new Dictionary<int, int>();   // id -> original terrain id
            var terrain = new Dictionary<int, int>(); // id -> current terrain (absent = baseline 0)
            const int Water = 99;
            int Base(int id) { return 1 + (id % 5); }
            bool Eligible(int id) { return (id * 2654435761u) % 5 != 0; }
            // timeline checks
            RM_CondenserPhase lastPhase = st.phase; int phaseEnter = now; bool disturbed = false;
            int dryBegan = -1, dryCountAtBegin = 0;
            string where = "";

            string Grid()   // terrain consistency: pool cells are water, everything else baseline
            {
                foreach (var kv in terrain) { if (kv.Value == Water && !pool.ContainsKey(kv.Key)) return $"cell {kv.Key} is water but not in the pool"; }
                foreach (var kv in pool) { if (!terrain.TryGetValue(kv.Key, out int t) || t != Water) return $"pool cell {kv.Key} is not water"; }
                return null;
            }
            void Restore(int id) { terrain.Remove(id); pool.Remove(id); }
            void DryAll() { foreach (int id in pool.Keys.ToList()) Restore(id); st.drying = false; }
            void StepDrying()
            {
                if (!st.drying || pool.Count == 0 || !alive) { if (pool.Count == 0) st.drying = false; return; }
                int n = RM_CondenserKernel.DryRestore(ref st, now, pool.Count, dryDays, Tpd);
                Check(n >= 0 && n <= pool.Count, $"DryRestore {n} of {pool.Count}");
                foreach (int id in pool.Keys.OrderByDescending(k => k / 100000 != gen ? 1000000 + (gen - k / 100000) : Disc[k % 100000]).Take(n).ToList()) Restore(id);
                if (pool.Count == 0) { st.drying = false; if (dryBegan >= 0) { double took = now - dryBegan; CDried++; Check(took >= dryDays * Tpd - 250 - 1 && took <= dryDays * Tpd + 500, $"the pool of {dryCountAtBegin} cells dried in {took} ticks, dryDays {dryDays} = {dryDays * Tpd}"); dryBegan = -1; } }
            }
            int Materialise(int radius)
            {
                Check(radius >= 1 && radius <= maxRadius, $"pool radius {radius} outside [1,{maxRadius}]");
                int cb = pool.Count;
                for (int k = 0; k < Disc.Count && Disc[k] <= radius * radius; k++)
                {
                    int id = gen * 100000 + k;
                    if (pool.ContainsKey(id) || !Eligible(id)) continue;
                    pool[id] = Base(id); terrain[id] = Water;
                }
                if (pool.Count > cb) CGrown++;
                return pool.Count;
            }

            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 1: enabled = !enabled; disturbed = true; break;
                        case 2: if (st.phase == RM_CondenserPhase.Waiting && alive) { targetValid = true; dist = 30 + a.a % 120; } break;
                        case 3: if (alive) { DryAll(); alive = false; } break;
                        case 4: if (alive) { DryAll(); alive = false; } break;
                        case 5: hasGoto = false; break;
                        case 6: siteAvail = !siteAvail; break;
                        case 0:
                            for (int t = 0, n = 1 + a.a % (a.b % 3 == 0 ? 700 : 60); t < n && alive; t++)
                            {
                                now += 250;
                                if (!enabled)
                                {
                                    if (pool.Count > 0) RM_CondenserKernel.StartDrying(ref st, now, pool.Count);
                                    if (st.drying && dryBegan < 0 && pool.Count > 0) { dryBegan = now; dryCountAtBegin = pool.Count; }
                                    StepDrying();
                                }
                                else
                                {
                                    if (st.phase == RM_CondenserPhase.Walking && targetValid) dist = Math.Max(0, dist - Speed);
                                    var before = st; bool wasValid = targetValid; int poolBefore = pool.Count; bool dryingBefore = st.drying;
                                    var act = RM_CondenserKernel.Tick(ref st, ref targetValid, now, seasonTicks, Tpd, (float)dist, hasGoto, pool.Count,
                                        maxRadius, growDays, () => (float)rng.NextDouble(), Materialise,
                                        () => { bool ok = siteAvail; if (ok) dist = 25 + rng.Next(150); return ok; });
                                    // ---- transition rules ----
                                    bool left = st.phase != before.phase;
                                    if (before.phase == RM_CondenserPhase.Settled && st.phase == RM_CondenserPhase.Waiting)
                                    {
                                        CWait++;
                                        Check(now - before.settleTick >= seasonTicks, $"left Settled after {now - before.settleTick} ticks, season {seasonTicks}");
                                        if (!disturbed) Check(now - before.settleTick < seasonTicks + 250, "stayed Settled a whole poll past the season");
                                        Check((act & CondenserAct.BeginWaiting) != 0 && !targetValid, "Waiting must start with no target");
                                        if (pool.Count > 0) { Check(st.drying && (dryingBefore || (act & CondenserAct.StartedDrying) != 0), "a pool was left undrying at the start of Waiting"); }
                                        if (!dryingBefore && st.drying) { Check((act & CondenserAct.StartedDrying) != 0 && st.dryStartCount == pool.Count, $"drying began without StartedDrying or with a stale count ({st.dryStartCount} vs {pool.Count} cells)"); dryBegan = now; dryCountAtBegin = pool.Count; }
                                        disturbed = false;
                                    }
                                    else if (before.phase == RM_CondenserPhase.Waiting && (st.phase == RM_CondenserPhase.Walking || st.phase == RM_CondenserPhase.Settled))
                                    {
                                        Check(now - before.phaseStartTick >= Tpd, $"Waiting lasted {now - before.phaseStartTick} ticks, a day is {Tpd}");
                                        if (st.phase == RM_CondenserPhase.Walking) { CWalk++; Check(targetValid && (act & CondenserAct.IssueGoto) != 0, "Walking began with no target or no goto"); dist = Math.Max(dist, 25); hasGoto = true; }
                                        else { CNoSite++; Check((act & CondenserAct.NoSite) != 0 && !targetValid && st.poolRadius == 0 && st.settleTick == now, "no-site fallback state"); }
                                    }
                                    else if (before.phase == RM_CondenserPhase.Walking && st.phase == RM_CondenserPhase.Settled)
                                    {
                                        CArrive++;
                                        Check(!wasValid || dist < 3 || now - before.phaseStartTick > 3 * Tpd, "arrived without reaching the target, timing out or losing it");
                                        Check(st.poolRadius == 0 && st.settleTick == now && st.drying == (pool.Count > 0), "arrival must reset the radius and keep a leftover pool drying");
                                        gen++; hasGoto = false; dist = 0; targetValid = false;
                                    }
                                    else if (!left && before.phase == RM_CondenserPhase.Walking)
                                    {
                                        Check(wasValid && dist >= 3 && now - before.phaseStartTick <= 3 * Tpd, "kept walking after arriving or timing out");
                                        if ((act & CondenserAct.IssueGoto) != 0) { Check(!hasGoto, "re-issued a goto while one was running"); hasGoto = true; }
                                    }
                                    else Check(!left, $"illegal phase change {before.phase} -> {st.phase}");
                                    if (st.phase == RM_CondenserPhase.Walking && before.phase != RM_CondenserPhase.Walking) { }
                                    // ---- effects ----
                                    if ((act & CondenserAct.Grow) != 0) Check(before.phase == RM_CondenserPhase.Settled && !dryingBefore, "grew while not settled or while drying");
                                    if (pool.Count > poolBefore) Check((act & CondenserAct.Grow) != 0, "the pool grew without a Grow act");
                                    if ((act & CondenserAct.StepDry) != 0) StepDrying();
                                    Check(st.poolRadius >= 0 && st.poolRadius <= maxRadius, "pool radius out of range");
                                    if (disturbed && before.phase == st.phase) { }
                                }
                                // ---- invariants every poll ----
                                string g = Grid(); Check(g == null, g);
                                if (st.phase == RM_CondenserPhase.Settled && !st.drying)
                                    foreach (int id in pool.Keys) Check(id / 100000 == gen, $"pool cell {id} of an old generation is stranded as permanent water (Settled, not drying)");
                                if (st.drying) Check(pool.Count > 0 || true, "");
                                if (st.phase == RM_CondenserPhase.Waiting || st.phase == RM_CondenserPhase.Walking) Check(st.drying || pool.Count == 0 || !enabled, $"a moving crab left its pool undrying (phase {st.phase}, pool {pool.Count}, start {st.dryStartCount}@{st.dryStartTick}, now {now}, radius {st.poolRadius})");
                                Check(st.phase != RM_CondenserPhase.Gone, "Gone is unreachable");
                            }
                            break;
                    }
                }
                // liveness: after the crab leaves and enough time passes with the setting on or off, no water stays behind
                if (alive && pool.Count > 0)
                {
                    enabled = false;
                    for (int i = 0; i < (int)(dryDays * Tpd / 250) + 4 && pool.Count > 0; i++)
                    {
                        now += 250; RM_CondenserKernel.StartDrying(ref st, now, pool.Count); if (st.drying && dryBegan < 0) { dryBegan = now; dryCountAtBegin = pool.Count; }
                        StepDrying(); Steps++;
                    }
                    Check(pool.Count == 0, $"{pool.Count} pool cells still water {dryDays} days after the setting was turned off");
                }
                if (pool.Count == 0) { string g = Grid(); Check(g == null && terrain.Count == 0, "terrain not restored to baseline: " + g); }
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string CondUnits(int seed)
        {
            var r = new Random(seed);
            // growth: radius reaches max, never past it, monotone; mean steps ~ 1 + (max-1)/perStep within a margin
            foreach (int max in new[] { 1, 2, 5 }) foreach (float gd in new[] { 0.25f, 1f, 3f })
            {
                long total = 0; int runs = 200;
                for (int i = 0; i < runs; i++)
                {
                    int rad = 0, n = 0;
                    while (rad < max && n < 100000) { int nr = RM_CondenserKernel.GrowRadius(rad, max, gd, Tpd, () => (float)r.NextDouble()); Check(nr >= Math.Max(rad, 1) && nr <= max, $"GrowRadius {rad} -> {nr} (max {max})"); rad = nr; n++; Steps++; }
                    Check(rad == max, $"radius never reached {max} (growDays {gd})");
                    total += n;
                }
                double perStep = max / Math.Max(1.0, gd * Tpd / 250.0), expect = max == 1 ? 1 : 1 + (max - 1) / perStep;
                Check(Math.Abs(total / (double)runs - expect) <= 0.2 * expect + 1, $"mean steps to radius {max} at growDays {gd}: {total / (double)runs:F1}, expected {expect:F1}");
            }
            Check(RM_CondenserKernel.GrowRadius(5, 5, 3f, Tpd, () => throw new Exception("rolled at max")) == 5, "growth past the cap or a roll at the cap");
            Check(RM_CondenserKernel.GrowRadius(0, 3, 0.001f, Tpd, () => 0f) == 3, "a huge perStep must reach the cap at once");
            // drying schedule: never instant, linear, monotone, ends at exactly dryDays
            foreach (float dd in new[] { 0.5f, 4f }) foreach (int n0 in new[] { 1, 7, 81 })
            {
                int prev = n0 + 1; long dt = (long)(dd * Tpd);
                Check(RM_CondenserKernel.DryKeep(n0, 0, 0, dd, Tpd) == n0, "nothing may dry at the first instant");
                Check(RM_CondenserKernel.DryKeep(n0, 0, 1, dd, Tpd) == n0 || n0 == 0, "a tick in, still the full pool");
                Check(RM_CondenserKernel.DryKeep(n0, 0, (int)dt, dd, Tpd) == 0 && RM_CondenserKernel.DryKeep(n0, 0, (int)dt + 5, dd, Tpd) == 0, "fully dry at dryDays");
                Check(RM_CondenserKernel.DryKeep(n0, 0, (int)dt - 1, dd, Tpd) >= 0, "keep >= 0");
                for (long t = 0; t <= dt; t += 250)
                {
                    int k = RM_CondenserKernel.DryKeep(n0, 0, (int)t, dd, Tpd); Steps++;
                    Check(k >= 0 && k <= n0 && k <= prev, $"DryKeep not monotone/in range ({k} after {prev}, n0 {n0})");
                    double lin = n0 * (1.0 - t / (double)dt);
                    Check(k >= Math.Floor(lin) && k <= Math.Ceiling(lin) + 1e-9, $"DryKeep {k} not within one cell of linear {lin:F2}");
                    prev = k;
                }
                Check(RM_CondenserKernel.DryKeep(n0, 1000, 500, dd, Tpd) == n0, "a clock before the start keeps the whole pool");
            }
            Check(RM_CondenserKernel.DryKeep(5, 0, 100, 0f, Tpd) == 0, "dryDays 0 dries at once");
            // start / restore bookkeeping, old save adoption
            var s = new CondenserState { dryStartCount = -1 };
            Check(!RM_CondenserKernel.StartDrying(ref s, 5, 0) && !s.drying, "no pool, no drying");
            Check(RM_CondenserKernel.StartDrying(ref s, 5, 9) && s.drying && s.dryStartCount == 9 && s.dryStartTick == 5, "start drying records the count");
            Check(!RM_CondenserKernel.StartDrying(ref s, 6, 9), "already drying");
            var old = new CondenserState { drying = true, dryStartTick = 3, dryStartCount = -1 };
            Check(RM_CondenserKernel.DryRestore(ref old, 1000, 20, 4f, Tpd) == 0 && old.dryStartCount == 20 && old.dryStartTick == 1000, "an old save (no start count) must adopt the current pool and restore nothing at once");
            // water accumulator: due exactly every interval/250 rare ticks, cap respected
            foreach (int interval in new[] { 250, 2500, 3000, 7000 })
            {
                int acc = 0, due = 0, N = 1000;
                for (int i = 0; i < N; i++) { Steps++; if (RM_CondenserKernel.WaterDue(ref acc, 250, interval)) due++; }
                Check(due == N / ((interval + 249) / 250), $"water due {due} times in {N} rare ticks at interval {interval}");
            }
            Check(RM_CondenserKernel.WaterSpawns(59, 60) && !RM_CondenserKernel.WaterSpawns(60, 60) && !RM_CondenserKernel.WaterSpawns(61, 60), "water cap");
            return null;
        }

        public static List<string> Condenser(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { string e = CondUnits(baseSeed); if (e != null) fails.Add("condenser units: " + e); } catch (Exception e) { fails.Add("condenser units: " + e.Message); }
            fails.AddRange(Family("condenser", n, baseSeed, s => Drive(s, GenCond, RunCond)));
            return fails;
        }

        // ════════════════════════ claim ════════════════════════
        private static readonly string[] ClaimNames = { "Offer", "Accept", "End", "Tick", "CrabDies", "WorldEnds", "Setting", "Fail" };
        public static long QOffers, QAccepts, QWithdrawn, QSuccess, QRivalWithdraws;

        private sealed class Quest { public int id; public int state;   /* 0 NotYet 1 Ongoing 2 Success 3 Fail 4 Invalid */ public bool Historical => state >= 2; }

        private static List<Act> GenClaim(Random r)
        {
            int n = 8 + r.Next(50);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(100);
                int kind = w < 28 ? 0 : w < 48 ? 1 : w < 58 ? 2 : w < 80 ? 3 : w < 84 ? 4 : w < 87 ? 5 : w < 93 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = ClaimNames });
            }
            return l;
        }

        private static string RunClaim(int seed, List<Act> acts)
        {
            var quests = new List<Quest>(); int nextId = 1;
            int claim = -1; bool settled = false, ended = false, condenserOn = true, questsOn = true, crabAlive = true;
            string where = "";
            bool Held(out int newClaim)
            {
                var q = quests.FirstOrDefault(x => x.id == claim);
                return RM_ClaimKernel.ClaimStillHeld(claim, q != null, q != null && q.Historical, out newClaim);
            }
            try
            {
                int step = 0;
                foreach (var a in acts)
                {
                    step++; Steps++; where = " at step " + step + " " + a;
                    switch (a.kind)
                    {
                        case 0:
                            {
                                bool held = Held(out int nc); claim = nc;
                                bool open = RM_ClaimKernel.OffersOpen(condenserOn, questsOn, true, ended, settled, held);
                                bool spec = condenserOn && questsOn && !ended && !settled && !held;
                                Check(open == spec, $"OffersOpen {open} != spec {spec}");
                                if (open && crabAlive) { quests.Add(new Quest { id = nextId++ }); QOffers++; }
                                if (settled || ended || held) Check(!open, "an offer opened while the matter was settled, ended or claimed");
                                break;
                            }
                        case 1:
                            {
                                var pend = quests.Where(q => q.state == 0).ToList();
                                if (pend.Count == 0) break;
                                var q0 = pend[a.a % pend.Count];
                                q0.state = 1; claim = q0.id; QAccepts++;
                                foreach (var o in quests) if (RM_ClaimKernel.RivalWithdrawsOnAccept(true, o.state == 0, o.id, q0.id)) { o.state = 4; QRivalWithdraws++; }
                                break;
                            }
                        case 2: case 7:
                            {
                                var on = quests.Where(q => q.state == 1).ToList();
                                if (on.Count == 0) break;
                                var q0 = on[a.a % on.Count];
                                bool ok = a.kind == 2;
                                q0.state = ok ? 2 : 3;
                                RM_ClaimKernel.Cleanup(ref claim, ref settled, q0.id, ok);
                                if (ok) QSuccess++;
                                break;
                            }
                        case 3:   // the 250-tick poll of every unaccepted offer
                            foreach (var q in quests.Where(x => x.state == 0).ToList())
                            {
                                bool held = Held(out int nc); claim = nc;
                                if (RM_ClaimKernel.Withdraws(!crabAlive, true, ended, settled, held, claim, q.id))
                                {
                                    q.state = 4; QWithdrawn++;
                                    RM_ClaimKernel.Cleanup(ref claim, ref settled, q.id, false);
                                }
                            }
                            break;
                        case 4: crabAlive = false; break;
                        case 5: ended = true; break;
                        case 6: if (a.a % 2 == 0) condenserOn = !condenserOn; else questsOn = !questsOn; break;
                    }
                    // ---- invariants after every step ----
                    var ongoing = quests.Where(q => q.state == 1).ToList();
                    Check(ongoing.Count <= 1, $"{ongoing.Count} claim quests are Ongoing at once (ids {string.Join(",", ongoing.Select(q => q.id))})");
                    if (ongoing.Count == 1) Check(claim == ongoing[0].id, $"the Ongoing quest {ongoing[0].id} does not hold the claim ({claim})");
                    if (ongoing.Count == 0 && quests.All(q => q.state != 0)) Check(claim == -1 || quests.Any(q => q.id == claim && !q.Historical) == false || true, "");
                    if (claim >= 0) { var cq = quests.FirstOrDefault(q => q.id == claim); Check(cq != null && cq.state <= 1, $"the claim {claim} names a finished quest"); }
                    Check(!(quests.Any(q => q.state == 2) && !settled), "a successful claim quest did not settle the matter");
                    if (settled) Check(quests.All(q => q.state != 0 || true), "");
                }
                // after a poll, nothing unaccepted survives a held claim or a settled world
                foreach (var q in quests.Where(x => x.state == 0).ToList())
                {
                    bool held = Held(out int nc); claim = nc;
                    if (RM_ClaimKernel.Withdraws(!crabAlive, true, ended, settled, held, claim, q.id)) q.state = 4;
                }
                if (quests.Any(q => q.state == 1) || settled) Check(quests.All(q => q.state != 0), "an unaccepted offer outlived the claim / settlement");
                return null;
            }
            catch (Exception e) { return e.Message + where; }
        }

        private static string ClaimUnits()
        {
            for (int m = 0; m < 64; m++)
            {
                bool en = (m & 1) != 0, qs = (m & 2) != 0, w = (m & 4) != 0, ended = (m & 8) != 0, set = (m & 16) != 0, held = (m & 32) != 0;
                Check(RM_ClaimKernel.OffersOpen(en, qs, w, ended, set, held) == (en && qs && w && !ended && !set && !held), $"OffersOpen row {m}"); Steps++;
            }
            for (int m = 0; m < 128; m++)
            {
                bool gone = (m & 1) != 0, w = (m & 2) != 0, ended = (m & 4) != 0, set = (m & 8) != 0, held = (m & 16) != 0; int claimId = (m & 32) != 0 ? 7 : 3; int my = (m & 64) != 0 ? 7 : 4;
                bool want = gone || !w || ended || set || (held && claimId != my);
                Check(RM_ClaimKernel.Withdraws(gone, w, ended, set, held, claimId, my) == want, $"Withdraws row {m}"); Steps++;
            }
            int nc;
            Check(!RM_ClaimKernel.ClaimStillHeld(-1, true, false, out nc) && nc == -1, "no claim");
            Check(RM_ClaimKernel.ClaimStillHeld(5, true, false, out nc) && nc == 5, "live claim holds");
            Check(!RM_ClaimKernel.ClaimStillHeld(5, true, true, out nc) && nc == -1, "a historical claim releases");
            Check(!RM_ClaimKernel.ClaimStillHeld(5, false, false, out nc) && nc == -1, "a vanished claim releases");
            int c = 5; bool st = false;
            RM_ClaimKernel.Cleanup(ref c, ref st, 4, true); Check(c == 5 && st, "another quest's success settles but does not steal my claim");
            c = 5; st = false; RM_ClaimKernel.Cleanup(ref c, ref st, 5, false); Check(c == -1 && !st, "my failure releases the claim without settling");
            Check(RM_ClaimKernel.RivalWithdrawsOnAccept(true, true, 2, 1) && !RM_ClaimKernel.RivalWithdrawsOnAccept(true, true, 1, 1) && !RM_ClaimKernel.RivalWithdrawsOnAccept(true, false, 2, 1) && !RM_ClaimKernel.RivalWithdrawsOnAccept(false, true, 2, 1), "RivalWithdrawsOnAccept");
            return null;
        }

        public static List<string> Claim(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { ClaimUnits(); } catch (Exception e) { fails.Add("claim units: " + e.Message); }
            fails.AddRange(Family("claim", n, baseSeed, s => Drive(s, GenClaim, RunClaim)));
            return fails;
        }

        // ════════════════════════ slot ════════════════════════
        public static long SlotHits, SlotNull, SlotPreferred;

        private static string SlotCase(int seed)
        {
            var r = new Random(seed);
            string[] names = { "A", "B", "C", "D", "E" };
            var fs = new List<FactionInfo>();
            int n = r.Next(0, 9);
            for (int i = 0; i < n; i++)
                fs.Add(new FactionInfo
                {
                    id = i + 1, defName = names[r.Next(names.Length)], isPlayer = r.Next(12) == 0, defeated = r.Next(10) == 0, temporary = r.Next(10) == 0, hidden = r.Next(10) == 0,
                    humanlike = r.Next(6) != 0, hostile = r.Next(3) == 0, permanentEnemy = r.Next(4) == 0, techLevel = 1 + r.Next(7), goodwill = r.Next(-100, 101)
                });
            var pref = new List<string>(); int np = r.Next(0, 4); for (int i = 0; i < np; i++) pref.Add(names[r.Next(names.Length)]);
            var fb = (RM_FactionSlotFallback)r.Next(3);
            int exclude = r.Next(0, 3) == 0 ? r.Next(1, n + 2) : -1;
            var got = RM_ClaimKernel.Resolve(fs, pref, fb, exclude);
            Steps++;
            // oracle: explicit scans, first-wins on ties
            bool wantsHostile = fb == RM_FactionSlotFallback.Hunters;
            var usable = new List<FactionInfo>();
            foreach (var f in fs) if (!f.isPlayer && !f.defeated && !f.temporary && !f.hidden && f.humanlike && f.id != exclude && f.hostile == wantsHostile) usable.Add(f);
            int want = -1;
            foreach (string pn in pref)
            {
                int best = -1;
                foreach (var f in usable) if (f.defName == pn && (best < 0 || f.goodwill > usable.First(x => x.id == best).goodwill)) best = f.id;
                if (best >= 0) { want = best; SlotPreferred++; break; }
            }
            if (want < 0 && usable.Count > 0)
            {
                IEnumerable<FactionInfo> pool;
                if (fb == RM_FactionSlotFallback.Collector)
                {
                    int bt = -1, bg = int.MinValue; pool = usable.Where(f => !f.permanentEnemy).ToList();
                    foreach (var f in pool) if (f.techLevel > bt || (f.techLevel == bt && f.goodwill > bg)) { bt = f.techLevel; bg = f.goodwill; want = f.id; }
                }
                else if (fb == RM_FactionSlotFallback.Hunters)
                {
                    int bp = -1, bt = -1;
                    foreach (var f in usable) { int p = f.permanentEnemy ? 1 : 0; if (p > bp || (p == bp && f.techLevel > bt)) { bp = p; bt = f.techLevel; want = f.id; } }
                }
                else
                {
                    int bb = 2, bg = int.MinValue;
                    foreach (var f in usable.Where(x => !x.permanentEnemy)) { int b = f.techLevel > RM_ClaimKernel.IndustrialTech ? 1 : 0; if (b < bb || (b == bb && f.goodwill > bg)) { bb = b; bg = f.goodwill; want = f.id; } }
                }
            }
            if (want < 0) { SlotNull++; Check(!got.HasValue, $"resolved faction {got?.id} when none qualifies"); return null; }
            SlotHits++;
            Check(got.HasValue && got.Value.id == want, $"slot resolved {(got.HasValue ? got.Value.id.ToString() : "none")}, oracle {want} (fallback {fb}, preferred [{string.Join(",", pref)}], exclude {exclude})");
            var pick = got.Value;
            Check(!pick.isPlayer && !pick.defeated && !pick.temporary && !pick.hidden && pick.humanlike && pick.id != exclude && pick.hostile == wantsHostile, "resolved an unusable faction");
            return null;
        }

        public static List<string> Slot(int n, int baseSeed) { return Family("slot", n, baseSeed, SlotCase); }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("pool", () => Pool(N(3000), S(1))),
                ("condenser", () => Condenser(N(1500), S(1))),
                ("claim", () => Claim(N(3000), S(1))),
                ("slot", () => Slot(N(5000), S(1))),
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
            Console.WriteLine($"reached: pool pulses {PPulses}, starvations {PStarve}, emergences {PEmerge}, escapes {PEscape}, vhorrin gauges {PVhorrinStates}; condenser waits {CWait}, walks {CWalk}, arrivals {CArrive}, no-site {CNoSite}, pools dried {CDried}, pools grown {CGrown}");
            Console.WriteLine($"reached: claim offers {QOffers}, accepts {QAccepts}, withdrawn {QWithdrawn}, rival withdraws {QRivalWithdraws}, successes {QSuccess}; slot hits {SlotHits}, none {SlotNull}, preferred {SlotPreferred}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (PStarve == 0 || PEmerge == 0 || PEscape == 0 || CWait == 0 || CWalk == 0 || CArrive == 0 || CNoSite == 0 || CDried == 0 || QAccepts == 0 || QWithdrawn == 0 || QSuccess == 0 || SlotHits == 0 || SlotNull == 0 || SlotPreferred == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"weepingstones fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
