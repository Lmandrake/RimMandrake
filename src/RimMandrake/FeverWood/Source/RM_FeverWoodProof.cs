using Verse;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_LIMB_PROOF_HOOK_1: jawa/static_call proof reads for the tentacle watch's private state
    /// (type=RimMandrake.FeverWood.RM_FeverWoodProof method=ProofLimbs args=""). Pure reads, never a mutation.</summary>
    public static class RM_FeverWoodProof
    {
        /// <summary>FEVERWOOD_HIVE_GUARD_CHAMBER_1: "rooms=N guards=N fedBy=<race|none> feeder=B" then each guard's
        /// " defName@cell home=cell food=0.00" for the current map.</summary>
        public static string ProofHive(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "ERROR no current map";
            RM_MapComponent_AntHive h = map.GetComponent<RM_MapComponent_AntHive>();
            if (h == null) return "ERROR no RM_MapComponent_AntHive on this map";
            string s = "rooms=" + h.roomCenters.Count + " guards=" + h.guards.Count
                + " fedBy=" + (h.guardFeederRace?.defName ?? "none") + " feeder=" + h.HasWildFeeder();
            foreach (Pawn g in h.guards)
            {
                s += " | " + g.def.defName + "@" + g.Position
                    + " home=" + g.TryGetComp<RimMandrake.CreatureBehaviors.RM_CompHomeTether>()?.Home
                    + " food=" + (g.needs?.food?.CurLevelPercentage ?? -1f).ToString("0.00");
            }
            return s;
        }

        /// <summary>ANT_HIVE_REAL_GEOMETRY_1: "walls=N reachEdge=B reachQueen=B enclosed=B roofed=F" for the current map:
        /// the entrance room reaches the map edge and the queen's room, and the queen's room is an indoor room.</summary>
        public static string ProofHiveGeometry(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "ERROR no current map";
            RM_MapComponent_AntHive h = map.GetComponent<RM_MapComponent_AntHive>();
            if (h == null || !h.HasHive) return "ERROR no hive on this map";
            ThingDef wall = DefDatabase<ThingDef>.GetNamedSilentFail(RM_GenStep_AntHiveDungeon.WallDefName);
            int roofed = 0;
            foreach (IntVec3 c in h.roomCenters)
            {
                if (c.Roofed(map)) roofed++;
            }
            Room queen = h.QueenRoom.GetRoom(map);
            return "walls=" + (wall == null ? -1 : map.listerThings.ThingsOfDef(wall).Count)
                + " reachEdge=" + map.reachability.CanReachMapEdge(h.EntranceRoom, TraverseParms.For(TraverseMode.PassDoors))
                + " reachQueen=" + map.reachability.CanReach(h.EntranceRoom, h.QueenRoom, Verse.AI.PathEndMode.OnCell, TraverseMode.PassDoors)
                + " enclosed=" + (queen != null && !queen.PsychologicallyOutdoors)
                + " roofed=" + roofed + "/" + h.roomCenters.Count;
        }

        /// <summary>"limbs=N cap=N pressure=N chorusSilenced=B sentinels=N blockedUntil=T cooldownLeft=T" for the current map.</summary>
        public static string ProofLimbs(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "ERROR no current map";
            RM_MapComponent_TentacleWatch w = map.GetComponent<RM_MapComponent_TentacleWatch>();
            if (w == null) return "ERROR no RM_MapComponent_TentacleWatch on this map";
            return w.ProofSnapshot();
        }
    }
}
