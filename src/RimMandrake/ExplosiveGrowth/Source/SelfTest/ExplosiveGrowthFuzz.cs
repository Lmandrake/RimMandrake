// Approach B for Explosive Growth: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_ExplosiveGrowthKernel.cs):
//   ledger  action sequences (plant/soak/suppress/take/debug-set/pass) over a 12-cell strip against an independent spec world,
//           full state + event multisets compared after every step, plus structural invariants
//   clock   StepCharge regimes and closed form, tell ladder, Hue / VisualScale curves, PassDelta clamp
//   slice   the 8-pass grid sweep slices (cover once, from any cursor) and the surge salinity band
//   top     EffectiveTop exhaustively (7 tops x 6 flags)
//   rate    the ruled moisture factor (spec §2.5) exhaustively, plus Cycles / CycleWet
//   outcome ResolveOutcome exhaustively and its Burst share, AgeRemoval, StaggerOpen, RainWet, SizeStep
//   tree    TreeMoistureFactor exhaustively, Drink (litres buy days) against a day-by-day spec world, the owner's worked
//           numbers (tree_burst_design_2026-10-17.md §3, §6b), JungleEndOfLife, ContinuousDrinkLitres
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
        private enum A { Plant, Remove, SetRate, SetGrowth, Soak, Suppress, Take, DebugSet, Force, Pass, Wait, SetWet }
        private struct Act
        {
            public A kind; public int c, v, w; public bool flag;
            public override string ToString() { return kind + "(" + c + "," + v + "," + w + (flag ? ",T" : "") + ")"; }
        }

        private struct PlantS { public bool exists; public int id; public float growth, rate; public bool soaks; }
        private struct RecS { public bool has; public int id; public float charge; public RM_TellStage stage; public float clock; public byte step; }

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
            public bool[] wet = new bool[Cells];   // presence-model sources other than the timed soak (spill, rain, river)
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
            public World w; public float[] clocks; public RM_EgLedger<int> lg; public int now;
            public bool CycleWet(int c) { return w.wet[c] || lg.IsSoaked(c, now); }
            public int Hash(int c) { return c * 7919; }
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
            public byte[] step = new byte[Cells];
            private static byte Step(float ch)
            {
                if (ch <= 0.15f) return 0;
                float t = (ch - 0.15f) / 0.85f; if (t > 1f) t = 1f;
                int k = 1 + (int)(t * 7.999f); return (byte)(k > 8 ? 8 : k);
            }
            private static bool Open(int hash, int now) { uint h = unchecked((uint)hash * 2654435761u); int d = (int)(h % 60000u); return ((now + d) % 60000) < 2500; }
            private bool Wet(int c, int now) { bool sp = supp[c] != 0 && now < supp[c]; return !sp && (w.wet[c] || (soak[c] != 0 && now < soak[c])); }
            public void Pass(int now, int dt, bool reprint, float ct, bool sounds, float[] clocks, bool stagger)
            {
                for (int c = 0; c < Cells; c++) { if (soak[c] != 0 && soak[c] <= now) soak[c] = 0; if (supp[c] != 0 && supp[c] <= now) supp[c] = 0; }
                for (int c = 0; c < Cells; c++)
                {
                    PlantS p = w.plants[c];
                    if (rec[c].has || !p.exists || !p.soaks) continue;
                    if (p.growth < 0.999f) continue;
                    if (!Wet(c, now)) continue;
                    if (stagger && !Open(c * 7919, now)) continue;
                    if (p.rate > 0f)
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
                    bool wet = Wet(c, now);
                    bool growing = p.rate > 0f;
                    float ch = rec[c].charge;
                    if (wet && growing) ch = ch + dt / (ct * rec[c].clock);
                    else if (!wet) ch = ch - dt / (ct * 0.5f);
                    rec[c].charge = ch;
                    if (ch <= 0f) { rec[c].has = false; w.ev.dirty.Add(c); continue; }
                    RM_TellStage want = ch >= 0.95f ? RM_TellStage.Silence : ch >= 0.85f ? RM_TellStage.Creak : ch >= 0.70f ? RM_TellStage.Tremble
                        : ch >= 0.45f ? RM_TellStage.Hue : ch >= 0.15f ? RM_TellStage.Swell : RM_TellStage.Ground;
                    bool dirty = false;
                    if (want > rec[c].stage)
                    {
                        if (sounds && want >= RM_TellStage.Creak && rec[c].stage < RM_TellStage.Creak) w.ev.creak.Add(c);
                        rec[c].stage = want; dirty = true;
                    }
                    byte st = Step(ch); if (st != rec[c].step) { rec[c].step = st; dirty = true; }
                    bool trem = rec[c].stage == RM_TellStage.Tremble || rec[c].stage == RM_TellStage.Creak;
                    if (trem) w.ev.puff.Add(c);
                    if (ch >= 1f) { rec[c].has = false; w.ev.fire.Add(c); w.Fire(c); continue; }
                    if (dirty || (reprint && trem)) w.ev.dirty.Add(c);
                }
            }
        }

        private static readonly float[] ChargeTicksSet = { 1024f, 2048f, 4096f };
        private static readonly int[] AllCells = Enumerable.Range(0, Cells).ToArray();
        private static readonly float[] ClockSet = { 0.25f, 0.5f, 1f, 2f };

        private static Act[] GenActs(Random r, int len)
        {
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(100);
                A kind = k < 14 ? A.Plant : k < 18 ? A.Remove : k < 24 ? A.SetRate : k < 28 ? A.SetGrowth : k < 44 ? A.Soak : k < 50 ? A.Suppress
                    : k < 53 ? A.Take : k < 57 ? A.DebugSet : k < 59 ? A.Force : k < 84 ? A.Pass : k < 90 ? A.SetWet : A.Wait;
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
            bool stagger = rr.Next(3) == 0;
            var world = new World(); var sw = new World();   // sw: the spec's own copy of the game
            var kernel = new RM_EgLedger<int>(); var spec = new Spec { w = sw };
            var sink = new FakeSink { w = world, clocks = clocks, lg = kernel };
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
                        case A.SetWet: world.wet[c] = a.flag; sw.wet[c] = a.flag; break;
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
                                else spec.rec[c] = new RecS { has = true, id = id, charge = val, stage = RM_ExplosiveGrowthKernel.StageFor(val), clock = 1f, step = 0 };
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
                                sink.now = now;
                                kernel.Pass(sink, AllCells, now, dt, reprint, ct, sounds, stagger);
                                spec.Pass(now, dt, reprint, ct, sounds, clocks, stagger);
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
                Check(Math.Abs(RM_ExplosiveGrowthKernel.VisualScale(0.95f, 2f, true) - (1f + RM_ExplosiveGrowthKernel.SizeStep(0.95f) / 8f)) < 1e-4f && Math.Abs(RM_ExplosiveGrowthKernel.VisualScale(1f, 2f, true) - 2f) < 1e-5f, "scale at the silent moment has no wobble and reaches max at charge 1");
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

        // ════════════════════════ scope ════════════════════════
        // PLANT_GROWTH_MERGE_NEVER_MEANT_APART: the ambient bands. (The scope is now a biome, read at runtime against
        // the DefDatabase; nothing Verse-free is left to fuzz there.)
        private static List<string> Scope()
        {
            var fails = new List<string>();
            try
            {
                // OQ-11: an ash restart lasts its window, extends never shortens, and prunes.
                {
                    var lg = new RM_EgLedger<int>();
                    lg.RestartAsh(3, 1000, 180000);
                    Check(lg.AshRestarted(3, 1000) && lg.AshRestarted(3, 180999) && !lg.AshRestarted(3, 181000), "ash window edges");
                    lg.RestartAsh(3, 2000, 10);
                    Check(lg.AshRestarted(3, 180999), "a shorter restart shortened the window");
                    lg.PruneExpired(181001);
                    Check(lg.ashUntil.Count == 0, "expired ash restart not pruned");
                    Cases++; Steps++;
                }
                // EGROWTH_SOAK_FIX_DURATION_INT_WRAP: a huge API duration soaks/suppresses (clamped), never wraps to expired.
                foreach (int now in new[] { 0, 1000, 5_000_000 })
                    foreach (int ticks in new[] { 1, 2500, int.MaxValue - 10, int.MaxValue })
                    {
                        var lg = new RM_EgLedger<int>();
                        Check(lg.TrySoak(1, now, ticks, true) && lg.IsSoaked(1, now) && lg.IsSoaked(1, now + Math.Min(ticks, 1_000_000) - 1),
                            $"TrySoak(now {now}, ticks {ticks}) not soaked within its duration (int wrap)");
                        lg.Suppress(new[] { 2 }, now, ticks);
                        Check(lg.IsSuppressed(2, now), $"Suppress(now {now}, ticks {ticks}) not suppressed at once (int wrap)");
                        Cases++; Steps++;
                    }
            }
            catch (Exception e) { fails.Add("scope: " + e.Message); }
            return fails;
        }


        // ════════════════════════ rate ════════════════════════
        // The ruled table restated from the spec text (§2.5), exhaustively over archetype x 8 flags, at the ruled defaults and
        // at random sliders.
        private static float SpecRate(RM_Archetype a, bool scope, bool stalled, bool sealedG, bool wet, bool ash, bool woody, bool near, RM_RateSettings s)
        {
            if (!scope) return 1f;                       // outside our biomes: vanilla (OQ-10)
            if (sealedG) return 1f;                      // H1 basins / pots / hydroponics
            if (a == RM_Archetype.Exempt) return 1f;
            if (a == RM_Archetype.Vanilla) return s.vanillaNeedsWater && !near ? s.vanillaDry : 1f;   // setting A, OQ-16/17
            if (stalled) return s.stunted;
            float r = a == RM_Archetype.WetNative ? s.wetNative                       // C1 x4 always
                    : (wet || (a == RM_Archetype.FireAdapted && ash)) ? s.dryWet : s.dryDry;   // C6, C5
            return woody ? r * s.treeRatio : r;          // EC1
        }

        private static List<string> Rate(int n, int seed0)
        {
            var fails = new List<string>();
            try
            {
                var rnd = new Random(seed0);
                for (int k = 0; k < n; k++)
                {
                    RM_RateSettings s = k == 0 ? RM_RateSettings.Ruled : new RM_RateSettings
                    {
                        dryWet = 1f + (float)rnd.NextDouble() * 19f, dryDry = 0.01f + (float)rnd.NextDouble(), wetNative = 1f + (float)rnd.NextDouble() * 9f,
                        treeRatio = 0.1f + (float)rnd.NextDouble() * 0.9f, stunted = 0.1f + (float)rnd.NextDouble() * 1.9f,
                        vanillaDry = 0.01f + (float)rnd.NextDouble(), vanillaNeedsWater = rnd.Next(2) == 0,
                    };
                    for (int ai = 0; ai < 5; ai++)
                        for (int m = 0; m < 128; m++)
                        {
                            var a = (RM_Archetype)ai;
                            bool sc = (m & 1) != 0, st = (m & 2) != 0, se = (m & 4) != 0, w = (m & 8) != 0, ash = (m & 16) != 0, wd = (m & 32) != 0, nr = (m & 64) != 0;
                            float got = RM_ExplosiveGrowthKernel.MoistureFactor(a, sc, st, se, w, ash, wd, nr, s);
                            float want = SpecRate(a, sc, st, se, w, ash, wd, nr, s);
                            Check(Math.Abs(got - want) < 1e-6f, $"MoistureFactor({a}, scope {sc}, stalled {st}, sealed {se}, wet {w}, ash {ash}, woody {wd}, near {nr}) = {got}, want {want}");
                            Check(got > 0f, "a factor of 0 would stop growth outright (the rule only scales, light alone stops it)");
                            bool cyc = RM_ExplosiveGrowthKernel.Cycles(a, sc, st, se);
                            Check(cyc == (sc && !st && !se && (a == RM_Archetype.DryNative || a == RM_Archetype.WetNative || a == RM_Archetype.FireAdapted)), $"Cycles({a},{sc},{st},{se})");
                            bool cw = RM_ExplosiveGrowthKernel.CycleWet(a, w, ash);
                            Check(cw == (a == RM_Archetype.WetNative || w || (a == RM_Archetype.FireAdapted && ash)), $"CycleWet({a},{w},{ash})");
                            Cases++; Steps++;
                        }
                }
                // the ruled numbers themselves (W3/C6/C1/EC1/OQ-16)
                RM_RateSettings d = RM_RateSettings.Ruled;
                Check(d.dryWet == 10f && d.dryDry == 0.1f && d.wetNative == 4f && d.treeRatio == 0.625f && d.vanillaDry == 0.1f && d.vanillaNeedsWater, "ruled defaults drifted");
                Check(RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.DryNative, true, false, false, true, false, true, false, d) == 6.25f, "dry tree wet != x6.25");
                Check(RM_ExplosiveGrowthKernel.MoistureFactor(RM_Archetype.WetNative, true, false, false, false, false, true, false, d) == 2.5f, "wet tree != x2.5");
            }
            catch (Exception e) { fails.Add("rate: " + e.Message); }
            return fails;
        }

        // ════════════════════════ outcome ════════════════════════
        private static List<string> Outcome(int n, int seed0)
        {
            var fails = new List<string>();
            try
            {
                float[] chances = { -1f, 0f, 0.3333f, 1f, 0.5f };
                float[] rolls = { 0f, 0.1f, 0.3332f, 0.3334f, 0.5f, 0.99999f };
                for (int ai = 0; ai < 5; ai++)
                    for (byte top = 0; top <= 6; top++)
                        foreach (float ch in chances)
                            foreach (float roll in rolls)
                                for (int m = 0; m < 8; m++)
                                {
                                    var a = (RM_Archetype)ai;
                                    bool crop = (m & 1) != 0, self = (m & 2) != 0, burst = (m & 4) != 0;
                                    RM_Outcome got = RM_ExplosiveGrowthKernel.ResolveOutcome(a, top, ch, 0.3333f, roll, crop, self, burst);
                                    RM_Outcome want;
                                    if (top == 6) want = RM_Outcome.None;
                                    else if (crop && self) want = RM_Outcome.SelfFruit;                       // EC3 / OQ-15
                                    else if (top >= 2 && top <= 5) want = RM_Outcome.OwnTop;                  // OQ-5: own odds
                                    else
                                    {
                                        float c = ch >= 0f ? ch : a == RM_Archetype.WetNative ? 0f : 0.3333f; // C3, §4.2
                                        want = burst && roll < c ? RM_Outcome.Burst : a == RM_Archetype.WetNative ? RM_Outcome.Wither : RM_Outcome.Fruit;
                                    }
                                    Check(got == want, $"ResolveOutcome({a}, top {top}, chance {ch}, roll {roll}, crop {crop}, selfFruit {self}, burst {burst}) = {got}, want {want}");
                                    Cases++; Steps++;
                                }
                // the 1-in-3 share over a uniform roll
                var r = new Random(seed0);
                int bursts = 0, N = Math.Max(3000, n * 30);
                for (int i = 0; i < N; i++) if (RM_ExplosiveGrowthKernel.ResolveOutcome(RM_Archetype.DryNative, 0, -1f, 0.3333f, (float)r.NextDouble(), false, true, true) == RM_Outcome.Burst) bursts++;
                double share = bursts / (double)N;
                Check(Math.Abs(share - 0.3333) < 0.03, $"dry-native Burst share {share:0.000}, ruled 1 in 3");
                // dormancy: the mean removal is (1 - r) x 2000; never more than 2000, never negative
                foreach (float rr in new[] { 0f, 0.0625f, 0.1f, 0.4f, 0.999f, 1f, 4f, 10f, -1f })
                {
                    double sum = 0; int M = 2000;
                    for (int i = 0; i < M; i++)
                    {
                        int off = RM_ExplosiveGrowthKernel.AgeRemoval(rr, (float)r.NextDouble());
                        Check(off >= 0 && off <= 2000, $"AgeRemoval({rr}) = {off} outside [0,2000]");
                        sum += off; Steps++;
                    }
                    double want = rr >= 1f ? 0 : (1 - Math.Max(0, rr)) * 2000;
                    Check(Math.Abs(sum / M - want) < 1.0, $"AgeRemoval({rr}) mean {sum / M:0.00}, want {want:0.00}");
                    Cases++;
                }
                Check(2000 - RM_ExplosiveGrowthKernel.AgeRemoval(0.1f, 0.5f) == 200, "x0.1 ages 200 ticks per 2000");
                // stagger: every cell opens exactly one hour in each day, and a reload replays it (pure)
                for (int k = 0; k < Math.Max(20, n / 10); k++)
                {
                    int h = r.Next();
                    int open = 0;
                    for (int t = 0; t < 60000; t += 250) if (RM_ExplosiveGrowthKernel.StaggerOpen(h, t)) open++;
                    Check(open == 10, $"StaggerOpen(hash {h}) open {open} of 240 passes, want 10 (one hour)");
                    Check(RM_ExplosiveGrowthKernel.StaggerOpen(h, 12345) == RM_ExplosiveGrowthKernel.StaggerOpen(h, 12345 + 60000), "stagger not periodic by day");
                    Cases++; Steps += 240;
                }
                // rain (OQ-9)
                Check(RM_ExplosiveGrowthKernel.RainWet(true, 5, 0, 0, 999), "raining is wet even after a drink (it refills)");
                Check(RM_ExplosiveGrowthKernel.RainWet(false, 100, 50, 7550, int.MinValue), "after-rain hours wet");
                Check(!RM_ExplosiveGrowthKernel.RainWet(false, 7550, 50, 7550, int.MinValue), "after-rain wet ends at its linger");
                Check(!RM_ExplosiveGrowthKernel.RainWet(false, 100, 50, 7550, 60), "a drink after the rain stopped dries the cell");
                Check(RM_ExplosiveGrowthKernel.RainWet(false, 100, 50, 7550, 40), "a drink during the rain does not");
                Check(!RM_ExplosiveGrowthKernel.RainWet(false, 100, -1, -1, int.MinValue), "never rained: dry");
                // size steps
                Check(RM_ExplosiveGrowthKernel.SizeStep(0.15f) == 0 && RM_ExplosiveGrowthKernel.SizeStep(0.1501f) == 1 && RM_ExplosiveGrowthKernel.SizeStep(1f) == 8, "SizeStep edges");
                float prev = 0; for (float x = 0; x <= 1.2f; x += 0.001f) { float st = RM_ExplosiveGrowthKernel.SizeStep(x); Check(st >= prev && st <= 8, "SizeStep not monotone in [0,8]"); prev = st; }
                Cases += 3;
            }
            catch (Exception e) { fails.Add("outcome: " + e.Message); }
            return fails;
        }

        // ════════════════════════ tree ════════════════════════
        // tree_burst_design_2026-10-17.md: T2 (no x10, no tree ratio; dry x0.1 kept; jungle x4 young, x1 grown), Q1/Q4 (40 L
        // per day of life: growth while young, then age), Q5/Q6 (a drink past the lifespan is a water-driven death), Q14
        // (unlimited life: growth only, never an end), Q11 (a jungle tree's end of life).
        private static float SpecTreeRate(RM_Archetype a, bool scope, bool stalled, bool sealedG, bool wet, bool ash, bool mature, RM_RateSettings s)
        {
            if (!scope || sealedG) return 1f;
            if (a == RM_Archetype.Exempt || a == RM_Archetype.Vanilla) return 1f;    // never trees; neutral
            if (stalled) return s.stunted;
            if (a == RM_Archetype.WetNative) return mature ? 1f : s.wetNative;        // Q11
            return (wet || (a == RM_Archetype.FireAdapted && ash)) ? 1f : s.dryDry;   // T2: the water's effect is the drink
        }

        private static List<string> Tree(int n, int seed0)
        {
            var fails = new List<string>();
            try
            {
                var rnd = new Random(seed0);
                // rate, exhaustive over archetype x 6 flags, ruled and random sliders
                for (int k = 0; k < Math.Max(1, n / 50); k++)
                {
                    RM_RateSettings s = k == 0 ? RM_RateSettings.Ruled : new RM_RateSettings
                    {
                        dryWet = 1f + (float)rnd.NextDouble() * 19f, dryDry = 0.01f + (float)rnd.NextDouble(), wetNative = 1f + (float)rnd.NextDouble() * 9f,
                        treeRatio = 0.1f + (float)rnd.NextDouble() * 0.9f, stunted = 0.1f + (float)rnd.NextDouble() * 1.9f,
                        vanillaDry = 0.01f + (float)rnd.NextDouble(), vanillaNeedsWater = rnd.Next(2) == 0,
                    };
                    for (int ai = 0; ai < 5; ai++)
                        for (int m = 0; m < 64; m++)
                        {
                            var a = (RM_Archetype)ai;
                            bool sc = (m & 1) != 0, st = (m & 2) != 0, se = (m & 4) != 0, w = (m & 8) != 0, ash = (m & 16) != 0, mat = (m & 32) != 0;
                            float got = RM_ExplosiveGrowthKernel.TreeMoistureFactor(a, sc, st, se, w, ash, mat, s);
                            float want = SpecTreeRate(a, sc, st, se, w, ash, mat, s);
                            Check(Math.Abs(got - want) < 1e-6f, $"TreeMoistureFactor({a}, scope {sc}, stalled {st}, sealed {se}, wet {w}, ash {ash}, mature {mat}) = {got}, want {want}");
                            Check(got <= Math.Max(Math.Max(Math.Max(1f, s.wetNative), s.stunted), s.dryDry) + 1e-6f, $"a tree above every ruled ceiling ({a}, wet {w}): {got}");
                            Cases++; Steps++;
                        }
                }
                RM_RateSettings d = RM_RateSettings.Ruled;
                Check(RM_ExplosiveGrowthKernel.TreeMoistureFactor(RM_Archetype.DryNative, true, false, false, true, false, false, d) == 1f, "dry tree wet != x1 (T2)");
                Check(RM_ExplosiveGrowthKernel.TreeMoistureFactor(RM_Archetype.DryNative, true, false, false, false, false, true, d) == 0.1f, "dry tree dry != x0.1 (RS §5.2)");
                Check(RM_ExplosiveGrowthKernel.TreeMoistureFactor(RM_Archetype.WetNative, true, false, false, false, false, false, d) == 4f, "jungle tree young != x4 (Q11)");
                Check(RM_ExplosiveGrowthKernel.TreeMoistureFactor(RM_Archetype.WetNative, true, false, false, true, false, true, d) == 1f, "jungle tree grown != x1 (Q11)");

                // the owner's worked numbers (§3 table, §6b): a 400 L spill at 40 L/day buys 10 days
                RM_DrinkResult sw = RM_ExplosiveGrowthKernel.Drink(0f, 0, 480f, true, 480 * 12 * 60000, 400f, 40f);
                Check(Math.Abs(sw.days - 10f) < 1e-5f && Math.Abs(sw.growth - 10f / 480f) < 1e-6f && sw.age == 0 && !sw.waterDeath, "Sweetline 480 d: one spill is +10/480 growth, no age");
                RM_DrinkResult vr = RM_ExplosiveGrowthKernel.Drink(0f, 0, 18f, true, 810 * 60000, 400f, 40f);
                Check(Math.Abs(vr.growth - 10f / 18f) < 1e-5f, "Vault Root: one spill is +56% growth");
                // litres to the end of life from maturity = remaining life days x 40 (§3)
                int life = 5760 * 60000;
                RM_DrinkResult edge = RM_ExplosiveGrowthKernel.Drink(1f, 480 * 60000, 480f, true, life, (5760 - 480) * 40f, 40f);
                Check(!edge.waterDeath && edge.age == life, "exactly the remaining life's litres lands ON the lifespan, not past it");
                RM_DrinkResult over = RM_ExplosiveGrowthKernel.Drink(1f, 480 * 60000, 480f, true, life, (5760 - 480) * 40f + 1f, 40f);
                Check(over.waterDeath, "one litre more is a water-driven death");
                RM_DrinkResult im = RM_ExplosiveGrowthKernel.Drink(0.5f, 123, 400f, false, 0, 1e9f, 40f);
                Check(im.growth == 1f && im.age == 123 && !im.waterDeath, "Q14: an unlimited-life tree only grows, never ages by water, never dies of it");
                Check(Math.Abs(RM_ExplosiveGrowthKernel.ContinuousDrinkLitres(2000, 40f) - 40f / 30f) < 1e-6f, "a TickLong of river = 40/30 L");
                Check(RM_ExplosiveGrowthKernel.ContinuousDrinkLitres(60000, 40f) == 40f, "a day of river = the cap");
                Check(RM_ExplosiveGrowthKernel.ContinuousDrinkLitres(2000, 0f) == 0f && RM_ExplosiveGrowthKernel.ContinuousDrinkLitres(-5, 40f) == 0f, "no cap / no time = no water");
                Check(!RM_ExplosiveGrowthKernel.JungleEndOfLife(1000, 2000, false, 0), "Q14: an immortal jungle tree never ends");
                Check(RM_ExplosiveGrowthKernel.JungleEndOfLife(99000, 2000, true, 100000) && !RM_ExplosiveGrowthKernel.JungleEndOfLife(98000, 2000, true, 100000)
                      && RM_ExplosiveGrowthKernel.JungleEndOfLife(200000, 2000, true, 100000), "JungleEndOfLife edges (vanilla Dying is age > lifespan)");
                Check(RM_ExplosiveGrowthKernel.JungleEndOfLife(int.MaxValue - 10, 2000, true, int.MaxValue), "JungleEndOfLife must not overflow");
                Cases += 12;

                // random drinks against a day-by-day spec world
                for (int k = 0; k < n; k++)
                {
                    float growDays = (float)(0.5 + rnd.NextDouble() * 600);
                    bool limited = rnd.Next(4) != 0;
                    float lifeDays = limited ? growDays * (float)(1 + rnd.NextDouble() * 60) : 0f;
                    int lifespan = limited ? (int)Math.Min(int.MaxValue, lifeDays * 60000.0) : 0;
                    float growth = rnd.Next(3) == 0 ? 1f : (float)rnd.NextDouble();
                    int age = rnd.Next(3) == 0 ? (int)(rnd.NextDouble() * Math.Min(int.MaxValue, Math.Max(1.0, lifespan * 1.2))) : rnd.Next(0, 6000000);
                    float perDay = (float)(1 + rnd.NextDouble() * 200);
                    float litres = rnd.Next(5) == 0 ? 0f : (float)(rnd.NextDouble() * rnd.NextDouble() * 400000);
                    RM_DrinkResult r = RM_ExplosiveGrowthKernel.Drink(growth, age, growDays, limited, lifespan, litres, perDay);
                    double days = litres > 0 ? litres / (double)perDay : 0;
                    // spec: growth first, the rest is age; age only when limited
                    double toMature = growth < 1f ? (1.0 - growth) * growDays : 0;
                    double wantGrowth = growth < 1f ? Math.Min(1.0, growth + days / growDays) : growth;
                    double rest = Math.Max(0, days - toMature);
                    long wantAge = limited && growth + days / growDays >= 1.0 ? Math.Min(int.MaxValue, age + (long)Math.Round(rest * 60000)) : age;
                    Check(Math.Abs(r.growth - wantGrowth) < 1e-4, $"seed {seed0} case {k}: growth {r.growth}, want {wantGrowth} (g0 {growth}, days {days}, growDays {growDays})");
                    Check(Math.Abs(r.age - wantAge) <= 1, $"seed {seed0} case {k}: age {r.age}, want {wantAge}");
                    Check(r.growth >= growth - 1e-6f && r.age >= age && r.growth <= 1f, "a drink never takes growth or age away");
                    bool wantDeath = limited && age <= lifespan && r.age > lifespan;
                    Check(r.waterDeath == wantDeath, $"waterDeath {r.waterDeath}, want {wantDeath} (age {age} -> {r.age}, lifespan {lifespan})");
                    if (!limited) Check(!r.waterDeath && r.age == age, "Q14: immortal never ages or dies by water");
                    if (limited && age > lifespan) Check(!r.waterDeath, "a tree dying of age is never re-killed by water");
                    Cases++; Steps++;
                }
            }
            catch (Exception e) { fails.Add("tree: " + e.Message); }
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
                ("scope", () => Scope()),
                ("rate", () => Rate(N(40), S(1))),
                ("outcome", () => Outcome(N(200), S(1))),
                ("tree", () => Tree(N(20000), S(1))),
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
