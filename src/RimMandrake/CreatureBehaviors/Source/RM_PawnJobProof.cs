using System.Linq;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>Dev proof (GLOOMCAST_WAKE_RIDERS_1 A2 and any job-state criterion): jawa/static_call reads a pawn's current job.</summary>
	public static class RM_PawnJobProof
	{
		/// <summary>ThingID of a spawned pawn on any loaded map -> "job=&lt;defName&gt; target=&lt;label&gt; dist=&lt;cells&gt;" or UNMEASURED.</summary>
		public static string ProofJob(string thingId)
		{
			Pawn p = Find.Maps.SelectMany(m => m.mapPawns.AllPawnsSpawned).FirstOrDefault(x => x.ThingID == thingId);
			if (p == null) return "UNMEASURED no spawned pawn " + thingId;
			Verse.AI.Job j = p.CurJob;
			if (j == null) return "job=none";
			Thing t = j.targetA.Thing;
			return "job=" + j.def.defName + " target=" + (t != null ? t.ThingID : j.targetA.ToString()) + (t != null ? " dist=" + (int)(t.Position - p.Position).LengthHorizontal : "");
		}

		/// <summary>RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL: ThingID -> what the shade landing search
		/// sees from this pawn's cell: its patch, whether it is crowded, the free shade cell the search picks, and the
		/// shade cells within the dash cap counted as free, held by a pawn or unstandable. Read only.</summary>
		public static string ProofLanding(string thingId)
		{
			Pawn p = Find.Maps.SelectMany(m => m.mapPawns.AllPawnsSpawned).FirstOrDefault(x => x.ThingID == thingId);
			if (p == null) return "UNMEASURED no spawned pawn " + thingId;
			RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(p.Map);
			RM_ShadePatchGraph graph = grid?.PatchGraph;
			if (graph == null) return "UNMEASURED no patch graph";
			CellIndices ci = p.Map.cellIndices;
			int r = UnityEngine.Mathf.CeilToInt(grid.HeatExtension?.maxDashCells ?? 0f);
			int free = 0, held = 0, unstandable = 0;
			var pawnsAt = new System.Collections.Generic.HashSet<IntVec3>(p.Map.mapPawns.AllPawnsSpawned.Where(o => o != p).Select(o => o.Position));
			foreach (IntVec3 c in CellRect.CenteredOn(p.Position, r).ClipInsideMap(p.Map))
			{
				if (graph.PatchAt(ci.CellToIndex(c)) == RM_ShadePatchGraph.NoPatch) continue;
				if (pawnsAt.Contains(c)) held++;
				else if (!c.Standable(p.Map)) unstandable++;
				else free++;
			}
			IntVec3 pick = RM_ShadeHop.SpreadLanding(p, graph, p.Position, out int pickLoad);
			return "pos=" + p.Position + " patch=" + graph.PatchAt(ci.CellToIndex(p.Position)) + " crowded=" + RM_ShadeHop.Crowded(p)
			       + " radius=" + r + " pick=" + pick + " pickPatch=" + graph.PatchAt(ci.CellToIndex(pick)) + " pickLoad=" + pickLoad + " others=" + RM_ShadeHop.OthersHere(p)
			       + " shadeInRadius free=" + free + " held=" + held + " unstandable=" + unstandable
			       + " job=" + (p.CurJob?.def.defName ?? "none");
		}
	}
}
