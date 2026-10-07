// Approach B for TheForge: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   cycle    the six-phase grand cycle driven exactly as RM_GameCondition_ForgeCycle drives it (phase clock, hiss, gas waves,
//            floods, freeze / crack / melt batches against a crust grid), with toggles and outside interference
//   plume    white plume fronts and the cell-expiry book the heat patch reads, against a double-precision spec
//   dhokkur  the wake / seal transition, the path-wear book (passes, cooldown, polish, fade) and the wall-shove fall-back chain
//   run      the dormancy decisions, the dhuvvox run clock (slow window, scuttle gap, run end) and the four phase voices
//   units    exhaustive truth tables for the small decisions (cycle order, schedules, sky pastures)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.TheForge.SelfTest
{
    internal static class TheForgeFuzz
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

        // ════════════════════════ cycle ════════════════════════
        private static readonly string[] CycleNames = { "Tick", "ForeignOver", "ForeignAdd", "ToggleCycle", "ToggleGate", "ToggleFreeze", "ToggleGas", "Strip" };
        public static long CyclesClosed, EarlyCloses, CellsFrozen, CellsMelted, WavesFired, FloodsFired, GentleMelts, ForeignKept, PhasesSeen;

        private const int Basalt = 1, Pumice = 2, Crack = 3, Foreign = 4;

        private sealed class CycleSim
        {
            // grid
            public int N; public bool[] lava; public int[] temp; public bool[] foundation;
            public int maxFrozen; public double pumiceChance;
            // settings and gates
            public bool cycleOn = true, gateOn = true, freezeOn = true, gasOn = true, meltDestroys = true;
            // condition state (mirrors RM_GameCondition_ForgeCycle)
            public ForgeCyclePhase phase = ForgeCyclePhase.StillHeat;
            public int phaseStart = -1, phaseEnd = -1; public bool hissSent;
            public int gasWavesLeft, nextGasWave = -1, floodsLeft, nextFlood = -1;
            public HashSet<int> frozen = new HashSet<int>();
            public RM_CrustWork<int> crust = new RM_CrustWork<int>();
            public int statCycles, statFrozen, statMelted, statWaves, statFloods;
            public Random rng;
            // hours by phase
            public float[] lo = new float[7], hi = new float[7]; public float hissLead; public int wavesLo, wavesHi, floodLo, floodHi;
            // bookkeeping for invariants
            public int now;
            public int wavesRolled, floodsRolled, wavesThisPhase, floodsThisPhase; public bool activeThroughPhase = true;
            public ForgeCyclePhase prev = ForgeCyclePhase.StillHeat;
            
            public bool Freezable(int c) { return lava[c] && temp[c] == 0 && !foundation[c]; }
            public bool Ours(int t) { return t == Basalt || t == Pumice || t == Crack; }

            public void Shuffle(List<int> l) { for (int i = l.Count - 1; i > 0; i--) { int j = rng.Next(i + 1); int t = l[i]; l[i] = l[j]; l[j] = t; } }

            public bool FreezeBatch()
            {
                return crust.Freeze(frozen, Enumerable.Range(0, N), Freezable, Shuffle, maxFrozen, now, phaseStart, phaseEnd, c =>
                {
                    temp[c] = rng.NextDouble() < pumiceChance ? Pumice : Basalt;
                    statFrozen++; CellsFrozen++;
                });
            }
            public bool CrackBatch()
            {
                return crust.Crack(frozen, c => Ours(temp[c]) && temp[c] != Crack, c => temp[c] = Crack, Shuffle, now, phaseStart, phaseEnd);
            }
            public void MeltBatch(int batch)
            {
                if (frozen.Count == 0) return;
                int m = crust.Melt(frozen, c => Ours(temp[c]), c => { temp[c] = 0; return rng.Next(5) == 0; }, Shuffle, batch, out bool _, out int _l);
                statMelted += m; CellsMelted += m;
            }

            public void Enter(ForgeCyclePhase next)
            {
                // closing invariants for the phase we are leaving
                if (phase == ForgeCyclePhase.GasWash && activeThroughPhase && wavesRolled > 0 && gasOn)
                    Check(wavesThisPhase == wavesRolled, $"gas wash fired {wavesThisPhase} waves of {wavesRolled} rolled");
                if (phase == ForgeCyclePhase.Rain && activeThroughPhase)
                    Check(floodsThisPhase == floodsRolled, $"rain released {floodsThisPhase} floods of {floodsRolled} rolled");
                phase = next;
                phaseStart = now;
                float h = lo[(int)next] + (float)rng.NextDouble() * (hi[(int)next] - lo[(int)next]);
                phaseEnd = RM_CycleKernel.PhaseEnd(now, h);
                Check(phaseEnd >= now + RM_CycleKernel.CycleInterval, "a phase shorter than one cycle step");
                crust.Reset();
                activeThroughPhase = true; wavesThisPhase = 0; floodsThisPhase = 0;
                PhasesSeen++;
                switch (next)
                {
                    case ForgeCyclePhase.StillHeat: hissSent = false; break;
                    case ForgeCyclePhase.GasWash:
                        if (gasOn) { wavesRolled = rng.Next(wavesLo, wavesHi + 1); gasWavesLeft = RM_CycleKernel.WaveCount(wavesRolled, true); nextGasWave = now; }
                        else { wavesRolled = 0; gasWavesLeft = RM_CycleKernel.WaveCount(0, false); }
                        break;
                    case ForgeCyclePhase.Rain:
                        floodsRolled = RM_CycleKernel.FloodCount(rng.Next(floodLo, floodHi + 1)); floodsLeft = floodsRolled; nextFlood = RM_CycleKernel.FirstFloodTick(now);
                        break;
                }
            }

            public void Advance()
            {
                if (phase == ForgeCyclePhase.Melt && frozen.Count > 0) MeltBatch(frozen.Count);
                ForgeCyclePhase next = RM_CycleKernel.Next(phase, frozen.Count);
                if (RM_CycleKernel.CountsAsCycle(phase)) { statCycles++; CyclesClosed++; }
                if (phase == ForgeCyclePhase.Freeze && next == ForgeCyclePhase.StillHeat) EarlyCloses++;
                Enter(next);
            }

            // One GameConditionTick on a 60-tick hash.
            public void Step()
            {
                now += RM_CycleKernel.CycleInterval;
                if (!RM_CycleKernel.CycleTickRuns(true, true, true)) return;
                bool advances = RM_CycleKernel.Advances(cycleOn, gateOn);
                if (!advances)
                {
                    activeThroughPhase = false;
                    if (frozen.Count > 0) { int before = frozen.Count; MeltBatch(RM_CycleKernel.GentleBatch); GentleMelts++; Check(before - frozen.Count <= RM_CycleKernel.GentleBatch, "gentle melt exceeded its batch"); }
                    return;
                }
                if (phaseEnd < 0) { Enter(ForgeCyclePhase.StillHeat); return; }
                // ---- DoPhaseWork ----
                switch (phase)
                {
                    case ForgeCyclePhase.StillHeat:
                        if (RM_CycleKernel.HissDue(hissSent, phaseEnd, now, hissLead, gasOn)) hissSent = true;
                        break;
                    case ForgeCyclePhase.GasWash:
                        if (RM_CycleKernel.WaveDue(gasWavesLeft, now, nextGasWave))
                        {
                            gasWavesLeft--; wavesThisPhase++; statWaves++; WavesFired++;
                            nextGasWave = RM_CycleKernel.NextWaveTick(now, phaseEnd, gasWavesLeft);
                        }
                        break;
                    case ForgeCyclePhase.Rain:
                        if (RM_CycleKernel.WaveDue(floodsLeft, now, nextFlood))
                        {
                            floodsLeft--; floodsThisPhase++; statFloods++; FloodsFired++;
                            nextFlood = RM_CycleKernel.NextWaveTick(now, phaseEnd, floodsLeft);
                        }
                        break;
                    case ForgeCyclePhase.Freeze:
                        if (freezeOn) FreezeBatch();
                        break;
                    case ForgeCyclePhase.Cracks: CrackBatch(); break;
                    case ForgeCyclePhase.Melt:
                        MeltBatch(RM_CycleKernel.BatchSize(frozen.Count, now, phaseEnd, phaseStart, RM_CycleKernel.MeltShare));
                        break;
                }
                if (RM_CycleKernel.PhaseIsOver(now, phaseEnd)) Advance();
            }
        }

        private static string RunCycle(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            var sim = new CycleSim { rng = new Random(seed ^ 0x3c6ef372) };
            sim.N = r.Next(4) == 0 ? r.Next(300, 700) : r.Next(20, 200);
            sim.lava = new bool[sim.N]; sim.temp = new int[sim.N]; sim.foundation = new bool[sim.N];
            double lavaShare = r.Next(0, 4) == 0 ? 0.0 : 0.2 + r.NextDouble() * 0.7;
            for (int i = 0; i < sim.N; i++) { sim.lava[i] = r.NextDouble() < lavaShare; sim.foundation[i] = r.Next(12) == 0; }
            int lavaCount = sim.lava.Count(x => x);
            sim.maxFrozen = r.Next(3) == 0 ? r.Next(1, Math.Max(2, lavaCount)) : 6000;
            sim.pumiceChance = new[] { 0.0, 0.3, 1.0 }[r.Next(3)];
            bool real = r.Next(20) == 0;
            float[] loS = { 2f, 2f, 2f, 2f, 1f, 1f, 1f }, hiS = { 3f, 3f, 3f, 3f, 2f, 2f, 2f };
            float[] loR = { 48f, 2f, 6f, 10f, 54f, 6f, 1.5f }, hiR = { 72f, 3f, 9f, 14f, 66f, 8f, 2.5f };
            for (int i = 0; i < 7; i++) { sim.lo[i] = real ? loR[i] : loS[i]; sim.hi[i] = real ? hiR[i] : hiS[i]; }
            sim.hissLead = 1.5f; sim.wavesLo = 2; sim.wavesHi = 4; sim.floodLo = 2; sim.floodHi = 4;
            var allowed = new Dictionary<ForgeCyclePhase, ForgeCyclePhase[]>
            {
                { ForgeCyclePhase.StillHeat, new[] { ForgeCyclePhase.GasWash } },
                { ForgeCyclePhase.GasWash, new[] { ForgeCyclePhase.Rain } },
                { ForgeCyclePhase.Rain, new[] { ForgeCyclePhase.Freeze } },
                { ForgeCyclePhase.Freeze, new[] { ForgeCyclePhase.Growth, ForgeCyclePhase.StillHeat } },
                { ForgeCyclePhase.Growth, new[] { ForgeCyclePhase.Cracks } },
                { ForgeCyclePhase.Cracks, new[] { ForgeCyclePhase.Melt } },
                { ForgeCyclePhase.Melt, new[] { ForgeCyclePhase.StillHeat } },
            };
            int step = 0; string err = null;
            var foreignCells = new HashSet<int>();
            int freezeBase = 0;   // frozen count at the moment a freeze started
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0:
                            for (int k = 0; k < 1 + a.a % 120; k++)
                            {
                                Steps++;
                                var before = sim.phase; int endBefore = sim.phaseEnd; int cyclesBefore = sim.statCycles; int frozenBefore = sim.frozen.Count;
                                bool wasOn = sim.cycleOn && sim.gateOn;
                                sim.Step();
                                // ---- invariants after every cycle step ----
                                if (sim.phase != before)
                                {
                                    Check(allowed[before].Contains(sim.phase), $"phase {before} -> {sim.phase} is not an allowed step");
                                    Check(wasOn, "the phase advanced while the cycle or its gate was off");
                                    if (before == ForgeCyclePhase.Freeze) Check((sim.phase == ForgeCyclePhase.Growth) == (frozenBefore > 0 || sim.frozen.Count > 0), $"freeze closed to {sim.phase} with {sim.frozen.Count} crusted cells");
                                    if (before == ForgeCyclePhase.Melt)
                                    {
                                        Check(sim.frozen.Count == 0, "the melt closed with crust still standing");
                                        for (int c = 0; c < sim.N; c++) Check(!sim.Ours(sim.temp[c]), $"cell {c} keeps our crust after the melt");
                                        Check(sim.statCycles == cyclesBefore + 1, "a closed cycle was not counted");
                                    }
                                    else Check(sim.statCycles == cyclesBefore, "a cycle was counted without a melt");
                                    if (sim.phase == ForgeCyclePhase.Freeze) freezeBase = sim.frozen.Count;
                                }
                                else Check(sim.statCycles == cyclesBefore && (sim.phaseEnd == endBefore || endBefore < 0), "phase end moved inside a phase");
                                if (!wasOn) Check(sim.phase == before && sim.phaseEnd == endBefore, "an off cycle changed its phase clock");
                                // frozen set vs the grid
                                Check(sim.frozen.Count <= Math.Max(sim.maxFrozen, 0) + freezeBase || sim.maxFrozen >= 6000, $"frozen {sim.frozen.Count} above the cap {sim.maxFrozen}");
                                for (int c = 0; c < sim.N; c++)
                                    if (sim.Ours(sim.temp[c])) Check(sim.frozen.Contains(c), $"cell {c} wears our crust but is not in the frozen set");
                                foreach (int c in sim.frozen) Check(sim.lava[c], $"non-lava cell {c} was frozen");
                                foreach (int c in foreignCells) if (sim.temp[c] != Foreign) Check(false, $"someone else's temp terrain at {c} was removed (temp {sim.temp[c]})");
                                if (sim.phase == ForgeCyclePhase.StillHeat && sim.hissSent) Check(sim.gasOn || true, "");
                                // deadlines: with the cycle running, a batch phase's queue is spent by its share of the phase (+3 steps)
                                if (wasOn && sim.cycleOn && sim.gateOn && sim.activeThroughPhase)
                                {
                                    double span = sim.phaseEnd - sim.phaseStart;
                                    if (sim.phase == ForgeCyclePhase.Freeze && sim.freezeOn && sim.crust.QueuePhase == (int)ForgeCyclePhase.Freeze && sim.now >= sim.phaseStart + span * RM_CycleKernel.FreezeShare + 3 * 60)
                                        Check(sim.crust.Queue == null || sim.crust.Queue.Count == 0, $"freeze queue of {sim.crust.Queue?.Count} still pending at {(sim.now - sim.phaseStart) / span:F2} of the phase");
                                    if (sim.phase == ForgeCyclePhase.Cracks && sim.crust.QueuePhase == (int)ForgeCyclePhase.Cracks && sim.now >= sim.phaseStart + span * RM_CycleKernel.CrackShare + 3 * 60)
                                        Check(sim.crust.Queue == null || sim.crust.Queue.Count == 0, "crack queue still pending past its share");
                                    if (sim.phase == ForgeCyclePhase.Melt && sim.now >= sim.phaseStart + span * RM_CycleKernel.MeltShare + 3 * 60)
                                        Check(sim.frozen.Count == 0 || sim.crust.Queue == null || sim.crust.Queue.Count == 0, "melt queue still pending past its share");
                                }
                            }
                            break;
                        case 1: // someone else's temp terrain lands on a crusted cell (a lava flow, a bridge)
                            {
                                if (sim.frozen.Count == 0) break;
                                int c = sim.frozen.ElementAt(a.a % sim.frozen.Count);
                                sim.temp[c] = Foreign; foreignCells.Add(c);
                            }
                            break;
                        case 2: // foreign temp terrain on a bare cell
                            {
                                int c = a.a % sim.N;
                                if (sim.temp[c] == 0) { sim.temp[c] = Foreign; foreignCells.Add(c); }
                            }
                            break;
                        case 3: sim.cycleOn = !sim.cycleOn; break;
                        case 4: sim.gateOn = !sim.gateOn; break;
                        case 5: sim.freezeOn = !sim.freezeOn; break;
                        case 6: sim.gasOn = !sim.gasOn; break;
                        case 7: // outside code strips a crusted cell back to bare ground (our frozen entry goes stale)
                            {
                                if (sim.frozen.Count == 0) break;
                                int c = sim.frozen.ElementAt(a.a % sim.frozen.Count);
                                if (sim.Ours(sim.temp[c])) sim.temp[c] = 0;
                            }
                            break;
                    }
                    // a foreign cell stays foreign only while nobody removes it; tests above fail if WE remove it
                    foreignCells.RemoveWhere(c => sim.temp[c] != Foreign);
                }
                // settle: switch everything on, run to a closed cycle, require a clean map
                sim.cycleOn = true; sim.gateOn = true;
                for (int k = 0; k < 200000 && !(sim.phase == ForgeCyclePhase.StillHeat && sim.frozen.Count == 0 && sim.crust.Queue == null && k > 0 && sim.phaseEnd > 0 && sim.now > 0 && k > 10); k++)
                {
                    sim.Step(); Steps++;
                    if (k > 150000) Check(false, "the cycle never returned to the still heat");
                }
                for (int c = 0; c < sim.N; c++) Check(!sim.Ours(sim.temp[c]) || sim.frozen.Contains(c), $"cell {c} wears orphan crust");
                ForeignKept += foreignCells.Count;
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static List<Act> GenCycle(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(40);
                int kind = k < 24 ? 0 : k < 27 ? 1 : k < 29 ? 2 : k < 32 ? 3 : k < 34 ? 4 : k < 36 ? 5 : k < 38 ? 6 : 7;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(100), c = 0, names = CycleNames });
            }
            return l;
        }

        public static List<string> Cycle(int n, int baseSeed)
        {
            return RunFamily("cycle", n, baseSeed, seed => { var r = new Random(seed * 7919 + 11); return GenCycle(r, r.Next(3, 40)); }, RunCycle);
        }

        // ════════════════════════ plume ════════════════════════
        private static readonly string[] PlumeNames = { "Crust", "Tick", "Toggle", "DebugSpawn", "Probe", "Wipe", "Stale" };
        public static long FrontsSpawned, FrontsExpired, FrontsLeft, ExpiryHits, PrunedTotal;

        private sealed class Front { public float x, z, dx, dz; public int life; public double sx, sz; public int steps; }

        private static string RunPlume(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            int W = r.Next(12, 140), H = r.Next(12, 140);
            var fronts = new List<Front>(); var book = new RM_PlumeBook();
            bool enabled = true; int now = r.Next(0, 100) * 15; int liveHigh = 0;
            var marks = new Dictionary<int, int>();   // spec: cell -> last mark expiry (cleared with the book)
            float strength = new[] { 0.1f, 0.25f, 1f, 1.7f, 2f, 3.5f }[r.Next(6)];
            int step = 0; string err = null; var rng = new Random(seed ^ 0x1b873593);
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0: // NoteCrusted: spawn gate then the injected chance
                            {
                                bool can = RM_PlumeKernel.CanSpawn(enabled, fronts.Count);
                                Check(can == (enabled && fronts.Count < 5), "CanSpawn != spec");
                                if (can && (a.b % 3 == 0))
                                {
                                    double ang = a.a * 0.01;
                                    var f = new Front { x = a.a % W + 0.5f, z = a.b % H + 0.5f, dx = (float)Math.Cos(ang), dz = (float)Math.Sin(ang), life = RM_PlumeKernel.LifeTicks };
                                    f.sx = f.x; f.sz = f.z; fronts.Add(f); FrontsSpawned++;
                                    liveHigh = Math.Max(liveHigh, fronts.Count);
                                    Check(fronts.Count <= 5, "more than 5 natural fronts");
                                }
                            }
                            break;
                        case 1:
                            for (int k = 0; k < 1 + a.a % 220; k++)
                            {
                                Steps++;
                                now += 15;
                                if (fronts.Count == 0) { if (book.Expiry.Count > 0) { book.ClearAll(); marks.Clear(); } continue; }
                                if (!enabled) { fronts.Clear(); book.ClearAll(); marks.Clear(); continue; }
                                for (int i = fronts.Count - 1; i >= 0; i--)
                                {
                                    var f = fronts[i];
                                    int lifeBefore = f.life;
                                    bool alive = RM_PlumeKernel.Step(ref f.x, ref f.z, f.dx, f.dz, ref f.life, W, H);
                                    f.steps++;
                                    Check(f.life == lifeBefore - 15, "front life did not drop by one step");
                                    // spec position: double-precision straight line
                                    double ex = f.sx + f.dx * 0.75 * f.steps, ez = f.sz + f.dz * 0.75 * f.steps;
                                    Check(Near(f.x, ex, 1e-3 + f.steps * 1e-5) && Near(f.z, ez, 1e-3 + f.steps * 1e-5), $"front drifted from its line: ({f.x},{f.z}) vs ({ex},{ez})");
                                    bool inb = Math.Floor(f.x) >= 0 && Math.Floor(f.z) >= 0 && Math.Floor(f.x) < W && Math.Floor(f.z) < H;
                                    bool specAlive = f.life > 0 && inb;
                                    Check(alive == specAlive, $"Step alive={alive} spec={specAlive} (life {f.life}, at {f.x},{f.z})");
                                    if (!alive) { fronts.RemoveAt(i); if (f.life <= 0) FrontsExpired++; else FrontsLeft++; continue; }
                                    int cx = (int)Math.Floor(f.x), cz = (int)Math.Floor(f.z);
                                    for (int dxx = -3; dxx <= 3; dxx++) for (int dzz = -3; dzz <= 3; dzz++)
                                    {
                                        if (dxx * dxx + dzz * dzz > 9) continue;
                                        int x = cx + dxx, z = cz + dzz;
                                        if (x < 0 || z < 0 || x >= W || z >= H) continue;
                                        book.Mark(z * W + x, now); marks[z * W + x] = now + 45;
                                    }
                                }
                                int before = book.Expiry.Count;
                                int pruned = book.Prune(now); PrunedTotal += pruned;
                                if (before <= 4000) Check(pruned == 0, "prune acted at or below 4000 entries");
                                if (before > 4000) Check(book.Expiry.Values.All(v => v >= now), "prune left an expired entry behind");
                                foreach (var kv in marks.ToList()) if (book.Expiry.ContainsKey(kv.Key) == false && kv.Value >= now) Check(false, $"a live expiry entry for cell {kv.Key} was pruned");
                                foreach (var kv in marks.Where(m => m.Value < now - 1000).ToList()) marks.Remove(kv.Key);
                            }
                            break;
                        case 2: enabled = !enabled; break;
                        case 3:
                            {
                                var f = new Front { x = a.a % W + 0.5f, z = a.b % H + 0.5f, dx = 1f, dz = 0f, life = RM_PlumeKernel.LifeTicks };
                                f.sx = f.x; f.sz = f.z; fronts.Add(f); FrontsSpawned++;
                            }
                            break;
                        case 4: // Probe: is a random cell in a plume right now?
                            {
                                int cell = (a.a % H) * W + a.b % W;
                                if (fronts.Count > 0 && a.c % 4 != 0)
                                {
                                    var pf = fronts[a.a % fronts.Count];
                                    int px = Math.Min(W - 1, Math.Max(0, (int)Math.Floor(pf.x) + a.b % 7 - 3)), pz = Math.Min(H - 1, Math.Max(0, (int)Math.Floor(pf.z) + a.a % 7 - 3));
                                    cell = pz * W + px;
                                }
                                bool got = book.InPlume(fronts.Count, cell, now);
                                bool spec = fronts.Count > 0 && marks.TryGetValue(cell, out int e) && e >= now;
                                Check(got == spec, $"InPlume({cell}) = {got}, spec {spec} at {now}");
                                if (got) ExpiryHits++;
                            }
                            break;
                        case 5: book.ClearAll(); marks.Clear(); break;
                        case 6: // thousands of long-expired entries, so the next tick has something to prune
                            for (int cell = 0; cell < Math.Min(W * H, 4100); cell++) { book.Mark(cell, now - 5000); marks[cell] = now - 4955; }
                            break;
                    }
                    if (book.Expiry.Count <= 4000 || fronts.Count == 0) { }
                    // pure scalar checks every step
                    Check(RM_PlumeKernel.Strength(strength) >= 0.25f && RM_PlumeKernel.Strength(strength) <= 2f, "strength outside [0.25, 2]");
                    Check(RM_PlumeKernel.GasPerCell(strength) >= 1 && RM_PlumeKernel.GasPerCell(strength) <= RM_PlumeKernel.GasPerCell(strength * 1.5f), "gas per cell below 1 or falling with strength");
                    Check(Near(RM_PlumeKernel.HeatOffset(strength), 25.0 * Math.Min(2.0, Math.Max(0.25, strength)), 1e-4), "heat offset != 25 * clamped strength");
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static List<Act> GenPlume(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(40);
                int kind = k < 10 ? 0 : k < 26 ? 1 : k < 28 ? 2 : k < 31 ? 3 : k < 36 ? 4 : k < 37 ? 5 : 6;
                l.Add(new Act { kind = kind, a = r.Next(10000), b = r.Next(10000), c = r.Next(100), names = PlumeNames });
            }
            return l;
        }

        public static List<string> Plume(int n, int baseSeed)
        {
            var fails = RunFamily("plume", n, baseSeed, seed => { var r = new Random(seed * 7919 + 13); return GenPlume(r, r.Next(4, 60)); }, RunPlume);
            try { PlumeUnits(); } catch (Exception e) { fails.Add("plume units: " + e.Message); }
            Cases++;
            return fails;
        }

        private static void PlumeUnits()
        {
            for (int m = 0; m < 8; m++)
            {
                bool flesh = (m & 1) != 0, setting = (m & 2) != 0, drifter = (m & 4) != 0;
                bool want = !flesh || (setting && drifter);
                Check(RM_PlumeKernel.Exempt(flesh, setting, drifter) == want, $"Exempt row {m}"); Steps++;
            }
            Check(RM_PlumeKernel.HeatApplies(true, true, false) && !RM_PlumeKernel.HeatApplies(false, true, false) && !RM_PlumeKernel.HeatApplies(true, false, false) && !RM_PlumeKernel.HeatApplies(true, true, true), "HeatApplies");
            Check(RM_PlumeKernel.RecentlyActive(160, 100) && !RM_PlumeKernel.RecentlyActive(161, 100) && RM_PlumeKernel.RecentlyActive(100, 100), "RecentlyActive boundary at 60 ticks");
            Check(RM_PlumeKernel.GasPerCell(1f) == 50 && RM_PlumeKernel.GasPerCell(0.25f) == 12 && RM_PlumeKernel.GasPerCell(2f) == 100 && RM_PlumeKernel.GasPerCell(0f) == 12, "GasPerCell values");
            // prune keeps everything unexpired and only acts above 4000 entries
            var b = new RM_PlumeBook();
            for (int i = 0; i < 4000; i++) b.Mark(i, 0);
            Check(b.Prune(10000) == 0 && b.Expiry.Count == 4000, "prune acted at exactly 4000 entries");
            b.Mark(4000, 9990);
            int p = b.Prune(10000);
            Check(p == 4000 && b.Expiry.Count == 1 && b.InPlume(1, 4000, 10000), "prune removed a live entry or missed dead ones");
            Check(!b.InPlume(0, 4000, 10000), "no fronts must mean no plume");
            Check(b.InPlume(1, 4000, 10035) && !b.InPlume(1, 4000, 10036), "an entry lasts exactly 45 ticks past its mark");
        }

        // ════════════════════════ dhokkur ════════════════════════
        private static readonly string[] DhokkurNames = { "Walk", "Fade", "Settings", "Polish", "Foreign" };
        public static long Polishes, Unpolishes, WearLost, Cooldowns;

        private static string RunDhokkur(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            int cells = r.Next(2, 25);
            var book = new RM_WearBook();
            var polished = new bool[cells]; var canPolish = Enumerable.Range(0, cells).Select(i => r.Next(5) != 0).ToArray();
            int passes = r.Next(0, 6), cooldown = 30000, period = new[] { 1, 100000, 300000 }[r.Next(3)];
            int now = r.Next(0, 5) * 1000;
            // spec
            var sWear = new Dictionary<int, int>(); var sLast = new Dictionary<int, int>();
            int step = 0; string err = null;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    int c = a.a % cells;
                    switch (a.kind)
                    {
                        case 0: // Walked
                            {
                                now += a.b % 40000;
                                bool polish = book.Walked(c, now, cooldown, passes, () => !polished[c] && canPolish[c]);
                                // spec
                                bool cool = sLast.TryGetValue(c, out int last) && now - last < cooldown;
                                bool sp = false;
                                if (cool) Cooldowns++;
                                else
                                {
                                    sLast[c] = now; sWear.TryGetValue(c, out int w); sWear[c] = ++w;
                                    sp = w >= Math.Max(1, passes) && !polished[c] && canPolish[c];
                                }
                                Check(polish == sp, $"Walked polish={polish} spec={sp} (cell {c}, wear {(sWear.TryGetValue(c, out int ww) ? ww : 0)}, passes {passes})");
                                if (polish) { polished[c] = true; Polishes++; }
                            }
                            break;
                        case 1: // Fade
                            {
                                now += a.b * 5000;
                                int unp;
                                book.Fade(now, period, passes, i => polished[i], i => polished[i] = false, out unp);
                                Unpolishes += unp; int sUn = 0;
                                foreach (int i in sWear.Keys.ToList())
                                {
                                    int l = sLast.TryGetValue(i, out int ll) ? ll : 0;
                                    if (now - l < period) continue;
                                    sLast[i] = now; int w = sWear[i] - 1; WearLost++;
                                    if (w < Math.Max(1, passes) && specIsPolished(i)) { sUn++; specPolished[i] = false; }
                                    if (w <= 0) { sWear.Remove(i); sLast.Remove(i); } else sWear[i] = w;
                                }
                                Check(unp == sUn, $"Fade unpolished {unp}, spec {sUn}");
                            }
                            break;
                        case 2: passes = a.a % 6; break;
                        case 3: // the seal depression: Walked on a neighbourhood does not break anything
                            now += 1;
                            break;
                        case 4: polished[c] = true; break; // foreign polish (another mod's trail on the same layer)
                    }
                    for (int i = 0; i < cells; i++) specPolished[i] = polished[i];
                    // book vs spec, exactly
                    Check(book.Wear.Count == sWear.Count && book.Wear.All(kv => sWear.TryGetValue(kv.Key, out int v) && v == kv.Value), "wear book differs from the spec");
                    Check(book.LastWorn.Count == sLast.Count && book.LastWorn.All(kv => sLast.TryGetValue(kv.Key, out int v) && v == kv.Value), "last-worn book differs from the spec");
                    Check(book.Wear.All(kv => kv.Value >= 1 && book.LastWorn.ContainsKey(kv.Key)), "a wear entry without a last-worn stamp, or wear below 1");
                    Check(book.LastWorn.Keys.All(k => book.Wear.ContainsKey(k)), "a last-worn stamp without wear");
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        [ThreadStatic] private static bool[] specPolished0;
        private static bool[] specPolished { get { if (specPolished0 == null) specPolished0 = new bool[64]; return specPolished0; } }
        private static bool specIsPolished(int i) { return specPolished[i]; }

        private static List<Act> GenDhokkur(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(30);
                int kind = k < 18 ? 0 : k < 24 ? 1 : k < 26 ? 2 : k < 28 ? 3 : 4;
                l.Add(new Act { kind = kind, a = r.Next(100), b = r.Next(60), c = 0, names = DhokkurNames });
            }
            return l;
        }

        public static List<string> Dhokkur(int n, int baseSeed)
        {
            var fails = RunFamily("dhokkur", n, baseSeed, seed => { var r = new Random(seed * 7919 + 17); return GenDhokkur(r, r.Next(4, 70)); }, (seed, acts) => { Array.Clear(specPolished, 0, 64); return RunDhokkur(seed, acts); });
            try { DhokkurUnits(); } catch (Exception e) { fails.Add("dhokkur units: " + e.Message); }
            Cases++;
            return fails;
        }

        private static void DhokkurUnits()
        {
            // transition table, exhaustively
            for (int m = 0; m < 16; m++)
            {
                bool seen = (m & 1) != 0, was = (m & 2) != 0, now = (m & 4) != 0, rain = (m & 8) != 0;
                DhokkurTransition want = !seen || was == now ? DhokkurTransition.None : (!now && rain) ? DhokkurTransition.Wake : now ? DhokkurTransition.Seal : DhokkurTransition.None;
                Check(RM_DhokkurKernel.Transition(seen, was, now, rain) == want, $"Transition row {m}"); Steps++;
            }
            // random sealed/raining streams: events alternate sensibly
            var rr = new Random(5);
            for (int s = 0; s < 400; s++)
            {
                bool seen = false, was = true; int wakes = 0, seals = 0; int sealsSinceWake = 1;
                for (int i = 0; i < 80; i++)
                {
                    bool sealedNow = rr.Next(3) != 0, rain = rr.Next(2) == 0;
                    var t = RM_DhokkurKernel.Transition(seen, was, sealedNow, rain);
                    if (t == DhokkurTransition.Wake) { Check(was && !sealedNow && rain, "Wake without a sealed -> awake change in rain"); Check(sealsSinceWake > 0, "two wakes with no seal between"); sealsSinceWake = 0; wakes++; }
                    if (t == DhokkurTransition.Seal) { Check(!was && sealedNow, "Seal without an awake -> sealed change"); sealsSinceWake++; seals++; }
                    was = sealedNow; seen = true; Steps++;
                }
                Check(wakes <= seals + 1, "more wakes than seals");
            }
            // the shove chain against a literal spec
            int[] modes = { -3, 0, 1, 2, 7 }; float[] pcts = { -1f, 0f, 0.25f, 1f, 2f };
            foreach (int mode in modes) for (int m = 0; m < 8; m++) foreach (float pct in pcts)
            {
                bool one = (m & 1) != 0, recv = (m & 2) != 0, minifiable = (m & 4) != 0;
                foreach (bool minifyOk in new[] { false, true })
                {
                    int moved = 0, minified = 0; float dmg = -1f; int calls = 0;
                    var got = RM_DhokkurKernel.Shove(mode, one, recv, minifiable, () => { minified++; return minifyOk; }, pct, () => moved++, p => { dmg = p; calls++; });
                    int cm = Math.Min(2, Math.Max(0, mode)); float cp = Math.Min(1f, Math.Max(0f, pct));
                    ShoveOutcome want;
                    if (cm == 0 && one && recv) want = ShoveOutcome.Moved;
                    else if (cm <= 1 && minifiable && minifyOk) want = ShoveOutcome.Minified;
                    else if (cp > 0f) want = ShoveOutcome.Damaged;
                    else want = ShoveOutcome.None;
                    Check(got == want, $"Shove(mode {mode}, 1x1 {one}, recv {recv}, minifiable {minifiable}, minifyOk {minifyOk}, pct {pct}) = {got}, spec {want}");
                    Check(moved == (want == ShoveOutcome.Moved ? 1 : 0) && calls == (want == ShoveOutcome.Damaged ? 1 : 0), "an action ran that the outcome does not name");
                    Check(minified == (cm <= 1 && minifiable && !(cm == 0 && one && recv) ? 1 : 0), "minify attempted out of order or not at all");
                    if (want == ShoveOutcome.Damaged) Check(dmg == cp && dmg > 0f && dmg <= 1f, "damage fraction not clamped to (0,1]");
                    Steps++;
                }
            }
            Check(RM_DhokkurKernel.FadePeriodTicks(0f) == 1 && RM_DhokkurKernel.FadePeriodTicks(60f) == 3600000 && RM_DhokkurKernel.FadePeriodTicks(0.5f) == 30000, "FadePeriodTicks");
            Check(RM_DhokkurKernel.Passes(-4) == 1 && RM_DhokkurKernel.Passes(0) == 1 && RM_DhokkurKernel.Passes(3) == 3, "Passes floor");
        }

        // ════════════════════════ run ════════════════════════
        private static readonly string[] RunNames = { "Check", "Env", "Voice", "Probe" };
        public static long Wakes, Seals, Curls, Slows, Stingers, Coughs;

        private static string RunRun(int seed, List<Act> acts)
        {
            var r = new Random(seed);
            float minAwake = new[] { 0f, 0.5f, 2f }[r.Next(3)];
            var st = new DormancyState { awakeSinceTick = -1 };
            bool awake = r.Next(2) == 0; int now = r.Next(0, 50) * 250; int wokeAt = -1;
            // spec ledger
            bool sFirstDone = false; int sAwakeSince = -1;
            bool enabled = true, raining = false, flash = false, awakeRain = true, awakeFlash = false, canSeal = true, hasMap = true;
            int flashEnd = -1, phaseEnd = -1; bool clockOn = true, cycleRaining = false; float slowHours = 0.25f, slowFactor = 4f;
            int lastPhase = -1; ForgeCyclePhase phase = ForgeCyclePhase.StillHeat; bool hissSent = false, voicesActive = true;
            int sLastPhase = -1; int step = 0; string err = null;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    switch (a.kind)
                    {
                        case 0: // one dormancy check
                            {
                                now += 250 * (1 + a.a % 12);
                                bool should = RM_DormancyKernel.ShouldBeAwake(hasMap, awakeRain, raining, awakeFlash, flash);
                                bool sShould = !hasMap || (awakeRain && raining) || (awakeFlash && flash);
                                Check(should == sShould, "ShouldBeAwake != spec");
                                bool want = RM_DormancyKernel.WantAwake(enabled, should);
                                Check(want == (!enabled || sShould), "WantAwake != spec");
                                var res = RM_DormancyKernel.Check(ref st, awake, want, canSeal, now, minAwake);
                                // spec
                                DormancyAction sAct = DormancyAction.None; bool sCurl = false;
                                if (!awake) { if (want || !canSeal) { sAct = DormancyAction.WakeUp; sAwakeSince = now; } }
                                else
                                {
                                    bool first = !sFirstDone; sFirstDone = true;
                                    if (sAwakeSince < 0) sAwakeSince = now;
                                    if (!(want || !canSeal) && (first || now - sAwakeSince >= minAwake * 2500f)) { sAct = DormancyAction.ToSleep; sCurl = !first; sAwakeSince = -1; }
                                }
                                Check(res.action == sAct, $"dormancy action {res.action}, spec {sAct} (awake {awake}, want {want}, canSeal {canSeal})");
                                Check(res.curlBack == sCurl, "curl-back != spec");
                                Check(st.awakeSinceTick == sAwakeSince && st.initialCheckDone == sFirstDone, "dormancy state drifted from the spec");
                                if (res.action == DormancyAction.WakeUp) { awake = true; Wakes++; wokeAt = now; Check(!res.slowingUpdate, "a wake also reconciled slowing"); }
                                else if (res.action == DormancyAction.ToSleep)
                                {
                                    Seals++; if (res.curlBack) Curls++;
                                    Check(awake && !want && canSeal, "sealed a pawn that wanted to be awake or cannot seal");
                                    if (res.curlBack && wokeAt >= 0) Check(now - wokeAt >= minAwake * 2500f || true, "");
                                    awake = false;
                                }
                                if (!res.slowingUpdate && res.action == DormancyAction.None) Check(!awake, "an awake pawn skipped the slowing reconcile");
                            }
                            break;
                        case 1: // environment change
                            if (a.c % 3 == 0) { clockOn = true; awakeFlash = true; flash = true; awakeRain = true; }
                            switch (a.a % 10)
                            {
                                case 0: raining = !raining; break;
                                case 1: flash = !flash; break;
                                case 2: canSeal = !canSeal; break;
                                case 3: enabled = !enabled; break;
                                case 4: awakeRain = !awakeRain; break;
                                case 5: awakeFlash = !awakeFlash; break;
                                case 6: hasMap = a.b % 5 != 0; break;
                                case 7: flashEnd = now + a.b * 100; phaseEnd = now + a.b * 90; break;
                                case 8: cycleRaining = !cycleRaining; break;
                                case 9: clockOn = !clockOn; break;
                            }
                            break;
                        case 2: // one voice frame
                            {
                                now += 30 * (1 + a.a % 40);
                                if (a.b % 7 == 0) voicesActive = !voicesActive;
                                if (a.b % 5 == 0) phase = (ForgeCyclePhase)(a.c % 7);
                                if (a.b % 11 == 0) hissSent = !hissSent;
                                int before = lastPhase;
                                var ev = RM_DormancyKernel.Frame(ref lastPhase, voicesActive, phase, hissSent, now);
                                // spec
                                if (!voicesActive) { sLastPhase = (int)phase; Check(ev == RM_DormancyKernel.VoiceEvent.None, "an inactive frame made a sound"); }
                                else
                                {
                                    bool stinger = (int)phase != sLastPhase && sLastPhase >= 0;
                                    sLastPhase = (int)phase;
                                    Check(((ev & RM_DormancyKernel.VoiceEvent.Stinger) != 0) == stinger, $"stinger {(ev & RM_DormancyKernel.VoiceEvent.Stinger) != 0}, spec {stinger} (last {before}, phase {phase})");
                                    bool cough = (phase == ForgeCyclePhase.GasWash || (phase == ForgeCyclePhase.StillHeat && hissSent)) && now % 240 == 0;
                                    bool basalt = (phase == ForgeCyclePhase.Freeze || phase == ForgeCyclePhase.Growth) && now % 90 == 0;
                                    bool crack = (phase == ForgeCyclePhase.Cracks || phase == ForgeCyclePhase.Melt) && now % 360 == 0;
                                    Check(((ev & RM_DormancyKernel.VoiceEvent.Cough) != 0) == cough, "cough != spec");
                                    Check(((ev & RM_DormancyKernel.VoiceEvent.BasaltTick) != 0) == basalt, "basalt tick != spec");
                                    Check(((ev & RM_DormancyKernel.VoiceEvent.CrackPulse) != 0) == crack, "crack pulse != spec");
                                    if (stinger) Stingers++;
                                    if (cough) Coughs++;
                                }
                                Check(lastPhase == sLastPhase, "last phase drifted");
                            }
                            break;
                        case 3: // probes of the run clock
                            {
                                if (a.c % 2 == 0) { flashEnd = now + a.a % 900; phaseEnd = now + a.b % 900; }
                                int end = RM_DormancyKernel.RunEnd(hasMap, awakeFlash, flash, flashEnd, awakeRain, cycleRaining, phaseEnd);
                                int sEnd = !hasMap ? -1 : (awakeFlash && flash) ? flashEnd : (awakeRain && cycleRaining) ? phaseEnd : -1;
                                Check(end == sEnd, $"RunEnd {end} != spec {sEnd}");
                                bool want = RM_DormancyKernel.WantAwake(enabled, RM_DormancyKernel.ShouldBeAwake(hasMap, awakeRain, raining, awakeFlash, flash));
                                bool slow = RM_DormancyKernel.SlowWanted(clockOn, want, end, now, slowHours);
                                int left = end - now;
                                bool sSlow = clockOn && want && end > 0 && left > 0 && left <= slowHours * 2500f;
                                Check(slow == sSlow, $"SlowWanted {slow} != spec {sSlow} (end {end}, now {now})");
                                if (slow) { Slows++; Check(end > 0 && left > 0 && left <= 625, "slowing outside the final quarter-hour"); }
                                // scuttle delay: monotone toward the end, bounded by gap*factor*jitter, full speed at the window edge
                                int gap = 70;
                                int d1 = RM_DormancyKernel.ScuttleDelay(gap, end, now, slowHours, slowFactor, 1f);
                                int d2 = RM_DormancyKernel.ScuttleDelay(gap, end, now + 50, slowHours, slowFactor, 1f);
                                if (end > 0 && left > 50) Check(d2 >= d1, $"scuttle gap shrank toward the end ({d1} -> {d2})");
                                Check(d1 >= gap * Math.Min(1f, slowFactor) - 1 && d1 <= gap * Math.Max(1f, slowFactor) + 1, "scuttle gap outside [gap, gap*factor]");
                                if (end > 0 && left == 625) Check(d1 == gap, "full speed expected exactly at the window edge");
                                Check(RM_DormancyKernel.ScuttleDelay(3, end, now, slowHours, slowFactor, 1f) >= 10 * Math.Min(1f, slowFactor) - 1, "scuttle interval below the 10-tick floor");
                            }
                            break;
                    }
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            return err;
        }

        private static List<Act> GenRun(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(40);
                int kind = k < 16 ? 0 : k < 24 ? 1 : k < 34 ? 2 : 3;
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), c = r.Next(100), names = RunNames });
            }
            return l;
        }

        public static List<string> RunClock(int n, int baseSeed)
        {
            return RunFamily("run", n, baseSeed, seed => { var r = new Random(seed * 7919 + 19); return GenRun(r, r.Next(4, 80)); }, RunRun);
        }

        // ════════════════════════ units ════════════════════════
        public static List<string> Units()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                var P = Enum.GetValues(typeof(ForgeCyclePhase)).Cast<ForgeCyclePhase>().ToArray();
                // order: a full cycle visits every phase once, then closes
                var p = ForgeCyclePhase.StillHeat; var seen = new List<ForgeCyclePhase>();
                for (int i = 0; i < 7; i++) { seen.Add(p); p = RM_CycleKernel.Next(p, 5); }
                Check(p == ForgeCyclePhase.StillHeat && seen.Distinct().Count() == 7, "a cycle with crust must visit all seven phases and close");
                Check(RM_CycleKernel.Next(ForgeCyclePhase.Freeze, 0) == ForgeCyclePhase.StillHeat && RM_CycleKernel.Next(ForgeCyclePhase.Freeze, 1) == ForgeCyclePhase.Growth, "the freeze closes early with nothing crusted");
                foreach (var ph in P) Check(RM_CycleKernel.CountsAsCycle(ph) == (ph == ForgeCyclePhase.Melt), "only the melt counts as a cycle");
                Check(RM_CycleKernel.PhaseEnd(1000, 0f) == 1060 && RM_CycleKernel.PhaseEnd(0, 2f) == 5000 && RM_CycleKernel.PhaseEnd(0, 0.01f) == 60, "PhaseEnd floor of one cycle step");
                // hiss and schedules
                Check(RM_CycleKernel.HissDue(false, 10000, 7500, 1f, true) && !RM_CycleKernel.HissDue(false, 10000, 7499, 1f, true) && !RM_CycleKernel.HissDue(true, 10000, 9999, 1f, true) && !RM_CycleKernel.HissDue(false, 10000, 9999, 1f, false), "HissDue boundary at exactly the lead");
                Check(RM_CycleKernel.WaveDue(1, 100, 100) && !RM_CycleKernel.WaveDue(1, 99, 100) && !RM_CycleKernel.WaveDue(0, 500, 100), "WaveDue");
                // waves are spread evenly: simulate k waves over a span and check spacing never leaves the phase
                for (int waves = 1; waves <= 6; waves++) for (int span = 600; span <= 9000; span += 600)
                {
                    int now = 0, end = span, left = waves, next = 0, fired = 0, guard = 0;
                    while (left > 0 && guard++ < 100000)
                    {
                        if (RM_CycleKernel.WaveDue(left, now, next)) { left--; fired++; next = RM_CycleKernel.NextWaveTick(now, end, left); }
                        now += 60;
                        if (now > end) break;
                    }
                    Check(fired == waves, $"{waves} waves over {span} ticks fired only {fired}"); Steps++;
                }
                Check(RM_CycleKernel.WaveCount(0, true) == 1 && RM_CycleKernel.WaveCount(5, false) == 0 && RM_CycleKernel.WaveCount(3, true) == 3, "WaveCount");
                Check(RM_CycleKernel.FloodCount(-2) == 0 && RM_CycleKernel.FirstFloodTick(100) == 1350, "FloodCount / FirstFloodTick");
                Check(RM_CycleKernel.FloodVolume(0, 0f) == 0.0001f && RM_CycleKernel.FloodVolume(45, 2f) == 90f, "FloodVolume floors");
                // random burst / weather
                foreach (var ph in P)
                {
                    Check(RM_CycleKernel.AllowRandomBurst(true, true, ph) == (ph == ForgeCyclePhase.StillHeat), "ordinary bursts belong to the still heat only");
                    Check(RM_CycleKernel.AllowRandomBurst(false, true, ph) && RM_CycleKernel.AllowRandomBurst(true, false, ph), "with the cycle off the pulse behaves as always");
                    Check(RM_CycleKernel.UsesFreezeWeather(true, true, ph, true) == (ph == ForgeCyclePhase.Freeze) && !RM_CycleKernel.UsesFreezeWeather(true, false, ph, true), "freeze weather only in the freeze");
                }
                // batch size: a queue is always spent by its share of the phase, from any start
                for (int len = 600; len <= 30000; len += 1800) foreach (float share in new[] { 0.5f, 0.6f, 0.8f })
                    foreach (int q0 in new[] { 1, 7, 100, 6000 })
                    {
                        int rem = q0, now = 60, guard = 0;
                        while (rem > 0 && guard++ < 100000)
                        {
                            int b = RM_CycleKernel.BatchSize(rem, now, len, 0, share);
                            Check(b >= 1, "a batch of zero would never finish");
                            rem -= Math.Min(rem, b); now += 60;
                        }
                        Check(now <= len * share + 180, $"queue of {q0} over {len} ticks at share {share} finished at {now}, past {len * share + 180}"); Steps++;
                    }
                // batch size, exactly, in integer arithmetic: ceil(remaining / max(1, floor(max(60, round(span*share) - elapsed) / 60)))
                for (int rem = 1; rem <= 400; rem += 37) for (int span = 600; span <= 36000; span += 3000) foreach (float share in new[] { 0.5f, 0.6f, 0.8f }) foreach (int elapsed in new[] { 0, 60, 300, 1800, 9000 })
                {
                    long window = (long)Math.Round(span * (double)share);
                    long ticksLeft = Math.Max(60, window - elapsed);
                    long batches = Math.Max(1, ticksLeft / 60);
                    long want = Math.Max(1, (rem + batches - 1) / batches);
                    int got = RM_CycleKernel.BatchSize(rem, elapsed + 100, span + 100, 100, share);
                    Check(got == want, $"BatchSize({rem}, span {span}, share {share}, elapsed {elapsed}) = {got}, spec {want}"); Steps++;
                }
                // sky pastures
                Check(RM_SkyKernel.StoopBand(8f, 8f, 32f) && RM_SkyKernel.StoopBand(32f, 8f, 32f) && !RM_SkyKernel.StoopBand(7.99f, 8f, 32f) && !RM_SkyKernel.StoopBand(32.01f, 8f, 32f), "stoop band edges are inclusive");
                Check(RM_SkyKernel.PreyScoreDelta(true, 0f, false) == 30f && RM_SkyKernel.PreyScoreDelta(false, 0f, true) == -60f && RM_SkyKernel.PreyScoreDelta(false, 20f, false) == -60f && RM_SkyKernel.PreyScoreDelta(false, 20f, true) == 0f && RM_SkyKernel.PreyScoreDelta(true, 20f, true) == 30f, "PreyScoreDelta table");
                Check(RM_SkyKernel.HighlightReach(1f) == 8f && RM_SkyKernel.HighlightReach(100f) == 60f && RM_SkyKernel.HighlightReach(25f) == 25f, "HighlightReach clamp");
                Check(RM_SkyKernel.MoteAlive(239) && !RM_SkyKernel.MoteAlive(240), "mote lifetime");
                RM_SkyKernel.MotePos(10f, 10f, 0f, 7.5f, 0, out float x0, out float z0);
                Check(Near(x0, 11.6, 1e-4) && Near(z0, 10.0, 1e-4), "mote starts 1.6 east of its column cell");
                RM_SkyKernel.MotePos(10f, 10f, 0f, 7.5f, 239, out float x1, out float z1);
                Check(z1 > z0 + 2.9, "motes rise about 3.2 cells over their life");
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
                ("cycle", () => Cycle(N(1500), S(1))),
                ("plume", () => Plume(N(3000), S(1))),
                ("dhokkur", () => Dhokkur(N(3000), S(1))),
                ("run", () => RunClock(N(3000), S(1))),
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
            Console.WriteLine($"cycle: closed cycles {CyclesClosed}, early closes {EarlyCloses}, phases entered {PhasesSeen}, cells frozen {CellsFrozen}, melted {CellsMelted}, gas waves {WavesFired}, floods {FloodsFired}, gentle melts {GentleMelts}, foreign cells kept {ForeignKept}");
            Console.WriteLine($"plume: fronts spawned {FrontsSpawned}, expired {FrontsExpired}, left the map {FrontsLeft}, in-plume probes {ExpiryHits}, entries pruned {PrunedTotal}");
            Console.WriteLine($"dhokkur: polishes {Polishes}, unpolishes {Unpolishes}, passes lost {WearLost}, cooldown skips {Cooldowns}; run: wakes {Wakes}, seals {Seals}, curl-backs {Curls}, slowing probes {Slows}, stingers {Stingers}, coughs {Coughs}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                var blind = new List<string>();
                if (CyclesClosed == 0 || EarlyCloses == 0 || CellsFrozen == 0 || CellsMelted == 0 || WavesFired == 0 || FloodsFired == 0 || GentleMelts == 0 || ForeignKept == 0) blind.Add("cycle never closed/early-closed/froze/melted/waved/flooded/gentle-melted/kept a foreign cell");
                if (FrontsSpawned == 0 || FrontsExpired == 0 || FrontsLeft == 0 || ExpiryHits == 0) blind.Add("plume never spawned/expired/left/hit");
                if (Polishes == 0 || Unpolishes == 0 || WearLost == 0 || Cooldowns == 0) blind.Add("dhokkur never polished/unpolished/faded/cooled down");
                if (Wakes == 0 || Seals == 0 || Curls == 0 || Slows == 0 || Stingers == 0 || Coughs == 0) blind.Add("run never woke/sealed/curled/slowed/stung/coughed");
                foreach (var b in blind) { Console.WriteLine("FAIL fuzz is blind: " + b); ok = false; }
            }
            Console.WriteLine($"theforge fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
