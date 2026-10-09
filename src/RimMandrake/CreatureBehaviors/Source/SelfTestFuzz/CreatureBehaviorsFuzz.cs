// Approach B for CreatureBehaviors: seeded random ACTION SEQUENCES over the production kernels the mod calls
//   shade   RM_MovingShadeLayer (moving-shade grid + dirty rectangles) vs a from-scratch recast oracle
//   bounds  RM_MovingShadeMath.ShadowBounds must contain every cell CastBody writes
//   swim    RM_SandSwimKernel.Evaluate (the sand swimmer's surface/submerge machine) against design invariants
// A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`, so it replays.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.CreatureBehaviors.FuzzSelfTest
{
    internal static class CreatureBehaviorsFuzz
    {
        public static long Cases, Steps;
        public static long CovStrike, CovMelee, CovDry, CovStorm, CovWindowStay, CovSubmerge, CovGroundBreach, CovShadeMoved, CovShadeCmp;
        public static long StaleOnToggle;   // tolerated: shade left standing after the setting turns off until the next forced recompute

        internal struct Act
        {
            public string[] names;
            public int kind, arg;
            public override string ToString() { return names[kind] + "(" + arg + ")"; }
        }

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

        // ───────────────────────── shade: moving-shade layer ─────────────────────────

        private static readonly string[] ShadeNames = { "Register", "Unregister", "Move", "Kill", "Refresh", "RefreshForce", "Sun", "ToggleOn" };

        private sealed class Caster { public bool alive = true; public int x, z; public bool hasProps; public float height; public int radius; public float depth; }

        private sealed class ShadeWorld : IRM_MovingCasterSource<int>
        {
            public int w, h;
            public RM_MovingShadeLayer<int> layer = new RM_MovingShadeLayer<int>();
            public Dictionary<int, Caster> model = new Dictionary<int, Caster>();   // every caster that ever existed
            public HashSet<int> reg = new HashSet<int>();                           // currently registered with the layer
            public bool on = true, directional;
            public float dx = 1, dz = 0, lenPerHeight = 2f;
            public bool toggledSinceForce;
            public const float MaxCast = 16f, Tip = 0.6f;

            public bool TryGetCaster(int key, out RM_MovingCasterInfo info)
            {
                info = default(RM_MovingCasterInfo);
                Caster c;
                if (!model.TryGetValue(key, out c)) return false;
                if (!c.alive) { info.alive = false; return key % 2 == 0; }     // a despawned pawn: some sources say "not alive", some say nothing
                info.alive = true; info.x = c.x; info.z = c.z;
                info.hasProps = c.hasProps; info.height = c.height; info.radius = c.radius; info.depth = c.depth;
                return true;
            }

            public float[] Oracle()
            {
                var g = new float[w * h];
                if (!on) return g;
                foreach (int id in reg)
                {
                    var c = model[id];
                    if (!c.alive || !c.hasProps || c.height <= 0f) continue;
                    float len = directional ? RM_SunHeatMath.ShadowLength(c.height, lenPerHeight, MaxCast) : 0f;
                    int a, b, cc, d;
                    if (!RM_MovingShadeMath.ShadowBounds(w, h, c.x, c.z, c.radius, directional, dx, dz, len, out a, out b, out cc, out d)) continue;
                    RM_MovingShadeMath.CastBody(g, w, h, c.x, c.z, c.radius, directional, dx, dz, len, Tip, c.depth);
                }
                return g;
            }
        }

        private static ShadeWorld MakeShade(int seed)
        {
            var r = new Random(seed);
            var w = new ShadeWorld { w = r.Next(1, 26), h = r.Next(1, 26) };
            w.directional = r.Next(3) != 0;
            w.dx = (float)(r.NextDouble() * 2 - 1); w.dz = (float)(r.NextDouble() * 2 - 1);
            w.lenPerHeight = (float)(r.NextDouble() * 5);
            return w;
        }

        private static string StepShade(ShadeWorld w, Act a)
        {
            int id = (a.arg / 7) % 6;
            switch (a.kind)
            {
                case 0: // Register: first time creates the caster, later times re-register an existing (maybe dead) one
                    {
                        Caster c;
                        if (!w.model.TryGetValue(id, out c))
                        {
                            c = new Caster
                            {
                                x = (a.arg * 31) % (w.w + 6) - 3, z = (a.arg * 17) % (w.h + 6) - 3,
                                hasProps = a.arg % 11 != 0, height = a.arg % 5 == 0 ? 0f : 0.5f + Unit(a.arg) * 3f,
                                radius = a.arg % 4, depth = a.arg % 6 == 0 ? 1.4f : a.arg % 9 == 0 ? 0f : Unit(a.arg + 1)
                            };
                            w.model[id] = c;
                        }
                        w.layer.Register(id);
                        w.reg.Add(id);
                        break;
                    }
                case 1: // Unregister
                    {
                        float[] snap = w.layer.Grid == null ? null : (float[])w.layer.Grid.Clone();
                        w.layer.Unregister(id, w.w, w.h);
                        w.reg.Remove(id);
                        if (snap != null)
                            for (int i = 0; i < snap.Length; i++)
                                if (w.layer.Grid[i] > snap[i]) return "Unregister raised cell " + i;
                        break;
                    }
                case 2: // Move (one cell, a jump, or off the map)
                    {
                        Caster c;
                        if (!w.model.TryGetValue(id, out c)) break;
                        int m = a.arg % 5;
                        c.x = m == 0 ? c.x + 1 : m == 1 ? c.x - 1 : (a.arg * 13) % (w.w + 6) - 3;
                        c.z = m == 2 ? c.z + 1 : m == 3 ? c.z - 1 : (a.arg * 29) % (w.h + 6) - 3;
                        break;
                    }
                case 3: // Kill (despawn): the layer must notice at its next refresh
                    {
                        Caster c;
                        if (w.model.TryGetValue(id, out c)) c.alive = false;
                        break;
                    }
                case 4: return RefreshShade(w, false);
                case 5: return RefreshShade(w, true);
                case 6: // Sun change: the component recomputes with force
                    w.directional = a.arg % 4 != 0;
                    w.dx = Unit(a.arg) * 2 - 1; w.dz = Unit(a.arg + 5) * 2 - 1;
                    if (a.arg % 13 == 0) { w.dx = 0; w.dz = 0; }
                    w.lenPerHeight = Unit(a.arg + 9) * 5f;
                    return RefreshShade(w, true);
                case 7:
                    w.on = !w.on; w.toggledSinceForce = true;
                    break;
            }
            return null;
        }

        private static string RefreshShade(ShadeWorld w, bool force)
        {
            // the component's guard: nothing registered and not forced is a no-op that may leave the grid null
            w.layer.Refresh(w, w.w, w.h, force, w.on, w.directional, w.dx, w.dz, w.lenPerHeight, ShadeWorld.MaxCast, ShadeWorld.Tip);
            if (force) w.toggledSinceForce = false;
            // dead casters are dropped by the refresh
            foreach (int id in w.reg.ToList()) if (!w.model[id].alive) w.reg.Remove(id);
            if (w.layer.Count != w.reg.Count) return "layer holds " + w.layer.Count + " casters, model " + w.reg.Count;
            if (w.layer.Grid == null) return null;
            var want = w.Oracle();
            CovShadeCmp++;
            if (want.Any(v => v > 0f)) CovShadeMoved++;
            for (int i = 0; i < want.Length; i++)
            {
                float v = w.layer.Grid[i];
                if (v < 0f || v > 1f) return "cell " + i + " = " + v + " outside [0,1]";
                if (v != want[i])
                {
                    if (!force && w.toggledSinceForce) { StaleOnToggle++; return null; }
                    return "incremental != fresh at cell " + (i % w.w) + "," + (i / w.w) + ": " + v + " vs " + want[i] + (force ? " (forced)" : "");
                }
            }
            return null;
        }

        private static string RunShade(int seed, List<Act> acts)
        {
            try
            {
                var w = MakeShade(seed);
                foreach (var a in acts)
                {
                    Steps++;
                    string e = StepShade(w, a);
                    if (e != null) return e + " [after " + a + "]";
                }
                return null;
            }
            catch (Exception ex) { return ex.GetType().Name + ": " + ex.Message; }
        }

        private static List<Act> GenShade(Random r, int len)
        {
            var l = new List<Act>(len);
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(20);
                int kind = k < 3 ? 0 : k < 4 ? 1 : k < 10 ? 2 : k < 11 ? 3 : k < 16 ? 4 : k < 17 ? 5 : k < 19 ? 6 : 7;
                l.Add(new Act { names = ShadeNames, kind = kind, arg = r.Next(1, 100000) });
            }
            return l;
        }

        public static List<string> Shade(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 7919 + 3);
                var acts = GenShade(r, r.Next(5, 120));
                Cases++;
                if (RunShade(seed, acts) == null) continue;
                var min = Shrink(acts, t => RunShade(seed, t) != null);
                fails.Add($"shade seed {seed}: {RunShade(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ───────────────────────── bounds: dirty rectangle covers the cast ─────────────────────────

        public static List<string> Bounds(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 104729 + 7);
                Cases++; Steps++;
                int w = r.Next(1, 40), h = r.Next(1, 40);
                int cx = r.Next(-6, w + 6), cz = r.Next(-6, h + 6), rad = r.Next(-3, 5);
                bool dir = r.Next(4) != 0;
                float dx = (float)(r.NextDouble() * 2 - 1) * (r.Next(6) == 0 ? 1e-3f : 1f), dz = (float)(r.NextDouble() * 2 - 1);
                if (r.Next(10) == 0) { dx = 0; dz = 0; }
                if (r.Next(8) == 0) { dx = r.Next(2) == 0 ? 1 : -1; dz = 0; }
                float height = (float)(r.NextDouble() * 4), lph = (float)(r.NextDouble() * 6);
                float len = dir ? RM_SunHeatMath.ShadowLength(height, lph, 16f) : 0f;
                float depth = (float)r.NextDouble();
                var g = new float[w * h];
                RM_MovingShadeMath.CastBody(g, w, h, cx, cz, rad, dir, dx, dz, len, 0.6f, depth);
                int a, b, c, d;
                bool ok = RM_MovingShadeMath.ShadowBounds(w, h, cx, cz, rad, dir, dx, dz, len, out a, out b, out c, out d);
                if (ok && (a < 0 || b < 0 || c > w - 1 || d > h - 1 || a > c || b > d)) { fails.Add($"bounds seed {seed}: bounds [{a},{b}]-[{c},{d}] not a non-empty rectangle inside the {w}x{h} map"); continue; }
                if (!ok && a <= c && b <= d) { fails.Add($"bounds seed {seed}: reported off the map but [{a},{b}]-[{c},{d}] is a rectangle"); continue; }
                if (depth > 0f && !dir)                                 // the isotropic ring: every cell of the (r+1) square on the map holds the depth
                {
                    int er = Math.Max(0, rad) + 1; bool bad = false;
                    for (int z = Math.Max(0, cz - er); z <= Math.Min(h - 1, cz + er) && !bad; z++)
                        for (int x = Math.Max(0, cx - er); x <= Math.Min(w - 1, cx + er); x++)
                            if (g[z * w + x] != depth) { fails.Add($"bounds seed {seed}: ring cell ({x},{z}) = {g[z * w + x]}, depth {depth} (r {rad})"); bad = true; break; }
                    if (bad) continue;
                }
                if (RM_SunHeatMath.Clamp01(depth) > 0f && depth > 0f && ShadowTouched(g) == 0 && ok && ((!dir) || len >= 0f) && rad >= 0 && cx >= 0 && cz >= 0 && cx < w && cz < h) { fails.Add($"bounds seed {seed}: a caster on the map with depth {depth} wrote nothing"); continue; }
                for (int i = 0; i < g.Length; i++)
                {
                    if (g[i] == 0f) continue;
                    int x = i % w, z = i / w;
                    if (!ok || x < a || x > c || z < b || z > d)
                    {
                        fails.Add($"bounds seed {seed}: cast wrote ({x},{z})={g[i]} outside bounds [{a},{b}]-[{c},{d}] ok={ok} (w{w} h{h} c({cx},{cz}) r{rad} dir={dir} d({dx},{dz}) len{len})");
                        break;
                    }
                    if (g[i] > 1f) { fails.Add($"bounds seed {seed}: cell value {g[i]} above 1"); break; }
                }
            }
            return fails;
        }

        private static int ShadowTouched(float[] g) { int n = 0; foreach (float v in g) if (v > 0f) n++; return n; }

        public static List<string> BoundsExtra(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n && fails.Count < 5; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 15485863 + 5);
                Cases++; Steps++;
                const int W = 60, H = 60;
                int cx = r.Next(20, 40), cz = r.Next(20, 40), rad = r.Next(0, 3);
                float ang = (float)(r.NextDouble() * Math.PI * 2), dx = (float)Math.Cos(ang), dz = (float)Math.Sin(ang);
                float len = 3f + (float)(r.NextDouble() * 8), depth = 0.2f + (float)r.NextDouble() * 0.8f;
                var g = new float[W * H];
                RM_MovingShadeMath.CastBody(g, W, H, cx, cz, rad, true, dx, dz, len, 0.6f, depth);
                int outside = 0;
                for (int i = 0; i < g.Length; i++)
                    if (g[i] > 0f && (Math.Abs(i % W - cx) > rad || Math.Abs(i / W - cz) > rad)) outside++;
                if (outside == 0) fails.Add($"bounds-tail seed {seed}: a directional caster (len {len:F1}, dir {dx:F2},{dz:F2}) cast no tail outside its footprint");
                var zero = new float[W * H];
                RM_MovingShadeMath.CastBody(zero, W, H, cx, cz, rad, r.Next(2) == 0, dx, dz, len, 0.6f, r.Next(2) == 0 ? 0f : -0.5f);
                if (ShadowTouched(zero) != 0) fails.Add($"bounds-zero seed {seed}: zero or negative depth still wrote shade");
            }
            return fails;
        }

        // ───────────────────────── swim: the sand swimmer machine ─────────────────────────

        private static readonly string[] SwimNames = { "Tick", "Damage", "Down", "Terrain", "Target", "Melee", "Storm", "Weather" };

        private enum TKind { None, PawnWater, PawnDry, Thing }

        private struct SwimEnv : IRM_SwimEnv
        {
            public SwimWorld w;
            public int Now { get { return w.now; } }
            public int SurfacedUntil { get { return w.surfacedUntil; } }
            public bool Submerged { get { return w.submerged; } }
            public bool DroidImmunity { get { return w.immunity; } }
            public float StrikeRange { get { return w.range; } }
            public bool OnSwimTerrain() { return w.onSwim; }
            public bool TryGetTarget(out bool isPawn, out bool hasWater, out int distSq)
            {
                isPawn = w.tk == TKind.PawnWater || w.tk == TKind.PawnDry;
                hasWater = w.tk == TKind.PawnWater;
                distSq = w.tk == TKind.None ? 0 : w.dist;
                return w.tk != TKind.None;
            }
            public bool StormBlindsStrike()
            {
                if (!(w.stormChance < 1f)) return false;
                w.rolls++;
                return w.rollFails;
            }
            public bool MeleeThreat() { w.meleeReads++; return w.melee; }
            public void EndJob() { w.endJobs++; }
            public void Surface(bool breach) { w.surfaceCalls++; w.DoSurface(breach); }
            public void Submerge() { w.submergeCalls++; if (!w.submerged) w.submerged = true; }
        }

        private sealed class SwimWorld
        {
            public int now, surfacedUntil = -1, surfacedTicks = 300;
            public bool submerged, onSwim = true, immunity = true, melee, rollFails, downed;
            public float range = 1.9f, stormChance = 1f;
            public TKind tk; public int dist;
            public int rolls, meleeReads, endJobs, surfaceCalls, submergeCalls, breaches;

            public void DoSurface(bool breach)
            {
                if (!submerged) return;            // the comp's Surface only acts on a swimmer that has the hediff
                submerged = false;
                if (breach) { surfacedUntil = RM_SandSwimKernel.BreachUntil(now, surfacedTicks); breaches++; }
            }
        }

        private static SwimWorld MakeSwim(int seed)
        {
            var r = new Random(seed);
            return new SwimWorld
            {
                onSwim = r.Next(5) != 0, immunity = r.Next(4) != 0, surfacedTicks = r.Next(0, 4) * 150,
                range = (float)(1 + r.NextDouble() * 2), stormChance = r.Next(3) == 0 ? 0.3f : 1f,
                now = r.Next(0, 5000)
            };
        }

        private static string Evaluate(SwimWorld w)
        {
            // snapshot, run, and check this Evaluate against the design table
            bool sub0 = w.submerged, on = w.onSwim, melee = w.melee;
            int until0 = w.surfacedUntil;
            w.rolls = w.meleeReads = w.endJobs = w.surfaceCalls = w.submergeCalls = w.breaches = 0;
            var env = new SwimEnv { w = w };
            RM_SandSwimKernel.Evaluate(ref env);
            bool hasT = w.tk != TKind.None;
            bool inRange = hasT && w.dist <= w.range * w.range;
            bool dry = w.tk == TKind.PawnDry && w.immunity && sub0;
            bool stormPossible = sub0 && hasT && !dry && w.stormChance < 1f;

            if (w.submerged && !w.onSwim) return "submerged off swim terrain";
            if (w.submerged && w.now < w.surfacedUntil) return "submerged inside the surfaced window (now " + w.now + " < " + w.surfacedUntil + ")";
            if (w.rolls > 1) return "storm rolled " + w.rolls + " times in one evaluate";
            if (w.rolls == 1 && !(stormPossible && on)) return "storm roll consumed when it cannot matter (sub0=" + sub0 + ")";
            if (w.rolls == 0 && stormPossible && on) return "storm roll skipped when it should apply";
            if (w.meleeReads > 1) return "melee threat read " + w.meleeReads + " times";
            if (w.endJobs > 2) return "job ended " + w.endJobs + " times";
            if (w.breaches > 0 && !sub0) return "breach from a swimmer that was not submerged";
            if (w.surfaceCalls + w.submergeCalls != 1 && !(w.surfaceCalls + w.submergeCalls == 0 && on)) return "evaluate made " + w.surfaceCalls + " surface and " + w.submergeCalls + " submerge calls";
            if (w.breaches > 0 && w.surfacedUntil != w.now + w.surfacedTicks) return "breach window " + w.surfacedUntil + " != now+ticks";
            if (w.breaches == 0 && w.surfacedUntil != until0) return "surfacedUntil moved without a breach";

            if (!on)
            {
                if (w.submerged) return "stayed under on hard ground";
                if (w.surfaceCalls != 1) return "no surface call on hard ground";
                if (sub0 && w.breaches != 1) return "left the sand without a breach";
                if (sub0) CovGroundBreach++;
                return null;
            }
            bool storm = stormPossible && w.rollFails;
            bool targetLive = hasT && !dry && !storm;
            if (dry) CovDry++;
            if (storm) CovStorm++;
            if (dry && w.endJobs < 1) return "droid-immune target not dropped";
            if (storm && w.endJobs < 1) return "storm-blinded strike not dropped";
            if (dry && !storm && !melee && w.rolls != 0) return "dry target still rolled";
            if (targetLive && w.dist <= w.range * w.range)
            {
                if (w.submerged) return "stayed under with a live target in strike range";
                if (sub0 && w.breaches != 1) return "strike did not breach";
                if (sub0) CovStrike++;
                return null;
            }
            if (melee)
            {
                if (w.submerged) return "stayed under in melee";
                if (sub0 && w.breaches != 1) return "melee did not breach";
                if (sub0) CovMelee++;
                return null;
            }
            // nothing forces it up
            if (w.now < until0)
            {
                if (sub0) return "submerged swimmer inside a surface window (state unreachable)";
                if (w.submerged) return "re-submerged inside the surfaced window";
                CovWindowStay++;
                return null;
            }
            if (!w.submerged) return "did not submerge with nothing holding it up (now " + w.now + " until " + until0 + ")";
            if (!sub0) CovSubmerge++;
            return null;
        }

        private static string StepSwim(SwimWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // Tick: time passes, then the 30-tick evaluate
                    w.now += 30 * (1 + a.arg % 12);
                    if (w.downed) { w.DoSurface(false); return null; }
                    w.rollFails = a.arg % 3 != 0;
                    return Evaluate(w);
                case 1: // Damage: a submerged swimmer is driven up with a breach
                    if (w.submerged) w.DoSurface(true);
                    return null;
                case 2: // Down / recover
                    w.downed = !w.downed;
                    if (w.downed) w.DoSurface(false);
                    return null;
                case 3: w.onSwim = a.arg % 4 != 0; return null;
                case 4: // Target
                    {
                        int m = a.arg % 5;
                        w.tk = m == 0 ? TKind.None : m == 1 ? TKind.PawnWater : m == 2 ? TKind.PawnDry : m == 3 ? TKind.Thing : TKind.PawnWater;
                        w.dist = a.arg % 3 == 0 ? 1 : a.arg % 3 == 1 ? 3 : 40;
                        if (a.arg % 7 == 0) { w.range = 1 + a.arg % 3; w.dist = (int)(w.range * w.range); }     // exactly on the strike line
                        return null;
                    }
                case 5: w.melee = a.arg % 3 == 0; return null;
                case 6: w.immunity = a.arg % 3 != 0; return null;
                case 7: w.stormChance = a.arg % 3 == 0 ? 0.25f : 1f; return null;
            }
            return null;
        }

        private static string RunSwim(int seed, List<Act> acts)
        {
            try
            {
                var w = MakeSwim(seed);
                foreach (var a in acts)
                {
                    Steps++;
                    string e = StepSwim(w, a);
                    if (e != null) return e + " [after " + a + "]";
                }
                return null;
            }
            catch (Exception ex) { return ex.GetType().Name + ": " + ex.Message; }
        }

        public static long SwimEvals, SwimBreaches, SwimSubmerges;

        public static List<string> Swim(int n, int baseSeed)
        {
            var fails = new List<string>();
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * 6151 + 11);
                int len = r.Next(8, 160);
                var acts = new List<Act>(len);
                for (int i = 0; i < len; i++)
                {
                    int q = r.Next(20);
                    int kind = q < 9 ? 0 : q < 10 ? 1 : q < 11 ? 2 : q < 13 ? 3 : q < 16 ? 4 : q < 18 ? 5 : q < 19 ? 6 : 7;
                    acts.Add(new Act { names = SwimNames, kind = kind, arg = r.Next(1, 100000) });
                }
                Cases++;
                if (RunSwim(seed, acts) == null)
                {
                    var w = MakeSwim(seed);
                    foreach (var a in acts) { StepSwim(w, a); if (a.kind == 0) SwimEvals++; }
                    SwimBreaches += w.breaches; if (w.submerged) SwimSubmerges++;
                    continue;
                }
                var min = Shrink(acts, t => RunSwim(seed, t) != null);
                fails.Add($"swim seed {seed}: {RunSwim(seed, min)} | {string.Join(" ", min)}");
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        /// <summary>SHIP_TOW_LINE_1: what a winch may hook. Property check against an independent restatement of the spec: a
        /// refusal exists exactly when a rule is broken, hostile or standing pawns are never hookable, and every refusal
        /// carries a reason.</summary>
        public static List<string> Winch(int n, int seed)
        {
            var fails = new List<string>();
            var r = new Random(seed);
            for (int i = 0; i < n; i++)
            {
                bool corpse = r.Next(3) == 0, pawn = r.Next(3) == 0, downedAnimal = r.Next(2) == 0, item = r.Next(2) == 0;
                float mass = (float)(r.NextDouble() * 1000), max = (float)(r.NextDouble() * 800), dist = (float)(r.NextDouble() * 60), range = (float)(r.NextDouble() * 40);
                string got = RM_SalvageWinchRules.RefusalFor(corpse, pawn, downedAnimal, item, mass, max, dist, range);
                bool shouldRefuse = (pawn && !downedAnimal) || (!pawn && !corpse && !item) || dist > range || mass > max;
                Cases++; Steps++;
                if ((got != null) != shouldRefuse) { fails.Add($"winch seed {seed} case {i}: refusal={got ?? "null"} but should refuse={shouldRefuse} (corpse {corpse} pawn {pawn} downedAnimal {downedAnimal} item {item} mass {mass} max {max} dist {dist} range {range})"); if (fails.Count > 5) break; }
            }
            Cases++; Steps++;
            if (RM_SalvageWinchRules.RefusalFor(true, false, false, false, 10f, 400f, 5f, 15f) != null || RM_SalvageWinchRules.RefusalFor(false, true, true, false, 100f, 400f, 5f, 15f) != null
                || RM_SalvageWinchRules.RefusalFor(false, true, false, false, 1f, 400f, 1f, 15f) == null || RM_SalvageWinchRules.RefusalFor(false, false, false, true, 401f, 400f, 1f, 15f) == null)
                fails.Add("winch units: corpse and downed beast hookable, standing pawn and overweight item refused");
            return fails;
        }

        /// <summary>VERMIN_EAT_BREEDING_FOOD_1: the litter's take. Property check: never takes more than needed, more than a stack holds,
        /// from an empty or negative stack, and takes nearest-first (a later stack is touched only when every earlier one is emptied).</summary>
        public static List<string> VerminFood(int n, int seed)
        {
            var fails = new List<string>();
            var r = new Random(seed);
            for (int i = 0; i < n; i++)
            {
                int len = r.Next(0, 9);
                var stacks = new List<int>();
                for (int k = 0; k < len; k++) stacks.Add(r.Next(-3, 40));
                int need = r.Next(-2, 60);
                int[] take = RM_VerminFoodMath.Plan(stacks, need);
                Cases++; Steps++;
                int total = RM_VerminFoodMath.Total(take);
                int avail = stacks.Where(x => x > 0).Sum();
                string bad = null;
                if (take.Length != stacks.Count) bad = "length";
                else if (total != Math.Max(0, Math.Min(need, avail))) bad = $"total {total} != min(need {need}, avail {avail})";
                else for (int k = 0; k < take.Length && bad == null; k++)
                {
                    if (take[k] < 0 || take[k] > Math.Max(0, stacks[k])) bad = $"stack {k} take {take[k]} of {stacks[k]}";
                    else if (take[k] > 0 && k + 1 < take.Length && take.Skip(k + 1).Any(x => x > 0) && take[k] < stacks[k]) bad = $"stack {k} not emptied before a later stack was touched";
                }
                if (bad != null) { fails.Add($"vermin-food seed {seed} case {i}: {bad} | stacks [{string.Join(",", stacks)}] need {need}"); if (fails.Count > 5) break; }
            }
            Cases++; Steps++;
            if (RM_VerminFoodMath.Total(RM_VerminFoodMath.Plan(new[] { 2, 5 }, 4)) != 4 || RM_VerminFoodMath.Plan(new[] { 2, 5 }, 4)[0] != 2 || RM_VerminFoodMath.Total(RM_VerminFoodMath.Plan(new[] { 1 }, 3)) != 1
                || RM_VerminFoodMath.Plan(null, 3).Length != 0)
                fails.Add("vermin-food units: nearest stack emptied first, a short pile gives what it has, null is empty");
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
                ("shade", () => Shade(N(4000), S(1))),
                ("bounds", () => Bounds(N(60000), S(1)).Concat(BoundsExtra(N(4000), S(1))).ToList()),
                ("swim", () => Swim(N(4000), S(1))),
                ("patch", () => PatchGraphFuzz.Patch(N(3000), S(1))),
                ("dash", () => PatchGraphFuzz.Dash(N(4000), S(1))),
                ("winch", () => Winch(N(20000), S(1))),
                ("vermin-food", () => VerminFood(N(20000), S(1))),
            };
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"swim branches hit: strike-breach {CovStrike}, melee-breach {CovMelee}, left-sand-breach {CovGroundBreach}, droid-drop {CovDry}, storm-drop {CovStorm}, window-stay {CovWindowStay}, submerge {CovSubmerge}");
            Console.WriteLine($"shade grid compared {CovShadeCmp} times, {CovShadeMoved} with shade on the map");
            Console.WriteLine($"patch graph reached: patches {PatchGraphFuzz.Patches}, rim cells {PatchGraphFuzz.Rims}, edges {PatchGraphFuzz.Edges}, cells at the cap {PatchGraphFuzz.Capped}, ring cells {PatchGraphFuzz.Rings}, flecks {PatchGraphFuzz.Flecks}");
            if (!oneSeed.HasValue && scale >= 1 && only == null && (PatchGraphFuzz.Patches == 0 || PatchGraphFuzz.Edges == 0 || PatchGraphFuzz.Capped == 0 || PatchGraphFuzz.Flecks == 0 || PatchGraphFuzz.Rings == 0)) { Console.WriteLine("FAIL patch fuzz never reached a patch / edge / cap / fleck / ring (blind)"); ok = false; }
            Console.WriteLine($"swim coverage: {SwimEvals} ticks, {SwimSubmerges} sequences ending submerged");
            Console.WriteLine($"moving shade left standing after the setting turned off, until the next forced recompute (known gap, tolerated): {StaleOnToggle}");
            Console.WriteLine($"creaturebehaviors fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
