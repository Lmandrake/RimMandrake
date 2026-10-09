using Verse;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_LIMB_PROOF_HOOK_1: jawa/static_call proof reads for the tentacle watch's private state
    /// (type=RimMandrake.FeverWood.RM_FeverWoodProof method=ProofLimbs args=""). Pure reads, never a mutation.</summary>
    public static class RM_FeverWoodProof
    {
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
