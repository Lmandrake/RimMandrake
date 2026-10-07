// Approach B for Explosive Growth: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_ExplosiveGrowthKernel.cs):
//   ledger  action sequences (plant/soak/suppress/take/debug-set/pass) over a 12-cell strip against an independent spec world,
//           full state + event multisets compared after every step, plus structural invariants
//   clock   StepCharge regimes and closed form, tell ladder, Hue / VisualScale curves, PassDelta clamp
//   slice   the 8-pass grid sweep slices (cover once, from any cursor) and the surge salinity band
//   top     EffectiveTop exhaustively (7 tops x 6 flags)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.ExplosiveGrowth.SelfTest
{
    internal static class ExplosiveGrowthFuzz
    {
        public static long Cases, Steps, Fires, Armed, Creaks, Refused;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private const int Cells = 12;

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

        // ════════════════════════ ledger ════════════════════════
        private enum A { Plant, Remove, SetRate, SetGrowth, Soak, Suppress, Take, DebugSet, Force, Pass, Wait }
        private struct Act
        {
            public A kind; public int c, v, w; public bool flag;
            public override string ToString() { return kind + "(" + c + "," + v + "," + w + (flag ? ",T" : "") + ")"; }
        }

        private struct PlantS { public bool exists; public int id; public float growth, rate; public bool soaks; }
        private struct RecS { public bool has; public int id; public float charge; public RM_TellStage stage; public float clock; }

        private sealed class Events
        {
            public List<int> dirty = new List<int>(), armed = new List<int>(), creak = new List<int>(), puff = new List<int>(), fire = new List<int>();
            public void Sort() { dirty.Sort(); armed.Sort(); creak.Sort(); puff.Sort(); fire.Sort(); }
            public string Show() { return $"dirty[{string.Join(",", dirty)}] armed[{string.Join(",", armed)}] creak[{string.Join(",", creak)}] puff[{string.Join(",", puff)}] fire[{string.Join(",", fire)}]"; }
            public bool Same(Events o) { return Show() == o.Show(); }
        }

        // The game's side of the world, shared by the kernel's sink and the spec so a fire does the same to both.
        private sealed class World
        {
            public PlantS[] plants = new PlantS[Cells];
            public int nextId = 100;
            public Events ev = new Events();
            public bool[] sound = new bool[1];
            public int[] fires = new int[Cells];
            public void Fire(int c)
            {
                // SplitAndDie, then (every other fire) the sown sprout replants THIS cell with a fresh immature plant. Only the
                // fired cell changes, so the outcome cannot depend on the order in which the pass visits cells.
                plants[c].exists = false;
                fires[c]++;
                if (fires[c] % 2 == 0)
                    plants[c] = new PlantS { exists = true, id = 5000 + c * 100 + fires[c], growth = 0.05f, rate = 1f, soaks = true };
            }
        }

        private sealed class FakeSink : IEgSink<int>
        {
            public World w; public float[] clocks;
            public bool TryGetPlant(int c, out int id, out float growth, out bool soaks)
            {
                PlantS p = w.plants[c];
                id = p.id; growth = p.growth; soaks = p.soaks;
                return p.exists;
            }
            public float GrowthRate(int c) { Check(w.plants[c].exists, "GrowthRate asked on an empty cell " + c); return w.plants[c].rate; }
            public float NewClockFactor(int c) { return clocks[c % clocks.Length]; }
            public void OnDirty(int c) { w.ev.dirty.Add(c); }
            public void OnArmed(int c) { w.ev.armed.Add(c); }
            public void OnCreak(int c) { w.ev.creak.Add(c); }
            public void OnTellPuff(int c) { w.ev.puff.Add(c); }
            public void OnFire(int c) { w.ev.fire.Add(c); w.Fire(c); }
        }

        // Independent spec: plain arrays, ascending-cell loops, every rule restated from the design text.
        private sealed class Spec
        {
            public int[] soak = new int[Cells], supp = new int[Cells];   // 0 = none (time starts above 0)
            public RecS[] rec = new RecS[Cells];
            public World w;
            public int last = -1;

            public bool Soak(int c, int now, int ticks, bool allowed)
            {
                if (!allowed) return false;
                if (supp[c] != 0 && now < supp[c]) return false;
                int until = now + Math.Max(1, ticks);
                if (soak[c] == 0 || soak[c] < until) soak[c] = until;
                return true;
            }
            public void Suppress(int c0, int n, int now, int ticks)
            {
                int until = now + Math.Max(1, ticks);
                for (int c = c0; c < c0 + n && c < Cells; c++)
                {
                    if (supp[c] == 0 || supp[c] < until) supp[c] = until;
                    soak[c] = 0;
                }
            }
            public void Pass(int now, int dt, bool reprint, float ct, bool sounds, float[] clocks)
            {
                for (int c = 0; c < Cells; c++) { if (soak[c] != 0 && soak[c] <= now) soak[c] = 0; if (supp[c] != 0 && supp[c] <= now) supp[c] = 0; }
                for (int c = 0; c < Cells; c++)
                {
                    if (soak[c] == 0) continue;
                    PlantS p = w.plants[c];
                    if (!p.exists || !p.soaks) continue;
                    if (p.growth < 0.999f) { if (reprint) w.ev.dirty.Add(c); continue; }
                    if (!rec[c].has && p.rate > 0f)
                    {
                        rec[c] = new RecS { has = true, id = p.id, charge = 0.0001f, stage = RM_TellStage.Ground, clock = clocks[c % clocks.Length] };
                        w.ev.armed.Add(c);
                    }
                }
                for (int c = 0; c < Cells; c++)
                {
                    if (!rec[c].has) continue;
                    PlantS p = w.plants[c];
                    if (!p.exists || p.id != rec[c].id) { rec[c].has = false; continue; }
                    if (!p.soaks) { rec[c].has = false; w.ev.dirty.Add(c); continue; }
                    bool wet = soak[c] != 0 && now < soak[c] && !(supp[c] != 0 && now < supp[c]);
                    bool growing = p.rate > 0f;
                    float ch = rec[c].charge;
                    if (wet && growing) ch = ch + dt / (ct * rec[c].clock);
                    else if (!wet) ch = ch - dt / (ct * 0.5f);
                    rec[c].charge = ch;
                    if (ch <= 0f) { rec[c].has = false; w.ev.dirty.Add(c); continue; }
                    RM_TellStage want = ch >= 0.95f ? RM_TellStage.Silence : ch >= 0.85f ? RM_TellStage.Creak : ch >= 0.70f ? RM_TellStage.Tremble
                        : ch >= 0.45f ? RM_TellStage.Hue : ch >= 0.15f ? RM_TellStage.Swell : RM_TellStage.Ground;
                    if (want > rec[c].stage)
                    {
                        if (sounds && want >= RM_TellStage.Creak && rec[c].stage < RM_TellStage.Creak) w.ev.creak.Add(c);
                        rec[c].stage = want; w.ev.dirty.Add(c);
                    }
                    if (rec[c].stage == RM_TellStage.Tremble || rec[c].stage == RM_TellStage.Creak) w.ev.puff.Add(c);
                    if (ch >= 1f) { rec[c].has = false; w.ev.fire.Add(c); w.Fire(c); continue; }
                    if (reprint) w.ev.dirty.Add(c);
                }
            }
        }

        private static readonly float[] ChargeTicksSet = { 1024f, 2048f, 4096f };
        private static readonly float[] ClockSet = { 0.25f, 0.5f, 1f, 2f };

        private static Act[] GenActs(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                A kind = k < 14 ? A.Plant : k < 18 ? A.Remove : k < 24 ? A.SetRate : k < 28 ? A.SetGrowth : k < 44 ? A.Soak : k < 50 ? A.Suppress
                    : k < 53 ? A.Take : k < 57 ? A.DebugSet : k < 59 ? A.Force : k < 90 ? A.Pass : A.Wait;
                a[i] = new Act { kind = kind, c = r.Next(Cells), v = r.Next(8), w = r.Next(8), flag = r.Next(4) != 0 };
            }
            return a;
        }

        // returns null if ok, else a message. Mirrors one case: same acts replayed on kernel and spec.
        private static string RunLedger(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x5bd1e995);
            float ct = ChargeTicksSet[rr.Next(ChargeTicksSet.Length)];
            var clocks = new float[Cells]; for (int i = 0; i < Cells; i++) clocks[i] = ClockSet[rr.Next(ClockSet.Length)];
            bool sounds = rr.Next(4) != 0;
            var world = new World(); var sw = new World();   // sw: the spec's own copy of the game
            var kernel = new RM_EgLedger<int>(); var spec = new Spec { w = sw };
            var sink = new FakeSink { w = world, clocks = clocks };
            int now = 1000, lastPass = -1, specLast = -1;
            int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    int c = a.c;
                    switch (a.kind)
                    {
                        case A.Plant:
                            {
                                float[] gs = { 0.1f, 0.999f, 1f, 0.998f };
                                var p = new PlantS { exists = true, id = world.nextId, growth = gs[a.v % 4], rate = (a.w & 1) == 0 ? 0f : 1f, soaks = a.flag };
                                world.plants[c] = p; world.nextId++; sw.plants[c] = p; sw.nextId = world.nextId;
                                break;
                            }
                        case A.Remove: world.plants[c].exists = false; sw.plants[c].exists = false; break;
                        case A.SetRate: world.plants[c].rate = a.v % 2; sw.plants[c].rate = a.v % 2; break;
                        case A.SetGrowth: { float g = a.v % 2 == 0 ? 0.5f : 1f; world.plants[c].growth = g; sw.plants[c].growth = g; break; }
                        case A.Soak:
                            {
                                int ticks = a.v == 0 ? 0 : a.v * 600; bool allowed = a.flag;
                                bool k = kernel.TrySoak(c, now, ticks, allowed), s = spec.Soak(c, now, ticks, allowed);
                                Check(k == s, $"TrySoak returned {k}, spec {s}");
                                if (!k && count) Refused++;
                                break;
                            }
                        case A.Suppress:
                            {
                                int n = 1 + a.v % 3, ticks = a.w * 500;
                                var cells = new List<int>(); for (int x = c; x < c + n && x < Cells; x++) cells.Add(x);
                                kernel.Suppress(cells, now, ticks); spec.Suppress(c, n, now, ticks);
                                break;
                            }
                        case A.Take:
                            {
                                int id = world.plants[c].exists ? world.plants[c].id : -1;
                                float k = kernel.TakeCharge(c, id);
                                float s = 0f; if (world.plants[c].exists && spec.rec[c].has && spec.rec[c].id == id) { s = spec.rec[c].charge; spec.rec[c].has = false; }
                                Check(k == s, $"TakeCharge {k} vs spec {s}");
                                break;
                            }
                        case A.DebugSet:
                            {
                                if (!world.plants[c].exists) break;
                                float val = a.v == 0 ? 0f : a.v / 8f; int id = world.plants[c].id;
                                kernel.DebugSetCharge(c, id, val);
                                if (val <= 0f) spec.rec[c].has = false;
                                else spec.rec[c] = new RecS { has = true, id = id, charge = val, stage = RM_ExplosiveGrowthKernel.StageFor(val), clock = 1f };
                                break;
                            }
                        case A.Force:
                            {
                                float val = 0.5f + a.v / 16f;
                                int k = kernel.DebugForceCharge(val), s = 0;
                                for (int x = 0; x < Cells; x++) if (spec.rec[x].has && spec.rec[x].charge < val) { spec.rec[x].charge = val; s++; }
                                Check(k == s, $"DebugForceCharge {k} vs {s}");
                                break;
                            }
                        case A.Wait: now += 250 * (1 + a.v); break;
                        case A.Pass:
                            {
                                now += 250 * (1 + a.v % 4) * (a.w == 7 ? 8 : 1);
                                int dt = RM_ExplosiveGrowthKernel.PassDelta(now, lastPass); lastPass = now;
                                int sdt = specLast < 0 ? 250 : Math.Max(1, Math.Min(now - specLast, 2000)); specLast = now;
                                Check(dt == sdt, $"PassDelta {dt} vs {sdt}");
                                world.ev = new Events(); sw.ev = new Events();
                                bool reprint = a.flag;
                                kernel.PruneExpired(now);
                                kernel.Pass(sink, now, dt, reprint, ct, sounds);
                                spec.Pass(now, dt, reprint, ct, sounds, clocks);
                                world.ev.Sort(); sw.ev.Sort();
                                Check(world.ev.Same(sw.ev), $"events differ: kernel {world.ev.Show()} vs spec {sw.ev.Show()}");
                                if (count) { Fires += world.ev.fire.Count; Armed += world.ev.armed.Count; Creaks += world.ev.creak.Count; }
                                // structural invariants of a finished pass
                                foreach (var kv in kernel.charges)
                                {
                                    PlantS p = world.plants[kv.Key];
                                    Check(p.exists && p.id == kv.Value.plantId, $"stale record survived the pass at {kv.Key}");
                                    Check(p.soaks, $"record on a non-soaking plant at {kv.Key}");
                                    Check(kv.Value.charge > 0f && kv.Value.charge < 1f, $"charge {kv.Value.charge} out of (0,1) after pass at {kv.Key}");
                                }
                                break;
                            }
                    }
                    // state equality + invariants after every action
                    for (int x = 0; x < Cells; x++)
                    {
                        int ks; kernel.soakUntil.TryGetValue(x, out ks);
                        int kp; kernel.suppressedUntil.TryGetValue(x, out kp);
                        Check(ks == spec.soak[x], $"soak[{x}] kernel {ks} vs spec {spec.soak[x]}");
                        Check(kp == spec.supp[x], $"supp[{x}] kernel {kp} vs spec {spec.supp[x]}");
                        RM_ChargeRecord kr; bool has = kernel.charges.TryGetValue(x, out kr);
                        Check(has == spec.rec[x].has, $"record presence at {x}: kernel {has} vs spec {spec.rec[x].has}");
                        if (has)
                        {
                            RecS s = spec.rec[x];
                            Check(kr.plantId == s.id && kr.charge == s.charge && kr.stage == s.stage && kr.clockFactor == s.clock,
                                $"record at {x}: kernel id{kr.plantId} c{kr.charge} {kr.stage} k{kr.clockFactor} vs spec id{s.id} c{s.charge} {s.stage} k{s.clock}");
                            Check(kr.stage >= RM_TellStage.Ground && kr.stage <= RM_TellStage.Silence, "stage out of ladder");
                        }
                        // a live soak and a live suppression never coexist on a cell
                        Check(!(kernel.IsSoaked(x, now) && kernel.IsSuppressed(x, now)), $"cell {x} is both soaked and suppressed");
                        Check(kernel.IsSoaked(x, now) == (spec.soak[x] != 0 && now < spec.soak[x]), $"IsSoaked({x}) disagrees with spec");
                        Check(kernel.IsSuppressed(x, now) == (spec.supp[x] != 0 && now < spec.supp[x]), $"IsSuppressed({x}) disagrees with spec");
                        // growth factor: 1 unless soaked now on a soaking plant, then max(1, multiplier)
                        float gf = kernel.GrowthFactor(x, now, world.plants[x].soaks, 3f);
                        float wantGf = spec.soak[x] != 0 && now < spec.soak[x] && world.plants[x].soaks ? 3f : 1f;
                        Check(gf == wantGf, $"GrowthFactor({x}) {gf} vs {wantGf}");
                    }
                    // a charge is never armed on an immature / dormant / non-soaking plant at the moment of arming (event check above) -
                    // and the tell stage never exceeds the ladder rung of a freshly armed charge
                    for (int x = 0; x < Cells; x++) if (kernel.charges.ContainsKey(x) && spec.rec[x].charge < 0f) throw new Exception("negative charge");
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> Ledger(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i;
                var r = new Random(seed);
                var acts = GenActs(r, 30 + r.Next(90));
                Cases++;
                string msg = RunLedger(acts, seed, true);
                if (msg == null) continue;
                var small = Shrink(acts.ToList(), t => RunLedger(t, seed, false) != null);
                fails.Add($"ledger seed {seed}: {RunLedger(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ clock ════════════════════════
        private static List<string> Clock(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    float ct = Math.Max(250f, (float)(r.NextDouble() * 20 * 2500)); float clock = 0.9f + (float)r.NextDouble() * 0.2f;
                    int dt = new[] { 250, 500, 1000, 2000 }[r.Next(4)];
                    float c0 = (float)r.NextDouble();
                    // regimes
                    Check(RM_ExplosiveGrowthKernel.StepCharge(c0, true, false, dt, ct, clock) == c0, "wet+dormant must HOLD exactly");
                    Check(RM_ExplosiveGrowthKernel.StepCharge(c0, true, true, dt, ct, clock) > c0, "wet+growing must advance");
                    Check(RM_ExplosiveGrowthKernel.StepCharge(c0, false, true, dt, ct, clock) < c0, "dry must decay");
                    Check(RM_ExplosiveGrowthKernel.StepCharge(c0, false, false, dt, ct, clock) < c0, "dry+dormant must decay");
                    // dry decays exactly twice as fast as wet charges (clock 1)
                    double up = RM_ExplosiveGrowthKernel.StepCharge(0f, true, true, dt, ct, 1f), down = -RM_ExplosiveGrowthKernel.StepCharge(0f, false, true, dt, ct, 1f);
                    Check(Math.Abs(down - 2 * up) < 1e-6 * Math.Max(1, down), $"dry rate {down} is not twice the wet rate {up}");
                    // closed form: k wet+growing passes from the armed charge reach 1.0 after ceil(ct*clock/dt) passes (within the float slack)
                    float c = 0.0001f; int passes = 0;
                    while (c < 1f && passes < 100000) { c = RM_ExplosiveGrowthKernel.StepCharge(c, true, true, dt, ct, clock); passes++; Steps++; }
                    int expect = (int)Math.Ceiling((1.0 - 0.0001) * ct * clock / dt);
                    Check(Math.Abs(passes - expect) <= 1, $"charge took {passes} passes, closed form {expect}");
                    // a dormant soaked charge is never lost, however long it waits
                    c = 0.0001f; for (int k = 0; k < 500; k++) c = RM_ExplosiveGrowthKernel.StepCharge(c, true, false, dt, ct, clock);
                    Check(c > 0f, "dormant charge lost");
                    // ladder
                    float x = (float)r.NextDouble() * 1.2f - 0.1f;
                    RM_TellStage st = RM_ExplosiveGrowthKernel.StageFor(x);
                    Check(st >= RM_TellStage.Ground && st <= RM_TellStage.Silence, "stage outside the ladder");
                    float y = x + (float)r.NextDouble() * 0.3f;
                    Check(RM_ExplosiveGrowthKernel.StageFor(y) >= st, $"StageFor not monotone at {x}->{y}");
                    Check(RM_ExplosiveGrowthKernel.Hue(y) >= RM_ExplosiveGrowthKernel.Hue(x), $"Hue not monotone at {x}->{y}");
                    float h = RM_ExplosiveGrowthKernel.Hue(x);
                    Check(h == 0f || h == 0.25f || h == 0.5f || h == 0.75f || h == 1f, $"Hue {h} not a quarter");
                    Check((h == 0f) == (x <= 0.45f), $"Hue zero iff charge<=0.45 (x={x}, h={h})");
                    float max = 1.2f + (float)r.NextDouble() * 2f;
                    foreach (bool par in new[] { false, true })
                    {
                        float s = RM_ExplosiveGrowthKernel.VisualScale(x, max, par);
                        if (x <= 0.15f) Check(s == 1f, $"scale {s} before swell at {x}");
                        else Check(s >= 1f * 0.965f && s <= max * 1.035f + 1e-4f, $"scale {s} outside [0.965, max*1.035] at {x}");
                        bool trem = x >= 0.70f && x < 0.95f;
                        float plain = RM_ExplosiveGrowthKernel.VisualScale(x, max, true) / 1.035f, other = RM_ExplosiveGrowthKernel.VisualScale(x, max, false) / 0.965f;
                        if (trem) Check(Math.Abs(plain - other) < 1e-4f, "tremble parity changed the base size");
                        else Check(RM_ExplosiveGrowthKernel.VisualScale(x, max, true) == RM_ExplosiveGrowthKernel.VisualScale(x, max, false), "parity wobbled outside the tremble band");
                    }
                    // swell is monotone outside the tremble band
                    float a = 0.16f + (float)r.NextDouble() * 0.5f, b = a + 0.05f;
                    Check(RM_ExplosiveGrowthKernel.VisualScale(b, max, true) >= RM_ExplosiveGrowthKernel.VisualScale(a, max, true), "swell shrank as charge grew");
                    // pass delta clamp
                    int now = r.Next(0, 100000), last = r.Next(0, 3) == 0 ? -1 : r.Next(0, 100000);
                    int d = RM_ExplosiveGrowthKernel.PassDelta(now, last);
                    Check(last < 0 ? d == 250 : d == Math.Max(1, Math.Min(now - last, 2000)), $"PassDelta({now},{last})={d}");
                    Check(d >= 1 && d <= 2000, "PassDelta outside [1,2000]");
                    Check(RM_ExplosiveGrowthKernel.SoakFactor((float)(r.NextDouble() * 3 - 1)) >= 1f, "soak factor below 1 (a soak must never slow growth)");
                    Check(RM_ExplosiveGrowthKernel.ChargeTicks(0f) == 250f && RM_ExplosiveGrowthKernel.ChargeTicks(6f) == 15000f, "ChargeTicks floor/default");
                }
                catch (Exception e) { fails.Add($"clock seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            // exact thresholds, both sides
            try
            {
                float[] th = { 0.15f, 0.45f, 0.70f, 0.85f, 0.95f };
                RM_TellStage[] up = { RM_TellStage.Swell, RM_TellStage.Hue, RM_TellStage.Tremble, RM_TellStage.Creak, RM_TellStage.Silence };
                for (int k = 0; k < th.Length; k++)
                {
                    Check(RM_ExplosiveGrowthKernel.StageFor(th[k]) == up[k], $"StageFor({th[k]}) is not {up[k]} (>= at the threshold)");
                    Check(RM_ExplosiveGrowthKernel.StageFor(th[k] - 1e-4f) == (RM_TellStage)((int)up[k] - 1), $"StageFor just under {th[k]}");
                }
                Check(RM_ExplosiveGrowthKernel.StageFor(0.0001f) == RM_TellStage.Ground, "fresh charge must read Ground");
                Check(RM_ExplosiveGrowthKernel.Hue(0.45f) == 0f && RM_ExplosiveGrowthKernel.Hue(0.4501f) == 0.25f && RM_ExplosiveGrowthKernel.Hue(1f) == 1f, "Hue edges");
                Check(RM_ExplosiveGrowthKernel.VisualScale(0.15f, 2f, true) == 1f && RM_ExplosiveGrowthKernel.VisualScale(0.1501f, 2f, true) > 1f, "swell starts strictly above 0.15");
                Check(Math.Abs(RM_ExplosiveGrowthKernel.VisualScale(0.95f, 2f, true) - (1f + 0.8f / 0.85f)) < 1e-4f && Math.Abs(RM_ExplosiveGrowthKernel.VisualScale(1f, 2f, true) - 2f) < 1e-5f, "scale at the silent moment has no wobble and reaches max at charge 1");
                Check(RM_ExplosiveGrowthKernel.PassDelta(5000, 100) == 2000 && RM_ExplosiveGrowthKernel.PassDelta(100, 100) == 1 && RM_ExplosiveGrowthKernel.PassDelta(0, -1) == 250, "PassDelta edges");
                Cases++;
            }
            catch (Exception e) { fails.Add("clock thresholds: " + e.Message); }
            return fails;
        }

        // ════════════════════════ slice ════════════════════════
        private static List<string> Slice(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    int len = r.Next(4) == 0 ? r.Next(0, 17) : r.Next(0, 200000);
                    int cursor = r.Next(0, 8);
                    var seen = new int[Math.Min(len, 200000)];
                    for (int k = 0; k < 8; k++)
                    {
                        int s, e;
                        RM_ExplosiveGrowthKernel.SliceRange(len, cursor, out s, out e);
                        Check(s >= 0 && e <= len, $"slice [{s},{e}) escapes [0,{len})");
                        Check(e >= s || s >= len, $"slice [{s},{e}) inverted");
                        for (int x = s; x < e; x++) seen[x]++;
                        cursor = RM_ExplosiveGrowthKernel.NextCursor(cursor); Steps++;
                        Check(cursor >= 0 && cursor < 8, "cursor left 0..7");
                    }
                    for (int x = 0; x < len; x++) if (seen[x] != 1) throw new Exception($"cell {x} of {len} swept {seen[x]} times in 8 passes (start cursor {cursor})");
                    Check(RM_ExplosiveGrowthKernel.NextCursor(7) == 0, "cursor does not wrap");
                }
                catch (Exception e) { fails.Add($"slice seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            try
            {
                Check(RM_ExplosiveGrowthKernel.InSurgeBand(0.25f) && RM_ExplosiveGrowthKernel.InSurgeBand(0.48f), "band edges are inclusive");
                Check(!RM_ExplosiveGrowthKernel.InSurgeBand(0.2499f) && !RM_ExplosiveGrowthKernel.InSurgeBand(0.4801f), "outside the band");
                var r = new Random(seed0);
                for (int k = 0; k < 5000; k++) { float s = (float)r.NextDouble(); Check(RM_ExplosiveGrowthKernel.InSurgeBand(s) == (s >= 0.25f && s <= 0.48f), $"band({s})"); Steps++; }
                Cases++;
            }
            catch (Exception e) { fails.Add("surge band: " + e.Message); }
            return fails;
        }

        // ════════════════════════ top ════════════════════════
        private static List<string> Top()
        {
            var fails = new List<string>();
            try
            {
                for (byte top = 0; top <= 7; top++)
                    for (int m = 0; m < 64; m++)
                    {
                        bool burst = (m & 1) != 0, tinder = (m & 2) != 0, slime = (m & 4) != 0, rupt = (m & 8) != 0, flush = (m & 16) != 0, churn = (m & 32) != 0;
                        byte got = RM_ExplosiveGrowthKernel.EffectiveTop(top, burst, tinder, slime, rupt, flush, churn);
                        byte fb = churn ? (byte)0 : (byte)6;
                        bool[] on = { true, burst, slime, tinder, rupt, flush };   // index = top 0..5
                        byte want = top == 6 || top == 7 ? top : top == 0 ? fb : on[top] ? top : fb;
                        Check(got == want, $"EffectiveTop({top}, flags {m}) = {got}, want {want}");
                        Check(got == top || got == fb, $"EffectiveTop({top}, flags {m}) = {got} is neither itself nor the fallback");
                        if (top >= 1 && top <= 5 && !on[top]) Check(got != top, "a disabled variant fired anyway");
                        Cases++; Steps++;
                    }
            }
            catch (Exception e) { fails.Add("top: " + e.Message); }
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
                ("ledger", () => Ledger(N(5000), S(1))),
                ("clock", () => Clock(N(3000), S(1))),
                ("slice", () => Slice(N(2000), S(1))),
                ("top", () => Top()),
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
            if (only == null || only == "ledger")
            {
                Console.WriteLine($"ledger reached: armed {Armed}, creak {Creaks}, fires {Fires}, soaks refused {Refused}");
                if (!oneSeed.HasValue && scale >= 1 && (Armed == 0 || Fires == 0 || Creaks == 0 || Refused == 0)) { Console.WriteLine("FAIL ledger fuzz never reached arm/creak/fire/refusal (blind)"); ok = false; }
            }
            Console.WriteLine($"explosivegrowth fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
