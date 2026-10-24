// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 pattern grammar, build step 5 (second half) -- TIDE as a TERRITORY SHAPE
// (design/RimMandrake/atmospheric_base_god_patterns_2026-10-24.md §1.3; review package §6 A "Tides through the hull").
//
// The wedge (RM_TerritoryKernel.Allocate) turns a sector about the fixtures' centroid. A TIDE instead orders the union
// by door-graph distance and lets the louder claimant hold the first k of that order, k breathing in and out on the
// boundary's own clock: colour seeps along corridors and through doors, floods a room and then the next, and never
// rotates. Owner ruling §9.15 (2026-10-23): "authored pairings for canon pairs (Ishko/Ta'Baa, Sh'kaar hunting Ishko),
// the leader's shape elsewhere". So:
//   * a PAIRING RULE (authored data, carried by the signature defs) names two signatures, the anchor each tides from,
//     and optionally that one HUNTS the other. Paired, the order is d_mine - d_theirs: each holds its own end of the
//     ship and the front meets between the two anchors (Ishko on Core and Ta'Baa on Threshold meet at the threshold);
//   * unpaired, the LEADER's shape decides alone: a Wedge leader keeps the wedge, a Tide leader floods from its own
//     anchor and the other claimant holds whatever the water has not reached;
//   * a hunter's share does not follow rank: it surges to MaxLeadShare, STANDS there (the beam pausing over the room it
//     found), and falls back, so Sh'kaar closes on Ishko's core whichever of the two is louder.
// Laws kept: both claimants always hold at least one fixture and the quieter at least a fifth at the widest swing
// (MinTideShare/MaxLeadShare); the share is monotone within each half of the turn, so a fixture changes hands at most
// twice a turn (hysteresis is structural, as in the TIDE layer); between clock steps nothing is reallocated.
// Degenerate canvases fall back to the wedge (design §5 (c): "open plan (TIDE degenerates to WEDGE)"): no graph, one
// room, or every fixture of the union in one room. CIRCUIT has no conduit graph yet and runs as TIDE(Power).
// Pure: no game types. The selftest (TerritoryTests.cs) drives every function here.
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_ShapeKind { Wedge = 0, Tide, Circuit }

    /// <summary>A claimant's own territory shape (the signature's &lt;territory&gt;). default = the wedge.</summary>
    public struct RM_TerritoryShape
    {
        public RM_ShapeKind kind;
        public RM_Anchor anchor;

        public static RM_TerritoryShape Wedge => default(RM_TerritoryShape);
        public static RM_TerritoryShape Tide(RM_Anchor a) => new RM_TerritoryShape { kind = RM_ShapeKind.Tide, anchor = a };

        /// <summary>CIRCUIT runs as TIDE(Power) until a conduit graph exists (design §1.3 fallback).</summary>
        public RM_Anchor TideAnchor => kind == RM_ShapeKind.Circuit ? RM_Anchor.Power : anchor;
        public bool IsTide => kind == RM_ShapeKind.Tide || kind == RM_ShapeKind.Circuit;
    }

    /// <summary>One authored canon pairing: `a` tides from anchorA, `b` from anchorB; aHunts = a's front hunts b.</summary>
    public struct RM_PairingRule
    {
        public string a, b;
        public RM_Anchor anchorA, anchorB;
        public bool aHunts;
        public string label;
    }

    public enum RM_PlanKind { Wedge = 0, LeaderTide, PairedTide }

    /// <summary>How the two front claimants share the union this turn.</summary>
    public struct RM_TerritoryPlan
    {
        public RM_PlanKind kind;
        public RM_Anchor leadAnchor, otherAnchor;
        public int hunter;          // -1 none, 0 the louder claimant hunts, 1 the quieter one hunts
        public string rule;         // the pairing's label, or null

        public override string ToString() => kind + (kind == RM_PlanKind.Wedge ? "" : "(" + leadAnchor
            + (kind == RM_PlanKind.PairedTide ? "/" + otherAnchor : "") + ")") + (hunter >= 0 ? " hunter=" + hunter : "") + (rule != null ? " [" + rule + "]" : "");
    }

    public static class RM_TerritoryShapes
    {
        public const float MinTideShare = 0.2f;   // = 1 - MaxLeadShare: at the widest swing the smaller side keeps a fifth
        public const float Swing = 0.2f;          // the tide's share swings leadShare +- Swing over one turn
        public const float HuntRise = 0.35f, HuntStand = 0.25f;   // fractions of a turn: surge, stand at the peak, fall
        public const double RaggedHops = 2.0;     // `ragged` jitters each fixture by up to ragged * this many hops

        // ---------------------------------------------------------------- the plan (§9.15)

        /// <summary>Paired rule first (either order), else the leader's own shape. Pure, order-independent in `rules`
        /// (the first matching rule by (a, b) ordinal wins, so two contradicting rules resolve the same way every time).</summary>
        public static RM_TerritoryPlan Plan(string leadSig, RM_TerritoryShape leadShape, string otherSig, IList<RM_PairingRule> rules)
        {
            RM_PairingRule? hit = null;
            bool leadIsA = false;
            if (rules != null && leadSig != null && otherSig != null && leadSig != otherSig)
                foreach (RM_PairingRule r in rules)
                {
                    bool fwd = r.a == leadSig && r.b == otherSig, rev = r.a == otherSig && r.b == leadSig;
                    if (!fwd && !rev) continue;
                    if (hit == null || string.CompareOrdinal(r.a + "\u0001" + r.b, hit.Value.a + "\u0001" + hit.Value.b) < 0
                        || (r.a == hit.Value.a && r.b == hit.Value.b && string.CompareOrdinal(r.label ?? "", hit.Value.label ?? "") < 0))
                    { hit = r; leadIsA = fwd; }
                }
            if (hit != null)
            {
                RM_PairingRule r = hit.Value;
                return new RM_TerritoryPlan
                {
                    kind = RM_PlanKind.PairedTide,
                    leadAnchor = leadIsA ? r.anchorA : r.anchorB,
                    otherAnchor = leadIsA ? r.anchorB : r.anchorA,
                    hunter = r.aHunts ? (leadIsA ? 0 : 1) : -1,
                    rule = r.label ?? (r.a + "/" + r.b),
                };
            }
            if (leadShape.IsTide)
                return new RM_TerritoryPlan { kind = RM_PlanKind.LeaderTide, leadAnchor = leadShape.TideAnchor, hunter = -1 };
            return new RM_TerritoryPlan { kind = RM_PlanKind.Wedge, hunter = -1 };
        }

        // ---------------------------------------------------------------- the share's clock

        /// <summary>The louder claimant's share of the union at this clock step. A plain tide swings round leadShare on a
        /// cosine; a hunt surges the HUNTER to MaxLeadShare, stands, and falls back to a tenth under its rank share.
        /// Monotone in each half of the turn either way.</summary>
        public static double Share(long step, int pairSalt, float leadShare, int hunter)
        {
            float ls = Math.Min(RM_TerritoryKernel.MaxLeadShare, Math.Max(RM_TerritoryKernel.MinLeadShare, float.IsNaN(leadShare) ? 0.5f : leadShare));
            double x = ((step % RM_TerritoryKernel.StepsPerTurn) + RM_TerritoryKernel.StepsPerTurn) % RM_TerritoryKernel.StepsPerTurn
                       / (double)RM_TerritoryKernel.StepsPerTurn + RM_SchemeKernel.Frac01(pairSalt, 19);
            x -= Math.Floor(x);
            if (hunter < 0)
                return Clamp(ls + Swing * Math.Cos(2 * Math.PI * x));
            double hb = hunter == 0 ? ls : 1.0 - ls;
            double lo = Math.Max(MinTideShare, hb - 0.1), hi = RM_TerritoryKernel.MaxLeadShare;
            double q;
            if (x < HuntRise) q = 0.5 - 0.5 * Math.Cos(Math.PI * x / HuntRise);
            else if (x < HuntRise + HuntStand) q = 1;
            else if (x < 2 * HuntRise + HuntStand) q = 0.5 + 0.5 * Math.Cos(Math.PI * (x - HuntRise - HuntStand) / HuntRise);
            else q = 0;
            double hs = lo + (hi - lo) * q;
            return Clamp(hunter == 0 ? hs : 1.0 - hs);
        }

        private static double Clamp(double s) => Math.Min(RM_TerritoryKernel.MaxLeadShare, Math.Max(MinTideShare, s));

        /// <summary>Fixtures the louder claimant holds: round(share * n), both sides keeping one with n &gt;= 2.</summary>
        public static int TideCount(int n, double share)
        {
            if (n <= 0) return 0;
            if (n == 1) return 1;
            int k = (int)Math.Round(n * share, MidpointRounding.AwayFromZero);
            return Math.Max(1, Math.Min(n - 1, k));
        }

        // ---------------------------------------------------------------- the order the water fills

        /// <summary>Is this union a canvas a tide can read? Needs a graph of two or more rooms and the union spread over
        /// at least two distinct nodes (outdoors counts as one).</summary>
        public static bool TideReadable(IList<int> nodes, RM_RoomGraph graph)
        {
            if (graph == null || graph.Count <= 1 || nodes == null || nodes.Count < 2) return false;
            int first = nodes[0];
            for (int i = 1; i < nodes.Count; i++) if (nodes[i] != first) return true;
            return false;
        }

        /// <summary>One fixture's place in the flood, compared lexicographically: lower fills first.</summary>
        public struct FloodKey
        {
            public double primary;    // paired: d_lead - d_other (+ ragged jitter); leader tide: d_lead (+ jitter)
            public double between;    // paired: d_lead / (d_lead + d_other), so inside one shell the fixtures nearer the
                                      // lead's anchor fill first and the other's anchor is the last thing it reaches
            public double room;       // a stable per-room hash, so an equal-key room fills as a block, not by id
        }

        public static FloodKey[] Keys(IList<int> ids, IList<int> nodes, RM_RoomGraph graph, RM_TerritoryPlan plan, float ragged)
        {
            int n = ids.Count;
            var key = new FloodKey[n];
            float rg = Math.Min(RM_TerritoryKernel.MaxRagged, Math.Max(0f, float.IsNaN(ragged) ? 0f : ragged));
            bool paired = plan.kind == RM_PlanKind.PairedTide;
            for (int i = 0; i < n; i++)
            {
                int node = nodes[i];
                double dl = graph.Distance(plan.leadAnchor, node), d = dl, bt = 0;
                if (paired)
                {
                    double dot = graph.Distance(plan.otherAnchor, node);
                    d -= dot;
                    bt = dl + dot > 0 ? dl / (dl + dot) : 0.5;
                }
                int roomKey = node >= 0 && node < graph.Count ? graph.roomIds[node] : int.MinValue + 7;
                key[i] = new FloodKey
                {
                    primary = d + (rg > 0 ? rg * RaggedHops * (RM_SchemeKernel.Frac01(ids[i], 31) - 0.5) : 0),
                    between = bt,
                    room = RM_SchemeKernel.Frac01(roomKey, 29),
                };
            }
            return key;
        }

        public static int[] Order(IList<int> ids, FloodKey[] key)
        {
            int n = ids.Count;
            var order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            Array.Sort(order, (p, q) =>
            {
                int c = key[p].primary.CompareTo(key[q].primary);
                if (c == 0) c = key[p].between.CompareTo(key[q].between);
                if (c == 0) c = key[p].room.CompareTo(key[q].room);
                return c != 0 ? c : ids[p].CompareTo(ids[q]);
            });
            return order;
        }

        /// <summary>Who holds each fixture of the union at this step under the plan: true = the louder claimant. Falls
        /// back to the wedge when the plan is Wedge or the canvas cannot read a tide. Pure.</summary>
        public static bool[] Allocate(IList<int> ids, IList<float> x, IList<float> z, IList<int> nodes, RM_RoomGraph graph,
                                      long step, int pairSalt, RM_TerritoryTuning tuning, RM_TerritoryPlan plan)
        {
            if (plan.kind == RM_PlanKind.Wedge || !TideReadable(nodes, graph))
                return RM_TerritoryKernel.Allocate(ids, x, z, step, pairSalt, tuning);
            int n = ids.Count;
            var lead = new bool[n];
            RM_TerritoryTuning t = RM_TerritoryTuning.Clamp(tuning);
            int[] order = Order(ids, Keys(ids, nodes, graph, plan, t.ragged));
            int k = TideCount(n, Share(step, pairSalt, t.leadShare, plan.hunter));
            for (int i = 0; i < k; i++) lead[order[i]] = true;
            return lead;
        }

        /// <summary>Does this plan actually run as a tide on this canvas (for the proof's counters)?</summary>
        public static bool RunsAsTide(RM_TerritoryPlan plan, IList<int> nodes, RM_RoomGraph graph) =>
            plan.kind != RM_PlanKind.Wedge && TideReadable(nodes, graph);
    }
}
