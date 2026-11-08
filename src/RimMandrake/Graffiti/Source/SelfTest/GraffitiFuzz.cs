// Approach B for Graffiti: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_GraffitiKernel.cs) and the two plain enum files:
//   pick    the weighted pick: in range, monotone in the roll, boundary rolls (0, each running sum, total, just over the total), zero / negative weights never picked,
//           observed frequencies match the weights
//   gates   meme / skill / hostility gates and the pool-membership rule exhaustively against independent truth tables
//   react   the relation-keyed reaction priority over all 2^11 flag combinations against an ordered-rule spec
//   misc    scrub protection, raid-exit gate, clan-only veto, room rule, thought-active, going-over, paint cadence clamp, spree forms
//   cells   wall-cell candidate gathering against a sort-then-take oracle (cap, bare before marked, scan order)
//   lure    the breach-lure choice: nearest wins, ties by key, order does not matter
//   wall    the wall-face draw: side priority over all 16 neighbour masks, offset onto that wall, angle facing it
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

        // ════════════════════════ social ════════════════════════
        // Reading a mark and answering it: every viewer standing against what the tables promise.
        private static List<string> Social(int n, int seed)
        {
            return Loop("social", n, seed, r =>
            {
                Steps++;
                var v = new RM_Viewer
                {
                    isMaker = r.Next(4) == 0, isSubject = r.Next(3) == 0, ownFaction = r.Next(2) == 0, hostileMaker = r.Next(4) == 0,
                    loverOfSubject = r.Next(4) == 0, loverOfMaker = r.Next(4) == 0, opinionOfMaker = r.Next(-100, 101), opinionOfSubject = r.Next(-100, 101),
                    kind = r.Next(3) == 0, hot = r.Next(3) == 0, psychopath = r.Next(4) == 0, hasIdeo = r.Next(2) == 0, makerHasIdeo = r.Next(2) == 0, sameIdeoAsMaker = r.Next(2) == 0,
                };
                var meaning = (RM_Meaning)r.Next(8);
                RM_Reaction react = RM_GraffitiKernel.ReactionOf(meaning, v);
                if (v.isMaker) Check(react == RM_Reaction.None, "a painter doesn't react to their own mark");
                if (!v.isMaker && v.hostileMaker) Check(react == RM_Reaction.Uneasy || react == RM_Reaction.Defiant, "an enemy's mark is an enemy's mark, whatever it says");
                if (!v.isMaker && !v.hostileMaker)
                {
                    if (meaning == RM_Meaning.Mockery && v.isSubject) Check(react == (v.kind ? RM_Reaction.ShrugsOff : RM_Reaction.Humiliated), "the subject of a mockery");
                    if (meaning == RM_Meaning.Mockery && !v.isSubject && v.opinionOfSubject >= 20) Check(react == RM_Reaction.FriendDefends, "a friend of the mocked");
                    if (meaning == RM_Meaning.Tribute && v.isSubject) Check(react == RM_Reaction.Honored, "the subject of a tribute");
                    if (meaning == RM_Meaning.Devotion) Check(react != RM_Reaction.Offended || (v.hasIdeo && v.makerHasIdeo && !v.sameIdeoAsMaker), "only another creed offends");
                    if (meaning == RM_Meaning.Memorial && v.psychopath) Check(react == RM_Reaction.None, "a psychopath mourns nobody");
                }
                if (meaning == RM_Meaning.None && !v.isMaker && !v.hostileMaker && !v.ownFaction) Check(react == RM_Reaction.None, "a stranger's plain tag means nothing");
                bool canFight = r.Next(2) == 0, here = r.Next(2) == 0, good = r.Next(2) == 0;
                float roll = (float)r.NextDouble();
                var reaction = (RM_Reaction)r.Next(21);
                RM_Answer answer = RM_GraffitiKernel.AnswerOf(reaction, v.hot, canFight, here, good, roll);
                if (answer == RM_Answer.Confront) Check(canFight && here, "nobody confronts a painter who isn't here, or who can't fight");
                if (answer == RM_Answer.Reply) Check(good && here, "a reply needs a good hand and someone to reply to");
                bool gentle = reaction == RM_Reaction.Amused || reaction == RM_Reaction.Moved || reaction == RM_Reaction.Honored || reaction == RM_Reaction.Uplifted || reaction == RM_Reaction.Warmed || reaction == RM_Reaction.Gleeful;
                if (gentle) Check(answer == RM_Answer.None, "nobody answers a mark they enjoyed");
                int worst = r.Next(-100, 101);
                bool enemy = r.Next(2) == 0, spree = r.Next(2) == 0, kind = r.Next(2) == 0, beloved = r.Next(2) == 0, mourned = r.Next(2) == 0;
                RM_Meaning wants = RM_GraffitiKernel.WantsToPaint(spree, kind, worst, enemy, beloved, mourned, roll);
                if (wants == RM_Meaning.Mockery) Check(!kind && enemy && worst <= RM_GraffitiKernel.EnemyOpinion, "cruelty needs an enemy and an unkind hand");
                if (wants == RM_Meaning.Tribute) Check(beloved && !spree, "a broken hand paints no valentines");
                if (wants == RM_Meaning.Memorial) Check(mourned, "a memorial needs someone mourned");
                if (!enemy && !beloved && !mourned) Check(wants == RM_Meaning.None, "a colony at peace paints nothing about anyone");
                Check(RM_GraffitiKernel.RefusesToPaint(RM_Meaning.Mockery, true) && !RM_GraffitiKernel.RefusesToPaint(RM_Meaning.Mockery, false) && !RM_GraffitiKernel.RefusesToPaint(RM_Meaning.Tribute, true), "who refuses what");
                int id = r.Next(), count = r.Next(1, 12);
                int hand = RM_GraffitiKernel.HandChoice(id, count, 3);
                Check(hand >= 0 && hand < count && hand == RM_GraffitiKernel.HandChoice(id, count, 3), "a painter's hand is stable and in range");
                Check(RM_GraffitiKernel.TerritoryStage(0) == -1 && RM_GraffitiKernel.TerritoryStage(1) == 0 && RM_GraffitiKernel.TerritoryStage(3) == 1 && RM_GraffitiKernel.TerritoryStage(9) == 2, "territory stages");
                Check(RM_GraffitiKernel.GoodwillOf(RM_Meaning.Insult, true, false, false) < RM_GraffitiKernel.GoodwillOf(RM_Meaning.Insult, false, true, false), "a named insult costs more than a taunt");
                // A memorial softens grief and never turns it into a gain: every ease about one dead pawn, in order, adds up to at most half the grief.
                float grief = (float)(r.NextDouble() * 30.0), before = 0f;
                int eases = r.Next(0, 5);
                for (int i = 0; i < eases; i++)
                {
                    float raw = (float)(r.NextDouble() * 8.0), share = RM_GraffitiKernel.EaseShare(grief, raw, before);
                    Check(share >= 0f && share <= raw + 1e-5f, "an ease is never more than itself");
                    before += share;
                }
                Check(before <= grief * RM_GraffitiKernel.GriefEaseShare + 1e-4f, $"eases {before} outweigh half the grief {grief}");
                Check(RM_GraffitiKernel.EaseShare(0f, 4f, 0f) == 0f, "no grief, no relief");
                Check(RM_GraffitiKernel.AmbientMoodBudget < RM_GraffitiKernel.GoodMoodBudget, "wall pleasure about nobody is a share of the good budget");
            });
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
                    bool was = (m & 1) != 0, now = (m & 2) != 0;
                    Check(RM_GraffitiKernel.TurnsToLeave(was, now) == (now && !was), $"TurnsToLeave({was},{now})");
                }
                for (int m = 0; m < 8; m++)
                {
                    Steps++;
                    bool roofed = (m & 1) != 0, known = (m & 2) != 0, outdoors = (m & 4) != 0;
                    Check(RM_GraffitiKernel.ExteriorFace(roofed, known, outdoors) == (!roofed && known && outdoors), $"ExteriorFace({roofed},{known},{outdoors})");
                    if (roofed) Check(!RM_GraffitiKernel.ExteriorFace(roofed, known, outdoors), "a roofed cell counted as an exterior face");
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

        // ════════════════════════ wall (GRAFFITI_WALLFACE) ════════════════════════
        // All 16 neighbour masks against an independent spec: north beats east beats west beats south; the offset is exactly one
        // unit step of the given length onto that wall; the angle turns the mark's top into the wall (Rot4.AsAngle) except on a south wall, where the mark stays upright (0); no wall draws
        // as the old upright floor mark.
        private static List<string> Wall()
        {
            return Loop("wall", 1, 1, r =>
            {
                int[] stepX = { 0, 1, 0, -1 }, stepZ = { 1, 0, -1, 0 };   // Rot4 0..3 FacingCell
                int[] priority = { 0, 1, 3, 2 };
                for (int mask = 0; mask < 16; mask++)
                {
                    Steps++;
                    bool[] has = { (mask & 1) != 0, (mask & 2) != 0, (mask & 4) != 0, (mask & 8) != 0 };   // n, e, s, w
                    int want = RM_GraffitiKernel.NoWall;
                    foreach (int p in priority) { if (has[p]) { want = p; break; } }
                    int side = RM_GraffitiKernel.WallSide(has[0], has[1], has[2], has[3]);
                    Check(side == want, $"mask {mask}: WallSide {side}, want {want}");
                    Check(side == RM_GraffitiKernel.NoWall || has[side], $"mask {mask}: side {side} has no wall");
                    Check(side == RM_GraffitiKernel.NoWall || RM_GraffitiKernel.FaceOfSide(side) != RM_GraffitiKernel.FaceNone, $"mask {mask}: side {side} has no face");
                }
                foreach (int bad in new[] { -2, 4, 99 })
                {
                    Check(RM_GraffitiKernel.FaceOfSide(bad) == RM_GraffitiKernel.FaceNone, $"out-of-range side {bad} has a face");
                }
                Check(RM_GraffitiKernel.FaceOfSide(0) == RM_GraffitiKernel.FaceFront && !RM_GraffitiKernel.SidePaintable(2), "a wall north of the floor shows its front; a wall south of it shows nothing");
                // Every mark, every link set, every face, every width: inside its face, and its art's map stays affine.
                float[][] geoms = { new[] { 0.40f, 0.22f }, new[] { 0.30f, 0.20f }, new[] { 0.45f, 0.30f } };
                foreach (float[] g in geoms)
                {
                    foreach (int face in new[] { RM_GraffitiKernel.FaceFront, RM_GraffitiKernel.FaceEast, RM_GraffitiKernel.FaceWest })
                    {
                        RM_GraffitiKernel.AlongOf(face, out int ax, out int az);
                        for (int linksA = 0; linksA < 16; linksA++)
                        {
                            for (int linksB = 0; linksB < 16; linksB++)
                            {
                                foreach (float width in new[] { 0.6f, 1f, 2f, 3f })
                                {
                                    foreach (float slope in new[] { -0.06f, 0f, 0.06f })
                                    {
                                        foreach (float lift in new[] { 0f, 0.5f, 1f })
                                        {
                                            Cases++; Steps++;
                                            int la = linksA, lb = linksB;
                                            Func<int, int> linksAt = k => k == 0 ? la : (k > 0 ? lb : (la & 8) != 0 ? 10 : -1);
                                            List<RM_MarkPiece> pieces = RM_GraffitiKernel.MarkPieces(linksAt, face, g[0], g[1], width, RM_GraffitiKernel.ClimbHeight, 0f, slope, lift, false);
                                            if (RM_GraffitiKernel.FaceExists(la, face))
                                            {
                                                Check(pieces.Exists(p => p.k == 0 && !p.onTop) && pieces.Exists(p => p.k == 0 && p.onTop), $"face {face} links {la}: a full mark must lie on its face and climb onto the top");
                                            }
                                            if (!RM_GraffitiKernel.FaceExists(la, face))
                                            {
                                                Check(pieces.Count == 0 || pieces.TrueForAll(p => p.k != 0), $"face {face} links {la}: drew on a cell with no such face");
                                            }
                                            foreach (RM_MarkPiece p in pieces)
                                            {
                                                List<RM_PlaneVert> edge = p.onTop ? RM_GraffitiKernel.TopPoly(linksAt(p.k), g[0], g[1]) : RM_GraffitiKernel.FacePoly(linksAt(p.k), face, g[0], g[1]);
                                                Check(edge != null && RM_GraffitiKernel.FaceExists(linksAt(p.k), face), $"face {face}: a piece on a cell with no face");
                                                if (edge == null) continue;
                                                foreach (RM_PlaneVert v in p.poly)
                                                {
                                                    float x = v.x - ax * p.k, z = v.z - az * p.k;
                                                    Check(x >= -1e-3f && x <= 1.001f && z >= -1e-3f && z <= 1.001f, $"face {face} links {linksAt(p.k)}: vertex ({x},{z}) leaves the wall cell");
                                                    for (int e = 0; e < edge.Count; e++)
                                                    {
                                                        RM_PlaneVert a = edge[e], b = edge[(e + 1) % edge.Count];
                                                        Check((b.x - a.x) * (z - a.z) - (b.z - a.z) * (x - a.x) >= -1e-3f, $"face {face} links {linksAt(p.k)}: vertex ({x},{z}) outside the face");
                                                    }
                                                    Check(v.u >= -1e-3f && v.u <= 1.001f && v.v >= -1e-3f && v.v <= 1.001f, "uv left the art");
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                // Measuring the crease: an outline at the tile's edge must not be taken for it.
                float[] prof = { 100, 100, 100, 100, 104, 104, 200, 240, 240, 240, 0, 0 };
                Check(RM_GraffitiKernel.CreaseCrossing(prof, 1, 7, 10) == 6, "crease crossing misread");
                Check(RM_GraffitiKernel.CreaseCrossing(new float[] { 90, 90, 90, 90 }, 0, 2, 4) == -1, "a flat tile has no crease");
            });
        }

        // The hand, the pace and the wall's manners: a mark may tilt and shrink but never grow out of its wall cell, every form takes
        // real time, overlap is symmetric, and a room's share grows with the room.
        private static List<string> Paint()
        {
            return Loop("paint", 1, 1, r =>
            {
                foreach (GraffitiForm form in Enum.GetValues(typeof(GraffitiForm)))
                {
                    foreach (int pace in new[] { int.MinValue, 0, 60, 250, 1000, int.MaxValue })
                    {
                        Cases++; Steps++;
                        int t = RM_GraffitiKernel.PaintTicks(form, pace);
                        Check(t >= 30 && t <= RM_GraffitiKernel.PaintTicksBase(form) * 4, $"{form} at pace {pace}: {t} ticks");
                    }
                    Check(RM_GraffitiKernel.JoyForm(form) || !RM_GraffitiKernel.SpreeForm(form), $"{form}: in the spree pool but not the joy pool");
                }
                for (int id = -2000; id < 200000; id += 37)
                {
                    foreach (float width in new[] { 1f, 2f, 3f })
                    {
                        Cases++; Steps++;
                        RM_GraffitiKernel.HandOf(id, width, out float slope, out float scale, out float slide, out float lift, out bool flip);
                        Check(scale > 0.5f && scale <= 1f, $"id {id}: scale {scale} grows out of the wall");
                        Check(Math.Abs(slope) <= 0.0601f && Math.Abs(slide) <= 0.1f && lift >= 0f && lift <= 1f, $"id {id}: slope {slope}, slide {slide}, lift {lift}");
                        RM_GraffitiKernel.HandOf(id, width, out float slope2, out float scale2, out float slide2, out float lift2, out bool flip2);
                        Check(slope == slope2 && scale == scale2 && slide == slide2 && lift == lift2 && flip == flip2, $"id {id}: the hand is not stable across redraws");
                    }
                }
                Check(RM_GraffitiKernel.WallMarksOverlap(0f, 0.5f, 0.5f) && !RM_GraffitiKernel.WallMarksOverlap(1f, 0.5f, 0.5f), "one-cell neighbours must not count as overlapping");
                Check(RM_GraffitiKernel.WallMarksOverlap(1f, 1.5f, 0.5f) && RM_GraffitiKernel.WallMarksOverlap(-1f, 1.5f, 0.5f), "a tag beside a piece's middle lies under it");
                Check(!RM_GraffitiKernel.RoomHoldsEnough(0, 1) && RM_GraffitiKernel.RoomHoldsEnough(1, 1), "a closet takes one mark");
                Check(!RM_GraffitiKernel.RoomHoldsEnough(4, 160) && RM_GraffitiKernel.RoomHoldsEnough(11, 160), "a hall takes more than a closet");
                Check(RM_GraffitiKernel.IdleHandTags(0f) && !RM_GraffitiKernel.IdleHandTags(RM_GraffitiKernel.IdleTagChance) && !RM_GraffitiKernel.IdleHandTags(1f), "the idle tag is a low chance, not a certainty");
                Check(RM_GraffitiKernel.SittingContinues(100, true, 1f), "a spree does not stop for joy");
                Check(!RM_GraffitiKernel.SittingContinues(RM_GraffitiKernel.MaxMarksPerJoySitting, false, 0f) && !RM_GraffitiKernel.SittingContinues(0, false, 1f) && RM_GraffitiKernel.SittingContinues(0, false, 0f), "a joy sitting ends when satisfied or after its few marks");
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
                ("social", () => Social(N(20000), S(1))),
                ("pick", () => Pick(N(3000), S(1))),
                ("gates", () => Gates()),
                ("react", () => React()),
                ("misc", () => Misc(1, 1)),
                ("cells", () => Cells(N(6000), S(1))),
                ("lure", () => Lure(N(4000), S(1))),
                ("wall", () => Wall()),
                ("paint", () => Paint()),
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
