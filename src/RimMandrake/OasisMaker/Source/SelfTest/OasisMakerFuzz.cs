// Approach B for OasisMaker: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_OasisKernel.cs):
//   score    shade falloff and the site score on random grids against a brute-force oracle; monotone in roofs, casters and rock
//   quality  floors, quality blend, radius cap, speed, the place worker's verdict (exhaustive tables + monotonicity)
//   state    the Dormant / Attuning / Working machine through random validity, master-switch, spawn and lock sequences
//   growth   the whole growth run on a toy terrain map: ring order, rung counts, pacing against closed-form tick counts, what may convert
//   rings    the ring bands partition the square around the centre exactly
//   ladder   the terrain ladders walked rung by rung
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.OasisMaker.SelfTest
{
    internal static class OasisMakerFuzz
    {
        public static long Cases, Steps, Locks, Grows, FullRuns, FarCasterOnly, Interrupted;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("0.#####", System.Globalization.CultureInfo.InvariantCulture); }

        private sealed class Grid : IOasisGrid
        {
            public int w, h; public bool[,] roof, caster, rock;
            public bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < w && z < h; }
            public bool Roofed(int x, int z) { return roof[x, z]; }
            public bool CastsShade(int x, int z) { return caster[x, z]; }
            public bool IsRock(int x, int z) { return rock[x, z]; }
        }

        private static Grid MakeGrid(Random r)
        {
            int w = r.Next(5, 40), h = r.Next(5, 40);
            var g = new Grid { w = w, h = h, roof = new bool[w, h], caster = new bool[w, h], rock = new bool[w, h] };
            double pr = new[] { 0.0, 0.02, 0.1, 0.4 }[r.Next(4)], pc = new[] { 0.0, 0.02, 0.1, 0.4 }[r.Next(4)], pk = new[] { 0.0, 0.1, 0.5, 0.9 }[r.Next(4)];
            for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) { g.roof[x, z] = r.NextDouble() < pr; g.caster[x, z] = r.NextDouble() < pc; g.rock[x, z] = r.NextDouble() < pk; }
            return g;
        }

        // ════════════════════════ score ════════════════════════
        private static double OracleShade(Grid g, int x, int z)
        {
            if (!g.InBounds(x, z)) return 0;
            if (g.roof[x, z]) return 1;
            double best = 0;
            for (int dz = -2; dz <= 2; dz++)
                for (int dx = -2; dx <= 2; dx++)
                {
                    if (dx == 0 && dz == 0) continue;
                    int nx = x + dx, nz = z + dz;
                    if (!g.InBounds(nx, nz) || !g.caster[nx, nz]) continue;
                    best = Math.Max(best, Math.Max(0.0, 1.0 - Math.Sqrt(dx * dx + dz * dz) / 3.0));
                }
            return best;
        }

        private static List<string> Score(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 7919 + 3);
                try
                {
                    var g = MakeGrid(r);
                    int radius = r.Next(4, 13), cx = r.Next(-3, g.w + 3), cz = r.Next(-3, g.h + 3);
                    // shade cell by cell vs the oracle, and the dead-range fact: shaded (>= 0.5) means roofed or 8-adjacent to a caster
                    bool farOnly = false;
                    for (int x = 0; x < g.w; x++)
                        for (int z = 0; z < g.h; z++)
                        {
                            float k = RM_OasisKernel.ShadeAt(g, x, z); double o = OracleShade(g, x, z);
                            Check(Math.Abs(k - o) < 1e-5, "shade at (" + x + "," + z + ") = " + F(k) + ", oracle " + F(o));
                            bool adjacent = false;
                            for (int dz = -1; dz <= 1; dz++) for (int dx = -1; dx <= 1; dx++) if ((dx != 0 || dz != 0) && g.InBounds(x + dx, z + dz) && g.caster[x + dx, z + dz]) adjacent = true;
                            Check((k >= RM_OasisKernel.ShadeThreshold) == (g.roof[x, z] || adjacent), "shaded=" + (k >= 0.5f) + " at (" + x + "," + z + ") but roofed=" + g.roof[x, z] + " adjacent caster=" + adjacent + " (a caster two cells off never reaches the 0.5 threshold)");
                            if (!g.roof[x, z] && !adjacent && k > 0f) farOnly = true;
                        }
                    if (farOnly) FarCasterOnly++;
                    Check(RM_OasisKernel.ShadeAt(g, -1, 0) == 0f && RM_OasisKernel.ShadeAt(g, g.w, 0) == 0f, "out of bounds must score 0");
                    // the site score vs a brute-force count
                    int wantShade = 0, wantRock = 0;
                    for (int dz = -radius; dz <= radius; dz++)
                        for (int dx = -radius; dx <= radius; dx++)
                        {
                            int x = cx + dx, z = cz + dz;
                            if (!g.InBounds(x, z)) continue;
                            if (OracleShade(g, x, z) >= 0.5 - 1e-9) wantShade++;
                            if (g.rock[x, z]) wantRock++;
                        }
                    RM_OasisKernel.ScoreAt(g, cx, cz, radius, out int shade, out int rock);
                    Check(shade == wantShade && rock == wantRock, "score " + shade + "/" + rock + ", oracle " + wantShade + "/" + wantRock + " at (" + cx + "," + cz + ") radius " + radius);
                    int cells = 0; for (int dz = -radius; dz <= radius; dz++) for (int dx = -radius; dx <= radius; dx++) if (g.InBounds(cx + dx, cz + dz)) cells++;
                    Check(shade <= cells && rock <= cells, "score above the in-bounds cell count");
                    RM_OasisKernel.ScoreAt(g, cx, cz, radius + 1, out int shade1, out int rock1);
                    Check(shade1 >= shade && rock1 >= rock, "a larger radius lowered the score");
                    // monotone: a roof, a caster or a rock added anywhere never lowers either score
                    int ax = r.Next(g.w), az = r.Next(g.h), which = r.Next(3);
                    if (which == 0) g.roof[ax, az] = true; else if (which == 1) g.caster[ax, az] = true; else g.rock[ax, az] = true;
                    RM_OasisKernel.ScoreAt(g, cx, cz, radius, out int shade2, out int rock2);
                    Check(shade2 >= shade && rock2 >= rock, "adding a " + new[] { "roof", "caster", "rock" }[which] + " lowered the score");
                }
                catch (Exception e) { fails.Add("score seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ quality ════════════════════════
        private static List<string> Quality(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Steps += 40;
                Check(RM_OasisKernel.MeetsFloor(8, 15, 8, 15) && !RM_OasisKernel.MeetsFloor(7, 15, 8, 15) && !RM_OasisKernel.MeetsFloor(8, 14, 8, 15) && RM_OasisKernel.MeetsFloor(100, 100, 8, 15), "floor is inclusive on both axes");
                Check(RM_OasisKernel.Quality01(8, 15, 8, 30, 15, 45) == 0f && RM_OasisKernel.Quality01(30, 45, 8, 30, 15, 45) == 1f && RM_OasisKernel.Quality01(99, 99, 8, 30, 15, 45) == 1f, "quality is 0 at the floors, 1 at the ceilings and held there");
                Check(Math.Abs(RM_OasisKernel.Quality01(30, 15, 8, 30, 15, 45) - 0.5f) < 1e-6 && Math.Abs(RM_OasisKernel.Quality01(8, 45, 8, 30, 15, 45) - 0.5f) < 1e-6, "one axis cannot buy more than half the quality");
                Check(RM_OasisKernel.InverseLerp(5, 5, 9) == 0f, "InverseLerp with equal ends is 0 (Unity)");
                Check(RM_OasisKernel.RadiusCap(6, 9, 0f) == 6 && RM_OasisKernel.RadiusCap(6, 9, 1f) == 9 && RM_OasisKernel.RadiusCap(6, 9, 0.5f) == 8, "radius cap: 6 poor, 9 excellent, 7.5 rounds half to even (8)");
                Check(RM_OasisKernel.SpeedMultiplier(0f) == 0.5f && RM_OasisKernel.SpeedMultiplier(1f) == 1.5f && RM_OasisKernel.SpeedMultiplier(0.5f) == 1f && RM_OasisKernel.SpeedMultiplier(7f) == 1.5f && RM_OasisKernel.SpeedMultiplier(-7f) == 0.5f, "speed runs 0.5x..1.5x and is held there");
                // the verdict over every combination
                for (int m = 0; m < 16; m++)
                {
                    bool master = (m & 1) != 0; int shade = (m & 2) != 0 ? 8 : 7, rock = (m & 4) != 0 ? 15 : 14; bool dummy = (m & 8) != 0;
                    var got = RM_OasisKernel.Verdict(master, shade, rock, 8, 15);
                    RM_OasisPlacement want = !master ? RM_OasisPlacement.Allowed : (shade >= 8 && rock >= 15) ? RM_OasisPlacement.Allowed : (shade < 8 && rock < 15) ? RM_OasisPlacement.NeedsBoth : shade < 8 ? RM_OasisPlacement.NeedsShade : RM_OasisPlacement.NeedsRock;
                    Check(got == want && !dummy || dummy && got == want, "verdict " + got + " for master " + master + " shade " + shade + " rock " + rock + ", expected " + want);
                    if (!master) Check(got == RM_OasisPlacement.Allowed, "a disabled mechanic blocked a placement");
                }
            }
            catch (Exception e) { fails.Add("quality units: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 131 + 29);
                try
                {
                    int sf = r.Next(1, 60), rf = r.Next(1, 90), se = sf + r.Next(1, 60), re = rf + r.Next(1, 90);
                    int shade = r.Next(0, 200), rock = r.Next(0, 300);
                    float q = RM_OasisKernel.Quality01(shade, rock, sf, se, rf, re);
                    Check(q >= 0f && q <= 1f, "quality " + F(q) + " outside [0,1]");
                    Check(RM_OasisKernel.Quality01(shade + 5, rock, sf, se, rf, re) >= q - 1e-6f && RM_OasisKernel.Quality01(shade, rock + 5, sf, se, rf, re) >= q - 1e-6f, "quality fell as a score rose");
                    Check(Math.Abs(RM_OasisKernel.Quality01(shade, rock, sf, se, rf, re) - (Math.Min(1, Math.Max(0, (shade - sf) / (double)(se - sf))) + Math.Min(1, Math.Max(0, (rock - rf) / (double)(re - rf)))) / 2) < 1e-5, "quality is not the mean of the two clamped ratios");
                    if (shade < sf && rock < rf) Check(q == 0f, "a site below both floors earned quality " + F(q));
                    int minCap = r.Next(3, 9), maxCap = minCap + r.Next(0, 5);
                    int cap = RM_OasisKernel.RadiusCap(minCap, maxCap, q);
                    Check(cap >= minCap && cap <= maxCap, "radius cap " + cap + " outside " + minCap + ".." + maxCap);
                    Check(RM_OasisKernel.RadiusCap(minCap, maxCap, Math.Min(1f, q + 0.1f)) >= cap, "radius cap fell as quality rose");
                    float sp = RM_OasisKernel.SpeedMultiplier(q);
                    Check(sp >= 0.5f - 1e-6f && sp <= 1.5f + 1e-6f && Math.Abs(sp - (0.5 + q)) < 1e-5, "speed " + F(sp) + " for quality " + F(q));
                    var v = RM_OasisKernel.Verdict(true, shade, rock, sf, rf);
                    Check((v == RM_OasisPlacement.Allowed) == RM_OasisKernel.MeetsFloor(shade, rock, sf, rf), "verdict disagrees with the floor test");
                    Check(v != RM_OasisPlacement.NeedsShade || shade < sf && rock >= rf, "NeedsShade while rock also fails");
                    Check(v != RM_OasisPlacement.NeedsRock || rock < rf && shade >= sf, "NeedsRock while shade also fails");
                    Check(v != RM_OasisPlacement.NeedsBoth || shade < sf && rock < rf, "NeedsBoth though one axis passes");
                }
                catch (Exception e) { fails.Add("quality seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ state ════════════════════════
        private static List<string> State(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 977 + 5);
                int step = 0;
                try
                {
                    var st = RM_OasisMakerState.Dormant; int ticksInState = 0; bool locked = false; int ring = 0, cap = r.Next(1, 10);
                    int days = r.Next(1, 4); int N = days * 60000 / 250;
                    bool master = true, spawned = true;
                    int consecutiveValid = 0, lockCalls = 0; bool everWorking = false;
                    int len = 1500 + r.Next(4500);
                    int flip = new[] { 3, 50, 1000, 5000 }[r.Next(4)];          // how often the world changes: from chaos to long calm stretches
                    bool valid = true;
                    for (int t = 0; t < len; t++)
                    {
                        step = t; Steps++;
                        if (r.Next(flip * 3) == 0) master = !master;
                        if (r.Next(flip * 3) == 0) spawned = !spawned;
                        if (r.Next(flip) == 0) valid = !valid;
                        if (r.Next(150) == 0) ring = Math.Min(cap, ring + r.Next(0, 2));
                        var before = st; int validCalls = 0; bool wasLocked = locked;
                        bool grow;
                        RM_OasisKernel.Step(ref st, ref ticksInState, master, spawned, () => { validCalls++; return valid; }, days, 60000, ref locked, () => lockCalls++, ring, cap, out grow);
                        Check(validCalls <= 1, "the (expensive) validity test ran " + validCalls + " times in one tick");
                        if (!master || !spawned)
                        {
                            Check(st == before && !grow && validCalls == 0 && locked == wasLocked, "state moved or scored while the mechanic is off / the building not spawned");
                            continue;
                        }
                        if (!valid && validCalls > 0) { Check(st == RM_OasisMakerState.Dormant && !grow, "an invalid site left state " + st); consecutiveValid = 0; }
                        else if (valid) consecutiveValid++;
                        if (before == RM_OasisMakerState.Dormant && valid) Check(st == RM_OasisMakerState.Attuning && ticksInState == 0, "a valid dormant machine did not start attuning");
                        if (before == RM_OasisMakerState.Dormant && !valid) Check(st == RM_OasisMakerState.Dormant && validCalls == 1, "a dormant machine on an invalid site changed");
                        if (st == RM_OasisMakerState.Working && before == RM_OasisMakerState.Attuning)
                        {
                            everWorking = true;
                            Check(consecutiveValid >= N + 1, "attuning finished after only " + consecutiveValid + " consecutive valid ticks; " + days + " days need " + N + " after the first");
                            Check(locked, "attuning finished without locking the quality");
                        }
                        if (before == RM_OasisMakerState.Attuning && st == RM_OasisMakerState.Attuning) Check(ticksInState < days * 60000 && ticksInState > 0, "attuning counter " + ticksInState + " outside 0.." + days * 60000);
                        if (grow) { Grows++; Check(before == RM_OasisMakerState.Working && st == RM_OasisMakerState.Working && valid && ring < cap, "grow=true outside a valid working machine with rings left"); }
                        if (before == RM_OasisMakerState.Working && st == RM_OasisMakerState.Working && valid && ring < cap) Check(grow, "a valid working machine with rings left did not grow");
                        if (st == RM_OasisMakerState.Working && valid && ring >= cap) Check(!grow, "grew past the radius cap");
                        Check(lockCalls <= 1, "quality was locked " + lockCalls + " times (only the first Attuning->Working may lock)");
                        if (!wasLocked && locked) { Locks++; Check(before == RM_OasisMakerState.Attuning && st == RM_OasisMakerState.Working, "quality locked outside Attuning->Working"); }
                        Check(!wasLocked || locked, "the quality lock was undone");
                    }
                    if (everWorking) Interrupted += valid ? 0 : 1;
                    // an uninterrupted run reaches Working on exactly the (N+1)th valid tick
                    var s2 = RM_OasisMakerState.Dormant; int t2 = 0; bool l2 = false; int lock2 = 0; int reached = -1;
                    for (int t = 1; t <= N + 5; t++)
                    {
                        RM_OasisKernel.Step(ref s2, ref t2, true, true, () => true, days, 60000, ref l2, () => lock2++, 0, cap, out bool g2);
                        if (s2 == RM_OasisMakerState.Working && reached < 0) reached = t;
                    }
                    Check(reached == N + 1, "an uninterrupted machine reached Working on tick " + reached + ", expected " + (N + 1) + " (" + days + " days)");
                    Check(lock2 == 1, "an uninterrupted run locked the quality " + lock2 + " times");
                    // dropping out and returning re-attunes from zero but never re-locks
                    RM_OasisKernel.Step(ref s2, ref t2, true, true, () => false, days, 60000, ref l2, () => lock2++, 0, cap, out bool _);
                    Check(s2 == RM_OasisMakerState.Dormant, "an invalid working machine did not go dormant");
                    for (int t = 0; t < N + 3; t++) RM_OasisKernel.Step(ref s2, ref t2, true, true, () => true, days, 60000, ref l2, () => lock2++, 0, cap, out bool _);
                    Check(s2 == RM_OasisMakerState.Working && lock2 == 1, "a returning machine re-locked its quality (locks " + lock2 + ")");
                }
                catch (Exception e) { fails.Add("state seed " + s + ": step " + step + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ growth ════════════════════════
        private static readonly string[] Terrains = { "Sand", "SoftSand", "Gravel", "Soil", "SoilRich", "Mud", "Marsh", "WaterShallow", "Granite_Rough", "Concrete", "WaterDeep" };

        private static List<string> Growth(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 331 + 9);
                try
                {
                    int cap = r.Next(1, 6);
                    float baseDays = new[] { 0.5f, 1f, 3f, 6f }[r.Next(4)], factor = new[] { 1.05f, 1.5f, 2f }[r.Next(3)];
                    float quality = (float)r.NextDouble(); float speed = RM_OasisKernel.SpeedMultiplier(quality);
                    int radius = cap + 2;
                    var terrain = new Dictionary<(int, int), string>();
                    for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++) terrain[(dx, dz)] = Terrains[r.Next(Terrains.Length)];
                    var initial = new Dictionary<(int, int), string>(terrain);
                    int progress = 0, ring = 0, climbed = 0;
                    var climbsByRing = new int[cap + 2]; int lastRing = 0; var order = new List<int>();
                    long ticks = 0, safety = 0;
                    var ringDoneAt = new Dictionary<int, long>();
                    int rare = RM_OasisKernel.RareTickInterval;
                    while (ring < cap && safety++ < 3000000)
                    {
                        Steps++;
                        ticks += rare;
                        int ringBefore = ring;
                        RM_OasisKernel.AdvanceGrowth(ref progress, ref ring, ref climbed, rare, speed, cap, baseDays, factor, 60000, rr =>
                        {
                            Check(rr >= lastRing, "ring " + rr + " climbed after ring " + lastRing + " (rings must finish in order)");
                            Check(rr == 0 || climbsByRing[rr - 1] == RM_OasisKernel.RungsForRing(rr - 1), "ring " + rr + " climbed before ring " + (rr - 1) + " was complete");
                            lastRing = rr; climbsByRing[rr]++; order.Add(rr);
                            Check(climbsByRing[rr] <= RM_OasisKernel.RungsForRing(rr), "ring " + rr + " climbed more rungs than its ladder has");
                            foreach (var key in terrain.Keys.ToList())
                            {
                                if (!RM_OasisKernel.InRing(rr, key.Item1, key.Item2)) continue;
                                string next = RM_OasisKernel.NextTerrain(rr, terrain[key]);
                                if (next != null) terrain[key] = next;
                            }
                        });
                        for (int rrr = ringBefore; rrr < ring; rrr++) ringDoneAt[rrr] = ticks;
                        Check(progress >= 0, "rung progress went negative");
                    }
                    Check(ring == cap, "growth never finished (ring " + ring + " of " + cap + ") in " + safety + " rare ticks");
                    FullRuns++;
                    // pacing: ring r needs ceil(R * perRung / perTickProgress) rare ticks, no carry across rings
                    long p = (int)(rare * speed), cumulative = 0;
                    for (int rr = 0; rr < cap; rr++)
                    {
                        long per = (int)RM_OasisKernel.PerRungTicks(rr, baseDays, factor, 60000);
                        long need = (RM_OasisKernel.RungsForRing(rr) * per + p - 1) / p;
                        cumulative += need * rare;
                        Check(ringDoneAt[rr] == cumulative, "ring " + rr + " finished at tick " + ringDoneAt[rr] + ", closed form says " + cumulative + " (speed " + F(speed) + ")");
                    }
                    for (int rr = 0; rr < cap; rr++) Check(climbsByRing[rr] == RM_OasisKernel.RungsForRing(rr), "ring " + rr + " climbed " + climbsByRing[rr] + " rungs");
                    // what converted
                    foreach (var kv in terrain)
                    {
                        int d = RM_OasisKernel.Chebyshev(kv.Key.Item1, kv.Key.Item2);
                        string was = initial[kv.Key], now = kv.Value;
                        bool inGrown = d <= cap;
                        if (!inGrown) { Check(now == was, "a cell at distance " + d + " beyond the cap " + cap + " changed " + was + " -> " + now); continue; }
                        int ringOf = d <= 1 ? 0 : d - 1;
                        string term = ringOf == 0 ? "WaterShallow" : "SoilRich";
                        string[] ladder = RM_OasisKernel.LadderForRing(ringOf);
                        string folded = was == "SoftSand" ? "Sand" : was;
                        if (Array.IndexOf(ladder, folded) >= 0) Check(now == term, "cell at distance " + d + " on this ring's ladder (" + was + ") ended " + now + ", not " + term);
                        else Check(now == was, "cell at distance " + d + " off the ladder (" + was + ") converted to " + now + " (only loose natural terrain converts)");
                    }
                }
                catch (Exception e) { fails.Add("growth seed " + s + ": " + e.Message); }
            }
            // extreme settings: durations stay positive and ordered, per-rung time never reaches 0
            Cases++;
            try
            {
                foreach (float b in new[] { 0.5f, 3f, 15f }) foreach (float f in new[] { 1.05f, 1.5f, 3f })
                    {
                        long prev = 0;
                        for (int ringI = 0; ringI < 12; ringI++)
                        {
                            Steps++;
                            long d = RM_OasisKernel.RingDurationTicks(ringI, b, f, 60000), per = RM_OasisKernel.PerRungTicks(ringI, b, f, 60000);
                            Check(d > prev, "ring duration did not grow with the ring index (base " + b + ", factor " + f + ", ring " + ringI + ")");
                            Check(per >= 1 && per * RM_OasisKernel.RungsForRing(ringI) <= d + RM_OasisKernel.RungsForRing(ringI), "per-rung time " + per + " of ring duration " + d);
                            prev = d;
                        }
                        Check(RM_OasisKernel.RingDurationTicks(0, b, f, 60000) == (long)(b * 60000.0), "ring 0 lasts exactly the base ring days");
                    }
                Check(RM_OasisKernel.PerRungTicks(0, 0f, 1.5f, 60000) == 1L, "a zero base time must still advance (per-rung time at least 1)");
            }
            catch (Exception e) { fails.Add("growth extremes: " + e.Message); }
            return fails;
        }

        // ════════════════════════ rings ════════════════════════
        private static List<string> Rings(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                for (int cap = 1; cap <= 12; cap++)
                {
                    Steps++;
                    for (int dx = -14; dx <= 14; dx++)
                        for (int dz = -14; dz <= 14; dz++)
                        {
                            int c = Math.Max(Math.Abs(dx), Math.Abs(dz));
                            int hits = 0, which = -1;
                            for (int ring = 0; ring < cap; ring++) if (RM_OasisKernel.InRing(ring, dx, dz)) { hits++; which = ring; }
                            if (c <= cap) Check(hits == 1, "cell (" + dx + "," + dz + ") at distance " + c + " belongs to " + hits + " of the first " + cap + " rings");
                            else Check(hits == 0, "cell (" + dx + "," + dz + ") at distance " + c + " beyond cap " + cap + " belongs to ring " + which);
                            if (c <= 1) Check(which == 0, "distance " + c + " is the pool zone (ring 0)"); else if (c <= cap) Check(which == c - 1, "distance " + c + " is ring " + (c - 1) + ", got " + which);
                        }
                }
                int lo, hi; RM_OasisKernel.RingBand(0, out lo, out hi); Check(lo == 0 && hi == 1, "pool zone is distance 0..1");
                RM_OasisKernel.RingBand(3, out lo, out hi); Check(lo == 4 && hi == 4, "ring 3 is the band at distance 4");
            }
            catch (Exception e) { fails.Add("rings: " + e.Message); }
            return fails;
        }

        // ════════════════════════ ladder ════════════════════════
        private static List<string> Ladder(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Steps += 30;
                foreach (int ring in new[] { 0, 1, 5 })
                {
                    string[] ladder = RM_OasisKernel.LadderForRing(ring);
                    Check(RM_OasisKernel.RungsForRing(ring) == ladder.Length - 1 && RM_OasisKernel.RungsForRing(ring) == (ring == 0 ? 5 : 3), "rung counts: pool 5, margin 3");
                    foreach (string start in new[] { "Sand", "SoftSand" })
                    {
                        string cur = start; int steps = 0; var seen = new HashSet<string>();
                        while (true)
                        {
                            string next = RM_OasisKernel.NextTerrain(ring, cur);
                            if (next == null) break;
                            Check(seen.Add(next), "ladder revisits " + next);
                            cur = next; steps++;
                            Check(steps <= 10, "ladder never ends");
                        }
                        Check(steps == RM_OasisKernel.RungsForRing(ring) && cur == ladder[ladder.Length - 1], start + " climbed " + steps + " rungs to " + cur + " on ring " + ring);
                    }
                    Check(RM_OasisKernel.NextTerrain(ring, "Granite_Rough") == null && RM_OasisKernel.NextTerrain(ring, "WaterDeep") == null && RM_OasisKernel.NextTerrain(ring, "") == null, "foreign terrain must not convert");
                    Check(RM_OasisKernel.NextTerrain(ring, "sand") == null, "defNames are case-sensitive");
                }
                Check(RM_OasisKernel.NextTerrain(0, "Soil") == "Mud" && RM_OasisKernel.NextTerrain(1, "Soil") == "SoilRich", "Soil climbs to Mud in the pool zone and SoilRich in the margin");
                Check(RM_OasisKernel.NextTerrain(1, "Mud") == null && RM_OasisKernel.NextTerrain(1, "Marsh") == null && RM_OasisKernel.NextTerrain(1, "WaterShallow") == null, "pool terrain is not on the margin ladder");
                Check(RM_OasisKernel.NextTerrain(0, "SoilRich") == null && RM_OasisKernel.NextTerrain(0, "WaterShallow") == null && RM_OasisKernel.NextTerrain(1, "SoilRich") == null, "terminals do not climb");
                Check(RM_OasisKernel.NextTerrain(0, "SoftSand") == "Gravel", "SoftSand is folded onto Sand's rung");
            }
            catch (Exception e) { fails.Add("ladder: " + e.Message); }
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
                ("score", () => Score(N(2000), S(1))),
                ("quality", () => Quality(N(5000), S(1))),
                ("state", () => State(N(1500), S(1))),
                ("growth", () => Growth(N(600), S(1))),
                ("rings", () => Rings(N(1), S(1))),
                ("ladder", () => Ladder(N(1), S(1))),
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
            if (only == null)
            {
                Console.WriteLine($"reached: locks {Locks}, growth ticks {Grows}, full growth runs {FullRuns}, grids where a caster two cells away scores but never reaches the shade threshold {FarCasterOnly}");
                if (!oneSeed.HasValue && scale >= 1 && (Locks == 0 || Grows == 0 || FullRuns == 0 || FarCasterOnly == 0)) { Console.WriteLine("FAIL the fuzz never reached a quality lock, growth, a full run and a far caster (blind)"); ok = false; }
            }
            Console.WriteLine($"oasismaker fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
