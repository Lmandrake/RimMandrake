using System.Collections.Generic;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>VEXXITH_USES_1: which liquid stands on a terrain or in a recorded canal fluid, keyed by defName so the same
    /// production code runs on the DefDatabase in game and on the shipped XML in the SelfTest. Natural terrains come from a
    /// LiquidDef's terrainSuite; canal fill terrains (RM_Fill_*) are on no suite and resolve through FluidDef, then the
    /// LiquidDef naming that fluid as canalFluid. The first liquid to name a fluid keeps it.</summary>
    public sealed class RM_CanalLiquidIndex
    {
        private readonly Dictionary<string, string> liquidOfTerrain = new Dictionary<string, string>();
        private readonly Dictionary<string, string> liquidOfFluid = new Dictionary<string, string>();
        private readonly HashSet<string> acid = new HashSet<string>();

        public void AddLiquid(string liquid, bool isAcid, string canalFluid, params string[] suiteTerrains)
        {
            if (isAcid)
            {
                acid.Add(liquid);
            }
            if (canalFluid != null && !liquidOfFluid.ContainsKey(canalFluid))
            {
                liquidOfFluid[canalFluid] = liquid;
            }
            foreach (string t in suiteTerrains)
            {
                if (t != null && !liquidOfTerrain.ContainsKey(t))
                {
                    liquidOfTerrain[t] = liquid;
                }
            }
        }

        /// <summary>After every AddLiquid: a fluid no liquid names adds nothing.</summary>
        public void AddFluid(string fluid, params string[] fillTerrains)
        {
            if (!liquidOfFluid.TryGetValue(fluid, out string liquid))
            {
                return;
            }
            foreach (string t in fillTerrains)
            {
                if (t != null && !liquidOfTerrain.ContainsKey(t))
                {
                    liquidOfTerrain[t] = liquid;
                }
            }
        }

        public string LiquidOfTerrain(string terrain)
        {
            return terrain != null && liquidOfTerrain.TryGetValue(terrain, out string l) ? l : null;
        }

        public bool CellIsAcid(string terrain, string recordedFluid)
        {
            string fromTerrain = LiquidOfTerrain(terrain);
            if (fromTerrain != null && acid.Contains(fromTerrain))
            {
                return true;
            }
            return recordedFluid != null && liquidOfFluid.TryGetValue(recordedFluid, out string l) && acid.Contains(l);
        }
    }
}
