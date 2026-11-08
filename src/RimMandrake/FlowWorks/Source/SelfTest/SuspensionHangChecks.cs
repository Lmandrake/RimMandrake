// SUSPENSION_BRIDGE_READS_HUNG (Artisan pass 4, 2026-11-08): the numbers of the hung look (RM_SuspensionHangMath.cs).
// The bar: suspension_bridge_reads_hung (a deck hung between anchors over a dug hole, not a floor tile or a pier bridge).
using System;
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
        }
    }
}
