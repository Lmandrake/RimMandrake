using System;
using System.Collections.Generic;

namespace RimMandrake.StructureInjections
{
    // Verse-free decisions of mandrake.rm.structureinjections: where a plan lands, how a RUN walks to the map edge, which order things are spawned
    // in, what a directive's direction / mode / pawn state means. GenStep_RimplacePlan calls these; the seeded fuzz under Source/SelfTest compiles
    // THIS file (and RimplacePlan.cs, which is just as engine-free) directly - no `using Verse;` here.
    public static class RM_PlanKernel
    {
        /// <summary>The plan-to-map translation. The anchor (a Thing found on the map) beats centring on the map; both need a FOOTPRINT; otherwise the
        /// plan lands at the explicit offset alone. Integer halves, exactly as the plan compiler's own centre.</summary>
        public static void Offset(bool hasFootprint, int fx, int fz, int fw, int fh, bool hasAnchor, int anchorX, int anchorZ,
            bool centerOnMap, int mapCenterX, int mapCenterZ, int offsetX, int offsetZ, out int dx, out int dz)
        {
            dx = offsetX; dz = offsetZ;
            if (!hasFootprint) return;
            int pcx = fx + fw / 2, pcz = fz + fh / 2;
            if (hasAnchor) { dx = anchorX - pcx + offsetX; dz = anchorZ - pcz + offsetZ; }
            else if (centerOnMap) { dx = mapCenterX - pcx + offsetX; dz = mapCenterZ - pcz + offsetZ; }
        }

        /// <summary>N,E,S,W as 0..3; anything else (including empty, or a longer string that merely contains N/E/S/W) is -1.</summary>
        public static int DirIndex(string dir)
        {
            if (dir == null || dir.Length != 1) return -1;
            return "NESW".IndexOf(dir[0]);
        }

        public static void DirStep(int dirIndex, out int sx, out int sz)
        {
            sx = 0; sz = 0;
            switch (dirIndex)
            {
                case 0: sz = 1; break;
                case 1: sx = 1; break;
                case 2: sz = -1; break;
                case 3: sx = -1; break;
                default: throw new ArgumentOutOfRangeException("dirIndex");
            }
        }

        public enum ClearMode { Soft, All, Unknown }

        public static ClearMode ParseClearMode(string mode)
        {
            if (mode == "all") return ClearMode.All;
            if (mode == "soft") return ClearMode.Soft;
            return ClearMode.Unknown;
        }

        public enum PawnState { Alive, Dead, Dessicated, Unknown }

        public static PawnState ParsePawnState(string state)
        {
            switch (state)
            {
                case "alive": return PawnState.Alive;
                case "dead": return PawnState.Dead;
                case "dessicated":
                case "skeleton": return PawnState.Dessicated;   // RimWorld's rot stages end at Dessicated: a skeleton is the terminal stage, not a separate state
                default: return PawnState.Unknown;
            }
        }

        public enum FactionKind { Wild, Named, Refused }

        /// <summary>"player" is refused (a mapgen template must never spawn a colonist); "wild" and blank mean no faction; anything else names a FactionDef.</summary>
        public static FactionKind ClassifyFaction(string faction)
        {
            if (faction == "player") return FactionKind.Refused;
            if (string.IsNullOrEmpty(faction) || faction == "wild") return FactionKind.Wild;
            return FactionKind.Named;
        }

        public enum RunProbe { Free, AlreadyThere, Blocked }

        /// <summary>Walks from (x,z) toward the map edge, calling `place` on each cell not already holding the run's def, stopping at the first Blocked cell.
        /// Returns how many cells were walked before stopping (not how many placed). The start cell outside the map walks nothing.</summary>
        public static int WalkRun(int x, int z, int dirIndex, int width, int height, Func<int, int, RunProbe> probe, Action<int, int> place)
        {
            int sx, sz;
            DirStep(dirIndex, out sx, out sz);
            int walked = 0;
            while (x >= 0 && z >= 0 && x < width && z < height)
            {
                RunProbe p = probe(x, z);
                if (p == RunProbe.Blocked) break;
                if (p == RunProbe.Free) place(x, z);
                walked++;
                x += sx; z += sz;
            }
            return walked;
        }

        /// <summary>Things that transmit power first (a connector binds to the nearest transmitter AT SPAWN), original order kept within each group.</summary>
        public static List<T> TransmittersFirst<T>(IList<T> things, Func<T, bool> transmits)
        {
            var first = new List<T>();
            var rest = new List<T>();
            foreach (T t in things) (transmits(t) ? first : rest).Add(t);
            first.AddRange(rest);
            return first;
        }
    }
}
