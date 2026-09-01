using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(Faction), "TryMakeInitialRelationsWith")]
public static class VanillaExpandedFramework_Faction_TryMakeInitialRelationsWith_Patch
{
	[HarmonyAfter(new string[] { "rimworld.erdelf.alien_race.main" })]
	public static void Postfix(Faction __instance, Faction other)
	{
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_0167: Unknown result type (might be due to invalid IL or missing references)
		FactionDefExtension factionDefExtension = FactionDefExtension.Get((Def)(object)__instance.def);
		FactionDefExtension factionDefExtension2 = FactionDefExtension.Get((Def)(object)other.def);
		StartingGoodwillByFaction startingGoodwillByFaction = factionDefExtension?.startingGoodwillByFactionDefs?.Find((StartingGoodwillByFaction x) => x.factionDef == other.def);
		StartingGoodwillByFaction startingGoodwillByFaction2 = factionDefExtension2?.startingGoodwillByFactionDefs?.Find((StartingGoodwillByFaction x) => x.factionDef == __instance.def);
		if (startingGoodwillByFaction != null || startingGoodwillByFaction2 != null)
		{
			int? num = startingGoodwillByFaction?.Min;
			int? num2 = startingGoodwillByFaction?.Max;
			int? num3 = startingGoodwillByFaction2?.Min;
			int? num4 = startingGoodwillByFaction2?.Max;
			int num5 = MinOfNullableInts(num, num3);
			int num6 = MinOfNullableInts(num2, num4);
			int num7 = Rand.RangeInclusive(num5, num6);
			FactionRelationKind kind = (FactionRelationKind)((num7 > -10) ? ((num7 < 75) ? 1 : 2) : 0);
			FactionRelation obj = __instance.RelationWith(other, false);
			obj.baseGoodwill = num7;
			obj.kind = kind;
			FactionRelation obj2 = other.RelationWith(__instance, false);
			obj2.baseGoodwill = num7;
			obj2.kind = kind;
		}
	}

	private static int MinOfNullableInts(int? num1, int? num2)
	{
		if (num1.HasValue && num2.HasValue)
		{
			if (!(num1 < num2))
			{
				return num2.Value;
			}
			return num1.Value;
		}
		if (num1.HasValue && !num2.HasValue)
		{
			return num1.Value;
		}
		if (!num1.HasValue && num2.HasValue)
		{
			return num2.Value;
		}
		return 0;
	}
}
