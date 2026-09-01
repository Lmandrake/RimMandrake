using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch]
public static class VanillaExpandedFramework_VehicleFramework_Turret_Patch
{
	public static bool VFLoaded = ModLister.AnyModActiveNoSuffix(new List<string>(1) { "SmashPhil.VehicleFramework" });

	public static MethodInfo targetMethod;

	public static FastInvokeHandler maxRangeInfo;

	public static FastInvokeHandler turretLocation;

	public static FastInvokeHandler turretRotation;

	public static FieldRef<object, Vector2> aimPieOffset;

	public static Type VehicleType;

	public static object currentFiringVehicleTurret;

	public static bool Prepare(MethodBase target)
	{
		if (target != null)
		{
			return true;
		}
		if (VFLoaded)
		{
			VehicleType = AccessTools.TypeByName("Vehicles.VehiclePawn");
			targetMethod = AccessTools.Method("Vehicles.VehicleTurret:FireTurret", (Type[])null, (Type[])null);
			MethodInfo methodInfo = AccessTools.PropertyGetter("Vehicles.VehicleTurret:MaxRange");
			MethodInfo methodInfo2 = AccessTools.PropertyGetter("Vehicles.VehicleTurret:TurretLocation");
			MethodInfo methodInfo3 = AccessTools.PropertyGetter("Vehicles.VehicleTurret:TurretRotation");
			FieldInfo fieldInfo = AccessTools.Field("Vehicles.VehicleTurret:aimPieOffset");
			if ((object)VehicleType != null && (object)targetMethod != null && (object)methodInfo != null && (object)methodInfo2 != null && (object)methodInfo3 != null && (object)fieldInfo != null)
			{
				maxRangeInfo = MethodInvoker.GetHandler(methodInfo, false);
				turretLocation = MethodInvoker.GetHandler(methodInfo2, false);
				turretRotation = MethodInvoker.GetHandler(methodInfo3, false);
				aimPieOffset = AccessTools.FieldRefAccess<object, Vector2>(fieldInfo);
				return true;
			}
			Log.Error("[VEF] Failed to patch VehicleFramework, vehicle turrets will not work with some expendable projectiles");
		}
		return false;
	}

	public static MethodBase TargetMethod()
	{
		return targetMethod;
	}

	public static void Prefix(object __instance)
	{
		currentFiringVehicleTurret = __instance;
	}

	public static void Finalizer()
	{
		currentFiringVehicleTurret = null;
	}
}
