using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>P14 (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD): RM_WaterLadder's freshwater table resolved to loaded defs, by the
	/// names in that one table (never a second list). Resolved once, after defs load.</summary>
	public static class RM_WaterLadderDefs
	{
		private static TerrainDef[] fresh;

		private static TerrainDef[] Table()
		{
			if (fresh == null)
			{
				var t = new TerrainDef[RM_WaterLadder.RungCount];
				for (int r = 0; r < t.Length; r++)
				{
					string name = RM_WaterLadder.FreshwaterDefName((RM_WaterLadder.Rung)r);
					t[r] = name == null ? null : DefDatabase<TerrainDef>.GetNamedSilentFail(name);
				}
				fresh = t;
			}
			return fresh;
		}

		/// <summary>The freshwater terrain for <paramref name="rung"/>, null for Dry or when the def is not loaded.</summary>
		public static TerrainDef Freshwater(RM_WaterLadder.Rung rung)
		{
			int k = (int)rung;
			TerrainDef[] t = Table();
			return k <= 0 || k >= t.Length ? null : t[k];
		}

		/// <summary>Is <paramref name="t"/> one of the freshwater ladder's wet looks?</summary>
		public static bool IsFreshwaterRung(TerrainDef t)
		{
			if (t == null)
			{
				return false;
			}
			TerrainDef[] table = Table();
			for (int r = 1; r < table.Length; r++)
			{
				if (table[r] == t)
				{
					return true;
				}
			}
			return false;
		}
	}
}
