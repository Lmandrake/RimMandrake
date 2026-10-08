// Approach B for ShipVermin: seeded fuzz over RM_VerminKernel against independent restatements.
//   nest   random tick sequences of one wreck nest (spawn/despawn, settings flips, rate changes, reloads) through the production Step /
//          NestIntervalTicks / BurstShouldSchedule against a model of the comp: one burst per nest life, attempts only on schedule, never in a
//          tick when disabled, the timer always moves forward, the refusal order is the documented one
//   pick   weighted pools and the roster rule: a forbidden slot is never picked (as the free kind or the swapped canon kind), the weights are honoured,
//          a roll anywhere in [0,1] lands on a valid entry
//   grant  the innate-ability decision, exhaustively
//   cone   the chemfuel spray: the aim point lands exactly `range` out, the cone is symmetric, contains the heading, never reaches behind the caster
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.ShipVermin.SelfTest
{
    internal static class ShipVerminFuzz
    {
        public static long Cases, Steps, Bursts, Attempts, Disabled, Reloads, Pools, Forbidden, ConeCells;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        // ═════════════ nest ═════════════
        private struct Op { public int kind; public int a; public float f; public override string ToString() { return kind + ":" + a + ":" + f.ToString(System.Globalization.CultureInfo.InvariantCulture); } }

        private static string RunNest(List<Op> ops, int seed)
        {
            // comp state
            int now = 0, next = -1, burstTick = -1; bool burstDone = false, spawned = true, enabled = true; float mult = 1f;
            int burstMax = seed % 3 == 0 ? 0 : 1 + seed % 4;
            int lastNext = -1; int bursts = 0;
            var rng = new Random(seed);
            void Spawn(bool reload)
            {
                // PostSpawnSetup
                if (next < 0) next = now + RM_VerminKernel.NestIntervalTicks(2f + (float)rng.NextDouble() * 2f, mult);
                if (RM_VerminKernel.BurstShouldSchedule(reload, burstDone, burstTick, burstMax)) burstTick = now + rng.Next(600, 2401);
            }
            Spawn(false);
            int step = 0;
            try
            {
                foreach (Op op in ops)
                {
                    step++; Steps++;
                    switch (op.kind)
                    {
                        case 0: // advance time (bounded so the fuzz stays fast; nests run on days-long timers)
                            now += op.a; break;
                        case 1: enabled = !enabled; break;
                        case 2: mult = op.f; break;
                        case 4: now = Math.Max(now, rng.Next(2) == 0 && burstTick >= 0 ? burstTick : next); break;   // land exactly ON a due tick
                        case 3: spawned = !spawned; if (spawned) { Reloads++; Spawn(rng.Next(2) == 0); } break;
                    }
                    var st = RM_VerminKernel.Step(spawned, enabled, burstDone, burstTick, next, now);
                    // model
                    bool wantBurst = spawned && enabled && !burstDone && burstTick >= 0 && now >= burstTick;
                    bool wantAttempt = spawned && enabled && now >= next;
                    Check(st.Burst == wantBurst && st.Attempt == wantAttempt, "Step " + st.Burst + "/" + st.Attempt + " want " + wantBurst + "/" + wantAttempt);
                    if (!spawned || !enabled) { Check(!st.Burst && !st.Attempt, "a disabled or despawned nest acted"); Disabled++; }
                    if (st.Burst) { burstDone = true; bursts++; Bursts++; Check(bursts == 1 || false, "a nest burst twice"); }
                    if (st.Attempt)
                    {
                        Attempts++;
                        int iv = RM_VerminKernel.NestIntervalTicks(2f + (float)rng.NextDouble() * 2f, mult);
                        Check(iv >= 1, "interval below one tick");
                        lastNext = next; next = now + iv;
                        Check(next > now && next > lastNext, "the timer did not move forward");
                    }
                    if (burstMax <= 0) Check(burstTick < 0 && bursts == 0, "a nest with no burst configured scheduled or fired one");
                }
            }
            catch (Exception ex) { return "step " + step + ": " + ex.Message; }
            return null;
        }

        private static List<Op> GenNest(Random rng)
        {
            var ops = new List<Op>();
            int n = rng.Next(5, 120);
            float[] mults = { 0.01f, 0.25f, 1f, 3f, 100f, 0f, -1f };
            for (int i = 0; i < n; i++)
            {
                int k = rng.Next(100);
                if (k < 60) ops.Add(new Op { kind = 0, a = rng.Next(1, rng.Next(4) == 0 ? 400000 : 4000) });
                else if (k < 72) ops.Add(new Op { kind = 1 });
                else if (k < 88) ops.Add(new Op { kind = 2, f = mults[rng.Next(mults.Length)] });
                else if (k < 94) ops.Add(new Op { kind = 4 });
                else ops.Add(new Op { kind = 3 });
            }
            return ops;
        }

        private static List<Op> Shrink(List<Op> ops, int seed)
        {
            var cur = new List<Op>(ops);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<Op>(cur); trial.RemoveRange(i, chunk);
                        long c = Bursts, a = Attempts, d = Disabled, r = Reloads;
                        bool fails = RunNest(trial, seed) != null;
                        Bursts = c; Attempts = a; Disabled = d; Reloads = r;
                        if (fails) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private static List<string> Nest(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; Cases++;
                var ops = GenNest(new Random(seed));
                string msg = RunNest(ops, seed);
                if (msg != null) fails.Add("nest seed " + seed + ": " + msg + " | " + string.Join(" ", Shrink(ops, seed)));
            }
            try
            {
                Cases++;
                // interval table: rate multiplier scales the wait inversely, never below one tick, the 0.01 floor stops a zero or negative rate dividing by zero
                foreach (float days in new[] { 0f, 0.0001f, 1f, 2f, 3.5f, 4f })
                    foreach (float m in new[] { -5f, 0f, 0.01f, 0.05f, 0.25f, 0.5f, 1f, 2f, 3f, 100f })
                    {
                        Steps++;
                        int t = RM_VerminKernel.NestIntervalTicks(days, m);
                        Check(t >= 1, "interval " + t + " for " + days + "d x" + m);
                        Check(m < 0.01f ? t == RM_VerminKernel.NestIntervalTicks(days, 0.01f) : true, "a rate below the floor must equal the floor");
                        if (m >= 0.01f && days >= 1f) Check(Math.Abs(t - days * 60000f / m) <= 1.0f + days * 60000f / m * 1e-6, "interval " + t + " is not days*60000/rate for " + days + "," + m);
                        Check(RM_VerminKernel.NestIntervalTicks(days, m * 2 + 0.01f) <= t, "a faster rate gave a longer wait");
                    }
                // exact boundaries of the weighted pick: a roll sitting on a cumulative edge belongs to the NEXT entry
                Check(RM_VerminKernel.PickByWeight(new[] { 1f, 1f }, 0.5) == 1 && RM_VerminKernel.PickByWeight(new[] { 1f, 3f }, 0.25) == 1 && RM_VerminKernel.PickByWeight(new[] { 2f, 2f }, 0.0) == 0 && RM_VerminKernel.PickByWeight(new[] { 1f, 1f, 2f }, 0.5) == 2, "pick boundaries");
                Check(RM_VerminKernel.PickByWeight(new[] { 5f }, 0.999999) == 0 && RM_VerminKernel.PickByWeight(new[] { 1f, 1f }, 1.0) == 1, "pick at the top of the roll");
                // spray geometry with known answers
                Check(Math.Abs(RM_VerminKernel.HalfAngleDeg(1, 2) - 45.0) < 1e-9 && Math.Abs(RM_VerminKernel.HalfAngleDeg(Math.Sqrt(3), 2) - 30.0) < 1e-9, "half angle is asin(halfWidth/hypotenuse)");
                Check(RM_VerminKernel.InCone(3, 0, 5, 0, 0.0) && !RM_VerminKernel.InCone(3, 1, 5, 0, 0.0) && RM_VerminKernel.InCone(-1, 0.001, -1, -0.001, 1.0), "cone edge is inclusive and wraps through 180");
                Steps += 4;
                // refusal table, exhaustive over the seven inputs: the first failing check wins, in the documented order
                var bools = new[] { false, true };
                foreach (bool map in bools) foreach (bool pc in bools) foreach (int pop in new[] { 0, 11, 12, 13 }) foreach (bool sp in bools) foreach (bool cell in bools) foreach (bool gen in bools)
                {
                    Steps++;
                    var got = RM_VerminKernel.SpawnRefusal(map, pc, pop, 12, sp, cell, gen);
                    var want = !map ? RM_VerminKernel.Refusal.NoMap : (pc && pop >= 12) ? RM_VerminKernel.Refusal.PopulationCap : !sp ? RM_VerminKernel.Refusal.NoSpecies : !cell ? RM_VerminKernel.Refusal.NoCell : !gen ? RM_VerminKernel.Refusal.GenerationFailed : RM_VerminKernel.Refusal.None;
                    Check(got == want, "SpawnRefusal(" + map + "," + pc + "," + pop + "," + sp + "," + cell + "," + gen + ") = " + got + " want " + want);
                    if (!pc) Check(got != RM_VerminKernel.Refusal.PopulationCap, "a map with no population component was capped (it must keep spawning only through the other gates)");
                }
                foreach (bool re in bools) foreach (bool done in bools) foreach (int bt in new[] { -1, 0, 100 }) foreach (int bm in new[] { 0, 1, 3 })
                {
                    Steps++;
                    Check(RM_VerminKernel.BurstShouldSchedule(re, done, bt, bm) == (!re && !done && bt < 0 && bm > 0), "BurstShouldSchedule");
                }
            }
            catch (Exception ex) { fails.Add("nest tables: " + ex.Message); }
            return fails;
        }

        // ═════════════ pick ═════════════
        private static List<string> Pick(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    string[] free = { "RM_Skivvik", "RM_Rattagh", "RM_Gorrud", "RM_Fethrik" };
                    // some slots have a canon kind swapped in
                    var canon = free.ToDictionary(f => f, f => rng.Next(2) == 0 ? "RSW_" + f.Substring(3) : null);
                    var enabled = free.ToDictionary(f => f, f => rng.Next(3) != 0);
                    var installed = new HashSet<string>(free.Concat(canon.Values.Where(v => v != null)).Where(_ => rng.Next(6) != 0));
                    Func<string, string> resolve = name => { if (!installed.Contains(name)) return null; string sw; return canon.TryGetValue(name, out sw) && sw != null && installed.Contains(sw) ? sw : name; };
                    var slots = free.Select(f => new RM_VerminKernel.RosterSlot { Kind = f, Enabled = enabled[f], ResolvedName = () => resolve(f) }).ToList();
                    string[] names = free.Concat(canon.Values.Where(v => v != null)).Concat(new[] { "Elsewhere_Beast", "", null, "RM_Ghost" }).ToArray();
                    var weights = new List<KeyValuePair<string, float>>();
                    int k = rng.Next(0, 7);
                    for (int i = 0; i < k; i++) weights.Add(new KeyValuePair<string, float>(names[rng.Next(names.Length)], new[] { 0f, -1f, 0.5f, 1f, 3f }[rng.Next(5)]));
                    Func<string, bool> allows = nm => RM_VerminKernel.RosterAllows(slots, nm);
                    var pool = RM_VerminKernel.BuildPool(weights, allows, resolve);
                    Pools++; Steps += k + 1;
                    // independent expectation
                    int expect = 0;
                    foreach (var w in weights)
                    {
                        bool slotted = free.Any(f => f == w.Key || resolve(f) == w.Key);
                        bool slotOn = !slotted || enabled[free.First(f => f == w.Key || resolve(f) == w.Key)];
                        if (!string.IsNullOrEmpty(w.Key) && w.Value > 0 && slotOn && resolve(w.Key) != null) expect++;
                        if (slotted && !slotOn) Forbidden++;
                    }
                    Check(pool.Count == expect, "pool has " + pool.Count + " entries, expected " + expect + " from " + string.Join(",", weights.Select(w => w.Key + "x" + w.Value)));
                    foreach (var e in pool)
                    {
                        Check(e.Value > 0f, "a non-positive weight entered the pool");
                        var slot = free.FirstOrDefault(f => f == e.Key || resolve(f) == e.Key);
                        Check(slot == null || enabled[slot], "a forbidden slot's species " + e.Key + " is in the pool");
                    }
                    if (pool.Count > 0)
                    {
                        var ws = pool.Select(e => e.Value).ToList();
                        double total = ws.Sum();
                        foreach (double roll in new[] { 0.0, 0.25, 0.5, 0.999999999, rng.NextDouble(), rng.NextDouble(), 1.0 })
                        {
                            int idx = RM_VerminKernel.PickByWeight(ws, roll);
                            Check(idx >= 0 && idx < ws.Count, "pick index " + idx + " out of range at roll " + roll);
                            double lo = ws.Take(idx).Sum() / total, hi = ws.Take(idx + 1).Sum() / total;
                            Check(roll >= lo - 1e-9 && (roll < hi + 1e-9 || idx == ws.Count - 1), "roll " + roll + " landed on entry " + idx + " covering [" + lo + "," + hi + ")");
                        }
                    }
                }
                catch (Exception ex) { fails.Add("pick seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ grant ═════════════
        private static List<string> Grant()
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                var bools = new[] { false, true };
                foreach (bool g in bools) foreach (bool on in bools) foreach (bool miss in bools) foreach (bool pawn in bools)
                {
                    Steps++;
                    var got = RM_VerminKernel.InnateGrant(g, on, miss, pawn);
                    var want = (g || !on) ? RM_VerminKernel.Grant.Nothing : miss ? RM_VerminKernel.Grant.MarkGrantedOnly : !pawn ? RM_VerminKernel.Grant.Nothing : RM_VerminKernel.Grant.Give;
                    Check(got == want, "InnateGrant(" + g + "," + on + "," + miss + "," + pawn + ") = " + got + " want " + want);
                    if (g) Check(got == RM_VerminKernel.Grant.Nothing, "an ability already granted was granted again");
                    if (!on) Check(got == RM_VerminKernel.Grant.Nothing, "the setting off still granted (a mite that already has it keeps it, but none gains it)");
                }
            }
            catch (Exception ex) { fails.Add("grant: " + ex.Message); }
            return fails;
        }

        // ═════════════ cone ═════════════
        private static List<string> Cone(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var rng = new Random(seed); Cases++;
                try
                {
                    int px = rng.Next(-20, 21), pz = rng.Next(-20, 21);
                    int ax = px + rng.Next(-15, 16), az = pz + rng.Next(-15, 16);
                    float range = new[] { 3f, 6f, 10f, 12.9f }[rng.Next(4)];
                    float width = new[] { 1f, 4f, 6f, 10f }[rng.Next(4)];
                    Steps++;
                    int ox, oz;
                    bool moved = RM_VerminKernel.AimPoint(px, pz, ax, az, range, out ox, out oz);
                    if (px == ax && pz == az) { Check(!moved && ox == ax && oz == az, "aiming at yourself must report no aim"); continue; }
                    Check(moved, "AimPoint reported no aim for a distinct cell");
                    double d = Math.Sqrt((double)(ox - px) * (ox - px) + (double)(oz - pz) * (oz - pz));
                    Check(Math.Abs(d - range) <= 0.75, "aim pushed out to " + d + " not " + range);
                    // same heading as the click, within rounding of a cell
                    double ang1 = Math.Atan2(az - pz, ax - px), ang2 = Math.Atan2(oz - pz, ox - px);
                    double dd = Math.Abs(ang1 - ang2); if (dd > Math.PI) dd = 2 * Math.PI - dd;
                    Check(dd <= Math.Atan(0.75 / range) * 2 + 1e-9, "the push-out changed the heading by " + dd + " rad");
                    double half = RM_VerminKernel.HalfAngleDeg(d, width);
                    Check(half > 0 && half < 90, "half angle " + half);
                    Check(Math.Abs(RM_VerminKernel.HalfAngleDeg(d, width * 2) - RM_VerminKernel.HalfAngleDeg(d, width)) > 0, "a wider spray did not widen the cone");
                    Check(RM_VerminKernel.HalfAngleDeg(d * 2, width) < half, "a longer cone did not narrow");
                    double adx = ox - px, adz = oz - pz;
                    Check(RM_VerminKernel.InCone(adx, adz, adx, adz, half), "the heading itself is outside the cone");
                    Check(!RM_VerminKernel.InCone(-adx, -adz, adx, adz, half), "the cell directly behind the caster is inside the cone");
                    for (int t = 0; t < 40; t++)
                    {
                        double cx = rng.Next(-14, 15), cz = rng.Next(-14, 15);
                        if (cx == 0 && cz == 0) continue;
                        bool inside = RM_VerminKernel.InCone(cx, cz, adx, adz, half);
                        // symmetric: reflecting the cell about the heading axis keeps the verdict
                        double len = Math.Sqrt(adx * adx + adz * adz), ux = adx / len, uz = adz / len;
                        double dot = cx * ux + cz * uz;
                        double rx = 2 * dot * ux - cx, rz = 2 * dot * uz - cz;
                        Check(RM_VerminKernel.InCone(rx, rz, adx, adz, half) == inside || Math.Abs(Angle(cx, cz, adx, adz) - half) < 1e-6, "the cone is not symmetric about its heading at " + cx + "," + cz);
                        double a = Angle(cx, cz, adx, adz);
                        if (Math.Abs(a - half) > 1e-6) Check(inside == (a <= half), "InCone says " + inside + " at angle " + a + " with half angle " + half);
                        if (inside) ConeCells++;
                    }
                }
                catch (Exception ex) { fails.Add("cone seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        private static double Angle(double ax, double az, double bx, double bz)
        {
            double d = Math.Abs(Math.Atan2(az, ax) - Math.Atan2(bz, bx)) * 180 / Math.PI;
            return d > 180 ? 360 - d : d;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("nest", () => Nest(N(5000), S(1))),
                ("pick", () => Pick(N(6000), S(1))),
                ("grant", () => Grant()),
                ("cone", () => Cone(N(4000), S(1))),
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
            Console.WriteLine($"reached: bursts {Bursts}, attempts {Attempts}, disabled ticks {Disabled}, respawns {Reloads}, pools {Pools}, forbidden-slot rows {Forbidden}, cone cells {ConeCells}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Bursts == 0 || Attempts == 0 || Disabled == 0 || Reloads == 0 || Pools == 0 || Forbidden == 0 || ConeCells == 0)) { Console.WriteLine("FAIL fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"shipvermin fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
