using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnCapacityUtility), "CalculateCapacityLevel")]
public static class VanillaExpandedFramework_PawnCapacityUtility_CalculateCapacityLevel
{
	public static void Postfix(ref float __result, HediffSet diffSet, PawnCapacityDef capacity, List<CapacityImpactor> impactors = null, bool forTradePrice = false)
	{
		if (diffSet?.pawn == null)
		{
			return;
		}
		float num = float.NegativeInfinity;
		if (diffSet.pawn.apparel != null)
		{
			foreach (Apparel item in diffSet.pawn.apparel.WornApparel)
			{
				ApparelExtension modExtension = ((Def)((Thing)item).def).GetModExtension<ApparelExtension>();
				object obj;
				if (modExtension == null)
				{
					obj = null;
				}
				else
				{
					List<PawnCapacityMinLevel> pawnCapacityMinLevels = modExtension.pawnCapacityMinLevels;
					obj = ((pawnCapacityMinLevels != null) ? GenCollection.FirstOrDefault<PawnCapacityMinLevel>(pawnCapacityMinLevels, (Predicate<PawnCapacityMinLevel>)((PawnCapacityMinLevel x) => x.capacity == capacity)) : null);
				}
				PawnCapacityMinLevel pawnCapacityMinLevel = (PawnCapacityMinLevel)obj;
				if (pawnCapacityMinLevel != null)
				{
					if (pawnCapacityMinLevel.minLevel > num)
					{
						num = pawnCapacityMinLevel.minLevel;
					}
					impactors?.Add((CapacityImpactor)(object)new CapacityImpactorGearMinLevel
					{
						gear = (Thing)(object)item,
						extension = modExtension,
						capacity = capacity
					});
				}
			}
		}
		if (diffSet.pawn.equipment != null)
		{
			foreach (ThingWithComps item2 in diffSet.pawn.equipment.AllEquipmentListForReading)
			{
				ApparelExtension modExtension2 = ((Def)((Thing)item2).def).GetModExtension<ApparelExtension>();
				object obj2;
				if (modExtension2 == null)
				{
					obj2 = null;
				}
				else
				{
					List<PawnCapacityMinLevel> pawnCapacityMinLevels2 = modExtension2.pawnCapacityMinLevels;
					obj2 = ((pawnCapacityMinLevels2 != null) ? GenCollection.FirstOrDefault<PawnCapacityMinLevel>(pawnCapacityMinLevels2, (Predicate<PawnCapacityMinLevel>)((PawnCapacityMinLevel x) => x.capacity == capacity)) : null);
				}
				PawnCapacityMinLevel pawnCapacityMinLevel2 = (PawnCapacityMinLevel)obj2;
				if (pawnCapacityMinLevel2 != null)
				{
					if (pawnCapacityMinLevel2.minLevel > num)
					{
						num = pawnCapacityMinLevel2.minLevel;
					}
					impactors?.Add((CapacityImpactor)(object)new CapacityImpactorGearMinLevel
					{
						gear = (Thing)(object)item2,
						extension = modExtension2,
						capacity = capacity
					});
				}
			}
		}
		if (!float.IsInfinity(num) && !float.IsNaN(num) && num > __result)
		{
			__result = GenMath.RoundedHundredth(num);
		}
	}
}
