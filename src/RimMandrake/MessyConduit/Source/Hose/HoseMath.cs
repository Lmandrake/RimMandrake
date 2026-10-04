// Messy Conduit L6 flexible hoses, the Verse-free half (design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md
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
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.Hose
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
    }

    public sealed class HoseLay
    {
        public bool Ok;
        public string Reason;
        /// <summary>The fell-back flag: the slack could not be laid clear of obstacles; Flat is the planned centreline.</summary>
        public bool FellBack;
        /// <summary>Equal-arc samples of the collapsed pose, the charged pose, and the planned centreline (same count).</summary>
        public List<V2> Flat = new List<V2>(), Plump = new List<V2>(), Centre = new List<V2>();
        /// <summary>Coupling positions: the reel end, every joiner, the free end (in that order).</summary>
        public List<V2> Couplings = new List<V2>();
        /// <summary>Sample indices of the joiners between two lengths: only at real bends of the planned route, never on a
        /// straight run (owner review 2026-10-04 B17).</summary>
        public List<int> Joints = new List<int>();
        public double PathLen, FlatLen, PlumpLen, MinBendFlat, MinBendPlump;
    }

    public static class HoseMath
    {
        // ---------------------------------------------------------------- width rules (measured from the art)
        /// <summary>The wire strand (SectionLayer_RM_MessyCords.StrandWidth 0.11) times Strand_Jawa.png's opaque
        /// band (25 of 32 px rows).</summary>
        public const double WireVisibleWidth = 0.11 * 25.0 / 32.0;
        /// <summary>Opaque band of the staged strips Textures/.../Hose/Strand_Flat.png (rows 2-60 of 64) and
        /// Strand_Plump.png (rows 1-62), measured 2026-10-02 (lane C cropped the v2 art to fill the strip).</summary>
        public const double FlatBand = 59.0 / 64.0, PlumpBand = 62.0 / 64.0;
        /// <summary>Visible width collapsed (4.4 wires) and the extra a full plump adds at plump amount 1 (to 5.4 wires).</summary>
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
        public static HoseLay Lay(CordWorld w, V2 a, V2 b, HoseShapeParams p, ulong seed)
        {
            var lay = new HoseLay();
            CordPlan plan = CordPlanner.Plan(w, a, b, new List<KeyValuePair<V2, WaypointKind>>());
            if (!plan.Ok) { lay.Reason = "no route"; return lay; }
            List<V2> C = CordPlanner.RoundCorners(plan.Points, Math.Max(0.45, p.MinBendRadius));
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
            lay.FlatLen = Geo.Length(lay.Flat);
            lay.PlumpLen = Geo.Length(lay.Plump);
            lay.MinBendFlat = MinBendRadius(lay.Flat, EndSkip);
            lay.MinBendPlump = MinBendRadius(lay.Plump, EndSkip);
            lay.Joints = Joints(lay.Centre, p.CouplingSpacing);
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

        private static bool Clear(CordWorld w, List<V2> pts)
        {
            for (int i = 1; i < pts.Count - 1; i++) if (!w.IsWalkable(pts[i].Floor)) return false;
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

        private static void StiffenPass(CordWorld w, List<V2> X, double minR, int iters)
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
        public static List<int> Joints(IList<V2> C, double minSpacing)
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
        public const double WrapK = 1.4, WrapLength = 0.6;
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
        public static string CheckInstall(CordWorld w, Cell reel, Cell target, double maxLength)
        {
            if (!w.InBounds(target)) return "out of bounds";
            if (target == reel) return "same cell";
            if (V2.Dist(reel.Centre, target.Centre) > maxLength) return "too far";
            if (!w.IsWalkable(target)) return "target blocked";
            List<Cell> path = CordPlanner.AStar(w, reel, target, 20000);
            if (path == null) return "no route";
            double len = 0;
            for (int i = 1; i < path.Count; i++) len += V2.Dist(path[i - 1].Centre, path[i].Centre);
            if (len * 1.08 > maxLength) return "route too long";
            return null;
        }

        // ---------------------------------------------------------------- flow signal rules
        /// <summary>The FlowWorks pump rule (design 3.3): the pump's last pulse moved liquid and that pulse is
        /// current (no older than 1.5 pulse intervals).</summary>
        public static bool PumpFlowing(double lastMovedUnits, int lastMovedTick, int now, int pulseTicks) =>
            lastMovedUnits > 0 && now - lastMovedTick <= pulseTicks + pulseTicks / 2;
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
}
