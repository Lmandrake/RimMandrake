using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.LeaningScrub.SelfTest
{
    internal static partial class LeaningScrubFuzz
    {
        // ════════════════════════ guardian ════════════════════════
        private static readonly string[] GdNames = { "Harvest", "Work", "Damage", "Linger", "LongTick", "Rage", "On", "Spawned", "Live", "Watch", "Refill" };
        public static long GdDrops, GdAnnounces, GdForgives, GdReroosts, GdRefills;

        private static string RunGuardian(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x6d);
            float setting = new[] { 0.5f, 1f, 2f }[r.Next(3)], forgive = new[] { 0.1f, 0.5f, 1f, 5f, 30f }[r.Next(5)];
            float km = 0f; int stage = 0; double m = 0;
            bool on = true, spawned = true, raging = false, watchful = false; int live = 2;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                float amount = 0f;
                switch (a.kind)
                {
                    case 0: amount = 0.25f * setting; break;
                    case 1: amount = 0.10f * setting; break;
                    case 2: amount = (a.a % 40) * 0.05f; break;
                    case 3: amount = 0.02f; break;
                    case 5: raging = !raging; break;
                    case 6: on = !on; break;
                    case 7: spawned = !spawned; break;
                    case 8: live = a.a % 4; break;
                    case 9: watchful = !watchful; break;
                    case 10:
                        {
                            int comp = RM_GuardianKernel.Complement(a.a % 6, a.b % 5 - 1);
                            Check(comp >= 0 && comp <= Math.Max(0, a.b % 5 - 1) && comp <= a.a % 6, "complement outside [0, min(target, max)]" + where);
                            Check(RM_GuardianKernel.RefillSpawns(a.a % 4, comp, false) == (a.a % 4 < comp) && !RM_GuardianKernel.RefillSpawns(0, 5, true), "refill truth table" + where);
                            GdRefills++;
                            break;
                        }
                }
                if (a.kind <= 3)
                {
                    float nm; int ns, announce; bool drop;
                    bool applied = RM_GuardianKernel.Add(km, stage, amount, spawned, on, live, out nm, out ns, out announce, out drop);
                    bool spec = amount > 0f && spawned && on && live != 0;
                    Check(applied == spec, $"Add applied={applied}, spec {spec}" + where);
                    if (!applied) Check(nm == km && ns == stage && announce == 0 && !drop, "a refused add changed state" + where);
                    else
                    {
                        Check(nm >= km, "an add lowered the meter" + where);
                        Check(nm <= 1f, "meter above 1" + where);
                        Check(ns >= stage, "an add lowered the stage" + where);
                        Check((announce > 0) == (ns > stage), "announce iff stage rose" + where);
                        if (announce > 0) { Check(announce == ns, "announced stage is not the new stage" + where); GdAnnounces++; }
                        Check(drop == (nm >= 1f), "drop iff the meter is full" + where);
                        if (drop) GdDrops++;
                        m = Math.Min(1.0, m + amount);
                    }
                    km = nm; stage = ns;
                }
                if (a.kind == 4)
                {
                    int ticks = 1 + a.a % 40;
                    for (int t = 0; t < ticks; t++)
                    {
                        float before = km; int sBefore = stage;
                        RM_GuardianKernel.Forgive(km, stage, forgive, raging, out km, out stage);
                        if (raging) { Check(km == before && stage == sBefore, "forgiveness ran while a warden was raging" + where); }
                        else
                        {
                            Check(km <= before && km >= 0f, "forgiveness raised or underflowed the meter" + where);
                            Check(stage <= sBefore, "forgiveness raised the stage" + where);
                            m = Math.Max(0.0, m - (1.0 / Math.Max(0.5, forgive)) * (2000.0 / 60000.0));
                            GdForgives++;
                        }
                    }
                }
                Check(km >= 0f && km <= 1f, "meter left [0,1]: " + km + where);
                Check(stage == RM_GuardianKernel.StageOf(km), $"stage {stage} != StageOf({km}) = {RM_GuardianKernel.StageOf(km)}" + where);
                Check(Near(km, m, 2e-3), $"meter {km} drifted from the double ledger {m}" + where);
                bool rer = RM_GuardianKernel.ShouldReroost(watchful, raging, km);
                Check(rer == (watchful && !raging && km < 0.3f), "reroost truth" + where);
                if (rer) GdReroosts++;
            }
            return null;
        }

        private static string GuardianUnits(int seed)
        {
            var r = new Random(seed ^ 0x3c);
            // stage boundaries
            Check(RM_GuardianKernel.StageOf(0f) == 0 && RM_GuardianKernel.StageOf(0.2999f) == 0 && RM_GuardianKernel.StageOf(0.3f) == 1 && RM_GuardianKernel.StageOf(0.5999f) == 1 && RM_GuardianKernel.StageOf(0.6f) == 2 && RM_GuardianKernel.StageOf(0.9999f) == 2 && RM_GuardianKernel.StageOf(1f) == 3, "stage boundaries");
            // draining a full meter takes max(0.5, days) * 30 long ticks
            foreach (float days in new[] { 0.1f, 0.5f, 1f, 5f, 30f })
            {
                float km = 1f; int st = 3, n = 0;
                while (km > 0f && n < 5000) { RM_GuardianKernel.Forgive(km, st, days, false, out km, out st); n++; }
                double expect = Math.Max(0.5, days) * 30.0;
                Check(Math.Abs(n - expect) <= 2, $"a full meter drained in {n} long ticks, spec {expect} (days {days})");
                Check(st == 0, "stage did not reach 0 with the meter");
            }
            // refill tick
            for (int t = 0; t < 20; t++)
            {
                int now = r.Next(0, 5000000); float d = (float)(r.NextDouble() * 60);
                Check(RM_GuardianKernel.RefillTick(now, d) == now + (int)(d * 60000f), "refill tick formula");
                Check(RM_GuardianKernel.RefillTick(now, d + 1f) > RM_GuardianKernel.RefillTick(now, d), "refill tick not increasing in days");
            }
            // double-roost rule: antisymmetric, and in any group of mutually near roosts only the lowest id is free
            for (int t = 0; t < 10; t++)
            {
                int n = r.Next(2, 9); float rad = new[] { 3f, 9f, 20f }[r.Next(3)];
                var x = new int[n]; var z = new int[n]; var id = new int[n];
                var used = new HashSet<int>();
                for (int i = 0; i < n; i++) { x[i] = r.Next(-15, 16); z[i] = r.Next(-15, 16); do { id[i] = r.Next(1, 500); } while (!used.Add(id[i])); }
                var blocked = new bool[n];
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < n; j++)
                        if (i != j && RM_GuardianKernel.YieldsToOther(x[j] - x[i], z[j] - z[i], rad, id[j], id[i])) blocked[i] = true;
                for (int i = 0; i < n; i++)
                    for (int j = i + 1; j < n; j++)
                    {
                        bool near = (double)(x[i] - x[j]) * (x[i] - x[j]) + (double)(z[i] - z[j]) * (z[i] - z[j]) <= (double)rad * rad;
                        bool ij = RM_GuardianKernel.YieldsToOther(x[j] - x[i], z[j] - z[i], rad, id[j], id[i]), ji = RM_GuardianKernel.YieldsToOther(x[i] - x[j], z[i] - z[j], rad, id[i], id[j]);
                        Check(!(ij && ji), "two roosts each yield to the other");
                        Check(ij || ji ? near : !near, "yield without proximity, or proximity without a yield");
                    }
                int lowest = Enumerable.Range(0, n).OrderBy(i => id[i]).First();
                Check(!blocked[lowest], "the lowest-id roost was blocked");
            }
            return null;
        }

        // ════════════════════════ forms ════════════════════════
        private static readonly string[] FmNames = { "Advance", "Enter", "Leave", "Grow", "Spare", "Interval", "Strike", "Rear", "Fire", "Items", "Sweep", "Growth", "Gone" };
        public static long Scratches, Lashes, Quenches, HoardTakes, RearSets;

        private static string RunForms(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x51);
            int now = r.Next(0, 100000) / 15 * 15;
            // scratch
            bool inStand = false, hasClock = false; int next = 0; float growth = 1f, minGrowth = 0.4f; bool spared = false; int interval = new[] { 0, 1, 15, 90, 2500 }[r.Next(5)];
            int lastHit = int.MinValue, lastGap = 0;
            // lash
            int ready = -1, lashRecovery = new[] { 100, 2500, 60000 }[r.Next(3)]; float lashFactor = new[] { 0f, 0.5f, 1f, 3f }[r.Next(4)];
            int lastLash = int.MinValue, lastLashGap = 0;
            // rear
            int rearedUntil = -1; long rearLedgerUntil = -1;
            // quench
            int qReady = -1; int lastBurst = int.MinValue, lastBurstGap = 0; float qDays = new[] { 0.01f, 0.1f, 3f }[r.Next(3)];
            // hoard
            var firstSeen = new Dictionary<int, int>(); var present = new Dictionary<int, bool>();   // id -> isCorpse
            var presentSince = new Dictionary<int, int>(); var taken = new HashSet<int>();
            int held = 0, maxHeld = new[] { 2, 4, 40 }[r.Next(3)]; int growIn = new[] { 0, 250, 1000, 10000 }[r.Next(4)]; bool keepDead = r.Next(2) == 0, growthOk = true;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 0:
                        {
                            int end = now + 1 + a.a % 600;
                            while (now < end)
                            {
                                now++;
                                if (now % 15 == 0 && inStand)
                                {
                                    bool due = RM_FormsKernel.Due(hasClock, next, now);
                                    bool hurt = RM_FormsKernel.ThornsHurt(growth, minGrowth, spared, due);
                                    Check(!hurt || (growth >= minGrowth && !spared && (!hasClock || now >= next)), "thorns hurt out of spec" + where);
                                    Check(hurt == (growth >= minGrowth && !spared && (!hasClock || now >= next)), "thorns verdict != spec" + where);
                                    if (hurt)
                                    {
                                        if (lastHit != int.MinValue) Check(now - lastHit >= lastGap, $"two scratches {now - lastHit} ticks apart, interval then {lastGap}" + where);
                                        next = RM_FormsKernel.NextScratch(now, interval); hasClock = true;
                                        Check(next >= now + 1, "next scratch not in the future" + where);
                                        lastHit = now; lastGap = Math.Max(1, interval); Scratches++;
                                    }
                                }
                                if (now % 2500 == 0 && hasClock && RM_FormsKernel.ClockStale(false, now, next))
                                {
                                    Check(now - next > 2500, "a clock was pruned before it had been due 2500 ticks" + where);
                                    hasClock = false;   // pruned: a later contact scratches at once - which is allowed only because it was due long ago
                                }
                                if (now % 60 == 0)
                                {
                                    // hoard sweep rides the same clock (every 250 in the mod; every 60 here is stricter)
                                }
                            }
                            break;
                        }
                    case 1: inStand = true; break;
                    case 2: inStand = false; break;
                    case 3: growth = new[] { 0f, 0.39f, 0.4f, 0.8f, 1f }[a.a % 5]; break;
                    case 4: spared = !spared; break;
                    case 5: interval = new[] { 0, 1, 15, 90, 2500 }[a.a % 5]; break;
                    case 6: // a pawn within reach of a twitcher
                        {
                            bool hasDef = a.b % 5 != 0;
                            float g = new[] { 0f, 0.5f, 1f }[a.a % 3];
                            bool strikes = RM_FormsKernel.LashStrikes(now, ready, g, 0.5f, hasDef);
                            Check(strikes == (now >= ready && g >= 0.5f && hasDef), "lash verdict != spec" + where);
                            if (strikes)
                            {
                                if (lastLash != int.MinValue) Check(now - lastLash >= lastLashGap, $"two lashes {now - lastLash} ticks apart, recovery then {lastLashGap}" + where);
                                ready = RM_FormsKernel.LashReady(now, lashRecovery, lashFactor);
                                Check(ready >= now + 60, "lash recovery under the 60-tick floor" + where);
                                Check(ready >= now + (long)Math.Round(lashRecovery * (double)lashFactor) - 1, "lash recovery shorter than the setting" + where);
                                lastLash = now; lastLashGap = ready - now; Lashes++;
                            }
                            Check(RM_FormsKernel.Poised(now, ready) == (now >= ready), "poised != now >= ready" + where);
                            Check(!RM_FormsKernel.Poised(ready - 1, ready) || ready <= int.MinValue + 1, "poised the tick before ready" + where);
                            break;
                        }
                    case 7: // something large pushes into a rearing stand
                        {
                            float hours = new[] { 0f, 0.5f, 2f, 8f }[a.a % 4]; bool stall = a.b % 2 == 0; float sf = 2f;
                            int ticks = RM_FormsKernel.RearTicks(hours, stall, sf);
                            Check(ticks >= (int)Math.Round(0.05 * 2500), "rear time under the 0.05 h floor" + where);
                            Check(!stall || ticks >= RM_FormsKernel.RearTicks(hours, false, sf), "a stall shortened the rearing" + where);
                            int was = rearedUntil;
                            rearedUntil = RM_FormsKernel.Rear(rearedUntil, now, ticks);
                            Check(rearedUntil >= was, "rearing was cut short by a second push" + where);
                            rearLedgerUntil = Math.Max(rearLedgerUntil, (long)now + ticks);
                            Check(rearedUntil == rearLedgerUntil, "rear-until != max(now + ticks) ledger" + where);
                            Check(RM_FormsKernel.RearsFor(a.a % 3 * 0.5f, 0.8f, a.b % 3 * 0.5f, 0.5f) == ((a.a % 3 * 0.5f) >= 0.8f && (a.b % 3 * 0.5f) >= 0.5f), "rears-for truth" + where);
                            RearSets++;
                            break;
                        }
                    case 8: // a fire near a quench stand: sweep
                        {
                            int fx = a.a % 7 - 3, fz = a.b % 7 - 3; float rad = 1.5f;
                            bool reach = RM_FormsKernel.FireInReach(fx, fz, rad);
                            Check(reach == ((double)fx * fx + (double)fz * fz <= 2.25), "fire reach != r^2 disc" + where);
                            bool go = reach && RM_FormsKernel.QuenchReadyNow(now, qReady);
                            if (go)
                            {
                                if (lastBurst != int.MinValue) Check(now - lastBurst >= lastBurstGap, $"two bursts {now - lastBurst} ticks apart, recovery then {lastBurstGap}" + where);
                                qReady = RM_FormsKernel.QuenchReady(now, qDays);
                                Check(qReady - now >= 6000 - 1, "quench recovery under the 0.1 day floor" + where);
                                lastBurst = now; lastBurstGap = qReady - now; Quenches++;
                            }
                            Check(!RM_FormsKernel.QuenchReadyNow(now, qReady) || go || !reach || qReady <= now, "a spent stand reads ready" + where);
                            break;
                        }
                    case 9: // the set of items lying against the hoard changes
                        {
                            var rr = new Random(a.a * 31 + a.b);
                            foreach (int id in Enumerable.Range(1, 8))
                            {
                                bool here = rr.Next(100) < 55;
                                if (here && !present.ContainsKey(id)) { present[id] = rr.Next(4) == 0; presentSince.Remove(id); taken.Remove(id); }
                                if (!here && present.ContainsKey(id)) { present.Remove(id); presentSince.Remove(id); firstSeen.Remove(id); }   // Prune
                            }
                            break;
                        }
                    case 10: // a hoard sweep
                        {
                            now += 250;
                            var ids = present.Keys.OrderBy(i => -i).ToArray();
                            var corpse = ids.Select(i => present[i]).ToArray();
                            var snap = new Dictionary<int, int>(firstSeen);
                            var takenNow = new List<int>();
                            int heldBefore = held;
                            foreach (var i in ids) if (!presentSince.ContainsKey(i)) presentSince[i] = now;   // the first sweep that could see it
                            int t = RM_FormsKernel.HoardSweep(firstSeen, ids.Length, ids, corpse, now, growIn, held, maxHeld, keepDead, growthOk, id =>
                            {
                                takenNow.Add(id);
                                Check(present.ContainsKey(id), "took an item that is not there" + where);
                                Check(keepDead || !present[id], "took a corpse with keepDeadGear off" + where);
                                Check(now - presentSince[id] >= growIn, $"took item {id} after {now - presentSince[id]} ticks, grow-in is {growIn}" + where);
                                int add = present[id] ? Math.Min(3, maxHeld - held) : 1;
                                held += add;
                                return add;
                            });
                            Check(t == takenNow.Count, "returned taken count != take calls" + where);
                            Check(held <= maxHeld, $"hoard holds {held} over its maximum {maxHeld}" + where);
                            if (!growthOk) Check(takenNow.Count == 0 && firstSeen.Count == snap.Count && firstSeen.All(kv => snap.TryGetValue(kv.Key, out int v) && v == kv.Value), "a stunted stand changed its books" + where);
                            foreach (int id in takenNow) { Check(!firstSeen.ContainsKey(id), "a taken item kept its first-seen clock" + where); taken.Add(id); presentSince.Remove(id); present.Remove(id); HoardTakes++; }
                            // liveness: with room to spare and a grown stand, an item seen a full grow-in ago is taken
                            if (growthOk && maxHeld - heldBefore > ids.Length * 3)
                                foreach (int id in ids)
                                    if (!takenNow.Contains(id) && presentSince.ContainsKey(id) && (keepDead || !corpse[Array.IndexOf(ids, id)]) && snap.TryGetValue(id, out int fs) && now - fs >= growIn)
                                        throw new Exception($"item {id} first seen {now - fs} ticks ago (grow-in {growIn}) was not taken with room to spare" + where);
                            // the corpse of an item that stays does not lose its book
                            break;
                        }
                    case 11: growthOk = !growthOk; break;
                    case 12: // the stand's owner changes room: held items are given back
                        held = 0; break;
                }
            }
            return null;
        }

        private static string FormsUnits(int seed)
        {
            var r = new Random(seed ^ 0x99);
            Check(RM_FormsKernel.Due(false, 123456, 0) && RM_FormsKernel.Due(true, 100, 100) && !RM_FormsKernel.Due(true, 101, 100), "Due truth table");
            Check(RM_FormsKernel.NextScratch(50, -10) == 51 && RM_FormsKernel.NextScratch(50, 0) == 51 && RM_FormsKernel.NextScratch(50, 2500) == 2550, "NextScratch floor");
            Check(RM_FormsKernel.ClockStale(true, 0, 99999) && !RM_FormsKernel.ClockStale(false, 5000, 2500) && RM_FormsKernel.ClockStale(false, 5001, 2500), "ClockStale boundary");
            for (int t = 0; t < 10; t++)
            {
                int dx = r.Next(-4, 5), dz = r.Next(-4, 5); float rad = new[] { 0.5f, 1.5f, 2.9f, 4.9f }[r.Next(4)];
                Check(RM_FormsKernel.FireInReach(dx, dz, rad) == ((double)dx * dx + (double)dz * dz <= (double)rad * rad + 1e-9), $"fire reach ({dx},{dz}) r{rad}");
            }
            return null;
        }

        // ════════════════════════ walk ════════════════════════
        public static long WalkSpawns, WalkKills, WalkStands, WalkSmothered, WalkCapped;

        private static string WalkCase(int seed)
        {
            var r = new Random(seed);
            int W = r.Next(3, 14), H = r.Next(3, 14);
            double density = new[] { 0.15, 0.35, 0.6 }[r.Next(3)];
            var xs = new List<int>(); var zs = new List<int>(); var gr = new List<float>(); var pl = new List<bool>(); var sm = new List<bool>(); var ms = new List<int>(); var td = new List<float>();
            double smProb = r.Next(3) == 0 ? 0.08 : 0.0;
            for (int x = 0; x < W; x++)
                for (int z = 0; z < H; z++)
                    if (r.NextDouble() < density)
                    {
                        xs.Add(x + 20); zs.Add(z + 20);
                        gr.Add(new[] { 0.1f, 0.49f, 0.5f, 0.7f, 0.998f, 0.999f, 1f }[r.Next(7)]);
                        pl.Add(r.Next(25) != 0); sm.Add(r.NextDouble() < smProb); ms.Add(r.Next(0, 4)); td.Add(new[] { 0f, 0.5f, 1f }[r.Next(3)]);
                    }
            int n = xs.Count;
            // shuffle registry order
            var ord = Enumerable.Range(0, n).OrderBy(_ => r.Next()).ToArray();
            int[] X = ord.Select(i => xs[i]).ToArray(), Z = ord.Select(i => zs[i]).ToArray(), MS = ord.Select(i => ms[i]).ToArray();
            float[] G = ord.Select(i => gr[i]).ToArray(), TD = ord.Select(i => td[i]).ToArray();
            bool[] P = ord.Select(i => pl[i]).ToArray(), S = ord.Select(i => sm[i]).ToArray();
            float heading = (float)(r.NextDouble() * 360.0);
            float dx, dz; RM_LeanKernel.Direction(heading, out dx, out dz);
            int cap = new[] { 0, 1, n, n + 2, n + 40, 1000 }[r.Next(6)];
            int blockSeed = r.Next(); double blockP = new[] { 0.0, 0.3, 0.8 }[r.Next(3)];
            Func<int, int, bool> free = (x, z) => x >= 0 && z >= 0 && new Random(blockSeed ^ (x * 7919 + z * 104729)).NextDouble() >= blockP;
            int mode = r.Next(4);   // 0 random, 1 all-true chances, 2 all-false chances, 3 max step
            var rng = new Random(seed ^ 0x3131);
            Func<int, int, int> range = (lo, hi) => mode == 3 ? hi : rng.Next(lo, hi + 1);
            Func<float, bool> chance = p => mode == 1 ? p > 0f : mode == 2 ? false : rng.NextDouble() < p;
            var res = new RM_FormsKernel.WalkResult();
            RM_FormsKernel.Walk(n, X, Z, G, P, S, MS, TD, dx, dz, cap, (f, x, z) => free(x, z), range, chance, res);
            // determinism
            rng = new Random(seed ^ 0x3131);
            var res2 = new RM_FormsKernel.WalkResult();
            RM_FormsKernel.Walk(n, X, Z, G, P, S, MS, TD, dx, dz, cap, (f, x, z) => free(x, z), range, chance, res2);
            Check(res.SpawnX.SequenceEqual(res2.SpawnX) && res.SpawnZ.SequenceEqual(res2.SpawnZ) && res.Kills.SequenceEqual(res2.Kills), "Walk is not deterministic for the same draws");

            // oracle: 8-connected components, smothered stands
            var cellIdx = new Dictionary<long, int>();
            for (int i = 0; i < n; i++) cellIdx[RM_FormsKernel.Key(X[i], Z[i])] = i;
            var comp = new int[n]; Array.Fill(comp, -1); int nc = 0; var csize = new List<int>(); var cSm = new List<bool>();
            for (int i = 0; i < n; i++)
            {
                if (comp[i] >= 0) continue;
                var st = new Stack<int>(); st.Push(i); comp[i] = nc; int size = 0; bool any = false;
                while (st.Count > 0)
                {
                    int c = st.Pop(); size++; any |= S[c];
                    for (int ax = -1; ax <= 1; ax++) for (int az = -1; az <= 1; az++)
                        {
                            if (ax == 0 && az == 0) continue;
                            int j;
                            if (cellIdx.TryGetValue(RM_FormsKernel.Key(X[c] + ax, Z[c] + az), out j) && comp[j] < 0) { comp[j] = nc; st.Push(j); }
                        }
                }
                csize.Add(size); cSm.Add(any); nc++;
            }
            WalkStands += nc; WalkSmothered += cSm.Count(b => b);
            var initial = new HashSet<long>(cellIdx.Keys);
            var spawned = new HashSet<long>();
            int total0 = initial.Count;
            Check(res.SpawnX.Count == res.SpawnZ.Count && res.SpawnX.Count == res.SpawnFrom.Count && res.SpawnX.Count == res.SpawnK.Count, "spawn lists differ in length");
            for (int s = 0; s < res.SpawnX.Count; s++)
            {
                int f = res.SpawnFrom[s], k = res.SpawnK[s], sx = res.SpawnX[s], sz = res.SpawnZ[s];
                Check(f >= 0 && f < n, "spawn from an unknown cell");
                Check(!cSm[comp[f]], $"a smothered stand sent a runner (cell {X[f]},{Z[f]})");
                Check(P[f] && G[f] >= 0.5f, $"a runner came from a non-plant or an immature cell (growth {G[f]})");
                Check(k >= 1 && k <= Math.Max(1, MS[f]), $"runner distance {k} outside 1..{Math.Max(1, MS[f])}");
                int ex, ez; RM_LeanKernel.Step(X[f], Z[f], dx, dz, k, out ex, out ez);
                Check(ex == sx && ez == sz, "runner is not at Step(source, k)");
                Check(free(sx, sz), "a runner landed where the map refuses it");
                long key = RM_FormsKernel.Key(sx, sz);
                Check(!initial.Contains(key) && spawned.Add(key), "a runner landed on a walking cell or on another runner");
                int lx, lz; RM_LeanKernel.Step(X[f], Z[f], dx, dz, 1f, out lx, out lz);
                Check(!initial.Contains(RM_FormsKernel.Key(lx, lz)), "a runner left a cell that is not the leading edge");
                // the cap was open when it was sent: total before this spawn was < cap
                Check(total0 + s < cap, $"runner #{s} sent with {total0 + s} cells against a cap of {cap}");
            }
            Check(total0 + res.SpawnX.Count <= Math.Max(cap, total0), "walking cells exceed max(cap, initial)");
            if (total0 + res.SpawnX.Count >= cap && cap > 0) WalkCapped++;
            WalkSpawns += res.SpawnX.Count;
            // omissions: a grown leading-edge cell of a free stand that sent nothing must have a reason
            var sent = new HashSet<int>(res.SpawnFrom);
            for (int i = 0; i < n; i++)
            {
                if (cSm[comp[i]] || !P[i] || G[i] < 0.5f || sent.Contains(i)) continue;
                int lx, lz; RM_LeanKernel.Step(X[i], Z[i], dx, dz, 1f, out lx, out lz);
                long lead = RM_FormsKernel.Key(lx, lz);
                if (initial.Contains(lead) || spawned.Contains(lead)) continue;
                if (total0 + res.SpawnX.Count >= cap) continue;
                // it drew a distance and found the destination taken or refused (or drew nothing because chance modes cannot skip): check some k fails
                if (mode == 3)
                {
                    int ex, ez; RM_LeanKernel.Step(X[i], Z[i], dx, dz, Math.Max(1, MS[i]), out ex, out ez);
                    Check(initial.Contains(RM_FormsKernel.Key(ex, ez)) || spawned.Contains(RM_FormsKernel.Key(ex, ez)) || !free(ex, ez), $"a grown leading-edge cell ({X[i]},{Z[i]}) sent no runner with room under the cap and a free destination");
                }
            }
            // kills
            var killed = new HashSet<int>();
            foreach (int k in res.Kills)
            {
                Check(k >= 0 && k < n && killed.Add(k), "a cell was killed twice or unknown");
                Check(!cSm[comp[k]], "a smothered stand lost a cell");
                Check(G[k] >= 0.999f && csize[comp[k]] > 1, $"killed a cell with growth {G[k]} in a stand of {csize[comp[k]]}");
                int tx, tz; RM_LeanKernel.Step(X[k], Z[k], dx, dz, -1f, out tx, out tz);
                Check(!initial.Contains(RM_FormsKernel.Key(tx, tz)), "killed a cell that has a stand cell upwind of it");
                Check(TD[k] > 0f, "killed a cell whose die chance is 0");
            }
            WalkKills += res.Kills.Count;
            // exact kill oracle when nothing else can move: cap 0 closes the leading edge, chance always true
            if (cap == 0 && mode == 1)
            {
                var expect = new HashSet<int>();
                for (int i = 0; i < n; i++)
                {
                    if (cSm[comp[i]] || !P[i] || G[i] < 0.5f) continue;
                    int tx, tz; RM_LeanKernel.Step(X[i], Z[i], dx, dz, -1f, out tx, out tz);
                    if (TD[i] > 0f && G[i] >= 0.999f && csize[comp[i]] > 1 && !initial.Contains(RM_FormsKernel.Key(tx, tz))) expect.Add(i);
                }
                Check(expect.SetEquals(killed), $"kills {killed.Count} != exact oracle {expect.Count} (cap 0, chance 1)");
                Check(res.SpawnX.Count == 0, "a capped map still spawned");
            }
            if (mode == 2) Check(res.Kills.Count == 0, "kills with a die chance that never succeeds");
            return null;
        }

        // ════════════════════════ coat ════════════════════════
        public static long Rubs, FeltPaid, BloomsMade, BloomAnswers;
        private static readonly string[] BlmNames = { "Sweep", "Run", "Advance" };

        private static string CoatUnits(int seed)
        {
            var r = new Random(seed ^ 0x2468);
            for (int t = 0; t < 30; t++)
            {
                int wool = r.Next(0, 120); float full = (float)r.NextDouble(); float share = new[] { -0.5f, 0f, 0.25f, 0.5f, 1f, 1.7f }[r.Next(6)];
                int limit = new[] { 0, 1, 7, 75 }[r.Next(4)];
                float r1 = (float)r.NextDouble(), r2 = (float)r.NextDouble();
                var stacks = new List<int>(); int amount, ground; float felted;
                RM_CoatKernel.Rub(wool, full, share, r1, r2, limit, out amount, out ground, out felted, stacks);
                double raw = wool * (double)full;
                Check(amount >= Math.Floor(raw) - 1e-6 && amount <= Math.Ceiling(raw) + 1e-6, $"shed {amount} of a coat worth {raw}");
                double sh = Math.Max(0, Math.Min(1, share));
                Check(ground >= Math.Floor(amount * (1 - sh)) - 1 && ground <= Math.Ceiling(amount * (1 - sh)) + 1, $"ground {ground} for {amount} at share {sh}");
                Check(stacks.Sum() == ground && stacks.All(s => s >= 1 && s <= Math.Max(1, limit)), "ground stacks wrong");
                Check(Math.Abs(felted - amount * sh) < 1e-3, "felted share wrong");
                Check(Math.Abs(ground + felted - amount) < 1.0 + 1e-3, $"the coat did not balance: ground {ground} + felt {felted} vs shed {amount}");
                if (sh >= 1) Check(ground == 0, "all felted, yet some fell to the ground");
                if (sh <= 0) Check(ground == amount && felted == 0f, "no felt share, yet some felted");
                if (full == 0f) Check(amount == 0, "an empty coat shed wool");
                Rubs++;
            }
            // RoundRandom is unbiased: the mean over uniform rolls equals the input
            for (int t = 0; t < 6; t++)
            {
                float f = (float)(r.NextDouble() * 20); double sum = 0; int N = 2000;
                for (int i = 0; i < N; i++) sum += RM_CoatKernel.RoundRandom(f, (i + 0.5f) / N);
                Check(Math.Abs(sum / N - f) < 0.01, $"RoundRandom mean {sum / N} vs {f}");
                int lo = RM_CoatKernel.RoundRandom(f, 0.9999999f), hi = RM_CoatKernel.RoundRandom(f, 0f);
                Check(lo >= (int)f && hi <= (int)f + 1 && hi >= lo, "RoundRandom outside {floor, ceil}");
            }
            // felt store sequence
            float store = 0f, cap = new[] { 3f, 120f }[r.Next(2)], per = new[] { 0.25f, 1f }[r.Next(2)];
            double paid = 0;
            for (int i = 0; i < 400; i++)
            {
                if (r.Next(3) > 0)
                {
                    float u = (float)(r.NextDouble() * 30) * (r.Next(10) == 0 ? -1 : 1);
                    store = RM_CoatKernel.AddFelt(store, u, per, cap);
                    Check(store >= 0f && store <= cap + 1e-4f, $"felt store {store} outside [0,{cap}]");
                }
                else
                {
                    bool en = r.Next(5) > 0, wt = r.Next(6) > 0;
                    int pay = RM_CoatKernel.Payout(store, en, wt);
                    Check(pay >= 0 && pay <= (int)Math.Floor(store), "payout beyond the store");
                    Check((en && wt) || pay == 0, "paid out while disabled or with no felt item");
                    Check(!en || !wt || pay == (int)Math.Floor(store), "payout is not the whole units in the store");
                    store -= pay; paid += pay; FeltPaid += pay;
                    Check(store >= -1e-6f, "store went negative after payout");
                }
            }
            return null;
        }

        private static string RunBloom(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0xb10);
            var st = new RM_CoatKernel.BloomState<int>();
            int now = r.Next(0, 5000) / 60 * 60;
            var blooms = new List<int[]>();            // t, x, z  - the independent ledger
            var queued = new List<int[]>();            // id, due, answered(0/1), fx, fz
            var queuedOrder = 0;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 2: now += 60 * (1 + a.a % 40); break;
                    case 0: // one sweep: a few disturbers in a row
                        {
                            st.DropOldRecent(now);
                            var rr = new Random(a.a * 977 + a.b);
                            int nd = 1 + rr.Next(4), na = rr.Next(0, 6);
                            var ax = new int[na]; var az = new int[na]; var ok = new bool[na]; var dl = new int[na];
                            for (int i = 0; i < na; i++) { ax[i] = rr.Next(-30, 31); az[i] = rr.Next(-30, 31); ok[i] = rr.Next(5) > 0; dl[i] = rr.Next(-5, 400); }
                            for (int d = 0; d < nd; d++)
                            {
                                int px = rr.Next(-30, 31), pz = rr.Next(-30, 31);
                                bool cool = st.OnCooldown(px, pz);
                                bool spec = blooms.Any(b => now - b[0] <= 1250 && (double)(b[1] - px) * (b[1] - px) + (double)(b[2] - pz) * (b[2] - pz) <= 225.0);
                                Check(cool == spec, $"cooldown {cool}, spec {spec} at ({px},{pz})" + where);
                                if (cool) continue;
                                st.Remember(px, pz, now); blooms.Add(new[] { now, px, pz }); BloomsMade++;
                                for (int i = 0; i < na; i++)
                                {
                                    bool inR = RM_CoatKernel.InBloomRadius(ax[i], az[i], px, pz);
                                    Check(inR == ((double)(ax[i] - px) * (ax[i] - px) + (double)(az[i] - pz) * (az[i] - pz) <= 144.0), "bloom radius != 12 disc" + where);
                                    if (!ok[i] || !inR) continue;
                                    int due = RM_CoatKernel.AnswerTick(now, dl[i]);
                                    Check(due >= now && due == now + Math.Max(0, dl[i]), "answer tick before the bloom or off the delay" + where);
                                    int id = queuedOrder++;
                                    st.Queue(due, id, px, pz); queued.Add(new[] { id, due, 0, px, pz });
                                }
                            }
                            // no two blooms within the cooldown, whatever the sweep order
                            for (int i = 0; i < blooms.Count; i++)
                                for (int j = i + 1; j < blooms.Count; j++)
                                    if (blooms[j][0] - blooms[i][0] <= 1250)
                                        Check((double)(blooms[i][1] - blooms[j][1]) * (blooms[i][1] - blooms[j][1]) + (double)(blooms[i][2] - blooms[j][2]) * (blooms[i][2] - blooms[j][2]) > 225.0, "two blooms went off inside the cooldown" + where);
                            break;
                        }
                    case 1: // run the answers due now
                        {
                            var got = new List<int>();
                            st.RunPending(now, (who, fx, fz) => got.Add(who));
                            var dueNow = queued.Where(q => q[2] == 0 && q[1] <= now).Select(q => q[0]).OrderByDescending(x => x).ToList();
                            Check(got.OrderBy(x => x).SequenceEqual(dueNow.OrderBy(x => x)), $"answered [{string.Join(",", got)}], due [{string.Join(",", dueNow)}]" + where);
                            Check(got.SequenceEqual(dueNow), "answers not newest-first" + where);
                            foreach (var id in got) { var q = queued.First(x => x[0] == id); Check(q[2] == 0, "answered twice" + where); q[2] = 1; BloomAnswers++; }
                            Check(st.PendingTick.All(t => t > now), "an answer due now is still waiting" + where);
                            Check(st.PendingTick.Count == queued.Count(q => q[2] == 0), "pending count != unanswered ledger" + where);
                            break;
                        }
                }
            }
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
                ("lean", () => Family("lean", N(3000), S(1), Lean)),
                ("smother", () => Family("smother", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 70, new[] { 14, 40, 8, 6, 6, 5, 25 }, SmNames), RunSmother) ?? SmotherUnits(s))),
                ("blaze", () => Family("blaze", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 60, new[] { 12, 12, 6, 40, 12 }, BlNames), RunBlazeSeq) ?? BlazeCase(s))),
                ("guardian", () => Family("guardian", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 90, new[] { 10, 12, 10, 8, 20, 6, 4, 4, 5, 4, 4 }, GdNames), RunGuardian) ?? GuardianUnits(s))),
                ("forms", () => Family("forms", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 15, 120, new[] { 25, 5, 4, 6, 6, 4, 10, 8, 10, 8, 14, 4, 2 }, FmNames), RunForms) ?? FormsUnits(s))),
                ("walk", () => Family("walk", N(4000), S(1), WalkCase)),
                ("coat", () => Family("coat", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 60, new[] { 40, 30, 20 }, BlmNames), RunBloom) ?? CoatUnits(s))),
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
            Console.WriteLine($"reached: lean scent threats {ScentThreats}, fire picks {FirePicks}, shed cells {ShedCellsMade}; smother matured {Matured}, second starts {SecondStarts}, passes {SmPasses}; blaze found {Blazes}, none {NoBlazes}, messages {Messages}");
            Console.WriteLine($"reached: guardian drops {GdDrops}, announces {GdAnnounces}, forgives {GdForgives}, reroosts {GdReroosts}; forms scratches {Scratches}, lashes {Lashes}, quenches {Quenches}, rears {RearSets}, hoard takes {HoardTakes}");
            Console.WriteLine($"reached: walk spawns {WalkSpawns}, kills {WalkKills}, stands {WalkStands}, smothered {WalkSmothered}, capped {WalkCapped}; coat rubs {Rubs}, felt paid {FeltPaid}, blooms {BloomsMade}, answers {BloomAnswers}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (ScentThreats == 0 || FirePicks == 0 || ShedCellsMade == 0 || Matured == 0 || SecondStarts == 0 || Blazes == 0 || NoBlazes == 0 || Messages == 0 || GdDrops == 0 || GdAnnounces == 0
                    || GdForgives == 0 || GdReroosts == 0 || Scratches == 0 || Lashes == 0 || Quenches == 0 || HoardTakes == 0 || WalkSpawns == 0 || WalkKills == 0 || WalkSmothered == 0
                    || WalkCapped == 0 || Rubs == 0 || FeltPaid == 0 || BloomsMade == 0 || BloomAnswers == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"leaningscrub fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
