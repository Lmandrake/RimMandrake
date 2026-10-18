using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.TakenByLand
{
    public enum TakenOutcome { LostMissing, LostDead, SpawnAlive, SpawnThenKill }

    /// <summary>
    /// TAKEN_BY_LAND_SERVICE_1 (X-10). Verse-free decisions of the one hold-and-return service (the river's swept-away and the
    /// dune gale's carry were the same mechanism built twice). Also compiled by the FlowWorks SelfTest.
    /// </summary>
    public static class RM_TakenByLandKernel
    {
        /// <summary>The book is scanned only when it holds something, and then only on every <paramref name="interval"/>th tick.</summary>
        public static bool ShouldScan(int count, int now, int interval) => !(count == 0 || interval <= 0 || now % interval != 0);

        public static bool IsDue(int returnTick, int now) => returnTick <= now;

        /// <summary>Tick a taken pawn is due back: <paramref name="days"/> from now, never earlier than the next tick.</summary>
        public static int ReturnTick(int now, float days, int ticksPerDay)
        {
            if (float.IsNaN(days) || days < 0f) days = 0f;
            double t = now + (double)days * ticksPerDay;
            return t >= int.MaxValue ? int.MaxValue : Math.Max(now + 1, (int)t);
        }

        public static TakenOutcome Decide(bool pawnMissing, bool mapMissing, bool dead, bool aliveRoll)
        {
            if (pawnMissing || mapMissing) return TakenOutcome.LostMissing;
            if (dead) return TakenOutcome.LostDead;
            return aliveRoll ? TakenOutcome.SpawnAlive : TakenOutcome.SpawnThenKill;
        }

        /// <summary>Remove and return (last to first) every record the predicate selects.</summary>
        public static List<T> TakeWhere<T>(IList<T> book, Func<T, bool> pick)
        {
            var taken = new List<T>();
            for (int i = book.Count - 1; i >= 0; i--)
            {
                if (pick(book[i]))
                {
                    taken.Add(book[i]);
                    book.RemoveAt(i);
                }
            }
            return taken;
        }

        /// <summary>Is a record a "storm's end" return: taken from this map by an EARLIER event than the one that just ended?</summary>
        public static bool EarlierEventOnMap(int recordMapId, int recordTakenTick, int mapId, int eventStartTick) =>
            recordMapId == mapId && recordTakenTick < eventStartTick;

        // ── RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS ─────────────────────────────────────────────────────────────────
        // Vanilla 1.6 Pawn.Notify_PassedToWorld (called by WorldPawns.AddPawn from PassToWorld/ExitMap): a pawn that is
        // the player's (or factionless and humanlike, or the ancients'), alive, whose WorldPawns.GetSituation is Free, is
        // handed to a random non-colony humanlike faction. A held pawn sat in WorldPawns as Free (KeepForever does not
        // change the situation), so every swept colonist / tamed animal / slave came back as TradersGuild, Pirate, ...
        // Free world pawns are also redress candidates (PawnGenerator) and quest picks. The service now reports its held
        // pawns as not Free, and restores the captured faction/guest state on return as a second line.

        /// <summary>Mirror of the vanilla Notify_PassedToWorld condition (the faction swap). Used by the offline mock.</summary>
        public static bool VanillaReassignsOnPassToWorld(bool factionNull, bool factionIsPlayer, bool factionIsAncients,
            bool humanlike, bool dead, bool situationFree) =>
            ((factionNull && humanlike) || factionIsPlayer || factionIsAncients) && !dead && situationFree;

        /// <summary>The Harmony postfix's rule on WorldPawns.GetSituation: a Free pawn the service holds is not Free.</summary>
        public static bool ShieldFromFree(bool vanillaSaysFree, bool held) => vanillaSaysFree && held;

        // ── SWEEP_PRISONER_FIX_NEVER_RETURNS (live day 3: a prisoner stood in moving water on the map edge and was gone at
        // tick 250, never booked, never back) ─ the river never took it. Vanilla JobGiver_PrisonerEscape: a prisoner of the
        // player whose district touches the map edge ESCAPES, and standing on the edge cell it exits at once (Pawn.ExitMap ->
        // WorldPawns.PassToWorld, Decide; guest status left Prisoner). In fiction it stepped off the edge INTO the current
        // the colonists beside it were swept off by, so the river takes it: an exit from a current lane is a sweep, held by
        // the service and walked home still a prisoner (or slave) of the player. A released prisoner, a caravan member or a
        // teleport leaves as vanilla says. Veto-able with the river's own switch: "Washed off the map at the edge" off (the
        // current stops at the edge) restores vanilla's escape there too.

        /// <summary>Is this ExitMap the river's? Prisoner or slave of the player, not released, leaving from a cell the
        /// current carries pawns on (lane + current running + edge washing on), not by caravan or teleport.</summary>
        public static bool ExitIntoCurrentIsSwept(bool washOffEdge, bool currentActive, bool prisonerOrSlaveOfPlayer,
            bool released, bool onCarryingLane, bool caravanOrTeleport) =>
            washOffEdge && currentActive && prisonerOrSlaveOfPlayer && !released && onCarryingLane && !caravanOrTeleport;

        // ── SWEEP_PRISONER_RETURN (live day 4, sweep_identity_fix3.json): the prisoner came back as itself, the letter fired,
        // and within 10 ticks it was off the map again, not held, not a world pawn. The return cell was the policy's random
        // EDGE cell (CellFinder.TryFindRandomEdgeCellWith); vanilla JobGiver_PrisonerEscape.ShouldStartEscaping is true for a
        // secure prisoner of the player whose district touches the map edge (or reaches one through open doors within 25
        // regions), and on an edge cell the exit spot is the cell itself, so Pawn.ExitMap ran at once (vanilla escape:
        // PassToWorld Decide, nothing books it). A prisoner now comes back to a cell that holds it, escape is off for
        // ReturnGuardTicks after the return, and an exit by a recently returned prisoner/slave writes a letter.

        /// <summary>Vanilla escapes are off this long after a return (one in-game hour): the colony's chance to see it.</summary>
        public const int ReturnGuardTicks = 2500;

        /// <summary>A prisoner/slave leaving the map this long after its return gets the service's "escaped" letter.</summary>
        public const int ReturnWatchTicks = 60000;

        /// <summary>Mirror of vanilla 1.6 JobGiver_PrisonerEscape.ShouldStartEscaping (the lord check is lordSecure).</summary>
        public static bool VanillaPrisonerStartsEscape(bool prisonerOfPlayer, bool prisonerIsSecure, bool lordSecure,
            bool districtTouchesEdge, bool openPathToEdge) =>
            prisonerOfPlayer && prisonerIsSecure && !lordSecure && (districtTouchesEdge || openPathToEdge);

        /// <summary>A cell that holds a prisoner: standable, off the edge, in a district vanilla's escape cannot reach the edge from.</summary>
        public static bool IsSecureReturnCell(bool standable, bool onEdge, bool districtTouchesEdge, bool openPathToEdge) =>
            standable && !onEdge && !districtTouchesEdge && !openPathToEdge;

        /// <summary>Where a returning prisoner may stand, in order of preference (tier 0 best).</summary>
        public enum PrisonerSpot { OwnedBed = 0, PrisonerBed = 1, PrisonCell = 2, EnclosedRoom = 3, Interior = 4 }

        public struct ReturnCandidate
        {
            public PrisonerSpot tier;
            public bool standable, onEdge, districtTouchesEdge, openPathToEdge;

            public ReturnCandidate(PrisonerSpot tier, bool standable, bool onEdge, bool districtTouchesEdge, bool openPathToEdge)
            {
                this.tier = tier;
                this.standable = standable;
                this.onEdge = onEdge;
                this.districtTouchesEdge = districtTouchesEdge;
                this.openPathToEdge = openPathToEdge;
            }

            public bool Secure => IsSecureReturnCell(standable, onEdge, districtTouchesEdge, openPathToEdge);
        }

        /// <summary>The index of the best cell for a returning prisoner: the best-tier SECURE cell; with none, the best-tier
        /// standable cell off the edge (the escape guard gives the colony an hour); -1 = none (the caller keeps its cell).
        /// <paramref name="secure"/> says which kind was found.</summary>
        public static int PickPrisonerReturn(IList<ReturnCandidate> cands, out bool secure)
        {
            secure = false;
            int best = -1;
            for (int i = 0; i < cands.Count; i++)
                if (cands[i].Secure && (best < 0 || cands[i].tier < cands[best].tier)) best = i;
            if (best >= 0) { secure = true; return best; }
            for (int i = 0; i < cands.Count; i++)
                if (cands[i].standable && !cands[i].onEdge && (best < 0 || cands[i].tier < cands[best].tier)) best = i;
            return best;
        }

        /// <summary>Is this ExitMap a returned prisoner/slave slipping away (the service writes the letter vanilla does not)?</summary>
        public static bool ExitIsLostReturn(bool prisonerOrSlaveOfPlayer, bool released, bool caravanOrTeleport,
            bool recentlyReturned) =>
            prisonerOrSlaveOfPlayer && !released && !caravanOrTeleport && recentlyReturned;

        /// <summary>Faction/guest state captured at the take, compared at the return. Ids are Faction.loadID (-1 = none);
        /// guestStatus is (int)GuestStatus, -1 when the pawn is nobody's guest, prisoner or slave (a vanilla slave has NO
        /// host faction: its master is its own Faction, so the Verse side keeps Slave even with host -1).</summary>
        public struct TakenState
        {
            public int factionId;
            public int hostFactionId;
            public int guestStatus;

            public TakenState(int factionId, int hostFactionId, int guestStatus)
            {
                this.factionId = factionId;
                this.hostFactionId = hostFactionId;
                this.guestStatus = guestStatus;
            }

            public override string ToString() => "faction=" + factionId + " host=" + hostFactionId + " guest=" + guestStatus;
        }

        [Flags]
        public enum RestoreNeed { None = 0, Faction = 1, Guest = 2 }

        /// <summary>What must be put back so the returning pawn is in the state it was taken in. Faction is restored first
        /// (SetFaction can clear guest status), so a faction change always implies a guest re-check.</summary>
        public static RestoreNeed NeedsRestore(TakenState captured, TakenState now)
        {
            RestoreNeed need = RestoreNeed.None;
            if (captured.factionId != now.factionId) need |= RestoreNeed.Faction | RestoreNeed.Guest;
            if (captured.hostFactionId != now.hostFactionId || captured.guestStatus != now.guestStatus) need |= RestoreNeed.Guest;
            return need;
        }
    }

    /// <summary>RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS: the thingIDNumbers the service holds right now. Filled BEFORE the
    /// taker removes the pawn (the faction swap fires inside PassToWorld), emptied the moment it is spawned back or lost,
    /// rebuilt from the book on load. Verse-free so the SelfTest drives the same set the Harmony postfix reads.</summary>
    public sealed class RM_TakenHoldSet
    {
        private readonly HashSet<int> ids = new HashSet<int>();

        public int Count => ids.Count;
        public bool Contains(int id) => ids.Contains(id);
        public void Hold(int id) { if (id >= 0) ids.Add(id); }
        public void Release(int id) { ids.Remove(id); }
        public void Clear() { ids.Clear(); }

        public void Rebuild(IEnumerable<int> held)
        {
            ids.Clear();
            foreach (int id in held) Hold(id);
        }
    }

    /// <summary>SWEEP_PRISONER_RETURN: the tick each pawn was given back (thingIDNumber -> tick). Session-only: the guard is an
    /// hour, and a loaded save's prisoner is already standing where the return put it. Verse-free for the SelfTest.</summary>
    public sealed class RM_TakenReturnGuard
    {
        private readonly Dictionary<int, int> returned = new Dictionary<int, int>();

        public int Count => returned.Count;
        public void Mark(int id, int tick) { if (id >= 0) returned[id] = tick; }
        public void Clear() { returned.Clear(); }

        /// <summary>Returned within <paramref name="window"/> ticks of <paramref name="now"/>.</summary>
        public bool Within(int id, int now, int window) =>
            returned.TryGetValue(id, out int t) && now >= t && now - t < window;

        public bool InGuard(int id, int now) => Within(id, now, RM_TakenByLandKernel.ReturnGuardTicks);
        public bool Recent(int id, int now) => Within(id, now, RM_TakenByLandKernel.ReturnWatchTicks);

        /// <summary>Forget returns older than the watch window (called on each return so the map stays small).</summary>
        public void Prune(int now)
        {
            var old = new List<int>();
            foreach (var kv in returned) if (now - kv.Value >= RM_TakenByLandKernel.ReturnWatchTicks || now < kv.Value) old.Add(kv.Key);
            foreach (int id in old) returned.Remove(id);
        }
    }
}
