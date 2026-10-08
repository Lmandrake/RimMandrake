// Pure decision kernels of the SWBestiary livestock (kiln-belly onnik, grief-eating moornak): no Verse, no RimWorld, no UnityEngine.
// The comps call these with the same expressions they used inline and keep the engine half (defs, messages, spawning, hediffs).
using System;
using System.Collections.Generic;

namespace RimMandrake.StarWars.Livestock
{
    /// <summary>The onnik's kiln-cycle feed ledger: spaced doses fire a good batch, a rushed dump a bad one, a long gap cools the kiln.</summary>
    public static class RSW_KilnKernel
    {
        public enum Result { Ignored, Counted, Fired }

        public struct Rules
        {
            public int DosesNeeded, WindowTicks, RushedSpanTicks, FireCooldownTicks;
            public float CooldownMultiplier;
        }

        /// <summary>The span between the first and last dose is "spaced" when it is at least the rushed span and at most the window.</summary>
        public static bool IsSpaced(int firstDoseTick, int lastDoseTick, int rushedSpanTicks, int windowTicks)
        {
            int span = lastDoseTick - firstDoseTick;
            return span >= rushedSpanTicks && span <= windowTicks;
        }

        /// <summary>Partial progress with no dose for longer than the window is lost.</summary>
        public static bool WentCold(IList<int> doses, int now, int windowTicks) { return doses.Count > 0 && now - doses[doses.Count - 1] > windowTicks; }

        /// <summary>The kiln went cold on the rare tick.</summary>
        public static void Cool(List<int> doses, int now, int windowTicks, bool enabled)
        {
            if (!enabled) return;
            if (WentCold(doses, now, windowTicks)) doses.Clear();
        }

        /// <summary>One dose eaten. Ignored: mechanic off, wrong feed, or the kiln is between batches. Counted: the dose is on the ledger.
        /// Fired: the ledger reached the needed doses; spaced says good or bad batch; the ledger is cleared and the next firing is
        /// not ready until now + the scaled cooldown.</summary>
        public static Result Register(List<int> doses, ref int nextFireReadyTick, bool enabled, bool feedMatches, int now, Rules r, out bool spaced)
        {
            spaced = false;
            if (!enabled) return Result.Ignored;
            if (!feedMatches) return Result.Ignored;
            if (now < nextFireReadyTick) return Result.Ignored;
            if (WentCold(doses, now, r.WindowTicks)) doses.Clear();
            doses.Add(now);
            if (doses.Count < r.DosesNeeded) return Result.Counted;
            spaced = IsSpaced(doses[0], doses[doses.Count - 1], r.RushedSpanTicks, r.WindowTicks);
            doses.Clear();
            nextFireReadyTick = now + Math.Max(0, (int)Math.Round(r.FireCooldownTicks * r.CooldownMultiplier));
            return Result.Fired;
        }

        public static bool FeedMatches(bool hasFeedDef, bool eatenIsFeedDef) { return !hasFeedDef || eatenIsFeedDef; }
    }

    /// <summary>The moornak's hidden grief ledger, the colony-wide unsettled hediff and the recurring release.</summary>
    public static class RSW_GriefKernel
    {
        public const int TickRareInterval = 250, TicksPerDay = 60000;

        /// <summary>Wild, awake and in the open: the per-individual self-taming gate (the roll itself is the engine's).</summary>
        public static bool CanSelfTame(bool hasFaction, bool downed, bool inMentalState, bool fogged) { return !hasFaction && !downed && !inMentalState && !fogged; }

        /// <summary>The release delay in ticks at the current slider.</summary>
        public static int ReleaseDelay(int releaseDelayTicks, float multiplier) { return (int)Math.Round(releaseDelayTicks * multiplier); }

        /// <summary>The hidden ledger after one rare tick: it grows by its daily rate and stops at its ceiling.</summary>
        public static float GrowGrief(float stored, float perDay, float max) { return Math.Min(stored + perDay * (TickRareInterval / (float)TicksPerDay), max); }

        /// <summary>The release timer starts when the animal is first seen in the player's colony.</summary>
        public static int JoinTick(int joinTick, bool playerOwned, int now) { return joinTick < 0 && playerOwned ? now : joinTick; }

        public static bool ReleaseDue(int joinTick, int now, int delay) { return joinTick >= 0 && now - joinTick >= delay; }

        /// <summary>A colonist with no unsettled hediff gets the step as its first severity; one that has it is pushed toward the target
        /// by a step and never above it. A severity already above the target (a release spike) is left alone to decay on its own.</summary>
        public static float NextUnsettled(bool has, float severity, float step, float target)
        {
            if (!has) return step;
            return Math.Max(severity, Math.Min(severity + step, target));
        }

        /// <summary>The release spike: every colonist's severity is set to the spike.</summary>
        public static float Spike(float spike) { return spike; }
    }
}
