using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // FOOTPRINT_TRACK_GRID_1 — a read-only state window on the grid for the
    // modcheck suite (CreatureBehaviors/validation.py). Public static fields
    // so `jawa/mod_settings_field typeName=RimMandrake.CreatureBehaviors.
    // RM_TrackGridDiag action=list` reads them with no new bridge tool. The
    // counters are session-scoped (never saved) and cost an increment per
    // print; nothing reads them in play.
    //
    // A chain reads them BEFORE and AFTER driving a walk and asserts on the
    // deltas, so an earlier session's numbers never satisfy a check.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_TrackGridDiag
    {
        /// <summary>Ground cell entries the postfix saw with tracks on (any surface or none).</summary>
        public static int stepsSeen;
        /// <summary>Prints laid (any map).</summary>
        public static int printsWritten;
        /// <summary>Prints laid by a walker that was invisible at the time.</summary>
        public static int invisiblePrintsWritten;
        /// <summary>Prints removed through the erase API (ClearCell / ClearRect; not sweeps or ClearAll).</summary>
        public static int cleared;

        public static string lastPrintPawn = "";
        public static string lastPrintCell = "";
        public static bool lastPrintInvisible;
        public static string lastPrintTexPath = "";
        /// <summary>Records held by the grid of the map that took the last print, right after it.</summary>
        public static int lastPoolCount;
        public static int lastPoolCapacity;
        /// <summary>Flagged-invisible records held by that grid, right after the last print.</summary>
        public static int lastPoolInvisible;

        // Per-walker tally (ThingID -> [prints, invisible prints]). The global counters above cannot say WHO laid a
        // print, so any other pawn on the strip (wildlife, a visitor, a stray colonist) inflates a control arm or
        // overwrites lastPrintInvisible; a suite that needs attribution reads PrintsBy(pawnId) instead.
        private static readonly Dictionary<string, int[]> byPawn = new Dictionary<string, int[]>();

        /// <summary>"prints|invisiblePrints|lastInvisible" laid by one pawn since session start (static_call arg: its ThingID).</summary>
        public static string PrintsBy(string pawnId)
        {
            int[] v;
            if (!byPawn.TryGetValue((pawnId ?? "").Trim(), out v)) return "0|0|false";
            return v[0] + "|" + v[1] + "|" + (v[2] == 1 ? "true" : "false");
        }

        internal static void Noted(RM_MapComponent_TrackGrid grid, Pawn pawn, IntVec3 c, bool invisible, string tex)
        {
            printsWritten++;
            int[] mine;
            if (!byPawn.TryGetValue(pawn.ThingID, out mine)) byPawn[pawn.ThingID] = mine = new int[3];
            mine[0]++;
            if (invisible) mine[1]++;
            mine[2] = invisible ? 1 : 0;
            if (invisible) invisiblePrintsWritten++;
            lastPrintPawn = pawn.ThingID;
            lastPrintCell = c.x + "," + c.z;
            lastPrintInvisible = invisible;
            lastPrintTexPath = tex ?? "";
            RM_TrackPool pool = grid.Pool;
            lastPoolCount = pool?.Count ?? 0;
            lastPoolCapacity = pool?.Capacity ?? 0;
            lastPoolInvisible = pool?.InvisibleCount ?? 0;
        }
    }
}
