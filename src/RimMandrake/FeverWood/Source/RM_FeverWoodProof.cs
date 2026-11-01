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
