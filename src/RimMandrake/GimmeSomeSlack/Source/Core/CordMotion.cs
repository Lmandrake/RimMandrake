// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Phase 1b lane A motion: the whipping live tail (B3), the downed-wire drip schedule (B4) and the
// wind sway of lifted pieces (B7, CPU path). Pure functions of (points, time, seed): the game side
// only feeds a clock and draws what comes back, so every pose here is testable offline.
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class CordMotion
    {
        /// <summary>How long the whipping end of a live floor terminal is, cells (design §8.5: ~0.4).</summary>
        public const double WhipLen = 0.4;

        /// <summary>The first Value() of new CordRng(seed ^ k*golden), computed without allocating: Whip calls this
        /// per snap interval every frame (thousands of times late in a session), so a CordRng per call was per-frame garbage.</summary>
        private static double H01(ulong seed, int k)
        {
            const ulong G = 0x9E3779B97F4A7C15UL;
            ulong z = unchecked((seed ^ (ulong)(k * 0x9E3779B1L)) ^ G) + G;   // CordRng ctor, then NextULong's state step
            z = unchecked((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL);
            z = unchecked((z ^ (z >> 27)) * 0x94D049BB133111EBUL);
            z ^= z >> 31;
            return (z >> 11) * (1.0 / 9007199254740992.0);
        }

        /// <summary>
        /// The whipping tail of a live floor terminal (phase 1b B3). tail[0] is where the tail joins the
        /// static cord and never moves; the free tip moves most (weight u^1.6). The bend is a sum of three
        /// sines plus a seeded random SNAP every 0.6-2.0 s (a sharp kick that decays in ~0.15 s), all
        /// perpendicular to the tail's own direction. t is seconds (real time in game, so a broken line is
        /// findable while paused). |displacement| never exceeds 1.9 x amp.
        /// </summary>
        internal static List<V2> Whip(IList<V2> tail, double t, ulong seed, double amp)
        {
            var o = new List<V2>(tail.Count);
            var cur = new WhipCursor();
            WhipInto(tail, t, seed, amp, o, ref cur);
            return o;
        }

        /// <summary>Where the last <see cref="WhipInto"/> call found its snap interval (GPT pre-release B15). The schedule is
        /// a running sum from t = 0, so a call that starts from the interval the previous call ended in, when the clock has
        /// not gone backwards, walks a handful of intervals instead of t/1.3 of them. Same answer either way (a selftest row
        /// compares the two). Default = start from scratch.</summary>
        public struct WhipCursor
        {
            public bool Valid;
            public int Idx;
            public double Acc, T;
        }

        /// <summary><see cref="Whip"/> into a caller's list (cleared first), resuming the snap search from
        /// <paramref name="cur"/>: no allocation, and per-frame cost no longer grows with session time.</summary>
        internal static void WhipInto(IList<V2> tail, double t, ulong seed, double amp, List<V2> o, ref WhipCursor cur)
        {
            o.Clear();
            int n = tail.Count;
            if (n < 2) { for (int i = 0; i < n; i++) o.Add(tail[i]); return; }
            double w1 = 5 + 3 * H01(seed, 1), w2 = 11 + 5 * H01(seed, 2), w3 = 2 + 1.5 * H01(seed, 3);
            double p1 = 6.283 * H01(seed, 4), p2 = 6.283 * H01(seed, 5), p3 = 6.283 * H01(seed, 6);
            double wave = 0.5 * Math.Sin(w1 * t + p1) + 0.25 * Math.Sin(w2 * t + p2) + 0.15 * Math.Sin(w3 * t + p3);
            // snaps: the timeline is cut into seeded intervals of 0.6-2.0 s; each starts with a kick
            double snap = 0, acc = H01(seed, 7) * 2.0 - 2.0;
            int idx = 0;
            double tt = t % 10000.0;
            if (cur.Valid && tt >= cur.T && cur.Acc <= tt) { acc = cur.Acc; idx = cur.Idx; }
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
            cur.Valid = true; cur.Acc = acc; cur.Idx = idx; cur.T = tt;
            for (int i = 0; i < n; i++)
            {
                double u = i / (double)(n - 1);
                Geo.TanNorm(tail, i, out V2 tg, out V2 nrm);
                double d = amp * Math.Pow(u, 1.6) * Geo.Clamp(wave + snap, -1.9, 1.9);
                o.Add(tail[i] + nrm * d);
            }
        }

        /// <summary>
        /// Wind sway of a lifted piece (phase 1b B7, CPU path; phase-2 doc §2.5 option 2): each point moves
        /// perpendicular to the piece by amp x wind x weight x (sin(wt+phi) + 0.3 sin(2.3wt+phi2)).
        /// weight is 0 at pins (a wall hole, an insulator) and rises toward the free end; wind is
        /// WindManager.WindSpeed clamped to 0..1.5. t is seconds of GAME time, so a paused frame holds.
        /// </summary>
        internal static List<V2> Sway(IList<V2> pts, IList<double> weight, double t, ulong seed, double amp, double wind)
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

        /// <summary>Peak floor-ripple displacement per unit wind, cells (optional setting, default ON since the owner's card).</summary>
        public const double RippleAmp = 0.035;

        /// <summary>
        /// Optional outdoor floor-cord ripple: a slow wave travelling along the cord, perpendicular to it, weight
        /// sin(pi u) over arc fraction u so both ends (plug, junction, stub) never move. Displacement
        /// amp x wind(0..1.5) x weight x sin(k s - w t + phi); |d| never exceeds 1.5 x amp. t is GAME seconds.
        /// </summary>
        internal static List<V2> Ripple(IList<V2> pts, double t, ulong seed, double amp, double wind)
        {
            var o = new List<V2>(pts.Count);
            double[] arc = null;
            RippleInto(pts, t, seed, amp, wind, o, ref arc);
            return o;
        }

        /// <summary><see cref="Ripple"/> into a caller's list (cleared first) with a reusable arc buffer (grown when too
        /// short). GPT pre-release B14: floorRipple is ON by default (owner card), and the allocating form made a List and an
        /// array per strand per frame for every outdoor cord on screen.</summary>
        internal static void RippleInto(IList<V2> pts, double t, ulong seed, double amp, double wind, List<V2> o, ref double[] arc)
        {
            o.Clear();
            int n = pts.Count;
            if (n < 3) { for (int i = 0; i < n; i++) o.Add(pts[i]); return; }
            if (arc == null || arc.Length < n) arc = new double[Math.Max(n, 64)];
            arc[0] = 0;
            for (int i = 1; i < n; i++) arc[i] = arc[i - 1] + V2.Dist(pts[i - 1], pts[i]);
            double len = arc[n - 1];
            if (len < 1e-9) { for (int i = 0; i < n; i++) o.Add(pts[i]); return; }
            double k = 2.4 + 1.2 * H01(seed, 21), om = 1.4 + 0.6 * H01(seed, 22), ph = 6.283 * H01(seed, 23);
            double a = amp * Geo.Clamp(wind, 0, 1.5);
            for (int i = 0; i < n; i++)
            {
                Geo.TanNorm(pts, i, out V2 tg, out V2 nrm);
                double u = arc[i] / len;
                double d = i == 0 || i == n - 1 ? 0 : a * Math.Sin(Math.PI * u) * Math.Sin(k * arc[i] - om * t + ph);
                o.Add(pts[i] + nrm * d);
            }
        }

        /// <summary>Shader-path sway weight per vertex for a lifted piece (CutoutPlant reads vertex alpha as the
        /// sway weight, PlantUtility/Plant.Print): 255 x weight x scale, 0 at pins, and ALL 0 under a roof.</summary>
        public static byte[] ShaderSwayAlpha(IList<double> weight, bool roofed, double scale)
        {
            int n = weight == null ? 0 : weight.Count;
            var a = new byte[n];
            if (roofed) return a;
            for (int i = 0; i < n; i++) a[i] = (byte)Math.Max(0, Math.Min(255, Math.Round(255.0 * weight[i] * scale)));
            return a;
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
