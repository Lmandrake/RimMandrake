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
	}
}
