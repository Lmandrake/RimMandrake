// ATMOSPHERIC_BASE_HARDEN_SMALL_LAMP_COUNTS -- the integer rules for small fixture counts, the hitch rule and the
// travelling ember. Spec: design/RimMandrake/atmospheric_base_mod_definition.md §2.6a. Pure: no Verse, no Unity.
//
//   * Percentages break on small groups (4% of 11 is 0.44; max(1, 10%) lets one lamp of one flash 100%). Every share
//     here is integer arithmetic in per-mille, with the rounding and the minimum stated, and swept 0..25 in the selftest.
//   * The pattern is a pure function of the clock, so a hitch is ONE recompute at the current time: nothing is queued,
//     so nothing is replayed, and a flicker whose window closed inside the gap is simply obsolete.
//   * L8's ember travels: a dark room's ember moves lamp to lamp on its own step, so the dark is never still.
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_Quota
    {
        /// <summary>never_tremor_reads_as_territory (the owner's bar): at no instant may more than a tenth of the driven
        /// fixtures flicker for the tremor.</summary>
        public const int TremorCeilingPerMille = 100;
        /// <summary>The smallest group in which one flicker is not more than a tenth. Below it the tremor is OFF, by the bar.</summary>
        public const int TremorMinFixtures = 1000 / TremorCeilingPerMille;
        /// <summary>L7: fast blinking is never the whole grid; above the guaranteed one, at most a tenth of the group flashes.</summary>
        public const int FlasherCeilingPerMille = 100;
        /// <summary>The smallest group that may have a flasher: one flasher and at least one fixture of slow mass.</summary>
        public const int FlasherMinFixtures = 2;

        /// <summary>A fraction as whole per-mille, rounded half away from zero; NaN, negative and zero are 0, above 1 is 1000.</summary>
        public static int PerMille(float fraction)
        {
            if (float.IsNaN(fraction) || fraction <= 0f) return 0;
            if (fraction >= 1f) return 1000;
            return (int)Math.Round(fraction * 1000.0, MidpointRounding.AwayFromZero);
        }

        /// <summary>How many fixtures may flicker for the tremor at one instant, of n driven.
        /// = min(ceil(n x share), floor(n / 10)), share clamped to the tenth. Rounding UP the asked share means a nonzero
        /// share is never silently zero once the group is big enough (n &gt;= TremorMinFixtures); the floor of the
        /// tenth means rounding up can never break the bar. Below ten fixtures one flicker would exceed a tenth, so 0.</summary>
        public static int TremorCap(int n, float share)
        {
            if (n <= 0) return 0;
            int pm = Math.Min(TremorCeilingPerMille, PerMille(share));
            if (pm == 0) return 0;
            long hard = (long)n * TremorCeilingPerMille / 1000;
            long want = ((long)n * pm + 999) / 1000;
            return (int)Math.Min(want, hard);
        }

        /// <summary>How many of a group of n play the fast flasher role when the scheme asks `requested`.
        /// = min(requested, max(1, floor(n / 10))) when n &gt;= 2 and requested &gt; 0, else 0. So: at least one whenever
        /// asked and the group has a fixture left over for the mass; never the whole group; a tenth above that.</summary>
        public static int FlasherCap(int n, int requested)
        {
            if (n < FlasherMinFixtures || requested <= 0) return 0;
            long ceiling = Math.Max(1L, (long)n * FlasherCeilingPerMille / 1000);
            return (int)Math.Min(requested, ceiling);
        }
    }

    public static class RM_Hitch
    {
        /// <summary>The longest gap between two evaluations that is still an ordinary frame. EvalEveryFrames (6) at
        /// 60 fps is 0.1 s; at 15 fps 0.4 s. Anything longer is a HITCH: counted, then the state is recomputed once
        /// at the current clock. Nothing is replayed, whatever the gap, because nothing is ever queued.</summary>
        public const double MaxDelaySeconds = 0.5;

        public static bool IsHitch(double previous, double now) => previous >= 0 && now - previous > MaxDelaySeconds;
    }

    /// <summary>L8: a chosen dark carries motion. The ember is one lit lamp per dark room, and it TRAVELS: every
    /// StepSeconds it moves to the next lamp along the room's sweep order (x, then z), turning back at either end, so
    /// consecutive positions are neighbours and the room is never still.</summary>
    public static class RM_Ember
    {
        /// <summary>The ember moves at least this often (the L8 "any 4 s window" proposal, review package §4).</summary>
        public const double StepSeconds = 4.0;

        public static long Step(double time) => (long)Math.Floor(time / StepSeconds);

        /// <summary>Position along a ping-pong walk of `count` stops at `step`: 0,1,..,count-1,count-2,..,1,0,1,..</summary>
        public static int Bounce(long step, int count)
        {
            if (count <= 1) return 0;
            long period = 2L * (count - 1);
            long k = ((step % period) + period) % period;
            return (int)(k < count ? k : period - k);
        }

        /// <summary>The lamp that holds the ember now, out of the room's eligible lamps already in sweep order; -1 for
        /// none. Two or more lamps: the bounce walk, a new lamp every step. One lamp: it alternates ember and black every
        /// step (going out is the change). No eligible lamp (the EMPTY ROOM): -1, and no lamp in that room is taken
        /// to black by the dark either, because only an eligible lamp reaches the dark at all.</summary>
        public static int Keeper(IList<int> orderedEligible, double time)
        {
            if (orderedEligible == null || orderedEligible.Count == 0) return -1;
            long step = Step(time);
            if (orderedEligible.Count == 1) return (step & 1L) == 0 ? orderedEligible[0] : -1;
            return orderedEligible[Bounce(step, orderedEligible.Count)];
        }
    }
}
