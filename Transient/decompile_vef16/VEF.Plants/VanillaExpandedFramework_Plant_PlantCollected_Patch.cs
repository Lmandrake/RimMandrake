using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Plants;

[HarmonyPatch(typeof(Plant))]
[HarmonyPatch("PlantCollected")]
public static class VanillaExpandedFramework_Plant_PlantCollected_Patch
{
	[HarmonyPrefix]
	public static void AddSecondaryOutput(Plant __instance, Pawn by)
	{
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		DualCropExtension modExtension = ((Def)((Thing)__instance).def).GetModExtension<DualCropExtension>();
		if (modExtension == null || !__instance.CanYieldNow())
		{
			return;
		}
		float statValue = StatExtension.GetStatValue((Thing)(object)by, StatDefOf.PlantHarvestYield, true, -1);
		if ((!by.RaceProps.Humanlike && !by.RaceProps.IsMechanoid) || __instance.Blighted || !(Rand.Value < statValue))
		{
			return;
		}
		int num = (int)((float)modExtension.outPutAmount * __instance.Growth);
		if (statValue > 1f)
		{
			num = GenMath.RoundRandom((float)num * statValue);
		}
		if (num <= 0)
		{
			return;
		}
		Thing val = null;
		if (modExtension.randomOutput && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)modExtension.randomSecondaryOutput))
		{
			val = ThingMaker.MakeThing(GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)modExtension.randomSecondaryOutput), (ThingDef)null);
		}
		else if (modExtension.secondaryOutput != null)
		{
			val = ThingMaker.MakeThing(modExtension.secondaryOutput, (ThingDef)null);
		}
		if (val != null)
		{
			val.stackCount = num;
			if (((Thing)by).Faction != Faction.OfPlayer)
			{
				ForbidUtility.SetForbidden(val, true, true);
			}
			GenPlace.TryPlaceThing(val, ((Thing)by).Position, ((Thing)by).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
		}
	}
}
