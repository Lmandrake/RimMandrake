using System;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>How far shock reaches (owner 2026-11-06, OWNER tsn 1793996551266756043: "Every sparking end shocks, but settable
    /// in settings to those three options: None, only downed lines, or all."). Shipped: All.</summary>
    public enum ShockReach { None = 0, OnlyDownedLines = 1, All = 2 }

    /// <summary>The three kinds of live line that can bite: a sparking floor-cord end (a cut conduit run, or a run the player
    /// stopped laying), a fallen overhead span, and another mod's dropped live cord (FlowWorks: a collapsed bridge deck's
    /// power cord). The last two are "downed lines".</summary>
    public enum LineKind { FloorEnd, DownedSpan, DroppedCord }

    /// <summary>
    /// RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO: who a live line shocks, as a pure function, so the whole table
    /// (line kind x live x setting x the pawn's job x spark budget) is decided offline (ShockRuleChecks, T_SHOCK_RULE_OFFLINE).
    /// The game halves only gather the inputs: RM_FallenWireShock (downed spans and dropped cords) and FloorEndShock (floor ends).
    /// </summary>
    public static class ShockRule
    {
        /// <summary>Does a line of this kind bite at all under this setting? Floor ends only under All; downed lines under
        /// Only downed lines and All; nothing under None. The aerial master switch is not an input: floor ends bite with it off.</summary>
        public static bool KindBites(ShockReach reach, LineKind kind) =>
            kind == LineKind.FloorEnd ? reach == ShockReach.All : reach != ShockReach.None;

        /// <summary>Is a pawn on a contact cell of this line shocked? Only a live line (by its power path at the last poll), only a
        /// living, not-yet-knocked-out flesh pawn, and never the pawn whose own job is fixing this line. How many ends are
        /// sparking on the map (the spark budget, maxSparkingEnds) is deliberately not an input: every live end bites.</summary>
        public static bool Takes(ShockReach reach, LineKind kind, bool live, bool flesh, bool dead, bool alreadyOut, bool fixingThisLine) =>
            live && KindBites(reach, kind) && flesh && !dead && !alreadyOut && !fixingThisLine;

        /// <summary>The floor-end fixer's exemption, scoped: a job target (a conduit blueprint or frame, or the conduit being
        /// built) at cell (tx, tz) joins the end whose conduit cell is (ex, ez) when it is that cell or one of its four
        /// neighbours (the destroyed cell the end faces, or the next cell of an unfinished run). A target anywhere else is some
        /// other job: that constructor is shocked like anyone. The caller passes only power-transmitting build targets.</summary>
        public static bool TargetJoinsEnd(int ex, int ez, int tx, int tz) => Math.Abs(ex - tx) + Math.Abs(ez - tz) <= 1;

        /// <summary>The one cell a floor end bites: the cell its drawn tip lies in. A cell two or more from it, along the live
        /// cord, is not a contact.</summary>
        public static (int x, int z) EndCell(double tipX, double tipZ) => ((int)Math.Floor(tipX), (int)Math.Floor(tipZ));

        /// <summary>The setting by its saved or probe-set name ("None", "OnlyDownedLines", "All"); anything else is null.</summary>
        public static ShockReach? Parse(string s) =>
            Enum.TryParse(s, false, out ShockReach r) && Enum.IsDefined(typeof(ShockReach), r) && !int.TryParse(s, out _) ? r : (ShockReach?)null;
    }
}
