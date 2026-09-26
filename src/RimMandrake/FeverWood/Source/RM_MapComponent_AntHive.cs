using System.Collections.Generic;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_ANT_HIVE_DUNGEON_1. Records what RM_GenStep_AntHiveDungeon
    // actually carved on this map, so follow-on work (the reactive alarm
    // mechanism once REACTION_MECHANISM_GENERALISE_1 reaches its ant-hive
    // step; the farm/parasite/guard chamber population once their creatures
    // exist) can place content into the already-generated layout instead of
    // re-deriving room positions from scratch. A map with no generated hive
    // simply has an empty RoomCenters list — always present, never null,
    // same "component always exists, data may be empty" shape as
    // RM_MapComponent_LivingRegrowth.BoleCenters.
    public class RM_MapComponent_AntHive : MapComponent
    {
        // Every room center, entrance first, deepest (queen's room) last.
        public List<IntVec3> roomCenters = new List<IntVec3>();

        public bool HasHive => roomCenters.Count > 0;

        public IntVec3 EntranceRoom => roomCenters.Count > 0 ? roomCenters[0] : IntVec3.Invalid;

        public IntVec3 QueenRoom => roomCenters.Count > 0 ? roomCenters[roomCenters.Count - 1] : IntVec3.Invalid;

        public RM_MapComponent_AntHive(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref roomCenters, "roomCenters", LookMode.Value);
            if (roomCenters == null)
            {
                roomCenters = new List<IntVec3>();
            }
        }
    }
}
