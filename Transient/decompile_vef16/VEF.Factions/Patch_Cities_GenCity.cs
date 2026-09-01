using RimWorld;
using Verse;

namespace VEF.Factions;

public static class Patch_Cities_GenCity
{
	public static class manual_RandomCityFaction_predicate
	{
		public static void Postfix(Faction x, ref bool __result)
		{
			if (__result)
			{
				FactionDefExtension factionDefExtension = FactionDefExtension.Get((Def)(object)x.def);
				__result = factionDefExtension.hasCities;
			}
		}
	}
}
