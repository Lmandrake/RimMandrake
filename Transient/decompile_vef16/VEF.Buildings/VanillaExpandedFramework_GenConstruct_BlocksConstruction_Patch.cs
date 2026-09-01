using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(GenConstruct), "BlocksConstruction")]
public static class VanillaExpandedFramework_GenConstruct_BlocksConstruction_Patch
{
	public static void Postfix(Thing constructible, Thing t, ref bool __result)
	{
		if (!__result)
		{
			return;
		}
		try
		{
			BuildableDef entityDefToBuild = ((constructible is Blueprint) ? constructible.def : ((!(constructible is Frame)) ? ((BuildableDef)constructible.def).blueprintDef : constructible.def.entityDefToBuild.blueprintDef)).entityDefToBuild;
			ThingDef val = (ThingDef)(object)((entityDefToBuild is ThingDef) ? entityDefToBuild : null);
			if (val?.building != null && val.building.canPlaceOverWall && val.HasComp(typeof(CompMountableOnWall)) && t.def.IsWall())
			{
				__result = false;
			}
		}
		catch
		{
		}
	}

	public static bool IsWall(this ThingDef def)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		if (EdificeUtility.IsEdifice((BuildableDef)(object)def))
		{
			if (!def.IsSmoothed && !((Def)def).defName.ToLower().Contains("wall"))
			{
				GraphicData graphicData = def.graphicData;
				if (graphicData == null || !((Enum)graphicData.linkFlags).HasFlag((Enum)(object)(LinkFlags)4))
				{
					if (def.building != null)
					{
						return def.building.supportsWallAttachments;
					}
					return false;
				}
			}
			return true;
		}
		return false;
	}
}
