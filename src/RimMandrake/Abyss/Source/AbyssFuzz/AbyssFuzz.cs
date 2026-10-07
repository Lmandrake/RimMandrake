// Approach B for the Abyss: seeded random ACTION SEQUENCES over the two Verse-free kernels the mod calls
// (RM_AbyssKernel.cs: Dark math, murk, lamps + krizzak, fold lane, cryptid signs, sunburn, biome score;
//  RM_AbyssStateKernel.cs: gust + gharrek, storm call, soundscape scheduler, hidden-ship cover + probe bookkeeping).
// The model (reference grids, double-precision oracles, event logs) is this file's own; every number under test comes from
// the production kernel. A failing sequence is shrunk by delta debugging and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;

namespace RimMandrake.Abyss.Fuzz
{
    internal static class AbyssFuzz
    {
        public static long Cases, Steps;
        private static readonly List<string> Info = new List<string>();
        private static readonly Dictionary<string, long> Stats = new Dictionary<string, long>();
        private static void Hit(string k) { Stats[k] = (Stats.TryGetValue(k, out long v) ? v : 0) + 1; }

        internal struct Act
        {
            public int kind, a, b, c;
            public string Name;
            public override string ToString() { return Name + "(" + a + "," + b + "," + c + ")"; }
        }

        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("R", CultureInfo.InvariantCulture); }
        private const float Eps = 1e-4f;

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

        private static List<string> RunFamily<W>(string name, int n, int baseSeed, int mult, string[] names, int[] kindWeights, int maxLen,
            Func<int, W> make, Action<W, Act> step, int aMax, int bMax, int cMax)
        {
            var fails = new List<string>();
            int total = kindWeights.Sum();
            Func<int, List<Act>, string> run = (seed, acts) =>
            {
                try { var w = make(seed); foreach (var a in acts) { step(w, a); Steps++; } return null; }
                catch (Exception ex) { return ex.Message; }
            };
            for (int k = 0; k < n; k++)
            {
                int seed = baseSeed + k;
                var r = new Random(seed * mult + 3);
                int len = r.Next(5, maxLen);
                var acts = new List<Act>(len);
                for (int i = 0; i < len; i++)
                {
                    int pick = r.Next(total), kind = 0;
                    while (pick >= kindWeights[kind]) { pick -= kindWeights[kind]; kind++; }
                    acts.Add(new Act { kind = kind, Name = names[kind], a = r.Next(aMax), b = r.Next(bMax), c = r.Next(cMax) });
                }
                Cases++;
                if (run(seed, acts) == null) continue;
                var min = Shrink(acts, t => run(seed, t) != null);
                fails.Add(name + " seed " + seed + ": " + run(seed, min) + " | " + string.Join(" ", min));
                if (fails.Count >= 5) break;
            }
            return fails;
        }

        // ===================================================================== dark: darkness math + murk hysteresis

        private static readonly string[] Weathers = { null, "Clear", RM_DarkKernel.DarkWeather, RM_DarkKernel.StormWeather, RM_DarkKernel.UnveilWeather };
        private static readonly float[] Temps = { -40f, 0f, 7.99f, 8f, 9f, 11f, 13.99f, 14f, 14.01f, 20f, 35f };
        private static readonly float[] Strengths = { 0f, 0.001f, 0.002f, 0.5f, 1f, 2f };
        private static readonly float[] Unit = { 0f, 0.1f, 0.25f, 0.5f, 0.75f, 1f };

        private sealed class DarkWorld
        {
            public string weather = RM_DarkKernel.DarkWeather;
            public float temp = 5f, noise = 0.5f, lane, phantom, strength = 1f, initSev = 0.5f;
            public bool roofed, enabled = true, has;
            public float sev;
        }

        private static void DarkStep(DarkWorld w, Act a)
        {
            switch (a.kind)
            {
                case 1: w.weather = Weathers[a.a % Weathers.Length]; break;
                case 2: w.temp = Temps[a.a % Temps.Length] + (a.b % 7) * 0.31f; break;
                case 3: w.noise = Unit[a.a % Unit.Length]; w.lane = Unit[a.b % Unit.Length]; w.phantom = Unit[a.c % Unit.Length]; break;
                case 4: w.strength = Strengths[a.a % Strengths.Length]; w.enabled = a.b % 4 != 0; break;
                case 5: w.roofed = !w.roofed; break;
                case 0:
                {
                    float dark = RM_DarkKernel.DarknessAt(w.weather, true, w.temp, w.roofed, w.noise, w.lane, w.phantom);
                    Check(dark >= 0f && dark <= 1f && !float.IsNaN(dark), "darkness " + dark + " outside [0,1]");
                    bool present = w.weather == RM_DarkKernel.DarkWeather || w.weather == RM_DarkKernel.StormWeather;
                    if (!present) Check(dark == 0f, "darkness " + dark + " with no Dark in weather " + (w.weather ?? "null"));
                    if (w.weather == RM_DarkKernel.UnveilWeather) Check(RM_DarkKernel.GrainMultiplier(w.weather) == 2f && dark == 0f, "the Unveiling must be clear air with double grain");
                    Check(RM_DarkKernel.DarknessAt(w.weather, false, w.temp, w.roofed, w.noise, w.lane, w.phantom) == 0f, "a cell off the map has darkness");
                    if (w.roofed) Check(RM_DarkKernel.DarknessAt(w.weather, true, w.temp, true, 0f, w.lane, w.phantom) == RM_DarkKernel.DarknessAt(w.weather, true, w.temp, true, 1f, w.lane, w.phantom), "roofed darkness depends on the outdoor noise");
                    Check(RM_DarkKernel.DarknessAt(w.weather, true, w.temp + 1.7f, w.roofed, w.noise, w.lane, w.phantom) <= dark + 1e-6f, "warmer air is darker");
                    Check(dark <= RM_DarkKernel.DarknessAt(w.weather, true, w.temp, w.roofed, w.noise, 0f, 0f) + 1e-6f, "a lane or phantom pocket made the Dark darker");
                    if (w.lane >= 1f || w.phantom >= 1f) Check(dark == 0f, "a fully cleared cell is dark");
                    // murk
                    bool active = w.enabled && w.strength > 0.001f;
                    float target = RM_DarkKernel.MurkTarget(active, dark, w.strength);
                    if (!active) Check(target == 0f, "inactive Dark still has a murk target");
                    var r = RM_DarkKernel.MurkStepFor(w.has, w.sev, target, w.initSev);
                    bool wantHas = target >= 0.03f;
                    Check(r.has == wantHas, "murk present=" + r.has + " for target " + target + " (floor 0.03)");
                    if (!wantHas) { Check(r.removed == w.has && !r.added && !r.set, "wrong removal bookkeeping below the floor"); }
                    else
                    {
                        Check(r.added == !w.has, "added=" + r.added + " but hediff present was " + w.has);
                        float start = w.has ? w.sev : w.initSev;
                        if (Math.Abs(start - target) >= 0.05f) Check(r.set && r.severity == target, "severity " + start + " not moved to target " + target);
                        else Check(!r.set && r.severity == start, "severity moved inside the hysteresis step: " + start + " -> " + r.severity + " target " + target);
                        Check(Math.Abs(r.severity - target) < 0.05f + Eps, "murk severity " + r.severity + " is " + Math.Abs(r.severity - target) + " from target " + target);
                    }
                    if (r.added) Hit("murk.added");
                    if (r.removed) Hit("murk.removed");
                    if (r.set) Hit("murk.set");
                    w.has = r.has; w.sev = r.has ? r.severity : 0f;
                    break;
                }
            }
        }

        // ===================================================================== lamp: Dark shrink + krizzak dimming on shared lamps

        private static readonly float[] Baselines = { 1.5f, 6f, 12f, 20f };
        private const float KMin = 0.25f, KFraction = 0.12f;

        private sealed class LampWorld
        {
            public RM_DarkKernel.Lamp[] lamps = new RM_DarkKernel.Lamp[3];
            public bool[] glows = { true, true, true };
            public float[] dark = new float[3];
            public bool on = true;
            public float strength = 1f;
            public int now = 1000;
        }

        private static LampWorld MakeLamp(int seed)
        {
            var r = new Random(seed * 41 + 9);
            var w = new LampWorld();
            for (int i = 0; i < 3; i++)
            {
                float b = Baselines[r.Next(Baselines.Length)];
                w.lamps[i] = new RM_DarkKernel.Lamp { radius = b, baseline = b };
                w.dark[i] = Unit[r.Next(Unit.Length)];
            }
            return w;
        }

        private static void LampInvariants(LampWorld w)
        {
            for (int i = 0; i < 3; i++)
            {
                var l = w.lamps[i];
                Check(l.radius >= 0f && l.radius <= l.baseline + Eps && !float.IsNaN(l.radius), "lamp " + i + " radius " + l.radius + " outside [0," + l.baseline + "]");
                if (l.kPresent)
                {
                    Check(l.kOriginal <= l.baseline + Eps, "lamp " + i + " krizzak original " + l.kOriginal + " above baseline " + l.baseline);
                    Check(l.radius >= l.kOriginal * KMin - Eps, "lamp " + i + " krizzak dimmed to " + l.radius + " under its floor " + l.kOriginal * KMin);
                }
                if (l.shrunkKnown) Check(Math.Abs(l.shrunkBaseline - l.baseline) < Eps, "lamp " + i + " remembered a baseline that is not its own");
            }
        }

        private static void LampStep(LampWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // the Dark's LampPass over every lamp
                    for (int i = 0; i < 3; i++)
                    {
                        var before = w.lamps[i];
                        bool useDark = w.on && w.glows[i] && !before.kPresent;
                        float darkness = useDark ? w.dark[i] : 0f;
                        bool changed = RM_DarkKernel.DarkLampPass(ref w.lamps[i], w.glows[i], w.on, darkness, w.strength);
                        var after = w.lamps[i];
                        Check(changed == (after.radius != before.radius), "changed=" + changed + " but radius went " + before.radius + " -> " + after.radius);
                        if (before.kPresent) Check(after.radius == before.radius, "the Dark touched a krizzak's lamp (" + before.radius + " -> " + after.radius + ")");
                        if (!w.on && !before.kPresent && before.shrunkKnown && before.radius < before.shrunkBaseline - 0.01f)
                        {
                            Check(after.radius == before.shrunkBaseline && !after.shrunkKnown, "a shrunk lamp was not restored with the Dark off (or kept a stale memory): " + before.radius + " -> " + after.radius + " known=" + after.shrunkKnown);
                            Hit("lamp.restored");
                        }
                        if (changed && after.radius < before.radius) Hit("lamp.shrunk");
                        if (w.on && w.glows[i] && !before.kPresent)
                        {
                            float f = 1f - 0.7f * Math.Min(1f, Math.Max(0f, darkness * w.strength));
                            float target = before.baseline * f;
                            Check(Math.Abs(after.radius - target) < 0.15f + Eps || after.radius == target, "lit lamp radius " + after.radius + " is not within slack of its target " + target);
                            Check(after.radius >= before.baseline * 0.3f - 0.15f - Eps, "the Dark pushed a lamp under 30% of its radius (less the slack): " + after.radius + "/" + before.baseline);
                        }
                        // idempotent at the same inputs
                        var again = w.lamps[i];
                        bool changed2 = RM_DarkKernel.DarkLampPass(ref again, w.glows[i], w.on, darkness, w.strength);
                        Check(!changed2 && again.radius == after.radius, "a second Dark pass at the same inputs changed lamp " + i);
                    }
                    break;
                case 1: // a krizzak feeds lamp a%3 (CompKrizzak skips a lamp already at its floor and one that is out)
                {
                    int i = a.a % 3;
                    if (!w.glows[i]) break;
                    if (RM_DarkKernel.KrizzakAtFloor(w.lamps[i], KMin)) break;
                    float before = w.lamps[i].radius;
                    bool shrank = RM_DarkKernel.KrizzakFeed(ref w.lamps[i], w.now, KFraction, KMin);
                    Check(shrank == (w.lamps[i].radius < before), "feed shrank=" + shrank + " but radius " + before + " -> " + w.lamps[i].radius);
                    Check(w.lamps[i].kPresent && w.lamps[i].kLastFed == w.now, "a feed did not record its tick");
                    if (shrank) Hit("lamp.fed");
                    break;
                }
                case 2: // recovery pass (every 250 ticks) after some quiet time
                    w.now += 250 * (1 + a.a % 12);
                    for (int i = 0; i < 3; i++)
                    {
                        var before = w.lamps[i];
                        RM_DarkKernel.KrizzakRecover(ref w.lamps[i], w.now);
                        var after = w.lamps[i];
                        if (before.kPresent && w.now - before.kLastFed < 600) Check(after.radius == before.radius && after.kPresent, "a lamp recovered before the idle period");
                        if (before.kPresent) Check(after.radius >= before.radius - Eps || after.radius == before.kOriginal, "recovery shrank a lamp: " + before.radius + " -> " + after.radius);
                        if (before.kPresent && !after.kPresent) Hit("lamp.recovered");
                        if (before.kPresent && !after.kPresent) Check(after.radius >= before.kOriginal - 0.01f - Eps, "an entry was spent while the lamp was still dim: " + after.radius + " vs " + before.kOriginal);
                    }
                    break;
                case 3: w.now += 60 * (1 + a.a % 20); break;
                case 4:
                    switch (a.a % 4)
                    {
                        case 0: w.on = !w.on; break;
                        case 1: w.dark[a.b % 3] = Unit[a.c % Unit.Length]; break;
                        case 2: w.glows[a.b % 3] = !w.glows[a.b % 3]; break;
                        default: w.strength = Strengths[a.b % Strengths.Length]; break;
                    }
                    break;
            }
            LampInvariants(w);
        }

        // ===================================================================== lane: fold-lamp lanes on a walled grid

        private static readonly int[][] FacingStep = { new[] { 0, 1 }, new[] { 1, 0 }, new[] { 0, -1 }, new[] { -1, 0 } };   // Rot4 north east south west

        private sealed class LaneWorld
        {
            public int W, H;
            public bool[] wall;
            public List<int[]> lamps = new List<int[]>();       // x, z, rot
            public RM_DarkKernel.ClearGrid grid;
        }

        private static LaneWorld MakeLane(int seed)
        {
            var r = new Random(seed * 53 + 1);
            var w = new LaneWorld { W = r.Next(8, 36), H = r.Next(8, 36) };
            w.wall = new bool[w.W * w.H];
            for (int i = 0; i < w.wall.Length; i++) w.wall[i] = r.Next(12) == 0;
            w.grid = new RM_DarkKernel.ClearGrid(w.W * w.H);
            return w;
        }

        private static float[] LaneReference(LaneWorld w)
        {
            var refGrid = new float[w.W * w.H];
            Func<int, int, bool> blocked = (x, z) => x < 0 || z < 0 || x >= w.W || z >= w.H || w.wall[x + z * w.W];
            foreach (int[] lamp in w.lamps)
            {
                int[] f = FacingStep[lamp[2]], s = FacingStep[(lamp[2] + 1) % 4];
                refGrid[lamp[0] + lamp[1] * w.W] = Math.Max(refGrid[lamp[0] + lamp[1] * w.W], 1f);
                for (int l = -2; l <= 2; l++)
                    for (int d = 1; d <= 14; d++)
                    {
                        if (Math.Abs(l) > HalfWidthRef(d)) continue;
                        // valid iff every shape cell of this column up to d is open
                        bool open = true;
                        for (int d2 = 1; d2 <= d; d2++)
                        {
                            if (Math.Abs(l) > HalfWidthRef(d2)) continue;
                            if (blocked(lamp[0] + f[0] * d2 + s[0] * l, lamp[1] + f[1] * d2 + s[1] * l)) { open = false; break; }
                        }
                        if (!open) break;
                        int x = lamp[0] + f[0] * d + s[0] * l, z = lamp[1] + f[1] * d + s[1] * l;
                        float v = d <= 10 ? 1f : 1f - (d - 10) / 5f;
                        refGrid[x + z * w.W] = Math.Max(refGrid[x + z * w.W], v);
                    }
            }
            return refGrid;
        }

        private static int HalfWidthRef(int d) { return d <= 2 ? 1 : (d <= 9 ? 2 : 1); }

        private static void LaneStep(LaneWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: w.lamps.Add(new[] { a.a % w.W, a.b % w.H, a.c % 4 }); if (w.lamps.Count > 4) w.lamps.RemoveAt(0); break;
                case 1: w.wall[(a.a % w.W) + (a.b % w.H) * w.W] = !w.wall[(a.a % w.W) + (a.b % w.H) * w.W]; break;
                case 2: if (w.lamps.Count > 0) w.lamps.RemoveAt(a.a % w.lamps.Count); break;
                case 3: // Rebuild
                {
                    w.grid.Reset();
                    Check(w.grid.clear.All(v => v == 0f) && w.grid.touched.Count == 0, "Reset left a nonzero cell or a touched entry");
                    foreach (int[] lamp in w.lamps)
                    {
                        int[] f = FacingStep[lamp[2]], s = FacingStep[(lamp[2] + 1) % 4];
                        RM_DarkKernel.LayLane(lamp[0], lamp[1], f[0], f[1], s[0], s[1],
                            (x, z) => x < 0 || z < 0 || x >= w.W || z >= w.H || w.wall[x + z * w.W],
                            (x, z, v) => { if (x >= 0 && z >= 0 && x < w.W && z < w.H) w.grid.Mark(x + z * w.W, v); });
                    }
                    float[] want = LaneReference(w);
                    foreach (float wv in want) if (wv > 0f) Hit("lane.cells");
                    if (w.lamps.Count > 0 && Enumerable.Range(0, want.Length).Any(i => w.wall[i])) Hit("lane.walled");
                    for (int i = 0; i < want.Length; i++)
                        Check(Math.Abs(w.grid.clear[i] - want[i]) < 1e-6f, "cell (" + i % w.W + "," + i / w.W + ") clearance " + w.grid.clear[i] + ", reference " + want[i]);
                    Check(w.grid.touched.Distinct().Count() == w.grid.touched.Count, "a cell was touched twice");
                    Check(new HashSet<int>(w.grid.touched).SetEquals(Enumerable.Range(0, want.Length).Where(i => want[i] > 0f)), "touched list differs from the nonzero cells");
                    foreach (int i in w.grid.touched)
                    {
                        Check(w.grid.clear[i] > 0f && w.grid.clear[i] <= 1f, "clearance " + w.grid.clear[i] + " out of (0,1]");
                        if (w.wall[i] && !w.lamps.Any(l => l[0] + l[1] * w.W == i)) Check(false, "a wall cell was cleared");
                    }
                    break;
                }
            }
        }

        // ===================================================================== cryptid: ring cells, exchange payout, phantom pockets

        private static readonly float[] Bmv = { 32f, 1.2f, 1.9f };
        private static readonly int[] Stacks = { 50, 75, 75 };
        private static readonly bool[] Full = { false, false, true };

        private sealed class CryptidWorld
        {
            public int W, H;
            public List<int[]> cairns = new List<int[]>();
        }

        private static CryptidWorld MakeCryptid(int seed)
        {
            var r = new Random(seed * 59 + 2);
            return new CryptidWorld { W = r.Next(5, 22), H = r.Next(5, 22) };
        }

        private static void CryptidStep(CryptidWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: w.cairns.Add(new[] { a.a % w.W, a.b % w.H }); break;
                case 1: if (w.cairns.Count > 0) w.cairns.RemoveAt(a.a % w.cairns.Count); break;
                case 2: // ring cells vs a brute-force Euclid count
                {
                    HashSet<int> got = RM_DarkKernel.CircleCells(w.cairns, w.W, w.H);
                    for (int x = 0; x < w.W; x++)
                        for (int z = 0; z < w.H; z++)
                        {
                            int n = 0;
                            foreach (int[] c in w.cairns) if (Math.Sqrt((c[0] - x) * (c[0] - x) + (c[1] - z) * (c[1] - z)) <= 2.9) n++;
                            Check(got.Contains(x + z * w.W) == (n >= 3), "cell (" + x + "," + z + ") has " + n + " cairns in range, in ring set = " + got.Contains(x + z * w.W));
                        }
                    Check(got.All(k => k >= 0 && k < w.W * w.H), "ring set holds an off-map key");
                    if (got.Count > 0) Hit("cryptid.rings");
                    break;
                }
                case 3: // exchange payout
                {
                    float mv = new float[] { 0f, 0.5f, 3f, 32f, 120f, 900f, 7000f, 1e6f }[a.a % 8];
                    int stack = new[] { 1, 1, 3, 75, 500 }[a.b % 5];
                    float roll = (a.c % 101) / 100f;
                    float v = RM_DarkKernel.ExchangeValue(mv, stack, roll);
                    float baseV = Math.Max(5f, mv * stack);
                    Check(v >= baseV * 0.8f - 1e-3f && v <= baseV * 1.3f + 1e-3f, "exchange value " + v + " outside 0.8..1.3 of " + baseV);
                    var counts = new int[3];
                    float left = RM_DarkKernel.ExchangeGoods(v, Bmv, Stacks, Full, counts);
                    double paid = 0;
                    for (int i = 0; i < 3; i++)
                    {
                        Check(counts[i] >= 0 && counts[i] <= Stacks[i], "goods " + i + " count " + counts[i] + " beyond its stack " + Stacks[i]);
                        paid += counts[i] * Bmv[i];
                    }
                    Check(paid <= v + 1e-3, "paid " + F(paid) + " for a value of " + F(v));
                    Check(Math.Abs((v - paid) - left) < 1e-2 + 1e-5 * v, "returned remainder " + left + " != value - paid " + F(v - paid));
                    Check(left >= -1e-3f, "negative remainder " + left);
                    // all the value is spent unless the steel stack (the last, uncapped-share rung) ran out
                    Check(left < Bmv[2] || counts[2] == Stacks[2], "value " + v + " left " + left + " unspent with steel not at its stack cap");
                    Hit("cryptid.exchange"); if (counts[2] == Stacks[2]) Hit("cryptid.exchange.capped");
                    if (v < Bmv[0]) Check(counts[0] == 0, "a component was paid for a value under its price");
                    break;
                }
                case 4: // phantom clearance profile
                {
                    float radius = 2.5f + (a.a % 16) / 10f;
                    float d1 = (a.b % 100) / 20f, d2 = d1 + (a.c % 50) / 25f;
                    float c1 = RM_DarkKernel.PhantomClearance(d1, radius), c2 = RM_DarkKernel.PhantomClearance(d2, radius);
                    Check(c1 >= 0f && c1 <= 1f && c2 >= 0f && c2 <= 1f, "phantom clearance outside [0,1]");
                    Check(c2 <= c1 + 1e-6f, "phantom clearance rose with distance: " + c1 + " at " + d1 + ", " + c2 + " at " + d2);
                    Check(RM_DarkKernel.PhantomClearance(0f, radius) == 1f, "phantom centre is not fully clear");
                    Check(RM_DarkKernel.PhantomClearance(radius, radius) == 0f && RM_DarkKernel.PhantomClearance(radius + 1f, radius) == 0f, "phantom reaches past its radius");
                    Check(RM_DarkKernel.PhantomClearance(radius * 0.999f, radius) < 0.01f, "phantom edge is not soft");
                    break;
                }
            }
        }

        // ===================================================================== cover: hidden-ship cover + probe scheduling

        private sealed class CoverWorld
        {
            public CoverState s = CoverState.Fresh();
            public int now = 250 * 7;
            public bool applies = true, hasEngine = true, probes = true, probeAlive;
            public int lamps;
            public int probeSpawn, seen;
            public Random rng;
            public double oracleCover;
            public int coveredSince = -1;            // start of the current continuous cover, -1 = not covered
            public int lastSpawn = -1;
            public double seenProb = 0.2;
        }

        private static CoverWorld MakeCover(int seed)
        {
            var w = new CoverWorld { rng = new Random(seed * 71 + 5) };
            w.lamps = new[] { 0, 2, 4, 3 }[w.rng.Next(4)];
            return w;
        }

        private static void CoverTick(CoverWorld w)
        {
            w.now += 250;
            // the probe's own per-tick work (it runs before the Interval gate): leave after a day, scan every 60 ticks
            if (w.probeAlive)
            {
                if (RM_CoverKernel.ProbeLeaves(w.now, w.probeSpawn)) { w.probeAlive = false; w.seen = 0; }
                else
                    for (int k = 0; k < 4 && w.probeAlive; k++)
                    {
                        bool seen = w.rng.NextDouble() < w.seenProb;
                        int before = w.seen;
                        w.seen = RM_CoverKernel.ProbeSeen(w.seen, seen);
                        Check(w.seen == (seen ? before + 60 : Math.Max(0, before - 60)), "seen counter " + before + " -> " + w.seen);
                        if (RM_CoverKernel.ProbeReports(w.seen))
                        {
                            Check(w.seen >= 600, "report below the threshold");
                            RM_CoverKernel.Collapse(ref w.s, true, w.now);
                            Check(w.s.cover == 0f && w.s.cooldownUntil == w.now + 3 * 60000, "a report did not collapse the cover into a cooldown");
                            w.oracleCover = 0; w.coveredSince = -1; w.probeAlive = false; w.seen = 0;
                            Hit("cover.report");
                        }
                    }
            }
            var before2 = w.s;
            int lit = w.lamps;
            CoverEvent ev = RM_CoverKernel.Step(ref w.s, w.now, w.applies, w.applies && w.hasEngine, lit, w.probes, w.probeAlive, (lo, hi) => lo + w.rng.Next(hi - lo));
            bool run = w.applies && w.hasEngine;
            if (!run)
            {
                Check(w.s.cover == 0f && w.s.coveredTicks == 0 && w.s.nextProbeTick == -1, "cover survived the engine leaving or the option being off");
                Check(w.s.cooldownUntil == before2.cooldownUntil, "the cooldown changed on a non-cooldown collapse");
                Check(ev == CoverEvent.None, "an event fired with no engine");
                w.oracleCover = 0; w.coveredSince = -1;
                return;
            }
            if (before2.cooldownUntil > w.now)
            {
                Check(w.s.cover == before2.cover && w.s.coveredTicks == before2.coveredTicks && ev == CoverEvent.None, "cover moved during the cooldown");
                Check(w.s.cover == 0f, "cover stood at " + w.s.cover + " during a cooldown");
                return;
            }
            bool quiet = lit <= 4;
            if (ev == CoverEvent.Lapsed)
            {
                Check(before2.coveredTicks + 250 >= RM_CoverKernel.MaxCoveredTicks, "cover lapsed after only " + (before2.coveredTicks + 250) + " covered ticks");
                Check(w.s.cover == 0f && w.s.coveredTicks == 0 && w.s.cooldownUntil == w.now + 3 * 60000, "a lapse did not zero the cover and arm a 3 day cooldown");
                Check(w.coveredSince >= 0 && w.now - w.coveredSince >= 14 * 60000, "a lapse after only " + (w.now - w.coveredSince) + " ticks of cover (design: ~15 days)");
                w.oracleCover = 0; w.coveredSince = -1;
                Hit("cover.lapse");
                return;
            }
            if (quiet && w.oracleCover < 1.0) w.oracleCover = Math.Min(1.0, w.oracleCover + 250.0 / (6.0 * 60000));
            else if (!quiet) w.oracleCover = Math.Max(0.0, w.oracleCover - 2.0 * 250.0 / (6.0 * 60000));
            Check(Math.Abs(w.s.cover - w.oracleCover) < 2e-5, "cover " + w.s.cover + " drifted from the reference " + F(w.oracleCover));
            w.oracleCover = w.s.cover;      // re-sync so float noise cannot accumulate over thousands of intervals
            bool covered = w.s.cover >= 0.6f;
            if (covered) Hit("cover.covered");
            if (covered && w.coveredSince < 0) w.coveredSince = w.now;
            if (!covered) { w.coveredSince = -1; Check(w.s.coveredTicks == 0 && w.s.nextProbeTick == -1, "leaving cover did not clear the covered clock and probe schedule"); }
            if (ev == CoverEvent.SpawnProbe)
            {
                Check(covered && w.probes && !w.probeAlive, "a probe was due while uncovered / disabled / one already out");
                Check(before2.nextProbeTick >= 0 && w.now >= before2.nextProbeTick, "a probe spawned before its scheduled tick");
                Check(w.now - w.coveredSince >= 3 * 60000 - 250, "a probe arrived " + (w.now - w.coveredSince) + " ticks into cover (design: not before 3 days)");
                if (w.lastSpawn >= 0 && w.coveredSince <= w.lastSpawn) Check(w.now - w.lastSpawn >= 3 * 60000, "two probes " + (w.now - w.lastSpawn) + " ticks apart in one cover");
                Check(w.s.nextProbeTick >= w.now + 3 * 60000 && w.s.nextProbeTick < w.now + 6 * 60000, "the next probe is scheduled " + (w.s.nextProbeTick - w.now) + " ticks out (design 3..6 days)");
                w.probeAlive = true; w.probeSpawn = w.now; w.seen = 0; w.lastSpawn = w.now;
                Hit("cover.probe");
            }
            Check(w.s.cover >= 0f && w.s.cover <= 1f, "cover " + w.s.cover + " outside [0,1]");
            Check(w.s.coveredTicks < RM_CoverKernel.MaxCoveredTicks, "covered clock reached its cap without a lapse");
        }

        private static void CoverStep(CoverWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: for (int i = 0, n = 1 + a.a % 20; i < n; i++) CoverTick(w); break;
                case 5: for (int i = 0, n = 50 + a.a * 4; i < n; i++) CoverTick(w); break;      // a long quiet or noisy stretch
                case 1: w.seenProb = new[] { 0.0, 0.2, 0.5, 0.9 }[a.a % 4]; break;               // what the probe's eyes find
                case 2: w.probeAlive = false; w.seen = 0; break;                                  // shot down
                case 3: w.lamps = new[] { 0, 2, 4, 4, 5, 6, 12 }[a.a % 7]; break;
                case 4:
                    switch (a.a % 6)
                    {
                        case 0: w.applies = !w.applies; break;
                        case 1: w.hasEngine = !w.hasEngine; break;
                        case 2: w.probes = !w.probes; break;
                        default: w.applies = true; w.hasEngine = true; break;                     // the common case: engine on the map
                    }
                    break;
                case 6: // save + load
                {
                    var copy = w.s;
                    w.s = new CoverState { cover = float.Parse(copy.cover.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture), coveredTicks = copy.coveredTicks, cooldownUntil = copy.cooldownUntil, nextProbeTick = copy.nextProbeTick };
                    Check(w.s.cover == copy.cover, "cover did not survive a text round trip");
                    break;
                }
            }
        }

        // ===================================================================== gust: wind excursions, forced gusts, gharrek feeding

        private sealed class GustWorld
        {
            public GustState s = GustState.Fresh();
            public int now = 5000;
            public Random rng;
            public double oracleAvg = -1;
            public float minSpeed = float.MaxValue, maxSpeed;
            public int gustStart = -1;               // observed start of the gust in progress
            public bool inGust;
            public int[] lastFed = { -1, -1, -1 };
            public int[] fedTimes = new int[3];
            public HashSet<int>[] fedCounts = { new HashSet<int>(), new HashSet<int>(), new HashSet<int>() };
            public bool feeders = true;
        }

        private static GustWorld MakeGust(int seed) { return new GustWorld { rng = new Random(seed * 83 + 7), now = 5000 + (seed % 7) * 10 }; }

        private static float Wind(GustWorld w, int mode)
        {
            switch (mode)
            {
                case 0: return 0.3f + (float)w.rng.NextDouble() * 0.05f;                 // calm
                case 1: return 0.3f + (float)w.rng.NextDouble() * 1.5f;                  // noisy
                case 2: return 1.2f + (float)w.rng.NextDouble() * 0.6f;                  // strong
                default: return (float)w.rng.NextDouble() * 0.2f;                         // near still
            }
        }

        private static void GustStep(GustWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // a burst of samples every 10 ticks
                {
                    int n = 1 + a.a % 90, mode = a.b % 4;
                    for (int i = 0; i < n; i++)
                    {
                        bool wasGust = w.inGust;                          // the gust state at the previous tick
                        w.now += 10;
                        float speed = Wind(w, a.c % 5 == 0 ? (i % 4) : mode);
                        int countBefore = w.s.count, endBefore = w.s.endTick;
                        if (w.oracleAvg < 0) w.oracleAvg = speed;
                        w.oracleAvg += (speed - w.oracleAvg) * 0.01;
                        w.minSpeed = Math.Min(w.minSpeed, speed); w.maxSpeed = Math.Max(w.maxSpeed, speed);
                        RM_GustKernel.Sample(ref w.s, w.now, speed);
                        Check(Math.Abs(w.s.average - w.oracleAvg) < 1e-3, "average " + w.s.average + " drifted from the reference " + F(w.oracleAvg));
                        Check(w.s.average >= w.minSpeed - 1e-4f && w.s.average <= w.maxSpeed + 1e-4f, "average " + w.s.average + " outside the speeds seen");
                        bool nowGust = RM_GustKernel.IsGust(w.s, w.now);
                        if (w.s.count != countBefore)
                        {
                            Check(w.s.count == countBefore + 1, "the gust count jumped " + countBefore + " -> " + w.s.count);
                            Check(endBefore <= w.now && w.s.startTick == w.now && nowGust, "a gust opened while one was running, or its start tick is wrong");
                            Check(w.now - endBefore >= 600, "a gust opened " + (w.now - endBefore) + " ticks after the last one (cooldown 600)");
                            Check(speed >= Math.Max(0.05, w.oracleAvg) * 1.3 - 1e-3, "a gust opened at speed " + speed + " vs average " + F(w.oracleAvg) + " (needs 1.3x)");
                            w.gustStart = w.now;
                            Hit("gust.natural");
                        }
                        if (wasGust && !nowGust)
                        {
                            int dur = w.now - w.gustStart;
                            Check(dur >= 120, "a gust ended after only " + dur + " ticks (min 120)");
                            Check(dur <= 900, "a gust lasted " + dur + " ticks (max 900)");
                            w.gustStart = -1;
                        }
                        if (nowGust) Check(w.gustStart >= 0 && w.now - w.gustStart <= 900, "a gust is still running " + (w.now - w.gustStart) + " ticks in");
                        w.inGust = nowGust;
                        GharrekAll(w);
                    }
                    break;
                }
                case 1: // ForceGust(ticks)
                {
                    int ticks = new[] { 0, 60, 120, 300, 900, 5000 }[a.a % 6];
                    bool was = RM_GustKernel.IsGust(w.s, w.now);
                    int countBefore = w.s.count, endBefore = w.s.endTick;
                    RM_GustKernel.Force(ref w.s, w.now, ticks);
                    Check(w.s.endTick >= endBefore, "a forced gust shortened the one in progress");
                    Check(RM_GustKernel.IsGust(w.s, w.now), "a forced gust is not a gust");
                    Check(w.s.endTick >= w.now + 120, "a forced gust shorter than the 120 minimum");
                    Hit("gust.forced");
                    if (!was) { Check(w.s.count == countBefore + 1 && w.s.startTick == w.now, "a forced gust from calm did not count as a new gust"); w.gustStart = w.now; }
                    else Check(w.s.count == countBefore, "a forced gust inside a gust counted twice");
                    w.inGust = true;
                    GharrekAll(w);
                    break;
                }
                case 2: // a gill ticks
                    GharrekAll(w); break;
                case 3: // save + load of the controller and the gills
                {
                    var c = w.s;
                    w.s = new GustState { average = float.Parse(c.average.ToString("R", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture), startTick = c.startTick, endTick = c.endTick, count = c.count };
                    Check(w.s.average == c.average, "average did not survive a text round trip");
                    break;
                }
                case 4: w.feeders = !w.feeders; GharrekAll(w); break;
            }
        }

        private static void GharrekAll(GustWorld w)
        {
            bool gust = RM_GustKernel.IsGust(w.s, w.now);
            for (int g = 0; g < 3; g++)
            {
                int lastBefore = w.lastFed[g];
                bool open, dormant;
                float fed = RM_GustKernel.GharrekStep(w.feeders, gust, w.s.count, 0.12f, ref w.lastFed[g], out dormant, out open);
                if (!w.feeders) { Check(!dormant && open && fed == 0f && w.lastFed[g] == lastBefore, "gills with the option off must be open, awake, and not fed"); continue; }
                Check(dormant == !gust && open == gust, "gill dormant=" + dormant + " open=" + open + " in gust=" + gust);
                if (gust && w.s.count != lastBefore) Check(fed == 0.12f && w.lastFed[g] == w.s.count, "a gill missed its feed for gust #" + w.s.count);
                else Check(fed == 0f, "a gill was fed twice for gust #" + w.s.count);
                if (fed > 0f) { Check(w.fedCounts[g].Add(w.s.count), "gill " + g + " fed twice for gust #" + w.s.count); w.fedTimes[g]++; Hit("gust.fed"); }
            }
        }

        // ===================================================================== storm: rumble -> flash -> maybe a summ

        private sealed class StormWorld
        {
            public StormState s = StormState.Fresh();
            public int now = 1000;
            public bool storm = true, enabled = true;
            public float strength = 1f;
            public Random rng;
            public int lastRumble = -1, lastFlash = -1;
        }

        private static void StormStepFn(StormWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0: // tick with a gap
                {
                    w.now += new[] { 1, 1, 1, 7, 60, 250, 2500, 9000 }[a.a % 8];
                    var before = w.s;
                    float chanceArg = -1f;
                    StormOut o = RM_StormKernel.Step(ref w.s, w.now, w.storm, w.enabled, w.strength,
                        (lo, hi) => lo + w.rng.Next(hi - lo + 1), p => { chanceArg = p; return w.rng.NextDouble() < p; });
                    if (!w.storm || !w.enabled)
                    {
                        Check(!o.rumble && !o.flash && !o.summ, "storm events fired out of a storm / with the option off");
                        Check(w.s.nextRumbleTick == -1 && w.s.pendingFlashTick == -1 && !w.s.pendingSumm, "the storm schedule survived the storm ending");
                        w.lastRumble = -1; w.lastFlash = -1;
                        break;
                    }
                    Check(!(o.rumble && o.flash), "a rumble and a flash in one step");
                    if (o.flash)
                    {
                        Check(before.pendingFlashTick >= 0 && w.now >= before.pendingFlashTick, "a flash fired before it was due");
                        Check(w.lastRumble >= 0 && w.now - w.lastRumble >= 180, "a flash " + (w.now - w.lastRumble) + " ticks after the rumble (min 180)");
                        Check(w.s.pendingFlashTick == -1 && !w.s.pendingSumm, "a flash left a pending flash or summ");
                        Check(o.summ == before.pendingSumm, "summ=" + o.summ + " but pendingSumm was " + before.pendingSumm);
                        w.lastFlash = w.now;
                        Hit("storm.flash"); if (o.summ) Hit("storm.summ");
                    }
                    else Check(!o.summ, "a summ came without a flash");
                    if (o.rumble)
                    {
                        Check(before.pendingFlashTick < 0 && w.now >= before.nextRumbleTick, "a rumble fired early or over a pending flash");
                        Check(w.s.pendingFlashTick >= w.now + 180 && w.s.pendingFlashTick <= w.now + 300, "flash scheduled " + (w.s.pendingFlashTick - w.now) + " ticks after the rumble (180..300)");
                        Check(w.s.nextRumbleTick >= w.now + 3000 && w.s.nextRumbleTick <= w.now + 9000, "next rumble scheduled " + (w.s.nextRumbleTick - w.now) + " ticks out (3000..9000)");
                        Check(chanceArg >= 0f && chanceArg <= 1f && chanceArg <= 0.2f * w.strength + 1e-6f, "summ chance " + chanceArg + " for strength " + w.strength);
                        if (w.strength <= 0f) Check(!w.s.pendingSumm, "a summ was queued with the Dark at strength 0");
                        if (w.lastRumble >= 0) Check(w.now - w.lastRumble >= 3000, "two rumbles " + (w.now - w.lastRumble) + " ticks apart in one storm");
                        w.lastRumble = w.now;
                        Hit("storm.rumble");
                    }
                    else Check(chanceArg < 0f, "the summ chance was rolled with no rumble");
                    if (w.s.pendingFlashTick < 0) Check(!w.s.pendingSumm, "a summ is pending with no flash scheduled");
                    break;
                }
                case 1: w.storm = !w.storm; break;
                case 2: w.enabled = !w.enabled; break;
                case 3: w.strength = Strengths[a.a % Strengths.Length]; break;
                case 4: // save + load
                {
                    var c = w.s;
                    w.s = new StormState { nextRumbleTick = c.nextRumbleTick, pendingFlashTick = c.pendingFlashTick, pendingSumm = c.pendingSumm };
                    break;
                }
            }
        }

        // ===================================================================== sound: which sounds are due

        private sealed class SoundWorld
        {
            public SoundState s = SoundState.Fresh();
            public int now = 60, gust = 0;
            public bool hasGust = true;
            public float mult = 1f, etch = 1f;
            public Random rng;
            public int impacts, rustles, lastImpact = -1, lastGrain = -1, grainScheduledAt = -1;
        }

        private static void SoundStepFn(SoundWorld w, Act a)
        {
            switch (a.kind)
            {
                case 0:
                {
                    w.now += new[] { 1, 1, 1, 5, 20, 60, 300 }[a.a % 7];
                    var before = w.s;
                    int gustArg = w.hasGust ? w.gust : -2;
                    SoundOut o = RM_SoundKernel.Step(ref w.s, w.now, gustArg, w.mult, w.etch, (lo, hi) => lo + w.rng.Next(hi - lo + 1));
                    if (!w.hasGust) Check(!o.impact, "an impact with no gust controller");
                    bool wantImpact = w.hasGust && before.lastGustCount >= 0 && w.gust != before.lastGustCount;
                    Check(o.impact == wantImpact, "impact=" + o.impact + " for gust count " + w.gust + " vs last seen " + before.lastGustCount);
                    if (w.hasGust && before.lastGustCount < 0) Check(!o.impact && w.s.lastGustCount == w.gust, "the first sight of the gust counter must be silent");
                    if (o.impact) { Hit("sound.impact"); w.impacts++; w.lastImpact = w.now; Check(w.s.pendingRustleTick >= w.now + 45 && w.s.pendingRustleTick <= w.now + 90, "rustle scheduled " + (w.s.pendingRustleTick - w.now) + " ticks after the impact (45..90)"); }
                    if (o.rustle)
                    {
                        w.rustles++; Hit("sound.rustle");
                        Check(w.lastImpact >= 0 && w.now - w.lastImpact >= 45, "a rustle with no impact 45+ ticks back");
                        Check(w.s.pendingRustleTick == -1, "a rustle left itself pending");
                    }
                    if (o.grain)
                    {
                        Hit("sound.grain");
                        Check(w.now % 60 == 0, "a grain tick off the 60 tick beat");
                        Check(w.mult > 0f && w.etch > 0.001f, "grain with no grain falling / etchfall off");
                        Check(before.nextGrainTick >= 0 && w.now >= before.nextGrainTick, "grain fired before it was due");
                        int gap = w.s.nextGrainTick - w.now;
                        Check(gap >= (int)Math.Round(240 / w.mult) && gap <= (int)Math.Round(900 / w.mult), "next grain " + gap + " ticks out with multiplier " + w.mult);
                    }
                    if ((w.mult <= 0f || w.etch <= 0.001f) && w.now % 60 == 0) Check(w.s.nextGrainTick == -1, "grain schedule survived etchfall/grain going quiet");
                    break;
                }
                case 1: w.gust += 1 + a.a % 2; break;
                case 2: w.mult = new[] { 0f, 1f, 2f }[a.a % 3]; w.etch = Strengths[a.b % Strengths.Length]; break;
                case 3: w.hasGust = !w.hasGust; break;
            }
        }

        // ===================================================================== units

        public static List<string> Units(int n, int baseSeed)
        {
            var fails = new List<string>();
            Action<string> bad = m => { if (fails.Count < 8) fails.Add("units: " + m); };
            var r = new Random(baseSeed);

            // --- the temperature curve: opaque <= 8, clear >= 14, half at 11, symmetric, monotone
            Cases++;
            {
                if (RM_DarkKernel.DarknessForTemperature(8f) != 1f || RM_DarkKernel.DarknessForTemperature(-30f) != 1f) bad("the Dark is not opaque at or below 8 C");
                if (RM_DarkKernel.DarknessForTemperature(14f) != 0f || RM_DarkKernel.DarknessForTemperature(40f) != 0f) bad("the Dark is not clear at or above 14 C");
                if (Math.Abs(RM_DarkKernel.DarknessForTemperature(11f) - 0.5f) > 1e-6f) bad("the Dark is not half at 11 C");
                if (Math.Abs(RM_DarkKernel.DarknessForTemperature(9.5f) - 0.84375f) > 1e-5f || Math.Abs(RM_DarkKernel.DarknessForTemperature(12.5f) - 0.15625f) > 1e-5f) bad("the Dark does not thin along a smoothstep (9.5 C should be 0.84375, 12.5 C 0.15625)");
                float prev = 1f;
                for (double t = -5; t <= 25; t += 0.01)
                {
                    Steps++;
                    float d = RM_DarkKernel.DarknessForTemperature((float)t);
                    if (d > prev + 1e-6f) bad("darkness rose from " + prev + " to " + d + " at " + t + " C");
                    if (Math.Abs(d + RM_DarkKernel.DarknessForTemperature((float)(22 - t)) - 1f) > 1e-5f && t > 4 && t < 18) bad("the curve is not symmetric about 11 C at " + t);
                    prev = d;
                }
                string[] ws = { null, "Clear", "RM_AbyssDark", "RM_AbyssWitchfire", "RM_AbyssUnveiling" };
                float[] grain = { 0, 0, 1, 1, 2 };
                for (int i = 0; i < ws.Length; i++) if (RM_DarkKernel.GrainMultiplier(ws[i]) != grain[i]) bad("grain multiplier for " + (ws[i] ?? "null"));
                if (RM_DarkKernel.EtchTries(1f, 1f) != 24 || RM_DarkKernel.EtchTries(0f, 1f) != 0 || RM_DarkKernel.EtchTries(0.01f, 1f) != 1 || RM_DarkKernel.EtchTries(1f, 2f) != 48 || RM_DarkKernel.EtchTries(3f, 2f) != 144) bad("etch tries table");
            }

            // --- summ sunburn: climbs to the cap in sun, cools out of it, never negative-removal early
            Cases++;
            for (int k = 0; k < 40; k++)
            {
                float burn = 0.04f, cool = 0.06f, max = 1f;
                bool has = false; float sev = 0f;
                int rare = 0;
                for (int i = 0; i < 400; i++)
                {
                    Steps++;
                    bool sun = (i / (5 + k)) % 2 == 0;
                    bool h2; float s2;
                    RM_DarkKernel.SunStep(has, sev, sun, burn, cool, max, out h2, out s2);
                    if (sun && !h2) bad("a summ in sun has no burn");
                    if (sun && s2 > max + 1e-6f) bad("burn " + s2 + " over the cap");
                    if (!sun && has && h2 && s2 > sev - cool + 1e-6f) bad("cooling did not cool");
                    if (!sun && has && !h2 && s2 > 0.001f) bad("the burn was removed at severity " + s2);
                    if (!sun && !has && h2) bad("a burn appeared out of sun");
                    has = h2; sev = Math.Max(0f, Math.Min(max, s2)); rare++;
                    if (!has) sev = 0f;
                }
            }

            // --- the lane profile
            Cases++;
            {
                int[] hw = { 1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1 };
                for (int d = 1; d <= 14; d++) { Steps++; if (RM_DarkKernel.LaneHalfWidth(d) != hw[d - 1]) bad("lane half width at " + d); }
                if (RM_DarkKernel.LaneValue(10) != 1f || Math.Abs(RM_DarkKernel.LaneValue(14) - 0.2f) > 1e-6f) bad("lane fade ends");
                float pv = 1f;
                for (int d = 1; d <= 14; d++) { float v = RM_DarkKernel.LaneValue(d); if (v > pv || v <= 0f) bad("lane value not a positive non-increasing fade at " + d); pv = v; }
            }

            // --- exchange: saturation, and the payout table with the shipped numbers (info)
            Cases++;
            {
                var counts = new int[3];
                float left = RM_DarkKernel.ExchangeGoods(3.0e38f, Bmv, Stacks, Full, counts);
                if (counts[0] != 50 || counts[1] != 75 || counts[2] != 75) bad("a huge value did not fill every stack: " + string.Join(",", counts));
                left = RM_DarkKernel.ExchangeGoods(float.NaN, Bmv, Stacks, Full, counts);
                if (counts.Any(c => c < 0)) bad("a NaN value paid a negative stack");
                var sb = new List<string>();
                foreach (float v in new[] { 50f, 100f, 500f, 1000f, 5000f })
                {
                    RM_DarkKernel.ExchangeGoods(v, Bmv, Stacks, Full, counts);
                    double paid = counts[0] * 32.0 + counts[1] * 1.2 + counts[2] * 1.9;
                    sb.Add(v + ":" + (100 * paid / v).ToString("F0") + "%");
                }
                Info.Add("exchange payout as a share of the value taken (component 32 x50, tholin 1.2 x75, steel 1.9 x75): " + string.Join("  ", sb));
            }

            // --- biome score
            Cases++;
            {
                var rg = new RM_DarkKernel.BiomeRanges { tempMin = -20f, tempMax = 15f, rainMin = 0f, rainMax = 700f, elevMin = 300f, elevMax = 3500f, baseScore = 34f, degreeWeight = 0.3f, rainfallDivisor = 200f, spawnChance = 0.02f };
                Func<float, bool> always = g => true, never = g => false;
                Steps += 12;
                if (RM_DarkKernel.BiomeScore(true, false, true, 1f, 0f, 100f, 1000f, rg, always) != -100f) bad("a null tile scored");
                if (RM_DarkKernel.BiomeScore(false, true, true, 1f, 0f, 100f, 1000f, rg, always) != -100f) bad("a water tile scored");
                if (RM_DarkKernel.BiomeScore(false, false, true, 0f, 0f, 100f, 1000f, rg, always) != -100f) bad("rarity 0 still scored");
                if (RM_DarkKernel.BiomeScore(false, false, false, 1f, 0f, 100f, 1000f, rg, always) != 0f) bad("flat ground scored");
                if (RM_DarkKernel.BiomeScore(false, false, true, 1f, 0f, 100f, 1000f, rg, never) != 0f) bad("a failed seeded gate scored");
                if (RM_DarkKernel.BiomeScore(false, false, true, 1f, 16f, 100f, 1000f, rg, always) != 0f) bad("too warm scored");
                if (RM_DarkKernel.BiomeScore(false, false, true, 1f, 0f, 700f, 1000f, rg, always) != 0f) bad("rainfall at the exclusive max scored");
                if (RM_DarkKernel.BiomeScore(false, false, true, 1f, 15f, 0f, 3500f, rg, always) < 34f) bad("the warm edge of the biome scored under the base score");
                bool gateSeen = false;
                RM_DarkKernel.BiomeScore(false, false, true, 8f, 0f, 100f, 1000f, rg, g => { gateSeen = true; return true; });
                if (!gateSeen) bad("rarity 8 x chance 0.02 should still be gated (0.16)");
                gateSeen = false;
                RM_DarkKernel.BiomeScore(false, false, true, 60f, 0f, 100f, 1000f, rg, g => { gateSeen = true; return false; });
                if (gateSeen) bad("a gate of 1.2 must not roll");
                for (int k = 0; k < Math.Max(1, n / 50); k++)
                {
                    float t = (float)(r.NextDouble() * 35 - 20), rain = (float)(r.NextDouble() * 700), el = (float)(300 + r.NextDouble() * 3200);
                    float s1 = RM_DarkKernel.BiomeScore(false, false, true, 1f, t, rain, el, rg, always), s2 = RM_DarkKernel.BiomeScore(false, false, true, 1f, Math.Min(15f, t + 2f), rain, el, rg, always);
                    float s3 = RM_DarkKernel.BiomeScore(false, false, true, 1f, t, Math.Min(699f, rain + 20f), el, rg, always);
                    Steps++;
                    if (s2 > s1 + 1e-4f) bad("a warmer tile scored higher: " + s1 + " -> " + s2);
                    if (s3 < s1 - 1e-4f) bad("a wetter tile scored lower: " + s1 + " -> " + s3);
                    if (s1 < 34f) bad("an eligible tile scored " + s1 + " under the base");
                }
                var rz = rg; rz.rainfallDivisor = 0f;
                if (float.IsInfinity(RM_DarkKernel.BiomeScore(false, false, true, 1f, 0f, 100f, 1000f, rz, always))) bad("a zero rainfall divisor divided by zero");
            }

            // --- a forced gust: at least 120 ticks, not `ticks`; in calm wind it is cut at 120, in a hard wind at the 900 cap
            Cases++;
            foreach (var cs in new[] { new { name = "calm", speed = 0.3f, wantLen = 120 }, new { name = "hard", speed = 3.0f, wantLen = 900 } })
            {
                var g = GustState.Fresh();
                int now = 1000;
                for (int i = 0; i < 100; i++) { RM_GustKernel.Sample(ref g, now, cs.name == "calm" ? 0.3f : 0.3f); now += 10; }   // settle the average at 0.3
                RM_GustKernel.Force(ref g, now, 5000);
                int start = now, len = -1;
                for (int i = 0; i < 200 && len < 0; i++)
                {
                    now += 10; Steps++;
                    RM_GustKernel.Sample(ref g, now, cs.speed);
                    if (!RM_GustKernel.IsGust(g, now)) len = now - start;
                }
                if (len != cs.wantLen) bad("ForceGust(5000) in " + cs.name + " wind lasted " + len + " ticks, expected " + cs.wantLen);
            }

            // --- the cover timeline (design numbers from the file header)
            Cases++;
            {
                Steps += 4;
                if (Math.Abs(1.0 / RM_CoverKernel.Rate - 1440.0) > 0.01) bad("full cover should take 1440 quiet intervals (6 days), got " + 1.0 / RM_CoverKernel.Rate);
                int toThreshold = (int)Math.Ceiling(0.6 / RM_CoverKernel.Rate);
                if (toThreshold * 250 < 3 * 60000 || toThreshold * 250 > 4 * 60000) bad("cover arrives after " + toThreshold * 250 + " ticks; design: slowly, 3-4 days");
                if (RM_CoverKernel.MaxCoveredTicks != 15 * 60000 || RM_CoverKernel.CooldownTicks != 3 * 60000) bad("cover cap / cooldown constants moved");
                if (RM_CoverKernel.IsCovered(false, 1f) || !RM_CoverKernel.IsCovered(true, 0.6f) || RM_CoverKernel.IsCovered(true, 0.59f)) bad("IsCovered boundary");
            }
            return fails;
        }

        // ===================================================================== driver

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("dark", () => RunFamily("dark", N(2500), S(1), 7919, new[] { "Murk", "Weather", "Temp", "Cell", "Strength", "Roof" }, new[] { 14, 2, 4, 3, 2, 1 }, 150, seed => new DarkWorld { initSev = new[] { 0f, 0.5f, 1f }[seed % 3] }, DarkStep, 100, 100, 100)),
                ("lamp", () => RunFamily("lamp", N(3000), S(1), 104729, new[] { "DarkPass", "Feed", "Recover", "Time", "Setting" }, new[] { 6, 5, 4, 2, 3 }, 160, MakeLamp, LampStep, 100, 100, 100)),
                ("lane", () => RunFamily("lane", N(1500), S(1), 6007, new[] { "AddLamp", "Wall", "DropLamp", "Rebuild" }, new[] { 3, 3, 1, 6 }, 70, MakeLane, LaneStep, 60, 60, 60)),
                ("cryptid", () => RunFamily("cryptid", N(2000), S(1), 30011, new[] { "AddCairn", "DropCairn", "Rings", "Exchange", "Phantom" }, new[] { 6, 1, 4, 6, 3 }, 60, MakeCryptid, CryptidStep, 800, 800, 800)),
                ("cover", () => RunFamily("cover", N(3000), S(1), 15485863, new[] { "Tick", "ProbeEyes", "ProbeGone", "Lamps", "Setting", "LongIdle", "Reload" }, new[] { 8, 2, 1, 2, 2, 7, 1 }, 60, MakeCover, CoverStep, 400, 10, 10)),
                ("gust", () => RunFamily("gust", N(2500), S(1), 32452843, new[] { "Samples", "Force", "GillTick", "Reload", "Feeders" }, new[] { 8, 2, 3, 1, 1 }, 120, MakeGust, GustStep, 1000, 10, 10)),
                ("storm", () => RunFamily("storm", N(3000), S(1), 49979687, new[] { "Tick", "Storm", "Enabled", "Strength", "Reload" }, new[] { 20, 2, 1, 1, 1 }, 200, seed => new StormWorld { rng = new Random(seed * 11 + 1) }, StormStepFn, 100, 10, 10)),
                ("sound", () => RunFamily("sound", N(3000), S(1), 67867967, new[] { "Tick", "NewGust", "Grain", "Controller" }, new[] { 20, 3, 2, 1 }, 200, seed => new SoundWorld { rng = new Random(seed * 13 + 1) }, SoundStepFn, 100, 10, 10)),
                ("units", () => Units(N(1000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine("fuzz " + f.name + ": " + (Cases - c0) + " cases, " + (Steps - s0) + " steps, " + t.Elapsed.TotalSeconds.ToString("F2") + "s, " + (fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES"));
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            foreach (string i in Info.Distinct()) Console.WriteLine("info " + i);
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                // a fuzz whose interesting events never happened proved nothing: every one of these must have fired
                string[] mustSee = { "murk.added", "murk.removed", "murk.set", "lamp.shrunk", "lamp.restored", "lamp.fed", "lamp.recovered", "lane.cells", "lane.walled", "cryptid.rings",
                    "cryptid.exchange", "cryptid.exchange.capped", "cover.covered", "cover.lapse", "cover.probe", "cover.report", "gust.natural", "gust.forced", "gust.fed",
                    "storm.rumble", "storm.flash", "storm.summ", "sound.impact", "sound.rustle", "sound.grain" };
                var missing = mustSee.Where(k => !Stats.ContainsKey(k)).ToList();
                Console.WriteLine("coverage: " + string.Join(" ", mustSee.Select(k => k + "=" + (Stats.TryGetValue(k, out long v) ? v : 0))));
                if (missing.Count > 0) { Console.WriteLine("FAIL the fuzz never reached: " + string.Join(", ", missing)); ok = false; }
            }
            Console.WriteLine("abyss fuzz: " + Cases + " cases, " + Steps + " steps, " + sw.Elapsed.TotalSeconds.ToString("F2") + "s total -> " + (ok ? "OK" : "FAILED"));
            return ok;
        }
    }
}
