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
                if (!Clear(w, F)) F = Geo.Resample(plan.Points, Sample);
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
            lay.FlatLen = Geo.Length(lay.Flat);
            lay.PlumpLen = Geo.Length(lay.Plump);
            double half = JoinerHalf(VisibleWidth(1, p.PlumpAmount));
            lay.Joints = new List<int>();
            foreach (int j in Joints(lay.Centre, p.CouplingSpacing, half, lay.Flat, lay.Plump))
            {
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
        public static List<int> Joints(IList<V2> C, double minSpacing) => Joints(C, minSpacing, 0);

        /// <summary>Half the length of a joiner (two couplings face to face plus their cloth wraps), cells, on a hose of
        /// <paramref name="visible"/> width: brass face to wrap end = 0.49 x fitting size + 0.55 (DrawEnds' Fitting).</summary>
        public static double JoinerHalf(double visible) => (JoinerFace + 0.03) * FittingSize(visible, PieceBand, CouplingMax) + WrapLength - 0.05;

        /// <summary>Art geometry of the coupling (measured 2026-10-02/04; RM_MapComponent_Hoses draws with these): the
        /// hose band where the hose enters it, its widest band (canvas fractions) and its brass face (canvas units).</summary>
        public const double PieceBand = 0.25, CouplingMax = 0.508, JoinerFace = 0.46;

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
            double len = RouteLength(w, reel, target, maxLength);
            if (len < 0) len = RouteLength(w, reel, target);
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
        public static double RouteLength(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1)
        {
            List<V2> p = RoutePulled(w, reel, target, maxLength);
            return p == null ? -1 : Geo.Length(p);
        }

        public static List<V2> RoutePulled(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1)
        {
            Cell s = reel.StartCellToward(target);
            List<Cell> path = RouteCells(w, s, target, maxLength > 0 ? SearchLengthBound(maxLength) : -1);
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
        public static List<Cell> RouteCells(CordWorld w, Cell start, Cell goal, double lengthBound)
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
                    double ng = top.g + step + w.ExtraCost(q);
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

        /// <summary>Where the hose leaves the reel. Round 5 (owner, station 11: "the hoses should aim to the mid-point of the
        /// reel wheel, so you can't see the end of the hose peeking through below the reel"): on the 2x2 reel the hose
        /// ends at the DRUM's axis, read off all four looks' Reel_Deployed art at drawSize 2.8 (axle bolt v 124/256, drum
        /// between the flanges u 118-245, centre u 180/256), so the hose disappears under the opaque drum; its end and
        /// its reel-end fitting are never drawn (RM_MapComponent_Hoses.DrawEnds). Round 4 had it just above the drum's
        /// underside (u 168, v 165), where its end showed through the gap above the base rail. A 1x1 reel keeps its centre.</summary>
        public V2 Mouth => W == 2 && H == 2 ? Centre + new V2(MouthDX, MouthDZ) : Centre;
        public const double ReelDrawSize = 2.8, MouthDX = (180.0 / 256 - 0.5) * ReelDrawSize, MouthDZ = (0.5 - 124.0 / 256) * ReelDrawSize;
        /// <summary>The drum's half-height below its axis (art: underside v 165/256), cells: the hose end must sit above it.</summary>
        public const double DrumBelowAxis = (165.0 - 124.0) / 256 * ReelDrawSize;
        /// <summary>True when the reel's own art hides the hose end (the 2x2 reel's drum): no reel-end fitting is drawn.</summary>
        public bool HidesHoseEnd => W == 2 && H == 2;
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
