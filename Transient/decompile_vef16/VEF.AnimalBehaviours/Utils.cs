using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public static class Utils
{
	public static float VacuumResistanceFromArmor(this Pawn pawn)
	{
		float num = 0f;
		Pawn_ApparelTracker apparel = pawn.apparel;
		List<Apparel> list = ((apparel != null) ? apparel.WornApparel : null);
		if (!GenList.NullOrEmpty<Apparel>((IList<Apparel>)list))
		{
			for (int i = 0; i < list.Count; i++)
			{
				float num2;
				if ((num2 = StatWorker.StatOffsetFromGear((Thing)(object)list[i], StatDefOf.VacuumResistance)) != 0f)
				{
					num += num2;
				}
			}
		}
		return num;
	}
}
