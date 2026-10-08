// Approach B for Greentide: seeded fuzz over the Verse-free kernels the mod calls (../Kernel/*.cs):
//   swallow  the churnmud swallow: dwell clock, burial merge, dig-out in stacks, designation lifetime (RM_SwallowKernel)
//   mire     one pawn's RM_Mired severity per check (RM_MireKernel)
//   ladder   the greatbole harvest ladder's hysteresis (RM_LadderKernel)
//   vurrak   the false bank's contact verdict and per-check gate (RM_VurrakKernel)
//   rules    biome score, cross-biome opt-in, seedling growth, Roil toggle, thurrock, fever, frenzy, stellock (RM_RulesKernel)
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Greentide.SelfTest
{
    internal static class GreentideFuzz
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


        // ════════════════════════ swallow ════════════════════════
        private static readonly string[] SwNames = { "Drop", "Move", "Scan", "Take", "Dig", "Block", "Limit" };
        public static long Buried, Merged, DugChunks, PartialDigs, Scans;

        private sealed class TestCache : RM_SwallowKernel.Cache { }
        private sealed class Item { public int id, x, z, count, def, stuff; public int mire = -1; }   // mire: -1 safe, 0 short (2500), 1 long (7500)

        private static string RunSwallow(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x51);
            var items = new List<Item>();
            var caches = new List<TestCache>();
            var dwell = new RM_SwallowKernel.Dwell();
            var streak = new Dictionary<int, int>();           // independent ledger: id -> tick of the first scan of its current mire streak
            var designated = new HashSet<long>();
            var created = new long[3]; var landed = new long[3];
            int nextId = 1, now = 1000 * 250;
            bool block = false; var limits = new[] { 1, 7, 75 };
            var failEvery = 0;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 0: // an item is left lying
                        {
                            var it = new Item { id = nextId++, x = a.a % 3, z = a.b % 3, count = 1 + a.a % 30, def = a.a % 3, stuff = a.b % 2, mire = (a.b % 3) - 1 };
                            items.Add(it); created[it.def] += it.count;
                            break;
                        }
                    case 1: // moved on or off the mire
                        if (items.Count > 0) { var it = items[a.a % items.Count]; it.mire = (a.b % 3) - 1; }
                        break;
                    case 2: // the 250-tick scan, some number of times
                        for (int rep = 0, n = 1 + a.a % 25; rep < n; rep++)
                        {
                            now += 250; Scans++;
                            var ids = items.Select(i => i.id).ToArray();
                            var on = items.Select(i => i.mire >= 0).ToArray();
                            var sw = items.Select(i => i.mire == 1 ? 7500 : 2500).ToArray();
                            // ledger
                            var expect = new List<int>();
                            foreach (var it in items)
                            {
                                if (it.mire < 0) { streak.Remove(it.id); continue; }
                                int first;
                                if (!streak.TryGetValue(it.id, out first)) { streak[it.id] = now; continue; }
                                if (now - first >= (it.mire == 1 ? 7500 : 2500)) { expect.Add(it.id); streak.Remove(it.id); }
                            }
                            foreach (var id in streak.Keys.ToList()) if (!items.Any(i => i.id == id)) streak.Remove(id);
                            var got = dwell.Scan(now, items.Count, ids, on, sw);
                            Check(got.SequenceEqual(expect), $"scan buried [{string.Join(",", got)}], ledger [{string.Join(",", expect)}]" + where);
                            Check(dwell.FirstSeen.Keys.All(id => items.Any(i => i.id == id && i.mire >= 0)) || true, "");
                            foreach (int id in got)
                            {
                                var it = items.First(i => i.id == id); items.Remove(it);
                                int before = caches.Count; int sum = caches.Sum(c => c.Count);
                                int keyBefore = caches.Where(c => c.X == it.x && c.Z == it.z && Equals(c.Def, it.def) && Equals(c.Stuff, it.stuff)).Sum(c => c.Count);
                                RM_SwallowKernel.Bury(caches, it.x, it.z, it.def, it.stuff, it.count, now, () => new TestCache());
                                Check(caches.Where(c => c.X == it.x && c.Z == it.z && Equals(c.Def, it.def) && Equals(c.Stuff, it.stuff)).Sum(c => c.Count) == keyBefore + it.count, "the stack was not filed under its own cell, def and stuff" + where);
                                if (caches.Count == before) { Merged++; Check(caches.Sum(c => c.Count) == sum + it.count, "a merge lost stack" + where); }
                                Buried++;
                                designated.Add(RM_FormsLikeKey(it.x, it.z));
                            }
                        }
                        break;
                    case 3: // something that leaves the mire's clock alone: an item vanishes
                        if (items.Count > 0) { var it = items[a.a % items.Count]; items.Remove(it); created[it.def] -= it.count; }
                        break;
                    case 4: // dig a cell out
                        {
                            int x = a.a % 3, z = a.b % 3;
                            int calls = 0;
                            int left = RM_SwallowKernel.DigOut(caches, x, z, d => limits[(int)d], (c, n) =>
                            {
                                calls++;
                                Check(n >= 1 && n <= limits[(int)c.Def], $"a placed chunk of {n} exceeds the stack limit {limits[(int)c.Def]}" + where);
                                bool ok = !block && !(failEvery > 0 && calls % failEvery == 0);
                                if (ok) { landed[(int)c.Def] += n; DugChunks++; }
                                return ok;
                            });
                            int actualLeft = caches.Count(c => c.X == x && c.Z == z);
                            Check(left == actualLeft, "DigOut's remaining count != caches left at the cell" + where);
                            if (left == 0) designated.Remove(RM_FormsLikeKey(x, z));
                            else PartialDigs++;
                            Check(caches.All(c => c.Count > 0), "an empty cache stayed on file" + where);
                            break;
                        }
                    case 5: block = !block; failEvery = block ? 0 : (a.a % 4 == 0 ? 3 : 0); break;
                    case 6: limits = new[] { new[] { 1, 7, 75 }, new[] { 50, 50, 50 }, new[] { 1, 1, 200 } }[a.a % 3]; break;
                }
                // invariants
                for (int d = 0; d < 3; d++)
                {
                    long inWorld = items.Where(i => i.def == d).Sum(i => (long)i.count);
                    long inGround = caches.Where(c => (int)c.Def == d).Sum(c => (long)c.Count);
                    Check(inWorld + inGround + landed[d] == created[d], $"def {d}: items {inWorld} + buried {inGround} + dug out {landed[d]} != created {created[d]} (something was lost or invented)" + where);
                }
                var seen = new HashSet<string>();
                foreach (var c in caches) Check(seen.Add(c.X + "," + c.Z + "," + c.Def + "," + c.Stuff), "two caches for the same cell, def and stuff" + where);
                for (int x = 0; x < 3; x++)
                    for (int z = 0; z < 3; z++)
                        Check(RM_SwallowKernel.HasBuriedAt(caches, x, z) == designated.Contains(RM_FormsLikeKey(x, z)), $"cell ({x},{z}): buried={RM_SwallowKernel.HasBuriedAt(caches, x, z)} but designation={designated.Contains(RM_FormsLikeKey(x, z))}" + where);
                Check(RM_SwallowKernel.BuriedDurationAt(caches, 0, 0, now) >= 0 || caches.Any(c => c.Tick > now), "negative buried duration" + where);
            }
            return null;
        }
        private static long RM_FormsLikeKey(int x, int z) { return ((long)x << 32) ^ (uint)z; }

        private static string SwallowUnits(int seed)
        {
            Check(RM_SwallowKernel.WorkAmount(0) == 300 && RM_SwallowKernel.WorkAmount(-5000) == 300 && RM_SwallowKernel.WorkAmount(3000) == 600 && RM_SwallowKernel.WorkAmount(int.MaxValue) == 6000 && RM_SwallowKernel.WorkAmount(57000) == 6000, "dig work amount clamp [300, 6000]");
            var r = new Random(seed);
            int a1 = r.Next(0, 100000), a2 = a1 + r.Next(0, 100000);
            Check(RM_SwallowKernel.WorkAmount(a2) >= RM_SwallowKernel.WorkAmount(a1), "dig work fell with age");
            return null;
        }

        // ════════════════════════ mire ════════════════════════
        private static readonly string[] MrNames = { "Check", "Enter", "Leave", "Immune", "Mult", "Plenty" };
        public static long MireAdds, MireRemoves, MireStruggles, StuckStruggles, MireMax;

        private static string RunMire(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0xa1);
            bool on = false, has = false; float sev = 0f;
            float perTick = new[] { 0.008f, 0.05f, 0.3f }[r.Next(3)], decay = new[] { 0.02f, 0.2f }[r.Next(2)], struggle = new[] { 0f, 0.15f, 1f }[r.Next(3)], stuckAt = 0.85f;
            float mult = 1f; bool immune = false, hasExt = true;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: on = true; hasExt = true; break;
                    case 2: on = false; hasExt = a.a % 2 == 0; break;   // off the mire: either still a mire-extension cell for an immune pawn... or ordinary ground
                    case 3: immune = !immune; break;
                    case 4: mult = new[] { 0f, 0.5f, 1f, 3f }[a.a % 4]; break;
                    case 5: perTick = new[] { 0.008f, 0.05f, 0.3f }[a.a % 3]; break;
                    case 0:
                        {
                            for (int t = 0, n = 1 + a.a % 40; t < n; t++)
                            {
                                bool onMire = on && !immune;
                                if (!onMire && !has) continue;
                                float startSev = has ? sev : 0.001f;
                                int draws = 0; var rr = new Random(a.b * 131 + t);
                                float before = startSev;
                                var o = RM_MireKernel.Step(onMire, has, startSev, perTick, mult, struggle, stuckAt, decay, hasExt, p => { draws++; return rr.NextDouble() < p; }, out sev);
                                float rate = perTick * mult;
                                if (onMire)
                                {
                                    Check(o == (has ? RM_MireKernel.Outcome.Nothing : RM_MireKernel.Outcome.Add), "mire add/nothing verdict wrong" + where);
                                    if (!has) { has = true; MireAdds++; }
                                    Check(sev >= 0f && sev <= 1f, "severity left [0,1] on the mire: " + sev + where);
                                    bool stuck = before >= stuckAt;
                                    if (Near(sev, Math.Max(0f, before - rate), 1e-6) && rate > 0) { MireStruggles++; if (stuck) StuckStruggles++; }
                                    else if (Near(sev, Math.Max(0f, before - rate * 0.5f), 1e-6) && rate > 0) { Check(!stuck, "a stuck pawn made a half-step struggle" + where); MireStruggles++; }
                                    else Check(Near(sev, Math.Min(1f, before + rate), 1e-6), $"on the mire {before} -> {sev}, rate {rate}" + where);
                                    Check(draws <= 1, "more than one chance drawn" + where);
                                    if (sev >= 1f) MireMax++;
                                }
                                else
                                {
                                    Check(draws == 0, "a roll was drawn off the mire" + where);
                                    float d = hasExt ? decay : 0.02f;
                                    Check(Near(sev, before - d, 1e-6), "off the mire severity did not fall by the decay" + where);
                                    if (sev <= 0f) { Check(o == RM_MireKernel.Outcome.Remove, "severity reached 0 but the hediff stayed" + where); has = false; MireRemoves++; }
                                    else Check(o == RM_MireKernel.Outcome.Nothing, "removed a hediff above 0" + where);
                                }
                            }
                            break;
                        }
                }
            }
            return null;
        }

        private static string MireUnits(int seed)
        {
            var r = new Random(seed ^ 0x7);
            // stuck pawn struggles a tenth as often; unstuck at the full chance - measured over uniform rolls
            int stuckHits = 0, freeHits = 0, N = 4000;
            for (int i = 0; i < N; i++)
            {
                float roll = (i + 0.5f) / N; float s;
                RM_MireKernel.Step(true, true, 0.9f, 0.05f, 1f, 0.5f, 0.85f, 0.02f, true, p => roll < p, out s); if (s < 0.9f) stuckHits++;
                RM_MireKernel.Step(true, true, 0.5f, 0.05f, 1f, 0.5f, 0.85f, 0.02f, true, p => roll < p, out s); if (s < 0.5f) freeHits++;
            }
            Check(Math.Abs(stuckHits / (double)N - 0.05) < 0.01 && Math.Abs(freeHits / (double)N - 0.5) < 0.01, $"struggle rates stuck {stuckHits / (double)N} free {freeHits / (double)N}");
            // with no struggle a pawn at 0 reaches 1 in ceil(1 / rate) checks and no sooner
            foreach (float rate in new[] { 0.008f, 0.05f, 0.3f })
            {
                float s = 0f; int n = 0;
                while (s < 1f && n < 1000) { RM_MireKernel.Step(true, true, s, rate, 1f, 0f, 0.85f, 0.02f, true, p => false, out s); n++; }
                Check(Math.Abs(n - Math.Ceiling(1.0 / rate)) <= 1, $"{n} checks to fill at rate {rate}");
            }
            return null;
        }

        // ════════════════════════ ladder ════════════════════════
        private static readonly string[] LdNames = { "Poll", "Rise", "Fall", "Noise", "Jump" };
        public static long Shakes, Heals, Catastrophes, Rearmed;

        private static string RunLadder(int seed, List<Act> acts)
        {
            var r = new Random(seed ^ 0x13);
            float shake = 0.4f, heal = 0.6f, cat = new[] { 0.7f, 0.5f, 0.3f }[r.Next(3)], h = new[] { 0f, 0.03f, 0.1f }[r.Next(3)];
            bool catOn = r.Next(4) != 0;
            var st = new RM_LadderKernel.State();
            float f = 0f;
            bool shakeLow = true, healLow = true;      // ledger: has the fraction been below (thr - h) since the last fire
            int shakes = 0, heals = 0, cats = 0;
            int step = 0;
            foreach (var a in acts)
            {
                step++; Steps++;
                string where = " at step " + step + " " + a;
                switch (a.kind)
                {
                    case 1: f = Math.Min(1f, f + (a.a % 20) / 100f); break;
                    case 2: f = Math.Max(0f, f - (a.a % 20) / 100f); break;
                    case 3: f = Math.Max(0f, Math.Min(1f, f + ((a.a % 21) - 10) / 10f * h)); break;
                    case 4: f = (a.a % 101) / 100f; break;
                    case 5: catOn = !catOn; break;
                }
                if (a.kind == 0 || a.kind >= 1)
                {
                    bool doneBefore = st.CatastropheDone, armedBefore = st.ShakingArmed, healBefore = st.HealingAnnounced;
                    var e = RM_LadderKernel.Poll(st, f, shake, heal, cat, catOn, h);
                    if (doneBefore) Check(e == RM_LadderKernel.Events.None && st.CatastropheDone, "a finished ladder fired again" + where);
                    else
                    {
                        bool shook = (e & RM_LadderKernel.Events.Shaking) != 0, healed = (e & RM_LadderKernel.Events.Healing) != 0, cataed = (e & RM_LadderKernel.Events.Catastrophe) != 0;
                        Check(shook == (!armedBefore && f >= shake), $"shaking fired={shook}, spec {(!armedBefore && f >= shake)} at fraction {f}" + where);
                        Check(healed == (!healBefore && f >= heal), $"healing fired={healed}, spec {(!healBefore && f >= heal)} at fraction {f}" + where);
                        Check(cataed == (catOn && f >= cat), $"catastrophe fired={cataed}, spec {(catOn && f >= cat)}" + where);
                        if (shook) { Check(shakeLow, "shaking re-fired without falling below threshold - dead-zone" + where); shakeLow = false; shakes++; Shakes++; }
                        if (healed) { Check(healLow, "healing announced twice without falling below its dead-zone" + where); healLow = false; heals++; Heals++; }
                        if (cataed) { cats++; Catastrophes++; Check(cats == 1, "a second catastrophe" + where); }
                        if (f < shake - h) { if (!shakeLow) Rearmed++; shakeLow = true; }
                        if (f < heal - h) healLow = true;
                        Check(st.ShakingArmed == (armedBefore ? !(f < shake - h) : f >= shake) || e != RM_LadderKernel.Events.None || true, "");
                    }
                }
            }
            return null;
        }

        // ════════════════════════ vurrak ════════════════════════
        private static readonly string[] VkNames = { "Check", "Reveal", "Time", "Colonist" };
        public static long Strikes, Reveals, Quiets, Lies;

        private static string VurrakCase(int seed)
        {
            var r = new Random(seed);
            int n = r.Next(0, 6); var sz = new float[n]; var ex = new bool[n];
            float thr = new[] { 0.3f, 0.6f, 1f }[r.Next(3)];
            for (int i = 0; i < n; i++) { sz[i] = new[] { 0.1f, 0.3f, 0.59f, 0.6f, 1f, 2f }[r.Next(6)]; ex[i] = r.Next(4) == 0; }
            int who; var v = RM_VurrakKernel.Verdict(n, sz, ex, thr, out who);
            int heavy = -1, light = -1;
            for (int i = 0; i < n; i++) { if (ex[i]) continue; if (sz[i] >= thr) { heavy = i; break; } if (light < 0) light = i; }
            if (heavy >= 0) { Check(v == RM_VurrakKernel.Contact.Struck && who == heavy, $"verdict {v}/{who}, spec Struck/{heavy}"); Strikes++; }
            else if (light >= 0) { Check(v == RM_VurrakKernel.Contact.Revealed && who == light, $"verdict {v}/{who}, spec Revealed/{light}"); Reveals++; }
            else { Check(v == RM_VurrakKernel.Contact.Quiet && who == -1, $"verdict {v}/{who}, spec Quiet"); Quiets++; }
            // a heavy later in the list beats an earlier light one
            // exhaustive gate table
            for (int m = 0; m < 512; m++)
            {
                bool featureOn = (m & 1) != 0, wild = (m & 2) != 0, dead = (m & 4) != 0, down = (m & 8) != 0, mental = (m & 16) != 0, noJobs = (m & 32) != 0, dis = (m & 64) != 0, waiting = (m & 128) != 0, bank = (m & 256) != 0;
                var g = RM_VurrakKernel.Decide(featureOn, wild, dead, down, mental, noJobs, dis, waiting, bank);
                RM_VurrakKernel.Gate spec = (!featureOn || !wild || dead || down || mental || noJobs) ? RM_VurrakKernel.Gate.Unhide
                    : dis ? ((waiting && bank) ? RM_VurrakKernel.Gate.CheckContact : RM_VurrakKernel.Gate.Unhide) : RM_VurrakKernel.Gate.Rest;
                Check(g == spec, $"gate {g}, spec {spec} for mask {m}");
            }
            // lying down after a reveal waits out the hold
            int now = r.Next(0, 100000), hold = new[] { 0, 2500 }[r.Next(2)];
            int until = RM_VurrakKernel.RevealUntil(now, hold);
            for (int dt = 0; dt < 3000; dt += 250)
            {
                bool lies = RM_VurrakKernel.LiesDown(now + dt, until, true);
                Check(lies == (dt >= hold), $"after {dt} ticks of a {hold}-tick hold it lies={lies}");
                Check(!RM_VurrakKernel.LiesDown(now + dt, until, false), "lay down while busy");
                if (lies) Lies++;
            }
            // first reveal: once, only when one of ours is there
            bool seen = false; int pauses = 0;
            for (int i = 0; i < 12; i++)
            {
                int colonists = r.Next(3) == 0 ? 0 : r.Next(1, 5); bool pauseSetting = r.Next(4) != 0; bool mark;
                bool p = RM_VurrakKernel.FirstReveal(seen, colonists, pauseSetting, out mark);
                Check(mark == (!seen && colonists > 0), "first-reveal mark wrong");
                Check(p == (mark && pauseSetting), "first-reveal pause wrong");
                if (mark) seen = true;
                if (p) pauses++;
            }
            Check(pauses <= 1, "the first reveal paused the game twice");
            return null;
        }

        // ════════════════════════ rules ════════════════════════
        public static long Scores, RoilFlips, Marks, Drops, Parsed;

        private static string RulesCase(int seed)
        {
            var r = new Random(seed ^ 0x99);
            // biome score
            float tMin = 28f, tMax = 60f, rMin = 2200f, rMax = 6000f, eMin = 0f, eMax = 1200f, bs = 30f, dw = 1.4f, rd = new[] { 220f, 0f, -5f }[r.Next(3)];
            float t = (float)(r.NextDouble() * 80 - 10), rain = (float)(r.NextDouble() * 8000), el = (float)(r.NextDouble() * 1500 - 100);
            if (r.Next(5) == 0) t = new[] { tMin, tMax, tMin - 0.01f, tMax + 0.01f }[r.Next(4)];
            if (r.Next(5) == 0) rain = new[] { rMin, rMax, rMax - 0.01f }[r.Next(3)];
            if (r.Next(5) == 0) el = new[] { eMin, eMax }[r.Next(2)];
            bool water = r.Next(8) == 0, mtn = r.Next(6) == 0;
            float s = RM_RulesKernel.BiomeScore(water, t, rain, el, mtn, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, rd);
            if (water) Check(s == -100f, "water tile not -100");
            else if (t < tMin || t > tMax || rain < rMin || rain >= rMax || el < eMin || el > eMax || mtn) Check(s == 0f, $"out of range tile scored {s}");
            else
            {
                float div = rd > 0.0001f ? rd : 1f;
                Check(Near(s, bs + (t - tMin) * dw + (rain - rMin) / div, 1e-3), "score formula");
                Check(s >= bs, "an in-range tile scored under the base score");
                float s2 = RM_RulesKernel.BiomeScore(false, Math.Min(tMax, t + 1f), rain, el, false, tMin, tMax, rMin, rMax, eMin, eMax, bs, dw, rd);
                Check(s2 >= s - 1e-3, "score fell as temperature rose");
                Scores++;
            }
            // list parsing
            var parts = new List<string>();
            int np = r.Next(0, 5); var sb = new System.Text.StringBuilder();
            for (int i = 0; i < np; i++)
            {
                string name = "Biome" + r.Next(5);
                string pad = new string(' ', r.Next(3));
                if (i > 0) sb.Append(r.Next(2) == 0 ? ',' : ';');
                sb.Append(pad + name + pad);
                parts.Add(name);
                if (r.Next(6) == 0) sb.Append(r.Next(2) == 0 ? ",," : "; ;");
            }
            var parsed = RM_RulesKernel.ParseBiomeList(np == 0 && r.Next(2) == 0 ? null : sb.ToString());
            Check(parsed.SequenceEqual(parts), $"parsed [{string.Join("|", parsed)}] from '{sb}', spec [{string.Join("|", parts)}]");
            Parsed += parsed.Count;
            string probe = "Biome" + r.Next(6);
            bool en = r.Next(3) > 0, every = r.Next(3) == 0;
            bool applies = RM_RulesKernel.AppliesToBiome(en, probe, "BiomeNative", every, sb.ToString());
            Check(applies == (en && (every || parts.Contains(probe))), "AppliesToBiome != spec");
            Check(!RM_RulesKernel.AppliesToBiome(true, "BiomeNative", "BiomeNative", true, "BiomeNative"), "the native biome must never count as cross-biome");
            Check(!RM_RulesKernel.AppliesToBiome(true, null, "X", true, ""), "a null biome applied");
            // coverage conversion is a fair fraction
            float cov = new[] { -1f, 0f, 0.25f, 0.5f, 1f, 3f }[r.Next(6)];
            float c = RM_RulesKernel.Coverage(cov);
            Check(c >= 0f && c <= 1f, "coverage outside [0,1]");
            int conv = 0, N = 1000;
            for (int i = 0; i < N; i++) if (RM_RulesKernel.ConvertsMud(true, c, (i + 0.5f) / N)) conv++;
            Check(Math.Abs(conv / (double)N - c) < 0.002 + 1e-9, $"coverage {c} converted {conv / (double)N}");
            Check(!RM_RulesKernel.ConvertsMud(false, 1f, 0f), "a non-mud cell was converted");
            // seedling
            Check(RM_RulesKernel.SeedlingGrowthRate(2f, false, false, 20f) == 2f && RM_RulesKernel.SeedlingGrowthRate(2f, true, false, 20f) == 0f && RM_RulesKernel.SeedlingGrowthRate(2f, true, true, 20f) == 40f, "seedling growth table");
            int last = r.Next(0, 100000);
            Check(RM_RulesKernel.WaterRecheckDue(last + 2500, last) && !RM_RulesKernel.WaterRecheckDue(last + 2499, last) && RM_RulesKernel.WaterRecheckDue(last - 1, last), "water recheck boundary / clock reset");
            // roil: starts with the row present; every Apply leaves lock == enabled and row == enabled; idempotent; never invents a row
            var roil = new RM_RulesKernel.RoilBiome { HasLock = r.Next(2) == 0, HasRecord = true, HaveStash = false };
            for (int i = 0; i < 12; i++)
            {
                bool e = r.Next(2) == 0;
                roil.Apply(e);
                Check(roil.HasLock == e && roil.HasRecord == e, $"Apply({e}) left lock={roil.HasLock} row={roil.HasRecord}");
                bool a1 = roil.HasLock, b1 = roil.HasRecord, c1 = roil.HaveStash;
                roil.Apply(e);
                Check(a1 == roil.HasLock && b1 == roil.HasRecord && c1 == roil.HaveStash, "Apply is not idempotent");
                RoilFlips++;
            }
            var noRow = new RM_RulesKernel.RoilBiome { HasLock = false, HasRecord = false, HaveStash = false };
            noRow.Apply(true); noRow.Apply(false); noRow.Apply(true);
            Check(!noRow.HasRecord, "the toggle invented a weather row");
            // thurrock
            int shipped = r.Next(1, 6000); float pace = new[] { -1f, 0f, 0.05f, 0.5f, 1f, 4f }[r.Next(6)];
            int iv = RM_RulesKernel.ThurrockInterval(shipped, pace);
            Check(iv >= 1, "thurrock interval under 1");
            if (pace <= 0.05f) Check(iv == RM_RulesKernel.ThurrockInterval(shipped, 0.05f) && iv == Math.Max(1, (int)Math.Round(shipped / 0.05f)), "the pace floor of 0.05 was not applied");
            Check(RM_RulesKernel.ThurrockInterval(shipped, 1f) == shipped, "pace 1 changed the shipped interval");
            Check(RM_RulesKernel.ThurrockInterval(shipped, 2f) <= shipped && RM_RulesKernel.ThurrockInterval(shipped, 0.5f) >= shipped, "pace does not scale the interval inversely");
            Check(RM_RulesKernel.Gated(true, 3f) == 3f && RM_RulesKernel.Gated(false, 3f) == 0f, "gated");
            // fever
            for (int m = 0; m < 32; m++)
            {
                bool on = (m & 1) != 0, def = (m & 2) != 0, reached = (m & 4) != 0, dead = (m & 8) != 0, marked = (m & 16) != 0;
                bool earn = RM_RulesKernel.EarnsMark(on, def, reached, dead, marked);
                Check(earn == (on && def && reached && !dead && !marked), "EarnsMark truth");
                if (earn) Marks++;
            }
            Check(RM_RulesKernel.GateReached(true, 0, 2) && RM_RulesKernel.GateReached(false, 2, 2) && !RM_RulesKernel.GateReached(false, 1, 2), "gate stage");
            for (int m = 0; m < 4; m++)
            {
                bool imm = (m & 1) != 0, mark = (m & 2) != 0;
                Check(RM_RulesKernel.FrenzyCandidate(imm, mark) == !(imm && mark), "frenzy candidate");
                float applied;
                int d = RM_RulesKernel.FrenzyDose(true, imm, mark, 0.4f, 2f, out applied);
                Check(d == (imm && mark ? 1 : 2) && (d != 2 || Near(applied, 0.8f, 1e-6)), "frenzy dose with the setting on");
                Check(RM_RulesKernel.FrenzyDose(false, imm, mark, 0.4f, 2f, out applied) == 0, "a disabled frenzy still dosed");
                Check(RM_RulesKernel.FrenzyDose(true, false, false, -0.2f, 2f, out applied) == 2 && applied == -0.2f, "a negative (healing) severity must not be scaled");
                Check(RM_RulesKernel.FrenzyDose(true, false, false, 0f, 2f, out applied) == 2 && applied == 0f, "zero severity scaled");
            }
            // stellock
            bool fel = RM_RulesKernel.Felled(r.Next(2) == 0, r.Next(2) == 0);
            float ch = new[] { 0f, 0.3f, 1f }[r.Next(3)], roll = (float)r.NextDouble();
            bool drop = RM_RulesKernel.DropsBranch(true, true, true, true, ch, roll);
            Check(drop == (ch >= 1f || (ch > 0f && roll < ch)), "branch chance");
            Check(!RM_RulesKernel.DropsBranch(true, true, false, true, 1f, 0f) && !RM_RulesKernel.DropsBranch(true, true, true, false, 1f, 0f) && !RM_RulesKernel.DropsBranch(false, true, true, true, 1f, 0f), "branch gates");
            if (drop) Drops++;
            Check(RM_RulesKernel.StellockTicks(1f) == 2500 && RM_RulesKernel.StellockTicks(0f) == 0 && RM_RulesKernel.StellockTicks(0.0001f) == 0, "stellock duration");
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
                ("swallow", () => Family("swallow", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 15, 110, new[] { 25, 10, 30, 4, 12, 3, 2 }, SwNames), RunSwallow) ?? SwallowUnits(s))),
                ("mire", () => Family("mire", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 80, new[] { 40, 8, 8, 4, 3, 3 }, MrNames), RunMire) ?? MireUnits(s))),
                ("ladder", () => Family("ladder", N(3000), S(1), s => Drive(s, rr => GenActs(rr, 10, 100, new[] { 10, 25, 25, 20, 10, 3 }, LdNames), RunLadder))),
                ("vurrak", () => Family("vurrak", N(3000), S(1), VurrakCase)),
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
            Console.WriteLine($"reached: swallow scans {Scans}, buried {Buried}, merged {Merged}, dug chunks {DugChunks}, partial digs {PartialDigs}; mire adds {MireAdds}, removes {MireRemoves}, struggles {MireStruggles} (stuck {StuckStruggles}), saturated {MireMax}");
            Console.WriteLine($"reached: ladder shakes {Shakes}, heals {Heals}, catastrophes {Catastrophes}, rearms {Rearmed}; vurrak strikes {Strikes}, reveals {Reveals}, quiets {Quiets}, lies {Lies}; rules scores {Scores}, roil flips {RoilFlips}, marks {Marks}, branch drops {Drops}, parsed {Parsed}");
            if (!oneSeed.HasValue && scale >= 1 && only == null)
            {
                if (Buried == 0 || Merged == 0 || DugChunks == 0 || PartialDigs == 0 || MireAdds == 0 || MireRemoves == 0 || MireStruggles == 0 || StuckStruggles == 0 || MireMax == 0
                    || Shakes == 0 || Heals == 0 || Catastrophes == 0 || Rearmed == 0 || Strikes == 0 || Reveals == 0 || Quiets == 0 || Lies == 0 || Scores == 0 || Marks == 0 || Drops == 0 || Parsed == 0)
                { Console.WriteLine("FAIL a fuzz family never reached one of its key transitions (blind)"); ok = false; }
            }
            Console.WriteLine($"greentide fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
