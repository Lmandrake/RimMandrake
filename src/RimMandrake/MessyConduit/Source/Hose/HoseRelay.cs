using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;

namespace RimMandrake.MessyConduit.Hose
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
        /// <summary>The relay's intake cells, in side order E, N, W, S and along each side.</summary>
        public static List<Cell> IntakeCells(HoseReelRect relay)
        {
            var o = new List<Cell>();
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s)) o.Add(e + s);
            return o;
        }

        public static bool IsIntakeOf(HoseReelRect relay, Cell c) => IntakeCells(relay).Contains(c);

        /// <summary>The intake a hose from <paramref name="fromMouth"/> ends on, or false when every intake is blocked.</summary>
        public static bool TryIntake(HoseReelRect relay, V2 fromMouth, Func<Cell, bool> walkable, out Cell intake)
        {
            intake = new Cell(0, 0);
            double best = double.MaxValue;
            bool found = false;
            foreach (Cell c in IntakeCells(relay))
            {
                if (walkable != null && !walkable(c)) continue;
                double d = V2.Dist(c.Centre, fromMouth);
                if (d < best - 1e-9) { best = d; intake = c; found = true; }
            }
            return found;
        }

        /// <summary>The unit step from the intake cell into the relay (zero when the cell is not an intake).</summary>
        public static Cell SideInto(HoseReelRect relay, Cell intake)
        {
            foreach (Cell s in HosePortRule.SideOrder)
                foreach (Cell e in relay.EdgeCells(s))
                    if (e + s == intake) return new Cell(-s.X, -s.Z);
            return new Cell(0, 0);
        }

        /// <summary>Where the hose ends: the midpoint of the edge the intake cell shares with the relay.</summary>
        public static V2 IntakePoint(HoseReelRect relay, Cell intake)
        {
            Cell d = SideInto(relay, intake);
            return intake.Centre + new V2(d.X * 0.5, d.Z * 0.5);
        }

        /// <summary>Index of the relay a hose whose free end is on <paramref name="far"/> feeds, or -1. self is skipped.</summary>
        public static int RelayOf(Cell far, IList<HoseReelRect> reels, int self)
        {
            for (int i = 0; i < reels.Count; i++)
                if (i != self && IsIntakeOf(reels[i], far)) return i;
            return -1;
        }

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
}
