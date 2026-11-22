using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decision of the firefoam sprayer carrier (PyrelandsFoamPath.cs, bar firefoam_sprayer_reaches_the_fruit):
    // whether a pawn holding RM_FE_FirefoamSprayer foams now, and which burning cell it aims at. The game calls these with the
    // pawn's own state, its path ahead (Pawn_PathFollower.curPath) and two cell tests; the offline fuzz drives the same code.
    //
    // The rule (RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH, 2026-11-22): a carrier foams the fire in its
    // way. "In its way" is a burning cell that is the carrier's own cell, a cell on its path ahead, or a neighbour of either
    // (vanilla fire spreads to a neighbour cell, and a pawn beside a burning cell is the next thing it reaches). It aims at
    // the first such cell in path order that the sprayer can hit from where the carrier stands. A fire away from the path is
    // not the carrier's business: it does not foam a burn line it only walks past at a distance.

    public enum RM_FoamGate { Foam, Disabled, NoSprayer, NotOurs, Drafted, Incapable, Busy, NotReady }

    public static class RM_FoamPathKernel
    {
        /// <summary>Path cells read ahead. Source: vanilla's own danger read of a new path looks 20 cells ahead
        /// (Pawn_PathFollower.PatherTick, PeekNextCells(20) then KnownDangerAt). A fire further on is read again on a later tick
        /// as the carrier walks; the sprayer's range (9.9) cannot reach most of it anyway.</summary>
        public const int LookAheadCells = 20;

        /// <summary>The 8 neighbours, in a fixed order (the four sides first, then the corners), so the aim is deterministic.</summary>
        private static readonly int[] NX = { 0, 1, 0, -1, 1, 1, -1, -1 };
        private static readonly int[] NZ = { 1, 0, -1, 0, 1, -1, -1, 1 };

        /// <summary>Whether this pawn may foam at all now. Order of the reasons is the order they are checked.
        /// enabled: the "Sprayer carriers foam the fire in their way" switch. ours: a humanlike of the player's faction (a
        /// visitor or raider who picked one up keeps vanilla behaviour). drafted: the player aims a drafted pawn himself.
        /// incapable: downed, in a mental state, or burning (vanilla's ExtinguishSelf comes first). busy: the stance is not
        /// mobile (already aiming or cooling down). ready: the sprayer's verb is available.</summary>
        public static RM_FoamGate Gate(bool enabled, bool carriesSprayer, bool ours, bool drafted, bool incapable, bool busy, bool ready)
        {
            if (!enabled) return RM_FoamGate.Disabled;
            if (!carriesSprayer) return RM_FoamGate.NoSprayer;
            if (!ours) return RM_FoamGate.NotOurs;
            if (drafted) return RM_FoamGate.Drafted;
            if (incapable) return RM_FoamGate.Incapable;
            if (busy) return RM_FoamGate.Busy;
            if (!ready) return RM_FoamGate.NotReady;
            return RM_FoamGate.Foam;
        }

        /// <summary>The cell to foam, or false. (px, pz): the carrier's cell. pathX/pathZ: the path cells ahead in walking order
        /// (the next cell first; empty when standing still); only the first LookAheadCells are read. burning(x, z): a free fire
        /// stands on the cell. canHit(x, z): the sprayer can hit the cell from the carrier's cell (range and line of sight).
        /// Reads, in order: the carrier's cell and its neighbours, then each path cell and its neighbours; returns the first
        /// burning cell that can be hit.</summary>
        public static bool PickTarget(int px, int pz, IList<int> pathX, IList<int> pathZ, Func<int, int, bool> burning,
            Func<int, int, bool> canHit, out int tx, out int tz)
        {
            int n = pathX == null || pathZ == null ? 0 : Math.Min(Math.Min(pathX.Count, pathZ.Count), LookAheadCells);
            for (int i = -1; i < n; i++)
            {
                int cx = i < 0 ? px : pathX[i];
                int cz = i < 0 ? pz : pathZ[i];
                if (burning(cx, cz) && canHit(cx, cz))
                {
                    tx = cx;
                    tz = cz;
                    return true;
                }
                for (int k = 0; k < 8; k++)
                {
                    int ax = cx + NX[k], az = cz + NZ[k];
                    if (burning(ax, az) && canHit(ax, az))
                    {
                        tx = ax;
                        tz = az;
                        return true;
                    }
                }
            }
            tx = tz = 0;
            return false;
        }

        /// <summary>True when (x, z) is "in the way": the carrier's cell, a path cell within LookAheadCells, or a neighbour of
        /// either. The fuzz's oracle for "a target is never a fire away from the path".</summary>
        public static bool InTheWay(int x, int z, int px, int pz, IList<int> pathX, IList<int> pathZ)
        {
            int n = pathX == null || pathZ == null ? 0 : Math.Min(Math.Min(pathX.Count, pathZ.Count), LookAheadCells);
            for (int i = -1; i < n; i++)
            {
                int cx = i < 0 ? px : pathX[i];
                int cz = i < 0 ? pz : pathZ[i];
                if (Math.Abs(x - cx) <= 1 && Math.Abs(z - cz) <= 1) return true;
            }
            return false;
        }
    }
}
