// Verse-free kernel of the scratching tree (RM_SweetlineScratching.cs Rub, RM_SweetlineStation.cs felt store) and the runway
// bloom's cooldown and delayed answers (RM_RunwayBloom.cs). SelfTest/LeaningScrubFuzz.cs compiles this file alone.
using System;
using System.Collections.Generic;

namespace RimMandrake.LeaningScrub
{
    public static class RM_CoatKernel
    {
        // GenMath.RoundRandom with an injected roll in [0,1): rounds up with probability equal to the fraction.
        public static int RoundRandom(float f, float roll)
        {
            int n = (int)f;
            if (roll < f - n) n++;
            return n;
        }

        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

        // A rub: amount of coat shed = RoundRandom(woolAmount * fullness); the felted share (not rounded) goes to the bark, the rest
        // (rounded) falls beside the trunk in stacks of at most stackLimit.
        public static void Rub(int woolAmount, float fullness, float feltShareSetting, float roll1, float roll2, int stackLimit,
                               out int amount, out int ground, out float felted, List<int> stacks)
        {
            amount = RoundRandom(woolAmount * fullness, roll1);
            float share = Clamp01(feltShareSetting);
            ground = RoundRandom(amount * (1f - share), roll2);
            felted = amount * share;
            if (stackLimit < 1) stackLimit = 1;
            int left = ground;
            while (left > 0)
            {
                int n = Math.Max(1, Math.Min(left, stackLimit));
                left -= n;
                stacks.Add(n);
            }
        }

        // The felt store: capped, never negative, paid out in whole units.
        public static float AddFelt(float store, float coatUnitsFelted, float feltPerUnit, float cap)
        {
            return Math.Min(cap, store + Math.Max(0f, coatUnitsFelted) * feltPerUnit);
        }
        public static int Payout(float store, bool enabled, bool hasWoolThing)
        {
            int pay = (int)Math.Floor(store);
            return (!enabled || pay <= 0 || !hasWoolThing) ? 0 : pay;
        }

        // ── runway bloom ──
        public const int CooldownTicks = 1250;
        public const float CooldownRadius = 15f;
        public const float BloomRadius = 12f;

        public static bool InBloomRadius(int ax, int az, int x, int z) { return RM_BlazeKernel.InHorDist(ax, az, x, z, BloomRadius); }
        public static int AnswerTick(int now, int delayTicks) { return now + Math.Max(0, delayTicks); }

        // The bloom's memory: recent blooms (the cooldown) and answers queued for later. T is whoever answers.
        public sealed class BloomState<T>
        {
            public readonly List<int> RecentTick = new List<int>(), RecentX = new List<int>(), RecentZ = new List<int>();
            public readonly List<int> PendingTick = new List<int>(), PendingFromX = new List<int>(), PendingFromZ = new List<int>();
            public readonly List<T> PendingWho = new List<T>();

            public void DropOldRecent(int now)
            {
                for (int i = RecentTick.Count - 1; i >= 0; i--)
                    if (now - RecentTick[i] > CooldownTicks) { RecentTick.RemoveAt(i); RecentX.RemoveAt(i); RecentZ.RemoveAt(i); }
            }

            public bool OnCooldown(int x, int z)
            {
                for (int i = 0; i < RecentTick.Count; i++)
                    if (RM_BlazeKernel.InHorDist(RecentX[i], RecentZ[i], x, z, CooldownRadius)) return true;
                return false;
            }

            public void Remember(int x, int z, int now) { RecentTick.Add(now); RecentX.Add(x); RecentZ.Add(z); }

            public void Queue(int tick, T who, int fromX, int fromZ) { PendingTick.Add(tick); PendingWho.Add(who); PendingFromX.Add(fromX); PendingFromZ.Add(fromZ); }

            // Answers that are due, newest queued first.
            public void RunPending(int now, Action<T, int, int> answer)
            {
                for (int i = PendingTick.Count - 1; i >= 0; i--)
                {
                    if (PendingTick[i] > now) continue;
                    T who = PendingWho[i]; int fx = PendingFromX[i], fz = PendingFromZ[i];
                    PendingTick.RemoveAt(i); PendingWho.RemoveAt(i); PendingFromX.RemoveAt(i); PendingFromZ.RemoveAt(i);
                    answer(who, fx, fz);
                }
            }

            public void Clear() { PendingTick.Clear(); PendingWho.Clear(); PendingFromX.Clear(); PendingFromZ.Clear(); }
        }
    }
}
