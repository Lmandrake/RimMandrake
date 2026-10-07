using System;
using System.Collections.Generic;

namespace RimMandrake.Ninefold
{
    /// <summary>
    /// The divine-satiation engine's arithmetic and bookkeeping decisions (GameComponent_Ninefold), with no Verse or
    /// UnityEngine type in it so the offline fuzz (Source/SelfTest/NinefoldFuzz.cs,
    /// `python3 src/RimMandrake/Utils/selftest_ninefold_fuzz.py`) compiles THIS file and drives the code the game runs.
    /// Gods are their enum ordinals (the save-format contract in God.cs). The component owns the state, the clock reads,
    /// the letters and the logging; every number and every "fire / queue / flip" decision comes from here.
    /// If a `using Verse;` lands in this file the selftest build breaks, which is the guard rail working.
    /// </summary>
    public static class RM_NinefoldKernel
    {
        public const float SatiationMin = -100f;
        public const float SatiationMax = 100f;
        public const float MoodMin = -100f;
        public const float MoodMax = 100f;

        static float Clamp(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

        /// <summary>Satiation moved by amount, held inside [-100, 100]. No drift to a baseline.</summary>
        public static float AddSatiation(float current, float amount) { return Clamp(current + amount, SatiationMin, SatiationMax); }

        /// <summary>Ta'Baa's rooted erosion for one hour: a flat decrement, held inside the band.</summary>
        public static float ErodeSatiation(float current, float erosion) { return Clamp(current - erosion, SatiationMin, SatiationMax); }

        /// <summary>
        /// One hour of a god's Mood walk: a small step scaled by amplitude (<paramref name="roll01"/> is Rand.Value),
        /// softly pulled back toward 0 so a god does not stick on a rail.
        /// </summary>
        public static float MoodStep(float mood, float amplitude, float roll01, float walkMultiplier)
        {
            float step = (roll01 - 0.5f) * 10f * amplitude * walkMultiplier;
            float pullback = -mood * 0.02f;
            return Clamp(mood + step + pullback, MoodMin, MoodMax);
        }

        /// <summary>Loudness is engagement magnitude: |satiation|.</summary>
        public static float Loudness(float satiation) { return Math.Abs(satiation); }

        /// <summary>Every god ordinal, loudest first, ties broken by ordinal (never RNG).</summary>
        public static List<int> LoudnessRank(float[] satiation)
        {
            var ranked = new List<int>(satiation.Length);
            for (int i = 0; i < satiation.Length; i++) ranked.Add(i);
            ranked.Sort((a, b) =>
            {
                int cmp = Loudness(satiation[b]).CompareTo(Loudness(satiation[a])); // descending
                return cmp != 0 ? cmp : a.CompareTo(b);
            });
            return ranked;
        }

        /// <summary>
        /// The front after an event: it moves only on a violent swing (the event's UNSCALED magnitude at or above
        /// <paramref name="largeThreshold"/>) to whoever is loudest now; before any reckoning it never moves.
        /// </summary>
        public static int FrontAfterSwing(bool frontReckoned, int frontGod, float rawAmount, float largeThreshold, int loudest)
        {
            if (!frontReckoned) return frontGod;
            if (Math.Abs(rawAmount) < largeThreshold) return frontGod;
            return loudest;
        }

        public enum Contact { None, Fire, Queued }

        /// <summary>
        /// A god's trigger fired. No-op if already unveiled or already queued; fires at once only when nothing is
        /// queued and the one-per-day gate is open; otherwise it joins the queue ("two gods never introduce
        /// themselves at once").
        /// </summary>
        public static Contact TryFirstContact(bool[] unveiled, List<int> pending, int now, int nextFirstContactTick, int god)
        {
            if (unveiled[god]) return Contact.None;
            if (pending.Contains(god)) return Contact.None;
            if (pending.Count == 0 && now >= nextFirstContactTick) return Contact.Fire;
            pending.Add(god);
            return Contact.Queued;
        }

        /// <summary>Marks a god unveiled and returns the next tick a first contact may fire.</summary>
        public static int MarkFired(bool[] unveiled, int god, int now, int oneDayTicks)
        {
            unveiled[god] = true;
            return now + oneDayTicks;
        }

        /// <summary>The next queued god due to fire (removed from the queue), or -1 when none is due.</summary>
        public static int PopDue(List<int> pending, int now, int nextFirstContactTick)
        {
            if (pending.Count == 0) return -1;
            if (now < nextFirstContactTick) return -1;
            int god = pending[0];
            pending.RemoveAt(0);
            return god;
        }

        /// <summary>Sh'kaar's counter: true once the count reaches the threshold.</summary>
        public static bool CountViolentDeath(ref int count, int threshold)
        {
            count++;
            return count >= threshold;
        }
    }
}
