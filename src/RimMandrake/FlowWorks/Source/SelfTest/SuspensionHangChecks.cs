// SUSPENSION_BRIDGE_READS_HUNG (Artisan pass 4, 2026-11-08): the numbers of the hung look (RM_SuspensionHangMath.cs).
// The bar: suspension_bridge_reads_hung (a deck hung between anchors over a dug hole, not a floor tile or a pier bridge).
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SuspensionHangChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static readonly SuspensionTier[] Tiers = { SuspensionTier.Rope, SuspensionTier.Timber, SuspensionTier.Steel, SuspensionTier.Heavy };

        /// <summary>No towers, one mid tower, and two towers where the span is long enough (tower indices lie in 1..len - 2).</summary>
        private static IEnumerable<List<int>> TowerSets(int len)
        {
            yield return new List<int>();
            if (len >= 5)
            {
                yield return new List<int> { len / 2 };
            }
            if (len >= 9)
            {
                yield return new List<int> { 3, len - 4 };
            }
        }

        private static float[] SupportsOf(List<int> idx, int len)
        {
            float[] sup = new float[idx.Count];
            for (int k = 0; k < idx.Count; k++)
            {
                sup[k] = RM_SuspensionHangMath.SupportAlong(idx[k], len);
            }
            return sup;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Hang_sag_lowest_mid_zero_at_supports", () =>
            {
                foreach (SuspensionTier t in Tiers)
                {
                    for (int n = 3; n <= 22; n++)
                    {
                        float a0 = 0.5f, a1 = n - 1.5f;
                        Assert(RM_SuspensionHangMath.SagAt(a0, a0, a1, t) == 0f && RM_SuspensionHangMath.SagAt(a1, a0, a1, t) == 0f,
                            t + " n" + n + ": sag at a support");
                        float mid = RM_SuspensionHangMath.SagAt((a0 + a1) / 2f, a0, a1, t);
                        Assert(mid >= RM_SuspensionHangMath.MinMidSag - 1e-4f && mid <= RM_SuspensionHangMath.MaxMidSag + 1e-4f,
                            t + " n" + n + ": mid sag " + mid + " out of the readable band");
                        float q = RM_SuspensionHangMath.SagAt(a0 + (a1 - a0) / 4f, a0, a1, t);
                        Assert(q > 0f && q < mid, t + " n" + n + ": quarter sag " + q + " not between 0 and mid " + mid);
                    }
                }
            });
            Case("Hang_longer_span_sags_more_rope_most", () =>
            {
                foreach (SuspensionTier t in Tiers)
                {
                    float prev = 0f;
                    for (int len = 4; len <= 12; len++)
                    {
                        float m = RM_SuspensionHangMath.MidSag(len, t);
                        Assert(m >= prev, t + ": " + len + "-cell segment sags " + m + " below shorter " + prev);
                        prev = m;
                    }
                }
                Assert(RM_SuspensionHangMath.MidSag(10f, SuspensionTier.Rope) > RM_SuspensionHangMath.MidSag(10f, SuspensionTier.Heavy),
                    "rope sags no more than heavy steel");
            });
            Case("Hang_cable_post_top_to_post_top_above_deck", () =>
            {
                foreach (SuspensionTier t in Tiers)
                {
                    float a0 = 0.5f, a1 = 6.5f, top = RM_SuspensionHangMath.PostHeight(t);
                    Assert(Math.Abs(RM_SuspensionHangMath.CableNorth(a0, a0, a1, t) - top) < 1e-4f, t + ": cable leaves the post top");
                    Assert(Math.Abs(RM_SuspensionHangMath.CableNorth(a1, a0, a1, t) - top) < 1e-4f, t + ": cable reaches the far post top");
                    float lowest = float.MaxValue;
                    for (int k = 0; k <= 20; k++)
                    {
                        float a = a0 + (a1 - a0) * k / 20f;
                        float rise = RM_SuspensionHangMath.CableNorth(a, a0, a1, t) + RM_SuspensionHangMath.SagAt(a, a0, a1, t);
                        Assert(rise >= RM_SuspensionHangMath.CableMidRise - 1e-4f, t + ": cable falls onto the deck at " + a);
                        lowest = Math.Min(lowest, RM_SuspensionHangMath.CableNorth(a, a0, a1, t));
                    }
                    float midC = RM_SuspensionHangMath.CableNorth((a0 + a1) / 2f, a0, a1, t);
                    Assert(Math.Abs(lowest - midC) < 1e-3f, t + ": cable lowest " + lowest + " not at mid-span " + midC);
                    Assert(top > 0.75f, t + ": post " + top + " not clearly taller than the deck");
                }
            });
            Case("Hang_splay_full_at_posts_none_mid", () =>
            {
                Assert(Math.Abs(RM_SuspensionHangMath.Splay(0f) - RM_SuspensionHangMath.MaxSplay) < 1e-5f, "no splay at the post");
                Assert(RM_SuspensionHangMath.Splay(0.5f) < 1e-5f, "splay at mid-span");
                Assert(RM_SuspensionHangMath.ShadowEast(0f) == 0f && RM_SuspensionHangMath.ShadowEast(40f) <= 0.6f, "shadow offset unbounded");
            });
            Case("Hang_supports_split_segments", () =>
            {
                float[] s = { 0.5f, 5f, 10.5f };
                Assert(RM_SuspensionHangMath.SagAt(5f, s, 3, SuspensionTier.Steel) == 0f, "sag at a tower");
                Assert(RM_SuspensionHangMath.SagAt(2.75f, s, 3, SuspensionTier.Steel) > 0f, "no sag in the first segment");
                Assert(RM_SuspensionHangMath.SagAt(0f, s, 3, SuspensionTier.Steel) == 0f, "sag over the anchor");
            });
            // pass 7: the three treatments and the slope guard that keeps the drawn deck from folding back on itself
            Case("Hang_slope_guard_holds_every_treatment", () =>
            {
                // sanity: without the guard a 1-cell rope walk at the readable minimum folds (slope over 1)
                float raw = RM_SuspensionHangMath.MidSag(1f, SuspensionTier.Heavy) * RM_SuspensionHangMath.SagMultiplier(RM_SuspensionHangMath.TreatmentRopeWalk);
                Assert(RM_SuspensionHangMath.MaxSlope(raw, 1f) > 1f, "instrument: the unguarded 1-cell rope walk should slope over 1, got " + RM_SuspensionHangMath.MaxSlope(raw, 1f));
                float[] lens = { 0.5f, 1f, 1.5f, 2f, 3f, 4f, 6f, 9f, 13f, 20f, 40f };
                int seen = 0;
                foreach (SuspensionTier t in Tiers)
                {
                    for (int tr = 0; tr <= 2; tr++)
                    {
                        foreach (float len in lens)
                        {
                            float mid = RM_SuspensionHangMath.TreatedMidSag(len, t, tr);
                            float slope = RM_SuspensionHangMath.MaxSlope(mid, len);
                            Assert(mid > 0f, t + " t" + tr + " len " + len + ": no sag");
                            Assert(slope <= 0.8f + 1e-4f, t + " t" + tr + " len " + len + ": slope " + slope + " over the guard");
                            // the drawn line z' = along - sag(along) must run one way only (a fold would draw the deck twice)
                            float prev = float.MinValue;
                            for (int k = 0; k <= 64; k++)
                            {
                                float a = len * k / 64f;
                                float z = a - mid * RM_SuspensionHangMath.Bow(a / len);
                                Assert(z > prev, t + " t" + tr + " len " + len + ": the drawn deck folds at " + a);
                                prev = z;
                            }
                            seen++;
                        }
                    }
                }
                Assert(seen == 4 * 3 * lens.Length, "instrument: checked " + seen + " cases");
            });
            Case("Hang_treatments_rope_walk_most_cable_stayed_least", () =>
            {
                foreach (SuspensionTier t in Tiers)
                {
                    for (int len = 3; len <= 16; len++)
                    {
                        float s0 = RM_SuspensionHangMath.TreatedMidSag(len, t, RM_SuspensionHangMath.TreatmentSuspension);
                        float s1 = RM_SuspensionHangMath.TreatedMidSag(len, t, RM_SuspensionHangMath.TreatmentRopeWalk);
                        float s2 = RM_SuspensionHangMath.TreatedMidSag(len, t, RM_SuspensionHangMath.TreatmentCableStayed);
                        Assert(s1 > s0 && s0 > s2 && s2 > 0f, t + " len " + len + ": sags " + s0 + "/" + s1 + "/" + s2 + " not rope walk > suspension > cable-stayed > 0");
                    }
                }
                float[] sup = { 0.5f, 4f, 9.5f };
                float[] mids = { 0.3f, 0.5f };
                Assert(RM_SuspensionHangMath.HungSagAt(4f, sup, mids, 3) == 0f, "hung sag at a tower");
                Assert(Math.Abs(RM_SuspensionHangMath.HungSagAt(6.75f, sup, mids, 3) - 0.5f) < 1e-4f, "second segment's own mid sag");
                Assert(RM_SuspensionHangMath.HungSagAt(10f, sup, mids, 3) == 0f, "hung sag over the far anchor");
            });
            // the anchors at the two ends: the first and last supports sit on the anchors' deck-facing edges, and their posts are
            // printed by the first and last deck squares, standing on those squares against the anchors
            Case("Hang_supports_at_anchor_ends_posts_on_end_squares", () =>
            {
                int seen = 0;
                for (int len = 3; len <= 22; len++)
                {
                    foreach (List<int> towers in TowerSets(len))
                    {
                        List<int> idx = RM_SuspensionMath.Supports(len, towers);
                        int n = idx.Count;
                        Assert(n == 2 + towers.Count, "len " + len + ": " + n + " supports for " + towers.Count + " tower(s)");
                        float[] sup = SupportsOf(idx, len);
                        Assert(sup[0] == 0.5f && sup[n - 1] == len - 1.5f, "len " + len + ": ends at " + sup[0] + " / " + sup[n - 1]);
                        for (int k = 0; k < n; k++)
                        {
                            if (k > 0)
                            {
                                Assert(sup[k] > sup[k - 1], "len " + len + ": supports not increasing at " + k);
                            }
                            int owner = RM_SuspensionHangMath.PostOwner(sup[k], len);
                            int want = k == 0 ? 1 : k == n - 1 ? len - 2 : idx[k];
                            Assert(owner == want, "len " + len + " support " + k + ": post printed by square " + owner + ", want " + want);
                            foreach (SuspensionTier t in Tiers)
                            {
                                float w = RM_SuspensionHangMath.PostWidth(t);
                                float foot = RM_SuspensionHangMath.PostFootAlong(k, n, sup[k], w);
                                Assert(foot - 0.5f * w >= owner - 0.5f - 1e-5f && foot + 0.5f * w <= owner + 0.5f + 1e-5f,
                                    "len " + len + " support " + k + " " + t + ": post at " + foot + " off its square " + owner);
                                Assert(foot >= 0.5f && foot <= len - 1.5f, "len " + len + " support " + k + ": post off the deck");
                                if (k == 0 || k == n - 1)
                                {
                                    Assert(Math.Abs(foot - sup[k]) <= 0.5f * w + 1e-5f, "len " + len + ": anchor post " + foot + " not against its anchor " + sup[k]);
                                }
                                seen++;
                            }
                        }
                    }
                }
                Assert(seen > 500, "instrument: checked " + seen + " posts");
            });
            // the hung look: from each support the deck drops steadily to its lowest mid-segment and rises back, in every look
            Case("Hang_sag_rises_monotonic_to_mid_span", () =>
            {
                int seen = 0;
                int[] looks = { RM_SuspensionHangMath.TreatmentSuspension, RM_SuspensionHangMath.TreatmentRopeWalk, RM_SuspensionHangMath.TreatmentCableStayed };
                foreach (SuspensionTier t in Tiers)
                {
                    foreach (int look in looks)
                    {
                        for (int len = 3; len <= 22; len++)
                        {
                            foreach (List<int> towers in TowerSets(len))
                            {
                                float[] sup = SupportsOf(RM_SuspensionMath.Supports(len, towers), len);
                                int n = sup.Length;
                                float[] mids = new float[n];
                                for (int k = 0; k + 1 < n; k++)
                                {
                                    mids[k] = RM_SuspensionHangMath.TreatedMidSag(sup[k + 1] - sup[k], t, look);
                                }
                                for (int k = 0; k + 1 < n; k++)
                                {
                                    float a0 = sup[k], a1 = sup[k + 1], mid = 0.5f * (a0 + a1);
                                    string at = t + " look " + look + " len " + len + " seg " + k;
                                    Assert(mids[k] > 0f, at + ": no sag");
                                    Assert(RM_SuspensionHangMath.HungSagAt(a0, sup, mids, n) == 0f && RM_SuspensionHangMath.HungSagAt(a1, sup, mids, n) == 0f, at + ": sag at a support");
                                    Assert(Math.Abs(RM_SuspensionHangMath.HungSagAt(mid, sup, mids, n) - mids[k]) < 1e-4f, at + ": mid-span is not the lowest point " + mids[k]);
                                    const int steps = 64;
                                    float prev = 0f;
                                    for (int j = 1; j <= steps; j++)
                                    {
                                        float a = a0 + (a1 - a0) * j / steps, sag = RM_SuspensionHangMath.HungSagAt(a, sup, mids, n);
                                        Assert(sag >= 0f && sag <= mids[k] + 1e-5f, at + ": sag " + sag + " outside 0.." + mids[k]);
                                        bool before = a <= mid + 1e-5f;
                                        bool afterMid = a - (a1 - a0) / steps >= mid - 1e-5f;
                                        if (before)
                                        {
                                            Assert(sag >= prev - 1e-6f, at + ": sag falls back before mid-span at " + a);
                                        }
                                        else if (afterMid)
                                        {
                                            Assert(sag <= prev + 1e-6f, at + ": sag deepens past mid-span at " + a);
                                        }
                                        prev = sag;
                                        seen++;
                                    }
                                }
                                Assert(RM_SuspensionHangMath.HungSagAt(0f, sup, mids, n) == 0f && RM_SuspensionHangMath.HungSagAt(len - 1f, sup, mids, n) == 0f, "len " + len + ": the anchors themselves sag");
                            }
                        }
                    }
                }
                Assert(seen > 10000, "instrument: sampled " + seen + " points");
            });
            // PAWN_WALKS_UNDER_DECK draw order: the redrawn deck (and its posts, cables and railing) lies above every layer of a
            // pawn on the hole's floor and below every layer of a pawn on the deck, for every altitude seed; the thresholds that
            // pick whom to redraw over take the floor pawns and never the walkers. Pawn layers as LipOcclusion_skips_shallower_pawn:
            // seed within one AltInc, layers 0.0037 under to 100 x 0.0003658537 over the seeded altitude.
            Case("Hang_deck_redraw_between_floor_and_deck_walkers", () =>
            {
                float pawnAlt = 28 * 0.36585367f, inc = 0.03658537f, under = 0.0037f, over = 100 * 0.0003658537f;
                float lip = pawnAlt - RM_WallFaceMath.SunkAltitudeDrop + RM_WallFaceMath.CoverAboveSunk;
                int seen = 0;
                for (int j = -20; j <= 20; j++)
                {
                    float seed = inc * j / 20f;
                    foreach (bool sunkenDeck in new[] { false, true })
                    {
                        float deck = RM_SuspensionHangMath.OccluderY(pawnAlt, sunkenDeck);
                        float rail = deck + RM_SuspensionHangMath.RailingAboveDeck;
                        float parts = RM_SuspensionHangMath.PartsY(pawnAlt, sunkenDeck);
                        // a sunken deck's walkers are sunk like the floor's; the floor band under it drops further again
                        float walker = pawnAlt + seed - (sunkenDeck ? RM_WallFaceMath.SunkAltitudeDrop : 0f);
                        float floor = pawnAlt + seed - RM_WallFaceMath.SunkAltitudeDrop - (sunkenDeck ? RM_SuspensionHangMath.SunkenExtraDrop : 0f);
                        string at = (sunkenDeck ? "sunken" : "surface") + " deck, seed " + seed;
                        Assert(!RM_SuspensionHangMath.RedrawCovers(pawnAlt - walker, sunkenDeck), at + ": the deck is redrawn over its own walker");
                        Assert(RM_SuspensionHangMath.RedrawCovers(pawnAlt - floor, sunkenDeck), at + ": the deck is not redrawn over the pawn beneath it");
                        Assert(deck < parts && rail < parts, at + ": posts and cables under the redrawn deck");
                        Assert(parts < walker - under && rail < walker - under && deck < walker - under, at + ": the deck or its parts over a walker's lowest layer");
                        Assert(deck > floor + over, at + ": the deck under the floor pawn's highest layer");
                        if (!sunkenDeck)
                        {
                            Assert(deck > lip, at + ": the deck under the pit's lip cover, a floor pawn would show through it");
                            Assert(!RM_SuspensionHangMath.RedrawCovers(pawnAlt - (pawnAlt + seed), true), at + ": a ground pawn picked as the floor band");
                        }
                        seen++;
                    }
                }
                Assert(seen == 82, "instrument: checked " + seen + " seeds");
            });
        }
    }
}
