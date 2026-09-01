using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public static class XenophobicRageMentalStateUtility
{
	private static List<Pawn> tmpTargets = new List<Pawn>();

	public static Pawn FindPawnToKill(Pawn pawn)
	{
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)pawn).Spawned)
		{
			return null;
		}
		tmpTargets.Clear();
		CompExtremeXenophobia compExtremeXenophobia = ThingCompUtility.TryGetComp<CompExtremeXenophobia>((Thing)(object)pawn);
		if (compExtremeXenophobia == null)
		{
			return null;
		}
		IReadOnlyList<Pawn> allPawnsSpawned = ((Thing)pawn).Map.mapPawns.AllPawnsSpawned;
		for (int i = 0; i < allPawnsSpawned.Count; i++)
		{
			Pawn val = allPawnsSpawned[i];
			if (((Thing)val).Faction == ((Thing)pawn).Faction && !compExtremeXenophobia.Props.AcceptedDefnames.Contains(((Def)((Thing)val).def).defName) && val.RaceProps.Humanlike && val != pawn && ReachabilityUtility.CanReach(pawn, LocalTargetInfo.op_Implicit((Thing)(object)val), (PathEndMode)2, (Danger)3, false, false, (TraverseMode)0) && (val.CurJob == null || !val.CurJob.exitMapOnArrival))
			{
				tmpTargets.Add(val);
			}
		}
		if (!GenCollection.Any<Pawn>(tmpTargets))
		{
			return null;
		}
		Pawn result = GenCollection.RandomElement<Pawn>((IEnumerable<Pawn>)tmpTargets);
		tmpTargets.Clear();
		return result;
	}
}
