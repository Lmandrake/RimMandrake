using System;
using HarmonyLib;
using RimWorld.Planet;

namespace VEF.Planet;

[HarmonyPatch(typeof(Caravan_PathFollower), "PatherTickInterval")]
public static class VanillaExpandedFramework_Caravan_PathFollower_PatherTickInterval_Patch
{
	public static void Prefix(Caravan_PathFollower __instance)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		if (!VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow.TryGetValue(__instance, out var value))
		{
			return;
		}
		if (value.destination != null)
		{
			if (__instance.Destination != ((WorldObject)value.destination).Tile)
			{
				CaravanArrivalAction_MovingBase caravanArrivalAction_MovingBase = Activator.CreateInstance(value.arrivalActionType) as CaravanArrivalAction_MovingBase;
				caravanArrivalAction_MovingBase.movingBase = value.destination;
				__instance.StartPath(((WorldObject)value.destination).Tile, (CaravanArrivalAction)(object)caravanArrivalAction_MovingBase, true, true);
			}
		}
		else
		{
			VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow.Remove(__instance);
		}
	}
}
