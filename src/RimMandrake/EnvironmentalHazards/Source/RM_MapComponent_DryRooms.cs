using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M2 build (greentide_kit_spec.md "M2. The dry-air
    // blower", piece 1: "dries the room ... registers its room (via
    // Thing.GetRoom()) in RM_MapComponent_DryRooms, which M1's condition
    // reads. Room-based, so one blower per structure suffices."
    //
    // Push-refreshed, not push-registered/deregistered like
    // RM_MapComponent_DreadField (this mod's own comparable pattern):
    // RM_CompDryFieldEmitter calls KeepDry() on every active tick rather
    // than once at spawn, because a Room object is NOT durable — vanilla
    // regenerates it whenever the enclosing geometry (a wall, a door)
    // changes, and a comp holding a stale Room reference across such a
    // change would silently stop drying anything. Re-fetching
    // parent.GetRoom() every active tick and re-registering means a
    // room-geometry change is self-healing within one tick cadence, no
    // spawn/despawn bookkeeping required.
    //
    // "Dry" is a decaying grant (dryUntilTick), not a boolean flag, so a
    // blower that runs out of fuel or loses power simply stops refreshing
    // it and the room naturally reverts once the grant lapses — exactly the
    // sheet's "when it runs out of fuel, the green notices within hours"
    // and requires no explicit stop/deregister path at all.
    //
    // Not Scribe-saved, same reasoning RM_MapComponent_DreadField's own
    // header already gives for this mod: entirely derived from currently
    // active blowers, which re-establish it within one CompTickRare cadence
    // (250 ticks) of a load — a negligible, honest gap, not a save-format
    // owed.
    public class RM_MapComponent_DryRooms : MapComponent
    {
        private readonly Dictionary<Room, int> dryUntilTick = new Dictionary<Room, int>();

        private int ticksUntilPrune;

        public RM_MapComponent_DryRooms(Map map)
            : base(map)
        {
        }

        public void KeepDry(Room room, int durationTicks)
        {
            if (room == null)
            {
                return;
            }

            dryUntilTick[room] = Find.TickManager.TicksGame + Mathf.Max(1, durationTicks);
        }

        public bool IsDry(Room room)
        {
            if (room == null)
            {
                return false;
            }

            return dryUntilTick.TryGetValue(room, out int until) && until >= Find.TickManager.TicksGame;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            // Cheap periodic prune so orphaned Room keys (left behind by a
            // geometry change, or a blower that despawned/ran dry for good)
            // do not grow the dictionary forever. A day's grace past
            // expiry, not immediate, so this never fights KeepDry's own
            // refresh cadence.
            if (--ticksUntilPrune > 0)
            {
                return;
            }

            ticksUntilPrune = 2000;

            if (dryUntilTick.Count == 0)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            List<Room> stale = null;
            foreach (KeyValuePair<Room, int> kv in dryUntilTick)
            {
                if (kv.Value < now - 60000)
                {
                    (stale ??= new List<Room>()).Add(kv.Key);
                }
            }

            if (stale != null)
            {
                for (int i = 0; i < stale.Count; i++)
                {
                    dryUntilTick.Remove(stale[i]);
                }
            }
        }
    }
}
