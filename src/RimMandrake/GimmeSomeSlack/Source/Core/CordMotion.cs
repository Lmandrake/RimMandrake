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
        /// <summary>How long the whipping end of a live floor terminal is, cells (was 0.4, shorter than its own glow: the owner, 2026-11-07,
        /// saw the end move while the spark stayed put).</summary>
        public const double WhipLen = 0.95;
        /// <summary>The whip's bend, cells: the tip's swing is up to 1.9 x this.</summary>
        public const double WhipAmp = 0.24;
        /// <summary>A fallen overhead wire is heavier and longer: its writhing end, and its bend.</summary>
        public const double WireWhipLen = 1.3, WireWhipAmp = 0.3;
        /// <summary>Seconds a bend takes to run from the joint out to the tip: the end snakes, it does not swing like a stick.</summary>
        public const double WhipLag = 0.16;

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
        /// perpendicular to the tail's own direction, and each runs out along the tail (<see cref="WhipLag"/>). t is seconds (real time in game, so a broken line is
        /// findable while paused). |displacement| never exceeds 1.9 x amp.
        /// </summary>
        internal static List<V2> Whip(IList<V2> tail, double t, ulong seed, double amp)
        {
            var o = new List<V2>(tail.Count);
            var cur = new WhipCursor();
            WhipInto(tail, t, seed, amp, o, ref cur);
            return o;
        }

        /// <summary>Where a live end's tip is on screen now: the outer point of the whip tail laid nearest it (owner 2026-11-07: "the spark of
        /// the cut powerline should follow the writhing edge of the cable"). No tail near it (whip off, far zoom, past the motion cap): the laid tip.</summary>
        internal static V2 RideTail(V2 laidTip, IList<V2> laid, IList<V2> now)
        {
            int best = RideIndex(laidTip, laid);
            return best >= 0 ? now[best] : laidTip;
        }

        /// <summary>The whip tail or swaying wall tail laid nearest this tip, or -1.</summary>
        internal static int RideIndex(V2 laidTip, IList<V2> laid)
        {
            int best = -1;
            double bd = 0.75 * 0.75;
            for (int i = 0; i < laid.Count; i++)
            {
                double dx = laid[i].X - laidTip.X, dz = laid[i].Z - laidTip.Z, d = dx * dx + dz * dz;
                if (d < bd) { bd = d; best = i; }
            }
            return best;
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
        internal static void WhipInto(IList<V2> tail, double t, ulong seed, double amp, List<V2> o, ref WhipCursor cur, double ampPos = 1, double ampNeg = 1)
        {
            o.Clear();
            int n = tail.Count;
            if (n < 2) { for (int i = 0; i < n; i++) o.Add(tail[i]); return; }
            double w1 = 5 + 3 * H01(seed, 1), w2 = 11 + 5 * H01(seed, 2), w3 = 2 + 1.5 * H01(seed, 3);
            double p1 = 6.283 * H01(seed, 4), p2 = 6.283 * H01(seed, 5), p3 = 6.283 * H01(seed, 6);
            // snaps: the timeline is cut into seeded intervals of 0.6-2.0 s; each starts with a kick
            double since = -1, kick = 0, acc = H01(seed, 7) * 2.0 - 2.0;
            int idx = 0;
            double tt = t % 10000.0;
            if (cur.Valid && tt >= cur.T && cur.Acc <= tt) { acc = cur.Acc; idx = cur.Idx; }
            while (acc <= tt && idx < 100000)
            {
                double len = 0.6 + 1.4 * H01(seed, 1000 + idx);
                if (tt < acc + len)
                {
                    since = tt - acc;
                    kick = H01(seed, 5000 + idx) < 0.5 ? -0.9 : 0.9;
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
                double lag = WhipLag * u, tu = t - lag;
                double wave = 0.5 * Math.Sin(w1 * tu + p1) + 0.25 * Math.Sin(w2 * tu + p2) + 0.15 * Math.Sin(w3 * tu + p3);
                // the kick swells in as it arrives: a step here drew a sharp zigzag at its front, running out along the tail
                double snap = since >= lag ? kick * (1 - Math.Exp(-(since - lag) / 0.035)) * Math.Exp(-(since - lag) / 0.15) : 0;
                double d = amp * Math.Pow(u, 1.6) * Geo.Clamp(wave + snap, -1.9, 1.9);
                o.Add(tail[i] + nrm * (d * (d > 0 ? ampPos : ampNeg)));
            }
        }

        /// <summary>How far this tail may swing to each side and stay on open floor (1, 0.6, 0.3 or 0 of its full swing): a cut end by a wall writhes away from
        /// it, never onto it. Reads the laid tail, so it holds still from frame to frame.</summary>
        internal static void WhipRoom(IList<V2> tail, double amp, Func<int, int, bool> open, out double ampPos, out double ampNeg)
        {
            ampPos = ampNeg = 0;
            foreach (double k in Room)
                if (TailClear(tail, 1.9 * amp * k, open)) { ampPos = k; break; }
            foreach (double k in Room)
                if (TailClear(tail, -1.9 * amp * k, open)) { ampNeg = k; break; }
        }

        private static readonly double[] Room = { 1.0, 0.6, 0.3 };

        private static bool TailClear(IList<V2> tail, double swing, Func<int, int, bool> open)
        {
            int n = tail.Count;
            for (int i = 1; i < n; i++)
            {
                Geo.TanNorm(tail, i, out V2 tg, out V2 nrm);
                double d = swing * Math.Pow(i / (double)(n - 1), 1.6);
                // every cell the point sweeps through on its way out, not only where it ends (Codex review 2026-11-09)
                if (!SweepOpen(tail[i], tail[i] + nrm * d, open)) return false;
            }
            return true;
        }

        /// <summary>True when every grid cell the segment a->b passes through is open (grid traversal, so a diagonal sweep
        /// cannot slip past a wall corner between samples).</summary>
        private static bool SweepOpen(V2 a, V2 b, Func<int, int, bool> open)
        {
            int x = (int)Math.Floor(a.X), z = (int)Math.Floor(a.Z);
            int xe = (int)Math.Floor(b.X), ze = (int)Math.Floor(b.Z);
            if (!open(x, z)) return false;
            double dx = b.X - a.X, dz = b.Z - a.Z;
            int sx = dx > 0 ? 1 : -1, sz = dz > 0 ? 1 : -1;
            double tdx = dx != 0 ? Math.Abs(1.0 / dx) : double.PositiveInfinity;
            double tdz = dz != 0 ? Math.Abs(1.0 / dz) : double.PositiveInfinity;
            double tmx = dx != 0 ? (dx > 0 ? x + 1 - a.X : a.X - x) * tdx : double.PositiveInfinity;
            double tmz = dz != 0 ? (dz > 0 ? z + 1 - a.Z : a.Z - z) * tdz : double.PositiveInfinity;
            for (int guard = Math.Abs(xe - x) + Math.Abs(ze - z); (x != xe || z != ze) && guard > 0; guard--)
            {
                if (Math.Abs(tmx - tmz) < 1e-12)
                {
                    // through a cell corner exactly: both side cells count as swept
                    if (!open(x + sx, z) || !open(x, z + sz)) return false;
                    x += sx; z += sz; tmx += tdx; tmz += tdz; guard--;
                }
                else if (tmx < tmz) { x += sx; tmx += tdx; }
                else { z += sz; tmz += tdz; }
                if (!open(x, z)) return false;
            }
            return true;
        }

        /// <summary>
        /// Wind sway of a lifted piece (phase 1b B7, CPU path; phase-2 doc §2.5 option 2): each point moves
        /// perpendicular to the piece by amp x wind x weight x (sin(wt+phi) + 0.3 sin(2.3wt+phi2)).
        /// weight is 0 at pins (a wall hole, an insulator) and rises toward the free end; wind is
        /// WindManager.WindSpeed clamped to 0..1.5. t is seconds of GAME time, so a paused frame holds.
        /// </summary>
        internal static List<V2> Sway(IList<V2> pts, IList<double> weight, double t, ulong seed, double amp, double wind)
        {
            var o = new List<V2>(pts.Count);
            SwayInto(pts, weight, t, seed, amp, wind, o);
            return o;
        }

        /// <summary>Sway into a caller-owned buffer (cleared, then refilled): the per-frame draw path allocates nothing.</summary>
        internal static void SwayInto(IList<V2> pts, IList<double> weight, double t, ulong seed, double amp, double wind, List<V2> o)
        {
            int n = pts.Count;
            o.Clear();
            double om = 1.1 + 0.5 * H01(seed, 11), ph = 6.283 * H01(seed, 12), ph2 = 6.283 * H01(seed, 13);
            double s = amp * Geo.Clamp(wind, 0, 1.5) * (Math.Sin(om * t + ph) + 0.3 * Math.Sin(2.3 * om * t + ph2));
            for (int i = 0; i < n; i++)
            {
                Geo.TanNorm(pts, i, out V2 tg, out V2 nrm);
                double wgt = weight == null || i >= weight.Count ? 0 : weight[i];
                o.Add(pts[i] + nrm * (s * wgt));
            }
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
