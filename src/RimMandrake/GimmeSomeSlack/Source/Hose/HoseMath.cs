// Gimme Some Slack L6 flexible hoses, the Verse-free half (design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md
// section 3). Also compiled by Source/SelfTest (HoseSelfTest.cs): no Verse/Unity here, ever.
//
// Owner, 2026-10-02: "The flexible water hoses should be much thicker and stiffer than the wires, much like the
// fire hoses they use. And they SHOULD "plump up" when water is flowing through them and "collapse down" when
// it's not."
//
// What lives here: width rules (measured from the shipped art), the Flat/Filling/Plump/Draining state machine and
// its hysteresis, the blend and wobble curves, the hose lay (the cord planner + rope settle with the stiff hose
// parameters, a bend-radius stiffening pass, the plump pose) and install validity. All pure functions of their
// inputs; the game side feeds a clock and a CordWorld and draws what comes back.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.Hose
{
    public enum HoseVis { Flat, Filling, Plump, Draining }

    /// <summary>State-machine timing, game ticks. Defaults = shipped (HoseSettings).</summary>
    public sealed class HoseTuning
    {
        /// <summary>Flat to plump (and back) blend time.</summary>
        public int TransitionTicks = 30;
        /// <summary>Hysteresis: the signal must read not-flowing this long (two FlowWorks pulses) before a plump hose drains.</summary>
        public int ReleaseTicks = 500;
        /// <summary>Hysteresis: a hose stays plump at least this long once it got there.</summary>
        public int MinPlumpDwell = 600;
    }

    /// <summary>
    /// Flat -> Filling -> Plump -> Draining -> Flat (design 3.4). Filling starts on the first flowing reading;
    /// Plump releases only after ReleaseTicks without flow AND MinPlumpDwell in Plump (the hysteresis: a pump that
    /// stalls for a pulse never makes the hose flicker); flow during Draining re-pressurises from wherever the blend
    /// is. The blend is continuous: it never moves more than 1/TransitionTicks per tick. Fields are public so the
    /// game side can save them (CompHoseReel) and a load keeps the state.
    /// </summary>
    public sealed class HoseStateMachine
    {
        public HoseVis State = HoseVis.Flat;
        /// <summary>Tick the current state began, and the blend it began at (Filling/Draining run from there).</summary>
        public int Since;
        public double B0;
        public int LastTrue = int.MinValue / 2;
        public int PlumpSince;
        /// <summary>State changes since creation (runtime evidence for the flicker check; also saved).</summary>
        public int Transitions;

        public void Update(int now, bool signal, HoseTuning t)
        {
            if (signal) LastTrue = now;
            int T = Math.Max(1, t.TransitionTicks);
            switch (State)
            {
                case HoseVis.Flat:
                    if (signal) Go(HoseVis.Filling, now, 0);
                    break;
                case HoseVis.Filling:
                    if (B0 + (now - Since) / (double)T >= 1 - 1e-12) { Go(HoseVis.Plump, now, 1); PlumpSince = now; }
                    break;
                case HoseVis.Plump:
                    if (!signal && now - LastTrue >= t.ReleaseTicks && now - PlumpSince >= t.MinPlumpDwell) Go(HoseVis.Draining, now, 1);
                    break;
                case HoseVis.Draining:
                    double b = Blend(now, t);
                    if (signal) Go(HoseVis.Filling, now, b);
                    else if (b <= 1e-12) Go(HoseVis.Flat, now, 0);
                    break;
            }
        }

        private void Go(HoseVis s, int now, double b0)
        {
            State = s;
            Since = now;
            B0 = b0;
            Transitions++;
        }

        /// <summary>Raw blend 0 (flat) .. 1 (plump) at tick now.</summary>
        public double Blend(int now, HoseTuning t)
        {
            int T = Math.Max(1, t.TransitionTicks);
            switch (State)
            {
                case HoseVis.Plump: return 1;
                case HoseVis.Filling: return Geo.Clamp(B0 + (now - Since) / (double)T, 0, 1);
                case HoseVis.Draining: return Geo.Clamp(B0 - (now - Since) / (double)T, 0, 1);
                default: return 0;
            }
        }

        /// <summary>Cut, reregister: instantly Flat (design 3.4 last row).</summary>
        public void ResetFlat()
        {
            State = HoseVis.Flat;
            B0 = 0;
            LastTrue = int.MinValue / 2;
        }
    }

    /// <summary>Shape inputs. Defaults = shipped (HoseSettings).</summary>
    public sealed class HoseShapeParams
    {
        /// <summary>Smallest bend radius, cells (the stiffness setting; Lane A's LayParams.Hose 1.2).</summary>
        public double MinBendRadius = 1.2;
        /// <summary>Scales the S-curve slack budget.</summary>
        public double Slack = 1.0;
        /// <summary>How much plumping changes the look: swelling, straightening, wobble (0 = none).</summary>
        public double PlumpAmount = 1.0;
        public double CouplingSpacing = 8;
        /// <summary>Round 4: the reel's hose length (cells). The S-curve slack budget is capped so the laid hose never
        /// reads longer than the hose (infinity = uncapped, the offline default).</summary>
        public double MaxLength = double.PositiveInfinity;
    }

    public sealed class HoseLay
    {
        public bool Ok;
        public string Reason;
        /// <summary>The fell-back flag: the slack could not be laid clear of obstacles; Flat is the planned centreline.</summary>
        public bool FellBack;
        /// <summary>2026-10-05: the hose leaves its reel straight through the outlet coupling (Lay's startOutward held).</summary>
        public bool Outlet;
        /// <summary>Equal-arc samples of the collapsed pose, the charged pose, and the planned centreline (same count).</summary>
        public List<V2> Flat = new List<V2>(), Plump = new List<V2>(), Centre = new List<V2>();
        /// <summary>Coupling positions: the reel end, every joiner, the free end (in that order).</summary>
        public List<V2> Couplings = new List<V2>();
        /// <summary>Sample indices of the joiners between two lengths: only at real bends of the planned route, never on a
        /// straight run (owner review 2026-10-04 B17).</summary>
        public List<int> Joints = new List<int>();
        public double PathLen, FlatLen, PlumpLen, MinBendFlat, MinBendPlump;
        /// <summary>Owner decision by question card 2026-10-06 (straight lead-out): arc length of the flat hose's lead-out (the
        /// straight run out of the nozzle plus the bend that joins it to the laid hose); 0 = no outlet.</summary>
        public double LeadOutLen;
    }

    public static class HoseMath
    {
        /// <summary>Round 6 (owner 2026-10-04): a reel's hose is 40 cells by default (was 30). The route rule is unchanged: a
        /// route fits when its taut length x RouteMargin (5%) is within the hose.</summary>
        public const double DefaultMaxLength = 40;
        /// <summary>Bumped when the shipped DefaultMaxLength changes; 0 = the files written before round 6 (default 30).</summary>
        public const int MaxLengthDefaultsVersion = 1;
        public const double OldDefaultMaxLength = 30;

        /// <summary>A saved hose length under the settings key "maxLength": a file written before round 6 that still holds
        /// the old shipped default (30) gets the new default; any length the player chose (or a file already written under
        /// the new default) is kept.</summary>
        public static double MigrateMaxLength(double saved, int savedDefaultsVersion) =>
            savedDefaultsVersion < MaxLengthDefaultsVersion && Math.Abs(saved - OldDefaultMaxLength) < 0.01 ? DefaultMaxLength : saved;

        // ---------------------------------------------------------------- width rules (measured from the art)
        /// <summary>The wire strand (SectionLayer_RM_MessyCords.StrandWidth, 0.08 since cords round 5) times
        /// Strand_Jawa.png's opaque band (25 of 32 px rows). Read only by the width-ratio checks and the probe
        /// (widthOverWire); no route clearance uses it (the hose clears walls by its own centreline, HoseMath.Clear).</summary>
        public const double WireVisibleWidth = 0.08 * 25.0 / 32.0;
        /// <summary>Opaque band of the staged strips Textures/.../Hose/Strand_Flat.png (rows 2-60 of 64) and
        /// Strand_Plump.png (rows 1-62), measured 2026-10-02 (lane C cropped the v2 art to fill the strip).</summary>
        public const double FlatBand = 59.0 / 64.0, PlumpBand = 62.0 / 64.0;
        /// <summary>Visible width collapsed (0.38 cell: 6.1 of today's 0.08 wires, 4.4 of the pre-round-5 0.11 ones) and the
        /// extra a full plump adds at plump amount 1 (0.465 cell).</summary>
        public const double FlatVisible = 0.38, PlumpExtra = 0.085;

        public static double VisibleWidth(double eased, double plumpAmount) => FlatVisible + PlumpExtra * Math.Max(0, plumpAmount) * Geo.Clamp(eased, 0, 1);
        public static double MeshWidthFlat(double visible) => visible / FlatBand;
        public static double MeshWidthPlump(double visible) => visible / PlumpBand;

        /// <summary>Smoothstep: the blend eases in and out.</summary>
        public static double Ease(double b)
        {
            b = Geo.Clamp(b, 0, 1);
            return b * b * (3 - 2 * b);
        }

        // ---------------------------------------------------------------- the brief transition wobble
        public const double WobbleAmp = 0.07;

        /// <summary>Ticks after a transition starts during which the wobble is drawn.</summary>
        public static int WobbleTicks(int transitionTicks) => Math.Max(1, transitionTicks) + 60;

        public static bool WobbleActive(int ticksSinceChange, int transitionTicks) => ticksSinceChange >= 0 && ticksSinceChange < WobbleTicks(transitionTicks);

        /// <summary>Lateral offset (cells) at arc fraction s, t ticks after a state change: a bulge travelling from
        /// the reel end along the hose during the transition, ringing down after it; pinned at both ends.</summary>
        public static double Wobble(double s, int t, int transitionTicks, double plumpAmount)
        {
            if (plumpAmount <= 0 || !WobbleActive(t, transitionTicks)) return 0;
            s = Geo.Clamp(s, 0, 1);
            double T = Math.Max(1, transitionTicks);
            double c = 1.3 * t / T;                                  // the bulge front
            double bulge = Math.Exp(-Math.Pow((s - c) / 0.12, 2));
            double ring = Math.Exp(-t / 22.0) * Math.Sin(2 * Math.PI * (2.5 * s) - 0.45 * t);
            double fade = 1 - t / (double)WobbleTicks(transitionTicks);
            return WobbleAmp * plumpAmount * Math.Sin(Math.PI * s) * (0.6 * bulge + 0.6 * ring) * fade;
        }

        // ---------------------------------------------------------------- lay
        /// <summary>Plump straightens this fraction of the way from the slack pose toward the planned centreline.</summary>
        public static double Straighten(double plumpAmount) => Geo.Clamp(0.35 * plumpAmount, 0, 0.6);
        public const double EndSkip = 0.5, Sample = 0.25;

        /// <summary>
        /// Lay a hose from a (the reel) to b (the free end): plan (A*, string-pull), round, then the rope sprawl and
        /// settle with the stiff hose parameters (LayParams.Hose, few gentle S-curves, no loops), then stiffen to
        /// the minimum bend radius. Plump = the same samples pulled Straighten() toward the centreline.
        /// </summary>
        /// <param name="endInward">Round 7 (relay, owner station 42): when set, the hose's last
        /// HoseRelay.EndStraight cells run dead straight along this unit direction into <paramref name="b"/>, so the end
        /// coupling sits on the receiving reel's inlet axis instead of the last bend's tangent.</param>
        /// <param name="startOutward">2026-10-05 (owner screenshot: the hose tucked under the pump instead of entering the
        /// outlet coupling): when set, the hose's first HoseReelRect.OutletStraight cells run dead straight from
        /// <paramref name="a"/> along this unit direction, so it leaves the reel THROUGH the outlet coupling; dropped when that
        /// run is not clear.</param>
        public static HoseLay Lay(CordWorld w, V2 a, V2 b, HoseShapeParams p, ulong seed, V2? endInward = null, V2? startOutward = null)
        {
            V2 bPlan = endInward.HasValue ? b - endInward.Value * HoseRelay.EndStraight : b;
            V2 aPlan = a;
            if (startOutward.HasValue)
            {
                // plan from one bend radius past the straight run, so the first turn is a full-radius curve after the coupling
                // rather than a kink where the straightened run meets it
                double lead = OutletLead(p);
                if (OutletClear(w, a, startOutward.Value, lead)) aPlan = a + startOutward.Value * lead;
                else if (OutletClear(w, a, startOutward.Value, LeadOutStraight(p))) aPlan = a + startOutward.Value * LeadOutStraight(p);
                else return new HoseLay { Reason = LeadOutBlocked };   // owner card 2026-10-06: refused, never laid without the lead-out
            }
            CordPlan plan = CordPlanner.Plan(w, aPlan, bPlan, new List<KeyValuePair<V2, WaypointKind>>());
            if (!plan.Ok) return new HoseLay { Reason = "no route" };
            if (startOutward.HasValue) plan.Points.Insert(0, a);
            if (endInward.HasValue) plan.Points.Add(b);
            return LayOn(w, a, b, plan.Points, p, seed, endInward, startOutward);
        }

        /// <summary>Owner decision by question card 2026-10-06: how far the hose runs dead straight out of the nozzle before it
        /// may bend. Taken from the minimum bend radius: the coupling's own run (OutletStraight) plus half a radius, so a
        /// stiffer hose stands farther out of the coupling before its (never tighter than minimum) curve starts.</summary>
        public static double LeadOutStraight(HoseShapeParams p) => HoseReelRect.OutletStraight + 0.5 * Math.Max(0.45, p.MinBendRadius);

        /// <summary>The lead-out: P's start replaced by a straight run of <paramref name="straight"/> from a along u, then the
        /// shortest radius-R curve (Dubins) onto P at some arc d past the straight run, P's heading there matched. The join point
        /// is chosen among candidates d = straight + R/2 .. straight + 8R (the least extra length whose new section is clear
        /// of walls; world null = no wall test). Null when no candidate fits. <paramref name="leadLen"/> = the new section's
        /// arc length (a to the join).</summary>
        public static List<(double extra, List<V2> pts, double leadLen)> LeadOutCandidates(CordWorld w, IList<V2> P, V2 a, V2 u, double straight, double R, int max)
        {
            var outp = new List<(double extra, List<V2> pts, double leadLen)>();
            if (P == null || P.Count < 2) return outp;
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1];
            V2 s0 = a + u * straight;
            if (w != null && !Clear(w, new List<V2> { a, s0 })) return outp;
            double Rd = R * 1.05;
            var cands = new List<(double extra, List<V2> sec, int j)>();
            for (int k = 0; k < 24; k++)
            {
                double d = straight + R * (0.5 + 0.5 * k);
                if (d > L - 0.5) break;
                int j = 1;
                while (j < P.Count - 1 && s[j] < d) j++;
                double seg = s[j] - s[j - 1];
                V2 Q = seg < 1e-12 ? P[j] : P[j - 1] + (P[j] - P[j - 1]) * ((d - s[j - 1]) / seg);
                // the join's heading is the chord Q lies on, so the hose runs on from Q to P[j] with no kink
                // every Dubins word, shortest first: the shortest often turns back over the reel, the other way round is clear
                foreach (List<V2> arc in DubinsAll(s0, u, Q, (P[j] - P[j - 1]).Norm(), Rd, Sample / 4, true))
                {
                var sec = new List<V2> { a };
                int ns = Math.Max(1, (int)Math.Ceiling(straight / Sample));
                for (int i = 1; i <= ns; i++) sec.Add(a + u * (straight * i / ns));   // densified so the smooth resample keeps it straight
                sec.AddRange(arc);
                double extra = Geo.Length(sec) - d;
                int jj = V2.Dist(sec[sec.Count - 1], P[j]) < 1e-9 ? j + 1 : j;
                if (jj >= P.Count) continue;
                cands.Add((extra, sec, jj));
                }
            }
            foreach (var c in cands.OrderBy(c => c.extra))
            {
                if (w != null && !Clear(w, new List<V2>(c.sec) { P[c.j] }, 0.5)) continue;
                var o = new List<V2>(c.sec);
                for (int i = c.j; i < P.Count; i++) o.Add(P[i]);
                if (SelfIntersects(ResampleN(o, Math.Max(8, (int)(Geo.Length(o) / Sample) + 1)))) continue;   // no loops (design)
                outp.Add((c.extra, o, Geo.Length(c.sec)));
                if (outp.Count >= max) break;
            }
            return outp;
        }

        /// <summary>Points of P within <paramref name="straight"/> of a projected back onto the outlet line.</summary>
        public static void KeepStraight(List<V2> P, V2 a, V2 u, double straight)
        {
            double[] s = Geo.CumLen(P);
            P[0] = a;
            for (int i = 1; i < P.Count - 1 && s[i] <= straight + 1e-9; i++)
            {
                V2 d = P[i] - a;
                P[i] = a + u * Math.Max(0, d.X * u.X + d.Z * u.Z);
            }
        }

        /// <summary>The final pose of a lead-out candidate at n samples: resampled along its Catmull-Rom curve (a plain
        /// equal-arc resample of a polyline at another spacing reads its bends up to ~2x tighter), the straight run kept.</summary>
        public static List<V2> LeadOutFinish(CordWorld w, List<V2> o, int n, V2 a, V2 u, double straight, double R)
        {
            List<V2> X = ResampleSmooth(o, n);
            KeepStraight(X, a, u, straight);
            return X;
        }

        /// <summary>n equal-arc samples of the uniform Catmull-Rom curve through p (8 sub-steps per segment), ends exact.</summary>
        public static List<V2> ResampleSmooth(IList<V2> p, int n)
        {
            if (p.Count < 3) return ResampleN(p, n);
            var d = new List<V2>(p.Count * 8 + 1) { p[0] };
            for (int i = 0; i < p.Count - 1; i++)
            {
                V2 p0 = i > 0 ? p[i - 1] : p[0] * 2 - p[1], p1 = p[i], p2 = p[i + 1], p3 = i + 2 < p.Count ? p[i + 2] : p[i + 1] * 2 - p[i];
                for (int k = 1; k <= 8; k++)
                {
                    double t = k / 8.0, t2 = t * t, t3 = t2 * t;
                    d.Add((p1 * 2 + (p2 - p0) * t + (p0 * 2 - p1 * 5 + p2 * 4 - p3) * t2 + (p1 * 3 - p0 - p2 * 3 + p3) * t3) * 0.5);
                }
            }
            List<V2> o = ResampleN(d, n);
            o[0] = p[0];
            o[n - 1] = p[p.Count - 1];
            return o;
        }

        /// <summary>The lead-out lay's sample spacing (cells) and count for a polyline.</summary>
        public const double LeadOutSpacing = Sample;
        public static int LeadOutSamples(IList<V2> p) => Math.Max(8, (int)Math.Ceiling(Geo.Length(p) / LeadOutSpacing) + 1);

        /// <summary>MinBendRadius restricted to arc positions [skip, upTo].</summary>
        public static double MinBendRadiusUpTo(IList<V2> X, double skip, double upTo)
        {
            double[] s = Geo.CumLen(X);
            double best = 99;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > upTo) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9) best = Math.Min(best, seg / th);
            }
            return best;
        }

        private static V2 PointAt(IList<V2> P, double[] s, double t)
        {
            for (int i = 1; i < P.Count; i++)
                if (s[i] >= t) { double seg = s[i] - s[i - 1]; return seg < 1e-12 ? P[i] : P[i - 1] + (P[i] - P[i - 1]) * ((t - s[i - 1]) / seg); }
            return P[P.Count - 1];
        }

        /// <summary>The shortest path from (p0, heading h0) to (p1, heading h1) whose curvature radius is never under R (Dubins:
        /// the best of LSL, RSR, LSR, RSL, RLR, LRL), sampled about every <paramref name="step"/> from p0 (exclusive) to p1
        /// (inclusive). Every candidate is integrated and kept only if it lands on p1 heading h1. Null if none does.</summary>
        public static List<List<V2>> DubinsAll(V2 p0, V2 h0, V2 p1, V2 h1, double R, double step, bool allWords)
        {
            double Mod(double x) { x %= 2 * Math.PI; return x < 0 ? x + 2 * Math.PI : x; }
            V2 D = p1 - p0;
            double d = D.Len / R, th = Math.Atan2(D.Z, D.X);
            double al = Mod(Math.Atan2(h0.Z, h0.X) - th), be = Mod(Math.Atan2(h1.Z, h1.X) - th);
            double sa = Math.Sin(al), sb = Math.Sin(be), ca = Math.Cos(al), cb = Math.Cos(be), cab = Math.Cos(al - be);
            var cands = new List<(string w, double t, double p, double q)>();
            double tmp;
            tmp = 2 + d * d - 2 * cab + 2 * d * (sa - sb);
            if (tmp >= 0) { double at = Math.Atan2(cb - ca, d + sa - sb); cands.Add(("LSL", Mod(-al + at), Math.Sqrt(tmp), Mod(be - at))); }
            tmp = 2 + d * d - 2 * cab + 2 * d * (sb - sa);
            if (tmp >= 0) { double at = Math.Atan2(ca - cb, d - sa + sb); cands.Add(("RSR", Mod(al - at), Math.Sqrt(tmp), Mod(-be + at))); }
            tmp = -2 + d * d + 2 * cab + 2 * d * (sa + sb);
            if (tmp >= 0) { double pp = Math.Sqrt(tmp), at = Math.Atan2(-ca - cb, d + sa + sb) - Math.Atan2(-2, pp); cands.Add(("LSR", Mod(-al + at), pp, Mod(-be + at))); }
            tmp = -2 + d * d + 2 * cab - 2 * d * (sa + sb);
            if (tmp >= 0) { double pp = Math.Sqrt(tmp), at = Math.Atan2(ca + cb, d - sa - sb) - Math.Atan2(2, pp); cands.Add(("RSL", Mod(al - at), pp, Mod(be - at))); }
            tmp = (6 - d * d + 2 * cab + 2 * d * (sa - sb)) / 8;
            if (Math.Abs(tmp) <= 1) { double pp = Mod(2 * Math.PI - Math.Acos(tmp)), t = Mod(al - Math.Atan2(ca - cb, d - sa + sb) + pp / 2); cands.Add(("RLR", t, pp, Mod(al - be - t + pp))); }
            tmp = (6 - d * d + 2 * cab + 2 * d * (-sa + sb)) / 8;
            if (Math.Abs(tmp) <= 1) { double pp = Mod(2 * Math.PI - Math.Acos(tmp)), t = Mod(-al - Math.Atan2(ca - cb, d + sa - sb) + pp / 2); cands.Add(("LRL", t, pp, Mod(be - al - t + pp))); }
            var all = new List<List<V2>>();
            double h1a = Math.Atan2(h1.Z, h1.X);
            foreach (var c in cands.OrderBy(c => c.t + c.p + c.q))
            {
                List<V2> pts = DubinsSample(p0, Math.Atan2(h0.Z, h0.X), c.w, new[] { c.t * R, c.p * R, c.q * R }, R, step, out double thEnd);
                double hErr = Math.Abs(Math.Atan2(Math.Sin(thEnd - h1a), Math.Cos(thEnd - h1a)));
                if (V2.Dist(pts[pts.Count - 1], p1) > 1e-3 * Math.Max(1, R) || hErr > 1e-3) continue;
                pts[pts.Count - 1] = p1;
                all.Add(pts);
                if (!allWords) break;
            }
            return all;
        }

        public static List<V2> Dubins(V2 p0, V2 h0, V2 p1, V2 h1, double R, double step)
        {
            List<List<V2>> a = DubinsAll(p0, h0, p1, h1, R, step, false);
            return a.Count > 0 ? a[0] : null;
        }

        private static List<V2> DubinsSample(V2 p0, double th, string word, double[] lens, double R, double step, out double thEnd)
        {
            var o = new List<V2>();
            double x = p0.X, z = p0.Z;
            for (int k = 0; k < 3; k++)
            {
                double l = lens[k];
                if (l <= 1e-12) continue;
                int n = Math.Max(1, (int)Math.Ceiling(l / step));
                double ds = l / n;
                for (int i = 0; i < n; i++)
                {
                    char m = word[k];
                    if (m == 'S') { x += ds * Math.Cos(th); z += ds * Math.Sin(th); }
                    else if (m == 'L') { double t2 = th + ds / R; x += R * (Math.Sin(t2) - Math.Sin(th)); z += R * (-Math.Cos(t2) + Math.Cos(th)); th = t2; }
                    else { double t2 = th - ds / R; x += R * (-Math.Sin(t2) + Math.Sin(th)); z += R * (Math.Cos(t2) - Math.Cos(th)); th = t2; }
                    o.Add(new V2(x, z));
                }
            }
            if (o.Count == 0) o.Add(p0);
            thEnd = th;
            return o;
        }

        /// <summary>How far out of the outlet the route is planned from: the straight run plus two bend radii, so even a turn
        /// back past 90 degrees rounds after the coupling's wrap instead of kinking at it.</summary>
        public static double OutletLead(HoseShapeParams p) => HoseReelRect.OutletStraight + 2 * Math.Max(0.45, p.MinBendRadius);

        /// <summary>The outlet run from <paramref name="a"/> (plus its 0.5-cell blend) lies on open ground.</summary>
        public static bool OutletClear(CordWorld w, V2 a, V2 outward, double run = HoseReelRect.OutletStraight)
        {
            V2 e = a + outward * (run + 0.5);
            return w.InBounds(e.Floor) && w.IsWalkable(e.Floor) && SegmentClear(w, a + outward * 0.5, e);
        }

        /// <summary>Colonist-carried hose (hose_carry_design_2026-10-04 section 6, stage S2): lay the hose along the cells
        /// a colonist actually WALKED instead of a planned route. The walked cells are pulled taut from the reel's mouth
        /// (HoseTrail.Pulled: any-angle, never through a wall or a pinched diagonal) and then run through exactly Lay's
        /// round -> settle -> stiffen pipeline. An EMPTY route is the legacy / DEV "planned" hose: it is HoseMath.Lay
        /// itself, so a save written before the carry stage lays byte-identically.</summary>
        public static HoseLay LayAlong(CordWorld w, V2 a, IList<Cell> route, V2 b, HoseShapeParams p, ulong seed, V2? endInward = null, V2? startOutward = null)
        {
            if (route == null || route.Count == 0) return Lay(w, a, b, p, seed, endInward, startOutward);
            var t = new HoseTrail(a, double.PositiveInfinity);
            t.Cells.AddRange(route);
            List<V2> pts = t.Pulled(w);
            // the walked end is the end cell's centre; a relay end (or any end point off that centre) is reached from it
            if (V2.Dist(pts[pts.Count - 1], b) > 1e-6) pts.Add(b);
            if (pts.Count < 2) return new HoseLay { Reason = "no route" };
            if (startOutward.HasValue)
            {
                double lead = OutletLead(p);
                if (!OutletClear(w, a, startOutward.Value, lead)) lead = LeadOutStraight(p);
                V2 o = a + startOutward.Value * lead;
                CordPlan hop = null;
                if (!OutletClear(w, a, startOutward.Value, lead)) return new HoseLay { Reason = LeadOutBlocked };
                else if (SegmentClear(w, o, pts[1])) pts.Insert(1, o);
                else if ((hop = CordPlanner.Plan(w, o, pts[1], new List<KeyValuePair<V2, WaypointKind>>())).Ok && hop.Points.Count >= 2)
                    pts.InsertRange(1, hop.Points.Take(hop.Points.Count - 1));     // round the reel to where the walk went
                else return new HoseLay { Reason = LeadOutBlocked };
            }
            return LayOn(w, a, b, pts, p, seed, endInward, startOutward);
        }

        /// <summary>Why a nozzled reel's hose was refused: no room for the straight lead-out (owner card 2026-10-06).</summary>
        public const string LeadOutBlocked = "no room for the straight lead-out from the nozzle";
        /// <summary>Why a hose was refused because, laid, it would be longer than the hose (GPT source read B3).</summary>
        public const string LaidTooLong = "route too long (the laid hose, lead-out included, is longer than the hose)";

        /// <summary>Lay's shared tail. GPT source read 2026-10-06 B3: the laid hose is never longer than the hose. CheckInstall
        /// judges the taut route, which does not count the outlet lead-out, and the slack cap only bounds the EXTRA; so a lay
        /// over the hose's length is retried with no slack, and refused (reel retracts with the reason) if still too long.</summary>
        private static HoseLay LayOn(CordWorld w, V2 a, V2 b, List<V2> planPoints, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward = null)
        {
            HoseLay lay = LayOnce(w, a, b, planPoints, p, seed, endInward, startOutward);
            if (!lay.Ok || !Overlong(lay, p.MaxLength)) return lay;
            if (p.Slack > 0)
            {
                var taut = new HoseShapeParams { MinBendRadius = p.MinBendRadius, Slack = 0, PlumpAmount = p.PlumpAmount, CouplingSpacing = p.CouplingSpacing, MaxLength = p.MaxLength };
                HoseLay t = LayOnce(w, a, b, planPoints, taut, seed, endInward, startOutward);
                if (t.Ok && !Overlong(t, p.MaxLength)) return t;
            }
            return new HoseLay { Reason = LaidTooLong, PathLen = lay.PathLen };
        }

        public static bool Overlong(HoseLay lay, double maxLength) => Math.Max(lay.FlatLen, lay.PlumpLen) > maxLength + 1e-6;

        private static HoseLay LayOnce(CordWorld w, V2 a, V2 b, List<V2> planPoints, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward = null)
        {
            var lay = new HoseLay();
            List<V2> C = CordPlanner.RoundCorners(planPoints, Math.Max(0.45, p.MinBendRadius));
            CordLayer.ProjectOut(w, C);
            C[0] = a;
            C[C.Count - 1] = b;
            double L = Geo.Length(C);
            lay.PathLen = L;
            LayParams prm = LayParams.Hose();
            prm.MinBendRadius = p.MinBendRadius;
            prm.SlackScale = Math.Max(0, p.Slack);
            CordRng rr = CordRng.Of(seed, "hose");
            double slack = rr.Range(prm.SlackLo, prm.SlackHi) * prm.SlackScale;
            double maxExtra = prm.SlackScale <= 0 ? 0 : Math.Min(Math.Max(slack * L, prm.MinExtra * Math.Min(1, prm.SlackScale)), prm.MaxExtra);
            maxExtra = Math.Max(0, Math.Min(maxExtra, p.MaxLength / RouteMargin - L));
            List<V2> F = new List<V2>(C);
            if (L > 1.2 && slack > 0)
            {
                // big gentle S-curves (design 3.5: amplitude 0.6-1.2 cells, wavelength 6-10 cells), sized so the
                // extra length (~L (pi A / lambda)^2) stays inside the slack budget and the curvature A (2 pi /
                // lambda)^2 stays inside the bend radius; then Lane A's rope settle with the hose parameters
                F = SCurves(w, C, prm, rr, maxExtra);
                SettleStats st = CordLayer.Settle(w, F, CordLayer.PinMask(w, F), Geo.Length(F), prm);
            }
            F[0] = a;
            F[F.Count - 1] = b;
            F = Stiffen(w, F, p.MinBendRadius);
            if (!Clear(w, F))
            {
                F = Stiffen(w, C, p.MinBendRadius);
                lay.FellBack = true;
                if (!Clear(w, F)) F = Geo.Resample(C, Sample);
                // round 4: the rounded centreline itself can clip a stub corner in a one-cell zig-zag; the string-pulled
                // plan (line of sight between its corners) is the last resort, and a hose that still crosses a wall is
                // not laid at all (the reel retracts it with the reason) rather than drawn through the wall
                if (!Clear(w, F)) F = Geo.Resample(planPoints, Sample);
                if (!Clear(w, F)) { lay.Reason = "no clear route (corners too tight for the hose)"; return lay; }
            }
            int n = Math.Max(8, F.Count);
            lay.Flat = ResampleN(F, n);
            lay.Centre = ResampleN(Geo.Resample(C, Sample), n);
            double k = Straighten(p.PlumpAmount);
            var P = new List<V2>(n);
            for (int i = 0; i < n; i++) P.Add(lay.Flat[i] + (lay.Centre[i] - lay.Flat[i]) * k);
            P = ResampleN(Stiffen(w, P, p.MinBendRadius), n);
            if (!Clear(w, P)) P = new List<V2>(lay.Flat);
            lay.Plump = P;
            if (endInward.HasValue)
            {
                lay.Flat = StraightenEnd(lay.Flat, b, endInward.Value, HoseRelay.EndStraight);
                lay.Centre = StraightenEnd(lay.Centre, b, endInward.Value, HoseRelay.EndStraight);
                lay.Plump = StraightenEnd(lay.Plump, b, endInward.Value, HoseRelay.EndStraight);
            }
            if (startOutward.HasValue)
            {
                lay.Outlet = true;
                // Owner decision by question card 2026-10-06 (straight lead-out): the hose leaves the nozzle dead straight for
                // LeadOutStraight cells, then joins the laid hose by the shortest curve whose radius is never under the hose's
                // minimum (a Dubins path). The 2026-10-05 position blend (StraightenStart over 2R) bent a U-turn to ~0.02 cell.
                // No clear lead-out = refused with the reason, never laid kinked or without it.
                double S = LeadOutStraight(p), R = Math.Max(0.45, p.MinBendRadius);
                V2 u = startOutward.Value;
                var fc = LeadOutCandidates(w, lay.Flat, a, u, S, R, 4);
                var qc = LeadOutCandidates(w, lay.Plump, a, u, S, R, 4);
                bool done = false;
                foreach (var pair in fc.SelectMany(x => qc.Select(y => (x, y))).OrderBy(t => t.x.extra + t.y.extra))
                {
                    int m = Math.Max(LeadOutSamples(pair.x.pts), LeadOutSamples(pair.y.pts));
                    List<V2> f = LeadOutFinish(w, pair.x.pts, m, a, u, S, R), q = LeadOutFinish(w, pair.y.pts, m, a, u, S, R);
                    if (!Clear(w, f) || !Clear(w, q)) continue;
                    double lead = Math.Max(pair.x.leadLen, pair.y.leadLen);
                    if (Math.Min(MinBendRadiusUpTo(f, EndSkip, lead + 2 * R + 1), MinBendRadiusUpTo(q, EndSkip, lead + 2 * R + 1)) < R * 0.97) continue;
                    var cc = LeadOutCandidates(null, lay.Centre, a, u, S, R, 1);
                    lay.Flat = f;
                    lay.Plump = q;
                    lay.Centre = cc.Count > 0 ? ResampleN(cc[0].pts, m) : ResampleN(StraightenStart(lay.Centre, a, u, S), m);
                    lay.LeadOutLen = pair.x.leadLen;
                    done = true;
                    break;
                }
                if (!done) return new HoseLay { Reason = LeadOutBlocked, PathLen = L };
            }
            lay.FlatLen = Geo.Length(lay.Flat);
            lay.PlumpLen = Geo.Length(lay.Plump);
            double half = JoinerHalf(VisibleWidth(1, p.PlumpAmount));
            lay.Joints = new List<int>();
            double[] sF = Geo.CumLen(lay.Flat);
            foreach (int j in Joints(lay.Centre, p.CouplingSpacing, half, lay.Flat, lay.Plump))
            {
                // owner card 2026-10-06: no rigid joiner inside the lead-out (its straightening would kink the lead-out's bend)
                if (lay.LeadOutLen > 0 && sF[Math.Min(j, sF.Length - 1)] - half < lay.LeadOutLen + 0.5) continue;
                // round 4 (owner, station 22: "improper connectivity of two pipe segments"): the joiner is a rigid ~2.3-cell
                // run of brass and cloth, so the hose under it is drawn dead straight along the joiner's own axis; a joint
                // whose straightened run would touch a wall is dropped rather than drawn bent or clipped
                List<V2> f = StraightenAt(lay.Flat, j, half), q = StraightenAt(lay.Plump, j, half);
                if (!Clear(w, f) || !Clear(w, q)) continue;
                lay.Flat = f;
                lay.Plump = q;
                lay.Joints.Add(j);
            }
            lay.FlatLen = Geo.Length(lay.Flat);
            lay.PlumpLen = Geo.Length(lay.Plump);
            lay.MinBendFlat = MinBendRadius(lay.Flat, EndSkip);
            lay.MinBendPlump = MinBendRadius(lay.Plump, EndSkip);
            lay.Couplings = new List<V2> { lay.Flat[0] };
            foreach (int j in lay.Joints) lay.Couplings.Add(lay.Flat[j]);
            lay.Couplings.Add(lay.Flat[lay.Flat.Count - 1]);
            lay.Ok = true;
            return lay;
        }

        /// <summary>The slack pose: a seeded sinusoid across the planned centreline, ramped to zero over 1.5 cells at
        /// each end, each point's offset shrunk until it sits clear of obstacles.</summary>
        public static List<V2> SCurves(CordWorld w, List<V2> C, LayParams prm, CordRng rr, double maxExtra)
        {
            List<V2> P = Geo.Resample(C, 0.1);
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1];
            double lambda = rr.Range(prm.ExcursionLo, prm.ExcursionHi);
            double aBudget = lambda / Math.PI * Math.Sqrt(Math.Max(0, maxExtra) / Math.Max(L, 1e-6));
            double aBend = lambda * lambda / (4 * Math.PI * Math.PI * Math.Max(0.2, prm.MinBendRadius));
            double amp = Math.Min(rr.Range(0.6, 1.2), Math.Min(aBudget, aBend));
            double ph = rr.Value() < 0.5 ? 0 : Math.PI;
            var o = new List<V2>(P.Count);
            for (int i = 0; i < P.Count; i++)
            {
                double ramp = Geo.Clamp(Math.Min(s[i], L - s[i]) / 1.5, 0, 1);
                ramp = ramp * ramp * (3 - 2 * ramp);
                double off = amp * ramp * Math.Sin(2 * Math.PI * s[i] / lambda + ph);
                Geo.TanNorm(P, i, out V2 t, out V2 n);
                V2 q = P[i] + n * off;
                for (int k = 0; k < 6 && w.Clearance(q) < LayParams.RC + 0.12; k++) { off *= 0.6; q = P[i] + n * off; }
                o.Add(q);
            }
            o[0] = C[0];
            o[o.Count - 1] = C[C.Count - 1];
            return Geo.Resample(o, prm.SampleStep > 0 ? prm.SampleStep : 0.25);
        }

        /// <summary>True when no part of the hose centreline lies over a blocked cell. Round 4 (owner, station 23): testing
        /// only the 0.25-cell samples let a stiffened hose cut the corner of a one-cell wall stub between two samples (his
        /// zig-zag maze measured 28 fine samples inside walls); every segment is now walked at 0.05 cell. The first and
        /// last 0.5 cell are exempt (the reel and the free end may sit on a building's cell).</summary>
        /// <summary>How far a centreline point may graze into a wall cell (cells): a string-pulled line touching a wall
        /// corner exactly is not a clip; a hose centre 0.06 inside a wall is (the hose itself is ~0.4 wide).</summary>
        public const double ClipTolerance = 0.06;

        /// <summary>Depth of q inside a blocked cell (0 when its cell is walkable): distance to the cell's nearest edge.</summary>
        public static double WallDepth(CordWorld w, V2 q)
        {
            Cell c = q.Floor;
            if (w.IsWalkable(c)) return 0;
            double fx = q.X - c.X, fz = q.Z - c.Z;
            return Math.Min(Math.Min(fx, 1 - fx), Math.Min(fz, 1 - fz));
        }

        public static bool Clear(CordWorld w, IList<V2> pts) => Clear(w, pts, 0.5);

        public static bool Clear(CordWorld w, IList<V2> pts, double endSkip)
        {
            if (pts.Count < 2) return true;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            Cell prev = pts[0].Floor;
            for (int i = 1; i < pts.Count; i++)
            {
                double d = s[i] - s[i - 1];
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.05));
                for (int j = 0; j <= k; j++)
                {
                    double at = s[i - 1] + d * j / k;
                    V2 q = pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k);
                    Cell c = q.Floor;
                    bool ends = at < endSkip || L - at < endSkip;
                    // a diagonal step between two cells whose shared corner is pinched by walls on BOTH other cells: the
                    // hose would slip through a zero-width gap between two wall corners (measured in the owner's maze:
                    // a 43-cell route laid 35 cells long by squeezing between diagonal stubs)
                    if (!ends && c.X != prev.X && c.Z != prev.Z && !w.IsWalkable(new Cell(c.X, prev.Z)) && !w.IsWalkable(new Cell(prev.X, c.Z)))
                        return false;
                    prev = c;
                    if (!ends && WallDepth(w, q) > ClipTolerance) return false;
                }
            }
            return true;
        }

        /// <summary>Bend-radius stiffening, coarse to fine (0.75, 0.5, then Sample-cell spacing: a midpoint pull is a
        /// diffusion, so a tight wrap spreads over many fine samples only after it has spread over a few coarse ones).
        /// Phase A first eases the hose away from obstacles; phase B pulls every point turning tighter than seg/minR
        /// toward its neighbours' midpoint and keeps the floor rule. The two ends are pins. Bounded iterations.</summary>
        public static List<V2> Stiffen(CordWorld w, List<V2> X0, double minR)
        {
            if (X0.Count < 4 || minR <= 0) return X0;
            List<V2> X = X0;
            foreach (double sp in new[] { 0.75, 0.5, Sample })
            {
                X = Geo.Resample(X, sp);
                X[0] = X0[0];
                X[X.Count - 1] = X0[X0.Count - 1];
                if (X.Count < 4) continue;
                if (w != null && sp == 0.75) EaseOffObstacles(w, X, minR);
                StiffenPass(w, X, minR, 1500);
            }
            return X;
        }

        /// <summary>Phase A. A stiff hose cannot hug an obstacle corner: wrapped round one at clearance d its bend
        /// radius is ~d, and the midpoint pull alone drives it INTO the corner (SelfTest "around a wall" measured
        /// 1.03 at clearance 0.10). So the points near an obstacle ease away toward clearance ~minR, with a light
        /// smoothing of those points only (open-floor S-curves untouched), accepting only steps that improve
        /// clearance (a 1-cell doorway keeps it centred, no jitter). LEARNED: pushing only the tight points made it
        /// worse (0.66) and pushing inside the stiffen loop at fine spacing left kinks (0.55).</summary>
        private static void EaseOffObstacles(CordWorld w, List<V2> X, double minR)
        {
            int n = X.Count;
            double dT = 1.1 * minR;
            var tmp = new V2[n];
            var near = new bool[n];
            for (int it = 0; it < 60; it++)
            {
                for (int i = 1; i < n - 1; i++)
                {
                    double c = w.Clearance(X[i]);
                    near[i] = c < dT;
                    if (!near[i]) continue;
                    V2 g = w.ClearanceGradient(X[i]);
                    if (g.Len < 1e-9) continue;
                    V2 q = X[i] + g * Math.Min(0.08, dT - c);
                    if (w.Clearance(q) > c + 1e-6) X[i] = q;
                }
                for (int i = 0; i < n; i++) tmp[i] = X[i];
                for (int i = 1; i < n - 1; i++)
                    if (near[i] || near[i - 1] || near[i + 1]) X[i] = tmp[i] + ((tmp[i - 1] + tmp[i + 1]) * 0.5 - tmp[i]) * 0.3;
                CordLayer.ProjectOut(w, X);
            }
        }

        internal static void StiffenPass(CordWorld w, List<V2> X, double minR, int iters)
        {
            int n = X.Count;
            for (int it = 0; it < iters; it++)
            {
                bool any = false;
                for (int i = 1; i < n - 1; i++)
                {
                    double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                    double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                    double maxT = seg / (minR * 1.02);
                    if (th <= maxT) continue;
                    V2 avg = (X[i - 1] + X[i + 1]) * 0.5;
                    X[i] = X[i] + (avg - X[i]) * Math.Min(0.9, 1 - maxT / th + 0.05);
                    any = true;
                }
                if (w != null) CordLayer.ProjectOut(w, X);
                if (!any) break;
            }
        }

        /// <summary>n equal-arc samples of a polyline (both ends kept exactly).</summary>
        public static List<V2> ResampleN(IList<V2> p, int n)
        {
            double[] s = Geo.CumLen(p);
            double L = s[s.Length - 1];
            var o = new List<V2>(n);
            int j = 0;
            for (int i = 0; i < n; i++)
            {
                double t = L * i / (n - 1);
                while (j < s.Length - 2 && s[j + 1] < t) j++;
                double seg = s[j + 1] - s[j];
                double u = seg < 1e-12 ? 0 : (t - s[j]) / seg;
                o.Add(p[j] + (p[j + 1] - p[j]) * Geo.Clamp(u, 0, 1));
            }
            o[0] = p[0];
            o[n - 1] = p[p.Count - 1];
            return o;
        }

        /// <summary>The drawn pose: flat-to-plump by the EASED blend e, plus the transition wobble t ticks after the
        /// last state change (perpendicular to the hose, pinned at the ends).</summary>
        public static List<V2> Pose(HoseLay lay, double e, int ticksSinceChange, int transitionTicks, double plumpAmount)
        {
            int n = lay.Flat.Count;
            var o = new List<V2>(n);
            for (int i = 0; i < n; i++) o.Add(lay.Flat[i] + (lay.Plump[i] - lay.Flat[i]) * e);
            if (!WobbleActive(ticksSinceChange, transitionTicks) || plumpAmount <= 0) return o;
            var w = new List<V2>(n);
            for (int i = 0; i < n; i++)
            {
                Geo.TanNorm(o, i, out V2 t, out V2 nn);
                w.Add(o[i] + nn * Wobble(i / (double)(n - 1), ticksSinceChange, transitionTicks, plumpAmount));
            }
            return w;
        }

        /// <summary>Smallest discrete bend radius (segment / turning angle) over points more than skip cells from either end.</summary>
        public static double MinBendRadius(IList<V2> X, double skip)
        {
            double[] s = Geo.CumLen(X);
            double L = s[s.Length - 1], best = 99;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > L - skip) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9) best = Math.Min(best, seg / th);
            }
            return best;
        }

        /// <summary>True when two non-adjacent segments cross (a loop).</summary>
        public static bool SelfIntersects(IList<V2> X)
        {
            int n = X.Count;
            for (int i = 0; i < n - 1; i++)
                for (int j = i + 2; j < n - 1; j++)
                    if (Cross(X[i], X[i + 1], X[j], X[j + 1])) return true;
            return false;
        }

        private static bool Cross(V2 a, V2 b, V2 c, V2 d)
        {
            double d1 = Orient(c, d, a), d2 = Orient(c, d, b), d3 = Orient(a, b, c), d4 = Orient(a, b, d);
            return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
        }

        private static double Orient(V2 a, V2 b, V2 c) => (b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X);

        /// <summary>How much the route turns at sample i, over +-1 cell of arc (radians).</summary>
        public static double TurnAt(IList<V2> C, double[] s, int i, double half = 1.0)
        {
            int a = i, b = i;
            while (a > 0 && s[i] - s[a] < half) a--;
            while (b < C.Count - 1 && s[b] - s[i] < half) b++;
            if (a == i || b == i) return 0;
            V2 u = C[i] - C[a], v = C[b] - C[i];
            double cr = u.X * v.Z - u.Z * v.X, dt = u.X * v.X + u.Z * v.Z;
            return Math.Abs(Math.Atan2(cr, dt));
        }

        /// <summary>Bend threshold for a joiner (radians, 35 deg over 2 cells of route). PROVISIONAL.</summary>
        public const double JointTurn = 35 * Math.PI / 180;

        /// <summary>
        /// Where one hose length is screwed to the next (owner review 2026-10-04 B17: "no connector along a straight
        /// length"): at the sharpest point of each bend of the PLANNED route (the centreline, not the slack wiggles),
        /// at least <paramref name="minSpacing"/> cells apart and 1.5 cells clear of either end. A straight hose has none.
        /// </summary>
        public static List<int> Joints(IList<V2> C, double minSpacing) => Joints(C, minSpacing, 0);

        /// <summary>Half the length of a joiner (two couplings face to face plus their cloth wraps), cells, on a hose of
        /// <paramref name="visible"/> width: brass face to wrap end = 0.49 x fitting size + 0.55 (DrawEnds' Fitting).</summary>
        public static double JoinerHalf(double visible) => JoinerWrapIn * FittingSize(visible, PieceBand, CouplingMax) + WrapLength;

        /// <summary>2026-10-05 (owner screenshot: a joiner read as "two flanged collars with a gap and a smaller ring floating
        /// between"): each half's wrap runs right up to the interlocked claws -- its inner edge <see cref="JoinerWrapIn"/> x the
        /// fitting size from the joint (the claws of the two mirrored couplings span +-0.08 there; Coupling_Bare.png lugs at
        /// u 96-112 of 128) -- so wrap, claws and wrap read as one fitting with no narrow coupling body or bare hose between.</summary>
        public const double JoinerWrapIn = 0.09;

        /// <summary>Art geometry of the coupling (measured 2026-10-02/04; RM_MapComponent_Hoses draws with these): the
        /// hose band where the hose enters it, its widest band (canvas fractions) and its brass face (canvas units).</summary>
        public const double PieceBand = 0.25, CouplingMax = 0.508, JoinerFace = 0.46;
        /// <summary>Centre offset (x fitting size) of each half of a JOINER. Owner 2026-10-05: the brass must look screwed together, not two
        /// couplings with a dark gap between them. Measured on Coupling_Bare.png (128px): the claw shoulder sits at u 105, the threaded
        /// stub's tip at u 122, so (105/128 - 0.5) = 0.32 puts the two shoulders against each other at the joint and the stubs overlap
        /// (mirrored, so they coincide) instead of standing apart. JoinerFace stays for an end coupling meeting a port or the reel.</summary>
        public const double JoinerMesh = 0.33;

        /// <summary>Most a joiner's run may turn and still count as straight (radians).</summary>
        public const double JointStraight = 10 * Math.PI / 180;

        /// <summary>
        /// Round 4 (owner, station 22): the joiners still mark the BENDS (B17: one per real bend, none along a straight
        /// length), but a rigid joiner cannot sit ON a bend: at the apex its brass lay across the corner while both hose
        /// lengths bent away from it. Each bend's joiner slides along the route to the nearest place where the next
        /// 2 x <paramref name="half"/> cells of planned route are straight (turn under JointStraight), clear of both ends
        /// and of the other joiners; a bend with no straight run near it (within 3 cells) gets none.
        /// </summary>
        public static List<int> Joints(IList<V2> C, double minSpacing, double half, params IList<V2>[] drawn)
        {
            List<int> bends = BendJoints(C, minSpacing);
            if (half <= 0) return bends;
            double[] s = Geo.CumLen(C);
            double[][] ds = drawn.Select(d => Geo.CumLen(d)).ToArray();
            double L = s[s.Length - 1];
            var o = new List<int>();
            foreach (int b in bends)
            {
                int best = -1;
                double bestD = double.MaxValue;
                for (int k = 1; k < C.Count - 1; k++)
                {
                    double dist = Math.Abs(s[k] - s[b]);
                    if (dist > 3 || dist >= bestD) continue;
                    if (s[k] - half < 0.75 || L - s[k] - half < 0.75) continue;
                    if (o.Any(j => Math.Abs(s[j] - s[k]) < 2 * half + 0.5)) continue;
                    if (RunTurn(C, s, s[k] - half, s[k] + half) > JointStraight) continue;
                    // ...and the drawn poses (with their slack S-curves) are nearly straight there too, so laying the run on
                    // its chord is a small correction, not a new kink
                    bool bent = false;
                    for (int q = 0; q < drawn.Length && !bent; q++)
                        bent = drawn[q].Count != C.Count || RunTurn(drawn[q], ds[q], ds[q][k] - half - 0.5, ds[q][k] + half + 0.5) > JointStraight;
                    if (bent) continue;
                    best = k;
                    bestD = dist;
                }
                if (best >= 0) o.Add(best);
            }
            o.Sort();
            return o;
        }

        /// <summary>Total absolute turning of the polyline between arc positions a and b (radians).</summary>
        public static double RunTurn(IList<V2> C, double[] s, double a, double b)
        {
            double t = 0;
            for (int i = 1; i < C.Count - 1; i++)
            {
                if (s[i] <= a || s[i] >= b) continue;
                V2 u = C[i] - C[i - 1], v = C[i + 1] - C[i];
                if (u.Len < 1e-9 || v.Len < 1e-9) continue;
                t += Math.Abs(Math.Atan2(u.X * v.Z - u.Z * v.X, u.X * v.X + u.Z * v.Z));
            }
            return t;
        }

        /// <summary>The pose with the run [s_j - half, s_j + half] laid on its chord (equal-arc along it), blended back into
        /// the hose over 0.5 cell either side, so the joiner's rigid brass and the hose under it share one axis.</summary>
        /// <summary>Round 7: the last <paramref name="straight"/> cells of P laid on the line into <paramref name="end"/> along
        /// <paramref name="inward"/> (blended back over 0.5 cell), the end exactly at <paramref name="end"/>.</summary>
        public static List<V2> StraightenEnd(IList<V2> P, V2 end, V2 inward, double straight, double blend = 0.5)
        {
            var o = new List<V2>(P);
            if (P.Count < 2) return o;
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1];
            for (int i = 1; i < P.Count; i++)
            {
                double back = L - s[i];
                double w = back <= straight ? 1 : back < straight + blend ? 1 - (back - straight) / blend : 0;
                if (w <= 0) continue;
                w = w >= 1 ? 1 : w * w * (3 - 2 * w);
                V2 line = end - inward * Math.Min(back, straight + blend);
                o[i] = P[i] + (line - P[i]) * w;
            }
            o[P.Count - 1] = end;
            return o;
        }

        /// <summary>2026-10-05: StraightenEnd mirrored -- the first <paramref name="straight"/> cells of P on the line out of
        /// <paramref name="start"/> along <paramref name="outward"/>, blended back over 0.5 cell.</summary>
        public static List<V2> StraightenStart(IList<V2> P, V2 start, V2 outward, double straight, double blend = 0.5)
        {
            var r = new List<V2>(P);
            r.Reverse();
            List<V2> o = StraightenEnd(r, start, outward * -1, straight, blend);
            o.Reverse();
            return o;
        }

        /// <summary>The point <paramref name="back"/> cells of arc before P's last point (interpolated).</summary>
        public static V2 PointBack(IList<V2> P, double back)
        {
            double[] s = Geo.CumLen(P);
            return At(P, s, Math.Max(0, s[s.Length - 1] - back));
        }

        public static List<V2> StraightenAt(IList<V2> P, int j, double half)
        {
            var o = new List<V2>(P);
            if (P.Count < 3 || j <= 0 || j >= P.Count - 1) return o;
            double[] s = Geo.CumLen(P);
            double L = s[s.Length - 1], s0 = Math.Max(0, s[j] - half), s1 = Math.Min(L, s[j] + half);
            V2 a = At(P, s, s0), b = At(P, s, s1);
            if (s1 - s0 < 1e-6) return o;
            const double blend = 0.5;
            for (int i = 1; i < P.Count - 1; i++)
            {
                double w = s[i] < s0 ? 1 - (s0 - s[i]) / blend : s[i] > s1 ? 1 - (s[i] - s1) / blend : 1;
                if (w <= 0) continue;
                w = w >= 1 ? 1 : w * w * (3 - 2 * w);
                V2 line = a + (b - a) * ((s[i] - s0) / (s1 - s0));
                o[i] = P[i] + (line - P[i]) * w;
            }
            return o;
        }

        /// <summary>P without its first <paramref name="cut"/> cells of arc (the new first point interpolated); P itself when
        /// the cut is not positive or would leave less than 0.5 cell.</summary>
        public static List<V2> TrimStart(IList<V2> P, double cut)
        {
            if (cut <= 0 || P.Count < 2) return new List<V2>(P);
            double[] s = Geo.CumLen(P);
            if (s[s.Length - 1] - cut < 0.5) return new List<V2>(P);
            var o = new List<V2> { At(P, s, cut) };
            for (int i = 0; i < P.Count; i++) if (s[i] > cut + 1e-6) o.Add(P[i]);
            return o;
        }

        private static V2 At(IList<V2> P, double[] s, double t)
        {
            int k = 0;
            while (k < s.Length - 2 && s[k + 1] < t) k++;
            double seg = s[k + 1] - s[k];
            double u = seg < 1e-12 ? 0 : (t - s[k]) / seg;
            return P[k] + (P[k + 1] - P[k]) * Geo.Clamp(u, 0, 1);
        }

        private static List<int> BendJoints(IList<V2> C, double minSpacing)
        {
            var o = new List<int>();
            if (C.Count < 5) return o;
            double[] s = Geo.CumLen(C);
            double L = s[s.Length - 1];
            var turn = new double[C.Count];
            for (int i = 0; i < C.Count; i++) turn[i] = TurnAt(C, s, i);
            var cand = new List<int>();
            for (int i = 1; i < C.Count - 1; i++)
                if (turn[i] >= JointTurn && turn[i] >= turn[i - 1] && turn[i] > turn[i + 1] && s[i] > 1.5 && L - s[i] > 1.5) cand.Add(i);
            foreach (int i in cand.OrderByDescending(i => turn[i]))
                if (o.All(j => Math.Abs(s[j] - s[i]) >= Math.Max(2, minSpacing))) o.Add(i);
            o.Sort();
            return o;
        }

        /// <summary>Hose ends (owner review 2026-10-04 B22): every end and every joiner piece sits behind a dense cloth
        /// BINDING WRAP, wider than the hose, that hides the hose-to-fitting transition for any hose type. The wrap is
        /// <see cref="WrapK"/> x the hose's visible width across and <see cref="WrapLength"/> cell along it.</summary>
        public const double WrapK = 1.3, WrapLength = 0.6;
        public static double WrapWidth(double visible) => WrapK * visible;

        /// <summary>Draw size of a fitting (canvas cells) on a hose of <paramref name="visible"/> width: matched to the hose
        /// by its hose band, but never so big that its widest part (<paramref name="maxBand"/>, canvas fraction) reads
        /// wider than 0.95 x the wrap (B22: "the fitting must not look wider than the wrap").</summary>
        public static double FittingSize(double visible, double hoseBand, double maxBand) =>
            Math.Min(visible / hoseBand, 0.95 * WrapWidth(visible) / maxBand);

        /// <summary>A joiner is TWO couplings face to face, each on its own length, so it reads as two lengths screwed
        /// tightly together (B9), never as one hose end lying across another. Centres of the forward piece (pointing
        /// along +d) and the backward piece (pointing along -d) for a joint at J; the brass faces meet at J.</summary>
        public static void JoinerPoses(V2 J, V2 d, double size, double face, out V2 forward, out V2 backward)
        {
            forward = J - d * (face * size);
            backward = J + d * (face * size);
        }

        /// <summary>Altitude lift of the hose ranked <paramref name="rank"/> (0 = oldest reel) so crossings draw one hose
        /// cleanly over the other (B18). Each band holds a hose's own steps (shadow -0.0004 .. fittings +0.001); bands are
        /// 0.0016 apart and capped at 12 ranks so the top band stays below the next altitude layer (0.0390625 away).</summary>
        public const double CrossBand = 0.0016;
        public const int CrossRanks = 12;
        public static float CrossLift(int rank) => (float)(CrossBand * Math.Max(0, Math.Min(CrossRanks, rank)));

        public static List<V2> Couplings(IList<V2> X, double spacing)
        {
            var o = new List<V2> { X[0] };
            double[] s = Geo.CumLen(X);
            double L = s[s.Length - 1];
            spacing = Math.Max(2, spacing);
            int j = 0;
            for (double at = spacing; at < L; at += spacing)
            {
                while (j < s.Length - 2 && s[j + 1] < at) j++;
                double seg = s[j + 1] - s[j];
                double u = seg < 1e-12 ? 0 : (at - s[j]) / seg;
                o.Add(X[j] + (X[j + 1] - X[j]) * u);
            }
            o.Add(X[X.Count - 1]);
            return o;
        }

        // ---------------------------------------------------------------- install validity
        /// <summary>Null when a hose may be laid from the reel cell to target, else the reason. maxLength is the
        /// hose's length (cells): the straight distance and the planned route must both fit it.</summary>
        public static string CheckInstall(CordWorld w, Cell reel, Cell target, double maxLength) =>
            CheckInstall(w, new HoseReelRect(reel.X, reel.Z, 1, 1), target, maxLength);

        /// <summary>Any reel footprint (round 3: the reel is 2x2). Distances run from the reel's CENTRE (where the hose
        /// leaves it); the route is A* from the reel cell nearest the target plus the hop from the centre to that cell.</summary>
        public static string CheckInstall(CordWorld w, HoseReelRect reel, Cell target, double maxLength)
        {
            if (!w.InBounds(target)) return "out of bounds";
            if (reel.Contains(target)) return "same cell";
            if (V2.Dist(reel.Centre, target.Centre) > maxLength) return "too far";
            if (!w.IsWalkable(target)) return "target blocked";
            // round 5: the search is bounded by the hose's length, so any route that fits is found however winding; only
            // when none is within reach does an unbounded search tell "too long" (a way exists) from "no route"
            // GPT source read 2026-10-06 B2: the question is "does a route FIT", so the route is the SHORTEST one (ExtraCost off);
            // the cost-first search returned a cheaper, longer dry detour and refused a costly corridor that fits
            double len = RouteLength(w, reel, target, maxLength, false);
            if (len < 0) len = RouteLength(w, reel, target, -1, false);
            if (len < 0) return "no route";
            if (len * RouteMargin > maxLength) return "route too long";
            return null;
        }

        /// <summary>Hose a route needs beyond its pulled-taut length (slack, bends round corners): 5%.</summary>
        public const double RouteMargin = 1.05;

        /// <summary>Round 4 (owner, station 23): the length a hose needs from the reel to target, or -1 for no route. The
        /// cell route pulled taut (any-angle, never through a wall or a pinched diagonal), from the reel's mouth. Round 3
        /// summed the cell path's centre-to-centre steps x1.08: a staircase, which over-read the owner's zig-zag maze at
        /// 48.5 cells where the hose actually lays 35. maxLength (the hose) bounds the search (RouteCells); without it the
        /// search runs to <see cref="RouteMaxExpand"/>.</summary>
        public static double RouteLength(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1, bool costs = true)
        {
            List<V2> p = RoutePulled(w, reel, target, maxLength, costs);
            return p == null ? -1 : Geo.Length(p);
        }

        public static List<V2> RoutePulled(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1, bool costs = true)
        {
            Cell s = reel.StartCellToward(target);
            List<Cell> path = RouteCells(w, s, target, maxLength > 0 ? SearchLengthBound(maxLength) : -1, costs);
            if (path == null) return null;
            var pts = new List<V2> { reel.Mouth };
            for (int i = 0; i < path.Count; i++) if (i > 0 || V2.Dist(path[0].Centre, reel.Mouth) > 1e-9) pts.Add(path[i].Centre);
            var o = new List<V2> { pts[0] };
            int a = 0;
            while (a < pts.Count - 1)
            {
                int b = a + 1;
                for (int j = pts.Count - 1; j > a + 1; j--) if (SegmentClear(w, pts[a], pts[j])) { b = j; break; }
                o.Add(pts[b]);
                a = b;
            }
            return o;
        }

        /// <summary>Round 5 (owner, station 34: "when challenged by a complex path it gave up and reeled in. Needs a longer
        /// path search."). The longest CELL path (8-way steps through cell centres) worth searching for a hose of
        /// maxLength: a route fits when its taut length x RouteMargin is within the hose, and a cell path through a
        /// one-cell zig-zag maze runs up to ~1.3x its taut length (round 4: 44.9 vs 35), so 1.5x + 4 never cuts off a
        /// route that fits. A 40-cell hose (the default since round 6) searches cell paths up to 61.1.</summary>
        public static double SearchLengthBound(double maxLength) => 1.5 * maxLength / RouteMargin + 4;

        /// <summary>Unbounded search (no hose length given, or the bounded search found nothing and the reason must be told
        /// apart): every cell of a 300x300 map, enough for any map a colony plays on.</summary>
        public const int RouteMaxExpand = 90000;

        /// <summary>State read: cells the last RouteCells expanded, and whether it ran out of budget.</summary>
        public static int LastRouteExpanded;
        public static bool LastRouteCapped;

        /// <summary>The hose's own route search (round 5). Round 4 used the cord planner's A* with a flat 20000-expansion cap,
        /// which is no bound on length at all: on a big open map a hard route spent it and read as "no route". This is the
        /// same A* (8-way, no corner cutting, ExtraCost for water and trees) with the search bounded by LENGTH: a node
        /// whose path length plus straight-line remainder exceeds lengthBound is never opened, so every route within the
        /// bound is found and the search never leaves the (2 x bound + 1)^2 square round the reel. lengthBound &lt;= 0 =
        /// unbounded, capped at RouteMaxExpand.</summary>
        public static List<Cell> RouteCells(CordWorld w, Cell start, Cell goal, double lengthBound, bool costs = true)
        {
            LastRouteExpanded = 0;
            LastRouteCapped = false;
            if (start == goal) return new List<Cell> { start };
            bool Ok(Cell c) => c == start || c == goal || w.IsWalkable(c);
            double H(Cell c)
            {
                int dx = Math.Abs(c.X - goal.X), dz = Math.Abs(c.Z - goal.Z);
                return Math.Max(dx, dz) + 0.414 * Math.Min(dx, dz);
            }
            int cap = lengthBound > 0 ? (int)Math.Min(RouteMaxExpand, Math.Pow(2 * Math.Ceiling(lengthBound) + 3, 2)) : RouteMaxExpand;
            var g = new Dictionary<Cell, double> { [start] = 0 };
            var len = new Dictionary<Cell, double> { [start] = 0 };
            var came = new Dictionary<Cell, Cell>();
            var open = new SortedSet<(double f, double g, Cell c)>(Comparer<(double f, double g, Cell c)>.Create((x, y) =>
            {
                int k = x.f.CompareTo(y.f);
                if (k != 0) return k;
                k = x.g.CompareTo(y.g);
                return k != 0 ? k : x.c.CompareTo(y.c);
            }));
            open.Add((H(start), 0, start));
            while (open.Count > 0)
            {
                var top = open.Min;
                open.Remove(top);
                Cell c = top.c;
                if (c == goal)
                {
                    var path = new List<Cell> { c };
                    while (came.TryGetValue(c, out Cell p)) { c = p; path.Add(c); }
                    path.Reverse();
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++LastRouteExpanded > cap) { LastRouteCapped = true; return null; }
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!w.InBounds(q) || !Ok(q)) continue;
                    if (d.X != 0 && d.Z != 0 && !(Ok(new Cell(c.X + d.X, c.Z)) && Ok(new Cell(c.X, c.Z + d.Z)))) continue;
                    double step = d.X != 0 && d.Z != 0 ? 1.414 : 1.0;
                    double nl = len[c] + step;
                    if (lengthBound > 0 && nl + H(q) > lengthBound) continue;
                    double ng = top.g + step + (costs ? w.ExtraCost(q) : 0);
                    if (!g.TryGetValue(q, out double old) || ng < old - 1e-12)
                    {
                        if (g.TryGetValue(q, out double o2)) open.Remove((o2 + H(q), o2, q));
                        g[q] = ng;
                        len[q] = nl;
                        came[q] = c;
                        open.Add((ng + H(q), ng, q));
                    }
                }
            }
            return null;
        }

        /// <summary>True when the straight segment a-b stays out of walls (ClipTolerance) and never slips through a
        /// pinched diagonal (two wall cells meeting corner to corner).</summary>
        public static bool SegmentClear(CordWorld w, V2 a, V2 b) => Clear(w, new List<V2> { a, b }, 0);

        /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1 (owner, by card 2026-10-04: "reroute within its length; if none exists,
        /// retract to the reel with a visible alert. Never a ghost hose; also enforce length on re-plan."). Run when an
        /// obstacle changes a laid hose's corridor, or its lay failed: null = keep it laid (re-route), else the reason it
        /// must be reeled in. The SAME test as installing, so a re-plan can never keep a hose install would refuse.
        /// layFailed: the planner could not lay a hose the route check passed -- also retracted, never left invisible.</summary>
        public static string CheckReplan(CordWorld w, HoseReelRect reel, Cell target, double maxLength, bool layFailed, string layReason)
        {
            string why = CheckInstall(w, reel, target, maxLength);
            if (why != null) return why;
            return layFailed ? (string.IsNullOrEmpty(layReason) ? "could not be laid" : layReason) : null;
        }

        // ---------------------------------------------------------------- flow signal rules
        /// <summary>The FlowWorks pump rule (design 3.3): the pump's last pulse moved liquid and that pulse is
        /// current (no older than 1.5 pulse intervals).</summary>
        public static bool PumpFlowing(double lastMovedUnits, int lastMovedTick, int now, int pulseTicks) =>
            lastMovedUnits > 0 && now - lastMovedTick <= pulseTicks + pulseTicks / 2;

        // ---------------------------------------------------------------- fittings never on top of another hose
        /// <summary>One laid hose for <see cref="Layer"/>: its reel's thing id (the B18 crossing order) and its lay.</summary>
        public sealed class LayeredHose
        {
            public int Id;
            public HoseLay Lay;
        }

        /// <summary>Draw order (rank 0 = lowest band) and the joiners each hose draws, by reel id.</summary>
        public sealed class Layering
        {
            public Dictionary<int, int> Rank = new Dictionary<int, int>();
            public Dictionary<int, List<int>> Joints = new Dictionary<int, List<int>>();
        }

        /// <summary>
        /// MESSYCONDUIT_CABLE_PILE_LOOK_1 rule 3 (owner 2026-10-04: "the brass fixtures at the ends don't just lay on top of
        /// other hose lenghts. That looks ridiculous. They CAN look like sealed joiners from one cable length to another").
        /// B18 ranks crossing hoses by reel age; on top of that, a hose whose END fitting rests on another hose's body is
        /// ranked BENEATH that hose (the other hose passes over the fitting), and a joiner that would still sit over a hose
        /// ranked below is not drawn (a joiner is optional; its straightened run stays). Ties and unconstrained hoses keep
        /// reel-id order; a cycle (two hoses each ending on the other) is broken at the lowest id, so the order is always
        /// total.
        /// </summary>
        public static Layering Layer(IList<LayeredHose> hoses, double visible)
        {
            var res = new Layering();
            int n = hoses.Count;
            // below[i] = the hoses i must be drawn beneath (i's end fitting lies on their body)
            var mustPrecede = new List<int>[n];
            var indeg = new int[n];
            for (int i = 0; i < n; i++) mustPrecede[i] = new List<int>();
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                {
                    if (i == j) continue;
                    if (EndFittingOn(hoses[i].Lay, true, hoses[j].Lay, visible) || EndFittingOn(hoses[i].Lay, false, hoses[j].Lay, visible))
                    { mustPrecede[i].Add(j); indeg[j]++; }
                }
            var placed = new bool[n];
            for (int r = 0; r < n; r++)
            {
                int pick = -1;
                for (int i = 0; i < n; i++)
                    if (!placed[i] && indeg[i] == 0 && (pick < 0 || hoses[i].Id < hoses[pick].Id)) pick = i;
                if (pick < 0)   // cycle: the lowest id goes next, its unmet constraints dropped
                    for (int i = 0; i < n; i++)
                        if (!placed[i] && (pick < 0 || hoses[i].Id < hoses[pick].Id)) pick = i;
                placed[pick] = true;
                res.Rank[hoses[pick].Id] = r;
                foreach (int j in mustPrecede[pick]) indeg[j]--;
            }
            for (int i = 0; i < n; i++)
            {
                HoseLay lay = hoses[i].Lay;
                var keep = new List<int>();
                foreach (int jt in lay.Joints)
                {
                    bool over = false;
                    for (int j = 0; j < n && !over; j++)
                        if (j != i && res.Rank[hoses[j].Id] < res.Rank[hoses[i].Id] && JointFittingOn(lay, jt, hoses[j].Lay, visible)) over = true;
                    if (!over) keep.Add(jt);
                }
                res.Joints[hoses[i].Id] = keep;
            }
            return res;
        }

        /// <summary>Every fitting (both ends, every drawn joiner) that draws over another hose's body under the given ranks
        /// and joiner lists (null = each lay's own Joints). Empty = rule 3 holds. The offline bar and the live probe share it.</summary>
        public static List<string> FittingsOnTop(IList<LayeredHose> hoses, IDictionary<int, int> rank, IDictionary<int, List<int>> joints, double visible)
        {
            var o = new List<string>();
            foreach (LayeredHose h in hoses)
                foreach (LayeredHose g in hoses)
                {
                    if (h == g || rank[h.Id] <= rank[g.Id]) continue;
                    if (EndFittingOn(h.Lay, true, g.Lay, visible)) o.Add($"hose {h.Id}: reel-end fitting on hose {g.Id}");
                    if (EndFittingOn(h.Lay, false, g.Lay, visible)) o.Add($"hose {h.Id}: free-end fitting on hose {g.Id}");
                    foreach (int jt in joints != null && joints.TryGetValue(h.Id, out List<int> js) ? js : h.Lay.Joints)
                        if (JointFittingOn(h.Lay, jt, g.Lay, visible)) o.Add($"hose {h.Id}: joiner at sample {jt} on hose {g.Id}");
                }
            return o;
        }

        /// <summary>A fitting's footprint: the lay's own centreline within [lo, hi] of arc, as wide as the cloth wrap.</summary>
        private static bool FootprintOn(HoseLay a, double lo, double hi, HoseLay b, double visible)
        {
            double reach = 0.5 * WrapWidth(visible) + 0.5 * visible, skip = JoinerHalf(visible);
            foreach (bool plump in new[] { false, true })
            {
                List<V2> P = plump ? a.Plump : a.Flat, Q = plump ? b.Plump : b.Flat;
                if (P == null || Q == null || P.Count < 2 || Q.Count < 2) continue;
                double[] sp = Geo.CumLen(P), sq = Geo.CumLen(Q);
                double Lq = sq[sq.Length - 1];
                for (int k = 0; k < P.Count; k++)
                {
                    if (sp[k] < lo || sp[k] > hi) continue;
                    // the other hose's own fitting runs are not its body: two fittings meeting read as a sealed joiner
                    for (int m = 0; m + 1 < Q.Count; m++)
                    {
                        if (sq[m + 1] < skip || sq[m] > Lq - skip) continue;
                        if (SegDist(P[k], Q[m], Q[m + 1]) < reach) return true;
                    }
                }
            }
            return false;
        }

        private static bool EndFittingOn(HoseLay a, bool start, HoseLay b, double visible)
        {
            List<V2> P = a.Flat;
            if (P == null || P.Count < 2) return false;
            double L = Geo.Length(P), h = JoinerHalf(visible);
            return start ? FootprintOn(a, 0, h, b, visible) : FootprintOn(a, L - h, L, b, visible);
        }

        private static bool JointFittingOn(HoseLay a, int jt, HoseLay b, double visible)
        {
            List<V2> P = a.Flat;
            if (P == null || jt < 0 || jt >= P.Count) return false;
            double s = Geo.CumLen(P)[jt], h = JoinerHalf(visible);
            return FootprintOn(a, s - h, s + h, b, visible);
        }

        private static double SegDist(V2 p, V2 a, V2 b)
        {
            V2 ab = b - a;
            double len2 = ab.X * ab.X + ab.Z * ab.Z;
            double t = len2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((p.X - a.X) * ab.X + (p.Z - a.Z) * ab.Z) / len2));
            return V2.Dist(a + ab * t, p);
        }
    }

    /// <summary>Per-fluid tint (design 3.4): FlowWorks' LiquidDef.color is white for every row today, so this
    /// table keyed by defName stands in. Unknown fluids read as water.</summary>
    public static class HoseTint
    {
        private static readonly Dictionary<string, int[]> table = new Dictionary<string, int[]>
        {
            { "water", new[] { 0x3E, 0x5C, 0x6B } }, { "freshwater", new[] { 0x3E, 0x5C, 0x6B } },
            { "saltwater", new[] { 0x46, 0x60, 0x6A } }, { "brine", new[] { 0x5E, 0x6A, 0x60 } },
            { "tar", new[] { 0x1A, 0x14, 0x10 } }, { "chemfuel", new[] { 0x7A, 0x5A, 0x1E } },
            { "propane", new[] { 0x8C, 0x8C, 0x70 } }, { "slimered", new[] { 0x6E, 0x34, 0x30 } },
            { "slimegreen", new[] { 0x44, 0x62, 0x3A } }, { "slimewhite", new[] { 0x9A, 0x98, 0x90 } },
            { "slimeyellow", new[] { 0x8A, 0x7C, 0x3A } }, { "toxicwater", new[] { 0x4E, 0x5E, 0x3A } },
        };

        public static int[] Rgb(string defName)
        {
            string k = (defName ?? "").ToLowerInvariant().Replace("rm_fluid_", "").Replace("rm_liquid_", "").Replace("_", "");
            return table.TryGetValue(k, out int[] v) ? v : table["water"];
        }

        public static IEnumerable<string> Known => table.Keys;
    }
    // ==================================================================== reel ports (owner review round 2, 2026-10-04)
    /// <summary>What a reel's inlet may couple to. Pipe = a static pipe cell (the universal pipe carries any liquid);
    /// Tank = any liquid store (the universal tank, RM_LiquidTank, a VE PipeSystem storage); Other = any other
    /// pipe-friendly building that opted in. Rank order is the preference order.</summary>
    public enum HosePortKind { Pipe, Tank, Other, None }

    /// <summary>The reel's footprint (round 3, owner 2026-10-04: "the reel should be 2x2, not 1x1, as the shown hose is
    /// quite large"). The hose leaves the reel at its CENTRE (a cell corner for 2x2) from under the sprite.</summary>
    public struct HoseReelRect
    {
        public int X0, Z0, W, H;
        public HoseReelRect(int x0, int z0, int w, int h) { X0 = x0; Z0 = z0; W = Math.Max(1, w); H = Math.Max(1, h); }
        public V2 Centre => new V2(X0 + W / 2.0, Z0 + H / 2.0);

        /// <summary>Where the hose leaves the reel. Owner 2026-10-05 (reversing round 5's hide-under-the-drum): the 2x2 reel's hose
        /// starts at its brass OUTLET, the nozzle on the left of the Reel_Deployed art (tip u 7-11/256, centre v 133-141/256 across the
        /// four looks; drawSize 2.8), and a coupling sits on that nozzle. The routing start is the nozzle's height on the footprint's
        /// west edge (inside the west cell, so a lay still starts in a reel cell); <see cref="NozzleTip"/> is where the coupling's face
        /// meets the nozzle. A 1x1 reel keeps its centre.</summary>
        public V2 Mouth => W == 2 && H == 2 ? Centre + new V2(MouthDX, MouthDZ) : Centre;
        public const double ReelDrawSize = 2.8, MouthDX = -0.98, MouthDZ = (0.5 - 135.0 / 256) * ReelDrawSize;
        /// <summary>The nozzle's tip, where the end coupling's face is drawn (2x2 reel only; the art's tip at u 9/256).</summary>
        public V2 NozzleTip => Centre + new V2((9.0 / 256 - 0.5) * ReelDrawSize, MouthDZ);
        /// <summary>The drum's half-height below its axis (art: underside v 165/256), cells.</summary>
        public const double DrumBelowAxis = (165.0 - 124.0) / 256 * ReelDrawSize;
        /// <summary>True when the reel's art carries a brass outlet nozzle the hose couples to (the 2x2 reel).</summary>
        public bool HasNozzle => W == 2 && H == 2;
        /// <summary>2026-10-05: the hose leaves a nozzled reel dead straight out of the outlet for this many cells from
        /// <see cref="Mouth"/> (0.32 to the tip + the end coupling and its wrap, ~1.1, + a margin), so it visibly runs through
        /// the coupling instead of turning away under the pump body.</summary>
        public const double OutletStraight = 1.6;
        /// <summary>How far the end coupling's threaded stub slides into the outlet nozzle (drawn under the reel sprite), so the
        /// two meet with no gap.</summary>
        public const double NozzleSeat = 0.07;
        /// <summary>The direction the hose leaves a nozzled reel (the outlet faces west on every look's art), or null.</summary>
        public V2? Outward => HasNozzle ? new V2(-1, 0) : (V2?)null;
        public bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
        public bool Overlaps(HosePortCandidate o) => o.X0 < X0 + W && X0 < o.X0 + o.W && o.Z0 < Z0 + H && Z0 < o.Z0 + o.H;

        /// <summary>The reel cells on one side (side = unit step outward), ascending along it.</summary>
        public List<Cell> EdgeCells(Cell side)
        {
            var l = new List<Cell>();
            if (side.X != 0) { int x = side.X > 0 ? X0 + W - 1 : X0; for (int z = Z0; z < Z0 + H; z++) l.Add(new Cell(x, z)); }
            else { int z = side.Z > 0 ? Z0 + H - 1 : Z0; for (int x = X0; x < X0 + W; x++) l.Add(new Cell(x, z)); }
            return l;
        }

        /// <summary>The reel cell nearest the target (the planner's start cell); ties to the lowest x, then z.</summary>
        public Cell StartCellToward(Cell target)
        {
            Cell best = new Cell(X0, Z0);
            double bd = double.MaxValue;
            for (int x = X0; x < X0 + W; x++)
                for (int z = Z0; z < Z0 + H; z++)
                {
                    var c = new Cell(x, z);
                    double d = V2.Dist(c.Centre, target.Centre);
                    if (d < bd - 1e-9) { bd = d; best = c; }
                }
            return best;
        }

        /// <summary>The cells just outside the footprint that share an edge with it (the only cells a port may occupy).</summary>
        public List<Cell> Perimeter()
        {
            var l = new List<Cell>();
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in EdgeCells(s)) l.Add(e + s);
            return l;
        }
    }

    public struct HosePortCandidate
    {
        public int X0, Z0, W, H;
        public HosePortKind Kind;
        public HosePortCandidate(int x0, int z0, int w, int h, HosePortKind kind) { X0 = x0; Z0 = z0; W = w; H = h; Kind = kind; }
        public bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
    }

    /// <summary>The Verse-free connection rule (SelfTest: HoseSelfTest.Ports). A reel couples to a neighbour only across
    /// a shared cell EDGE (a corner touch would draw a feed through empty air); among those it prefers a pipe, then a
    /// tank, then anything else, and breaks ties by side in the fixed order east, north, west, south, so the answer
    /// never depends on thing-list order.</summary>
    public static class HosePortRule
    {
        public static readonly Cell[] SideOrder = { new Cell(1, 0), new Cell(0, 1), new Cell(-1, 0), new Cell(0, -1) };

        /// <summary>Index of the chosen candidate, or -1. side = the unit step from the reel to the contact cell.</summary>
        public static int Pick(Cell reel, IList<HosePortCandidate> cands, out Cell side) =>
            Pick(new HoseReelRect(reel.X, reel.Z, 1, 1), cands, out side, out _);

        /// <summary>Any reel footprint (round 3: 2x2). contact = the neighbour cell (outside the reel) across the shared
        /// edge; the reel cell it touches is contact - side. Ties: kind, then side (E, N, W, S), then the lowest cell along
        /// that side -- never candidate order.</summary>
        public static int Pick(HoseReelRect reel, IList<HosePortCandidate> cands, out Cell side, out Cell contact)
        {
            side = new Cell(0, 0);
            contact = new Cell(0, 0);
            int best = -1, bestRank = int.MaxValue;
            for (int i = 0; i < cands.Count; i++)
            {
                HosePortCandidate c = cands[i];
                if (c.Kind == HosePortKind.None || reel.Overlaps(c)) continue;
                for (int s = 0; s < SideOrder.Length; s++)
                {
                    List<Cell> edge = reel.EdgeCells(SideOrder[s]);
                    for (int k = 0; k < edge.Count; k++)
                    {
                        Cell n = edge[k] + SideOrder[s];
                        if (!c.Contains(n)) continue;
                        int rank = ((int)c.Kind * 8 + s) * 64 + k;
                        if (rank < bestRank) { bestRank = rank; best = i; side = SideOrder[s]; contact = n; }
                    }
                }
            }
            return best;
        }

        /// <summary>The feed hose from the reel's inlet to the port: it starts 0.25 cell out from the reel centre (under
        /// the reel sprite) and ends at the contact cell's centre, i.e. at the pipe's own centreline, or under the tank's
        /// sprite (drawn below buildings, so it disappears beneath it instead of stopping short at its outline).
        /// coupling = where the brass coupling sits: on the shared edge.</summary>
        public static void Feed(Cell reel, Cell side, out V2 from, out V2 to, out V2 coupling)
        {
            V2 d = new V2(side.X, side.Z), c = reel.Centre;
            from = c + d * 0.25;
            to = (reel + side).Centre;
            coupling = c + d * 0.5;
        }
    }
}
