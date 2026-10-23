using System.Collections.Generic;
using System.Reflection;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_LEGACY_MIGRATION_FLAG_1 A2, the live row's dev surface (jawa/static_call; never called by the game).
	/// A channel dug by a save older than the original-terrain record has nothing to restore when it is filled back in; the fix
	/// (6ab18bb6a) hands it the commonest neighbouring ground instead of leaving channel terrain at D=0. Staging that state needs
	/// the record gone, which nothing in play can do, so this surface forgets one cell's record by reflection (the field is the
	/// engine's private store; no production API should grow a "forget" for a test).</summary>
	public static class RM_LegacyFillProof
	{
		private static readonly FieldInfo OriginalField = typeof(RM_MapComponent_Excavation)
			.GetField("originalTerrain", BindingFlags.Instance | BindingFlags.NonPublic);

		/// <summary>WRITES. arg "x,z", an undug cell on the current map: dig it one notch through the engine (the record is
		/// written), forget that record, fill it back to the surface through the engine's own FillIn, and read the ground.
		/// "LEGACYFILL before=T dug=T forgot=b after=T afterIsChannel=b depth=n neighbours=T:n,... fallbackOn=b", or
		/// "REFUSED: ...". The expected answer with the setting on: after = the commonest non-channel neighbour (Soil on a
		/// cleared plot), afterIsChannel=False; off: afterIsChannel=True (the old trench).</summary>
		public static string ProofLegacyFill(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(',');
			if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
			{
				return "REFUSED: arg must be x,z on the current map";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || !c.InBounds(map))
			{
				return "REFUSED: no excavation engine, or the cell is off the map";
			}
			if (OriginalField == null)
			{
				return "REFUSED: RM_MapComponent_Excavation.originalTerrain not found (renamed?)";
			}
			if (eng.ExcavatedDepthAt(c) != 0)
			{
				return "REFUSED: the cell is already dug (D=" + eng.ExcavatedDepthAt(c) + "); reset the plot first";
			}
			TerrainDef before = map.terrainGrid.BaseTerrainAt(c);
			byte d = eng.Deepen(c);
			if (d == 0)
			{
				return "REFUSED: Deepen made no cut at " + x + "," + z + " (undiggable ground?) before=" + before?.defName;
			}
			TerrainDef dug = map.terrainGrid.BaseTerrainAt(c);
			bool forgot = OriginalField.GetValue(eng) is Dictionary<int, TerrainDef> rec && rec.Remove(map.cellIndices.CellToIndex(c));
			for (int i = 0; i < RM_ExcavationDepth.MaxDigCeiling && eng.ExcavatedDepthAt(c) > 0; i++)
			{
				eng.FillIn(c);
			}
			TerrainDef after = map.terrainGrid.BaseTerrainAt(c);
			Dictionary<string, int> votes = new Dictionary<string, int>();
			for (int k = 0; k < 8; k++)
			{
				IntVec3 n = c + GenAdj.AdjacentCells[k];
				if (n.InBounds(map))
				{
					string t = map.terrainGrid.BaseTerrainAt(n)?.defName ?? "null";
					votes.TryGetValue(t, out int v);
					votes[t] = v + 1;
				}
			}
			List<string> nb = new List<string>();
			foreach (KeyValuePair<string, int> kv in votes)
			{
				nb.Add(kv.Key + ":" + kv.Value);
			}
			nb.Sort(System.StringComparer.Ordinal);
			bool afterIsChannel = RM_ExcavationDepth.DepthOfDryTerrain(after) != RM_ExcavationDepth.Surface;
			return "LEGACYFILL before=" + before?.defName + " dug=" + dug?.defName + " forgot=" + forgot + " after=" + after?.defName
				+ " afterIsChannel=" + afterIsChannel + " depth=" + eng.ExcavatedDepthAt(c) + " neighbours=" + string.Join(",", nb)
				+ " fallbackOn=" + RimMandrakeFlowWorksSettings.legacyFillFallbackEnabled;
		}
	}
}
