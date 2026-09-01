using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch]
public static class JobDriver_ManTurret_FindFuelForTurretLambda_Patch
{
	private static bool Prefix()
	{
		return JobDriver_ManTurret_GunNeedsRefueling_Patch.Prepare();
	}

	private static MethodBase TargetMethod()
	{
		MethodInfo methodInfo2 = AccessToolsExtensions.FindIncludingInnerTypes<MethodInfo>(typeof(JobDriver_ManTurret), (Func<Type, MethodInfo>)delegate(Type t)
		{
			if (t == typeof(JobDriver_ManTurret))
			{
				return (MethodInfo)null;
			}
			FieldInfo fieldInfo = AccessToolsExtensions.Field(t, "pawn");
			if (fieldInfo == null || !GenTypes.SameOrSubclassOf<Pawn>(fieldInfo.FieldType))
			{
				return (MethodInfo)null;
			}
			fieldInfo = AccessToolsExtensions.Field(t, "refuelableComp");
			if (fieldInfo == null || !GenTypes.SameOrSubclassOf<CompRefuelable>(fieldInfo.FieldType))
			{
				return (MethodInfo)null;
			}
			MethodInfo[] methods = t.GetMethods(AccessTools.all);
			foreach (MethodInfo methodInfo in methods)
			{
				if (methodInfo.Name.Contains("FindFuelForTurret") && methodInfo.Name.Contains("FuelValidator") && methodInfo.ReturnType == typeof(bool) && methodInfo.GetParameters().Any((ParameterInfo p) => p.Name == "t" && GenTypes.SameOrSubclassOf<Thing>(p.ParameterType)))
				{
					return methodInfo;
				}
			}
			return (MethodInfo)null;
		});
		if (methodInfo2 == null)
		{
			Log.Error("[VEF] Failed to find a fuel validator for JobDriver_ManTurret:FindFuelForTurret. Reservations for pawns operating mannable turrets may break.");
		}
		return methodInfo2;
	}

	private static void Postfix(Pawn ___pawn, CompRefuelable ___refuelableComp, Thing t, ref bool __result)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Expected O, but got Unknown
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		if (!__result || ___pawn == null || t == null || ((ThingComp)(___refuelableComp?)).parent == null)
		{
			return;
		}
		AutoRefuelMannedTurrets modExtension = ((Def)((Thing)((ThingComp)___refuelableComp).parent).def).GetModExtension<AutoRefuelMannedTurrets>();
		if (modExtension != null && modExtension.reloadsMoreThanSingleItem)
		{
			int num = Mathf.Clamp(modExtension.ModifyRefuelCount((Building)((ThingComp)___refuelableComp).parent, t), 1, t.stackCount);
			if (num > 1)
			{
				__result = ReservationUtility.CanReserve(___pawn, LocalTargetInfo.op_Implicit(t), 10, num, (ReservationLayerDef)null, false);
			}
		}
	}
}
