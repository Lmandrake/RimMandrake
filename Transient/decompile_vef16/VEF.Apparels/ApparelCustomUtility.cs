using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class ApparelCustomUtility
{
	public static bool WearsApparel(this Pawn pawn, ThingDef thingDef)
	{
		Pawn_ApparelTracker apparel = pawn.apparel;
		if (((apparel != null) ? apparel.WornApparel : null) != null)
		{
			foreach (Apparel item in pawn.apparel.WornApparel)
			{
				if (((Thing)item).def == thingDef)
				{
					return true;
				}
			}
		}
		return false;
	}
}
