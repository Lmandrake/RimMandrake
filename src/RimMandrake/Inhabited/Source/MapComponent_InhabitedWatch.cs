using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Watches an inhabited place's map for the cause that ends its cast, and
    /// says so the moment it fires. INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
    ///
    /// WHY A MapComponent AND NOT A PATCH. Map.FillComponents instantiates every
    /// non-abstract MapComponent subclass on every map, so this needs no def, no
    /// patch and no registration -- and unlike a Harmony hook on some damage or
    /// destruction method it cannot go stale against a renamed target. The cost
    /// is one WorldObjectAt lookup every <see cref="IntervalTicks"/> ticks per
    /// live map, on maps that overwhelmingly have no place on them at all.
    ///
    /// 🔑 IT ONLY RECORDS. The consequence is InhabitedFateWorker.Apply, at
    /// teardown -- see that class for why the cast does not walk off in front of
    /// the player. Once a cause has fired this component stops looking: a place
    /// breaks once, and re-firing would spam the message.
    ///
    /// Nothing is scribed here. Everything it decides lives on the world object,
    /// which is where a save can carry it.
    /// </summary>
    public class MapComponent_InhabitedWatch : MapComponent
    {
        /// <summary>Roughly four seconds of game time. Fine enough that a fire in
        /// the granary is noticed while it is still a fire.</summary>
        private const int IntervalTicks = 250;

        public MapComponent_InhabitedWatch(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % IntervalTicks != 0)
            {
                return;
            }
            WorldObject_Inhabited place = Find.WorldObjects?.WorldObjectAt<WorldObject_Inhabited>(map.Tile);
            if (place == null || place.threatened || place.placeDef == null)
            {
                return;
            }
            string cause = InhabitedFateWorker.DetectCause(place, map);
            if (cause == null)
            {
                return;
            }

            place.threatened = true;
            place.threatReason = cause;
            Messages.Message(cause.Translate(place.LabelCap), MessageTypeDefOf.NeutralEvent,
                historical: false);
            Log.Message("[RimMandrake.Inhabited] fate cause '" + cause + "' fired at " + place.LabelCap
                        + "; it is acted on when the map is left.");
        }
    }
}
