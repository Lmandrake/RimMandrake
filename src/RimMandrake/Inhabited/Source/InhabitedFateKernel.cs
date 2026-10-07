using System;
using System.Collections.Generic;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// What could end a cast. The default is nothing: they live here.
    /// Flight is CAUSED, never scheduled -- every value below names a cause,
    /// not a timer.
    ///
    /// WIRED. InhabitedFateWorker.DetectCause turns each value below into a real
    /// test on a live map, MapComponent_InhabitedWatch runs it during the visit,
    /// and InhabitedFateWorker.Apply acts on it at teardown -- the cast goes to
    /// the DisplacedPool and the place reads Abandoned or Looted from then on.
    ///
    /// ⏱️ CAUSE AND CONSEQUENCE ARE SEPARATED BY THE VISIT. Nobody walks off the
    /// map in front of the player; the place is empty the next time they come.
    /// InhabitedFateWorker's class comment has the engine reason (Pawn.ExitMap
    /// hands a non-player pawn to WorldPawns, and WorldPawnGC then eats the
    /// roster) and names what a visible walk-off would take.
    /// </summary>
    public enum InhabitedFate
    {
        /// <summary>Nothing ends them. The default and the great majority.</summary>
        Resident,
        /// <summary>They break and go if the player menaces them. Costs goodwill,
        /// and hostility ends only at goodwill 0, so a fright is not a thing a
        /// gift repairs.</summary>
        FleeIfThreatened,
        /// <summary>A gravship coming out of the sky is enough. The ship is a
        /// presence in the world, not transport.</summary>
        FleeOnArrival,
        /// <summary>A genuine caravan passing through. The rare case.</summary>
        Transient
    }

    /// <summary>
    /// What the world map reports about a place. Drawn by
    /// WorldObject_Inhabited.GetInspectString.
    ///
    /// Written in three places: GenStep_InhabitedCast and Patch_MapRemoval both
    /// set Abandoned when nobody is left, and InhabitedFateWorker.Apply picks
    /// Abandoned or Looted by whether the larder survived.
    ///
    /// ⚠️ Squatted is DECLARED, NOT WRITTEN. Nothing sets it, because nothing in
    /// this mod yet moves a second party into an emptied place -- it is the state
    /// a later "somebody else has taken it over" feature will write, and inventing
    /// a trigger for it here would have been a guess.
    /// </summary>
    public enum InhabitedState
    {
        Inhabited,
        Abandoned,
        Looted,
        Squatted
    }

    public enum RouteStance
    {
        AtWork,
        AtRest,
        Defending
    }

    /// <summary>What a head-count of the cast standing on the map found.</summary>
    public struct CastCount
    {
        public int standing;
        public bool anyDowned;
    }

    /// <summary>
    /// The fate decision, the stock arithmetic and the daily routine, with no Verse type in them so the offline fuzz
    /// (`python3 src/RimMandrake/Utils/selftest_inhabited_fuzz.py`) compiles THIS file. InhabitedFateWorker,
    /// InhabitedStock, WorldObject_Inhabited and LordToil_InhabitedRoutine call it; nothing here is a copy.
    /// </summary>
    public static class InhabitedFateKernel
    {
        public const string CauseTransient = "InhabitedFateTransient";
        public const string CauseGravship = "InhabitedFateGravship";
        public const string CauseBurned = "InhabitedFateBurned";
        public const string CauseHostile = "InhabitedFateHostile";
        public const string CauseHarmed = "InhabitedFateHarmed";
        public const string CauseRobbed = "InhabitedFateRobbed";

        /// <summary>
        /// Has a cause fired? The translation key naming it, or null. Cheapest test first; the engine scans arrive as
        /// delegates so a Resident place pays for none of them.
        /// </summary>
        public static string Cause(InhabitedFate fate, Func<bool> playerHasGravEngine, bool stockAreaExists,
            Func<bool> fireOnStockArea, bool factionHostile, bool colonistsOnMap, int groundedCount,
            Func<CastCount> countCast, int stockSpawnedCount, Func<int> stockLeftOnMap, float robbedFraction)
        {
            switch (fate)
            {
                case InhabitedFate.Resident:
                    return null;
                case InhabitedFate.Transient:
                    return CauseTransient;
                case InhabitedFate.FleeOnArrival:
                    return playerHasGravEngine() ? CauseGravship : null;
                case InhabitedFate.FleeIfThreatened:
                    return Menace(stockAreaExists, fireOnStockArea, factionHostile, colonistsOnMap, groundedCount,
                        countCast, stockSpawnedCount, stockLeftOnMap, robbedFraction);
            }
            return null;
        }

        private static string Menace(bool stockAreaExists, Func<bool> fireOnStockArea, bool factionHostile,
            bool colonistsOnMap, int groundedCount, Func<CastCount> countCast, int stockSpawnedCount,
            Func<int> stockLeftOnMap, float robbedFraction)
        {
            if (stockAreaExists && fireOnStockArea())
            {
                return CauseBurned;
            }
            if (factionHostile)
            {
                return CauseHostile;
            }
            if (colonistsOnMap && groundedCount > 0)
            {
                CastCount c = countCast();
                if (c.anyDowned)
                {
                    return CauseHarmed;
                }
                // A dead resident is a Corpse, not a Pawn, so the shortfall IS the casualty count.
                if (c.standing < groundedCount)
                {
                    return CauseHarmed;
                }
            }
            if (stockSpawnedCount > 0)
            {
                int left = stockLeftOnMap();
                if (left < stockSpawnedCount * robbedFraction)
                {
                    return CauseRobbed;
                }
            }
            return null;
        }

        /// <summary>Does Apply act at all? Only a threatened place whose fate is not Resident.</summary>
        public static bool ShouldApply(InhabitedFate fate, bool threatened)
        {
            return threatened && fate != InhabitedFate.Resident;
        }

        /// <summary>An emptied larder is a LOOTING; a full one left behind is an ABANDONMENT.</summary>
        public static InhabitedState StateAfterFate(int stockThingCount)
        {
            return stockThingCount == 0 ? InhabitedState.Looted : InhabitedState.Abandoned;
        }

        /// <summary>The state after the cast was recalled at teardown: nobody left reads Abandoned; any other state stands.</summary>
        public static InhabitedState StateAfterRecall(InhabitedState state, int soulCount)
        {
            return soulCount == 0 && state == InhabitedState.Inhabited ? InhabitedState.Abandoned : state;
        }

        // ---------------------------------------------------------------- stock

        /// <summary>
        /// Split an authored count at the stack limit: 200 steel at a limit of 75 is 75, 75, 50. The parts always sum to the count and
        /// none exceeds the limit (a limit below 1 is treated as 1).
        /// </summary>
        public static List<int> SplitStacks(int count, int stackLimit)
        {
            List<int> parts = new List<int>();
            int limit = Math.Max(1, stackLimit);
            int remaining = count;
            while (remaining > 0)
            {
                int n = Math.Min(limit, remaining);
                parts.Add(n);
                remaining -= n;
            }
            return parts;
        }

        /// <summary>
        /// Is this thing the place's to take back? Spawned live items only; corpses never (they hold their pawn and would
        /// deep-scribe a dead resident into the world object); the player's own never; otherwise it was a stack we dropped
        /// or it lies in the stock area.
        /// </summary>
        public static bool IsPlaceGoods(bool spawnedAndAlive, bool isItem, bool isCorpse, bool playerOwned,
            bool inLedger, bool inStockArea)
        {
            if (!spawnedAndAlive || !isItem || isCorpse || playerOwned)
            {
                return false;
            }
            return inLedger || inStockArea;
        }

        // ---------------------------------------------------------------- routine

        public static bool IsSleepingHour(int hour, int sleepStartHour, int wakeHour)
        {
            if (sleepStartHour == wakeHour)
            {
                return false;
            }
            if (sleepStartHour < wakeHour)
            {
                return hour >= sleepStartHour && hour < wakeHour;
            }
            return hour >= sleepStartHour || hour < wakeHour;
        }

        public const int DefendTicks = 1200;

        public static RouteStance Stance(bool hasLord, int ticksGame, int lastPawnHarmTick, bool sleepingHour)
        {
            if (hasLord && ticksGame - lastPawnHarmTick < DefendTicks)
            {
                return RouteStance.Defending;
            }
            return sleepingHour ? RouteStance.AtRest : RouteStance.AtWork;
        }
    }
}
