// Approach B for Scarlands: seeded fuzz over the Verse-free kernels the Warscar mod calls (../Kernel/*.cs):
//   aero    the aerosol-screen coverage union (RM_AerosolKernel) against a brute-force lattice oracle
//   ring    the projector-ring condition / salvage / repair state machine (RM_RingKernel) against a literal spec ledger
//   settle  the Settling calm/wind hysteresis (RM_SettlingKernel) against a consecutive-sample oracle
//   reveal  the buried-ordnance reveal rule, exhaustively
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Scarlands.SelfTest
{
    internal static class ScarlandsFuzz
    {
        public static long Cases, Steps;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float Unit(int arg) { return (unchecked((uint)arg * 2654435761u) >> 8) / 16777216f; }

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

        // ════════════════════════ aero ════════════════════════
        private sealed class RawScreen
        {
            public int map, x, z;
            public float propsRadius, factor;
            public bool hasRefuel, hasFuel, spawned, hasFlick, switchOn, needsPower, hasPower, powerOn;
            public RawScreen Clone() { return (RawScreen)MemberwiseClone(); }
            public override string ToString()
            {
                return $"S(m{map} @{x},{z} r{propsRadius}x{factor}{(hasRefuel ? (hasFuel ? " fuel" : " DRY") : "")}{(spawned ? "" : " unspawned")}{(hasFlick ? (switchOn ? " on" : " OFF") : "")}{(needsPower && hasPower ? (powerOn ? " pow" : " NOPOWER") : "")})";
            }
        }

        // The kernel's view of a RawScreen: every number comes from the production kernel, the way the comp computes it.
        private sealed class FakeScreen : IAerosolScreenView
        {
            public RawScreen raw; public object[] maps;
            public bool Live { get { return RM_AerosolKernel.IsLive(raw.spawned, raw.hasFlick, raw.switchOn, raw.needsPower, raw.hasPower, raw.powerOn); } }
            public bool CountsFor(object map) { return ReferenceEquals(maps[raw.map], map) && Live; }
            public int ScreenX { get { return raw.x; } }
            public int ScreenZ { get { return raw.z; } }
            public float ScreenRadius { get { return RM_AerosolKernel.Radius(raw.propsRadius, raw.factor, raw.hasRefuel, raw.hasFuel); } }
        }

        private const int Grid = 32;
        public static long Boundary;

        private static bool[,] Eval(List<RawScreen> screens, bool[] nullSlot, object[] maps, int queryMap, bool enabled, float factorMul = 1f)
        {
            var list = new List<FakeScreen>();
            for (int i = 0; i < screens.Count; i++)
            {
                if (nullSlot != null && nullSlot[i]) { list.Add(null); continue; }
                var r = screens[i].Clone(); r.factor *= factorMul;
                list.Add(new FakeScreen { raw = r, maps = maps });
            }
            var res = new bool[Grid, Grid];
            object qm = queryMap < 0 ? null : maps[queryMap];
            for (int x = 0; x < Grid; x++) for (int z = 0; z < Grid; z++)
                res[x, z] = RM_AerosolKernel.Screened(enabled, qm, x, z, list);
            return res;
        }

        // Independent spec: brute force over a double-precision lattice, liveness restated as a truth table.
        private static bool[,] Oracle(List<RawScreen> screens, bool[] nullSlot, int queryMap, bool enabled)
        {
            var res = new bool[Grid, Grid];
            if (!enabled || queryMap < 0) return res;
            for (int i = 0; i < screens.Count; i++)
            {
                if (nullSlot != null && nullSlot[i]) continue;
                var s = screens[i];
                if (s.map != queryMap) continue;
                bool live = s.spawned;
                if (s.hasFlick && !s.switchOn) live = false;
                if (s.needsPower && s.hasPower && !s.powerOn) live = false;
                if (!live) continue;
                double r = (double)s.propsRadius * (double)s.factor;
                if (s.hasRefuel && !s.hasFuel) r /= 2.0;
                for (int x = 0; x < Grid; x++) for (int z = 0; z < Grid; z++)
                {
                    long d2 = (long)(x - s.x) * (x - s.x) + (long)(z - s.z) * (z - s.z);
                    if (d2 <= r * r) res[x, z] = true;
                }
            }
            return res;
        }

        private static int Diff(bool[,] a, bool[,] b, out int fx, out int fz)
        {
            fx = fz = -1; int n = 0;
            for (int x = 0; x < Grid; x++) for (int z = 0; z < Grid; z++) if (a[x, z] != b[x, z]) { if (n == 0) { fx = x; fz = z; } n++; }
            return n;
        }
        private static bool Subset(bool[,] a, bool[,] b)
        {
            for (int x = 0; x < Grid; x++) for (int z = 0; z < Grid; z++) if (a[x, z] && !b[x, z]) return false;
            return true;
        }

        private static readonly float[] Factors = { 0.5f, 0.75f, 1f, 1.25f, 1.5f, 2f };

        private static RawScreen MakeScreen(Random r)
        {
            return new RawScreen
            {
                map = r.Next(3), x = r.Next(Grid), z = r.Next(Grid),
                propsRadius = r.Next(0, 49) * 0.25f, factor = Factors[r.Next(Factors.Length)],
                hasRefuel = r.Next(3) == 0, hasFuel = r.Next(2) == 0,
                spawned = r.Next(10) != 0, hasFlick = r.Next(3) == 0, switchOn = r.Next(4) != 0,
                needsPower = r.Next(4) != 0, hasPower = r.Next(5) != 0, powerOn = r.Next(4) != 0
            };
        }

        private static string AeroCase(int seed)
        {
            var r = new Random(seed);
            var maps = new object[] { new object(), new object(), new object() };
            var screens = new List<RawScreen>();
            int n = r.Next(0, 9);
            for (int i = 0; i < n; i++) screens.Add(MakeScreen(r));
            // pin one cell exactly on a Pythagorean boundary now and then (r=5 covers (3,4) of the centre)
            if (n > 0 && r.Next(3) == 0) { screens[0].propsRadius = 5f; screens[0].factor = 1f; screens[0].hasRefuel = false; }
            var nullSlot = new bool[n];
            for (int i = 0; i < n; i++) nullSlot[i] = r.Next(12) == 0;
            int q = r.Next(5) == 0 ? -1 : r.Next(3);
            bool enabled = r.Next(8) != 0;
            string d = string.Join(" ", screens) + $" q={q} enabled={enabled}";

            var got = Eval(screens, nullSlot, maps, q, enabled);
            var want = Oracle(screens, nullSlot, q, enabled);
            Steps += Grid * Grid;
            int bad = Diff(got, want, out int fx, out int fz);
            if (bad != 0) Check(false, $"coverage differs from lattice oracle at {bad} cells, first ({fx},{fz}): kernel={got[fx, fz]} oracle={want[fx, fz]} | {d}");

            // boundary exercise tally: cells at exactly squared distance == r*r of a live screen
            foreach (var s in screens)
            {
                double rad = (double)s.propsRadius * s.factor * (s.hasRefuel && !s.hasFuel ? 0.5 : 1.0);
                for (int x = 0; x < Grid; x++) for (int z = 0; z < Grid; z++)
                    if (s.map == q && (long)(x - s.x) * (x - s.x) + (long)(z - s.z) * (z - s.z) == rad * rad && rad > 0) Boundary++;
            }

            if (!enabled || q < 0) Check(got.Cast<bool>().All(b => !b), "setting off or no map still screened a cell | " + d);

            // order independence
            var idx = Enumerable.Range(0, n).OrderBy(_ => r.Next()).ToList();
            var s2 = idx.Select(i => screens[i]).ToList(); var n2 = idx.Select(i => nullSlot[i]).ToArray();
            Check(Diff(Eval(s2, n2, maps, q, enabled), got, out fx, out fz) == 0, $"shuffling the registry changed coverage at ({fx},{fz}) | " + d);

            // union monotone: add a screen -> superset; drop one -> subset
            var plus = new List<RawScreen>(screens) { MakeScreen(r) };
            var plusNull = nullSlot.Concat(new[] { false }).ToArray();
            Check(Subset(got, Eval(plus, plusNull, maps, q, enabled)), "adding a screen uncovered a cell | " + d);
            if (n > 0)
            {
                int k = r.Next(n);
                var minus = new List<RawScreen>(screens); minus.RemoveAt(k);
                var minusNull = nullSlot.Where((_, i) => i != k).ToArray();
                Check(Subset(Eval(minus, minusNull, maps, q, enabled), got), "removing a screen covered a new cell | " + d);
            }
            // a bigger radius factor only widens; a dry gel feed is never wider than a fuelled one
            Check(Subset(got, Eval(screens, nullSlot, maps, q, enabled, 1.5f)), "x1.5 radius uncovered a cell | " + d);
            Check(Subset(Eval(screens, nullSlot, maps, q, enabled, 0.5f), got), "x0.5 radius covered a new cell | " + d);
            // an unrelated map's screens never count: evaluating a map no screen is on is empty
            var other = new List<RawScreen>(screens.Select(s => { var c = s.Clone(); c.map = (q < 0 ? 0 : (q + 1) % 3); return c; }));
            if (q >= 0) Check(Eval(other, nullSlot, maps, q, enabled).Cast<bool>().All(b => !b), "screens on another map covered this one | " + d);
            return null;
        }

        // unit truths of Radius / IsLive / Covers, exhaustively
        private static string AeroUnits()
        {
            foreach (float p in new[] { 0f, 3f, 7.9f, 12f })
                foreach (float f in new[] { 0.5f, 1f, 2f })
                {
                    Steps += 4;
                    float full = p * f;
                    Check(RM_AerosolKernel.Radius(p, f, false, false) == full, $"no refuelable must keep the full radius ({p}x{f})");
                    Check(RM_AerosolKernel.Radius(p, f, true, true) == full, $"fuelled must keep the full radius ({p}x{f})");
                    Check(RM_AerosolKernel.Radius(p, f, true, false) == full * 0.5f, $"dry gel feed must halve the radius ({p}x{f})");
                    Check(RM_AerosolKernel.Radius(p, f, false, true) == full, $"fuel flag without a refuelable comp must not matter ({p}x{f})");
                }
            for (int m = 0; m < 64; m++)
            {
                bool sp = (m & 1) != 0, hf = (m & 2) != 0, on = (m & 4) != 0, np = (m & 8) != 0, hp = (m & 16) != 0, po = (m & 32) != 0;
                bool want = sp && !(hf && !on) && !(np && hp && !po);
                Check(RM_AerosolKernel.IsLive(sp, hf, on, np, hp, po) == want, $"IsLive truth table row {m}");
                Steps++;
            }
            // self-powered ring (needsPower=false) ignores a dead power trader entirely
            Check(RM_AerosolKernel.IsLive(true, false, false, false, true, false), "needsPower=false must ignore power");
            // exact boundary: radius 5 reaches (3,4) and not (4,4)
            Check(RM_AerosolKernel.Covers(3, 4, 0, 0, 5f), "r=5 must cover the 3-4-5 cell");
            Check(!RM_AerosolKernel.Covers(4, 4, 0, 0, 5f), "r=5 must not cover (4,4)");
            Check(RM_AerosolKernel.Covers(0, 0, 0, 0, 0f), "r=0 still covers its own cell");
            return null;
        }

        public static List<string> Aero(int n, int baseSeed)
        {
            var fails = new List<string>();
            Cases++;
            try { AeroUnits(); } catch (Exception e) { fails.Add("aero units: " + e.Message); }
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { AeroCase(baseSeed + k); } catch (Exception e) { fails.Add($"aero seed {baseSeed + k}: {e.Message} {(e is IndexOutOfRangeException ? e.StackTrace : "")}"); }
            }
            return fails;
        }

        // ════════════════════════ ring ════════════════════════
        internal struct Act
        {
            public int kind, ring, arg;
            public override string ToString()
            {
                string[] names = { "Spawn", "Evaluate", "Salvage", "Repair", "Engine", "Lift", "WakeSetting", "SalvageSetting" };
                return names[kind] + "(r" + ring + "," + arg + ")";
            }
        }

        // The harness's mirror of RM_CompWarscarRing's state, driven only through kernel calls.
        private sealed class Ring
        {
            public bool dead, wild = true, spawned, gone, evaluated, wake; public int cond = -1;
            public int x, z;
            public int stripped;
            // literal spec ledger (independent of the kernel)
            public int specCond = -1; public bool specEval, specWild = true, specSpawned, specGone;
            public int everWorking;   // number of times it became Working by repair
        }

        private static float RollValue(int arg)
        {
            switch (arg % 8) { case 0: return 0.69f; case 1: return 0.7f; case 2: return 0.71f; case 3: return 0f; case 4: return 0.9999f; default: return Unit(arg); }
        }

        public static long Stripped, Uninstalled, Repaired, WokenHum;
        private static bool ShipWakes, SalvageOn;

        private static string RunRings(int seed, List<Act> acts, out string digest)
        {
            var r = new Random(seed);
            int n = 1 + r.Next(4);
            var rings = new Ring[n];
            for (int i = 0; i < n; i++) rings[i] = new Ring { dead = r.Next(3) == 0, x = r.Next(60), z = r.Next(60) };
            ShipWakes = true; SalvageOn = true;
            string err = null;
            int step = 0;
            try
            {
                foreach (var a in acts)
                {
                    step++; Steps++;
                    var g = rings[a.ring % n];
                    switch (a.kind)
                    {
                        case 0: // Spawn / install: PostSpawnSetup rolls only an unrolled ring
                            if (g.spawned || g.gone) break;
                            g.spawned = true;
                            if (g.cond < 0) g.cond = g.dead ? (int)RingCondition.Dead : RM_RingKernel.RollLive(RollValue(a.arg));
                            // spec
                            g.specSpawned = true;
                            if (g.specCond < 0) { float v = RollValue(a.arg); g.specCond = g.dead ? 0 : (v < 0.7f ? 2 : 1); }
                            break;
                        case 1:
                            if (g.spawned && g.wild && RM_RingKernel.CanEvaluate(g.evaluated)) g.evaluated = true;
                            if (g.specSpawned && g.specWild && !g.specEval) g.specEval = true;
                            break;
                        case 2:
                            if (SalvageOn && g.spawned && RM_RingKernel.CanSalvage(g.evaluated, g.wild))
                            {
                                RingCondition c = RM_RingKernel.Effective(g.cond);
                                if (RM_RingKernel.Salvage(c) == SalvageResult.Strip) { g.gone = true; g.spawned = false; g.stripped++; Stripped++; }
                                else { g.cond = (int)RM_RingKernel.SalvagedCondition(c); g.evaluated = true; g.wild = false; g.dead = false; g.spawned = false; Uninstalled++; }
                            }
                            if (SalvageOn && g.specSpawned && g.specEval && g.specWild)
                            {
                                if (g.specCond == 0) { g.specGone = true; g.specSpawned = false; }
                                else { g.specWild = false; g.specEval = true; g.specSpawned = false; }
                            }
                            break;
                        case 3:
                            if (SalvageOn && g.spawned && !g.dead && RM_RingKernel.CanRepair(g.wild, RM_RingKernel.Effective(g.cond)))
                            { g.cond = (int)RM_RingKernel.Repaired(); g.everWorking++; Repaired++; }
                            if (SalvageOn && g.specSpawned && !g.specWild && g.specCond == 1) g.specCond = 2;
                            break;
                        case 4:
                            if (g.dead && g.spawned) g.wake = ShipWakes && RM_RingKernel.EngineWakes(a.arg % 80, (a.arg / 80) % 80, g.x, g.z);
                            break;
                        case 5: if (g.dead) g.wake = false; break;
                        case 6: ShipWakes = !ShipWakes; break;
                        case 7: SalvageOn = !SalvageOn; break;
                    }
                    // ---- invariants after every step ----
                    foreach (var q in rings)
                    {
                        Check(q.cond == q.specCond, $"ring condition {q.cond} != spec {q.specCond}");
                        Check(q.evaluated == q.specEval && q.wild == q.specWild && q.spawned == q.specSpawned && q.gone == q.specGone, "state drifted from the spec ledger");
                        if (q.cond >= 0) Check(q.cond <= 2, "condition out of enum range");
                        if (q.dead && q.cond >= 0) Check(q.cond == 0, "dead-def ring left Dead");
                        if (!q.dead && q.cond >= 0 && q.wild) Check(q.cond != 0, "live-def ring rolled Dead");
                        if (q.gone) Check(!q.spawned, "stripped ring still spawned");
                        if (!q.wild) Check(q.evaluated, "a salvaged (player) ring must be evaluated");
                        if (!q.wild) Check(!q.dead, "a salvaged ring is a Dead-def ring");
                        var eff = RM_RingKernel.Effective(q.cond);
                        if (!q.wild) Check(eff != RingCondition.Dead, "salvaged ring is Dead: Dead must be stripped, not carried");
                        bool baseLive = !q.dead && q.spawned;
                        bool live = RM_RingKernel.IsScreenLive(q.dead, baseLive, eff, ShipWakes, q.wake, q.spawned);
                        if (q.dead) Check(live == (ShipWakes && q.wake && q.spawned), "dead ring liveness != wake");
                        else Check(live == (q.spawned && eff == RingCondition.Working), "live ring liveness != Working");
                        if (q.dead && !ShipWakes) Check(!live, "a dead ring hummed with shipWakesLine off");
                        if (q.cond == 1 && !q.dead) Check(!live, "a Failing ring held a dome");
                        if (RM_RingKernel.CanRepair(q.wild, eff) && q.wild) Check(false, "wild ring repairable");
                    }
                }
            }
            catch (Exception e) { err = $"step {step}: {e.Message}"; }
            digest = string.Join(",", rings.Select(q => $"{q.cond}{(q.evaluated ? 'e' : '-')}{(q.wild ? 'w' : 'i')}{(q.gone ? 'x' : '.')}"));
            return err;
        }

        private static List<Act> GenRing(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(20);
                int kind = k < 4 ? 0 : k < 8 ? 1 : k < 12 ? 2 : k < 15 ? 3 : k < 17 ? 4 : k == 17 ? 5 : k == 18 ? 6 : 7;
                if (kind == 6 || kind == 7) { if (r.Next(3) != 0) kind = r.Next(4); }
                l.Add(new Act { kind = kind, ring = r.Next(4), arg = r.Next(6400) });
            }
            return l;
        }

        public static List<string> Rings(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 1);
                var acts = GenRing(r, r.Next(4, 90));
                Cases++;
                string err = RunRings(seed, acts, out string d1);
                if (err == null)
                {
                    RunRings(seed, acts, out string d2);
                    if (d1 != d2) fails.Add($"ring seed {seed}: two replays diverged");
                    continue;
                }
                var min = Shrink(acts, t => RunRings(seed, t, out _) != null);
                string e2 = RunRings(seed, min, out _);
                fails.Add($"ring seed {seed}: {e2} | {string.Join(" ", min)}");
            }
            // exact units: the condition roll boundary, its frequency, the 40-cell wake lattice
            try { RingUnits(); } catch (Exception e) { fails.Add("ring units: " + e.Message); }
            Cases++;
            return fails;
        }

        private static void RingUnits()
        {
            Check(RM_RingKernel.RollLive(0.69f) == 2 && RM_RingKernel.RollLive(0.7f) == 1 && RM_RingKernel.RollLive(0f) == 2 && RM_RingKernel.RollLive(0.9999f) == 1, "RollLive boundary at 0.7");
            Check(RM_RingKernel.RollLive(0.72f) == 1 && RM_RingKernel.RollLive(0.5f) == 2 && RM_RingKernel.RollLive(0.6f) == 2, "RollLive off-boundary probes");
            var r = new Random(7); int w = 0; int N = 100000;
            for (int i = 0; i < N; i++) { Steps++; int c = RM_RingKernel.RollLive((float)r.NextDouble()); Check(c == 1 || c == 2, "live ring rolled Dead"); if (c == 2) w++; }
            Check(Math.Abs(w / (double)N - 0.7) < 0.01, $"Working fraction {w / (double)N} not ~0.7");
            Check(RM_RingKernel.Effective(-1) == RingCondition.Dead, "unrolled reads Dead");
            // wake lattice: reaches exactly 40 cells, not 41, over every lattice point near the circle
            for (int dx = -45; dx <= 45; dx++) for (int dz = -45; dz <= 45; dz++)
            {
                Steps++;
                bool want = (long)dx * dx + (long)dz * dz <= 1600;
                Check(RM_RingKernel.EngineWakes(100 + dx, 100 + dz, 100, 100) == want, $"EngineWakes({dx},{dz}) expected {want}");
            }
            // transition table
            for (int c = 0; c <= 2; c++) for (int ev = 0; ev < 2; ev++) for (int wd = 0; wd < 2; wd++)
            {
                var cond = (RingCondition)c; bool evaluated = ev == 1, wild = wd == 1;
                Check(RM_RingKernel.CanSalvage(evaluated, wild) == (evaluated && wild), "CanSalvage table");
                Check(RM_RingKernel.CanRepair(wild, cond) == (!wild && c == 1), "CanRepair table");
                Check(RM_RingKernel.CanEvaluate(evaluated) == !evaluated, "CanEvaluate table");
                Check(RM_RingKernel.Salvage(cond) == (c == 0 ? SalvageResult.Strip : SalvageResult.Uninstall), "Salvage table");
                Check(RM_RingKernel.SalvagedCondition(cond) == cond, "salvage must carry the condition unchanged");
            }
            Check(RM_RingKernel.Repaired() == RingCondition.Working, "repair yields Working");
            Check(RM_RingKernel.FirstLiveForcedWorking(0, true) && !RM_RingKernel.FirstLiveForcedWorking(0, false) && !RM_RingKernel.FirstLiveForcedWorking(1, true), "first live ring forced Working, only the first");
        }

        // ════════════════════════ settle ════════════════════════
        private sealed class SettleCfg { public float thr, endWind, calmHours, endHours; }

        private static float Wind(Random r, SettleCfg c)
        {
            switch (r.Next(8))
            {
                case 0: return c.thr;                       // exactly calm threshold: NOT calm (strict <)
                case 1: return c.endWind;                   // exactly end threshold: NOT strong (strict >)
                case 2: return BitDec(c.thr, -1);
                case 3: return BitDec(c.endWind, +1);
                default: return (float)(r.NextDouble() * 1.2);
            }
        }
        private static float BitDec(float f, int dir) { return BitConverter.Int32BitsToSingle(BitConverter.SingleToInt32Bits(f) + dir); }

        private static string SettleCase(int seed)
        {
            var r = new Random(seed);
            var c = new SettleCfg { thr = (r.Next(1, 17)) * 0.05f, endWind = r.Next(1, 25) * 0.05f, calmHours = r.Next(2, 97) * 0.25f, endHours = r.Next(1, 49) * 0.25f };
            int needCalm = (int)Math.Ceiling(c.calmHours * 10.0), needWind = (int)Math.Ceiling(c.endHours * 10.0);
            string cfg = $"thr={c.thr} end={c.endWind} calmH={c.calmHours} endH={c.endHours}";
            bool active = false; int calm = 0, windy = 0;
            int runCalm = 0, runWind = 0;   // oracle: consecutive qualifying samples since the last reset
            int len = r.Next(50, 600);
            int starts = 0, ends = 0;
            for (int i = 0; i < len; i++)
            {
                Steps++;
                // bursts: long calm or long wind runs so the thresholds are actually reached
                float wnd = r.Next(30) == 0 ? (r.Next(2) == 0 ? 0f : 1.1f) : Wind(r, c);
                int burst = r.Next(25) == 0 ? r.Next(20, 120) : 1;
                for (int b = 0; b < burst; b++)
                {
                    bool wasActive = active;
                    if (!active)
                    {
                        calm = RM_SettlingKernel.NextCalm(calm, wnd, c.thr);
                        runCalm = wnd < c.thr ? runCalm + 1 : 0;
                        Check(calm == runCalm * RM_SettlingKernel.SampleInterval, $"sample {i}: calm counter {calm} != {runCalm} consecutive calm samples | {cfg}");
                        bool start = RM_SettlingKernel.ShouldStart(calm, c.calmHours);
                        Check(start == (runCalm >= needCalm), $"sample {i}: start={start} but {runCalm} consecutive calm samples, need {needCalm} | {cfg}");
                        if (start) { Check(wnd < c.thr, "Settling started on a non-calm sample"); active = true; calm = 0; windy = 0; runCalm = 0; runWind = 0; starts++; }
                    }
                    else
                    {
                        windy = RM_SettlingKernel.NextWindy(windy, wnd, c.endWind);
                        runWind = wnd > c.endWind ? runWind + 1 : 0;
                        Check(windy == runWind * RM_SettlingKernel.SampleInterval, $"sample {i}: windy counter {windy} != {runWind} consecutive strong samples | {cfg}");
                        bool end = RM_SettlingKernel.ShouldEnd(windy, c.endHours);
                        Check(end == (runWind >= needWind), $"sample {i}: end={end} but {runWind} consecutive strong samples, need {needWind} | {cfg}");
                        if (end) { Check(wnd > c.endWind, "Settling ended on a non-strong sample"); active = false; calm = 0; windy = 0; runCalm = 0; runWind = 0; ends++; }
                    }
                    Check(wasActive || !active || starts > 0, "unreachable");
                }
            }
            // liveness: from any state, enough consecutive qualifying samples always flips it
            if (active) { for (int i = 0; i < needWind; i++) { windy = RM_SettlingKernel.NextWindy(windy, BitDec(c.endWind, +1) < 0 ? 1f : Math.Max(c.endWind + 0.01f, 0.5f), c.endWind); } Check(RM_SettlingKernel.ShouldEnd(windy, c.endHours), $"enough strong wind never ended it | {cfg}"); }
            else { for (int i = 0; i < needCalm; i++) calm = RM_SettlingKernel.NextCalm(calm, c.thr * 0.5f, c.thr); Check(RM_SettlingKernel.ShouldStart(calm, c.calmHours), $"enough calm never started it | {cfg}"); }
            return null;
        }

        public static List<string> Settle(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                Cases++;
                try { SettleCase(baseSeed + k); } catch (Exception e) { fails.Add($"settle seed {baseSeed + k}: {e.Message}"); }
            }
            return fails;
        }

        // ════════════════════════ reveal ════════════════════════
        public static List<string> Reveal(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int open = 0; open <= 8; open++) for (int film = 0; film <= open; film++) foreach (bool relaxed in new[] { false, true })
            {
                Cases++; Steps++;
                bool want = open > 0 && (relaxed ? film >= 1 : film * 10 >= open * 6);   // 60% as an exact rational
                bool got = RM_SettlingKernel.RevealOk(open, film, relaxed);
                if (got != want) fails.Add($"reveal open={open} film={film} relaxed={relaxed}: kernel={got} spec={want}");
                if (relaxed && !got && RM_SettlingKernel.RevealOk(open, film, false)) fails.Add($"reveal open={open} film={film}: strict reveals but the last look does not");
                if (film > 0 && got == false && RM_SettlingKernel.RevealOk(open, film - 1, relaxed)) fails.Add($"reveal open={open}: more film revealed less (film {film})");
            }
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
                ("aero", () => Aero(N(4000), S(1))),
                ("ring", () => Rings(N(4000), S(1))),
                ("settle", () => Settle(N(3000), S(1))),
                ("reveal", () => Reveal(0, 0)),
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
            if (only == null || only == "ring") { Console.WriteLine($"ring transitions reached: stripped {Stripped}, uninstalled {Uninstalled}, repaired {Repaired}"); if (!oneSeed.HasValue && scale >= 1 && (Stripped == 0 || Uninstalled == 0 || Repaired == 0)) { Console.WriteLine("FAIL ring fuzz never reached a transition (blind)"); ok = false; } }
            Console.WriteLine($"aero cells sitting exactly on a screen radius (boundary exercised): {Boundary}");
            Console.WriteLine($"scarlands fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
