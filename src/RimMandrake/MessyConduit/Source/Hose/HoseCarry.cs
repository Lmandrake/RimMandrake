// Colonist-carried hose, stage S1 (design/RimMandrake/hose_carry_design_2026-10-04.md sections 3, 5, 8): the state enum,
// the transition table and the walked-trail rule. Verse-free pure C#, also compiled by the SelfTest. The reel (S2) and the
// job drivers (S3) call these; nothing here knows a Pawn.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>Saved on the reel (appended order only).</summary>
    public enum HoseCarryState { Stored = 0, Carrying = 1, Dropped = 2, Laid = 3, Retracting = 4 }

    /// <summary>Everything that can happen to a hose's state (design section 3 table, one event per row).</summary>
    public enum HoseCarryEvent
    {
        Grab, Step, Stretch, Stow, SetDown, Interrupt, PickUp, Wind, Replan, ReplanFail, WindDone, WindInterrupt, ReelGone, DevLay, DevReelIn
    }

    public static class HoseCarryTable
    {
        private static void Add(Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> t, HoseCarryEvent e, HoseCarryState to, params HoseCarryState[] from)
        {
            foreach (HoseCarryState f in from) t[(f, e)] = to;
        }

        public static Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> Build()
        {
            var t = new Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState>();
            const HoseCarryState S = HoseCarryState.Stored, C = HoseCarryState.Carrying, D = HoseCarryState.Dropped, L = HoseCarryState.Laid, R = HoseCarryState.Retracting;
            Add(t, HoseCarryEvent.Grab, C, S);
            Add(t, HoseCarryEvent.Step, C, C);
            Add(t, HoseCarryEvent.Stretch, D, C);
            Add(t, HoseCarryEvent.Stow, S, C);
            Add(t, HoseCarryEvent.SetDown, L, C);
            Add(t, HoseCarryEvent.Interrupt, D, C);
            Add(t, HoseCarryEvent.PickUp, C, L, D);
            Add(t, HoseCarryEvent.Wind, R, L, D);
            Add(t, HoseCarryEvent.Replan, L, L);
            Add(t, HoseCarryEvent.Replan, D, D);
            Add(t, HoseCarryEvent.ReplanFail, R, L, D);
            Add(t, HoseCarryEvent.WindDone, S, R);
            Add(t, HoseCarryEvent.WindInterrupt, D, R);
            Add(t, HoseCarryEvent.ReelGone, S, S, C, D, L, R);
            Add(t, HoseCarryEvent.DevLay, L, S, L, D);
            Add(t, HoseCarryEvent.DevReelIn, S, S, L, D);
            return t;
        }

        public static readonly Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> Default = Build();

        /// <summary>The next state, or null when the pair is refused.</summary>
        public static HoseCarryState? Next(HoseCarryState s, HoseCarryEvent e, Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> table = null)
        {
            return (table ?? Default).TryGetValue((s, e), out HoseCarryState to) ? to : (HoseCarryState?)null;
        }
    }

    public enum TrailStep { Unchanged, Appended, Truncated, Stowed, Stretched }

    /// <summary>The cells the carrier actually walked (design section 8). Trail[0] is the reel's start cell.</summary>
    public sealed class HoseTrail
    {
        public readonly List<Cell> Cells = new List<Cell>();
        public V2 Mouth;
        public double MaxLength;
        /// <summary>The section 8 backtrack rule; false only in the selftest's can-fail mutant.</summary>
        public bool TruncateOnRevisit = true;

        public HoseTrail(V2 mouth, double maxLength) { Mouth = mouth; MaxLength = maxLength; }

        public Cell Last => Cells[Cells.Count - 1];

        public void Begin(Cell start) { Cells.Clear(); Cells.Add(start); }

        /// <summary>The trail pulled taut from the mouth (any-angle, never through a wall or pinched diagonal), the same
        /// geometry HoseMath.RoutePulled uses, but over the walked cells.</summary>
        public List<V2> Pulled(CordWorld w)
        {
            var pts = new List<V2> { Mouth };
            foreach (Cell c in Cells) if (pts.Count == 1 ? V2.Dist(c.Centre, Mouth) > 1e-9 : true) pts.Add(c.Centre);
            var o = new List<V2> { pts[0] };
            int a = 0;
            while (a < pts.Count - 1)
            {
                int b = a + 1;
                for (int j = pts.Count - 1; j > a + 1; j--) if (HoseMath.SegmentClear(w, pts[a], pts[j])) { b = j; break; }
                o.Add(pts[b]);
                a = b;
            }
            return o;
        }

        public double PulledLength(CordWorld w) => Geo.Length(Pulled(w));

        /// <summary>The carrier entered cell c. Backtrack: a cell already on the trail truncates to it (index 0 = back at the
        /// reel: Stowed). Otherwise append, then pull taut; past MaxLength the append is undone (Stretched): the end
        /// lies at the last cell that fitted.</summary>
        public TrailStep Step(Cell c, CordWorld w)
        {
            if (Cells.Count > 0 && Cells[Cells.Count - 1] == c) return TrailStep.Unchanged;
            if (TruncateOnRevisit)
            {
                int i = Cells.IndexOf(c);
                if (i >= 0)
                {
                    Cells.RemoveRange(i + 1, Cells.Count - i - 1);
                    return i == 0 ? TrailStep.Stowed : TrailStep.Truncated;
                }
            }
            Cells.Add(c);
            if (PulledLength(w) > MaxLength + 1e-9)
            {
                Cells.RemoveAt(Cells.Count - 1);
                return TrailStep.Stretched;
            }
            return TrailStep.Appended;
        }

        /// <summary>Winding w cells in: drop trailing cells until the pulled length is at most (length - w). Keeps one cell.</summary>
        public void ShortenBy(double wound, CordWorld w)
        {
            double target = PulledLength(w) - wound;
            while (Cells.Count > 1 && PulledLength(w) > target + 1e-9) Cells.RemoveAt(Cells.Count - 1);
        }

        /// <summary>Retract draw: the polyline clipped at arc length (total - wound), one interpolated end point.</summary>
        public static List<V2> Clip(IList<V2> p, double wound)
        {
            double keep = Math.Max(0, Geo.Length(p) - Math.Max(0, wound));
            var o = new List<V2> { p[0] };
            double acc = 0;
            for (int i = 1; i < p.Count; i++)
            {
                double seg = V2.Dist(p[i - 1], p[i]);
                if (acc + seg >= keep - 1e-12)
                {
                    double f = seg < 1e-12 ? 0 : (keep - acc) / seg;
                    if (f > 1e-12) o.Add(p[i - 1] + (p[i] - p[i - 1]) * f);
                    return o;
                }
                o.Add(p[i]);
                acc += seg;
            }
            return o;
        }
    }

    /// <summary>The reel's carry state with its trail, the invariants of design section 3 held by construction.</summary>
    public sealed class HoseCarryMachine
    {
        public HoseCarryState State = HoseCarryState.Stored;
        public readonly HoseTrail Trail;
        public bool HasCarrier, HasWinder, AutoRetract, PendingKept;
        public double Wound;
        public readonly CordWorld World;
        public Dictionary<(HoseCarryState, HoseCarryEvent), HoseCarryState> Table = HoseCarryTable.Default;

        public HoseCarryMachine(CordWorld w, V2 mouth, double maxLength) { World = w; Trail = new HoseTrail(mouth, maxLength); }

        public Cell? Far => State == HoseCarryState.Laid || State == HoseCarryState.Dropped ? Trail.Last : (Cell?)null;

        private bool Go(HoseCarryEvent e)
        {
            HoseCarryState? n = HoseCarryTable.Next(State, e, Table);
            if (n == null) return false;
            State = n.Value;
            return true;
        }

        public bool Grab(Cell start)
        {
            if (!Go(HoseCarryEvent.Grab)) return false;
            Trail.Begin(start); HasCarrier = true; Wound = 0; AutoRetract = false;
            return true;
        }

        /// <summary>The carrier entered a cell.</summary>
        public bool CarrierStep(Cell c)
        {
            if (State != HoseCarryState.Carrying) return false;
            TrailStep r = Trail.Step(c, World);
            if (r == TrailStep.Stowed) { Go(HoseCarryEvent.Stow); Trail.Cells.Clear(); HasCarrier = false; }
            else if (r == TrailStep.Stretched) { Go(HoseCarryEvent.Stretch); HasCarrier = false; PendingKept = false; }
            else Go(HoseCarryEvent.Step);
            return true;
        }

        public bool SetDown() { if (!Go(HoseCarryEvent.SetDown)) return false; HasCarrier = false; PendingKept = false; return true; }
        public bool Interrupt() { if (!Go(HoseCarryEvent.Interrupt)) return false; HasCarrier = false; PendingKept = true; return true; }
        public bool PickUp() { if (!Go(HoseCarryEvent.PickUp)) return false; HasCarrier = true; return true; }
        public bool BeginWind() { if (!Go(HoseCarryEvent.Wind)) return false; HasWinder = true; AutoRetract = false; Wound = 0; return true; }

        /// <summary>Wind cells in; reaching the trail's pulled length stows the hose.</summary>
        public bool WindBy(double cells)
        {
            if (State != HoseCarryState.Retracting) return false;
            Wound += cells;
            if (Wound >= Trail.PulledLength(World) - 1e-9) { Go(HoseCarryEvent.WindDone); Trail.Cells.Clear(); HasWinder = false; AutoRetract = false; Wound = 0; }
            return true;
        }

        public bool WindInterrupt()
        {
            if (!Go(HoseCarryEvent.WindInterrupt)) return false;
            Trail.ShortenBy(Wound, World); HasWinder = false; AutoRetract = false; Wound = 0;
            return true;
        }

        /// <summary>The 250-tick corridor check re-planned: the route replaces the trail if it fits, else auto-retract.</summary>
        public bool Replan(List<Cell> route)
        {
            if (State != HoseCarryState.Laid && State != HoseCarryState.Dropped) return false;
            var t = new HoseTrail(Trail.Mouth, Trail.MaxLength);
            t.Cells.AddRange(route);
            if (route.Count == 0 || t.PulledLength(World) > Trail.MaxLength + 1e-9)
            {
                Go(HoseCarryEvent.ReplanFail); AutoRetract = true; HasWinder = false; Wound = 0;
                return true;
            }
            Go(HoseCarryEvent.Replan);
            Trail.Cells.Clear(); Trail.Cells.AddRange(route);
            return true;
        }

        public bool ReelGone() { Go(HoseCarryEvent.ReelGone); Trail.Cells.Clear(); HasCarrier = HasWinder = AutoRetract = false; Wound = 0; return true; }

        /// <summary>DEV instant lay of a planned route; refused when it does not fit.</summary>
        public bool DevLay(List<Cell> route)
        {
            if (route.Count == 0 || HoseCarryTable.Next(State, HoseCarryEvent.DevLay, Table) == null) return false;
            var t = new HoseTrail(Trail.Mouth, Trail.MaxLength);
            t.Cells.AddRange(route);
            if (t.PulledLength(World) > Trail.MaxLength + 1e-9) return false;
            Go(HoseCarryEvent.DevLay);
            Trail.Cells.Clear(); Trail.Cells.AddRange(route);
            HasCarrier = HasWinder = AutoRetract = false;
            return true;
        }

        public bool DevReelIn() { if (!Go(HoseCarryEvent.DevReelIn)) return false; Trail.Cells.Clear(); return true; }

        /// <summary>The section 3 invariants; null when all hold, else the first broken one.</summary>
        public string Invariant()
        {
            if ((State == HoseCarryState.Carrying) != HasCarrier) return "Carrying <=> carrier";
            if ((State == HoseCarryState.Retracting && !AutoRetract) != HasWinder) return "Retracting(non-auto) <=> winder";
            if (State != HoseCarryState.Stored && Trail.Cells.Count < 1) return "trail >= 1 outside Stored";
            if (State == HoseCarryState.Stored && Trail.Cells.Count != 0) return "Stored has no trail";
            if (State != HoseCarryState.Stored && Trail.PulledLength(World) > Trail.MaxLength + 1e-9) return "pulled length <= MaxLength";
            if ((State == HoseCarryState.Laid || State == HoseCarryState.Dropped) && Far.Value != Trail.Last) return "far == trail.Last";
            return null;
        }
    }
}
