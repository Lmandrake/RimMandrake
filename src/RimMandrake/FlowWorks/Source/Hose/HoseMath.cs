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
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    public enum HoseVis { Flat, Filling, Plump, Draining }

    /// <summary>State-machine timing, game ticks. Defaults = shipped (RM_HoseSettings).</summary>
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

    /// <summary>Shape inputs. Defaults = shipped (RM_HoseSettings).</summary>
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
        /// <summary>Owner by card 2026-10-24 "Shorten the lead-out": the straight lead-out out of the nozzle when the lead search
        /// shortened it (HoseMath.LayAlong); 0 = the full LeadOutStraight.</summary>
        public double LeadOut;

        /// <summary>This shape with the straight lead-out set to <paramref name="lead"/>.</summary>
        public HoseShapeParams WithLeadOut(double lead) => new HoseShapeParams { MinBendRadius = MinBendRadius, Slack = Slack, PlumpAmount = PlumpAmount, CouplingSpacing = CouplingSpacing, MaxLength = MaxLength, LeadOut = lead };
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
        internal List<V2> Flat = new List<V2>(), Plump = new List<V2>(), Centre = new List<V2>();
        /// <summary>Coupling positions: the reel end, every joiner, the free end (in that order).</summary>
        internal List<V2> Couplings = new List<V2>();
        /// <summary>Sample indices of the joiners between two lengths: only at real bends of the planned route, never on a
        /// straight run (owner review 2026-10-04 B17).</summary>
        public List<int> Joints = new List<int>();
        public double PathLen, FlatLen, PlumpLen, MinBendFlat, MinBendPlump;
        /// <summary>Owner decision by question card 2026-10-06 (straight lead-out): arc length of the flat hose's lead-out (the
        /// straight run out of the nozzle plus the bend that joins it to the laid hose); 0 = no outlet.</summary>
        public double LeadOutLen;
        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: the poses are clothoid chains (G2, |kappa| &lt;= 1/R, exact length); when
        /// false, G2Why says why the shaped poses were kept.</summary>
        public bool G2;
        public string G2Why;
        /// <summary>The curvature limit the lay was shaped under (1/R) and the straight runs at its start (the lead-out) and end.</summary>
        public double Kmax = 1 / 1.2, Lead0, Lead1;
        /// <summary>The lead-out was shortened below the full one (owner by card 2026-10-24 "Shorten the lead-out"): Lead0 is it.</summary>
        public bool LeadShortened;
        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 3: why a tank-port end was laid to its cell centre (the draw then
        /// bends it onto the port) instead of onto the port's axis; null = laid onto the port, or no port.</summary>
        public string PortWhy;
        /// <summary>Step 4: the shaped route was too tight for a G2 curve and the hose was re-laid along a wider guide.</summary>
        public bool Rerouted;
    }

    public static class HoseMath
    {
        /// <summary>FLOWWORKS_HOSE_FIX_NAN_WINDING_INSTANT: a setting clamped to [lo, hi], with a non-finite value (a hand-edited
        /// or corrupt "NaN" in the settings file, which float.Parse accepts) read as <paramref name="fallback"/>. Mathf.Clamp
        /// passes NaN through, and a NaN winding speed finished every retraction on its first tick.</summary>
        public static float FiniteClamp(float v, float lo, float hi, float fallback)
        {
            if (float.IsNaN(v)) return fallback;
            return v < lo ? lo : v > hi ? hi : v;
        }

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
        /// <summary>Visible width collapsed and the extra a full plump adds at plump amount 1: 0.18 cell flat, 0.23 plump.
        /// Owner 2026-10-22 00:00, after seeing the 0.09 hose live: "Hoses need to be twice as thick, too thin to see now."
        /// (HOSE_GIRTH_TUNE_MUCH_THINNER; the 2026-10-21 thinning to 0.09 overshot.)</summary>
        public const double FlatVisible = 0.18, PlumpExtra = 0.05;

        /// <summary>HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16: "shrink the tube diameter a bit to make it less
        /// fire-hydrant-thick"): every visible width (and so every fitting, wrap and clearance sized from it) times this. Set from
        /// RM_HoseSettings.thickness; 1 = the shipped width (0.18 cell flat, 2026-10-22).</summary>
        public static double WidthScale = 1.0;

        public static double VisibleWidth(double eased, double plumpAmount) => WidthScale * (FlatVisible + PlumpExtra * Math.Max(0, plumpAmount) * Geo.Clamp(eased, 0, 1));
        public static double MeshWidthFlat(double visible) => visible / FlatBand;
        public static double MeshWidthPlump(double visible) => visible / PlumpBand;

        /// <summary>The contact shadow under a hose (shared Strand_Shadow, drawn in every look): its opacity and its width as a
        /// multiple of the visible width, from empty (eased 0, flat) to full (1, plump). Owner card 2026-10-22
        /// (HOSE_GIRTH_TUNE_MUCH_THINNER, "Darker shadow first"): the empty Scrapper hose vanished on desert soil, so the EMPTY
        /// shadow went from 0.55 opacity at 1.15x to 0.80 at 1.35x; the full hose's (0.85, 1.5x) is unchanged.</summary>
        public const double ShadowAlphaEmpty = 0.80, ShadowAlphaFull = 0.85, ShadowWidthEmpty = 1.35, ShadowWidthFull = 1.5;
        public static double ShadowAlpha(double eased) => ShadowAlphaEmpty + (ShadowAlphaFull - ShadowAlphaEmpty) * Geo.Clamp(eased, 0, 1);
        public static double ShadowWidth(double eased) => ShadowWidthEmpty + (ShadowWidthFull - ShadowWidthEmpty) * Geo.Clamp(eased, 0, 1);

        /// <summary>HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT: a hose that meets its port from the side is not re-aimed
        /// (<see cref="EndOnPort"/> would loop it back behind the end), so its end stays on the end cell's centre and the coupling
        /// (port point = end + axis x 0.5) sat at the old edge midpoint, beside a port moved along its edge
        /// (<see cref="TankPortGeometry.MovedAlong"/>, RM_LiquidTank's measured flange). This slides the last <paramref name="span"/>
        /// cells of arc sideways by a smoothstep ramp (0 at L - span, 1 at the end) so the end lands exactly half a cell short of
        /// <paramref name="port"/> along <paramref name="axis"/>; the shift's slope stays under 1, so the tail never folds back.
        /// A new list; the input is untouched.</summary>
        internal static List<V2> SlideEndOnto(List<V2> pts, V2 port, V2 axis, double span = 0.75)
        {
            if (pts == null || pts.Count < 2) return pts;
            int n = pts.Count;
            V2 delta = port - axis * 0.5 - pts[n - 1];
            var res = new List<V2>(pts);
            if (delta.Len < 1e-9) return res;
            double[] s = Geo.CumLen(pts);
            double L = s[n - 1];
            for (int i = 0; i < n; i++)
            {
                double t = span <= 0 ? (i == n - 1 ? 1 : 0) : Geo.Clamp((s[i] - (L - span)) / span, 0, 1);
                if (t <= 0) continue;
                res[i] = pts[i] + delta * Ease(t);
            }
            return res;
        }

        /// <summary>HOSE_ENDS_FIX_MISSES_THE_PORTS: re-aim a drawn hose's last <paramref name="run"/> cells so it ends at
        /// <paramref name="end"/> arriving along <paramref name="axis"/> (unit, pointing into the port): the polyline is cut at arc
        /// length L - run and finished with a cubic Hermite from there (the hose's own tangent) to the end (tangent = axis), so the
        /// last stretch runs straight into the coupling instead of meeting it from the side. Unchanged when the hose is shorter
        /// than the run or already ends there.</summary>
        internal static List<V2> EndOnPort(List<V2> pts, V2 end, V2 axis, double run = 0.9, int samples = 8)
        {
            if (pts == null || pts.Count < 2) return pts;
            if (V2.Dist(pts[pts.Count - 1], end) < 1e-6) return pts;
            double L = Geo.Length(pts);
            if (L <= run + 1e-6) return pts;
            var outp = new List<V2>(pts.Count + samples);
            double acc = 0, cut = L - run;
            V2 a = pts[0], ta = new V2(1, 0);
            outp.Add(pts[0]);
            for (int i = 1; i < pts.Count; i++)
            {
                double seg = V2.Dist(pts[i - 1], pts[i]);
                if (acc + seg >= cut)
                {
                    double t = seg < 1e-12 ? 0 : (cut - acc) / seg;
                    a = pts[i - 1] + (pts[i] - pts[i - 1]) * t;
                    ta = (pts[i] - pts[i - 1]).Norm();
                    if (t > 1e-9) outp.Add(a);
                    break;
                }
                acc += seg;
                outp.Add(pts[i]);
            }
            double k = V2.Dist(a, end);
            V2 m0 = ta * k, m1 = axis * k;
            for (int s = 1; s <= samples; s++)
            {
                double u = s / (double)samples, u2 = u * u, u3 = u2 * u;
                outp.Add(a * (2 * u3 - 3 * u2 + 1) + m0 * (u3 - 2 * u2 + u) + end * (-2 * u3 + 3 * u2) + m1 * (u3 - u2));
            }
            return outp;
        }

        /// <summary>HOSE_LEADIN_FIX_STUB_IN_THE_CANAL: a hose whose last stretch turns more than this off the port's axis met the
        /// port from the SIDE (its straight lead-out cell was water, a wall, a building: the route came round).</summary>
        public const double SideEntryCos = 0.82;   // ~35 degrees

        /// <summary>Where the brass coupling at a port end sits and how long its cloth wrap runs (DrawEnds draws exactly this).
        /// <paramref name="face0"/> = the port point the coupling's face meets, <paramref name="axis"/> = unit, into the port,
        /// <paramref name="size"/> = the drawn coupling size (FittingSize x widen), <paramref name="vis"/> = the hose's visible width.
        /// Straight arrival (the usual): the coupling's face at face0, the full <see cref="WrapLength"/> wrap back along the hose.
        /// Side arrival (BENCH live round 2, save d map C: Kludged station south port 150,189, canal at 150,188, the hose came in
        /// from the east): the hose lies ACROSS the axis there, so a full straight lead-in -- the coupling's back half and a 0.6-cell
        /// wrap -- stuck out past the hose towards the canal. The fitting becomes an elbow: nothing of it reaches farther back along
        /// the axis than the hose's own far edge (the coupling slides into the building by the excess, where the building's body
        /// covers it, and the wrap is cut to cover only the join). Returns true for a side arrival.</summary>
        internal static bool PortFitting(IList<V2> pts, V2 face0, V2 axis, double size, double vis, out V2 face, out double wrapLen) =>
            PortFitting(pts, face0, axis, ref size, vis, out face, out wrapLen);

        /// <summary>Most a side-arrival coupling slides into the building (cells); past that the reducer collar is drawn smaller
        /// instead (<paramref name="size"/> comes back reduced), so its face never sits deep inside the footprint.</summary>
        public const double PortSlideMax = 0.1;

        internal static bool PortFitting(IList<V2> pts, V2 face0, V2 axis, ref double size, double vis, out V2 face, out double wrapLen)
        {
            face = face0;
            wrapLen = WrapLength;
            if (!SideArrival(pts, axis)) return false;
            int n = pts.Count;
            // along the axis, measured from face0 (negative = away from the port): the hose's far edge and the fitting's parts
            double hoseBack = Dot(pts[n - 1] - face0, axis) - vis / 2;
            if ((JoinerFace + 0.5) * size > PortSlideMax - hoseBack) size = Math.Max(0.05, (PortSlideMax - hoseBack) / (JoinerFace + 0.5));
            double pieceBack = -(JoinerFace + 0.5) * size;               // the coupling art's back edge (FittingCentre, Piece)
            double shift = Math.Max(0, hoseBack - pieceBack);
            face = face0 + axis * shift;
            double wrapFront = shift - (JoinerFace + 0.03) * size + 0.05; // DrawEnds' Fitting: brass at -0.03 x size off the centre
            wrapLen = Geo.Clamp(wrapFront - hoseBack, 0, WrapLength);
            return true;
        }

        /// <summary>True when the hose's last ~0.5 cell runs more than ~35 degrees off <paramref name="axis"/> (it meets the port
        /// from the side).</summary>
        internal static bool SideArrival(IList<V2> pts, V2 axis)
        {
            int n = pts == null ? 0 : pts.Count;
            if (n < 2) return false;
            double[] s = Geo.CumLen(pts);
            V2 d1 = pts[n - 1] - At(pts, s, Math.Max(0, s[n - 1] - 0.5));
            if (d1.Len < 1e-9) return false;
            return Dot(d1.Norm(), axis) < SideEntryCos;
        }

        private static double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;

        /// <summary>Smootherstep of x over [0, 1] (0 below, 1 above): value, slope and second derivative are 0 at both ends.</summary>
        public static double SmootherStep(double x)
        {
            x = Geo.Clamp(x, 0, 1);
            return x * x * x * (x * (6 * x - 15) + 10);
        }

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
        internal static HoseLay Lay(CordWorld w, V2 a, V2 b, HoseShapeParams p, ulong seed, V2? endInward = null, V2? startOutward = null)
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
            if (!plan.Ok) return DirectJoin(w, a, b, p, seed, endInward, startOutward) ?? new HoseLay { Reason = "no route" };
            if (startOutward.HasValue) plan.Points.Insert(0, a);
            if (endInward.HasValue) plan.Points.Add(b);
            HoseLay lay = LayOn(w, a, b, plan.Points, p, seed, endInward, startOutward);
            return lay.Ok ? lay : DirectJoin(w, a, b, p, seed, endInward, startOutward) ?? lay;
        }

        /// <summary>REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT (owner walk 2026-10-23: "it said there was no room to attach it, even
        /// though it clearly has an open hose port"): a nozzle-to-nozzle link between two close reels whose outlet points AWAY
        /// from the target. The planned route starts OutletLead past the nozzle and heads straight back, a hairpin no join of
        /// the minimum bend radius can follow, so the lay was refused with <see cref="LeadOutBlocked"/>. When the ordinary lay
        /// fails and both ends have a direction, the hose is planned as the lead-out's straight run, then the shortest
        /// curves of at least the bend radius (every Dubins word, wall-clear, no loop, fewest stray reel/pump cells first)
        /// onto the end coupling's straight -- the way a stiff hose actually swings round -- and laid taut along that plan.
        /// Null when no such plan lays (the caller keeps its own refusal).</summary>
        internal static HoseLay DirectJoin(CordWorld w, V2 a, V2 b, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward)
        {
            if (!endInward.HasValue || !startOutward.HasValue) return null;
            V2 u = startOutward.Value, v = endInward.Value;
            double S = LeadOutStraight(p), R = Math.Max(0.45, p.MinBendRadius) * 1.05;
            if (!OutletClear(w, a, u, S)) return null;
            V2 s0 = a + u * S, e0 = b - v * HoseRelay.EndStraight;
            var taut = new HoseShapeParams { MinBendRadius = p.MinBendRadius, Slack = 0, PlumpAmount = p.PlumpAmount, CouplingSpacing = p.CouplingSpacing, MaxLength = p.MaxLength, LeadOut = p.LeadOut };
            var cands = new List<(int hits, double len, List<V2> pts)>();
            var none = new HashSet<Cell>();
            foreach (List<V2> arc in DubinsAll(s0, u, e0, v, R, Sample / 4, true))
            {
                var pts = new List<V2> { a };
                int ns = Math.Max(1, (int)Math.Ceiling(S / Sample));
                for (int i = 1; i <= ns; i++) pts.Add(a + u * (S * i / ns));
                pts.AddRange(arc);
                int ne = Math.Max(1, (int)Math.Ceiling(HoseRelay.EndStraight / Sample));
                for (int i = 1; i <= ne; i++) pts.Add(e0 + v * (HoseRelay.EndStraight * i / ne));
                if (!Clear(w, pts) || SelfIntersects(ResampleN(pts, Math.Max(8, (int)(Geo.Length(pts) / Sample) + 1)))) continue;
                cands.Add((RigHits(w, pts, none), Geo.Length(pts), pts));
            }
            foreach (var c in cands.OrderBy(c => c.hits).ThenBy(c => c.len))
            {
                if (c.len > p.MaxLength) continue;
                HoseLay lay = LayOn(w, a, b, c.pts, taut, seed, endInward, startOutward, true);
                if (lay.Ok) return lay;
            }
            return null;
        }

        /// <summary>A lead-out join whose plump pose is longer than this x the flat one (+0.5 cell) is a last resort (the fuzz
        /// "plump much longer than flat" bound, HoseFuzz).</summary>
        public const double PlumpGrowthMax = 1.25;

        /// <summary>Owner decision by question card 2026-10-06: how far the hose runs dead straight out of the nozzle before it
        /// may bend. Taken from the minimum bend radius: the coupling's own run (OutletStraight) plus half a radius, so a
        /// stiffer hose stands farther out of the coupling before its (never tighter than minimum) curve starts.
        /// A lay the lead search shortened (owner by card 2026-10-24 "Shorten the lead-out") runs straight for its LeadOut.</summary>
        public static double LeadOutStraight(HoseShapeParams p) => p.LeadOut > 0 ? p.LeadOut : FullLeadOut(p);
        /// <summary>The full lead-out of the 2026-10-06 card, before any shortening.</summary>
        public static double FullLeadOut(HoseShapeParams p) => HoseReelRect.OutletStraight + 0.5 * Math.Max(0.45, p.MinBendRadius);

        /// <summary>The lead-out: P's start replaced by a straight run of <paramref name="straight"/> from a along u, then the
        /// shortest radius-R curve (Dubins) onto P at some arc d past the straight run, P's heading there matched. The join point
        /// is chosen among candidates d = straight + R/2 .. straight + 8R (the least extra length whose new section is clear
        /// of walls; world null = no wall test). Null when no candidate fits. <paramref name="leadLen"/> = the new section's
        /// arc length (a to the join).</summary>
        internal static List<LeadCand> LeadOutCandidates(CordWorld w, IList<V2> P, V2 a, V2 u, double straight, double R, int max)
        {
            var outp = new List<LeadCand>();
            if (P == null || P.Count < 2) return outp;
            LayScratch ls = LayScratch.Get();
            double[] s = LayScratch.CumOf(P, ref ls.CandCum);
            double L = s[P.Count - 1];
            V2 s0 = a + u * straight;
            if (w != null) { List<V2> run = ls.Pose; run.Clear(); run.Add(a); run.Add(s0); if (!Clear(w, run)) return outp; }
            double Rd = R * 1.05;
            // HOSE_LAY_FIX_GC_STORM_FROM_WORKER: a candidate keeps only its Dubins arc; its section (a, the densified straight
            // run, the arc) and the pose it would make are assembled in this thread's scratch when it is judged, and copied
            // out only when it is taken (most are turned away: a wall, a loop). The section's length is summed in the same
            // order Geo.Length sums it, so the ranking is unchanged.
            // HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC (live round 7): a taken candidate keeps only what makes its pose (its
            // Dubins word, where it joins P); the pose is rebuilt in scratch by whoever reads it (LeadCand.PoseInto). The word and candidate lists are this thread's, and the
            // ranking is an index-tiebroken sort (the stable order OrderBy gave) on a reused array, not a LINQ sort.
            int ns = Math.Max(1, (int)Math.Ceiling(straight / Sample));
            List<V2> arc = ls.Arc;
            List<DubinsWord> words = ls.Words;
            List<RawCand> cands = ls.Cands;
            cands.Clear();
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
                V2 hQ = (P[j] - P[j - 1]).Norm();
                words.Clear();
                DubinsWords(s0, u, Q, hQ, Rd, Sample / 4, true, words, arc);
                foreach (DubinsWord dw in words)
                {
                DubinsArc(s0, u, Q, dw, Rd, Sample / 4, arc);
                double secLen = 0;
                V2 prev = a;
                for (int i = 1; i <= ns; i++) { V2 q = a + u * (straight * i / ns); secLen += V2.Dist(prev, q); prev = q; }   // densified so the smooth resample keeps it straight
                for (int i = 0; i < arc.Count; i++) { secLen += V2.Dist(prev, arc[i]); prev = arc[i]; }
                double extra = secLen - d;
                int jj = V2.Dist(arc[arc.Count - 1], P[j]) < 1e-9 ? j + 1 : j;
                if (jj >= P.Count) continue;
                cands.Add(new RawCand { extra = extra, dw = dw, Q = Q, j = jj, secLen = secLen, order = cands.Count });
                }
            }
            RawCand[] sorted = ls.SortedCands(cands);
            List<V2> o = ls.Pose, r = ls.Resampled;
            for (int ci = 0; ci < cands.Count; ci++)
            {
                RawCand c = sorted[ci];
                o.Clear();
                o.Add(a);
                for (int i = 1; i <= ns; i++) o.Add(a + u * (straight * i / ns));
                o.AddRange(DubinsArc(s0, u, c.Q, c.dw, Rd, Sample / 4, arc));
                int secCount = o.Count;
                if (w != null) { o.Add(P[c.j]); bool clear = Clear(w, o, 0.5); o.RemoveAt(secCount); if (!clear) continue; }
                for (int i = c.j; i < P.Count; i++) o.Add(P[i]);
                double len = Geo.Length(o);
                ResampleNInto(o, Math.Max(8, (int)(len / Sample) + 1), r);
                if (SelfIntersects(r)) continue;   // no loops (design)
                outp.Add(new LeadCand { extra = c.extra, leadLen = c.secLen, Len = len, P = P, J = c.j, A = a, U = u, Straight = straight, Ns = ns, Q = c.Q, Dw = c.dw, Rd = Rd });
                if (outp.Count >= max) break;
            }
            return outp;
        }

        /// <summary>A lead-out join LeadOutCandidates found: its extra length over the arc it replaces, the section's arc
        /// length (leadLen), the whole pose's length (Geo.Length of the pose, summed in the same order), and what makes the
        /// pose: a, the densified straight run, the Dubins arc for Dw, then P from index J on.</summary>
        internal sealed class LeadCand
        {
            internal double extra, leadLen, Len, Straight, Rd;
            internal IList<V2> P;
            internal int J, Ns;
            internal V2 A, U, Q;
            internal DubinsWord Dw;
            /// <summary>The whole pose into <paramref name="o"/> (cleared; returned). Uses this thread's arc scratch.</summary>
            internal List<V2> PoseInto(List<V2> o)
            {
                o.Clear();
                o.Add(A);
                for (int i = 1; i <= Ns; i++) o.Add(A + U * (Straight * i / Ns));
                o.AddRange(DubinsArc(A + U * Straight, U, Q, Dw, Rd, Sample / 4, LayScratch.Get().Arc));
                for (int i = J; i < P.Count; i++) o.Add(P[i]);
                return o;
            }
        }

        private struct RawCand : IComparable<RawCand>
        {
            internal double extra, secLen;
            internal DubinsWord dw;
            internal V2 Q;
            internal int j, order;
            public int CompareTo(RawCand o) { int c = extra.CompareTo(o.extra); return c != 0 ? c : order.CompareTo(o.order); }
        }

        /// <summary>One lay thread's reusable point lists and arc-length buffer for poses that are judged and mostly thrown
        /// away (HOSE_LAY_FIX_GC_STORM_FROM_WORKER). A user fills and reads one before calling anything else that uses it.</summary>
        private sealed class LayScratch
        {
            [ThreadStatic] private static LayScratch mine;
            internal readonly List<V2> Pose = new List<V2>(), Resampled = new List<V2>(), Dense = new List<V2>(), Arc = new List<V2>(), Cand = new List<V2>();
            internal double[] Cum = new double[64], ClearCum = new double[64], CandCum = new double[64], KeepCum = new double[64];
            internal readonly List<DubinsWord> Words = new List<DubinsWord>();
            internal readonly List<RawCand> Cands = new List<RawCand>();
            private RawCand[] sorted = new RawCand[64];
            internal PairKey[] Pairs = new PairKey[64];
            /// <summary>HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC: finished lead-out poses (LeadFin) and their arc lengths, handed
            /// back by LayOnce once its join is chosen (never the poses the lay kept).</summary>
            internal readonly Stack<List<V2>> FreePoses = new Stack<List<V2>>();
            internal readonly Stack<double[]> FreeCums = new Stack<double[]>();
            internal static LayScratch Get() => mine ?? (mine = new LayScratch());
            internal static double[] CumOf(IList<V2> p, ref double[] buf)
            {
                if (buf.Length < p.Count) buf = new double[Math.Max(p.Count, 2 * buf.Length)];
                buf[0] = 0;
                for (int i = 1; i < p.Count; i++) buf[i] = buf[i - 1] + V2.Dist(p[i - 1], p[i]);
                return buf;
            }
            internal RawCand[] SortedCands(List<RawCand> c)
            {
                if (sorted.Length < c.Count) sorted = new RawCand[Math.Max(c.Count, 2 * sorted.Length)];
                c.CopyTo(sorted);
                Array.Sort(sorted, 0, c.Count);
                return sorted;
            }
            internal List<V2> TakePose() => FreePoses.Count > 0 ? FreePoses.Pop() : new List<V2>();
            internal double[] TakeCum() => FreeCums.Count > 0 ? FreeCums.Pop() : new double[64];
        }

        /// <summary>A lead-out pair's rank key (the summed extra), ties broken by the flat-major index: the stable order the
        /// OrderBy it replaces gave.</summary>
        private struct PairKey : IComparable<PairKey>
        {
            internal double k;
            internal int x, y, order;
            public int CompareTo(PairKey o) { int c = k.CompareTo(o.k); return c != 0 ? c : order.CompareTo(o.order); }
        }

        /// <summary>One finished lead-out pose (LeadOutFinish) and the pair tests LayOnce runs on it, each worked out once: the
        /// wall test now, the arc lengths for the bend test, and the stray-reel count and body gap on first use (both pure in
        /// the pose for one lay). Its pose and arc lengths come from this thread's pools and go back by Release.</summary>
        private sealed class LeadFin
        {
            internal readonly List<V2> Pts;
            internal readonly bool Clear;
            private double[] s;
            private int rig = -1;
            private double gap = double.NaN;
            internal LeadFin(CordWorld w, List<V2> pts) { Pts = pts; Clear = HoseMath.Clear(w, pts); }
            internal double MinBendUpTo(double upTo)
            {
                if (s == null) { s = LayScratch.Get().TakeCum(); s = LayScratch.CumOf(Pts, ref s); }
                return MinBendRadiusUpTo(Pts, s, EndSkip, upTo);
            }
            internal int RigOf(CordWorld w, HashSet<Cell> planCells) => rig >= 0 ? rig : (rig = RigHits(w, Pts, planCells));
            internal double GapOf(CordWorld w, double startSkip) => !double.IsNaN(gap) ? gap : (gap = BodyGap(w, Pts, startSkip, EndSkip));
            /// <summary>Back to the pools: the arc lengths always, the pose unless the lay kept it.</summary>
            internal void Release(LayScratch ls, HoseLay kept)
            {
                if (s != null) { ls.FreeCums.Push(s); s = null; }
                if (!ReferenceEquals(Pts, kept.Flat) && !ReferenceEquals(Pts, kept.Plump) && !ReferenceEquals(Pts, kept.Centre)) ls.FreePoses.Push(Pts);
            }
        }

        /// <summary>Points of P within <paramref name="straight"/> of a projected back onto the outlet line.</summary>
        internal static void KeepStraight(List<V2> P, V2 a, V2 u, double straight)
        {
            LayScratch ls = LayScratch.Get();
            double[] s = LayScratch.CumOf(P, ref ls.KeepCum);
            P[0] = a;
            for (int i = 1; i < P.Count - 1 && s[i] <= straight + 1e-9; i++)
            {
                V2 d = P[i] - a;
                P[i] = a + u * Math.Max(0, d.X * u.X + d.Z * u.Z);
            }
        }

        /// <summary>The final pose of a lead-out candidate at n samples: resampled along its Catmull-Rom curve (a plain
        /// equal-arc resample of a polyline at another spacing reads its bends up to ~2x tighter), the straight run kept.</summary>
        internal static List<V2> LeadOutFinishInto(IList<V2> o, int n, V2 a, V2 u, double straight, List<V2> into)
        {
            List<V2> X = ResampleSmoothInto(o, n, into);
            KeepStraight(X, a, u, straight);
            return X;
        }

        /// <summary>n equal-arc samples of the uniform Catmull-Rom curve through p (8 sub-steps per segment), ends exact.</summary>
        internal static List<V2> ResampleSmoothInto(IList<V2> p, int n, List<V2> o)
        {
            if (p.Count < 3) return ResampleNInto(p, n, o);
            List<V2> d = LayScratch.Get().Dense;   // ResampleNInto copies out of it before anything else can refill it
            d.Clear();
            d.Add(p[0]);
            for (int i = 0; i < p.Count - 1; i++)
            {
                V2 p0 = i > 0 ? p[i - 1] : p[0] * 2 - p[1], p1 = p[i], p2 = p[i + 1], p3 = i + 2 < p.Count ? p[i + 2] : p[i + 1] * 2 - p[i];
                for (int k = 1; k <= 8; k++)
                {
                    double t = k / 8.0, t2 = t * t, t3 = t2 * t;
                    d.Add((p1 * 2 + (p2 - p0) * t + (p0 * 2 - p1 * 5 + p2 * 4 - p3) * t2 + (p1 * 3 - p0 - p2 * 3 + p3) * t3) * 0.5);
                }
            }
            ResampleNInto(d, n, o);
            o[0] = p[0];
            o[n - 1] = p[p.Count - 1];
            return o;
        }

        /// <summary>The lead-out lay's sample spacing (cells).</summary>
        public const double LeadOutSpacing = Sample;
        /// <summary>The lead-out lay's sample count for a pose of length <paramref name="len"/> (LeadCand.Len).</summary>
        internal static int LeadOutSamplesOfLen(double len) => Math.Max(8, (int)Math.Ceiling(len / LeadOutSpacing) + 1);

        /// <summary>MinBendRadius restricted to arc positions [skip, upTo].</summary>
        internal static double MinBendRadiusUpTo(IList<V2> X, double skip, double upTo) => MinBendRadiusUpTo(X, Geo.CumLen(X), skip, upTo);

        /// <summary>As above on X's own cumulative arc lengths <paramref name="s"/> (Geo.CumLen).</summary>
        internal static double MinBendRadiusUpTo(IList<V2> X, double[] s, double skip, double upTo)
        {
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

        /// <summary>The shortest path from (p0, heading h0) to (p1, heading h1) whose curvature radius is never under R (Dubins:
        /// the best of LSL, RSR, LSR, RSL, RLR, LRL), sampled about every <paramref name="step"/> from p0 (exclusive) to p1
        /// (inclusive). Every candidate is integrated and kept only if it lands on p1 heading h1; shortest first, only the
        /// shortest unless <paramref name="allWords"/>. Empty if none does (Dubins returns null then).</summary>
        internal static List<List<V2>> DubinsAll(V2 p0, V2 h0, V2 p1, V2 h1, double R, double step, bool allWords)
        {
            var all = new List<List<V2>>();
            var words = new List<DubinsWord>();
            DubinsWords(p0, h0, p1, h1, R, step, allWords, words, null);
            foreach (DubinsWord dw in words) all.Add(DubinsArc(p0, h0, p1, dw, R, step, new List<V2>()));
            return all;
        }

        /// <summary>One Dubins word that lands (DubinsWords): its letters and its three section lengths (cells).</summary>
        internal struct DubinsWord { internal string W; internal double L0, L1, L2; }
        private struct DubCand { internal string w; internal double t, p, q, key; }
        [ThreadStatic] private static DubCand[] dubScratch;

        /// <summary>DubinsAll's arc for <paramref name="dw"/>, sampled into <paramref name="o"/> (cleared; returned), its last
        /// point exactly p1.</summary>
        internal static List<V2> DubinsArc(V2 p0, V2 h0, V2 p1, DubinsWord dw, double R, double step, List<V2> o)
        {
            DubinsSampleInto(p0, Math.Atan2(h0.Z, h0.X), dw.W, dw.L0, dw.L1, dw.L2, R, step, o, out _);
            o[o.Count - 1] = p1;
            return o;
        }

        /// <summary>DubinsAll's words, shortest first, only those whose sampled arc lands on p1 heading h1, appended to
        /// <paramref name="into"/>; the landing test samples into <paramref name="scratch"/> (a fresh list when null). The
        /// lay's lead-out search keeps these and samples an arc only when it judges it (HOSE_LAY_FIX_GC_STORM_FROM_WORKER).</summary>
        internal static void DubinsWords(V2 p0, V2 h0, V2 p1, V2 h1, double R, double step, bool allWords, List<DubinsWord> into, List<V2> scratch)
        {
            double Mod(double x) { x %= 2 * Math.PI; return x < 0 ? x + 2 * Math.PI : x; }
            V2 D = p1 - p0;
            double d = D.Len / R, th = Math.Atan2(D.Z, D.X);
            double al = Mod(Math.Atan2(h0.Z, h0.X) - th), be = Mod(Math.Atan2(h1.Z, h1.X) - th);
            double sa = Math.Sin(al), sb = Math.Sin(be), ca = Math.Cos(al), cb = Math.Cos(be), cab = Math.Cos(al - be);
            // HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC: the (at most six) words on this thread's reused array, ranked by an
            // insertion sort that keeps equal lengths in the order found (the stable order the LINQ OrderBy gave)
            DubCand[] cands = dubScratch ?? (dubScratch = new DubCand[6]);
            int nc = 0;
            void Add(string wd, double t, double p, double q)
            {
                var c = new DubCand { w = wd, t = t, p = p, q = q, key = t + p + q };
                int i = nc++;
                while (i > 0 && cands[i - 1].key.CompareTo(c.key) > 0) { cands[i] = cands[i - 1]; i--; }
                cands[i] = c;
            }
            double tmp;
            tmp = 2 + d * d - 2 * cab + 2 * d * (sa - sb);
            if (tmp >= 0) { double at = Math.Atan2(cb - ca, d + sa - sb); Add("LSL", Mod(-al + at), Math.Sqrt(tmp), Mod(be - at)); }
            tmp = 2 + d * d - 2 * cab + 2 * d * (sb - sa);
            if (tmp >= 0) { double at = Math.Atan2(ca - cb, d - sa + sb); Add("RSR", Mod(al - at), Math.Sqrt(tmp), Mod(-be + at)); }
            tmp = -2 + d * d + 2 * cab + 2 * d * (sa + sb);
            if (tmp >= 0) { double pp = Math.Sqrt(tmp), at = Math.Atan2(-ca - cb, d + sa + sb) - Math.Atan2(-2, pp); Add("LSR", Mod(-al + at), pp, Mod(-be + at)); }
            tmp = -2 + d * d + 2 * cab - 2 * d * (sa + sb);
            if (tmp >= 0) { double pp = Math.Sqrt(tmp), at = Math.Atan2(ca + cb, d - sa - sb) - Math.Atan2(2, pp); Add("RSL", Mod(al - at), pp, Mod(be - at)); }
            tmp = (6 - d * d + 2 * cab + 2 * d * (sa - sb)) / 8;
            if (Math.Abs(tmp) <= 1) { double pp = Mod(2 * Math.PI - Math.Acos(tmp)), t = Mod(al - Math.Atan2(ca - cb, d - sa + sb) + pp / 2); Add("RLR", t, pp, Mod(al - be - t + pp)); }
            tmp = (6 - d * d + 2 * cab + 2 * d * (-sa + sb)) / 8;
            if (Math.Abs(tmp) <= 1) { double pp = Mod(2 * Math.PI - Math.Acos(tmp)), t = Mod(-al - Math.Atan2(ca - cb, d + sa - sb) + pp / 2); Add("LRL", t, pp, Mod(be - al - t + pp)); }
            double h1a = Math.Atan2(h1.Z, h1.X);
            List<V2> pts = scratch ?? new List<V2>();
            for (int ci = 0; ci < nc; ci++)
            {
                DubCand c = cands[ci];
                var dw = new DubinsWord { W = c.w, L0 = c.t * R, L1 = c.p * R, L2 = c.q * R };
                DubinsSampleInto(p0, Math.Atan2(h0.Z, h0.X), dw.W, dw.L0, dw.L1, dw.L2, R, step, pts, out double thEnd);
                double hErr = Math.Abs(Math.Atan2(Math.Sin(thEnd - h1a), Math.Cos(thEnd - h1a)));
                if (V2.Dist(pts[pts.Count - 1], p1) > 1e-3 * Math.Max(1, R) || hErr > 1e-3) continue;
                into.Add(dw);
                if (!allWords) break;
            }
        }

        internal static List<V2> Dubins(V2 p0, V2 h0, V2 p1, V2 h1, double R, double step)
        {
            List<List<V2>> a = DubinsAll(p0, h0, p1, h1, R, step, false);
            return a.Count > 0 ? a[0] : null;
        }

        private static void DubinsSampleInto(V2 p0, double th, string word, double l0, double l1, double l2, double R, double step, List<V2> o, out double thEnd)
        {
            o.Clear();
            double x = p0.X, z = p0.Z;
            for (int k = 0; k < 3; k++)
            {
                double l = k == 0 ? l0 : k == 1 ? l1 : l2;
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
        }

        /// <summary>How far out of the outlet the route is planned from: the straight run plus two bend radii, so even a turn
        /// back past 90 degrees rounds after the coupling's wrap instead of kinking at it.</summary>
        public static double OutletLead(HoseShapeParams p) => p.LeadOut > 0 ? p.LeadOut : HoseReelRect.OutletStraight + 2 * Math.Max(0.45, p.MinBendRadius);

        /// <summary>The outlet run from <paramref name="a"/> (plus its 0.5-cell blend) lies on open ground.</summary>
        internal static bool OutletClear(CordWorld w, V2 a, V2 outward, double run = HoseReelRect.OutletStraight)
        {
            V2 e = a + outward * (run + 0.5);
            return w.InBounds(e.Floor) && w.IsWalkable(e.Floor) && SegmentClear(w, a + outward * 0.5, e);
        }

        /// <summary>Colonist-carried hose (hose_carry_design_2026-10-04 section 6, stage S2): lay the hose along the cells
        /// a colonist actually WALKED instead of a planned route. The walked cells are pulled taut from the reel's mouth
        /// (HoseTrail.Pulled: any-angle, never through a wall or a pinched diagonal) and then run through exactly Lay's
        /// round -> settle -> stiffen pipeline. An EMPTY route is the legacy / DEV "planned" hose: it is HoseMath.Lay
        /// itself, so a save written before the carry stage lays byte-identically.</summary>
        internal static HoseLay LayAlong(CordWorld w, V2 a, IList<Cell> route, V2 b, HoseShapeParams p, ulong seed, V2? endInward = null, V2? startOutward = null)
        {
            HoseLay lay = LayAlongAt(w, a, route, b, p, seed, endInward, startOutward);
            if (!startOutward.HasValue || !G2On || p.LeadOut > 0 || (lay.Ok && lay.G2)) return lay;
            // step 6 (owner by card 2026-10-24 "Shorten the lead-out"): no G2 curve fits behind the full straight lead-out (a
            // short span), so the lead-out shrinks -- the largest lead in [LeadOutMin, full) whose lay is G2 (LeadSearch), never
            // shorter than that. A lead-out a wall blocks stays refused (card 2026-10-06); a hose that fits keeps the full lead.
            double full = FullLeadOut(p);
            if (!OutletClear(w, a, startOutward.Value, full)) return TooClose(lay, a, b, p);
            HoseLay best = null;
            double got = LeadSearch(full, ld =>
            {
                HoseLay t = LayAlongAt(w, a, route, b, p.WithLeadOut(ld), seed, endInward, startOutward);
                if (!(t.Ok && t.G2)) return false;
                best = t;
                return true;
            });
            if (got <= 0) return TooClose(lay, a, b, p);
            // the search's last fitting lay is the one at `got` (LeadSearch only moves its lower end onto a lead that fit)
            best.LeadShortened = true;
            LeadShortened++;
            return best;
        }

        /// <summary>Step 5 (delegated call 2026-10-24, no kinked fallback): a nozzled reel's lay that no G2 curve carries at any
        /// lead-out down to LeadOutMin is refused with <see cref="TooCloseToBend"/> instead of drawn as the shaped pose -- when
        /// the target is within <see cref="TooCloseReach"/> of the mouth, the span the reason names. A longer route that misses
        /// G2 (a 1-cell corridor that cannot hold the bend, HoseSelfTest maze 6: 11 of 300 seeds) is not "too close" and keeps
        /// its shaped lay, as before step 5.</summary>
        private static HoseLay TooClose(HoseLay shaped, V2 a, V2 b, HoseShapeParams p)
        {
            // already refused with its own reason, or never fitted (a stub under a cell: G2Fit leaves no G2Why)
            if (!shaped.Ok || shaped.G2Why == null) return shaped;
            if (V2.Dist(a, b) > TooCloseReach(p)) return shaped;
            TooCloseRefused++;
            return new HoseLay { Reason = TooCloseToBend, G2Why = shaped.G2Why, PathLen = shaped.PathLen };
        }

        /// <summary>The full lead-out plus one whole turn at the minimum bend: a target nearer the mouth than this is a span too
        /// short to bend into (2.2 + 7.54 = 9.74 cells at the default 1.2 bend; the near ring's farthest port is ~7).</summary>
        internal static double TooCloseReach(HoseShapeParams p) => FullLeadOut(p) + 2 * Math.PI * Math.Max(0.45, p.MinBendRadius);

        /// <summary>Lays refused with <see cref="TooCloseToBend"/> since load (the selftest's cost line).</summary>
        internal static int TooCloseRefused;

        private static HoseLay LayAlongAt(CordWorld w, V2 a, IList<Cell> route, V2 b, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward)
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
                // HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE: the walk starts on the reel's own cells; once the hose leaves by
                // the nozzle those points are behind it, and hopping to them would drag it back over the drum
                while (pts.Count > 2 && w.ExtraCost(pts[1].Floor) >= BuildingCrossCost) pts.RemoveAt(1);
                if (!OutletClear(w, a, startOutward.Value, lead)) return new HoseLay { Reason = LeadOutBlocked };
                else if (SegmentClear(w, o, pts[1]) && SegmentAvoidsBuildings(w, o, pts[1])) pts.Insert(1, o);
                else if ((hop = CordPlanner.Plan(w, o, pts[1], new List<KeyValuePair<V2, WaypointKind>>())).Ok && hop.Points.Count >= 2)
                    pts.InsertRange(1, hop.Points.Take(hop.Points.Count - 1));     // round the reel to where the walk went
                else return DirectJoin(w, a, b, p, seed, endInward, startOutward) ?? new HoseLay { Reason = LeadOutBlocked };
            }
            HoseLay lay = LayOn(w, a, b, pts, p, seed, endInward, startOutward);
            return lay.Ok ? lay : DirectJoin(w, a, b, p, seed, endInward, startOutward) ?? lay;
        }

        /// <summary>Why a nozzled reel's hose was refused: no room for the straight lead-out (owner card 2026-10-06).</summary>
        public const string LeadOutBlocked = "no room for the straight lead-out from the nozzle";
        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 5 (delegated call, no kinked fallback): no curve within the bend
        /// limit joins the nozzle's lead-out to the end, so the lay is refused with this player-visible reason.</summary>
        public const string TooCloseToBend = "Too close for the hose to bend \u2014 move the reel back";
        /// <summary>Why a hose was refused because, laid, it would be longer than the hose (GPT source read B3).</summary>
        public const string LaidTooLong = "route too long (the laid hose, lead-out included, is longer than the hose)";

        /// <summary>Lay's shared tail. GPT source read 2026-10-06 B3: the laid hose is never longer than the hose. CheckInstall
        /// judges the taut route, which does not count the outlet lead-out, and the slack cap only bounds the EXTRA; so a lay
        /// over the hose's length is retried with no slack, and refused (reel retracts with the reason) if still too long.</summary>
        private static HoseLay LayOn(CordWorld w, V2 a, V2 b, List<V2> planPoints, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward = null, bool shaped = false)
        {
            HoseLay lay = LayOnce(w, a, b, planPoints, p, seed, endInward, startOutward, shaped);
            if (!lay.Ok || !Overlong(lay, p.MaxLength)) return lay;
            if (p.Slack > 0)
            {
                var taut = new HoseShapeParams { MinBendRadius = p.MinBendRadius, Slack = 0, PlumpAmount = p.PlumpAmount, CouplingSpacing = p.CouplingSpacing, MaxLength = p.MaxLength, LeadOut = p.LeadOut };
                HoseLay t = LayOnce(w, a, b, planPoints, taut, seed, endInward, startOutward, shaped);
                if (t.Ok && !Overlong(t, p.MaxLength)) return t;
            }
            return new HoseLay { Reason = LaidTooLong, PathLen = lay.PathLen };
        }

        public static bool Overlong(HoseLay lay, double maxLength) => Math.Max(lay.FlatLen, lay.PlumpLen) > maxLength + 1e-6;

        /// <param name="shaped">REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT: the plan is already a hose-shaped curve (DirectJoin's Dubins
        /// path, every bend at the minimum radius), laid as it is: rounding, S-curves and stiffening are skipped. Stiffening pulls
        /// a curve with fixed ends toward their chord, so a swing round behind the reel collapsed to the 2-cell straight line
        /// between the two nozzles and no lead-out could join it.</param>
        private static HoseLay LayOnce(CordWorld w, V2 a, V2 b, List<V2> planPoints, HoseShapeParams p, ulong seed, V2? endInward, V2? startOutward = null, bool shaped = false)
        {
            if (shaped) return LayShaped(w, a, b, planPoints, p, endInward, startOutward);
            var lay = new HoseLay();
            // HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE: the reel/pump cells the PLAN crosses (it chose to, at their cost); every
            // shaping stage below prefers a pose that enters no other one (RigHits), so a bend or S-curve never swings the
            // hose back over a reel the plan went round
            HashSet<Cell> planCells = CellsAlong(planPoints);
            int Rig(List<V2> pts) => RigHits(w, pts, planCells);
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
            if (!Clear(w, F) || Rig(F) > 0)
            {
                // round 4: the rounded centreline itself can clip a stub corner in a one-cell zig-zag; the string-pulled
                // plan (line of sight between its corners) is the last resort, and a hose that still crosses a wall is
                // not laid at all (the reel retracts it with the reason) rather than drawn through the wall.
                // Scenic route: the first wall-clear pose with the fewest stray reel/pump cells wins (with none near, that
                // is the first wall-clear pose, as before)
                List<V2> first = F;
                List<V2> best = null;
                int bestHits = int.MaxValue;
                foreach (Func<List<V2>> make in new Func<List<V2>>[] { () => first, () => Stiffen(w, C, p.MinBendRadius),
                                                                      () => Geo.Resample(C, Sample), () => Geo.Resample(planPoints, Sample) })
                {
                    List<V2> cand = make();
                    if (!Clear(w, cand)) continue;
                    int h = Rig(cand);
                    if (h < bestHits) { best = cand; bestHits = h; }
                    if (h == 0) break;
                }
                if (best == null) { lay.Reason = "no clear route (corners too tight for the hose)"; return lay; }
                lay.FellBack = !ReferenceEquals(best, first);
                F = best;
            }
            int n = Math.Max(8, F.Count);
            lay.Flat = ResampleN(F, n);
            lay.Centre = ResampleN(Geo.Resample(C, Sample), n);
            double k = Straighten(p.PlumpAmount);
            var P = new List<V2>(n);
            for (int i = 0; i < n; i++) P.Add(lay.Flat[i] + (lay.Centre[i] - lay.Flat[i]) * k);
            P = ResampleN(Stiffen(w, P, p.MinBendRadius), n);
            if (!Clear(w, P) || Rig(P) > Rig(lay.Flat)) P = new List<V2>(lay.Flat);
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
                bool done = false;
                // scenic route: first only joins that cross no stray reel/pump cell; only if one was turned away for that alone
                // does a second pass take the old first-that-fits (a cost, never a refusal)
                bool rigTurnedAway = false;
                // HOSE_BEND_FIX_SHAVES_WALL_CORNERS: first only joins whose drawn body clears every wall (BodyGap); the old
                // centreline rule only when every join was turned away for that alone
                double bodyHalf = BodyHalf(p.PlumpAmount);
                bool bodyTurnedAway = false;
                (List<V2> f, List<V2> q, LeadCand cc, int m, double lead)? shave = null;
                double shaveGap = double.NegativeInfinity;
                // HOSE_ENDS_FIX_MISSES_THE_PORTS (fuzz seeds 144 & co. once the nozzle moved to the measured art): the cheapest
                // pair can join the plump pose by a long detour the flat pose does not take, so the hose visibly grows when it
                // fills. Such a pair is only kept as the last resort, after every other join was tried.
                (List<V2> f, List<V2> q, LeadCand cc, int m, double lead)? longPlump = null;
                // HOSE_LAY_FIX_GC_STORM_FROM_WORKER: the candidates and finished poses depend on neither pass flag, so they are
                // made once per lay for all four passes; the 4-list is the 24-list's prefix (both shortest first, cut at
                // the count), so a finished pose keyed by its index is the same pose in either
                var fFin = new Dictionary<long, LeadFin>();
                var qFin = new Dictionary<long, LeadFin>();
                var fcOf = new Dictionary<int, List<LeadCand>>();
                var qcOf = new Dictionary<int, List<LeadCand>>();
                // HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC: the centre's join depends on no pair, so it is found once (it was found
                // again for every pair that passed the wall, bend, rig and body tests); finished poses come from this thread's
                // pool and go back to it below, all but the two the lay keeps
                List<LeadCand> ccs = null;
                LayScratch ls = LayScratch.Get();
                foreach (bool body in new[] { true, false })
                {
                if (done || (!body && BodyRuleOn && !bodyTurnedAway) || (body && !BodyRuleOn)) continue;
                rigTurnedAway = false;
                foreach (bool scenic in new[] { true, false })
                {
                if (done || (!scenic && !rigTurnedAway)) break;
                // 2026-10-10 (full-list M4, maze 6 selftest): the 4 shortest joins all land just before a jog in the planned
                // line (the outlet run meets the first cell centre), and the bend window past the join reads that jog at ~0.7
                // < R -- 85 of 300 seeds refused. When none of the 4 fits, joins farther along (up to the 24 the search
                // yields) are tried before refusing.
                foreach (int cmax in new[] { 4, 24 })
                {
                if (done) break;
                if (!fcOf.TryGetValue(cmax, out var fc)) fcOf[cmax] = fc = LeadOutCandidates(w, lay.Flat, a, u, S, R, cmax);
                if (!qcOf.TryGetValue(cmax, out var qc)) qcOf[cmax] = qc = LeadOutCandidates(w, lay.Plump, a, u, S, R, cmax);
                // HOSE_LAY_FIX_GC_STORM_FROM_WORKER: a pair's finished pose and every test on it depend on its own candidate and
                // the sample count only, so each is made and judged once (LeadFin) rather than once per pair it is in: up to
                // 24 x 24 pairs re-finished both sides each, ~265 MB of garbage per outflow lay on the 325 basin map
                LeadFin Fin(Dictionary<long, LeadFin> memo, LeadCand c, int idx, int m)
                {
                    long key = ((long)idx << 32) | (uint)m;
                    if (!memo.TryGetValue(key, out LeadFin fin))
                        memo[key] = fin = new LeadFin(w, LeadOutFinishInto(c.PoseInto(ls.Cand), m, a, u, S, ls.TakePose()));
                    return fin;
                }
                // HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC: ranked on this thread's reused array, ties by the flat-major index (the
                // stable order the LINQ OrderBy gave)
                int np = fc.Count * qc.Count;
                if (ls.Pairs.Length < np) ls.Pairs = new PairKey[Math.Max(np, 2 * ls.Pairs.Length)];
                PairKey[] pairs = ls.Pairs;
                for (int xi = 0, o = 0; xi < fc.Count; xi++)
                    for (int yi = 0; yi < qc.Count; yi++, o++) pairs[o] = new PairKey { k = fc[xi].extra + qc[yi].extra, x = xi, y = yi, order = o };
                Array.Sort(pairs, 0, np);
                for (int pi = 0; pi < np; pi++)
                {
                    PairKey ix = pairs[pi];
                    var pair = (x: fc[ix.x], y: qc[ix.y]);
                    int m = Math.Max(LeadOutSamplesOfLen(pair.x.Len), LeadOutSamplesOfLen(pair.y.Len));
                    LeadFin fF = Fin(fFin, pair.x, ix.x, m), qF = Fin(qFin, pair.y, ix.y, m);
                    List<V2> f = fF.Pts, q = qF.Pts;
                    if (!fF.Clear || !qF.Clear) continue;
                    double lead = Math.Max(pair.x.leadLen, pair.y.leadLen);
                    if (Math.Min(fF.MinBendUpTo(lead + 2 * R + 1), qF.MinBendUpTo(lead + 2 * R + 1)) < R * 0.97) continue;
                    if (scenic && fF.RigOf(w, planCells) + qF.RigOf(w, planCells) > 0) { rigTurnedAway = true; continue; }
                    double gap = Math.Min(fF.GapOf(w, S), qF.GapOf(w, S));
                    if (body && gap < bodyHalf) { bodyTurnedAway = true; continue; }
                    var cc = ccs ?? (ccs = LeadOutCandidates(null, lay.Centre, a, u, S, R, 1));
                    if (Geo.Length(q) > Geo.Length(f) * PlumpGrowthMax + 0.5)
                    {
                        if (longPlump == null) longPlump = (f, q, cc.Count > 0 ? cc[0] : null, m, pair.x.leadLen);
                        continue;
                    }
                    // no join clears the body: of the joins that fit, the one standing farthest off the walls
                    if (!body && BodyRuleOn) { if (gap > shaveGap) { shave = (f, q, cc.Count > 0 ? cc[0] : null, m, pair.x.leadLen); shaveGap = gap; } continue; }
                    lay.Flat = f;
                    lay.Plump = q;
                    lay.Centre = cc.Count > 0 ? ResampleN(cc[0].PoseInto(ls.Cand), m) : ResampleN(StraightenStart(lay.Centre, a, u, S), m);
                    lay.LeadOutLen = pair.x.leadLen;
                    done = true;
                    break;
                }
                if (!done && shave.HasValue)
                {
                    var sv = shave.Value;
                    lay.Flat = sv.f;
                    lay.Plump = sv.q;
                    lay.Centre = sv.cc != null ? ResampleN(sv.cc.PoseInto(ls.Cand), sv.m) : ResampleN(StraightenStart(lay.Centre, a, u, S), sv.m);
                    lay.LeadOutLen = sv.lead;
                    done = true;
                }
                }
                }
                }
                if (!done && longPlump.HasValue)
                {
                    var lp = longPlump.Value;
                    lay.Flat = lp.f;
                    lay.Plump = lp.q;
                    lay.Centre = lp.cc != null ? ResampleN(lp.cc.PoseInto(ls.Cand), lp.m) : ResampleN(StraightenStart(lay.Centre, a, u, S), lp.m);
                    lay.LeadOutLen = lp.lead;
                    done = true;
                }
                foreach (LeadFin fin in fFin.Values) fin.Release(ls, lay);
                foreach (LeadFin fin in qFin.Values) fin.Release(ls, lay);
                if (!done) return new HoseLay { Reason = LeadOutBlocked, PathLen = L };
            }
            return Finish(w, lay, p, Rig, endInward, startOutward);
        }

        /// <summary>LayOnce's shared tail: joiners (rigid, straightened, dropped where they would touch a wall or a reel),
        /// lengths, bend radii and couplings. <paramref name="Rig"/> counts stray reel/pump cells as the caller judges them.</summary>
        private static HoseLay Finish(CordWorld w, HoseLay lay, HoseShapeParams p, Func<List<V2>, int> Rig, V2? endInward, V2? startOutward)
        {
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
                // HOSE_BEND_FIX_SHAVES_WALL_CORNERS: a joiner's straightened run never pulls the drawn body onto a wall it cleared
                if (BodyRuleOn)
                {
                    double bh = BodyHalf(p.PlumpAmount), sk = lay.LeadOutLen > 0 ? LeadOutStraight(p) : EndSkip;
                    if (BodyGap(w, f, sk, EndSkip) < Math.Min(bh, BodyGap(w, lay.Flat, sk, EndSkip)) - 1e-9
                        || BodyGap(w, q, sk, EndSkip) < Math.Min(bh, BodyGap(w, lay.Plump, sk, EndSkip)) - 1e-9) continue;
                }
                if (Rig(f) > Rig(lay.Flat) || Rig(q) > Rig(lay.Plump)) continue;
                lay.Flat = f;
                lay.Plump = q;
                lay.Joints.Add(j);
            }
            G2Fit(w, lay, p, Rig, endInward, startOutward);
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

        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: off = the poses are left as the shaping stages made them. ON since
        /// 2026-10-24: the Gauss-Newton solver with the analytic Jacobian costs about half a millisecond a solve (the hose fuzz:
        /// ~2 ms per laid hose); the offline ruler's `--hose-curves g2off` measures the shaped poses alone.</summary>
        internal static bool G2On = true;
        /// <summary>The fit's curvature limit as a fraction of 1/R (the ruler allows 1/R x 1.05 on its discrete stencil).</summary>
        internal const double G2KappaMargin = 0.95;
        /// <summary>Tracking weights tried in turn: a fit that drapes too far from the shaped pose (into a wall, over a reel) is
        /// pulled back onto it.</summary>
        private static readonly double[] G2TrackWeights = { 1, 8, 64 };
        /// <summary>An infeasible fit is retried heavier only when its end came this close (cells).</summary>
        internal static double G2RetryGap = 0.3;

        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS (owner 2026-10-23 22:15): the shaped flat and charged poses re-laid as
        /// clothoid chains (HoseClothoid) of the hose's own length, so position, heading and curvature are continuous everywhere,
        /// |curvature| stays under 1/R, the lead-out leaves the nozzle dead straight along its axis, the end arrives straight
        /// along <paramref name="endInward"/>, and every joiner's run is straight. Both poses get the same material sampling
        /// (the drawn transition lerps them index by index). A fit that is not feasible, or that touches a wall, a stray reel or
        /// the body clearance the shaped pose had, is retried pulled closer to the shaped pose; if none holds, the shaped poses
        /// are kept as they were.</summary>
        private static void G2Fit(CordWorld w, HoseLay lay, HoseShapeParams p, Func<List<V2>, int> Rig, V2? endInward, V2? startOutward)
        {
            double R = Math.Max(0.45, p.MinBendRadius), kmax = G2KappaMargin / R;
            lay.Kmax = 1 / R;
            lay.Lead0 = lay.Outlet && startOutward.HasValue ? LeadOutStraight(p) : 0;
            lay.Lead1 = endInward.HasValue ? HoseRelay.EndStraight : 0;
            if (!G2On || lay.Flat.Count < 3) return;
            double L = Geo.Length(lay.Flat);
            if (L < 1.0) return;
            G2Tried++;
            double[] sF = Geo.CumLen(lay.Flat);
            double half = JoinerHalf(VisibleWidth(1, p.PlumpAmount));
            var spans = new List<(double, double)>();
            var js = new List<double>();
            foreach (int j in lay.Joints)
            {
                double s = sF[Math.Min(j, sF.Length - 1)];
                js.Add(s);
                spans.Add((s - half, s + half));
            }
            V2? a0 = null;
            double lead0 = 0;
            if (lay.Outlet && startOutward.HasValue) { a0 = startOutward.Value.Norm(); lead0 = LeadOutStraight(p); }
            V2? a1 = endInward.HasValue ? endInward.Value.Norm() : (V2?)null;
            double lead1 = a1.HasValue ? HoseRelay.EndStraight : 0;
            int rigF = Rig(lay.Flat), rigP = Rig(lay.Plump);
            double sk = lay.LeadOutLen > 0 ? LeadOutStraight(p) : EndSkip, bh = BodyHalf(p.PlumpAmount);
            double gapF = BodyRuleOn ? Math.Min(bh, BodyGap(w, lay.Flat, sk, EndSkip)) : 0, gapP = BodyRuleOn ? Math.Min(bh, BodyGap(w, lay.Plump, sk, EndSkip)) : 0;
            var why = new List<string>();
            double fitLen = 0;
            List<V2> FitAt(List<V2> route, int rig0, double gap0, double len, bool scan)
            {
                // a shortened lead marks a span near its bend limit, where only a narrow band of lengths carries the curve
                if (scan && p.LeadOut > 0)
                    foreach (double m in ShortLeadStretch) { List<V2> r = FitOnce(route, rig0, gap0, len * m); if (r != null) { fitLen = len * m; return r; } }
                else { List<V2> r = FitOnce(route, rig0, gap0, len); if (r != null) { fitLen = len; return r; } }
                return null;
            }
            List<V2> Fit(List<V2> route, int rig0, double gap0, double len) => FitAt(route, rig0, gap0, len, true);
            List<V2> FitOnce(List<V2> route, int rig0, double gap0, double len)
            {
                if (len > p.MaxLength) return null;
                foreach (double step in p.LeadOut > 0 ? ShortLeadSteps : FullLeadSteps)
                foreach (double tw in G2TrackWeights)
                {
                    HoseClothoid.Result r = HoseClothoid.Fair(route, len, a0, lead0, a1, lead1, spans, kmax, tw, step);
                    // a heavier pull onto the route mostly helps a fit that strayed (into a wall, over a reel); an infeasible fit
                    // whose end stayed far off (ends and bend limits that disagree) is not retried: it is the costly kind
                    if (!r.Feasible) { why.Add("x" + tw + " " + r.Why); if (r.EndErr > G2RetryGap) break; continue; }
                    if (!Clear(w, r.Pts)) { why.Add("x" + tw + " touches a wall"); continue; }
                    if (Rig(r.Pts) > rig0) { why.Add("x" + tw + " crosses a reel"); continue; }
                    if (BodyRuleOn && BodyGap(w, r.Pts, sk, EndSkip) < gap0 - 1e-9) { why.Add("x" + tw + " body nearer a wall"); continue; }
                    return r.Pts;
                }
                return null;
            }
            List<V2> f = Fit(lay.Flat, rigF, gapF, L);
            List<V2> q = null;
            if (f == null)
            {
                string flatWhy = "flat pose: " + string.Join("; ", why);
                why.Clear();
                // step 4 (design s1, R4: re-route, never kink): the shaped route is too tight for the bend limits, so the hose is
                // re-laid along a wider guide; both poses take that one curve. A re-route is a choice, not a rescue, so its body
                // clears every wall by the full charged half-width (bh), never only as well as the shaped pose it replaces
                f = Reroute(w, lay, p, a0, lead0, a1, lead1, kmax, Math.Min(rigF, rigP), BodyRuleOn ? bh : 0, why, Fit, Rig);
                if (f == null) { lay.G2Why = flatWhy + " | re-route: " + (why.Count > 0 ? string.Join("; ", why) : "no guide"); return; }
                q = f;
                L = Geo.Length(f);
                lay.Rerouted = true;
            }
            else
            {
                why.Clear();
                L = fitLen;
                q = FitAt(lay.Plump, rigP, gapP, L, false);
                if (q == null || q.Count != f.Count) { lay.G2Why = "charged pose: " + string.Join("; ", why); return; }
            }
            double step = L / (f.Count - 1);
            lay.Flat = f;
            lay.Plump = q;
            lay.Centre = ResampleN(lay.Centre, f.Count);
            lay.Joints = js.Select(s => Math.Max(1, Math.Min(f.Count - 2, (int)Math.Round(s / step)))).ToList();
            lay.G2 = true;
            G2Done++;
        }

        /// <summary>Owner by card 2026-10-24 "Shorten the lead-out": the shortest straight run a nozzle's lead-out may shrink to.</summary>
        internal const double LeadOutMin = 0.6;
        /// <summary>The straight lead-out <paramref name="lay"/> was laid with: its own when the lead search shortened it, else
        /// <paramref name="p"/>'s.</summary>
        internal static double LeadOf(HoseLay lay, HoseShapeParams p) => lay.LeadShortened && lay.Lead0 > 0 ? lay.Lead0 : LeadOutStraight(p);
        /// <summary>The descending grid the lead search tries before bisecting (the full lead itself is tried by the caller).</summary>
        internal static readonly double[] LeadGrid = { 1.8, 1.4, 1.0, 0.6 };
        /// <summary>The bisection's resolution (cells).</summary>
        internal const double LeadTol = 0.05;
        /// <summary>Lays whose lead-out was shortened (selftest cost report).</summary>
        internal static long LeadShortened;
        /// <summary>Node spacings a fit tries (0 = HoseClothoid.NodeStep). A shortened lead marks a short span, whose few free
        /// curvature nodes the straight leads' node rounding eats; finer nodes give its end equalities room. Long hoses are
        /// fitted exactly as before.</summary>
        private static readonly double[] FullLeadSteps = { 0 }, ShortLeadSteps = { 0, 0.25 };
        /// <summary>Lengths a shortened-lead fit tries, as multiples of its route's (the slack and charged poses then share the
        /// one found, R6).</summary>
        internal static readonly double[] ShortLeadStretch = { 1.0, 0.97, 1.03, 0.94, 1.07 };

        /// <summary>The largest lead in [<see cref="LeadOutMin"/>, <paramref name="full"/>) for which <paramref name="fits"/> holds,
        /// to <see cref="LeadTol"/>: <see cref="LeadGrid"/> descending to the first that fits, then bisection between it and the
        /// grid lead above it (or <paramref name="full"/>, which the caller found does not fit). 0 when none fits. Deterministic;
        /// at most |grid| + 5 tries. The offline explorer (FlowWorks/Tools/hose_geometry_explore.py, largest_lead) is the same rule.</summary>
        internal static double LeadSearch(double full, Func<double, bool> fits)
        {
            double prev = full;
            foreach (double g in LeadGrid)
            {
                if (g >= full - 1e-9) continue;
                if (fits(g))
                {
                    double lo = g, hi = prev;
                    while (hi - lo > LeadTol + 1e-9)
                    {
                        double mid = Math.Round((lo + hi) / 2, 4);
                        if (fits(mid)) lo = mid; else hi = mid;
                    }
                    return lo;
                }
                prev = g;
            }
            return 0;
        }

        /// <summary>Guide radii for a re-route, as multiples of the fit's own limit 1/kmax: the clothoid ramps into and out of
        /// each arc need room the Dubins arc alone does not leave.</summary>
        private static readonly double[] RerouteRadii = { 1.15, 1.4, 1.8 };
        /// <summary>A free end's heading is tried as shaped and turned by these (degrees).</summary>
        private static readonly double[] RerouteFreeTurns = { 0, 30, -30, 60, -60 };
        /// <summary>At most this many guides are fitted per lay (an infeasible fit is the costly kind).</summary>
        internal static int RerouteMaxFits = 8;
        /// <summary>A guide longer than this multiple of the shaped route is a detour no one would lay (a loop round a reel).</summary>
        internal const double RerouteMaxDetour = 2.0;
        /// <summary>Lengths tried per guide, as multiples of the guide's own.</summary>
        private static readonly double[] RerouteStretch = { 1.0, 1.05, 1.12, 1.2, 1.3 };
        internal static long Rerouted;

        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 4: when the shaped route cannot carry a G2 curve (too tight a
        /// turn for R, or a U-turn whose fit stalls), guides are laid between the two lead ends as Dubins paths at radii wider than
        /// the fit's limit (every word, shortest first), and the hose is fitted to the first guide that stays clear, crosses no
        /// more reels, keeps the body clearance and is no longer than the hose. The guide's own length is the hose's laid
        /// length. Lays with joiners are not re-routed (their spans sit on the shaped route). Null when no guide fits.</summary>
        private static List<V2> Reroute(CordWorld w, HoseLay lay, HoseShapeParams p, V2? a0, double lead0, V2? a1, double lead1,
            double kmax, int rig0, double gap0, List<string> why, Func<List<V2>, int, double, double, List<V2>> fit, Func<List<V2>, int> rig)
        {
            if (lay.Joints.Count > 0) { why.Add("has joiners"); return null; }
            List<V2> P = lay.Flat;
            int n = P.Count;
            V2 A = P[0], B = P[n - 1];
            double[] s = Geo.CumLen(P);
            double Ls = s[n - 1];
            V2 Dir(double t0, double t1) => (At(P, s, t1) - At(P, s, t0)).Norm();
            V2 Turn(V2 v, double deg) { double c = Math.Cos(deg * Math.PI / 180), si = Math.Sin(deg * Math.PI / 180); return new V2(v.X * c - v.Z * si, v.X * si + v.Z * c); }
            double look = Math.Min(0.6, Ls / 4);
            V2 h0 = a0 ?? Dir(0, look), h1 = a1 ?? Dir(Ls - look, Ls);
            var guides = new List<(double len, List<V2> pts)>();
            foreach (double t0 in a0.HasValue ? new double[] { 0 } : RerouteFreeTurns)
                foreach (double t1 in a1.HasValue ? new double[] { 0 } : RerouteFreeTurns)
                {
                    V2 g0 = Turn(h0, t0), g1 = Turn(h1, t1);
                    V2 q0 = A + g0 * lead0, q1 = B - g1 * lead1;
                    foreach (double m in RerouteRadii)
                        foreach (List<V2> d in DubinsAll(q0, g0, q1, g1, m / kmax, Sample, true))
                        {
                            var g = new List<V2> { A };
                            if (lead0 > 0) g.Add(q0);
                            g.AddRange(d);
                            if (lead1 > 0) g.Add(B);
                            double len = Geo.Length(g);
                            // a guide is a lay a hand would make: clear, no loop, over no more reels, and no big detour
                            if (len > p.MaxLength || len > Ls * RerouteMaxDetour || SelfIntersects(g) || !Clear(w, g) || rig(g) > rig0) continue;
                            guides.Add((len, g));
                        }
                }
            int fits = 0;
            foreach (var g in guides.OrderBy(x => x.len))
            {
                if (fits++ >= RerouteMaxFits) { why.Add("fit budget spent"); break; }
                // the guide's own length first; a little more lets the ramps into its arcs drape where the bare length is tight
                foreach (double stretch in RerouteStretch)
                {
                    if (g.len * stretch > p.MaxLength) break;
                    List<V2> f = fit(g.pts, rig0, gap0, g.len * stretch);
                    if (f == null || SelfIntersects(f)) continue;
                    Rerouted++;
                    return f;
                }
            }
            if (guides.Count == 0) why.Add("no clear guide");
            return null;
        }

        /// <summary>Lays the G2 fit was tried on / held on (selftest cost report).</summary>
        internal static long G2Tried, G2Done;

        /// <summary>REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT: a DirectJoin plan laid as drawn (see LayOnce's <c>shaped</c>). The plan
        /// already runs straight out of the nozzle for LeadOutStraight cells, round at the minimum radius and straight into the
        /// end coupling, so flat, plump and centre are that one curve and the lead-out is its straight run.</summary>
        private static HoseLay LayShaped(CordWorld w, V2 a, V2 b, List<V2> planPoints, HoseShapeParams p, V2? endInward, V2? startOutward)
        {
            HashSet<Cell> planCells = CellsAlong(planPoints);
            int Rig(List<V2> pts) => RigHits(w, pts, planCells);
            List<V2> C = Geo.Resample(planPoints, Sample);
            C[0] = a;
            C[C.Count - 1] = b;
            if (!Clear(w, C)) return new HoseLay { Reason = "no clear route (corners too tight for the hose)" };
            var lay = new HoseLay { PathLen = Geo.Length(C), Flat = C, Plump = new List<V2>(C), Centre = new List<V2>(C) };
            if (startOutward.HasValue) { lay.Outlet = true; lay.LeadOutLen = LeadOutStraight(p); }
            return Finish(w, lay, p, Rig, endInward, startOutward);
        }

        /// <summary>The slack pose: a seeded sinusoid across the planned centreline, ramped to zero over 1.5 cells at
        /// each end, each point's offset shrunk until it sits clear of obstacles.</summary>
        internal static List<V2> SCurves(CordWorld w, List<V2> C, LayParams prm, CordRng rr, double maxExtra)
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

        /// <summary>How far a centreline point may graze into a wall cell (cells): a string-pulled line touching a wall
        /// corner exactly is not a clip; a hose centre 0.06 inside a wall is (the hose itself is ~0.4 wide).</summary>
        public const double ClipTolerance = 0.06;

        /// <summary>Depth of q inside the blocked ground (0 when its cell is walkable): the distance to the nearest WALKABLE cell
        /// box, i.e. -CordWorld.Clearance, the measure the Gimme Some Slack cords have always used. HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE
        /// (2026-10-22): from round 4 (9e9f153d4e) this was the distance to the edge of q's OWN cell, whatever lay across that
        /// edge, so a hose on the seam between two wall cells read ~0 and passed (the walkthrough's reel o1 drawn through walls
        /// (22,39)/(22,40) at z = 40.0). A corner or face graze of a walkable cell still reads ~0.</summary>
        internal static double WallDepth(CordWorld w, V2 q)
        {
            if (w.IsWalkable(q.Floor)) return 0;
            return -w.Clearance(q);
        }

        /// <summary>True when no part of the hose centreline lies over a blocked cell. Round 4 (owner, station 23): testing
        /// only the 0.25-cell samples let a stiffened hose cut the corner of a one-cell wall stub between two samples (his
        /// zig-zag maze measured 28 fine samples inside walls); every segment is now walked at 0.05 cell. The first and
        /// last 0.5 cell (endSkip in the overload below) are exempt (the reel and the free end may sit on a building's cell).</summary>
        internal static bool Clear(CordWorld w, IList<V2> pts) => Clear(w, pts, 0.5);

        /// <summary>HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS live instrument (HoseProbe census "wallCross", proof_hose.py HW1): a
        /// sample this deep inside blocked ground is the hose's own half-width through a wall, a crossing, not a graze.</summary>
        public const double WallCrossDepth = 0.12;

        /// <summary>Samples (every 0.05 cell, the first and last 0.5 cell skipped as in Clear) deeper than WallCrossDepth inside
        /// blocked ground; <paramref name="first"/> is the first one's cell.</summary>
        internal static int WallCrossings(CordWorld w, IList<V2> pts, out Cell first)
        {
            first = default;
            int hits = 0;
            if (pts == null || pts.Count < 2) return 0;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            for (int i = 1; i < pts.Count; i++)
            {
                double d = s[i] - s[i - 1];
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.05));
                for (int j = 0; j < k; j++)
                {
                    double at = s[i - 1] + d * j / k;
                    if (at < 0.5 || L - at < 0.5) continue;
                    V2 q = pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k);
                    if (WallDepth(w, q) > WallCrossDepth) { if (hits == 0) first = q.Floor; hits++; }
                }
            }
            return hits;
        }

        /// <summary>HOSE_BEND_FIX_SHAVES_WALL_CORNERS (BENCH live round 2, save d map C: a hose bent round a one-cell wall's end
        /// shaved its corner). <see cref="Clear"/> judges the CENTRELINE and lets it graze a wall corner by ClipTolerance, so a bend
        /// wrapped tight round a corner drew half the hose's width over the wall. The drawn body is the centreline +- this much
        /// (half the widest drawn hose, plump at full blend, plus a hair); a shaping stage prefers a pose whose
        /// <see cref="BodyGap"/> is at least this, and keeps the old centreline rule only when no such pose exists.</summary>
        public static double BodyHalf(double plumpAmount) => 0.5 * VisibleWidth(1, plumpAmount) + BodyMargin;
        public const double BodyMargin = 0.01;
        /// <summary>The body rule on (shipped) / off (the selftest's can-fail run only: off lays exactly as before the fix).</summary>
        internal static bool BodyRuleOn = true;

        /// <summary>Least clearance (<see cref="CordWorld.Clearance"/>: distance to the nearest unwalkable cell) of the polyline,
        /// sampled every 0.05 cell, ignoring the first <paramref name="startSkip"/> and the last <paramref name="endSkip"/> cells
        /// (the nozzle's straight run and the end fitting sit against their own buildings).</summary>
        internal static double BodyGap(CordWorld w, IList<V2> pts, double startSkip, double endSkip)
        {
            double best = 99;
            if (w == null || pts == null || pts.Count < 2) return best;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            for (int i = 1; i < pts.Count; i++)
            {
                double d = s[i] - s[i - 1];
                int k = Math.Max(1, (int)Math.Ceiling(d / 0.05));
                for (int j = 0; j <= k; j++)
                {
                    double at = s[i - 1] + d * j / k;
                    if (at < startSkip || L - at < endSkip) continue;
                    best = Math.Min(best, w.Clearance(pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k)));
                }
            }
            return best;
        }

        internal static bool Clear(CordWorld w, IList<V2> pts, double endSkip)
        {
            if (pts.Count < 2) return true;
            LayScratch ls = LayScratch.Get();
            double[] s = LayScratch.CumOf(pts, ref ls.ClearCum);
            double L = s[pts.Count - 1];
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
                    // PIPE_POLES phase 6 (design §P5): the hose never drops down (or climbs) a sheer wall between bands; it
                    // crosses only a ramp or ladder link. Ends included: an end's own half cell is never on another band.
                    if (!w.StepAllowed(prev, c)) return false;
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
        internal static List<V2> Stiffen(CordWorld w, List<V2> X0, double minR)
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
        internal static List<V2> ResampleN(IList<V2> p, int n) => ResampleNInto(p, n, new List<V2>(n));

        /// <summary>ResampleN into <paramref name="o"/> (cleared first; returned).</summary>
        internal static List<V2> ResampleNInto(IList<V2> p, int n, List<V2> o)
        {
            LayScratch ls = LayScratch.Get();
            double[] s = LayScratch.CumOf(p, ref ls.Cum);
            double L = s[p.Count - 1];
            o.Clear();
            int j = 0;
            for (int i = 0; i < n; i++)
            {
                double t = L * i / (n - 1);
                while (j < p.Count - 2 && s[j + 1] < t) j++;
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
        internal static List<V2> Pose(HoseLay lay, double e, int ticksSinceChange, int transitionTicks, double plumpAmount)
        {
            int n = lay.Flat.Count;
            var o = new List<V2>(n);
            for (int i = 0; i < n; i++) o.Add(lay.Flat[i] + (lay.Plump[i] - lay.Flat[i]) * e);
            // a lay whose lead-out was shortened is a span at its bend limit: it has no room to wobble (step 6)
            if (!WobbleActive(ticksSinceChange, transitionTicks) || plumpAmount <= 0 || lay.LeadShortened) return o;
            var w = new List<V2>(n);
            // HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: on a G2 lay the wobble is off over the straight runs at the ends and fades in
            // by a smootherstep over a cell (its offset, slope and curvature all start at zero), so it never bends a lead
            double[] sm = lay.G2 ? Geo.CumLen(o) : null;
            double Lm = lay.G2 ? sm[n - 1] : 0;
            for (int i = 0; i < n; i++)
            {
                Geo.TanNorm(o, i, out V2 t, out V2 nn);
                double env = 1;
                if (lay.G2) env = SmootherStep(sm[i] - lay.Lead0 - 0.25) * SmootherStep(Lm - sm[i] - lay.Lead1 - 0.25);
                w.Add(o[i] + nn * (env * Wobble(i / (double)(n - 1), ticksSinceChange, transitionTicks, plumpAmount)));
            }
            return w;
        }

        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: the centreline DrawAll meshes for a laid hose (before a mate and the
        /// outlet trim), Verse-free so HoseCurveChecks measures the production draw path. <paramref name="portAt"/> = the tank
        /// port the free end couples to (null = none), <paramref name="portAxis"/> = the step from the end cell into the tank.</summary>
        internal static List<V2> DrawnPose(HoseLay lay, double e, int ticksSinceChange, int transitionTicks, double plumpAmount,
            V2? portAt, V2 portAxis)
        {
            List<V2> pts = Pose(lay, e, ticksSinceChange, transitionTicks, plumpAmount);
            if (!portAt.HasValue) return pts;
            // HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 3: EnsureLay lays a tank-port end onto the port (endInward = its axis),
            // so the hose already arrives there dead straight; re-shaping it here would only bend what the lay got right
            if (OnPortAxis(pts, portAt.Value - portAxis * 0.5, portAxis)) return pts;
            // HOSE_LEADIN_FIX_STUB_IN_THE_CANAL: a hose that meets the port from the side is not re-aimed (the Hermite would loop
            // back behind the end); DrawEnds gives it an elbow fitting instead (HoseMath.PortFitting)
            if (!SideArrival(pts, portAxis))
            {
                // HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS: the last few cells re-laid as a clothoid chain of the same length that
                // arrives dead straight along the port axis, joined to the kept hose in position, heading and curvature
                if (G2On)
                {
                    List<V2> g = HoseClothoid.TailOnto(pts, portAt.Value - portAxis * 0.5, portAxis.Norm(), HoseRelay.EndStraight,
                        lay.Kmax * G2KappaMargin, lay.Lead0, out _);
                    if (g != null) return g;
                }
                return EndOnPort(pts, portAt.Value - portAxis * 0.5, portAxis, 1.2);
            }
            // HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT: a side arrival keeps its heading but slides onto a moved port
            return SlideEndOnto(pts, portAt.Value, portAxis);
        }

        /// <summary>HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 3 (EnsureLay and HoseCurveChecks alike): a free end coupled to a tank
        /// port is laid onto the port itself -- ending half a cell out from the flange (<paramref name="portAt"/> - axis x 0.5),
        /// its last EndStraight dead straight along <paramref name="portAxis"/> -- so the clothoid fit owns the arrival. When that
        /// lay is refused or no G2 curve fits it (a run too short for the lead-out, the port and the bend radius together), the
        /// end is laid as before, to <paramref name="cellEnd"/> with a free heading, and DrawnPose bends it onto the port.
        /// Step 4: <paramref name="bodyHit"/> (null = not checked) says where a candidate lay, as drawn, runs through its own
        /// reel or the fixture (<see cref="BodyHit"/>); a lay drawn through either is never returned -- when both candidates
        /// are, the lay is refused with <see cref="BodyInTheWay"/>. <paramref name="layTo"/> lays to (end, endInward).</summary>
        internal static HoseLay PortLay(Func<V2, V2?, HoseLay> layTo, V2 cellEnd, V2? inward, V2? portAt, V2 portAxis,
            Func<HoseLay, string> bodyHit = null)
        {
            if (!portAt.HasValue) return layTo(cellEnd, inward);
            V2 ax = portAxis.Norm();
            HoseLay onPort = layTo(portAt.Value - ax * 0.5, ax);
            string hitOn = onPort.Ok && bodyHit != null ? bodyHit(onPort) : null;
            bool onOk = onPort.Ok && hitOn == null;
            if (onOk && (onPort.G2 || !G2On)) return onPort;
            HoseLay old = layTo(cellEnd, inward);
            string hitOld = old.Ok && bodyHit != null ? bodyHit(old) : null;
            if (old.Ok && hitOld == null)
            {
                old.PortWhy = onPort.Ok ? (hitOn != null ? "onto the port axis " + hitOn : "no G2 curve onto the port axis: " + onPort.G2Why)
                    : "refused onto the port axis: " + onPort.Reason;
                return old;
            }
            if (onOk) return onPort;
            if (hitOn != null || hitOld != null)
            {
                BodyRefused++;
                return new HoseLay { Reason = BodyInTheWay, PortWhy = hitOld ?? hitOn, PathLen = old.Ok ? old.PathLen : onPort.PathLen };
            }
            if (onPort.Ok) return onPort;
            // both refused: the port's own reason when it is that no curve bends onto the port (step 5), else the cell lay's
            return onPort.Reason == TooCloseToBend ? onPort : old;
        }

        /// <summary>Why a port lay was refused (step 4): every lay that reaches the port is drawn through the reel or the tank.</summary>
        public const string BodyInTheWay = "The hose would run through the reel or the tank \u2014 move the reel back";
        /// <summary>Lays refused with <see cref="BodyInTheWay"/> since load (the selftest's cost line).</summary>
        internal static int BodyRefused;
        /// <summary>The first stretch of the drawn hose that may lie on its own reel: the mouth sits up to 0.31 inside the reel's
        /// rect (HoseReelRect.Mouth, N facing) and the lead-out leaves it along the nozzle.</summary>
        internal const double OwnReelMouthRun = 0.5;

        /// <summary>Step 4: where <paramref name="lay"/>, drawn steady flat and charged (DrawnPose, the port end bent on as
        /// DrawAll does), runs with its centreline more than 0.02 inside its own reel (past <see cref="OwnReelMouthRun"/>)
        /// or the fixture's footprint (cells x0..x0+w, z0..z0+h); null = clear of both.</summary>
        internal static string BodyHit(HoseLay lay, V2? portAt, V2 portAxis, HoseReelRect reel, int x0, int z0, int w, int h)
        {
            const double inset = 0.02;
            bool In(V2 q, double a0, double b0, double a1, double b1) => q.X > a0 + inset && q.X < a1 - inset && q.Z > b0 + inset && q.Z < b1 - inset;
            foreach (double e in new[] { 0.0, 1.0 })
            {
                List<V2> pts = DrawnPose(lay, e, int.MaxValue / 2, 1, 0, portAt, portAxis);
                double s = 0;
                for (int i = 0; i < pts.Count; i++)
                {
                    if (i > 0) s += V2.Dist(pts[i - 1], pts[i]);
                    if (s > OwnReelMouthRun && In(pts[i], reel.X0, reel.Z0, reel.X0 + reel.W, reel.Z0 + reel.H)) return (e == 0 ? "flat" : "charged") + " through the reel";
                    if (In(pts[i], x0, z0, x0 + w, z0 + h)) return (e == 0 ? "flat" : "charged") + " through the tank";
                }
            }
            return null;
        }

        /// <summary>True when pts ends on <paramref name="end"/> (within 0.02 cell) and its last EndStraight runs along
        /// <paramref name="axis"/> (within 1 degree): the lay already meets the port, nothing to re-aim.</summary>
        internal static bool OnPortAxis(IList<V2> pts, V2 end, V2 axis)
        {
            int n = pts.Count;
            if (n < 2 || V2.Dist(pts[n - 1], end) > 0.02) return false;
            V2 u = axis.Norm();
            V2 back = PointBack(pts, HoseRelay.EndStraight);
            V2 d = pts[n - 1] - back;
            double len = d.Len;
            if (len < 1e-6) return false;
            double cos = (d.X * u.X + d.Z * u.Z) / len;
            return cos > Math.Cos(Math.PI / 180);
        }

        /// <summary>Smallest discrete bend radius (segment / turning angle) over points more than skip cells from either end.</summary>
        internal static double MinBendRadius(IList<V2> X, double skip)
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
        internal static bool SelfIntersects(IList<V2> X)
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
        internal static double TurnAt(IList<V2> C, double[] s, int i, double half = 1.0)
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
        internal static List<int> Joints(IList<V2> C, double minSpacing) => Joints(C, minSpacing, 0);

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
        internal static List<int> Joints(IList<V2> C, double minSpacing, double half, params IList<V2>[] drawn)
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
        internal static double RunTurn(IList<V2> C, double[] s, double a, double b)
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

        /// <summary>Round 7: the last <paramref name="straight"/> cells of P laid on the line into <paramref name="end"/> along
        /// <paramref name="inward"/> (blended back over 0.5 cell), the end exactly at <paramref name="end"/>.</summary>
        internal static List<V2> StraightenEnd(IList<V2> P, V2 end, V2 inward, double straight, double blend = 0.5)
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
        internal static List<V2> StraightenStart(IList<V2> P, V2 start, V2 outward, double straight, double blend = 0.5)
        {
            var r = new List<V2>(P);
            r.Reverse();
            List<V2> o = StraightenEnd(r, start, outward * -1, straight, blend);
            o.Reverse();
            return o;
        }

        /// <summary>The point <paramref name="back"/> cells of arc before P's last point (interpolated).</summary>
        internal static V2 PointBack(IList<V2> P, double back)
        {
            double[] s = Geo.CumLen(P);
            return At(P, s, Math.Max(0, s[s.Length - 1] - back));
        }

        /// <summary>The pose with the run [s_j - half, s_j + half] laid on its chord (equal-arc along it), blended back into
        /// the hose over 0.5 cell either side, so the joiner's rigid brass and the hose under it share one axis.</summary>
        internal static List<V2> StraightenAt(IList<V2> P, int j, double half)
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
        internal static List<V2> TrimStart(IList<V2> P, double cut)
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

        /// <summary>An open free end's wrap runs this far (cell) past the hose's cut, hiding its square end.</summary>
        public const double WrapOverCut = 0.02;

        /// <summary>HOSE_MOUTH_FIX_FACE_ON_DISC (art brief C6: a hose lying flat never shows its opening to the camera): the
        /// open free end's Mouth piece drawn EDGE-ON, a lip line <paramref name="along"/> deep and <paramref name="across"/>
        /// wide whose outer edge is the wrap's outer face; <paramref name="back"/> = its centre's distance behind the cut.
        /// Was a 0.30 x 0.86 squashed disc that read as the end turned up at the camera.</summary>
        public static void OpenEndLip(double visible, out double along, out double across, out double back)
        {
            across = 0.86 * visible;
            along = 0.08 * visible;
            back = along / 2 - WrapOverCut;
        }

        /// <summary>Draw size of a fitting (canvas cells) on a hose of <paramref name="visible"/> width: matched to the hose
        /// by its hose band, but never so big that its widest part (<paramref name="maxBand"/>, canvas fraction) reads
        /// wider than 0.95 x the wrap (B22: "the fitting must not look wider than the wrap").</summary>
        public static double FittingSize(double visible, double hoseBand, double maxBand) =>
            Math.Min(visible / hoseBand, 0.95 * WrapWidth(visible) / maxBand);

        /// <summary>A joiner is TWO couplings face to face, each on its own length, so it reads as two lengths screwed
        /// tightly together (B9), never as one hose end lying across another. Centres of the forward piece (pointing
        /// along +d) and the backward piece (pointing along -d) for a joint at J; the brass faces meet at J.</summary>
        internal static void JoinerPoses(V2 J, V2 d, double size, double face, out V2 forward, out V2 backward)
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

        // ---------------------------------------------------------------- install validity
        /// <summary>Null when a hose may be laid from the reel cell to target, else the reason. maxLength is the
        /// hose's length (cells): the straight distance and the planned route must both fit it.</summary>
        internal static string CheckInstall(CordWorld w, Cell reel, Cell target, double maxLength) =>
            CheckInstall(w, new HoseReelRect(reel.X, reel.Z, 1, 1), target, maxLength);

        /// <summary>Any reel footprint (round 3: the reel is 2x2). Distances run from the reel's MOUTH (where the hose
        /// leaves it); the route is A* from the reel cell nearest the target, pulled taut from the mouth (RoutePulled).</summary>
        internal static string CheckInstall(CordWorld w, HoseReelRect reel, Cell target, double maxLength)
        {
            if (!w.InBounds(target)) return "out of bounds";
            if (reel.Contains(target)) return "same cell";
            // HOSE_LAY_POLISH_CENTRE_VS_MOUTH (C8a-F4): the route starts at the MOUTH, so the straight distance from there is its
            // lower bound; measuring from the centre refused a just-in-range target on the mouth side as "too far"
            if (V2.Dist(reel.Mouth, target.Centre) > maxLength) return "too far";
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
        internal static double RouteLength(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1, bool costs = true)
        {
            List<V2> p = RoutePulled(w, reel, target, maxLength, costs);
            return p == null ? -1 : Geo.Length(p);
        }

        internal static List<V2> RoutePulled(CordWorld w, HoseReelRect reel, Cell target, double maxLength = -1, bool costs = true)
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

        /// <summary>State read: cells the last RouteCells ON THIS THREAD expanded, and whether it ran out of budget. Per thread
        /// and written only when the search returns (review 2026-10-26, HOSE_ROUTE_FIX_THREAD_BUDGET): the budget itself is a
        /// local -- a shared counter let a lay worker's search (HoseLayQueue) spend the main thread's CheckReplan budget.</summary>
        [ThreadStatic] public static int LastRouteExpanded;
        [ThreadStatic] public static bool LastRouteCapped;

        /// <summary>The hose's own route search (round 5). Round 4 used the cord planner's A* with a flat 20000-expansion cap,
        /// which is no bound on length at all: on a big open map a hard route spent it and read as "no route". This is the
        /// same A* (8-way, no corner cutting, ExtraCost for water and trees) with the search bounded by LENGTH: a node
        /// whose path length plus straight-line remainder exceeds lengthBound is never opened, so every route within the
        /// bound is found and the search never leaves the (2 x bound + 1)^2 square round the reel. lengthBound &lt;= 0 =
        /// unbounded, capped at RouteMaxExpand.</summary>
        internal static List<Cell> RouteCells(CordWorld w, Cell start, Cell goal, double lengthBound, bool costs = true)
        {
            LastRouteExpanded = 0;
            LastRouteCapped = false;
            int expanded = 0;
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
                    LastRouteExpanded = expanded;
                    return path;
                }
                if (top.g > g[c] + 1e-12) continue;
                if (++expanded > cap) { LastRouteExpanded = expanded; LastRouteCapped = true; return null; }
                foreach (Cell d in Cell.Dirs8)
                {
                    Cell q = c + d;
                    if (!w.InBounds(q) || !Ok(q)) continue;
                    if (d.X != 0 && d.Z != 0 && !(Ok(new Cell(c.X + d.X, c.Z)) && Ok(new Cell(c.X, c.Z + d.Z)))) continue;
                    // PIPE_POLES phase 6 (design §P5): into or out of a dug square only across a ramp or ladder link
                    if (!w.StepAllowed(c, q)) continue;
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
            LastRouteExpanded = expanded;
            return null;
        }

        /// <summary>True when the straight segment a-b stays out of walls (ClipTolerance) and never slips through a
        /// pinched diagonal (two wall cells meeting corner to corner).</summary>
        internal static bool SegmentClear(CordWorld w, V2 a, V2 b) => Clear(w, new List<V2> { a, b }, 0);

        /// <summary>HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE (owner 2026-10-17, water scene S3: "It should prefer to NOT pass
        /// through the reel but go around on the bare ground"). The extra route cost of a cell holding the hose rig's own
        /// machinery (a hose reel or a pump: PassThroughOnly, so the path grid calls it walkable). Before this the hose world
        /// costed such a cell 0, so a hose leaving a reel's west nozzle for a target to the east U-turned straight back over
        /// its own drum. Two reel cells at this cost (12) outweigh any detour round a 2x2 footprint, so the planner goes
        /// round; it is a cost, not a block, so a hose with no other way still crosses. Above water (3) and trees (1.5), so
        /// <see cref="SegmentAvoidsBuildings"/> can tell a building cell from those by cost alone.</summary>
        public const float BuildingCrossCost = 6f;

        /// <summary>The cells a polyline passes through (sampled every 0.05 cell).</summary>
        internal static HashSet<Cell> CellsAlong(IList<V2> pts)
        {
            var cells = new HashSet<Cell>();
            if (pts.Count > 0) cells.Add(pts[0].Floor);
            for (int i = 1; i < pts.Count; i++)
            {
                int k = Math.Max(1, (int)Math.Ceiling(V2.Dist(pts[i - 1], pts[i]) / 0.05));
                for (int j = 0; j <= k; j++) cells.Add((pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k)).Floor);
            }
            return cells;
        }

        /// <summary>How many distinct reel/pump cells (cost &gt;= <see cref="BuildingCrossCost"/>) a hose pose enters that are
        /// not in <paramref name="allowed"/> (the plan's own cells). 0 in any world with no reel or pump near the hose.</summary>
        internal static int RigHits(CordWorld w, IList<V2> pts, HashSet<Cell> allowed)
        {
            // HOSE_LAY_FIX_GARBAGE_FORCES_FULL_GC: walks the same 0.05-cell samples CellsAlong takes into this thread's
            // reused set (a fresh CellsAlong set per call was ~0.5 MB a lay: 158 calls)
            HashSet<Cell> hit = rigHitScratch ?? (rigHitScratch = new HashSet<Cell>());
            hit.Clear();
            void Try(Cell c) { if (!allowed.Contains(c) && w.ExtraCost(c) >= BuildingCrossCost) hit.Add(c); }
            if (pts.Count > 0) Try(pts[0].Floor);
            for (int i = 1; i < pts.Count; i++)
            {
                int k = Math.Max(1, (int)Math.Ceiling(V2.Dist(pts[i - 1], pts[i]) / 0.05));
                for (int j = 0; j <= k; j++) Try((pts[i - 1] + (pts[i] - pts[i - 1]) * (j / (double)k)).Floor);
            }
            int n = hit.Count;
            hit.Clear();
            return n;
        }
        [ThreadStatic] private static HashSet<Cell> rigHitScratch;

        /// <summary>True when the straight segment a-b enters no building-costed cell (<see cref="BuildingCrossCost"/>) other
        /// than those in <paramref name="allowed"/> (a walked trail's own cells) and the two end cells. The any-angle pulls
        /// (HoseTrail.Pulled, LayAlong's lead-out hop) use it so a taut shortcut never cuts back across a reel the route went
        /// round: the same rule CordPlanner's string-pull applies to every costed cell (GSS pre-release A5).</summary>
        internal static bool SegmentAvoidsBuildings(CordWorld w, V2 a, V2 b, ICollection<Cell> allowed = null)
        {
            Cell ca = a.Floor, cb = b.Floor;
            int n = (int)(V2.Dist(a, b) / 0.05) + 2;
            for (int i = 0; i < n; i++)
            {
                Cell c = (a + (b - a) * (i / (double)(n - 1))).Floor;
                if (c == ca || c == cb || (allowed != null && allowed.Contains(c))) continue;
                if (w.ExtraCost(c) >= BuildingCrossCost) return false;
            }
            return true;
        }

        /// <summary>HOSE_BLOCKED_REROUTE_RETRACT_1 (owner, by card 2026-10-04: "reroute within its length; if none exists,
        /// retract to the reel with a visible alert. Never a ghost hose; also enforce length on re-plan."). Run when an
        /// obstacle changes a laid hose's corridor, or its lay failed: null = keep it laid (re-route), else the reason it
        /// must be reeled in. The SAME test as installing, so a re-plan can never keep a hose install would refuse.
        /// layFailed: the planner could not lay a hose the route check passed -- also retracted, never left invisible.</summary>
        internal static string CheckReplan(CordWorld w, HoseReelRect reel, Cell target, double maxLength, bool layFailed, string layReason)
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
        public static Layering Layer(IList<LayeredHose> hoses, double visible) => Layer(hoses, visible, null);

        /// <summary>
        /// HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP (live round 5, 2026-10-26): <see cref="Layer(IList{LayeredHose}, double)"/> was
        /// all pairs with no broad phase, and every pair re-summed both strands (Geo.CumLen, two arrays a variant) before testing
        /// a footprint sample against every segment of the other hose. RM_MapComponent_Hoses.Layered rebuilds it whenever ANY
        /// reel's lay object changes, so on the 325 basin map (200 hoses) every frame of a re-lay wave paid a full rebuild inside
        /// DrawAll -- the ~1 s mean / 5.9 s max DrawAll that the lay queue had moved the lays themselves off.
        /// Same result, bit for bit (HoseLayerChecks HL1 against the old body, kept there as the oracle):
        ///  1. each lay's strands, arc sums and box are made once (<see cref="LayerCache"/>: once per lay OBJECT, kept across
        ///     rebuilds while the lay is still some hose's);
        ///  2. a pair whose boxes (grown by the fitting reach) do not meet has no fitting on the other: it is not tested;
        ///  3. a pair's facts (an end fitting on the other's body; which joiners sit over it) depend on the two lays only, so a
        ///     rebuild re-tests only pairs with a lay it has not seen (a re-lay wave tests ~ changed x overlapping);
        ///  4. the order (reel id, end fittings first, cycles broken at the lowest id) and the joiner pass are unchanged.
        /// A visible-width change (the plump setting) empties the cache. Main thread only; the cache is the caller's.
        /// </summary>
        public static Layering Layer(IList<LayeredHose> hoses, double visible, LayerCache cache)
        {
            cache = cache ?? new LayerCache();
            cache.Begin(visible);
            var res = new Layering();
            int n = hoses.Count;
            var g = new LayerGeom[n];
            for (int i = 0; i < n; i++) g[i] = cache.Geom(hoses[i].Lay);
            // facts[i] = (j, facts of i's fittings on j) for every j whose box meets i's
            var near = new List<KeyValuePair<int, LayerPair>>[n];
            var mustPrecede = new List<int>[n];
            var indeg = new int[n];
            for (int i = 0; i < n; i++) mustPrecede[i] = new List<int>();
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                {
                    if (i == j || !g[i].Meets(g[j], cache.Reach)) continue;
                    LayerPair f = cache.Pair(g[i], g[j]);
                    (near[i] ?? (near[i] = new List<KeyValuePair<int, LayerPair>>())).Add(new KeyValuePair<int, LayerPair>(j, f));
                    if (f.EndOn) { mustPrecede[i].Add(j); indeg[j]++; }
                }
            var placed = new bool[n];
            var rank = new int[n];
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
            // the rank a hose's joiners are judged at: the dictionary's (a repeated id keeps its last rank, as the old body read it)
            for (int i = 0; i < n; i++) rank[i] = res.Rank[hoses[i].Id];
            for (int i = 0; i < n; i++)
            {
                HoseLay lay = hoses[i].Lay;
                var keep = new List<int>();
                foreach (int jt in lay.Joints)
                {
                    bool over = false;
                    if (near[i] != null)
                        foreach (KeyValuePair<int, LayerPair> kv in near[i])
                            if (rank[kv.Key] < rank[i] && kv.Value.JointsOver != null && kv.Value.JointsOver.Contains(jt)) { over = true; break; }
                    if (!over) keep.Add(jt);
                }
                res.Joints[hoses[i].Id] = keep;
            }
            cache.End();
            return res;
        }

        /// <summary>One lay as <see cref="Layer(IList{LayeredHose}, double, LayerCache)"/> reads it: its strands (null = fewer
        /// than 2 points, never tested), their arc sums (Geo.CumLen, as the old body summed them) and one box over both.</summary>
        public sealed class LayerGeom
        {
            internal HoseLay Lay;
            internal int Id;
            internal int Used;
            internal List<V2> Flat, Plump;
            internal double[] SFlat, SPlump;
            internal double FlatLen;
            internal double X0 = double.PositiveInfinity, Z0 = double.PositiveInfinity, X1 = double.NegativeInfinity, Z1 = double.NegativeInfinity;

            internal LayerGeom(HoseLay lay, int id)
            {
                Lay = lay;
                Id = id;
                seenFlat = lay.Flat; seenPlump = lay.Plump; seenJoints = lay.Joints;
                nFlat = lay.Flat?.Count ?? -1; nPlump = lay.Plump?.Count ?? -1; nJoints = lay.Joints?.Count ?? -1;
                if (lay.Flat != null && lay.Flat.Count >= 2) { Flat = lay.Flat; SFlat = Geo.CumLen(Flat); FlatLen = Geo.Length(Flat); Grow(Flat); }
                if (lay.Plump != null && lay.Plump.Count >= 2) { Plump = lay.Plump; SPlump = Geo.CumLen(Plump); Grow(Plump); }
            }

            private readonly List<V2> seenFlat, seenPlump;
            private readonly List<int> seenJoints;
            private readonly int nFlat, nPlump, nJoints;

            /// <summary>The lay still holds the lists this was built from, at the same lengths (landed lays are never edited; a
            /// lay that was is re-read rather than trusted).</summary>
            internal bool Current =>
                ReferenceEquals(Lay.Flat, seenFlat) && ReferenceEquals(Lay.Plump, seenPlump) && ReferenceEquals(Lay.Joints, seenJoints)
                && (Lay.Flat?.Count ?? -1) == nFlat && (Lay.Plump?.Count ?? -1) == nPlump && (Lay.Joints?.Count ?? -1) == nJoints;

            // a NaN coordinate never widens the box: no distance to a NaN point is below anything (the old test was false too)
            private void Grow(List<V2> p)
            {
                foreach (V2 v in p)
                {
                    if (v.X < X0) X0 = v.X;
                    if (v.X > X1) X1 = v.X;
                    if (v.Z < Z0) Z0 = v.Z;
                    if (v.Z > Z1) Z1 = v.Z;
                }
            }

            /// <summary>The two boxes, this one grown by <paramref name="reach"/>, overlap (false = provably no fitting of one on
            /// the other: every sample is in its box, every segment in the other's).</summary>
            internal bool Meets(LayerGeom o, double reach) =>
                X0 - reach <= o.X1 && o.X0 <= X1 + reach && Z0 - reach <= o.Z1 && o.Z0 <= Z1 + reach;
        }

        /// <summary>What lay A's fittings do over lay B's body: an end fitting rests on it; these joiner samples sit over it.</summary>
        public sealed class LayerPair
        {
            internal bool EndOn;
            internal HashSet<int> JointsOver;
            internal int Used;
        }

        /// <summary>Per-lay geometry and per-pair facts kept between <see cref="Layer(IList{LayeredHose}, double, LayerCache)"/>
        /// rebuilds; an entry no rebuild used is dropped at the rebuild's end. Probe counters: pairs tested, pairs reused.</summary>
        public sealed class LayerCache
        {
            private readonly Dictionary<HoseLay, LayerGeom> geoms = new Dictionary<HoseLay, LayerGeom>();
            private readonly Dictionary<long, LayerPair> pairs = new Dictionary<long, LayerPair>();
            private double visible = double.NaN;
            private int nextId, pass;
            internal double Reach, Half;
            public long PairsTested, PairsReused, Rebuilds, EndsOn, JointsOver;
            public int GeomCount => geoms.Count;
            public int PairCount => pairs.Count;

            internal void Begin(double vis)
            {
                // the margin covers rounding in SegDist's foot point (a box test must never reject a pair the exact test keeps)
                if (!(vis == visible)) { geoms.Clear(); pairs.Clear(); visible = vis; }
                Reach = 0.5 * WrapWidth(vis) + 0.5 * vis + 1e-6;
                Half = JoinerHalf(vis);
                pass++;
                Rebuilds++;
            }

            internal LayerGeom Geom(HoseLay lay)
            {
                if (!geoms.TryGetValue(lay, out LayerGeom g) || !g.Current) geoms[lay] = g = new LayerGeom(lay, nextId++);
                g.Used = pass;
                return g;
            }

            internal LayerPair Pair(LayerGeom a, LayerGeom b)
            {
                long k = ((long)a.Id << 32) | (uint)b.Id;
                if (pairs.TryGetValue(k, out LayerPair f)) { PairsReused++; f.Used = pass; return f; }
                PairsTested++;
                f = new LayerPair { Used = pass };
                double vis = visible;
                f.EndOn = EndFittingOnG(a, true, b, vis, Half) || EndFittingOnG(a, false, b, vis, Half);
                foreach (int jt in a.Lay.Joints)
                    if (JointFittingOnG(a, jt, b, vis, Half)) (f.JointsOver ?? (f.JointsOver = new HashSet<int>())).Add(jt);
                if (f.EndOn) EndsOn++;
                if (f.JointsOver != null) JointsOver += f.JointsOver.Count;
                pairs[k] = f;
                return f;
            }

            /// <summary>Entries this rebuild did not use belong to lays no hose has any more.</summary>
            internal void End()
            {
                List<HoseLay> goneG = null;
                foreach (var kv in geoms) if (kv.Value.Used != pass) (goneG ?? (goneG = new List<HoseLay>())).Add(kv.Key);
                if (goneG != null) foreach (HoseLay l in goneG) geoms.Remove(l);
                List<long> goneP = null;
                foreach (var kv in pairs) if (kv.Value.Used != pass) (goneP ?? (goneP = new List<long>())).Add(kv.Key);
                if (goneP != null) foreach (long k in goneP) pairs.Remove(k);
            }
        }

        // the old FootprintOn / EndFittingOn / JointFittingOn over a LayerGeom: the same samples, sums and tests, made once
        private static bool FootprintOnG(LayerGeom a, double lo, double hi, LayerGeom b, double visible)
        {
            double reach = 0.5 * WrapWidth(visible) + 0.5 * visible, skip = JoinerHalf(visible);
            for (int v = 0; v < 2; v++)
            {
                bool plump = v == 1;
                List<V2> P = plump ? a.Plump : a.Flat, Q = plump ? b.Plump : b.Flat;
                if (P == null || Q == null) continue;
                double[] sp = plump ? a.SPlump : a.SFlat, sq = plump ? b.SPlump : b.SFlat;
                double Lq = sq[sq.Length - 1];
                for (int k = 0; k < P.Count; k++)
                {
                    if (sp[k] < lo || sp[k] > hi) continue;
                    V2 p = P[k];
                    // a sample outside the other strand's box by more than the reach is no nearer any of its segments
                    if (p.X + reach < b.X0 - 1e-6 || p.X - reach > b.X1 + 1e-6 || p.Z + reach < b.Z0 - 1e-6 || p.Z - reach > b.Z1 + 1e-6) continue;
                    for (int m = 0; m + 1 < Q.Count; m++)
                    {
                        if (sq[m + 1] < skip || sq[m] > Lq - skip) continue;
                        if (SegDist(p, Q[m], Q[m + 1]) < reach) return true;
                    }
                }
            }
            return false;
        }

        private static bool EndFittingOnG(LayerGeom a, bool start, LayerGeom b, double visible, double h)
        {
            if (a.Flat == null) return false;
            double L = a.FlatLen;
            return start ? FootprintOnG(a, 0, h, b, visible) : FootprintOnG(a, L - h, L, b, visible);
        }

        private static bool JointFittingOnG(LayerGeom a, int jt, LayerGeom b, double visible, double h)
        {
            if (a.Flat == null || jt < 0 || jt >= a.Flat.Count) return false;
            double s = a.SFlat[jt];
            return FootprintOnG(a, s - h, s + h, b, visible);
        }

        /// <summary>The pre-2026-10-26 body of <see cref="Layer(IList{LayeredHose}, double)"/>: all pairs, every strand re-summed
        /// per pair. Kept for RM_MapComponent_Hoses.FrameLegacy (the live A/B) and as HoseLayerChecks' oracle.</summary>
        internal static Layering LayerAllPairs(IList<LayeredHose> hoses, double visible)
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

    // ==================================================================== reel ports (owner review round 2, 2026-10-04)
    /// <summary>What a reel's inlet may couple to. Pipe = a static pipe cell (the universal pipe carries any liquid);
    /// Tank = any liquid store (the universal tank, RM_LiquidTank, a VE PipeSystem storage); Other = any other
    /// pipe-friendly building that opted in; Machine = a FlowWorks liquid machine (pump, converter, pipe adapter, reactor,
    /// bath bench: hose port step 6), an origin that a hose may be screwed onto. Rank order is the preference order, and
    /// Machine ranks last (selftest S12): a reel beside both a tank and a pump couples to the tank.</summary>
    public enum HosePortKind { Pipe, Tank, Other, Machine, None }

    /// <summary>
    /// HOSE_ENDS_FIX_MISSES_THE_PORTS: where a hose end coupled to a building meets its DRAWN port. The universal tank
    /// (RM_LiquidTank and its looks: 2x2, drawSize 2, Graphic_Single) draws one port flange on its west and on its east edge,
    /// on the footprint's centre line (measured per look from Textures/RimMandrake/FlowWorks/Tank/&lt;Look&gt;/RM_LiquidTank.png;
    /// FlowWorks/selftest_hose_ports.py pins the table to the art). A 2x2 footprint's centre line is a cell corner, so the hose's end
    /// cell is always half a cell off it: the hose bends over its last stretch onto the port (HoseMath.EndOnPort). Every other
    /// approach (a tank's north or south side, the tall tank, machines, pipes) keeps the shared edge's midpoint.
    /// </summary>
    public static class TankPortGeometry
    {
        public const string TankDef = "RM_LiquidTank";
        public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };
        /// <summary>Port flange centre, dz cells from the footprint centre, per look (alpha &gt; 128 rows at the edge column).</summary>
        public static readonly double[] PortDz = { 0.021, 0.025, -0.016, -0.057 };

        /// <summary>The drawn port a hose end on side (sx, sz) of a 2x2 universal tank couples to, or false (keep the edge midpoint).
        /// (sx, sz) = unit step from the end cell into the tank; (bx, bz) = the tank's footprint minimum.</summary>
        internal static bool PortPoint(string look, int bx, int bz, int bw, int bh, int sx, int sz, out V2 port)
        {
            port = default(V2);
            if (bw != 2 || bh != 2 || sz != 0 || Math.Abs(sx) != 1) return false;
            int i = Array.IndexOf(Looks, look);
            double dz = PortDz[i < 0 ? 0 : i];
            port = new V2(sx > 0 ? bx : bx + bw, bz + bh / 2.0 + dz);
            return true;
        }

        /// <summary>OFF_BODY_PORTS (delegated design ruling 2026-10-23, infrastructure/state/delegated/2026-10-23/off_body_ports.json;
        /// owner 2026-10-23: couplers' art goes UNDER the fixture): a hose port lies where the art's body is. These lanes' edge
        /// midpoints had no body on their inward axis (RM_UniversalCargoTank upper west/east: CARGO_UPPER_PORT_DECIDE_NOTHING_UNDER)
        /// or two under-couplers met on open ground at a narrow body's corner (tall / XTall south lane 0 + west lane 0, east lane 0 +
        /// south lane 1: UNDER_COUPLER_DECIDE_CORNER_CROWDING), so the port slides ALONG its edge, inside the same end cell (hose
        /// laying and pathing unchanged), to the given offset from the footprint minimum. One geometry per def, every look passes
        /// (measured by FlowWorks/selftest_hose_fittings.py, which parses this table). Key: def|side|lane, side 0 south 1 north
        /// 2 west 3 east (the end cell's side), lane = the end cell's index along that side.</summary>
        public static readonly Dictionary<string, double> MovedAlong = new Dictionary<string, double>
        {
            { "RM_UniversalCargoTank|2|1", 1.25 },
            { "RM_UniversalCargoTank|3|1", 1.25 },
            { "RM_LiquidTankTall|0|0", 0.75 },
            { "RM_LiquidTankTall|0|1", 1.25 },
            { "RM_LiquidTankTall|2|0", 0.75 },
            { "RM_LiquidTankTall|3|0", 0.75 },
            { "RM_UniversalCargoTankXTall|0|0", 0.75 },
            { "RM_UniversalCargoTankXTall|0|1", 1.25 },
            { "RM_UniversalCargoTankXTall|2|0", 0.75 },
            { "RM_UniversalCargoTankXTall|3|0", 0.75 },
        };

        /// <summary>The drawn port a hose end in cell (ex, ez), on side (sx, sz) of fixture <paramref name="def"/> (footprint min
        /// (bx, bz), size bw x bh), couples to: RM_LiquidTank's measured flange (<see cref="PortPoint"/>) or a moved lane
        /// (<see cref="MovedAlong"/>); false = the shared edge's midpoint.</summary>
        internal static bool HosePort(string def, string look, int bx, int bz, int bw, int bh, int ex, int ez, int sx, int sz, out V2 port)
        {
            if (def == TankDef) return PortPoint(look, bx, bz, bw, bh, sx, sz, out port);
            port = default(V2);
            if (Math.Abs(sx) + Math.Abs(sz) != 1) return false;
            int side = sz == 1 ? 0 : sz == -1 ? 1 : sx == 1 ? 2 : 3;
            int lane = sx != 0 ? ez - bz : ex - bx;
            if (!MovedAlong.TryGetValue(def + "|" + side + "|" + lane, out double along)) return false;
            double edgeX = ex + 0.5 + sx * 0.5, edgeZ = ez + 0.5 + sz * 0.5;
            port = sx != 0 ? new V2(edgeX, bz + along) : new V2(bx + along, edgeZ);
            return true;
        }
    }

    /// <summary>The reel's footprint (round 3, owner 2026-10-04: "the reel should be 2x2, not 1x1, as the shown hose is
    /// quite large"). The hose leaves the reel at its CENTRE (a cell corner for 2x2) from under the sprite.</summary>
    public struct HoseReelRect
    {
        public int X0, Z0, W, H;
        public HoseReelRect(int x0, int z0, int w, int h) { X0 = x0; Z0 = z0; W = Math.Max(1, w); H = Math.Max(1, h); }
        internal V2 Centre => new V2(X0 + W / 2.0, Z0 + H / 2.0);

        /// <summary>Where the hose leaves the reel. Owner 2026-10-05 (reversing round 5's hide-under-the-drum): the 2x2 reel's hose
        /// starts at its brass OUTLET nozzle, and a coupling sits on that nozzle. HOSE_ENDS_FIX_MISSES_THE_PORTS (owner 2026-10-21:
        /// "Hose attached to tank and reel broken"): the nozzle tip is MEASURED per look from the installed laid art
        /// (ReelIntakeGeometry.OutletTip, generated, --check in FlowWorks/selftest_hose_ports.py), never a constant (one went stale when the
        /// art was replaced). The routing start is that tip, clamped inside the outlet-side cells so a lay still starts in a reel
        /// cell; <see cref="NozzleTip"/> is where the coupling's face meets the nozzle. REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST (owner
        /// card 2026-10-22, "Player turns the reel"): the tip, the clamp and <see cref="Outward"/> turn with <see cref="Rot"/>.
        /// A 1x1 reel keeps its centre.</summary>
        internal V2 Mouth
        {
            get
            {
                if (!HasNozzle) return Centre;
                V2 t = NozzleTip;
                switch (Rot)
                {
                    case 1: return new V2(Math.Min(t.X, X0 + W - 0.02), t.Z);   // east
                    case 0: return new V2(t.X, Math.Min(t.Z, Z0 + H - 0.02));   // north
                    case 2: return new V2(t.X, Math.Max(t.Z, Z0 + 0.02));       // south
                    default: return new V2(Math.Max(t.X, X0 + 0.02), t.Z);      // west
                }
            }
        }
        private int rotCode;
        /// <summary>The way the reel's outlet faces, as a Rot4 int (0 N, 1 E, 2 S, 3 W). Default (a rect built without one) = 3,
        /// west: the drawn picture's own outlet, the only facing before 2026-10-22.</summary>
        public int Rot { get => (rotCode + 3) % 4; set => rotCode = (((value % 4) + 4) % 4 + 1) % 4; }
        /// <summary>An art-frame offset (dx, dz) from the footprint centre, turned to this facing: east = the west picture
        /// mirrored; north / south = the frame turned 90 degrees clockwise / anticlockwise. REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED:
        /// north and south now have pictures of their own, drawn UNTURNED, and ReelIntakeGeometry measures each of them turned
        /// into this same frame (frame 1 / 2), so this mapping lands their measured points where they are drawn.</summary>
        internal V2 FromArt(double dx, double dz)
        {
            switch (Rot)
            {
                case 1: return new V2(-dx, dz);
                case 0: return new V2(dz, -dx);
                case 2: return new V2(-dz, dx);
                default: return new V2(dx, dz);
            }
        }
        /// <summary>How a facing's picture is drawn: the angle the plane turns clockwise seen from above (RimWorld's
        /// Rot4.AsAngle sense) and whether its u is mirrored. REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED (owner card 2026-10-22,
        /// "install all 16"): north and south draw their own pictures (Reel_*_north / _south) unturned; east is the west
        /// picture mirrored (owner card); west as drawn. The north/south stand-in (the west picture turned) is gone.</summary>
        public static void ArtPose(int rot, out float angle, out bool mirror)
        {
            angle = 0f;
            mirror = ((rot % 4) + 4) % 4 == 1;   // east: the west picture mirrored
        }
        /// <summary>The inverse of <see cref="FromArt"/>: a world offset from the centre, in the west picture's frame.</summary>
        internal V2 ToArt(double x, double z)
        {
            switch (Rot)
            {
                case 1: return new V2(-x, z);
                case 0: return new V2(-z, x);
                case 2: return new V2(z, -x);
                default: return new V2(x, z);
            }
        }
        /// <summary>The reel's look (HoseStyles.Looks); null or unknown = the base (Scrapper) art.</summary>
        public string Look;
        /// <summary>The laid art's nozzle tip, where the end coupling's face is drawn (2x2 reel only).</summary>
        internal V2 NozzleTip
        {
            get
            {
                if (!HasNozzle) return Centre;
                ReelIntakeGeometry.OutletTip(Look, true, out double dx, out double dz, Rot);
                return Centre + FromArt(dx, dz);
            }
        }
        /// <summary>True when the reel's art carries a brass outlet nozzle the hose couples to (the 2x2 reel).</summary>
        public bool HasNozzle => W == 2 && H == 2;
        /// <summary>2026-10-05: the hose leaves a nozzled reel dead straight out of the outlet for this many cells from
        /// <see cref="Mouth"/> (0.32 to the tip + the end coupling and its wrap, ~1.1, + a margin), so it visibly runs through
        /// the coupling instead of turning away under the pump body.</summary>
        public const double OutletStraight = 1.6;
        /// <summary>How far the end coupling's threaded stub slides into the outlet nozzle (drawn under the reel sprite), so the
        /// two meet with no gap.</summary>
        public const double NozzleSeat = 0.07;
        /// <summary>The direction the hose leaves a nozzled reel: the way its outlet faces (<see cref="Rot"/>; the picture's outlet
        /// is west), or null.</summary>
        internal V2? Outward => HasNozzle ? FromArt(-1, 0) : (V2?)null;
        internal bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
        public bool Overlaps(HosePortCandidate o) => o.X0 < X0 + W && X0 < o.X0 + o.W && o.Z0 < Z0 + H && Z0 < o.Z0 + o.H;

        /// <summary>The reel cells on one side (side = unit step outward), ascending along it.</summary>
        internal List<Cell> EdgeCells(Cell side)
        {
            var l = new List<Cell>();
            if (side.X != 0) { int x = side.X > 0 ? X0 + W - 1 : X0; for (int z = Z0; z < Z0 + H; z++) l.Add(new Cell(x, z)); }
            else { int z = side.Z > 0 ? Z0 + H - 1 : Z0; for (int x = X0; x < X0 + W; x++) l.Add(new Cell(x, z)); }
            return l;
        }

        /// <summary>The reel cell nearest the target (the planner's start cell); ties to the lowest x, then z.</summary>
        internal Cell StartCellToward(Cell target)
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
        internal List<Cell> Perimeter()
        {
            var l = new List<Cell>();
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in EdgeCells(s)) l.Add(e + s);
            return l;
        }

        /// <summary>HOSES_MAP1_DIAGNOSE_TICK_STALLS: <see cref="Perimeter"/> written into <paramref name="l"/> (cleared first), same
        /// cells in the same order, without the per-call lists (the hose tick reads it ~4 times a tick on a busy map).</summary>
        internal void PerimeterInto(List<Cell> l)
        {
            l.Clear();
            Cell[] order = HosePortRule.SideOrder;
            for (int si = 0; si < order.Length; si++)
            {
                Cell s = order[si];
                if (s.X != 0) { int x = s.X > 0 ? X0 + W - 1 : X0; for (int z = Z0; z < Z0 + H; z++) l.Add(new Cell(x, z) + s); }
                else { int z = s.Z > 0 ? Z0 + H - 1 : Z0; for (int x = X0; x < X0 + W; x++) l.Add(new Cell(x, z) + s); }
            }
        }
    }

    public struct HosePortCandidate
    {
        public int X0, Z0, W, H;
        public HosePortKind Kind;
        public HosePortCandidate(int x0, int z0, int w, int h, HosePortKind kind) { X0 = x0; Z0 = z0; W = w; H = h; Kind = kind; }
        internal bool Contains(Cell c) => c.X >= X0 && c.X < X0 + W && c.Z >= Z0 && c.Z < Z0 + H;
    }

    /// <summary>The Verse-free connection rule (SelfTest: HoseSelfTest.Ports). A reel couples to a neighbour only across
    /// a shared cell EDGE (a corner touch would draw a feed through empty air); among those it prefers a pipe, then a
    /// tank, then anything else, and breaks ties by side in the fixed order east, north, west, south, so the answer
    /// never depends on thing-list order.</summary>
    public static class HosePortRule
    {
        /// <summary>Joints study 2026-10-22 (UI note): a Deploy aimed AT a tank, pump or machine (its own, unwalkable square)
        /// answered "target blocked". The order now lands on the free square beside that thing nearest the reel's mouth; this
        /// picks it: the candidate nearest <paramref name="mouth"/> (ties: the first). -1 when there is none.</summary>
        internal static int NearestApproach(IList<Cell> cands, V2 mouth)
        {
            int best = -1;
            double bd = double.MaxValue;
            for (int i = 0; i < cands.Count; i++)
            {
                double d = V2.Dist(cands[i].Centre, mouth);
                if (d < bd - 1e-9) { bd = d; best = i; }
            }
            return best;
        }

        /// <summary>HOSE_TANK_LAY_FIX_ENDS_ON_LID (live art look 2026-10-22): a lay aimed at a solid port thing's own square (a
        /// tank) must end on the free square in front of its port, never on the thing itself, and is REFUSED when no such square
        /// is free (an aim that fell through unchanged left the end lying on the tank's lid, 0.207 cell off its port). Null =
        /// fine (pick = the chosen approach, or -1 when the aim was not at a solid port), else the refusal.</summary>
        internal static string AimAtSolidPort(bool aimedAtSolidPort, string portLabel, IList<Cell> approach, V2 mouth, out int pick)
        {
            pick = -1;
            if (!aimedAtSolidPort) return null;
            pick = NearestApproach(approach, mouth);
            return pick >= 0 ? null : "no free square in front of the " + (string.IsNullOrEmpty(portLabel) ? "tank" : portLabel)
                                      + "'s port to couple the hose to (clear a square beside it, or aim at one)";
        }

        internal static readonly Cell[] SideOrder = { new Cell(1, 0), new Cell(0, 1), new Cell(-1, 0), new Cell(0, -1) };

        /// <summary>Index of the chosen candidate, or -1. side = the unit step from the reel to the contact cell.</summary>
        internal static int Pick(Cell reel, IList<HosePortCandidate> cands, out Cell side) =>
            Pick(new HoseReelRect(reel.X, reel.Z, 1, 1), cands, out side, out _);

        /// <summary>Any reel footprint (round 3: 2x2). contact = the neighbour cell (outside the reel) across the shared
        /// edge; the reel cell it touches is contact - side. Ties: kind, then side (E, N, W, S), then the lowest cell along
        /// that side -- never candidate order.</summary>
        internal static int Pick(HoseReelRect reel, IList<HosePortCandidate> cands, out Cell side, out Cell contact)
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
        internal static void Feed(Cell reel, Cell side, out V2 from, out V2 to, out V2 coupling)
        {
            V2 d = new V2(side.X, side.Z), c = reel.Centre;
            from = c + d * 0.25;
            to = (reel + side).Centre;
            coupling = c + d * 0.5;
        }
    }
}
