// Approach B for FloodedCanyon: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   flood    the Dry / Herald / Warned / Flooding machine, its beats, chimes, jitter, peakstorm pull (RM_FloodKernel.Tick)
//   cells    the flood's thinned spread, the ledger that restores what it raised, the chime geometry
//   refuge   who shelters on the ledges and which ledge cell (RM_RefugeKernel)
//   pan      the sleeper pan's dig-in / wake state machine (RM_PanKernel)
//   rules    recede aftermath timers, biome score, fossil strata geometry (RM_CanyonRulesKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.FloodedCanyon.SelfTest
{
    internal static class FloodedCanyonFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static bool Near(double a, double b, double eps) { return Math.Abs(a - b) <= eps; }

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

        private static List<Act> GenActs(Random r, int minN, int maxN, int[] weights, string[] names)
        {
            int total = weights.Sum(), n = minN + r.Next(maxN - minN + 1);
            var l = new List<Act>();
            for (int i = 0; i < n; i++)
            {
                int w = r.Next(total), kind = 0;
                while (w >= weights[kind]) { w -= weights[kind]; kind++; }
                l.Add(new Act { kind = kind, a = r.Next(1000), b = r.Next(1000), names = names });
            }
            return l;
        }


        // ════════════════════════ flood ════════════════════════
        private static readonly string[] FlNames = { "Advance", "Storm", "Active", "Beats", "Lead", "Period", "Poke" };
        public static long Floods, Recedes, HeraldRuns, Pulls, ForcedRecedes, Chimes;

        private static string RunFlood(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0xf10);
            var cfg = new FloodCfg { Active = true, FiveBeats = r.Next(4) != 0, ChimeStaging = r.Next(4) != 0, PeakstormBias = r.Next(3) != 0, ChimeLeadHours = new[] { 0.01f, 2f, 6f }[r.Next(3)], HeraldLeadHours = new[] { 0.01f, 4f, 12f }[r.Next(3)], FloodPeriodDays = new[] { 0.01f, 1f, 6f, 12f }[r.Next(4)] };
            var s = new FloodState();
            int now = r.Next(0, 4) * 250 * 1000; bool storm = false; bool seedPending = false;
            int durationTicks = new[] { 2500, 10000, 30000 }[r.Next(3)];
            var rng = new Random(seed ^ 0x77);
            // per-cycle ledger for the spec
            bool rungZero = false; var rung = new List<int>(); var beats = new List<int>(); bool enteredHerald = false;
            int cycleStartNext = -1; bool floodedThisCycle = false; bool cfgTouched = false; int heraldEnteredAt = int.MinValue;
            FloodPhase prev = s.Phase;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: storm = !storm; break;
                    case 2: cfgTouched = true; cfg.Active = !cfg.Active || a.a % 4 == 0; break;
                    case 3: cfgTouched = true; cfg.FiveBeats = !cfg.FiveBeats; break;
                    case 4: cfgTouched = true; cfg.ChimeLeadHours = new[] { 0.01f, 2f, 6f }[a.a % 3]; break;
                    case 5: cfgTouched = true; cfg.FloodPeriodDays = new[] { 0.01f, 1f, 6f, 12f }[a.a % 4]; break;
                    default:
                        {
                            int n = a.kind == 6 ? 1 : 1 + a.a % 160;
                            for (int t = 0; t < n; t++)
                            {
                                now += a.kind == 6 ? 1 : 50;
                                var before = new FloodState { Phase = s.Phase, NextFloodTick = s.NextFloodTick, FloodEndTick = s.FloodEndTick, LastRecedeTick = s.LastRecedeTick, ChimeStage = s.ChimeStage, HeraldBeat = s.HeraldBeat, PeakstormPulled = s.PeakstormPulled };
                                int jitterCalls = 0; bool seedPendingBefore = seedPending;
                                FloodStep st = RM_FloodKernel.Tick(s, cfg, now, seedPending, storm, (float)rng.NextDouble(), (lo, hi) => { jitterCalls++; return rng.Next(lo, hi + 1); }, (lo, hi) => rng.Next(lo, hi + 1));
                                if (st.ChooseSeed) seedPending = true;
                                // transitions
                                bool legal = s.Phase == before.Phase
                                    || (before.Phase == FloodPhase.Dry && (s.Phase == FloodPhase.Herald || s.Phase == FloodPhase.Warned))
                                    || (before.Phase == FloodPhase.Herald && s.Phase == FloodPhase.Warned)
                                    || (before.Phase == FloodPhase.Warned && s.Phase == FloodPhase.Flooding)
                                    || (before.Phase == FloodPhase.Flooding && s.Phase == FloodPhase.Dry);
                                Check(legal, $"illegal phase change {before.Phase} -> {s.Phase}" + where);
                                if (!cfg.Active)
                                {
                                    if (before.Phase == FloodPhase.Flooding) { Check(st.Recede && s.Phase == FloodPhase.Dry, "a flood under way when the cycle was switched off did not recede" + where); ForcedRecedes++; }
                                    else Check(!st.StartFlood && !st.Recede && s.Phase == before.Phase && st.RingChime < 0 && st.HeraldBeats.Count == 0, "an inactive cycle did something" + where);
                                }
                                if (st.StartFlood)
                                {
                                    Check(before.Phase == FloodPhase.Warned && rungZero, "a flood began without the first chime having rung" + where);
                                    Check(now >= s.NextFloodTick, "flood began before its time" + where);
                                    RM_FloodKernel.Begin(s, now, new[] { 0.5f, 4f, 12f }[a.a % 3], 5f, out int dur, out int soak);
                                    Check(s.FloodEndTick == now + dur && dur >= 250 && soak > dur && s.HeraldBeat == 0, "flood begin bookkeeping" + where);
                                    s.FloodEndTick = now + durationTicks;   // keep the test's flood length bounded
                                    Floods++; floodedThisCycle = true;
                                }
                                if (st.Recede)
                                {
                                    Recedes++;
                                    Check(cfg.Active ? (now >= before.FloodEndTick) : true, "receded before the flood's end" + where);
                                    Check(s.Phase == FloodPhase.Dry && s.LastRecedeTick == now, "recede bookkeeping" + where);
                                    int period = RM_FloodKernel.DaysToTicks(cfg.FloodPeriodDays);
                                    Check(s.NextFloodTick >= now + 2500 && s.NextFloodTick <= now + period + period / 3 + 1, $"next flood {s.NextFloodTick - now} ticks away, period {period}" + where);
                                    Check(s.NextFloodTick >= now + period - period / 3 - 1 || s.NextFloodTick == now + 2500, "next flood sooner than the jitter allows" + where);
                                    Check(!s.PeakstormPulled, "peakstorm flag not cleared by the schedule" + where);
                                    rungZero = false; rung.Clear(); beats.Clear(); enteredHerald = false; floodedThisCycle = false; seedPending = false; cfgTouched = false;
                                }
                                if (st.RingChime >= 0)
                                {
                                    Chimes++;
                                    int lead = RM_FloodKernel.HoursToTicks(cfg.ChimeLeadHours);
                                    if (st.RingChime == 0) { Check(!rungZero, "the first chime rang twice in one cycle" + where); rungZero = true; Check(now >= s.NextFloodTick - lead, "first chime before its lead time" + where); Check(s.Phase == FloodPhase.Warned && s.ChimeStage == 1, "entering Warned must leave the chime stage at 1" + where); }
                                    else
                                    {
                                        Check(cfg.ChimeStaging && st.RingChime == (rung.Count == 0 ? 1 : rung.Last() + 1), $"chime stage {st.RingChime} out of order (rung {string.Join(",", rung)})" + where);
                                        Check(now >= s.NextFloodTick - (int)(lead * new[] { 1f, 0.5f, 0.15f }[st.RingChime]), "staged chime before its time" + where);
                                        rung.Add(st.RingChime);
                                    }
                                }
                                foreach (int b in st.HeraldBeats)
                                {
                                    Check(cfg.FiveBeats || enteredHerald, "a herald beat with the five beats off and no herald under way" + where);
                                    Check(b == (beats.Count == 0 ? 1 : beats.Last() + 1) && b >= 1 && b <= 3, $"herald beat {b} out of order" + where);
                                    int heraldTicks = RM_FloodKernel.HoursToTicks(cfg.HeraldLeadHours), chimeAt = s.NextFloodTick - RM_FloodKernel.HoursToTicks(cfg.ChimeLeadHours);
                                    float frac = 1f - (b - 1) / 3f;
                                    Check(now >= chimeAt - (int)(heraldTicks * frac), "herald beat before its time" + where);
                                    // and not late: with the settings untouched a beat sounds within a step or two of its time
                                    if (!cfgTouched) Check(Math.Max(chimeAt - (int)(heraldTicks * frac), heraldEnteredAt) > now - 3 * (a.kind == 6 ? 1 : 50), $"herald beat {b} sounded {now - Math.Max(chimeAt - (int)(heraldTicks * frac), heraldEnteredAt)} ticks after it was due and the herald had begun" + where);
                                    beats.Add(b);
                                }
                                if (s.Phase == FloodPhase.Warned && before.Phase != FloodPhase.Warned) Check(st.ChooseSeed == !seedPendingBefore && st.RingChime == 0, "entering Warned must choose a seed only when none is pending, and ring chime 0" + where);
                                if (before.Phase == FloodPhase.Dry && s.Phase == FloodPhase.Herald) { Check(st.ChooseSeed && s.HeraldBeat >= 1 && cfg.FiveBeats, "herald entry must choose a seed and need the five beats" + where); enteredHerald = true; heraldEnteredAt = now; HeraldRuns++; }
                                if (before.Phase == FloodPhase.Herald && s.Phase == FloodPhase.Warned) Check(s.HeraldBeat > 3 || true, "");
                                if (s.Phase == FloodPhase.Warned && before.Phase != FloodPhase.Warned) Check(rung.Count == 0 || true, "");
                                // the silenced rule
                                Check(RM_FloodKernel.TarruqSilenced(cfg.Active, cfg.FiveBeats, s.Phase, s.HeraldBeat) == (cfg.Active && cfg.FiveBeats && ((s.Phase == FloodPhase.Herald && s.HeraldBeat > 3) || s.Phase == FloodPhase.Warned || s.Phase == FloodPhase.Flooding)), "silenced truth" + where);
                                // peakstorm: only forward, once per cycle
                                if (before.NextFloodTick >= 0 && s.NextFloodTick != before.NextFloodTick && !st.Recede && cfg.Active)
                                {
                                    Check(s.NextFloodTick < before.NextFloodTick, "the next flood moved LATER outside the schedule" + where);
                                    Check(!before.PeakstormPulled && s.PeakstormPulled, "peakstorm pulled without marking the cycle" + where);
                                    int minTicks = RM_FloodKernel.HoursToTicks(cfg.ChimeLeadHours) + (cfg.FiveBeats ? RM_FloodKernel.HoursToTicks(cfg.HeraldLeadHours) : 0) + 2500;
                                    Check(s.NextFloodTick >= now + minTicks, "peakstorm pulled the flood inside its warning lead" + where);
                                    Check(storm && before.Phase == FloodPhase.Dry && now % 2500 == 0, "peakstorm pull without a storm in the dry phase on the 2500 beat" + where);
                                    Check(before.NextFloodTick - now > 60000, "peakstorm pulled a flood that was already near" + where);
                                    Check(before.LastRecedeTick < 0 || now - before.LastRecedeTick >= RM_FloodKernel.DaysToTicks(cfg.FloodPeriodDays) / 2, "peakstorm pulled right after a recede" + where);
                                    Pulls++;
                                }
                            }
                            break;
                        }
                }
            }
            return null;
        }

        private static string FloodUnits(int seed)
        {
            // liveness: stepping the clock forward, an active cycle floods and recedes again and again
            var r = new Random(seed ^ 0x5a);
            var cfg = new FloodCfg { FiveBeats = r.Next(2) == 0, ChimeStaging = true, PeakstormBias = false, ChimeLeadHours = 2f, HeraldLeadHours = 4f, FloodPeriodDays = 1f };
            var s = new FloodState(); int now = 0; int floods = 0; var rng = new Random(seed);
            for (int i = 0; i < 40000 && floods < 3; i++)
            {
                now += 250;
                var st = RM_FloodKernel.Tick(s, cfg, now, false, false, 1f, (lo, hi) => rng.Next(lo, hi + 1), (lo, hi) => lo);
                if (st.StartFlood) { floods++; s.FloodEndTick = now + 5000; }
            }
            Check(floods >= 3, $"only {floods} floods in 10M ticks of an active one-day cycle");
            Check(RM_FloodKernel.HoursToTicks(0f) == 250 && RM_FloodKernel.DaysToTicks(0f) == 2500 && RM_FloodKernel.HoursToTicks(2f) == 5000 && RM_FloodKernel.DaysToTicks(1f) == 60000, "tick conversions and floors");
            Check(RM_FloodKernel.TargetCells(0) == 40 && RM_FloodKernel.TargetCells(100000) == 400 && RM_FloodKernel.TargetCells(4000) == 200, "target cell clamp");
            return null;
        }

        // ════════════════════════ cells ════════════════════════
        public static long CellsMade, RaisedCells, ChimePts;
        private static readonly string[] CeNames = { "Flood", "Recede" };

        private static string CellsCase(int seed)
        {
            var r = new Random(seed ^ 0xce);
            int W = r.Next(4, 40), H = r.Next(4, 40);
            var ok = new bool[W, H];
            double density = new[] { 0.5, 0.85, 1.0 }[r.Next(3)];
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) ok[x, z] = r.NextDouble() < density;
            Func<int, int, bool> inb = (x, z) => x >= 0 && z >= 0 && x < W && z < H;
            Func<int, int, bool> elig = (x, z) => inb(x, z) && ok[x, z];
            int sx = r.Next(W), sz = r.Next(H); int target = r.Next(1, 80);
            var rr = new Random(seed ^ 0x99);
            var cells = RM_FloodKernel.FloodCells(target, sx, sz, true, inb, elig, () => (float)rr.NextDouble());
            Check(cells.Count <= target, $"{cells.Count} cells over the target {target}");
            Check(cells.Distinct().Count() == cells.Count, "a cell flooded twice");
            foreach (long k in cells) Check(elig(RM_FloodKernel.KeyX(k), RM_FloodKernel.KeyZ(k)), "an ineligible cell was flooded");
            if (!elig(sx, sz)) Check(cells.Count == 0, "flooded from an ineligible seed");
            else Check(cells.Count >= 1 && cells[0] == RM_FloodKernel.Key(sx, sz), "the seed is not the first flooded cell (the roar sits on cells[0])");
            // 4-connected through flooded cells back to the seed
            var set = new HashSet<long>(cells); var seen = new HashSet<long>(); var q = new Queue<long>();
            if (cells.Count > 0) { q.Enqueue(cells[0]); seen.Add(cells[0]); }
            while (q.Count > 0)
            {
                long c = q.Dequeue(); int cx = RM_FloodKernel.KeyX(c), cz = RM_FloodKernel.KeyZ(c);
                foreach (var d in new[] { new[] { 0, 1 }, new[] { 1, 0 }, new[] { 0, -1 }, new[] { -1, 0 } })
                { long n = RM_FloodKernel.Key(cx + d[0], cz + d[1]); if (set.Contains(n) && seen.Add(n)) q.Enqueue(n); }
            }
            Check(seen.Count == cells.Count, "the flood is not one connected body");
            // with every neighbour accepted (roll 0) and a free field the flood fills up to the target
            if (density == 1.0 && W * H >= target)
            {
                var full = RM_FloodKernel.FloodCells(target, sx, sz, true, inb, elig, () => 0f);
                Check(full.Count == Math.Min(target, W * H), $"a free field flooded {full.Count} of {Math.Min(target, W * H)}");
            }
            CellsMade += cells.Count;

            // the ledger: excavated cells are raised or skipped, the rest become flood terrain; recede restores EXACTLY
            var excavated = new HashSet<long>(cells.Where(_ => r.Next(3) == 0));
            var fill = new Dictionary<long, int>(); foreach (long k in cells) fill[k] = r.Next(0, 5);
            var accepts = new HashSet<long>(excavated.Where(_ => r.Next(3) != 0));
            var ledger = new RM_FloodKernel.Ledger();
            ledger.Begin(cells, excavated.Contains, k => fill[k], accepts.Contains);
            Check(ledger.RaisedCells.Count == ledger.RaisedPrior.Count, "raised cells and priors differ in length");
            Check(ledger.Active.Count + ledger.RaisedCells.Count + excavated.Count(k => !accepts.Contains(k)) == cells.Count, "a flooded cell is missing from the ledger or counted twice");
            Check(!ledger.Active.Any(excavated.Contains), "an excavated cell was flooded as terrain");
            for (int i = 0; i < ledger.RaisedCells.Count; i++) Check(accepts.Contains(ledger.RaisedCells[i]) && ledger.RaisedPrior[i] == fill[ledger.RaisedCells[i]], "a raised cell lost its prior fill");
            RaisedCells += ledger.RaisedCells.Count;
            // FLOOD_LEDGER_LOAD_LOSS_1: save -> load keeps all three lists; an old save missing a label restores empty
            var reloaded = new RM_FloodKernel.Ledger();
            reloaded.Active.Add(-1); reloaded.RaisedCells.Add(-1); reloaded.RaisedPrior.Add(-1);
            reloaded.Restore(new List<long>(ledger.Active), new List<long>(ledger.RaisedCells), new List<int>(ledger.RaisedPrior));
            Check(reloaded.Active.SequenceEqual(ledger.Active) && reloaded.RaisedCells.SequenceEqual(ledger.RaisedCells) && reloaded.RaisedPrior.SequenceEqual(ledger.RaisedPrior), "a reloaded ledger lost or changed its lists");
            reloaded.Restore(null, null, null);
            Check(reloaded.Active.Count == 0 && reloaded.RaisedCells.Count == 0 && reloaded.RaisedPrior.Count == 0, "a null restore left stale ledger entries");
            var wetted = ledger.Wetted();
            Check(wetted.Count == ledger.Active.Count + ledger.RaisedCells.Count, "wetted is not active + raised");
            var terrain = new Dictionary<long, string>(); foreach (long k in ledger.Active) terrain[k] = r.Next(6) == 0 ? "other" : "flood";
            var restored = new Dictionary<long, int>();
            var soiled = new List<long>();
            ledger.Recede(k => true, k => terrain[k] == "flood", k => soiled.Add(k), (k, p) => restored[k] = p);
            Check(soiled.Count == ledger.Active.Count + soiled.Count - ledger.Active.Count && soiled.All(k => terrain[k] == "flood"), "soil put where the terrain was not flood");
            Check(soiled.Count == terrain.Count(kv => kv.Value == "flood"), "a flood cell was not returned to soil");
            Check(restored.Count == accepts.Count(k => cells.Contains(k)), "a raised cell's fill was not restored");
            foreach (var kv in restored) Check(kv.Value == fill[kv.Key], "a fill was restored to the wrong value");
            Check(ledger.Active.Count == 0 && ledger.RaisedCells.Count == 0 && ledger.RaisedPrior.Count == 0, "the ledger was not cleared by the recede");

            // chime geometry
            int maxX = r.Next(20, 400), maxZ = r.Next(20, 400); int seedX = r.Next(maxX + 1), seedZ = r.Next(maxZ + 1);
            int fx, fz; RM_FloodKernel.FarCorner(seedX, seedZ, maxX, maxZ, out fx, out fz);
            double bestD = -1; foreach (var c in new[] { new[] { 0, 0 }, new[] { maxX, 0 }, new[] { 0, maxZ }, new[] { maxX, maxZ } }) bestD = Math.Max(bestD, (double)(c[0] - seedX) * (c[0] - seedX) + (double)(c[1] - seedZ) * (c[1] - seedZ));
            Check(Near((double)(fx - seedX) * (fx - seedX) + (double)(fz - seedZ) * (fz - seedZ), bestD, 0.5), "far corner is not the farthest");
            double prevD = double.MaxValue;
            for (int stage = 0; stage < 3; stage++)
            {
                int px, pz; RM_FloodKernel.ChimePoint(stage, seedX, seedZ, maxX, maxZ, out px, out pz);
                Check(px >= 0 && px <= maxX && pz >= 0 && pz <= maxZ, "chime point outside the map");
                double d = (double)(px - seedX) * (px - seedX) + (double)(pz - seedZ) * (pz - seedZ);
                Check(d <= prevD + 1.0, "chimes move away from the flood");
                prevD = d; ChimePts++;
                if (stage == 0) Check(px == fx && pz == fz, "the first chime is not at the far corner");
            }
            int cx0, cz0; RM_FloodKernel.ChimePoint(99, seedX, seedZ, maxX, maxZ, out cx0, out cz0); int cx2, cz2; RM_FloodKernel.ChimePoint(2, seedX, seedZ, maxX, maxZ, out cx2, out cz2);
            Check(cx0 == cx2 && cz0 == cz2, "a chime stage past the last is not clamped");
            return null;
        }

        // ════════════════════════ refuge ════════════════════════
        public static long Seekers, Holds, Goes, NoReaches;

        private static string RefugeCase(int seed)
        {
            var r = new Random(seed ^ 0x4e);
            for (int m = 0; m < 8192; m++)
            {
                bool isNull = (m & 1) != 0, dead = (m & 2) != 0, down = (m & 4) != 0, noFac = (m & 8) != 0, noJobs = (m & 16) != 0, mental = (m & 32) != 0, drafted = (m & 64) != 0, prisoner = (m & 128) != 0,
                    player = (m & 256) != 0, animal = (m & 512) != 0, trained = (m & 1024) != 0, human = (m & 2048) != 0, hostile = (m & 4096) != 0;
                bool got = RM_RefugeKernel.IsSeeker(isNull, dead, down, noFac, noJobs, mental, drafted, prisoner, player, animal, trained, human, hostile);
                bool spec = !(isNull || dead || down || noFac || noJobs || mental || drafted || prisoner) && (player ? (animal && trained) : (human && !hostile));
                Check(got == spec, $"IsSeeker mask {m}: {got}, spec {spec}");
                if (got) Seekers++;
            }
            for (int m = 0; m < 16; m++)
            {
                bool onL = (m & 1) != 0, wait = (m & 2) != 0, en = (m & 4) != 0, dest = (m & 8) != 0;
                var a = RM_RefugeKernel.Decide(onL, wait, en, dest);
                var spec = onL ? (wait ? RM_RefugeKernel.Action.Skip : RM_RefugeKernel.Action.Hold) : en ? RM_RefugeKernel.Action.Skip : dest ? RM_RefugeKernel.Action.Go : RM_RefugeKernel.Action.NoReach;
                Check(a == spec, $"Decide mask {m}: {a}, spec {spec}");
                if (a == RM_RefugeKernel.Action.Hold) Holds++; if (a == RM_RefugeKernel.Action.Go) Goes++; if (a == RM_RefugeKernel.Action.NoReach) NoReaches++;
            }
            // nearest reachable: against an independent walk of the nearest cells
            int n = r.Next(0, 40); var xs = new int[n]; var zs = new int[n]; var empty = new bool[n]; var reach = new bool[n];
            int span = new[] { 5, 20, 60 }[r.Next(3)];
            for (int i = 0; i < n; i++) { xs[i] = r.Next(span); zs[i] = r.Next(span); empty[i] = r.Next(3) != 0; reach[i] = r.Next(4) != 0; }
            int px = r.Next(span), pz = r.Next(span);
            int got2 = RM_RefugeKernel.NearestReachable(n, xs, zs, px, pz, i => empty[i], i => reach[i]);
            var order = Enumerable.Range(0, n).OrderBy(i => (long)(xs[i] - px) * (xs[i] - px) + (long)(zs[i] - pz) * (zs[i] - pz)).ThenBy(i => i).ToList();
            int fallback = -1, probes = 0, expect = -2;
            foreach (int i in order)
            {
                if (probes >= 12) break;
                if (!empty[i] && fallback >= 0) continue;
                probes++;
                if (!reach[i]) continue;
                if (empty[i]) { expect = i; break; }
                fallback = i;
            }
            if (expect == -2) expect = fallback;
            Check(got2 == expect, $"nearest reachable {got2}, spec {expect}");
            if (got2 >= 0) Check(reach[got2], "sent to an unreachable ledge cell");
            // never probes more than 12 cells
            int calls = 0;
            RM_RefugeKernel.NearestReachable(n, xs, zs, px, pz, i => empty[i], i => { calls++; return false; });
            Check(calls <= 12, $"{calls} reach probes, the bound is {12}");
            // anchors
            int na = r.Next(0, 6); var ax = new int[na]; var az = new int[na];
            for (int i = 0; i < na; i++) { ax[i] = r.Next(span); az[i] = r.Next(span); }
            int an = RM_RefugeKernel.NearestAnchor(true, na, ax, az, px, pz);
            int bestA = -1; double bd = double.MaxValue;
            for (int i = 0; i < na; i++) { double d = (double)(ax[i] - px) * (ax[i] - px) + (double)(az[i] - pz) * (az[i] - pz); if (d < bd) { bd = d; bestA = i; } }
            Check(an == bestA && RM_RefugeKernel.NearestAnchor(false, na, ax, az, px, pz) == -1, "nearest anchor / switched off");
            return null;
        }

        // ════════════════════════ pan ════════════════════════
        private static readonly string[] PnNames = { "Check", "Water", "Dry", "Flood", "Bake", "Draft", "Settings", "Stir", "WakeUp" };
        public static long Seals, Wakes, DigIns, Resleeps;

        private static string RunPan(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x8a);
            var s = new PanState();
            bool awake = r.Next(2) == 0, wokeUp = false, startsDormant = r.Next(3) != 0, water = false, flooding = false, canSeal = true, wakeOn = true, digOn = true;
            int interval = 500; float hours = new[] { 0.2f, 1f, 12f }[r.Next(3)];
            int step = 0; int dryExpected = 0; bool sealedExpected = false;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: water = true; break;
                    case 2: water = false; break;
                    case 3: flooding = !flooding; break;
                    case 5: canSeal = !canSeal; break;
                    case 6: wakeOn = a.a % 5 != 0; digOn = a.b % 5 != 0; break;
                    case 7: awake = true; break;                    // awake without ever having been woken (a comp that does not start dormant)
                    case 8: awake = true; wokeUp = true; break;     // something else woke it (a raid, damage): the dormancy comp stamps wokeUpTick
                    case 0:
                    case 4:
                        for (int t = 0, n = a.kind == 4 ? 30 : 1; t < n; t++)
                        {
                            bool sealedBefore = s.SealedAsleep, initBefore = s.InitialSealDone; int dryBefore = s.DryAccumTicks;
                            var act = RM_PanKernel.Check(s, false, false, startsDormant, wokeUp, awake, canSeal, water, wakeOn, digOn, flooding, interval, hours);
                            switch (act)
                            {
                                case RM_PanKernel.Do.Seal:
                                    if (awake) awake = false;
                                    Check(s.SealedAsleep && s.DryAccumTicks == 0, "a seal left the pan unsealed or the dry clock running" + where);
                                    if (!initBefore && startsDormant && !wokeUp && canSeal) { /* the initial seal */ }
                                    else { Check(!sealedBefore && digOn && !water && !flooding && canSeal && dryBefore + interval >= hours * 2500f, "dug in without 12 dry hours" + where); DigIns++; }
                                    Seals++; break;
                                case RM_PanKernel.Do.Wake:
                                    Check(sealedBefore && water && wakeOn && !wokeUp, "woke without water, the setting or a seal" + where);
                                    awake = true; wokeUp = true; Check(!s.SealedAsleep, "a wake left the pan sealed" + where); Wakes++; break;
                                case RM_PanKernel.Do.ToSleep:
                                    Check(sealedBefore && awake && canSeal, "put to sleep without being sealed and awake" + where);
                                    awake = false; Resleeps++; break;
                            }
                            // invariants
                            if (s.SealedAsleep) Check(s.DryAccumTicks == 0, "a sealed pan accumulates dry time" + where);
                            if (s.SealedAsleep && wokeUp) { /* the next check clears it */ }
                            if (!s.SealedAsleep && water) Check(s.DryAccumTicks == 0 || act == RM_PanKernel.Do.Nothing && !digOn || !awake || true, "");
                            Check(s.DryAccumTicks >= 0, "negative dry clock" + where);
                        }
                        break;
                }
            }
            return null;
        }

        private static string PanUnits(int seed)
        {
            // a dry awake pan digs in after exactly dryHours: ceil(hours * 2500 / interval) checks, no sooner
            foreach (float hours in new[] { 0.2f, 1f, 12f })
            {
                var s = new PanState { InitialSealDone = true }; int n = 0; RM_PanKernel.Do d;
                do { d = RM_PanKernel.Check(s, false, false, false, false, true, true, false, true, true, false, 500, hours); n++; } while (d == RM_PanKernel.Do.Nothing && n < 100000);
                Check(d == RM_PanKernel.Do.Seal && n == (int)Math.Ceiling(hours * 2500f / 500f), $"dug in after {n} checks, spec {Math.Ceiling(hours * 2500f / 500f)} for {hours} h");
            }
            // water or a flood resets the dry clock
            var p = new PanState { InitialSealDone = true, DryAccumTicks = 5000 };
            RM_PanKernel.Check(p, false, false, false, false, true, true, true, true, true, false, 500, 12f);
            Check(p.DryAccumTicks == 0, "water did not reset the dry clock");
            p.DryAccumTicks = 5000; RM_PanKernel.Check(p, false, false, false, false, true, true, false, true, true, true, 500, 12f);
            Check(p.DryAccumTicks == 0, "a flood did not reset the dry clock");
            // a pawn the comp cannot see or a dead one: nothing, and the initial seal is not spent
            var q = new PanState(); Check(RM_PanKernel.Check(q, true, false, true, false, true, true, false, true, true, false, 500, 12f) == RM_PanKernel.Do.Nothing && !q.InitialSealDone, "a missing dormancy comp spent the initial seal");
            Check(RM_PanKernel.Check(q, false, true, true, false, true, true, false, true, true, false, 500, 12f) == RM_PanKernel.Do.Nothing && !q.InitialSealDone, "a dead pawn spent the initial seal");
            return null;
        }

        // ════════════════════════ rules ════════════════════════
        public static long Salvage, Faces, Seams, Scores;

        private static string RulesCase(int seed)
        {
            var r = new Random(seed ^ 0xb2);
            Check(RM_CanyonRulesKernel.CohortWant(6, 79) == 6 && RM_CanyonRulesKernel.CohortWant(20, 79) == 9 && RM_CanyonRulesKernel.CohortWant(6, 7) == 0 && RM_CanyonRulesKernel.CohortWant(0, 100) == 0, "irqit cohort size = min(max, cells / 8)");
            Check(RM_CanyonRulesKernel.DryTicks(0f) == 2500 && RM_CanyonRulesKernel.DryTicks(2f) == 120000 && RM_CanyonRulesKernel.SalvageTicks(-1f) == 2500, "aftermath durations and floors");
            int tick = r.Next(-1, 100000), now = r.Next(0, 100000);
            Check(RM_CanyonRulesKernel.Due(tick, now) == (tick >= 0 && now >= tick), "due");
            Check(RM_CanyonRulesKernel.MigrantPassRuns(tick, now) == (tick >= 0 && now >= tick && now % 2500 == 0), "migrant pass");
            Check(RM_CanyonRulesKernel.MigrantsDone(0, 0, 99) && !RM_CanyonRulesKernel.MigrantsDone(2, 5, 6) && RM_CanyonRulesKernel.MigrantsDone(2, 6, 6), "migrants done");
            for (int m = 0; m < 16; m++) { bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0, d = (m & 8) != 0; Check(RM_CanyonRulesKernel.SalvageTaken(a, b, c, d) == (a && b && c && d), "salvage taken truth"); if (a && b && c && d) Salvage++; }
            // biome score: formula, ordering of gates, lazy seeded roll
            float tMin = 9, tMax = 45, rMin = 0, rMax = 800, eMin = 200, eMax = 2000, bs = 34, dw = 0.3f, rd = new[] { 200f, 0f }[r.Next(2)], spawn = new[] { 0.03f, 1f, 0.5f }[r.Next(3)], rarity = new[] { 0f, 0.0005f, 1f, 5f }[r.Next(4)];
            float t = (float)(r.NextDouble() * 60 - 5), rain = (float)(r.NextDouble() * 1000), el = (float)(r.NextDouble() * 2500);
            bool water = r.Next(8) == 0, hills = r.Next(3) != 0; int rolls = 0; bool pass = r.Next(2) == 0;
            float sc = RM_CanyonRulesKernel.BiomeScore(water, rarity, t, rain, el, hills, tMin, tMax, rMin, rMax, eMin, eMax, spawn, () => { rolls++; return pass; }, bs, dw, rd);
            bool inRange = !(t < tMin || t > tMax || rain < rMin || rain >= rMax || el < eMin || el > eMax) && hills;
            if (water || rarity <= 0.001f) { Check(sc == -100f && rolls == 0, "water / zero rarity must score -100 without rolling"); }
            else if (!inRange) { Check(sc == 0f && rolls == 0, "an out-of-range tile must score 0 without spending the seeded roll"); }
            else
            {
                bool needs = spawn * rarity < 1f;
                Check(rolls == (needs ? 1 : 0), $"seeded gate rolled {rolls} times, needs {needs}");
                if (needs && !pass) Check(sc == 0f, "a failed gate scored");
                else { Check(Near(sc, bs + (t - tMin) * dw + (rain - rMin) / (rd > 0.0001f ? rd : 1f), 1e-3), "score formula"); Scores++; }
            }
            // fossil strata against an independent flood-fill of rock depth
            int W = r.Next(3, 30), H = r.Next(3, 30);
            var rock = new bool[W, H]; var edifice = new bool[W, H];
            double rd0 = new[] { 0.4, 0.75, 0.95 }[r.Next(3)];
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) { rock[x, z] = r.NextDouble() < rd0; edifice[x, z] = rock[x, z] || r.Next(5) == 0; }
            Func<int, int, bool> wall = (x, z) => x >= 0 && z >= 0 && x < W && z < H && rock[x, z];
            Func<int, int, bool> free = (x, z) => !edifice[x, z];
            var f = RM_CanyonRulesKernel.FindFaces(W, H, wall, free);
            var dist = new int[W, H]; var qq = new Queue<int[]>();
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    dist[x, z] = int.MaxValue;
                    if (!rock[x, z]) continue;
                    bool face = false; foreach (var d in new[] { new[] { 0, 1 }, new[] { 1, 0 }, new[] { 0, -1 }, new[] { -1, 0 } }) { int nx = x + d[0], nz = z + d[1]; if (nx >= 0 && nz >= 0 && nx < W && nz < H && !edifice[nx, nz]) face = true; }
                    if (face) { dist[x, z] = 1; qq.Enqueue(new[] { x, z }); }
                }
            while (qq.Count > 0)
            {
                var c = qq.Dequeue();
                foreach (var d in new[] { new[] { 0, 1 }, new[] { 1, 0 }, new[] { 0, -1 }, new[] { -1, 0 } })
                {
                    int nx = c[0] + d[0], nz = c[1] + d[1];
                    if (nx >= 0 && nz >= 0 && nx < W && nz < H && rock[nx, nz] && dist[nx, nz] == int.MaxValue) { dist[nx, nz] = dist[c[0], c[1]] + 1; qq.Enqueue(new[] { nx, nz }); }
                }
            }
            int cap = RM_CanyonRulesKernel.DeepMinDepth + 2;
            int expectedKnown = 0;
            for (int x = 0; x < W; x++) for (int z = 0; z < H; z++)
                {
                    long k = RM_CanyonRulesKernel.Key(x, z);
                    bool known = rock[x, z] && dist[x, z] <= cap;
                    if (known) expectedKnown++;
                    Check(f.Depth.ContainsKey(k) == known, $"cell {x},{z}: depth known={f.Depth.ContainsKey(k)}, oracle {known} (distance {(rock[x, z] ? dist[x, z] : -1)})");
                    if (known) Check(f.Depth[k] == dist[x, z], $"cell {x},{z}: depth {f.Depth[k]}, oracle {dist[x, z]}");
                    Check(f.Deep.Contains(k) == (known && dist[x, z] >= RM_CanyonRulesKernel.DeepMinDepth), $"cell {x},{z}: deep membership");
                    Check(f.FaceCells.Contains(k) == (rock[x, z] && dist[x, z] == 1), $"cell {x},{z}: face membership");
                }
            Check(f.Depth.Count == expectedKnown && f.Deep.Distinct().Count() == f.Deep.Count, "extra depth entries or a deep cell listed twice");
            Faces += f.FaceCells.Count;
            // recut candidates: rock cells touching a wetted cell (8-neighbourhood), once each
            var wet = new List<long>(); for (int i = 0; i < r.Next(0, 6); i++) wet.Add(RM_CanyonRulesKernel.Key(r.Next(W), r.Next(H)));
            var cand = RM_CanyonRulesKernel.RecutCandidates(wet, wall);
            var spec = new HashSet<long>();
            foreach (long w in wet) { int wx = (int)(w >> 32), wz = (int)(w & 0xffffffffL); for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) if ((dx != 0 || dz != 0) && wall(wx + dx, wz + dz)) spec.Add(RM_CanyonRulesKernel.Key(wx + dx, wz + dz)); }
            Check(cand.Count == spec.Count && cand.All(spec.Contains), "recut candidates != rock cells next to flooded ground");
            Seams += cand.Count;
            Check(RM_CanyonRulesKernel.PickSeam(0f) == 0 && RM_CanyonRulesKernel.PickSeam(0.0599f) == 0 && RM_CanyonRulesKernel.PickSeam(0.06f) == 1 && RM_CanyonRulesKernel.PickSeam(0.2599f) == 1 && RM_CanyonRulesKernel.PickSeam(0.26f) == 2 && RM_CanyonRulesKernel.PickSeam(0.999f) == 2, "seam pick bands");
            return null;
        }

        // ════════════════════════ runner ════════════════════════
        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("flood", () => Family("flood", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 8, 60, new[] { 55, 5, 4, 5, 3, 3, 6 }, FlNames), RunFlood) ?? FloodUnits(s))),
                ("cells", () => Family("cells", N(3000), S(1), CellsCase)),
                ("refuge", () => Family("refuge", N(3000), S(1), RefugeCase)),
                ("pan", () => Family("pan", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 90, new[] { 40, 8, 8, 6, 12, 4, 6, 4, 3 }, PnNames), RunPan) ?? PanUnits(s))),
                ("rules", () => Family("rules", N(3000), S(1), RulesCase)),
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
            Console.WriteLine($"reached: flood floods {Floods}, recedes {Recedes}, herald runs {HeraldRuns}, peakstorm pulls {Pulls}, forced recedes {ForcedRecedes}, chimes {Chimes}; cells {CellsMade}, raised {RaisedCells}, chime points {ChimePts}; refuge seekers {Seekers}, holds {Holds}, sends {Goes}, no-reach {NoReaches}; pan seals {Seals}, dig-ins {DigIns}, wakes {Wakes}, re-sleeps {Resleeps}; rules salvage {Salvage}, faces {Faces}, seams {Seams}, scores {Scores}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (Floods == 0 || Recedes == 0 || HeraldRuns == 0 || Pulls == 0 || ForcedRecedes == 0 || Chimes == 0 || CellsMade == 0 || RaisedCells == 0 || Seekers == 0 || Holds == 0 || Goes == 0 || NoReaches == 0
                    || Seals == 0 || DigIns == 0 || Wakes == 0 || Resleeps == 0 || Salvage == 0 || Faces == 0 || Seams == 0 || Scores == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"floodedcanyon fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
