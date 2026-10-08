// Approach B for NightsideIce: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_NightsideIceKernel.cs):
//   dial      the heat dial maths (raw -> target -> eased dial) and the hourly tick offsets, against double-precision restatements
//   source    the hottest-heater pick against an argmax oracle, and the 250-tick source cache through a toggling world
//   breach    the hourly roll (chance, gate, cooldown) incl. a long-run simulation of how often a crack really opens, the shivven count, the countdown
//   crack     a crack's 60-tick look: the 6 h and 1 h warnings once each, the break on time, silent when untaught or muted, through jumps and reloads
//   edge      the base-edge distance band and the path leg index
//   icepath   the shivven's ice-only breadth-first path on random grids against an independent search
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.NightsideIce.SelfTest
{
    internal static class NightsideIceFuzz
    {
        public static long Cases, Steps, PathsOnIce, PathsOffIce, PathsHull, PathsLimited, EmptyPaths, Breaches, WarnBoth, Refreshes, StaleKeeps;
        public static double MeanIntervalHours, PredictedIntervalHours;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static string F(double v) { return v.ToString("0.#####", System.Globalization.CultureInfo.InvariantCulture); }

        // ════════════════════════ dial ════════════════════════
        private static List<string> Dial(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 7919 + 3);
                try
                {
                    // build a raw from parts exactly as Measure does
                    float heaters = 0f, fires = 0f, power = 0f, rooms = 0f;
                    double oracleRaw = 0;
                    int nh = r.Next(0, 6);
                    for (int i = 0; i < nh; i++) { float h = r.Next(1, 300); heaters += h; oracleRaw += h; }
                    int nf = r.Next(0, 4);
                    for (int i = 0; i < nf; i++) { float size = (float)r.NextDouble() * 1.5f; float add = RM_NightsideIceKernel.FireHeat(size); Check(Math.Abs(add - size * 20.0) < 1e-4, "fire heat " + F(add) + " != 20 x size " + F(size)); fires += add; oracleRaw += size * 20.0; }
                    int np = r.Next(0, 5);
                    for (int i = 0; i < np; i++) { float watts = -r.Next(10, 2000); float add = RM_NightsideIceKernel.PowerHeat(watts); Check(add > 0f && Math.Abs(add - (-watts) * 0.01) < 1e-4, "power heat " + F(add) + " for output " + watts); power += add; oracleRaw += -watts * 0.01; }
                    int nr = r.Next(0, 5);
                    for (int i = 0; i < nr; i++)
                    {
                        float outdoor = r.Next(-150, 0), room = outdoor + r.Next(-20, 60); int cells = r.Next(1, 120);
                        float add = RM_NightsideIceKernel.RoomHeat(room, outdoor, cells);
                        double want = room > outdoor ? (room - outdoor) * cells * 0.002 : 0.0;
                        Check(add >= 0f && Math.Abs(add - want) < 1e-3, "room heat " + F(add) + ", want " + F(want) + " (room " + room + ", outdoor " + outdoor + ", cells " + cells + ")");
                        rooms += add; oracleRaw += want;
                    }
                    float raw = heaters + fires + power + rooms;
                    Check(Math.Abs(raw - oracleRaw) < 1e-2 + oracleRaw * 1e-5, "raw " + F(raw) + " != the sum of its parts " + F(oracleRaw));
                    float scale = new[] { 0f, 0.5f, 1f, 25f, 150f, 600f }[r.Next(6)];
                    float t = RM_NightsideIceKernel.Target(raw, scale);
                    double wantT = 1.0 - Math.Exp(-raw / Math.Max(1.0, scale));
                    Check(Math.Abs(t - wantT) < 1e-5, "target " + F(t) + " != " + F(wantT) + " (raw " + F(raw) + ", scale " + scale + ")");
                    Check(t >= 0f && t < 1.0000001f, "target " + F(t) + " outside [0,1)");
                    Check(raw > 0f ? t > 0f : t == 0f, "target zero iff raw is zero: raw " + F(raw) + " target " + F(t));
                    Check(RM_NightsideIceKernel.Target(raw + 5f, scale) >= t, "target fell as raw rose");
                    Check(RM_NightsideIceKernel.Target(raw, scale + 50f) <= t + 1e-7f, "target rose as the scale rose (a bigger scale is a duller dial)");
                    Check(Math.Abs(RM_NightsideIceKernel.Target(scale < 1f ? 1f : scale, scale) - 0.63212) < 1e-4, "a raw of one scale must read about 63%");
                    Check(RM_NightsideIceKernel.Target(10f, 0f) == RM_NightsideIceKernel.Target(10f, 1f) && RM_NightsideIceKernel.Target(10f, -5f) == RM_NightsideIceKernel.Target(10f, 1f), "a scale under 1 must be held at 1");
                    // easing
                    float dial = (float)r.NextDouble();
                    float e = RM_NightsideIceKernel.Ease(dial, t);
                    Check(Math.Abs(e - (dial + (t - dial) * 0.5)) < 1e-5, "ease " + F(e) + " is not halfway from " + F(dial) + " to " + F(t));
                    Check(e >= Math.Min(dial, t) - 1e-6 && e <= Math.Max(dial, t) + 1e-6, "ease overshot");
                    Check(Math.Abs(e - t) <= Math.Abs(dial - t) * 0.5 + 1e-6, "ease did not halve the gap");
                    float d2 = dial; for (int k = 0; k < 40; k++) d2 = RM_NightsideIceKernel.Ease(d2, t);
                    Check(Math.Abs(d2 - t) < 1e-4, "forty hours of easing did not reach the target");
                    Check(RM_NightsideIceKernel.Ease(5f, 5f) == 1f && RM_NightsideIceKernel.Ease(-3f, -3f) == 0f, "ease must hold the dial in 0..1");
                    // tick offsets: one hit per hour, breach five ticks after the dial
                    int start = r.Next(0, 1000000), dialHits = 0, breachHits = 0;
                    for (int tick = start; tick < start + RM_NightsideIceKernel.IntervalTicks * 4; tick++)
                    {
                        bool dd = RM_NightsideIceKernel.DialDue(tick), bb = RM_NightsideIceKernel.BreachDue(tick);
                        if (dd) dialHits++;
                        if (bb) breachHits++;
                        Check(!(dd && bb), "dial and breach due on the same tick " + tick);
                        if (dd) Check(RM_NightsideIceKernel.BreachDue(tick + 5) && !RM_NightsideIceKernel.BreachDue(tick + 4), "the breach look is not exactly 5 ticks after the dial update");
                    }
                    Check(dialHits == 4 && breachHits == 4, "expected 4 dial and 4 breach looks in four hours, got " + dialHits + "/" + breachHits);
                }
                catch (Exception e) { fails.Add("dial seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ source ════════════════════════
        private static List<string> Source(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 131 + 29);
                try
                {
                    int count = r.Next(0, 9);
                    var heat = new List<float>(); var working = new List<bool>();
                    for (int i = 0; i < count; i++) { heat.Add(r.Next(4) == 0 ? 0f : r.Next(1, 6) * 50f); working.Add(r.Next(3) != 0); }
                    Func<int> oracle = () =>
                    {
                        int best = -1;
                        for (int i = 0; i < heat.Count; i++) if (working[i] && heat[i] > 0f && (best < 0 || heat[i] > heat[best])) best = i;
                        return best;
                    };
                    Steps++;
                    Check(RM_NightsideIceKernel.HottestIndex(heat, working) == oracle(), "hottest index " + RM_NightsideIceKernel.HottestIndex(heat, working) + ", argmax says " + oracle());
                    // the cache, through a world where heaters switch on and off
                    int now = 1000, readTick = -99999, cached = -1; bool hasRead = false;
                    int pickedAtRead = -1;
                    for (int step = 0; step < 60; step++)
                    {
                        Steps++;
                        now += r.Next(1, 200);
                        if (count > 0 && r.Next(3) == 0) { int k = r.Next(count); working[k] = !working[k]; }
                        if (count > 0 && r.Next(10) == 0) { int k = r.Next(count); heat[k] = r.Next(0, 6) * 50f; }
                        bool cachedWorking = cached >= 0 && working[cached] && heat[cached] > 0f;
                        if (RM_NightsideIceKernel.SourceCacheValid(now, readTick, cached >= 0, cachedWorking))
                        {
                            if (hasRead) StaleKeeps++;
                            Check(now - readTick < 250, "a cache older than 250 ticks was served");
                            Check(cached < 0 || cachedWorking, "a dead heater was served from the cache");
                            Check(cached == pickedAtRead, "the cache served something other than its last read");
                        }
                        else
                        {
                            readTick = now; hasRead = true; Refreshes++;
                            cached = RM_NightsideIceKernel.HottestIndex(heat, working);
                            pickedAtRead = cached;
                            Check(cached == oracle(), "a refresh picked " + cached + ", argmax says " + oracle());
                            Check(cached < 0 || (working[cached] && heat[cached] > 0f), "a refresh picked a heater that is not working");
                        }
                    }
                    // exact boundaries of the cache window
                    Check(RM_NightsideIceKernel.SourceCacheValid(1249, 1000, false, false) && !RM_NightsideIceKernel.SourceCacheValid(1250, 1000, false, false), "cache window is exactly 250 ticks");
                    Check(!RM_NightsideIceKernel.SourceCacheValid(1100, 1000, true, false) && RM_NightsideIceKernel.SourceCacheValid(1100, 1000, true, true), "a dead cached heater must force a re-read inside the window");
                }
                catch (Exception e) { fails.Add("source seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ breach ════════════════════════
        private static List<string> Breach(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Steps++;
                Check(RM_NightsideIceKernel.BreachChance(1f, 1f) == 1f / 24f, "a full dial at scale 1 is 1/24 an hour");
                Check(Math.Abs(RM_NightsideIceKernel.BreachChance(1f, 0.5f) - 1.0 / 96.0) < 1e-7, "half a dial is a quarter of that (1/96)");
                Check(RM_NightsideIceKernel.BreachChance(1f, 0f) == 0f && RM_NightsideIceKernel.BreachChance(0f, 1f) == 0f, "a zero dial or scale never breaches");
                Check(RM_NightsideIceKernel.BreachChance(1000f, 1f) == 1f, "chance is held at 1");
                Check(RM_NightsideIceKernel.BreachThreshold == 0.15f && RM_NightsideIceKernel.CooldownTicks == 120000, "breach threshold 0.15 and a two-day cooldown (PROVISIONAL tuning, pinned)");
                // shivven count table
                int[] want = { 2, 2, 3, 4, 4, 5, 6, 6, 7, 8 };
                float[] at = { 0f, 0.05f, 0.2f, 0.3f, 0.45f, 0.6f, 0.75f, 0.8f, 0.9f, 1f };
                int[] expect = { 2, 2, 3, 4, 5, 6, 6, 7, 7, 8 };
                _ = want;
                for (int i = 0; i < at.Length; i++) Check(RM_NightsideIceKernel.ShivvenCount(at[i]) == expect[i], "shivven count at dial " + at[i] + " is " + RM_NightsideIceKernel.ShivvenCount(at[i]) + ", expected " + expect[i]);
                Check(RM_NightsideIceKernel.ShivvenCount(0.25f) == 4 && RM_NightsideIceKernel.ShivvenCount(0.75f) == 6, "half-to-even at the .5 boundaries (1.5 -> 2, 4.5 -> 4)");
                Check(RM_NightsideIceKernel.ShivvenCount(7f) == 8 && RM_NightsideIceKernel.ShivvenCount(-2f) == 2, "the dial is held in 0..1 before it is scaled");
                Check(RM_NightsideIceKernel.BreakHours(true, 24, 0) == 24 && RM_NightsideIceKernel.BreakHours(true, 0, 0) == 1 && RM_NightsideIceKernel.BreakHours(true, -5, 0) == 1, "the taught countdown is the setting, at least 1 hour");
                Check(RM_NightsideIceKernel.BreakHours(false, 24, 11) == 11, "later cracks use the roll");
                // the roll gate over every combination
                for (int m = 0; m < 16; m++)
                {
                    bool applies = (m & 1) != 0, open = (m & 2) != 0; int now = (m & 4) != 0 ? 5000 : 1000; float dial = (m & 8) != 0 ? 0.15f : 0.1499f;
                    bool got = RM_NightsideIceKernel.BreachRollMade(applies, open, now, 5000, dial);
                    bool wantG = applies && !open && now >= 5000 && dial >= 0.15f;
                    Steps++;
                    Check(got == wantG, "BreachRollMade(applies " + applies + ", open " + open + ", now " + now + ", dial " + dial + ") = " + got);
                }
            }
            catch (Exception e) { fails.Add("breach units: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 977 + 5);
                try
                {
                    float d1 = (float)r.NextDouble(), d2 = Math.Min(1f, d1 + (float)r.NextDouble() * 0.3f); float sc1 = 0.1f + (float)r.NextDouble() * 3.9f, sc2 = sc1 + (float)r.NextDouble();
                    Check(RM_NightsideIceKernel.BreachChance(sc1, d2) >= RM_NightsideIceKernel.BreachChance(sc1, d1), "chance fell as the dial rose");
                    Check(RM_NightsideIceKernel.BreachChance(sc2, d1) >= RM_NightsideIceKernel.BreachChance(sc1, d1), "chance fell as the frequency scale rose");
                    Check(RM_NightsideIceKernel.ShivvenCount(d2) >= RM_NightsideIceKernel.ShivvenCount(d1) && RM_NightsideIceKernel.ShivvenCount(d1) >= 2 && RM_NightsideIceKernel.ShivvenCount(d2) <= 8, "shivven count not monotone in 2..8");
                    float c = RM_NightsideIceKernel.BreachChance(sc1, d1);
                    Check(c >= 0f && c <= 1f && (c == 1f || Math.Abs(c - sc1 * d1 * d1 / 24.0) < 1e-6), "chance " + F(c) + " is not scale x dial^2 / 24");
                }
                catch (Exception e) { fails.Add("breach seed " + s + ": " + e.Message); }
            }
            // long-run: how often does a crack really open? one roll per hour once the cooldown has passed, a crack blocks rolls while open
            Cases++;
            try
            {
                var r = new Random(seed0 * 31 + 7);
                float dial = 1f, scale = 1f;
                float p = RM_NightsideIceKernel.BreachChance(scale, dial);
                int now = 0, cooldownUntil = -1, openUntil = -1, lastOpen = -1; long sumInterval = 0, intervals = 0;
                int hours = 400000;
                for (int h = 0; h < hours; h++)
                {
                    now = h * RM_NightsideIceKernel.TicksPerHour + RM_NightsideIceKernel.BreachTickOffset;
                    Steps++;
                    bool crackOpen = now < openUntil;
                    if (!RM_NightsideIceKernel.BreachRollMade(true, crackOpen, now, cooldownUntil, dial)) continue;
                    if (r.NextDouble() < p)
                    {
                        Breaches++;
                        bool teach = lastOpen < 0;
                        int bh = RM_NightsideIceKernel.BreakHours(teach, 24, teach ? 0 : r.Next(8, 17));
                        openUntil = now + bh * RM_NightsideIceKernel.TicksPerHour;
                        cooldownUntil = now + RM_NightsideIceKernel.CooldownTicks;
                        if (lastOpen >= 0) { sumInterval += now - lastOpen; intervals++; }
                        lastOpen = now;
                    }
                }
                MeanIntervalHours = sumInterval / (double)Math.Max(1, intervals) / RM_NightsideIceKernel.TicksPerHour;
                PredictedIntervalHours = RM_NightsideIceKernel.CooldownTicks / (double)RM_NightsideIceKernel.TicksPerHour + (1.0 / p - 1.0);
                Check(intervals > 1000, "the long run opened only " + intervals + " cracks");
                Check(Math.Abs(MeanIntervalHours - PredictedIntervalHours) < PredictedIntervalHours * 0.03, "at a full dial a crack opens every " + F(MeanIntervalHours) + " h on average; the cooldown plus the geometric wait predicts " + F(PredictedIntervalHours) + " h");
            }
            catch (Exception e) { fails.Add("breach long run: " + e.Message); }
            return fails;
        }

        // ════════════════════════ crack ════════════════════════
        private static List<string> Crack(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 331 + 9);
                try
                {
                    bool taught = r.Next(2) == 0, warnings = r.Next(4) != 0;
                    int horizon = r.Next(1, 80) * 2500;               // ticks until it breaks, from the first look
                    int now = 0, breakTick = horizon;
                    bool w6 = false, w1 = false; int said6 = 0, said1 = 0; bool broke = false; int brokeAt = -1;
                    int maxSteps = 4000;
                    for (int k = 0; k < maxSteps && !broke; k++)
                    {
                        Steps++;
                        int jump = r.Next(8) == 0 ? r.Next(60, 20000) : 60;           // a time skip now and then (sleep, fast forward)
                        now += jump;
                        if (r.Next(10) == 0) { /* save + load: both flags are Scribed, nothing changes */ }
                        int left = breakTick - now;
                        bool b = RM_NightsideIceKernel.CrackLook(left, taught, warnings, ref w6, ref w1, out bool say6, out bool say1);
                        if (say6) said6++;
                        if (say1) said1++;
                        if (say6 && say1) WarnBoth++;
                        Check(!(say6 && left > 6 * 2500), "the 6 h warning spoke with " + left + " ticks left");
                        Check(!(say1 && left > 2500), "the 1 h warning spoke with " + left + " ticks left");
                        Check(taught && warnings || (!say6 && !say1), "an untaught or muted crack spoke");
                        Check(b == (left <= 0), "break=" + b + " with " + left + " ticks left");
                        if (taught && warnings && left <= 6 * 2500) Check(w6, "the 6 h flag is unset at " + left + " ticks left");
                        if (taught && warnings && left <= 2500) Check(w1, "the 1 h flag is unset at " + left + " ticks left");
                        if (b) { broke = true; brokeAt = now; }
                    }
                    Check(broke, "the crack never broke");
                    Check(brokeAt >= breakTick, "broke early at " + brokeAt + " before " + breakTick);
                    Check(said6 <= 1 && said1 <= 1, "a warning spoke twice (6h " + said6 + ", 1h " + said1 + ")");
                    if (taught && warnings) Check(said6 == 1 && said1 == 1 || horizon <= 6 * 2500 + 20000, "a taught crack that lived through the thresholds said " + said6 + "/" + said1);
                }
                catch (Exception e) { fails.Add("crack seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ edge ════════════════════════
        private static List<string> Edge(int n, int seed0)
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                Check(!RM_NightsideIceKernel.InEdgeBand(8f) && RM_NightsideIceKernel.InEdgeBand(9f) && RM_NightsideIceKernel.InEdgeBand(144f) && !RM_NightsideIceKernel.InEdgeBand(145f), "edge band is 9..144 squared, inclusive (3 to 12 cells)");
                Check(!RM_NightsideIceKernel.InEdgeBand(float.MaxValue), "no buildings at all (nearest = MaxValue) is not an edge");
                // the source footprint is 5..6 x 5..6; the ring around it touches, its inside and anything further does not
                Check(RM_NightsideIceKernel.Touches(4, 5, 5, 5, 6, 6) && RM_NightsideIceKernel.Touches(7, 7, 5, 5, 6, 6) && RM_NightsideIceKernel.Touches(5, 4, 5, 5, 6, 6) && RM_NightsideIceKernel.Touches(6, 7, 5, 5, 6, 6), "the one-cell ring (corners included) touches the source");
                Check(!RM_NightsideIceKernel.Touches(5, 5, 5, 5, 6, 6) && !RM_NightsideIceKernel.Touches(6, 6, 5, 5, 6, 6) && !RM_NightsideIceKernel.Touches(3, 5, 5, 5, 6, 6) && !RM_NightsideIceKernel.Touches(8, 8, 5, 5, 6, 6) && !RM_NightsideIceKernel.Touches(5, 3, 5, 5, 6, 6), "inside the footprint or two cells off does not touch");
                Check(RM_NightsideIceKernel.Score(4, 5, 5, 5, 5, 5, 6, 6, true) == -1f && RM_NightsideIceKernel.Score(2, 5, 5, 5, 5, 5, 6, 6, true) == 9f && RM_NightsideIceKernel.Score(4, 5, 5, 5, 5, 5, 6, 6, false) == 0f, "score: -1 touching, squared distance otherwise, 0 off the ice");
                for (int legCells = -3; legCells <= 20; legCells++)
                    for (int count = 1; count <= 30; count++)
                    {
                        int idx = RM_NightsideIceKernel.LegIndex(legCells, count);
                        Check(idx >= 0 && idx < count, "leg index " + idx + " outside the path (cells " + legCells + ", count " + count + ")");
                        if (legCells >= 1) Check(idx == Math.Min(legCells, count) - 1, "leg index for " + legCells + " cells over " + count + " is " + idx);
                    }
            }
            catch (Exception e) { fails.Add("edge: " + e.Message); }
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 17 + 3);
                try
                {
                    int cx = r.Next(-30, 30), cz = r.Next(-30, 30);
                    var b = Enumerable.Range(0, r.Next(1, 40)).Select(i => (x: cx + r.Next(-25, 26), z: cz + r.Next(-25, 26))).ToList();
                    float nearest = float.MaxValue;
                    foreach (var p in b) { float d = (p.x - cx) * (p.x - cx) + (p.z - cz) * (p.z - cz); if (d < nearest) nearest = d; }
                    bool got = RM_NightsideIceKernel.InEdgeBand(nearest);
                    bool want = b.Any(p => Math.Sqrt((p.x - cx) * (p.x - cx) + (p.z - cz) * (p.z - cz)) < 3 - 1e-9) ? false
                        : b.Min(p => Math.Sqrt((p.x - cx) * (p.x - cx) + (p.z - cz) * (p.z - cz))) <= 12 + 1e-9;
                    Check(got == want, "edge band " + got + " for nearest " + F(Math.Sqrt(nearest)) + " cells; oracle " + want);
                }
                catch (Exception e) { fails.Add("edge seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ icepath ════════════════════════
        private sealed class Grid : IIceGrid
        {
            public int w, h; public bool[,] stand, ice;
            public bool InBounds(int x, int z) { return x >= 0 && z >= 0 && x < w && z < h; }
            // Outside the map everything reads as standable ice: the engine's IntVec3.Standable on an out-of-bounds cell is not a safe "no", so the
            // kernel's own InBounds test is the only thing keeping a path inside the map.
            public bool Standable(int x, int z) { return !InBounds(x, z) || stand[x, z]; }
            public bool IsIce(int x, int z) { return !InBounds(x, z) || ice[x, z]; }
        }

        private static Grid MakeGrid(Random r, int mode)
        {
            int w = r.Next(6, 26), h = r.Next(6, 26);
            var g = new Grid { w = w, h = h, stand = new bool[w, h], ice = new bool[w, h] };
            double wall = new[] { 0.0, 0.1, 0.25, 0.4 }[r.Next(4)];
            for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) { g.stand[x, z] = r.NextDouble() >= wall; g.ice[x, z] = false; }
            // ice blobs
            int blobs = r.Next(1, 6);
            for (int b = 0; b < blobs; b++)
            {
                int bx = r.Next(w), bz = r.Next(h), br = r.Next(2, 9);
                for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) if ((x - bx) * (x - bx) + (z - bz) * (z - bz) <= br * br && r.NextDouble() < 0.9) g.ice[x, z] = true;
            }
            if (mode == 1) for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) g.ice[x, z] = r.NextDouble() < 0.85;     // mostly ice
            return g;
        }

        private static float Sc(int x, int z, int sx, int sz, int[] rect, bool onIce)
        {
            if (!onIce) return 0f;
            bool inside = x >= rect[0] && x <= rect[2] && z >= rect[1] && z <= rect[3];
            bool ring = x >= rect[0] - 1 && x <= rect[2] + 1 && z >= rect[1] - 1 && z <= rect[3] + 1;
            if (ring && !inside) return -1f;
            return (x - sx) * (x - sx) + (z - sz) * (z - sz);
        }

        private static List<string> IcePath(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 1009 + 13);
                try
                {
                    var g = MakeGrid(r, r.Next(4) == 0 ? 1 : 0);
                    // the source: a 1x1 to 3x3 footprint made non-standable (a building)
                    int sw = r.Next(1, 4), sh = r.Next(1, 4);
                    int sx0 = r.Next(1, Math.Max(2, g.w - sw)), sz0 = r.Next(1, Math.Max(2, g.h - sh));
                    int[] rect = { sx0, sz0, Math.Min(g.w - 1, sx0 + sw - 1), Math.Min(g.h - 1, sz0 + sh - 1) };
                    for (int x = rect[0]; x <= rect[2]; x++) for (int z = rect[1]; z <= rect[3]; z++) { g.stand[x, z] = false; g.ice[x, z] = false; }
                    int srcX = (rect[0] + rect[2]) / 2, srcZ = (rect[1] + rect[3]) / 2;
                    // the hull rule: sometimes floor (no ice) all around the source
                    bool hull = r.Next(5) == 0;
                    if (hull) for (int x = rect[0] - 2; x <= rect[2] + 2; x++) for (int z = rect[1] - 2; z <= rect[3] + 2; z++) if (g.InBounds(x, z)) g.ice[x, z] = false;
                    // the start: a random standable cell
                    var cells = new List<(int, int)>();
                    for (int x = 0; x < g.w; x++) for (int z = 0; z < g.h; z++) if (g.stand[x, z]) cells.Add((x, z));
                    if (cells.Count == 0) continue;
                    var st = cells[r.Next(cells.Count)];
                    bool startOnIce = g.ice[st.Item1, st.Item2];
                    int budget = new[] { 1, 2, 5, 20, 100, 100000 }[r.Next(6)];
                    var path = RM_NightsideIceKernel.IcePath(g, st.Item1, st.Item2, startOnIce, srcX, srcZ, rect[0], rect[1], rect[2], rect[3], budget);
                    var full = RM_NightsideIceKernel.IcePath(g, st.Item1, st.Item2, startOnIce, srcX, srcZ, rect[0], rect[1], rect[2], rect[3], 1000000);

                    // --- validity of any path
                    Validate(g, st, startOnIce, path);
                    Validate(g, st, startOnIce, full);
                    if (path.Count == 0) EmptyPaths++;

                    // --- an independent search mirroring the documented algorithm (queue of cells, budget = cells taken off the queue,
                    //     best updated when a cell is queued, strict improvement only, compass order N E S W SE NE NW SW): exact path equality
                    {
                        int[] ox = { 0, 1, 0, -1, 1, 1, -1, -1 }, oz = { 1, 0, -1, 0, -1, 1, 1, -1 };
                        var par = new Dictionary<(int, int), (int, int)> { [st] = st };
                        var q = new Queue<(int, int)>(); q.Enqueue(st);
                        var best = st; float bestSc = Sc(st.Item1, st.Item2, srcX, srcZ, rect, startOnIce); int left = budget;
                        while (q.Count > 0 && left-- > 0)
                        {
                            var c = q.Dequeue();
                            if (!startOnIce && g.InBounds(c.Item1, c.Item2) && g.ice[c.Item1, c.Item2]) { best = c; break; }
                            for (int i = 0; i < 8; i++)
                            {
                                var nb = (c.Item1 + ox[i], c.Item2 + oz[i]);
                                if (par.ContainsKey(nb) || !g.InBounds(nb.Item1, nb.Item2) || !g.stand[nb.Item1, nb.Item2]) continue;
                                if (startOnIce && !g.ice[nb.Item1, nb.Item2]) continue;
                                if (i >= 4)
                                {
                                    bool sa = g.Standable(nb.Item1, c.Item2), sb = g.Standable(c.Item1, nb.Item2);
                                    if (!(sa && sb)) continue;
                                    if (startOnIce && !(g.IsIce(nb.Item1, c.Item2) && g.IsIce(c.Item1, nb.Item2))) continue;
                                }
                                par[nb] = c; q.Enqueue(nb);
                                float sc = Sc(nb.Item1, nb.Item2, srcX, srcZ, rect, startOnIce);
                                if (sc < bestSc) { bestSc = sc; best = nb; }
                            }
                        }
                        var want = new List<(int, int)>();
                        for (var c = best; c != st; c = par[c]) want.Add(c);
                        want.Reverse();
                        Check(want.SequenceEqual(path.Select(kv => (kv.Key, kv.Value))), "with budget " + budget + " the path has " + path.Count + " cells, the mirrored search " + want.Count + " (or different cells)");
                    }

                    // --- independent search: shortest distances over the same move rules (written separately: layered frontier, not a queue)
                    var dist = new Dictionary<(int, int), int> { [st] = 0 };
                    var frontier = new List<(int, int)> { st };
                    int depth = 0;
                    while (frontier.Count > 0)
                    {
                        depth++;
                        var next = new List<(int, int)>();
                        foreach (var c in frontier)
                            for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
                                {
                                    if (dx == 0 && dz == 0) continue;
                                    var q = (c.Item1 + dx, c.Item2 + dz);
                                    if (dist.ContainsKey(q) || !g.InBounds(q.Item1, q.Item2) || !g.stand[q.Item1, q.Item2]) continue;
                                    if (startOnIce && !g.ice[q.Item1, q.Item2]) continue;
                                    if (dx != 0 && dz != 0)
                                    {
                                        bool a = g.Standable(q.Item1, c.Item2), b = g.Standable(c.Item1, q.Item2);
                                        if (!a || !b) continue;
                                        if (startOnIce && !(g.ice[q.Item1, c.Item2] && g.ice[c.Item1, q.Item2])) continue;
                                    }
                                    dist[q] = depth; next.Add(q);
                                }
                        frontier = next;
                    }
                    if (startOnIce)
                    {
                        PathsOnIce++;
                        if (hull) PathsHull++;
                        float bestScore = dist.Keys.Min(c => Sc(c.Item1, c.Item2, srcX, srcZ, rect, true));
                        var endF = full.Count == 0 ? st : (full[full.Count - 1].Key, full[full.Count - 1].Value);
                        Check(Sc(endF.Item1, endF.Item2, srcX, srcZ, rect, true) == bestScore, "unlimited search ended at score " + Sc(endF.Item1, endF.Item2, srcX, srcZ, rect, true) + ", the best reachable is " + bestScore);
                        Check(full.Count == dist[endF], "path length " + full.Count + " is not the shortest distance " + dist[endF] + " to its end");
                        // a touching reachable cell is always preferred
                        if (dist.Keys.Any(c => Sc(c.Item1, c.Item2, srcX, srcZ, rect, true) == -1f)) Check(Sc(endF.Item1, endF.Item2, srcX, srcZ, rect, true) == -1f, "a touching cell is reachable but the path does not end on one");
                        // budgets never improve on the unlimited result and never beat it
                        var endB = path.Count == 0 ? st : (path[path.Count - 1].Key, path[path.Count - 1].Value);
                        Check(Sc(endB.Item1, endB.Item2, srcX, srcZ, rect, true) >= bestScore, "a limited search beat the optimum");
                        if (budget < 100000) PathsLimited++;
                        // more budget is never worse
                        var bigger = RM_NightsideIceKernel.IcePath(g, st.Item1, st.Item2, startOnIce, srcX, srcZ, rect[0], rect[1], rect[2], rect[3], budget * 4 + 1);
                        var endG = bigger.Count == 0 ? st : (bigger[bigger.Count - 1].Key, bigger[bigger.Count - 1].Value);
                        Check(Sc(endG.Item1, endG.Item2, srcX, srcZ, rect, true) <= Sc(endB.Item1, endB.Item2, srcX, srcZ, rect, true), "a larger budget ended on a worse cell");
                    }
                    else
                    {
                        PathsOffIce++;
                        var iceReach = dist.Where(kv => g.ice[kv.Key.Item1, kv.Key.Item2]).ToList();
                        if (iceReach.Count == 0) Check(full.Count == 0, "no ice is reachable but a path of " + full.Count + " cells was returned");
                        else
                        {
                            int nearestIce = iceReach.Min(kv => kv.Value);
                            Check(full.Count == nearestIce, "off the ice, the path to the first ice is " + full.Count + " cells, the nearest ice is " + nearestIce + " away");
                            var last = full[full.Count - 1];
                            Check(g.ice[last.Key, last.Value], "the path to the ice does not end on ice");
                            for (int i = 0; i < full.Count - 1; i++) Check(!g.ice[full[i].Key, full[i].Value], "the way to the ice crosses ice before its end");
                        }
                        if (path.Count > 0) Check(g.ice[path[path.Count - 1].Key, path[path.Count - 1].Value], "a limited search off the ice ended on something that is not ice");
                    }
                }
                catch (Exception e) { fails.Add("icepath seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        private static void Validate(Grid g, (int, int) st, bool onIce, List<KeyValuePair<int, int>> path)
        {
            var prev = st; var seen = new HashSet<(int, int)> { st };
            foreach (var c in path)
            {
                var cur = (c.Key, c.Value);
                int dx = cur.Item1 - prev.Item1, dz = cur.Item2 - prev.Item2;
                Check(Math.Abs(dx) <= 1 && Math.Abs(dz) <= 1 && (dx != 0 || dz != 0), "path step " + prev + " -> " + cur + " is not to a neighbouring cell");
                Check(g.InBounds(cur.Item1, cur.Item2) && g.stand[cur.Item1, cur.Item2], "path cell " + cur + " is out of bounds or not standable");
                Check(seen.Add(cur), "path revisits " + cur);
                if (onIce) Check(g.ice[cur.Item1, cur.Item2], "path cell " + cur + " is not ice (the shivven never leave the ice)");
                if (dx != 0 && dz != 0)
                {
                    Check(g.Standable(cur.Item1, prev.Item2) && g.Standable(prev.Item1, cur.Item2), "diagonal step " + prev + " -> " + cur + " cuts a corner through a wall");
                    if (onIce) Check(g.ice[cur.Item1, prev.Item2] && g.ice[prev.Item1, cur.Item2], "diagonal step " + prev + " -> " + cur + " cuts a corner off the ice");
                }
                prev = cur;
            }
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("dial", () => Dial(N(6000), S(1))),
                ("source", () => Source(N(4000), S(1))),
                ("breach", () => Breach(N(4000), S(1))),
                ("crack", () => Crack(N(4000), S(1))),
                ("edge", () => Edge(N(4000), S(1))),
                ("icepath", () => IcePath(N(6000), S(1))),
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
                Console.WriteLine($"reached: on-ice paths {PathsOnIce}, off-ice paths {PathsOffIce}, hull cases {PathsHull}, budget-limited {PathsLimited}, empty paths {EmptyPaths}, breaches {Breaches}, cache refreshes {Refreshes}, cache hits {StaleKeeps}, both warnings in one look {WarnBoth}");
                Console.WriteLine($"info at a full dial (scale 1) a crack opens every {MeanIntervalHours:F1} h on average (two-day cooldown + geometric wait predicts {PredictedIntervalHours:F1} h); the comment/setting text promises about one a day");
                if (!oneSeed.HasValue && scale >= 1 && (PathsOnIce == 0 || PathsOffIce == 0 || PathsHull == 0 || PathsLimited == 0 || EmptyPaths == 0 || Breaches == 0 || Refreshes == 0 || StaleKeeps == 0 || WarnBoth == 0)) { Console.WriteLine("FAIL the fuzz never reached on/off-ice paths, hull cases, budgets, empty paths, breaches, cache hits and double warnings (blind)"); ok = false; }
            }
            Console.WriteLine($"nightsideice fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
