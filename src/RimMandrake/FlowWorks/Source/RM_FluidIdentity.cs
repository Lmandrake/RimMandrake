using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LIQUID_BODY_FLUID_IDENTITY_1 step 1: which FluidDef a natural liquid terrain is. Built once from every
	/// LiquidDef's terrainSuite (shallow / deep / chestDeep) -> its canalFluid. A terrain no LiquidDef claims answers
	/// null and the caller falls back (FormBody: water). Lazily built after defs load; never mutated after.
	/// </summary>
	public static class RM_FluidIdentity
	{
		private static Dictionary<TerrainDef, FluidDef> byTerrain;

		public static FluidDef FluidOfTerrain(TerrainDef terrain)
		{
			if (terrain == null)
			{
				return null;
			}
			if (byTerrain == null)
			{
				var d = new Dictionary<TerrainDef, FluidDef>();
				foreach (LiquidDef liquid in DefDatabase<LiquidDef>.AllDefsListForReading)
				{
					if (liquid?.terrainSuite == null || liquid.canalFluid == null)
					{
						continue;
					}
					foreach (TerrainDef t in new[] { liquid.terrainSuite.shallow, liquid.terrainSuite.deep, liquid.terrainSuite.chestDeep })
					{
						if (t != null && !d.ContainsKey(t))
						{
							d[t] = liquid.canalFluid;
						}
					}
				}
				byTerrain = d;
			}
			return byTerrain.TryGetValue(terrain, out FluidDef f) ? f : null;
		}
	}

	/// <summary>static_call census (LIQUID_BODY_FLUID_IDENTITY_1 step 1): on the current map, wet excavated cells
	/// with and without a recorded fluid, the distinct fluids recorded, and each body's fluid.
	/// "FLUIDID wet N | recorded R | unrecorded U | fluids [a,b] | bodies [id:fluid,...]".</summary>
	public static class RM_FluidIdentityProof
	{
		/// <summary>Debug/bridge fill with a NAMED fluid (static_call, one string): "x,z,fill,FluidDefName".
		/// Routes through the driver API, so the no-mix rule refuses a cell holding another fluid.</summary>
		public static string ProofFillWithFluid(string arg)
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			string[] p = (arg ?? "").Split(',');
			if (p.Length != 4 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z) || !int.TryParse(p[2], out int fill))
				return "REFUSED: arg must be x,z,fill,FluidDefName";
			FluidDef fluid = DefDatabase<FluidDef>.GetNamedSilentFail(p[3].Trim());
			if (fluid == null) return "REFUSED: no FluidDef " + p[3];
			IntVec3 c = new IntVec3(x, 0, z);
			if (!ex.TrySetDriverFill(c, fill, fluid))
				return "REFUSED: " + c + " not excavated or holds another fluid (" + (ex.FluidAt(c)?.defName ?? "none") + ")";
			return "FILLED " + c + " F=" + ex.FillAt(c) + " fluid=" + (ex.FluidAt(c)?.defName ?? "none");
		}

		public static string ProofCensus()
		{
			Map map = Find.CurrentMap;
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null) return "REFUSED: no excavation component on the current map";
			int wet = 0, rec = 0;
			var fluids = new HashSet<string>();
			foreach (IntVec3 c in map.AllCells)
			{
				// EXCAVATED cells only, as the doc above says: FillAt reads natural water as full, so a river map counted
				// 2,347 river cells as "wet, unrecorded" (MEASURED 2026-10-06). A natural body's fluid is the bodies list.
				if (ex.ExcavatedDepthAt(c) == 0 || ex.FillAt(c) == 0) continue;
				wet++;
				FluidDef f = ex.FluidAt(c);
				if (f != null) { rec++; fluids.Add(f.defName); }
			}
			var bodies = new List<string>();
			foreach (RM_LiquidBody b in ex.Stock.Bodies) bodies.Add(b.id + ":" + (b.fluid?.defName ?? "null"));
			return "FLUIDID wet " + wet + " | recorded " + rec + " | unrecorded " + (wet - rec)
				+ " | fluids [" + string.Join(",", fluids) + "] | bodies [" + string.Join(",", bodies) + "]";
		}
	}
}
