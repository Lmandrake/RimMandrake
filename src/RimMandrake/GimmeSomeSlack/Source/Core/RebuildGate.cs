// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 3 (live round 4, 2026-10-26: a far dig left the probe's farSkips unmoved). The map
// component's rebuild-or-skip state, moved out of RM_MapComponent_CordGraph so the SelfTest can drive it.
using System;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>
    /// Decides, per mesh-dirty event, whether the cords must be rebuilt, and counts what it decided. Terrain, roof, building
    /// and fog events are benign at a cell outside the last Build's reach that holds nothing powered (SelfTest reach
    /// soundness); every other event is relevant. A benign event that is not our own reprint is a far skip, counted when it is
    /// classified: round 2 counted it only when our section layer regenerated, which vanilla does for on-screen sections only,
    /// so an off-screen dig (the only kind a far dig usually is) skipped the rebuild and was never counted.
    /// </summary>
    internal sealed class RebuildGate
    {
        /// <summary>Since the last published build: did a relevant event land, or only benign ones?</summary>
        public bool RelevantSinceBuild = true, BenignSinceBuild;
        /// <summary>Benign events that were not our own reprint (each one a rebuild the round-1 code would have run).</summary>
        public int FarSkips;
        /// <summary>Layer regenerates answered with the published pieces (every event since the build was benign).</summary>
        public int RegenSkips;
        public int RelevantEvents;
        public string LastRelevant = "";
        /// <summary>The last far skip's layer flags and cell (formatted on read: far events come by the hundred while mining).</summary>
        public ulong LastFarSkipFlags;
        public Cell LastFarSkipCell;

        public string LastFarSkip(Func<ulong, string> flagNames) =>
            FarSkips == 0 ? "" : flagNames(LastFarSkipFlags) + "@" + LastFarSkipCell.X + "," + LastFarSkipCell.Z;

        /// <summary>True when an event with these layer flags at <paramref name="c"/> cannot change the next Build.</summary>
        public static bool IsBenign(bool own, ulong layerFlags, ulong benignFlags, CordReach reach, Cell c, Func<Cell, bool> holdsPower) =>
            own || ((layerFlags & ~benignFlags) == 0UL && reach != null && !reach.All && !reach.Reaches(c) && !holdsPower(c));

        /// <summary>Classifies and records one event; returns true when it is benign (nothing to mark stale).</summary>
        public bool Note(bool own, ulong layerFlags, ulong benignFlags, CordReach reach, Cell c, Func<Cell, bool> holdsPower, Func<ulong, string> flagNames)
        {
            if (IsBenign(own, layerFlags, benignFlags, reach, c, holdsPower))
            {
                BenignSinceBuild = true;
                if (!own)
                {
                    FarSkips++;
                    LastFarSkipFlags = layerFlags;
                    LastFarSkipCell = c;
                }
                return true;
            }
            RelevantSinceBuild = true;
            RelevantEvents++;
            LastRelevant = flagNames(layerFlags) + "@" + c.X + "," + c.Z +
                (reach == null ? " noReach" : reach.Reaches(c) ? " inReach" : " outReach") + (holdsPower(c) ? " powered" : "");
            return false;
        }

        /// <summary>Our layer regenerates on a frame that has not built: true = rebuild, false = the published pieces stand.</summary>
        public bool RegenerateNeedsBuild()
        {
            if (!RelevantSinceBuild && BenignSinceBuild)
            {
                BenignSinceBuild = false;
                RegenSkips++;
                return false;
            }
            return true;
        }

        /// <summary>A build is starting: until it publishes complete, the cords stay stale.</summary>
        public void Building() => RelevantSinceBuild = true;

        /// <summary>A build published; <paramref name="pending"/> edges were left to a later build (lay budget).</summary>
        public void Published(int pending)
        {
            RelevantSinceBuild = pending > 0;
            BenignSinceBuild = false;
        }

        public void Invalidate() => RelevantSinceBuild = true;
    }
}
