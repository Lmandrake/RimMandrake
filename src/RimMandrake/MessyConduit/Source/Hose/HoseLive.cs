using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>What the hose's free end lies on (hose_carry_design_2026-10-04 section 7). DERIVED from where the end lies,
    /// never saved. Appended order only.</summary>
    public enum HoseEndKind { None = 0, Free = 1, Relay = 2, Port = 3, Water = 4 }

    /// <summary>
    /// Verse-free geometry of the LIVE hose (design section 6, stage S4), selftested by HoseLiveChecks: the carried hose
    /// (a cached prefix along the walked trail + a per-frame tail to the carrier's hand), the retract clip (the laid pose cut at
    /// the wound fraction), the animated auto-retract of a cut hose, and the end-kind rule.
    /// </summary>
    public static class HoseLive
    {
        /// <summary>The carried hose's corner radius where the cached prefix meets the per-frame tail (cells).</summary>
        public const double JunctionBack = 0.5;
        /// <summary>Sample spacing near / far (LOD: CameraZoomRange.Far and beyond).</summary>
        public const double SampleNear = 0.25, SampleFar = 0.5;
        /// <summary>Speed an auto-retracted (cut) hose winds back at, cells per tick (3 cells/s, the base winding speed).</summary>
        public const double AutoWindPerTick = 3.0 / 60.0;

        /// <summary>Section 7, the end-kind rule: a relay intake beats a port (pipe/tank beside the end) beats water beats
        /// nothing. No hose out = None.</summary>
        public static HoseEndKind EndKind(bool hoseOut, bool onRelay, bool besidePort, bool inWater)
        {
            if (!hoseOut) return HoseEndKind.None;
            if (onRelay) return HoseEndKind.Relay;
            if (besidePort) return HoseEndKind.Port;
            if (inWater) return HoseEndKind.Water;
            return HoseEndKind.Free;
        }

        /// <summary>The carried hose's PREFIX (rebuilt only when the walked trail changes): the trail pulled taut from the
        /// reel mouth (<paramref name="pulled"/>, HoseTrail.Pulled), corners rounded, resampled at <paramref name="step"/>, and
        /// cut back <see cref="JunctionBack"/> from its last point (the last trail cell's centre) so the per-frame tail can
        /// round the corner there. Returns the samples; <paramref name="corner"/> = the uncut last point.</summary>
        public static List<V2> Prefix(IList<V2> pulled, double bendRadius, double step, out V2 corner)
        {
            corner = pulled[pulled.Count - 1];
            if (pulled.Count < 2) return new List<V2> { pulled[0] };
            List<V2> round = pulled.Count >= 3 ? CordPlanner.RoundCorners(pulled, Math.Max(0.45, bendRadius)) : new List<V2>(pulled);
            round[0] = pulled[0];
            round[round.Count - 1] = corner;
            double L = Geo.Length(round);
            List<V2> cut = HoseTrail.Clip(round, Math.Min(JunctionBack, 0.5 * L));
            if (cut.Count < 2) return new List<V2> { round[0] };
            return Geo.Resample(cut, step);
        }

        /// <summary>The per-frame TAIL from the prefix's end <paramref name="from"/> round the corner (the last trail cell's
        /// centre) to the carrier's <paramref name="hand"/>: a quadratic curve from 'from' with the corner as control, landing
        /// on the corner-to-hand line, then straight to the hand. First point = from, last = hand.</summary>
        public static List<V2> Tail(V2 from, V2 corner, V2 hand, double step)
        {
            var o = new List<V2> { from };
            double toHand = V2.Dist(corner, hand);
            double back = V2.Dist(from, corner);
            if (toHand < 0.05 || back < 1e-6)
            {
                AddLine(o, corner, step);
                if (toHand > 1e-6) AddLine(o, hand, step);
                return o;
            }
            V2 land = corner + (hand - corner) * (Math.Min(back, toHand) / toHand);
            int n = Math.Max(2, (int)Math.Ceiling((back + V2.Dist(corner, land)) / step));
            for (int i = 1; i <= n; i++)
            {
                double t = i / (double)n, u = 1 - t;
                o.Add(from * (u * u) + corner * (2 * u * t) + land * (t * t));
            }
            AddLine(o, hand, step);
            return o;
        }

        private static void AddLine(List<V2> o, V2 to, double step)
        {
            V2 a = o[o.Count - 1];
            double d = V2.Dist(a, to);
            if (d < 1e-6) return;
            int n = Math.Max(1, (int)Math.Ceiling(d / step));
            for (int i = 1; i <= n; i++) o.Add(a + (to - a) * (i / (double)n));
        }

        /// <summary>The ribbon u offset that continues a strip of length <paramref name="len"/> started at s0 (RM_MapComponent_Hoses
        /// .Ribbon: u = 4 s0 + arc / (4 width)), so the tail's texture runs on from the prefix without a seam.</summary>
        public static double ContinueS0(double s0, double len, double width) => s0 + len / (16.0 * Math.Max(1e-6, width));

        /// <summary>Retract draw: the pose cut at the wound FRACTION of the hose (wound / total trail length, both measured in
        /// pulled cells), so the drawn length is (1 - wound/total) of the laid pose's length; the end piece rides the cut.
        /// At least the first two samples stay (the hose never draws as a single point while on screen).</summary>
        public static List<V2> ClipWound(IList<V2> pose, double wound, double total)
        {
            double L = Geo.Length(pose);
            double f = total <= 1e-9 ? 1 : Math.Max(0, Math.Min(1, wound / total));
            List<V2> c = HoseTrail.Clip(pose, f * L);
            if (c.Count < 2) c = new List<V2> { pose[0], pose[0] + (pose[Math.Min(1, pose.Count - 1)] - pose[0]) * 0.05 };
            return c;
        }

        /// <summary>The cells an auto-retracting (cut) hose has wound in <paramref name="ticks"/> after it started.</summary>
        public static double AutoWound(int ticks) => Math.Max(0, ticks) * AutoWindPerTick;

        /// <summary>Is the animated auto-retract of a hose of length L done after <paramref name="ticks"/>?</summary>
        public static bool AutoDone(int ticks, double L) => AutoWound(ticks) >= L - 1e-9;

        /// <summary>Joiner indices still on a pose clipped to <paramref name="n"/> samples (a joiner needs one sample beyond it).</summary>
        public static List<int> JointsWithin(IList<int> joints, int n)
        {
            var o = new List<int>();
            if (joints == null) return o;
            foreach (int j in joints) if (j < n - 2) o.Add(j);
            return o;
        }
    }
}
