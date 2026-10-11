// KHORRAK_STEEL_DIET_TIER_1: the metal-eater kernel fuzz, moved verbatim with the mechanic from SWBestiary's BestiaryFuzz.cs
// (family "eat"). Seeded bite sequences over the PRODUCTION RM_MetalEaterKernel.Chew (every item is eventually consumed, every bite
// shrinks it, no state repeats) plus exhaustive gate tables and the donor-parity unit rows.
using System;
using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors.FuzzSelfTest
{
    internal static class MetalEaterFuzz
    {
        public static long Bites, Eaten;
        private static long Cases { get { return CreatureBehaviorsFuzz.Cases; } set { CreatureBehaviorsFuzz.Cases = value; } }
        private static long Steps { get { return CreatureBehaviorsFuzz.Steps; } set { CreatureBehaviorsFuzz.Steps = value; } }
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        public static List<string> EatCases(int n, int seed0)
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
                        var b = RM_MetalEaterKernel.Chew(full, useHp, ignore, pct, maxHp, curHp, limit, curStack); bites++; Steps++;
                        if (full) { Check(b.Destroy && bites == 1, "fully-destroy did not consume at once"); }
                        else if (useHp && !ignore) Check(b.HitPoints < curHp, $"a bite did not lower the hit points ({curHp} -> {b.HitPoints}): the creature would eat the same item forever");
                        else Check(b.StackCount < curStack, $"a bite did not shrink the stack ({curStack} -> {b.StackCount})");
                        if (!useHp || ignore) Check(b.HitPoints == curHp || full, "hit points changed on the stack path");
                        if (useHp && !ignore) Check(b.StackCount == curStack, "stack changed on the hit-point path");
                        if (b.Destroy)
                        {
                            dead = true;
                            if (!full && useHp && !ignore) Check(b.HitPoints <= 0, "destroyed while hit points remained");
                            if (!full && !(useHp && !ignore)) Check(b.StackCount < RM_MetalEaterKernel.MinStackLeft, "destroyed with a healthy stack left");
                        }
                        else
                        {
                            if (useHp && !ignore) Check(b.HitPoints > 0, "survived at zero hit points");
                            else Check(b.StackCount >= RM_MetalEaterKernel.MinStackLeft, "survived under the minimum stack");
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
                        float pri = RM_MetalEaterKernel.Priority(en, need, comp, pct, want);
                        Check(pri == (en && need && comp && pct < want ? 9.5f : 0f), $"Priority({m},{pct})");
                        Check(RM_MetalEaterKernel.Hungry(pct, want) == (pct < want), "Hungry");
                        Steps++;
                    }
                for (int m = 0; m < 16; m++)
                    Check(RM_MetalEaterKernel.DigDue((m & 1) != 0, (m & 2) != 0, (m & 4) != 0 ? 0.1f : 0.3f, 0.2f, (m & 8) != 0) == ((m & 1) != 0 && (m & 2) != 0 && (m & 4) != 0 && (m & 8) != 0), $"DigDue({m})");
                for (int m = 0; m < 8; m++)
                    Check(RM_MetalEaterKernel.BlocksNormalFood((m & 1) != 0, (m & 2) != 0, (m & 4) != 0) == (m == 7), $"BlocksNormalFood({m})");
                var c = RM_MetalEaterKernel.Chew(false, false, false, 0.2f, 100, 100, 75, 30);
                Check(c.StackCount == 15 && !c.Destroy, "steel stack of 30 loses 15");
                c = RM_MetalEaterKernel.Chew(false, false, false, 0.2f, 100, 100, 75, 24);
                Check(c.StackCount == 9 && c.Destroy, "a stack that drops under ten is eaten whole (donor parity)");
                c = RM_MetalEaterKernel.Chew(false, true, false, 0.2f, 100, 100, 75, 30);
                Check(c.HitPoints == 80 && !c.Destroy && c.StackCount == 30, "slag at 100 hit points loses 20");
                c = RM_MetalEaterKernel.Chew(false, true, false, 0.2f, 1, 1, 75, 1);
                Check(c.Destroy, "a one-hit-point item is eaten in one bite");
                c = RM_MetalEaterKernel.Chew(false, true, true, 0.2f, 100, 100, 75, 30);
                Check(c.HitPoints == 100 && c.StackCount == 15, "ignoreUseHitPoints takes the stack path");
            }
            catch (Exception e) { fails.Add("eat tables: " + e.Message); }
            return fails;
        }
    }
}
