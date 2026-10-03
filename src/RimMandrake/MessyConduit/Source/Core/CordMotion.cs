// Messy Conduit core: Verse-free (see CordMath.cs header).
// Phase 1b lane A motion: the whipping live tail (B3), the downed-wire drip schedule (B4) and the
// wind sway of lifted pieces (B7, CPU path). Pure functions of (points, time, seed): the game side
// only feeds a clock and draws what comes back, so every pose here is testable offline.
using System;
using System.Collections.Generic;

namespace RimMandrake.MessyConduit.Core
{
    public static class CordMotion
    {
        /// <summary>How long the whipping end of a live floor terminal is, cells (design §8.5: ~0.4).</summary>
        public const double WhipLen = 0.4;

        private static double H01(ulong seed, int k) => new CordRng(seed ^ (ulong)(k * 0x9E3779B1L)).Value();

        /// <summary>
        /// The whipping tail of a live floor terminal (phase 1b B3). tail[0] is where the tail joins the
        /// static cord and never moves; the free tip moves most (weight u^1.6). The bend is a sum of three
        /// sines plus a seeded random SNAP every 0.6-2.0 s (a sharp kick that decays in ~0.15 s), all
        /// perpendicular to the tail's own direction. t is seconds (real time in game, so a broken line is
        /// findable while paused). |displacement| never exceeds 1.9 x amp.
        /// </summary>
        public static List<V2> Whip(IList<V2> tail, double t, ulong seed, double amp)
        {
            int n = tail.Count;
            var o = new List<V2>(n);
            if (n < 2) { o.AddRange(tail); return o; }
            double w1 = 5 + 3 * H01(seed, 1), w2 = 11 + 5 * H01(seed, 2), w3 = 2 + 1.5 * H01(seed, 3);
            double p1 = 6.283 * H01(seed, 4), p2 = 6.283 * H01(seed, 5), p3 = 6.283 * H01(seed, 6);
            double wave = 0.5 * Math.Sin(w1 * t + p1) + 0.25 * Math.Sin(w2 * t + p2) + 0.15 * Math.Sin(w3 * t + p3);
            // snaps: the timeline is cut into seeded intervals of 0.6-2.0 s; each starts with a kick
            double snap = 0, acc = H01(seed, 7) * 2.0 - 2.0;
            int idx = 0;
            double tt = t % 10000.0;
            while (acc <= tt && idx < 100000)
            {
                double len = 0.6 + 1.4 * H01(seed, 1000 + idx);
                if (tt < acc + len)
                {
                    double since = tt - acc;
                    double sgn = H01(seed, 5000 + idx) < 0.5 ? -1 : 1;
                    snap = sgn * 0.9 * Math.Exp(-since / 0.15);
                    break;
                }
                acc += len;
                idx++;
            }
            for (int i = 0; i < n; i++)
            {
                double u = i / (double)(n - 1);
                Geo.TanNorm(tail, i, out V2 tg, out V2 nrm);
                double d = amp * Math.Pow(u, 1.6) * Geo.Clamp(wave + snap, -1.9, 1.9);
                o.Add(tail[i] + nrm * d);
            }
            return o;
        }

        /// <summary>
        /// Wind sway of a lifted piece (phase 1b B7, CPU path; phase-2 doc §2.5 option 2): each point moves
        /// perpendicular to the piece by amp x wind x weight x (sin(wt+phi) + 0.3 sin(2.3wt+phi2)).
        /// weight is 0 at pins (a wall hole, an insulator) and rises toward the free end; wind is
        /// WindManager.WindSpeed clamped to 0..1.5. t is seconds of GAME time, so a paused frame holds.
        /// </summary>
        public static List<V2> Sway(IList<V2> pts, IList<double> weight, double t, ulong seed, double amp, double wind)
        {
            int n = pts.Count;
            var o = new List<V2>(n);
            double om = 1.1 + 0.5 * H01(seed, 11), ph = 6.283 * H01(seed, 12), ph2 = 6.283 * H01(seed, 13);
            double s = amp * Geo.Clamp(wind, 0, 1.5) * (Math.Sin(om * t + ph) + 0.3 * Math.Sin(2.3 * om * t + ph2));
            for (int i = 0; i < n; i++)
            {
                Geo.TanNorm(pts, i, out V2 tg, out V2 nrm);
                double wgt = weight == null || i >= weight.Count ? 0 : weight[i];
                o.Add(pts[i] + nrm * (s * wgt));
            }
            return o;
        }
    }

    public enum DripState { Drip, Flash, Quiet, Crackle }

    /// <summary>
    /// The downed-wire burst schedule of one live WALL terminal (phase 1b B4, design §8.7.2): never a
    /// steady arc, but irregular cycles of DRIP (1-4 sparks thrown downward 0.15 s apart), FLASH (a big
    /// glow for ~4 frames), QUIET (an ember) and CRACKLE (3 sparks in 0.2 s). Gaps between events are
    /// exponential, mean 0.9 s, clamped 0.3-2.5 s. Seeded per terminal; the caller supplies the clock.
    /// </summary>
    public sealed class DownedWireSchedule
    {
        public const double MeanGap = 0.9, MinGap = 0.3, MaxGap = 2.5;
        private readonly CordRng rng;
        public DripState State;
        /// <summary>When the current event started and when the next one is due (seconds).</summary>
        public double StateAt, NextAt, LastGap;
        /// <summary>Sparks the current event throws (DRIP 1-4, CRACKLE 3, else 0) and their spacing (s).</summary>
        public int Sparks;
        public double SparkSpacing;
        public int Events;

        public DownedWireSchedule(ulong seed, double now)
        {
            rng = new CordRng(seed);
            NextAt = now + rng.Range(0, MeanGap);    // terminals start out of step with each other
            State = DripState.Quiet;
            StateAt = now;
        }

        public bool Due(double now) => now >= NextAt;

        /// <summary>Start the next event at `now` and schedule the one after it.</summary>
        public DripState Advance(double now)
        {
            double r = rng.Value();
            State = r < 0.40 ? DripState.Drip : r < 0.60 ? DripState.Flash : r < 0.85 ? DripState.Quiet : DripState.Crackle;
            Sparks = State == DripState.Drip ? rng.Int(1, 4) : State == DripState.Crackle ? 3 : 0;
            SparkSpacing = State == DripState.Drip ? 0.15 : State == DripState.Crackle ? 0.07 : 0;
            double gap = -MeanGap * Math.Log(1 - rng.Value() * 0.999999);
            LastGap = Geo.Clamp(gap, MinGap, MaxGap);
            StateAt = now;
            NextAt = now + LastGap;
            Events++;
            return State;
        }

        /// <summary>Glow multiplier at time now: FLASH 2.0 for ~4 frames (0.07 s) then fading; DRIP and
        /// CRACKLE a brief 0.6-0.8 pop; QUIET an ember 0.3. Brief and irregular, never constant.</summary>
        public double Glow(double now)
        {
            double since = now - StateAt;
            switch (State)
            {
                case DripState.Flash: return since < 0.07 ? 2.0 : 0.3 + 1.7 * Math.Exp(-(since - 0.07) / 0.12);
                case DripState.Drip: return 0.3 + 0.3 * Math.Exp(-since / 0.2);
                case DripState.Crackle: return 0.3 + 0.5 * Math.Exp(-since / 0.1);
                default: return 0.3;
            }
        }

        /// <summary>How many of the current event's sparks are due by `now` (the caller throws the difference).</summary>
        public int SparksDue(double now)
        {
            if (Sparks <= 0) return 0;
            double since = now - StateAt;
            return Math.Min(Sparks, 1 + (int)Math.Floor(since / Math.Max(1e-6, SparkSpacing)));
        }
    }
}
