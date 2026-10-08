// Approach B for Graffiti: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_GraffitiKernel.cs) and the two plain enum files:
//   pick    the weighted pick: in range, monotone in the roll, boundary rolls (0, total, one ulp over), zero / negative weights never picked,
//           observed frequencies match the weights
//   gates   meme / skill / hostility gates and the pool-membership rule exhaustively against independent truth tables
//   react   the relation-keyed reaction priority over all 2^11 flag combinations against an ordered-rule spec
//   misc    scrub protection, raid-exit gate, clan-only veto, room rule, thought-active, going-over, paint cadence clamp, spree forms
//   cells   wall-cell candidate gathering against a sort-then-take oracle (cap, bare before marked, scan order)
//   lure    the breach-lure choice: nearest wins, ties by key, order does not matter
// A failing case is printed as `family seed N: message | detail`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.Graffiti.SelfTest
{
    internal static class GraffitiFuzz
    {
        public static long Cases, Steps, Picks, ZeroFirst, Capped, Fallbacks, Ties;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static List<string> Loop(string name, int n, int seed, Action<Random> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { one(new Random(seed + i)); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        // ════════════════════════ pick ════════════════════════
        private static List<string> Pick(int n, int seed)
        {
            return Loop("pick", n, seed, r =>
            {
                Steps++;
                int count = r.Next(0, 9);
                float[] pool = { 0f, 0.5f, 1f, 1f, 1f, 2f, 3f, 10f, -1f };
                var w = Enumerable.Range(0, count).Select(_ => pool[r.Next(pool.Length)]).ToList();
                if (count > 0 && r.Next(6) == 0) w[0] = 0f;                       // a leading zero: roll 0 must not land on it
                float total = RM_GraffitiKernel.Total(w);
                Check(Math.Abs(total - w.Where(x => x > 0f).Sum()) < 1e-4f, "Total is not the sum of the positive weights");
                if (count == 0 || total <= 0f)
                {
                    Check(RM_GraffitiKernel.PickIndex(w, 0f) == -1 && RM_GraffitiKernel.PickIndex(w, 5f) == -1, "a pick from an empty / weightless pool");
                    return;
                }
                int prev = -1;
                for (int k = 0; k <= 40; k++)
                {
                    float roll = total * k / 40f;
                    int idx = RM_GraffitiKernel.PickIndex(w, roll);
                    Check(idx >= 0 && idx < count, $"index {idx} out of range for {count} weights");
                    Check(w[idx] > 0f, $"picked index {idx} with weight {w[idx]} at roll {roll} (weights {string.Join(",", w)})");
                    Check(idx >= prev, "the pick moved backwards as the roll rose");
                    prev = idx;
                }
                { float run = 0f; for (int i = 0; i < count; i++) { if (w[i] <= 0f) continue; run += w[i]; Check(RM_GraffitiKernel.PickIndex(w, run) == i, $"a roll exactly on the running sum {run} picked {RM_GraffitiKernel.PickIndex(w, run)}, not entry {i} (a boundary roll belongs to the entry it completes)"); } }
                int firstPos = w.FindIndex(x => x > 0f), lastPos = w.FindLastIndex(x => x > 0f);
                Check(RM_GraffitiKernel.PickIndex(w, 0f) == firstPos, $"roll 0 picked {RM_GraffitiKernel.PickIndex(w, 0f)}, the first positive weight is {firstPos}");
                if (w[0] <= 0f) ZeroFirst++;
                Check(RM_GraffitiKernel.PickIndex(w, total) == lastPos, $"roll = total picked {RM_GraffitiKernel.PickIndex(w, total)}, the last positive weight is {lastPos}");
                Check(RM_GraffitiKernel.PickIndex(w, total * 1.0001f + 0.001f) == lastPos, "a roll just over the total did not fall back to the last entry");
                if (RM_GraffitiKernel.PickIndex(w, total * 1.0001f + 0.001f) == lastPos) Fallbacks++;
                // frequencies
                var hits = new int[count];
                const int draws = 4000;
                for (int d = 0; d < draws; d++) hits[RM_GraffitiKernel.PickIndex(w, (float)(r.NextDouble() * total))]++;
                Picks += draws;
                for (int i = 0; i < count; i++)
                {
                    double p = Math.Max(0f, w[i]) / total, exp = p * draws, sd = Math.Sqrt(draws * p * (1 - p)) + 1;
                    Check(Math.Abs(hits[i] - exp) <= 6 * sd, $"entry {i} (weight {w[i]}/{total}) drawn {hits[i]} of {draws}, expected {exp:F0}");
                }
            });
        }

        // ════════════════════════ gates ════════════════════════
        private static List<string> Gates()
        {
            var fails = new List<string>();
            Cases++;
            try
            {
                for (int m = 0; m < 8; m++)
                {
                    bool req = (m & 1) != 0, ideo = (m & 2) != 0, holds = (m & 4) != 0; Steps++;
                    bool want = !req || (ideo && holds);
                    Check(RM_GraffitiKernel.MemeGate(req, ideo, holds) == want, $"MemeGate({req},{ideo},{holds})");
                }
                foreach (int min in new[] { -2, 0, 1, 6, 12 })
                    foreach (bool has in new[] { false, true })
                        foreach (int lvl in new[] { 0, 5, 6, 7, 20 })
                        {
                            Steps++;
                            bool want = min <= 0 || (has && lvl >= min);
                            Check(RM_GraffitiKernel.SkillGate(min, has, lvl) == want, $"SkillGate({min},{has},{lvl})");
                        }
                for (int m = 0; m < 64; m++)
                {
                    bool named = (m & 1) != 0, defOk = (m & 2) != 0, facOk = (m & 4) != 0, placerF = (m & 8) != 0, isTarget = (m & 16) != 0, hostile = (m & 32) != 0; Steps++;
                    bool want = !named || !defOk || !facOk || (placerF && !isTarget && hostile);
                    Check(RM_GraffitiKernel.HostilityGate(named, defOk, facOk, placerF, isTarget, hostile) == want, $"HostilityGate({named},{defOk},{facOk},{placerF},{isTarget},{hostile})");
                }
                for (int m = 0; m < 16; m++)
                {
                    bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0; float wgt = (m & 8) != 0 ? 1f : 0f; Steps++;
                    Check(RM_GraffitiKernel.InPool(a, b, c, wgt) == (a && b && c && wgt > 0f), $"InPool({a},{b},{c},{wgt})");
                }
                Check(!RM_GraffitiKernel.InPool(true, true, true, -1f), "a negative weight is in the pool");
            }
            catch (Exception e) { fails.Add("gates seed 0: " + e.Message); }
            return fails;
        }

        // ════════════════════════ react ════════════════════════
        private static List<string> React()
        {
            var fails = new List<string>();
            try
            {
                var seen = new HashSet<RM_ReactionSlot>();
                for (int m = 0; m < 4096; m++)
                {
                    Cases++; Steps++;
                    bool[] f = Enumerable.Range(0, 11).Select(i => (m >> i & 1) == 1).ToArray();
                    var got = RM_GraffitiKernel.ReactionSlot(f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10]);
                    // spec: an ordered list of (slot, applies)
                    var rules = new (RM_ReactionSlot s, bool on)[]
                    {
                        (RM_ReactionSlot.Subject, f[1] && f[2]), (RM_ReactionSlot.OwnFaction, f[3] && f[4]), (RM_ReactionSlot.SameIdeo, f[5] && f[6]),
                        (RM_ReactionSlot.HostileMaker, f[7] && f[8]), (RM_ReactionSlot.OtherIdeo, f[9] && f[10]),
                    };
                    RM_ReactionSlot want = RM_ReactionSlot.Flat;
                    if (f[0]) foreach (var rule in rules) if (rule.on) { want = rule.s; break; }
                    if (got != want) { fails.Add($"react seed {m}: flags {string.Join("", f.Select(x => x ? 1 : 0))} got {got} want {want}"); if (fails.Count > 2) return fails; }
                    seen.Add(got);
                }
                if (seen.Count != 6) fails.Add("react seed 0: only " + seen.Count + " of 6 slots reachable");
            }
            catch (Exception e) { fails.Add("react seed 0: " + e.Message); }
            return fails;
        }

        // ════════════════════════ misc ════════════════════════
        private static List<string> Misc(int n, int seed)
        {
            var fails = new List<string>();
            fails.AddRange(Loop("misc", 1, 1, _ =>
            {
                for (int m = 0; m < 128; m++)
                {
                    Steps++;
                    bool[] f = Enumerable.Range(0, 7).Select(i => (m >> i & 1) == 1).ToArray();
                    bool prot = RM_GraffitiKernel.ProtectsFromAutoClean(f[0], f[1], f[2], f[3], f[4], f[5], f[6]);
                    bool want = !f[0] && f[1] && f[2] && f[3] && (f[4] || f[5] || f[6]);
                    Check(prot == want, $"ProtectsFromAutoClean({string.Join(",", f)}) = {prot}");
                    if (f[0]) Check(!prot, "a forced clean was blocked (the player's override must always work)");
                }
                for (int m = 0; m < 32; m++)
                {
                    Steps++;
                    bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0, d = (m & 8) != 0, e = (m & 16) != 0;
                    Check(RM_GraffitiKernel.RaidExitTags(a, b, c, d, e) == (a && b && c && !d && e), $"RaidExitTags({a},{b},{c},{d},{e})");
                }
                for (int m = 0; m < 4; m++)
                {
                    Steps++;
                    bool clan = (m & 1) != 0, own = (m & 2) != 0;
                    Check(RM_GraffitiKernel.ClanOnlyBlocks(clan, own) == (clan && !own), $"ClanOnlyBlocks({clan},{own})");
                }
                for (int m = 0; m < 8; m++)
                {
                    Steps++;
                    bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0;
                    Check(RM_GraffitiKernel.SameRoomOrUnknown(a, b, c) == (!a || !b || c), $"SameRoomOrUnknown({a},{b},{c})");
                }
                for (int m = 0; m < 16; m++)
                {
                    Steps++;
                    bool a = (m & 1) != 0, b = (m & 2) != 0, c = (m & 4) != 0, d = (m & 8) != 0;
                    Check(RM_GraffitiKernel.ThoughtActive(a, b, c, d) == (a && b && c && d), "ThoughtActive");
                }
                Check(RM_GraffitiKernel.IsRival(true, false) && !RM_GraffitiKernel.IsRival(true, true) && !RM_GraffitiKernel.IsRival(false, false) && !RM_GraffitiKernel.IsRival(false, true), "IsRival table");
                foreach (int v in new[] { int.MinValue, -1, 0, 1, 59, 60, 250, 1000, 1001, int.MaxValue })
                {
                    int c = RM_GraffitiKernel.PaintInterval(v);
                    Check(c >= 60 && c <= 1000 && c > 0, $"PaintInterval({v}) = {c}");
                    if (v >= 60 && v <= 1000) Check(c == v, "an in-range paint interval was changed: " + v);
                }
                var spree = Enum.GetValues(typeof(GraffitiForm)).Cast<GraffitiForm>().Where(RM_GraffitiKernel.SpreeForm).ToList();
                Check(spree.Count == 4 && spree.Contains(GraffitiForm.Scrawl) && spree.Contains(GraffitiForm.Tag) && spree.Contains(GraffitiForm.ThrowUp) && spree.Contains(GraffitiForm.Glyph), "spree forms are not exactly Scrawl/Tag/ThrowUp/Glyph: " + string.Join(",", spree));
                Check(Enum.GetValues(typeof(GraffitiForm)).Length == 8, "GraffitiForm gained / lost a value: add it to the spree table decision");
                Check(Enum.GetValues(typeof(GraffitiCategory)).Length == 6, "GraffitiCategory gained / lost a value");
            }));
            return fails;
        }

        // ════════════════════════ cells ════════════════════════
        private static List<string> Cells(int n, int seed)
        {
            return Loop("cells", n, seed, r =>
            {
                Steps++;
                int count = r.Next(0, 80);
                double pu = r.NextDouble(), pm = r.NextDouble();
                var cells = Enumerable.Range(0, count).Select(_ => { bool u = r.NextDouble() < pu; return new RM_MarkCell(u, u && r.NextDouble() < pm); }).ToList();
                List<int> got = RM_GraffitiKernel.Gather(cells);
                var bare = Enumerable.Range(0, count).Where(i => cells[i].usable && !cells[i].marked).ToList();
                var marked = Enumerable.Range(0, count).Where(i => cells[i].usable && cells[i].marked).ToList();
                var want = (bare.Count > 0 ? bare : marked).Take(12).ToList();
                Check(got.SequenceEqual(want), $"pool [{string.Join(",", got)}], oracle [{string.Join(",", want)}]");
                Check(got.Count <= 12, "pool above the cap");
                if (bare.Count > 12 || marked.Count > 12) Capped++;
                Check(got.All(i => cells[i].usable), "an unusable cell in the pool");
                if (bare.Count > 0) Check(got.All(i => !cells[i].marked), "a marked cell offered while a bare one exists (the spree would repaint one wall)");
                else if (marked.Count > 0) Check(got.All(i => cells[i].marked), "fallback pool is not the marked cells");
                else Check(got.Count == 0, "a pool from no usable cell");
                // the scan stops at the 12th bare cell: nothing after it may change the answer
                var trimmed = cells.Take(bare.Count >= 12 ? bare[11] + 1 : count).ToList();
                Check(RM_GraffitiKernel.Gather(trimmed).SequenceEqual(got), "cells after the 12th bare cell changed the pool (the scan should have stopped)");
            });
        }

        // ════════════════════════ lure ════════════════════════
        private static List<string> Lure(int n, int seed)
        {
            return Loop("lure", n, seed, r =>
            {
                Steps++;
                int count = r.Next(0, 10);
                var d = Enumerable.Range(0, count).Select(_ => (long)r.Next(0, 6) * (r.Next(8) == 0 ? 100000000L : 1L)).ToList();
                var key = Enumerable.Range(0, count).Select(i => 1000 + i).OrderBy(_ => r.Next()).ToList();
                int best = RM_GraffitiKernel.ChooseLure(d, key);
                if (count == 0) { Check(best == -1, "a lure from nothing"); return; }
                long min = d.Min();
                Check(d[best] == min, $"lure {best} at {d[best]} is not the nearest ({min})");
                var tied = Enumerable.Range(0, count).Where(i => d[i] == min).ToList();
                if (tied.Count > 1) Ties++;
                Check(key[best] == tied.Min(i => key[i]), "a tie was not broken by the lowest key");
                var perm = Enumerable.Range(0, count).OrderBy(_ => r.Next()).ToList();
                int pbest = RM_GraffitiKernel.ChooseLure(perm.Select(i => d[i]).ToList(), perm.Select(i => key[i]).ToList());
                Check(perm[pbest] == best, "the lure depends on the order of the marks");
            });
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("pick", () => Pick(N(3000), S(1))),
                ("gates", () => Gates()),
                ("react", () => React()),
                ("misc", () => Misc(1, 1)),
                ("cells", () => Cells(N(6000), S(1))),
                ("lure", () => Lure(N(4000), S(1))),
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
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: picks {Picks}, leading-zero pools {ZeroFirst}, fall-backs to last {Fallbacks}, capped pools {Capped}, tied lures {Ties}");
                if (Picks == 0 || ZeroFirst == 0 || Fallbacks == 0 || Capped == 0 || Ties == 0) { Console.WriteLine("FAIL fuzz never reached picks / leading zero / fall-back / cap / tie (blind)"); ok = false; }
            }
            Console.WriteLine($"graffiti fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
