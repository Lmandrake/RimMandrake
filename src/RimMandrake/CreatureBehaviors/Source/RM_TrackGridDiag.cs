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

        internal static void Noted(RM_MapComponent_TrackGrid grid, Pawn pawn, IntVec3 c, bool invisible, string tex)
        {
            printsWritten++;
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
