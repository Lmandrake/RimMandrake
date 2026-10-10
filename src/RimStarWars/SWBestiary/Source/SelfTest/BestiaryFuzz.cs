// Approach B for SWBestiary: seeded fuzz over the Verse-free kernels the mod assemblies call:
//   ../Livestock/Kernel/RSW_LivestockKernel.cs        kiln   the onnik's dose ledger, cooldown and cooling
//                                                      grief  the moornak's join timer, hidden ledger, unsettled hediff and release
//   ../BeastMechanics/Kernel/RSW_BeastKernel.cs        eat    the ferroclaw's bites, hunger gates and the food-block prefix
//                                                      hoard  the scrap bird: eligibility, nearest nest, nest cells and caps, takeable scrap
//                                                      toxin  the norphea's need: rise, fall, thresholds, hediff stage, clamp
//                                                      spew   the fuel-spew cone geometry
//                                                      ability the innate-ability grant steps
//   ../JawaIkee/Kernel/RSW_IkeeKernel.cs               ikee   the creep / comfort thought stage and radius
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.StarWars.JawaIkee;
using RimMandrake.StarWars.Livestock;
using RimMandrake.StarWars.SWBestiary;

namespace RimMandrake.StarWars.SWBestiary.SelfTest
{
    internal static class BestiaryFuzz
    {
        public static long Cases, Steps, Fires, Good, Bad, Cooled, Joins, Releases, Spiked, Bites, Eaten, Nests, Builds, Refused, Withdrawals, Spews, ShapesChecked;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

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

        private struct Act
        {
            public int kind, a, b, c; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + "," + c + (f ? ",T" : "") + ")"; }
        }

        private static Act[] Gen(Random r, int len, int[] kindWeights)
        {
            int total = kindWeights.Sum();
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= kindWeights[kind]) { k -= kindWeights[kind]; kind++; }
                a[i] = new Act { kind = kind, a = r.Next(1 << 16), b = r.Next(1 << 16), c = r.Next(1 << 16), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static List<string> Family(string name, int n, int seed0, int[] weights, int minLen, int spread, Func<IList<Act>, int, bool, string> run)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = Gen(r, minLen + r.Next(spread), weights); Cases++;
                if (run(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => run(t, seed, false) != null);
                fails.Add($"{name} seed {seed}: {run(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ kiln ════════════════════════
        // kinds: 0 feed, 1 advance, 2 rare tick, 3 settings, 4 wrong feed
        private static string RunKiln(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x1b873593);
            var rules = new RSW_KilnKernel.Rules
            {
                DosesNeeded = 2 + rr.Next(3), WindowTicks = new[] { 600, 6000, 60000 }[rr.Next(3)], FireCooldownTicks = new[] { 0, 1000, 240000 }[rr.Next(3)], CooldownMultiplier = 1f
            };
            rules.RushedSpanTicks = rules.WindowTicks / 4;
            var doses = new List<int>(); int nextReady = -1; bool enabled = true;
            int now = rr.Next(100000), step = 0, lastFire = int.MinValue, lastNextReady = -1;
            try
            {
                foreach (Act a in acts)
                {
                    step++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 3: enabled = (a.a & 7) != 0; rules.CooldownMultiplier = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.b % 5]; break;
                        case 1:
                            now += new[] { 1, 100, rules.RushedSpanTicks - 1, rules.RushedSpanTicks, rules.WindowTicks / 3, rules.WindowTicks, rules.WindowTicks + 1, 3 * rules.WindowTicks }[a.a % 8]; break;
                        case 2:
                            {
                                var before = doses.ToList();
                                RSW_KilnKernel.Cool(doses, now, rules.WindowTicks, enabled);
                                bool cold = before.Count > 0 && now - before.Last() > rules.WindowTicks;
                                if (!enabled || !cold) Check(doses.SequenceEqual(before), "the rare tick changed a warm or disabled ledger");
                                else { Check(doses.Count == 0, "a cold kiln kept its doses"); if (count) Cooled++; }
                                break;
                            }
                        default:
                            {
                                bool right = a.kind == 0;
                                var before = doses.ToList(); int nrBefore = nextReady;
                                var res = RSW_KilnKernel.Register(doses, ref nextReady, enabled, RSW_KilnKernel.FeedMatches(true, right), now, rules, out bool spaced);
                                if (!enabled || !right || now < nrBefore)
                                {
                                    Check(res == RSW_KilnKernel.Result.Ignored && doses.SequenceEqual(before) && nextReady == nrBefore && !spaced, "an ignored dose changed the kiln");
                                    break;
                                }
                                // the ledger the dose lands on: the old one unless it went cold
                                var basis = before.Count > 0 && now - before.Last() > rules.WindowTicks ? new List<int>() : before;
                                basis = basis.Concat(new[] { now }).ToList();
                                if (basis.Count < rules.DosesNeeded)
                                {
                                    Check(res == RSW_KilnKernel.Result.Counted && doses.SequenceEqual(basis) && nextReady == nrBefore, "a counted dose did not land on the ledger");
                                }
                                else
                                {
                                    Check(res == RSW_KilnKernel.Result.Fired && doses.Count == 0, "the needed dose did not fire / clear");
                                    int span = basis.Last() - basis.First();
                                    Check(spaced == (span >= rules.RushedSpanTicks && span <= rules.WindowTicks), $"spaced {spaced} for span {span} (rushed {rules.RushedSpanTicks}, window {rules.WindowTicks})");
                                    int cd = (int)Math.Round(rules.FireCooldownTicks * rules.CooldownMultiplier);
                                    Check(nextReady == now + cd, $"next ready {nextReady} vs {now + cd}");
                                    Check(now >= nrBefore, "fired during the cooldown");
                                    if (lastFire != int.MinValue) Check(now - lastFire >= lastNextReady - lastFire || true, "-");
                                    if (lastFire != int.MinValue) Check(now >= lastNextReady, $"fired at {now} before the previous cooldown ended at {lastNextReady}");
                                    lastFire = now; lastNextReady = nextReady;
                                    if (count) { Fires++; if (spaced) Good++; else Bad++; }
                                }
                                break;
                            }
                    }
                    // invariants
                    Check(doses.Count < rules.DosesNeeded, $"ledger holds {doses.Count} doses, the firing count is {rules.DosesNeeded}");
                    for (int i = 1; i < doses.Count; i++) Check(doses[i] >= doses[i - 1] && doses[i] - doses[i - 1] <= rules.WindowTicks, "ledger has an out-of-order dose or a gap over the window");
                }
            }
            catch (Exception e) { return $"step {step}: {e.Message}"; }
            return null;
        }

        private static List<string> KilnTables()
        {
            var fails = new List<string>();
            try
            {
                Check(RSW_KilnKernel.IsSpaced(0, 15000, 15000, 60000) && RSW_KilnKernel.IsSpaced(0, 60000, 15000, 60000) && !RSW_KilnKernel.IsSpaced(0, 14999, 15000, 60000) && !RSW_KilnKernel.IsSpaced(0, 60001, 15000, 60000), "IsSpaced edges are inclusive");
                // Slow feeding is NOT spaced: three doses 20 h apart each stay inside the window but span 40 h, so the batch is cracked. Pinned as the shipped reading.
                var rules = new RSW_KilnKernel.Rules { DosesNeeded = 3, WindowTicks = 60000, RushedSpanTicks = 15000, FireCooldownTicks = 240000, CooldownMultiplier = 1f };
                var d = new List<int>(); int next = -1; bool sp;
                RSW_KilnKernel.Register(d, ref next, true, true, 0, rules, out sp); RSW_KilnKernel.Register(d, ref next, true, true, 50000, rules, out sp);
                var r = RSW_KilnKernel.Register(d, ref next, true, true, 100000, rules, out sp);
                Check(r == RSW_KilnKernel.Result.Fired && !sp, "slow feeding (span over the window) reads as a rushed dump (pinned shipped reading)");
                d.Clear(); next = -1;
                RSW_KilnKernel.Register(d, ref next, true, true, 0, rules, out sp); RSW_KilnKernel.Register(d, ref next, true, true, 20000, rules, out sp);
                r = RSW_KilnKernel.Register(d, ref next, true, true, 40000, rules, out sp);
                Check(r == RSW_KilnKernel.Result.Fired && sp, "three doses over 40000 ticks fire a good batch");
                // a single dose can never be spaced when the rushed span is positive
                rules.DosesNeeded = 1; d.Clear(); next = -1;
                r = RSW_KilnKernel.Register(d, ref next, true, true, 0, rules, out sp);
                Check(r == RSW_KilnKernel.Result.Fired && !sp, "a one-dose kiln always fires cracked");
                Check(RSW_KilnKernel.FeedMatches(false, false) && RSW_KilnKernel.FeedMatches(true, true) && !RSW_KilnKernel.FeedMatches(true, false), "FeedMatches");
            }
            catch (Exception e) { fails.Add("kiln tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ grief ════════════════════════
        // kinds: 0 rare tick, 1 player tames, 2 colonist arrives, 3 slider/settings, 4 decay, 5 moornak leaves the map
        private sealed class Colonist { public bool has, spiked; public float sev; }

        private static string RunGrief(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x6a09e667);
            float step = new[] { 0.01f, 0.05f, 0.2f }[rr.Next(3)], target = new[] { 0.3f, 0.6f, 0.9f }[rr.Next(3)], spike = 1f, initial = 0.4f, perDay = new[] { 0f, 0.05f, 0.5f }[rr.Next(3)], max = 1f;
            int baseDelay = new[] { 3000, 30000, 600000 }[rr.Next(3)]; float mult = 1f; bool enabled = true;
            var cols = new List<Colonist>(); int nc = 1 + rr.Next(4); for (int i = 0; i < nc; i++) cols.Add(new Colonist());
            float stored = initial; int joinTick = -1, now = rr.Next(200000); bool player = false, onMap = true, released = false;
            int lastRelease = int.MinValue, stepNo = 0; float decayPerDay = new[] { 0f, 0.5f, 2f }[rr.Next(3)];
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 1: player = true; break;
                        case 2: cols.Add(new Colonist()); if (cols.Count > 6) cols.RemoveAt(0); break;
                        case 3: enabled = (a.a & 7) != 0; mult = new[] { 0.25f, 0.5f, 1f, 2f, 3f }[a.b % 5]; break;
                        case 5: onMap = !onMap; break;
                        case 4:
                            {
                                int ticks = 1 + a.a % 20000; now += ticks;
                                foreach (var c in cols) if (c.has) { c.sev -= decayPerDay * ticks / 60000f; if (c.sev <= 0f) { c.has = false; c.sev = 0f; } }
                                break;
                            }
                        default:
                            {
                                now += RSW_GriefKernel.TickRareInterval;
                                foreach (var c in cols) if (c.has) { c.sev -= decayPerDay * RSW_GriefKernel.TickRareInterval / 60000f; if (c.sev <= 0f) { c.has = false; c.sev = 0f; } }
                                if (!enabled || !onMap) break;
                                // self-tame gate is a table below; here the player owns it only when a.k1 said so
                                int j0 = joinTick;
                                joinTick = RSW_GriefKernel.JoinTick(joinTick, player, now);
                                Check(j0 >= 0 ? joinTick == j0 : joinTick == (player ? now : -1), "JoinTick");
                                if (joinTick >= 0 && j0 < 0 && count) Joins++;
                                var before = cols.Select(c => (c.has, c.sev)).ToList();
                                foreach (var c in cols)
                                {
                                    float next = RSW_GriefKernel.NextUnsettled(c.has, c.sev, step, target);
                                    c.sev = next; c.has = true;
                                }
                                for (int i = 0; i < cols.Count; i++)
                                {
                                    var (had, sev) = before[i];
                                    if (!had) Check(cols[i].sev == step, "a new unsettled hediff did not start at one step");
                                    else
                                    {
                                        Check(cols[i].sev >= sev, $"the unsettled update LOWERED a colonist's severity {sev} -> {cols[i].sev} (a release spike erased)");
                                        Check(cols[i].sev <= Math.Max(sev, target) + 1e-6f, "the update pushed past the target");
                                        if (sev < target) Check(Math.Abs(cols[i].sev - Math.Min(sev + step, target)) < 1e-6f, "update is not min(sev + step, target) below the target");
                                    }
                                }
                                float s0 = stored;
                                stored = RSW_GriefKernel.GrowGrief(stored, perDay, max);
                                Check(stored >= s0 && stored <= max + 1e-6f, "grief ledger fell or passed its ceiling");
                                int delay = RSW_GriefKernel.ReleaseDelay(baseDelay, mult);
                                bool due = RSW_GriefKernel.ReleaseDue(joinTick, now, delay);
                                Check(due == (joinTick >= 0 && now - joinTick >= delay), "ReleaseDue");
                                if (due)
                                {
                                    Check(player, "a release without the player's ownership");
                                    Check(now - Math.Max(joinTick, lastRelease == int.MinValue ? joinTick : lastRelease) >= delay || lastRelease == int.MinValue, "release came early");
                                    foreach (var c in cols) { c.sev = RSW_GriefKernel.Spike(spike); c.has = true; c.spiked = true; }
                                    stored = initial; joinTick = now; lastRelease = now; released = true;
                                    if (count) { Releases++; Spiked++; }
                                }
                                else if (released && decayPerDay == 0f)
                                {
                                    // after a release with no decay the spike must survive the following updates
                                    foreach (var c in cols) if (c.spiked) Check(c.sev >= spike - 1e-6f && c.has, "the release spike did not survive the next update");
                                }
                                break;
                            }
                    }
                    foreach (var c in cols) Check(!c.has || (c.sev > 0f && c.sev <= 1.0001f), "unsettled severity out of range");
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> GriefTables()
        {
            var fails = new List<string>();
            try
            {
                for (int m = 0; m < 16; m++)
                {
                    bool fac = (m & 1) != 0, down = (m & 2) != 0, ment = (m & 4) != 0, fog = (m & 8) != 0;
                    Check(RSW_GriefKernel.CanSelfTame(fac, down, ment, fog) == (!fac && !down && !ment && !fog), $"CanSelfTame({m})");
                }
                Check(RSW_GriefKernel.ReleaseDelay(1800000, 1f) == 1800000 && RSW_GriefKernel.ReleaseDelay(1800000, 0.25f) == 450000 && RSW_GriefKernel.ReleaseDelay(1800000, 3f) == 5400000, "ReleaseDelay anchors (30 days, 7.5 days, 90 days)");
                Check(Math.Abs(RSW_GriefKernel.GrowGrief(0.4f, 0.05f, 1f) - (0.4f + 0.05f * 250f / 60000f)) < 1e-7f && RSW_GriefKernel.GrowGrief(0.999f, 0.5f, 1f) == 1f, "GrowGrief");
                Check(RSW_GriefKernel.NextUnsettled(false, 0f, 0.05f, 0.6f) == 0.05f && RSW_GriefKernel.NextUnsettled(true, 0.59f, 0.05f, 0.6f) == 0.6f && RSW_GriefKernel.NextUnsettled(true, 1f, 0.05f, 0.6f) == 1f && RSW_GriefKernel.NextUnsettled(true, 0.6f, 0.05f, 0.6f) == 0.6f, "NextUnsettled anchors (a spike above the target is kept)");
                Check(RSW_GriefKernel.JoinTick(-1, false, 77) == -1 && RSW_GriefKernel.JoinTick(-1, true, 77) == 77 && RSW_GriefKernel.JoinTick(5, true, 77) == 5 && RSW_GriefKernel.JoinTick(5, false, 77) == 5, "JoinTick");
            }
            catch (Exception e) { fails.Add("grief tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ eat ════════════════════════
        private static List<string> EatCases(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    bool full = r.Next(6) == 0, useHp = r.Next(2) == 0, ignore = r.Next(4) == 0;
                    float pct = new[] { 0.001f, 0.05f, 0.2f, 0.5f, 1f }[r.Next(5)];
                    int maxHp = new[] { 1, 2, 10, 100, 300 }[r.Next(5)], hp = 1 + r.Next(maxHp), limit = new[] { 1, 10, 75, 100 }[r.Next(4)], stack = 1 + r.Next(150);
                    int bites = 0, curHp = hp, curStack = stack; bool dead = false;
                    var seen = new HashSet<(int, int)>();
                    while (!dead && bites < 100000)
                    {
                        var b = RSW_EatKernel.Chew(full, useHp, ignore, pct, maxHp, curHp, limit, curStack); bites++; Steps++;
                        if (full) { Check(b.Destroy && bites == 1, "fully-destroy did not consume at once"); }
                        else if (useHp && !ignore) Check(b.HitPoints < curHp, $"a bite did not lower the hit points ({curHp} -> {b.HitPoints}): the creature would eat the same item forever");
                        else Check(b.StackCount < curStack, $"a bite did not shrink the stack ({curStack} -> {b.StackCount})");
                        if (!useHp || ignore) Check(b.HitPoints == curHp || full, "hit points changed on the stack path");
                        if (useHp && !ignore) Check(b.StackCount == curStack, "stack changed on the hit-point path");
                        if (b.Destroy)
                        {
                            dead = true;
                            if (!full && useHp && !ignore) Check(b.HitPoints <= 0, "destroyed while hit points remained");
                            if (!full && !(useHp && !ignore)) Check(b.StackCount < RSW_EatKernel.MinStackLeft, "destroyed with a healthy stack left");
                        }
                        else
                        {
                            if (useHp && !ignore) Check(b.HitPoints > 0, "survived at zero hit points");
                            else Check(b.StackCount >= RSW_EatKernel.MinStackLeft, "survived under the minimum stack");
                        }
                        Check(seen.Add((b.HitPoints, b.StackCount)) || b.Destroy, "bite loop revisited a state");
                        curHp = b.HitPoints; curStack = b.StackCount;
                    }
                    Check(dead, "the item was never consumed");
                    Bites += bites; Eaten++;
                }
                catch (Exception e) { fails.Add($"eat seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            try
            {
                // gates, exhaustive
                for (int m = 0; m < 8; m++)
                    for (int fp = 0; fp < 3; fp++)
                    {
                        bool en = (m & 1) != 0, need = (m & 2) != 0, comp = (m & 4) != 0; float pct = fp == 0 ? 0.2f : fp == 1 ? 0.5f : 0.9f, want = 0.5f;
                        float pri = RSW_EatKernel.Priority(en, need, comp, pct, want);
                        Check(pri == (en && need && comp && pct < want ? 9.5f : 0f), $"Priority({m},{pct})");
                        Check(RSW_EatKernel.Hungry(pct, want) == (pct < want), "Hungry");
                        Steps++;
                    }
                for (int m = 0; m < 16; m++)
                    Check(RSW_EatKernel.DigDue((m & 1) != 0, (m & 2) != 0, (m & 4) != 0 ? 0.1f : 0.3f, 0.2f, (m & 8) != 0) == ((m & 1) != 0 && (m & 2) != 0 && (m & 4) != 0 && (m & 8) != 0), $"DigDue({m})");
                for (int m = 0; m < 8; m++)
                    Check(RSW_EatKernel.BlocksNormalFood((m & 1) != 0, (m & 2) != 0, (m & 4) != 0) == (m == 7), $"BlocksNormalFood({m})");
                var c = RSW_EatKernel.Chew(false, false, false, 0.2f, 100, 100, 75, 30);
                Check(c.StackCount == 15 && !c.Destroy, "steel stack of 30 loses 15");
                c = RSW_EatKernel.Chew(false, false, false, 0.2f, 100, 100, 75, 24);
                Check(c.StackCount == 9 && c.Destroy, "a stack that drops under ten is eaten whole (donor parity)");
                c = RSW_EatKernel.Chew(false, true, false, 0.2f, 100, 100, 75, 30);
                Check(c.HitPoints == 80 && !c.Destroy && c.StackCount == 30, "slag at 100 hit points loses 20");
                c = RSW_EatKernel.Chew(false, true, false, 0.2f, 1, 1, 75, 1);
                Check(c.Destroy, "a one-hit-point item is eaten in one bite");
                c = RSW_EatKernel.Chew(false, true, true, 0.2f, 100, 100, 75, 30);
                Check(c.HitPoints == 100 && c.StackCount == 15, "ignoreUseHitPoints takes the stack path");
            }
            catch (Exception e) { fails.Add("eat tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ hoard ════════════════════════
        private static string RunHoardWorld(int seed, bool count)
        {
            var r = new Random(seed ^ 0x3c6ef372);
            int W = 40, H = 40;
            try
            {
                var home = new bool[W, H]; var roofed = new bool[W, H]; var occupied = new bool[W, H]; var plant = new bool[W, H]; var open = new bool[W, H]; var reach = new bool[W, H];
                for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) { open[x, z] = r.Next(10) != 0; roofed[x, z] = r.Next(8) == 0; occupied[x, z] = r.Next(12) == 0; plant[x, z] = r.Next(6) == 0; reach[x, z] = r.Next(15) != 0; }
                int hx = r.Next(W), hz = r.Next(H), hs = 3 + r.Next(10);
                for (int x = 0; x < W; x++) for (int z = 0; z < H; z++) home[x, z] = Math.Abs(x - hx) < hs && Math.Abs(z - hz) < hs && r.Next(5) != 0;
                int cap = 1 + r.Next(5); float spacing = new[] { 3f, 8f, 18f }[r.Next(3)];
                var nests = new List<(int x, int z)>();
                int builds = 0, refused = 0;
                for (int bird = 0; bird < 60; bird++)
                {
                    Steps++;
                    int px = r.Next(W), pz = r.Next(H);
                    if (!RSW_HoardKernel.CanAddNest(nests.Count, cap)) { refused++; Check(nests.Count >= cap, "CanAddNest refused under the cap"); continue; }
                    bool placed = false;
                    foreach (bool cover in new[] { true, false })
                    {
                        for (int tries = 0; tries < 12 && !placed; tries++)
                        {
                            int cx = px + r.Next(-8, 9), cz = pz + r.Next(-8, 9);
                            bool inb = cx >= 0 && cz >= 0 && cx < W && cz < H;
                            var probes = new List<string>();
                            Func<bool> P(string n, Func<bool> f) { return () => { probes.Add(n); return f(); }; }
                            bool ok = RSW_HoardKernel.NestCellOk(inb, P("open", () => open[cx, cz]), P("home", () => home[cx, cz]), P("occ", () => occupied[cx, cz]), P("roof", () => roofed[cx, cz]), P("reach", () => reach[cx, cz]),
                                () => { probes.Add("space"); float m = float.MaxValue; foreach (var n in nests) m = Math.Min(m, (float)Math.Sqrt((n.x - cx) * (n.x - cx) + (n.z - cz) * (n.z - cz))); return m; }, spacing, cover,
                                P("plant", () => { for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) { int ax = cx + dx, az = cz + dz; if ((dx != 0 || dz != 0) && ax >= 0 && az >= 0 && ax < W && az < H && plant[ax, az]) return true; } return false; }));
                            // spec: ordered gates, probes only as far as the first refusal
                            var want = new List<string>(); bool wantOk = true;
                            if (!inb) wantOk = false;
                            else { want.Add("open"); if (!open[cx, cz]) wantOk = false; else { want.Add("home"); if (home[cx, cz]) wantOk = false; else { want.Add("occ"); if (occupied[cx, cz]) wantOk = false; else { want.Add("roof"); if (roofed[cx, cz]) wantOk = false; else { want.Add("reach"); if (!reach[cx, cz]) wantOk = false; else { want.Add("space"); float m = float.MaxValue; foreach (var n in nests) m = Math.Min(m, (float)Math.Sqrt((n.x - cx) * (n.x - cx) + (n.z - cz) * (n.z - cz))); if (m < spacing) wantOk = false; else if (cover) { want.Add("plant"); bool np = false; for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) { int ax = cx + dx, az = cz + dz; if ((dx != 0 || dz != 0) && ax >= 0 && az >= 0 && ax < W && az < H && plant[ax, az]) np = true; } if (!np) wantOk = false; } } } } } } }
                            Check(ok == wantOk, $"NestCellOk at ({cx},{cz}) = {ok} vs {wantOk}");
                            Check(probes.SequenceEqual(want), $"nest-cell probes [{string.Join(",", probes)}] vs [{string.Join(",", want)}]");
                            if (ok) { nests.Add((cx, cz)); placed = true; builds++; }
                        }
                        if (placed) break;
                    }
                    Check(nests.Count <= cap, "more nests than the cap");
                }
                for (int i = 0; i < nests.Count; i++)
                {
                    var n = nests[i];
                    Check(!home[n.x, n.z] && !roofed[n.x, n.z] && !occupied[n.x, n.z] && open[n.x, n.z] && reach[n.x, n.z], "a nest was built on a forbidden cell");
                    for (int j = 0; j < i; j++) Check(Math.Sqrt((n.x - nests[j].x) * (n.x - nests[j].x) + (n.z - nests[j].z) * (n.z - nests[j].z)) >= spacing - 1e-4, "two nests closer than the spacing");
                }
                if (count) { Builds += builds; Refused += refused; Nests += nests.Count; }
            }
            catch (Exception e) { return e.Message; }
            return null;
        }

        private static List<string> HoardCases(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; Cases++;
                string m = RunHoardWorld(seed, true);
                if (m != null) { fails.Add($"hoard seed {seed}: {m}"); if (fails.Count >= 3) break; }
                // nearest nest vs brute force, lazy reach
                try
                {
                    var r = new Random(seed ^ 0x7f4a7c15); int k = r.Next(8);
                    var dist = new List<float>(); var sp = new List<bool>(); var rc = new List<bool>();
                    for (int j = 0; j < k; j++) { dist.Add(r.Next(0, 12) * 2f); sp.Add(r.Next(5) != 0); rc.Add(r.Next(4) != 0); }
                    float radius = new[] { 0f, 10f, 40f }[r.Next(3)];
                    var asked = new List<int>();
                    int got = RSW_HoardKernel.NearestNest(dist, sp, j => { asked.Add(j); return rc[j]; }, radius);
                    int want = -1; float bd = float.MaxValue; var wantAsked = new List<int>();
                    for (int j = 0; j < k; j++) { if (!sp[j] || dist[j] > radius || dist[j] >= bd) continue; wantAsked.Add(j); if (!rc[j]) continue; want = j; bd = dist[j]; }
                    Check(got == want, $"NearestNest {got} vs {want}");
                    Check(asked.SequenceEqual(wantAsked), "NearestNest asked reachability for the wrong nests");
                    for (int j = 0; j < k; j++) if (sp[j] && rc[j] && dist[j] <= radius) Check(want >= 0 && dist[want] <= dist[j], "a closer nest was passed over");
                    Steps++;
                }
                catch (Exception e) { fails.Add($"hoard nearest seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            try
            {
                // Eligible exhaustive
                for (int m = 0; m < 128; m++)
                    foreach (int fp in new[] { 0, 1, 2 })
                        foreach (int rp in new[] { 0, 1, 2, 3 })
                        {
                            bool en = (m & 1) != 0, alive = (m & 2) != 0, comp = (m & 4) != 0, awake = (m & 8) != 0, calm = (m & 16) != 0, hands = (m & 32) != 0, egg = (m & 64) != 0;
                            bool hasFood = fp > 0, hasRest = rp > 0; float food = fp == 1 ? 0.2f : 0.8f, rest = rp == 1 ? 0.39f : rp == 2 ? 0.4f : 0.9f;
                            bool got = RSW_HoardKernel.Eligible(en, alive, comp, awake, calm, hands, hasFood, food, 0.5f, hasRest, rest, egg);
                            bool want = en && alive && comp && awake && calm && hands && !(hasFood && food < 0.5f) && !(hasRest && rest < 0.4f) && !egg;
                            Check(got == want, $"Eligible({m},{fp},{rp})");
                            Steps++;
                        }
                // Takeable: lazy order
                for (int m = 0; m < 512; m++)
                {
                    var probes = new List<string>();
                    bool spawned = (m & 1) != 0, hasMap = (m & 2) != 0, home = (m & 4) != 0, store = (m & 8) != 0, bld = (m & 16) != 0, steal = (m & 256) != 0; int stack = (m & 32) != 0 ? 5 : 0; float d = (m & 64) != 0 ? 2f : (m & 128) != 0 ? 2.01f : 9f;
                    bool got = RSW_HoardKernel.Takeable(spawned, stack, hasMap, steal, () => { probes.Add("h"); return home; }, () => { probes.Add("s"); return store; }, () => { probes.Add("b"); return bld; }, () => { probes.Add("d"); return d; });
                    var want = new List<string>(); bool w = true;
                    if (!spawned || stack <= 0 || !hasMap) w = false;
                    else if (steal) { want.Add("d"); if (d <= 2f) w = false; }
                    else { want.Add("h"); if (home) w = false; else { want.Add("s"); if (store) w = false; else { want.Add("b"); if (bld) w = false; else { want.Add("d"); if (d <= 2f) w = false; } } } }
                    Check(got == w, $"Takeable({m})"); Check(probes.SequenceEqual(want), $"Takeable probes [{string.Join(",", probes)}] vs [{string.Join(",", want)}]");
                    Steps++;
                }
                Check(!RSW_HoardKernel.RaidOver(-99999, 5) && !RSW_HoardKernel.RaidOver(100, 100) && RSW_HoardKernel.RaidOver(100, 101) && RSW_HoardKernel.RaidOver(0, 1), "RaidOver edges");
                Check(RSW_HoardKernel.TheftMessageDue(-1, 0, 2500) && !RSW_HoardKernel.TheftMessageDue(100, 2599, 2500) && RSW_HoardKernel.TheftMessageDue(100, 2600, 2500), "TheftMessageDue edges");
                Check(RSW_HoardKernel.CanAddNest(3, 4) && !RSW_HoardKernel.CanAddNest(4, 4) && !RSW_HoardKernel.CanAddNest(5, 4) && !RSW_HoardKernel.CanAddNest(0, 0), "CanAddNest edges");
                Check(RSW_HoardKernel.SpacingOk(18f, 18f) && !RSW_HoardKernel.SpacingOk(17.9f, 18f) && RSW_HoardKernel.SpacingOk(float.MaxValue, 18f), "SpacingOk edges");
            }
            catch (Exception e) { fails.Add("hoard tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ toxin ════════════════════════
        // kinds: 0 interval, 1 toggle fed, 2 toggle enabled, 3 toggle frozen, 4 set level, 5 many intervals
        private static string RunToxin(IList<Act> acts, int seed, bool count)
        {
            var rr = new Random(seed ^ 0x5be0cd19);
            float fall = new[] { 0f, 0.5f, 5f, 40f }[rr.Next(4)], max = 1f, level = 0.8f + (float)rr.NextDouble() * 0.2f;
            bool fed = false, enabled = true, frozen = false; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 1: fed = !fed; break;
                        case 2: enabled = !enabled; break;
                        case 3: frozen = !frozen; break;
                        case 4: level = RSW_ToxinKernel.Clamp(new[] { 0f, 0.005f, 0.01f, 0.0101f, 0.05f, 0.1f, 0.1001f, 0.5f, 1f }[a.a % 9], max); break;
                        default:
                            {
                                int n = a.kind == 5 ? 1 + a.a % 400 : 1;
                                for (int i = 0; i < n; i++)
                                {
                                    float before = level; int catBefore = RSW_ToxinKernel.Category(level);
                                    // the mod's own call (it never passes frozen: it returns first)
                                    if (!frozen) level = RSW_ToxinKernel.Clamp(RSW_ToxinKernel.Next(level, max, false, enabled, enabled && fed, fall), max);
                                    if (frozen) { Check(RSW_ToxinKernel.Next(level, max, true, enabled, fed, fall) == level, "a frozen need moved"); Check(level == before, "frozen level changed"); }
                                    else if (!enabled) Check(level == max, "mechanic off but the need is not full");
                                    else if (fed) Check(level >= before && (level == max || Math.Abs(level - before - 0.015f) < 1e-6f), $"fed need moved {before} -> {level}");
                                    else Check(level <= before && (level == 0f || Math.Abs(before - level - fall / 60000f * 150f) < 1e-6f), $"unfed need moved {before} -> {level}");
                                    int cat = RSW_ToxinKernel.Category(level);
                                    if (cat == RSW_ToxinKernel.Withdrawal && catBefore != RSW_ToxinKernel.Withdrawal && count) Withdrawals++;
                                }
                                break;
                            }
                    }
                    Check(level >= 0f && level <= max, "need level out of range");
                    int c = RSW_ToxinKernel.Category(level);
                    Check((c == RSW_ToxinKernel.Withdrawal) == (level <= 0.01f) && (c == RSW_ToxinKernel.Satisfied) == (level > 0.1f), $"category {c} at level {level}");
                    Check(RSW_ToxinKernel.HediffStage(c) == (level <= 0.01f ? 1 : 0), "hediff stage disagrees with withdrawal");
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        private static List<string> ToxinTables()
        {
            var fails = new List<string>();
            try
            {
                Check(RSW_ToxinKernel.Category(0.1f) == RSW_ToxinKernel.Desire && RSW_ToxinKernel.Category(0.1001f) == RSW_ToxinKernel.Satisfied && RSW_ToxinKernel.Category(0.01f) == RSW_ToxinKernel.Withdrawal && RSW_ToxinKernel.Category(0.0101f) == RSW_ToxinKernel.Desire && RSW_ToxinKernel.Category(0f) == RSW_ToxinKernel.Withdrawal && RSW_ToxinKernel.Category(1f) == RSW_ToxinKernel.Satisfied, "category edges");
                Check(RSW_ToxinKernel.HediffStage(RSW_ToxinKernel.Withdrawal) == 1 && RSW_ToxinKernel.HediffStage(RSW_ToxinKernel.Desire) == 0 && RSW_ToxinKernel.HediffStage(RSW_ToxinKernel.Satisfied) == 0, "only withdrawal is the harmful stage");
                Check(RSW_ToxinKernel.Clamp(-1f, 1f) == 0f && RSW_ToxinKernel.Clamp(2f, 1f) == 1f && RSW_ToxinKernel.Clamp(0.3f, 1f) == 0.3f, "Clamp");
                Check(Math.Abs(RSW_ToxinKernel.Next(0.5f, 1f, false, true, true, 5f) - 0.515f) < 1e-6f && Math.Abs(RSW_ToxinKernel.Next(0.5f, 1f, false, true, false, 6f) - (0.5f - 0.015f)) < 1e-6f && RSW_ToxinKernel.Next(0.2f, 1f, false, false, false, 5f) == 1f && RSW_ToxinKernel.Next(0.2f, 1f, true, false, false, 5f) == 0.2f, "Next anchors");
            }
            catch (Exception e) { fails.Add("toxin tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ spew ════════════════════════
        private static double AngleBetween(int ax, int az, int bx, int bz)
        {
            double cross = Math.Abs((double)ax * bz - (double)az * bx), dot = (double)ax * bx + (double)az * bz;
            return Math.Atan2(cross, dot) * 180.0 / Math.PI;
        }

        private static List<string> SpewCases(int n, int seed0)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed); Cases++;
                try
                {
                    int px = 20 + r.Next(40), pz = 20 + r.Next(40); int tx = px + r.Next(-25, 26), tz = pz + r.Next(-25, 26);
                    float range = new[] { 1f, 3f, 6f, 10f, 15f }[r.Next(5)], width = new[] { 1f, 2f, 4f, 6f, 10f }[r.Next(5)];
                    var c = RSW_SpewKernel.ConeFor(px, pz, tx, tz, range, width);
                    Check(c.Empty == (px == tx && pz == tz), "Empty only when the target is the pawn's own cell");
                    if (c.Empty) continue;
                    double aimLen = Math.Sqrt((double)(c.AimX - px) * (c.AimX - px) + (double)(c.AimZ - pz) * (c.AimZ - pz));
                    Check(Math.Abs(aimLen - range) <= 0.71 + 1e-6, $"aim point {aimLen:F2} cells away, range {range}");
                    // the aim lies on the pawn-to-target ray (within the rounding of its two coordinates)
                    Check(AngleBetween(tx - px, tz - pz, c.AimX - px, c.AimZ - pz) <= 45.0 || range < 2f, "the aim point left the pawn-to-target ray");
                    Check(c.HalfAngle > 0f && c.HalfAngle < 90f, $"half angle {c.HalfAngle}");
                    double wantHalf = Math.Atan2(width / 2.0, aimLen) * 180.0 / Math.PI;
                    Check(Math.Abs(c.HalfAngle - wantHalf) < 0.01, $"half angle {c.HalfAngle} vs atan(w/2 / d) {wantHalf}");
                    int R = (int)range + 2; int inCount = 0; var wide = RSW_SpewKernel.ConeFor(px, pz, tx, tz, range, width * 2f);
                    for (int cx = -R; cx <= R; cx++)
                        for (int cz = -R; cz <= R; cz++)
                        {
                            if (cx == 0 && cz == 0) continue;
                            bool got = RSW_SpewKernel.InCone(c, cx, cz);
                            double ang = AngleBetween(cx, cz, c.AimX - px, c.AimZ - pz);
                            if (Math.Abs(ang - c.HalfAngle) > 0.01) Check(got == (ang <= c.HalfAngle), $"cell ({cx},{cz}) at {ang:F2} deg from the axis, half {c.HalfAngle:F2}: in-cone {got}");
                            if (got) { inCount++; Check(RSW_SpewKernel.InCone(wide, cx, cz) || Math.Abs(ang - wide.HalfAngle) <= 0.01, "a wider spray lost a cell"); }
                            Steps++;
                        }
                    // the axis itself and the aim cell are in; the opposite side is out
                    Check(RSW_SpewKernel.InCone(c, c.AimX - px, c.AimZ - pz), "the aim cell is outside its own cone");
                    if (c.AimX != px || c.AimZ != pz) Check(!RSW_SpewKernel.InCone(c, -(c.AimX - px), -(c.AimZ - pz)), "the cell behind the pawn is inside the cone");
                    ShapesChecked += inCount > 0 ? 1 : 0; Spews++;
                }
                catch (Exception e) { fails.Add($"spew seed {seed}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            try
            {
                // a target on the pawn's own cell gives an empty cone (never a NaN aim point)
                Check(RSW_SpewKernel.ConeFor(30, 30, 30, 30, 10f, 6f).Empty && !RSW_SpewKernel.ConeFor(30, 30, 31, 30, 10f, 6f).Empty && !RSW_SpewKernel.ConeFor(30, 30, 30, 31, 10f, 6f).Empty, "own-cell cone");
                Check(Math.Abs(RSW_SpewKernel.DeltaAngle(179f, -179f) - 2f) < 1e-4f && Math.Abs(RSW_SpewKernel.DeltaAngle(-179f, 179f) + 2f) < 1e-4f && Math.Abs(RSW_SpewKernel.DeltaAngle(10f, 370f)) < 1e-4f && RSW_SpewKernel.DeltaAngle(30f, 30f) == 0f && Math.Abs(RSW_SpewKernel.DeltaAngle(0f, 180f) - 180f) < 1e-4f, "DeltaAngle anchors");
                for (float a = -360f; a <= 360f; a += 7.5f) for (float b = -360f; b <= 360f; b += 11f) { float d = RSW_SpewKernel.DeltaAngle(a, b); Check(d > -180.0001f && d <= 180.0001f, $"DeltaAngle({a},{b}) = {d}"); Steps++; }
                Check(RSW_SpewKernel.AngleOf(1, 0) == 0f && Math.Abs(RSW_SpewKernel.AngleOf(0, 1) - 90f) < 1e-4f && Math.Abs(RSW_SpewKernel.AngleOf(-1, 0) - 180f) < 1e-4f && Math.Abs(RSW_SpewKernel.AngleOf(0, -1) + 90f) < 1e-4f, "AngleOf quadrants (x east, z north)");
            }
            catch (Exception e) { fails.Add("spew tables: " + e.Message); }
            return fails;
        }

        // ════════════════════════ ability + ikee ════════════════════════
        private static List<string> AbilityIkee()
        {
            var fails = new List<string>();
            try
            {
                for (int m = 0; m < 16; m++)
                {
                    bool granted = (m & 1) != 0, en = (m & 2) != 0, has = (m & 4) != 0, pawn = (m & 8) != 0;
                    var got = RSW_AbilityKernel.Decide(granted, en, has, pawn);
                    var want = granted || !en ? RSW_AbilityKernel.Step.Nothing : !has ? RSW_AbilityKernel.Step.MarkGrantedOnly : !pawn ? RSW_AbilityKernel.Step.Nothing : RSW_AbilityKernel.Step.Grant;
                    Check(got == want, $"AbilityKernel.Decide({m}) = {got}");
                    Steps++;
                }
                for (int m = 0; m < 32; m++)
                {
                    bool en = (m & 1) != 0, onMap = (m & 2) != 0, human = (m & 4) != 0, near = (m & 8) != 0, tol = (m & 16) != 0; int asked = 0;
                    int got = RSW_IkeeKernel.Stage(en, onMap, human, () => { asked++; return near; }, tol);
                    int want = !en || !onMap || !human || !near ? RSW_IkeeKernel.Inactive : tol ? RSW_IkeeKernel.Comforted : RSW_IkeeKernel.Unsettled;
                    Check(got == want, $"IkeeKernel.Stage({m}) = {got}");
                    Check(asked == (en && onMap && human ? 1 : 0), "the ikee search ran when it should not (or not when it should)");
                    Steps++;
                }
                foreach (float radius in new[] { 0f, 1f, 5f, 12f, 12.5f, 13f })
                    for (int dx = -15; dx <= 15; dx++)
                        for (int dz = -15; dz <= 15; dz++)
                        {
                            Check(RSW_IkeeKernel.Nearby(dx, dz, radius) == ((double)dx * dx + (double)dz * dz <= (double)radius * radius), $"Nearby({dx},{dz},{radius})");
                            Steps++;
                        }
                Check(RSW_IkeeKernel.DefaultRadius == 12f && RSW_IkeeKernel.Inactive == -1 && RSW_IkeeKernel.Comforted == 0 && RSW_IkeeKernel.Unsettled == 1, "ikee constants (stage 0 comforted, stage 1 unsettled)");
                Cases++;
            }
            catch (Exception e) { fails.Add("ability/ikee: " + e.Message); }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            bool tables = !oneSeed.HasValue && scale > 0;
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("kiln", () => { var f = Family("kiln", N(5000), S(1), new[] { 45, 25, 12, 6, 12 }, 20, 120, RunKiln); if (tables) f.AddRange(KilnTables()); return f; }),
                ("grief", () => { var f = Family("grief", N(5000), S(1), new[] { 60, 4, 6, 6, 18, 6 }, 20, 160, RunGrief); if (tables) f.AddRange(GriefTables()); return f; }),
                ("eat", () => EatCases(N(5000), S(1))),
                ("hoard", () => HoardCases(N(1500), S(1))),
                ("toxin", () => { var f = Family("toxin", N(5000), S(1), new[] { 40, 10, 6, 6, 8, 30 }, 20, 160, RunToxin); if (tables) f.AddRange(ToxinTables()); return f; }),
                ("spew", () => SpewCases(N(600), S(1))),
                ("ikee", () => tables || oneSeed.HasValue ? AbilityIkee() : new List<string>()),
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
            Console.WriteLine($"reached: fires {Fires} (good {Good}, cracked {Bad}), cooled {Cooled}, joins {Joins}, releases {Releases}, bites {Bites} over {Eaten} items, nests {Nests} from {Builds} builds ({Refused} refused at the cap), withdrawals {Withdrawals}, spews {Spews}");
            if (!oneSeed.HasValue && scale >= 1)
            {
                bool all = only == null;
                if ((all || only == "kiln") && (Fires == 0 || Good == 0 || Bad == 0 || Cooled == 0)) { Console.WriteLine("FAIL kiln fuzz never fired good / cracked or never cooled (blind)"); ok = false; }
                if ((all || only == "grief") && (Joins == 0 || Releases == 0)) { Console.WriteLine("FAIL grief fuzz never joined or released (blind)"); ok = false; }
                if ((all || only == "eat") && (Eaten == 0 || Bites <= Eaten)) { Console.WriteLine("FAIL eat fuzz never took a multi-bite item (blind)"); ok = false; }
                if ((all || only == "hoard") && (Nests == 0 || Refused == 0)) { Console.WriteLine("FAIL hoard fuzz never built a nest or never hit the cap (blind)"); ok = false; }
                if ((all || only == "toxin") && Withdrawals == 0) { Console.WriteLine("FAIL toxin fuzz never reached withdrawal (blind)"); ok = false; }
                if ((all || only == "spew") && ShapesChecked == 0) { Console.WriteLine("FAIL spew fuzz never produced a non-empty cone (blind)"); ok = false; }
            }
            Console.WriteLine($"swbestiary fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
