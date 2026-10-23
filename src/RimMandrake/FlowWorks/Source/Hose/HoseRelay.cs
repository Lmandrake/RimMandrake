using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Round 6 (owner 2026-10-04: "So if the hose can only reach 30 cells, how does the player go farther? Maybe they place
    /// another reel out there to connect to? If so we should show that working."). Verse-free rules of a RELAY: a hose that
    /// ends at another reel's intake feeds that reel, which lays its own hose onward.
    ///   * intake: a cell just outside the relay's footprint across one of its SIDE edges (never a corner), like a pipe or
    ///     tank coupled to a reel (HosePortRule). The hose ends on the shared edge, a coupling pointing into the relay.
    ///   * which intake: the walkable one whose centre is nearest the feeding reel's mouth; ties in side order E, N, W, S,
    ///     then the lowest cell along that side.
    ///   * a reel feeds the relay whose intake cell its laid free end is on (derived, never saved; two candidates -> the
    ///     lowest index given, the caller passes them in thing-id order).
    ///   * each hose keeps its own length cap, route search, re-route and retract: nothing about a hose changes because
    ///     it is in a chain.
    ///   * a chain may not loop back on itself (refused at lay time; ignored by the flow read).
    /// </summary>
    public static class HoseRelay
    {
        /// <summary>Work counter (review S1 perf test): how many times a reel's intake cells were enumerated.</summary>
        public static long IntakeCellCalls;

        /// <summary>The relay's intake cells, in side order E, N, W, S and along each side.</summary>
        internal static List<Cell> IntakeCells(HoseReelRect relay)
        {
            IntakeCellCalls++;
            var o = new List<Cell>();
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s)) o.Add(e + s);
            return o;
        }

        internal static bool IsIntakeOf(HoseReelRect relay, Cell c) => IntakeCells(relay).Contains(c);

        /// <summary>REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT (owner walk 2026-10-23: the hose went "to the western on the right,
        /// overlapping its handle and ignoring where it has an obvious hose connector"): the cells a NEW link may end on. A 2x2
        /// reel's art draws ONE hose connector, its brass nozzle, on the side it faces (HoseReelRect.Outward); the other three
        /// sides are its crank, drum and frame. So a nozzled relay offers only the two cells in front of its nozzle (both couple
        /// to the drawn nozzle, DrawnEnd); any other footprint offers every intake cell. Recognition of an existing link
        /// (IsIntakeOf / RelayOf) still reads all sides, so a hose laid before this rule keeps feeding.</summary>
        internal static List<Cell> PortCells(HoseReelRect relay)
        {
            if (!relay.HasNozzle) return IntakeCells(relay);
            V2 o = relay.Outward.Value;
            var s = new Cell((int)Math.Round(o.X), (int)Math.Round(o.Z));
            var l = new List<Cell>();
            foreach (Cell e in relay.EdgeCells(s)) l.Add(e + s);
            return l;
        }

        /// <summary>The intake a hose from <paramref name="fromMouth"/> ends on (one of <see cref="PortCells"/>, the nearest),
        /// or false when every one is blocked.</summary>
        internal static bool TryIntake(HoseReelRect relay, V2 fromMouth, Func<Cell, bool> walkable, out Cell intake)
        {
            intake = new Cell(0, 0);
            double best = double.MaxValue;
            bool found = false;
            foreach (Cell c in PortCells(relay))
            {
                if (walkable != null && !walkable(c)) continue;
                double d = V2.Dist(c.Centre, fromMouth);
                if (d < best - 1e-9) { best = d; intake = c; found = true; }
            }
            return found;
        }

        /// <summary>The unit step from the intake cell into the relay (zero when the cell is not an intake).</summary>
        internal static Cell SideInto(HoseReelRect relay, Cell intake)
        {
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s))
                    if (e + s == intake) return new Cell(-s.X, -s.Z);
            return new Cell(0, 0);
        }

        /// <summary>Where the hose ends: the midpoint of the edge the intake cell shares with the relay.</summary>
        internal static V2 IntakePoint(HoseReelRect relay, Cell intake)
        {
            Cell d = SideInto(relay, intake);
            return intake.Centre + new V2(d.X * 0.5, d.Z * 0.5);
        }

        /// <summary>Round 7 (owner, station 42: "pipe does NOT hook up properly to the next reel station"): where the hose
        /// that ends on <paramref name="intake"/> is DRAWN to, and the direction its last stretch and end coupling point
        /// (into the relay). On a 2x2 reel: from the west, the art's one brass inlet (the coupling's face meets the inlet's
        /// face, both west cells); from the east, north or south, the place along that cell's half of the edge where the
        /// drawn reel comes closest to the edge, the coupling's face on the drawn outline (ReelIntakeGeometry, measured
        /// per look and per art: <paramref name="deployed"/> = the relay has laid its own hose). Always within
        /// <see cref="EndTolerance"/> of the footprint edge. Any other footprint: the edge midpoint (IntakePoint).</summary>
        internal static V2 DrawnEnd(HoseReelRect relay, Cell intake, string look, bool deployed, out V2 inward)
        {
            Cell d = SideInto(relay, intake);
            inward = new V2(d.X, d.Z);
            if (relay.W != 2 || relay.H != 2 || (d.X == 0 && d.Z == 0)) return IntakePoint(relay, intake);
            V2 c = relay.Centre;
            double perp, depth;
            // REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST: the side and the edge cell are read in the facing's art frame (ToArt), measured
            // there (REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED: north/south from their own pictures, ReelIntakeGeometry frame by
            // relay.Rot), and turned back (FromArt)
            V2 ca = relay.ToArt(intake.Centre.X - c.X, intake.Centre.Z - c.Z);
            V2 pa;
            if (Math.Abs(ca.X) >= Math.Abs(ca.Z) && ca.X < 0)       // intake on the picture's WEST side (its brass inlet)
            {
                ReelIntakeGeometry.WestInlet(look, deployed, out perp, out depth, relay.Rot);
                pa = new V2(-relay.W / 2.0 - depth, perp);
            }
            else if (Math.Abs(ca.X) >= Math.Abs(ca.Z))              // EAST
            {
                ReelIntakeGeometry.Edge(look, deployed, 0, ca.Z > 0 ? 1 : 0, out perp, out depth, relay.Rot);
                pa = new V2(relay.W / 2.0 + depth, perp);
            }
            else if (ca.Z > 0)                                      // NORTH
            {
                ReelIntakeGeometry.Edge(look, deployed, 1, ca.X > 0 ? 1 : 0, out perp, out depth, relay.Rot);
                pa = new V2(perp, relay.H / 2.0 + depth);
            }
            else                                                    // SOUTH
            {
                ReelIntakeGeometry.Edge(look, deployed, 2, ca.X > 0 ? 1 : 0, out perp, out depth, relay.Rot);
                pa = new V2(perp, -relay.H / 2.0 - depth);
            }
            return c + relay.FromArt(pa.X, pa.Z);
        }

        /// <summary>How far a drawn relay end may sit from the footprint edge (cells): the reel art overhangs or falls short
        /// of its 2x2 footprint, and the hose ends on the drawing, not in the air beside it. 0.35 for the 10-05 art at drawSize
        /// 2.8; the 2026-10-21 art at 2.15 draws up to ~0.7 inside the edge (HOSE_ENDS_FIX_MISSES_THE_PORTS).</summary>
        public const double EndTolerance = 0.75;

        /// <summary>The straight run the hose makes into its end coupling (cells), so the coupling's axis is the intake's.</summary>
        public const double EndStraight = 0.6;

        /// <summary>Signed distance of <paramref name="p"/> from the relay's edge on the side the hose comes in from (+ =
        /// outside), and whether p lies within that edge's span (between its corners).</summary>
        internal static double EdgeOffset(HoseReelRect relay, V2 inward, V2 p, out bool withinSpan)
        {
            V2 o = new V2(-inward.X, -inward.Z);
            if (o.X != 0)
            {
                double edge = o.X > 0 ? relay.X0 + relay.W : relay.X0;
                withinSpan = p.Z > relay.Z0 && p.Z < relay.Z0 + relay.H;
                return (p.X - edge) * o.X;
            }
            double ez = o.Z > 0 ? relay.Z0 + relay.H : relay.Z0;
            withinSpan = p.X > relay.X0 && p.X < relay.X0 + relay.W;
            return (p.Z - ez) * o.Z;
        }

        /// <summary>Index of the relay a hose whose free end is on <paramref name="far"/> feeds, or -1. self is skipped.</summary>
        internal static int RelayOf(Cell far, IList<HoseReelRect> reels, int self)
        {
            for (int i = 0; i < reels.Count; i++)
                if (i != self && IsIntakeOf(reels[i], far)) return i;
            return -1;
        }

        /// <summary>GPT source read 2026-10-06 B10: where a reel's hose WILL end for the loop test: a pending carry order's end
        /// (Deploy or Move) wins over the laid end, so two pending orders cannot close a ring that neither sees laid.</summary>
        public static int IntendedNext(int laidNext, bool pendingEnd, int pendingNext) => pendingEnd ? pendingNext : laidNext;

        /// <summary>True when laying a hose from reel <paramref name="from"/> into relay <paramref name="to"/> would close a
        /// loop: following the chain downstream from <paramref name="to"/> (next(i) = the relay i feeds, -1 = none) reaches
        /// <paramref name="from"/>.</summary>
        public static bool WouldLoop(int from, int to, Func<int, int> next)
        {
            var seen = new HashSet<int>();
            for (int i = to; i >= 0 && seen.Add(i); i = next(i))
                if (i == from) return true;
            return false;
        }

        /// <summary>The reels a chain passes through from <paramref name="start"/> downstream (start first); stops at a loop.</summary>
        public static List<int> Chain(int start, Func<int, int> next)
        {
            var o = new List<int>();
            var seen = new HashSet<int>();
            for (int i = start; i >= 0 && seen.Add(i); i = next(i)) o.Add(i);
            return o;
        }
    }
    /// <summary>
    /// Review S1 (design FINAL §3.1 "Index", G1.17): the relay adjacency of one map, built ONCE in O(reels) and shared by
    /// drawing, Loops, FeedersOf, the debug flow provider and RM_HoseLinks. Inputs are in thing-id order (the relay
    /// tie-break): each reel's footprint, its laid free end (null = not laid) and its debug-flow flag.
    ///   * next(i): the relay i's laid hose ends on (the lowest-index reel other than i with that intake cell), or -1.
    ///   * a laid edge i -> next(i) closes a loop exactly when i lies on a cycle of next (functional graph), so
    ///     Loops(i, next(i)) is a precomputed flag, and Feeders(r) = { j : next(j) = r, j not on a cycle }.
    /// </summary>
    public sealed class HoseRelayIndex
    {
        public readonly int Count;
        private readonly int[] next;
        private readonly bool[] onCycle;
        private readonly bool[] debug;
        private readonly List<int>[] feeders;
        private readonly Dictionary<Cell, List<int>> intake = new Dictionary<Cell, List<int>>();
        private static readonly List<int> NoFeeders = new List<int>();

        /// <summary>True when any reel carries the debug-flow flag; with none the debug provider has nothing to say.</summary>
        public readonly bool AnyDebug;

        /// <summary>Work counter: feeder steps the debug provider walked (review S1: an idle map walks none).</summary>
        public static long DebugWalkSteps;

        internal HoseRelayIndex(IList<HoseReelRect> rects, IList<Cell?> laidFar, IList<bool> debugFlag)
        {
            Count = rects.Count;
            next = new int[Count];
            onCycle = new bool[Count];
            debug = new bool[Count];
            feeders = new List<int>[Count];
            for (int i = 0; i < Count; i++)
            {
                foreach (Cell c in HoseRelay.IntakeCells(rects[i]))
                {
                    if (!intake.TryGetValue(c, out List<int> l)) intake[c] = l = new List<int>(1);
                    if (l.Count == 0 || l[l.Count - 1] != i) l.Add(i);
                }
                debug[i] = debugFlag != null && debugFlag[i];
                if (debug[i]) AnyDebug = true;
            }
            for (int i = 0; i < Count; i++) next[i] = laidFar[i].HasValue ? RelayAt(laidFar[i].Value, i) : -1;
            // cycle marking on the functional graph: 0 unvisited, 1 on the current path, 2 finished
            var state = new byte[Count];
            var path = new List<int>();
            for (int s = 0; s < Count; s++)
            {
                if (state[s] != 0) continue;
                path.Clear();
                int i = s;
                while (i >= 0 && state[i] == 0) { state[i] = 1; path.Add(i); i = next[i]; }
                if (i >= 0 && state[i] == 1)
                    for (int k = path.IndexOf(i); k < path.Count; k++) onCycle[path[k]] = true;
                foreach (int p in path) state[p] = 2;
            }
            for (int j = 0; j < Count; j++)
            {
                int r = next[j];
                if (r < 0 || onCycle[j]) continue;
                if (feeders[r] == null) feeders[r] = new List<int>();
                feeders[r].Add(j);
            }
        }

        /// <summary>The reel (other than <paramref name="self"/>) with <paramref name="c"/> as an intake cell, or -1.</summary>
        internal int RelayAt(Cell c, int self)
        {
            if (!intake.TryGetValue(c, out List<int> l)) return -1;
            foreach (int i in l) if (i != self) return i;
            return -1;
        }

        /// <summary>The relay reel i's laid hose ends on, or -1 (loops included: this is the raw laid end).</summary>
        public int Next(int i) => i >= 0 && i < Count ? next[i] : -1;

        /// <summary>True when reel i's laid hose closes a loop (Loops(i, Next(i))).</summary>
        public bool OnLoop(int i) => i >= 0 && i < Count && onCycle[i];

        /// <summary>Reels feeding r, ascending (thing-id order), loops excluded.</summary>
        public IReadOnlyList<int> Feeders(int r) => r >= 0 && r < Count && feeders[r] != null ? feeders[r] : NoFeeders;

        /// <summary>HoseRelay.WouldLoop over the laid ends.</summary>
        public bool WouldLoop(int from, int to) => HoseRelay.WouldLoop(from, to, Next);

        /// <summary>The debug provider's chain read: does any reel feeding r down a relay chain carry the debug flag?
        /// <paramref name="walkable"/> = the feeder has a laid hose with a lay (only those pass the flag on).</summary>
        public bool FedByDebug(int r, Func<int, bool> walkable)
        {
            if (!AnyDebug || r < 0 || r >= Count) return false;
            var seen = new HashSet<int> { r };
            var stack = new Stack<int>();
            stack.Push(r);
            while (stack.Count > 0)
                foreach (int f in Feeders(stack.Pop()))
                {
                    DebugWalkSteps++;
                    if (!seen.Add(f) || !walkable(f)) continue;
                    if (debug[f]) return true;
                    stack.Push(f);
                }
            return false;
        }
    }
    /// <summary>
    /// HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES (owner 2026-10-22: <i>"I can't even tell what's going on here with the
    /// connnectors. Just look at them!"</i>, then <i>"let's try to fix the connectors"</i>). The ONE place a hose joint's
    /// geometry is decided: where each drawn fitting's face lands, where a link from a pipe/tank/pump beside a reel runs, and
    /// how far a drawn end may sit from its port before the joint check calls it a gap. The draw code (RM_MapComponent_Hoses)
    /// and the live joint check (HoseProbe "joints") both read these, and HoseJointChecks pins them offline. Lives in this
    /// file (compiled by the mod and the SelfTest alike) so no project file had to change.
    ///   * a 2x2 reel has ONE fitting, its brass nozzle (ReelIntakeGeometry.OutletTip, measured per look, art and facing):
    ///     a laid hose's coupling face sits on it; a link from a port in FRONT of the nozzle of a stored reel couples to it too;
    ///   * a port on any other side (behind the crank, above or below the drum), or in front of a reel whose nozzle already
    ///     carries its laid hose, has no fitting to meet: the link runs from the port's centre line in under the reel to its
    ///     centre (PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE, owner 2026-10-18), hidden by the reel's body, never ending in air and
    ///     never carrying a coupling floating between the two buildings.
    /// </summary>
    public static class HoseJoints
    {
        /// <summary>The joint check's tolerance (cells): a drawn end or fitting face farther than this from the point it must
        /// meet is a gap. 0.05 cell = ~6 px at the closest zoom (114 px/cell): the smallest gap the audit's crops showed was
        /// 0.1.</summary>
        public const double Tolerance = 0.05;

        /// <summary>The centre of a fitting whose working face is at <paramref name="face"/>, pointing along <paramref name="d"/>
        /// (RM_MapComponent_Hoses.Fitting): face + d x centreOff x size. With centreOff = -JoinerFace the drawn coupling's face
        /// (art u 0.46, HO9 pins it) lands exactly on <paramref name="face"/>.</summary>
        internal static V2 FittingCentre(V2 face, V2 d, double centreOff, double size) => face + d * (centreOff * size);

        /// <summary>Where the drawn coupling's face reaches for a fitting centred at <paramref name="centre"/> (the inverse).</summary>
        internal static V2 CouplingFace(V2 centre, V2 d, double size) => centre + d * (HoseMath.JoinerFace * size);

        /// <summary>The laid hose's reel-end coupling: its face point (seated <see cref="HoseReelRect.NozzleSeat"/> into the
        /// laid art's nozzle tip) and its axis (into the reel).</summary>
        internal static V2 NozzleCoupling(HoseReelRect r, out V2 inward)
        {
            inward = -(r.Outward ?? new V2(-1, 0));
            return r.NozzleTip + inward * HoseReelRect.NozzleSeat;
        }

        /// <summary>The STORED art's nozzle tip (a reel that has not laid its hose shows Reel_PumpHookup).</summary>
        internal static V2 StoredNozzleTip(HoseReelRect r)
        {
            ReelIntakeGeometry.OutletTip(r.Look, false, out double dx, out double dz, r.Rot);
            return r.Centre + r.FromArt(dx, dz);
        }

        /// <summary>
        /// The link from a pipe, tank or pump beside a reel's body to the reel (RM_MapComponent_Hoses.DrawFeed).
        /// <paramref name="side"/> = unit step from the reel to <paramref name="contact"/> (the port's cell beside it). Returns
        /// the polyline (from the port's cell centre: a pipe's centre line, or under the tank/pump body) and, when the link
        /// couples to the nozzle, the coupling's face point and axis; onNozzle false = the link runs in under the reel to its
        /// centre and no coupling is drawn.
        /// </summary>
        internal static List<V2> ReelFeed(HoseReelRect reel, Cell side, Cell contact, bool laid, out bool onNozzle, out V2 face, out V2 axis)
        {
            V2 p = contact.Centre, s = new V2(side.X, side.Z);
            onNozzle = false;
            face = axis = default(V2);
            V2? outw = reel.Outward;
            if (outw.HasValue && !laid && Math.Abs(outw.Value.X - s.X) < 1e-9 && Math.Abs(outw.Value.Z - s.Z) < 1e-9)
            {
                V2 tip = StoredNozzleTip(reel);
                axis = -s;
                face = tip + axis * HoseReelRect.NozzleSeat;
                // from the port's centre line, square across inside the port's cell to the nozzle's line, then straight in
                V2 jog = side.X != 0 ? new V2(p.X, tip.Z) : new V2(tip.X, p.Z);
                onNozzle = true;
                var l = new List<V2> { p };
                if (V2.Dist(jog, p) > 1e-6) l.Add(jog);
                l.Add(face - axis * 0.02);   // the hose runs into the coupling's back; the coupling face meets the tip
                return l;
            }
            var o = new List<V2> { p };
            double[] stub = RimMandrake.FlowWorks.Machinery.LiquidJoinRule.CentreStub(contact.X, contact.Z, -side.X, -side.Z, reel.X0, reel.Z0, reel.W, reel.H);
            if (stub != null) for (int i = 0; i + 1 < stub.Length; i += 2) o.Add(new V2(stub[i], stub[i + 1]));
            else o.Add(reel.Centre);
            return o;
        }

        /// <summary>The joint check's one test: distance from a drawn point to the point it must meet, and whether it passes.</summary>
        internal static bool Meets(V2 drawn, V2 port, out double gap)
        {
            gap = V2.Dist(drawn, port);
            return gap <= Tolerance;
        }

        /// <summary>JOINT_GATE_HARDEN_TRUST_THE_DRAWN_BOX (audit F9: "the drawn collar's box must overlap the nozzle/port sprite
        /// box"). The opaque box of a coupling AS DRAWN (RM_MapComponent_Hoses records each one's centre, axis and size): the
        /// Coupling_Bare art runs from the hose entry at the canvas's -X edge (-0.5 size) to its brass face at +JoinerFace size
        /// along <paramref name="d"/>, and is <paramref name="band"/> x size wide (its widest opaque band, HO9 pins both).
        /// Returns the distance from <paramref name="target"/> (the measured nozzle tip or port point) to that box: 0 when the
        /// drawn collar covers the point, so a collar that stops short of the nozzle (audit D9) or floats beside a port reads as
        /// a gap even when the geometry function that placed it says otherwise.</summary>
        internal static double CollarBoxGap(V2 centre, V2 d, double size, double band, V2 target)
        {
            V2 u = d.Norm();
            V2 rel = target - centre;
            double along = rel.X * u.X + rel.Z * u.Z, perp = Math.Abs(rel.X * u.Z - rel.Z * u.X);
            double lo = -0.5 * size, hi = HoseMath.JoinerFace * size, hw = 0.5 * band * size;
            double da = along < lo ? lo - along : along > hi ? along - hi : 0;
            double dp = Math.Max(0, perp - hw);
            return Math.Sqrt(da * da + dp * dp);
        }
    }

    /// <summary>
    /// HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK (audit F2/D2: "the hose is going under the battery and wall") and
    /// HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE (audit F8/D11: two hoses "cross flat, one painted over the other with no lift or
    /// shadow"). The Verse-free half of drawing a laid hose OVER something: which stretches of a drawn pose (arc spans, cells
    /// from its start) lie over a flagged cell (a walk-over building drawn above the hose layer) or over another hose, and the
    /// pose cut to such a span. The draw (RM_MapComponent_Hoses) redraws those stretches above the building layer, or casts a
    /// crossing shadow there, and records the spans so the joint check reads what was drawn. Lives in this file (compiled
    /// by the mod and the SelfTest alike) so no project file had to change.
    /// </summary>
    public static class HoseOverDraw
    {
        /// <summary>Sampling step along the pose (cells).</summary>
        public const double Step = 0.05;
        /// <summary>A building's sprite overhangs its cell a little (a battery's is 1 x 2 on 1 x 2 cells but its outline art
        /// runs to the edge): each span over a building runs this far past the flagged cells at both ends.</summary>
        public const double BuildingMargin = 0.3;
        /// <summary>The altitude layer a hose stretch lying over a walk-over building is redrawn on (vanilla
        /// AltitudeLayer.BuildingOnTop = 17: above Building 15, below Item 18 and every pawn layer), plus the hose's base lift
        /// and its crossing band, so its top (CrossRanks bands + fittings) stays under the Item layer (SelfTest pins it).</summary>
        public const int OverBuildingLayer = 17;

        /// <summary>Arc spans {a0, a1} (sorted, merged, clipped to [0, L]) where the pose's samples satisfy
        /// <paramref name="flagged"/>, each widened by <paramref name="margin"/> at both ends.</summary>
        internal static List<double[]> SpansWhere(IList<V2> pts, Func<V2, bool> flagged, double margin)
        {
            var o = new List<double[]>();
            if (pts == null || pts.Count < 2) return o;
            double[] s = Geo.CumLen(pts);
            double L = s[s.Length - 1];
            if (L < 1e-9) return o;
            int n = Math.Max(1, (int)Math.Ceiling(L / Step));
            double start = -1, last = 0;
            int k = 0;
            for (int i = 0; i <= n; i++)
            {
                double t = L * i / n;
                while (k < s.Length - 2 && s[k + 1] < t) k++;
                double seg = s[k + 1] - s[k];
                V2 p = pts[k] + (pts[k + 1] - pts[k]) * (seg < 1e-12 ? 0 : Geo.Clamp((t - s[k]) / seg, 0, 1));
                if (flagged(p)) { if (start < 0) start = t; last = t; }
                else if (start >= 0) { Add(o, start - margin, last + margin, L); start = -1; }
            }
            if (start >= 0) Add(o, start - margin, last + margin, L);
            return o;
        }

        /// <summary>Spans over cells <paramref name="flagged"/> marks (a walk-over building drawn above the hose).</summary>
        internal static List<double[]> Spans(IList<V2> pts, Func<Cell, bool> flagged, double margin) =>
            SpansWhere(pts, p => flagged(p.Floor), margin);

        /// <summary>Spans where the pose passes within <paramref name="reach"/> of any of <paramref name="lowers"/> (the hoses
        /// drawn beneath it): where the two ribbons overlap, reach = the sum of their half widths.</summary>
        internal static List<double[]> CrossSpans(IList<V2> upper, IList<IList<V2>> lowers, double reach, double margin)
        {
            var near = new List<IList<V2>>();
            if (upper == null || upper.Count < 2 || lowers == null) return new List<double[]>();
            Bounds(upper, out double ux0, out double uz0, out double ux1, out double uz1);
            foreach (IList<V2> q in lowers)
            {
                if (q == null || q.Count < 2) continue;
                Bounds(q, out double x0, out double z0, out double x1, out double z1);
                if (x0 - reach > ux1 || x1 + reach < ux0 || z0 - reach > uz1 || z1 + reach < uz0) continue;
                near.Add(q);
            }
            if (near.Count == 0) return new List<double[]>();
            return SpansWhere(upper, p =>
            {
                foreach (IList<V2> q in near) if (DistToPolyline(p, q) <= reach) return true;
                return false;
            }, margin);
        }

        /// <summary>The pose between arc <paramref name="a0"/> and <paramref name="a1"/> (end points interpolated).</summary>
        internal static List<V2> Slice(IList<V2> pts, double a0, double a1)
        {
            var o = new List<V2>();
            if (pts == null || pts.Count < 2 || a1 <= a0) return o;
            double[] s = Geo.CumLen(pts);
            o.Add(PointAt(pts, s, a0));
            for (int i = 0; i < pts.Count; i++) if (s[i] > a0 + 1e-6 && s[i] < a1 - 1e-6) o.Add(pts[i]);
            o.Add(PointAt(pts, s, a1));
            return o;
        }

        /// <summary>True when arc <paramref name="t"/> lies inside one of <paramref name="spans"/>.</summary>
        internal static bool Covers(IList<double[]> spans, double t)
        {
            if (spans == null) return false;
            foreach (double[] sp in spans) if (t >= sp[0] - 1e-9 && t <= sp[1] + 1e-9) return true;
            return false;
        }

        /// <summary>Distance from <paramref name="p"/> to the polyline <paramref name="q"/> (its nearest segment).</summary>
        internal static double DistToPolyline(V2 p, IList<V2> q)
        {
            double best = double.MaxValue;
            for (int i = 1; i < q.Count; i++)
            {
                V2 a = q[i - 1], ab = q[i] - a;
                double l2 = ab.X * ab.X + ab.Z * ab.Z;
                double u = l2 < 1e-12 ? 0 : Geo.Clamp(((p.X - a.X) * ab.X + (p.Z - a.Z) * ab.Z) / l2, 0, 1);
                double dd = V2.Dist(a + ab * u, p);
                if (dd < best) best = dd;
            }
            return best;
        }

        /// <summary>The point at arc <paramref name="t"/> along the pose (clamped to its ends).</summary>
        internal static V2 PointAtArc(IList<V2> pts, double t) => PointAt(pts, Geo.CumLen(pts), t);

        private static V2 PointAt(IList<V2> pts, double[] s, double t)
        {
            int k = 0;
            while (k < s.Length - 2 && s[k + 1] < t) k++;
            double seg = s[k + 1] - s[k];
            return pts[k] + (pts[k + 1] - pts[k]) * (seg < 1e-12 ? 0 : Geo.Clamp((t - s[k]) / seg, 0, 1));
        }

        private static void Bounds(IList<V2> q, out double x0, out double z0, out double x1, out double z1)
        {
            x0 = z0 = double.MaxValue; x1 = z1 = double.MinValue;
            foreach (V2 p in q) { x0 = Math.Min(x0, p.X); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); z1 = Math.Max(z1, p.Z); }
        }

        private static void Add(List<double[]> o, double a0, double a1, double L)
        {
            a0 = Math.Max(0, a0); a1 = Math.Min(L, a1);
            if (a1 < a0) return;          // a zero-length span (one flagged sample, no margin) is kept: Covers still sees it
            if (o.Count > 0 && a0 <= o[o.Count - 1][1] + 1e-9) { o[o.Count - 1][1] = Math.Max(o[o.Count - 1][1], a1); return; }
            o.Add(new[] { a0, a1 });
        }
    }
}
