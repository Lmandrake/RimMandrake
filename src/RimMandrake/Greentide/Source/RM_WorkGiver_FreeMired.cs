using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Greentide
{
	/// <summary>GREENTIDE_STANDALONE_MOD_1 (M8, mire half). Hands out a
	/// pull-free job for any player-side pawn stuck at or above the mire's
	/// stuck threshold. WorkTypeDef assigned in XML (RM_Greentide_JobDefs.xml).</summary>
	public class RM_WorkGiver_FreeMired : WorkGiver_Scanner
	{
		public override PathEndMode PathEndMode => PathEndMode.Touch;

		public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
		{
			IReadOnlyList<Pawn> all = pawn.Map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < all.Count; i++)
			{
				Pawn candidate = all[i];
				if (candidate != pawn && candidate.Faction == Faction.OfPlayer
					&& candidate.health?.hediffSet.HasHediff(RM_DefOf.RM_Mired) == true)
				{
					yield return candidate;
				}
			}
		}

		public override bool ShouldSkip(Pawn pawn, bool forced = false)
		{
			return pawn.Faction != Faction.OfPlayer;
		}

		public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			if (!(t is Pawn target) || target == pawn || target.Faction != Faction.OfPlayer)
			{
				return false;
			}
			Hediff mired = target.health?.hediffSet.GetFirstHediffOfDef(RM_DefOf.RM_Mired);
			if (mired == null)
			{
				return false;
			}
			RM_MireExtension ext = target.Position.GetTerrain(pawn.Map)?.GetModExtension<RM_MireExtension>();
			float stuckThreshold = ext?.stuckThreshold ?? 0.85f;
			if (mired.Severity < stuckThreshold)
			{
				return false;
			}
			return pawn.CanReserve(target, 1, -1, null, forced);
		}

		public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
		{
			return JobMaker.MakeJob(RM_DefOf.RM_FreeMired, t);
		}
	}
}
