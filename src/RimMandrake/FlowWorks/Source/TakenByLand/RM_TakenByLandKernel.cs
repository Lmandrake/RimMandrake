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
}
