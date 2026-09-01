using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(GenConstruct), "CanConstruct", new Type[]
{
	typeof(Thing),
	typeof(Pawn),
	typeof(bool),
	typeof(bool),
	typeof(JobDef)
})]
public static class VanillaExpandedFramework_GenConstruct_CanConstruct_Patch
{
	public static void Postfix(ref bool __result, Thing t)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		if (!__result)
		{
			return;
		}
		try
		{
			BuildableDef val = t?.def?.entityDefToBuild;
			if (val == null)
			{
				return;
			}
			ThingDef val2 = (ThingDef)(object)((val is ThingDef) ? val : null);
			if (val2 != null && val2.HasComp(typeof(CompMountableOnWall)) && GenGrid.InBounds(t.Position, t.Map))
			{
				Building edifice = GridsUtility.GetEdifice(t.Position, t.Map);
				if (edifice == null || edifice is Frame || !((Thing)edifice).def.IsWall())
				{
					__result = false;
				}
			}
		}
		catch
		{
		}
	}
}
